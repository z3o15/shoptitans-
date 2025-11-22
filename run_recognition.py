#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏装备图像识别 - 主运行程序
每次运行时保留一个主文件，便于重复使用
"""

import os
import sys
import shutil
import glob
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from equipment_recognizer import EnhancedEquipmentRecognizer
from screenshot_cutter import ScreenshotCutter
from config_manager import get_config_manager, create_recognizer_from_config

def clear_previous_results():
    """清理之前的结果，保留主文件"""
    print("清理之前的结果...")
    
    # 清理切割后的装备
    cropped_dir = "images/cropped_equipment"
    if os.path.exists(cropped_dir):
        for filename in os.listdir(cropped_dir):
            file_path = os.path.join(cropped_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"删除文件 {file_path} 时出错: {e}")
        print(f"✓ 已清理 {cropped_dir} 目录")
    
    # 清理日志目录（保留最近的一个日志文件）
    logs_dir = "recognition_logs"
    if os.path.exists(logs_dir):
        log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
        if len(log_files) > 1:
            # 按修改时间排序，保留最新的
            log_files.sort(key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)), reverse=True)
            for log_file in log_files[1:]:
                try:
                    os.remove(os.path.join(logs_dir, log_file))
                except Exception as e:
                    print(f"删除日志文件 {log_file} 时出错: {e}")
            print(f"✓ 已清理旧日志文件，保留最新的: {log_files[0]}")

def log_recognition_results(base_img_path, screenshot_path, matched_items, start_time, end_time, algorithm_used="unknown"):
    """记录识别结果到日志文件"""
    log_dir = "recognition_logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"recognition_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("游戏装备图像识别结果\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"基准装备: {base_img_path}\n")
        f.write(f"游戏截图: {screenshot_path}\n")
        f.write(f"使用算法: {algorithm_used}\n")
        processing_time_seconds = (end_time - start_time).total_seconds()
        f.write(f"处理耗时: {processing_time_seconds:.2f} 秒\n\n")
        
        f.write(f"匹配结果 (共 {len(matched_items)} 个):\n")
        f.write("-" * 40 + "\n")
        
        if matched_items:
            for i, (filename, similarity) in enumerate(matched_items, 1):
                f.write(f"{i}. {filename} - 相似度: {similarity}%\n")
        else:
            f.write("未找到匹配的装备\n")
        
        f.write("\n" + "=" * 60 + "\n")
    
    print(f"✓ 结果已记录到: {log_file}")
    return log_file

def main():
    """主程序入口"""
    print("=" * 60)
    print("游戏装备图像识别系统")
    print("=" * 60)
    
    # 初始化配置管理器
    config_manager = get_config_manager()
    config_manager.print_config_summary()
    
    # 清理之前的结果
    clear_previous_results()
    
    # 从配置获取路径
    paths_config = config_manager.get_paths_config()
    IMAGES_DIR = paths_config.get("images_dir", "images")
    BASE_EQUIPMENT_DIR = paths_config.get("base_equipment_dir", "base_equipment")
    GAME_SCREENSHOTS_DIR = paths_config.get("game_screenshots_dir", "game_screenshots")
    CROPPED_EQUIPMENT_DIR = paths_config.get("cropped_equipment_dir", "cropped_equipment")
    CROPPED_FOLDER = os.path.join(IMAGES_DIR, CROPPED_EQUIPMENT_DIR)
    
    # 创建必要目录
    os.makedirs(CROPPED_FOLDER, exist_ok=True)
    
    # 自动检测基准装备图
    base_equipment_dir = os.path.join(IMAGES_DIR, BASE_EQUIPMENT_DIR)
    if not os.path.exists(base_equipment_dir):
        print(f"❌ 错误: 找不到基准装备目录 {base_equipment_dir}")
        print("请创建 images/base_equipment/ 目录并放入基准装备图")
        return
    
    # 查找基准装备图（支持多种格式）
    base_equipment_files = []
    for ext in ['*.webp', '*.png', '*.jpg', '*.jpeg']:
        base_equipment_files.extend(glob.glob(os.path.join(base_equipment_dir, ext)))
    
    if not base_equipment_files:
        print(f"❌ 错误: 在 {base_equipment_dir} 中找不到基准装备图")
        print("请将基准装备图放入 images/base_equipment/ 目录")
        print("支持的格式: .webp, .png, .jpg, .jpeg")
        return
    
    # 使用第一个找到的基准装备图
    BASE_EQUIPMENT_PATH = base_equipment_files[0]
    
    # 自动检测游戏截图
    game_screenshots_dir = os.path.join(IMAGES_DIR, GAME_SCREENSHOTS_DIR)
    if not os.path.exists(game_screenshots_dir):
        print(f"❌ 错误: 找不到游戏截图目录 {game_screenshots_dir}")
        print("请创建 images/game_screenshots/ 目录并放入游戏截图")
        return
    
    # 查找游戏截图（支持多种格式）
    screenshot_files = []
    for ext in ['*.webp', '*.png', '*.jpg', '*.jpeg']:
        screenshot_files.extend(glob.glob(os.path.join(game_screenshots_dir, ext)))
    
    if not screenshot_files:
        print(f"❌ 错误: 在 {game_screenshots_dir} 中找不到游戏截图")
        print("请将游戏截图放入 images/game_screenshots/ 目录")
        print("支持的格式: .webp, .png, .jpg, .jpeg")
        return
    
    # 使用第一个找到的游戏截图
    SCREENSHOT_PATH = screenshot_files[0]
    
    print(f"✓ 基准装备: {BASE_EQUIPMENT_PATH}")
    print(f"✓ 游戏截图: {SCREENSHOT_PATH}")
    print(f"✓ 输出目录: {CROPPED_FOLDER}")
    
    # 如果有多个文件，显示所有可用文件
    if len(base_equipment_files) > 1:
        print(f"\n可用的基准装备图:")
        for i, file in enumerate(base_equipment_files, 1):
            print(f"  {i}. {os.path.basename(file)}")
    
    if len(screenshot_files) > 1:
        print(f"\n可用的游戏截图:")
        for i, file in enumerate(screenshot_files, 1):
            print(f"  {i}. {os.path.basename(file)}")
    
    # 初始化工具
    recognizer = create_recognizer_from_config(config_manager)
    cutter = ScreenshotCutter()
    
    start_time = datetime.now()
    
    try:
        # 步骤1：轮廓检测切割游戏截图
        print(f"\n{'='*50}")
        print("步骤1: 轮廓检测切割游戏截图")
        print(f"{'='*50}")
        print("使用轮廓检测自动识别和切割装备...")
        
        success = cutter.cut_fixed(
            screenshot_path=SCREENSHOT_PATH,
            output_folder=CROPPED_FOLDER,
            grid=(5, 2),        # 5列2行的装备网格
            item_width=210,      # 装备宽度
            item_height=160,     # 装备高度
            margin_left=10,      # 左侧边距
            margin_top=270,      # 顶部边距
            h_spacing=15,        # 装备横向间隔
            v_spacing=20         # 装备纵向间隔
        )
        
        if not success:
            print("❌ 截图切割失败")
            return
        
        # 步骤2：批量对比装备
        print(f"\n{'='*50}")
        print("步骤2: 批量对比装备")
        print(f"{'='*50}")
        
        # 遍历所有切割后的装备图像
        matched_items = []
        threshold = 80
        
        print(f"使用算法: {'高级模板匹配' if recognizer.use_advanced_algorithm else '传统dHash'}")
        
        for filename in sorted(os.listdir(CROPPED_FOLDER)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                item_path = os.path.join(CROPPED_FOLDER, filename)
                
                # 使用增强版识别器的compare_images方法
                similarity, is_match = recognizer.compare_images(BASE_EQUIPMENT_PATH, item_path, threshold)
                
                if is_match:
                    matched_items.append((filename, similarity))
                    print(f"【匹配成功】{filename} - 相似度：{similarity}%")
                else:
                    print(f"【未匹配】{filename} - 相似度：{similarity}%")
        
        # 步骤3：输出结果
        end_time = datetime.now()
        
        print(f"\n{'='*50}")
        print("识别结果汇总")
        print(f"{'='*50}")
        
        if matched_items:
            print(f"✅ 成功识别到 {len(matched_items)} 个匹配的装备:")
            for i, (filename, similarity) in enumerate(matched_items, 1):
                print(f"  {i}. {filename} - 相似度: {similarity}%")
        else:
            print("❌ 未识别到匹配的装备")
        
        print(f"\n处理耗时: {(end_time - start_time).total_seconds():.2f} 秒")
        
        # 记录结果到日志文件
        algorithm_used = "高级模板匹配" if recognizer.use_advanced_algorithm else "传统dHash"
        log_file = log_recognition_results(
            BASE_EQUIPMENT_PATH,
            SCREENSHOT_PATH,
            matched_items,
            start_time,
            end_time,
            algorithm_used
        )
        
        print(f"\n📁 切割结果保存在: {CROPPED_FOLDER}")
        print(f"📝 详细日志保存在: {log_file}")
        
    except Exception as e:
        print(f"❌ 处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()