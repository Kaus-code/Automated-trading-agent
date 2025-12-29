
import yfinance as yf
import pandas as pd

class DataFetcher:
    """
    Class to fetch historical stock data.
    """
    def __init__(self):
        pass

    def fetch_stock_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches historical stock data from Yahoo Finance.
        """
        print(f"Fetching data for {ticker} from {start_date} to {end_date}...")
        try:
            data = yf.download(ticker, start=start_date, end=end_date)
            
            if data.empty:
                print(f"No data found for {ticker}.")
                return pd.DataFrame()
                
            return data
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return pd.DataFrame()
