import streamlit as st
from football_engine import TacticalEngine

st.title("⚽ 英超戰術精算系統")
engine = TacticalEngine()

# 側邊欄配置
st.sidebar.header("賽事設定")
home = st.sidebar.selectbox("主隊", list(engine.teams.keys()))
away = st.sidebar.selectbox("客隊", list(engine.teams.keys()))

# 執行模擬
if st.sidebar.button("開始模擬"):
    g_a, g_b = engine.simulate_match(home, away)
    
    # 計算勝平負機率
    home_win = np.mean(g_a > g_b) * 100
    draw = np.mean(g_a == g_b) * 100
    away_win = np.mean(g_a < g_b) * 100
    
    st.write(f"### 預測結果")
    st.metric("主隊勝率", f"{home_win:.1f}%")
    st.metric("平局機率", f"{draw:.1f}%")
    st.metric("客隊勝率", f"{away_win:.1f}%")

