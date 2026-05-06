"""Feature engineering for transfer fee prediction."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from .constants import (
    CATEGORY_MULTIPLIERS,
    NUMERIC_FEATURES,
    POSITION_MULTIPLIERS,
    TIER_TWO_LEAGUE_CODES,
    TOP_FIVE_LEAGUE_CODES,
    age_factor,
)


def league_tier_factor(tier: float) -> float:
    if tier <= 1:
        return 1.3
    if tier == 2:
        return 1.0
    if tier == 3:
        return 0.8
    return 0.65


def international_factor(caps: float) -> float:
    if caps > 50:
        return 1.30
    if caps >= 20:
        return 1.15
    if caps > 0:
        return 1.05
    return 1.0


def contract_years_left(expiry_year: float) -> float:
    try:
        year = float(expiry_year)
    except (TypeError, ValueError):
        return 2.0
    if year <= 0:
        return 2.0
    return max(0.0, year - date.today().year)


def selling_need_factor(years_left: float) -> float:
    if years_left < 1:
        return 0.85
    if years_left < 2:
        return 0.95
    return 1.05


def detailed_position_multiplier(sub_position: object, category: object) -> float:
    sub = str(sub_position or "")
    cat = str(category or "Midfielder")
    return POSITION_MULTIPLIERS.get(sub, CATEGORY_MULTIPLIERS.get(cat, 1.0))


def performance_factor(row: pd.Series) -> float:
    category = str(row.get("position_category", ""))
    sub = str(row.get("sub_position", ""))
    goals_p90 = float(row.get("goals_per_90", 0) or 0)
    assists_p90 = float(row.get("assists_per_90", 0) or 0)
    if category == "Attacker" or "Forward" in sub or "Winger" in sub:
        if goals_p90 > 0.7:
            return 1.5
        if goals_p90 >= 0.5:
            return 1.2
        if goals_p90 >= 0.3:
            return 1.0
        return 0.7
    if category == "Midfielder":
        if assists_p90 > 0.3:
            return 1.3
        if assists_p90 >= 0.1:
            return 1.1
    return 1.0


def height_factor(row: pd.Series) -> float:
    height = float(row.get("height_cm", 0) or 0)
    sub = str(row.get("sub_position", ""))
    category = str(row.get("position_category", ""))
    if height <= 0:
        return 1.0
    if category == "Goalkeeper":
        return 1.08 if 188 <= height <= 200 else 0.96
    if "Centre-Back" in sub:
        return 1.06 if height >= 185 else 0.96
    return 1.0


def foot_factor(foot: object) -> float:
    text = str(foot or "").lower()
    if "both" in text:
        return 1.08
    if "left" in text:
        return 1.03
    return 1.0


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the dataframe with ML-ready features."""
    result = df.copy()
    for column in [
        "age", "goals_total", "assists_total", "minutes_played", "games_played",
        "international_caps", "current_value_eur", "peak_value_eur", "value_1yr_ago",
        "league_tier", "club_strength_score", "height_cm", "last_transfer_fee",
    ]:
        if column not in result.columns:
            result[column] = 0
        result[column] = pd.to_numeric(result[column], errors="coerce").fillna(0)

    minutes_90 = (result["minutes_played"] / 90).replace(0, np.nan)
    result["goals_per_90"] = (result["goals_total"] / minutes_90).replace([np.inf, -np.inf], 0).fillna(0)
    result["assists_per_90"] = (result["assists_total"] / minutes_90).replace([np.inf, -np.inf], 0).fillna(0)
    result["goal_contribution"] = result["goals_per_90"] + result["assists_per_90"]
    result["age_factor"] = result["age"].apply(age_factor)
    result["position_multiplier"] = result.apply(
        lambda row: detailed_position_multiplier(row.get("sub_position"), row.get("position_category")),
        axis=1,
    )
    result["league_tier_factor"] = result["league_tier"].apply(league_tier_factor)
    result["international_factor"] = result["international_caps"].apply(international_factor)
    result["consistency_score"] = (result["games_played"] / 34).clip(0, 1)
    result["peak_ratio"] = (
        result["current_value_eur"] / result["peak_value_eur"].replace(0, np.nan)
    ).replace([np.inf, -np.inf], 0).fillna(0).clip(0, 2)
    result["log_current_value"] = np.log1p(result["current_value_eur"].clip(lower=0))
    result["age_peak_distance"] = (result["age"] - 26).abs()
    result["contract_years_left"] = result.get("contract_expiry_year", 0).apply(contract_years_left)
    result["selling_club_need"] = result["contract_years_left"].apply(selling_need_factor)
    result["position_scarcity"] = result["sub_position"].astype(str).map({
        "Centre-Forward": 1.25, "Right Winger": 1.18, "Left Winger": 1.18,
        "Defensive Midfield": 1.12, "Attacking Midfield": 1.12,
    }).fillna(1.0)
    result["height_factor"] = result.apply(height_factor, axis=1)
    foot_values = result["foot"] if "foot" in result.columns else pd.Series(["Unknown"] * len(result), index=result.index)
    result["foot_factor"] = foot_values.apply(foot_factor)
    result["nationality_factor"] = np.where(
        (result["current_league_id"] if "current_league_id" in result.columns else pd.Series([""] * len(result), index=result.index)).astype(str).isin(TOP_FIVE_LEAGUE_CODES),
        1.08,
        1.0,
    )
    if "goals_last_season" not in result.columns:
        result["goals_last_season"] = result["goals_total"]
    result["goals_last_season"] = pd.to_numeric(result["goals_last_season"], errors="coerce").fillna(0)
    previous = result["value_1yr_ago"].replace(0, np.nan)
    result["value_trend"] = (
        (result["current_value_eur"] - previous) / previous
    ).replace([np.inf, -np.inf], 0).fillna(0).clip(-1, 3)
    if "transfer_date" in result.columns:
        result["transfer_year"] = pd.to_datetime(result["transfer_date"], errors="coerce").dt.year.fillna(date.today().year)
    else:
        result["transfer_year"] = date.today().year
    result["market_inflation"] = 1.0 + ((result["transfer_year"] - result["transfer_year"].min()).clip(lower=0) * 0.025)
    result["buying_club_premium"] = 1.0
    season_values = result["transfer_season"] if "transfer_season" in result.columns else pd.Series([""] * len(result), index=result.index)
    result["transfer_season_factor"] = np.where(season_values.astype(str).str.contains("winter", case=False, na=False), 0.92, 1.0)
    result["performance_factor"] = result.apply(performance_factor, axis=1)

    for feature in NUMERIC_FEATURES:
        if feature not in result.columns:
            result[feature] = 0
        result[feature] = pd.to_numeric(result[feature], errors="coerce").replace([np.inf, -np.inf], 0).fillna(0)

    return result


def model_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series | None]:
    """Return model features and optional log transfer-fee target."""
    featured = add_features(df)
    x = featured[NUMERIC_FEATURES].copy()
    y = None
    if "transfer_fee" in featured.columns:
        fees = pd.to_numeric(featured["transfer_fee"], errors="coerce").fillna(0)
        y = np.log1p(fees.clip(lower=0))
    elif "last_transfer_fee" in featured.columns:
        fees = pd.to_numeric(featured["last_transfer_fee"], errors="coerce").fillna(0)
        y = np.log1p(fees.clip(lower=0))
    return x, y
