from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .bootstrap import create_runtime, project_root
from .enums import DataClassification
from .evaluation import run_evaluation, write_evaluation


def _json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, default=str))


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
        "--classification",
        choices=[member.value for member in DataClassification],
        default=DataClassification.RESTRICTED.value,
    )

    subparsers.add_parser(
        "demo", help="Import the fictional fixture and run to the human-review gate."
    )

    run_parser = subparsers.add_parser("run", help="Run a stored dataset to human review.")
    run_parser.add_argument("dataset_id")

    approve_parser = subparsers.add_parser("approve", help="Record human report approval.")
    approve_parser.add_argument("report_id")
    approve_parser.add_argument("--actor", required=True)
    approve_parser.add_argument("--reason", required=True)

    reject_parser = subparsers.add_parser("reject", help="Record human report rejection.")
    reject_parser.add_argument("report_id")
    reject_parser.add_argument("--actor", required=True)
    reject_parser.add_argument("--reason", required=True)

    export_parser = subparsers.add_parser("export", help="Export an approved report.")
    export_parser.add_argument("report_id")

    evaluation_parser = subparsers.add_parser(
        "evaluate", help="Run the labelled synthetic evaluation harness."
    )
    evaluation_parser.add_argument(
        "--cases", type=Path, default=project_root() / "fixtures" / "evaluation_cases.json"
    )
    evaluation_parser.add_argument(
        "--output", type=Path, default=project_root() / "var" / "evaluation" / "latest.json"
    )
    evaluation_parser.add_argument("--repeats", type=int, default=3)

    serve_parser = subparsers.add_parser("serve", help="Run the local review interface.")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "evaluate":
        evaluation_result = run_evaluation(args.cases.resolve(), repeats=args.repeats)
        write_evaluation(evaluation_result, args.output.resolve())
        _json(
            {
                "output": str(args.output.resolve()),
                "summaries": evaluation_result["summaries"],
            }
        )
        return 0

    if args.command == "serve":
        if args.host not in {"127.0.0.1", "localhost", "::1"}:
            raise SystemExit("This research prototype may only bind to a loopback interface.")
        import uvicorn

        uvicorn.run("portfolio_agent.web:app", host=args.host, port=args.port, reload=False)
        return 0

    runtime = create_runtime()
    if args.command == "init-db":
        _json({"database_url": runtime.settings.database_url, "status": "initialised"})
    elif args.command == "import":
        import_result = runtime.importer.import_file(
            args.path.resolve(),
            period_label=args.period,
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
        runtime.reports.approve(args.report_id, actor=args.actor, reason=args.reason)
        _json({"report_id": args.report_id, "status": "approved"})
    elif args.command == "reject":
        runtime.reports.reject(args.report_id, actor=args.actor, reason=args.reason)
        _json({"report_id": args.report_id, "status": "rejected"})
    elif args.command == "export":
        bundle = runtime.reports.export(args.report_id)
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
