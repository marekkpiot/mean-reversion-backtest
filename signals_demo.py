from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from src.signals import (
    generate_target_positions,
)


DATA_FILE = "data/spread_zscore.csv"

ENTRY_THRESHOLD = 2.0
EXIT_THRESHOLD = 0.5


def load_spread_results() -> pd.DataFrame:
    """
    Charge le spread et son z-score.
    """

    results = pd.read_csv(
        DATA_FILE,
        index_col=0,
        parse_dates=True,
    )

    results = results.sort_index()

    required_columns = {
        "spread",
        "rolling_mean",
        "rolling_std",
        "zscore",
    }

    missing_columns = (
        required_columns
        - set(results.columns)
    )

    if missing_columns:
        raise ValueError(
            "Colonnes absentes : "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    return results


def add_positions(
    results: pd.DataFrame,
) -> pd.DataFrame:
    """
    Ajoute les positions souhaitées et les positions
    réellement utilisables dans le backtest.
    """

    results = results.copy()

    results["target_position"] = (
        generate_target_positions(
            zscore=results["zscore"],
            entry_threshold=ENTRY_THRESHOLD,
            exit_threshold=EXIT_THRESHOLD,
        )
    )

    # Le signal observé à la clôture du jour t
    # est appliqué à partir du jour suivant.
    results["position"] = (
        results["target_position"]
        .shift(1)
        .fillna(0)
        .astype(int)
    )

    return results


def display_statistics(
    results: pd.DataFrame,
) -> None:
    """
    Affiche quelques informations sur les positions.
    """

    print("Nombre de journées sans position :")

    print(
        (results["position"] == 0).sum()
    )

    print()
    print(
        "Nombre de journées en position longue "
        "sur le spread :"
    )

    print(
        (results["position"] == 1).sum()
    )

    print()
    print(
        "Nombre de journées en position courte "
        "sur le spread :"
    )

    print(
        (results["position"] == -1).sum()
    )

    previous_target_position = (
        results["target_position"]
        .shift(1)
        .fillna(0)
    )

    long_entries = (
        (results["target_position"] == 1)
        & (previous_target_position == 0)
    )

    short_entries = (
        (results["target_position"] == -1)
        & (previous_target_position == 0)
    )

    exits = (
        (results["target_position"] == 0)
        & (previous_target_position != 0)
    )

    print()
    print(
        "Nombre d'entrées longues :",
        long_entries.sum(),
    )

    print(
        "Nombre d'entrées courtes :",
        short_entries.sum(),
    )

    print(
        "Nombre de sorties :",
        exits.sum(),
    )


def save_results(
    results: pd.DataFrame,
) -> None:
    """
    Enregistre les signaux obtenus.
    """

    Path("data").mkdir(exist_ok=True)

    results.to_csv(
        "data/signals.csv",
        index=True,
    )


def plot_trading_signals(
    results: pd.DataFrame,
) -> None:
    """
    Trace le z-score et les points d'entrée et de sortie.
    """

    Path("figures").mkdir(exist_ok=True)

    previous_position = (
        results["target_position"]
        .shift(1)
        .fillna(0)
    )

    long_entries = (
        (results["target_position"] == 1)
        & (previous_position == 0)
    )

    short_entries = (
        (results["target_position"] == -1)
        & (previous_position == 0)
    )

    exits = (
        (results["target_position"] == 0)
        & (previous_position != 0)
    )

    plt.figure(figsize=(11, 6))

    plt.plot(
        results.index,
        results["zscore"],
        label="Z-score",
    )

    plt.axhline(
        ENTRY_THRESHOLD,
        linestyle="--",
        label="Seuil d'entrée supérieur",
    )

    plt.axhline(
        -ENTRY_THRESHOLD,
        linestyle="--",
        label="Seuil d'entrée inférieur",
    )

    plt.axhline(
        EXIT_THRESHOLD,
        linestyle=":",
        label="Zone de sortie",
    )

    plt.axhline(
        -EXIT_THRESHOLD,
        linestyle=":",
    )

    plt.axhline(
        0.0,
        linestyle="-",
    )

    plt.scatter(
        results.index[long_entries],
        results.loc[
            long_entries,
            "zscore",
        ],
        marker="^",
        label="Achat du spread",
    )

    plt.scatter(
        results.index[short_entries],
        results.loc[
            short_entries,
            "zscore",
        ],
        marker="v",
        label="Vente du spread",
    )

    plt.scatter(
        results.index[exits],
        results.loc[
            exits,
            "zscore",
        ],
        marker="x",
        label="Fermeture",
    )

    plt.title(
        "Signaux de trading fondés sur le z-score"
    )

    plt.xlabel("Date")
    plt.ylabel("Z-score")
    plt.grid()
    plt.legend()

    plt.savefig(
        "figures/trading_signals.png",
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()


def plot_positions(
    results: pd.DataFrame,
) -> None:
    """
    Trace la position réellement appliquée.
    """

    plt.figure(figsize=(11, 4))

    plt.step(
        results.index,
        results["position"],
        where="post",
        label="Position",
    )

    plt.axhline(
        0.0,
        linestyle="--",
    )

    plt.yticks(
        [-1, 0, 1],
        [
            "Vente du spread",
            "Aucune position",
            "Achat du spread",
        ],
    )

    plt.title(
        "Positions de la stratégie"
    )

    plt.xlabel("Date")
    plt.ylabel("Position")
    plt.grid()

    plt.savefig(
        "figures/positions.png",
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()


def main() -> None:
    results = load_spread_results()

    results = add_positions(results)

    display_statistics(results)

    save_results(results)

    plot_trading_signals(results)
    plot_positions(results)

    print()
    print(
        "Résultats enregistrés dans "
        "data/signals.csv"
    )

    print(
        "Graphiques enregistrés dans "
        "figures/trading_signals.png "
        "et figures/positions.png"
    )


if __name__ == "__main__":
    main()