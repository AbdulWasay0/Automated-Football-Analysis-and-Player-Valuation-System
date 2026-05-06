"""Player search and advanced filtering."""

from __future__ import annotations

import pandas as pd

from .constants import age_factor
from .data_loader import load_data
from .display import print_filter_results, print_player_card
from .feature_engineering import add_features
from .predictor import find_player


def search_player(name: str) -> dict:
    df = load_data()
    player = find_player(name, df)
    print_player_card(player)
    return player.to_dict()


def advanced_filter(
    budget_m: float | None = None,
    max_age: int | None = None,
    position: str = "Any",
    min_goals: int = 0,
    min_assists: int = 0,
    league: str = "Any",
    min_goals_per_90: float | None = None,
    nationality: str | None = None,
    foot: str = "Any",
    min_caps: int | None = None,
    sort_by: str = "score",
) -> pd.DataFrame:
    df = add_features(load_data())
    result = df.copy()
    if budget_m is not None:
        result = result[result["current_value_eur"] <= float(budget_m) * 1_000_000]
    if max_age is not None:
        result = result[result["age"] <= int(max_age)]
    if position and position.lower() != "any":
        result = result[result["position_category"].astype(str).str.lower() == position.lower()]
    if min_goals:
        result = result[result["goals_total"] >= int(min_goals)]
    if min_assists:
        result = result[result["assists_total"] >= int(min_assists)]
    if league and league.lower() != "any":
        result = result[result["current_league"].astype(str).str.contains(league, case=False, na=False)]
    if min_goals_per_90 is not None:
        result = result[result["goals_per_90"] >= float(min_goals_per_90)]
    if nationality:
        result = result[result["nationality"].astype(str).str.contains(nationality, case=False, na=False)]
    if foot and foot.lower() != "any":
        result = result[result["foot"].astype(str).str.contains(foot, case=False, na=False)]
    if min_caps is not None:
        result = result[result["international_caps"] >= int(min_caps)]

    if result.empty:
        print_filter_results(result, "No players found")
        return result

    value_for_money = result["goal_contribution"] / (result["current_value_eur"] / 1_000_000 + 1)
    result["score"] = (
        result["goals_per_90"].clip(0, 2) * 0.3
        + value_for_money.clip(0, 2) * 0.3
        + result["age"].apply(age_factor) * 0.2
        + result["consistency_score"] * 0.2
    ) * 10

    sort_map = {
        "value": "current_value_eur",
        "goals": "goals_total",
        "age": "age",
        "score": "score",
    }
    column = sort_map.get(sort_by.lower(), "score")
    ascending = column == "age"
    result = result.sort_values(column, ascending=ascending)
    print_filter_results(result, f"SEARCH RESULTS ({len(result)} players found)")
    return result

