import pandas as pd
import yfinance as yf
import numpy as np
import os

def calculate_rolling_averages(df):
    #df = pd.read_csv('rolling_sentiment.csv')
    df['3d_avg'] = df.groupby('ticker')['avg_sentiment'].transform(lambda x : x.rolling(3, min_periods=1).mean())
    df['10d_avg'] = df.groupby('ticker')['avg_sentiment'].transform(lambda x : x.rolling(10, min_periods=1).mean())
    df['30d_avg'] = df.groupby('ticker')['avg_sentiment'].transform(lambda x : x.rolling(30, min_periods=1).mean())
    df['60d_avg'] = df.groupby('ticker')['avg_sentiment'].transform(lambda x : x.rolling(60, min_periods=1).mean())
    df['90d_avg'] = df.groupby('ticker')['avg_sentiment'].transform(lambda x : x.rolling(90, min_periods=1).mean())

    return df 
    #tickers = df['ticker'].unique().tolist()
    #prices = yf.download(tickers, period='10d')['Close']

    #df.to_csv('sentiment_signals.csv', index=False)
    #print("Signals updated successfully.")



def process_data():
    print("Files currently in the folder:", os.listdir('.'))
    filename = 'rolling_sentiment.csv'


    # DEBUG: Check if the file even exists
    if not os.path.exists(filename):
        print(f"CRITICAL ERROR: {filename} does not exist!")
        return pd.DataFrame() # Return empty

    sentiment_df = pd.read_csv(filename, parse_dates=['date'])
    print(f"Read {len(sentiment_df)} rows from {filename}")

    # DEBUG: See how many rows we loaded
    print(f"Loaded {len(sentiment_df)} rows from rolling_sentiment.csv")
    
    if sentiment_df.empty:
        print("WARNING: sentiment_df is empty!")
        return sentiment_df


    tickers = sentiment_df['ticker'].unique().tolist()
    price_data = yf.download(tickers, period="90d", interval="1d")
    
    prices = price_data['Close'].stack().reset_index()
    prices.columns = ['date', 'ticker', 'close_price']
    volumes = price_data['Volume'].stack().reset_index()
    volumes.columns = ['date', 'ticker', 'volume']

    merged_df = pd.merge(sentiment_df, prices, on=['date', 'ticker'], how='left')
    merged_df = pd.merge(merged_df, volumes, on=['date', 'ticker'], how='left')

    merged_df = merged_df.sort_values(['ticker', 'date'])
    merged_df['close_price'] = merged_df.groupby('ticker')['close_price'].ffill()

    #merged_df.to_csv('sentiment_signals.csv', index=False)
    return merged_df


if __name__ == "main":
    raw_merged_df = process_data()
    final_df = calculate_rolling_averages(raw_merged_df)

    # 2. THE DEBUG CHECK
    print("--- PIPELINE DEBUG INFO ---")
    if final_df is None:
        print("ERROR: final_df is None!")
    elif final_df.empty:
        print("ERROR: final_df is EMPTY. No data to save.")
    else:
        print(f"SUCCESS: final_df has {len(final_df)} rows and {len(final_df.columns)} columns.")
        print("PREVIEW OF FINAL DATA:")
        print(final_df.head()) # This prints the first 5 rows to the GitHub log



    final_df.to_csv('sentiment_signals.csv', index=False)
    print(f"Successfully saved {len(final_df)} rows to sentiment_signals.csv")
