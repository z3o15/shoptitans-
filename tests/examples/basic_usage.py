#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本使用示例
演示如何使用装备识别系统进行基本的图像识别任务
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from equipment_recognizer import EquipmentRecognizer
from screenshot_cutter import ScreenshotCutter
from main import EquipmentMatcher

def example_1_basic_comparison():
    """示例1：基本的图像相似度比较"""
    print("=" * 50)
    print("示例1：基本图像相似度比较")
    print("=" * 50)
    
    # 初始化识别器
    recognizer = EquipmentRecognizer(default_threshold=80)
    
    # 比较两张图像
    img1_path = "../data/基准装备图.webp"
    img2_path = "../data/游戏截图.png"
    
    if not os.path.exists(img1_path) or not os.path.exists(img2_path):
        print("请确保基准装备图和游戏截图存在于data目录中")
        return
    
    similarity, is_match = recognizer.compare_images(img1_path, img2_path)
    print(f"图像相似度: {similarity}%")
    print(f"是否匹配: {'是' if is_match else '否'}")

def example_2_screenshot_cutting():
    """示例2：截图切割"""
    print("\n" + "=" * 50)
    print("示例2：截图切割")
    print("=" * 50)
    
    screenshot_path = "../data/游戏截图.png"
    output_folder = "../output/example_2_cropped"
    
    if not os.path.exists(screenshot_path):
        print("请确保游戏截图存在于data目录中")
        return
    
    cutter = ScreenshotCutter()
    
    # 方法1：固定坐标切割
    print("使用固定坐标切割...")
    success1 = cutter.cut_fixed(
        screenshot_path=screenshot_path,
        output_folder=os.path.join(output_folder, "fixed"),
        grid=(6, 2),
        item_width=100,
        item_height=120,
        margin_left=20,
        margin_top=350
    )
    print(f"固定坐标切割{'成功' if success1 else '失败'}")
    
    # 方法2：轮廓检测切割
    print("\n使用轮廓检测切割...")
    success2 = cutter.cut_contour(
        screenshot_path=screenshot_path,
        output_folder=os.path.join(output_folder, "contour"),
        min_area=800,
        max_area=50000
    )
    print(f"轮廓检测切割{'成功' if success2 else '失败'}")

def example_3_batch_matching():
    """示例3：批量装备匹配"""
    print("\n" + "=" * 50)
    print("示例3：批量装备匹配")
    print("=" * 50)
    
    base_img_path = "../data/基准装备图.webp"
    crop_folder = "../output/example_2_cropped/fixed"  # 使用示例2的切割结果
    
    if not os.path.exists(base_img_path):
        print("请确保基准装备图存在于data目录中")
        return
    
    if not os.path.exists(crop_folder):
        print("请先运行示例2进行截图切割")
        return
    
    # 初始化匹配器
    matcher = EquipmentMatcher(default_threshold=75)
    
    # 执行批量匹配
    matched_items = matcher.batch_compare(
        base_img_path=base_img_path,
        crop_folder=crop_folder,
        threshold=75
    )
    
    print(f"\n匹配结果：找到 {len(matched_items)} 个匹配的装备")
    for filename, similarity in matched_items:
        print(f"- {filename}: {similarity}%")

def example_4_full_pipeline():
    """示例4：完整的处理流程"""
    print("\n" + "=" * 50)
    print("示例4：完整处理流程")
    print("=" * 50)
    
    screenshot_path = "../data/游戏截图.png"
    base_img_path = "../data/基准装备图.webp"
    output_folder = "../output/example_4_full"
    
    if not os.path.exists(screenshot_path) or not os.path.exists(base_img_path):
        print("请确保基准装备图和游戏截图存在于data目录中")
        return
    
    # 初始化匹配器
    matcher = EquipmentMatcher(default_threshold=80)
    
    # 执行完整流程
    matched_items = matcher.process_screenshot(
        screenshot_path=screenshot_path,
        base_img_path=base_img_path,
        output_folder=output_folder,
        cutting_method='auto',  # 自动选择切割方式
        threshold=80
    )
    
    print(f"\n最终结果：识别到 {len(matched_items)} 个匹配的装备")

def example_5_custom_parameters():
    """示例5：自定义参数"""
    print("\n" + "=" * 50)
    print("示例5：自定义参数")
    print("=" * 50)
    
    # 自定义识别器参数
    recognizer = EquipmentRecognizer(default_threshold=85)
    
    # 计算单个图像的哈希值
    base_img_path = "../data/基准装备图.webp"
    if os.path.exists(base_img_path):
        hash_value = recognizer.get_dhash(base_img_path)
        print(f"基准装备的dHash值: {hash_value}")
    
    # 分析截图
    screenshot_path = "../data/游戏截图.png"
    if os.path.exists(screenshot_path):
        cutter = ScreenshotCutter()
        analysis = cutter.analyze_screenshot(screenshot_path)
        print("\n截图分析结果:")
        for key, value in analysis.items():
            print(f"- {key}: {value}")

def main():
    """主函数"""
    print("游戏装备图像识别系统 - 使用示例")
    print("请确保已将基准装备图和游戏截图放入data目录中")
    
    try:
        # 运行所有示例
        example_1_basic_comparison()
        example_2_screenshot_cutting()
        example_3_batch_matching()
        example_4_full_pipeline()
        example_5_custom_parameters()
        
        print("\n" + "=" * 50)
        print("所有示例运行完成！")
        print("请查看output目录中的结果文件")
        print("=" * 50)
        
    except Exception as e:
        print(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()