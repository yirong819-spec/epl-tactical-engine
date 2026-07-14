import streamlit as st
import numpy as np
import json
import os
from scipy.stats import poisson

# --- 1. 數據庫初始化 (穩定讀取) ---
def 取得數據庫():
    # 檢查 data/teams.json 是否存在
    if os.path.exists('data/teams.json'):
        try:
            with open('data/teams.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    # 若檔案不存在或損壞，回傳預設數據以防系統崩潰
    return {
        "曼城": {"Elo": 2050, "控球係數": 0.96}, 
        "阿森納": {"Elo": 2010, "控球係數": 0.94},
        "利物浦": {"Elo": 1980, "控球係數": 0.90},
        "切爾西": {"Elo": 1900, "控球係數": 0.84}
    }

# --- 2. 核心精算模型 (泊松分佈) ---
def 執行預言(h_data, a_data):
    # 預測邏輯：以 Elo 與 控球係數 為變數
    h_rate = (h_data.get('Elo', 1500) / 1000) * h_data.get('控球係數', 0.5)
    a_rate = (a_data.get('Elo', 1500) / 1000) * a_data.get('控球係數', 0.5)
    
    # 模擬 50,000 場比賽
    主進球 = np.random.poisson(h_rate, 50000)
    客進球 = np.random.poisson(a_rate, 50000)
    總進球 = 主進球 + 客進球
    
    return {
        "主勝": np.mean(主進球 > 客進球),
        "平局": np.mean(主進球 == 客進球),
        "客勝": np.mean(主進球 < 客進球),
        "大分率": np.mean(總進球 > 2.5),
        "建議波膽": f"{np.bincount(主進球).argmax()}:{np.bincount(客進球).argmax()}"
    }

# --- 3. UI 渲染 (預言家視覺化) ---
st.title("⚽ 2026/27 英超預言家精算系統")
teams = 取得數據庫()

st.subheader("深度對戰精算")
col1, col2 = st.columns(2)
h_pick = col1.selectbox("選擇主隊", list(teams.keys()))
a_pick = col2.selectbox("選擇客隊", list(teams.keys()))

if st.button("啟動預言"):
    res = 執行預言(teams[h_pick], teams[a_pick])
    
    # 顯示勝率儀表板
    c1, c2, c3 = st.columns(3)
    c1.metric("主勝", f"{res['主勝']:.1%}")
    c2.metric("平局", f"{res['平局']:.1%}")
    c3.metric("客勝", f"{res['客勝']:.1%}")
    
    st.divider()
    st.metric("大分機率 (> 2.5 球)", f"{res['大分率']:.1%}")
    st.success(f"系統預言波膽：{res['建議波膽']}")
