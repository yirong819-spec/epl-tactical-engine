import streamlit as st
import numpy as np
import json
import os
from scipy.stats import poisson

# 初始化函數
def 取得數據庫():
    # 確保路徑正確：專案根目錄/data/teams.json
    path = os.path.join('data', 'teams.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"找不到檔案: {path}，請檢查 GitHub 檔案路徑")
        return {}

def 執行模擬(h_data, a_data):
    # 泊松分佈模擬：攻守能力加權
    h_rate = h_data.get('控球係數', 0.5) * 2.5
    a_rate = a_data.get('控球係數', 0.5) * 2.2
    
    # 模擬 10 萬次
    主進球 = np.random.poisson(h_rate, 100000)
    客進球 = np.random.poisson(a_rate, 100000)
    總進球 = 主進球 + 客進球
    
    return {
        "主勝": np.mean(主進球 > 客進球),
        "平局": np.mean(主進球 == 客進球),
        "客勝": np.mean(主進球 < 客進球),
        "大分率": np.mean(總進球 > 2.5),
        "建議波膽": f"{np.bincount(主進球).argmax()}:{np.bincount(客進球).argmax()}"
    }

# 介面
st.title("⚽ 2026/27 英超戰略精算室")
teams = 取得數據庫()

if not teams:
    st.stop() # 停止執行以免發生錯誤

col1, col2 = st.columns(2)
h_pick = col1.selectbox("主隊", list(teams.keys()))
a_pick = col2.selectbox("客隊", list(teams.keys()))

if h_pick and a_pick:
    res = 執行模擬(teams[h_pick], teams[a_pick])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("主勝", f"{res['主勝']:.1%}")
    c2.metric("平局", f"{res['平局']:.1%}")
    c3.metric("客勝", f"{res['客勝']:.1%}")
    
    st.divider()
    st.metric("大分機率 (> 2.5)", f"{res['大分率']:.1%}")
    st.success(f"系統精算建議波膽：{res['建議波膽']}")
