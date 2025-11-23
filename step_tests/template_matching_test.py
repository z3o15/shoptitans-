#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板匹配测试程序
使用cv2.matchTemplate进行像素模板匹配和颜色相似度计算
"""

import os
import sys
import cv2
import numpy as np
from PIL import Image
import json
from datetime import datetime

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

def template_matching(template, scene):
    """
    使用cv2.matchTemplate进行模板匹配
    返回匹配相似度（0-100%）
    """
    try:
        # 确保模板不大于场景
        if template.shape[0] > scene.shape[0] or template.shape[1] > scene.shape[1]:
            # 如果模板大于场景，调整场景大小
            scene = cv2.resize(scene, (template.shape[1], template.shape[0]))
        
        # 转换为灰度图像进行匹配
        if len(template.shape) == 3:
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        else:
            template_gray = template
            
        if len(scene.shape) == 3:
            scene_gray = cv2.cvtColor(scene, cv2.COLOR_BGR2GRAY)
        else:
            scene_gray = scene
        
        # 使用多种匹配方法并取最佳结果
        methods = [
            cv2.TM_CCOEFF_NORMED,
            cv2.TM_CCORR_NORMED,
            cv2.TM_SQDIFF_NORMED
        ]
        
        best_score = 0
        best_method = ""
        
        for method in methods:
            result = cv2.matchTemplate(scene_gray, template_gray, method)
            
            if method == cv2.TM_SQDIFF_NORMED:
                # 对于SQDIFF，值越小越好
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                score = (1 - min_val) * 100  # 转换为0-100%
                if score > best_score:
                    best_score = score
                    best_method = "SQDIFF_NORMED"
            else:
                # 对于其他方法，值越大越好
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                score = max_val * 100  # 转换为0-100%
                if score > best_score:
                    best_score = score
                    best_method = "CCOEFF_NORMED" if method == cv2.TM_CCOEFF_NORMED else "CCORR_NORMED"
        
        return best_score, best_method
    except Exception as e:
        log_message("ERROR", f"模板匹配失败: {e}")
        return 0, ""

def create_background_mask(image, target_color_bgr=(46, 33, 46), tolerance=20):
    """
    创建背景掩码，精确排除指定背景色，保留装备边缘的偏紫部分
    增加容差范围到±20，并添加浅紫色排除逻辑
    
    掩码逻辑：
    - 255值: 背景区域(深紫色39212e、浅紫色20904f71及其变化范围)
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

