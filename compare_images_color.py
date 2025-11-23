#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比较两张图片的颜色相似度
"""

import os
import sys
import cv2
import numpy as np
from PIL import Image

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入模板匹配测试中的函数
from step_tests.template_matching_test import (
    load_image,
    calculate_color_similarity,
    calculate_color_similarity_enhanced,
    create_combined_mask,
    create_background_mask
)

def log_message(tag, message):
    """统一日志输出格式"""
    print(f"[{tag}] {message}")

def create_white_mask(image, white_threshold=240):
    """
    创建白色背景掩码
    白色像素（RGB值都大于阈值）被视为背景
    """
    # 转换为RGB
    if len(image.shape) == 3:
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        rgb_image = image
    
    # 创建白色掩码（所有通道都大于阈值的像素）
    white_mask = np.all(rgb_image >= white_threshold, axis=2).astype(np.uint8) * 255
    
    return white_mask

def analyze_image_background(image, image_name):
    """分析图像的背景和前景分布"""
    log_message("ANALYSIS", f"分析图像 {image_name} 的背景和前景分布")
    
    # 创建白色背景掩码
    white_mask = create_white_mask(image)
    
    # 计算背景和前景像素数量
    bg_pixels = np.sum(white_mask == 255)
    fg_pixels = np.sum(white_mask == 0)
    total_pixels = white_mask.shape[0] * white_mask.shape[1]
    
    bg_ratio = bg_pixels / total_pixels
    fg_ratio = fg_pixels / total_pixels
    
    log_message("INFO", f"{image_name} 白色背景像素: {bg_pixels} ({bg_ratio*100:.2f}%)")
    log_message("INFO", f"{image_name} 装备像素: {fg_pixels} ({fg_ratio*100:.2f}%)")
    
    # 分析背景和前景的平均颜色
    if bg_pixels > 0:
        bg_color = np.mean(image[white_mask == 255], axis=0)
        log_message("INFO", f"{image_name} 白色背景平均颜色 (BGR): {bg_color}")
    
    if fg_pixels > 0:
        fg_color = np.mean(image[white_mask == 0], axis=0)
        log_message("INFO", f"{image_name} 装备平均颜色 (BGR): {fg_color}")
    
    return white_mask, bg_ratio, fg_ratio

def compare_images(image_path1, image_path2):
    """
    比较两张图片的颜色相似度
    """
    log_message("INIT", f"开始比较图片颜色相似度")
    log_message("INFO", f"图片1: {image_path1}")
    log_message("INFO", f"图片2: {image_path2}")
    
    # 加载图片
    img1 = load_image(image_path1)
    img2 = load_image(image_path2)
    
    if img1 is None:
        log_message("ERROR", f"无法加载图片1: {image_path1}")
        return
    
    if img2 is None:
        log_message("ERROR", f"无法加载图片2: {image_path2}")
        return
    
    log_message("INFO", f"图片1尺寸: {img1.shape}")
    log_message("INFO", f"图片2尺寸: {img2.shape}")
    
    # 分析每张图片的背景和前景
    white_mask1, bg_ratio1, fg_ratio1 = analyze_image_background(img1, "图片1")
    white_mask2, bg_ratio2, fg_ratio2 = analyze_image_background(img2, "图片2")
    
    # 创建装备区域掩码（非白色区域）
    equipment_mask1 = cv2.bitwise_not(white_mask1)
    equipment_mask2 = cv2.bitwise_not(white_mask2)
    
    # 创建组合装备掩码（两张图片都有装备的区域）
    combined_equipment_mask = cv2.bitwise_and(equipment_mask1, equipment_mask2)
    
    # 计算整体颜色相似度（包含背景）
    img1_resized = cv2.resize(img1, (100, 100))
    img2_resized = cv2.resize(img2, (100, 100))
    
    # 转换为HSV色彩空间
    hsv1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2HSV)
    hsv2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2HSV)
    
    # 计算整体直方图
    hist_size = [50, 60]
    h_ranges = [0, 180]
    s_ranges = [0, 256]
    ranges = h_ranges + s_ranges
    
    hist1_all = cv2.calcHist([hsv1], [0, 1], None, hist_size, ranges)
    hist2_all = cv2.calcHist([hsv2], [0, 1], None, hist_size, ranges)
    
    cv2.normalize(hist1_all, hist1_all, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    cv2.normalize(hist2_all, hist2_all, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    
    correlation_all = cv2.compareHist(hist1_all, hist2_all, cv2.HISTCMP_CORREL)
    similarity_all = max(0, min(1, (correlation_all + 1) / 2))
    
    log_message("RESULT", f"整体颜色相似度（包含背景）: {similarity_all:.4f} ({similarity_all*100:.2f}%)")
    
    # 调整装备掩码大小以匹配调整后的图像
    combined_equipment_mask_resized = cv2.resize(combined_equipment_mask, (100, 100))
    
    # 计算装备区域颜色相似度（排除白色背景）
    hist1_equipment = cv2.calcHist([hsv1], [0, 1], combined_equipment_mask_resized, hist_size, ranges)
    hist2_equipment = cv2.calcHist([hsv2], [0, 1], combined_equipment_mask_resized, hist_size, ranges)
    
    cv2.normalize(hist1_equipment, hist1_equipment, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    cv2.normalize(hist2_equipment, hist2_equipment, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    
    correlation_equipment = cv2.compareHist(hist1_equipment, hist2_equipment, cv2.HISTCMP_CORREL)
    similarity_equipment = max(0, min(1, (correlation_equipment + 1) / 2))
    
    log_message("RESULT", f"装备颜色相似度（排除白色背景）: {similarity_equipment:.4f} ({similarity_equipment*100:.2f}%)")
    
    # 计算标准颜色相似度
    standard_similarity = calculate_color_similarity(img1, img2)
    log_message("RESULT", f"标准颜色相似度: {standard_similarity:.4f} ({standard_similarity*100:.2f}%)")
    
    # 计算增强颜色相似度
    enhanced_similarity = calculate_color_similarity_enhanced(img1, img2)
    log_message("RESULT", f"增强颜色相似度: {enhanced_similarity:.4f} ({enhanced_similarity*100:.2f}%)")
    
    log_message("DEBUG", f"装备掩码形状: {combined_equipment_mask.shape}")
    log_message("DEBUG", f"装备掩码唯一值: {np.unique(combined_equipment_mask)}")
    
    # 计算装备区域占比
    equipment_pixels = np.sum(combined_equipment_mask == 255)
    total_pixels = combined_equipment_mask.shape[0] * combined_equipment_mask.shape[1]
    equipment_ratio = equipment_pixels / total_pixels
    log_message("INFO", f"装备区域占比: {equipment_ratio:.4f} ({equipment_ratio*100:.2f}%)")
    
    # 计算装备区域的平均颜色（排除白色背景）
    equipment_pixels1 = img1[combined_equipment_mask == 255]
    equipment_pixels2 = img2[combined_equipment_mask == 255]
    
    if len(equipment_pixels1) > 0 and len(equipment_pixels2) > 0:
        mean_color1 = np.mean(equipment_pixels1, axis=0)
        mean_color2 = np.mean(equipment_pixels2, axis=0)
        
        log_message("INFO", f"图片1装备平均颜色 (BGR): {mean_color1}")
        log_message("INFO", f"图片2装备平均颜色 (BGR): {mean_color2}")
        
        # 计算颜色差异
        color_distance = np.linalg.norm(mean_color1 - mean_color2)
        log_message("INFO", f"装备颜色欧氏距离: {color_distance:.4f}")
        
        # 转换为RGB显示
        mean_color1_rgb = mean_color1[::-1]  # BGR转RGB
        mean_color2_rgb = mean_color2[::-1]  # BGR转RGB
        log_message("INFO", f"图片1装备平均颜色 (RGB): {mean_color1_rgb}")
        log_message("INFO", f"图片2装备平均颜色 (RGB): {mean_color2_rgb}")
        
        # 分析颜色差异
        if mean_color1_rgb[0] > mean_color2_rgb[0]:
            log_message("ANALYSIS", "图片1装备颜色比图片2更红")
        elif mean_color1_rgb[0] < mean_color2_rgb[0]:
            log_message("ANALYSIS", "图片2装备颜色比图片1更红")
            
        if mean_color1_rgb[1] > mean_color2_rgb[1]:
            log_message("ANALYSIS", "图片1装备颜色比图片2更绿")
        elif mean_color1_rgb[1] < mean_color2_rgb[1]:
            log_message("ANALYSIS", "图片2装备颜色比图片1更绿")
            
        if mean_color1_rgb[2] > mean_color2_rgb[2]:
            log_message("ANALYSIS", "图片1装备颜色比图片2更蓝")
        elif mean_color1_rgb[2] < mean_color2_rgb[2]:
            log_message("ANALYSIS", "图片2装备颜色比图片1更蓝")
    
    # 解释结果
    log_message("EXPLANATION", "关于颜色相似度的解释:")
    log_message("EXPLANATION", "1. 整体颜色相似度：考虑整张图片的所有像素（包括白色背景）")
    log_message("EXPLANATION", "2. 装备颜色相似度：只考虑装备区域（排除白色背景）")
    log_message("EXPLANATION", "3. 标准颜色相似度：使用原始方法计算（可能未正确排除白色背景）")
    log_message("EXPLANATION", "4. 增强颜色相似度：使用多种方法综合计算")
    log_message("EXPLANATION", "5. 由于白色背景占主导，整体相似度会很高")
    log_message("EXPLANATION", "6. 装备颜色相似度更能反映装备本身的颜色差异")
    
    log_message("RESULT", "颜色相似度比较完成")

def main():
    """主函数"""
    image_path1 = "test/compare_masked/07.png"
    image_path2 = "test/compare_masked/08.png"
    
    compare_images(image_path1, image_path2)

if __name__ == "__main__":
    main()