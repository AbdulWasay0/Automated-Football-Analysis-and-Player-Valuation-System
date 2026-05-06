"""Side-by-side player comparison."""

from __future__ import annotations

from .data_loader import load_data
from .display import print_comparison_table
from .predictor import find_player


def _peak_projection(player) -> float:
    value = float(player.get("current_value_eur", 0) or 0)
    age = float(player.get("age", 0) or 0)
    if age <= 22:
        return value * 1.45
    if age <= 27:
        return value * 1.2
    if age <= 30:
        return value * 0.95
    return value * 0.7


def compare_players(player1_name: str, player2_name: str) -> dict:
    df = load_data()
    p1 = find_player(player1_name, df).to_dict()
    p2 = find_player(player2_name, df).to_dict()
    p1["peak_value_projection"] = _peak_projection(p1)
    p2["peak_value_projection"] = _peak_projection(p2)

    verdict = {
        "Better current value": p1["name"] if p1.get("current_value_eur", 0) >= p2.get("current_value_eur", 0) else p2["name"],
        "Higher potential": p1["name"] if p1["peak_value_projection"] >= p2["peak_value_projection"] else p2["name"],
        "Better playmaker": p1["name"] if p1.get("assists_per_90", 0) >= p2.get("assists_per_90", 0) else p2["name"],
        "Better scorer": p1["name"] if p1.get("goals_per_90", 0) >= p2.get("goals_per_90", 0) else p2["name"],
        "Best buy": p1["name"] if (p1["peak_value_projection"] / max(p1.get("current_value_eur", 1), 1)) >= (p2["peak_value_projection"] / max(p2.get("current_value_eur", 1), 1)) else p2["name"],
    }
    print_comparison_table(p1, p2, verdict)
    return verdict

