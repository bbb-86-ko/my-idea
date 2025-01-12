import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import praw
import tweepy

# Function to get trending stocks from Reddit using PRAW (Reddit API)
def get_reddit_trending_stocks_with_praw(subreddit, query):
    try:
        reddit = praw.Reddit(
            client_id="your_client_id",
            client_secret="your_client_secret",
            user_agent="your_user_agent"
        )
        mentions = {}
        for comment in reddit.subreddit(subreddit).search(query, limit=100):
            for word in comment.body.split():
                if word.isupper() and len(word) <= 5:
                    mentions[word] = mentions.get(word, 0) + 1
        return pd.DataFrame(mentions.items(), columns=['Ticker', 'Mentions']).sort_values(by='Mentions', ascending=False)
    except Exception as e:
        st.error(f"Failed to fetch data from Reddit: {e}")
        return pd.DataFrame()

# Function to get trending stocks from Twitter (X) using Tweepy v2 API
def get_twitter_trending_stocks_v2(query, count=100):
    try:
        client = tweepy.Client(bearer_token="your_bearer_token")
        response = client.search_recent_tweets(query=query, max_results=count, tweet_fields=["text"])
        mentions = {}
        if response.data:
            for tweet in response.data:
                for word in tweet.text.split():
                    if word.startswith('$') and len(word) <= 6:
                        ticker = word[1:].upper()
                        mentions[ticker] = mentions.get(ticker, 0) + 1
        return pd.DataFrame(mentions.items(), columns=['Ticker', 'Mentions']).sort_values(by='Mentions', ascending=False)
    except Exception as e:
        st.error(f"Failed to fetch data from Twitter: {e}")
        return pd.DataFrame()

# Function to get trending stocks from StockTwits with User-Agent header
def get_stocktwits_trending_stocks_with_headers():
    try:
        url = "https://api.stocktwits.com/api/2/trending/symbols.json"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get('symbols', [])
            trending = []
            for symbol in data:
                trending.append({
                    "Ticker": symbol['symbol'],
                    "Title": symbol['title'],
                    "Watchlist Count": symbol['watchlist_count']
                })
            return pd.DataFrame(trending)
        else:
            st.error(f"Failed to fetch data from StockTwits: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to fetch data from StockTwits: {e}")
        return pd.DataFrame()

# Streamlit UI
st.title("Trending Stocks Monitor")
st.write("Monitor trending stocks from Reddit, Twitter, and StockTwits in real-time.")

# Sidebar for User inputs
st.sidebar.header("User Inputs")
subreddit = st.sidebar.text_input("Enter Reddit Subreddit (e.g., wallstreetbets):", "wallstreetbets")

ticker_list = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NFLX", "NVDA", "INTC", "AMD"]
selected_ticker = st.sidebar.selectbox("Select Ticker Symbol:", ticker_list)
fetch_twitter = st.sidebar.checkbox("Fetch data from Twitter (X)?", value=True)
fetch_reddit = st.sidebar.checkbox("Fetch data from Reddit?", value=True)
fetch_stocktwits = st.sidebar.checkbox("Fetch data from StockTwits?", value=True)

if st.sidebar.button("Fetch Trending Stocks"):
    combined_data = pd.DataFrame()

    if fetch_reddit:
        st.write("Fetching data from Reddit...")
        reddit_data = get_reddit_trending_stocks_with_praw(subreddit, selected_ticker)
        if not reddit_data.empty:
            reddit_data['Source'] = 'Reddit'
            combined_data = pd.concat([combined_data, reddit_data], ignore_index=True)

    if fetch_twitter:
        st.write("Fetching data from Twitter...")
        twitter_data = get_twitter_trending_stocks_v2(selected_ticker)
        if not twitter_data.empty:
            twitter_data['Source'] = 'Twitter'
            combined_data = pd.concat([combined_data, twitter_data], ignore_index=True)

    if fetch_stocktwits:
        st.write("Fetching data from StockTwits...")
        stocktwits_data = get_stocktwits_trending_stocks_with_headers()
        if not stocktwits_data.empty:
            stocktwits_data['Source'] = 'StockTwits'
            combined_data = pd.concat([combined_data, stocktwits_data[['Ticker', 'Title', 'Watchlist Count']]], ignore_index=True)

    if not combined_data.empty:
        st.write("### Combined Trending Stocks")
        st.dataframe(combined_data.sort_values(by='Mentions', ascending=False))
    else:
        st.write("No trending stocks found.")
