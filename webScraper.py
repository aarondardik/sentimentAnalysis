from bs4 import BeautifulSoup
import requests
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime



tickers = {
    'AAPL': 'Apple Inc.',
    'XOM': 'Exxon',
    'TSLA': 'Tesla',
    'MSFT': 'Microsoft',
    'NVDA': 'Nvidia',
    'AMZN': 'Amazon',
    'GOOGL' : 'Alphabet Inc.',
    'AVGO' : 'Broadcom',
    'BRK.B' : 'Berkshire Hathaway',
    'WMT' : 'Walmart',
    'JPM' : 'JPMorgan Chase',
    'LLY' : 'Lilly (Eli)',
    'V' : 'Visa Inc.',
    'JNJ' : 'Johnson & Johnson',
    'MU' : 'Micron Technology',
    'ORCL' : 'Oracle Corporation',
    'MA' : 'Mastercard',
    'AMD' : 'Advanced Micro Devices',
    'COST' : 'Costco',
    'NFLX' : 'Netflix',
    'BAC' : 'Bank of America',
    'CAT' : 'Caterpillar Inc.',
    'ABBV' : 'Abbvie',
    'CVX' : 'Chevron Corporation',
    'PLTR' : 'Palantir Technologies',
    'HD' : 'Home Depot',
    'INTC' : 'Intel',
    'PG' : 'Procter & Gamble',
    'CSCO' : 'Cisco',
    'LRCX' : 'Lam Research',
    'KO' : 'Coca-Cola Company',
    'GE' : 'GE Aerospace',
    'AMAT' : 'Applied Materials',
    'MS' : 'Morgan Stanley',
    'UNH' : 'UnitedHealth Group',
    'MRK' : 'Merck & Co.',
    'GS' : 'Goldman Sachs',
    'GEV' : 'GE Vernova',
    'RTX' : 'RTX Corporation'
}

# Initialize the sentiment analyzer efficiently
try:
    sia = SentimentIntensityAnalyzer()
    print("\nNLTK Already here.\n")
except LookupError:
    nltk.download('vader_lexicon', quiet=True)
    sia = SentimentIntensityAnalyzer()





def process_ticker_sentiment(ticker):
    """Fetches RSS feed, parses headlines, and calculates sentiment."""
    url = f"https://news.google.com/rss/search?q={ticker}+stock+news&hl=en-US&gl=US&ceid=US:en"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        if not items:
            return None

        # Analyze each headline and find the average score
        scores = []
        for item in items:
            headline = item.title.text
            score = sia.polarity_scores(headline)['compound']
            scores.append(score)
        
        # Calculate the average sentiment for the ticker today
        avg_score = sum(scores) / len(scores)
        
        return {
            'ticker': ticker,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'avg_sentiment': round(avg_score, 4),
            'article_count': len(items)
        }

    except Exception as e:
        print(f"Error processing {ticker}: {e}")
        return None

# --- EXECUTION ---
daily_results = []

for ticker in tickers:
    print(f"Analyzing {ticker}...")
    result = process_ticker_sentiment(ticker)
    if result:
        daily_results.append(result)

if not daily_results:
    print("No news found today. Skipping CSV update.")
else:
    df = pd.DataFrame(daily_results)
    # Print out today's results
    print("\n--- Daily Sentiment Summary ---")  
    print(df)
    # Save the results to the CSV
    df.to_csv('rolling_sentiment.csv', mode='a', header=not pd.io.common.file_exists('rolling_sentiment.csv'), index=False)