def create_combined_mask(img1, img2, target_color_bgr=(46, 33, 46), tolerance=15):
    """
    为两张图像创建组合掩码，确保两张图像使用相同的掩码策略
    
    Args:
        img1: 第一张图像（BGR格式）
        img2: 第二张图像（BGR格式）
        target_color_bgr: 目标背景色（BGR格式）
        tolerance: 颜色容差范围
        
    Returns:
        组合前景掩码（255为前景，0为背景）
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

# 注释掉增强颜色相似度计算方法，只保留简单的欧氏距离方法
# def calculate_color_similarity_enhanced(img1, img2):
#     """
#     计算两张图片的颜色相似度（增强版本）
#     使用多种方法综合计算颜色相似度，更好地区分明显不同的颜色
#     返回相似度（0-1）
#     """
#     try:
#         # 调整图像大小为相同尺寸
#         target_size = (100, 100)  # 使用较小的尺寸提高性能
#         img1_resized = cv2.resize(img1, target_size)
#         img2_resized = cv2.resize(img2, target_size)
#
#         # 创建组合掩码，确保两张图像使用相同的掩码策略
#         combined_mask = create_combined_mask(img1_resized, img2_resized)
#
#         # 检查是否有足够的前景区域进行比较
#         if np.sum(combined_mask) < target_size[0] * target_size[1] * 0.1:  # 少于10%的前景区域
#             log_message("WARNING", "前景区域过小，颜色相似度可能不准确")
#
#         # 方法1: HSV全通道直方图比较（包含V通道）
#         hsv1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2HSV)
#         hsv2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2HSV)
#
#         # 计算HSV三通道直方图
#         hist_size = [30, 40, 30]  # H、S、V通道的bin数量
#         h_ranges = [0, 180]  # H通道范围
#         s_ranges = [0, 256]  # S通道范围
#         v_ranges = [0, 256]  # V通道范围
#         ranges = h_ranges + s_ranges + v_ranges
#
#         hist1_hsv = cv2.calcHist([hsv1], [0, 1, 2], combined_mask, hist_size, ranges)
#         hist2_hsv = cv2.calcHist([hsv2], [0, 1, 2], combined_mask, hist_size, ranges)
#
#         cv2.normalize(hist1_hsv, hist1_hsv, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
#         cv2.normalize(hist2_hsv, hist2_hsv, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
#
#         # 使用多种比较方法
#         correlation_hsv = cv2.compareHist(hist1_hsv, hist2_hsv, cv2.HISTCMP_CORREL)
#         chi_square_hsv = cv2.compareHist(hist1_hsv, hist2_hsv, cv2.HISTCMP_CHISQR)
#         intersection_hsv = cv2.compareHist(hist1_hsv, hist2_hsv, cv2.HISTCMP_INTERSECT)
#
#         # 方法2: LAB色彩空间比较（更接近人眼感知）
#         lab1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2LAB)
#         lab2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2LAB)
#
#         # 计算LAB三通道直方图
#         lab_hist_size = [30, 30, 30]  # L、A、B通道的bin数量
#         l_ranges = [0, 256]  # L通道范围
#         a_ranges = [0, 256]  # A通道范围
#         b_ranges = [0, 256]  # B通道范围
#         lab_ranges = l_ranges + a_ranges + b_ranges
#
#         hist1_lab = cv2.calcHist([lab1], [0, 1, 2], combined_mask, lab_hist_size, lab_ranges)
#         hist2_lab = cv2.calcHist([lab2], [0, 1, 2], combined_mask, lab_hist_size, lab_ranges)
#
#         cv2.normalize(hist1_lab, hist1_lab, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
#         cv2.normalize(hist2_lab, hist2_lab, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
#
#         correlation_lab = cv2.compareHist(hist1_lab, hist2_lab, cv2.HISTCMP_CORREL)
#
#         # 方法3: 直接像素颜色差异计算
#         # 只计算前景区域的平均颜色差异
#         fg_pixels1 = img1_resized[combined_mask > 0]
#         fg_pixels2 = img2_resized[combined_mask > 0]
#
#         if len(fg_pixels1) > 0 and len(fg_pixels2) > 0:
#             # 计算平均颜色
#             mean_color1 = np.mean(fg_pixels1, axis=0)
#             mean_color2 = np.mean(fg_pixels2, axis=0)
#
#             # 计算欧氏距离
#             color_distance = np.linalg.norm(mean_color1 - mean_color2)
#             # 转换为相似度（距离越小，相似度越高）
#             pixel_similarity = max(0, 1 - color_distance / 441.67)  # 441.67是最大可能距离(sqrt(255^2*3))
#         else:
#             pixel_similarity = 0
#
#         # 综合多种方法的相似度
#         # HSV相关性权重40%，LAB相关性权重30%，像素差异权重30%
#         hsv_similarity = max(0, min(1, (correlation_hsv + 1) / 2))
#         lab_similarity = max(0, min(1, (correlation_lab + 1) / 2))
#
#         combined_similarity = (
#             0.4 * hsv_similarity +
#             0.3 * lab_similarity +
#             0.3 * pixel_similarity
#         )
#
#         return combined_similarity
#     except Exception as e:
#         log_message("ERROR", f"增强颜色相似度计算失败: {e}")
#         return 0

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

