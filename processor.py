import pandas as pd
import yfinance as yf
import numpy as np

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
    sentiment_df = pd.read_csv('rolling_sentiment.csv', parse_dates=['date'])
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
    final_df.to_csv('sentiment_signals.csv', index=False)
    print("Pipeline complete: Price data merged and rolling averages calculated.")
