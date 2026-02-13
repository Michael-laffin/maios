"""Read file skill for MAIOS."""

from typing import Any

from maios.skills.base import BaseSkill
from maios.skills.registry import register_skill


@register_skill
class ReadFileSkill(BaseSkill):
    """Read contents of a file."""

    name = "read_file"
    description = "Read the contents of a file from the project"
    required_permissions = ["file:read"]

    input_schema = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to read (relative to project root)",
            },
            "start_line": {
                "type": "integer",
                "description": "Starting line number (1-indexed, optional)",
            },
            "end_line": {
                "type": "integer",
                "description": "Ending line number (1-indexed, optional)",
            },
        },
        "required": ["file_path"],
    }

    async def execute(
        self,
        file_path: str,
        start_line: int | None = None,
        end_line: int | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Read file contents.

        Note: Actual file access requires sandbox environment.
        This is a placeholder that validates input.
        """
        if not file_path or not file_path.strip():
            return {
                "status": "error",
                "error": "No file path provided",
            }

        # Security: Prevent path traversal
        if ".." in file_path or file_path.startswith("/"):
            return {
                "status": "error",
                "error": "Invalid file path: path traversal not allowed",
            }

        # Placeholder - actual file reading via sandbox
        return {
            "status": "pending",
            "message": "File reading requires sandbox environment (MetaContainer)",
            "file_path": file_path,
            "start_line": start_line,
            "end_line": end_line,
        }
