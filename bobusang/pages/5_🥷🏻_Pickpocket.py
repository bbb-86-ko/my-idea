import streamlit as st
import pandas as pd
import json
# import pydeck as pdk

# get API key from environment variable
GOOGLE_MAPS_API_KEY = st.secrets["GEMINI_API_KEY"]

# 1. CSV 파일 읽기
df = pd.read_csv("./data/pickpocket_300.csv", on_bad_lines='skip')

# 2. JSON으로 변환
data = df.to_dict(orient="records")  # 리스트[딕셔너리] 형태

# 데이터 불러오기
# with open("./data/pickpocket_300.json", encoding='utf-8') as f:
#     data = json.load(f)

df = pd.DataFrame(data)

st.title("🧳 AI가 알려준 Pickpocket Place")
st.markdown("소매치기 발생 지역을 함께 확인해보세요!")

# 🎯 1. 국가 선택
country_options = sorted(df["country"].dropna().unique())
selected_countries = st.sidebar.pills("🌍 국가를 선택하세요", options=country_options, default=[])

# 국가 필터 적용
filtered_df = df[df["country"].str.contains(selected_countries)] if selected_countries else df

# 🎯 2. 도시 선택 (선택된 국가에 한정)
city_options = sorted(filtered_df["city"].dropna().unique())
selected_cities = st.sidebar.pills("🌆 도시를 선택하세요", options=city_options, default=[])

# 도시 필터 적용
filtered_df = filtered_df[filtered_df["city"].str.contains(selected_cities)] if selected_cities else filtered_df

# 🎯 3. 소매치기 유형 선택 (선택된 도시 기준)
type_options = sorted(filtered_df["pickpocket_type"].dropna().unique())
selected_types = st.sidebar.pills("⚠️ 소매치기 유형을 선택하세요", options=type_options, default=[])

# 유형 필터 적용
filtered_df = filtered_df[filtered_df["pickpocket_type"].str.contains(selected_types)] if selected_types else filtered_df

# 🔍 필터링
filtered_df = df.copy()
filtered_data = data.copy()

if selected_countries:
    filtered_df = filtered_df[filtered_df["country"].str.contains(selected_countries)]
    filtered_data = [d for d in filtered_data if d["country"] in selected_countries]
if selected_cities:
    filtered_df = filtered_df[filtered_df["city"].str.contains(selected_cities)]
    filtered_data = [d for d in filtered_data if d["city"] in selected_cities]
if selected_types:
    filtered_df = filtered_df[filtered_df["pickpocket_type"].str.contains(selected_types)]
    filtered_data = [d for d in filtered_data if d["pickpocket_type"] in selected_types]

# 📊 통계 정보
st.pills("", options=[
    f"🌍 국가 수: {len(filtered_df['country'].unique())}",
    f"🌆 도시 수: {len(filtered_df['city'].unique())}",
    f"⚠️ 소매치기 유형 수: {len(filtered_df['pickpocket_type'].unique())}",
    f"🏢 장소 수: {len(filtered_df['place'].unique())}"
], default=[])
# 테이블
st.markdown("🗂️ 위험 장소 목록")
st.dataframe(
    filtered_df[["country", "city", "place", "pickpocket_type", "address"]], 
    column_config={
        "country": "국가", "city": "도시", "place": "장소", "pickpocket_type": "소매치기 유형", "address": "주소"
    },
    hide_index=True
)



# 지도 출력
st.markdown("📍 위험 장소")
# 기본 지도 좌표 (서울)
default_lat, default_lon = (
    (filtered_data[0]["lat"], filtered_data[0]["lon"])
    if filtered_data else
    (37.5665, 126.9780)
)

# Streamlit 세션 상태 초기화
if "selected_lat" not in st.session_state:
    st.session_state.selected_lat = ""
if "selected_lon" not in st.session_state:
    st.session_state.selected_lon = ""

# 지도에 표시할 마커 데이터 변환 (JavaScript에서 사용할 JSON 형태)
map_markers = json.dumps(filtered_data)

# JavaScript + Google Maps API 삽입
map_html = f"""
<!DOCTYPE html>
<html>
  <head>
    <script src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAPS_API_KEY}&callback=initMap" async defer></script>
    <script>
      let tempMarker = null;

      function initMap() {{
        var map = new google.maps.Map(document.getElementById('map'), {{
          center: {{lat: {default_lat}, lng: {default_lon}}},
          zoom: 5
        }});

        var locations = {map_markers};

        // 기존 마커 추가
        locations.forEach(function(location) {{
          new google.maps.Marker({{
            position: new google.maps.LatLng(location.lat, location.lon),
            map: map,
            title: location.description
          }});
        }});

        // 지도 클릭 시 새로운 마커 추가 (이전 마커 삭제 후 새로 생성)
        map.addListener("click", function(event) {{
          if (tempMarker) {{
            tempMarker.setMap(null); // 기존 임시 마커 제거
          }}

          tempMarker = new google.maps.Marker({{
            position: event.latLng,
            map: map,
            title: "선택한 위치",
            icon: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png"
          }});

          console.log("Map Click Event: ", event);
          console.log("Selected Latitude: ", event.latLng.lat());
          console.log("Selected Longitude: ", event.latLng.lng());

          // 클릭한 위치의 좌표를 Streamlit으로 전달
          window.parent.postMessage(
            JSON.stringify({{lat: event.latLng.lat(), lon: event.latLng.lng()}}),
            "*"
          );
        }});
      }}
    </script>
  </head>
  <body>
    <div id="map" style="height: 500px; width: 100%;"></div>
  </body>
</html>
"""

# Streamlit에서 지도 렌더링
st.components.v1.html(map_html, height=600)

# JavaScript에서 전달된 데이터를 Streamlit이 받도록 설정
st.markdown(
    """
    <script>
      window.addEventListener("message", function(event) {
          console.log("Received PostMessage Event: ", event);
          try {
              const data = JSON.parse(event.data);
              console.log("Parsed Data: ", data);
              const latInput = document.getElementById("selectedLat");
              const lonInput = document.getElementById("selectedLon");
              latInput.value = data.lat;
              lonInput.value = data.lon;
              latInput.dispatchEvent(new Event("input"));
              lonInput.dispatchEvent(new Event("input"));
          } catch (error) {
              console.error("Invalid data received:", event.data);
          }
      });
    </script>
    """,
    unsafe_allow_html=True
)