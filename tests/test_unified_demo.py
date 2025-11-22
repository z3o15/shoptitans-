#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一测试程序演示脚本
展示如何使用统一测试程序进行各种测试
"""

import os
import sys
import subprocess

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def demo_unified_test():
    """演示统一测试程序的使用"""
    print("=" * 80)
    print("统一测试程序演示")
    print("=" * 80)
    
    # 确保在tests目录中
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 测试命令列表
    test_commands = [
        ("显示帮助信息", ["python", "test_unified.py", "--help"]),
        ("配置管理器测试", ["python", "test_unified.py", "config"]),
        ("独立模块测试", ["python", "test_unified.py", "standalone"]),
        ("增强识别器测试", ["python", "test_unified.py", "enhanced"]),
        ("主程序集成测试", ["python", "test_unified.py", "main"]),
        ("系统基础测试", ["python", "test_unified.py", "system"]),
    ]
    
    for test_name, cmd in test_commands:
        print(f"\n{'='*60}")
        print(f"演示: {test_name}")
        print(f"命令: {' '.join(cmd)}")
        print(f"{'='*60}")
        
        success, stdout, stderr = run_command(cmd, cwd=script_dir)
        
        if success:
            # 只显示前几行输出，避免过多信息
            lines = stdout.split('\n')
            preview_lines = lines[:10]  # 显示前10行
            print("\n".join(preview_lines))
            
            if len(lines) > 10:
                print(f"\n... (输出已截断，共 {len(lines)} 行)")
        else:
            print(f"❌ 命令执行失败:")
            print(stderr)
        
        print("\n按回车键继续...")
        input()

def main():
    """主函数"""
    print("统一测试程序演示")
    print("这个脚本将演示如何使用统一测试程序进行各种测试")
    print("\n注意：某些测试可能因为缺少测试图像而跳过部分功能")
    print("这是正常行为，不影响测试程序的功能验证")
    
    demo_unified_test()
    
    print("\n" + "=" * 80)
    print("演示完成！")
    print("=" * 80)
    
    print("\n使用说明:")
    print("1. cd tests  # 进入测试目录")
    print("2. python test_unified.py --help  # 查看帮助信息")
    print("3. python test_unified.py [测试类型]  # 执行特定测试")
    print("\n支持的测试类型:")
    print("- system: 系统基础测试")
    print("- mvp: MVP功能测试")
    print("- enhanced: 增强识别器测试")
    print("- standalone: 独立模块测试")
    print("- config: 配置管理器测试")
    print("- main: 主程序集成测试")
    print("- full: 完整测试（执行所有测试）")
    print("\n可选参数:")
    print("--verbose 或 -v: 显示详细输出")

if __name__ == "__main__":
    main()