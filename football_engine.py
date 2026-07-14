import numpy as np
import json
import streamlit as st
from scipy.stats import poisson

class 戰略預測引擎:
    def __init__(self):
        # 請務必確認這裡的路徑正確
        with open('data/teams.json', 'r', encoding='utf-8') as f:
            self.teams = json.load(f)

    @st.cache_data(ttl=3600)
    def 取得當日賽程(self):
        # 為了除錯，我們先回傳一個靜態列表，確保這方法確實存在
        return [("曼城", "阿森納"), ("利物浦", "切爾西")]

    def 計算比分(self, h, a):
        # 運算邏輯...
        matrix = np.outer(poisson.pmf(np.arange(6), self.teams[h]['控球係數']*2.5), 
                          poisson.pmf(np.arange(6), self.teams[a]['控球係數']*2.2))
        return {
            "主勝": np.sum(np.tril(matrix, -1)),
            "平": np.sum(np.diag(matrix)),
            "客勝": np.sum(np.triu(matrix, 1)),
            "波膽": "2:1", 
            "大分機率": 0.5
        }
