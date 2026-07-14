import streamlit as st
from football_engine import 戰略預測引擎

engine = 戰略預測引擎()
st.title("⚽ 2026/27 英超自動化戰略室")

for h, a in engine.取得當日賽程():
    res = engine.計算比分(h, a)
    with st.expander(f"對戰：{h} vs {a}", expanded=True):
        col1, col2, col3 = st.columns(3)
        col1.metric("主勝", f"{res['主勝']:.1%}")
        col2.metric("平", f"{res['平']:.1%}")
        col3.metric("客勝", f"{res['客勝']:.1%}")
        st.write(f"預測波膽：{res['波膽']} | 大分機率：{res['大分機率']:.1%}")
