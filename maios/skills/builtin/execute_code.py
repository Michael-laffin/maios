# maios/skills/builtin/execute_code.py
import logging
from typing import Any

from maios.sandbox import sandbox_manager, ExecutionRequest
from maios.skills.base import BaseSkill
from maios.skills.registry import register_skill

logger = logging.getLogger(__name__)


@register_skill
class ExecuteCodeSkill(BaseSkill):
    """Execute code in a sandboxed environment."""

    name = "execute_code"
    description = "Execute Python or JavaScript code in a sandbox"
    required_permissions = ["exec"]

    input_schema = {
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Code to execute"},
            "language": {"type": "string", "enum": ["python", "javascript"]},
            "timeout": {"type": "integer", "default": 30},
        },
        "required": ["code", "language"],
    }

    async def execute(
        self,
        code: str,
        language: str = "python",
        timeout: int = 30,
        **kwargs,
    ) -> dict[str, Any]:
        """Execute code in sandbox.

        Uses Docker-based sandbox manager for secure code execution
        with resource limits and network isolation.
        """
        # Validate language
        if language not in ["python", "javascript"]:
            return {
                "status": "error",
                "error": f"Unsupported language: {language}. Supported: python, javascript",
            }

        # Validate code
        if not code or not code.strip():
            return {
                "status": "error",
                "error": "No code provided",
            }

        # Check if sandbox is available
        if not sandbox_manager.is_healthy():
            logger.warning("Docker sandbox not available, returning placeholder response")
            return {
                "status": "unavailable",
                "message": "Docker sandbox is not available. Please ensure Docker is running.",
                "code_length": len(code),
                "language": language,
            }

        try:
            # Create execution request
            request = ExecutionRequest(
                language=language,
                code=code,
                timeout_seconds=timeout,
            )

            # Execute in sandbox
            result = await sandbox_manager.execute_code(request)

            # Build response
            if result.error:
                return {
                    "status": "error",
                    "error": result.error,
                    "stderr": result.stderr,
                    "exit_code": result.exit_code,
                    "duration_ms": result.duration_ms,
                }

            return {
                "status": "success" if result.exit_code == 0 else "error",
                "exit_code": result.exit_code,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration_ms": result.duration_ms,
                "memory_used_mb": result.memory_used_mb,
            }

        except Exception as e:
            logger.exception(f"Code execution failed: {e}")
            return {
                "status": "error",
                "error": f"Execution failed: {str(e)}",
            }
