import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

def calculate_signals(data, short_window=20, long_window=50, volume_window=20):
    # 이동평균선 계산
    data['Short_MA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window).mean()


    # 거래량 이동평균선 계산
    data['Volume_MA'] = data['Volume'].rolling(window=volume_window).mean()

    # # NaN 값 제거
    data = data.dropna()
    
    # # 상승 시그널 탐지
    # data['Signal'] = (data['Short_MA'] > data['Long_MA']) & (data['Volume'] > data['Volume_MA'])

    # return data
    # 멀티인덱스 제거 (열 이름 단순화)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(1)

    # 상승 시그널 탐지
    data['Signal'] = (data['Short_MA'] > data['Long_MA']) & (data['Volume'] > data['Volume_MA'])

    return data

def plot_data(data):
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # 주가 및 이동평균선
    ax1.plot(data.index, data['Close'], label='Close', alpha=0.6)
    ax1.plot(data.index, data['Short_MA'], label='Short MA (20)', linestyle='--')
    ax1.plot(data.index, data['Long_MA'], label='Long MA (50)', linestyle='--')
    ax1.set_ylabel('Price')
    ax1.legend(loc='upper left')

    # 거래량
    ax2 = ax1.twinx()
    ax2.bar(data.index, data['Volume'], color='gray', alpha=0.3, label='Volume')
    ax2.plot(data.index, data['Volume_MA'], label='Volume MA (20)', color='orange', linestyle='--')
    ax2.set_ylabel('Volume')
    ax2.legend(loc='upper right')

    # 상승 시그널
    signal_dates = data[data['Signal']].index
    ax1.scatter(signal_dates, data.loc[signal_dates, 'Close'], color='red', label='Buy Signal', marker='^')

    fig.tight_layout()
    return fig

# Streamlit 앱 구성
st.title("Volume & Moving Average Signal Finder")
st.sidebar.header("Settings")

# 사용자 입력 받기
symbol = st.sidebar.text_input("Stock Ticker", value="AAPL")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-01-01"))

short_window = st.sidebar.slider("Short Moving Average Window", min_value=5, max_value=50, value=20)
long_window = st.sidebar.slider("Long Moving Average Window", min_value=20, max_value=200, value=50)
volume_window = st.sidebar.slider("Volume Moving Average Window", min_value=5, max_value=50, value=20)

# 데이터 가져오기
try:
    data = yf.download(symbol, start=start_date, end=end_date)
    if data.empty:
        st.error("No data available for the given ticker and date range.")
    else:
        # 인덱스 정렬
        data.sort_index(inplace=True)

        # 시그널 계산
        data = calculate_signals(data, short_window, long_window, volume_window)
        print(data)

        # 결과 출력
        st.write(f"### {symbol} Data")
        st.write(data.tail())

        # 차트 출력
        st.write("### Price and Volume Chart")
        fig = plot_data(data)
        st.pyplot(fig)
except Exception as e:
    st.error(f"An error occurred: {e}")
