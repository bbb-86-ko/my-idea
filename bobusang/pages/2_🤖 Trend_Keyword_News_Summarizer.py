# Description: keyword를 입력하면 해당 keyword에 대한 뉴스를 요약해서 보여주는 스트림릿 앱
# Date: 2021-09-29
# Writer: Bobusang

import streamlit as st
import feedparser
import requests
import pandas as pd
import google.generativeai as genai
from pytrends.request import TrendReq
from urllib.parse import quote
import random

# get API key from environment variable
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# API 키 설정
genai.configure(api_key=GEMINI_API_KEY)

# gemini model 설정
genaiModel = genai.GenerativeModel("gemini-1.5-flash")

# 뉴스 가져오기 함수
def fetch_news(stock_list):
    news_data = []
    for stock in stock_list:
        # 구글 뉴스 RSS URL 생성
        google_news_url = f"https://news.google.com/rss/search?q={quote(stock)}&hl=en"
        # yahoo_news_url = f"https://finance.yahoo.com/rss/{quote(stock)}"
        
        # 구글 뉴스 RSS 파싱
        google_feed = feedparser.parse(google_news_url)
        # yahoo_feed = feedparser.parse(yahoo_news_url)
        
        # 최신 3개 기사 가져오기
        google_articles = google_feed.entries[:5]
        # yahoo_articles = yahoo_feed.entries[:3]
        
        # 뉴스 데이터 저장
        # for article in google_articles + yahoo_articles:
        for article in google_articles:
            news_data.append({
                "stock": stock,
                "title": article.title,
                "link": article.link,
                "summary": None  # 요약 대기 상태
            })
    return news_data

# 뉴스 요약 함수
# @st.cache_data(show_spinner=False)
def summarize_news(article_title, article_link):
    prompt = f"Summarize the news article titled '{article_title}' available at {article_link}."
    try:
        gemini_response = genaiModel.generate_content(prompt)
        print("gemini_response start ------------------------------------------------")
        print(gemini_response)
        print("gemini_response end ------------------------------------------------")
        summary = gemini_response.text
    except Exception as e:
        st.error(f"Error summarizing news: {e}")
        summary = "Unable to generate summary at this time."
    return summary


# 키워드
def get_keywords():
    return [
         "삼성전자",
        "SK하이닉스",
        "LG에너지솔루션",
        "삼성바이오로직스",
        "현대차",
        "POSCO홀딩스",
        "기아",
        "네이버",
        "LG화학",
        "삼성SDI",
        "애플",
        "엔비디아",
        "마이크로소프트",
        "알파벳",
        "아마존",
        "메타",
        "테슬라",
        "브로드컴",
        "TSMC",
        "버크셔 해서웨이"
    ]

# 실시간 트렌딩 검색어 가져오기
# Pytrends 객체 생성
pytrends = TrendReq(hl='en-US', tz=360)
def get_trending_keywords():
    try:
        trending_searches_df = pytrends.trending_searches(pn='south_korea')  # 지역 선택 (e.g., 'united_states', 'south_korea')
        return trending_searches_df
    except Exception as e:
        print(f"Error: {e}")
        return None
# 관련 키워드 추천
def get_keyword_suggestions(keyword):
    try:
        suggestions = pytrends.suggestions(keyword)
        return pd.DataFrame(suggestions)
    except Exception as e:
        print(f"Error: {e}")
        return None
# 특정 키워드의 시간별 검색 트렌드
def get_keyword_trends(keywords, timeframe='today 1-m', geo='US'):
    try:
        pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo, gprop='')
        interest_over_time_df = pytrends.interest_over_time()
        return interest_over_time_df
    except Exception as e:
        print(f"Error: {e}")
        return None
# 상위 차트 가져오기
def get_top_charts():
    try:
        top_charts_df = pytrends.top_charts(2023, hl='ko-KR', tz=300, geo='KR')
        return top_charts_df
    except Exception as e:
        print(f"Error: {e}")
        return None

# Streamlit UI
st.title("🤖 Trend Keyword News Summarizer")



# 주식 목록
# trending_keywords = get_top_charts()
# stock_list = trending_keywords['title'].tolist()
# 주식 목록
# my_list = get_keywords()
# stock_list = random.sample(my_list, len(my_list))
stock_list = get_keywords()
with st.container():
    if stock_list is not None:
        selection = st.pills("🔑  **Trend Keywords**", stock_list)
        if selection:
            with st.spinner(f"Fetching news for {selection}..."):
                news_list = fetch_news([selection])
                st.session_state.news_list = news_list
                st.success(f"News fetched successfully for {selection}!")

# # 뉴스 표시
with st.container():
    if "news_list" in st.session_state:
        news_list = st.session_state.news_list
        print(news_list)
        news_titles = list(map(lambda news: news['title'], news_list))
        selected_option = st.radio(
            "📰 What's your favorite news",
            news_titles,
            captions=[],
            index=0,
        )
        selected_index = news_titles.index(selected_option)
        
        if selected_option:
            with st.container():
                with st.spinner("🤖 Summarizing..."):
                    news = news_list[selected_index]
                    summary = summarize_news(news["title"], news["link"])
                    news["summary"] = summary
                    if summary:
                        st.markdown(
                            f"""
                                ----------------------
                                ###### 🤖 **Summary**

                                {summary}
                                
                                [Read Full Article]({news['link']})
                                
                                ----------------------
                            """
                            , unsafe_allow_html=True
                        )
                    else:
                        st.text_area("🤖 It cannot be summarized.")
                    