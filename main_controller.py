#!/usr/bin/env python3
"""
主控制器 - 調用 improve.py 和 trajectory_cli.py 的功能
"""

import sys
import os
from pathlib import Path
import argparse

# 導入自定義模塊
import improve
from trajectory_cli import TrajectoryPlotterCLI


def smooth_and_plot(input_file, window_length=45, polyorder=3, plot_output=None, selected_ids=None,
                    output_ids=None, zoom_to_fit=False, title_prefix="Selected Object Trajectories"):
    """
    執行軌跡平滑處理並繪製圖表
    
    Args:
        input_file (str): 輸入的 JSON 文件路徑
        window_length (int): 平滑窗口長度（必須為奇數）
        polyorder (int): 多項式階數
        plot_output (str): 圖表輸出文件名（可選）
        selected_ids (list): 預選的要處理的軌跡 ID 列表（可選）
        output_ids (list): 預選的要輸出的軌跡 ID 列表（可選）
    
    Returns:
        tuple: (smoothed_file_path, plot_file_path)
    """
    
    # 1. 執行軌跡平滑
    print("=" * 50)
    print("步驟 1: 執行軌跡平滑處理")
    print("=" * 50)
    
    input_path = Path(input_file)
    smoothed_file = f"{input_path.stem}_smoothed.json"
    
    print(f"輸入文件: {input_file}")
    print(f"輸出文件: {smoothed_file}")
    print(f"窗口長度: {window_length}")
    print(f"多項式階數: {polyorder}")
    
    try:
        improve.smooth_trajectories(input_file, smoothed_file, window_length, polyorder)
        print("✓ 軌跡平滑處理完成")
    except Exception as e:
        print(f"✗ 軌跡平滑處理失敗: {e}")
        return None, None
    
    # 2. 執行軌跡繪圖
    print("\n" + "=" * 50)
    print("步驟 2: 執行軌跡繪圖")
    print("=" * 50)
    
    try:
        plotter = TrajectoryPlotterCLI()
        
        # 載入平滑後的軌跡數據
        if not plotter.load_trajectory_data(smoothed_file):
            print("✗ 無法載入軌跡數據")
            return smoothed_file, None
        
        # 載入衛星圖像
        if not plotter.load_satellite_image():
            print("✗ 無法載入衛星圖像")
            return smoothed_file, None
        
        # 如果沒有預選的要處理的軌跡 ID，則讓用戶選擇
        if selected_ids is None:
            print("步驟 2.1: 選擇要處理的軌跡")
            selected_ids = select_trajectories_for_processing(plotter)
            
        if not selected_ids:
            print("沒有選擇軌跡進行處理")
            return smoothed_file, None
        
        print(f"將處理 {len(selected_ids)} 條軌跡: {selected_ids}")
        
        # 如果沒有預選的要輸出的軌跡 ID，則讓用戶從平滑後的文件中選擇
        if output_ids is None:
            print("\n步驟 2.2: 從平滑後的文件中選擇要輸出的軌跡")
            output_ids = select_trajectories_for_output(smoothed_file, selected_ids)
            
        if not output_ids:
            print("沒有選擇軌跡進行輸出")
            return smoothed_file, None
        
        print(f"將輸出 {len(output_ids)} 條軌跡: {output_ids}")
        
        # 生成輸出文件名
        if plot_output is None:
            if len(output_ids) == len(plotter.extract_trajectories()):
                plot_output = f"trajectory_plot_{plotter.location_name}_{input_path.stem}_smoothed_all.png"
            else:
                ids_str = "_".join(map(str, sorted(output_ids)[:5]))
                if len(output_ids) > 5:
                    ids_str += f"_plus{len(output_ids)-5}more"
                plot_output = f"trajectory_plot_{plotter.location_name}_{input_path.stem}_smoothed_IDs_{ids_str}.png"
        
        # 使用選定的軌跡進行繪圖
        trajectories = plotter.extract_trajectories()
        object_classes = plotter.get_object_classes()
        
        # 過濾出要輸出的軌跡
        output_trajectories = {tid: trajectories[tid] for tid in output_ids if tid in trajectories}
        
        if not output_trajectories:
            print("✗ 選中的輸出軌跡 ID 都不存在")
            return smoothed_file, None
        
        print(f"繪製 {len(output_trajectories)} 條選中的軌跡...")
        
        # 使用選定軌跡進行繪圖
        if plotter.plot_selected_trajectories(
            output_trajectories,
            object_classes,
            plot_output,
            zoom_to_fit=zoom_to_fit,
            title_prefix=title_prefix,
        ):
            print(f"✓ 軌跡繪圖完成: {plot_output}")
            return smoothed_file, plot_output
        else:
            print("✗ 軌跡繪圖失敗")
            return smoothed_file, None
            
    except Exception as e:
        print(f"✗ 軌跡繪圖過程發生錯誤: {e}")
        return smoothed_file, None


