import streamlit as st
from PIL import Image
import io
import google.generativeai as genai
import os
# from notion_client import Client
import requests
import json
# PDF 라이브러리
from fpdf import FPDF

# get API key from environment variable
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# API 키 설정
genai.configure(api_key=GEMINI_API_KEY)

# gemini model 설정
genaiModel = genai.GenerativeModel("gemini-1.5-flash")

# Streamlit 앱 설정
st.set_page_config(page_title="I know your kcal", page_icon="🏃🏻")

# 앱 헤더
st.title("🏃🏻 I know your kcal")

st.write(os.getcwd())

# 이미지 업로드
uploaded_file = st.file_uploader(
    label="오늘 먹은 음식 사진을 업로드하세요", 
    type=["png", "jpg", "jpeg"],
)

if uploaded_file:
    # 이미지를 표시
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 차트 이미지", use_container_width=True)
    
    # 차트 이미지 처리 단계 (추후 구현 가능)
    st.write("이미지에서 차트 데이터를 추출하는 중...")
    
    # GPT 및 Gemini API 호출
    with st.spinner("분석을 진행 중입니다..."):
        # Gemini 요청 (예: dummy response)
        gemini_response = genaiModel.generate_content([
            """
                답변은 markdown 형식과 한국어로 부탁합니다.
                음식 사진을 분석하여 대략적인 칼로리 정보를 알려드립니다.
                예상 칼로리 | 잘한것 | 부족한것 | 조언 등을 알려주세요.
                음식 사진이 아니면 "음식 사진이 아닙니다." 라고 답변해주세요.
            """,
            image  # 실제론 이미지 자체를 전달하는 게 아닌, 이미지를 분석한 결과 등을 넣어야 할 수도 있음
        ])
        gemini_analysis = gemini_response.text

    # 결과 출력
    st.subheader("🧐 분석 결과")
    if gemini_analysis:
        st.markdown(gemini_analysis)
    else:
        st.markdown("분석 결과 없음.")

    st.write(os.path.abspath(__file__))
    st.write(os.path.getcwd())
    st.write(os.path.abspath("../fonts/NanumGothic/NanumGothic-Regular.ttf"))

    # TODO: PDF 만들기 버튼
    # # PDF 만들기 버튼
    # if gemini_analysis:
    #         pdf = FPDF()  
    #         pdf.add_font(
    #             "NanumGothic-Regular", 
    #             "", 
    #             "../fonts/NanumGothic/NanumGothic-Regular.ttf", 
    #             uni=True
    #         )
    #         pdf.set_font("NanumGothic-Regular", "", 10)
    #         pdf.add_page()
    #         pdf.multi_cell(0, 10, gemini_analysis)
            
    #         pdf_buffer_bytearray = pdf.output(dest="S")  # bytearray로 반환되는 경우가 있음
    #         pdf_buffer = bytes(pdf_buffer_bytearray)     # bytearray → bytes 변환
            
    #         st.download_button(
    #             label="PDF 다운로드",
    #             data=pdf_buffer,
    #             file_name="analysis.pdf",
    #             mime="application/pdf")
    # else:
    #     st.warning("분석 결과가 비어 있습니다.")

