import numpy as np
import pandas as pd


def compute_performance_metrics(
    backtest_results: pd.DataFrame,
    periods_per_year: int = 252,
) -> dict:
    """
    Calcule les principales mesures de performance
    du backtest.
    """

    required_columns = {
        "position",
        "gross_strategy_return",
        "strategy_return",
        "transaction_cost",
        "gross_equity_curve",
        "equity_curve",
        "drawdown",
    }

    missing_columns = (
        required_columns
        - set(backtest_results.columns)
    )

    if missing_columns:
        raise ValueError(
            "Colonnes absentes : "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    daily_returns = (
        backtest_results["strategy_return"]
        .dropna()
    )

    if len(daily_returns) < 2:
        raise ValueError(
            "Il n'y a pas assez de rendements."
        )

    gross_total_return = (
        backtest_results[
            "gross_equity_curve"
        ].iloc[-1]
        - 1.0
    )

    net_total_return = (
        backtest_results[
            "equity_curve"
        ].iloc[-1]
        - 1.0
    )

    number_of_periods = len(
        daily_returns
    )

    annualized_return = (
        backtest_results[
            "equity_curve"
        ].iloc[-1]
        ** (
            periods_per_year
            / number_of_periods
        )
        - 1.0
    )

    daily_volatility = daily_returns.std(
        ddof=1
    )

    annualized_volatility = (
        daily_volatility
        * np.sqrt(periods_per_year)
    )

    if (
        daily_volatility == 0
        or np.isnan(daily_volatility)
    ):
        sharpe_ratio = np.nan

    else:
        # On suppose ici un taux sans risque nul.
        sharpe_ratio = (
            daily_returns.mean()
            / daily_volatility
            * np.sqrt(periods_per_year)
        )

    maximum_drawdown = (
        backtest_results[
            "drawdown"
        ].min()
    )

    time_in_market = (
        backtest_results["position"]
        != 0
    ).mean()

    previous_position = (
        backtest_results["position"]
        .shift(1)
        .fillna(0)
    )

    entries = (
        (backtest_results["position"] != 0)
        & (previous_position == 0)
    )

    exits = (
        (backtest_results["position"] == 0)
        & (previous_position != 0)
    )

    total_transaction_cost = (
        backtest_results[
            "transaction_cost"
        ].sum()
    )

    return {
        "gross_total_return": float(
            gross_total_return
        ),
        "net_total_return": float(
            net_total_return
        ),
        "annualized_return": float(
            annualized_return
        ),
        "annualized_volatility": float(
            annualized_volatility
        ),
        "sharpe_ratio": float(
            sharpe_ratio
        ),
        "maximum_drawdown": float(
            maximum_drawdown
        ),
        "time_in_market": float(
            time_in_market
        ),
        "number_of_entries": int(
            entries.sum()
        ),
        "number_of_exits": int(
            exits.sum()
        ),
        "total_transaction_cost": float(
            total_transaction_cost
        ),
    }