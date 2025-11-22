#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级使用示例
演示装备识别系统的高级功能和定制用法
"""

import sys
import os
import json
import time
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from equipment_recognizer import EnhancedEquipmentRecognizer
from screenshot_cutter import ScreenshotCutter
from main import EquipmentMatcher

class AdvancedEquipmentMatcher(EquipmentMatcher):
    """扩展的装备匹配器，提供更多高级功能"""
    
    def __init__(self, default_threshold=80):
        super().__init__(default_threshold, use_advanced_algorithm=True)
        self.performance_stats = {}
    
    def benchmark_performance(self, base_img_path, test_images_folder):
        """性能基准测试
        
        Args:
            base_img_path: 基准图像路径
            test_images_folder: 测试图像文件夹
        """
        print("开始性能基准测试...")
        
        test_times = []
        similarities = []
        
        for filename in os.listdir(test_images_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                img_path = os.path.join(test_images_folder, filename)
                
                start_time = time.time()
                # 使用增强版识别器的compare_images方法
                similarity, _ = self.recognizer.compare_images(base_img_path, img_path)
                similarities.append(similarity)
                
                end_time = time.time()
                test_times.append(end_time - start_time)
        
        # 计算统计数据
        self.performance_stats = {
            'total_images': len(test_times),
            'avg_time_per_image': sum(test_times) / len(test_times) if test_times else 0,
            'total_time': sum(test_times),
            'avg_similarity': sum(similarities) / len(similarities) if similarities else 0,
            'max_similarity': max(similarities) if similarities else 0,
            'min_similarity': min(similarities) if similarities else 0
        }
        
        print("基准测试结果:")
        for key, value in self.performance_stats.items():
            print(f"- {key}: {value:.4f}" if isinstance(value, float) else f"- {key}: {value}")
    
    def multi_threshold_analysis(self, base_img_path, crop_folder, thresholds=[60, 70, 80, 90]):
        """多阈值分析
        
        Args:
            base_img_path: 基准图像路径
            crop_folder: 切割图像文件夹
            thresholds: 要测试的阈值列表
        """
        print("开始多阈值分析...")
        
        results = {}
        
        for threshold in thresholds:
            matched_count = 0
            total_count = 0
            
            for filename in os.listdir(crop_folder):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    total_count += 1
                    img_path = os.path.join(crop_folder, filename)
                    
                    # 使用增强版识别器的compare_images方法
                    similarity, is_match = self.recognizer.compare_images(base_img_path, img_path, threshold)
                    if is_match:
                        matched_count += 1
            
            results[threshold] = {
                'matched': matched_count,
                'total': total_count,
                'match_rate': matched_count / total_count if total_count > 0 else 0
            }
        
        print("\n多阈值分析结果:")
        print("阈值\t匹配数\t总数\t匹配率")
        print("-" * 40)
        for threshold, data in results.items():
            print(f"{threshold}\t{data['matched']}\t{data['total']}\t{data['match_rate']:.2%}")
        
        return results
    
    def export_detailed_report(self, output_path):
        """导出详细报告
        
        Args:
            output_path: 输出文件路径
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'performance_stats': getattr(self, 'performance_stats', {}),
            'processing_results': self.results,
            'system_info': {
                'python_version': sys.version,
                'platform': sys.platform
            }
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"详细报告已导出到: {output_path}")
        except Exception as e:
            print(f"导出报告出错: {e}")

def example_1_batch_processing():
    """示例1：批量处理多个截图"""
    print("=" * 60)
    print("高级示例1：批量处理多个截图")
    print("=" * 60)
    
    # 假设有多个截图文件
    screenshot_folder = "../data"
    base_img_path = "../data/基准装备图.webp"
    output_base_folder = "../output/batch_processing"
    
    if not os.path.exists(base_img_path):
        print("请确保基准装备图存在于data目录中")
        return
    
    # 查找所有截图文件
    screenshot_files = []
    for filename in os.listdir(screenshot_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) and '截图' in filename:
            screenshot_files.append(os.path.join(screenshot_folder, filename))
    
    if not screenshot_files:
        print("未找到截图文件，请确保data目录中有包含'截图'字样的图像文件")
        return
    
    print(f"找到 {len(screenshot_files)} 个截图文件")
    
    # 初始化高级匹配器
    matcher = AdvancedEquipmentMatcher(default_threshold=80)
    print(f"使用算法: {'高级模板匹配' if matcher.recognizer.use_advanced_algorithm else '传统dHash'}")
    
    # 批量处理
    all_results = []
    for i, screenshot_path in enumerate(screenshot_files):
        print(f"\n处理截图 {i+1}/{len(screenshot_files)}: {os.path.basename(screenshot_path)}")
        
        output_folder = os.path.join(output_base_folder, f"screenshot_{i+1}")
        matched_items = matcher.process_screenshot(
            screenshot_path=screenshot_path,
            base_img_path=base_img_path,
            output_folder=output_folder,
            cutting_method='auto',
            threshold=80
        )
        
        all_results.append({
            'screenshot': os.path.basename(screenshot_path),
            'matched_count': len(matched_items),
            'matched_items': matched_items
        })
    
    # 输出汇总结果
    print("\n" + "=" * 60)
    print("批量处理汇总:")
    print("=" * 60)
    total_matched = sum(result['matched_count'] for result in all_results)
    print(f"总截图数: {len(screenshot_files)}")
    print(f"总匹配数: {total_matched}")
    print(f"平均每截图匹配数: {total_matched / len(screenshot_files):.1f}")
    
    # 导出详细报告
    report_path = os.path.join(output_base_folder, "batch_report.json")
    matcher.export_detailed_report(report_path)

