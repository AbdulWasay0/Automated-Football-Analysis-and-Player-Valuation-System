"""Shared constants and pricing rules for the CLI application."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_FILES_DIR = PROJECT_ROOT / "csv_files"
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

PLAYERS_ENRICHED_PATH = PROCESSED_DATA_DIR / "players_enriched.csv"
TRANSFERS_ENRICHED_PATH = PROCESSED_DATA_DIR / "transfers_enriched.csv"

MODEL_PATHS = {
    "xgboost": MODELS_DIR / "xgboost_transfer_model.pkl",
    "random_forest": MODELS_DIR / "rf_transfer_model.pkl",
    "neural_network": MODELS_DIR / "nn_transfer_model.pkl",
    "scaler": MODELS_DIR / "scaler.pkl",
    "features": MODELS_DIR / "feature_columns.pkl",
}

TOP_CLUBS = {
    "real madrid", "manchester city", "man city", "fc barcelona", "barcelona",
    "bayern munich", "paris saint-germain", "psg", "liverpool", "arsenal",
    "chelsea", "manchester united", "man united", "tottenham hotspur",
    "juventus", "inter milan", "ac milan", "atletico madrid", "borussia dortmund",
}

TOP_FIVE_LEAGUE_CODES = {"GB1", "ES1", "L1", "IT1", "FR1"}
TIER_TWO_LEAGUE_CODES = {"GB2", "NL1", "PO1", "BE1", "TR1", "RU1", "SC1"}

POSITION_MULTIPLIERS = {
    "Centre-Forward": 1.6,
    "Second Striker": 1.45,
    "Left Winger": 1.4,
    "Right Winger": 1.4,
    "Attacking Midfield": 1.3,
    "Central Midfield": 1.1,
    "Defensive Midfield": 1.1,
    "Left Midfield": 1.15,
    "Right Midfield": 1.15,
    "Left-Back": 1.0,
    "Right-Back": 1.0,
    "Centre-Back": 0.95,
    "Goalkeeper": 0.85,
}

CATEGORY_MULTIPLIERS = {
    "Attacker": 1.5,
    "Midfielder": 1.2,
    "Defender": 1.0,
    "Goalkeeper": 0.9,
}

NUMERIC_FEATURES = [
    "age", "height_cm", "goals_total", "assists_total", "goals_per_90",
    "assists_per_90", "goal_contribution", "minutes_played", "games_played",
    "yellow_cards", "red_cards", "international_caps", "current_value_eur",
    "peak_value_eur", "club_strength_score", "league_tier", "age_factor",
    "position_multiplier", "league_tier_factor", "international_factor",
    "consistency_score", "peak_ratio", "log_current_value", "age_peak_distance",
    "contract_years_left", "position_scarcity", "height_factor", "foot_factor",
    "nationality_factor", "goals_last_season", "value_trend", "transfer_year",
    "market_inflation", "buying_club_premium", "selling_club_need",
    "transfer_season_factor", "performance_factor", "country_total_clubs",
    "country_total_players", "country_average_age", "confederation_strength",
    "national_team_squad_size", "national_team_market_value",
    "national_team_fifa_ranking", "national_team_strength_score",
    "avg_match_attendance", "max_match_attendance", "domestic_game_share",
    "international_game_share", "lineup_starts", "lineup_subs",
    "captain_appearances", "captaincy_rate", "event_count",
    "event_goal_count", "event_card_count", "event_substitution_count",
    "event_assist_count", "club_win_rate", "club_goal_diff_per_game",
    "club_points_per_game", "club_avg_position",
]


def position_category(position: str | float | None, sub_position: str | float | None = None) -> str:
    text = f"{position or ''} {sub_position or ''}".lower()
    if "goalkeeper" in text:
        return "Goalkeeper"
    if any(token in text for token in ["attack", "winger", "forward", "striker"]):
        return "Attacker"
    if "midfield" in text:
        return "Midfielder"
    if any(token in text for token in ["defence", "defender", "back", "centre-back", "center-back"]):
        return "Defender"
    return "Midfielder"


def age_factor(age: float) -> float:
    if age <= 0:
        return 0.75
    if 18 <= age <= 22:
        return 0.85
    if 23 <= age <= 27:
        return 1.0
    if 28 <= age <= 30:
        return 0.8
    if 31 <= age <= 32:
        return 0.65
    if age >= 33:
        return 0.45
    return 0.75


def age_label(age: float) -> str:
    if age <= 22:
        return "Rising"
    if age <= 27:
        return "Prime"
    if age <= 32:
        return "Declining"
    return "Sharp Drop"


def euro(value: float | int | None) -> str:
    try:
        amount = float(value or 0)
    except (TypeError, ValueError):
        amount = 0.0
    return f"€{amount:,.0f}"


def euro_m(value: float | int | None) -> str:
    try:
        amount = float(value or 0)
    except (TypeError, ValueError):
        amount = 0.0
    return f"€{amount / 1_000_000:.1f}M"
