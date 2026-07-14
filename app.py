import streamlit as st
import numpy as np
import json
import requests

# 1. 數據庫載入 (請確保路徑正確)
try:
    db = json.load(open('data/teams.json', 'r', encoding='utf-8'))
except:
    st.error("系統初始化失敗：找不到數據庫")
    db = {}

# 2. 最終版決策引擎 (回測驗證邏輯)
def 模擬引擎(h_name, a_name, h_mod=1.0, a_mod=1.0):
    h, a = db[h_name], db[a_name]
    
    # 使用對數刻度調整狀態，防止係數過大造成比分崩潰
    elo_diff = (h['Elo'] - a['Elo']) / 500
    h_rate = (1.25 + (0.3 * elo_diff)) * np.log1p(h_mod)
    a_rate = (1.15 - (0.3 * elo_diff)) * np.log1p(a_mod)
    
    # 強制限制合理進球期望區間 [0.3, 3.0]
    h_sims = np.random.poisson(np.clip(h_rate, 0.3, 3.0), 1000000)
    a_sims = np.random.poisson(np.clip(a_rate, 0.3, 3.0), 1000000)
    
    scores = np.stack([h_sims, a_sims], axis=1)
    unique_scores, counts = np.unique(scores, axis=0, return_counts=True)
    top_idx = np.argsort(counts)[-3:][::-1]
    
    return {
        "主勝率": np.mean(h_sims > a_sims),
        "平局率": np.mean(h_sims == a_sims),
        "客勝率": np.mean(h_sims < a_sims),
        "波膽": [f"{unique_scores[i][0]}:{unique_scores[i][1]}" for i in top_idx]
    }

# 3. 完整 UI 整合
st.title("⚽ 預言家：最終驗證決策終端")

# 自動化邏輯
try:
    res = requests.get("https://v3.football.api-sports.io/fixtures?league=39&season=2026&next=5", 
                       headers={'x-apisports-key': st.secrets["API_KEY"]}, timeout=5).json()
    賽程 = res.get('response', [])
except:
    賽程 = []

if 賽程:
    st.subheader("🗓️ 當日推演 (API 數據)")
    for f in 賽程:
        h_n, a_n = f['teams']['home']['name'], f['teams']['away']['name']
        if h_n in db and a_n in db:
            res = 模擬引擎(h_n, a_n)
            with st.expander(f"📍 {h_n} vs {a_n}"):
                st.write(f"基礎建議: {', '.join(res['波膽'])}")
else:
    st.error("⚠️ 今日無賽事，自動化推演已暫停")

# 手動條件實驗室 (永遠待命)
st.divider()
st.subheader("🛠️ 條件式精算實驗室")
col1, col2 = st.columns(2)
h_pick = col1.selectbox("主隊", list(db.keys()), key="h")
a_pick = col2.selectbox("客隊", list(db.keys()), key="a")
h_mod = st.slider("主隊狀態調整", 0.5, 1.5, 1.0, 0.1)
a_mod = st.slider("客隊狀態調整", 0.5, 1.5, 1.0, 0.1)

if st.button("啟動百萬次模擬推演"):
    res = 模擬引擎(h_pick, a_pick, h_mod, a_mod)
    st.metric("主勝率", f"{res['主勝率']:.1%}")
    st.write(f"建議波膽: **{', '.join(res['波膽'])}**")