def example_2_threshold_optimization():
    """示例2：阈值优化分析"""
    print("\n" + "=" * 60)
    print("高级示例2：阈值优化分析")
    print("=" * 60)
    
    base_img_path = "../data/基准装备图.webp"
    crop_folder = "../output/example_2_cropped/fixed"
    
    if not os.path.exists(base_img_path) or not os.path.exists(crop_folder):
        print("请确保基准装备图存在，并先运行基础示例2生成切割结果")
        return
    
    # 初始化高级匹配器
    matcher = AdvancedEquipmentMatcher(default_threshold=80)
    print(f"使用算法: {'高级模板匹配' if matcher.recognizer.use_advanced_algorithm else '传统dHash'}")
    
    # 执行多阈值分析
    thresholds = [50, 60, 70, 75, 80, 85, 90, 95]
    results = matcher.multi_threshold_analysis(base_img_path, crop_folder, thresholds)
    
    # 找出最佳阈值（可根据实际需求调整标准）
    best_threshold = None
    best_balance = 0
    
    for threshold, data in results.items():
        # 这里使用匹配率和匹配数的平衡作为评估标准
        balance = data['match_rate'] * data['matched']
        if balance > best_balance:
            best_balance = balance
            best_threshold = threshold
    
    print(f"\n推荐阈值: {best_threshold} (平衡值: {best_balance:.2f})")

def example_3_performance_benchmark():
    """示例3：性能基准测试"""
    print("\n" + "=" * 60)
    print("高级示例3：性能基准测试")
    print("=" * 60)
    
    base_img_path = "../data/基准装备图.webp"
    test_folder = "../output/example_2_cropped/fixed"
    
    if not os.path.exists(base_img_path) or not os.path.exists(test_folder):
        print("请确保基准装备图存在，并先运行基础示例2生成测试图像")
        return
    
    # 初始化高级匹配器
    matcher = AdvancedEquipmentMatcher(default_threshold=80)
    print(f"使用算法: {'高级模板匹配' if matcher.recognizer.use_advanced_algorithm else '传统dHash'}")
    
    # 执行性能基准测试
    matcher.benchmark_performance(base_img_path, test_folder)
    
    # 导出性能报告
    report_path = "../output/performance_report.json"
    matcher.export_detailed_report(report_path)

def example_4_custom_cutting_strategy():
    """示例4：自定义切割策略"""
    print("\n" + "=" * 60)
    print("高级示例4：自定义切割策略")
    print("=" * 60)
    
    screenshot_path = "../data/游戏截图.png"
    output_folder = "../output/custom_cutting"
    
    if not os.path.exists(screenshot_path):
        print("请确保游戏截图存在于data目录中")
        return
    
    cutter = ScreenshotCutter()
    
    # 分析截图
    analysis = cutter.analyze_screenshot(screenshot_path)
    print("截图分析结果:")
    for key, value in analysis.items():
        print(f"- {key}: {value}")
    
    # 根据分析结果选择切割策略
    if analysis.get('valid_contours', 0) > 8:
        print("\n检测到较多轮廓，使用轮廓检测切割")
        success = cutter.cut_contour(
            screenshot_path=screenshot_path,
            output_folder=os.path.join(output_folder, "adaptive_contour"),
            min_area=max(500, analysis.get('area_range', (0, 0))[0] * 0.5),
            max_area=min(50000, analysis.get('area_range', (0, 0))[1] * 1.5)
        )
    else:
        print("\n轮廓较少，使用固定坐标切割")
        success = cutter.cut_fixed(
            screenshot_path=screenshot_path,
            output_folder=os.path.join(output_folder, "adaptive_fixed"),
            grid=(6, 2),
            item_width=100,
            item_height=120,
            margin_left=20,
            margin_top=350
        )
    
    print(f"自适应切割{'成功' if success else '失败'}")

def main():
    """主函数"""
    print("游戏装备图像识别系统 - 高级使用示例")
    print("这些示例展示了系统的高级功能和定制用法")
    
    try:
        # 演示算法选择功能
        print("\n" + "=" * 60)
        print("算法选择演示")
        print("=" * 60)
        
        # 创建增强版识别器实例
        recognizer = EnhancedEquipmentRecognizer(
            default_threshold=80,
            use_advanced_algorithm=True,  # 使用高级算法
            enable_masking=True,
            enable_histogram=True
        )
        
        # 显示算法信息
        print("\n当前算法配置:")
        info = recognizer.get_algorithm_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        # 演示算法切换
        print("\n切换到传统算法:")
        recognizer.set_algorithm_mode(False)
        info = recognizer.get_algorithm_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        print("\n切换回高级算法:")
        recognizer.set_algorithm_mode(True)
        info = recognizer.get_algorithm_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        # 运行其他示例
        example_1_batch_processing()
        example_2_threshold_optimization()
        example_3_performance_benchmark()
        example_4_custom_cutting_strategy()
        
        print("\n" + "=" * 60)
        print("所有高级示例运行完成！")
        print("请查看output目录中的详细报告和结果")
        print("=" * 60)
        
    except Exception as e:
        print(f"运行高级示例时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()