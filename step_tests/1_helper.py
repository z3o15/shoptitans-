#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辅助功能测试模块
从 enhanced_recognition_start.py 提取的独立测试模块
包含各种辅助功能和测试
"""

import os
import sys
import subprocess
import tempfile
import shutil
from datetime import datetime
import time
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 添加项目根目录到Python路径，以便能够导入src模块
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入新的统一日志管理器
try:
    from src.unified_logger import get_unified_logger
    LOGGER_AVAILABLE = True
except ImportError:
    try:
        from unified_logger import get_unified_logger
        LOGGER_AVAILABLE = True
    except ImportError:
        LOGGER_AVAILABLE = False
        print("⚠️ 统一日志管理器不可用，使用默认输出")

def check_dependencies():
    """检查依赖是否已安装"""
    if LOGGER_AVAILABLE:
        logger = get_unified_logger()
        logger.start_step("step1_helper", "系统依赖检查")
    else:
        print("检查系统依赖...")
    
    required_packages = ['cv2', 'PIL', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            elif package == 'numpy':
                import numpy
            if LOGGER_AVAILABLE:
                logger.log_success(f"{package}")
            else:
                print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            if LOGGER_AVAILABLE:
                logger.log_error(f"{package}")
            else:
                print(f"✗ {package}")
    
    if missing_packages:
        if LOGGER_AVAILABLE:
            logger.log_info(f"缺少依赖包: {', '.join(missing_packages)}")
            logger.log_info("正在安装依赖...")
        else:
            print(f"\n缺少依赖包: {', '.join(missing_packages)}")
            print("正在安装依赖...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            if LOGGER_AVAILABLE:
                logger.log_success("依赖安装完成")
                logger.end_step("step1_helper", "完成")
            else:
                print("✓ 依赖安装完成")
            return True
        except subprocess.CalledProcessError:
            if LOGGER_AVAILABLE:
                logger.log_error("依赖安装失败，请手动运行: pip install -r requirements.txt")
                logger.end_step("step1_helper", "失败")
            else:
                print("✗ 依赖安装失败，请手动运行: pip install -r requirements.txt")
            return False
    else:
        if LOGGER_AVAILABLE:
            logger.log_success("所有依赖已安装")
            logger.end_step("step1_helper", "完成")
        else:
            print("✓ 所有依赖已安装")
        return True

def check_data_files():
    """检查数据文件是否存在 - 仅检查基础目录结构，不涉及其他步骤的输出"""
    if LOGGER_AVAILABLE:
        logger = get_step_logger()
        logger.start_step("step1_helper", "数据文件检查")
    else:
        print("\n检查数据文件...")
    
    # 检查基准装备图目录
    base_equipment_dir = "images/base_equipment"
    if not os.path.exists(base_equipment_dir):
        if LOGGER_AVAILABLE:
            logger.log_error(f"缺少基准装备图目录: {base_equipment_dir}")
        else:
            print(f"✗ 缺少基准装备图目录: {base_equipment_dir}")
        return False
    
    # 检查目录中的基准装备图文件
    base_image_files = []
    for filename in os.listdir(base_equipment_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            base_image_files.append(filename)
    
    if not base_image_files:
        if LOGGER_AVAILABLE:
            logger.log_error(f"基准装备图目录为空: {base_equipment_dir}")
        else:
            print(f"✗ 基准装备图目录为空: {base_equipment_dir}")
        return False
    else:
        if LOGGER_AVAILABLE:
            logger.log_info(f"找到 {len(base_image_files)} 个基准装备图文件")
            for filename in sorted(base_image_files):
                logger.log_info(f"  - {filename}")
        else:
            print(f"✓ 找到 {len(base_image_files)} 个基准装备图文件:")
            for filename in sorted(base_image_files):
                print(f"  - {filename}")
    
    # 检查游戏截图目录
    game_screenshots_dir = "images/game_screenshots"
    if not os.path.exists(game_screenshots_dir):
        if LOGGER_AVAILABLE:
            logger.log_error(f"缺少游戏截图目录: {game_screenshots_dir}")
        else:
            print(f"✗ 缺少游戏截图目录: {game_screenshots_dir}")
        return False
    
    # 检查目录中的游戏截图文件
    screenshot_files = []
    for filename in os.listdir(game_screenshots_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            screenshot_files.append(filename)
    
    if not screenshot_files:
        if LOGGER_AVAILABLE:
            logger.log_warning(f"游戏截图目录为空: {game_screenshots_dir}")
        else:
            print(f"⚠️ 游戏截图目录为空: {game_screenshots_dir}")
    else:
        if LOGGER_AVAILABLE:
            logger.log_info(f"找到 {len(screenshot_files)} 个游戏截图文件")
            for filename in sorted(screenshot_files):
                logger.log_info(f"  - {filename}")
        else:
            print(f"✓ 找到 {len(screenshot_files)} 个游戏截图文件:")
            for filename in sorted(screenshot_files):
                print(f"  - {filename}")
    
    # 注释掉切割装备目录检查，这属于步骤2的功能
    # 切割装备目录的检查应该由步骤2自己负责
    
    if LOGGER_AVAILABLE:
        logger.end_step("step1_helper", "完成")
    
    return True

def clear_previous_results():
    """清理之前的结果，保留主文件 - 仅清理日志文件，不涉及其他步骤的输出"""
    if LOGGER_AVAILABLE:
        logger = get_step_logger()
        logger.start_step("step1_helper", "清理日志文件")
    else:
        print("\n" + "=" * 60)
        print("清理日志文件")
        print("=" * 60)
        print("此操作将清理旧的日志文件")
        print("-" * 60)
    
    # 确认操作
    if LOGGER_AVAILABLE:
        logger.log_info("确认要清理以下内容吗？")
        logger.log_info("1. 旧的日志文件 (recognition_logs)")
        logger.log_info("注意：最新的日志文件将被保留")
    else:
        print("确认要清理以下内容吗？")
        print("1. 旧的日志文件 (recognition_logs)")
        print("注意：最新的日志文件将被保留")
    
    confirm = input("\n确认清理？(y/n): ").strip().lower()
    if confirm != 'y':
        if LOGGER_AVAILABLE:
            logger.log_info("已取消清理操作")
            logger.end_step("step1_helper", "已取消")
        else:
            print("已取消清理操作")
        return
    
    # 注释掉切割装备目录的清理，这属于步骤2的功能
    # 清理切割后的装备
    # cropped_dir = "images/cropped_equipment"
    # if os.path.exists(cropped_dir):
    #     try:
    #         for filename in os.listdir(cropped_dir):
    #             file_path = os.path.join(cropped_dir, filename)
    #             try:
    #                 if os.path.isfile(file_path):
    #                     os.unlink(file_path)
    #                 elif os.path.isdir(file_path):
    #                     shutil.rmtree(file_path)
    #             except Exception as e:
    #                 if LOGGER_AVAILABLE:
    #                     logger.log_error(f"删除文件 {file_path} 时出错: {e}")
    #                 else:
    #                     print(f"删除文件 {file_path} 时出错: {e}")
    #         if LOGGER_AVAILABLE:
    #             logger.log_success(f"已清理 {cropped_dir} 目录")
    #         else:
    #             print(f"✓ 已清理 {cropped_dir} 目录")
    #     except Exception as e:
    #         print(f"清理 {cropped_dir} 目录时出错: {e}")
    
    # 注释掉marker目录的清理，这属于步骤2的功能
    # 清理marker目录
    # marker_dir = "images/cropped_equipment_marker"
    # if os.path.exists(marker_dir):
    #     try:
    #         for filename in os.listdir(marker_dir):
    #             file_path = os.path.join(marker_dir, filename)
    #             try:
    #                 if os.path.isfile(file_path):
    #                     os.unlink(file_path)
    #                 elif os.path.isdir(file_path):
    #                     shutil.rmtree(file_path)
    #             except Exception as e:
    #                 if LOGGER_AVAILABLE:
    #                     logger.log_error(f"删除marker文件 {file_path} 时出错: {e}")
    #                 else:
    #                     print(f"删除marker文件 {file_path} 时出错: {e}")
    #         if LOGGER_AVAILABLE:
    #             logger.log_success(f"已清理 {marker_dir} 目录")
    #         else:
    #             print(f"✓ 已清理 {marker_dir} 目录")
    #     except Exception as e:
    #         print(f"清理 {marker_dir} 目录时出错: {e}")
    
    # 清理日志目录（保留最近的一个日志文件）
    logs_dir = "recognition_logs"
    if os.path.exists(logs_dir):
        try:
            log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
            if len(log_files) > 1:
                # 按修改时间排序，保留最新的
                log_files.sort(key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)), reverse=True)
                for log_file in log_files[1:]:
                    try:
                        os.remove(os.path.join(logs_dir, log_file))
                    except Exception as e:
                        if LOGGER_AVAILABLE:
                            logger.log_error(f"删除日志文件 {log_file} 时出错: {e}")
                        else:
                            print(f"删除日志文件 {log_file} 时出错: {e}")
                if LOGGER_AVAILABLE:
                    logger.log_success(f"已清理旧日志文件，保留最新的: {log_files[0]}")
                else:
                    print(f"✓ 已清理旧日志文件，保留最新的: {log_files[0]}")
            elif log_files:
                if LOGGER_AVAILABLE:
                    logger.log_info(f"只有一个日志文件，保留: {log_files[0]}")
                else:
                    print(f"✓ 只有一个日志文件，保留: {log_files[0]}")
            else:
                if LOGGER_AVAILABLE:
                    logger.log_info("日志目录为空")
                else:
                    print("✓ 日志目录为空")
        except Exception as e:
            if LOGGER_AVAILABLE:
                logger.log_error(f"清理日志目录时出错: {e}")
            else:
                print(f"清理日志目录时出错: {e}")
    
    if LOGGER_AVAILABLE:
        logger.log_success("清理完成")
        logger.end_step("step1_helper", "完成")
    else:
        print("\n✅ 清理完成！")


def test_v2_optimizations():
    """测试V2.0优化功能 - 仅测试基础工具，不涉及其他步骤的功能"""
    if LOGGER_AVAILABLE:
        logger = get_step_logger()
        logger.start_step("step1_helper", "V2.0优化功能测试")
    else:
        print("\n" + "=" * 60)
        print("测试V2.0优化功能")
        print("=" * 60)
        print("此功能将测试基础工具的优化功能")
        print("-" * 60)
    
    test_results = []
    
    try:
        # 测试1：图像哈希工具
        print("\n1. 测试图像哈希工具...")
        try:
            import cv2
            import numpy as np
            from src.utils.image_hash import get_dhash, calculate_hamming_distance
            
            # 创建两个测试图像
            img1 = np.ones((50, 50, 3), dtype=np.uint8) * 128
            img2 = np.ones((50, 50, 3), dtype=np.uint8) * 128
            
            # 计算哈希
            hash1 = get_dhash(img1)
            hash2 = get_dhash(img2)
            distance = calculate_hamming_distance(hash1, hash2)
            
            if distance == 0:  # 相同图像的哈希距离应该为0
                print("✓ 图像哈希工具测试通过")
                test_results.append(("图像哈希工具", True))
            else:
                print("❌ 图像哈希工具测试失败")
                test_results.append(("图像哈希工具", False))
        except Exception as e:
            print(f"❌ 图像哈希工具测试失败: {e}")
            test_results.append(("图像哈希工具", False))
        
        # 注释掉其他测试，这些属于其他步骤的功能
        # 测试2：自动缓存更新器 - 属于匹配步骤
        # 测试3：图像预处理流水线 - 属于切割步骤
        # 测试4：质量检测器 - 属于切割步骤
        # 测试5：可视化调试器 - 属于匹配步骤
        # 测试6：增强特征匹配器 - 属于匹配步骤
        # 测试7：ORB特征点优化 - 属于匹配步骤
        
    except Exception as e:
        if LOGGER_AVAILABLE:
            logger.log_error(f"V2.0优化测试过程中出错: {e}")
        else:
            print(f"❌ V2.0优化测试过程中出错: {e}")
        test_results.append(("测试执行", False))
    
    # 输出测试结果
    if LOGGER_AVAILABLE:
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        
        logger.log_info(f"总计: {passed}/{total} 个测试通过")
        
        # 生成报告
        stats = logger.get_step_stats("step1_helper")
        additional_info = {
            "files_processed": [name for name, _ in test_results],
            "test_results": test_results
        }
        
        report_generator = get_report_generator()
        report_generator.generate_step_report("step1_helper", stats, additional_info)
        
        logger.end_step("step1_helper", "完成" if passed == total else "部分失败")
        
        return passed == total
    else:
        print("\n" + "=" * 60)
        print("V2.0优化测试结果汇总")
        print("=" * 60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✓ 通过" if result else "✗ 失败"
            print(f"{test_name:20} {status}")
            if result:
                passed += 1
        
        print("-" * 60)
        print(f"总计: {passed}/{total} 个测试通过")
        
        if passed == total:
            print("🎉 V2.0优化功能测试全部通过！")
            return True
        else:
            print("⚠️ 部分测试失败，请检查相关功能。")
            return False

def main():
    """主函数"""
    print("辅助功能测试模块")
    print("=" * 50)
    print("1. 检查环境和依赖")
    print("2. 检查数据文件")
    print("3. 清理切割结果和日志")
    print("4. 测试V2.0优化功能")
    print("0. 退出")
    print("-" * 50)
    
    while True:
        try:
            choice = input("请选择操作 (0-4): ").strip()
            
            if choice == '0':
                print("感谢使用，再见！")
                break
            elif choice == '1':
                check_dependencies()
            elif choice == '2':
                check_data_files()
            elif choice == '3':
                clear_previous_results()
            elif choice == '4':
                test_v2_optimizations()
            else:
                print("无效选择，请输入0-4之间的数字")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()