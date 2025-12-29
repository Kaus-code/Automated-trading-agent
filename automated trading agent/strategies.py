"""
Trading Strategy Implementations
Contains various algorithmic trading strategies
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """Abstract base class for all trading strategies"""
    
    def __init__(self, params):
        self.params = params
        
    @abstractmethod
    def generate_signals(self, data):
        """Generate buy/sell signals"""
        pass
    
    def calculate_positions(self, signals):
        """Convert signals to positions"""
        positions = signals.shift(1)  # Avoid look-ahead bias
        return positions

class MovingAverageCrossover(BaseStrategy):
    """Simple Moving Average Crossover Strategy"""
    
    def generate_signals(self, data):
        """
        Generate signals based on SMA crossover
        Buy when short MA crosses above long MA
        Sell when short MA crosses below long MA
        """
        df = data.copy()
        short_window = self.params.get('short', 50)
        long_window = self.params.get('long', 200)
        
        # Calculate moving averages
        df['SMA_Short'] = df['Close'].rolling(window=short_window).mean()
        df['SMA_Long'] = df['Close'].rolling(window=long_window).mean()
        
        # Generate signals
        df['Signal'] = 0
        df.loc[df['SMA_Short'] > df['SMA_Long'], 'Signal'] = 1  # Buy
        df.loc[df['SMA_Short'] < df['SMA_Long'], 'Signal'] = -1  # Sell
        
        # Identify crossover points
        df['Crossover'] = df['Signal'].diff()
        
        return df

class RSIStrategy(BaseStrategy):
    """Relative Strength Index Strategy"""
    
    def generate_signals(self, data):
        """
        Generate signals based on RSI
        Buy when RSI < oversold threshold
        Sell when RSI > overbought threshold
        """
        df = data.copy()
        period = self.params.get('period', 14)
        oversold = self.params.get('oversold', 30)
        overbought = self.params.get('overbought', 70)
        
        # Calculate RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Generate signals
        df['Signal'] = 0
        df.loc[df['RSI'] < oversold, 'Signal'] = 1  # Oversold - Buy
        df.loc[df['RSI'] > overbought, 'Signal'] = -1  # Overbought - Sell
        
        return df

class MACDStrategy(BaseStrategy):
    """Moving Average Convergence Divergence Strategy"""
    
    def generate_signals(self, data):
        """
        Generate signals based on MACD crossover
        """
        df = data.copy()
        fast = self.params.get('fast', 12)
        slow = self.params.get('slow', 26)
        signal = self.params.get('signal', 9)
        
        # Calculate MACD
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
        df['MACD'] = ema_fast - ema_slow
        df['Signal_Line'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']
        
        # Generate signals
        df['Signal'] = 0
        df.loc[df['MACD'] > df['Signal_Line'], 'Signal'] = 1  # Buy
        df.loc[df['MACD'] < df['Signal_Line'], 'Signal'] = -1  # Sell
        
        return df

class BollingerBandsStrategy(BaseStrategy):
    """Bollinger Bands Mean Reversion Strategy"""
    
    def generate_signals(self, data):
        """Generate signals based on Bollinger Bands"""
        df = data.copy()
        period = self.params.get('period', 20)
        std_dev = self.params.get('std_dev', 2)
        
        # Calculate Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=period).mean()
        df['BB_Std'] = df['Close'].rolling(window=period).std()
        df['BB_Upper'] = df['BB_Middle'] + (std_dev * df['BB_Std'])
        df['BB_Lower'] = df['BB_Middle'] - (std_dev * df['BB_Std'])
        
        # Generate signals
        df['Signal'] = 0
        df.loc[df['Close'] < df['BB_Lower'], 'Signal'] = 1  # Buy at lower band
        df.loc[df['Close'] > df['BB_Upper'], 'Signal'] = -1  # Sell at upper band
        
        return df

class MomentumStrategy(BaseStrategy):
    """Price Momentum Strategy"""
    
    def generate_signals(self, data):
        """Generate signals based on price momentum"""
        df = data.copy()
        lookback = self.params.get('lookback', 20)
        threshold = self.params.get('threshold', 0.02)
        
        # Calculate momentum
        df['Momentum'] = df['Close'].pct_change(periods=lookback)
        
        # Generate signals
        df['Signal'] = 0
        df.loc[df['Momentum'] > threshold, 'Signal'] = 1  # Strong upward momentum
        df.loc[df['Momentum'] < -threshold, 'Signal'] = -1  # Strong downward momentum
        
        return df

class CompositeStrategy(BaseStrategy):
    """Combination of multiple strategies"""
    
    def __init__(self, strategies_list):
        self.strategies = strategies_list
        
    def generate_signals(self, data):
        """Combine signals from multiple strategies"""
        df = data.copy()
        
        all_signals = []
        for strategy in self.strategies:
            signals = strategy.generate_signals(data)
            all_signals.append(signals['Signal'])
        
        # Average the signals
        df['Signal'] = pd.concat(all_signals, axis=1).mean(axis=1)
        
        # Convert to discrete signals
        df['Signal'] = df['Signal'].apply(lambda x: 1 if x > 0.3 else (-1 if x < -0.3 else 0))
        
        return df