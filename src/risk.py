import pandas as pd


def apply_risk_management(
    prices: pd.DataFrame,
    desired_positions: pd.Series,
    first_ticker: str = "SPY",
    second_ticker: str = "IVV",
    weight_per_leg: float = 0.5,
    stop_loss: float = 0.005,
    max_abs_position: float = 1.0,
) -> pd.DataFrame:
    """
    Applique une limite de position et un stop-loss.

    stop_loss = 0.005 signifie que la position est fermée
    lorsque sa perte cumulée atteint environ 0,5 % du capital.

    Le stop-loss est vérifié à la fin de chaque journée.
    La fermeture devient donc effective le jour suivant.
    """

    required_tickers = {
        first_ticker,
        second_ticker,
    }

    missing_tickers = (
        required_tickers
        - set(prices.columns)
    )

    if missing_tickers:
        raise ValueError(
            "Prix absents pour : "
            + ", ".join(
                sorted(missing_tickers)
            )
        )

    if stop_loss <= 0:
        raise ValueError(
            "Le stop-loss doit être strictement positif."
        )

    if not 0 < max_abs_position <= 1:
        raise ValueError(
            "La limite de position doit être "
            "comprise entre 0 et 1."
        )

    if weight_per_leg <= 0:
        raise ValueError(
            "Le poids de chaque jambe doit être positif."
        )

    # Rendements quotidiens de SPY et IVV.
    asset_returns = (
        prices[
            [
                first_ticker,
                second_ticker,
            ]
        ]
        .pct_change()
    )

    # Rendement d'une position longue sur le spread.
    spread_return = (
        asset_returns[first_ticker]
        - asset_returns[second_ticker]
    )

    spread_return.name = "spread_return"

    # On regroupe les rendements et les positions
    # sur les dates communes.
    results = pd.concat(
        [
            spread_return,
            desired_positions.rename(
                "desired_position"
            ),
        ],
        axis=1,
        join="inner",
    ).sort_index()

    results["desired_position"] = (
        results["desired_position"]
        .fillna(0.0)
        .astype(float)
    )

    # Limite explicitement les positions.
    results["limited_position"] = (
        results["desired_position"]
        .clip(
            lower=-max_abs_position,
            upper=max_abs_position,
        )
    )

    managed_positions = pd.Series(
        0.0,
        index=results.index,
        name="managed_position",
    )

    trade_cumulative_returns = pd.Series(
        0.0,
        index=results.index,
        name="trade_cumulative_return",
    )

    stop_loss_triggered = pd.Series(
        False,
        index=results.index,
        name="stop_loss_triggered",
    )

    current_position = 0.0

    # Valeur du capital consacré au trade.
    # Il commence à 1 au début de chaque position.
    trade_equity = 1.0

    # Après un stop, on empêche une réentrée immédiate
    # tant que le signal initial n'est pas revenu à zéro.
    blocked_after_stop = False

    for date in results.index:
        desired_position = float(
            results.at[
                date,
                "limited_position",
            ]
        )

        current_spread_return = (
            results.at[
                date,
                "spread_return",
            ]
        )

        if blocked_after_stop:
            # On attend que le signal normal revienne
            # à zéro avant d'autoriser un nouveau trade.
            if desired_position == 0.0:
                blocked_after_stop = False

            current_position = 0.0
            trade_equity = 1.0

        else:
            # Le signal demande une nouvelle position,
            # une fermeture ou un changement de sens.
            if desired_position != current_position:
                current_position = desired_position
                trade_equity = 1.0

        # Position réellement détenue pendant cette journée.
        position_today = current_position

        managed_positions.at[date] = (
            position_today
        )

        if (
            position_today != 0.0
            and pd.notna(current_spread_return)
        ):
            daily_trade_return = (
                weight_per_leg
                * position_today
                * current_spread_return
            )

            # Composition des rendements du trade.
            trade_equity = (
                trade_equity
                * (1.0 + daily_trade_return)
            )

            cumulative_trade_return = (
                trade_equity - 1.0
            )

            # Le seuil est atteint à la fin de la journée.
            if cumulative_trade_return <= -stop_loss:
                stop_loss_triggered.at[date] = True

                # La position sera nulle à partir
                # de la prochaine journée.
                blocked_after_stop = True
                current_position = 0.0

        else:
            cumulative_trade_return = 0.0

        trade_cumulative_returns.at[date] = (
            cumulative_trade_return
        )

    results["managed_position"] = (
        managed_positions
    )

    results["trade_cumulative_return"] = (
        trade_cumulative_returns
    )

    results["stop_loss_triggered"] = (
        stop_loss_triggered
    )

    return results