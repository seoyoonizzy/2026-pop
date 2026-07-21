import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import os
from utils import (
    find_data_file, load_data, get_age_columns,
    compute_ratio_matrix, find_similar_regions
)

st.set_page_config(page_title="유사 지역 Top5", layout="wide")

st.title("🔗 인구 구조 유사 지역 Top 5")
st.caption("연령대별 인구 구성비 기준 코사인 유사도로 산출한 전국 유사 지역")

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = st.session_state.get("data_path") or find_data_file(APP_DIR)

if data_path is None:
    st.error("데이터 파일을 찾을 수 없습니다. app.py와 같은 폴더에 CSV 파일을 넣어주세요.")
    st.stop()

df = load_data(data_path)
region_list = df["행정구역명"].dropna().unique().tolist()

st.sidebar.header("🔍 지역 선택")

default_region = st.session_state.get("selected_region", region_list[0])

search_text = st.sidebar.text_input("지역명 검색 (직접 입력)", value="")

if search_text:
    filtered_regions = [r for r in region_list if search_text in r]
else:
    filtered_regions = region_list

if not filtered_regions:
    st.sidebar.warning("검색 결과가 없습니다. 전체 목록을 표시합니다.")
    filtered_regions = region_list

default_index = filtered_regions.index(default_region) if default_region in filtered_regions else 0

selected_region = st.sidebar.selectbox(
    "지역 선택 (목록에서 선택, 읍면동 포함)",
    options=filtered_regions,
    index=default_index
)

top_n = st.sidebar.slider("비교할 유사 지역 수", min_value=3, max_value=10, value=5)

matched_rows = df.index[df["행정구역명"] == selected_region].tolist()

if not matched_rows:
    st.error("선택한 지역의 데이터를 찾을 수 없습니다.")
    st.stop()

target_idx = matched_rows[0]
row = df.loc[target_idx]

age_cols_gye = get_age_columns(df, "계")
ratio_mat, row_sums = compute_ratio_matrix(df, age_cols_gye)

ages_all = [100 if "100세" in c else int(re.search(r"(\d+)세$", c).group(1)) for c in age_cols_gye]
pops_all = [row[c] for c in age_cols_gye]

top_idx, top_sims = find_similar_regions(ratio_mat, row_sums, target_idx, top_n=top_n)
similar_names = df["행정구역명"].iloc[top_idx].tolist()

st.subheader(f"'{selected_region}'과 인구 구조가 가장 비슷한 전국 지역 Top {top_n}")

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=ages_all, y=pops_all,
    mode="lines", name=f"{selected_region} (기준)",
    line=dict(color="black", width=3)
))

palette = ["#4C78A8", "#E45756", "#54A24B", "#EECA3B", "#B279A2", "#FF9DA6", "#9D755D", "#BAB0AC"]
for rank, (idx, sim, name) in enumerate(zip(top_idx, top_sims, similar_names)):
    r = df.loc[idx]
    pops_i = [r[c] for c in age_cols_gye]
    fig2.add_trace(go.Scatter(
        x=ages_all, y=pops_i,
        mode="lines", name=f"{rank+1}위 {name} (유사도 {sim:.3f})",
        line=dict(color=palette[rank % len(palette)], width=2)
    ))

fig2.update_layout(
    title="인구 구조 유사 지역 비교 (절대 인구수 기준)",
    xaxis_title="연령", yaxis_title="인구수 (명)",
    hovermode="x unified", template="plotly_white", height=550,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
)
st.plotly_chart(fig2, use_container_width=True)

fig3 = go.Figure()
target_ratio_pct = ratio_mat[target_idx] * 100
fig3.add_trace(go.Scatter(
    x=ages_all, y=target_ratio_pct,
    mode="lines", name=f"{selected_region} (기준)",
    line=dict(color="black", width=3)
))
for rank, (idx, sim, name) in enumerate(zip(top_idx, top_sims, similar_names)):
    ratio_pct = ratio_mat[idx] * 100
    fig3.add_trace(go.Scatter(
        x=ages_all, y=ratio_pct,
        mode="lines", name=f"{rank+1}위 {name} (유사도 {sim:.3f})",
        line=dict(color=palette[rank % len(palette)], width=2)
    ))

fig3.update_layout(
    title="인구 구조 유사 지역 비교 (연령대 구성비 % 기준)",
    xaxis_title="연령", yaxis_title="인구 비율 (%)",
    hovermode="x unified", template="plotly_white", height=550,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
)
st.plotly_chart(fig3, use_container_width=True)

total_col = "2026년06월_계_총인구수"
result_df = pd.DataFrame({
    "순위": range(1, len(top_idx)+1),
    "지역명": similar_names,
    "유사도(코사인)": [f"{s:.4f}" for s in top_sims],
    "총인구수": [f"{int(df.loc[i, total_col]):,}" for i in top_idx]
})
st.dataframe(result_df, use_container_width=True, hide_index=True)
