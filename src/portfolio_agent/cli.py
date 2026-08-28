from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import replace
from datetime import date
from pathlib import Path
from tempfile import mkdtemp
from typing import Any

from .bootstrap import (
    create_fixture_research_runtime,
    create_openai_experiment_runtime,
    create_runtime,
    project_root,
)
from .config import Settings
from .enums import DataClassification
from .evaluation import run_evaluation, write_evaluation
from .evaluation_datasets import manifest_for_legacy_cases
from .experiments import run_openai_synthetic_smoke
from .visualizations import generate_visual_pack


def _json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, default=str))


def _load_local_openai_key(root: Path) -> bool:
    """Load only OPENAI_API_KEY from a private ignored .env for the explicit smoke command."""
    if os.getenv("OPENAI_API_KEY"):
        return False
    env_path = root / ".env"
    if not env_path.is_file():
        raise RuntimeError("Set OPENAI_API_KEY in the process environment or private local .env.")
    if env_path.stat().st_mode & 0o077:
        raise RuntimeError("Private .env permissions are too broad; run: chmod 600 .env")

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").lstrip()
        name, raw_value = line.split("=", 1)
        if name.strip() != "OPENAI_API_KEY":
            continue
        value = raw_value.strip()
        if value[:1] in {'"', "'"}:
            if len(value) < 2 or value[-1] != value[0]:
                raise RuntimeError("OPENAI_API_KEY has unmatched quotes in .env.")
            value = value[1:-1]
        if not value:
            raise RuntimeError("OPENAI_API_KEY is empty in .env.")
        os.environ["OPENAI_API_KEY"] = value
        return True
    raise RuntimeError("OPENAI_API_KEY is missing from .env.")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="portfolio-agent",
        description="Local evidence-first portfolio reporting research prototype.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-db", help="Initialise the local database and metric catalogue.")

    import_parser = subparsers.add_parser("import", help="Import XLSX, CSV, or JSON locally.")
    import_parser.add_argument("path", type=Path)
    import_parser.add_argument("--period")
    import_parser.add_argument(
        "--cutoff",
        type=date.fromisoformat,
        help="Reporting cutoff in YYYY-MM-DD format; required by the CBIT workbook profile.",
    )
    import_parser.add_argument(
        "--classification",
        choices=[member.value for member in DataClassification],
        default=DataClassification.RESTRICTED.value,
    )

    subparsers.add_parser(
        "demo", help="Import the fictional fixture and run to the human-review gate."
    )

    openai_smoke_parser = subparsers.add_parser(
        "openai-smoke",
        help="Run one real OpenAI extraction inside the synthetic eight-stage workflow.",
    )
    openai_smoke_parser.add_argument(
        "--acknowledge-synthetic-only",
        action="store_true",
        help="Confirm that only the checksum-pinned synthetic fixture may be sent externally.",
    )

    run_parser = subparsers.add_parser("run", help="Run a stored dataset to human review.")
    run_parser.add_argument("dataset_id")

    approve_parser = subparsers.add_parser("approve", help="Record human report approval.")
    approve_parser.add_argument("report_id")
    approve_parser.add_argument("--actor", required=True)
    approve_parser.add_argument("--reason", required=True)
    approve_parser.add_argument("--expected-version", required=True, type=int)

    reject_parser = subparsers.add_parser("reject", help="Record human report rejection.")
    reject_parser.add_argument("report_id")
    reject_parser.add_argument("--actor", required=True)
    reject_parser.add_argument("--reason", required=True)
    reject_parser.add_argument("--expected-version", required=True, type=int)

    export_parser = subparsers.add_parser("export", help="Export an approved report.")
    export_parser.add_argument("report_id")
    export_parser.add_argument("--expected-version", required=True, type=int)

    evaluation_parser = subparsers.add_parser(
        "evaluate", help="Run the labelled synthetic evaluation harness."
    )
    evaluation_inputs = evaluation_parser.add_mutually_exclusive_group()
    evaluation_inputs.add_argument(
        "--manifest",
        type=Path,
        help="Versioned D0/D1/D2 evaluation manifest.",
    )
    evaluation_inputs.add_argument(
        "--cases",
        type=Path,
        help=(
            "Deprecated cases-file path; it must be admitted by a sibling evaluation_manifest.json."
        ),
    )
    evaluation_parser.add_argument(
        "--output", type=Path, default=project_root() / "var" / "evaluation" / "latest.json"
    )
    evaluation_parser.add_argument("--repeats", type=int, default=3)

    visual_parser = subparsers.add_parser(
        "visualize", help="Generate the deterministic dissertation SVG visual pack."
    )
    visual_parser.add_argument(
        "--input",
        type=Path,
        default=project_root() / "fixtures" / "visualisation_pack.json",
    )
    visual_parser.add_argument(
        "--output",
        type=Path,
        default=project_root() / "docs" / "figures" / "generated",
    )

    serve_parser = subparsers.add_parser("serve", help="Run the local review interface.")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)
    serve_parser.add_argument(
        "--fixture-research",
        action="store_true",
        help=(
            "Serve with an offline fixture research corpus. The full agent workflow runs, "
            "but no external model call and no outbound request is made and every run is "
            "synthetic."
        ),
    )
    serve_parser.add_argument(
        "--docker-local",
        action="store_true",
        help=(
            "Bind inside a container and accept only private container-network clients. "
            "The published host port must still be restricted to loopback."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "evaluate":
        if args.cases is not None:
            print(
                "warning: --cases is deprecated; use --manifest instead",
                file=sys.stderr,
            )
            manifest_path = manifest_for_legacy_cases(args.cases)
        else:
            manifest_path = (
                args.manifest
                if args.manifest is not None
                else project_root() / "fixtures" / "evaluation_manifest.json"
            )
        evaluation_result = run_evaluation(manifest_path.resolve(), repeats=args.repeats)
        write_evaluation(evaluation_result, args.output.resolve())
        _json(
            {
                "output": str(args.output.resolve()),
                "summaries": evaluation_result["summaries"],
            }
        )
        return 0

    if args.command == "visualize":
        manifest = generate_visual_pack(args.input.resolve(), args.output.resolve())
        _json(
            {
                "output": str(args.output.resolve()),
                "figure_count": manifest["figure_count"],
                "manifest": str(args.output.resolve() / "manifest.json"),
            }
        )
        return 0

    if args.command == "serve":
        if not args.docker_local and args.host not in {"127.0.0.1", "localhost", "::1"}:
            raise SystemExit("This research prototype may only bind to a loopback interface.")
        import uvicorn

        from .web import create_app

        serve_runtime = create_fixture_research_runtime() if args.fixture_research else None
        if serve_runtime is not None:
            print(
                "Fixture research enabled: no external model call and no outbound request. "
                "Every run produced in this mode is synthetic.",
                file=sys.stderr,
            )
        uvicorn.run(
            create_app(
                serve_runtime,
                allow_container_network_clients=args.docker_local,
            ),
            host="0.0.0.0" if args.docker_local else args.host,
            port=args.port,
            reload=False,
        )
        return 0

    if args.command == "openai-smoke":
        if not args.acknowledge_synthetic_only:
            raise SystemExit("Refusing live model use without --acknowledge-synthetic-only.")
        root = project_root()
        loaded_local_key = _load_local_openai_key(root)
        try:
            runtime_parent = root / "var" / "experiments" / "runtimes"
            runtime_parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            runtime_parent.chmod(0o700)
            runtime_root = Path(mkdtemp(prefix="openai-smoke.", dir=runtime_parent))
            settings = replace(
                Settings.from_env(root),
                database_url=f"sqlite:///{runtime_root / 'portfolio.db'}",
                raw_data_dir=runtime_root / "raw",
                source_snapshot_dir=runtime_root / "sources",
                allow_external_llm=True,
                allow_live_public_retrieval=False,
                enable_synthetic_fixture_connector=True,
            )
            experiment_runtime = create_openai_experiment_runtime(settings)
            try:
                result = run_openai_synthetic_smoke(experiment_runtime)
            finally:
                experiment_runtime.engine.dispose()
            result["runtime_directory"] = str(runtime_root)
            result["serve_command"] = (
                f"PORTFOLIO_DATABASE_URL='{settings.database_url}' "
                f"PORTFOLIO_RAW_DATA_DIR='{settings.raw_data_dir}' "
                f"PORTFOLIO_SOURCE_SNAPSHOT_DIR='{settings.source_snapshot_dir}' "
                ".venv/bin/portfolio-agent serve"
            )
            _json(result)
        finally:
            if loaded_local_key:
                os.environ.pop("OPENAI_API_KEY", None)
        return 0

    runtime = create_runtime()
    if args.command == "init-db":
        _json({"database_url": runtime.settings.database_url, "status": "initialised"})
    elif args.command == "import":
        import_result = runtime.importer.import_file(
            args.path.resolve(),
            period_label=args.period,
            reporting_cutoff=args.cutoff,
            classification=DataClassification(args.classification),
        )
        _json(import_result.model_dump(mode="json"))
    elif args.command == "demo":
        imported = runtime.importer.import_file(
            project_root() / "fixtures" / "synthetic_portfolio.json",
            classification=DataClassification.SYNTHETIC,
        )
        pipeline = runtime.workflow.run(imported.dataset_id)
        _json(
            {
                "import": imported.model_dump(mode="json"),
                "pipeline": pipeline.model_dump(mode="json"),
                "next_action": "Review and explicitly approve or reject the pending report.",
            }
        )
    elif args.command == "run":
        _json(runtime.workflow.run(args.dataset_id).model_dump(mode="json"))
    elif args.command == "approve":
        runtime.reports.approve(
            args.report_id,
            actor=args.actor,
            reason=args.reason,
            expected_lock_version=args.expected_version,
        )
        _json({"report_id": args.report_id, "status": "approved"})
    elif args.command == "reject":
        runtime.reports.reject(
            args.report_id,
            actor=args.actor,
            reason=args.reason,
            expected_lock_version=args.expected_version,
        )
        _json({"report_id": args.report_id, "status": "rejected"})
    elif args.command == "export":
        bundle = runtime.reports.export(args.report_id, expected_lock_version=args.expected_version)
        _json(
            {
                "report_id": bundle.report_id,
                "version": bundle.version,
                "content_hash": bundle.content_hash,
                "json": str(bundle.json_path),
                "markdown": str(bundle.markdown_path),
                "html": str(bundle.html_path),
            }
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
