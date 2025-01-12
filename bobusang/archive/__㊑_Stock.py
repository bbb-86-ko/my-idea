import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Streamlit Layout
st.title("Stock Analysis App with yFinance")
st.sidebar.header("User Input")

# User Input
ticker_symbol = st.sidebar.text_input("Enter Ticker Symbol (e.g., AAPL, MSFT):", "AAPL")
data_period = st.sidebar.selectbox("Select Data Period:", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"])
data_interval = st.sidebar.selectbox("Select Data Interval:", ["1d", "5d", "1wk", "1mo", "3mo"])

# Fetching Data
stock_data = yf.Ticker(ticker_symbol)
# st.write(stock_data)

# Display Basic Info
st.header("Company Information")
info = stock_data.info
st.write({
    "Name": info.get("longName", "N/A"),
    "Sector": info.get("sector", "N/A"),
    "Industry": info.get("industry", "N/A"),
    "Market Cap": f"${info.get('marketCap', 'N/A'):,}" if info.get("marketCap") else "N/A",
    "Website": info.get("website", "N/A"),
})

# Display Stock Data
st.header("Historical Stock Data")
df = stock_data.history(period=data_period, interval=data_interval)
st.write(df)

# Plot Stock Price
st.header("Stock Price Chart")
st.line_chart(df["Close"])

# Display Dividends and Splits
st.header("Dividends and Splits")
dividends = stock_data.dividends
splits = stock_data.splits
st.write("Dividends", dividends)
st.write("Stock Splits", splits)

# Financials
st.header("Financial Data")
st.write("Income Statement")
st.write(stock_data.financials)

st.write("Balance Sheet")
st.write(stock_data.balance_sheet)

st.write("Cash Flow")
st.write(stock_data.cashflow)

# Recommendations
st.header("Analyst Recommendations")
recommendations = stock_data.recommendations
if recommendations is not None:
    st.write(recommendations)
else:
    st.write("No recommendations available.")

# News
st.header("News")
news = stock_data.news
# st.write(news)
if news:
    for article in news:
        st.write(f"**{article['content']['title']}**")
        st.write(article['content']['canonicalUrl']['url'])
else:
    st.write("No news available.")
