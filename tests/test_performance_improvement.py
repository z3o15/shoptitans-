#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试脚本 - 测试特征缓存系统的性能提升
对比优化前后的识别速度和准确率
"""

import os
import sys
import time
import statistics
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.equipment_recognizer import EnhancedEquipmentRecognizer
from src.feature_matcher import FeatureEquipmentRecognizer, FeatureType


def test_recognition_performance(recognizer, base_image_path, target_folder, test_name):
    """
    测试识别器性能
    
    Args:
        recognizer: 识别器实例
        base_image_path: 基准图像路径
        target_folder: 目标图像文件夹
        test_name: 测试名称
        
    Returns:
        Dict: 性能测试结果
    """
    print(f"\n{'='*60}")
    print(f"测试 {test_name}")
    print(f"{'='*60}")
    
    # 获取所有目标图像
    target_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
        target_files.extend(Path(target_folder).glob(ext))
    
    if not target_files:
        print(f"未找到目标图像在 {target_folder}")
        return None
    
    print(f"找到 {len(target_files)} 个目标图像进行测试")
    
    # 记录每个图像的识别时间
    recognition_times = []
    successful_matches = 0
    
    # 预热（如果使用缓存，确保缓存已加载）
    if target_files:
        first_file = str(target_files[0])
        start_time = time.time()
        recognizer.compare_images(base_image_path, first_file)
        warmup_time = time.time() - start_time
        print(f"预热时间: {warmup_time:.3f}s")
    
    # 正式测试
    for i, target_file in enumerate(target_files):
        target_path = str(target_file)
        
        # 记录开始时间
        start_time = time.time()
        
        # 执行识别
        similarity, is_match = recognizer.compare_images(base_image_path, target_path)
        
        # 记录结束时间
        end_time = time.time()
        recognition_time = end_time - start_time
        recognition_times.append(recognition_time)
        
        if is_match:
            successful_matches += 1
        
        # 显示进度
        if (i + 1) % 10 == 0 or i == len(target_files) - 1:
            print(f"已处理 {i + 1}/{len(target_files)} 个图像，平均时间: {statistics.mean(recognition_times):.3f}s")
    
    # 计算统计信息
    avg_time = statistics.mean(recognition_times)
    min_time = min(recognition_times)
    max_time = max(recognition_times)
    median_time = statistics.median(recognition_times)
    
    # 计算性能指标
    total_time = sum(recognition_times)
    throughput = len(target_files) / total_time  # 图像/秒
    
    result = {
        'test_name': test_name,
        'total_images': len(target_files),
        'successful_matches': successful_matches,
        'match_rate': successful_matches / len(target_files) * 100,
        'total_time': total_time,
        'avg_time': avg_time,
        'min_time': min_time,
        'max_time': max_time,
        'median_time': median_time,
        'throughput': throughput,
        'times': recognition_times
    }
    
    # 显示结果
    print(f"\n{test_name} 性能测试结果:")
    print(f"  总图像数: {result['total_images']}")
    print(f"  成功匹配: {result['successful_matches']}")
    print(f"  匹配率: {result['match_rate']:.1f}%")
    print(f"  总时间: {result['total_time']:.3f}s")
    print(f"  平均时间: {result['avg_time']:.3f}s")
    print(f"  最短时间: {result['min_time']:.3f}s")
    print(f"  最长时间: {result['max_time']:.3f}s")
    print(f"  中位时间: {result['median_time']:.3f}s")
    print(f"  处理速度: {result['throughput']:.1f} 图像/秒")
    
    return result


def compare_performance(results):
    """
    比较性能测试结果
    
    Args:
        results: 测试结果列表
    """
    if len(results) < 2:
        print("需要至少两个测试结果进行比较")
        return
    
    print(f"\n{'='*60}")
    print("性能对比分析")
    print(f"{'='*60}")
    
    # 找到基准结果（第一个）
    baseline = results[0]
    baseline_name = baseline['test_name']
    
    print(f"\n基准: {baseline_name}")
    print(f"  平均时间: {baseline['avg_time']:.3f}s")
    print(f"  处理速度: {baseline['throughput']:.1f} 图像/秒")
    
    # 对比其他结果
    for result in results[1:]:
        test_name = result['test_name']
        
        # 计算性能提升
        time_improvement = (baseline['avg_time'] - result['avg_time']) / baseline['avg_time'] * 100
        throughput_improvement = (result['throughput'] - baseline['throughput']) / baseline['throughput'] * 100
        
        print(f"\n对比: {test_name}")
        print(f"  平均时间: {result['avg_time']:.3f}s ({time_improvement:+.1f}%)")
        print(f"  处理速度: {result['throughput']:.1f} 图像/秒 ({throughput_improvement:+.1f}%)")
        print(f"  匹配率: {result['match_rate']:.1f}% vs {baseline['match_rate']:.1f}%")
    
    # 找出最佳性能
    best_result = min(results, key=lambda x: x['avg_time'])
    worst_result = max(results, key=lambda x: x['avg_time'])
    
    print(f"\n性能排名:")
    print(f"  最快: {best_result['test_name']} ({best_result['avg_time']:.3f}s)")
    print(f"  最慢: {worst_result['test_name']} ({worst_result['avg_time']:.3f}s)")
    print(f"  性能差异: {(worst_result['avg_time'] - best_result['avg_time']) / best_result['avg_time'] * 100:.1f}%")


def main():
    """主函数"""
    print("特征缓存系统性能测试")
    print("=" * 60)
    
    # 测试参数
    base_equipment_dir = "images/base_equipment"
    cropped_equipment_dir = "images/cropped_equipment"
    
    # 查找最新的时间目录
    subdirs = []
    for item in os.listdir(cropped_equipment_dir):
        item_path = os.path.join(cropped_equipment_dir, item)
        if os.path.isdir(item_path) and item.replace('_', '').replace(':', '').isdigit():
            subdirs.append(item)
    
    if not subdirs:
        print("未找到切割装备目录")
        return
    
    latest_dir = sorted(subdirs)[-1]
    target_folder = os.path.join(cropped_equipment_dir, latest_dir)
    
    # 选择基准装备
    base_files = []
    for filename in os.listdir(base_equipment_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            base_files.append(filename)
    
    if not base_files:
        print("未找到基准装备图像")
        return
    
    base_image_path = os.path.join(base_equipment_dir, base_files[0])
    print(f"使用基准装备: {base_files[0]}")
    print(f"目标目录: {target_folder}")
    
    # 测试结果列表
    results = []
    
    # 测试1: 传统特征匹配（无缓存）
    try:
        traditional_recognizer = FeatureEquipmentRecognizer(
            feature_type=FeatureType.ORB,
            min_match_count=8,
            match_ratio_threshold=0.75,
            min_homography_inliers=6
        )
        
        result = test_recognition_performance(
            traditional_recognizer, 
            base_image_path, 
            target_folder, 
            "传统特征匹配(无缓存)"
        )
        
        if result:
            results.append(result)
    except Exception as e:
        print(f"传统特征匹配测试失败: {e}")
    
    # 测试2: 增强特征匹配（有缓存）
    try:
        enhanced_recognizer = EnhancedEquipmentRecognizer(
            algorithm_type="enhanced_feature",
            feature_type="ORB",
            min_match_count=8,
            match_ratio_threshold=0.75,
            min_homography_inliers=6,
            use_cache=True,
            target_size=(116, 116),
            nfeatures=1000
        )
        
        # 构建缓存（如果需要）
        enhanced_recognizer.build_cache_if_needed(base_equipment_dir)
        
        result = test_recognition_performance(
            enhanced_recognizer, 
            base_image_path, 
            target_folder, 
            "增强特征匹配(有缓存)"
        )
        
        if result:
            results.append(result)
    except Exception as e:
        print(f"增强特征匹配测试失败: {e}")
    
    # 比较性能
    if results:
        compare_performance(results)
        
        # 保存详细结果
        import json
        output_file = f"performance_test_{time.strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细结果已保存到: {output_file}")
    else:
        print("没有成功的测试结果")


if __name__ == "__main__":
    main()