def calculate_color_similarity_with_euclidean(img1, img2):
    """
    使用LAB色彩空间欧氏距离计算两张图片的颜色相似度
    使用指定的掩码策略排除背景色，只计算装备区域的颜色相似度
    LAB色彩空间更接近人类视觉感知
    返回相似度（0-1）
    """
    try:
        # 调整图像大小为相同尺寸
        target_size = (100, 100)  # 使用较小的尺寸提高性能
        img1_resized = cv2.resize(img1, target_size)
        img2_resized = cv2.resize(img2, target_size)
        
        # 使用指定的掩码策略
        log_message("DEBUG", "使用掩码策略计算颜色相似度（背景色39212e、浅紫色20904f71）")
        
        # 创建背景掩码（深紫色39212e和浅紫色20904f71）
        bg_mask1 = create_background_mask(img1_resized)
        bg_mask2 = create_background_mask(img2_resized)
        
        # 创建装备区域掩码（非背景区域）
        equipment_mask1 = cv2.bitwise_not(bg_mask1)
        equipment_mask2 = cv2.bitwise_not(bg_mask2)
        
        # 创建组合装备掩码（两张图片都有装备的区域）
        combined_equipment_mask = cv2.bitwise_and(equipment_mask1, equipment_mask2)
        
        # 检查是否有足够的装备区域进行比较
        equipment_pixels = np.sum(combined_equipment_mask == 255)
        total_pixels = target_size[0] * target_size[1]
        equipment_ratio = equipment_pixels / total_pixels
        
        if equipment_ratio < 0.05:  # 少于5%的装备区域
            log_message("WARNING", "装备区域过小，颜色相似度可能不准确")
        
        # 转换为LAB色彩空间（更接近人类视觉感知）
        lab1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2LAB)
        lab2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2LAB)
        
        # 获取装备区域的像素
        equipment_pixels1 = lab1[combined_equipment_mask == 255]
        equipment_pixels2 = lab2[combined_equipment_mask == 255]
        
        if len(equipment_pixels1) == 0 or len(equipment_pixels2) == 0:
            log_message("WARNING", "没有找到装备像素，返回相似度为0")
            return 0
        
        # 计算平均颜色
        mean_color1 = np.mean(equipment_pixels1, axis=0)
        mean_color2 = np.mean(equipment_pixels2, axis=0)
        
        # 计算LAB色彩空间的欧氏距离
        # LAB色彩空间的感知差异更符合人类视觉
        color_distance = np.linalg.norm(mean_color1 - mean_color2)
        
        # 转换为相似度（距离越小，相似度越高）
        # 增加最大距离阈值，使颜色相似度计算更加合理
        # LAB空间中，距离30已经是较大的差异，使用30作为最大距离
        max_distance = 30.0  # 增加最大距离，使相似度计算更加合理
        similarity = max(0, 1 - color_distance / max_distance)
        
        # 记录详细的颜色差异信息（用于调试）
        if color_distance > 10:  # 调整阈值，记录更多差异信息
            l_diff = mean_color1[0] - mean_color2[0]  # 亮度差异
            a_diff = mean_color1[1] - mean_color2[1]  # 红-绿差异
            b_diff = mean_color1[2] - mean_color2[2]  # 黄-蓝差异
            
            log_message("DEBUG", f"LAB颜色距离: {color_distance:.2f}")
            log_message("DEBUG", f"图片1平均颜色 (LAB): {mean_color1}")
            log_message("DEBUG", f"图片2平均颜色 (LAB): {mean_color2}")
            log_message("DEBUG", f"LAB差异: L{l_diff:+.2f}, A{a_diff:+.2f}, B{b_diff:+.2f}")
            log_message("DEBUG", f"颜色相似度: {similarity:.3f}")
        
        return similarity
    except Exception as e:
        log_message("ERROR", f"颜色相似度计算失败: {e}")
        return 0

# 注释掉标准颜色相似度计算方法，只保留简单的欧氏距离方法
# def calculate_color_similarity(img1, img2):
#     """
#     计算两张图片的颜色相似度（优化版本）
#     正确排除白色背景，只计算装备区域的颜色相似度
#     返回相似度（0-1）
#     """
#     try:
#         # 调整图像大小为相同尺寸
#         target_size = (100, 100)  # 使用较小的尺寸提高性能
#         img1_resized = cv2.resize(img1, target_size)
#         img2_resized = cv2.resize(img2, target_size)
#
#         # 创建白色背景掩码
#         white_mask1 = create_white_mask(img1_resized)
#         white_mask2 = create_white_mask(img2_resized)
#
#         # 创建装备区域掩码（非白色区域）
#         equipment_mask1 = cv2.bitwise_not(white_mask1)
#         equipment_mask2 = cv2.bitwise_not(white_mask2)
#
#         # 创建组合装备掩码（两张图片都有装备的区域）
#         combined_equipment_mask = cv2.bitwise_and(equipment_mask1, equipment_mask2)
#
#         # 检查是否有足够的装备区域进行比较
#         equipment_pixels = np.sum(combined_equipment_mask == 255)
#         total_pixels = target_size[0] * target_size[1]
#         equipment_ratio = equipment_pixels / total_pixels
#
#         if equipment_ratio < 0.05:  # 少于5%的装备区域
#             log_message("WARNING", "装备区域过小，颜色相似度可能不准确")
#
#         # 转换为HSV色彩空间
#         hsv1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2HSV)
#         hsv2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2HSV)
#
#         # 计算直方图（只计算装备区域，排除白色背景）
#         hist_size = [50, 60]  # H和S通道的bin数量
#         h_ranges = [0, 180]  # H通道范围
#         s_ranges = [0, 256]  # S通道范围
#         ranges = h_ranges + s_ranges
#
#         hist1 = cv2.calcHist([hsv1], [0, 1], combined_equipment_mask, hist_size, ranges)
#         hist2 = cv2.calcHist([hsv2], [0, 1], combined_equipment_mask, hist_size, ranges)
#
#         # 归一化直方图
#         cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
#         cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
#
#         # 计算相关性
#         correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
#
#         # 确保结果在0-1范围内
#         similarity = max(0, min(1, (correlation + 1) / 2))
#
#         return similarity
#     except Exception as e:
#         log_message("ERROR", f"颜色相似度计算失败: {e}")
#         return 0

