import streamlit as st
import numpy as np
from football_engine import 戰術決策引擎

st.set_page_config(page_title="2026 英超戰術精算系統", layout="wide")
st.title("⚽ 2026/27 英超戰術基因博弈系統")
引擎 = 戰術決策引擎()

# 側邊欄配置
st.sidebar.header("精算參數配置")
主隊名 = st.sidebar.selectbox("主場球隊", list(引擎.隊伍數據.keys()))
主傷 = st.sidebar.checkbox("主隊：關鍵骨幹傷停")
主疲 = st.sidebar.checkbox("主隊：歐戰疲勞")

st.sidebar.divider()
客隊名 = st.sidebar.selectbox("客場球隊", list(引擎.隊伍數據.keys()))
客傷 = st.sidebar.checkbox("客隊：關鍵骨幹傷停")
客疲 = st.sidebar.checkbox("客隊：歐戰疲勞")

# 自動推演逻辑
進球_主, 進球_客 = 引擎.蒙地卡羅模擬(主隊名, 客隊名, 主傷, 客傷, 主疲, 客疲)

st.divider()
st.subheader("精算預測結果 (基於 10 萬次蒙地卡羅模擬)")
列1, 列2, 列3 = st.columns(3)
列1.metric("主隊獲勝機率", f"{np.mean(進球_主 > 進球_客)*100:.1f}%")
列2.metric("平局機率", f"{np.mean(進球_主 == 進球_客)*100:.1f}%")
列3.metric("客隊獲勝機率", f"{np.mean(進球_主 < 進球_客)*100:.1f}%")
