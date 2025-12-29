
"""
Performance Metrics Calculator
Comprehensive performance analysis for trading strategies
"""

import pandas as pd
import numpy as np
from scipy import stats

class PerformanceAnalyzer:
    """Calculate various performance metrics"""
    
    def __init__(self, risk_free_rate=0.02):
        self.risk_free_rate = risk_free_rate
        
    def calculate_metrics(self, results):
        """
        Calculate comprehensive performance metrics
        
        Args:
            results: DataFrame from backtester
            
        Returns:
            Dictionary of performance metrics
        """
        metrics = {}
        
        # Basic returns
        metrics['total_return'] = self._total_return(results)
        metrics['annualized_return'] = self._annualized_return(results)
        metrics['volatility'] = self._volatility(results)
        
        # Risk-adjusted returns
        metrics['sharpe_ratio'] = self._sharpe_ratio(results)
        metrics['sortino_ratio'] = self._sortino_ratio(results)
        metrics['calmar_ratio'] = self._calmar_ratio(results)
        
        # Drawdown metrics
        metrics['max_drawdown'] = self._max_drawdown(results)
        metrics['avg_drawdown'] = self._avg_drawdown(results)
        metrics['drawdown_duration'] = self._drawdown_duration(results)
        
        # Trade statistics
        metrics.update(self._trade_statistics(results))
        
        # Additional metrics
        metrics['information_ratio'] = self._information_ratio(results)
        metrics['beta'] = self._beta(results)
        metrics['alpha'] = self._alpha(results)
        metrics['var_95'] = self._value_at_risk(results, 0.95)
        metrics['cvar_95'] = self._conditional_var(results, 0.95)
        
        return metrics
    
    def _total_return(self, df):
        """Calculate total return"""
        return df['Cumulative_Strategy_Return'].iloc[-1] - 1
    
    def _annualized_return(self, df):
        """Calculate annualized return"""
        total_return = self._total_return(df)
        years = len(df) / 252
        return (1 + total_return) ** (1 / years) - 1
    
    def _volatility(self, df):
        """Calculate annualized volatility"""
        return df['Strategy_Return'].std() * np.sqrt(252)
    
    def _sharpe_ratio(self, df):
        """Calculate Sharpe ratio"""
        excess_returns = df['Strategy_Return'] - self.risk_free_rate / 252
        if excess_returns.std() == 0:
            return 0
        return (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
    
    def _sortino_ratio(self, df):
        """Calculate Sortino ratio (downside deviation)"""
        excess_returns = df['Strategy_Return'] - self.risk_free_rate / 252
        downside_returns = excess_returns[excess_returns < 0]
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0
        return (excess_returns.mean() / downside_returns.std()) * np.sqrt(252)
    
    def _calmar_ratio(self, df):
        """Calculate Calmar ratio"""
        annual_return = self._annualized_return(df)
        max_dd = abs(self._max_drawdown(df))
        if max_dd == 0:
            return 0
        return annual_return / max_dd
    
    def _max_drawdown(self, df):
        """Calculate maximum drawdown"""
        if 'Drawdown' in df.columns:
            return df['Drawdown'].min()
        return 0
    
    def _avg_drawdown(self, df):
        """Calculate average drawdown"""
        if 'Drawdown' in df.columns:
            drawdowns = df['Drawdown'][df['Drawdown'] < 0]
            return drawdowns.mean() if len(drawdowns) > 0 else 0
        return 0
    
    def _drawdown_duration(self, df):
        """Calculate longest drawdown duration in days"""
        if 'Drawdown' in df.columns:
            in_drawdown = df['Drawdown'] < 0
            durations = []
            current_duration = 0
            
            for is_dd in in_drawdown:
                if is_dd:
                    current_duration += 1
                else:
                    if current_duration > 0:
                        durations.append(current_duration)
                    current_duration = 0
            
            return max(durations) if durations else 0
        return 0
    
    def _trade_statistics(self, df):
        """Calculate trade-level statistics"""
        if 'Position' not in df.columns:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'avg_trade_duration': 0
            }
        
        # Identify trades
        position_changes = df['Position'].diff().fillna(0) != 0
        trades = df[position_changes]
        
        if len(trades) < 2:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'avg_trade_duration': 0
            }
        
        # Calculate returns for each trade
        trade_returns = []
        for i in range(len(trades) - 1):
            start_idx = trades.index[i]
            end_idx = trades.index[i + 1]
            trade_return = df.loc[end_idx, 'Cumulative_Strategy_Return'] / \
                          df.loc[start_idx, 'Cumulative_Strategy_Return'] - 1
            trade_returns.append(trade_return)
        
        trade_returns = np.array(trade_returns)
        wins = trade_returns[trade_returns > 0]
        losses = trade_returns[trade_returns < 0]
        
        return {
            'total_trades': len(trade_returns),
            'win_rate': len(wins) / len(trade_returns) if len(trade_returns) > 0 else 0,
            'avg_win': wins.mean() if len(wins) > 0 else 0,
            'avg_loss': losses.mean() if len(losses) > 0 else 0,
            'profit_factor': abs(wins.sum() / losses.sum()) if len(losses) > 0 and losses.sum() != 0 else 0,
            'avg_trade_duration': len(df) / len(trades) if len(trades) > 0 else 0
        }
    
    def _information_ratio(self, df):
        """Calculate information ratio vs benchmark"""
        excess_returns = df['Strategy_Return'] - df['Daily_Return']
        if excess_returns.std() == 0:
            return 0
        return (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
    
    def _beta(self, df):
        """Calculate beta vs market"""
        market_returns = df['Daily_Return'].dropna()
        strategy_returns = df['Strategy_Return'].dropna()
        
        if len(market_returns) != len(strategy_returns):
            min_len = min(len(market_returns), len(strategy_returns))
            market_returns = market_returns[-min_len:]
            strategy_returns = strategy_returns[-min_len:]
        
        if len(market_returns) == 0 or market_returns.var() == 0:
            return 0
        
        covariance = np.cov(strategy_returns, market_returns)[0][1]
        market_variance = market_returns.var()
        return covariance / market_variance
    
    def _alpha(self, df):
        """Calculate alpha (excess return vs expected return)"""
        beta = self._beta(df)
        strategy_return = self._annualized_return(df)
        market_return = (df['Cumulative_Market_Return'].iloc[-1] - 1)
        years = len(df) / 252
        market_return_ann = (1 + market_return) ** (1 / years) - 1
        
        expected_return = self.risk_free_rate + beta * (market_return_ann - self.risk_free_rate)
        return strategy_return - expected_return
    
    def _value_at_risk(self, df, confidence=0.95):
        """Calculate Value at Risk"""
        returns = df['Strategy_Return'].dropna()
        if len(returns) == 0:
            return 0
        return np.percentile(returns, (1 - confidence) * 100)
    
    def _conditional_var(self, df, confidence=0.95):
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        returns = df['Strategy_Return'].dropna()
        if len(returns) == 0:
            return 0
        var = self._value_at_risk(df, confidence)
        return returns[returns <= var].mean()
    
    def generate_report(self, metrics):
        """Generate formatted performance report"""
        report = f"""
{'='*70}
PERFORMANCE METRICS REPORT
{'='*70}

RETURNS:
  Total Return:              {metrics['total_return']:>12.2%}
  Annualized Return:         {metrics['annualized_return']:>12.2%}
  Volatility (Ann.):         {metrics['volatility']:>12.2%}

RISK-ADJUSTED RETURNS:
  Sharpe Ratio:              {metrics['sharpe_ratio']:>12.2f}
  Sortino Ratio:             {metrics['sortino_ratio']:>12.2f}
  Calmar Ratio:              {metrics['calmar_ratio']:>12.2f}
  Information Ratio:         {metrics['information_ratio']:>12.2f}

DRAWDOWN METRICS:
  Maximum Drawdown:          {metrics['max_drawdown']:>12.2%}
  Average Drawdown:          {metrics['avg_drawdown']:>12.2%}
  Longest DD Duration:       {metrics['drawdown_duration']:>12.0f} days

TRADE STATISTICS:
  Total Trades:              {metrics['total_trades']:>12.0f}
  Win Rate:                  {metrics['win_rate']:>12.2%}
  Average Win:               {metrics['avg_win']:>12.2%}
  Average Loss:              {metrics['avg_loss']:>12.2%}
  Profit Factor:             {metrics['profit_factor']:>12.2f}
  Avg Trade Duration:        {metrics['avg_trade_duration']:>12.1f} days

MARKET COMPARISON:
  Beta:                      {metrics['beta']:>12.2f}
  Alpha (Ann.):              {metrics['alpha']:>12.2%}

RISK METRICS:
  Value at Risk (95%):       {metrics['var_95']:>12.2%}
  Conditional VaR (95%):     {metrics['cvar_95']:>12.2%}

{'='*70}
"""
        return report