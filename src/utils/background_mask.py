#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
背景掩码工具模块
提供统一的背景掩码创建功能，用于图像处理中的背景去除
"""

import cv2
import numpy as np


def create_background_mask(image, target_color_bgr=(46, 33, 46), tolerance=20):
    """
    创建背景掩码，精确排除指定背景色，保留装备边缘的偏紫部分
    增加容差范围到±20，并添加浅紫色排除逻辑
    
    掩码逻辑：
    - 255值: 背景区域(深紫色39212e、浅紫色20904f71、颜色103,53,79及其变化范围)
    - 0值: 前景区域(装备)
    
    Args:
        image: 输入图像（BGR格式）
        target_color_bgr: 目标背景色（BGR格式），默认为39212e的BGR值
        tolerance: 颜色容差范围（增加到±20）
        
    Returns:
        背景掩码（255为背景，0为前景）
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
        
        # 创建额外紫色掩码（103,53,79正负50）
        # 注意：103,53,79是RGB值，需要转换为BGR：79,53,103
        extra_purple_lower = np.array([
            max(0, 79 - 50),  # B: 79-50
            max(0, 53 - 50),  # G: 53-50
            max(0, 103 - 50)  # R: 103-50
        ])
        extra_purple_upper = np.array([
            min(255, 79 + 50),  # B: 79+50
            min(255, 53 + 50),  # G: 53+50
            min(255, 103 + 50)  # R: 103+50
        ])
        mask_extra_purple = cv2.inRange(image, extra_purple_lower, extra_purple_upper)
        
        # 合并背景掩码（深紫色、浅紫色和额外紫色都视为背景）
        mask_combined = cv2.bitwise_or(mask_bg, mask_light_purple)
        mask_combined = cv2.bitwise_or(mask_combined, mask_extra_purple)
        
        # 进一步降低形态学操作强度，最大程度减少对文字边缘的影响
        # 完全禁用腐蚀和膨胀操作，只保留最基本的颜色掩码
        # kernel_small = np.ones((2, 2), np.uint8)
        # mask_combined = cv2.erode(mask_combined, kernel_small, iterations=1)
        # mask_combined = cv2.dilate(mask_combined, kernel_small, iterations=1)
        
        # 应用非常轻微的高斯模糊，只平滑最细微的边缘
        mask_combined = cv2.GaussianBlur(mask_combined, (3, 3), 0.1)  # 大幅降低模糊强度
        
        # 二值化，确保只有0和255
        _, mask_combined = cv2.threshold(mask_combined, 200, 255, cv2.THRESH_BINARY)
        
        return mask_combined
    except Exception as e:
        print(f"[ERROR] 背景掩码创建失败: {e}")
        return np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)