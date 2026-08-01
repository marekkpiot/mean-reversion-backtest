from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from src.backtest import (
    compute_strategy_returns,
)

from src.metrics import (
    compute_performance_metrics,
)


PRICES_FILE = "data/prices.csv"
RISK_FILE = "data/risk_positions.csv"

INITIAL_CAPITAL = 10_000.0

TRANSACTION_COST_BPS = 5.0


def load_prices() -> pd.DataFrame:
    prices = pd.read_csv(
        PRICES_FILE,
        index_col=0,
        parse_dates=True,
    )

    return prices.sort_index()


def load_risk_positions() -> pd.DataFrame:
    """
    Charge les positions après gestion du risque.
    """

    risk_results = pd.read_csv(
        RISK_FILE,
        index_col=0,
        parse_dates=True,
    )

    risk_results = risk_results.sort_index()

    if (
        "managed_position"
        not in risk_results.columns
    ):
        raise ValueError(
            "La colonne managed_position "
            "est absente."
        )

    return risk_results


def display_results(
    backtest_results: pd.DataFrame,
) -> None:
    """
    Affiche les principales performances.
    """

    metrics = compute_performance_metrics(
        backtest_results
    )

    gross_final_capital = (
        INITIAL_CAPITAL
        * (
            1.0
            + metrics[
                "gross_total_return"
            ]
        )
    )

    net_final_capital = (
        INITIAL_CAPITAL
        * (
            1.0
            + metrics[
                "net_total_return"
            ]
        )
    )

    cost_impact = (
        gross_final_capital
        - net_final_capital
    )

    print("Résultats du backtest")
    print()

    print(
        f"Capital initial : "
        f"{INITIAL_CAPITAL:.2f} €"
    )

    print(
        f"Capital final avant frais : "
        f"{gross_final_capital:.2f} €"
    )

    print(
        f"Capital final après frais : "
        f"{net_final_capital:.2f} €"
    )

    print(
        f"Impact des frais : "
        f"{cost_impact:.2f} €"
    )

    print()

    print(
        f"Rendement total avant frais : "
        f"{100 * metrics['gross_total_return']:.2f} %"
    )

    print(
        f"Rendement total après frais : "
        f"{100 * metrics['net_total_return']:.2f} %"
    )

    print(
        f"Rendement annualisé : "
        f"{100 * metrics['annualized_return']:.2f} %"
    )

    print(
        f"Volatilité annualisée : "
        f"{100 * metrics['annualized_volatility']:.2f} %"
    )

    print(
        f"Sharpe ratio : "
        f"{metrics['sharpe_ratio']:.3f}"
    )

    print(
        f"Drawdown maximum : "
        f"{100 * metrics['maximum_drawdown']:.2f} %"
    )

    print(
        f"Temps passé en position : "
        f"{100 * metrics['time_in_market']:.2f} %"
    )

    print()

    print(
        "Nombre d'entrées :",
        metrics["number_of_entries"],
    )

    print(
        "Nombre de sorties :",
        metrics["number_of_exits"],
    )


def save_results(
    backtest_results: pd.DataFrame,
) -> None:
    Path("data").mkdir(exist_ok=True)

    backtest_results.to_csv(
        "data/backtest_results.csv",
        index=True,
    )


def plot_equity_curves(
    backtest_results: pd.DataFrame,
) -> None:
    """
    Compare la courbe de capital avant et après frais.
    """

    Path("figures").mkdir(exist_ok=True)

    gross_portfolio_value = (
        INITIAL_CAPITAL
        * backtest_results[
            "gross_equity_curve"
        ]
    )

    net_portfolio_value = (
        INITIAL_CAPITAL
        * backtest_results[
            "equity_curve"
        ]
    )

    plt.figure(figsize=(11, 5))

    plt.plot(
        gross_portfolio_value.index,
        gross_portfolio_value,
        label="Avant frais",
    )

    plt.plot(
        net_portfolio_value.index,
        net_portfolio_value,
        label="Après frais",
    )

    plt.axhline(
        INITIAL_CAPITAL,
        linestyle="--",
        label="Capital initial",
    )

    plt.title(
        "Courbe de capital avant et après frais"
    )

    plt.xlabel("Date")
    plt.ylabel("Valeur du portefeuille (€)")
    plt.grid()
    plt.legend()

    plt.savefig(
        "figures/equity_curve_with_costs.png",
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()


def plot_drawdown(
    backtest_results: pd.DataFrame,
) -> None:
    """
    Trace la perte par rapport au précédent sommet.
    """

    plt.figure(figsize=(11, 5))

    drawdown_percentage = (
        100
        * backtest_results["drawdown"]
    )

    plt.plot(
        drawdown_percentage.index,
        drawdown_percentage,
        label="Drawdown",
    )

    plt.fill_between(
        drawdown_percentage.index,
        drawdown_percentage,
        0.0,
        alpha=0.3,
    )

    plt.axhline(
        0.0,
        linestyle="--",
    )

    plt.title(
        "Drawdown de la stratégie"
    )

    plt.xlabel("Date")
    plt.ylabel("Drawdown (%)")
    plt.grid()
    plt.legend()

    plt.savefig(
        "figures/drawdown.png",
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()


def main() -> None:
    prices = load_prices()
    risk_results = load_risk_positions()

    backtest_results = (
        compute_strategy_returns(
            prices=prices,
            positions=risk_results[
            "managed_position"],
            first_ticker="SPY",
            second_ticker="IVV",
            weight_per_leg=0.5,
            transaction_cost_bps=(
                TRANSACTION_COST_BPS
            ),
        )
    )

    display_results(
        backtest_results
    )

    save_results(
        backtest_results
    )

    plot_equity_curves(
        backtest_results
    )

    plot_drawdown(
        backtest_results
    )

    print()
    print(
        "Résultats enregistrés dans "
        "data/backtest_results.csv"
    )

    print(
        "Graphiques enregistrés dans "
        "figures/equity_curve_with_costs.png "
        "et figures/drawdown.png"
    )


if __name__ == "__main__":
    main()