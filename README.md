# Mean-Reversion Backtest

Educational project implementing and evaluating a simple mean-reversion trading strategy on two highly correlated ETFs: SPY and IVV.

The objective is to build a complete backtesting pipeline including:

* market data retrieval;
* spread construction;
* rolling z-score calculation;
* trading signals;
* position management;
* transaction costs;
* stop-loss rules;
* PnL calculation;
* performance analysis.

The project is designed as an introduction to systematic trading and backtesting methodology.

---

## Project Objective

SPY and IVV are two exchange-traded funds that both track the S&P 500 index.

Because they are exposed to almost the same underlying market, their prices tend to move very closely together.

However, temporary deviations can occur.

The strategy is based on the idea that these deviations may revert toward their historical average.

The objective is therefore to detect unusually large deviations between SPY and IVV and trade in the direction of mean reversion.

---

# Project Structure

```text
mean-reversion-backtest/
│
├── figures/
│   └── ...
│
├── src/
│   ├── ...
│
│
├── ...
├── requirements.txt
├── .gitignore
└── README.md
```

The exact file organization may vary depending on the implementation, but the project separates data processing, signal generation, backtesting and visualization.

---

# 1. Market Data

The strategy uses historical prices for:

```text
SPY
IVV
```

Both ETFs track the S&P 500 and therefore have very similar long-term price dynamics.

Historical market data is downloaded and aligned by date before being used in the backtest.

Only dates for which both assets have valid observations are retained.

---

# 2. Why Use Two Similar ETFs?

The strategy does not attempt to predict the direction of the overall stock market.

Instead, it focuses on the relative behaviour of two strongly related assets.

For example:

```text
SPY rises strongly
IVV rises less strongly
```

The difference between the two assets may temporarily increase.

If this difference later returns toward its usual level, a relative-value trade may generate a profit.

The strategy therefore tries to exploit:

```text
temporary relative deviations
rather than
absolute market direction
```

---

# 3. Log-Price Spread

The spread is constructed using the logarithm of the two ETF prices.

Conceptually:

```text
spread
=
log(SPY price)
-
log(IVV price)
```

Using logarithmic prices is convenient because relative price changes become easier to interpret.

If the two ETFs move perfectly together, the spread should remain relatively stable.

Temporary deviations create movements in the spread.

---

# 4. Rolling Mean and Standard Deviation

The current spread alone does not tell us whether a deviation is unusually large.

The strategy therefore compares the current spread with its recent historical behaviour.

A rolling window of:

```text
20 trading days
```

is used.

For each date, the program calculates:

```text
rolling mean of the spread

rolling standard deviation of the spread
```

These values describe the recent equilibrium level and recent variability of the spread.

---

# 5. Z-Score

The z-score measures how far the current spread is from its rolling mean.

Conceptually:

```text
z-score
=
current spread - rolling mean
--------------------------------
rolling standard deviation
```

Examples:

```text
z-score = 0
→ spread close to its recent average

z-score = +2
→ spread approximately two standard deviations above its recent average

z-score = -2
→ spread approximately two standard deviations below its recent average
```

The z-score is therefore used as the main trading signal.

---

# 6. Trading Logic

The strategy assumes that unusually large deviations will eventually revert toward the rolling mean.

The entry thresholds are:

```text
z-score > +2

or

z-score < -2
```

If:

```text
z-score > +2
```

the spread is considered unusually high.

Since:

```text
spread = log(SPY) - log(IVV)
```

this suggests that SPY is relatively expensive compared with IVV.

The strategy therefore takes approximately:

```text
short SPY
long IVV
```

If:

```text
z-score < -2
```

SPY is relatively cheap compared with IVV.

The strategy takes approximately:

```text
long SPY
short IVV
```

---

# 7. Exit Rule

A position is not immediately closed when the z-score crosses zero.

Instead, the trade is closed once the spread has moved sufficiently close to its recent equilibrium.

The exit threshold used is:

```text
|z-score| < 0.5
```

In other words:

```text
-0.5 < z-score < +0.5
```

This creates a distinction between:

```text
entry zone
→ large deviation

exit zone
→ spread close to equilibrium
```

---

# 8. Position Size

The strategy uses approximately equal exposure on both legs.

Conceptually:

```text
50% allocation to one leg
50% allocation to the other leg
```

For a long-SPY / short-IVV trade:

```text
+0.5 SPY
-0.5 IVV
```

For a short-SPY / long-IVV trade:

```text
-0.5 SPY
+0.5 IVV
```

The absolute total position is limited so that the strategy does not take unlimited leverage.

The maximum absolute position is:

```text
1
```

---

# 9. Position Persistence

Once a trade has been opened, the position remains active until an exit condition or stop-loss condition is reached.

This is important because a trading strategy cannot simply recompute a completely independent position every day.

The program therefore tracks whether the strategy is currently:

```text
long the spread

short the spread

or flat
```

