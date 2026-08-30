#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: compile_resume.sh RESUME.tex OUTPUT_DIR [CAREER_EVIDENCE.yaml]" >&2
  exit 64
fi

source_file=$1
output_dir=$2
evidence_file=${3:-}

if [[ ! -f "$source_file" || "${source_file##*.}" != "tex" ]]; then
  echo "Input must be an existing .tex file: $source_file" >&2
  exit 66
fi

mkdir -p "$output_dir"
source_abs=$(realpath "$source_file")
output_abs=$(realpath "$output_dir")
job_name=$(basename "$source_file" .tex)

if command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error \
    -output-directory="$output_abs" "$source_abs"
elif command -v pdflatex >/dev/null 2>&1; then
  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error \
    -output-directory="$output_abs" "$source_abs"
  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error \
    -output-directory="$output_abs" "$source_abs"
else
  echo "Neither latexmk nor pdflatex is installed" >&2
  exit 69
fi

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
audit_args=(--pdf "$output_abs/$job_name.pdf" --max-pages 1 --json-out "$output_abs/pdf-audit.json" --text-out "$output_abs/extracted.txt")
if [[ -n "$evidence_file" ]]; then
  audit_args+=(--evidence "$evidence_file")
fi
python3 "$script_dir/audit_pdf.py" "${audit_args[@]}"
echo "$output_abs/$job_name.pdf"

