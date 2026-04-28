# 軌跡處理主控制器使用說明

這個主控制器 (`main_controller.py`) 可以調用 `improve.py` 和 `trajectory_cli.py` 的功能，提供統一的軌跡處理介面。

## Conda 環境設置

建議使用專案內的 [environment.yml](/Users/eric/code/traffic-trajectory-smooth/environment.yml) 建立環境：

```bash
conda env create -f environment.yml
conda activate traffic-trajectory-smooth
```

如果之後更新了依賴，可以同步環境：

```bash
conda env update -f environment.yml --prune
```

確認安裝成功：

```bash
python -c "import numpy, scipy, matplotlib, PIL; print('conda env ok')"
```

## 功能特色

1. **軌跡平滑處理**: 使用 `improve.py` 的功能對軌跡進行平滑處理
2. **軌跡繪圖**: 使用 `trajectory_cli.py` 的功能繪製軌跡圖表
3. **靈活的處理模式**: 支援原始軌跡繪圖、平滑軌跡處理，或兩者並行
4. **分離式軌跡選擇**: 支援分別選擇要處理的軌跡和要輸出的軌跡
5. **多種選擇方式**: 包括特定 ID、類別、範圍選擇

## 核心概念

### 處理軌跡 vs 輸出軌跡

- **處理軌跡**: 指定哪些軌跡要進行平滑處理（僅影響平滑算法的計算）
- **輸出軌跡**: 指定哪些軌跡要在最終圖表中顯示

### 重要特性

- **平滑軌跡輸出選擇**: 從平滑後的 JSON 文件中選擇輸出軌跡，可以看到所有軌跡（包括處理過和沒有處理過的）
- **原始軌跡輸出選擇**: 從原始文件中選擇輸出軌跡
- **狀態標記**: 系統會標記每條軌跡是「已處理」還是「原始」狀態

這種設計允許你：
- 處理特定軌跡以獲得平滑效果
- 從平滑後的文件中選擇任意軌跡進行輸出（包括未處理的原始軌跡）
- 比較處理過和未處理的軌跡效果

## 使用方法

### 基本用法

```bash
# 處理軌跡文件（默認會執行平滑處理和繪圖，需要選擇軌跡）
python main_controller.py test1_8_50_s.json

# 僅執行平滑處理和繪圖
python main_controller.py test1_8_50_s.json --mode smooth

# 僅執行原始軌跡繪圖
python main_controller.py test1_8_050_s.json --mode original

# 僅執行測試放大輸出（依輸出軌跡的整體範圍等比放大）
python main_controller.py test1_8_050_s.json --mode test

# 執行兩種處理（原始 + 平滑）
python main_controller.py test1_8_50_s.json --mode both
```

### 進階參數

```bash
# 自定義平滑參數
python main_controller.py test1_8_50_s.json --window-length 21 --polyorder 2

# 指定輸出目錄
python main_controller.py test1_8_50_s.json --output-dir ./results/
```

### 參數說明

- `input_file`: 輸入的 JSON 軌跡文件（必需）
- `--mode`: 處理模式
  - `smooth`: 僅執行平滑處理和繪圖
  - `original`: 僅執行原始軌跡繪圖
  - `test`: 僅執行原始軌跡的放大測試輸出，會根據所有要輸出的軌跡共同的 `x/y` 極值做等比放大，直到寬或高其中一邊貼齊圖片
  - `both`: 執行兩種處理（默認）
- `--window-length`: 平滑窗口長度，必須為奇數（默認 45）
- `--polyorder`: 多項式階數（默認 3）
- `--output-dir`: 輸出目錄（可選）

## 軌跡選擇流程

### 單一模式 (original 或 smooth)

1. **步驟 1**: 選擇要處理的軌跡
2. **步驟 2**: 
   - **原始模式**: 從原始文件中選擇要輸出的軌跡
   - **平滑模式**: 從平滑後的文件中選擇要輸出的軌跡（包含所有軌跡）

### Both 模式

