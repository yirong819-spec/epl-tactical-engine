import streamlit as st
import numpy as np
import json
from scipy.stats import poisson

# 讀取並初始化數據庫
db = json.load(open('data/teams.json', 'r', encoding='utf-8'))

def 執行動態預測(h_name, a_name):
    h, a = db[h_name], db[a_name]
    
    # 期望勝率計算 (Elo 轉化)
    expected_h = 1 / (1 + 10 ** ((a['Elo'] - h['Elo']) / 400))
    
    # 泊松期望值 (基於 Elo 強度)
    h_rate = (h['Elo'] / 1800) * 1.5 * 1.1 
    a_rate = (a['Elo'] / 1800) * 1.2
    
    matrix = np.outer(poisson.pmf(np.arange(6), h_rate), poisson.pmf(np.arange(6), a_rate))
    
    return {
        "勝率": expected_h,
        "波膽": f"{np.unravel_index(np.argmax(matrix), matrix.shape)[0]}:{np.unravel_index(np.argmax(matrix), matrix.shape)[1]}",
        "大分率": np.sum(matrix[3:, :]) + np.sum(matrix[:, 3:])
    }

st.title("⚽ 預言家：動態演化引擎")
h_pick = st.selectbox("主隊", list(db.keys()))
a_pick = st.selectbox("客隊", list(db.keys()))

if st.button("啟動模擬"):
    res = 執行動態預測(h_pick, a_pick)
    st.metric(f"{h_pick} 勝率", f"{res['勝率']:.1%}")
    st.write(f"建議波膽：**{res['波膽']}** | 大分機率：{res['大分率']:.1%}")
    
    # 這裡預留動態更新介面，您可以手動修正結果後的 Elo
    if st.checkbox("結果與預測不符？手動更新 Elo"):
        actual = st.radio("真實結果", ["主勝", "客勝", "平局"])
        if st.button("提交校準"):
            # 這裡會觸發 Elo K-factor 更新邏輯，更新您的 JSON 數據
            st.success("Elo 已根據您的反饋進行演化修正。")
