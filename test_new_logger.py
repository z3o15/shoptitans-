#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的日志系统
验证步骤日志管理器和报告生成器的功能
"""

import time
import random
from pathlib import Path

# 导入新的日志系统
from src.unified_logger import get_unified_logger, init_unified_logger_from_config


def test_step_logger():
    """测试步骤日志管理器"""
    print("🧪 测试步骤日志管理器...")
    
    # 初始化日志系统
    config = {
        "base_output_dir": "output",
        "console_mode": True,
        "output": {
            "show_step_progress": True,
            "show_item_details": False,  # 不显示每个项目的详细信息
            "show_warnings": True,
            "show_errors": True,
            "show_success_summary": True,
            "show_performance_metrics": True
        }
    }
    
    logger = init_unified_logger_from_config(config)
    
    # 测试步骤1：辅助工具
    logger.start_step("step1_helper", "测试辅助工具功能")
    
    logger.log_info("开始初始化辅助工具", show_in_console=True)
    time.sleep(0.5)
    
    logger.log_warning("这是一个测试警告", show_in_console=True)
    
    # 模拟处理一些文件
    for i in range(3):
        file_path = f"test_file_{i+1}.txt"
        success = random.choice([True, True, True, False])  # 75%成功率
        details = f"大小: {random.randint(100, 1000)} bytes" if success else "文件损坏"
        logger.log_file_processed(file_path, success=success, details=details)
        time.sleep(0.2)
    
    logger.log_performance_metric("处理速度", "2.5 files/sec")
    logger.log_info("辅助工具处理完成", show_in_console=True)
    
    logger.end_step("step1_helper", "完成")
    
    # 测试步骤2：图片裁剪
    logger.start_step("step2_cut", "测试图片裁剪功能")
    
    logger.log_info("开始图片裁剪处理", show_in_console=True)
    
    # 模拟处理进度
    total_images = 10
    for i in range(total_images):
        time.sleep(0.1)
        logger.log_progress(i+1, total_images, f"处理图片 {i+1}")
        
        # 随机记录一些文件处理
        if i % 3 == 0:
            file_path = f"image_{i+1}.png"
            success = random.choice([True, True, False])  # 66%成功率
            logger.log_file_processed(file_path, success=success)
    
    logger.log_performance_metric("平均处理时间", "0.12 sec/image")
    logger.log_error("测试错误：图片格式不支持", show_in_console=True)
    
    logger.end_step("step2_cut", "完成")
    
    # 测试步骤3：装备匹配
    logger.start_step("step3_match", "测试装备匹配功能")
    
    logger.log_info("开始装备特征匹配", show_in_console=True)
    
    # 模拟匹配过程
    equipment_list = ["sword", "shield", "armor", "helmet", "boots"]
    for i, equipment in enumerate(equipment_list):
        time.sleep(0.3)
        success = random.choice([True, True, True, False])  # 75%成功率
        confidence = random.uniform(0.7, 0.95) if success else random.uniform(0.3, 0.6)
        details = f"置信度: {confidence:.2f}"
        logger.log_file_processed(f"{equipment}.png", success=success, details=details)
    
    logger.log_performance_metric("匹配准确率", "78.5%")
    logger.log_success("装备匹配完成", show_in_console=True)
    
    logger.end_step("step3_match", "完成")
    
    # 测试步骤5：OCR识别
    logger.start_step("step5_ocr", "测试OCR识别功能")
    
    logger.log_info("开始文字识别", show_in_console=True)
    
    # 模拟OCR处理
    text_items = ["100", "250", "500", "1000", "invalid_text"]
    for i, text in enumerate(text_items):
        time.sleep(0.2)
        is_valid = text.isdigit()
        logger.log_file_processed(f"amount_{i+1}.png", success=is_valid, 
                                 details=f"识别结果: {text}")
    
    logger.log_performance_metric("识别准确率", "80.0%")
    logger.log_warning("发现无法识别的文本", show_in_console=True)
    
    logger.end_step("step5_ocr", "完成")
    
    # 生成汇总报告
    additional_info = {
        "system_info": {
            "python_version": "3.8+",
            "platform": "Windows",
            "memory_usage": "256MB"
        },
        "recommendations": [
            "建议提高图片预处理质量以提高OCR准确率",
            "考虑增加更多的装备特征模板",
            "优化错误处理机制"
        ]
    }
    
    summary_report = logger.generate_summary_report(additional_info)
    print(f"\n📋 汇总报告已生成: {summary_report}")
    
    # 关闭所有日志
    logger.close_all_logs()
    
    print("✅ 步骤日志管理器测试完成")


def verify_directory_structure():
    """验证目录结构"""
    print("\n🔍 验证目录结构...")
    
    expected_dirs = [
        "output/step1_helper/temp_files",
        "output/step2_cut/images",
        "output/step2_cut/txt",
        "output/step3_match/images",
        "output/step3_match/txt",
        "output/step5_ocr/images",
        "output/step5_ocr/txt"
    ]
    
    expected_files = [
        "output/step1_helper/log.txt",
        "output/step1_helper/report.md",
        "output/step2_cut/log.txt",
        "output/step2_cut/report.md",
        "output/step3_match/log.txt",
        "output/step3_match/report.md",
        "output/step5_ocr/log.txt",
        "output/step5_ocr/report.md",
        "output/summary_report.md"
    ]
    
    # 检查目录
    for dir_path in expected_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"  ✅ 目录存在: {dir_path}")
        else:
            print(f"  ❌ 目录缺失: {dir_path}")
    
    # 检查文件
    for file_path in expected_files:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"  ✅ 文件存在: {file_path} ({size} bytes)")
        else:
            print(f"  ❌ 文件缺失: {file_path}")
    
    print("🔍 目录结构验证完成")


def show_log_samples():
    """显示日志示例"""
    print("\n📄 显示日志示例...")
    
    log_files = [
        "output/step1_helper/log.txt",
        "output/step2_cut/log.txt",
        "output/step3_match/log.txt",
        "output/step5_ocr/log.txt"
    ]
    
    for log_file in log_files:
        path = Path(log_file)
        if path.exists():
            print(f"\n--- {log_file} ---")
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # 显示前5行和后5行
                for line in lines[:5]:
                    print(line.rstrip())
                if len(lines) > 10:
                    print("  ... (省略中间内容) ...")
                for line in lines[-5:]:
                    print(line.rstrip())
    
    print("\n📄 日志示例显示完成")


if __name__ == "__main__":
    print("🚀 开始测试新的日志系统...")
    
    try:
        # 测试步骤日志管理器
        test_step_logger()
        
        # 验证目录结构
        verify_directory_structure()
        
        # 显示日志示例
        show_log_samples()
        
        print("\n🎉 所有测试完成！新的日志系统工作正常。")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()