and updates the position accordingly.

---

# 10. Avoiding Look-Ahead Bias

A crucial issue in backtesting is look-ahead bias.

Suppose a signal is calculated using today's closing price.

That signal cannot realistically be used to trade at the same closing price because the price was required to compute the signal.

To avoid this, the strategy shifts the position by one period:

```python
position = signal.shift(1)
```

This means:

```text
information observed at date t
→ position applied at date t + 1
```

The backtest therefore does not use future information.

This is one of the most important differences between a realistic backtest and an artificially optimistic one.

---

# 11. Returns

Daily returns are calculated for both assets.

Conceptually:

```text
SPY return
=
percentage change in SPY price

IVV return
=
percentage change in IVV price
```

The return of the trading strategy depends on the positions held in each ETF.

For example, with:

```text
+0.5 SPY
-0.5 IVV
```

the strategy return is approximately:

```text
0.5 × SPY return
-
0.5 × IVV return
```

The strategy therefore depends mainly on the relative movement between the two ETFs.

---

# 12. PnL

The daily PnL is obtained from the positions held and the subsequent asset returns.

Conceptually:

```text
strategy return
=
SPY position × SPY return
+
IVV position × IVV return
```

The daily strategy returns are then accumulated over time to obtain the evolution of the portfolio.

This makes it possible to study:

```text
profitability
risk
drawdowns
stability
```

---

# 13. Transaction Costs

A strategy that frequently changes positions generates trading costs.

Ignoring these costs can make a backtest unrealistically optimistic.

The project therefore includes proportional transaction costs of:

```text
5 basis points
```

where:

```text
1 basis point = 0.01%

5 basis points = 0.05%
```

Transaction costs are applied when the position changes.

Conceptually:

```text
transaction cost
=
cost rate
×
traded position
```

The net strategy return becomes:

```text
net return
=
gross strategy return
-
transaction costs
```

---

# 14. Why Transaction Costs Matter

A mean-reversion strategy may trade relatively frequently.

A strategy could appear profitable before costs:

```text
gross return > 0
```

but become much less attractive after accounting for repeated purchases and sales.

Including transaction costs therefore provides a more realistic evaluation.

---

# 15. Stop-Loss

The project also includes a stop-loss mechanism.

The stop-loss threshold is:

```text
0.5%
```

Its purpose is to prevent a position from continuing to accumulate losses when the assumed mean-reversion relationship temporarily breaks down.

The idea is:

```text
trade opened
      ↓
loss becomes too large
      ↓
position closed
```

The stop-loss introduces a basic form of risk management into the strategy.

---

# 16. Why Mean Reversion Can Fail

A large z-score does not guarantee that the spread will return immediately toward its mean.

For example:

```text
z-score = +2
```

can become:

```text
+2.5
+3
+4
```

before eventually reverting.

It may also reflect a genuine change in the relationship between the two assets.

Mean reversion is therefore an assumption, not a certainty.

This is why risk-management mechanisms such as position limits and stop-losses are important.

---

# 17. Backtesting

The backtest reproduces the strategy historically.

The general process is:

```text
historical prices
       ↓
log-price spread
       ↓
rolling statistics
       ↓
z-score
       ↓
trading signals
       ↓
shifted positions
       ↓
asset returns
       ↓
transaction costs
       ↓
strategy PnL
       ↓
performance metrics
```

The purpose of the backtest is not to prove that the strategy will work in the future.

It is used to evaluate how the trading rules would have behaved on historical data.

---

# 18. Why Backtesting Is Useful

A backtest can reveal whether a strategy has undesirable characteristics.

For example:

```text
very large drawdowns
excessive trading
high sensitivity to transaction costs
unstable performance
poor risk-adjusted returns
```

It also makes it possible to compare different trading rules in a consistent framework.

However:

```text
good historical performance
does not guarantee
good future performance
```

---

# 19. Cumulative Performance

Daily strategy returns are compounded to calculate portfolio performance over time.

Conceptually:

```text
portfolio value today
=
portfolio value yesterday
×
(1 + daily return)
```

This produces an equity curve representing the evolution of the strategy.

The equity curve is useful for visualizing:

```text
growth
periods of loss
recovery
drawdowns
```

---

# 20. Performance Metrics

Several metrics can be used to evaluate the strategy.

They provide information about both return and risk.

---

# 21. Total Return

Total return measures the overall change in portfolio value over the backtest period.

Conceptually:

```text
total return
=
final portfolio value
---------------------
initial portfolio value
-
1
```

A positive total return means that the strategy generated a profit over the historical period.

---

# 22. Volatility

Volatility measures the variability of strategy returns.

A strategy with highly unstable returns has higher volatility.

Conceptually:

```text
high volatility
→ larger fluctuations

low volatility
→ more stable returns
```

Volatility is a measure of risk, but it does not distinguish between positive and negative movements.

---

# 23. Sharpe Ratio

The Sharpe ratio compares return with volatility.

