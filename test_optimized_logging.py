#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的日志系统
验证终端只显示关键日志和错误信息，详细调试信息写入对应步骤的日志文件
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_logging_system():
    """测试优化后的日志系统"""
    print("=" * 60)
    print("测试优化后的日志系统")
    print("=" * 60)
    
    try:
        from src.unified_logger import get_unified_logger
        
        # 初始化统一日志管理器
        logger = get_unified_logger()
        
        # 配置输出策略
        logger.configure_output(
            console_level="WARNING",  # 只显示WARNING及以上级别
            show_step_progress=True,
            show_warnings=True,
            show_errors=True,
            show_success_summary=False,  # 不显示成功摘要
            show_performance_metrics=False
        )
        
        print("\n1. 测试步骤开始和结束...")
        logger.start_step("step1_helper", "测试辅助工具功能")
        
        print("\n2. 测试不同级别的日志输出...")
        # 这些信息应该只写入日志文件，不在终端显示
        logger.log_info("这是一条信息日志，应该只在文件中显示")
        logger.log_success("这是一条成功日志，应该只在文件中显示")
        
        # 这些警告和错误应该在终端显示
        logger.log_warning("这是一条警告日志，应该在终端显示")
        logger.log_error("这是一条错误日志，应该在终端显示")
        
        print("\n3. 测试文件处理日志...")
        # 模拟文件处理
        test_files = ["test1.png", "test2.jpg", "test3.png"]
        for i, file in enumerate(test_files):
            success = i % 2 == 0  # 模拟成功和失败
            logger.log_file_processed(file, success, "测试文件处理")
            
            # 添加一些详细信息，这些应该只在日志文件中
            logger.log_info(f"处理文件 {file} 的详细信息: 分辨率=100x100, 大小=1.2MB")
        
        print("\n4. 测试进度日志...")
        # 测试进度日志
        for i in range(0, 101, 25):
            logger.log_progress(i, 100, f"处理进度 {i}%")
            time.sleep(0.1)  # 短暂延迟以便观察
        
        print("\n5. 测试性能指标...")
        # 测试性能指标，这些应该只在日志文件中
        logger.log_performance_metric("处理速度", "15.3 图片/秒")
        logger.log_performance_metric("内存使用", "256MB")
        
        # 结束步骤
        logger.end_step("step1_helper", "完成")
        
        print("\n6. 检查生成的日志文件...")
        step_dir = logger.get_step_dir("step1_helper")
        if step_dir:
            log_file = step_dir / "log.txt"
            if log_file.exists():
                print(f"✓ 日志文件已创建: {log_file}")
                
                # 读取并显示日志文件内容
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    print("\n日志文件内容:")
                    print("-" * 40)
                    print(log_content)
                    print("-" * 40)
            else:
                print(f"✗ 日志文件未创建: {log_file}")
        
        print("\n7. 检查目录结构...")
        expected_dirs = [
            "step_tests/step1_helper",
            "step_tests/step2_cut",
            "step_tests/step3_match",
            "step_tests/step5_ocr"
        ]
        
        for dir_path in expected_dirs:
            if os.path.exists(dir_path):
                print(f"✓ 目录存在: {dir_path}")
                
                # 检查子目录
                subdirs = ["images", "txt", "temp_files"]
                for subdir in subdirs:
                    subdir_path = os.path.join(dir_path, subdir)
                    if os.path.exists(subdir_path):
                        print(f"  ✓ 子目录存在: {subdir}")
            else:
                print(f"✗ 目录不存在: {dir_path}")
        
        # 生成汇总报告
        print("\n8. 生成汇总报告...")
        summary_file = logger.generate_summary_report({
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_results": "日志系统优化测试完成"
        })
        
        if summary_file and os.path.exists(summary_file):
            print(f"✓ 汇总报告已生成: {summary_file}")
        
        # 关闭所有日志
        logger.close_all_logs()
        
        print("\n" + "=" * 60)
        print("日志系统测试完成！")
        print("请检查:")
        print("1. 终端输出是否只显示关键信息（警告、错误、步骤进度）")
        print("2. 日志文件是否包含所有详细信息")
        print("3. 目录结构是否正确创建")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"✗ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_logging_system()