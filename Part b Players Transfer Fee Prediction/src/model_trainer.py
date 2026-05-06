"""Train transfer fee regression models."""

from __future__ import annotations

import math

import joblib
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

from .constants import MODEL_PATHS, MODELS_DIR, NUMERIC_FEATURES
from .data_loader import load_transfers
from .display import console
from .feature_engineering import add_features, model_matrix

try:
    from xgboost import XGBRegressor
except Exception:  # pragma: no cover - depends on local installation
    XGBRegressor = None


def _metrics(name: str, y_true_log, y_pred_log) -> dict:
    y_true = np.expm1(y_true_log)
    y_pred = np.expm1(y_pred_log).clip(min=0)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = math.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true_log, y_pred_log)
    mape = np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1))) * 100
    return {"model": name, "mae": mae, "rmse": rmse, "r2": r2, "mape": mape}


def train_all(force: bool = False) -> list[dict]:
    """Train and persist XGBoost/fallback, Random Forest, MLP, scaler, and feature list."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    if not force and all(MODEL_PATHS[k].exists() for k in ["xgboost", "random_forest", "neural_network", "scaler", "features"]):
        return []

    transfers = load_transfers(force_rebuild=force)
    transfers = transfers[pd_to_numeric(transfers.get("transfer_fee", 0)) > 0].copy()
    if len(transfers) < 50:
        raise RuntimeError("Not enough paid transfer rows to train models.")

    featured = add_features(transfers)
    x, y = model_matrix(featured)
    valid = y.notna() & np.isfinite(y) & (y > 0)
    x, y = x[valid], y[valid]

    stratify = None
    if "position_category" in featured.columns:
        cats = featured.loc[valid, "position_category"].astype(str)
        if cats.value_counts().min() >= 2:
            stratify = cats

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=stratify
    )

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    if XGBRegressor is not None:
        primary = XGBRegressor(
            n_estimators=500,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=42,
            n_jobs=-1,
        )
        primary_name = "XGBoost"
    else:
        primary = HistGradientBoostingRegressor(max_iter=500, learning_rate=0.05, max_leaf_nodes=31, random_state=42)
        primary_name = "HistGradientBoosting fallback"
    primary.fit(x_train, y_train)

    rf = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1)
    rf.fit(x_train, y_train)

    nn = MLPRegressor(
        hidden_layer_sizes=(256, 128, 64),
        activation="relu",
        max_iter=500,
        early_stopping=True,
        random_state=42,
    )
    nn.fit(x_train_scaled, y_train)

    joblib.dump(primary, MODEL_PATHS["xgboost"])
    joblib.dump(rf, MODEL_PATHS["random_forest"])
    joblib.dump(nn, MODEL_PATHS["neural_network"])
    joblib.dump(scaler, MODEL_PATHS["scaler"])
    joblib.dump(NUMERIC_FEATURES, MODEL_PATHS["features"])

    metrics = [
        _metrics(primary_name, y_test, primary.predict(x_test)),
        _metrics("Random Forest", y_test, rf.predict(x_test)),
        _metrics("Neural Network", y_test, nn.predict(x_test_scaled)),
    ]

    console.print("[bold cyan]Model evaluation[/bold cyan]")
    for item in metrics:
        console.print(
            f"{item['model']}: MAE €{item['mae']:,.0f} | RMSE €{item['rmse']:,.0f} | "
            f"R² {item['r2']:.3f} | MAPE {item['mape']:.1f}%"
        )

    if hasattr(primary, "feature_importances_"):
        importances = sorted(zip(NUMERIC_FEATURES, primary.feature_importances_), key=lambda x: x[1], reverse=True)[:10]
        console.print("[bold cyan]Top 10 XGBoost features[/bold cyan]")
        for feature, importance in importances:
            console.print(f"{feature}: {importance:.4f}")

    return metrics


def pd_to_numeric(series):
    import pandas as pd

    return pd.to_numeric(series, errors="coerce").fillna(0)
