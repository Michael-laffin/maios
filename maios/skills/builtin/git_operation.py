"""Git operation skill for MAIOS."""

from typing import Any

from maios.skills.base import BaseSkill
from maios.skills.registry import register_skill


@register_skill
class GitOperationSkill(BaseSkill):
    """Perform git operations."""

    name = "git_operation"
    description = "Perform git operations like status, diff, commit, push, pull"
    required_permissions = ["git:read", "git:write"]

    input_schema = {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["status", "diff", "log", "commit", "push", "pull", "branch", "checkout"],
                "description": "Git operation to perform",
            },
            "args": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Additional arguments for the operation",
            },
            "message": {
                "type": "string",
                "description": "Commit message (for commit operation)",
            },
            "branch": {
                "type": "string",
                "description": "Branch name (for branch/checkout operations)",
            },
        },
        "required": ["operation"],
    }

    # Operations that only require read permission
    READ_ONLY_OPERATIONS = ["status", "diff", "log"]

    async def execute(
        self,
        operation: str,
        args: list[str] | None = None,
        message: str | None = None,
        branch: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Perform git operation.

        Note: Actual git operations require sandbox environment.
        This is a placeholder that validates input.
        """
        valid_operations = ["status", "diff", "log", "commit", "push", "pull", "branch", "checkout"]
        if operation not in valid_operations:
            return {
                "status": "error",
                "error": f"Invalid operation: {operation}. Must be one of {valid_operations}",
            }

        # Validate commit has message
        if operation == "commit" and not message:
            return {
                "status": "error",
                "error": "Commit operation requires a message",
            }

        # Validate branch operations have branch name
        if operation in ["branch", "checkout"] and not branch:
            return {
                "status": "error",
                "error": f"{operation} operation requires a branch name",
            }

        # Placeholder - actual git operations via sandbox
        return {
            "status": "pending",
            "message": "Git operations require sandbox environment (MetaContainer)",
            "operation": operation,
            "args": args or [],
            "message": message,
            "branch": branch,
        }

    def validate_permissions(self, agent_permissions: list[str]) -> bool:
        """Check if agent has required permissions based on operation."""
        # For read-only operations, only need git:read
        # For write operations, need git:write
        # This is a simplified check - actual operation checking happens at execution time
        if "git:read" in agent_permissions or "git:write" in agent_permissions:
            return True
        return False
