import json
import numpy as np
from scipy.signal import savgol_filter

def smooth_trajectories(input_file, output_file, window_length=11, polyorder=3):
    # 讀取原始 JSON 檔案
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. 依照 tracked_id 收集所有座標點
    # 建立一個字典，鍵為 id，值為該物件在各影格中的引用與座標
    trajectories = {}

    for frame in data['frames']:
        for obj in frame.get('objects', []):
            tid = obj.get('tracked_id')
            if tid is not None:
                if tid not in trajectories:
                    trajectories[tid] = []
                # 儲存物件引用以供後續修改，以及座標值
                trajectories[tid].append({
                    'obj_ref': obj,
                    'coords': obj['sat_coords']
                })

    # 2. 對每個 ID 的軌跡進行平滑處理
    for tid, points in trajectories.items():
        if len(points) < window_length:
            # 如果資料點太少，不足以進行濾波，則跳過或縮小視窗
            continue

        # 提取座標數組 (N, 2)
        coords_array = np.array([p['coords'] for p in points])
        
        try:
            # 分別對 X 和 Y 軸進行平滑
            # savgol_filter 會根據周圍點擬合多項式，消除微小抖動
            smoothed_x = savgol_filter(coords_array[:, 0], window_length, polyorder)
            smoothed_y = savgol_filter(coords_array[:, 1], window_length, polyorder)

            # 3. 將平滑後的座標寫回原始物件結構中
            for i, p in enumerate(points):
                p['obj_ref']['sat_coords'] = [float(smoothed_x[i]), float(smoothed_y[i])]
                
                # 同步更新中心點 sat_center (如果你的結構中有這個欄位)
                if 'sat_center' in p['obj_ref']:
                    p['obj_ref']['sat_center'] = [float(smoothed_x[i]), float(smoothed_y[i])]
                    
        except Exception as e:
            print(f"處理 ID {tid} 時發生錯誤: {e}")

    # 4. 輸出新檔案
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"成功處理完成！已儲存至: {output_file}")

def main():
    """主函數，當直接執行此腳本時調用"""
    input_json = 'test1_8_50_s.json'  # 你的原始檔名
    output_json = 'test1_8_50_s_smoothed.json' # 輸出檔名

    # window_length 必須是奇數，代表計算平滑的範圍（影格數）
    # 49.97 fps 下，設定 11 或 15 大約是處理 0.2~0.3 秒內的震盪
    smooth_trajectories(input_json, output_json, window_length=45, polyorder=3)

if __name__ == "__main__":
    main()