
import requests
import csv
import time

# Alpha Vantage API details

# key removed 
api_key = "#"
csv_file_path =r"c:\Users\USER\Documents\Python Scripts\tickers.csv"
sma_period = 200
ticker_limit = 2 # Set the limit to the first 100 tickers

def load_tickers_from_csv(file_path, limit=100):
    """Load stock tickers from the first column of a CSV file, limited to the first `limit` entries."""
    tickers = []
    try:
        with open(file_path, mode="r") as file:
            reader = csv.reader(file)
            for idx, row in enumerate(reader):
                if idx >= limit:
                    break
                tickers.append(row[1])  # Assuming tickers are in the sec column
        return tickers
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def get_daily_close_price(symbol):
    """Fetch the latest daily closing price."""
    endpoint = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key
    }
    response = requests.get(endpoint, params=params)
    data = response.json()
    
    if "Time Series (Daily)" in data:
        latest_date = list(data["Time Series (Daily)"].keys())[0]
        close_price = float(data["Time Series (Daily)"][latest_date]["4. close"])
        return close_price, latest_date
    else:
        print(f"Error fetching daily data for {symbol}: {data}")
        return None, None

def get_200_day_sma(symbol):
    """Fetch the 200-day SMA."""
    endpoint = "https://www.alphavantage.co/query"
    params = {
        "function": "SMA",
        "symbol": symbol,
        "interval": "daily",
        "time_period": sma_period,
        "series_type": "close",
        "apikey": api_key
    }
    response = requests.get(endpoint, params=params)
    data = response.json()
    
    if "Technical Analysis: SMA" in data:
        latest_date = list(data["Technical Analysis: SMA"].keys())[0]
        sma_value = float(data["Technical Analysis: SMA"][latest_date]["SMA"])
        return sma_value, latest_date
    else:
        print(f"Error fetching SMA data for {symbol}: {data}")
        return None, None

def monitor_stocks(tickers):
    """Monitor multiple stocks and send alerts if price drops below 200-day SMA."""
    while True:
        for symbol in tickers:
            close_price, price_date = get_daily_close_price(symbol)
            sma_value, sma_date = get_200_day_sma(symbol)

            if close_price and sma_value:
                print(f"\n{symbol} - Latest Close Price ({price_date}): {close_price}")
                print(f"{symbol} - 200-Day SMA ({sma_date}): {sma_value}")
                
                if close_price < sma_value:
                    print(f"ALERT: {symbol} price {close_price} is below the 200-day SMA {sma_value}!")
                else:
                    print(f"{symbol} price is above the 200-day SMA.")
            else:
                print(f"Failed to retrieve data for {symbol}. Retrying...")

        # Wait for a day before checking again
        print("\nWaiting for the next check...")
        time.sleep(86400)  # 86400 seconds = 1 day

# Load tickers from the CSV file with a limit of 100
tickers = load_tickers_from_csv(csv_file_path, ticker_limit)

if tickers:
    print(f"Loaded {len(tickers)} tickers: {tickers}")
    monitor_stocks(tickers)
else:
    print("No tickers found. Please check the CSV file.")
