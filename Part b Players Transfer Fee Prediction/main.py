from __future__ import annotations

import traceback

from rich.prompt import Confirm, IntPrompt, Prompt

from src.constants import MODEL_PATHS
from src.data_loader import load_data
from src.display import console, loading_spinner, print_error, print_header, print_main_menu, print_success
from src.market_insights import generate_market_insights
from src.model_trainer import train_all
from src.performance_predictor import predict_future_performance
from src.player_compare import compare_players
from src.player_search import advanced_filter, search_player
from src.predictor import predict_transfer_fee
from src.transfer_simulator import simulate_transfer


def startup() -> None:
    print_header()
    with loading_spinner("Loading dataset..."):
        players = load_data()
    console.print(f"[green]Dataset ready:[/green] {len(players):,} players loaded.")

    required = ["xgboost", "random_forest", "neural_network", "scaler"]
    missing_models = [MODEL_PATHS[key] for key in required if not MODEL_PATHS[key].exists()]
    if missing_models:
        console.print("[yellow]Models are not trained yet.[/yellow]")
        if Confirm.ask("Train models now? This can take several minutes", default=False):
            with loading_spinner("Training transfer fee models..."):
                train_all()
        else:
            console.print("[yellow]Continuing with rule-based fallback predictions until models are trained.[/yellow]")


def pause() -> None:
    Prompt.ask("\nPress Enter to return to main menu", default="")


def menu_search() -> None:
    name = Prompt.ask("Enter player name")
    search_player(name)


def menu_predict() -> None:
    player = Prompt.ask("Enter player name")
    from_club = Prompt.ask("From club")
    to_club = Prompt.ask("To club")
    model = Prompt.ask("Model", choices=["xgboost", "random_forest", "neural_network"], default="xgboost")
    from src.display import print_transfer_result

    print_transfer_result(predict_transfer_fee(player, from_club, to_club, model=model))


def menu_future() -> None:
    player = Prompt.ask("Enter player name")
    seasons = IntPrompt.ask("Seasons ahead", default=6)
    predict_future_performance(player, seasons)


def menu_filter() -> None:
    budget = Prompt.ask("Budget max in EUR millions (blank for any)", default="")
    max_age = Prompt.ask("Max age (blank for any)", default="")
    position = Prompt.ask("Position", choices=["Attacker", "Midfielder", "Defender", "Goalkeeper", "Any"], default="Any")
    min_goals = IntPrompt.ask("Minimum goals", default=0)
    min_assists = IntPrompt.ask("Minimum assists", default=0)
    league = Prompt.ask("League (blank/Any for any)", default="Any")
    nationality = Prompt.ask("Nationality (blank for any)", default="")
    foot = Prompt.ask("Foot", choices=["Left", "Right", "Both", "Any"], default="Any")
    sort_by = Prompt.ask("Sort by", choices=["score", "value", "goals", "age"], default="score")
    advanced_filter(
        budget_m=float(budget) if budget else None,
        max_age=int(max_age) if max_age else None,
        position=position,
        min_goals=min_goals,
        min_assists=min_assists,
        league=league,
        nationality=nationality or None,
        foot=foot,
        sort_by=sort_by,
    )


def menu_compare() -> None:
    player1 = Prompt.ask("Player 1")
    player2 = Prompt.ask("Player 2")
    compare_players(player1, player2)


def menu_simulate() -> None:
    player = Prompt.ask("Enter player name")
    from_club = Prompt.ask("From club")
    to_club = Prompt.ask("To club")
    budget = Prompt.ask("Budget in EUR millions (blank to skip)", default="")
    simulate_transfer(player, from_club, to_club, float(budget) if budget else None)


def main() -> None:
    try:
        startup()
    except Exception as exc:
        print_error(f"Startup failed: {exc}")
        console.print_exception(show_locals=False)
        return

    actions = {
        1: menu_search,
        2: menu_predict,
        3: menu_future,
        4: menu_filter,
        5: menu_compare,
        6: generate_market_insights,
        7: menu_simulate,
    }

    while True:
        print_main_menu()
        choice = IntPrompt.ask("Enter choice", default=8)
        if choice == 8:
            print_success("Goodbye.")
            break
        action = actions.get(choice)
        if action is None:
            print_error("Invalid menu choice. Enter a number from 1 to 8.")
            continue
        try:
            action()
        except KeyboardInterrupt:
            print_error("Operation cancelled.")
        except Exception as exc:
            print_error(str(exc))
            if Confirm.ask("Show technical traceback?", default=False):
                console.print(traceback.format_exc())
        pause()


if __name__ == "__main__":
    main()
