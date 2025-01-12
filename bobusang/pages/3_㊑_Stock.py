import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from yfinance import shared

# 타임아웃 설정
requests_session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=3)
requests_session.mount('https://', adapter)
requests_session.mount('http://', adapter)
shared._requests = requests_session

# Streamlit Layout
st.title("㊑ Stock Information")
st.sidebar.header("User Input")

# Predefined Ticker List
ticker_list = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NFLX", "NVDA", "INTC", "AMD"]
selected_ticker = st.sidebar.selectbox("Select Ticker Symbol:", ticker_list)
data_period = st.sidebar.selectbox("Select Data Period:", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"])
data_interval = st.sidebar.selectbox("Select Data Interval:", ["1d", "5d", "1wk", "1mo", "3mo"])

# 캐싱된 yf.Ticker 객체
@st.cache_resource(ttl=60)  # 60초 동안 캐싱
def get_ticker_object(ticker):
    return yf.Ticker(ticker)

def display_company_info(basic_info):
    st.header("Company Information")
    # 왼쪽: 회사 이름 및 산업 정보, 시가총액 및 웹사이트
    
    st.markdown(f"- **Name**: {basic_info.get('Name', 'N/A')}")
    st.markdown(f"- **Sector**: {basic_info.get('Sector', 'N/A')}")
    st.markdown(f"- **Industry**: {basic_info.get('Industry', 'N/A')}")
    st.markdown(f"- **Market Cap**: {basic_info.get('Market Cap', 'N/A')}")
    if basic_info.get("Website", "N/A") != "N/A":
        st.markdown(f"- **Website**: {basic_info.get('Website')}")
    else:
        st.markdown("- **Website**: N/A")

# 데이터 추출 함수들
def get_basic_info(ticker_object):
    info = ticker_object.info
    return {
        "Name": info.get("longName", "N/A"),
        "Sector": info.get("sector", "N/A"),
        "Industry": info.get("industry", "N/A"),
        "Market Cap": f"${info.get('marketCap', 'N/A'):,}" if info.get("marketCap") else "N/A",
        "Website": info.get("website", "N/A"),
    }

def get_history_data(ticker_object, period, interval):
    return ticker_object.history(period=period, interval=interval)

def get_dividends_data(ticker_object):
    return ticker_object.dividends

def get_splits_data(ticker_object):
    return ticker_object.splits

def get_financials_data(ticker_object):
    return ticker_object.financials

def get_news_data(ticker_object):
    return ticker_object.news

# 메인 앱 로직
if st.sidebar.button("get data"):
    # yf.Ticker 객체 가져오기
    ticker_object = get_ticker_object(selected_ticker)

# Basic Info
    with st.spinner("Loading Data..."):
        try:
            basic_info = get_basic_info(ticker_object)
            display_company_info(basic_info)
        except Exception as e:
            st.error(f"Error fetching company information: {e}")

    # Historical Data
    with st.spinner("Loading Data..."):
        st.header("Historical Stock Data")
        try:
            df = get_history_data(ticker_object, data_period, data_interval)
            st.write(df)
            st.line_chart(df["Close"])
        except Exception as e:
            st.error(f"Error fetching historical data: {e}")

    # Dividends and Splits
    with st.spinner("Loading Data..."):
        st.header("Dividends and Splits")
        try:
            dividends = get_dividends_data(ticker_object)
            splits = get_splits_data(ticker_object)
            st.write("Dividends", dividends)
            st.write("Stock Splits", splits)
        except Exception as e:
            st.error(f"Error fetching dividends or splits: {e}")

    # Financials
    with st.spinner("Loading Data..."):
        st.header("Financial Data")
        try:
            financials = get_financials_data(ticker_object)
            st.write("Income Statement")
            st.write(financials)
        except Exception as e:
            st.error(f"Error fetching financial data: {e}")

    # News
    st.header("News")
    with st.spinner("Loading Data..."):
        try:
            news = get_news_data(ticker_object)
            if news:
                for article in news:
                    st.write(f"**{article['content']['title']}**")
                    st.write(article['content']['canonicalUrl']['url'])
            else:
                st.write("No news available.")
        except Exception as e:
            st.error(f"Error fetching news: {e}")
