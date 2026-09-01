#!/usr/bin/env bash
#
# Rebuild every dissertation figure from source, deterministically.
#
#   ./scripts/render_mermaid_figures.sh              # theme + all figures + manifest
#   ./scripts/render_mermaid_figures.sh sys_f1_architecture_deployment_boundary
#
# Steps:
#   1. expand exhibits/figure_palette.json into the shared Mermaid config and stylesheet;
#   2. render each exhibits/<figure>.mmd to <figure>.svg (vector) and <figure>.png (LaTeX input);
#   3. rebind exhibits/MERMAID_MANIFEST.csv to the new source, render and shared-input hashes.
#
# Colour never appears in an .mmd source. Each figure only assigns semantic roles with
# `class <nodes> fx-<role>`, and exhibits/figure_palette.json defines what every role means.
#
# The LaTeX build consumes the PNG renders; the SVG renders are the vector master copies.

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly DISSERTATION_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly EXHIBIT_DIR="${DISSERTATION_DIR}/exhibits"
readonly MERMAID_CLI_VERSION="11.16.0"
readonly PALETTE_PATH="${EXHIBIT_DIR}/figure_palette.json"
readonly CONFIG_PATH="${EXHIBIT_DIR}/mermaid-config.json"
readonly CSS_PATH="${EXHIBIT_DIR}/mermaid.css"
readonly PNG_SCALE="2"

# Every figure in the manuscript pipeline, in manuscript order.
readonly FIGURES=(
  "intro_f1_problem_to_research_contract"
  "lit_f1_evidence_claim_admission_audit_chain"
  "lit_f2_discovery_is_not_evidence"
  "meth_f1_design_science_evidence_chain"
  "meth_f2_dataset_freeze_timeline"
  "meth_f3_analysis_decision_flow"
  "sys_f1_architecture_deployment_boundary"
  "sys_f2_canonical_data_provenance_model"
  "sys_f3_legal_identity_decision_flow"
  "sys_f4_fixed_workflow_verification_state_machine"
  "sys_f5_company_research_evidence_funnel"
  "eval_f1_d0_metric_profile"
)

mermaid() {
  npx -y "@mermaid-js/mermaid-cli@${MERMAID_CLI_VERSION}" "$@"
}

render_figure() {
  local figure_name="$1"
  local source_path="${EXHIBIT_DIR}/${figure_name}.mmd"

  if [[ ! -f "${source_path}" ]]; then
    echo "error: no Mermaid source at ${source_path}" >&2
    return 1
  fi

  echo "  ${figure_name}"
  mermaid \
    --input "${source_path}" \
    --output "${EXHIBIT_DIR}/${figure_name}.svg" \
    --configFile "${CONFIG_PATH}" \
    --cssFile "${CSS_PATH}" \
    --backgroundColor white \
    --quiet
  mermaid \
    --input "${source_path}" \
    --output "${EXHIBIT_DIR}/${figure_name}.png" \
    --configFile "${CONFIG_PATH}" \
    --cssFile "${CSS_PATH}" \
    --backgroundColor white \
    --scale "${PNG_SCALE}" \
    --quiet
}

main() {
  echo "Building shared figure theme from $(basename "${PALETTE_PATH}")"
  python3 "${SCRIPT_DIR}/build_figure_theme.py"

  local -a selected=("$@")
  if [[ ${#selected[@]} -eq 0 ]]; then
    selected=("${FIGURES[@]}")
  fi

  echo "Rendering ${#selected[@]} figure(s) to SVG and PNG"
  local figure
  for figure in "${selected[@]}"; do
    render_figure "${figure}"
  done

  echo "Rebinding exhibits/MERMAID_MANIFEST.csv"
  python3 "${SCRIPT_DIR}/update_mermaid_manifest.py"
}

main "$@"
