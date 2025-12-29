
"""
Visualization Module
Generates charts and reports for strategy performance
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

class Visualizer:
    """Create visualizations for trading results"""
    
    def __init__(self):
        sns.set(style="darkgrid")
        
    def create_report(self, results_dict, output_path='reports/'):
        """
        Generate a performance report with charts
        """
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
        for key, data in results_dict.items():
            self._plot_equity_curve(data['results'], key, output_path)
            self._plot_drawdown(data['results'], key, output_path)
    
    def _plot_equity_curve(self, df, label, output_path):
        """Plot equity curve"""
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['Cumulative_Strategy_Return'], label='Strategy')
        plt.plot(df.index, df['Cumulative_Market_Return'], label='Market', alpha=0.7)
        plt.title(f'Equity Curve - {label}')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Return')
        plt.legend()
        plt.savefig(f"{output_path}/{label}_equity.png")
        plt.close()
        
    def _plot_drawdown(self, df, label, output_path):
        """Plot drawdown"""
        if 'Drawdown' in df.columns:
            plt.figure(figsize=(12, 4))
            plt.fill_between(df.index, df['Drawdown'], 0, color='red', alpha=0.3)
            plt.plot(df.index, df['Drawdown'], color='red', alpha=0.6)
            plt.title(f'Drawdown - {label}')
            plt.ylabel('Drawdown')
            plt.xlabel('Date')
            plt.savefig(f"{output_path}/{label}_drawdown.png")
            plt.close()
