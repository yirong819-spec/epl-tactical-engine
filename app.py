import streamlit as st
import numpy as np
import json
import requests
from scipy.stats import poisson

# 載入數據
db = json.load(open('data/teams.json', 'r', encoding='utf-8'))

def 執行預測邏輯(h_name, a_name):
    h, a = db[h_name], db[a_name]
    expected_h = 1 / (1 + 10 ** ((a['Elo'] - h['Elo']) / 400))
    h_rate = (h['Elo'] / 1800) * 1.5 
    a_rate = (a['Elo'] / 1800) * 1.2
    matrix = np.outer(poisson.pmf(np.arange(6), h_rate), poisson.pmf(np.arange(6), a_rate))
    return expected_h, f"{np.unravel_index(np.argmax(matrix), matrix.shape)[0]}:{np.unravel_index(np.argmax(matrix), matrix.shape)[1]}"

st.title("⚽ 預言家：自動化賽事分析儀")

# 1. 優先執行 API 自動化流程
api_key = st.secrets.get("API_KEY")
try:
    # 嘗試抓取今日賽事 (next=5)
    res = requests.get("https://v3.football.api-sports.io/fixtures?league=39&season=2026&next=5", 
                       headers={'x-apisports-key': api_key}).json()
    賽程 = res.get('response', [])
except:
    賽程 = []

if 賽程:
    st.subheader("🗓️ 今日自動推演結果")
    for f in 賽程:
        h_name = f['teams']['home']['name'] # 注意：這裡可能需要翻譯映射
        a_name = f['teams']['away']['name']
        
        # 僅當隊伍存在於您的 JSON 資料庫時才執行
        if h_name in db and a_name in db:
            勝率, 波膽 = 執行預測邏輯(h_name, a_name)
            with st.expander(f"{h_name} vs {a_name}"):
                st.metric("勝率", f"{勝率:.1%}")
                st.write(f"建議波膽：{波膽}")
else:
    # 2. 只有在無賽事時才開啟手動模式
    st.warning("今日無官方聯賽賽事，切換至手動實驗室")
    col1, col2 = st.columns(2)
    h_pick = col1.selectbox("選擇主隊", list(db.keys()))
    a_pick = col2.selectbox("選擇客隊", list(db.keys()))
    if st.button("啟動精算"):
        勝率, 波膽 = 執行預測邏輯(h_pick, a_pick)
        st.metric(f"{h_pick} 勝率", f"{勝率:.1%}")
        st.write(f"建議波膽：{波膽}")
