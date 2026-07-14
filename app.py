import streamlit as st
import numpy as np
import json
import requests
from scipy.stats import poisson

# 讀取數據
try:
    db = json.load(open('data/teams.json', 'r', encoding='utf-8'))
except:
    db = {}

def 執行預測邏輯(h_name, a_name):
    h, a = db[h_name], db[a_name]
    expected_h = 1 / (1 + 10 ** ((a['Elo'] - h['Elo']) / 400))
    h_rate = (h['Elo'] / 1800) * 1.5 
    a_rate = (a['Elo'] / 1800) * 1.2
    matrix = np.outer(poisson.pmf(np.arange(6), h_rate), poisson.pmf(np.arange(6), a_rate))
    return expected_h, f"{np.unravel_index(np.argmax(matrix), matrix.shape)[0]}:{np.unravel_index(np.argmax(matrix), matrix.shape)[1]}"

st.title("⚽ 預言家：自動化賽事分析儀")

# API 嘗試
api_key = st.secrets.get("API_KEY")
賽程 = []
try:
    res = requests.get("https://v3.football.api-sports.io/fixtures?league=39&season=2026&next=5", 
                       headers={'x-apisports-key': api_key}, timeout=5).json()
    賽程 = res.get('response', [])
except:
    pass

# === 修正點：即便沒有賽程，也強制顯示手動區塊 ===
if 賽程:
    st.subheader("🗓️ 今日自動推演")
    for f in 賽程:
        h_n = f['teams']['home']['name']
        a_n = f['teams']['away']['name']
        if h_n in db and a_n in db:
            勝率, 波膽 = 執行預測邏輯(h_n, a_n)
            with st.expander(f"{h_n} vs {a_n}"):
                st.metric("勝率", f"{勝率:.1%}")
                st.write(f"建議波膽：{波膽}")
else:
    st.warning("⚠️ 目前無自動化賽事數據，進入手動分析模式")

# === 強制顯示手動區塊，不再消失 ===
st.divider()
st.subheader("🛠️ 手動精算實驗室")
col1, col2 = st.columns(2)
h_pick = col1.selectbox("選擇主隊", list(db.keys()), key="h")
a_pick = col2.selectbox("選擇客隊", list(db.keys()), key="a")
if st.button("啟動精算"):
    勝率, 波膽 = 執行預測邏輯(h_pick, a_pick)
    st.metric(f"{h_pick} 勝率", f"{勝率:.1%}")
    st.write(f"建議波膽：{波膽}")
