"""
Main Trading Strategy Application
Author: [Your Name]
Date: December 2024
Description: Comprehensive algorithmic trading system with multiple strategies
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import custom modules
from strategies import MovingAverageCrossover, RSIStrategy, MACDStrategy
from backtester import Backtester
from risk_manager import RiskManager
from portfolio_optimizer import PortfolioOptimizer
from performance_metrics import PerformanceAnalyzer
from data_fetcher import DataFetcher
from visualization import Visualizer

class TradingSystem:
    """Main trading system orchestrator"""
    
    def __init__(self, config):
        self.config = config
        self.data_fetcher = DataFetcher()
        self.backtester = Backtester()
        self.risk_manager = RiskManager(config['risk_params'])
        self.visualizer = Visualizer()
        self.results = {}
        
    def load_data(self, tickers, start_date, end_date):
        """Load historical data for multiple tickers"""
        print(f"Loading data for {len(tickers)} tickers...")
        self.data = {}
        for ticker in tickers:
            try:
                df = yf.download(ticker, start=start_date, end=end_date, progress=False)
                self.data[ticker] = df
                print(f"✓ {ticker}: {len(df)} days loaded")
            except Exception as e:
                print(f"✗ {ticker}: Failed - {str(e)}")
        return self.data
    
    def run_strategy(self, strategy_name, ticker, params):
        """Execute a specific trading strategy"""
        print(f"\n{'='*60}")
        print(f"Running {strategy_name} on {ticker}")
        print(f"{'='*60}")
        
        if ticker not in self.data:
            print(f"Error: No data for {ticker}")
            return None
        
        data = self.data[ticker].copy()
        
        # Apply strategy
        if strategy_name == "SMA_Crossover":
            strategy = MovingAverageCrossover(params)
        elif strategy_name == "RSI":
            strategy = RSIStrategy(params)
        elif strategy_name == "MACD":
            strategy = MACDStrategy(params)
        else:
            print(f"Unknown strategy: {strategy_name}")
            return None
        
        # Generate signals
        signals = strategy.generate_signals(data)
        
        # Apply risk management
        signals = self.risk_manager.apply_position_sizing(signals)
        
        # Backtest
        results = self.backtester.run(data, signals)
        
        # Analyze performance
        analyzer = PerformanceAnalyzer()
        metrics = analyzer.calculate_metrics(results)
        
        # Store results
        key = f"{ticker}_{strategy_name}"
        self.results[key] = {
            'data': data,
            'signals': signals,
            'results': results,
            'metrics': metrics
        }
        
        # Print summary
        self.print_summary(metrics, ticker, strategy_name)
        
        return results
    
    def print_summary(self, metrics, ticker, strategy):
        """Print performance summary"""
        print(f"\n{ticker} - {strategy} Performance:")
        print(f"{'─'*60}")
        print(f"Total Return:        {metrics['total_return']:.2%}")
        print(f"Sharpe Ratio:        {metrics['sharpe_ratio']:.2f}")
        print(f"Max Drawdown:        {metrics['max_drawdown']:.2%}")
        print(f"Win Rate:            {metrics['win_rate']:.2%}")
        print(f"Profit Factor:       {metrics['profit_factor']:.2f}")
        print(f"Total Trades:        {metrics['total_trades']}")
        print(f"Avg Win:             {metrics['avg_win']:.2%}")
        print(f"Avg Loss:            {metrics['avg_loss']:.2%}")
        
    def compare_strategies(self):
        """Compare all executed strategies"""
        print(f"\n{'='*80}")
        print("STRATEGY COMPARISON")
        print(f"{'='*80}")
        
        comparison_df = pd.DataFrame([
            {
                'Strategy': key,
                'Return': self.results[key]['metrics']['total_return'],
                'Sharpe': self.results[key]['metrics']['sharpe_ratio'],
                'Max DD': self.results[key]['metrics']['max_drawdown'],
                'Win Rate': self.results[key]['metrics']['win_rate']
            }
            for key in self.results
        ])
        
        print(comparison_df.to_string(index=False))
        return comparison_df
    
    def generate_report(self, output_path='reports/'):
        """Generate comprehensive HTML report"""
        print(f"\nGenerating detailed report...")
        self.visualizer.create_report(self.results, output_path)
        print(f"✓ Report saved to {output_path}")

def main():
    """Main execution function"""
    print("="*80)
    print("ALGORITHMIC TRADING SYSTEM v2.0")
    print("="*80)
    
    # Configuration
    config = {
        'tickers': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
        'start_date': '2015-01-01',
        'end_date': '2024-12-01',
        'risk_params': {
            'max_position_size': 0.2,
            'stop_loss': 0.02,
            'take_profit': 0.05,
            'max_drawdown': 0.15
        },
        'strategies': [
            {'name': 'SMA_Crossover', 'params': {'short': 50, 'long': 200}},
            {'name': 'RSI', 'params': {'period': 14, 'oversold': 30, 'overbought': 70}},
            {'name': 'MACD', 'params': {'fast': 12, 'slow': 26, 'signal': 9}}
        ]
    }
    
    # Initialize system
    system = TradingSystem(config)
    
    # Load data
    system.load_data(config['tickers'], config['start_date'], config['end_date'])
    
    # Run strategies on all tickers
    for ticker in config['tickers'][:2]:  # Run on first 2 for demo
        for strategy_config in config['strategies']:
            system.run_strategy(
                strategy_config['name'],
                ticker,
                strategy_config['params']
            )
    
    # Compare results
    comparison = system.compare_strategies()
    
    # Generate report
    system.generate_report()
    
    print("\n" + "="*80)
    print("EXECUTION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()