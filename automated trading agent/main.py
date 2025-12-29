import yfinance as yf  # For stock data
import pandas as pd    # For data manipulation
import numpy as np     # For numerical operations
import matplotlib.pyplot as plt  # For visualizations


# Define parameters
ticker = "AAPL"  # Apple stock
start_date = "2010-01-01"
end_date = "2020-01-01"

# Fetch historical stock data
data = yf.download(ticker, start=start_date, end=end_date)

# Display first few rows
print(data.head())

# Calculate Simple Moving Averages
short_window = 50  # Short-term SMA
long_window = 200  # Long-term SMA

data['SMA50'] = data['Close'].rolling(window=short_window).mean()
data['SMA200'] = data['Close'].rolling(window=long_window).mean()
# Define signals
data['Signal'] = 0  # Initialize Signal column with 0
data.loc[data['SMA50'] > data['SMA200'], 'Signal'] = 1  # Buy
data.loc[data['SMA50'] < data['SMA200'], 'Signal'] = -1  # Sell 
# Create positions (shift signals to avoid look-ahead bias)
data['Position'] = data['Signal'].shift(1)

# Calculate daily percentage change in stock prices
data['Daily Return'] = data['Close'].pct_change()

# Calculate returns based on the strategy
data['Strategy Return'] = data['Position'] * data['Daily Return']

# Calculate cumulative returns
data['Cumulative Market Return'] = (1 + data['Daily Return']).cumprod()
data['Cumulative Strategy Return'] = (1 + data['Strategy Return']).cumprod()
total_strategy_return = data['Cumulative Strategy Return'].iloc[-1] - 1
total_market_return = data['Cumulative Market Return'].iloc[-1] - 1

print(f"Total Strategy Return: {total_strategy_return:.2%}")
print(f"Total Market Return: {total_market_return:.2%}")