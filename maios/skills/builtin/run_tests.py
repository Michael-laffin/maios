"""Run tests skill for MAIOS."""

from typing import Any

from maios.skills.base import BaseSkill
from maios.skills.registry import register_skill


@register_skill
class RunTestsSkill(BaseSkill):
    """Execute tests in the project."""

    name = "run_tests"
    description = "Run test suites (pytest, jest, etc.) in the project"
    required_permissions = ["exec"]

    input_schema = {
        "type": "object",
        "properties": {
            "test_path": {
                "type": "string",
                "description": "Path to test file or directory",
            },
            "test_filter": {
                "type": "string",
                "description": "Filter to run specific tests",
            },
            "framework": {
                "type": "string",
                "enum": ["pytest", "jest", "unittest", "auto"],
                "description": "Test framework to use",
            },
            "coverage": {
                "type": "boolean",
                "description": "Whether to collect coverage",
            },
            "verbose": {
                "type": "boolean",
                "description": "Verbose output",
            },
        },
        "required": [],
    }

    async def execute(
        self,
        test_path: str = ".",
        test_filter: str | None = None,
        framework: str = "auto",
        coverage: bool = False,
        verbose: bool = True,
        **kwargs,
    ) -> dict[str, Any]:
        """Run tests.

        Note: Actual test execution requires sandbox environment.
        This is a placeholder that validates input.
        """
        if framework not in ["pytest", "jest", "unittest", "auto"]:
            return {
                "status": "error",
                "error": f"Unsupported framework: {framework}",
            }

        # Security: Prevent path traversal
        if ".." in test_path or test_path.startswith("/"):
            return {
                "status": "error",
                "error": "Invalid test path: path traversal not allowed",
            }

        # Placeholder - actual test execution via sandbox
        return {
            "status": "pending",
            "message": "Test execution requires sandbox environment (MetaContainer)",
            "test_path": test_path,
            "test_filter": test_filter,
            "framework": framework,
            "coverage": coverage,
            "verbose": verbose,
        }
