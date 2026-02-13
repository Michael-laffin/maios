"""Write file skill for MAIOS."""

from typing import Any

from maios.skills.base import BaseSkill
from maios.skills.registry import register_skill


@register_skill
class WriteFileSkill(BaseSkill):
    """Write content to a file."""

    name = "write_file"
    description = "Write or append content to a file in the project"
    required_permissions = ["file:write"]

    input_schema = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to write (relative to project root)",
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file",
            },
            "mode": {
                "type": "string",
                "enum": ["write", "append"],
                "description": "Write mode: 'write' to overwrite, 'append' to add",
            },
        },
        "required": ["file_path", "content"],
    }

    async def execute(
        self,
        file_path: str,
        content: str,
        mode: str = "write",
        **kwargs,
    ) -> dict[str, Any]:
        """Write content to file.

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

        if mode not in ["write", "append"]:
            return {
                "status": "error",
                "error": f"Invalid mode: {mode}. Must be 'write' or 'append'",
            }

        # Placeholder - actual file writing via sandbox
        return {
            "status": "pending",
            "message": "File writing requires sandbox environment (MetaContainer)",
            "file_path": file_path,
            "content_length": len(content),
            "mode": mode,
        }
