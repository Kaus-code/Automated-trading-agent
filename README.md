# 📈 Advanced Algorithmic Trading System

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

A professional-grade, modular algorithmic trading system built in Python. This project is designed to backtest, analyze, and optimize trading strategies using historical market data. It features a robust architecture separating data handling, strategy logic, risk management, and performance analytics.

## 🚀 Features

### 🧠 Trading Strategies
The system includes a suite of standard technical analysis strategies:
- **Moving Average Crossover (SMA)**: Captures trends by comparing short-term and long-term averages.
- **RSI (Relative Strength Index)**: Identifies overbought and oversold conditions for mean reversion.
- **MACD (Moving Average Convergence Divergence)**: Momentum tracking using moving averages.
- **Bollinger Bands**: Volatility-based strategy trading mean reversions from band edges.
- **Momentum**: Trend following based on rate of change.
- **Composite Strategy**: A meta-strategy that combines signals from multiple indicators.

### 🛡️ Risk Management
A dedicated `RiskManager` module ensures capital preservation:
- **Position Sizing**: Dynamic sizing using **Kelly Criterion** and Volatility Scaling.
- **Stop Loss & Take Profit**: Automated exit rules to cap losses and secure gains.
- **Drawdown Limits**: Halts trading if portfolio drawdown exceeds safety thresholds.
- **Diversification Checks**: Prevents over-concentration in correlated assets.
- **Value at Risk (VaR)**: Statistical risk measurement.

### 📊 Performance Analytics
Comprehensive `PerformanceAnalyzer` generating institutional-grade metrics:
- **Returns**: Total Return, Annualized Return.
- **Risk-Adjusted**: Sharpe Ratio, Sortino Ratio, Calmar Ratio, Information Ratio.
- **Drawdowns**: Max Drawdown, Average Drawdown Duration.
- **Trade Stats**: Win Rate, Profit Factor, Average Win/Loss.
- **Market Comparison**: Alpha and Beta against the benchmark.

### 📉 Visualization
Automated reporting module (`Visualizer`) that generates:
- **Equity Curves**: Strategy vs. Buy & Hold benchmark.
- **Drawdown Charts**: Visual representation of underwater periods.
- **Reports**: Auto-saved to the `reports/` directory.

---

## � Project Structure

```text
automated trading agent/
├── data/                   # (Updates) Caches downloaded historical data
├── logs/                   # (Updates) Runtime logs
├── reports/                # (Updates) Generated performance plots and metrics
├── tests/                  # Unit tests for system modules
│
├── main.py                 # 🚀 Entry point: Orchestrates the workflow
├── config.yaml             # ⚙️ Configuration parameters (Tickers, Risk, Dates)
├── .env                    # 🔒 Environment variables (API Keys) - excluded from git
├── requirements.txt        # 📦 Project dependencies
│
├── strategies.py           # 🧠 Strategy logic implementation (Strategy Design Pattern)
├── backtester.py           # ⚡ specialized Backtesting engine
├── risk_manager.py         # 🛡️ Risk management and position sizing logic
├── performance_metrics.py  # 📊 Financial metrics calculation
├── portfolio_optimizer.py  # ⚖️ Portfolio allocation logic
├── data_fetcher.py         # 📡 Data interface (yfinance wrapper)
└── visualization.py        # 🎨 Plotting and reporting utilities
```

---

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Kaus-code/Automated-trading-.git
    cd Automated-trading-
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r "automated trading agent/requirements.txt"
    ```

---

## ⚙️ Configuration

The system is highly configurable via `config.yaml`. You can modify:

-   **Universes**: List of stock tickers to trade (e.g., AAPL, MSFT).
-   **Date Range**: Start and End dates for the backtest.
-   **Risk Parameters**:
    -   `max_position_size`: Max capital allocatable to a single trade.
    -   `stop_loss` / `take_profit`: Percentage targets.
    -   `max_drawdown`: Safety switch level.
-   **Strategy Parameters**: Tweak lookback periods (e.g., SMA 50/200, RSI 14).

**Example `config.yaml` snippet:**
```yaml
risk_management:
  max_position_size: 0.2
  stop_loss: 0.02
  take_profit: 0.05

strategies:
  sma_crossover:
    short_window: 50
    long_window: 200
```

---

## 🚀 Usage

To run the trading bot and execute the backtest pipeline:

1.  Navigate to the agent directory:
    ```bash
    cd "automated trading agent"
    ```

2.  Run the main script:
    ```bash
    python main.py
    ```

**What happens next?**
1.  The system loads configuration from `config.yaml`.
2.  `DataFetcher` downloads historical data (default: Yahoo Finance).
3.  The engine iterates through tickers and strategies (SMA, RSI, MACD).
4.  `RiskManager` applies sizing and constraints.
5.  `Backtester` simulates trading execution.
6.  Performance reports and charts are generated in the `reports/` folder.
7.  A summary table is printed to the console.

---

## 📊 Sample Output

After execution, check the `reports/` folder for visual insights:

| Equity Curve | Drawdown Analysis |
|:---:|:---:|
| `AAPL_SMA_Crossover_equity.png` | `AAPL_SMA_Crossover_drawdown.png` |
| Shows strategy growth vs market | Shows depth and duration of losses |

**Console Output Example:**
```text
AAPL - SMA_Crossover Performance:
────────────────────────────────────────────────────────────
Total Return:        145.20%
Sharpe Ratio:        1.85
Max Drawdown:        -12.50%
Win Rate:            58.30%
Profit Factor:       2.10
```

---

## ⚠️ Disclaimer

**Educational Use Only**: This software is for educational purposes. Algorithmic trading involves significant risk. The strategies provided are basic examples and should **not** be used for live trading with real money without extensive modification, testing, and professional financial advice.

---

## 🤝 Contributing

Contributions are welcome!
1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request