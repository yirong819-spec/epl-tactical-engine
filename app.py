import streamlit as st
import numpy as np
import json
import requests
from scipy.stats import poisson

# 1. 核心數據庫載入
db = json.load(open('data/teams.json', 'r', encoding='utf-8'))

# 2. 經過回測修正的決策引擎
def 執行嚴謹預測(h_name, a_name):
    h, a = db[h_name], db[a_name]
    
    # 戰術修正：Elo 轉化率
    elo_diff = (h['Elo'] - a['Elo']) / 400
    
    # 基礎期望值
    h_rate = 1.3 + (0.3 * elo_diff)
    a_rate = 1.1 - (0.3 * elo_diff)
    
    # 戰術防守修正：若兩隊均為強隊(Elo > 1700)，進球期望壓縮 15% (避免大比分誤判)
    if h['Elo'] > 1700 and a['Elo'] > 1700:
        h_rate *= 0.85
        a_rate *= 0.85
        
    # 泊松矩陣演算
    matrix = np.outer(poisson.pmf(np.arange(5), h_rate), poisson.pmf(np.arange(5), a_rate))
    
    # 正規化勝平負權重 (Dixon-Coles 常數調整)
    matrix[np.eye(5, dtype=bool)] *= 1.25 
    matrix /= matrix.sum()
    
    return {
        "主勝": np.sum(np.tril(matrix, -1)),
        "平局": np.sum(np.diag(matrix)),
        "客勝": np.sum(np.triu(matrix, 1)),
        "波膽": f"{np.unravel_index(np.argmax(matrix), matrix.shape)[0]}:{np.unravel_index(np.argmax(matrix), matrix.shape)[1]}"
    }

# 3. 儀表板架構 (優先執行自動化，失敗則進入實驗室)
st.title("⚽ 預言家：戰術校準決策終端")

api_key = st.secrets.get("API_KEY")
try:
    res = requests.get("https://v3.football.api-sports.io/fixtures?league=39&season=2026&next=5", 
                       headers={'x-apisports-key': api_key}, timeout=5).json()
    賽程 = res.get('response', [])
except:
    賽程 = []

if 賽程:
    st.subheader("🗓️ 當日自動化賽事推演")
    for f in 賽程:
        h_n, a_n = f['teams']['home']['name'], f['teams']['away']['name']
        if h_n in db and a_n in db:
            res = 執行嚴謹預測(h_n, a_n)
            with st.expander(f"📍 {h_n} vs {a_n}", expanded=True):
                c1, c2, c3 = st.columns(3)
                c1.metric("主勝", f"{res['主勝']:.1%}"); c2.metric("平局", f"{res['平局']:.1%}"); c3.metric("客勝", f"{res['客勝']:.1%}")
                st.write(f"戰術波膽建議: **{res['波膽']}**")
else:
    st.warning("ℹ️ 當前無自動賽程，已自動切換至手動實驗室")

# 強制保留的手動操作區塊
st.divider()
st.subheader("🛠️ 手動校準實驗室")
col1, col2 = st.columns(2)
h_pick = col1.selectbox("主隊", list(db.keys()), key="h")
a_pick = col2.selectbox("客隊", list(db.keys()), key="a")
if st.button("啟動精算"):
    res = 執行嚴謹預測(h_pick, a_pick)
    st.metric("核心主勝率", f"{res['主勝']:.1%}")
    st.write(f"模型精算波膽: **{res['波膽']}**")
