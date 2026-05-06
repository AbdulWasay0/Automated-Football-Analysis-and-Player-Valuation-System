"""In-session transfer simulation."""

from __future__ import annotations

from rich.panel import Panel

from .constants import euro
from .data_loader import load_data
from .display import console
from .predictor import find_player, predict_transfer_fee


SESSION_PLAYERS = None


def _session_df():
    global SESSION_PLAYERS
    if SESSION_PLAYERS is None:
        SESSION_PLAYERS = load_data().copy()
    return SESSION_PLAYERS


def simulate_transfer(player_name: str, from_club: str, to_club: str, budget: float | None = None) -> dict:
    df = _session_df()
    player = find_player(player_name, df)
    current_club = str(player.get("current_club", ""))
    if from_club and from_club.lower() not in current_club.lower():
        console.print(f"[yellow]Warning:[/yellow] dataset says current club is {current_club}, not {from_club}.")

    result = predict_transfer_fee(player_name, from_club, to_club)
    fee = float(result["predicted_fee"])
    if budget is not None and fee > float(budget) * 1_000_000:
        raise ValueError(f"Transfer exceeds budget. Fee {euro(fee)} vs budget {euro(float(budget) * 1_000_000)}")

    age = int(player.get("age", 0) or 0)
    contract_years = 5 if age <= 24 else 4 if age <= 28 else 3 if age <= 31 else 2
    wages = fee / 260
    old_strength = float(player.get("club_strength_score", 50) or 50)
    new_strength = min(100, old_strength + 2.5)

    df.loc[df["player_id"] == player["player_id"], "current_club"] = to_club

    data = {
        "player": str(player["name"]),
        "from_club": from_club,
        "to_club": to_club,
        "fee": fee,
        "weekly_wages": wages,
        "contract_years": contract_years,
        "from_strength": max(0, old_strength - 1.5),
        "to_strength": new_strength,
    }
    console.print(Panel(
        f"[bold]{data['player']}[/bold] has moved from\n"
        f"{from_club} -> {to_club}\n\n"
        f"Transfer Fee: {euro(fee)}\n"
        f"Contract: {contract_years} years\n"
        f"Weekly Wages: {euro(wages)}/week\n\n"
        f"{from_club} Squad Strength: {old_strength:.1f} -> {data['from_strength']:.1f}\n"
        f"{to_club} Squad Strength: {old_strength:.1f} -> {new_strength:.1f}",
        title="[bold green]TRANSFER CONFIRMED[/bold green]",
        border_style="green",
    ))
    return data

