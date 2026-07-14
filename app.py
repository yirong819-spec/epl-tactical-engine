import streamlit as st
import numpy as np
import requests
import json
import os
from scipy.stats import poisson

# --- 隊名映射 ---
隊名對照 = {
    "Arsenal": "阿森納", "Manchester City": "曼城", "Liverpool": "利物浦",
    "Chelsea": "切爾西", "Tottenham": "熱刺", "Newcastle": "紐卡索聯",
    "Manchester United": "曼聯", "Aston Villa": "阿斯頓維拉", "Brighton": "布萊頓"
}

def 執行模擬(h_data, a_data):
    # 核心邏輯：Elo 差異決定期望值
    h_rate = (h_data.get('Elo', 1500) / 1000) * h_data.get('控球係數', 0.5) * 2.5
    a_rate = (a_data.get('Elo', 1500) / 1000) * a_data.get('控球係數', 0.5) * 2.2
    
    主 = np.random.poisson(h_rate, 50000)
    客 = np.random.poisson(a_rate, 50000)
    總 = 主 + 客
    
    return {
        "主勝": np.mean(主 > 客), "平局": np.mean(主 == 客), "客勝": np.mean(主 < 客),
        "大分率": np.mean(總 > 2.5), "小分率": np.mean(總 <= 2.5),
        "波膽": f"{np.bincount(主).argmax()}:{np.bincount(客).argmax()}"
    }

st.title("⚽ 2026 英超預言家：完整儀表板")
teams = json.load(open('data/teams.json', 'r', encoding='utf-8'))

# 獲取 API 賽程
try:
    api_key = st.secrets["API_KEY"]
    res = requests.get("https://v3.football.api-sports.io/fixtures?league=39&season=2026&next=10", 
                       headers={'x-apisports-key': api_key}).json()
    賽程 = [(隊名對照.get(f['teams']['home']['name'], f['teams']['home']['name']), 
             隊名對照.get(f['teams']['away']['name'], f['teams']['away']['name'])) 
            for f in res.get('response', [])]
except:
    賽程 = []

if 賽程:
    for h, a in 賽程:
        if h in teams and a in teams:
            res = 執行模擬(teams[h], teams[a])
            with st.expander(f"📍 {h} vs {a}", expanded=True):
                # 第一排：勝平負
                c1, c2, c3 = st.columns(3)
                c1.metric("主勝", f"{res['主勝']:.1%}"); c2.metric("平局", f"{res['平局']:.1%}"); c3.metric("客勝", f"{res['客勝']:.1%}")
                # 第二排：大小分與波膽
                c4, c5, c6 = st.columns(3)
                c4.metric("大分 (>2.5)", f"{res['大分率']:.1%}"); c5.metric("小分 (<=2.5)", f"{res['小分率']:.1%}"); c6.metric("建議波膽", res['波膽'])
else:
    st.info("今日無賽事，切換至自由精算模式")
    h_pick = st.selectbox("主隊", list(teams.keys()))
    a_pick = st.selectbox("客隊", list(teams.keys()))
    if st.button("啟動預言"):
        res = 執行模擬(teams[h_pick], teams[a_pick])
        st.write(f"### 勝負：主 {res['主勝']:.1%} | 平 {res['平局']:.1%} | 客 {res['客勝']:.1%}")
        st.write(f"### 大小分：大 {res['大分率']:.1%} | 小 {res['小分率']:.1%} | 波膽: {res['波膽']}")
