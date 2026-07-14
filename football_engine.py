import numpy as np
import json
import requests
from bs4 import BeautifulSoup
from scipy.stats import poisson

class 戰略預測引擎:
    def __init__(self):
        with open('data/teams.json', 'r', encoding='utf-8') as f:
            self.teams = json.load(f)

    def 獲取今日賽程(self):
        # 這裡連接至英超公開賽程 API 或數據抓取點
        # 為確保穩定性，我們使用結構化數據源
        url = "https://www.premierleague.com/fixtures" 
        # 實際部署時，這裡會解析該網頁的當日賽程
        return [("曼城", "阿森納"), ("利物浦", "切爾西")] # 模擬返回

    def 預測單場(self, h_name, a_name):
        h, a = self.teams.get(h_name), self.teams.get(a_name)
        if not h or not a: return None
        
        matrix = np.outer(poisson.pmf(np.arange(6), h['控球係數']*2.8), 
                          poisson.pmf(np.arange(6), a['控球係數']*2.5))
        
        return {
            "主勝": np.sum(np.tril(matrix, -1)),
            "平": np.sum(np.diag(matrix)),
            "客勝": np.sum(np.triu(matrix, 1)),
            "波膽": f"{np.unravel_index(np.argmax(matrix), matrix.shape)[0]}:{np.unravel_index(np.argmax(matrix), matrix.shape)[1]}",
            "大分": 1 - np.sum(matrix[0:3, 0:3])
        }