1. **步驟 1**: 選擇要處理的軌跡
2. **執行平滑處理**: 生成平滑後的 JSON 文件
3. **步驟 2**: 從平滑後的文件中選擇要輸出的軌跡（原始和平滑圖表共用）
4. 執行原始軌跡繪圖
5. 執行平滑軌跡繪圖

## 軌跡選擇方式

程序會自動顯示所有可用的軌跡，並提供以下選擇方式：

### 1. 處理/輸出所有軌跡
- 選擇選項 1
- 處理或輸出文件中的所有軌跡

### 2. 選擇特定 ID
- 選擇選項 2
- 輸入要處理/輸出的軌跡 ID，用逗號分隔
- 例如：`7,373,738`

### 3. 按類別選擇
- 選擇選項 3
- 系統會顯示所有可用的物件類別（如 Car、Truck、Two_Wheeler 等）
- 選擇要處理/輸出的類別編號，用逗號分隔
- 例如：`1,3` 選擇第 1 和第 3 個類別

### 4. 選擇 ID 範圍
- 選擇選項 4
- 輸入起始和結束 ID
- 系統會處理/輸出該範圍內的所有軌跡

### 5. 只輸出已處理的軌跡 (僅輸出選擇時可用)
- 選擇選項 5
- 只選擇在處理階段被選中的軌跡

### 6. 只輸出原始軌跡 (僅輸出選擇時可用)
- 選擇選項 6
- 只選擇在處理階段未被選中的軌跡

### 7. 取消操作
- 選擇選項 0
- 取消當前操作

## 輸出文件

根據選擇的模式和軌跡，會生成以下文件：

1. **平滑軌跡文件**: `{原文件名}_smoothed.json`
2. **原始軌跡圖**: 
   - 所有軌跡: `trajectory_plot_{位置名}_{原文件名}_all.png`
   - 特定軌跡: `trajectory_plot_{位置名}_{原文件名}_IDs_{ID列表}.png`
3. **測試放大軌跡圖**:
   - 通用輸出: `trajectory_plot_test_{原文件名}.png`
   - 特定軌跡: `trajectory_plot_test_{原文件名}_IDs_{ID列表}.png`
4. **平滑軌跡圖**: 
   - 所有軌跡: `trajectory_plot_{位置名}_{原文件名}_smoothed_all.png`
   - 特定軌跡: `trajectory_plot_{位置名}_{原文件名}_smoothed_IDs_{ID列表}.png`

## 使用範例

### 範例 1: 處理所有軌跡，輸出特定軌跡
```bash
python main_controller.py test1_8_50_s.json --mode smooth

# 交互過程:
# 步驟 1 - 選擇要處理的軌跡:
# 選擇選項 (0-4): 1  # 處理所有軌跡

# 步驟 2 - 從平滑後的文件中選擇要輸出的軌跡:
# 選擇選項 (0-6): 2  # 選擇特定 ID
# 請輸入要輸出的軌跡 ID: 7,373

# 結果: 所有軌跡都被處理以獲得最佳平滑效果，但只輸出 ID 7 和 373
# 注意: 輸出選擇是從平滑後的文件中進行，可以看到所有軌跡（包括處理過和未處理的）
```

### 範例 2: 處理特定軌跡，輸出包含未處理軌跡
```bash
python main_controller.py test1_8_50_s.json --mode smooth

# 交互過程:
# 步驟 1 - 選擇要處理的軌跡:
# 選擇選項 (0-4): 3  # 按類別選擇
# 請選擇類別編號: 1  # 選擇 Car 類別

# 步驟 2 - 從平滑後的文件中選擇要輸出的軌跡:
# 選擇選項 (0-6): 1  # 輸出所有軌跡

# 結果: 只有 Car 類別的軌跡被平滑處理，但輸出包含所有軌跡
# 可以比較處理過的 Car 軌跡和未處理的其他軌跡
```

