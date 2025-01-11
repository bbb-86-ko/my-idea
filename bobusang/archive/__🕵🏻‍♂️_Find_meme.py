import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Streamlit 제목 및 설명
st.title("주식 데이터 시각화 및 급등 종목 탐지")
st.markdown("Streamlit을 이용한 주식 데이터 분석 도구입니다.")

# 사용자 입력
ticker = st.text_input("종목 티커 입력 (예: AAPL, TSLA, AMZN)", "AAPL")
start_date = st.date_input("시작 날짜", pd.to_datetime("2023-01-01"))
end_date = st.date_input("종료 날짜", pd.to_datetime("today"))
volume_threshold = st.slider("거래량 증가율 임계값 (%)", 10, 100, 50)
price_change_threshold = st.slider("주가 변동률 임계값 (%)", 5, 50, 10)

# 데이터 가져오기
if st.button("데이터 가져오기"):
    try:
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        stock_data["Price Change (%)"] = stock_data["Close"].pct_change() * 100
        stock_data["Volume Change (%)"] = stock_data["Volume"].pct_change() * 100

        print(stock_data)

        # 급등 종목 필터링
        filtered_data = stock_data[
            (stock_data["Volume Change (%)"] > volume_threshold) &
            (stock_data["Price Change (%)"] > price_change_threshold)
        ]

        # 데이터 시각화
        st.subheader(f"{ticker} 주가 데이터")
        st.line_chart(stock_data["Close"])

        st.subheader(f"{ticker} 거래량 데이터")
        st.line_chart(stock_data["Volume"])

        st.subheader("급등 종목 필터링 결과")
        if not filtered_data.empty:
            st.write(filtered_data)
            st.markdown(f"### 📈 **{len(filtered_data)}개의 급등 데이터 발견!**")
        else:
            st.write("급등 종목이 없습니다.")

        # 추가 시각화
        st.subheader("급등 구간 강조")
        fig, ax = plt.subplots()
        ax.plot(stock_data.index, stock_data["Close"], label="Close Price", color="blue")
        ax.scatter(filtered_data.index, filtered_data["Close"], color="red", label="Significant Increase")
        ax.legend()
        st.pyplot(fig)

    except Exception as e:
        st.error(f"데이터를 가져오는데 실패했습니다: {e}")
