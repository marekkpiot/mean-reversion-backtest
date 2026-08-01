import numpy as np
import pandas as pd


def compute_log_ratio_spread(
    prices: pd.DataFrame,
    first_ticker: str = "SPY",
    second_ticker: str = "IVV",
) -> pd.Series:
    """
    Calcule le logarithme du ratio entre deux actifs.

    spread = log(prix du premier actif)
             - log(prix du second actif)

    Ce qui est équivalent à :

    spread = log(
        prix du premier actif
        / prix du second actif
    )
    """

    required_columns = {
        first_ticker,
        second_ticker,
    }

    missing_columns = (
        required_columns
        - set(prices.columns)
    )

    if missing_columns:
        raise ValueError(
            "Colonnes absentes : "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    if (
        prices[
            [first_ticker, second_ticker]
        ]
        <= 0
    ).any().any():
        raise ValueError(
            "Tous les prix doivent être "
            "strictement positifs."
        )

    spread = (
        np.log(prices[first_ticker])
        - np.log(prices[second_ticker])
    )

    spread.name = "spread"

    return spread


def compute_rolling_zscore(
    spread: pd.Series,
    window: int = 20,
) -> pd.DataFrame:
    """
    Calcule la moyenne, l'écart-type et le z-score
    glissants d'un spread.

    z-score =
        (spread - moyenne glissante)
        / écart-type glissant
    """

    if window < 2:
        raise ValueError(
            "La fenêtre doit contenir "
            "au moins deux observations."
        )

    rolling_mean = spread.rolling(
        window=window,
        min_periods=window,
    ).mean()

    rolling_standard_deviation = (
        spread.rolling(
            window=window,
            min_periods=window,
        ).std()
    )

    zscore = (
        spread - rolling_mean
    ) / rolling_standard_deviation

    # Si l'écart-type vaut zéro,
    # le z-score ne peut pas être calculé.
    zscore = zscore.where(
        rolling_standard_deviation > 0
    )

    results = pd.DataFrame(
        {
            "spread": spread,
            "rolling_mean": rolling_mean,
            "rolling_std": (
                rolling_standard_deviation
            ),
            "zscore": zscore,
        }
    )

    return results