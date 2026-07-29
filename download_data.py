from pathlib import Path

import matplotlib

# Empêche l'erreur d'affichage graphique rencontrée
# précédemment sous Windows.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf


TICKERS = ["SPY", "IVV"]

START_DATE = "2020-01-01"
END_DATE = "2026-01-01"


def download_close_prices() -> pd.DataFrame:
    """
    Télécharge les prix de clôture ajustés de SPY et IVV.

    Returns
    -------
    prices:
        DataFrame dont chaque colonne correspond à un actif
        et chaque ligne à une date.
    """

    raw_data = yf.download(
        tickers=TICKERS,
        start=START_DATE,
        end=END_DATE,
        interval="1d",
        auto_adjust=True,
        progress=False,
    )

    if raw_data.empty:
        raise RuntimeError(
            "Aucune donnée n'a été téléchargée."
        )

    if "Close" not in raw_data.columns:
        raise RuntimeError(
            "La colonne Close est absente des données."
        )

    prices = raw_data["Close"].copy()

    # Sécurité au cas où une seule série serait renvoyée.
    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    missing_tickers = [
        ticker
        for ticker in TICKERS
        if ticker not in prices.columns
    ]

    if missing_tickers:
        raise RuntimeError(
            "Données absentes pour : "
            + ", ".join(missing_tickers)
        )

    prices = prices[TICKERS]

    prices = prices.sort_index()

    return prices


def inspect_and_clean_prices(
    prices: pd.DataFrame,
) -> pd.DataFrame:
    """
    Affiche des contrôles simples et supprime les lignes
    contenant des valeurs manquantes.
    """

    print("Premières lignes :")
    print(prices.head())

    print()
    print("Dernières lignes :")
    print(prices.tail())

    print()
    print("Dimensions avant nettoyage :")
    print(prices.shape)

    print()
    print("Valeurs manquantes par actif :")
    print(prices.isna().sum())

    duplicate_dates = (
        prices.index.duplicated().sum()
    )

    print()
    print(
        "Nombre de dates dupliquées :",
        duplicate_dates,
    )

    cleaned_prices = (
        prices
        .loc[~prices.index.duplicated()]
        .dropna(how="any")
    )

    print()
    print("Dimensions après nettoyage :")
    print(cleaned_prices.shape)

    if cleaned_prices.empty:
        raise RuntimeError(
            "Il ne reste aucune donnée après nettoyage."
        )

    return cleaned_prices


def save_prices(
    prices: pd.DataFrame,
) -> None:
    """
    Enregistre les prix nettoyés dans un fichier CSV.
    """

    Path("data").mkdir(exist_ok=True)

    prices.to_csv(
        "data/prices.csv",
        index=True,
    )

    print()
    print(
        "Données enregistrées dans "
        "data/prices.csv"
    )


def plot_normalized_prices(
    prices: pd.DataFrame,
) -> None:
    """
    Trace les deux séries en les faisant commencer à 100.
    """

    Path("figures").mkdir(exist_ok=True)

    normalized_prices = (
        100.0
        * prices
        / prices.iloc[0]
    )

    plt.figure(figsize=(10, 5))

    for ticker in TICKERS:
        plt.plot(
            normalized_prices.index,
            normalized_prices[ticker],
            label=ticker,
        )

    plt.title(
        "Évolution normalisée de SPY et IVV"
    )

    plt.xlabel("Date")
    plt.ylabel("Valeur normalisée, base 100")
    plt.grid()
    plt.legend()

    plt.savefig(
        "figures/normalized_prices.png",
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()

    print(
        "Graphique enregistré dans "
        "figures/normalized_prices.png"
    )


def main() -> None:
    prices = download_close_prices()

    cleaned_prices = inspect_and_clean_prices(
        prices
    )

    save_prices(cleaned_prices)

    plot_normalized_prices(
        cleaned_prices
    )


if __name__ == "__main__":
    main()