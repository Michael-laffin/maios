"""Search code skill for MAIOS."""

from typing import Any

from maios.skills.base import BaseSkill
from maios.skills.registry import register_skill


@register_skill
class SearchCodeSkill(BaseSkill):
    """Search for patterns in the codebase."""

    name = "search_code"
    description = "Search for text patterns or regex in project files"
    required_permissions = ["file:read"]

    input_schema = {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Search pattern (text or regex)",
            },
            "path": {
                "type": "string",
                "description": "Directory to search in (relative to project root)",
            },
            "file_pattern": {
                "type": "string",
                "description": "Glob pattern for files to search (e.g., '*.py')",
            },
            "is_regex": {
                "type": "boolean",
                "description": "Whether pattern is a regex",
            },
            "case_sensitive": {
                "type": "boolean",
                "description": "Whether search is case sensitive",
            },
        },
        "required": ["pattern"],
    }

    async def execute(
        self,
        pattern: str,
        path: str = ".",
        file_pattern: str = "*",
        is_regex: bool = False,
        case_sensitive: bool = True,
        **kwargs,
    ) -> dict[str, Any]:
        """Search for pattern in codebase.

        Note: Actual search requires sandbox environment.
        This is a placeholder that validates input.
        """
        if not pattern or not pattern.strip():
            return {
                "status": "error",
                "error": "No search pattern provided",
            }

        # Security: Prevent path traversal
        if ".." in path or path.startswith("/"):
            return {
                "status": "error",
                "error": "Invalid path: path traversal not allowed",
            }

        # Placeholder - actual search via sandbox
        return {
            "status": "pending",
            "message": "Code search requires sandbox environment (MetaContainer)",
            "pattern": pattern,
            "path": path,
            "file_pattern": file_pattern,
            "is_regex": is_regex,
            "case_sensitive": case_sensitive,
        }
