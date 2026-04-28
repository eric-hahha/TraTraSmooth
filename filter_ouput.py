import json

# 設定原始檔案路徑與輸出路徑
input_file = 'test1_8_050_s 晚上9.28.40.json'
output_file = 'filtered_tracked_id_373.json'
target_tracked_id = 373

# 讀取 JSON 資料
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

filtered_frames = []

# 遍歷每一幀，篩選出符合 tracked_id 的物件
for frame in data.get('frames', []):
    filtered_objects = [obj for obj in frame.get('objects', []) if obj.get('tracked_id') == target_tracked_id]
    
    # 如果該幀包含目標物件，則保留該幀資訊
    if filtered_objects:
        new_frame = frame.copy()
        new_frame['objects'] = filtered_objects
        filtered_frames.append(new_frame)

# 建立新的 JSON 結構
output_data = data.copy()
output_data['frames'] = filtered_frames

# 輸出成 JSON 檔案
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"篩選完成，共找到 {len(filtered_frames)} 幀包含 tracked_id {target_tracked_id} 的資料。")