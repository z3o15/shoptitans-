#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试��有模块的基本功能
"""

import sys
import os
from pathlib import Path

def test_imports():
    """测试所有模块导入"""
    print("=== 测试模块导入 ===")

    # 设置路径
    project_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_root.parent))

    try:
        # 测试配置管理器
        from src.config.config_manager import get_config_manager
        config = get_config_manager()
        print("OK 配置管理器导入成功")

        # 测试截图切割器
        from src.core.screenshot_cutter import ScreenshotCutter
        print("OK 截图切割器导入成功")

        # 测试OCR模块
        from src.ocr.enhanced_ocr_recognizer import EnhancedOCRRecognizer
        from src.ocr.csv_record_manager import CSVRecordManager
        print("OK OCR模块导入成功")

        return True

    except Exception as e:
        print(f"ERROR 模块导入失败: {e}")
        return False

def test_paths():
    """测试路径配置"""
    print("\n=== 测试路径配置 ===")

    # 获取项目根目录（step_tests的上级目录）
    project_root = Path(__file__).resolve().parents[1]

    paths_to_test = [
        project_root / "images" / "game_screenshots",
        project_root / "images" / "base_equipment",
        project_root / "images" / "equipment_crop",
        project_root / "images" / "equipment_transparent"
    ]

    all_exist = True
    for path_str in paths_to_test:
        path = Path(path_str)
        exists = path.exists()
        status = "OK" if exists else "ERROR"
        print(f"{status} {path}: {exists}")
        if not exists:
            all_exist = False

    return all_exist

def test_dependencies():
    """测试基础依赖"""
    print("\n=== 测试基础依赖 ===")

    dependencies = [
        ("cv2", "OpenCV"),
        ("PIL", "Pillow"),
        ("numpy", "NumPy")
    ]

    all_available = True
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"OK {name}")
        except ImportError:
            print(f"ERROR {name} - 未安装")
            all_available = False

    return all_available

def main():
    """主函数"""
    print("开始测试所有模块...")

    tests = [
        ("依赖检查", test_dependencies),
        ("路径检查", test_paths),
        ("模块导入", test_imports)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"ERROR {name} 测试失败: {e}")
            results.append((name, False))

    print(f"\n=== 测试结果汇总 ===")
    for name, result in results:
        status = "OK 通过" if result else "ERROR 失败"
        print(f"{name}: {status}")

    all_passed = all(result for _, result in results)
    print(f"\n总体结果: {'OK 所有测试通过' if all_passed else 'ERROR 部分测试失败'}")

    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())