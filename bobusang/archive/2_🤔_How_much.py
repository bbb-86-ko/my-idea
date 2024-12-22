import streamlit as st
from PIL import Image
import io
import openai
import google.generativeai as genai
import os

# get API key from environment variable
OPEN_API_KEY = st.secrets["OPEN_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# API 키 설정
openai.api_key = OPEN_API_KEY
# openai.api_key = "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"

# GEMINI_API_KEY = "AIzaSyBHezWieGWLCzjvrblc5OMHqJNC6q_HC_M"
genai.configure(api_key=GEMINI_API_KEY)
# genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# gemini model 설정 (https://ai.google.dev/gemini-api/docs/models/gemini?hl=ko&_gl=1*aav4qa*_up*MQ..*_ga*NjA2MTc5NzgzLjE3MzQ4NTA5NTU.*_ga_P1DBVKWT6V*MTczNDg1MDk1NC4xLjAuMTczNDg1MTE0NS4wLjAuOTE2MjM5OTQ.#model-variations)
genaiModel = genai.GenerativeModel("gemini-1.5-pro")


# Streamlit 앱 설정
st.set_page_config(page_title="How much", page_icon="🤔")

# 앱 헤더
st.title("🤔 얼마?")
# st.write("업로드한 주식 차트 이미지를 분석하여 기술적 분석 결과를 제공합니다.")

# 이미지 업로드
uploaded_file = st.file_uploader("주식 차트 이미지를 업로드하세요", type=["png", "jpg", "jpeg"])

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
        # GPT 요청
        # gpt_response = openai.chat.completions.create(
        #     model="gpt-4",
        #     messages=[
        #         {"role": "system", "content": "You are a stock market technical analysis expert."},
        #         {"role": "user", "content": "Analyze the following stock chart."}
        #     ],
        # )

        # Gemini 요청 (예: dummy response)
        gemini_response = genaiModel.generate_content([
                # "Analyze the following stock chart.",
                """
                    한국어로 부탁합니다.
                    적정 매수, 매도 가격을 분석해주세요.
                    주식 차트가 아닌 것이 나오면 "적정 매수, 매도 가격을 분석할 수 없습니다." 라고 답변해주세요.
                """,
                image
            ])
        # gemini_analysis = gemini_response.json().get("analysis", "Gemini 분석 결과 없음.")
        gemini_analysis = gemini_response.text

    # 결과 출력
    st.subheader("🧐 분석 결과")
    # st.markdown("### GPT의 분석 결과")
    # st.text(gpt_analysis)
    # st.markdown("### Gemini의 분석 결과")
    if gemini_analysis:
        st.markdown(gemini_analysis)
    else:
        st.markdown("분석 결과 없음.")