### 範例 3: 使用狀態篩選功能
```bash
python main_controller.py test1_8_50_s.json --mode smooth

# 交互過程:
# 步驟 1 - 選擇要處理的軌跡:
# 選擇選項 (0-4): 2  # 選擇特定 ID
# 請輸入要處理的軌跡 ID: 7,373

# 步驟 2 - 從平滑後的文件中選擇要輸出的軌跡:
# 選擇選項 (0-6): 5  # 只輸出已處理的軌跡

# 結果: 只處理 ID 7 和 373，並且只輸出這些已處理的軌跡
```

### 範例 4: Both 模式統一選擇
```bash
python main_controller.py test1_8_50_s.json --mode both

# 交互過程:
# 步驟 1: 選擇要處理的軌跡
# 選擇選項 (0-4): 1  # 處理所有軌跡

# 執行平滑處理...

# 步驟 2: 從平滑後的文件中選擇要輸出的軌跡
# 選擇選項 (0-6): 6  # 只輸出原始軌跡

# 結果: 
# - 所有軌跡都被平滑處理
# - 原始和平滑圖表都只顯示未被處理的軌跡（在這個例子中是矛盾的，因為所有軌跡都被處理了）
# - 實際上會顯示空結果或錯誤訊息
```

### 範例 5: 自定義平滑參數
```bash
python main_controller.py test1_8_100_s.json --window-length 11 --polyorder 2

# 使用較小的窗口長度進行更細緻的平滑
```

## 實際應用場景

### 場景 1: 最佳平滑效果
- **處理**: 選擇所有軌跡（讓算法考慮所有軌跡的相互影響）
- **輸出**: 選擇感興趣的特定軌跡
- **適用**: 當你想要最佳的平滑效果，但只關心特定軌跡的結果

### 場景 2: 快速處理
- **處理**: 只選擇感興趣的軌跡
- **輸出**: 輸出所有處理過的軌跡
- **適用**: 當你只關心特定軌跡，且想要快速處理

### 場景 3: 比較分析
- **處理**: 選擇特定類別的軌跡
- **輸出**: 從中選擇代表性的軌跡
- **適用**: 當你想要分析特定類別的軌跡行為

## 模塊化調用

你也可以在其他 Python 腳本中導入和使用這些功能：

```python
from main_controller import smooth_and_plot, process_original_and_plot, select_trajectories_for_processing, select_trajectories_for_output
from trajectory_cli import TrajectoryPlotterCLI

# 手動選擇軌跡
plotter = TrajectoryPlotterCLI()
plotter.load_trajectory_data('test1_8_50_s.json')

# 選擇要處理的軌跡
processing_ids = select_trajectories_for_processing(plotter)

# 選擇要輸出的軌跡
output_ids = select_trajectories_for_output(plotter, processing_ids)

# 執行處理
smoothed_file, plot_file = smooth_and_plot('test1_8_50_s.json', 
                                          selected_ids=processing_ids, 
                                          output_ids=output_ids)
original_plot = process_original_and_plot('test1_8_50_s.json', 
                                        selected_ids=processing_ids, 
                                        output_ids=output_ids)
```

## 依賴需求

確保已安裝所需的 Python 套件：

```bash
pip install -r trajectory_plotter_requirements.txt
```

主要依賴包括：
- numpy
- scipy
- matplotlib
- PIL (Pillow)
- json

## 修改說明

### 對 `improve.py` 的修改
- 添加了 `main()` 函數和 `if __name__ == "__main__":` 檢查
- 使其可以作為模塊導入，同時保持獨立執行能力

### 對 `trajectory_cli.py` 的修改
- 改進了衛星圖像載入邏輯，支援多種路徑格式
- 添加了 `plot_selected_trajectories()` 方法，支援繪製指定的軌跡
- 保持原有的交互式選擇功能

### 新增的 `main_controller.py`
- 統一的命令行介面
- 分離式軌跡選擇（處理 vs 輸出）
- 豐富的軌跡選擇選項（ID、類別、範圍）
- 智能的文件命名規則
- 完整的錯誤處理和狀態報告
- Both 模式的統一選擇機制
- 支援複雜的軌跡處理工作流程
