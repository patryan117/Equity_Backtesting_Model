# Equity Backtesting Model:

- An exploratory analysis that simulates algorithmic trading strategies for small and mid-cap biotech companies.  Diffentiating factors between strategies includes several financial and non-financial inputs (sd-limit, trailing-window, hold-period, etc.) 

- collect.py: Extracts a collection of micro-cap bio-tech company financial history and stores in a subdirectory as a set of .csv files. 
- backtest_model.py Object oriented strategy simulator; takes model type and settings as parameters and outputs roi/net return spreads.
