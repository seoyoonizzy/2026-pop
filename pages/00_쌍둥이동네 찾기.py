import pandas as pd
import numpy as np
import re
import os
import glob
import streamlit as st

def find_data_file(app_dir):
    exact_candidates = [
        "202606_202606_연령별인구현황_월간.csv",
        "202606_202606_yeonryeongbyeolinguhyeonhwang_weolgan.csv",
    ]
    for name in exact_candidates:
        path = os.path.join(app_dir, name)
        if os.path.exists(path):
            return path
    csv_files = glob.glob(os.path.join(app_dir, "*.csv"))
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

@st.cache_data
def get_region_list(df):
    return df["행정구역명"].dropna().unique().tolist()
