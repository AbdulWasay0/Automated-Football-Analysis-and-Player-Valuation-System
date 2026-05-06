"""Rich terminal display helpers."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterable

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .constants import age_label, euro, euro_m


console = Console()


def print_header() -> None:
    console.print(Panel.fit(
        "[bold cyan]FOOTBALL PLAYER INTELLIGENCE SYSTEM[/bold cyan]\n"
        "[white]AI-Powered Valuation & Prediction[/white]",
        border_style="cyan",
        box=box.DOUBLE,
    ))


def print_main_menu() -> None:
    console.print(Panel(
        "[cyan]1.[/cyan] Search Player by Name\n"
        "[cyan]2.[/cyan] Predict Transfer Value\n"
        "[cyan]3.[/cyan] Future Performance Prediction\n"
        "[cyan]4.[/cyan] Advanced Filter & Search\n"
        "[cyan]5.[/cyan] Compare Two Players\n"
        "[cyan]6.[/cyan] Market Insights & Reports\n"
        "[cyan]7.[/cyan] Simulate Player Transfer\n"
        "[cyan]8.[/cyan] Exit",
        title="[bold white]MAIN MENU[/bold white]",
        border_style="cyan",
        box=box.SQUARE,
    ))


def print_error(message: str) -> None:
    console.print(Panel(str(message), title="[bold red]Error[/bold red]", border_style="red"))


def print_success(message: str) -> None:
    console.print(Panel(str(message), title="[bold green]Success[/bold green]", border_style="green"))


@contextmanager
def loading_spinner(text: str):
    console.print(f"[cyan]{text}[/cyan]")
    yield


def player_table(title: str = "Players") -> Table:
    table = Table(title=title, box=box.SIMPLE_HEAVY, border_style="cyan")
    for column in ["#", "Name", "Age", "Club", "Pos", "Goals", "Asst", "Value", "Score"]:
        table.add_column(column, justify="right" if column in {"#", "Age", "Goals", "Asst", "Score"} else "left")
    return table


def print_player_card(player) -> None:
    panel = (
        f"[bold]Name:[/bold]        [yellow]{player.get('name', 'Unknown')}[/yellow]\n"
        f"[bold]Age:[/bold]         {int(player.get('age', 0))} ({age_label(player.get('age', 0))})\n"
        f"[bold]Position:[/bold]    {player.get('sub_position', player.get('position_category', 'Unknown'))}\n"
        f"[bold]Club:[/bold]        {player.get('current_club', 'Unknown')}\n"
        f"[bold]League:[/bold]      {player.get('current_league', 'Unknown')} (Tier {int(player.get('league_tier', 0) or 0)})\n"
        f"[bold]Nationality:[/bold] {player.get('nationality', 'Unknown')}\n\n"
        f"[bold cyan]STATS[/bold cyan]\n"
        f"Goals: {int(player.get('goals_total', 0))} | Assists: {int(player.get('assists_total', 0))}\n"
        f"Goals/90: {float(player.get('goals_per_90', 0)):.2f} | "
        f"Assists/90: {float(player.get('assists_per_90', 0)):.2f}\n"
        f"Minutes: {int(player.get('minutes_played', 0)):,} | Games: {int(player.get('games_played', 0)):,}\n"
        f"Int'l Caps: {int(player.get('international_caps', 0))}\n\n"
        f"[bold cyan]VALUATION[/bold cyan]\n"
        f"Current Value: [bold yellow]{euro(player.get('current_value_eur', 0))}[/bold yellow]\n"
        f"Peak Value:    [bold yellow]{euro(player.get('peak_value_eur', 0))}[/bold yellow]"
    )
    console.print(Panel(panel, title="[bold cyan]PLAYER PROFILE[/bold cyan]", border_style="cyan", box=box.SQUARE))


def print_transfer_result(data: dict) -> None:
    lines = [
        f"[bold]Player:[/bold] {data['player']}",
        f"[bold]From:[/bold]   {data['from_club']}",
        f"[bold]To:[/bold]     {data['to_club']}",
        "",
        f"[bold yellow]PREDICTED TRANSFER FEE: {euro(data['predicted_fee'])}[/bold yellow]",
        "",
        "[bold cyan]BREAKDOWN[/bold cyan]",
    ]
    for key, value in data["breakdown"].items():
        lines.append(f"{key:<26} {value}")
    console.print(Panel("\n".join(lines), title="[bold cyan]TRANSFER VALUATION[/bold cyan]", border_style="cyan", box=box.SQUARE))


def print_filter_results(df, title: str = "SEARCH RESULTS") -> None:
    table = player_table(title)
    for i, (_, row) in enumerate(df.head(20).iterrows(), 1):
        table.add_row(
            str(i), str(row.get("name", ""))[:24], str(int(row.get("age", 0))),
            str(row.get("current_club", ""))[:18], str(row.get("sub_position", row.get("position_category", "")))[:12],
            str(int(row.get("goals_total", 0))), str(int(row.get("assists_total", 0))),
            euro_m(row.get("current_value_eur", 0)), f"{float(row.get('score', 0)):.2f}",
        )
    console.print(table)


def print_comparison_table(p1: dict, p2: dict, verdict: dict) -> None:
    table = Table(title="PLAYER COMPARISON", box=box.SQUARE, border_style="cyan")
    table.add_column("Attribute")
    table.add_column(str(p1.get("name", "Player 1")), style="yellow")
    table.add_column(str(p2.get("name", "Player 2")), style="yellow")
    rows = [
        ("Age", int(p1.get("age", 0)), int(p2.get("age", 0))),
        ("Position", p1.get("sub_position", ""), p2.get("sub_position", "")),
        ("Club", p1.get("current_club", ""), p2.get("current_club", "")),
        ("Goals", int(p1.get("goals_total", 0)), int(p2.get("goals_total", 0))),
        ("Assists", int(p1.get("assists_total", 0)), int(p2.get("assists_total", 0))),
        ("Goals/90", f"{float(p1.get('goals_per_90', 0)):.2f}", f"{float(p2.get('goals_per_90', 0)):.2f}"),
        ("Assists/90", f"{float(p1.get('assists_per_90', 0)):.2f}", f"{float(p2.get('assists_per_90', 0)):.2f}"),
        ("Value", euro_m(p1.get("current_value_eur", 0)), euro_m(p2.get("current_value_eur", 0))),
        ("Peak Value", euro_m(p1.get("peak_value_projection", p1.get("peak_value_eur", 0))), euro_m(p2.get("peak_value_projection", p2.get("peak_value_eur", 0)))),
    ]
    for row in rows:
        table.add_row(str(row[0]), str(row[1]), str(row[2]))
    console.print(table)
    console.print(Panel("\n".join(f"{k}: [green]{v}[/green]" for k, v in verdict.items()), title="VERDICT", border_style="green"))


def print_trajectory_table(player_name: str, rows: Iterable[dict], insights: dict) -> None:
    table = Table(title=f"FUTURE PERFORMANCE TRAJECTORY: {player_name}", box=box.SQUARE, border_style="cyan")
    for column in ["Season", "Age", "Goals", "Assists", "Value"]:
        table.add_column(column)
    for row in rows:
        marker = "  PEAK" if row.get("is_peak") else ""
        table.add_row(str(row["season"]), str(row["age"]), str(row["goals"]), str(row["assists"]), euro_m(row["value"]) + marker)
    console.print(table)
    console.print(Panel("\n".join(f"{k}: [yellow]{v}[/yellow]" for k, v in insights.items()), title="INSIGHTS", border_style="cyan"))
