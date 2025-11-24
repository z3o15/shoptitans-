#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试日志适配器
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from logger_adapter import create_logger_adapter
    from unified_logger import get_unified_logger
    
    print("🧪 测试日志适配器...")
    
    # 测试新日志系统
    print("\n📝 测试新日志系统:")
    adapter = create_logger_adapter(use_new_logger=True)
    adapter.start_step("step2_cut", "测试新日志系统")
    adapter.log_info("这是一条测试信息", show_in_console=True)
    adapter.log_warning("这是一条测试警告", show_in_console=True)
    adapter.log_success("测试完成", show_in_console=True)
    adapter.end_step("step2_cut", "完成")
    
    # 测试旧日志系统
    try:
        from node_logger import get_logger as get_node_logger
        print("\n📝 测试旧日志系统:")
        adapter = create_logger_adapter(use_new_logger=False)
        adapter.start_step("step2_cut", "测试旧日志系统")
        adapter.log_info("这是一条测试信息")
        adapter.log_warning("这是一条测试警告")
        adapter.log_success("测试完成")
        adapter.end_step("step2_cut", "完成")
    except ImportError:
        print("\n⚠️ 旧日志系统不可用，跳过测试")
    
    print("\n✅ 日志适配器测试完成")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保所有必要的模块都在src目录中")