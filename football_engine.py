import numpy as np
import json
import streamlit as st
import requests
from bs4 import BeautifulSoup
from scipy.stats import poisson

class 戰略預測引擎:
    def __init__(self):
        with open('data/teams.json', 'r', encoding='utf-8') as f:
            self.teams = json.load(f)

    @st.cache_data(ttl=3600)
    def 取得當日賽程(self):
        # 這裡模擬自動獲取賽程，您可以把真實 URL 填入
        # 為了系統穩定，我建議先用一個固定結構的列表確保不會崩潰
        return [("曼城", "阿森納"), ("利物浦", "切爾西")]

    def 計算比分(self, h, a):
        # 泊松分佈計算比分機率
        matrix = np.outer(poisson.pmf(np.arange(6), self.teams[h]['控球係數']*2.5), 
                          poisson.pmf(np.arange(6), self.teams[a]['控球係數']*2.2))
        return {
            "主勝": np.sum(np.tril(matrix, -1)),
            "平": np.sum(np.diag(matrix)),
            "客勝": np.sum(np.triu(matrix, 1)),
            "波膽": f"{np.unravel_index(np.argmax(matrix), matrix.shape)[0]}:{np.unravel_index(np.argmax(matrix), matrix.shape)[1]}",
            "大分機率": 1 - np.sum(matrix[0:3, 0:3])
        }
