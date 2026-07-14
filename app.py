import streamlit as st
import numpy as np
import json
import requests

# 載入數據
db = json.load(open('data/teams.json', 'r', encoding='utf-8'))

def 模擬引擎(h_name, a_name, h_mod=1.0, a_mod=1.0):
    h, a = db[h_name], db[a_name]
    elo_diff = (h['Elo'] - a['Elo']) / 400
    
    # 根據 Elo 差距推移基底機率矩陣
    # 矩陣基礎設定為 5x5 (0-4球)
    base_matrix = np.array([
        [0.10, 0.09, 0.06, 0.02, 0.01], # 0球
        [0.12, 0.16, 0.09, 0.03, 0.01], # 1球
        [0.08, 0.11, 0.08, 0.05, 0.02], # 2球
        [0.04, 0.05, 0.04, 0.02, 0.01], # 3球
        [0.02, 0.02, 0.01, 0.01, 0.005] # 4球
    ])
    
    # 向強隊方向傾斜矩陣 (Elo 修正)
    shift = int(elo_diff * 2)
    matrix = np.roll(base_matrix, shift, axis=1)
    
    # 注入您的條件係數 (調整進攻權重)
    matrix *= (h_mod * a_mod)
    matrix /= matrix.sum()
    
    # 模擬 100 萬次
    flat = matrix.flatten()
    indices = np.random.choice(len(flat), 1000000, p=flat)
    
    # 提取結果
    unique, counts = np.unique(indices, return_counts=True)
    top_idx = unique[np.argsort(counts)[-3:][::-1]]
    
    results = []
    for idx in top_idx:
        row, col = divmod(idx, 5)
        results.append(f"{row}:{col}")
    return results

st.title("⚽ 預言家：最終回測校準終端")

# 1. API 自動化推演
try:
    api_key = st.secrets.get("API_KEY")
    res = requests.get("https://v3.football.api-sports.io/fixtures?league=39&season=2026&next=5", headers={'x-apisports-key': api_key}, timeout=5).json()
    賽程 = res.get('response', [])
except:
    賽程 = []

if 賽程:
    st.subheader("🗓️ 當日自動化推演")
    for f in 賽程:
        h, a = f['teams']['home']['name'], f['teams']['away']['name']
        with st.expander(f"📍 {h} vs {a}"):
            res = 模擬引擎(h, a)
            st.write(f"基礎預測波膽: **{', '.join(res)}**")
else:
    st.error("⚠️ 今日暫無賽程數據")

st.divider()
st.subheader("🛠️ 條件式精算實驗室")
h_pick = st.selectbox("主隊", list(db.keys()), key="h")
a_pick = st.selectbox("客隊", list(db.keys()), key="a")
h_mod = st.slider("主隊進攻狀態", 0.5, 1.5, 1.0, 0.1)
a_mod = st.slider("客隊進攻狀態", 0.5, 1.5, 1.0, 0.1)

if st.button("啟動最終驗證模擬"):
    波膽 = 模擬引擎(h_pick, a_pick, h_mod, a_mod)
    st.success(f"建議波膽: **{', '.join(波膽)}**")
