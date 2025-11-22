#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版装备识别器使用示例
演示如何使用 EnhancedEquipmentRecognizer 类进行装备识别
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.equipment_recognizer import EnhancedEquipmentRecognizer


def main():
    """主函数：演示增强版识别器的使用"""
    print("=" * 60)
    print("增强版装备识别器使用示例")
    print("=" * 60)
    
    # 创建增强版识别器实例
    recognizer = EnhancedEquipmentRecognizer(
        default_threshold=60,           # 默认匹配阈值
        use_advanced_algorithm=True,     # 默认使用高级算法
        enable_masking=True,             # 启用掩码匹配
        enable_histogram=True            # 启用直方图验证
    )
    
    # 显示算法信息
    print("\n📊 识别器信息:")
    info = recognizer.get_algorithm_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # 测试图像路径
    base_image = "images/base_equipment/target_equipment_1.webp"
    target_image = "images/cropped_equipment/图层 2.png"
    
    # 检查文件是否存在
    if not os.path.exists(base_image):
        print(f"\n❌ 基准图像不存在: {base_image}")
        return
    
    if not os.path.exists(target_image):
        print(f"\n❌ 目标图像不存在: {target_image}")
        return
    
    # 演示算法切换功能
    print(f"\n🔄 演示算法切换功能:")
    
    # 使用高级算法
    print("\n1. 使用高级模板匹配算法:")
    recognizer.set_algorithm_mode(True)
    similarity1, match1 = recognizer.compare_images(base_image, target_image)
    print(f"   相似度: {similarity1:.2f}%, 匹配: {match1}")
    
    # 使用传统算法
    print("\n2. 使用传统dHash算法:")
    recognizer.set_algorithm_mode(False)
    similarity2, match2 = recognizer.compare_images(base_image, target_image)
    print(f"   相似度: {similarity2:.2f}%, 匹配: {match2}")
    
    # 算法对比
    print(f"\n📈 算法对比结果:")
    print(f"   高级算法: {similarity1:.2f}%")
    print(f"   传统算法: {similarity2:.2f}%")
    print(f"   差异: {similarity1 - similarity2:.2f}%")
    
    # 演示批量识别功能
    print(f"\n📦 演示批量识别功能:")
    recognizer.set_algorithm_mode(True)  # 使用高级算法
    
    target_folder = "images/cropped_equipment"
    if os.path.exists(target_folder):
        batch_results = recognizer.batch_recognize(
            base_image, 
            target_folder, 
            threshold=40.0  # 降低阈值以显示更多结果
        )
        
        print(f"批量识别结果 (找到 {len(batch_results)} 个匹配):")
        for i, result in enumerate(batch_results[:5], 1):  # 只显示前5个结果
            print(f"  {i}. {result['item_name']} - 置信度: {result['confidence']:.2f}% - 算法: {result['algorithm']}")
    else:
        print(f"目标文件夹不存在: {target_folder}")
    
    # 演示高级识别功能（仅当高级算法可用时）
    if info.get('advanced_available', False):
        print(f"\n🔍 演示高级识别功能:")
        recognizer.set_algorithm_mode(True)
        advanced_result = recognizer.recognize_equipment_advanced(base_image, target_image)
        
        if advanced_result:
            print(f"装备名称: {advanced_result.item_name}")
            print(f"匹配方式: {advanced_result.matched_by.name}")
            print(f"模板相似度: {advanced_result.similarity:.2f}%")
            print(f"综合置信度: {advanced_result.confidence:.2f}%")
        else:
            print("高级识别失败")
    
    print(f"\n✅ 示例演示完成！")


if __name__ == "__main__":
    main()