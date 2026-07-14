import streamlit as st
from football_engine import 戰略預測引擎

st.set_page_config(page_title="2026 英超戰略自動化", layout="wide")
engine = 戰略預測引擎()

st.title("⚽ 2026 英超自動化精算清單")
st.caption("系統已連接至賽程數據庫，自動更新今日對戰資訊。")

# 自動抓取並執行
賽程 = engine.獲取今日賽程()
for home, away in 賽程:
    res = engine.預測單場(home, away)
    if res:
        with st.expander(f"🔴 {home} vs {away}", expanded=True):
            col1, col2, col3 = st.columns(3)
            col1.metric("主勝", f"{res['主勝']:.1%}")
            col2.metric("平", f"{res['平']:.1%}")
            col3.metric("客勝", f"{res['客勝']:.1%}")
            st.write(f"**建議比分：** {res['波膽']} | **大分機率：** {res['大分']:.1%}")
