import numpy as np
import json

class TacticalEngine:
    def __init__(self, data_path='data/teams.json'):
        with open(data_path, 'r', encoding='utf-8') as f:
            self.teams = json.load(f)

    def get_tactical_modifier(self, style_a, style_b):
        """處理戰術相剋：回傳攻擊效率修正係數"""
        # 簡單示例：逼搶剋制傳控
        if style_a == "Control" and style_b == "Pressing":
            return 0.85
        return 1.0

    def simulate_match(self, team_a_name, team_b_name, trials=100000):
        """執行蒙地卡羅物理模擬"""
        t1 = self.teams.get(team_a_name)
        t2 = self.teams.get(team_b_name)

        # 戰術修正
        modifier = self.get_tactical_modifier(t1['Style'], t2['Style'])
        
        # λ 值計算 (基礎能力 * 戰術修正)
        lambda_a = (t1['P_Retention'] * 2.5) * modifier
        lambda_b = (t2['P_Retention'] * 2.2)
        
        # 蒙地卡羅模擬
        goals_a = np.random.poisson(lambda_a, trials)
        goals_b = np.random.poisson(lambda_b, trials)
        
        return goals_a, goals_b
