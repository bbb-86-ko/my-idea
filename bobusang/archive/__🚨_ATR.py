# import streamlit as st
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt

# # Streamlit 앱 설정
# st.title("ATR 기반 변동성 매매 전략")
# st.markdown("삼성전자 데이터를 활용한 ATR 기반 매매 신호 생성 및 분석")

# # 파일 업로드
# uploaded_file = st.file_uploader("CSV 파일 업로드 (OHLC 데이터)", type=["csv"])
# if uploaded_file:
#     # 데이터 로드
#     data = pd.read_csv(uploaded_file)
#     st.write("업로드된 데이터:", data)

#     # ATR 계산
#     st.subheader("ATR 계산")
#     data['TR'] = np.maximum(data['고가'] - data['저가'], 
#                             np.maximum(abs(data['고가'] - data['종가'].shift(1)), 
#                                        abs(data['저가'] - data['종가'].shift(1))))
#     data['ATR'] = data['TR'].rolling(window=14).mean()

#     st.write("ATR 계산 결과:", data[['고가', '저가', '종가', 'ATR']])

#     # 매수/매도 신호 생성
#     st.subheader("매수/매도 신호 생성")
#     data['Buy_Signal'] = (data['종가'] > data['고가'].shift(1)) & ((data['종가'] - data['고가'].shift(1)) > data['ATR'] * 1.5)
#     data['Sell_Signal'] = (data['종가'] < data['저가'].shift(1)) & ((data['저가'].shift(1) - data['종가']) > data['ATR'] * 1.5)

#     st.write("신호 데이터:", data[['종가', 'ATR', 'Buy_Signal', 'Sell_Signal']])

#     # 매매 신호 시각화
#     st.subheader("매매 신호 시각화")
#     fig, ax = plt.subplots(figsize=(12, 6))
#     ax.plot(data['종가'], label="종가", color="blue")
#     ax.plot(data['ATR'], label="ATR", color="orange", linestyle="--")
#     ax.scatter(data.index[data['Buy_Signal']], data['종가'][data['Buy_Signal']], marker="^", color="green", label="매수 신호")
#     ax.scatter(data.index[data['Sell_Signal']], data['종가'][data['Sell_Signal']], marker="v", color="red", label="매도 신호")
#     ax.set_title("ATR 및 매매 신호")
#     ax.set_xlabel("날짜")
#     ax.set_ylabel("가격")
#     ax.legend()
#     st.pyplot(fig)

#     # 손절/익절 계산
#     st.subheader("손절/익절 시뮬레이션")
#     data['Stop_Loss'] = data['종가'] - data['ATR'] * 1.5
#     data['Take_Profit'] = data['종가'] + data['ATR'] * 2

#     # 전략 결과 요약
#     st.subheader("전략 결과 요약")
#     buy_signals = data[data['Buy_Signal']]
#     sell_signals = data[data['Sell_Signal']]
#     st.write(f"매수 신호 발생 수: {len(buy_signals)}")
#     st.write(f"매도 신호 발생 수: {len(sell_signals)}")

#     # 성과 평가
#     st.subheader("성과 분석")
#     results = []
#     for index, row in buy_signals.iterrows():
#         entry_price = row['종가']
#         stop_loss = row['Stop_Loss']
#         take_profit = row['Take_Profit']
#         for i in range(index + 1, len(data)):
#             if data.loc[i, '종가'] <= stop_loss:
#                 results.append({'Type': 'Loss', 'Price': stop_loss})
#                 break
#             elif data.loc[i, '종가'] >= take_profit:
#                 results.append({'Type': 'Profit', 'Price': take_profit})
#                 break

#     results_df = pd.DataFrame(results)
#     if not results_df.empty:
#         st.write("손익 분석 결과:")
#         st.write(results_df)
#         st.write("손익 비율:")
#         st.write(results_df['Type'].value_counts())
#         st.write("총 수익:", results_df[results_df['Type'] == 'Profit']['Price'].sum() - 
#                                 results_df[results_df['Type'] == 'Loss']['Price'].sum())
#     else:
#         st.write("성과 데이터가 없습니다.")

# else:
#     st.warning("CSV 파일을 업로드해 주세요.")


import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# Streamlit 앱 제목 및 설명
st.title("주식 데이터 분석 및 ATR 기반 변동성 매매 전략")
st.markdown("Streamlit을 활용하여 급등 종목 탐색과 ATR 기반 변동성 매매 전략을 구현합니다.")

