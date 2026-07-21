import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import os
from utils import find_data_file, load_data, get_age_columns

st.set_page_config(page_title="지역별 인구 구조 대시보드", layout="wide")

st.title("📊 지역별 연령별 인구 구조 대시보드")
st.caption("행정안전부 주민등록 연령별 인구현황 데이터 기반")
st.info("👈 왼쪽 사이드바 하단에서 '유사지역 Top5' 페이지로 이동할 수 있습니다.")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = find_data_file(APP_DIR)

if data_path is None:
    st.error(
        "데이터 파일을 찾을 수 없습니다.\n"
        "app.py와 같은 폴더에 인구현황 CSV 파일을 넣어주세요.\n"
        f"현재 폴더: {APP_DIR}"
    )
    st.stop()

df = load_data(data_path)
region_list = df["행정구역명"].dropna().unique().tolist()

st.sidebar.header("🔍 지역 선택")
st.sidebar.caption(f"불러온 파일: {os.path.basename(data_path)}")

search_text = st.sidebar.text_input("지역명 검색 (직접 입력)", value="")

if search_text:
    filtered_regions = [r for r in region_list if search_text in r]
else:
    filtered_regions = region_list

if not filtered_regions:
    st.sidebar.warning("검색 결과가 없습니다. 전체 목록을 표시합니다.")
    filtered_regions = region_list

selected_region = st.sidebar.selectbox(
    "지역 선택 (목록에서 선택, 읍면동 포함)",
    options=filtered_regions,
    index=0
)

st.session_state["selected_region"] = selected_region
st.session_state["data_path"] = data_path

gender_option = st.sidebar.radio("성별 구분", ["전체(계)", "남성", "여성", "남녀 비교"])

matched_rows = df.index[df["행정구역명"] == selected_region].tolist()

if not matched_rows:
    st.error("선택한 지역의 데이터를 찾을 수 없습니다.")
    st.stop()

target_idx = matched_rows[0]
row = df.loc[target_idx]

def build_age_series(gender_key):
    age_cols = get_age_columns(df, gender_key)
    ages, pops = [], []
    for c in age_cols:
        m = re.search(r"(\d+)세$", c)
        age = 100 if "100세" in c else int(m.group(1))
        ages.append(age)
        pops.append(row[c])
    return ages, pops

fig = go.Figure()

if gender_option == "전체(계)":
    ages, pops = build_age_series("계")
    fig.add_trace(go.Scatter(x=ages, y=pops, mode="lines+markers", name="전체", line=dict(color="#4C78A8")))
elif gender_option == "남성":
    ages, pops = build_age_series("남")
    fig.add_trace(go.Scatter(x=ages, y=pops, mode="lines+markers", name="남성", line=dict(color="#4C78A8")))
elif gender_option == "여성":
    ages, pops = build_age_series("여")
    fig.add_trace(go.Scatter(x=ages, y=pops, mode="lines+markers", name="여성", line=dict(color="#E45756")))
else:
    ages_m, pops_m = build_age_series("남")
    ages_f, pops_f = build_age_series("여")
    fig.add_trace(go.Scatter(x=ages_m, y=pops_m, mode="lines+markers", name="남성", line=dict(color="#4C78A8")))
    fig.add_trace(go.Scatter(x=ages_f, y=pops_f, mode="lines+markers", name="여성", line=dict(color="#E45756")))

fig.update_layout(
    title=f"{selected_region} 연령별 인구 구조",
    xaxis_title="연령",
    yaxis_title="인구수 (명)",
    hovermode="x unified",
    template="plotly_white",
    height=550,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

col1, col2, col3 = st.columns(3)
total_col = "2026년06월_계_총인구수"
col1.metric("총인구수", f"{int(row[total_col]):,} 명")

age_cols_gye = get_age_columns(df, "계")
ages_all = [100 if "100세" in c else int(re.search(r"(\d+)세$", c).group(1)) for c in age_cols_gye]
pops_all = [row[c] for c in age_cols_gye]
total_pop = sum(pops_all)
avg_age = sum(a * p for a, p in zip(ages_all, pops_all)) / total_pop if total_pop > 0 else 0
col2.metric("평균 연령(추정)", f"{avg_age:.1f} 세")

elderly_pop = sum(p for a, p in zip(ages_all, pops_all) if a >= 65)
elderly_ratio = elderly_pop / total_pop * 100 if total_pop > 0 else 0
col3.metric("65세 이상 비율", f"{elderly_ratio:.1f} %")

with st.expander("📋 원본 데이터 미리보기"):
    st.dataframe(row.to_frame().T)
