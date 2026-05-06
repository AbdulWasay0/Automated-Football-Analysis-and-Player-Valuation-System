# Football Player Intelligence System

CLI application for football player search, transfer fee prediction, future trajectory projection, player comparison, market reports, and in-session transfer simulation.

## Dataset

Use the Transfermarkt Kaggle dataset:

https://www.kaggle.com/datasets/davidcariboo/player-scores

This project supports either location:

- `csv_files/`, which already exists in this folder
- `data/raw/`, as described in the original specification

Required files:

- `players.csv`
- `clubs.csv`
- `competitions.csv`
- `appearances.csv`
- `transfers.csv`
- `player_valuations.csv`
- `games.csv`
- `club_games.csv`
- `game_events.csv`
- `game_lineups.csv`
- `countries.csv`
- `national_teams.csv`

## Setup

Use Python 3.10 or 3.11.

```bash
python setup.py
```

If you do not want to train models immediately, run:

```bash
pip install -r requirements.txt
python main.py
```

The app can still predict fees with the rule-based fallback until trained models exist.

## Run

```bash
python main.py
```

## Features

1. Search Player by Name
2. Predict Transfer Value
3. Future Performance Prediction
4. Advanced Filter & Search
5. Compare Two Players
6. Market Insights & Reports
7. Simulate Player Transfer

## Model Notes

The model target is `log1p(transfer_fee)`, converted back with `expm1`.

Trained models:

- XGBoost Regressor primary model when XGBoost is installed
- Random Forest Regressor
- MLPRegressor Neural Network

If XGBoost is unavailable, the project saves a scikit-learn gradient boosting fallback under the same model path so the CLI remains usable.