def select_trajectories_for_output_from_plotter(plotter, processed_ids):
    """
    從 plotter 實例中選擇要繪圖的軌跡（用於原始軌跡處理）
    
    Args:
        plotter: TrajectoryPlotterCLI 實例
        processed_ids: 已處理的軌跡 ID 列表（可選，用於標記）
    
    Returns:
        list: 選中要繪圖的軌跡 ID 列表，如果取消則返回 None
    """
    trajectories = plotter.extract_trajectories()
    object_classes = plotter.get_object_classes()
    
    if not trajectories:
        print("警告: 沒有軌跡數據")
        return None
    
    print(f"\n選擇要繪圖的軌跡 (共 {len(trajectories)} 條):")
    print("ID  | 類別           | 點數   | 顏色預覽")
    print("-" * 45)
    
    for tid in sorted(trajectories.keys()):
        obj_class = object_classes.get(tid, "unknown")
        points_count = len(trajectories[tid])
        color = plotter.get_color_for_id(tid)
        print(f"{tid:3d} | {obj_class:12s} | {points_count:6d} | {color}")
    
    print("\n選擇要繪圖的軌跡:")
    print("請輸入特定 ID")
    print("0. 取消")
    
    while True:
        try:
            available_ids = sorted(trajectories.keys())
            print(f"\n可用的 ID: {', '.join(map(str, available_ids))}")
            ids_input = input("請輸入要繪圖的軌跡 ID (用逗號分隔，或輸入 0 取消): ").strip()
            
            if ids_input == "0":
                return None
            
            if not ids_input:
                continue
            
            try:
                selected_ids = [int(x.strip()) for x in ids_input.split(',')]
                valid_ids = [tid for tid in selected_ids if tid in trajectories]
                
                if not valid_ids:
                    print("錯誤: 沒有有效的 ID")
                    continue
                
                invalid_ids = [tid for tid in selected_ids if tid not in trajectories]
                if invalid_ids:
                    print(f"警告: 以下 ID 不存在: {invalid_ids}")
                
                print(f"已選擇 {len(valid_ids)} 條軌跡用於繪圖: {valid_ids}")
                return valid_ids
                
            except ValueError:
                print("錯誤: 請輸入有效的數字")
                continue
                
        except KeyboardInterrupt:
            print("\n\n操作已取消")
            return None


def select_trajectories_for_output(smoothed_file, processed_ids=None):
    """
    從平滑後的 JSON 文件中選擇要輸出的軌跡
    
    Args:
        smoothed_file (str): 平滑後的 JSON 文件路徑
        processed_ids (list): 已處理的軌跡 ID 列表（可選，用於標記）
    
    Returns:
        list: 選中要輸出的軌跡 ID 列表，如果取消則返回 None
    """
    # 創建臨時 plotter 來讀取平滑後的數據
    temp_plotter = TrajectoryPlotterCLI()
    
    if not temp_plotter.load_trajectory_data(smoothed_file):
        print(f"錯誤: 無法載入平滑後的軌跡數據: {smoothed_file}")
        return None
    
    trajectories = temp_plotter.extract_trajectories()
    object_classes = temp_plotter.get_object_classes()
    
    if not trajectories:
        print("警告: 平滑後的文件中沒有軌跡數據")
        return None
    
    print(f"\n從平滑後的文件中選擇要輸出的軌跡 (共 {len(trajectories)} 條):")
    print("ID  | 類別           | 點數   | 狀態     | 顏色預覽")
    print("-" * 55)
    
    for tid in sorted(trajectories.keys()):
        obj_class = object_classes.get(tid, "unknown")
        points_count = len(trajectories[tid])
        color = temp_plotter.get_color_for_id(tid)
        
        # 標記軌跡是否被處理過
        if processed_ids and tid in processed_ids:
            status = "已處理"
        else:
            status = "原始"
        
        print(f"{tid:3d} | {obj_class:12s} | {points_count:6d} | {status:6s} | {color}")
    
    print("\n選擇要輸出的軌跡:")
    print("請輸入特定 ID")
    print("0. 取消")
    
    while True:
        try:
            available_ids = sorted(trajectories.keys())
            print(f"\n可用的 ID: {', '.join(map(str, available_ids))}")
            ids_input = input("請輸入要輸出的軌跡 ID (用逗號分隔，或輸入 0 取消): ").strip()
            
            if ids_input == "0":
                return None
            
            if not ids_input:
                continue
            
            try:
                selected_ids = [int(x.strip()) for x in ids_input.split(',')]
                valid_ids = [tid for tid in selected_ids if tid in trajectories]
                
                if not valid_ids:
                    print("錯誤: 沒有有效的 ID")
                    continue
                
                invalid_ids = [tid for tid in selected_ids if tid not in trajectories]
                if invalid_ids:
                    print(f"警告: 以下 ID 不存在: {invalid_ids}")
                
                print(f"已選擇 {len(valid_ids)} 條軌跡用於輸出: {valid_ids}")
                return valid_ids
                
            except ValueError:
                print("錯誤: 請輸入有效的數字")
                continue
                
        except KeyboardInterrupt:
            print("\n\n操作已取消")
            return None


