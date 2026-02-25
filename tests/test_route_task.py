import pathlib
import os
import sys
import tempfile
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "skills" / "project-task-router" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import route_task  # noqa: E402


class RouteTaskTests(unittest.TestCase):
    def test_unknown_task_needs_clarification(self) -> None:
        result = route_task.route_task("Do something weird with moonshots")
        self.assertEqual(result["route"], "needs-clarification")
        self.assertEqual(result["confidence"], "low")
        self.assertIn("evidence", result)

    def test_substring_keywords_do_not_false_positive(self) -> None:
        result = route_task.route_task("Need something unusual")
        self.assertEqual(result["route"], "needs-clarification")

    def test_hyphenated_security_terms_route_correctly(self) -> None:
        result = route_task.route_task(
            "Implement HIPAA-compliant audit logging for appointment updates"
        )
        self.assertEqual(result["route"], "security-compliance-reliability")
        self.assertGreaterEqual(len(result["primary_skills"]), 1)

    def test_routes_all_top_domains(self) -> None:
        cases = [
            ("Run customer discovery interviews and validate TAM SAM SOM", "market-discovery-validation"),
            ("Create roadmap and positioning strategy for MVP pricing", "product-strategy-positioning"),
            ("Draft architecture and API integration spec with data model", "architecture-build-planning"),
            ("Implement endpoint migration and refactor failing feature tests", "feature-implementation"),
            (
                "Improve frontend dashboard layout and accessibility in design system",
                "ui-ux-frontend",
            ),
            ("Complete HIPAA compliance threat model and audit controls", "security-compliance-reliability"),
            ("Build RAG pipeline with embeddings and LLM evaluation metrics", "data-analytics-ai"),
            (
                "Improve deployment pipeline, on-call runbook, and SLO observability",
                "platform-ops-reliability",
            ),
        ]

        for task_text, expected_route in cases:
            with self.subTest(task=task_text):
                result = route_task.route_task(task_text)
                self.assertEqual(result["route"], expected_route)

    def test_ambiguous_route_surfaces_alternatives(self) -> None:
        result = route_task.route_task("Architecture planning for endpoint migration")
        self.assertEqual(result["route"], "architecture-build-planning")
        self.assertIn("feature-implementation", result["alternatives"])

    def test_missing_capabilities_with_known_inventory(self) -> None:
        result = route_task.route_task(
            text="Improve frontend layout and accessibility",
            inline_skills="ui-ux-pro-max,design-system",
        )
        self.assertEqual(result["route"], "ui-ux-frontend")
        self.assertIn("product-design", result["missing_capabilities"])

    def test_no_required_capabilities_available_returns_clarification(self) -> None:
        result = route_task.route_task(
            text="Improve frontend layout and accessibility",
            inline_skills="",
        )
        self.assertEqual(result["route"], "needs-clarification")

    def test_evidence_contains_all_domains(self) -> None:
        result = route_task.route_task("Build RAG pipeline with embeddings")
        self.assertEqual(len(result["evidence"]), 8)

    def test_single_strong_keyword_routes(self) -> None:
        result = route_task.route_task("HIPAA")
        self.assertEqual(result["route"], "security-compliance-reliability")

    def test_single_weak_keyword_stays_in_clarification(self) -> None:
        result = route_task.route_task("planning")
        self.assertEqual(result["route"], "needs-clarification")

    def test_discover_installed_skills_reads_home_manifest(self) -> None:
        home_dir = pathlib.Path("C:/mock-home")
        manifest_path = home_dir / ".codex" / "installed-skills.json"

        def exists_side_effect(path_obj: pathlib.Path) -> bool:
            return str(path_obj) == str(manifest_path)

        with mock.patch.dict(
            os.environ, {key: "" for key in route_task.ENV_SKILL_KEYS}, clear=False
        ):
            with mock.patch("route_task.Path.home", return_value=home_dir):
                with mock.patch("route_task.Path.exists", autospec=True, side_effect=exists_side_effect):
                    with mock.patch("route_task._load_skills_file", return_value={"alpha-skill", "beta-skill"}):
                        skills, source = route_task.discover_installed_skills()

        self.assertEqual(skills, {"alpha-skill", "beta-skill"})
        self.assertEqual(source, str(manifest_path))

    def test_discover_installed_skills_reads_plugin_manifest(self) -> None:
        plugin_root = pathlib.Path("C:/repo/skills/project-task-router")
        script_path = plugin_root / "scripts" / "route_task.py"
        manifest_path = plugin_root / "installed-skills.json"

        def exists_side_effect(path_obj: pathlib.Path) -> bool:
            return str(path_obj) == str(manifest_path)

        with mock.patch.dict(
            os.environ, {key: "" for key in route_task.ENV_SKILL_KEYS}, clear=False
        ):
            with mock.patch.object(route_task, "__file__", str(script_path)):
                with mock.patch("route_task.Path.home", return_value=pathlib.Path("C:/mock-home")):
                    with mock.patch("route_task.Path.exists", autospec=True, side_effect=exists_side_effect):
                        with mock.patch("route_task._load_skills_file", return_value={"plugin-skill"}):
                            skills, source = route_task.discover_installed_skills()

        self.assertEqual(skills, {"plugin-skill"})
        self.assertEqual(source, str(manifest_path))

    def test_malformed_json_skills_file_degrades_gracefully(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp_file:
            tmp_file.write("alpha-skill,beta-skill")
            temp_path = pathlib.Path(tmp_file.name)

        try:
            skills, source = route_task.discover_installed_skills(skills_file=str(temp_path))
        finally:
            temp_path.unlink(missing_ok=True)

        self.assertEqual(skills, {"alpha-skill", "beta-skill"})
        self.assertEqual(source, str(temp_path))


if __name__ == "__main__":
    unittest.main()
