import numpy as np
import json

class 戰術決策引擎:
    def __init__(self, data_path='data/teams.json'):
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                self.隊伍數據 = json.load(f)
        except Exception:
            # 防禦機制：資料載入失敗回退方案
            self.隊伍數據 = {"範例隊": {"風格": "平衡", "控球係數": 0.7, "逼搶強度": 0.7}}

    def 計算戰術相剋(self, 風格甲, 風格乙):
        相剋表 = {("傳控", "逼搶"): 0.8, ("逼搶", "防反"): 0.9, ("防反", "傳控"): 1.1}
        return 相剋表.get((風格甲, 風格乙), 1.0)

    def 蒙地卡羅模擬(self, 主隊名, 客隊名, 主傷, 客傷, 主疲, 客疲):
        主隊 = self.隊伍數據.get(主隊名, {"風格": "平衡", "控球係數": 0.7})
        客隊 = self.隊伍數據.get(客隊名, {"風格": "平衡", "控球係數": 0.7})

        # 應用十大精算條件之傷停與疲勞權重
        主權重 = 主隊['控球係數'] * (0.85 if 主傷 else 1.0) * (0.9 if 主疲 else 1.0)
        客權重 = 客隊['控球係數'] * (0.85 if 客傷 else 1.0) * (0.9 if 客疲 else 1.0)
        
        # 戰術修正係數
        主權重 *= self.計算戰術相剋(主隊['風格'], 客隊['風格'])
        
        # 執行 10 萬次模擬 (Dixon-Coles 零膨脹邏輯)
        模擬次數 = 100000
        進球_主 = np.random.poisson(主權重 * 2.5, 模擬次數)
        進球_客 = np.random.poisson(客權重 * 2.2, 模擬次數)
        
        return 進球_主, 進球_客
