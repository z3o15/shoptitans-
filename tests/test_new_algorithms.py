#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新算法集成脚本
验证特征匹配算法是否正确集成到主系统中
"""

import os
import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.equipment_recognizer import EnhancedEquipmentRecognizer

def test_feature_matching():
    """测试特征匹配算法"""
    print("=" * 60)
    print("测试特征匹配算法集成")
    print("=" * 60)
    
    try:
        # 创建特征匹配识别器
        recognizer = EnhancedEquipmentRecognizer(
            default_threshold=60,
            algorithm_type="feature",
            feature_type="ORB",
            min_match_count=8,
            match_ratio_threshold=0.75
        )
        
        print("✓ 特征匹配识别器创建成功")
        
        # 显示算法信息
        info = recognizer.get_algorithm_info()
        print("\n算法信息:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        # 测试图像路径
        base_image_path = "images/base_equipment/noblering.webp"
        target_image_path = "images/cropped_equipment/20251122_160114/08.png"
        
        # 检查文件是否存在
        if not os.path.exists(base_image_path):
            print(f"\n⚠️ 基准图像不存在: {base_image_path}")
            return False
        
        if not os.path.exists(target_image_path):
            print(f"\n⚠️ 目标图像不存在: {target_image_path}")
            return False
        
        # 执行单次匹配测试
        print(f"\n🔍 测试单次匹配:")
        similarity, is_match = recognizer.compare_images(base_image_path, target_image_path)
        print(f"相似度: {similarity:.2f}%, 匹配: {is_match}")
        
        # 执行批量匹配测试
        print(f"\n🔍 测试批量匹配:")
        target_folder = "images/cropped_equipment/20251122_160114"
        batch_results = recognizer.batch_recognize(base_image_path, target_folder, threshold=40.0)
        
        print(f"批量匹配结果 (找到 {len(batch_results)} 个匹配):")
        for i, result in enumerate(batch_results[:5], 1):  # 只显示前5个结果
            print(f"{i}. {result['item_name']} - 置信度: {result['confidence']:.2f}% - 算法: {result['algorithm']}")
            if 'match_count' in result:
                print(f"   匹配数量: {result['match_count']}, 单应性内点: {result['homography_inliers']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 特征匹配测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_advanced_matching():
    """测试高级彩色模板匹配算法"""
    print("\n" + "=" * 60)
    print("测试高级彩色模板匹配算法集成")
    print("=" * 60)
    
    try:
        # 创建高级匹配识别器
        recognizer = EnhancedEquipmentRecognizer(
            default_threshold=60,
            algorithm_type="advanced",
            enable_masking=True,
            enable_histogram=True
        )
        
        print("✓ 高级匹配识别器创建成功")
        
        # 测试图像路径
        base_image_path = "images/base_equipment/noblering.webp"
        target_image_path = "images/cropped_equipment/20251122_160114/08.png"
        
        # 执行单次匹配测试
        print(f"\n🔍 测试单次匹配:")
        similarity, is_match = recognizer.compare_images(base_image_path, target_image_path)
        print(f"相似度: {similarity:.2f}%, 匹配: {is_match}")
        
        return True
        
    except Exception as e:
        print(f"❌ 高级匹配测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_traditional_matching():
    """测试传统dHash算法"""
    print("\n" + "=" * 60)
    print("测试传统dHash算法集成")
    print("=" * 60)
    
    try:
        # 创建传统匹配识别器
        recognizer = EnhancedEquipmentRecognizer(
            default_threshold=60,
            algorithm_type="traditional"
        )
        
        print("✓ 传统匹配识别器创建成功")
        
        # 测试图像路径
        base_image_path = "images/base_equipment/noblering.webp"
        target_image_path = "images/cropped_equipment/20251122_160114/08.png"
        
        # 执行单次匹配测试
        print(f"\n🔍 测试单次匹配:")
        similarity, is_match = recognizer.compare_images(base_image_path, target_image_path)
        print(f"相似度: {similarity:.2f}%, 匹配: {is_match}")
        
        return True
        
    except Exception as e:
        print(f"❌ 传统匹配测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def compare_algorithms():
    """对比三种算法的效果"""
    print("\n" + "=" * 80)
    print("算法效果对比测试")
    print("=" * 80)
    
    base_image_path = "images/base_equipment/noblering.webp"
    target_image_path = "images/cropped_equipment/20251122_160114/08.png"
    
    algorithms = [
        ("特征匹配(ORB)", "feature", {"feature_type": "ORB"}),
        ("高级彩色模板匹配", "advanced", {}),
        ("传统dHash", "traditional", {})
    ]
    
    results = []
    
    for name, algo_type, params in algorithms:
        try:
            print(f"\n🔍 测试 {name}:")
            
            if algo_type == "feature":
                recognizer = EnhancedEquipmentRecognizer(
                    default_threshold=60,
                    algorithm_type=algo_type,
                    feature_type=params["feature_type"],
                    min_match_count=8,
                    match_ratio_threshold=0.75
                )
            elif algo_type == "advanced":
                recognizer = EnhancedEquipmentRecognizer(
                    default_threshold=60,
                    algorithm_type=algo_type,
                    enable_masking=True,
                    enable_histogram=True
                )
            else:
                recognizer = EnhancedEquipmentRecognizer(
                    default_threshold=60,
                    algorithm_type=algo_type
                )
            
            similarity, is_match = recognizer.compare_images(base_image_path, target_image_path)
            results.append((name, similarity, is_match))
            
            print(f"  相似度: {similarity:.2f}%, 匹配: {is_match}")
            
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
            results.append((name, 0.0, False))
    
    # 输出对比结果
    print(f"\n📊 算法对比结果:")
    print(f"{'算法名称':<20} {'相似度':<10} {'匹配结果':<8}")
    print("-" * 40)
    for name, similarity, is_match in results:
        print(f"{name:<20} {similarity:<10.2f} {'✓' if is_match else '✗':<8}")
    
    # 找出最佳算法
    best_result = max(results, key=lambda x: x[1])
    print(f"\n🏆 最佳算法: {best_result[0]} (相似度: {best_result[1]:.2f}%)")

def main():
    """主函数"""
    print("🚀 新算法集成测试")
    print("测试特征匹配、高级模板匹配和传统dHash算法的集成情况")
    
    success_count = 0
    total_tests = 3
    
    # 测试各种算法
    if test_feature_matching():
        success_count += 1
    
    if test_advanced_matching():
        success_count += 1
    
    if test_traditional_matching():
        success_count += 1
    
    # 对比算法效果
    try:
        compare_algorithms()
        success_count += 1
    except Exception as e:
        print(f"❌ 算法对比测试失败: {e}")
    
    # 总结
    print(f"\n" + "=" * 60)
    print(f"测试完成: {success_count}/{total_tests + 1} 项测试通过")
    
    if success_count == total_tests + 1:
        print("🎉 所有测试通过！新算法已成功集成到主系统中")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步调试")
        return False

if __name__ == "__main__":
    main()