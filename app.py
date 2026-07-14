import streamlit as st
import numpy as np
import json
import requests

# 1. 安全數據載入
try:
    with open('data/teams.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
except:
    db = None

# 2. 核心邏輯 (矩陣映射)
def 執行預言(h_name, a_name, h_mod=1.0, a_mod=1.0):
    h, a = db[h_name], db[a_name]
    diff = h['Elo'] - a['Elo']
    dom = np.array([[0.05, 0.15, 0.10, 0.05, 0.02], [0.10, 0.20, 0.15, 0.08, 0.03], [0.05, 0.10, 0.10, 0.05, 0.02], [0.02, 0.05, 0.03, 0.01, 0.00]])
    bal = np.array([[0.15, 0.20, 0.08, 0.02, 0.01], [0.20, 0.25, 0.10, 0.03, 0.01], [0.08, 0.10, 0.05, 0.02, 0.00], [0.02, 0.03, 0.01, 0.00, 0.00]])
    ups = np.array([[0.08, 0.12, 0.08, 0.05, 0.02], [0.10, 0.15, 0.12, 0.08, 0.04], [0.05, 0.10, 0.08, 0.05, 0.02], [0.02, 0.04, 0.02, 0.01, 0.00]])
    
    matrix = dom if diff > 200 else (bal if diff > -50 else ups)
    matrix = matrix * (h_mod / a_mod)
    matrix /= matrix.sum()
    
    flat = matrix.flatten()
    idx = np.random.choice(len(flat), 1000000, p=flat)
    unique, counts = np.unique(idx, return_counts=True)
    top = unique[np.argsort(counts)[-3:][::-1]]
    return [f"{i // 5}:{i % 5}" for i in top]

# 3. 完整 UI 佈局
st.title("⚽ 預言家：整合終端")

# A. 自動化賽程檢查區 (絕對保留)
st.subheader("🗓️ 當日自動化賽程")
try:
    res = requests.get("https://v3.football.api-sports.io/fixtures?league=39&season=2026&next=5", 
                       headers={'x-apisports-key': st.secrets.get("API_KEY", "")}, timeout=5).json()
    賽程 = res.get('response', [])
    if not 賽程:
        st.warning("⚠️ 今日無賽事數據")
    else:
        for f in 賽程:
            st.write(f"📍 {f['teams']['home']['name']} vs {f['teams']['away']['name']}")
except:
    st.error("⚠️ 無法連線至 API，自動化檢查暫停")

# B. 手動條件實驗室 (絕對保留)
st.divider()
st.subheader("🛠️ 條件式精算實驗室")
if db:
    h_pick = st.selectbox("主隊", list(db.keys()), key="h")
    a_pick = st.selectbox("客隊", list(db.keys()), key="a")
    h_mod = st.slider("主隊狀態", 0.5, 1.5, 1.0, 0.1)
    a_mod = st.slider("客隊狀態", 0.5, 1.5, 1.0, 0.1)

    if st.button("啟動精算"):
        res = 執行預言(h_pick, a_pick, h_mod, a_mod)
        st.success(f"建議波膽: **{', '.join(res)}**")
else:
    st.error("數據庫錯誤，無法執行模擬")
