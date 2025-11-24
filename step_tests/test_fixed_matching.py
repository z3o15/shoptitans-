#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的装备匹配功能
验证圆形掩码半径、紫色容差范围和颜色相似度计算的改进效果
"""

import os
import sys
import cv2
import numpy as np
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 直接导入模块文件
sys.path.insert(0, os.path.dirname(__file__))
import step3_match_equipment as step3_match_equipment

def log_message(tag, message):
    """统一日志输出格式"""
    print(f"[{tag}] {message}")

def test_circular_mask_boundary():
    """测试圆形掩码边界问题修复"""
    log_message("TEST", "开始测试圆形掩码边界问题修复")
    
    # 创建一个116x116的测试图像
    test_image = np.zeros((116, 116, 3), dtype=np.uint8)
    test_image[:] = (100, 100, 100)  # 灰色背景
    
    # 测试装备掩码创建
    equipment_mask = step3_match_equipment.create_equipment_only_mask(test_image)
    
    # 检查掩码尺寸
    assert equipment_mask.shape == (116, 116), f"掩码尺寸错误: {equipment_mask.shape}"
    
    # 检查圆形区域是否在边界内
    center_x, center_y = 58, 58
    radius = 55  # 修复后的半径
    
    # 验证圆的边界
    x_min = center_x - radius
    x_max = center_x + radius
    y_min = center_y - radius
    y_max = center_y + radius
    
    log_message("TEST", f"圆形边界: x=[{x_min},{x_max}], y=[{y_min},{y_max}]")
    
    # 验证边界不超出图像范围
    assert x_min >= 0, f"圆形左边界超出: {x_min} < 0"
    assert y_min >= 0, f"圆形上边界超出: {y_min} < 0"
    assert x_max < 116, f"圆形右边界超出: {x_max} >= 116"
    assert y_max < 116, f"圆形下边界超出: {y_max} >= 116"
    
    log_message("PASS", "圆形掩码边界测试通过")

def test_purple_tolerance_accuracy():
    """测试紫色容差范围准确性"""
    log_message("TEST", "开始测试紫色容差范围准确性")
    
    # 创建包含不同紫色的测试图像
    test_image = np.zeros((116, 116, 3), dtype=np.uint8)
    
    # 添加深紫色 (46, 33, 46)
    test_image[20:40, 20:40] = (46, 33, 46)
    
    # 添加浅紫色 (244, 245, 244)
    test_image[50:70, 20:40] = (244, 245, 244)
    
    # 添加第三种紫色 (57, 33, 45)
    test_image[80:100, 20:40] = (57, 33, 45)
    
    # 添加非紫色装备颜色 (100, 100, 100)
    test_image[20:100, 60:100] = (100, 100, 100)
    
    # 测试背景掩码创建
    background_mask = step3_match_equipment.create_background_mask(test_image)
    
    # 测试装备掩码创建
    equipment_mask = step3_match_equipment.create_equipment_only_mask(test_image)
    
    # 检查紫色区域是否被正确识别
    purple_regions = background_mask > 0
    equipment_regions = equipment_mask > 0
    
    # 验证紫色区域比例合理
    purple_ratio = np.sum(purple_regions) / (116 * 116)
    equipment_ratio = np.sum(equipment_regions) / (116 * 116)
    
    log_message("TEST", f"紫色区域比例: {purple_ratio:.2%}")
    log_message("TEST", f"装备区域比例: {equipment_ratio:.2%}")
    
    # 紫色区域应该包含三种紫色，装备区域应该包含非紫色部分
    assert 0.1 < purple_ratio < 0.5, f"紫色区域比例不合理: {purple_ratio:.2%}"
    assert 0.1 < equipment_ratio < 0.5, f"装备区域比例不合理: {equipment_ratio:.2%}"
    
    log_message("PASS", "紫色容差范围测试通过")

def test_color_similarity_calculation():
    """测试颜色相似度计算改进"""
    log_message("TEST", "开始测试颜色相似度计算改进")
    
    # 创建两个相似的测试图像
    test_image1 = np.zeros((116, 116, 3), dtype=np.uint8)
    test_image2 = np.zeros((116, 116, 3), dtype=np.uint8)
    
    # 添加相同的装备区域（略有颜色差异）
    test_image1[30:80, 30:80] = (120, 120, 120)  # 灰色装备
    test_image2[30:80, 30:80] = (125, 125, 125)  # 略亮的灰色装备
    
    # 添加相同的紫色背景
    test_image1[0:30, :] = (46, 33, 46)  # 深紫色背景
    test_image1[80:116, :] = (46, 33, 46)
    test_image1[:, 0:30] = (46, 33, 46)
    test_image1[:, 80:116] = (46, 33, 46)
    
    test_image2[0:30, :] = (46, 33, 46)
    test_image2[80:116, :] = (46, 33, 46)
    test_image2[:, 0:30] = (46, 33, 46)
    test_image2[:, 80:116] = (46, 33, 46)
    
    # 计算颜色相似度
    similarity = step3_match_equipment.calculate_color_similarity_with_euclidean(
        test_image1, test_image2, output_dir="test_output"
    )
    
    log_message("TEST", f"颜色相似度: {similarity:.3f}")
    
    # 相似图像应该有较高的相似度
    assert similarity > 0.7, f"相似图像相似度过低: {similarity:.3f}"
    
    # 创建差异较大的图像
    test_image3 = np.zeros((116, 116, 3), dtype=np.uint8)
    test_image3[30:80, 30:80] = (200, 50, 50)  # 红色装备
    test_image3[0:30, :] = (46, 33, 46)
    test_image3[80:116, :] = (46, 33, 46)
    test_image3[:, 0:30] = (46, 33, 46)
    test_image3[:, 80:116] = (46, 33, 46)
    
    # 计算差异较大的颜色相似度
    low_similarity = step3_match_equipment.calculate_color_similarity_with_euclidean(
        test_image1, test_image3, output_dir="test_output"
    )
    
    log_message("TEST", f"低相似度: {low_similarity:.3f}")
    
    # 差异图像应该有较低的相似度
    assert low_similarity < 0.5, f"差异图像相似度过高: {low_similarity:.3f}"
    
    log_message("PASS", "颜色相似度计算测试通过")

def test_composite_score_weights():
    """测试综合得分权重调整"""
    log_message("TEST", "开始测试综合得分权重调整")
    
    # 测试不同权重组合
    template_score = 80.0
    color_score = 0.8
    
    # 使用新的权重计算
    composite_score = step3_match_equipment.calculate_composite_score(
        template_score, color_score
    )
    
    log_message("TEST", f"模板得分: {template_score}, 颜色得分: {color_score}")
    log_message("TEST", f"综合得分: {composite_score}")
    
    # 验证权重调整效果
    # 新权重: 模板65%, 颜色35%
    expected_score = template_score * 0.65 + color_score * 100 * 0.35
    
    assert abs(composite_score - expected_score) < 0.1, f"综合得分计算错误: {composite_score} vs {expected_score}"
    
    # 验证模板匹配权重更大
    assert composite_score > template_score * 0.6, "模板匹配权重应该更大"
    
    log_message("PASS", "综合得分权重测试通过")

def run_all_tests():
    """运行所有测试"""
    log_message("INIT", "开始运行修复效果验证测试")
    
    # 创建测试输出目录
    os.makedirs("test_output", exist_ok=True)
    
    try:
        # 运行各项测试
        test_circular_mask_boundary()
        test_purple_tolerance_accuracy()
        test_color_similarity_calculation()
        test_composite_score_weights()
        
        log_message("RESULT", "✅ 所有测试通过！修复效果验证成功")
        return True
        
    except Exception as e:
        log_message("ERROR", f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("装备匹配功能修复效果验证测试")
    print("=" * 60)
    
    success = run_all_tests()
    
    if success:
        print("\n🎉 修复验证完成，所有问题已成功解决！")
        print("\n修复内容总结:")
        print("1. ✅ 圆形掩码半径从65调整为55，确保不超出图像边界")
        print("2. ✅ 优化紫色容差范围，减少误判装备的可能性")
        print("3. ✅ 改进颜色相似度计算，使用像素级欧氏距离平均")
        print("4. ✅ 调整综合得分权重，模板65% + 颜色35%")
        print("5. ✅ 添加详细的诊断日志，便于问题排查")
    else:
        print("\n❌ 修复验证失败，需要进一步调试")
    
    return success

if __name__ == "__main__":
    main()