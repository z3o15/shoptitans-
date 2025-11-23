#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成掩码后的装备图片
用于可视化背景掩码效果，验证掩码策略是否正确
"""

import os
import sys
import cv2
import numpy as np
from PIL import Image

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def log_message(tag, message):
    """统一日志输出格式"""
    print(f"[{tag}] {message}")

def load_image(image_path):
    """加载图像并处理透明通道"""
    try:
        # 使用PIL加载图像以正确处理透明通道
        img = Image.open(image_path)
        
        # 如果是RGBA图像，转换为RGB（白色背景）
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        
        # 转换为numpy数组
        img_array = np.array(img)
        
        # 转换为BGR格式（OpenCV格式）
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        return img_array
    except Exception as e:
        log_message("ERROR", f"加载图像失败 {image_path}: {e}")
        return None

def create_background_mask(image, target_color_bgr=(46, 33, 46), tolerance=20):
    """
    创建背景掩码，精确排除指定背景色，保留装备边缘的偏紫部分
    增加容差范围到±20，并添加浅紫色排除逻辑
    
    掩码逻辑：
    - 255值: 背景区域(深紫色39212e、浅紫色20904f71及其变化范围)
    - 0值: 前景区域(装备)
    """
    try:
        # 创建颜色范围掩码，增加容差以覆盖39212e深紫色的变化范围
        lower_bound = np.array([
            max(0, target_color_bgr[0] - tolerance),
            max(0, target_color_bgr[1] - tolerance),
            max(0, target_color_bgr[2] - tolerance)
        ])
        upper_bound = np.array([
            min(255, target_color_bgr[0] + tolerance),
            min(255, target_color_bgr[1] + tolerance),
            min(255, target_color_bgr[2] + tolerance)
        ])
        
        # 创建初始背景掩码（深紫色39212e范围）
        mask_bg = cv2.inRange(image, lower_bound, upper_bound)
        
        # 创建浅紫色掩码（20904f71正负5）
        light_purple_lower = np.array([241, 240, 241])  # 20904f71的BGR值，容差±5
        light_purple_upper = np.array([247, 250, 247])
        mask_light_purple = cv2.inRange(image, light_purple_lower, light_purple_upper)
        
        # 合并背景掩码（深紫色和浅紫色都视为背景）
        mask_combined = cv2.bitwise_or(mask_bg, mask_light_purple)
        
        # 使用更精细的形态学操作
        kernel_small = np.ones((2, 2), np.uint8)
        
        # 轻微腐蚀，确保只去掉真正的背景区域
        mask_combined = cv2.erode(mask_combined, kernel_small, iterations=1)
        
        # 再轻微膨胀，但使用较小的核，避免影响装备边缘
        mask_combined = cv2.dilate(mask_combined, kernel_small, iterations=1)
        
        # 应用更温和的高斯模糊，只轻微平滑边缘
        mask_combined = cv2.GaussianBlur(mask_combined, (3, 3), 0.5)
        
        # 二值化，确保只有0和255
        _, mask_combined = cv2.threshold(mask_combined, 200, 255, cv2.THRESH_BINARY)
        
        return mask_combined
    except Exception as e:
        log_message("ERROR", f"背景掩码创建失败: {e}")
        return np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)

def create_combined_mask(img1, img2, target_color_bgr=(46, 33, 46), tolerance=20):
    """
    为两张图像创建组合掩码，确保两张图像使用相同的掩码策略
    
    掩码逻辑：
    - 255值: 背景区域(深紫色39212e、浅紫色20904f71及其变化范围)
    - 0值: 前景区域(装备)
    """
    try:
        # 为两张图像分别创建背景掩码
        mask1_bg = create_background_mask(img1, target_color_bgr, tolerance)
        mask2_bg = create_background_mask(img2, target_color_bgr, tolerance)
        
        # 创建前景掩码
        mask1_fg = cv2.bitwise_not(mask1_bg)
        mask2_fg = cv2.bitwise_not(mask2_bg)
        
        # 合并前景掩码，只计算两张图像都有前景的区域
        combined_mask = cv2.bitwise_and(mask1_fg, mask2_fg)
        
        return combined_mask
    except Exception as e:
        log_message("ERROR", f"组合掩码创建失败: {e}")
        return np.ones((img1.shape[0], img1.shape[1]), dtype=np.uint8) * 255

def apply_mask_to_image(image, mask):
    """
    将掩码应用到图像，生成掩码后的图像
    背景区域变为白色，前景区域保持原色
    
    掩码逻辑（与create_background_mask一致）：
    - 255值: 背景区域(深紫色39212e、浅紫色20904f71及其变化范围)
    - 0值: 前景区域(装备)
    """
    try:
        # 创建白色背景
        white_bg = np.ones_like(image) * 255
        
        # 确保掩码是二值的（0和255）
        mask_binary = np.where(mask > 127, 255, 0).astype(np.uint8)
        
        # 将前景区域复制到白色背景上
        # 掩码中255是背景，0是前景（与create_background_mask的输出一致）
        result = np.where(mask_binary[:, :, np.newaxis] == 0, image, white_bg)
        
        return result
    except Exception as e:
        log_message("ERROR", f"掩码应用失败: {e}")
        return image

def generate_masked_images():
    """生成掩码后的装备图片"""
    log_message("INIT", "开始生成掩码后的装备图片")
    
    # 设置路径
    base_dir = "images/base_equipment_new"
    compare_dir = "images/cropped_equipment_transparent"
    output_dir = "test"
    
    # 检查目录是否存在
    if not os.path.exists(base_dir):
        log_message("ERROR", f"基准图像目录不存在: {base_dir}")
        return False
    
    if not os.path.exists(compare_dir):
        log_message("ERROR", f"对比图像目录不存在: {compare_dir}")
        return False
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "base_masked"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "compare_masked"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "masks"), exist_ok=True)
    
    # 获取图像列表
    base_images = [f for f in os.listdir(base_dir) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    compare_images = [f for f in os.listdir(compare_dir) 
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    log_message("INIT", f"找到 {len(base_images)} 个基准图像")
    log_message("INIT", f"找到 {len(compare_images)} 个对比图像")
    
    # 处理基准图像
    log_message("PROCESS", "处理基准图像...")
    for base_img in base_images:
        base_path = os.path.join(base_dir, base_img)
        base_image = load_image(base_path)
        
        if base_image is None:
            continue
        
        # 创建背景掩码
        mask_bg = create_background_mask(base_image)
        
        # 应用掩码到图像
        masked_image = apply_mask_to_image(base_image, mask_bg)
        
        # 保存结果
        output_path = os.path.join(output_dir, "base_masked", base_img)
        mask_path = os.path.join(output_dir, "masks", f"mask_{base_img}")
        
        cv2.imwrite(output_path, masked_image)
        cv2.imwrite(mask_path, mask_bg)
        
        log_message("SAVE", f"保存: {output_path}, 掩码: {mask_path}")
    
    # 处理对比图像
    log_message("PROCESS", "处理对比图像...")
    for compare_img in compare_images:
        compare_path = os.path.join(compare_dir, compare_img)
        compare_image = load_image(compare_path)
        
        if compare_image is None:
            continue
        
        # 创建背景掩码
        mask_bg = create_background_mask(compare_image)
        
        # 应用掩码到图像
        masked_image = apply_mask_to_image(compare_image, mask_bg)
        
        # 保存结果
        output_path = os.path.join(output_dir, "compare_masked", compare_img)
        mask_path = os.path.join(output_dir, "masks", f"mask_{compare_img}")
        
        cv2.imwrite(output_path, masked_image)
        cv2.imwrite(mask_path, mask_bg)
        
        log_message("SAVE", f"保存: {output_path}, 掩码: {mask_path}")
    
    log_message("RESULT", f"掩码后的图片已保存到: {output_dir}")
    log_message("RESULT", f"  - 基准图像掩码后: {os.path.join(output_dir, 'base_masked')}")
    log_message("RESULT", f"  - 对比图像掩码后: {os.path.join(output_dir, 'compare_masked')}")
    log_message("RESULT", f"  - 掩码图像: {os.path.join(output_dir, 'masks')}")
    
    return True

def main():
    """主函数"""
    log_message("INIT", "掩码后装备图片生成程序")
    
    try:
        success = generate_masked_images()
        if success:
            log_message("INIT", "生成成功完成")
        else:
            log_message("ERROR", "生成失败")
    except KeyboardInterrupt:
        log_message("INIT", "程序被用户中断")
    except Exception as e:
        log_message("ERROR", f"发生错误: {e}")

if __name__ == "__main__":
    main()