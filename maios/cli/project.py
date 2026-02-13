from typing import Optional
import httpx
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Project management commands")
console = Console()
API_BASE = "http://localhost:8000/api"


@app.command("list")
def list_projects():
    """List all projects."""
    try:
        response = httpx.get(f"{API_BASE}/projects")
        response.raise_for_status()
        projects = response.json()

        if not projects:
            console.print("[yellow]No projects found[/yellow]")
            return

        table = Table(title="Projects")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Phase", style="magenta")

        for p in projects:
            table.add_row(
                str(p["id"])[:8],
                p["name"],
                p["status"],
                p.get("orchestrator_phase", "N/A"),
            )

        console.print(table)
    except httpx.ConnectError:
        console.print("[red]Error: Cannot connect to MAIOS server[/red]")
        console.print("[yellow]Make sure the server is running: maios server[/yellow]")
        raise typer.Exit(1)


@app.command("create")
def create_project(
    name: str = typer.Argument(..., help="Project name"),
    description: Optional[str] = typer.Option(None, "--description", "-d"),
    request: Optional[str] = typer.Option(None, "--request", "-r"),
):
    """Create a new project."""
    payload = {"name": name}
    if description:
        payload["description"] = description
    if request:
        payload["initial_request"] = request

    try:
        response = httpx.post(f"{API_BASE}/projects", json=payload)
        response.raise_for_status()
        project = response.json()

        console.print(f"[green]Created project:[/green] {project['name']}")
        console.print(f"[cyan]ID:[/cyan] {project['id']}")
    except httpx.ConnectError:
        console.print("[red]Error: Cannot connect to MAIOS server[/red]")
        raise typer.Exit(1)


@app.command("status")
def project_status(
    project_id: str = typer.Argument(..., help="Project ID"),
):
    """Show project status."""
    try:
        response = httpx.get(f"{API_BASE}/projects/{project_id}")
        response.raise_for_status()
        project = response.json()

        console.print(f"[bold]{project['name']}[/bold]")
        console.print(f"Status: [yellow]{project['status']}[/yellow]")
        console.print(f"Phase: [magenta]{project['orchestrator_phase']}[/magenta]")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            console.print("[red]Project not found[/red]")
        raise typer.Exit(1)
    except httpx.ConnectError:
        console.print("[red]Error: Cannot connect to MAIOS server[/red]")
        raise typer.Exit(1)
