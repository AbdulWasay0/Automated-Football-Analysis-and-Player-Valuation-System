"""Future performance and value trajectory prediction."""

from __future__ import annotations

from datetime import date

from .constants import euro_m
from .data_loader import load_data
from .display import print_trajectory_table
from .predictor import find_player


def _curve_multiplier(category: str, age: int) -> float:
    if category == "Goalkeeper":
        if age <= 27:
            return 0.9
        if age <= 33:
            return 1.0
        if age <= 35:
            return 0.82
        return 0.62
    if category == "Defender":
        if age <= 25:
            return 0.88
        if age <= 30:
            return 1.0
        if age <= 32:
            return 0.78
        return 0.58
    if category == "Midfielder":
        if age <= 22:
            return 0.82
        if age <= 29:
            return 1.0
        if age <= 32:
            return 0.76
        return 0.55
    if age <= 22:
        return 0.75
    if age <= 27:
        return 1.0
    if age <= 29:
        return 0.88
    if age <= 32:
        return 0.72
    return 0.55


def _value_growth(category: str, age: int) -> float:
    if age <= 22:
        return 1.17
    if age <= 27:
        return 1.08
    if category == "Goalkeeper" and age <= 33:
        return 1.02
    if category == "Defender" and age <= 30:
        return 1.03
    if age <= 30:
        return 0.93
    return 0.82


def predict_future_performance(player_name: str, seasons_ahead: int = 6) -> tuple[list[dict], dict]:
    player = find_player(player_name, load_data())
    category = str(player.get("position_category", "Midfielder"))
    current_age = int(player.get("age", 0) or 0)
    goals = max(float(player.get("goals_last_season", player.get("goals_total", 0)) or 0), float(player.get("goals_per_90", 0) or 0) * 25)
    assists = max(float(player.get("assists_last_season", player.get("assists_total", 0)) or 0), float(player.get("assists_per_90", 0) or 0) * 25)
    value = float(player.get("current_value_eur", 0) or 0)

    rows = []
    for i in range(int(seasons_ahead)):
        age = current_age + i
        season_start = date.today().year + i
        perf = _curve_multiplier(category, age)
        if i > 0:
            value *= _value_growth(category, age)
        rows.append({
            "season": f"{season_start}/{str(season_start + 1)[-2:]}",
            "age": age,
            "goals": round(goals * perf),
            "assists": round(assists * perf),
            "value": value,
            "is_peak": False,
        })

    peak = max(rows, key=lambda row: row["value"])
    peak["is_peak"] = True
    decline = next((row["age"] for row in rows if row["value"] < peak["value"] * 0.92 and row["age"] > peak["age"]), "Not in range")
    insights = {
        "Peak Performance": f"Age {peak['age']}",
        "Peak Value": f"Age {peak['age']} ({euro_m(peak['value'])})",
        "Decline Begins": decline,
        "Best Time to Buy": "Now" if current_age < peak["age"] else "Only at discount",
    }
    print_trajectory_table(str(player.get("name", player_name)), rows, insights)
    return rows, insights

