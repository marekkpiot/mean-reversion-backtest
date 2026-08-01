from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from src.spread import (
    compute_log_ratio_spread,
    compute_rolling_zscore,
)


DATA_FILE = "data/prices.csv"
ROLLING_WINDOW = 20


def load_prices() -> pd.DataFrame:
    """
    Charge les prix précédemment enregistrés.
    """

    prices = pd.read_csv(
        DATA_FILE,
        index_col=0,
        parse_dates=True,
    )

    prices = prices.sort_index()

    return prices


def save_results(
    results: pd.DataFrame,
) -> None:
    """
    Enregistre le spread et le z-score.
    """

    Path("data").mkdir(exist_ok=True)

    results.to_csv(
        "data/spread_zscore.csv",
        index=True,
    )


def plot_spread(
    results: pd.DataFrame,
) -> None:
    """
    Trace le spread et sa moyenne glissante.
    """

    Path("figures").mkdir(exist_ok=True)

    plt.figure(figsize=(10, 5))

    plt.plot(
        results.index,
        results["spread"],
        label="Spread logarithmique",
    )

    plt.plot(
        results.index,
        results["rolling_mean"],
        linestyle="--",
        label="Moyenne glissante",
    )

    plt.title(
        "Spread logarithmique entre SPY et IVV"
    )

    plt.xlabel("Date")
    plt.ylabel("Spread")
    plt.grid()
    plt.legend()

    plt.savefig(
        "figures/spread.png",
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()


def plot_zscore(
    results: pd.DataFrame,
) -> None:
    """
    Trace le z-score du spread.
    """

    plt.figure(figsize=(10, 5))

    plt.plot(
        results.index,
        results["zscore"],
        label="Z-score",
    )

    plt.axhline(
        0.0,
        linestyle="-",
        label="Niveau normal",
    )

    plt.axhline(
        2.0,
        linestyle="--",
        label="Seuil supérieur",
    )

    plt.axhline(
        -2.0,
        linestyle="--",
        label="Seuil inférieur",
    )

    plt.title(
        "Z-score glissant du spread SPY / IVV"
    )

    plt.xlabel("Date")
    plt.ylabel("Z-score")
    plt.grid()
    plt.legend()

    plt.savefig(
        "figures/zscore.png",
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()


def main() -> None:
    prices = load_prices()

    spread = compute_log_ratio_spread(
        prices=prices,
        first_ticker="SPY",
        second_ticker="IVV",
    )

    results = compute_rolling_zscore(
        spread=spread,
        window=ROLLING_WINDOW,
    )

    print("Premières lignes :")
    print(results.head(25))

    print()
    print("Dernières lignes :")
    print(results.tail())

    print()
    print(
        "Nombre de z-scores disponibles :",
        results["zscore"].notna().sum(),
    )

    print()
    print(
        "Z-score minimal :",
        results["zscore"].min(),
    )

    print(
        "Z-score maximal :",
        results["zscore"].max(),
    )

    save_results(results)

    plot_spread(results)
    plot_zscore(results)

    print()
    print(
        "Résultats enregistrés dans "
        "data/spread_zscore.csv"
    )

    print(
        "Graphiques enregistrés dans "
        "figures/spread.png et "
        "figures/zscore.png"
    )


if __name__ == "__main__":
    main()