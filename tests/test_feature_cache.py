#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
特征缓存系统测试脚本
测试特征缓存系统的基本功能和性能提升
"""

import os
import sys
import time
import json
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_feature_cache_manager():
    """测试特征缓存管理器"""
    print("=" * 60)
    print("测试特征缓存管理器")
    print("=" * 60)
    
    try:
        from src.feature_cache_manager import FeatureCacheManager
        
        # 创建缓存管理器
        cache_manager = FeatureCacheManager()
        
        # 检查缓存状态
        print("1. 检查缓存状态...")
        if cache_manager.is_cache_valid():
            print("✓ 缓存有效")
        else:
            print("⚠️ 缓存无效或不存在，尝试构建...")
            success = cache_manager.build_cache()
            if success:
                print("✓ 缓存构建成功")
            else:
                print("❌ 缓存构建失败")
                return False
        
        # 获取缓存统计信息
        print("\n2. 获取缓存统计信息...")
        stats = cache_manager.get_cache_stats()
        print(f"✓ 缓存中的装备数量: {stats['equipment_count']}")
        print(f"✓ 缓存创建时间: {stats['created_at']}")
        print(f"✓ 缓存版本: {stats['version']}")
        print(f"✓ 特征类型: {stats['feature_type']}")
        print(f"✓ 目标尺寸: {stats['target_size']}")
        
        # 测试特征获取
        print("\n3. 测试特征获取...")
        equipment_files = list(cache_manager.cache_data['features'].keys())[:3]  # 测试前3个装备
        for equip_file in equipment_files:
            equip_name = os.path.splitext(equip_file)[0]  # 去掉扩展名
            kp, des = cache_manager.get_cached_features(equip_name)
            if kp is not None:
                print(f"✓ {equip_name}: {len(kp)} 个关键点, {des.shape if des is not None else 'None'} 描述符")
            else:
                print(f"❌ {equip_name}: 无法获取特征")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试特征缓存管理器失败: {e}")
        return False

def test_enhanced_feature_matcher():
    """测试增强特征匹配器"""
    print("\n" + "=" * 60)
    print("测试增强特征匹配器")
    print("=" * 60)
    
    try:
        from src.enhanced_feature_matcher import EnhancedFeatureMatcher
        from src.feature_cache_manager import FeatureCacheManager
        from src.config_manager import get_config_manager
        
        # 获取配置
        config_manager = get_config_manager()
        rec_config = config_manager.get_recognition_config()
        
        # 创建缓存管理器和匹配器
        cache_manager = FeatureCacheManager()
        matcher = EnhancedFeatureMatcher(
            cache_manager=cache_manager,
            min_match_count=rec_config.get('min_match_count', 4),
            match_ratio_threshold=rec_config.get('match_ratio_threshold', 0.85),
            min_homography_inliers=rec_config.get('min_homography_inliers', 3)
        )
        
        # 检查是否有测试图像
        base_dir = "images/base_equipment"
        if not os.path.exists(base_dir):
            print("❌ 基准装备目录不存在")
            return False
        
        # 获取测试图像
        equipment_files = [f for f in os.listdir(base_dir) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))][:2]
        
        if len(equipment_files) < 2:
            print("❌ 需要至少2个基准装备图像进行测试")
            return False
        
        # 测试匹配性能
        print("1. 测试匹配性能...")
        img1_path = os.path.join(base_dir, equipment_files[0])
        img2_path = os.path.join(base_dir, equipment_files[1])
        
        # 使用缓存进行匹配
        start_time = time.time()
        result = matcher.recognize_equipment(img1_path, img2_path)
        cache_time = time.time() - start_time
        
        print(f"✓ 缓存匹配时间: {cache_time:.4f}秒")
        print(f"✓ 匹配结果: {result}")
        
        # 测试不使用缓存的匹配
        print("\n2. 测试不使用缓存的匹配...")
        matcher_no_cache = EnhancedFeatureMatcher(use_cache=False)
        
        start_time = time.time()
        result_no_cache = matcher_no_cache.recognize_equipment(img1_path, img2_path)
        no_cache_time = time.time() - start_time
        
        print(f"✓ 无缓存匹配时间: {no_cache_time:.4f}秒")
        print(f"✓ 匹配结果: {result_no_cache}")
        
        # 计算性能提升
        if no_cache_time > 0:
            speedup = no_cache_time / cache_time
            improvement = (1 - cache_time / no_cache_time) * 100
            print(f"\n3. 性能对比:")
            print(f"✓ 速度提升: {speedup:.2f}x")
            print(f"✓ 时间节省: {improvement:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试增强特征匹配器失败: {e}")
        return False

def test_equipment_recognizer():
    """测试装备识别器集成"""
    print("\n" + "=" * 60)
    print("测试装备识别器集成")
    print("=" * 60)
    
    try:
        from src.equipment_recognizer import EnhancedEquipmentRecognizer
        
        # 创建增强版识别器
        recognizer = EnhancedEquipmentRecognizer(
            algorithm_type="enhanced_feature",
            default_threshold=80
        )
        
        # 获取算法信息
        print("1. 获取算法信息...")
        info = recognizer.get_algorithm_info()
        print(f"✓ 当前算法: {info['current_algorithm']}")
        print(f"✓ 特征缓存: {info.get('feature_cache_enabled', False)}")
        
        # 检查是否有测试图像
        base_dir = "images/base_equipment"
        if not os.path.exists(base_dir):
            print("❌ 基准装备目录不存在")
            return False
        
        # 获取测试图像
        equipment_files = [f for f in os.listdir(base_dir) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))][:2]
        
        if len(equipment_files) < 2:
            print("❌ 需要至少2个基准装备图像进行测试")
            return False
        
        # 测试图像比较
        print("\n2. 测试图像比较...")
        img1_path = os.path.join(base_dir, equipment_files[0])
        img2_path = os.path.join(base_dir, equipment_files[1])
        
        start_time = time.time()
        similarity, is_match = recognizer.compare_images(img1_path, img2_path)
        compare_time = time.time() - start_time
        
        print(f"✓ 比较时间: {compare_time:.4f}秒")
        print(f"✓ 相似度: {similarity:.2f}%")
        print(f"✓ 匹配结果: {is_match}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试装备识别器集成失败: {e}")
        return False

def test_config_integration():
    """测试配置集成"""
    print("\n" + "=" * 60)
    print("测试配置集成")
    print("=" * 60)
    
    try:
        from src.config_manager import get_config_manager, create_recognizer_from_config
        
        # 获取配置管理器
        config_manager = get_config_manager()
        
        # 检查特征缓存配置
        print("1. 检查特征缓存配置...")
        feature_cache_config = config_manager.get_feature_cache_config()
        print(f"✓ 缓存启用: {feature_cache_config.get('enabled', False)}")
        print(f"✓ 缓存文件: {feature_cache_config.get('cache_file', 'N/A')}")
        print(f"✓ 目标尺寸: {feature_cache_config.get('target_size', 'N/A')}")
        print(f"✓ 特征点数: {feature_cache_config.get('nfeatures', 'N/A')}")
        
        # 从配置创建识别器
        print("\n2. 从配置创建识别器...")
        recognizer = create_recognizer_from_config(config_manager)
        
        # 获取算法信息
        info = recognizer.get_algorithm_info()
        print(f"✓ 当前算法: {info['current_algorithm']}")
        print(f"✓ 特征缓存: {info.get('feature_cache_enabled', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试配置集成失败: {e}")
        return False

def run_performance_test():
    """运行性能测试"""
    print("\n" + "=" * 60)
    print("运行性能测试")
    print("=" * 60)
    
    try:
        from src.enhanced_feature_matcher import EnhancedFeatureMatcher
        from src.feature_matcher import FeatureEquipmentMatcher
        from src.feature_cache_manager import FeatureCacheManager
        from src.config_manager import get_config_manager
        
        # 获取配置
        config_manager = get_config_manager()
        rec_config = config_manager.get_recognition_config()
        
        # 检查是否有足够的测试图像
        base_dir = "images/base_equipment"
        if not os.path.exists(base_dir):
            print("❌ 基准装备目录不存在")
            return False
        
        equipment_files = [f for f in os.listdir(base_dir)
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        
        if len(equipment_files) < 5:
            print("❌ 需要至少5个基准装备图像进行性能测试")
            return False
        
        # 创建匹配器
        cache_manager = FeatureCacheManager()
        enhanced_matcher = EnhancedFeatureMatcher(
            cache_manager=cache_manager,
            min_match_count=rec_config.get('min_match_count', 4),
            match_ratio_threshold=rec_config.get('match_ratio_threshold', 0.85),
            min_homography_inliers=rec_config.get('min_homography_inliers', 3)
        )
        traditional_matcher = FeatureEquipmentMatcher(
            min_match_count=rec_config.get('min_match_count', 4),
            match_ratio_threshold=rec_config.get('match_ratio_threshold', 0.85),
            min_homography_inliers=rec_config.get('min_homography_inliers', 3)
        )
        
        # 测试图像
        test_images = equipment_files[:5]
        test_paths = [os.path.join(base_dir, img) for img in test_images]
        
        print(f"1. 使用 {len(test_images)} 个图像进行性能测试...")
        
        # 测试增强匹配器（使用缓存）
        print("\n2. 测试增强匹配器（使用缓存）...")
        enhanced_times = []
        for i in range(len(test_paths)):
            for j in range(i+1, len(test_paths)):
                start_time = time.time()
                result = enhanced_matcher.recognize_equipment(test_paths[i], test_paths[j])
                end_time = time.time()
                enhanced_times.append(end_time - start_time)
        
        enhanced_avg_time = sum(enhanced_times) / len(enhanced_times)
        print(f"✓ 增强匹配器平均时间: {enhanced_avg_time:.4f}秒")
        
        # 测试传统匹配器（不使用缓存）
        print("\n3. 测试传统匹配器（不使用缓存）...")
        traditional_times = []
        for i in range(len(test_paths)):
            for j in range(i+1, len(test_paths)):
                start_time = time.time()
                result = traditional_matcher.recognize_equipment(test_paths[i], test_paths[j])
                end_time = time.time()
                traditional_times.append(end_time - start_time)
        
        traditional_avg_time = sum(traditional_times) / len(traditional_times)
        print(f"✓ 传统匹配器平均时间: {traditional_avg_time:.4f}秒")
        
        # 计算性能提升
        speedup = traditional_avg_time / enhanced_avg_time
        improvement = (1 - enhanced_avg_time / traditional_avg_time) * 100
        
        print(f"\n4. 性能对比结果:")
        print(f"✓ 速度提升: {speedup:.2f}x")
        print(f"✓ 时间节省: {improvement:.1f}%")
        print(f"✓ 传统匹配器总时间: {sum(traditional_times):.4f}秒")
        print(f"✓ 增强匹配器总时间: {sum(enhanced_times):.4f}秒")
        
        # 保存性能测试结果
        test_results = {
            "test_time": datetime.now().isoformat(),
            "test_images": len(test_images),
            "total_comparisons": len(enhanced_times),
            "traditional_matcher": {
                "average_time": traditional_avg_time,
                "total_time": sum(traditional_times)
            },
            "enhanced_matcher": {
                "average_time": enhanced_avg_time,
                "total_time": sum(enhanced_times)
            },
            "performance_improvement": {
                "speedup": speedup,
                "time_saved_percent": improvement
            }
        }
        
        with open("feature_cache_performance_test.json", "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ 性能测试结果已保存到: feature_cache_performance_test.json")
        
        return True
        
    except Exception as e:
        print(f"❌ 运行性能测试失败: {e}")
        return False

def main():
    """主函数"""
    print("特征缓存系统测试")
    print("=" * 60)
    
    # 检查基础环境
    if not os.path.exists("images/base_equipment"):
        print("❌ 基准装备目录不存在，请先准备测试数据")
        return
    
    # 运行测试
    tests = [
        ("特征缓存管理器", test_feature_cache_manager),
        ("增强特征匹配器", test_enhanced_feature_matcher),
        ("装备识别器集成", test_equipment_recognizer),
        ("配置集成", test_config_integration),
        ("性能测试", run_performance_test)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            print(f"\n开始测试: {test_name}")
            result = test_func()
            results[test_name] = result
            if result:
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试出错: {e}")
            results[test_name] = False
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！特征缓存系统工作正常。")
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()