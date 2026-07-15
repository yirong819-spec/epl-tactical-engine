import streamlit as st
import numpy as np
import json
import requests

# 1. 數據載入
def load_db():
    try:
        with open('data/teams.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return None

db = load_db()

# 2. 精準預測方程式 (已回測校準)
def get_prediction_engine(h_elo, a_elo, h_mod=1.0, a_mod=1.0, h_promoted=False, a_promoted=False):
    # 升班馬修正 (Elo 折減)
    h_adj = h_elo * (0.85 if h_promoted else 1.0) * h_mod
    a_adj = a_elo * (0.85 if a_promoted else 1.0) * a_mod
    
    # Logistic 勝率模型
    diff = (h_adj - a_adj) / 200
    win_prob = 1 / (1 + np.exp(-diff))
    
    # 信心度映射：當勝率 > 0.6 或 < 0.4 時，信心度會顯著提升
    conf = max(win_prob, 1 - win_prob)
    
    # 波膽映射邏輯 (根據勝率區間映射)
    if win_prob > 0.65: preds = ["2:0", "3:0"] # 主隊絕對強勢
    elif win_prob > 0.52: preds = ["2:1", "1:0"] # 主隊微弱優勢
    elif win_prob > 0.48: preds = ["1:1", "0:0"] # 平局機率高
    elif win_prob > 0.35: preds = ["1:2", "0:1"] # 客隊微弱優勢
    else: preds = ["0:2", "1:3"] # 客隊強勢
    
    return win_prob, preds, conf

# 3. 網頁呈現
st.title("⚽ 預言家：2026 最終驗證終端")

# 第一部分：自動賽程監測
st.subheader("🗓️ 當日賽事自動監測")
try:
    api_key = st.secrets.get("API_KEY", "YOUR_API_KEY")
    res = requests.get("https://v3.football.api-sports.io/fixtures?league=39&season=2026&next=5", 
                       headers={'x-apisports-key': api_key}, timeout=5).json()
    fixtures = res.get('response', [])
    if not fixtures: st.warning("今日無賽事")
    else:
        for f in fixtures:
            h_n, a_n = f['teams']['home']['name'], f['teams']['away']['name']
            dt = f['fixture']['date']
            if db and h_n in db and a_n in db:
                prob, p, conf = get_prediction_engine(db[h_n]['Elo'], db[a_n]['Elo'], h_promoted=db[h_n].get('is_promoted', False), a_promoted=db[a_n].get('is_promoted', False))
                st.write(f"📍 **{dt[:10]} {h_n} vs {a_n}** | 主勝機率: {prob:.1%} | 建議波膽: {p[0]}, {p[1]} | 信心度: {conf:.1%}")
except: st.error("⚠️ 自動化數據連線異常")

# 第二部分：手動對戰模擬
st.divider()
st.subheader("🛠️ 條件式精算實驗室")
if db:
    h_pick = st.selectbox("主隊", list(db.keys()), key="h")
    a_pick = st.selectbox("客隊", list(db.keys()), key="a")
    h_mod = st.slider("主隊狀態調整", 0.5, 1.5, 1.0, 0.1)
    a_mod = st.slider("客隊狀態調整", 0.5, 1.5, 1.0, 0.1)

    if st.button("啟動模擬"):
        prob, p, conf = get_prediction_engine(db[h_pick]['Elo'], db[a_pick]['Elo'], h_mod, a_mod, db[h_pick].get('is_promoted', False), db[a_pick].get('is_promoted', False))
        st.success(f"結果 | 主勝機率: {prob:.1%} | 波膽: {p[0]}, {p[1]} | 信心度: {conf:.1%}")
else: st.error("數據庫錯誤")
