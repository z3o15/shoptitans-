#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MVP测试运行脚本
简化的测试入口，快速验证高级装备识别器功能
"""

import os
import sys

def check_environment():
    """检查测试环境"""
    print("🔍 检查测试环境...")
    
    # 检查必要文件
    required_files = [
        "src/advanced_matcher.py",
        "src/equipment_recognizer.py",
        "images/base_equipment/target_equipment_1.webp",
        "images/cropped_equipment/"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少必要文件:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\n💡 解决方案:")
        print("   1. 确保已运行过截图切割（python run_recognition.py）")
        print("   2. 检查基准装备图像是否存在于正确位置")
        print("   3. 确保所有必要文件都已创建")
        return False
    
    print("✅ 环境检查通过")
    return True


def run_quick_test():
    """运行快速测试"""
    print("\n🚀 运行快速MVP测试...")
    
    try:
        # 导入并运行测试
        from test_mvp import main as test_main
        test_main()
        
    except ImportError as e:
        print(f"❌ 导入测试模块失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")
        return False
    
    return True


def show_results():
    """显示测试结果"""
    print("\n📊 查看测试结果:")
    
    # 检查报告文件
    if os.path.exists("MVP_TEST_REPORT.md"):
        print("✅ 测试报告已生成: MVP_TEST_REPORT.md")
        print("   请打开查看详细测试结果")
    else:
        print("⚠️  测试报告未找到")
    
    # 检查输出目录
    if os.path.exists("images/cropped_equipment"):
        files = len(list(os.listdir("images/cropped_equipment")))
        print(f"✅ 切割装备数量: {files}")
    
    print("\n💡 下一步:")
    print("1. 根据测试结果调整参数")
    print("2. 集成到主识别流程中")
    print("3. 添加更多装备类型支持")


def main():
    """主函数"""
    print("=" * 60)
    print("高级装备识别器 MVP 测试")
    print("=" * 60)
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请解决上述问题后重试")
        return
    
    # 运行快速测试
    if run_quick_test():
        print("\n✅ MVP测试完成")
        show_results()
    else:
        print("\n❌ MVP测试失败")


if __name__ == "__main__":
    main()