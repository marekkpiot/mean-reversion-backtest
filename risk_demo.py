from pathlib import Path

import pandas as pd

from src.risk import (
    apply_risk_management,
)


PRICES_FILE = "data/prices.csv"
SIGNALS_FILE = "data/signals.csv"

STOP_LOSS = 0.005
MAX_ABS_POSITION = 1.0


def load_prices() -> pd.DataFrame:
    """
    Charge les prix historiques.
    """

    prices = pd.read_csv(
        PRICES_FILE,
        index_col=0,
        parse_dates=True,
    )

    return prices.sort_index()


def load_signals() -> pd.DataFrame:
    """
    Charge les positions calculées à partir du z-score.
    """

    signals = pd.read_csv(
        SIGNALS_FILE,
        index_col=0,
        parse_dates=True,
    )

    signals = signals.sort_index()

    if "position" not in signals.columns:
        raise ValueError(
            "La colonne position est absente."
        )

    return signals


def display_results(
    risk_results: pd.DataFrame,
) -> None:
    """
    Affiche les effets de la gestion du risque.
    """

    number_of_stops = int(
        risk_results[
            "stop_loss_triggered"
        ].sum()
    )

    days_before_risk_management = int(
        (
            risk_results[
                "desired_position"
            ]
            != 0
        ).sum()
    )

    days_after_risk_management = int(
        (
            risk_results[
                "managed_position"
            ]
            != 0
        ).sum()
    )

    print("Gestion du risque")
    print()

    print(
        f"Stop-loss : "
        f"{100 * STOP_LOSS:.2f} %"
    )

    print(
        f"Position maximale : "
        f"{MAX_ABS_POSITION:.1f}"
    )

    print()

    print(
        "Nombre de stop-loss déclenchés :",
        number_of_stops,
    )

    print(
        "Journées en position avant gestion :",
        days_before_risk_management,
    )

    print(
        "Journées en position après gestion :",
        days_after_risk_management,
    )

    if number_of_stops > 0:
        print()
        print("Dates de déclenchement :")

        triggered_rows = risk_results.loc[
            risk_results[
                "stop_loss_triggered"
            ],
            [
                "desired_position",
                "managed_position",
                "trade_cumulative_return",
            ],
        ]

        print(triggered_rows)


def save_results(
    risk_results: pd.DataFrame,
) -> None:
    """
    Enregistre les positions après gestion du risque.
    """

    Path("data").mkdir(exist_ok=True)

    risk_results.to_csv(
        "data/risk_positions.csv",
        index=True,
    )


def main() -> None:
    prices = load_prices()
    signals = load_signals()

    risk_results = apply_risk_management(
        prices=prices,
        desired_positions=signals["position"],
        first_ticker="SPY",
        second_ticker="IVV",
        weight_per_leg=0.5,
        stop_loss=STOP_LOSS,
        max_abs_position=MAX_ABS_POSITION,
    )

    display_results(risk_results)

    save_results(risk_results)

    print()
    print(
        "Résultats enregistrés dans "
        "data/risk_positions.csv"
    )


if __name__ == "__main__":
    main()