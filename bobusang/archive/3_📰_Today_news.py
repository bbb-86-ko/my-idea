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
        google_articles = google_feed.entries[:1]
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
st.title("Stock News Summarizer")

# 실행
trending_keywords = get_top_charts()
stock_list = trending_keywords['title'].tolist()
if trending_keywords is not None:
    st.write("📈 **Trending Keywords**")
    st.write(", ".join(stock_list))

# 주식 목록 입력
# stock_input = st.text_area("Enter stock symbols (comma-separated):", "AAPL")
# stock_list = [s.strip() for s in stock_input.split(",") if s.strip()]
stock_list = trending_keywords['title'].tolist()

if st.button("Fetch News"):
    with st.spinner("Fetching news..."):
        news_list = fetch_news(stock_list)
        st.session_state.news_list = news_list
        st.success("News fetched successfully!")

# 뉴스 표시
if "news_list" in st.session_state:
    for idx, news in enumerate(st.session_state.news_list):
        expander_key = f"expander_{idx}"
        
        with st.expander(f"📈 {news['stock']}: {news['title']}"):
            # FIXME: expander가 열릴 때 요약을 생성하도록 수정
            # Expander가 처음 열릴 때 요약 실행
                # GPT 및 Gemini API 호출
                # with st.spinner("분석을 진행 중입니다..."):
                #     summary = summarize_news(news["title"], news["link"])
                #     news["summary"] = summary
                #     if summary:
                #         st.write("🤖 Summary")
                #         st.write(summary)
                #     else:
                #         st.write("🤖 It cannot be summarized.")
                st.markdown(f"[Read Full Article]({news['link']})", unsafe_allow_html=True)

