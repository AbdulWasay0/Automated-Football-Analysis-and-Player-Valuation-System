"""Transfer fee prediction logic."""

from __future__ import annotations

import difflib
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .constants import MODEL_PATHS, TOP_CLUBS, euro
from .data_loader import load_data
from .feature_engineering import (
    add_features,
    age_factor,
    international_factor,
    league_tier_factor,
    performance_factor,
    selling_need_factor,
)


def fuzzy_match(value: str, choices: list[str], cutoff: float = 0.55) -> str | None:
    matches = difflib.get_close_matches(value, choices, n=1, cutoff=cutoff)
    return matches[0] if matches else None


def find_player(name: str, df: pd.DataFrame | None = None) -> pd.Series:
    df = df if df is not None else load_data()
    names = df["name"].astype(str).tolist()
    exact = df[df["name"].astype(str).str.lower() == name.lower()]
    if not exact.empty:
        return exact.iloc[0]
    contains = df[df["name"].astype(str).str.contains(name, case=False, na=False, regex=False)]
    if not contains.empty:
        return contains.sort_values("current_value_eur", ascending=False).iloc[0]
    match = fuzzy_match(name, names)
    if match is None:
        suggestions = difflib.get_close_matches(name, names, n=3, cutoff=0.35)
        hint = f" Suggestions: {', '.join(suggestions)}" if suggestions else ""
        raise ValueError(f"Player not found: {name}.{hint}")
    return df[df["name"] == match].iloc[0]


def buying_club_premium(to_club: str) -> float:
    club = str(to_club or "").lower()
    if club in TOP_CLUBS or any(top in club for top in TOP_CLUBS):
        return 1.20
    if any(word in club for word in ["united", "city", "madrid", "barcelona", "milan", "bayern"]):
        return 1.10
    return 1.0


def _formula_prediction(row: pd.Series, to_club: str) -> tuple[float, dict]:
    base = max(float(row.get("current_value_eur", 0) or 0), float(row.get("peak_value_eur", 0) or 0) * 0.35)
    featured = add_features(pd.DataFrame([row])).iloc[0]
    position_mult = float(featured.get("position_multiplier", 1))
    age_mult = age_factor(float(row.get("age", 0) or 0))
    league_mult = league_tier_factor(float(row.get("league_tier", 4) or 4))
    caps_mult = international_factor(float(row.get("international_caps", 0) or 0))
    club_mult = buying_club_premium(to_club)
    perf_mult = performance_factor(featured)
    consistency = 1.1 if float(row.get("games_played", 0) or 0) / 34 > 0.85 else 1.0
    years_left = float(featured.get("contract_years_left", 2) or 2)
    contract_mult = selling_need_factor(years_left)
    # The raw factors are kept visible, but the fallback applies them as weighted
    # premiums. Fully compounding every football premium makes elite players
    # unrealistically expensive before an ML model is trained.
    weighted_premium = (
        (position_mult - 1) * 0.25
        + (age_mult - 1) * 0.40
        + (league_mult - 1) * 0.20
        + (caps_mult - 1) * 0.15
        + (club_mult - 1) * 0.20
        + (perf_mult - 1) * 0.20
        + (consistency - 1) * 0.15
        + (contract_mult - 1) * 0.10
    )
    predicted = base * max(0.35, 1 + weighted_premium)
    breakdown = {
        "Current Value": euro(base),
        "Position Multiplier": f"x{position_mult:.2f}",
        f"Age Factor ({int(row.get('age', 0) or 0)})": f"x{age_mult:.2f}",
        "League Tier Factor": f"x{league_mult:.2f}",
        "Buying Club Premium": f"+{(club_mult - 1) * 100:.0f}%",
        "International Factor": f"x{caps_mult:.2f}",
        "Performance Factor": f"x{perf_mult:.2f}",
        "Contract Urgency": f"x{contract_mult:.2f}",
    }
    return max(0, predicted), breakdown


def _model_key(model: str) -> str:
    return {
        "xgboost": "xgboost",
        "rf": "random_forest",
        "random_forest": "random_forest",
        "nn": "neural_network",
        "neural_network": "neural_network",
    }.get(model, "xgboost")


def _load_model(model: str):
    requested_key = _model_key(model)
    candidates = [requested_key]
    if requested_key == "xgboost":
        candidates.extend(["random_forest", "neural_network"])

    errors = []
    for key in dict.fromkeys(candidates):
        path = MODEL_PATHS[key]
        if not Path(path).exists():
            continue
        try:
            return joblib.load(path), key, errors
        except ModuleNotFoundError as exc:
            errors.append(f"{key} unavailable: missing module '{exc.name}'")
        except Exception as exc:
            errors.append(f"{key} unavailable: {exc}")

    return None, requested_key, errors


def predict_transfer_fee(player_name: str, from_club: str, to_club: str, model: str = "xgboost") -> dict:
    df = load_data()
    player = find_player(player_name, df)
    formula_value, breakdown = _formula_prediction(player, to_club)
    estimator, key, model_errors = _load_model(model)

    predicted = formula_value
    if estimator is not None and MODEL_PATHS["features"].exists():
        try:
            featured = add_features(pd.DataFrame([player]))
            feature_columns = joblib.load(MODEL_PATHS["features"])
            x = featured[feature_columns]
            if key == "neural_network" and MODEL_PATHS["scaler"].exists():
                x = joblib.load(MODEL_PATHS["scaler"]).transform(x)
            ml_pred = float(np.expm1(estimator.predict(x)[0]))
            if ml_pred > 0:
                # Blend ML with pricing factors; pure historical model often underprices star moves.
                predicted = (ml_pred * 0.65) + (formula_value * 0.35)
                breakdown["ML Base Prediction"] = euro(ml_pred)
        except Exception as exc:
            model_errors.append(f"{key} prediction skipped: {exc}")

    breakdown["Model Used"] = key.replace("_", " ").title() if estimator is not None else "Formula Fallback"
    if model_errors:
        breakdown["Model Note"] = "; ".join(model_errors)
    breakdown["TOTAL"] = euro(predicted)
    return {
        "player": str(player.get("name", player_name)),
        "from_club": from_club,
        "to_club": to_club,
        "predicted_fee": predicted,
        "breakdown": breakdown,
        "player_row": player.to_dict(),
    }
