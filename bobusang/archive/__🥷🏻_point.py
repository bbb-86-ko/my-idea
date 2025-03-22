import streamlit as st
import json
import pandas as pd
import googlemaps

# get API key from environment variable
GOOGLE_MAPS_API_KEY = st.secrets["GEMINI_API_KEY"]

# 데이터 파일
DATA_FILE = "data/pickpocket_300.json"

# 데이터 로드 함수
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# 데이터 저장 함수
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# 데이터 불러오기
data = load_data()

# 데이터 목록 표시
st.subheader("🥷🏻 소매치기 출몰 지역 목록")

view_data = list(map(lambda d: {
    "pickpocket_type": d["pickpocket_type"],
    "country": d["country"],
    "city": d["city"],
    "place": d["place"],
    "address": d["address"]
}, data))

# 데이터프레임 생성
df = pd.DataFrame(view_data)

# 데이터 테이블 표시
st.dataframe(hide_index=True,data=df)

# # 기본 지도 좌표 (서울)
# default_lat, default_lon = data[0]["lat"], data[0]["lon"] if data else (37.5665, 126.9780)

# # Streamlit 세션 상태 초기화
# if "selected_lat" not in st.session_state:
#     st.session_state.selected_lat = ""
# if "selected_lon" not in st.session_state:
#     st.session_state.selected_lon = ""

# # 지도에 표시할 마커 데이터 변환 (JavaScript에서 사용할 JSON 형태)
# map_markers = json.dumps(data)

# # JavaScript + Google Maps API 삽입
# map_html = f"""
# <!DOCTYPE html>
# <html>
#   <head>
#     <script src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAPS_API_KEY}&callback=initMap" async defer></script>
#     <script>
#       let tempMarker = null;

#       function initMap() {{
#         var map = new google.maps.Map(document.getElementById('map'), {{
#           center: {{lat: {default_lat}, lng: {default_lon}}},
#           zoom: 5
#         }});

#         var locations = {map_markers};

#         // 기존 마커 추가
#         locations.forEach(function(location) {{
#           new google.maps.Marker({{
#             position: new google.maps.LatLng(location.lat, location.lon),
#             map: map,
#             title: location.description
#           }});
#         }});

#         // 지도 클릭 시 새로운 마커 추가 (이전 마커 삭제 후 새로 생성)
#         map.addListener("click", function(event) {{
#           if (tempMarker) {{
#             tempMarker.setMap(null); // 기존 임시 마커 제거
#           }}

#           tempMarker = new google.maps.Marker({{
#             position: event.latLng,
#             map: map,
#             title: "선택한 위치",
#             icon: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png"
#           }});

#           console.log("Map Click Event: ", event);
#           console.log("Selected Latitude: ", event.latLng.lat());
#           console.log("Selected Longitude: ", event.latLng.lng());

#           // 클릭한 위치의 좌표를 Streamlit으로 전달
#           window.parent.postMessage(
#             JSON.stringify({{lat: event.latLng.lat(), lon: event.latLng.lng()}}),
#             "*"
#           );
#         }});
#       }}
#     </script>
#   </head>
#   <body>
#     <div id="map" style="height: 500px; width: 100%;"></div>
#   </body>
# </html>
# """

# # Streamlit에서 지도 렌더링
# st.components.v1.html(map_html, height=600)

# # JavaScript에서 전달된 데이터를 Streamlit이 받도록 설정
# st.markdown(
#     """
#     <script>
#       window.addEventListener("message", function(event) {
#           console.log("Received PostMessage Event: ", event);
#           try {
#               const data = JSON.parse(event.data);
#               console.log("Parsed Data: ", data);
#               const latInput = document.getElementById("selectedLat");
#               const lonInput = document.getElementById("selectedLon");
#               latInput.value = data.lat;
#               lonInput.value = data.lon;
#               latInput.dispatchEvent(new Event("input"));
#               lonInput.dispatchEvent(new Event("input"));
#           } catch (error) {
#               console.error("Invalid data received:", event.data);
#           }
#       });
#     </script>
#     """,
#     unsafe_allow_html=True
# )