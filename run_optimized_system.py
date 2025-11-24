#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化后的系统运行脚本
演示优化后的终端输出效果，只显示关键信息
"""

import os
import sys
import time
from datetime import datetime

# 导入统一日志管理器
try:
    from src.unified_logger import get_unified_logger, init_unified_logger_from_config
    from src.config_manager import get_config_manager
    UNIFIED_LOGGER_AVAILABLE = True
except ImportError:
    try:
        from unified_logger import get_unified_logger, init_unified_logger_from_config
        from config_manager import get_config_manager
        UNIFIED_LOGGER_AVAILABLE = True
    except ImportError:
        UNIFIED_LOGGER_AVAILABLE = False
        print("⚠️ 统一日志管理器不可用，使用默认输出")

def step1_get_screenshots():
    """步骤1：获取原始图片"""
    if UNIFIED_LOGGER_AVAILABLE:
        logger = get_unified_logger()
        logger.start_step("step1_helper", "获取原始图片")
    
    # 检查游戏截图目录
    game_screenshots_dir = "images/game_screenshots"
    
    if not os.path.exists(game_screenshots_dir):
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_error(f"游戏截图目录不存在: {game_screenshots_dir}")
            logger.end_step("step1_helper", "失败")
        else:
            print(f"❌ 游戏截图目录不存在: {game_screenshots_dir}")
        return False
    
    # 列出所有截图
    screenshot_files = []
    for filename in os.listdir(game_screenshots_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            screenshot_files.append(filename)
    
    if not screenshot_files:
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_error(f"游戏截图目录为空: {game_screenshots_dir}")
            logger.end_step("step1_helper", "失败")
        else:
            print(f"❌ 游戏截图目录为空: {game_screenshots_dir}")
        return False
    
    if UNIFIED_LOGGER_AVAILABLE:
        logger.log_success(f"找到 {len(screenshot_files)} 个游戏截图")
        logger.end_step("step1_helper", "完成")
    else:
        print(f"✓ 找到 {len(screenshot_files)} 个游戏截图")
    
    return True

def step2_cut_screenshots():
    """步骤2：分割原始图片"""
    if UNIFIED_LOGGER_AVAILABLE:
        logger = get_unified_logger()
        logger.start_step("step2_cut", "分割原始图片")
    
    # 检查游戏截图
    game_screenshots_dir = "images/game_screenshots"
    screenshot_files = []
    for filename in os.listdir(game_screenshots_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            screenshot_files.append(filename)
    
    if not screenshot_files:
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_error("未找到游戏截图，请先完成步骤1")
            logger.end_step("step2_cut", "失败")
        else:
            print("❌ 未找到游戏截图，请先完成步骤1")
        return False
    
    # 确保输出目录存在
    output_dir = "images/cropped_equipment"
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建时间戳子目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamp_dir = os.path.join(output_dir, timestamp)
    os.makedirs(timestamp_dir, exist_ok=True)
    
    # 模拟截图切割过程
    total_screenshots = len(screenshot_files)
    total_equipment = 0
    
    for i, screenshot in enumerate(screenshot_files, 1):
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_progress(i, total_screenshots, f"处理截图: {screenshot}")
        else:
            print(f"处理截图 {i}/{total_screenshots}: {screenshot}")
        
        # 模拟切割出12个装备图片
        for j in range(12):
            # 创建模拟的装备图片文件（空文件作为占位符）
            equipment_filename = f"{screenshot}_equipment_{j+1}.png"
            equipment_path = os.path.join(timestamp_dir, equipment_filename)
            with open(equipment_path, 'w') as f:
                f.write("")  # 创建空文件作为占位符
            total_equipment += 1
        
        # 模拟处理时间
        time.sleep(0.5)
    
    if UNIFIED_LOGGER_AVAILABLE:
        logger.log_success(f"共切割出 {total_equipment} 个装备图片")
        logger.end_step("step2_cut", "完成")
    else:
        print(f"✓ 共切割出 {total_equipment} 个装备图片")
    
    return True

def step3_match_equipment():
    """步骤3：装备识别匹配"""
    if UNIFIED_LOGGER_AVAILABLE:
        logger = get_unified_logger()
        logger.start_step("step3_match", "装备识别匹配")
    
    # 检查基准装备
    base_equipment_dir = "images/base_equipment"
    base_image_files = []
    for filename in os.listdir(base_equipment_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            base_image_files.append(filename)
    
    if not base_image_files:
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_error("未找到基准装备图片")
            logger.end_step("step3_match", "失败")
        else:
            print("❌ 未找到基准装备图片")
        return False
    
    # 检查切割装备
    cropped_equipment_dir = "images/cropped_equipment"
    cropped_files = []
    
    # 检查是否有时间命名的子目录
    subdirs = []
    for item in os.listdir(cropped_equipment_dir):
        item_path = os.path.join(cropped_equipment_dir, item)
        if os.path.isdir(item_path) and item.replace('_', '').replace(':', '').isdigit():
            subdirs.append(item)
    
    if subdirs:
        # 如果有时间命名的子目录，使用最新的一个
        latest_dir = sorted(subdirs)[-1]
        latest_dir_path = os.path.join(cropped_equipment_dir, latest_dir)
        for filename in os.listdir(latest_dir_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                cropped_files.append(os.path.join(latest_dir, filename))
        cropped_equipment_dir = latest_dir_path
    else:
        # 如果没有时间命名的子目录，直接在主目录中查找
        for filename in os.listdir(cropped_equipment_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                cropped_files.append(filename)
    
    if not cropped_files:
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_error("未找到切割装备图片，请先完成步骤2")
            logger.end_step("step3_match", "失败")
        else:
            print("❌ 未找到切割装备图片，请先完成步骤2")
        return False
    
    # 模拟装备匹配过程
    total_files = len(cropped_files)
    matched_count = 0
    
    for i, filename in enumerate(cropped_files, 1):
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_progress(i, total_files, f"匹配装备")
        else:
            print(f"匹配装备 {i}/{total_files}")
        
        # 模拟匹配结果（假设30%的匹配率）
        import random
        is_match = random.random() < 0.3
        
        if is_match:
            matched_count += 1
            if UNIFIED_LOGGER_AVAILABLE:
                logger.log_success(f"匹配成功: {os.path.basename(filename)}", show_in_console=True)
            else:
                print(f"✓ 匹配成功: {os.path.basename(filename)}")
        
        # 模拟处理时间
        time.sleep(0.1)
    
    if UNIFIED_LOGGER_AVAILABLE:
        logger.log_success(f"在 {total_files} 个装备中找到 {matched_count} 个匹配项")
        logger.end_step("step3_match", "完成")
    else:
        print(f"✓ 在 {total_files} 个装备中找到 {matched_count} 个匹配项")
    
    return True

def step4_integrate_results():
    """步骤4：整合装备名称和金额识别结果"""
    if UNIFIED_LOGGER_AVAILABLE:
        logger = get_unified_logger()
        logger.start_step("step5_ocr", "整合装备名称和金额识别结果")
    
    # 模拟整合过程
    time.sleep(1)
    
    if UNIFIED_LOGGER_AVAILABLE:
        logger.log_success("成功整合装备名称和金额识别结果")
        logger.end_step("step5_ocr", "完成")
    else:
        print("✓ 成功整合装备名称和金额识别结果")
    
    return True

def main():
    """主函数"""
    global UNIFIED_LOGGER_AVAILABLE
    print("=" * 60)
    print("优化后的游戏装备图像识别系统")
    print("=" * 60)
    print("本演示展示优化后的终端输出效果")
    print("只显示关键信息，详细信息保存在日志文件中")
    print("=" * 60)
    
    # 初始化统一日志管理器
    if UNIFIED_LOGGER_AVAILABLE:
        try:
            config_manager = get_config_manager()
            logger_config = {
                "base_output_dir": "output",
                "console_mode": True,
                "output": {
                    "show_step_progress": True,
                    "show_item_details": False,
                    "show_warnings": True,
                    "show_errors": True,
                    "show_success_summary": True,
                    "show_performance_metrics": False,
                    "console_level": "INFO"
                }
            }
            init_unified_logger_from_config(logger_config)
            logger = get_unified_logger()
            # 使用预定义的步骤ID，避免"未知的步骤ID"错误
            logger.start_step("step1_helper", "装备识别系统")
        except Exception as e:
            print(f"⚠️ 初始化日志系统失败: {e}")
            UNIFIED_LOGGER_AVAILABLE = False
    
    start_time = time.time()
    
    # 执行四个核心步骤
    steps = [
        ("步骤1：获取原始图片", step1_get_screenshots),
        ("步骤2：分割原始图片", step2_cut_screenshots),
        ("步骤3：装备识别匹配", step3_match_equipment),
        ("步骤4：整合装备名称和金额识别结果", step4_integrate_results)
    ]
    
    for step_name, step_func in steps:
        print(f"\n🚀 执行: {step_name}")
        success = step_func()
        if not success:
            if UNIFIED_LOGGER_AVAILABLE:
                logger.log_error(f"{step_name} 失败，终止流程")
                logger.end_step("step1_helper", "失败")
            else:
                print(f"❌ {step_name} 失败，终止流程")
            return False
        
        # 步骤间暂停
        time.sleep(0.5)
    
    # 生成汇总报告
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    if UNIFIED_LOGGER_AVAILABLE:
        logger.log_success(f"所有步骤执行完成！总耗时: {elapsed_time:.2f}秒")
        logger.end_step("step1_helper", "完成")
        
        # 生成汇总报告
        additional_info = {
            "total_time": f"{elapsed_time:.2f}秒",
            "steps_completed": len(steps),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        report_path = logger.generate_summary_report(additional_info)
        print(f"\n📊 详细报告已生成: {report_path}")
    else:
        print(f"\n✅ 所有步骤执行完成！总耗时: {elapsed_time:.2f}秒")
    
    print("\n" + "=" * 60)
    print("🎉 优化后的系统演示完成！")
    print("=" * 60)
    print("优化效果:")
    print("1. 终端只显示关键信息（步骤开始/结束、错误、成功摘要）")
    print("2. 详细信息保存在日志文件中")
    print("3. 进度显示更加简洁（只在关键节点显示）")
    print("4. 错误信息突出显示")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 程序被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)