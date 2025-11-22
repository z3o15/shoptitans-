#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一测试程序
整合所有测试功能，支持命令行参数选择特定测试类型
"""

import os
import sys
import argparse
import time
import tempfile
import shutil
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_system():
    """系统基础测试（来自 tests/test_system.py）"""
    print("\n" + "=" * 60)
    print("系统基础测试")
    print("=" * 60)
    
    results = []
    
    try:
        # 导入系统测试模块
        from tests.test_system import (
            create_test_images, 
            test_equipment_recognizer, 
            test_screenshot_cutter, 
            test_equipment_matcher,
            cleanup_test_files
        )
        
        # 创建测试图像
        print("创建测试图像...")
        if create_test_images():
            results.append(("创建测试图像", True))
        else:
            results.append(("创建测试图像", False))
        
        # 测试各个组件
        results.append(("装备识别器", test_equipment_recognizer()))
        results.append(("截图切割器", test_screenshot_cutter()))
        results.append(("装备匹配器", test_equipment_matcher()))
        
        # 清理测试文件
        cleanup_test_files()
        
    except Exception as e:
        print(f"❌ 系统测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        results.append(("系统测试", False))
    
    return results

def test_mvp():
    """MVP功能测试（来自 tests/test_mvp.py）"""
    print("\n" + "=" * 60)
    print("MVP功能测试")
    print("=" * 60)
    
    results = []
    
    try:
        # 导入MVP测试模块
        from tests.test_mvp import (
            create_test_images,
            test_single_recognition,
            test_batch_recognition,
            test_different_configurations
        )
        
        # 检查测试图像
        if create_test_images():
            results.append(("检查测试图像", True))
        else:
            results.append(("检查测试图像", False))
            return results
        
        # 执行各项测试
        try:
            test_single_recognition()
            results.append(("单个装备识别", True))
        except Exception as e:
            print(f"❌ 单个装备识别测试失败: {e}")
            results.append(("单个装备识别", False))
        
        try:
            test_batch_recognition()
            results.append(("批量装备识别", True))
        except Exception as e:
            print(f"❌ 批量装备识别测试失败: {e}")
            results.append(("批量装备识别", False))
        
        try:
            test_different_configurations()
            results.append(("不同配置测试", True))
        except Exception as e:
            print(f"❌ 不同配置测试失败: {e}")
            results.append(("不同配置测试", False))
        
    except Exception as e:
        print(f"❌ MVP测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        results.append(("MVP测试", False))
    
    return results

def test_enhanced():
    """增强识别器测试（来自 tests/test_enhanced_recognizer.py）"""
    print("\n" + "=" * 60)
    print("增强识别器测试")
    print("=" * 60)
    
    results = []
    
    try:
        # 导入增强识别器测试模块
        from tests.test_enhanced_recognizer import (
            test_config_manager,
            test_enhanced_recognizer,
            test_main_integration,
            test_backward_compatibility
        )
        
        # 执行各项测试
        results.append(("配置管理器", test_config_manager()))
        results.append(("增强版识别器", test_enhanced_recognizer()))
        results.append(("主程序集成", test_main_integration()))
        results.append(("向后兼容性", test_backward_compatibility()))
        
    except Exception as e:
        print(f"❌ 增强识别器测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        results.append(("增强识别器测试", False))
    
    return results

def test_standalone():
    """独立模块测试"""
    print("\n" + "=" * 60)
    print("独立模块测试")
    print("=" * 60)
    
    results = []
    
    try:
        # 测试独立模块导入
        try:
            from src.advanced_matcher_standalone import AdvancedEquipmentRecognizer
            print("✅ 成功导入独立模块")
            results.append(("独立模块导入", True))
        except ImportError as e:
            print(f"❌ 导入独立模块失败: {e}")
            results.append(("独立模块导入", False))
            return results
        
        # 创建识别器实例
        try:
            recognizer = AdvancedEquipmentRecognizer(enable_masking=True, enable_histogram=True)
            print("✅ 成功创建 AdvancedEquipmentRecognizer 实例")
            results.append(("创建识别器实例", True))
        except Exception as e:
            print(f"❌ 创建识别器实例失败: {e}")
            results.append(("创建识别器实例", False))
            return results
        
        # 测试基本功能
        try:
            print(f"  - 掩码匹配: {'启用' if recognizer.enable_masking else '禁用'}")
            print(f"  - 直方图验证: {'启用' if recognizer.enable_histogram else '禁用'}")
            print(f"  - 标准尺寸: {recognizer.item_max_size}")
            results.append(("基本功能检查", True))
        except Exception as e:
            print(f"❌ 基本功能检查失败: {e}")
            results.append(("基本功能检查", False))
        
        # 测试识别功能
        base_image = 'images/base_equipment/target_equipment_1.webp'
        target_image = 'images/cropped_equipment/图层 2.png'
        
        if os.path.exists(base_image) and os.path.exists(target_image):
            try:
                result = recognizer.recognize_equipment(base_image, target_image)
                print("✅ 成功执行装备识别")
                print(f"  - 装备名称: {result.item_name}")
                print(f"  - 置信度: {result.confidence:.2f}%")
                print(f"  - 匹配方式: {result.matched_by.name}")
                results.append(("装备识别功能", True))
            except Exception as e:
                print(f"❌ 装备识别功能测试失败: {e}")
                results.append(("装备识别功能", False))
        else:
            print("⚠️ 示例图像不存在，跳过功能测试")
            results.append(("装备识别功能", None))  # 跳过测试
        
    except Exception as e:
        print(f"❌ 独立模块测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        results.append(("独立模块测试", False))
    
    return results

def test_config():
    """配置管理器集成测试"""
    print("\n" + "=" * 60)
    print("配置管理器集成测试")
    print("=" * 60)
    
    results = []
    
    try:
        # 测试配置管理器导入
        try:
            from src.config_manager import ConfigManager, get_config_manager, create_recognizer_from_config
            print("✅ 成功导入配置管理器")
            results.append(("配置管理器导入", True))
        except ImportError as e:
            print(f"❌ 导入配置管理器失败: {e}")
            results.append(("配置管理器导入", False))
            return results
        
        # 创建配置管理器实例
        try:
            config_manager = ConfigManager()
            print("✅ 成功创建配置管理器实例")
            results.append(("创建配置管理器", True))
        except Exception as e:
            print(f"❌ 创建配置管理器实例失败: {e}")
            results.append(("创建配置管理器", False))
            return results
        
        # 显示配置摘要
        try:
            print("\n配置摘要:")
            config_manager.print_config_summary()
            results.append(("配置摘要显示", True))
        except Exception as e:
            print(f"❌ 配置摘要显示失败: {e}")
            results.append(("配置摘要显示", False))
        
        # 测试获取配置
        try:
            rec_config = config_manager.get_recognition_config()
            print(f"\n识别配置:")
            print(f"  - 默认阈值: {rec_config.get('default_threshold', 80)}")
            print(f"  - 使用高级算法: {rec_config.get('use_advanced_algorithm', True)}")
            print(f"  - 启用掩码匹配: {rec_config.get('enable_masking', True)}")
            print(f"  - 启用直方图验证: {rec_config.get('enable_histogram', True)}")
            results.append(("获取识别配置", True))
        except Exception as e:
            print(f"❌ 获取识别配置失败: {e}")
            results.append(("获取识别配置", False))
        
        # 测试创建识别器
        try:
            recognizer = create_recognizer_from_config(config_manager)
            print("\n✅ 成功从配置创建识别器")
            results.append(("从配置创建识别器", True))
        except Exception as e:
            print(f"❌ 从配置创建识别器失败: {e}")
            results.append(("从配置创建识别器", False))
        
        # 测试配置更新
        try:
            print("\n测试配置更新...")
            original_threshold = config_manager.get_default_threshold()
            config_manager.set_default_threshold(75.0)
            new_threshold = config_manager.get_default_threshold()
            print(f"阈值更新: {original_threshold}% -> {new_threshold}%")
            
            # 恢复原始阈值
            config_manager.set_default_threshold(original_threshold)
            results.append(("配置更新功能", True))
        except Exception as e:
            print(f"❌ 配置更新功能测试失败: {e}")
            results.append(("配置更新功能", False))
        
        print("\n✅ 配置管理器集成测试完成")
        
    except Exception as e:
        print(f"❌ 配置管理器集成测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        results.append(("配置管理器集成测试", False))
    
    return results

def test_main():
    """主程序集成测试"""
    print("\n" + "=" * 60)
    print("主程序集成测试")
    print("=" * 60)
    
    results = []
    
    try:
        # 测试主程序导入
        try:
            from src.main import EquipmentMatcher
            from src.config_manager import get_config_manager
            print("✅ 成功导入主程序模块")
            results.append(("主程序模块导入", True))
        except ImportError as e:
            print(f"❌ 导入主程序模块失败: {e}")
            results.append(("主程序模块导入", False))
            return results
        
        # 创建配置管理器
        try:
            config_manager = get_config_manager()
            print("✅ 成功创建配置管理器")
            results.append(("创建配置管理器", True))
        except Exception as e:
            print(f"❌ 创建配置管理器失败: {e}")
            results.append(("创建配置管理器", False))
            return results
        
        # 创建装备匹配器
        try:
            matcher = EquipmentMatcher(config_manager)
            print("✅ 成功创建装备匹配器")
            results.append(("创建装备匹配器", True))
        except Exception as e:
            print(f"❌ 创建装备匹配器失败: {e}")
            results.append(("创建装备匹配器", False))
            return results
        
        # 测试批量比较功能
        base_image = 'images/base_equipment/target_equipment_1.webp'
        crop_folder = 'images/cropped_equipment'
        
        if os.path.exists(base_image) and os.path.exists(crop_folder):
            try:
                print(f"\n测试批量比较功能:")
                print(f"  基准图像: {base_image}")
                print(f"  切割装备目录: {crop_folder}")
                
                # 执行批量比较（使用较低阈值以便看到更多结果）
                results_batch = matcher.batch_compare(base_image, crop_folder, threshold=50.0)
                print(f"\n批量比较完成，找到 {len(results_batch)} 个匹配项")
                
                if results_batch:
                    print("匹配结果:")
                    for i, (filename, similarity) in enumerate(results_batch[:5], 1):
                        print(f"  {i}. {filename}: {similarity:.2f}%")
                
                results.append(("批量比较功能", True))
            except Exception as e:
                print(f"❌ 批量比较功能测试失败: {e}")
                results.append(("批量比较功能", False))
        else:
            print("⚠️ 测试图像或目录不存在，跳过批量比较测试")
            results.append(("批量比较功能", None))  # 跳过测试
        
        print("\n✅ 主程序集成测试完成")
        
    except Exception as e:
        print(f"❌ 主程序集成测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        results.append(("主程序集成测试", False))
    
    return results

def print_test_summary(all_results):
    """打印测试结果汇总"""
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    total_tests = 0
    
    for test_type, results in all_results.items():
        if not results:
            continue
            
        print(f"\n【{test_type}】")
        print("-" * 40)
        
        test_passed = 0
        test_failed = 0
        test_skipped = 0
        
        for test_name, result in results:
            total_tests += 1
            
            if result is True:
                status = "✅ 通过"
                test_passed += 1
                total_passed += 1
            elif result is False:
                status = "❌ 失败"
                test_failed += 1
                total_failed += 1
            else:  # None or other
                status = "⚠️ 跳过"
                test_skipped += 1
                total_skipped += 1
            
            print(f"  {test_name:<25} {status}")
        
        print(f"  小计: {test_passed} 通过, {test_failed} 失败, {test_skipped} 跳过")
    
    print("\n" + "=" * 80)
    print("总体统计")
    print("=" * 80)
    print(f"总测试数: {total_tests}")
    print(f"通过: {total_passed} ({total_passed/total_tests*100:.1f}%)")
    print(f"失败: {total_failed} ({total_failed/total_tests*100:.1f}%)")
    print(f"跳过: {total_skipped} ({total_skipped/total_tests*100:.1f}%)")
    
    if total_failed == 0:
        print("\n🎉 所有测试通过！系统功能正常。")
        return True
    else:
        print(f"\n⚠️ 有 {total_failed} 个测试失败，请检查相关功能。")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="统一测试程序 - 游戏装备图像识别系统")
    parser.add_argument(
        'test_type',
        choices=['system', 'mvp', 'enhanced', 'standalone', 'config', 'main', 'full'],
        help='选择要执行的测试类型'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细输出'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("游戏装备图像识别系统 - 统一测试程序")
    print("=" * 80)
    print(f"测试类型: {args.test_type}")
    print(f"详细输出: {'是' if args.verbose else '否'}")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = {}
    
    try:
        if args.test_type == 'system' or args.test_type == 'full':
            all_results['系统基础测试'] = test_system()
        
        if args.test_type == 'mvp' or args.test_type == 'full':
            all_results['MVP功能测试'] = test_mvp()
        
        if args.test_type == 'enhanced' or args.test_type == 'full':
            all_results['增强识别器测试'] = test_enhanced()
        
        if args.test_type == 'standalone' or args.test_type == 'full':
            all_results['独立模块测试'] = test_standalone()
        
        if args.test_type == 'config' or args.test_type == 'full':
            all_results['配置管理器测试'] = test_config()
        
        if args.test_type == 'main' or args.test_type == 'full':
            all_results['主程序集成测试'] = test_main()
        
        # 打印测试结果汇总
        success = print_test_summary(all_results)
        
        print(f"\n结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return success
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        return False
    except Exception as e:
        print(f"\n❌ 测试过程中出现未捕获的异常: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)