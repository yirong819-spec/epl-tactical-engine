import numpy as np
import json
import os
from scipy.stats import poisson

class 戰略預測引擎:
    def __init__(self):
        with open('data/teams.json', 'r', encoding='utf-8') as f:
            self.teams = json.load(f)

    def 預測單場(self, h_name, a_name):
        h, a = self.teams.get(h_name), self.teams.get(a_name)
        # 泊松分佈運算矩陣
        matrix = np.outer(poisson.pmf(np.arange(6), h['控球係數']*2.8), 
                          poisson.pmf(np.arange(6), a['控球係數']*2.5))
        
        home_win = np.sum(np.tril(matrix, -1))
        draw = np.sum(np.diag(matrix))
        away_win = np.sum(np.triu(matrix, 1))
        score_idx = np.unravel_index(np.argmax(matrix), matrix.shape)
        
        return {
            "主勝": home_win, "平": draw, "客勝": away_win,
            "波膽": f"{score_idx[0]}:{score_idx[1]}",
            "大分機率": 1 - np.sum(matrix[0:3, 0:3])
        }
