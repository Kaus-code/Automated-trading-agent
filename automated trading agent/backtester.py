
"""
Backtesting Engine
Simulates trading strategies on historical data
"""

import pandas as pd
import numpy as np

class Backtester:
    """Class to backtest trading strategies"""
    
    def __init__(self, initial_capital=100000, commission=0.001):
        self.initial_capital = initial_capital
        self.commission = commission
        
    def run(self, data, signals):
        """
        Run the backtest
        
        Args:
            data: DataFrame with price data ('Close')
            signals: DataFrame with 'Signal' and 'Position_Size' columns
            
        Returns:
            DataFrame with backtest results
        """
        df = data.copy()
        
        # Ensure signals align with data
        df['Signal'] = signals['Signal']
        if 'Position_Size' in signals.columns:
            df['Position_Size'] = signals['Position_Size']
        else:
            df['Position_Size'] = 1.0
            
        # Calculate daily returns
        df['Daily_Return'] = df['Close'].pct_change()
        
        # Calculate strategy returns
        # Position is entered at the close of the signal day (or open of next day - simplified here to close)
        # Shift position by 1 to simulate entering at next open/close
        df['Position'] = df['Signal'].shift(1).fillna(0)
        
        # Handle position sizing
        if 'Position_Size' in df.columns:
             df['Position'] = df['Position'] * df['Position_Size'].shift(1).fillna(1.0)

        # Strategy return = Position * Daily Return
        # Subtract commission on trade execution
        df['Trade_Exec'] = df['Position'].diff().abs().fillna(0)
        df['Strategy_Return'] = (df['Position'] * df['Daily_Return']) - (df['Trade_Exec'] * self.commission)
        
        # Calculate cumulative returns
        df['Cumulative_Market_Return'] = (1 + df['Daily_Return']).cumprod()
        df['Cumulative_Strategy_Return'] = (1 + df['Strategy_Return']).cumprod()
        
        # Track portfolio value
        df['Portfolio_Value'] = self.initial_capital * df['Cumulative_Strategy_Return']
        
        # Calculate Drawdown
        df['Peak'] = df['Cumulative_Strategy_Return'].cummax()
        df['Drawdown'] = (df['Cumulative_Strategy_Return'] - df['Peak']) / df['Peak']
        
        return df
