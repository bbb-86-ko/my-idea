import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

# Streamlit 제목 및 설명
st.title("주식 데이터 시각화 및 급등 전조 시그널 탐지")
st.markdown("Streamlit을 이용한 주식 데이터 분석 도구입니다.")

st.sidebar.header("Settings")

# 사용자 입력
ticker = st.sidebar.text_input("종목 티커 입력 (예: AAPL, TSLA, AMZN)", "AAPL")
start_date = st.sidebar.date_input("시작 날짜", pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("종료 날짜", pd.to_datetime("today"))
volume_threshold = st.sidebar.slider("거래량 증가율 임계값 (%)", 10, 100, 50)
price_change_threshold = st.sidebar.slider("주가 변동률 임계값 (%)", 5, 50, 10)

# 데이터 가져오기
if st.sidebar.button("데이터 가져오기"):
    try:
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        stock_data["Price Change (%)"] = stock_data["Close"].pct_change() * 100
        stock_data["Volume Change (%)"] = stock_data["Volume"].pct_change() * 100

        # 이동평균 계산 (단기: 5일, 장기: 20일)
        stock_data["SMA_5"] = stock_data["Close"].rolling(window=5).mean()
        stock_data["SMA_20"] = stock_data["Close"].rolling(window=20).mean()

        # 급등 전조 시그널 조건
        stock_data["Signal"] = (
            (stock_data["Volume Change (%)"] > volume_threshold) &  # 거래량 급증
            (stock_data["Price Change (%)"] > price_change_threshold) &  # 주가 급등
            (stock_data["SMA_5"] > stock_data["SMA_20"])  # 단기 이동평균선이 장기 이동평균선 위
        )

        # 급등 전조 데이터 필터링
        pre_signal_data = stock_data[stock_data["Signal"]]

        # 데이터 시각화
        st.subheader(f"{ticker} 주가 데이터")
        st.line_chart(stock_data["Close"])

        st.subheader(f"{ticker} 거래량 데이터")
        st.line_chart(stock_data["Volume"])

        st.subheader("급등 전조 시그널 탐지 결과")
        if not pre_signal_data.empty:
            st.write(pre_signal_data[["Close", "Volume", "Price Change (%)", "Volume Change (%)", "SMA_5", "SMA_20"]])
            st.markdown(f"### 🔍 **{len(pre_signal_data)}개의 급등 전조 시그널 발견!**")
        else:
            st.write("급등 전조 시그널이 없습니다.")

        # 추가 시각화
        st.subheader("급등 전조 구간 강조")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(stock_data.index, stock_data["Close"], label="Close Price", color="blue")
        ax.plot(stock_data.index, stock_data["SMA_5"], label="SMA 5", color="orange", linestyle="--")
        ax.plot(stock_data.index, stock_data["SMA_20"], label="SMA 20", color="green", linestyle="--")
        ax.scatter(pre_signal_data.index, pre_signal_data["Close"], color="red", label="Pre-Signal", marker="o")
        ax.legend()
        st.pyplot(fig)

        # TODO 주가 정보 + 뉴스 => 분석

    except Exception as e:
        st.error(f"데이터를 가져오는데 실패했습니다: {e}")