# 注释掉区域分割相关方法，只保留简单的欧氏距离方法
# def segment_equipment_region(image):
#     """
#     分割装备区域，排除背景
#
#     Args:
#         image: 输入图像（BGR格式）
#
#     Returns:
#         装备区域掩码（255为装备，0为背景）
#     """
#     try:
#         # 转换为灰度图
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
#
#         # 高斯模糊
#         blurred = cv2.GaussianBlur(gray, (5, 5), 0)
#
#         # 自适应阈值分割
#         thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#                                      cv2.THRESH_BINARY_INV, 11, 2)
#
#         # 形态学操作，去除噪声并填充缺口
#         kernel = np.ones((3, 3), np.uint8)
#         # 开运算去除小噪声
#         opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
#         # 闭运算填充缺口
#         closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=2)
#
#         # 查找轮廓并保留最大轮廓（假设装备是最大物体）
#         contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
#         if contours:
#             # 找到最大轮廓
#             max_contour = max(contours, key=cv2.contourArea)
#
#             # 创建掩码
#             mask = np.zeros_like(gray)
#             cv2.fillPoly(mask, [max_contour], 255)
#
#             # 轻微膨胀，确保包含装备边缘
#             mask = cv2.dilate(mask, kernel, iterations=1)
#
#             return mask
#
#         # 如果没有找到轮廓，返回全白掩码（不排除任何区域）
#         return np.ones_like(gray) * 255
#
#     except Exception as e:
#         log_message("ERROR", f"装备区域分割失败: {e}")
#         return np.ones_like(image[:, :, 0]) * 255

# def calculate_color_similarity_with_region_segmentation(img1, img2):
#     """
#     使用区域分割计算颜色相似度（高级版本）
#     先分割装备区域，然后只在装备区域内计算颜色相似度
#     返回相似度（0-1）
#     """
#     try:
#         # 调整图像大小为相同尺寸
#         target_size = (100, 100)  # 使用较小的尺寸提高性能
#         img1_resized = cv2.resize(img1, target_size)
#         img2_resized = cv2.resize(img2, target_size)
#
#         # 分割装备区域
#         mask1 = segment_equipment_region(img1_resized)
#         mask2 = segment_equipment_region(img2_resized)
#
#         # 合并掩码，只计算两张图像都有装备的区域
#         combined_mask = cv2.bitwise_and(mask1, mask2)
#
#         # 检查是否有足够的装备区域进行比较
#         if np.sum(combined_mask) < target_size[0] * target_size[1] * 0.1:  # 少于10%的区域
#             log_message("WARNING", "装备区域过小，颜色相似度可能不准确")
#
#         # 转换为HSV色彩空间
#         hsv1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2HSV)
#         hsv2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2HSV)
#
#         # 计算直方图（只计算装备区域）
#         hist_size = [50, 60]  # H和S通道的bin数量
#         h_ranges = [0, 180]  # H通道范围
#         s_ranges = [0, 256]  # S通道范围
#         ranges = h_ranges + s_ranges
#
#         hist1 = cv2.calcHist([hsv1], [0, 1], combined_mask, hist_size, ranges)
#         hist2 = cv2.calcHist([hsv2], [0, 1], combined_mask, hist_size, ranges)
#
#         # 归一化直方图
#         cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
#         cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
#
#         # 计算相关性
#         correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
#
#         # 确保结果在0-1范围内
#         similarity = max(0, min(1, (correlation + 1) / 2))
#
#         return similarity
#     except Exception as e:
#         log_message("ERROR", f"区域分割颜色相似度计算失败: {e}")
#         return 0

def calculate_composite_score(template_score, color_score, template_weight=0.75, color_weight=0.25):
    """
    计算综合得分（简化版本）
    只使用模板匹配和颜色欧氏距离
    
    Args:
        template_score: 模板匹配得分（0-100）
        color_score: 颜色相似度得分（0-1）
        template_weight: 模板匹配权重（默认0.75，调整模板匹配权重）
        color_weight: 颜色相似度权重（默认0.25，调整颜色权重）
        
    Returns:
        综合得分（0-100）
    """
    # 将颜色相似度转换为0-100范围
    color_score_100 = color_score * 100
    
    # 计算加权平均
    composite_score = template_score * template_weight + color_score_100 * color_weight
    
    return composite_score

