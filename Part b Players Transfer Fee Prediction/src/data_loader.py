"""Load Transfermarkt CSV files and build enriched player/transfer datasets."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .constants import (
    CSV_FILES_DIR,
    NUMERIC_FEATURES,
    PLAYERS_ENRICHED_PATH,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    TIER_TWO_LEAGUE_CODES,
    TOP_FIVE_LEAGUE_CODES,
    TRANSFERS_ENRICHED_PATH,
    position_category,
)


REQUIRED_FILES = {
    "players.csv", "clubs.csv", "competitions.csv", "appearances.csv",
    "transfers.csv", "player_valuations.csv", "games.csv", "club_games.csv",
    "game_events.csv", "game_lineups.csv", "countries.csv", "national_teams.csv",
}


def find_data_dir() -> Path:
    """Return the first dataset directory that contains the required CSV files."""
    for candidate in (RAW_DATA_DIR, CSV_FILES_DIR):
        if candidate.exists() and all((candidate / name).exists() for name in REQUIRED_FILES):
            return candidate
    return RAW_DATA_DIR


def _read_csv(data_dir: Path, filename: str, usecols: Iterable[str] | None = None) -> pd.DataFrame:
    path = data_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    try:
        return pd.read_csv(path, usecols=usecols, low_memory=False)
    except ValueError:
        return pd.read_csv(path, low_memory=False)


def _age_from_dob(series: pd.Series) -> pd.Series:
    dob = pd.to_datetime(series, errors="coerce")
    today = pd.Timestamp(date.today())
    return ((today - dob).dt.days / 365.25).round().fillna(0).astype(int)


def _league_tier(competition_id: object, sub_type: object = None) -> int:
    code = str(competition_id or "")
    subtype = str(sub_type or "").lower()
    if code in TOP_FIVE_LEAGUE_CODES or subtype == "first_tier":
        return 1
    if code in TIER_TWO_LEAGUE_CODES or subtype == "second_tier":
        return 2
    if "third" in subtype:
        return 3
    return 4


def _club_strength(clubs: pd.DataFrame) -> pd.DataFrame:
    clubs = clubs.copy()
    for column in ["stadium_seats", "national_team_players", "squad_size", "average_age"]:
        if column not in clubs.columns:
            clubs[column] = 0
        clubs[column] = pd.to_numeric(clubs[column], errors="coerce").fillna(0)
    seats = clubs["stadium_seats"]
    national = clubs["national_team_players"]
    seat_score = 100 * (seats - seats.min()) / max(1, seats.max() - seats.min())
    national_score = 100 * (national - national.min()) / max(1, national.max() - national.min())
    clubs["club_strength_score"] = (seat_score * 0.55 + national_score * 0.45).clip(0, 100)
    return clubs[[
        "club_id", "name", "domestic_competition_id", "squad_size", "average_age",
        "national_team_players", "stadium_seats", "club_strength_score",
    ]].rename(columns={"name": "club_name"})


def _normalised_score(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce").fillna(0)
    spread = numeric.max() - numeric.min()
    if spread <= 0:
        return pd.Series(0.0, index=series.index)
    score = 100 * (numeric - numeric.min()) / spread
    if not higher_is_better:
        score = 100 - score
    return score.fillna(0)


def _club_form(club_games: pd.DataFrame) -> pd.DataFrame:
    data = club_games.copy()
    for column in ["own_goals", "opponent_goals", "own_position", "is_win"]:
        if column not in data.columns:
            data[column] = 0
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data["points"] = np.where(data["is_win"].fillna(0) > 0, 3, np.where(data["own_goals"] == data["opponent_goals"], 1, 0))
    data["goal_diff"] = data["own_goals"].fillna(0) - data["opponent_goals"].fillna(0)
    form = data.groupby("club_id", as_index=False).agg(
        club_win_rate=("is_win", "mean"),
        club_goal_diff_per_game=("goal_diff", "mean"),
        club_points_per_game=("points", "mean"),
        club_avg_position=("own_position", "mean"),
    )
    for column in ["club_win_rate", "club_goal_diff_per_game", "club_points_per_game", "club_avg_position"]:
        form[column] = pd.to_numeric(form[column], errors="coerce").fillna(0)
    return form


def _country_context(countries: pd.DataFrame) -> pd.DataFrame:
    data = countries.copy()
    data["confederation"] = data.get("confederation", "").astype(str).str.lower()
    data["confederation_strength"] = data["confederation"].map({
        "europa": 1.20,
        "europe": 1.20,
        "sudamerika": 1.15,
        "south america": 1.15,
        "afrika": 1.00,
        "africa": 1.00,
        "asien": 0.92,
        "asia": 0.92,
        "nord- und mittelamerika": 0.95,
        "north america": 0.95,
        "oceania": 0.85,
        "ozeanien": 0.85,
    }).fillna(1.0)
    return data[["country_name", "total_clubs", "total_players", "average_age", "confederation_strength"]].rename(columns={
        "country_name": "nationality",
        "total_clubs": "country_total_clubs",
        "total_players": "country_total_players",
        "average_age": "country_average_age",
    })


def _national_team_context(national_teams: pd.DataFrame) -> pd.DataFrame:
    data = national_teams.copy()
    for column in ["squad_size", "total_market_value", "fifa_ranking"]:
        if column not in data.columns:
            data[column] = 0
        data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0)
    market_score = _normalised_score(data["total_market_value"], higher_is_better=True)
    ranking_score = _normalised_score(data["fifa_ranking"].replace(0, np.nan), higher_is_better=False)
    data["national_team_strength_score"] = (market_score * 0.65 + ranking_score * 0.35).fillna(0)
    return data[[
        "national_team_id", "squad_size", "total_market_value",
        "fifa_ranking", "national_team_strength_score",
    ]].rename(columns={
        "national_team_id": "current_national_team_id",
        "squad_size": "national_team_squad_size",
        "total_market_value": "national_team_market_value",
        "fifa_ranking": "national_team_fifa_ranking",
    })


def _appearance_game_context(appearances: pd.DataFrame, games: pd.DataFrame) -> pd.DataFrame:
    game_lookup = games[["game_id", "attendance", "competition_type"]].copy()
    game_lookup["attendance"] = pd.to_numeric(game_lookup["attendance"], errors="coerce").fillna(0)
    merged = appearances[["player_id", "game_id"]].merge(game_lookup, on="game_id", how="left")
    competition_type = merged["competition_type"].astype(str).str.lower()
    merged["domestic_game"] = competition_type.str.contains("domestic", na=False).astype(int)
    merged["international_game"] = competition_type.str.contains("international|national_team", regex=True, na=False).astype(int)
    grouped = merged.groupby("player_id", as_index=False).agg(
        avg_match_attendance=("attendance", "mean"),
        max_match_attendance=("attendance", "max"),
        domestic_games=("domestic_game", "sum"),
        international_games=("international_game", "sum"),
        contextual_games=("game_id", "nunique"),
    )
    denom = grouped["contextual_games"].replace(0, np.nan)
    grouped["domestic_game_share"] = (grouped["domestic_games"] / denom).fillna(0)
    grouped["international_game_share"] = (grouped["international_games"] / denom).fillna(0)
    return grouped[[
        "player_id", "avg_match_attendance", "max_match_attendance",
        "domestic_game_share", "international_game_share",
    ]]


def _lineup_context(lineups: pd.DataFrame) -> pd.DataFrame:
    data = lineups.copy()
    lineup_type = data.get("type", "").astype(str).str.lower()
    data["lineup_start"] = (lineup_type == "starting_lineup").astype(int)
    data["lineup_sub"] = (lineup_type == "substitutes").astype(int)
    data["captain"] = pd.to_numeric(data.get("team_captain", 0), errors="coerce").fillna(0)
    grouped = data.groupby("player_id", as_index=False).agg(
        lineup_starts=("lineup_start", "sum"),
        lineup_subs=("lineup_sub", "sum"),
        captain_appearances=("captain", "sum"),
        lineup_rows=("game_id", "nunique"),
    )
    grouped["captaincy_rate"] = (grouped["captain_appearances"] / grouped["lineup_rows"].replace(0, np.nan)).fillna(0)
    return grouped[["player_id", "lineup_starts", "lineup_subs", "captain_appearances", "captaincy_rate"]]


def _event_context(events: pd.DataFrame) -> pd.DataFrame:
    data = events.copy()
    event_type = data.get("type", "").astype(str).str.lower()
    data["event_count"] = 1
    data["event_goal_count"] = event_type.str.contains("goal", na=False).astype(int)
    data["event_card_count"] = event_type.str.contains("card", na=False).astype(int)
    data["event_substitution_count"] = event_type.str.contains("substitution", na=False).astype(int)
    grouped = data.groupby("player_id", as_index=False).agg(
        event_count=("event_count", "sum"),
        event_goal_count=("event_goal_count", "sum"),
        event_card_count=("event_card_count", "sum"),
        event_substitution_count=("event_substitution_count", "sum"),
    )
    assists = (
        data.dropna(subset=["player_assist_id"])
        .assign(player_id=lambda frame: pd.to_numeric(frame["player_assist_id"], errors="coerce"))
        .dropna(subset=["player_id"])
        .groupby("player_id", as_index=False)
        .size()
        .rename(columns={"size": "event_assist_count"})
    )
    grouped["player_id"] = pd.to_numeric(grouped["player_id"], errors="coerce")
    return grouped.merge(assists, on="player_id", how="left").fillna({"event_assist_count": 0})


def build_enriched_data(force: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build and save enriched player and transfer datasets."""
    if not force and PLAYERS_ENRICHED_PATH.exists() and TRANSFERS_ENRICHED_PATH.exists():
        return pd.read_csv(PLAYERS_ENRICHED_PATH), pd.read_csv(TRANSFERS_ENRICHED_PATH)

    data_dir = find_data_dir()
    missing = [name for name in REQUIRED_FILES if not (data_dir / name).exists()]
    if missing:
        raise FileNotFoundError(
            "CSV files are missing. Put the Transfermarkt Kaggle CSV files in "
            f"{RAW_DATA_DIR} or {CSV_FILES_DIR}. Missing: {', '.join(missing)}"
        )

    players = _read_csv(data_dir, "players.csv")
    clubs = _club_strength(_read_csv(data_dir, "clubs.csv"))
    clubs = clubs.merge(_club_form(_read_csv(data_dir, "club_games.csv")), on="club_id", how="left")
    competitions = _read_csv(data_dir, "competitions.csv")
    appearances = _read_csv(data_dir, "appearances.csv")
    transfers = _read_csv(data_dir, "transfers.csv")
    valuations = _read_csv(data_dir, "player_valuations.csv")
    games = _read_csv(data_dir, "games.csv", usecols=["game_id", "attendance", "competition_type"])
    countries = _country_context(_read_csv(data_dir, "countries.csv"))
    national_teams = _national_team_context(_read_csv(data_dir, "national_teams.csv"))
    lineups = _lineup_context(_read_csv(
        data_dir,
        "game_lineups.csv",
        usecols=["game_id", "player_id", "type", "team_captain"],
    ))
    events = _event_context(_read_csv(
        data_dir,
        "game_events.csv",
        usecols=["player_id", "player_assist_id", "type"],
    ))

    base = players.copy()
    base["age"] = _age_from_dob(base.get("date_of_birth"))
    base["position_category"] = [
        position_category(pos, sub)
        for pos, sub in zip(base.get("position", ""), base.get("sub_position", ""))
    ]
    base = base.rename(columns={
        "height_in_cm": "height_cm",
        "country_of_citizenship": "nationality",
        "current_club_name": "current_club",
        "current_club_domestic_competition_id": "current_league_id",
        "market_value_in_eur": "current_value_eur",
        "highest_market_value_in_eur": "peak_value_eur",
    })

    appearances["date"] = pd.to_datetime(appearances["date"], errors="coerce")
    max_year = int(appearances["date"].dt.year.max()) if appearances["date"].notna().any() else date.today().year
    apps_all = appearances.groupby("player_id", as_index=False).agg(
        goals_total=("goals", "sum"),
        assists_total=("assists", "sum"),
        yellow_cards=("yellow_cards", "sum"),
        red_cards=("red_cards", "sum"),
        minutes_played=("minutes_played", "sum"),
        games_played=("game_id", "nunique"),
    )
    apps_last = (
        appearances[appearances["date"].dt.year == max_year]
        .groupby("player_id", as_index=False)
        .agg(goals_last_season=("goals", "sum"), assists_last_season=("assists", "sum"))
    )
    game_context = _appearance_game_context(appearances, games)

    valuations["date"] = pd.to_datetime(valuations["date"], errors="coerce")
    valuations["market_value_in_eur"] = pd.to_numeric(valuations["market_value_in_eur"], errors="coerce")
    val_latest = (
        valuations.sort_values("date")
        .groupby("player_id", as_index=False)
        .tail(1)[["player_id", "market_value_in_eur"]]
        .rename(columns={"market_value_in_eur": "latest_value_from_history"})
    )
    val_peak = (
        valuations.groupby("player_id", as_index=False)["market_value_in_eur"].max()
        .rename(columns={"market_value_in_eur": "peak_value_from_history"})
    )
    cutoff = valuations["date"].max() - pd.DateOffset(years=1) if valuations["date"].notna().any() else pd.Timestamp(date.today())
    val_1yr = (
        valuations[valuations["date"] <= cutoff].sort_values("date")
        .groupby("player_id", as_index=False)
        .tail(1)[["player_id", "market_value_in_eur"]]
        .rename(columns={"market_value_in_eur": "value_1yr_ago"})
    )

    transfers["transfer_date"] = pd.to_datetime(transfers["transfer_date"], errors="coerce")
    transfers["transfer_fee"] = pd.to_numeric(transfers["transfer_fee"], errors="coerce").fillna(0)
    transfers["market_value_in_eur"] = pd.to_numeric(transfers["market_value_in_eur"], errors="coerce").fillna(0)
    last_transfer = (
        transfers.sort_values("transfer_date")
        .groupby("player_id", as_index=False)
        .tail(1)[[
            "player_id", "transfer_date", "transfer_season", "from_club_id", "to_club_id",
            "from_club_name", "to_club_name", "transfer_fee", "market_value_in_eur",
        ]]
        .rename(columns={
            "transfer_fee": "last_transfer_fee",
            "market_value_in_eur": "transfer_market_value_eur",
        })
    )

    competitions["league_tier"] = competitions.apply(
        lambda row: _league_tier(row.get("competition_id"), row.get("sub_type")),
        axis=1,
    )
    comp_lookup = competitions[[
        "competition_id", "name", "country_name", "league_tier",
    ]].rename(columns={
        "competition_id": "current_league_id",
        "name": "current_league",
    })

    enriched = (
        base.merge(apps_all, on="player_id", how="left")
        .merge(apps_last, on="player_id", how="left")
        .merge(game_context, on="player_id", how="left")
        .merge(lineups, on="player_id", how="left")
        .merge(events, on="player_id", how="left")
        .merge(val_latest, on="player_id", how="left")
        .merge(val_peak, on="player_id", how="left")
        .merge(val_1yr, on="player_id", how="left")
        .merge(last_transfer, on="player_id", how="left")
        .merge(clubs, left_on="current_club_id", right_on="club_id", how="left")
        .merge(comp_lookup, on="current_league_id", how="left")
        .merge(countries, on="nationality", how="left")
        .merge(national_teams, on="current_national_team_id", how="left")
    )

    enriched["current_value_eur"] = pd.to_numeric(enriched.get("current_value_eur"), errors="coerce")
    enriched["current_value_eur"] = enriched["current_value_eur"].fillna(enriched["latest_value_from_history"]).fillna(0)
    enriched["peak_value_eur"] = pd.to_numeric(enriched.get("peak_value_eur"), errors="coerce")
    enriched["peak_value_eur"] = enriched["peak_value_eur"].fillna(enriched["peak_value_from_history"]).fillna(enriched["current_value_eur"]).fillna(0)
    enriched["height_cm"] = pd.to_numeric(enriched.get("height_cm"), errors="coerce")
    enriched["international_caps"] = pd.to_numeric(enriched.get("international_caps"), errors="coerce").fillna(0)
    enriched["contract_expiry_year"] = pd.to_datetime(enriched.get("contract_expiration_date"), errors="coerce").dt.year

    numeric_defaults = [
        "goals_total", "assists_total", "yellow_cards", "red_cards", "minutes_played",
        "games_played", "goals_last_season", "assists_last_season", "last_transfer_fee",
        "club_strength_score", "league_tier", "value_1yr_ago",
    ]
    numeric_defaults.extend([column for column in NUMERIC_FEATURES if column not in numeric_defaults])
    for column in numeric_defaults:
        if column not in enriched.columns:
            enriched[column] = 0
        enriched[column] = pd.to_numeric(enriched[column], errors="coerce").fillna(0)

    minutes_90 = (enriched["minutes_played"] / 90).replace(0, np.nan)
    enriched["goals_per_90"] = (enriched["goals_total"] / minutes_90).replace([np.inf, -np.inf], 0).fillna(0)
    enriched["assists_per_90"] = (enriched["assists_total"] / minutes_90).replace([np.inf, -np.inf], 0).fillna(0)

    wanted = [
        "player_id", "name", "age", "position", "sub_position", "position_category",
        "height_cm", "foot", "nationality", "current_club", "current_club_id",
        "current_league", "current_league_id", "league_tier", "goals_total",
        "assists_total", "goals_per_90", "assists_per_90", "minutes_played",
        "games_played", "yellow_cards", "red_cards", "international_caps",
        "current_value_eur", "peak_value_eur", "value_1yr_ago", "last_transfer_fee",
        "from_club_name", "to_club_name", "transfer_date", "transfer_season",
        "club_strength_score", "contract_expiry_year", "goals_last_season",
        "assists_last_season",
    ]
    wanted.extend([column for column in NUMERIC_FEATURES if column not in wanted])
    for column in wanted:
        if column not in enriched.columns:
            enriched[column] = np.nan
    enriched = enriched[wanted]
    enriched = impute_missing(enriched)

    transfer_feature_columns = [
        "player_id", "age", "position", "sub_position", "position_category",
        "current_value_eur", "peak_value_eur", "goals_per_90", "assists_per_90",
        "international_caps", "league_tier", "club_strength_score",
        "games_played", "minutes_played", "contract_expiry_year",
    ]
    transfer_feature_columns.extend([
        column for column in NUMERIC_FEATURES
        if column in enriched.columns and column not in transfer_feature_columns
    ])
    transfers_enriched = transfers.merge(
        enriched[transfer_feature_columns],
        on="player_id",
        how="left",
    )
    transfers_enriched = impute_missing(transfers_enriched)

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(PLAYERS_ENRICHED_PATH, index=False)
    transfers_enriched.to_csv(TRANSFERS_ENRICHED_PATH, index=False)
    return enriched, transfers_enriched


def impute_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Impute numeric columns by position-group median where possible."""
    result = df.copy()
    numeric_cols = result.select_dtypes(include=["number"]).columns
    if "position_category" in result.columns:
        for column in numeric_cols:
            result[column] = result[column].fillna(
                result.groupby("position_category")[column].transform("median")
            )
    for column in numeric_cols:
        result[column] = result[column].fillna(result[column].median()).fillna(0)
    for column in result.select_dtypes(exclude=["number"]).columns:
        result[column] = result[column].fillna("Unknown")
    return result


def load_data(force_rebuild: bool = False) -> pd.DataFrame:
    """Load the enriched player dataset, building it if needed."""
    players, _ = build_enriched_data(force=force_rebuild)
    return players


def load_transfers(force_rebuild: bool = False) -> pd.DataFrame:
    """Load the enriched transfer dataset, building it if needed."""
    _, transfers = build_enriched_data(force=force_rebuild)
    return transfers
