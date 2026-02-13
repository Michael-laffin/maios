# tests/unit/test_execute_code.py
import pytest
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_execute_code_skill_exists():
    """Test execute_code skill is registered."""
    from maios.skills.builtin.execute_code import ExecuteCodeSkill

    skill = ExecuteCodeSkill()
    assert skill.name == "execute_code"
    assert "exec" in skill.required_permissions


@pytest.mark.asyncio
async def test_execute_code_skill_validates_input():
    """Test execute_code validates input."""
    from maios.skills.builtin.execute_code import ExecuteCodeSkill

    skill = ExecuteCodeSkill()
    result = await skill.execute(code="print('hello')", language="python")

    # Result should have a status
    assert "status" in result


@pytest.mark.asyncio
async def test_execute_code_rejects_unsupported_language():
    """Test execute_code rejects unsupported languages."""
    from maios.skills.builtin.execute_code import ExecuteCodeSkill

    skill = ExecuteCodeSkill()
    result = await skill.execute(code="puts 'hello'", language="ruby")

    assert result["status"] == "error"
    assert "Unsupported language" in result["error"]


@pytest.mark.asyncio
async def test_execute_code_rejects_empty_code():
    """Test execute_code rejects empty code."""
    from maios.skills.builtin.execute_code import ExecuteCodeSkill

    skill = ExecuteCodeSkill()
    result = await skill.execute(code="", language="python")

    assert result["status"] == "error"
    assert "No code provided" in result["error"]


@pytest.mark.asyncio
async def test_execute_code_returns_unavailable_when_docker_not_running():
    """Test execute_code returns unavailable when Docker is not running."""
    from maios.skills.builtin.execute_code import ExecuteCodeSkill

    skill = ExecuteCodeSkill()

    with patch("maios.skills.builtin.execute_code.sandbox_manager") as mock_manager:
        mock_manager.is_healthy.return_value = False

        result = await skill.execute(code="print('hello')", language="python")

        assert result["status"] == "unavailable"
        assert "Docker" in result["message"]


@pytest.mark.asyncio
async def test_execute_code_uses_sandbox_manager():
    """Test execute_code uses sandbox manager for execution."""
    from maios.skills.builtin.execute_code import ExecuteCodeSkill
    from maios.sandbox.models import ExecutionResult

    skill = ExecuteCodeSkill()

    mock_result = ExecutionResult(
        exit_code=0,
        stdout="Hello, World!\n",
        stderr="",
        duration_ms=100,
    )

    with patch("maios.skills.builtin.execute_code.sandbox_manager") as mock_manager:
        mock_manager.is_healthy.return_value = True
        mock_manager.execute_code = AsyncMock(return_value=mock_result)

        result = await skill.execute(code="print('Hello, World!')", language="python")

        assert result["status"] == "success"
        assert result["exit_code"] == 0
        assert "Hello, World!" in result["stdout"]
        assert result["duration_ms"] == 100

        # Verify sandbox manager was called correctly
        mock_manager.execute_code.assert_called_once()
        call_args = mock_manager.execute_code.call_args[0][0]
        assert call_args.language == "python"
        assert call_args.code == "print('Hello, World!')"


@pytest.mark.asyncio
async def test_execute_code_handles_execution_error():
    """Test execute_code handles execution errors."""
    from maios.skills.builtin.execute_code import ExecuteCodeSkill
    from maios.sandbox.models import ExecutionResult

    skill = ExecuteCodeSkill()

    mock_result = ExecutionResult(
        exit_code=1,
        stdout="",
        stderr="NameError: name 'x' is not defined\n",
        duration_ms=50,
        error="Execution failed",
    )

    with patch("maios.skills.builtin.execute_code.sandbox_manager") as mock_manager:
        mock_manager.is_healthy.return_value = True
        mock_manager.execute_code = AsyncMock(return_value=mock_result)

        result = await skill.execute(code="print(x)", language="python")

        assert result["status"] == "error"
        assert result["exit_code"] == 1
        assert "NameError" in result["stderr"]


@pytest.mark.asyncio
async def test_execute_code_handles_exception():
    """Test execute_code handles unexpected exceptions."""
    from maios.skills.builtin.execute_code import ExecuteCodeSkill

    skill = ExecuteCodeSkill()

    with patch("maios.skills.builtin.execute_code.sandbox_manager") as mock_manager:
        mock_manager.is_healthy.return_value = True
        mock_manager.execute_code = AsyncMock(side_effect=Exception("Docker error"))

        result = await skill.execute(code="print('hello')", language="python")

        assert result["status"] == "error"
        assert "Docker error" in result["error"]


@pytest.mark.asyncio
async def test_execute_code_with_custom_timeout():
    """Test execute_code passes custom timeout to sandbox."""
    from maios.skills.builtin.execute_code import ExecuteCodeSkill
    from maios.sandbox.models import ExecutionResult

    skill = ExecuteCodeSkill()

    mock_result = ExecutionResult(
        exit_code=0,
        stdout="done",
        stderr="",
        duration_ms=5000,
    )

    with patch("maios.skills.builtin.execute_code.sandbox_manager") as mock_manager:
        mock_manager.is_healthy.return_value = True
        mock_manager.execute_code = AsyncMock(return_value=mock_result)

        result = await skill.execute(
            code="import time; time.sleep(5)",
            language="python",
            timeout=60,
        )

        assert result["status"] == "success"

        # Verify timeout was passed
        call_args = mock_manager.execute_code.call_args[0][0]
        assert call_args.timeout_seconds == 60
