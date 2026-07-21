import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import re
import os
import glob

st.set_page_config(page_title="지역별 인구 구조 대시보드", layout="wide")

st.title("📊 지역별 연령별 인구 구조 대시보드")
st.caption("행정안전부 주민등록 연령별 인구현황 데이터 기반")

APP_DIR = os.path.dirname(os.path.abspath(__file__))

def find_data_file():
    exact_candidates = [
        "202606_202606_연령별인구현황_월간.csv",
        "202606_202606_yeonryeongbyeolinguhyeonhwang_weolgan.csv",
    ]
    for name in exact_candidates:
        path = os.path.join(APP_DIR, name)
        if os.path.exists(path):
            return path
    csv_files = glob.glob(os.path.join(APP_DIR, "*.csv"))
    if csv_files:
        return csv_files[0]
    return None

@st.cache_data
def load_data(path):
    df = pd.read_csv(
        path,
        encoding="cp949",
        engine="python",
        on_bad_lines="skip",
        thousands=","
    )
    df["행정구역명"] = df["행정구역"].apply(lambda x: re.sub(r"\s*\(.*\)$", "", str(x)).strip())
    return df

def get_age_columns(df, gender="계"):
    pattern = re.compile(rf"_{gender}_\d+세$|_{gender}_100세 이상$")
    cols = [c for c in df.columns if pattern.search(c)]
    cols_sorted = sorted(
        cols,
        key=lambda c: 100 if "100세" in c else int(re.search(r"(\d+)세$", c).group(1))
    )
    return cols_sorted

@st.cache_data
def compute_ratio_matrix(df, age_cols):
    mat = df[age_cols].values.astype(float)
    row_sums = mat.sum(axis=1)
    ratio_mat = np.zeros_like(mat)
    valid = row_sums > 0
    ratio_mat[valid] = mat[valid] / row_sums[valid][:, None]
    return ratio_mat, row_sums

def find_similar_regions(ratio_mat, row_sums, target_idx, top_n=5):
    target_vec = ratio_mat[target_idx]
    target_norm = np.linalg.norm(target_vec)
    sims = np.full(len(ratio_mat), -1.0)
    for i in range(len(ratio_mat)):
        if i == target_idx or row_sums[i] == 0:
            continue
        v = ratio_mat[i]
        denom = target_norm * np.linalg.norm(v)
        sims[i] = np.dot(target_vec, v) / denom if denom > 0 else -1
    top_idx = np.argsort(sims)[::-1][:top_n]
    return top_idx, sims[top_idx]

data_path = find_data_file()

if data_path is None:
    st.error(
        "데이터 파일을 찾을 수 없습니다.\n"
        "app.py와 같은 폴더에 인구현황 CSV 파일을 넣어주세요.\n"
        f"현재 폴더: {APP_DIR}"
    )
    st.stop()

df = load_data(data_path)
region_list = df["행정구역명"].dropna().unique().tolist()
age_cols_gye = get_age_columns(df, "계")
ratio_mat, row_sums = compute_ratio_matrix(df, age_cols_gye)

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

gender_option = st.sidebar.radio("성별 구분", ["전체(계)", "남성", "여성", "남녀 비교"])

matched_rows = df.index[df["행정구역명"] == selected_region].tolist()

if not matched_rows:
    st.error("선택한 지역의 데이터를 찾을 수 없습니다.")
    st.stop()

target_idx = matched_rows[0]
row = df.loc[target_idx]

def build_age_series(gender_key):
    age_cols = get_age_columns(df, gender_key)
    ages = []
    pops = []
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

ages_all = [100 if "100세" in c else int(re.search(r"(\d+)세$", c).group(1)) for c in age_cols_gye]
pops_all = [row[c] for c in age_cols_gye]
total_pop = sum(pops_all)
avg_age = sum(a * p for a, p in zip(ages_all, pops_all)) / total_pop if total_pop > 0 else 0
col2.metric("평균 연령(추정)", f"{avg_age:.1f} 세")

elderly_pop = sum(p for a, p in zip(ages_all, pops_all) if a >= 65)
elderly_ratio = elderly_pop / total_pop * 100 if total_pop > 0 else 0
col3.metric("65세 이상 비율", f"{elderly_ratio:.1f} %")

st.divider()
st.subheader(f"🔗 '{selected_region}'과 인구 구조가 가장 비슷한 전국 지역 Top 5")
st.caption("연령대별 인구 비율(구성비) 기준 코사인 유사도로 산출한 결과입니다.")

top_idx, top_sims = find_similar_regions(ratio_mat, row_sums, target_idx, top_n=5)
similar_names = df["행정구역명"].iloc[top_idx].tolist()

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=ages_all, y=[p for p in pops_all],
    mode="lines", name=f"{selected_region} (기준)",
    line=dict(color="black", width=3, dash="solid")
))

palette = ["#4C78A8", "#E45756", "#54A24B", "#EECA3B", "#B279A2"]
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
    xaxis_title="연령",
    yaxis_title="인구수 (명)",
    hovermode="x unified",
    template="plotly_white",
    height=550,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
)

st.plotly_chart(fig2, use_container_width=True)

fig3 = go.Figure()
target_ratio_pct = ratio_mat[target_idx] * 100
fig3.add_trace(go.Scatter(
    x=ages_all, y=target_ratio_pct,
    mode="lines", name=f"{selected_region} (기준)",
    line=dict(color="black", width=3, dash="solid")
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
    xaxis_title="연령",
    yaxis_title="인구 비율 (%)",
    hovermode="x unified",
    template="plotly_white",
    height=550,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
)

st.plotly_chart(fig3, use_container_width=True)

result_df = pd.DataFrame({
    "순위": range(1, len(top_idx)+1),
    "지역명": similar_names,
    "유사도(코사인)": [f"{s:.4f}" for s in top_sims],
    "총인구수": [f"{int(df.loc[i, total_col]):,}" for i in top_idx]
})
st.dataframe(result_df, use_container_width=True, hide_index=True)

with st.expander("📋 원본 데이터 미리보기"):
    st.dataframe(row.to_frame().T)
