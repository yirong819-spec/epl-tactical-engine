import streamlit as st
import numpy as np
import json
from scipy.stats import poisson

# 1. 直接在 app.py 定義引擎邏輯，解決 Import 引用的快取錯誤
class 戰略預測引擎:
    def __init__(self):
        with open('data/teams.json', 'r', encoding='utf-8') as f:
            self.teams = json.load(f)

    def 取得當日賽程(self):
        # 此處為您的賽程表，若無 API 則維持此結構
        return [("曼城", "阿森納"), ("利物浦", "切爾西")]

    def 計算比分(self, h, a):
        matrix = np.outer(poisson.pmf(np.arange(6), self.teams[h]['控球係數']*2.5), 
                          poisson.pmf(np.arange(6), self.teams[a]['控球係數']*2.2))
        return {
            "主勝": np.sum(np.tril(matrix, -1)),
            "平": np.sum(np.diag(matrix)),
            "客勝": np.sum(np.triu(matrix, 1)),
            "波膽": f"{np.unravel_index(np.argmax(matrix), matrix.shape)[0]}:{np.unravel_index(np.argmax(matrix), matrix.shape)[1]}",
            "大分機率": 1 - np.sum(matrix[0:3, 0:3])
        }

# 2. 初始化引擎並渲染
st.title("⚽ 2026/27 英超精算室")
engine = 戰略預測引擎()

# 3. 渲染賽程
for h, a in engine.取得當日賽程():
    res = engine.計算比分(h, a)
    with st.expander(f"📍 {h} vs {a}", expanded=True):
        col1, col2, col3 = st.columns(3)
        col1.metric("主勝", f"{res['主勝']:.1%}")
        col2.metric("平局", f"{res['平']:.1%}")
        col3.metric("客勝", f"{res['客勝']:.1%}")
        st.write(f"建議比分：{res['波膽']} | 大分機率：{res['大分機率']:.1%}")
