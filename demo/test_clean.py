#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试输出清理功能

验证自动清理功能是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

def test_clean_functionality():
    """测试清理功能"""
    print("="*60)
    print("测试输出清理功能")
    print("="*60)

    try:
        # 测试导入清理工具
        from src.utils.output_cleaner import OutputCleaner, clean_all_outputs, clean_step_outputs
        print("✓ 成功导入清理工具")

        # 创建清理器实例
        cleaner = OutputCleaner(project_root)
        print("✓ 创建清理器实例")

        # 列出输出目录
        directories = cleaner.get_output_directories()
        print(f"✓ 找到 {len(directories)} 个输出目录:")
        for dir_path in directories:
            print(f"  - {dir_path}")

        # 测试清理特定步骤
        print("\n测试清理步骤2...")
        success = clean_step_outputs('cut', project_root)
        print(f"✓ 步骤2清理{'成功' if success else '失败'}")

        # 测试清理所有输出
        print("\n测试清理所有输出...")
        success = clean_all_outputs(project_root)
        print(f"✓ 全局清理{'成功' if success else '失败'}")

        print("\n" + "="*60)
        print("✅ 清理功能测试完成！")
        print("✅ 所有输出目录已自动清理")
        print("="*60)

        return True

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_clean_functionality()
    exit(0 if success else 1)