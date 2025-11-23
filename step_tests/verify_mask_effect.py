#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证掩码效果的脚本
检查掩码是否正确地识别了背景和前景
"""

import os
import sys
import cv2
import numpy as np

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def log_message(tag, message):
    """统一日志输出格式"""
    print(f"[{tag}] {message}")

def analyze_mask(mask_path):
    """分析掩码图像，统计黑白像素比例"""
    try:
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        if mask is None:
            log_message("ERROR", f"无法加载掩码图像: {mask_path}")
            return None
            
        # 统计像素值
        total_pixels = mask.shape[0] * mask.shape[1]
        white_pixels = np.sum(mask == 255)  # 背景像素
        black_pixels = np.sum(mask == 0)    # 前景像素
        
        white_ratio = white_pixels / total_pixels * 100
        black_ratio = black_pixels / total_pixels * 100
        
        return {
            'total_pixels': total_pixels,
            'white_pixels': white_pixels,
            'black_pixels': black_pixels,
            'white_ratio': white_ratio,
            'black_ratio': black_ratio
        }
    except Exception as e:
        log_message("ERROR", f"分析掩码失败 {mask_path}: {e}")
        return None

def verify_masked_image(original_path, masked_path, mask_path):
    """验证掩码后的图像是否正确"""
    try:
        # 加载原始图像和掩码后图像
        original = cv2.imread(original_path)
        masked = cv2.imread(masked_path)
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        
        if original is None or masked is None or mask is None:
            log_message("ERROR", f"无法加载图像进行验证")
            return False
            
        # 检查尺寸是否一致
        if original.shape != masked.shape:
            log_message("ERROR", f"原始图像和掩码后图像尺寸不一致")
            return False
            
        # 检查掩码后图像的背景区域是否为白色
        # 获取掩码中为255（背景）的像素位置
        bg_mask = mask == 255
        
        # 检查这些位置在掩码后图像中是否为白色
        bg_pixels_masked = masked[bg_mask]
        
        # 计算背景区域的平均颜色
        avg_bg_color = np.mean(bg_pixels_masked, axis=0)
        
        # 检查是否接近白色（允许一定误差）
        is_white_bg = np.all(avg_bg_color > 240)  # 所有通道值都大于240
        
        return is_white_bg
    except Exception as e:
        log_message("ERROR", f"验证掩码后图像失败: {e}")
        return False

def main():
    """主函数"""
    log_message("INIT", "开始验证掩码效果")
    
    # 设置路径
    base_dir = "images/base_equipment_new"
    compare_dir = "images/cropped_equipment_transparent"
    base_masked_dir = "test/base_masked"
    compare_masked_dir = "test/compare_masked"
    masks_dir = "test/masks"
    
    # 检查目录是否存在
    if not all(os.path.exists(d) for d in [base_dir, compare_dir, base_masked_dir, compare_masked_dir, masks_dir]):
        log_message("ERROR", "必要的目录不存在，请先运行 generate_masked_images.py")
        return
    
    # 获取图像列表
    base_images = [f for f in os.listdir(base_dir) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    compare_images = [f for f in os.listdir(compare_dir) 
                     if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    log_message("INIT", f"找到 {len(base_images)} 个基准图像")
    log_message("INIT", f"找到 {len(compare_images)} 个对比图像")
    
    # 验证基准图像
    log_message("VERIFY", "验证基准图像掩码效果...")
    base_success = 0
    for img in base_images:
        original_path = os.path.join(base_dir, img)
        masked_path = os.path.join(base_masked_dir, img)
        mask_path = os.path.join(masks_dir, f"mask_{img}")
        
        # 分析掩码
        mask_stats = analyze_mask(mask_path)
        if mask_stats:
            log_message("STATS", f"{img}: 背景{mask_stats['white_ratio']:.1f}%, 前景{mask_stats['black_ratio']:.1f}%")
        
        # 验证掩码后图像
        is_valid = verify_masked_image(original_path, masked_path, mask_path)
        if is_valid:
            base_success += 1
            log_message("OK", f"{img}: 掩码验证通过")
        else:
            log_message("FAIL", f"{img}: 掩码验证失败")
    
    # 验证对比图像
    log_message("VERIFY", "验证对比图像掩码效果...")
    compare_success = 0
    for img in compare_images:
        original_path = os.path.join(compare_dir, img)
        masked_path = os.path.join(compare_masked_dir, img)
        mask_path = os.path.join(masks_dir, f"mask_{img}")
        
        # 分析掩码
        mask_stats = analyze_mask(mask_path)
        if mask_stats:
            log_message("STATS", f"{img}: 背景{mask_stats['white_ratio']:.1f}%, 前景{mask_stats['black_ratio']:.1f}%")
        
        # 验证掩码后图像
        is_valid = verify_masked_image(original_path, masked_path, mask_path)
        if is_valid:
            compare_success += 1
            log_message("OK", f"{img}: 掩码验证通过")
        else:
            log_message("FAIL", f"{img}: 掩码验证失败")
    
    # 输出总结
    log_message("RESULT", f"基准图像验证: {base_success}/{len(base_images)} 通过")
    log_message("RESULT", f"对比图像验证: {compare_success}/{len(compare_images)} 通过")
    log_message("RESULT", f"总体验证: {base_success + compare_success}/{len(base_images) + len(compare_images)} 通过")
    
    if base_success + compare_success == len(base_images) + len(compare_images):
        log_message("RESULT", "所有图像掩码验证通过！")
    else:
        log_message("WARNING", "部分图像掩码验证失败，可能需要调整掩码参数")

if __name__ == "__main__":
    main()