def select_trajectories_for_processing(plotter):
    """
    選擇要處理的軌跡
    
    Args:
        plotter: TrajectoryPlotterCLI 實例
    
    Returns:
        list: 選中的軌跡 ID 列表，如果取消則返回 None
    """
    trajectories = plotter.extract_trajectories()
    object_classes = plotter.get_object_classes()
    
    if not trajectories:
        print("警告: 沒有找到軌跡數據")
        return None
    
    print(f"\n找到 {len(trajectories)} 條軌跡:")
    print("ID  | 類別           | 點數   | 顏色預覽")
    print("-" * 45)
    
    for tid in sorted(trajectories.keys()):
        obj_class = object_classes.get(tid, "unknown")
        points_count = len(trajectories[tid])
        color = plotter.get_color_for_id(tid)
        print(f"{tid:3d} | {obj_class:12s} | {points_count:6d} | {color}")
    
    print("\n選擇要處理的軌跡:")
    print("請輸入特定 ID")
    print("0. 取消")
    
    while True:
        try:
            available_ids = sorted(trajectories.keys())
            print(f"\n可用的 ID: {', '.join(map(str, available_ids))}")
            ids_input = input("請輸入要處理的軌跡 ID (用逗號分隔，或輸入 0 取消): ").strip()
            
            if ids_input == "0":
                return None
            
            if not ids_input:
                continue
            
            try:
                selected_ids = [int(x.strip()) for x in ids_input.split(',')]
                valid_ids = [tid for tid in selected_ids if tid in trajectories]
                
                if not valid_ids:
                    print("錯誤: 沒有有效的 ID")
                    continue
                
                invalid_ids = [tid for tid in selected_ids if tid not in trajectories]
                if invalid_ids:
                    print(f"警告: 以下 ID 不存在: {invalid_ids}")
                
                print(f"已選擇 {len(valid_ids)} 條軌跡: {valid_ids}")
                return valid_ids
                
            except ValueError:
                print("錯誤: 請輸入有效的數字")
                continue
                
        except KeyboardInterrupt:
            print("\n\n操作已取消")
            return None


