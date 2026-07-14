import streamlit as st
import numpy as np
import json
from scipy.stats import poisson

# 1. 初始化引擎數據庫 (請確保 data/teams.json 在正確路徑)
def 取得數據庫():
    try:
        with open('data/teams.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"曼城": {"控球係數": 0.96}, "阿森納": {"控球係數": 0.94}} # 備用預設

def 執行模擬(h_data, a_data, 模擬次數=100000):
    主進球 = np.random.poisson(h_data['控球係數'] * 2.5, 模擬次數)
    客進球 = np.random.poisson(a_data['控球係數'] * 2.2, 模擬次數)
    總進球 = 主進球 + 客進球
    
    return {
        "主勝": np.mean(主進球 > 客進球),
        "平局": np.mean(主進球 == 客進球),
        "客勝": np.mean(主進球 < 客進球),
        "大分率": np.mean(總進球 > 2.5),
        "建議波膽": f"{np.bincount(主進球).argmax()}:{np.bincount(客進球).argmax()}"
    }

# 2. UI 渲染層
st.title("⚽ 2026/27 英超戰略精算系統")
teams = 取得數據庫()

# 賽程模擬 (自動與手動切換)
st.subheader("今日賽程預測")
賽程 = [] # 若無賽事則為空列表

if not 賽程:
    st.warning("今日暫無官方賽程。已自動切換至：深度自選模擬模式")
    col1, col2 = st.columns(2)
    h_pick = col1.selectbox("主隊", list(teams.keys()))
    a_pick = col2.selectbox("客隊", list(teams.keys()))
    if h_pick and a_pick:
        res = 執行模擬(teams[h_pick], teams[a_pick])
        st.write(f"### 對戰：{h_pick} vs {a_pick}")
        c1, c2, c3 = st.columns(3)
        c1.metric("主勝", f"{res['主勝']:.1%}")
        c2.metric("平", f"{res['平']:.1%}")
        c3.metric("客勝", f"{res['客勝']:.1%}")
        st.info(f"建議波膽：{res['建議波膽']} | 大分機率：{res['大分率']:.1%}")