Conceptually:

```text
Sharpe ratio
=
return
--------
risk
```

A higher Sharpe ratio indicates that more return is obtained for a given level of volatility.

It should not be interpreted as a complete measure of strategy quality, but it is useful for comparing risk-adjusted performance.

---

# 24. Maximum Drawdown

Maximum drawdown measures the largest loss from a previous portfolio peak to the following trough.

Suppose the portfolio evolves as:

```text
€10,000
→ €15,000
→ €9,000
```

The relevant drawdown is measured from:

```text
peak = €15,000
```

to:

```text
trough = €9,000
```

The loss is:

```text
€6,000
```

relative to the peak:

```text
€6,000 / €15,000
=
40%
```

Therefore:

```text
maximum drawdown = 40%
```

This metric is particularly useful because it represents the type of loss an investor would have experienced after reaching a previous portfolio high.

---

# 25. Why Maximum Drawdown Matters

Two strategies may have similar final returns but very different paths.

For example:

```text
Strategy A:
smooth growth
small drawdowns

Strategy B:
large crashes
followed by recoveries
```

Even if both finish at the same value, Strategy B is significantly more difficult and risky to hold.

Maximum drawdown therefore provides information that total return alone cannot capture.

---

# 26. Strategy Interpretation

The strategy is a relative-value strategy.

It does not primarily attempt to forecast:

```text
whether the S&P 500 will rise or fall
```

Instead, it attempts to forecast:

```text
whether the relative difference
between SPY and IVV
will revert toward its recent average
```

This reduces exposure to the general direction of the market compared with a simple directional strategy.

---

# 27. Main Result

The project demonstrates the complete construction of a simple systematic trading strategy.

The main steps are:

```text
identify a relative-value relationship
        ↓
construct a spread
        ↓
normalize it using a z-score
        ↓
define systematic trading rules
        ↓
avoid look-ahead bias
        ↓
include transaction costs
        ↓
apply risk management
        ↓
evaluate historical performance
```

The most important result is not simply whether the historical return is positive.

The project illustrates how a trading idea must be translated into precise and testable rules.

---

# 28. Limitations

This project is intentionally simplified.

Several limitations should be considered.

## Historical Relationship

SPY and IVV have historically tracked the same underlying index, but their statistical relationship is not guaranteed to remain identical in the future.

---

## Rolling Parameters

The rolling mean and standard deviation are estimated from only:

```text
20 trading days
```

Different window lengths may produce different signals.

---

## Fixed Thresholds

The strategy uses fixed thresholds:

```text
entry: ±2

exit: ±0.5
```

These values were selected for the project and are not necessarily optimal.

Optimizing thresholds excessively on historical data could lead to overfitting.

---

## Transaction Costs

The project assumes constant transaction costs of:

```text
5 basis points
```

Real trading costs vary through time and may depend on:

```text
liquidity
bid-ask spreads
market conditions
order size
```

---

## No Market Impact

The strategy assumes that trades do not affect market prices.

This is reasonable for a small educational backtest but may not hold for large trading volumes.

---

## Simplified Execution

The backtest uses historical prices and simplified execution assumptions.

Real trading may involve:

```text
slippage
latency
partial fills
different bid and ask prices
```

---

## Model Risk

A high z-score does not guarantee future mean reversion.

The spread may move because the statistical relationship between the assets has changed.

---

# 29. Possible Extensions

Several extensions could improve the project:

```text
out-of-sample testing
walk-forward validation
dynamic entry thresholds
cointegration testing
different rolling-window lengths
more realistic transaction costs
slippage
parameter sensitivity analysis
multiple ETF pairs
portfolio-level risk management
different stop-loss rules
```

These extensions would help evaluate the robustness of the strategy.

---

# 30. Skills Developed

This project provides practice with:

```text
Python
NumPy
pandas
Matplotlib
financial time series
market data
log returns
rolling statistics
z-scores
mean-reversion strategies
systematic trading
position management
backtesting
look-ahead bias
transaction costs
risk management
stop-losses
PnL
portfolio returns
volatility
Sharpe ratio
maximum drawdown
strategy evaluation
Git
GitHub
```

---

# 31. Conclusion

This project implements a complete mean-reversion backtest using SPY and IVV.

The strategy detects temporary deviations between the two ETFs through a rolling z-score.

Large deviations trigger relative-value positions:

```text
SPY relatively expensive
→ short SPY / long IVV

SPY relatively cheap
→ long SPY / short IVV
```

Positions are closed when the spread returns sufficiently close to its recent mean.

The backtest also includes important practical considerations:

```text
position lagging
transaction costs
position limits
stop-loss rules
performance metrics
```

The project therefore provides a simple introduction to the process of transforming a statistical trading idea into a systematic and testable strategy.

---

# Disclaimer

This project is for educational purposes only.

It does not constitute financial advice or a trading strategy intended for direct use in real financial markets.