def run_template_matching_test(save_debug_images=False, generate_masked_images=True):
    """
    运行模板匹配测试（简化版本）
    使用模板匹配+掩码+颜色欧氏距离，按照指定的掩码策略处理背景色
    
    Args:
        save_debug_images: 是否保存调试图像（已禁用掩码图像生成）
        generate_masked_images: 是否生成掩码后的图像
    """
    log_message("INIT", "开始模板匹配测试（简化版本）")
    log_message("CONFIG", f"使用模板匹配+掩码+颜色欧氏距离（背景色39212e、浅紫色20904f71）")
    log_message("CONFIG", f"模板匹配权重: 75%, 颜色权重: 25%")
    log_message("CONFIG", f"保存调试图像: {save_debug_images}（已禁用掩码图像生成）")
    log_message("CONFIG", f"生成掩码后图像: {generate_masked_images}")
    
    # 设置路径（使用绝对路径，确保无论从哪个目录运行都能正确找到图像）
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    base_dir = os.path.join(project_root, "images/base_equipment_new")
    compare_dir = os.path.join(project_root, "images/cropped_equipment_transparent")
    output_dir = os.path.join(project_root, "images/template_matching_results")
    
    # 设置掩码后图像保存路径
    masked_output_dir = os.path.join(project_root, "images/test")
    base_masked_dir = os.path.join(masked_output_dir, "base_masked")
    compare_masked_dir = os.path.join(masked_output_dir, "compare_masked")
    masks_dir = os.path.join(masked_output_dir, "masks")
    
    # 检查目录是否存在
    if not os.path.exists(base_dir):
        log_message("ERROR", f"基准图像目录不存在: {base_dir}")
        return False
    
    if not os.path.exists(compare_dir):
        log_message("ERROR", f"对比图像目录不存在: {compare_dir}")
        return False
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建掩码后图像目录
    if generate_masked_images:
        os.makedirs(masked_output_dir, exist_ok=True)
        os.makedirs(base_masked_dir, exist_ok=True)
        os.makedirs(compare_masked_dir, exist_ok=True)
        os.makedirs(masks_dir, exist_ok=True)
        log_message("INIT", f"掩码后图像将保存到: {masked_output_dir}")
    
    # 禁用调试图像保存功能
    debug_dir = None
    if save_debug_images:
        debug_dir = os.path.join(output_dir, f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(debug_dir, exist_ok=True)
        log_message("INIT", f"调试图像将保存到: {debug_dir}（注意：掩码图像生成已禁用）")
    
    # 获取基准图像列表
    base_images = [f for f in os.listdir(base_dir)
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    # 获取对比图像列表
    compare_images = [f for f in os.listdir(compare_dir)
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    if not base_images:
        log_message("ERROR", "未找到基准图像")
        return False
    
    if not compare_images:
        log_message("ERROR", "未找到对比图像")
        return False
    
    log_message("INIT", f"找到 {len(base_images)} 个基准图像")
    log_message("INIT", f"找到 {len(compare_images)} 个对比图像")
    
    # 存储所有匹配结果
    all_results = []
    
    # 对每个对比图像进行匹配
    for compare_img in compare_images:
        log_message("MATCH", f"正在处理对比图像: {compare_img}")
        
        compare_path = os.path.join(compare_dir, compare_img)
        compare_image = load_image(compare_path)
        
        if compare_image is None:
            continue
        
        best_match = None
        best_score = 0
        
        # 与每个基准图像进行匹配
        for base_img in base_images:
            base_path = os.path.join(base_dir, base_img)
            base_image = load_image(base_path)
            
            if base_image is None:
                continue
            
            # 计算模板匹配相似度
            template_score, method = template_matching(base_image, compare_image)
            
            # 计算颜色相似度（使用欧氏距离方法）
            color_score = calculate_color_similarity_with_euclidean(base_image, compare_image)
           
            # 计算综合得分（简化版本）
            composite_score = calculate_composite_score(template_score, color_score)
            
            # 记录结果
            result = {
                'base_image': base_img,
                'compare_image': compare_img,
                'template_score': template_score,
                'template_method': method,
                'color_score': color_score,
                'composite_score': composite_score
            }
            
            all_results.append(result)
            
            # 更新最佳匹配
            if composite_score > best_score:
                best_score = composite_score
                best_match = result
        
        # 禁用掩码调试图像保存功能
        if best_match and debug_dir:
            try:
                base_path = os.path.join(base_dir, best_match['base_image'])
                base_image = load_image(base_path)
                
                if base_image is not None:
                    # 调整图像大小为相同尺寸以便比较
                    target_size = (100, 100)
                    base_resized = cv2.resize(base_image, target_size)
                    compare_resized = cv2.resize(compare_image, target_size)
                    
                    # 保存原始图像对比（不生成掩码）
                    cv2.imwrite(os.path.join(debug_dir, f"{compare_img}_base_original.png"), base_resized)
                    cv2.imwrite(os.path.join(debug_dir, f"{compare_img}_compare_original.png"), compare_resized)
                    
                    log_message("DEBUG", f"已保存原始对比图像到: {debug_dir}（掩码图像生成已禁用）")
            except Exception as e:
                log_message("ERROR", f"保存调试图像失败: {e}")
        
        # 输出最佳匹配结果
        if best_match:
            if best_match['composite_score'] > 94:
                log_message("RESULT",
                           f"对应装备: {best_match['base_image']} ← {best_match['compare_image']} "
                           f"(综合得分: {best_match['composite_score']:.2f}%, "
                           f"模板匹配: {best_match['template_score']:.2f}%, "
                           f"颜色相似度: {best_match['color_score']:.3f})")
            else:
                log_message("RESULT",
                           f"最佳匹配: {best_match['base_image']} → {best_match['compare_image']} "
                           f"(综合得分: {best_match['composite_score']:.2f}%, "
                           f"模板匹配: {best_match['template_score']:.2f}%, "
                           f"颜色相似度: {best_match['color_score']:.3f})")
    
    # 保存详细结果到JSON文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = os.path.join(output_dir, f"template_matching_results_{timestamp}.json")
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    # 生成汇总报告
    summary_file = os.path.join(output_dir, f"template_matching_summary_{timestamp}.txt")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("模板匹配测试结果汇总（简化版本）\n")
        f.write("=" * 50 + "\n")
        f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"基准图像数量: {len(base_images)}\n")
        f.write(f"对比图像数量: {len(compare_images)}\n")
        f.write(f"总匹配次数: {len(all_results)}\n")
        f.write(f"匹配方法: 模板匹配+掩码+颜色欧氏距离\n")
        f.write(f"掩码策略: 背景色39212e(±20)、浅紫色20904f71(±5)\n")
        f.write(f"保存调试图像: {save_debug_images}\n")
        # 添加权重配置信息
        f.write(f"模板匹配权重: 75% (0.75)\n")
        f.write(f"颜色相似度权重: 25% (0.25)\n")
        f.write(f"颜色空间: LAB色彩空间\n")
        f.write(f"最大颜色距离: 10.0\n")
        if debug_dir:
            f.write(f"调试图像目录: {debug_dir}\n")
        f.write("\n")
        
        # 按对比图像分组显示最佳匹配
        f.write("各对比图像的最佳匹配结果:\n")
        f.write("-" * 50 + "\n")
        
        for compare_img in compare_images:
            compare_results = [r for r in all_results if r['compare_image'] == compare_img]
            if compare_results:
                best = max(compare_results, key=lambda x: x['composite_score'])
                f.write(f"{compare_img}:\n")
                if best['composite_score'] > 94:
                    f.write(f"  对应装备: {best['base_image']}\n")
                else:
                    f.write(f"  最佳匹配: {best['base_image']}\n")
                f.write(f"  综合得分: {best['composite_score']:.2f}%\n")
                f.write(f"  模板匹配: {best['template_score']:.2f}% ({best['template_method']})\n")
                f.write(f"  颜色相似度: {best['color_score']:.3f}\n\n")
    
    # 生成掩码后的图像
    if generate_masked_images:
        log_message("PROCESS", "开始生成掩码后的图像...")
        
        # 处理基准图像
        for base_img in base_images:
            base_path = os.path.join(base_dir, base_img)
            log_message("DEBUG", f"加载基准图像: {base_path}")
            base_image = load_image(base_path)
            
            if base_image is None:
                log_message("ERROR", f"无法加载基准图像: {base_path}")
                continue
            
            # 创建背景掩码
            log_message("DEBUG", f"为 {base_img} 创建背景掩码")
            mask_bg = create_background_mask(base_image)
            
            # 应用掩码到图像
            log_message("DEBUG", f"为 {base_img} 应用掩码到图像")
            masked_image = apply_mask_to_image(base_image, mask_bg)
            
            # 保存结果
            output_path = os.path.join(base_masked_dir, base_img)
            mask_path = os.path.join(masks_dir, f"mask_{base_img}")
            
            log_message("DEBUG", f"准备保存 {base_img}: 掩码图像={output_path}, 掩码文件={mask_path}")
            
            # 检查目录是否存在
            if not os.path.exists(base_masked_dir):
                log_message("ERROR", f"目录不存在: {base_masked_dir}")
                os.makedirs(base_masked_dir, exist_ok=True)
            
            if not os.path.exists(masks_dir):
                log_message("ERROR", f"目录不存在: {masks_dir}")
                os.makedirs(masks_dir, exist_ok=True)
            
            # 保存文件并检查结果
            try:
                log_message("DEBUG", f"掩码图像形状: {masked_image.shape}, 数据类型: {masked_image.dtype}")
                log_message("DEBUG", f"掩码形状: {mask_bg.shape}, 数据类型: {mask_bg.dtype}")
                
                result1 = cv2.imwrite(output_path, masked_image)
                log_message("DEBUG", f"cv2.imwrite 掩码图像返回值: {result1}")
                
                if not result1:
                    log_message("ERROR", f"保存基准掩码图像失败: {output_path}")
                    # 尝试使用PIL作为备用方案
                    try:
                        # 转换BGR到RGB
                        if len(masked_image.shape) == 3 and masked_image.shape[2] == 3:
                            rgb_image = cv2.cvtColor(masked_image, cv2.COLOR_BGR2RGB)
                            pil_img = Image.fromarray(rgb_image)
                        else:
                            pil_img = Image.fromarray(masked_image)
                        pil_img.save(output_path)
                        log_message("SUCCESS", f"使用PIL成功保存基准掩码图像: {output_path}")
                        result1 = True
                    except Exception as pil_e:
                        log_message("ERROR", f"PIL保存也失败: {str(pil_e)}")
                else:
                    log_message("SAVE", f"成功保存基准掩码图像: {output_path}")
                
                result2 = cv2.imwrite(mask_path, mask_bg)
                log_message("DEBUG", f"cv2.imwrite 掩码返回值: {result2}")
                
                if not result2:
                    log_message("ERROR", f"保存掩码文件失败: {mask_path}")
                    # 尝试使用PIL作为备用方案
                    try:
                        pil_mask = Image.fromarray(mask_bg)
                        pil_mask.save(mask_path)
                        log_message("SUCCESS", f"使用PIL成功保存掩码文件: {mask_path}")
                        result2 = True
                    except Exception as pil_e:
                        log_message("ERROR", f"PIL保存掩码也失败: {str(pil_e)}")
                else:
                    log_message("SAVE", f"成功保存掩码文件: {mask_path}")
                    
                # 验证文件是否真的存在
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    log_message("DEBUG", f"确认文件存在: {output_path}, 大小: {file_size} 字节")
                else:
                    log_message("ERROR", f"文件不存在: {output_path}")
                    
                if os.path.exists(mask_path):
                    file_size = os.path.getsize(mask_path)
                    log_message("DEBUG", f"确认掩码文件存在: {mask_path}, 大小: {file_size} 字节")
                else:
                    log_message("ERROR", f"掩码文件不存在: {mask_path}")
                    
            except Exception as e:
                log_message("ERROR", f"保存 {base_img} 时发生异常: {e}")
                import traceback
                traceback.print_exc()
        
        # 处理对比图像
        for compare_img in compare_images:
            compare_path = os.path.join(compare_dir, compare_img)
            log_message("DEBUG", f"加载对比图像: {compare_path}")
            compare_image = load_image(compare_path)
            
            if compare_image is None:
                log_message("ERROR", f"无法加载对比图像: {compare_path}")
                continue
            
            # 创建背景掩码
            log_message("DEBUG", f"为 {compare_img} 创建背景掩码")
            mask_bg = create_background_mask(compare_image)
            
            # 应用掩码到图像
            log_message("DEBUG", f"为 {compare_img} 应用掩码到图像")
            masked_image = apply_mask_to_image(compare_image, mask_bg)
            
            # 保存结果
            output_path = os.path.join(compare_masked_dir, compare_img)
            mask_path = os.path.join(masks_dir, f"mask_{compare_img}")
            
            log_message("DEBUG", f"准备保存 {compare_img}: 掩码图像={output_path}, 掩码文件={mask_path}")
            
            # 检查目录是否存在
            if not os.path.exists(compare_masked_dir):
                log_message("ERROR", f"目录不存在: {compare_masked_dir}")
                os.makedirs(compare_masked_dir, exist_ok=True)
            
            # 保存文件并检查结果
            try:
                log_message("DEBUG", f"对比掩码图像形状: {masked_image.shape}, 数据类型: {masked_image.dtype}")
                log_message("DEBUG", f"对比掩码形状: {mask_bg.shape}, 数据类型: {mask_bg.dtype}")
                
                result1 = cv2.imwrite(output_path, masked_image)
                log_message("DEBUG", f"cv2.imwrite 对比掩码图像返回值: {result1}")
                
                if not result1:
                    log_message("ERROR", f"保存对比掩码图像失败: {output_path}")
                    # 尝试使用PIL作为备用方案
                    try:
                        # 转换BGR到RGB
                        if len(masked_image.shape) == 3 and masked_image.shape[2] == 3:
                            rgb_image = cv2.cvtColor(masked_image, cv2.COLOR_BGR2RGB)
                            pil_img = Image.fromarray(rgb_image)
                        else:
                            pil_img = Image.fromarray(masked_image)
                        pil_img.save(output_path)
                        log_message("SUCCESS", f"使用PIL成功保存对比掩码图像: {output_path}")
                        result1 = True
                    except Exception as pil_e:
                        log_message("ERROR", f"PIL保存也失败: {str(pil_e)}")
                else:
                    log_message("SAVE", f"成功保存对比掩码图像: {output_path}")
                
                result2 = cv2.imwrite(mask_path, mask_bg)
                log_message("DEBUG", f"cv2.imwrite 对比掩码返回值: {result2}")
                
                if not result2:
                    log_message("ERROR", f"保存掩码文件失败: {mask_path}")
                    # 尝试使用PIL作为备用方案
                    try:
                        pil_mask = Image.fromarray(mask_bg)
                        pil_mask.save(mask_path)
                        log_message("SUCCESS", f"使用PIL成功保存掩码文件: {mask_path}")
                        result2 = True
                    except Exception as pil_e:
                        log_message("ERROR", f"PIL保存掩码也失败: {str(pil_e)}")
                else:
                    log_message("SAVE", f"成功保存掩码文件: {mask_path}")
                    
                # 验证文件是否真的存在
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    log_message("DEBUG", f"确认文件存在: {output_path}, 大小: {file_size} 字节")
                else:
                    log_message("ERROR", f"文件不存在: {output_path}")
                    
                if os.path.exists(mask_path):
                    file_size = os.path.getsize(mask_path)
                    log_message("DEBUG", f"确认掩码文件存在: {mask_path}, 大小: {file_size} 字节")
                else:
                    log_message("ERROR", f"掩码文件不存在: {mask_path}")
                    
            except Exception as e:
                log_message("ERROR", f"保存 {compare_img} 时发生异常: {e}")
                import traceback
                traceback.print_exc()
        
        log_message("RESULT", f"掩码后的图片已保存到: {masked_output_dir}")
        log_message("RESULT", f"  - 基准图像掩码后: {base_masked_dir}")
        log_message("RESULT", f"  - 对比图像掩码后: {compare_masked_dir}")
        log_message("RESULT", f"  - 掩码图像: {masks_dir}")
    
    log_message("RESULT", f"测试完成，结果已保存到: {output_dir}")
    log_message("RESULT", f"详细结果: {result_file}")
    log_message("RESULT", f"汇总报告: {summary_file}")
    
    return True

def main():
    """主函数"""
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='模板匹配测试程序（简化版本）')
    parser.add_argument('--save-debug-images', action='store_true',
                       help='保存调试图像（掩码等）')
    parser.add_argument('--no-masked-images', action='store_true',
                       help='不生成掩码后的图像')
    
    args = parser.parse_args()
    
    log_message("INIT", "模板匹配测试程序（简化版本）")
    log_message("CONFIG", f"使用模板匹配+掩码+颜色欧氏距离")
    log_message("CONFIG", f"掩码策略: 背景色39212e(±20)、浅紫色20904f71(±5)")
    log_message("CONFIG", f"模板匹配权重: 75%, 颜色权重: 25%")
    
    try:
        # 运行简化方法
        generate_masked = not args.no_masked_images
        success = run_template_matching_test(save_debug_images=args.save_debug_images,
                                        generate_masked_images=generate_masked)
        
        if success:
            log_message("INIT", "测试成功完成")
        else:
            log_message("ERROR", "测试失败")
    except KeyboardInterrupt:
        log_message("INIT", "程序被用户中断")
    except Exception as e:
        log_message("ERROR", f"发生错误: {e}")

if __name__ == "__main__":
    main()
