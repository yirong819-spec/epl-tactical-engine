import streamlit as st
import numpy as np
import json
import requests
from scipy.stats import poisson

# 讀取數據
try:
    db = json.load(open('data/teams.json', 'r', encoding='utf-8'))
except:
    db = {}

def 專業精算引擎(h_elo, a_elo):
    # 1. 基礎期望值 (使用對數壓縮防止數值膨脹)
    h_attack = np.log1p(h_elo / 1000) * 1.5
    a_attack = np.log1p(a_elo / 1000) * 1.2
    
    # 2. Dixon-Coles 修正 (考慮平局因素)
    # 將平局常數引入矩陣，使勝率回歸現實區間 (通常強隊主勝在 45-55%)
    matrix = np.outer(poisson.pmf(np.arange(6), h_attack), poisson.pmf(np.arange(6), a_attack))
    
    # 平局修正：平局的機率在泊松分佈中常被低估，需手動賦予權重
    diag = np.diag(matrix)
    matrix[np.eye(6, dtype=bool)] = diag * 1.25 # 提升平局權重 25%
    matrix /= matrix.sum() # 正規化矩陣
    
    # 3. 軌道二：極端風險模擬
    爆發力 = np.random.exponential(0.15, 50000)
    主進球 = np.random.poisson(h_attack, 50000) * (1 + 爆發力)
    客進球 = np.random.poisson(a_attack, 50000)
    
    return {
        "主勝": np.sum(np.tril(matrix, -1)),
        "平局": np.sum(np.diag(matrix)),
        "客勝": np.sum(np.triu(matrix, 1)),
        "爆冷風險": np.mean(主進球 > 客進球 + 3) if h_elo < a_elo else np.mean(客進球 > 主進球 + 3),
        "波膽": f"{np.unravel_index(np.argmax(matrix), matrix.shape)[0]}:{np.unravel_index(np.argmax(matrix), matrix.shape)[1]}"
    }

st.title("⚽ 預言家：專業決策終端")

# API 優先推演
api_key = st.secrets.get("API_KEY")
try:
    res = requests.get("https://v3.football.api-sports.io/fixtures?league=39&season=2026&next=5", 
                       headers={'x-apisports-key': api_key}).json()
    賽程 = res.get('response', [])
except:
    賽程 = []

if 賽程:
    for f in 賽程:
        h_name, a_name = f['teams']['home']['name'], f['teams']['away']['name']
        if h_name in db and a_name in db:
            res = 專業精算引擎(db[h_name]['Elo'], db[a_name]['Elo'])
            with st.expander(f"📍 {h_name} vs {a_name}", expanded=True):
                c1, c2, c3 = st.columns(3)
                c1.metric("主勝", f"{res['主勝']:.1%}"); c2.metric("平局", f"{res['平局']:.1%}"); c3.metric("客勝", f"{res['客勝']:.1%}")
                st.write(f"建議波膽: **{res['波膽']}** | 爆冷/大勝風險: {res['爆冷風險']:.1%}")
else:
    st.info("今日無賽事，切換手動模式")
    # ... (手動選擇區塊)
