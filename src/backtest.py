import pandas as pd


def compute_asset_returns(
    prices: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calcule les rendements quotidiens des actifs.

    rendement(t)
    =
    prix(t) / prix(t-1) - 1
    """

    if prices.empty:
        raise ValueError(
            "Le tableau de prix est vide."
        )

    if prices.shape[1] < 2:
        raise ValueError(
            "Il faut au moins deux actifs."
        )

    if (prices <= 0).any().any():
        raise ValueError(
            "Tous les prix doivent être positifs."
        )

    asset_returns = prices.pct_change()

    asset_returns.columns = [
        f"{column}_return"
        for column in prices.columns
    ]

    return asset_returns


def compute_strategy_returns(
    prices: pd.DataFrame,
    positions: pd.Series,
    first_ticker: str = "SPY",
    second_ticker: str = "IVV",
    weight_per_leg: float = 0.5,
    transaction_cost_bps: float = 5.0,
) -> pd.DataFrame:
    """
    Calcule les rendements d'une stratégie de pair trading.

    Le résultat contient les rendements avant et après
    frais de transaction.
    """

    if first_ticker not in prices.columns:
        raise ValueError(
            f"La colonne {first_ticker} est absente."
        )

    if second_ticker not in prices.columns:
        raise ValueError(
            f"La colonne {second_ticker} est absente."
        )

    if weight_per_leg <= 0:
        raise ValueError(
            "Le poids de chaque jambe doit être positif."
        )

    if transaction_cost_bps < 0:
        raise ValueError(
            "Les frais ne peuvent pas être négatifs."
        )

    asset_returns = compute_asset_returns(
        prices[
            [
                first_ticker,
                second_ticker,
            ]
        ]
    )

    combined_data = pd.concat(
        [
            asset_returns,
            positions.rename("position"),
        ],
        axis=1,
        join="inner",
    )

    combined_data["position"] = (
        combined_data["position"]
        .fillna(0)
        .astype(float)
    )

    first_return_column = (
        f"{first_ticker}_return"
    )

    second_return_column = (
        f"{second_ticker}_return"
    )

    # Rendement d'une position longue sur le spread :
    # long SPY et short IVV.
    combined_data["spread_return"] = (
        combined_data[first_return_column]
        - combined_data[second_return_column]
    )

    # Rendement avant frais.
    combined_data["gross_strategy_return"] = (
        weight_per_leg
        * combined_data["position"]
        * combined_data["spread_return"]
    )

    combined_data["gross_strategy_return"] = (
        combined_data["gross_strategy_return"]
        .fillna(0.0)
    )

    # Position détenue la veille.
    previous_position = (
        combined_data["position"]
        .shift(1)
        .fillna(0.0)
    )

    # Importance du changement de position.
    combined_data["position_change"] = (
        combined_data["position"]
        - previous_position
    ).abs()

    # Montant total échangé, relativement au capital.
    #
    # Exemple :
    # passage de 0 à +1
    # => achat de 50 % de SPY
    # => vente de 50 % d'IVV
    # => turnover total = 100 %.
    combined_data["turnover"] = (
        2.0
        * weight_per_leg
        * combined_data["position_change"]
    )

    # Conversion des points de base en taux décimal.
    transaction_cost_rate = (
        transaction_cost_bps / 10_000.0
    )

    combined_data["transaction_cost"] = (
        transaction_cost_rate
        * combined_data["turnover"]
    )

    # Rendement réellement conservé après les frais.
    combined_data["strategy_return"] = (
        combined_data["gross_strategy_return"]
        - combined_data["transaction_cost"]
    )

    # Courbe de capital avant frais.
    combined_data["gross_equity_curve"] = (
        1.0
        + combined_data["gross_strategy_return"]
    ).cumprod()

    # Courbe de capital après frais.
    combined_data["equity_curve"] = (
        1.0
        + combined_data["strategy_return"]
    ).cumprod()

    combined_data["cumulative_return"] = (
        combined_data["equity_curve"]
        - 1.0
    )

    # Plus haut niveau atteint jusqu'à chaque date.
    combined_data["running_maximum"] = (
        combined_data["equity_curve"]
        .cummax()
    )

    # Perte par rapport au précédent sommet.
    combined_data["drawdown"] = (
        combined_data["equity_curve"]
        / combined_data["running_maximum"]
        - 1.0
    )

    return combined_data