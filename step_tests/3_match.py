#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤3：装备图片匹配功能测试
从 3_step2_cut_screenshots.py 提取的图像匹配模块
"""

import os
import sys
import subprocess
from datetime import datetime
import json
import cv2
import numpy as np
from PIL import Image

# 添加项目根目录到Python路径，以便能够导入src模块
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入新的统一日志管理器
try:
    from src.unified_logger import get_unified_logger
    LOGGER_AVAILABLE = True
except ImportError:
    try:
        from unified_logger import get_unified_logger
        LOGGER_AVAILABLE = True
    except ImportError:
        LOGGER_AVAILABLE = False
        print("⚠️ 统一日志管理器不可用，使用默认输出")

# 导入统一的背景掩码函数
try:
    from src.utils.background_mask import create_background_mask
except ImportError:
    try:
        from utils.background_mask import create_background_mask
    except ImportError:
        if LOGGER_AVAILABLE:
            logger = get_step_logger()
            logger.log_warning("无法导入统一的背景掩码函数，将使用本地定义")
        else:
            print("⚠️ 无法导入统一的背景掩码函数，将使用本地定义")
        # 如果无法导入，定义一个本地函数作为后备
        def create_background_mask(image, target_color_bgr=(46, 33, 46), tolerance=20):
            """本地后备的背景掩码函数"""
            try:
                # 创建颜色范围掩码
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
                
                mask_bg = cv2.inRange(image, lower_bound, upper_bound)
                
                # 创建浅紫色掩码
                light_purple_lower = np.array([241, 240, 241])
                light_purple_upper = np.array([247, 250, 247])
                mask_light_purple = cv2.inRange(image, light_purple_lower, light_purple_upper)
                
                # 创建第三种颜色掩码
                third_color_lower = np.array([45, 30, 35])
                third_color_upper = np.array([65, 40, 50])
                mask_third_color = cv2.inRange(image, third_color_lower, third_color_upper)
                
                # 合并掩码
                mask_combined = cv2.bitwise_or(mask_bg, mask_light_purple)
                mask_combined = cv2.bitwise_or(mask_combined, mask_third_color)
                
                # 应用轻微高斯模糊
                mask_combined = cv2.GaussianBlur(mask_combined, (3, 3), 0.5)
                
                # 二值化
                _, mask_combined = cv2.threshold(mask_combined, 200, 255, cv2.THRESH_BINARY)
                
                return mask_combined
            except Exception as e:
                if LOGGER_AVAILABLE:
                    logger.log_error(f"背景掩码创建失败: {e}")
                else:
                    log_message("ERROR", f"背景掩码创建失败: {e}")
                return np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)

def check_dependencies():
    """检查依赖是否已安装"""
    required_packages = ['cv2', 'PIL', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            elif package == 'numpy':
                import numpy
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"缺少依赖包: {', '.join(missing_packages)}")
        print("正在安装依赖...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            return True
        except subprocess.CalledProcessError:
            print("依赖安装失败，请手动运行: pip install -r requirements.txt")
            return False
    
    return True

def log_message(tag, message):
    """统一日志输出格式"""
    if LOGGER_AVAILABLE:
        logger = get_step_logger()
        if tag == "ERROR":
            logger.log_error(message)
        elif tag == "WARNING":
            logger.log_warning(message)
        elif tag == "RESULT":
            logger.log_info(message)
        else:
            logger.log_info(f"[{tag}] {message}")
    else:
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
    使用cv2.TM_CCOEFF_NORMED进行模板匹配
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
        
        # 只使用TM_CCOEFF_NORMED方法
        result = cv2.matchTemplate(scene_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        score = max_val * 100  # 转换为0-100%
        
        return score, "TM_CCOEFF_NORMED"
    except Exception as e:
        log_message("ERROR", f"模板匹配失败: {e}")
        return 0, ""

# create_background_mask函数已移至src/utils/background_mask.py，现在从那里导入

def apply_mask_to_image(image, mask):
    """
    将掩码应用到图像，生成掩码后的图像
    背景区域变为白色，前景区域（装备+紫色圆形）保持原色
    
    掩码逻辑（与create_background_mask一致）：
    - 255值: 前景区域(装备本体 + 圆圈紫色区域，应该被保留用于匹配)
    - 0值: 背景区域(矩形整体背景，外圈紫色以外区域，应该被忽略)
    """
    try:
        # 创建白色背景
        white_bg = np.ones_like(image) * 255
        
        # 确保掩码是二值的（0和255）
        mask_binary = np.where(mask > 127, 255, 0).astype(np.uint8)
        
        # 将前景区域（装备+紫色圆形）复制到白色背景上
        # 掩码中255是装备+紫色圆形，0是背景（与create_background_mask的输出一致）
        result = np.where(mask_binary[:, :, np.newaxis] == 255, image, white_bg)
        
        return result
    except Exception as e:
        log_message("ERROR", f"掩码应用失败: {e}")
        return image

def calculate_color_similarity_with_euclidean(img1, img2, output_dir=None):
    """
    使用LAB色彩空间欧氏距离计算两张图片的颜色相似度
    使用圆形掩码策略：在矩形中心画一个半径为55的圆，圆内紫色去除，圆外黑色
    改进：使用像素级欧氏距离平均，而不是整图平均，提高稳健性
    只计算圆形区域内非紫色装备本体的颜色相似度
    LAB色彩空间更接近人类视觉感知
    返回相似度（0-1）
    
    Args:
        img1: 第一张图像
        img2: 第二张图像
        output_dir: 输出目录，用于保存掩码图像进行验证
    """
    try:
        # 调整图像大小为相同尺寸（保持116*116）
        target_size = (116, 116)  # 保持原始尺寸
        img1_resized = cv2.resize(img1, target_size)
        img2_resized = cv2.resize(img2, target_size)
        
        # 使用圆形掩码策略：在矩形中心画一个半径为55的圆，圆内紫色去除，圆外黑色
        log_message("DEBUG", "使用改进的圆形掩码策略计算颜色相似度（像素级欧氏距离）")
        
        # 创建装备本体掩码（圆形区域内非紫色部分）
        equipment_mask1 = create_equipment_only_mask(img1_resized)
        equipment_mask2 = create_equipment_only_mask(img2_resized)
        
        # 创建组合装备掩码（两张图片都有装备的区域）
        combined_equipment_mask = cv2.bitwise_and(equipment_mask1, equipment_mask2)
        
        # 保存装备本体掩码图像用于验证
        if output_dir:
            equipment_mask_dir = os.path.join(output_dir, "equipment_masks")
            os.makedirs(equipment_mask_dir, exist_ok=True)
            
            # 生成唯一文件名
            import time
            timestamp = str(int(time.time()))[-6:]  # 取时间戳后6位
            
            cv2.imwrite(os.path.join(equipment_mask_dir, f"equipment_mask1_{timestamp}.png"), equipment_mask1)
            cv2.imwrite(os.path.join(equipment_mask_dir, f"equipment_mask2_{timestamp}.png"), equipment_mask2)
            cv2.imwrite(os.path.join(equipment_mask_dir, f"combined_equipment_mask_{timestamp}.png"), combined_equipment_mask)
            
            # 保存掩码后的图像用于验证
            img1_masked = cv2.bitwise_and(img1_resized, img1_resized, mask=equipment_mask1)
            img2_masked = cv2.bitwise_and(img2_resized, img2_resized, mask=equipment_mask2)
            cv2.imwrite(os.path.join(equipment_mask_dir, f"img1_equipment_only_{timestamp}.png"), img1_masked)
            cv2.imwrite(os.path.join(equipment_mask_dir, f"img2_equipment_only_{timestamp}.png"), img2_masked)
            
            log_message("DEBUG", f"装备本体掩码已保存到 {equipment_mask_dir}/ 目录用于验证")
        
        # 检查是否有足够的装备区域进行比较
        equipment_pixels = np.sum(combined_equipment_mask == 255)
        total_pixels = target_size[0] * target_size[1]
        equipment_ratio = equipment_pixels / total_pixels
        
        if equipment_ratio < 0.05:  # 少于5%的装备区域
            log_message("WARNING", "装备区域过小，颜色相似度可能不准确")
        
        # 转换为LAB色彩空间（更接近人类视觉感知）
        lab1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2LAB)
        lab2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2LAB)
        
        # 获取装备区域的像素坐标
        equipment_coords = np.where(combined_equipment_mask == 255)
        
        if len(equipment_coords[0]) == 0:
            log_message("WARNING", "没有找到装备像素，返回相似度为0")
            return 0
        
        # 改进：计算像素级欧氏距离平均，而不是整图平均
        pixel_distances = []
        for y, x in zip(equipment_coords[0], equipment_coords[1]):
            pixel1 = lab1[y, x]
            pixel2 = lab2[y, x]
            pixel_distance = np.linalg.norm(pixel1 - pixel2)
            pixel_distances.append(pixel_distance)
        
        # 计算平均像素距离
        avg_pixel_distance = np.mean(pixel_distances)
        
        # 添加诊断信息
        log_message("DEBUG", f"装备像素数量: {len(pixel_distances)}")
        log_message("DEBUG", f"平均像素距离: {avg_pixel_distance:.2f}")
        log_message("DEBUG", f"距离标准差: {np.std(pixel_distances):.2f}")
        
        # 转换为相似度（距离越小，相似度越高）
        # 调整最大距离阈值为300，适应LAB空间的大距离
        max_distance = 300.0  # 调整最大距离，适应LAB空间的实际距离范围
        similarity = max(0, 1 - avg_pixel_distance / max_distance)
        
        # 记录详细的颜色差异信息（用于调试）
        if avg_pixel_distance > 7.5:  # 调整阈值，记录更多差异信息
            log_message("DEBUG", f"平均LAB颜色距离: {avg_pixel_distance:.2f}")
            log_message("DEBUG", f"颜色相似度: {similarity:.3f}")
        
        return similarity
    except Exception as e:
        log_message("ERROR", f"颜色相似度计算失败: {e}")
        return 0

def create_equipment_only_mask(image, tolerance=23):
    """
    创建装备本体掩码，使用圆形掩码策略
    在矩形中心画一个半径为55的圆作为范围控制，圆内紫色去除保留装备，圆外全部为黑色
    
    掩码逻辑：
    - 255值: 圆形区域内非紫色的装备本体（白色）
    - 0值: 圆形区域外（黑色）和圆形区域内紫色部分（黑色）
    
    Args:
        image: 输入图像（BGR格式）
        tolerance: 颜色容差范围
        
    Returns:
        装备本体掩码（255为圆形区域内非紫色装备，0为其他区域）
    """
    try:
        # 确保图像尺寸为116x116
        height, width = image.shape[:2]
        if height != 116 or width != 116:
            # 调整图像大小为116x116
            image = cv2.resize(image, (116, 116))
            height, width = 116, 116
        
        # 修复：调整圆形半径，确保不超出图像边界
        center_x, center_y = width // 2, height // 2
        max_radius = min(center_x, center_y)  # 确保圆不超出边界
        radius = min(55, max_radius)  # 使用55或更小的半径，确保安全边界
        
        # 添加诊断日志
        log_message("DEBUG", f"圆形掩码参数: 图像尺寸={width}x{height}, 中心=({center_x},{center_y}), 半径={radius}")
        log_message("DEBUG", f"圆的边界: x=[{center_x-radius},{center_x+radius}], y=[{center_y-radius},{center_y+radius}]")
        
        # 创建空白掩码
        circle_mask = np.zeros((height, width), dtype=np.uint8)
        
        # 在掩码上画圆（255表示圆内区域）
        cv2.circle(circle_mask, (center_x, center_y), radius, 255, -1)
        
        # 创建深紫色掩码（39212e范围，调整容差）
        lower_bound = np.array([
            max(0, 46 - tolerance),
            max(0, 33 - tolerance),
            max(0, 46 - tolerance)
        ])
        upper_bound = np.array([
            min(255, 46 + tolerance),
            min(255, 33 + tolerance),
            min(255, 46 + tolerance)
        ])
        mask_deep_purple = cv2.inRange(image, lower_bound, upper_bound)
        
        # 创建浅紫色掩码（20904f71范围，调整容差）
        light_purple_lower = np.array([242, 241, 242])  # 调整浅紫色范围，减少容差
        light_purple_upper = np.array([246, 249, 246])
        mask_light_purple = cv2.inRange(image, light_purple_lower, light_purple_upper)
        
        # 创建第三种颜色掩码（57,33,45范围，调整容差范围）
        third_color_lower = np.array([45, 30, 35])  # 调整第三种紫色范围，减少跨度
        third_color_upper = np.array([65, 40, 50])
        mask_third_color = cv2.inRange(image, third_color_lower, third_color_upper)
        
        # 添加诊断日志
        purple_pixel_count = np.sum(mask_deep_purple > 0) + np.sum(mask_light_purple > 0) + np.sum(mask_third_color > 0)
        total_pixels = image.shape[0] * image.shape[1]
        purple_ratio = purple_pixel_count / total_pixels
        log_message("DEBUG", f"装备掩码紫色像素统计: {purple_pixel_count}/{total_pixels} ({purple_ratio:.2%})")
        
        # 合并所有紫色区域掩码
        purple_mask = cv2.bitwise_or(cv2.bitwise_or(mask_deep_purple, mask_light_purple), mask_third_color)
        
        # 应用圆形掩码：只保留圆形区域内的紫色
        purple_in_circle = cv2.bitwise_and(purple_mask, circle_mask)
        
        # 创建最终装备掩码：
        # 1. 圆形区域内非紫色部分为255（白色）
        # 2. 圆形区域外全部为0（黑色）
        # 3. 圆形区域内紫色部分为0（黑色）
        
        # 先创建圆形区域掩码（255表示圆内，0表示圆外）
        equipment_mask = circle_mask.copy()
        
        # 从圆形区域中去除紫色部分（将紫色部分设为0）
        equipment_mask = cv2.bitwise_and(equipment_mask, cv2.bitwise_not(purple_in_circle))
        
        # 形态学处理，去除噪点
        kernel = np.ones((3, 3), np.uint8)
        equipment_mask = cv2.morphologyEx(equipment_mask, cv2.MORPH_OPEN, kernel)
        equipment_mask = cv2.morphologyEx(equipment_mask, cv2.MORPH_CLOSE, kernel)
        
        # 轻微羽化处理
        equipment_mask = cv2.GaussianBlur(equipment_mask.astype(np.float32), (3, 3), 0.5)
        
        # 二值化，确保只有0和255
        _, equipment_mask = cv2.threshold(equipment_mask, 200, 255, cv2.THRESH_BINARY)
        
        return equipment_mask.astype(np.uint8)
    except Exception as e:
        log_message("ERROR", f"装备本体掩码创建失败: {e}")
        return np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)

def calculate_composite_score(template_score, color_score, template_weight=0.65, color_weight=0.35):
    """
    计算综合得分（改进版本）
    只使用模板匹配和颜色欧氏距离
    调整权重，增加模板匹配的重要性，减少颜色相似度的影响
    
    Args:
        template_score: 模板匹配得分（0-100）
        color_score: 颜色相似度得分（0-1）
        template_weight: 模板匹配权重（默认0.65，增加模板匹配权重）
        color_weight: 颜色相似度权重（默认0.35，减少颜色权重）
        
    Returns:
        综合得分（0-100）
    """
    # 将颜色相似度转换为0-100范围
    color_score_100 = color_score * 100
    
    # 计算加权平均
    composite_score = template_score * template_weight + color_score_100 * color_weight
    
    # 添加诊断日志
    log_message("DEBUG", f"综合得分计算: 模板={template_score:.2f}×{template_weight:.2f} + 颜色={color_score:.3f}×{color_weight:.2f} = {composite_score:.2f}")
    
    return composite_score

def match_equipment_images(base_dir, compare_dir, output_dir):
    """
    执行装备图片匹配（两阶段匹配策略）
    第一阶段：模板匹配筛选候选
    第二阶段：颜色匹配区分高分候选
    
    Args:
        base_dir: 基准图像目录
        compare_dir: 对比图像目录
        output_dir: 输出目录
        
    Returns:
        匹配结果列表
    """
    log_message("INIT", "开始装备图片匹配（两阶段匹配策略）")
    log_message("CONFIG", f"阶段1：TM_CCOEFF_NORMED模板匹配筛选候选")
    log_message("CONFIG", f"阶段2：颜色欧氏距离区分高分候选（仅对多个高分候选使用）")
    
    # 检查目录是否存在
    if not os.path.exists(base_dir):
        log_message("ERROR", f"基准图像目录不存在: {base_dir}")
        return []
    
    if not os.path.exists(compare_dir):
        log_message("ERROR", f"对比图像目录不存在: {compare_dir}")
        return []
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建掩码图像保存目录
    masked_output_dir = os.path.join(output_dir, "masked_images")
    os.makedirs(masked_output_dir, exist_ok=True)
    
    # 创建对比图像保存目录
    comparison_output_dir = os.path.join(output_dir, "comparisons")
    os.makedirs(comparison_output_dir, exist_ok=True)
    
    # 创建装备掩码保存目录
    equipment_mask_dir = os.path.join(output_dir, "equipment_masks")
    os.makedirs(equipment_mask_dir, exist_ok=True)
    
    # 获取基准图像列表
    base_images = [f for f in os.listdir(base_dir)
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    # 获取对比图像列表
    compare_images = [f for f in os.listdir(compare_dir)
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    if not base_images:
        log_message("ERROR", "未找到基准图像")
        return []
    
    if not compare_images:
        log_message("ERROR", "未找到对比图像")
        return []
    
    log_message("INIT", f"找到 {len(base_images)} 个基准图像")
    log_message("INIT", f"找到 {len(compare_images)} 个对比图像")
    log_message("INIT", f"掩码图像将保存到: {masked_output_dir}")
    log_message("INIT", f"对比图像将保存到: {comparison_output_dir}")
    log_message("INIT", f"装备掩码图像将保存到: {equipment_mask_dir}")
    
    # 存储所有匹配结果
    all_results = []
    
    # 对每个对比图像进行匹配
    for compare_img in compare_images:
        log_message("MATCH", f"正在处理对比图像: {compare_img}")
        
        compare_path = os.path.join(compare_dir, compare_img)
        compare_image = load_image(compare_path)
        
        if compare_image is None:
            continue
        
        # 为对比图像创建掩码并保存
        compare_mask = create_background_mask(compare_image)
        compare_masked_image = apply_mask_to_image(compare_image, compare_mask)
        
        # 保存对比图像的掩码和掩码后图像
        compare_mask_path = os.path.join(masked_output_dir, f"mask_{compare_img}")
        compare_masked_path = os.path.join(masked_output_dir, f"masked_{compare_img}")
        
        cv2.imwrite(compare_mask_path, compare_mask)
        cv2.imwrite(compare_masked_path, compare_masked_image)
        
        log_message("DEBUG", f"已保存对比图像掩码: {compare_mask_path}")
        log_message("DEBUG", f"已保存对比图像掩码后图像: {compare_masked_path}")
        
        # 阶段1：对所有基准图像进行模板匹配
        template_candidates = []
        for base_img in base_images:
            base_path = os.path.join(base_dir, base_img)
            base_image = load_image(base_path)
            
            if base_image is None:
                continue
            
            # 计算模板匹配相似度
            template_score, method = template_matching(base_image, compare_image)
            
            # 记录模板匹配候选
            candidate = {
                'base_image': base_img,
                'base_image_obj': base_image,
                'template_score': template_score,
                'template_method': method
            }
            template_candidates.append(candidate)
            
            log_message("DEBUG", f"模板匹配 {base_img}: {template_score:.2f}%")
        
        # 按模板匹配得分排序
        template_candidates.sort(key=lambda x: x['template_score'], reverse=True)
        
        # 确定是否需要颜色匹配
        template_threshold = 70.0  # 模板匹配阈值
        high_score_candidates = [c for c in template_candidates if c['template_score'] >= template_threshold]
        
        log_message("DEBUG", f"模板匹配阈值: {template_threshold}%, 高分候选数量: {len(high_score_candidates)}")
        
        # 阶段2：对高分候选进行颜色匹配
        final_candidates = []
        for candidate in high_score_candidates:
            base_img = candidate['base_image']
            base_image = candidate['base_image_obj']
            
            # 为基准图像创建掩码并保存
            base_mask = create_background_mask(base_image)
            base_masked_image = apply_mask_to_image(base_image, base_mask)
            
            # 保存基准图像的掩码和掩码后图像
            base_mask_path = os.path.join(masked_output_dir, f"mask_{base_img}")
            base_masked_path = os.path.join(masked_output_dir, f"masked_{base_img}")
            
            cv2.imwrite(base_mask_path, base_mask)
            cv2.imwrite(base_masked_path, base_masked_image)
            
            log_message("DEBUG", f"已保存基准图像掩码: {base_mask_path}")
            log_message("DEBUG", f"已保存基准图像掩码后图像: {base_masked_path}")
            
            # 计算颜色相似度（使用欧氏距离方法）
            color_score = calculate_color_similarity_with_euclidean(base_image, compare_image, output_dir)
            
            # 计算综合得分
            composite_score = calculate_composite_score(candidate['template_score'], color_score)
            
            # 记录最终候选
            final_candidate = {
                'base_image': base_img,
                'base_image_obj': base_image,
                'base_masked_image': base_masked_image,
                'base_mask': base_mask,
                'template_score': candidate['template_score'],
                'template_method': candidate['template_method'],
                'color_score': color_score,
                'composite_score': composite_score
            }
            final_candidates.append(final_candidate)
            
            # 记录结果到总结果列表
            result = {
                'base_image': base_img,
                'compare_image': compare_img,
                'template_score': candidate['template_score'],
                'template_method': candidate['template_method'],
                'color_score': color_score,
                'composite_score': composite_score
            }
            all_results.append(result)
            
            log_message("DEBUG", f"颜色匹配 {base_img}: 颜色相似度={color_score:.3f}, 综合得分={composite_score:.2f}%")
        
        # 如果没有高分候选，选择模板匹配最高的
        if not final_candidates and template_candidates:
            best_template = template_candidates[0]
            log_message("DEBUG", f"无高分候选，选择模板匹配最高: {best_template['base_image']} ({best_template['template_score']:.2f}%)")
            
            # 为最佳模板匹配创建掩码和图像
            base_image = best_template['base_image_obj']
            base_mask = create_background_mask(base_image)
            base_masked_image = apply_mask_to_image(base_image, base_mask)
            
            base_mask_path = os.path.join(masked_output_dir, f"mask_{best_template['base_image']}")
            base_masked_path = os.path.join(masked_output_dir, f"masked_{best_template['base_image']}")
            
            cv2.imwrite(base_mask_path, base_mask)
            cv2.imwrite(base_masked_path, base_masked_image)
            
            # 创建最终候选（无颜色匹配）
            final_candidate = {
                'base_image': best_template['base_image'],
                'base_image_obj': base_image,
                'base_masked_image': base_masked_image,
                'base_mask': base_mask,
                'template_score': best_template['template_score'],
                'template_method': best_template['template_method'],
                'color_score': 0.0,  # 无颜色匹配
                'composite_score': best_template['template_score']  # 仅使用模板匹配得分
            }
            final_candidates.append(final_candidate)
            
            # 记录结果到总结果列表
            result = {
                'base_image': best_template['base_image'],
                'compare_image': compare_img,
                'template_score': best_template['template_score'],
                'template_method': best_template['template_method'],
                'color_score': 0.0,
                'composite_score': best_template['template_score']
            }
            all_results.append(result)
        
        # 选择最佳匹配
        best_match = None
        best_score = 0
        best_base_masked = None
        best_base_mask = None
        
        if final_candidates:
            # 按综合得分排序，选择最佳匹配
            final_candidates.sort(key=lambda x: x['composite_score'], reverse=True)
            best_candidate = final_candidates[0]
            
            best_match = {
                'base_image': best_candidate['base_image'],
                'compare_image': compare_img,
                'template_score': best_candidate['template_score'],
                'template_method': best_candidate['template_method'],
                'color_score': best_candidate['color_score'],
                'composite_score': best_candidate['composite_score']
            }
            best_score = best_candidate['composite_score']
            best_base_masked = best_candidate['base_masked_image']
            best_base_mask = best_candidate['base_mask']
            
            log_message("DEBUG", f"选择最佳匹配: {best_candidate['base_image']} (综合得分: {best_candidate['composite_score']:.2f}%)")
        
        # 创建对比图像并保存
        if best_match and best_base_masked is not None:
            # 调整图像大小为相同尺寸以便比较
            target_size = (200, 200)  # 增大尺寸以便更好地查看
            
            # 尝试使用equipment_masks目录下的掩码后装备图像
            # 获取equipment_masks目录
            equipment_mask_dir = os.path.join(output_dir, "equipment_masks")
            
            # 查找匹配的掩码后装备图像
            base_masked_eq_img = None
            compare_masked_eq_img = None
            
            try:
                # 查找基准图像对应的掩码后装备图像
                base_files = [f for f in os.listdir(equipment_mask_dir) 
                             if f.startswith("img1_equipment_only_") and f.endswith(".png")]
                if base_files:
                    # 使用最新的掩码后装备图像
                    base_files.sort(reverse=True)
                    base_eq_path = os.path.join(equipment_mask_dir, base_files[0])
                    base_masked_eq_img = load_image(base_eq_path)
                    log_message("DEBUG", f"使用基准掩码后装备图像: {base_eq_path}")
                
                # 查找对比图像对应的掩码后装备图像
                compare_files = [f for f in os.listdir(equipment_mask_dir) 
                                if f.startswith("img2_equipment_only_") and f.endswith(".png")]
                if compare_files:
                    # 使用最新的掩码后装备图像
                    compare_files.sort(reverse=True)
                    compare_eq_path = os.path.join(equipment_mask_dir, compare_files[0])
                    compare_masked_eq_img = load_image(compare_eq_path)
                    log_message("DEBUG", f"使用对比掩码后装备图像: {compare_eq_path}")
            except Exception as e:
                log_message("ERROR", f"加载掩码后装备图像失败: {e}")
            
            # 如果找不到掩码后装备图像，使用原始掩码图像作为备选
            if base_masked_eq_img is None:
                base_masked_eq_img = best_base_masked
            if compare_masked_eq_img is None:
                compare_masked_eq_img = compare_masked_image
            
            # 调整图像大小
            base_resized = cv2.resize(base_masked_eq_img, target_size)
            compare_resized = cv2.resize(compare_masked_eq_img, target_size)
            
            # 创建对比图像
            comparison_image = np.zeros((target_size[0], target_size[1] * 2, 3), dtype=np.uint8)
            comparison_image[:, :target_size[1]] = base_resized
            comparison_image[:, target_size[1]:] = compare_resized
            
            # 在图像上添加文本信息
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            color = (255, 255, 255)
            thickness = 1
            
            # 添加基准图像信息
            base_text = f"{best_match['base_image']}"
            cv2.putText(comparison_image, base_text, (10, 20), font, font_scale, color, thickness)
            cv2.putText(comparison_image, f"Score: {best_match['composite_score']:.2f}%", (10, 40), font, font_scale, color, thickness)
            
            # 添加对比图像信息
            compare_text = f"{compare_img}"
            cv2.putText(comparison_image, compare_text, (target_size[1] + 10, 20), font, font_scale, color, thickness)
            cv2.putText(comparison_image, f"Template: {best_match['template_score']:.2f}%", (target_size[1] + 10, 40), font, font_scale, color, thickness)
            cv2.putText(comparison_image, f"Color: {best_match['color_score']:.3f}", (target_size[1] + 10, 60), font, font_scale, color, thickness)
            
            # 保存对比图像
            comparison_filename = f"comparison_{compare_img}_vs_{best_match['base_image']}.jpg"
            comparison_path = os.path.join(comparison_output_dir, comparison_filename)
            cv2.imwrite(comparison_path, comparison_image)
            
            log_message("DEBUG", f"已保存对比图像: {comparison_path}")
        
        # 输出最佳匹配结果到终端
        if best_match:
            if best_match['composite_score'] > 90:
                log_message("RESULT",
                           f"按照阈值匹配90%：最终筛选出{best_match['base_image']} ← {best_match['compare_image']} "
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
    result_file = os.path.join(output_dir, f"matching_results_{timestamp}.json")
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    # 生成汇总报告
    summary_file = os.path.join(output_dir, f"matching_summary_{timestamp}.txt")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("装备图片匹配结果汇总\n")
        f.write("=" * 50 + "\n")
        f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"基准图像数量: {len(base_images)}\n")
        f.write(f"对比图像数量: {len(compare_images)}\n")
        f.write(f"总匹配次数: {len(all_results)}\n")
        f.write(f"匹配方法: 两阶段匹配策略\n")
        f.write(f"阶段1: TM_CCOEFF_NORMED模板匹配筛选候选\n")
        f.write(f"阶段2: 颜色欧氏距离区分高分候选\n")
        f.write(f"模板匹配阈值: 70.0%\n")
        f.write(f"模板匹配掩码策略: 已禁用\n")
        f.write(f"颜色匹配掩码策略: 圆形掩码策略（半径55，圆内紫色去除，圆外黑色）\n")
        f.write(f"装备掩码图像: 保存到 equipment_masks/ 目录\n")
        f.write(f"圆形掩码: 图像中心半径55的圆形区域，圆内紫色去除，圆外黑色\n")
        f.write(f"图像尺寸: 保持116*116像素\n")
        f.write(f"颜色相似度: 仅对高分候选启用（LAB色彩空间）\n")
        f.write(f"模板匹配权重: 65% (0.65)\n")
        f.write(f"颜色相似度权重: 35% (0.35)\n")
        f.write(f"颜色空间: LAB色彩空间\n")
        f.write(f"最大颜色距离: 300.0\n")
        f.write("\n")
        
        # 按对比图像分组显示最佳匹配
        f.write("各对比图像的最佳匹配结果:\n")
        f.write("-" * 50 + "\n")
        
        for compare_img in compare_images:
            compare_results = [r for r in all_results if r['compare_image'] == compare_img]
            if compare_results:
                best = max(compare_results, key=lambda x: x['composite_score'])
                f.write(f"{compare_img}:\n")
                if best['composite_score'] > 90:
                    f.write(f"  按照阈值匹配90%：最终筛选出{best['base_image']}\n")
                else:
                    f.write(f"  最佳匹配: {best['base_image']}\n")
                f.write(f"  综合得分: {best['composite_score']:.2f}%\n")
                f.write(f"  模板匹配: {best['template_score']:.2f}% ({best['template_method']})\n")
                f.write(f"  颜色相似度: {best['color_score']:.3f}\n\n")
    
    log_message("RESULT", f"匹配完成，结果已保存到: {output_dir}")
    log_message("RESULT", f"详细结果: {result_file}")
    log_message("RESULT", f"汇总报告: {summary_file}")
    
    return all_results

def step3_match_equipment(auto_mode=True, base_dir=None, compare_dir=None, output_dir=None):
    """步骤3：装备图片匹配"""
    # 初始化日志系统
    if LOGGER_AVAILABLE:
        logger = get_unified_logger()
        logger.start_step("step3_match", "装备匹配")
    else:
        log_message("INIT", "开始执行步骤3：装备图片匹配")
    
    # 检查依赖
    if not check_dependencies():
        if LOGGER_AVAILABLE:
            logger.end_step("step3_match", "失败")
        return False
    
    # 设置默认路径
    if base_dir is None:
        base_dir = "images/base_equipment"  # 修正：使用正确的基准图像目录
    if compare_dir is None:
        compare_dir = "images/cropped_equipment_transparent"  # 使用透明背景的裁剪图像
    if output_dir is None:
        if LOGGER_AVAILABLE:
            output_dir = logger.get_step_dir("step3_match") / "images"
            txt_output_dir = logger.get_step_dir("step3_match") / "txt"
            txt_output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = "step_tests/step3_match/images"  # 更新：输出到step3_match目录下
    
    # 执行匹配
    try:
        match_results = match_equipment_images(base_dir, compare_dir, output_dir)
        
        if match_results:
            if LOGGER_AVAILABLE:
                logger.log_success(f"图片匹配完成，共处理 {len(match_results)} 次匹配")
                logger.log_info(f"基准图像: {len(set(r['base_image'] for r in match_results))} 个")
                logger.log_info(f"对比图像: {len(set(r['compare_image'] for r in match_results))} 个")
                logger.log_info(f"结果已保存到: {output_dir}")
                
                # 生成处理报告
                stats = logger.get_step_stats("step3_match")
                additional_info = {
                    "files_processed": [r['compare_image'] for r in match_results],
                    "match_results": match_results,
                    "base_images": list(set(r['base_image'] for r in match_results))
                }
                
                report_generator.generate_step_report("step3_match", stats, additional_info)
                logger.end_step("step3_match", "完成")
                
                logger.log_info(f"Total images: {len(set(r['compare_image'] for r in match_results))}, Processed: {len(match_results)}")
            else:
                log_message("RESULT", f"图片匹配完成，共处理 {len(match_results)} 次匹配")
                log_message("RESULT", f"  - 基准图像: {len(set(r['base_image'] for r in match_results))} 个")
                log_message("RESULT", f"  - 对比图像: {len(set(r['compare_image'] for r in match_results))} 个")
                log_message("RESULT", f"  - 结果已保存到: {output_dir}")
            return True
        else:
            if LOGGER_AVAILABLE:
                logger.log_warning("图片匹配未产生结果")
                logger.end_step("step3_match", "无结果")
            else:
                log_message("WARNING", "图片匹配未产生结果")
            return False
            
    except Exception as e:
        if LOGGER_AVAILABLE:
            logger.log_error(f"图片匹配过程中出错: {e}")
            logger.end_step("step3_match", "失败")
        else:
            log_message("ERROR", f"图片匹配过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    log_message("INIT", "步骤3：装备图片匹配功能测试模块")
    
    try:
        import argparse
        
        # 解析命令行参数
        parser = argparse.ArgumentParser(description='步骤3：装备图片匹配功能测试')
        parser.add_argument('--base-dir', type=str, default=None,
                           help='基准图像目录路径')
        parser.add_argument('--compare-dir', type=str, default=None,
                           help='对比图像目录路径')
        parser.add_argument('--output-dir', type=str, default=None,
                           help='输出目录路径')
        
        args = parser.parse_args()
        
        # 自动执行步骤3功能
        success = step3_match_equipment(
            auto_mode=True,
            base_dir=args.base_dir,
            compare_dir=args.compare_dir,
            output_dir=args.output_dir
        )
        
        if not success:
            print("\n❌ 步骤3自动化执行失败！")
            
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()