def process_original_and_plot(input_file, plot_output=None, output_ids=None, zoom_to_fit=False,
                              title_prefix="Selected Object Trajectories"):
    """
    直接對原始文件進行軌跡繪圖（不進行平滑處理）
    
    Args:
        input_file (str): 輸入的 JSON 文件路徑
        plot_output (str): 圖表輸出文件名（可選）
        output_ids (list): 預選的要輸出的軌跡 ID 列表（可選）
    
    Returns:
        str: 圖表文件路徑
    """
    
    print("=" * 50)
    print("執行原始軌跡繪圖")
    print("=" * 50)
    
    try:
        plotter = TrajectoryPlotterCLI()
        
        # 載入軌跡數據
        if not plotter.load_trajectory_data(input_file):
            print("✗ 無法載入軌跡數據")
            return None
        
        # 載入衛星圖像
        if not plotter.load_satellite_image():
            print("✗ 無法載入衛星圖像")
            return None
        
        # 如果沒有預選的要輸出的軌跡 ID，則讓用戶選擇
        if output_ids is None:
            print("選擇要繪圖的軌跡")
            output_ids = select_trajectories_for_output_from_plotter(plotter, None)
            
        if not output_ids:
            print("沒有選擇軌跡進行繪圖")
            return None
        
        print(f"將繪圖 {len(output_ids)} 條軌跡: {output_ids}")
        
        # 生成輸出文件名
        if plot_output is None:
            input_path = Path(input_file)
            if len(output_ids) == len(plotter.extract_trajectories()):
                plot_output = f"trajectory_plot_{plotter.location_name}_{input_path.stem}_all.png"
            else:
                ids_str = "_".join(map(str, sorted(output_ids)[:5]))
                if len(output_ids) > 5:
                    ids_str += f"_plus{len(output_ids)-5}more"
                plot_output = f"trajectory_plot_{plotter.location_name}_{input_path.stem}_IDs_{ids_str}.png"
        
        # 使用選定的軌跡進行繪圖
        trajectories = plotter.extract_trajectories()
        object_classes = plotter.get_object_classes()
        
        # 過濾出要輸出的軌跡
        output_trajectories = {tid: trajectories[tid] for tid in output_ids if tid in trajectories}
        
        if not output_trajectories:
            print("✗ 選中的軌跡 ID 都不存在")
            return None
        
        print(f"繪製 {len(output_trajectories)} 條選中的軌跡...")
        
        # 使用選定軌跡進行繪圖
        if plotter.plot_selected_trajectories(
            output_trajectories,
            object_classes,
            plot_output,
            zoom_to_fit=zoom_to_fit,
            title_prefix=title_prefix,
        ):
            print(f"✓ 軌跡繪圖完成: {plot_output}")
            return plot_output
        else:
            print("✗ 軌跡繪圖失敗")
            return None
            
    except Exception as e:
        print(f"✗ 軌跡繪圖過程發生錯誤: {e}")
        return None


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='軌跡處理主控制器')
    parser.add_argument('input_file', help='輸入的 JSON 軌跡文件')
    parser.add_argument('--mode', choices=['smooth', 'original', 'both', 'test'], default='both',
                       help='處理模式: smooth(僅平滑+繪圖), original(僅原始繪圖), both(兩者都做), test(原始軌跡等比放大輸出)')
    parser.add_argument('--window-length', type=int, default=45,
                       help='平滑窗口長度（必須為奇數，默認45）')
    parser.add_argument('--polyorder', type=int, default=3,
                       help='多項式階數（默認3）')
    parser.add_argument('--output-dir', help='輸出目錄（可選）')
    
    args = parser.parse_args()
    
    # 檢查輸入文件是否存在
    if not os.path.exists(args.input_file):
        print(f"錯誤: 輸入文件不存在: {args.input_file}")
        sys.exit(1)
    
    # 檢查窗口長度是否為奇數
    if args.window_length % 2 == 0:
        print(f"錯誤: 窗口長度必須為奇數，當前值: {args.window_length}")
        sys.exit(1)
    
    print("TrafficLab 軌跡處理主控制器")
    print("=" * 50)
    print(f"輸入文件: {args.input_file}")
    print(f"處理模式: {args.mode}")
    
    # 如果是 both 模式，需要先選擇軌跡，然後兩個步驟都使用相同的選擇
    processing_ids = None
    output_ids = None
    
    if args.mode == 'both':
        print("\n由於選擇了 'both' 模式，請先統一選擇要處理的軌跡:")
        
        # 創建臨時 plotter 來選擇軌跡
        temp_plotter = TrajectoryPlotterCLI()
        if temp_plotter.load_trajectory_data(args.input_file):
            print("步驟 1: 選擇要處理的軌跡（原始和平滑處理將使用相同的軌跡選擇）")
            processing_ids = select_trajectories_for_processing(temp_plotter)
            if not processing_ids:
                print("沒有選擇軌跡，程序退出")
                sys.exit(0)
            
            # 先執行平滑處理以生成平滑後的文件
            print("\n執行平滑處理以生成平滑後的文件...")
            input_path = Path(args.input_file)
            smoothed_file = f"{input_path.stem}_smoothed.json"
            
            try:
                improve.smooth_trajectories(args.input_file, smoothed_file, args.window_length, args.polyorder)
                print(f"✓ 平滑處理完成: {smoothed_file}")
            except Exception as e:
                print(f"✗ 平滑處理失敗: {e}")
                sys.exit(1)
            
            print("\n步驟 2: 從平滑後的文件中選擇要輸出的軌跡（原始和平滑處理將使用相同的輸出選擇）")
            output_ids = select_trajectories_for_output(smoothed_file, processing_ids)
            if not output_ids:
                print("沒有選擇輸出軌跡，程序退出")
                sys.exit(0)
        else:
            print("無法載入軌跡數據")
            sys.exit(1)
    
    results = []
    
    if args.mode in ['original', 'both', 'test']:
        print("\n開始處理原始軌跡...")
        test_plot_output = None
        if args.mode == 'test':
            input_path = Path(args.input_file)
            if output_ids:
                ids_str = "_".join(map(str, sorted(output_ids)[:5]))
                if len(output_ids) > 5:
                    ids_str += f"_plus{len(output_ids)-5}more"
                test_plot_output = f"trajectory_plot_test_{input_path.stem}_IDs_{ids_str}.png"
            else:
                test_plot_output = f"trajectory_plot_test_{input_path.stem}.png"

        original_plot = process_original_and_plot(
            args.input_file,
            plot_output=test_plot_output,
            output_ids=output_ids,
            zoom_to_fit=(args.mode == 'test'),
            title_prefix='Zoomed Test Trajectories' if args.mode == 'test' else 'Selected Object Trajectories',
        )
        if original_plot:
            if args.mode == 'test':
                results.append(f"測試放大軌跡圖: {original_plot}")
            else:
                results.append(f"原始軌跡圖: {original_plot}")
    
    if args.mode in ['smooth', 'both']:
        if args.mode == 'both':
            # Both 模式下，平滑處理已經在選擇階段完成了
            print("\n開始處理平滑軌跡繪圖...")
            input_path = Path(args.input_file)
            smoothed_file = f"{input_path.stem}_smoothed.json"
            
            # 直接進行繪圖
            try:
                plotter = TrajectoryPlotterCLI()
                
                # 載入平滑後的軌跡數據
                if not plotter.load_trajectory_data(smoothed_file):
                    print("✗ 無法載入軌跡數據")
                else:
                    # 載入衛星圖像
                    if not plotter.load_satellite_image():
                        print("✗ 無法載入衛星圖像")
                    else:
                        # 生成輸出文件名
                        if len(output_ids) == len(plotter.extract_trajectories()):
                            plot_output = f"trajectory_plot_{plotter.location_name}_{input_path.stem}_smoothed_all.png"
                        else:
                            ids_str = "_".join(map(str, sorted(output_ids)[:5]))
                            if len(output_ids) > 5:
                                ids_str += f"_plus{len(output_ids)-5}more"
                            plot_output = f"trajectory_plot_{plotter.location_name}_{input_path.stem}_smoothed_IDs_{ids_str}.png"
                        
                        # 使用選定的軌跡進行繪圖
                        trajectories = plotter.extract_trajectories()
                        object_classes = plotter.get_object_classes()
                        
                        # 過濾出要輸出的軌跡
                        output_trajectories = {tid: trajectories[tid] for tid in output_ids if tid in trajectories}
                        
                        if output_trajectories:
                            print(f"繪製 {len(output_trajectories)} 條選中的軌跡...")
                            
                            # 使用選定軌跡進行繪圖
                            if plotter.plot_selected_trajectories(output_trajectories, object_classes, plot_output):
                                print(f"✓ 軌跡繪圖完成: {plot_output}")
                                results.append(f"平滑軌跡文件: {smoothed_file}")
                                results.append(f"平滑軌跡圖: {plot_output}")
                            else:
                                print("✗ 軌跡繪圖失敗")
                        else:
                            print("✗ 選中的輸出軌跡 ID 都不存在")
                            
            except Exception as e:
                print(f"✗ 軌跡繪圖過程發生錯誤: {e}")
        else:
            # 單獨的 smooth 模式
            print("\n開始處理平滑軌跡...")
            smoothed_file, smoothed_plot = smooth_and_plot(
                args.input_file, 
                args.window_length, 
                args.polyorder,
                selected_ids=processing_ids,
                output_ids=output_ids
            )
            if smoothed_file:
                results.append(f"平滑軌跡文件: {smoothed_file}")
            if smoothed_plot:
                results.append(f"平滑軌跡圖: {smoothed_plot}")
    
    # 顯示結果摘要
    print("\n" + "=" * 50)
    print("處理完成摘要")
    print("=" * 50)
    
    if results:
        print("成功生成的文件:")
        for result in results:
            print(f"  ✓ {result}")
    else:
        print("✗ 沒有成功生成任何文件")
        sys.exit(1)


if __name__ == "__main__":
    main()
