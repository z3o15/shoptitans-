#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强版识别器的集成功能
验证所有文件更新是否正确工作
"""

import os
import sys

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_config_manager():
    """测试配置管理器"""
    print("=" * 50)
    print("测试配置管理器")
    print("=" * 50)
    
    try:
        from src.config_manager import get_config_manager, create_recognizer_from_config
        
        # 获取配置管理器
        config_manager = get_config_manager()
        print("✓ 配置管理器创建成功")
        
        # 测试获取配置
        rec_config = config_manager.get_recognition_config()
        print(f"✓ 识别配置获取成功: 算法模式={rec_config.get('use_advanced_algorithm')}")
        
        # 测试创建识别器
        recognizer = create_recognizer_from_config(config_manager)
        print("✓ 从配置创建识别器成功")
        
        # 显示算法信息
        info = recognizer.get_algorithm_info()
        print(f"✓ 算法信息获取成功: 当前算法={info.get('current_algorithm')}")
        
        return True
    except Exception as e:
        print(f"❌ 配置管理器测试失败: {e}")
        return False

def test_enhanced_recognizer():
    """测试增强版识别器"""
    print("\n" + "=" * 50)
    print("测试增强版识别器")
    print("=" * 50)
    
    try:
        from src.equipment_recognizer import EnhancedEquipmentRecognizer
        
        # 创建识别器实例
        recognizer = EnhancedEquipmentRecognizer(
            default_threshold=80,
            use_advanced_algorithm=True,
            enable_masking=True,
            enable_histogram=True
        )
        print("✓ 增强版识别器创建成功")
        
        # 测试算法切换
        print("✓ 测试算法切换功能...")
        recognizer.set_algorithm_mode(False)
        recognizer.set_algorithm_mode(True)
        print("✓ 算法切换功能正常")
        
        # 测试算法信息
        info = recognizer.get_algorithm_info()
        print(f"✓ 算法信息获取成功: {info.get('current_algorithm')}")
        
        return True
    except Exception as e:
        print(f"❌ 增强版识别器测试失败: {e}")
        return False

def test_main_integration():
    """测试主程序集成"""
    print("\n" + "=" * 50)
    print("测试主程序集成")
    print("=" * 50)
    
    try:
        from src.main import EquipmentMatcher
        from src.config_manager import get_config_manager
        
        # 创建配置管理器
        config_manager = get_config_manager()
        
        # 创建装备匹配器
        matcher = EquipmentMatcher(config_manager)
        print("✓ 装备匹配器创建成功")
        
        # 检查识别器类型
        recognizer_type = type(matcher.recognizer).__name__
        print(f"✓ 识别器类型: {recognizer_type}")
        
        if recognizer_type == "EnhancedEquipmentRecognizer":
            print("✓ 正确使用增强版识别器")
        else:
            print("❌ 未使用增强版识别器")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 主程序集成测试失败: {e}")
        return False

def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n" + "=" * 50)
    print("测试向后兼容性")
    print("=" * 50)
    
    try:
        from src.equipment_recognizer import EquipmentRecognizer, EnhancedEquipmentRecognizer
        
        # 测试传统识别器仍然可用
        traditional_recognizer = EquipmentRecognizer()
        print("✓ 传统识别器仍然可用")
        
        # 测试增强版识别器继承自传统识别器
        enhanced_recognizer = EnhancedEquipmentRecognizer()
        print("✓ 增强版识别器创建成功")
        
        # 测试增强版识别器具有传统方法
        if hasattr(enhanced_recognizer, 'get_dhash') and hasattr(enhanced_recognizer, 'calculate_similarity'):
            print("✓ 增强版识别器保持传统方法")
        else:
            print("❌ 增强版识别器缺少传统方法")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 向后兼容性测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("增强版识别器集成测试")
    print("验证所有文件更新是否正确工作")
    
    tests = [
        ("配置管理器", test_config_manager),
        ("增强版识别器", test_enhanced_recognizer),
        ("主程序集成", test_main_integration),
        ("向后兼容性", test_backward_compatibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试出现异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果汇总
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！增强版识别器集成成功！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关代码")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)