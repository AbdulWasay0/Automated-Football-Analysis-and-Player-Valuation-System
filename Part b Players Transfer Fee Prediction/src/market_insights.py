"""Market insight reports."""

from __future__ import annotations

import pandas as pd
from rich import box
from rich.panel import Panel
from rich.table import Table

from .constants import euro_m
from .data_loader import load_data, load_transfers
from .display import console
from .feature_engineering import add_features


def generate_market_insights() -> dict:
    players = add_features(load_data())
    transfers = load_transfers()

    avg_by_position = players.groupby("position_category")["current_value_eur"].mean().sort_values(ascending=False)
    top_players = players.sort_values("current_value_eur", ascending=False).head(10)
    age_curve = players.assign(age_bucket=pd.cut(players["age"], [0, 22, 28, 32, 99], labels=["18-22 Rising", "23-28 Peak", "29-32 Declining", "33+ Sharp drop"]))
    age_curve = age_curve.groupby("age_bucket", observed=True)["current_value_eur"].mean()

    players["rule_value"] = (
        players["current_value_eur"] * players["position_multiplier"] * players["age_factor"]
        * players["league_tier_factor"] * players["international_factor"] * players["performance_factor"]
    )
    undervalued = players[players["current_value_eur"] > 0].copy()
    undervalued["gap_pct"] = ((undervalued["rule_value"] - undervalued["current_value_eur"]) / undervalued["current_value_eur"]) * 100
    undervalued = undervalued.sort_values("gap_pct", ascending=False).head(5)

    transfers["transfer_fee"] = pd.to_numeric(transfers.get("transfer_fee", 0), errors="coerce").fillna(0)
    spenders = transfers.groupby("to_club_name")["transfer_fee"].sum().sort_values(ascending=False).head(10)
    sellers = transfers.groupby("from_club_name")["transfer_fee"].sum().sort_values(ascending=False).head(10)
    most_transferred = transfers.groupby("player_name")["player_id"].count().sort_values(ascending=False).head(10)

    table = Table(title="MARKET INSIGHTS", box=box.SQUARE, border_style="cyan")
    table.add_column("Section", style="cyan")
    table.add_column("Insight")
    table.add_row("Average Value by Position", "\n".join(f"{idx}: {euro_m(val)}" for idx, val in avg_by_position.items()))
    table.add_row("Value vs Age Curve", "\n".join(f"{idx}: {euro_m(val)}" for idx, val in age_curve.items()))
    table.add_row("Most Expensive Players", "\n".join(f"{i}. {r['name']} - {euro_m(r['current_value_eur'])}" for i, r in enumerate(top_players.to_dict("records"), 1)))
    table.add_row("Most Undervalued", "\n".join(f"{r['name']} - Pred {euro_m(r['rule_value'])}, Actual {euro_m(r['current_value_eur'])}" for r in undervalued.to_dict("records")))
    table.add_row("Top Spending Clubs", "\n".join(f"{club}: {euro_m(value)}" for club, value in spenders.items()))
    table.add_row("Most Transferred", "\n".join(f"{name}: {count} transfers" for name, count in most_transferred.items()))
    console.print(table)

    return {
        "avg_by_position": avg_by_position,
        "age_curve": age_curve,
        "top_players": top_players,
        "undervalued": undervalued,
        "spenders": spenders,
        "sellers": sellers,
        "most_transferred": most_transferred,
    }
