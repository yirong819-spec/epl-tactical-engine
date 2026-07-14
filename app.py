import streamlit as st
import numpy as np
import json
import os
from scipy.stats import poisson

# --- 數據庫載入 ---
def 取得數據庫():
    path = os.path.join('data', 'teams.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {} # 若資料庫不存在則回傳空字典，由後續邏輯處理

# --- 核心模擬器 ---
def 執行模擬(h_data, a_data):
    h_rate = (h_data.get('Elo', 1500) / 1000) * h_data.get('控球係數', 0.5)
    a_rate = (a_data.get('Elo', 1500) / 1000) * a_data.get('控球係數', 0.5)
    主 = np.random.poisson(h_rate, 50000)
    客 = np.random.poisson(a_rate, 50000)
    return {
        "主勝": np.mean(主 > 客), "平局": np.mean(主 == 客), "客勝": np.mean(主 < 客),
        "波膽": f"{np.bincount(主).argmax()}:{np.bincount(客).argmax()}"
    }

# --- 介面層 ---
st.title("⚽ 2026/27 英超全面戰略儀表板")
teams = 取得數據庫()

if not teams:
    st.error("系統偵測不到資料庫，請檢查 data/teams.json 是否正確載入。")
else:
    st.sidebar.header("比賽篩選器")
    # 這裡讓您可以一次選取多場比賽進行對比
    selected_teams = st.sidebar.multiselect("選擇參與預測的隊伍", list(teams.keys()), default=list(teams.keys())[:4])
    
    st.subheader("精算對戰清單")
    
    # 自動遍歷所有已選隊伍的組合
    for i in range(len(selected_teams)):
        for j in range(len(selected_teams)):
            if i != j:
                h, a = selected_teams[i], selected_teams[j]
                res = 執行模擬(teams[h], teams[a])
                
                with st.expander(f"📍 {h} vs {a}"):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("主勝", f"{res['主勝']:.1%}")
                    c2.metric("平局", f"{res['平局']:.1%}")
                    c3.metric("客勝", f"{res['客勝']:.1%}")
                    c4.metric("建議波膽", res['波膽'])
