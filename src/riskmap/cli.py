import typer
from rich import print
from rich.table import Table
from rich.console import Console
from .risk_manager import RiskManager
from .risk_scoring import calculate_score
from .control_mapper import ControlMapper
from .register_exporter import export_to_csv, export_to_json
from .pdf_exporter import export_to_pdf

app = typer.Typer(help="📘 RiskMap - Multi-Framework GRC Risk & Control Mapping Tool")
console = Console()
risk_manager = RiskManager()
control_mapper = ControlMapper()

# ---------------------------
# COMMAND: Add Risk
# ---------------------------
@app.command()
def add(
    name: str = typer.Argument(..., help="Risk name"),
    description: str = typer.Option("", "--desc", help="Risk description"),
    likelihood: int = typer.Option(..., "--likelihood", "-l", help="Likelihood (1-5)"),
    impact: int = typer.Option(..., "--impact", "-i", help="Impact (1-5)")
):
    """
    Add a new risk to the risk register.
    """
    risk = risk_manager.add_risk(name, description, likelihood, impact, "soc2")
    
    # Auto-calculate score
    risk.score = calculate_score(risk.likelihood, risk.impact)
    
    # Auto-map controls
    risk.controls = control_mapper.map_controls(risk.name, risk.description, "soc2")
    
    risk_manager.update_risk(risk)

    print(f"[green]Risk added successfully![/green]")
    print(f"ID: {risk.id} | Score: {risk.score} | Controls: {', '.join(risk.controls)}")


# ---------------------------
# COMMAND: List Risks
# ---------------------------
@app.command("list")
def list_risks():
    """
    List all stored risks.
    """
    risks = risk_manager.list_risks()
    if not risks:
        print("[yellow]No risks found.[/yellow]")
        return

    table = Table(title="Risk Register")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Score", style="green")
    table.add_column("Controls", style="blue")

    for risk in risks:
        table.add_row(
            str(risk.id), 
            risk.name, 
            str(risk.score), 
            ", ".join(risk.controls)
        )

    console.print(table)


# ---------------------------
# COMMAND: Score Risk
# ---------------------------
@app.command()
def score(risk_id: int):
    """
    Score a specific risk by ID.
    """
    risk = risk_manager.get_risk(risk_id)
    if not risk:
        print(f"[red]Risk ID {risk_id} not found.[/red]")
        return

    risk.score = calculate_score(risk.likelihood, risk.impact)
    risk_manager.update_risk(risk)
    print(f"[green]Risk {risk_id} scored: {risk.score}[/green]")


# ---------------------------
# COMMAND: Map Controls
# ---------------------------
@app.command("map-controls")
def map_controls(
    risk_id: int
):
    """
    Map controls to a given risk.
    """
    risk = risk_manager.get_risk(risk_id)
    if not risk:
        print(f"[red]Risk ID {risk_id} not found.[/red]")
        return

    controls = control_mapper.map_controls(risk.name, risk.description, "soc2")
    risk.controls = controls
    risk_manager.update_risk(risk)
    
    print(f"[green]Mapped controls for Risk {risk_id}: {', '.join(controls)}[/green]")


# ---------------------------
# COMMAND: Export Risk Register
# ---------------------------
@app.command()
def export(
    format: str = typer.Option("csv", "--format", "-f", help="Export format: csv | json | pdf")
):
    """
    Export the entire risk register in CSV, JSON, or PDF format.
    """
    risks = risk_manager.list_risks()
    if not risks:
        print("[yellow]No risks to export.[/yellow]")
        return

    filename = f"risk_register.{format}"
    if format.lower() == "csv":
        export_to_csv(risks, filename)
    elif format.lower() == "json":
        export_to_json(risks, filename)
    elif format.lower() == "pdf":
        export_to_pdf(risks, filename)
    else:
        print(f"[red]Unsupported format: {format}[/red]")
        return

    print(f"[green]Risk register exported to {filename}[/green]")


# ---------------------------
# COMMAND: Delete Risk
# ---------------------------
@app.command()
def delete(risk_id: int):
    """
    Delete a risk by ID.
    """
    if risk_manager.delete_risk(risk_id):
        print(f"[green]Risk {risk_id} deleted.[/green]")
    else:
        print(f"[red]Risk ID {risk_id} not found.[/red]")
