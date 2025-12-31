"""
Main Trading Strategy Application
Author: Kaustubh Sharma 
Date: January 2026
Description: Comprehensive algorithmic trading system with multiple strategies
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yaml
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
        
        # Initialize Backtester with "Paper Money" settings from config
        self.initial_capital = config.get('portfolio', {}).get('initial_capital', 10000)
        self.commission = config.get('capital', {}).get('commission', 1.0)
        self.backtester = Backtester(initial_capital=self.initial_capital, commission_fee=self.commission)
        
        self.risk_manager = RiskManager(config.get('risk_management', config.get('risk_params', {})))
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
                print(f"[OK] {ticker}: {len(df)} days loaded")
            except Exception as e:
                print(f"[FAIL] {ticker}: Failed - {str(e)}")
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
        
        # Apply strategy (case-insensitive)
        strat_name_upper = strategy_name.upper()
        if strat_name_upper in ["SMA_CROSSOVER", "SMA"]:
            strategy = MovingAverageCrossover(params)
        elif strat_name_upper == "RSI":
            strategy = RSIStrategy(params)
        elif strat_name_upper == "MACD":
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
        """Print performance summary with Paper Money metrics"""
        print(f"\n{ticker} - {strategy} Performance:")
        print(f"{'─'*60}")
        
        # Paper Money Reporting
        # Use metrics['total_return'] which is (Final_Equity / Initial_Capital) - 1
        total_return_pct = metrics.get('total_return', 0)
        final_balance = self.initial_capital * (1 + total_return_pct)
        net_profit = final_balance - self.initial_capital
        
        print(f"Starting Capital:    ${self.initial_capital:,.2f}")
        print(f"Ending Balance:      ${final_balance:,.2f}")
        print(f"Net Paper Profit:    ${net_profit:,.2f} ({total_return_pct:.2%})")
        print(f"{'─'*60}")
        print(f"Sharpe Ratio:        {metrics.get('sharpe_ratio', 0):.2f}")
        print(f"Max Drawdown:        {metrics.get('max_drawdown', 0):.2%}")
        print(f"Win Rate:            {metrics.get('win_rate', 0):.2%}")
        print(f"Profit Factor:       {metrics.get('profit_factor', 0):.2f}")
        print(f"Total Trades:        {metrics.get('total_trades', 0)}")
        
    def compare_strategies(self):
        """Compare all executed strategies"""
        print(f"\n{'='*80}")
        print("STRATEGY COMPARISON")
        print(f"{'='*80}")
        
        comparison_df = pd.DataFrame([
            {
                'Strategy': key,
                'Return': self.results[key]['metrics'].get('total_return', 0),
                'Sharpe': self.results[key]['metrics'].get('sharpe_ratio', 0),
                'Max DD': self.results[key]['metrics'].get('max_drawdown', 0),
                'Win Rate': self.results[key]['metrics'].get('win_rate', 0)
            }
            for key in self.results
        ])
        
        print(comparison_df.to_string(index=False))
        return comparison_df
    
    def generate_report(self, output_path='reports/'):
        """Generate comprehensive HTML report"""
        print(f"\nGenerating detailed report...")
        self.visualizer.create_report(self.results, output_path)
        print(f"[OK] Report saved to {output_path}")

def main():
    """Main execution function"""
    print("="*80)
    print("ALGORITHMIC TRADING SYSTEM v2.0")
    print("="*80)
    
    # Load Configuration from config.yaml
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print("[OK] Configuration loaded from config.yaml")
    except Exception as e:
        print(f"! Using default configuration (Error: {e})")
        config = {
            'tickers': ['AAPL', 'MSFT'],
            'date_range': {'start': '2015-01-01', 'end': '2024-12-01'},
            'portfolio': {'initial_capital': 10000, 'currency': 'USD'},
            'capital': {'commission': 1.0},
            'risk_management': {
                'max_position_size': 0.2,
                'stop_loss': 0.02,
                'take_profit': 0.05
            },
            'strategies': [
                {'name': 'SMA_Crossover', 'params': {'short': 50, 'long': 200}},
            ]
        }
    
    # Initialize system
    system = TradingSystem(config)
    
    # Load data
    system.load_data(
        config['tickers'], 
        config.get('date_range', {}).get('start', '2015-01-01'), 
        config.get('date_range', {}).get('end', '2024-12-01')
    )
    
    # Run strategies on tickers
    tickers_to_test = config['tickers'][:2] # Run on first 2 for demonstration
    
    # Mapping strategy names from config to the names used in run_strategy
    # config.yaml has 'sma_crossover', 'rsi', 'macd'
    # main.py expects 'SMA_Crossover', 'RSI', 'MACD'
    for ticker in tickers_to_test:
        if 'strategies' in config and isinstance(config['strategies'], dict):
            # If strategies are a dict in config.yaml
            for strat_name, strat_params in config['strategies'].items():
                system.run_strategy(strat_name.upper(), ticker, strat_params)
        elif 'strategies' in config and isinstance(config['strategies'], list):
            # If strategies are a list (from our fallback)
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