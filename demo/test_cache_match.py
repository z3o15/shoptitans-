#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试缓存匹配功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.feature_cache import FeatureCache
def main():
    print("开始测试缓存匹配功能...")

    # 测试缓存系统
    print("1. 测试特征缓存系统...")
    cache = FeatureCache()
    info = cache.get_cache_info()
    print(f"缓存目录: {info['cache_dir']}")
    print(f"缓存特征数: {info['total_features']}")

    if info['total_features'] == 0:
        print("错误: 缓存为空，请先运行 python build_cache.py output_enter_image/base_equipment")
        return 1

    print("2. 测试匹配功能...")
    try:
        # 直接运行匹配脚本
        import subprocess
        result = subprocess.run([
            sys.executable, "step_tests/3_match_cached.py",
            "--base-dir", "output_enter_image/base_equipment",
            "--compare-dir", "output_enter_image/equipment_transparent"
        ], capture_output=True, text=True)

        print("匹配输出:")
        print(result.stdout)
        if result.stderr:
            print("错误信息:")
            print(result.stderr)

        success = result.returncode == 0
        if success:
            print("匹配测试成功!")
            return 0
        else:
            print("匹配测试失败!")
            return 1

    except Exception as e:
        print(f"测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())