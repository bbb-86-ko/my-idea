import streamlit as st
from PIL import Image
import io
import google.generativeai as genai
import os

# get API key from environment variable
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# API 키 설정
genai.configure(api_key=GEMINI_API_KEY)

# gemini model 설정 (https://ai.google.dev/gemini-api/docs/models/gemini?hl=ko&_gl=1*aav4qa*_up*MQ..*_ga*NjA2MTc5NzgzLjE3MzQ4NTA5NTU.*_ga_P1DBVKWT6V*MTczNDg1MDk1NC4xLjAuMTczNDg1MTE0NS4wLjAuOTE2MjM5OTQ.#model-variations)
# genaiModel = genai.GenerativeModel("gemini-1.5-pro")
genaiModel = genai.GenerativeModel("gemini-1.5-flash")

# Streamlit 앱 설정
st.set_page_config(page_title="I know your kcal", page_icon="🏃🏻")

# 앱 헤더
st.title("🏃🏻 I know your kcal")

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

    # 예: 이미지 데이터를 API로 전송
    # 여기에 딥러닝 기반 차트 분석 또는 OCR 로직 추가 가능
    # image_data = io.BytesIO(uploaded_file.read())

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
                image
            ])
        gemini_analysis = gemini_response.text

    # 결과 출력
    st.subheader("🧐 분석 결과")
    if gemini_analysis:
        st.markdown(gemini_analysis)
    else:
        st.markdown("분석 결과 없음.")


