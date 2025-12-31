
"""
Backtesting Engine
Simulates trading strategies on historical data
"""

import pandas as pd
import numpy as np

class Backtester:
    """Class to backtest trading strategies"""
    
    def __init__(self, initial_capital=10000, commission_fee=1.0):
        self.initial_capital = initial_capital
        self.commission_fee = commission_fee  # Fixed fee per trade
        
    def run(self, data, signals):
        """
        Run the backtest with Paper Money logic
        
        Args:
            data: DataFrame with price data ('Close')
            signals: DataFrame with 'Signal' and 'Position_Size' columns
            
        Returns:
            DataFrame with backtest results
        """
        df = data.copy()
        
        # Handle potential MultiIndex from yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        if 'Signal' in signals.columns:
            # If signals['Signal'] is a DataFrame (MultiIndex), take the first column
            sig_col = signals['Signal']
            if isinstance(sig_col, pd.DataFrame):
                df['Signal'] = sig_col.iloc[:, 0]
            else:
                df['Signal'] = sig_col
        else:
            df['Signal'] = 0

        # Initialize tracking columns
        df['Cash'] = 0.0
        df['Shares'] = 0.0
        df['Total_Equity'] = 0.0
        df['Transaction_Cost'] = 0.0
        
        # Simulation variables
        current_cash = self.initial_capital
        current_shares = 0
        
        # Handle potential MultiIndex from yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Iterate through data to simulate trades
        for i in range(len(df)):
            try:
                price = df['Close'].iloc[i]
                if isinstance(price, pd.Series):
                    price = price.iloc[0]
                    
                signal = df['Signal'].iloc[i]
                if isinstance(signal, pd.Series):
                    signal = signal.iloc[0]
                
                # Rule A: The "Affordability" Check & Trading Logic
                # Buy on signal 1
                if signal == 1 and current_shares == 0:
                    available_cash = current_cash - self.commission_fee
                    if available_cash > price:
                        num_shares = int(available_cash // price)
                        if num_shares > 0:
                            current_shares = num_shares
                            current_cash -= (num_shares * price) + self.commission_fee
                            df.at[df.index[i], 'Transaction_Cost'] = self.commission_fee
                        
                # Sell on signal -1 or 0 (configurable, but strategies use -1/0)
                elif (signal == -1 or signal == 0) and current_shares > 0:
                    current_cash += (current_shares * price) - self.commission_fee
                    df.at[df.index[i], 'Transaction_Cost'] = self.commission_fee
                    current_shares = 0
            except Exception as e:
                # Fallback for any iteration errors
                continue
            
            # Rule C: The "Equity" Calculation
            # Total Equity = Current Cash + (Shares Held * Current Market Price)
            df.at[df.index[i], 'Cash'] = current_cash
            df.at[df.index[i], 'Shares'] = current_shares
            df.at[df.index[i], 'Total_Equity'] = current_cash + (current_shares * price)
            
        # Calculate returns for compatibility with other components
        df['Portfolio_Value'] = df['Total_Equity']
        df['Cumulative_Strategy_Return'] = df['Total_Equity'] / self.initial_capital
        df['Strategy_Return'] = df['Total_Equity'].pct_change().fillna(0)
        
        # Market benchmark
        df['Daily_Return'] = df['Close'].pct_change().fillna(0)
        df['Cumulative_Market_Return'] = (1 + df['Daily_Return']).cumprod()
        
        # Calculate Drawdown
        df['Peak'] = df['Cumulative_Strategy_Return'].cummax()
        df['Drawdown'] = (df['Cumulative_Strategy_Return'] - df['Peak']) / df['Peak']
        
        # Position for trade statistics (1 if holding, 0 if not)
        df['Position'] = (df['Shares'] > 0).astype(int)
        
        return df
