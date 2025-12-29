
import yfinance as yf
ticker = "AAPL"
data = yf.download(ticker, start="2020-01-01", end="2020-01-10")
print("Columns:", data.columns)
print("Head:", data.head())
try:
    print("Close column:", data['Close'].head())
except Exception as e:
    print("Error accessing Close:", e)
