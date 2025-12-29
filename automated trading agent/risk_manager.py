
"""
Risk Management Module
Implements position sizing, stop losses, and risk controls
"""

import pandas as pd
import numpy as np

class RiskManager:
    """Comprehensive risk management system"""
    
    def __init__(self, params):
        self.max_position_size = params.get('max_position_size', 1.0)
        self.stop_loss = params.get('stop_loss', 0.02)
        self.take_profit = params.get('take_profit', 0.05)
        self.max_drawdown = params.get('max_drawdown', 0.20)
        self.max_correlation = params.get('max_correlation', 0.7)
        self.risk_per_trade = params.get('risk_per_trade', 0.02)
        
    def apply_position_sizing(self, signals):
        """
        Apply position sizing rules based on volatility and risk
        
        Uses Kelly Criterion and volatility-based sizing
        """
        df = signals.copy()
        
        # Calculate volatility
        df['Volatility'] = df['Close'].pct_change().rolling(20).std()
        
        # Volatility-adjusted position sizing
        avg_vol = df['Volatility'].mean()
        df['Position_Size'] = df['Signal'] * np.minimum(
            self.max_position_size,
            (avg_vol / df['Volatility']).fillna(1)
        )
        
        # Apply Kelly Criterion
        if 'Strategy_Return' in df.columns:
            win_rate = (df['Strategy_Return'] > 0).sum() / len(df)
            avg_win = df[df['Strategy_Return'] > 0]['Strategy_Return'].mean()
            avg_loss = abs(df[df['Strategy_Return'] < 0]['Strategy_Return'].mean())
            
            if avg_loss > 0:
                kelly_fraction = (win_rate / avg_loss) - ((1 - win_rate) / avg_win)
                kelly_fraction = np.clip(kelly_fraction, 0, self.max_position_size)
                df['Position_Size'] = df['Position_Size'] * kelly_fraction
        
        return df
    
    def apply_stop_loss(self, df, entry_price, position):
        """Apply stop loss to positions"""
        if position == 1:  # Long position
            stop_price = entry_price * (1 - self.stop_loss)
            return df['Close'] <= stop_price
        elif position == -1:  # Short position
            stop_price = entry_price * (1 + self.stop_loss)
            return df['Close'] >= stop_price
        return False
    
    def apply_take_profit(self, df, entry_price, position):
        """Apply take profit to positions"""
        if position == 1:  # Long position
            target_price = entry_price * (1 + self.take_profit)
            return df['Close'] >= target_price
        elif position == -1:  # Short position
            target_price = entry_price * (1 - self.take_profit)
            return df['Close'] <= target_price
        return False
    
    def check_drawdown_limit(self, portfolio_value, peak_value):
        """Check if drawdown exceeds maximum allowed"""
        current_dd = (portfolio_value - peak_value) / peak_value
        return current_dd < -self.max_drawdown
    
    def calculate_var(self, returns, confidence=0.95):
        """Calculate Value at Risk"""
        return np.percentile(returns, (1 - confidence) * 100)
    
    def calculate_position_correlation(self, positions_df):
        """Calculate correlation between positions"""
        return positions_df.corr()
    
    def diversification_check(self, new_position, existing_positions):
        """Check if new position maintains diversification"""
        if len(existing_positions) == 0:
            return True
        
        all_positions = existing_positions.copy()
        all_positions[new_position['ticker']] = new_position['returns']
        
        correlation_matrix = pd.DataFrame(all_positions).corr()
        max_corr = correlation_matrix[new_position['ticker']].drop(new_position['ticker']).max()
        
        return max_corr < self.max_correlation
    
    def trailing_stop(self, df, entry_price, highest_price, position, trail_pct=0.05):
        """Implement trailing stop loss"""
        if position == 1:  # Long position
            stop_price = highest_price * (1 - trail_pct)
            return df['Close'] <= stop_price
        elif position == -1:  # Short position
            stop_price = highest_price * (1 + trail_pct)
            return df['Close'] >= stop_price
        return False

class PortfolioRiskManager:
    """Portfolio-level risk management"""
    
    def __init__(self, max_portfolio_risk=0.15):
        self.max_portfolio_risk = max_portfolio_risk
        self.positions = {}
        
    def add_position(self, ticker, size, entry_price):
        """Add new position to portfolio"""
        self.positions[ticker] = {
            'size': size,
            'entry_price': entry_price,
            'current_value': size * entry_price
        }
    
    def update_position(self, ticker, current_price):
        """Update position value"""
        if ticker in self.positions:
            size = self.positions[ticker]['size']
            self.positions[ticker]['current_value'] = size * current_price
    
    def calculate_portfolio_var(self, returns_dict, confidence=0.95):
        """Calculate portfolio-wide Value at Risk"""
        portfolio_returns = pd.DataFrame(returns_dict).sum(axis=1)
        return np.percentile(portfolio_returns, (1 - confidence) * 100)
    
    def get_portfolio_exposure(self):
        """Calculate total portfolio exposure"""
        total_value = sum(pos['current_value'] for pos in self.positions.values())
        return total_value
    
    def rebalance_required(self, target_weights, current_weights, threshold=0.05):
        """Check if rebalancing is needed"""
        weight_diff = np.abs(np.array(target_weights) - np.array(current_weights))
        return np.any(weight_diff > threshold)