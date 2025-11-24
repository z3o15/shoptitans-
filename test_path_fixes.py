#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路径修复验证脚本
测试所有路径冲突问题是否已解决
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_path_manager():
    """测试路径管理器"""
    print("=" * 60)
    print("测试路径管理器")
    print("=" * 60)
    
    try:
        from src.utils.path_manager import get_path_manager, get_path, validate_path, get_path_validation_report
        
        # 获取路径管理器实例
        path_manager = get_path_manager()
        
        # 测试获取路径
        print("\n1. 测试获取路径:")
        test_keys = ['images_dir', 'base_equipment_dir', 'cache_dir']
        for key in test_keys:
            path = get_path(key)
            print(f"  {key}: {path}")
        
        # 测试路径验证
        print("\n2. 测试路径验证:")
        for key in test_keys:
            validation = validate_path(key)
            status = "✓ 有效" if validation['valid'] else "✗ 无效"
            print(f"  {key}: {status}")
            if not validation['valid'] and validation['error']:
                print(f"    错误: {validation['error']}")
        
        # 测试路径验证报告
        print("\n3. 路径验证报告:")
        report = get_path_validation_report()
        print(report)
        
        return True
    except Exception as e:
        print(f"❌ 路径管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_manager():
    """测试配置管理器"""
    print("\n" + "=" * 60)
    print("测试配置管理器")
    print("=" * 60)
    
    try:
        from src.config.config_manager import get_config_manager
        
        # 获取配置管理器实例
        config_manager = get_config_manager()
        
        # 测试路径方法
        print("\n1. 测试配置管理器路径方法:")
        test_keys = ['images_dir', 'base_equipment_dir', 'cache_dir']
        for key in test_keys:
            path = config_manager.get_path(key)
            print(f"  {key}: {path}")
        
        # 测试路径验证
        print("\n2. 测试配置管理器路径验证:")
        for key in test_keys:
            validation = config_manager.validate_path(key)
            status = "✓ 有效" if validation['valid'] else "✗ 无效"
            print(f"  {key}: {status}")
        
        return True
    except Exception as e:
        print(f"❌ 配置管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fixed_modules():
    """测试修复后的模块"""
    print("\n" + "=" * 60)
    print("测试修复后的模块")
    print("=" * 60)
    
    # 测试截图切割模块
    print("\n1. 测试截图切割模块:")
    try:
        from src.core.screenshot_cutter import ScreenshotCutter
        print("  ✓ 截图切割模块导入成功")
    except Exception as e:
        print(f"  ❌ 截图切割模块导入失败: {e}")
        return False
    
    # 测试OCR识别器模块
    print("\n2. 测试OCR识别器模块:")
    try:
        from src.ocr.enhanced_ocr_recognizer import EnhancedOCRRecognizer
        print("  ✓ OCR识别器模块导入成功")
    except Exception as e:
        print(f"  ❌ OCR识别器模块导入失败: {e}")
        return False
    
    # 测试特征缓存管理器
    print("\n3. 测试特征缓存管理器:")
    try:
        from src.cache.feature_cache_manager import FeatureCacheManager
        print("  ✓ 特征缓存管理器导入成功")
    except Exception as e:
        print(f"  ❌ 特征缓存管理器导入失败: {e}")
        return False
    
    # 测试预处理模块
    print("\n4. 测试预处理模块:")
    try:
        from src.preprocessing.enhanced_preprocess_start import process_preprocessed_images
        print("  ✓ 预处理模块导入成功")
    except Exception as e:
        print(f"  ❌ 预处理模块导入失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("路径冲突修复验证测试")
    print("测试所有路径冲突问题是否已解决")
    
    # 运行所有测试
    tests = [
        ("路径管理器", test_path_manager),
        ("配置管理器", test_config_manager),
        ("修复后的模块", test_fixed_modules)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有路径冲突问题已成功修复！")
        return True
    else:
        print(f"\n⚠️ 还有 {total - passed} 个问题需要解决")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)