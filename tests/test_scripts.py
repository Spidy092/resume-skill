from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)


class ResumeOptimizerTests(unittest.TestCase):
    def test_valid_claims_pass(self) -> None:
        result = run(
            "python3", "scripts/verify_claims.py",
            "--evidence", str(FIXTURES / "career-evidence.yaml"),
            "--resume", str(FIXTURES / "resume-valid.yaml"),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_unsupported_metric_and_technology_fail(self) -> None:
        result = run(
            "python3", "scripts/verify_claims.py",
            "--evidence", str(FIXTURES / "career-evidence.yaml"),
            "--resume", str(FIXTURES / "resume-invalid.yaml"),
        )
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        messages = " ".join(item["message"] for item in report["issues"])
        self.assertIn("75%", messages)
        self.assertIn("Kubernetes", messages)

    def test_job_comparison_matches_aliases_and_ranks_relevant_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "analysis.json"
            result = run(
                "python3", "scripts/compare_jd.py",
                "--evidence", str(FIXTURES / "career-evidence.yaml"),
                "--job", str(FIXTURES / "job-description.txt"),
                "--json-out", str(output),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
            matched = {row["canonical"]: row for row in report["skill_matches"]}
            self.assertEqual(matched["GitHub Actions"]["classification"], "supported_direct")
            self.assertEqual(matched["AWS"]["classification"], "supported_alias")
            self.assertEqual(report["project_scores"][0]["id"], "project-release")

    @unittest.skipUnless(shutil.which("latexmk") and shutil.which("pdftotext"), "TeX/PDF tools unavailable")
    def test_template_compiles_and_extracts_in_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            tex_file = Path(temp) / "resume.tex"
            render = run(
                "python3", "scripts/render_resume.py",
                "--evidence", str(FIXTURES / "career-evidence.yaml"),
                "--resume", str(FIXTURES / "resume-valid.yaml"),
                "--output", str(tex_file),
            )
            self.assertEqual(render.returncode, 0, render.stdout + render.stderr)
            result = run("bash", "scripts/compile_resume.sh", str(tex_file), temp, str(FIXTURES / "career-evidence.yaml"))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads((Path(temp) / "pdf-audit.json").read_text())
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["pages"], 1)


if __name__ == "__main__":
    unittest.main()
