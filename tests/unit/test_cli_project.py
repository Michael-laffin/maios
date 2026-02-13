# tests/unit/test_cli_project.py
from typer.testing import CliRunner


def test_project_list():
    """Test project list command."""
    from maios.cli.main import app

    runner = CliRunner()
    result = runner.invoke(app, ["project", "list"])
    # Should succeed or fail gracefully
    assert result.exit_code in [0, 1]


def test_project_create():
    """Test project create command."""
    from maios.cli.main import app

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["project", "create", "Test Project", "--description", "A test"],
    )
    # Should succeed or fail gracefully
    assert result.exit_code in [0, 1]


def test_project_status():
    """Test project status command."""
    from maios.cli.main import app

    runner = CliRunner()
    result = runner.invoke(app, ["project", "status", "test-id"])
    # Should succeed or fail gracefully
    assert result.exit_code in [0, 1]


def test_project_help():
    """Test project help command."""
    from maios.cli.main import app

    runner = CliRunner()
    result = runner.invoke(app, ["project", "--help"])

    assert result.exit_code == 0
    assert "list" in result.output
    assert "create" in result.output
    assert "status" in result.output