# 사용자 입력
ticker = st.text_input("종목 티커 입력 (예: AAPL, TSLA, AMZN)", "AAPL")
start_date = st.date_input("시작 날짜", pd.to_datetime("2023-01-01"))
end_date = st.date_input("종료 날짜", pd.to_datetime("today"))
volume_threshold = st.slider("거래량 증가율 임계값 (%)", 10, 100, 50)
price_change_threshold = st.slider("주가 변동률 임계값 (%)", 5, 50, 10)

# 데이터 다운로드
if st.button("데이터 가져오기"):
    try:
        # Yahoo Finance 데이터 다운로드
        data = yf.download(ticker, start=start_date, end=end_date)
        data['Price Change (%)'] = data['Close'].pct_change() * 100
        data['Volume Change (%)'] = data['Volume'].pct_change() * 100
        

        
        # ATR 계산
        st.subheader("ATR 계산")
        data['TR'] = np.maximum(data['High'] - data['Low'], 
                                np.maximum(abs(data['High'] - data['Close'].shift(1)), 
                                           abs(data['Low'] - data['Close'].shift(1))))
        data['ATR'] = data['TR'].rolling(window=14).mean()

        # 급등 종목 필터링
        st.subheader("급등 종목 필터링")
        filtered_data = data[
            (data['Volume Change (%)'] > volume_threshold) &
            (data['Price Change (%)'] > price_change_threshold)
        ]
        if not filtered_data.empty:
            st.write("급등 종목 데이터:", filtered_data)
        else:
            st.write("급등 종목이 없습니다.")

        # 매수/매도 신호 생성
        st.subheader("ATR 기반 매수/매도 신호 생성")
        data['Buy_Signal'] = (data['Close'] > data['High'].shift(1)) & ((data['Close'] - data['High'].shift(1)) > data['ATR'] * 1.5)
        data['Sell_Signal'] = (data['Close'] < data['Low'].shift(1)) & ((data['Low'].shift(1) - data['Close']) > data['ATR'] * 1.5)
        st.write("ATR 기반 신호 데이터:", data[['Close', 'ATR', 'Buy_Signal', 'Sell_Signal']])

        # 데이터 시각화
        st.subheader("주가 및 매매 신호 시각화")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(data['Close'], label="종가", color="blue")
        ax.plot(data['ATR'], label="ATR", color="orange", linestyle="--")
        ax.scatter(data.index[data['Buy_Signal']], data['Close'][data['Buy_Signal']], marker="^", color="green", label="매수 신호")
        ax.scatter(data.index[data['Sell_Signal']], data['Close'][data['Sell_Signal']], marker="v", color="red", label="매도 신호")
        ax.set_title(f"{ticker} - ATR 및 매매 신호")
        ax.set_xlabel("날짜")
        ax.set_ylabel("가격")
        ax.legend()
        st.pyplot(fig)

        # 손절/익절 계산
        st.subheader("손절/익절 시뮬레이션")
        data['Stop_Loss'] = data['Close'] - data['ATR'] * 1.5
        data['Take_Profit'] = data['Close'] + data['ATR'] * 2
        st.write("손절/익절 데이터:", data[['Close', 'Stop_Loss', 'Take_Profit']])

        # 전략 결과 요약
        st.subheader("전략 결과 요약")
        buy_signals = data[data['Buy_Signal']]
        sell_signals = data[data['Sell_Signal']]
        st.write(f"매수 신호 발생 수: {len(buy_signals)}")
        st.write(f"매도 신호 발생 수: {len(sell_signals)}")

        # 성과 분석
        st.subheader("성과 분석")
        results = []
        for index, row in buy_signals.iterrows():
            entry_price = row['Close']
            stop_loss = row['Stop_Loss']
            take_profit = row['Take_Profit']
            for i in range(index + 1, len(data)):
                if data.iloc[i]['Close'] <= stop_loss:
                    results.append({'Type': 'Loss', 'Price': stop_loss})
                    break
                elif data.iloc[i]['Close'] >= take_profit:
                    results.append({'Type': 'Profit', 'Price': take_profit})
                    break

        results_df = pd.DataFrame(results)
        if not results_df.empty:
            st.write("손익 분석 결과:")
            st.write(results_df)
            st.write("손익 비율:")
            st.write(results_df['Type'].value_counts())
            st.write("총 수익:", results_df[results_df['Type'] == 'Profit']['Price'].sum() - 
                                    results_df[results_df['Type'] == 'Loss']['Price'].sum())
        else:
            st.write("성과 데이터가 없습니다.")
    except Exception as e:
        st.error(f"데이터를 가져오는데 실패했습니다: {e}")

