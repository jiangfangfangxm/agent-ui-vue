import sys
import unittest
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.app_compiler import compile_app


class AppCompilerTests(unittest.TestCase):
    def test_compiles_warning_review_app_to_generated_artifacts(self):
        repo_root = Path(__file__).resolve().parents[2]
        config_path = repo_root / "apps" / "warning-review.app.yaml"
        output_root = repo_root / "generated" / "_test_app_compiler"
        shutil.rmtree(output_root, ignore_errors=True)
        try:
            result = compile_app(config_path, output_root)

            self.assertEqual(result.app_id, "warning_review_workbench")
            self.assertFalse(result.warnings)
            expected_files = {
                "app.normalized.json",
                "frontend/workflow-definition.generated.ts",
                "python/workflow_definition.generated.py",
                "tests/test_transition_contracts.generated.py",
                "README.generated.md",
            }
            generated_files = {
                path.relative_to(result.output_dir).as_posix()
                for path in result.written_files
            }

            self.assertEqual(expected_files, generated_files)

            workflow_definition = (
                result.output_dir / "python" / "workflow_definition.generated.py"
            ).read_text(encoding="utf-8")
            self.assertIn("save_report_revision", workflow_definition)
            self.assertIn("allowed_events_for_state", workflow_definition)
        finally:
            shutil.rmtree(output_root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
