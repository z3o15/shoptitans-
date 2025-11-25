#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤3：装备图片匹配功能

本模块专注于装备图片匹配功能，实现两阶段匹配策略：
1. LAB色彩空间模板匹配筛选候选
2. 像素级LAB欧氏距离颜色匹配区分高分候选

优化特性：
- 使用LAB色彩空间进行模板匹配，更好地区分彩色装备
- 最小化文件输出，只保留最终对比图
- 内存中处理掩码，避免文件激增
- 导出CSV表格记录匹配结果
"""

import os
import sys
import json
import csv
import logging
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Generator
from dataclasses import dataclass, asdict
from datetime import datetime

import cv2
import numpy as np
from PIL import Image

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

# ==================== 配置日志 ====================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# ==================== 数据类 ====================
@dataclass
class MatchResult:
    """匹配结果数据类"""
    base_image: str
    compare_image: str
    template_score: float
    template_method: str
    color_score: float
    composite_score: float
    debug_info: Dict = None  # 调试信息
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class MatchConfig:
    """匹配配置数据类"""
    template_threshold: float = 70.0
    max_color_distance: float = 300.0
    circle_radius: int = 55
    equipment_ratio_threshold: float = 0.02  # 降低阈值
    save_comparison_images: bool = True
    use_circle_mask: bool = True  # 是否使用圆形掩码


# ==================== 图像处理工具类 ====================
class ImageProcessor:
    """图像处理工具类"""
    
    @staticmethod
    def load_image(image_path: Path) -> Optional[np.ndarray]:
        """加载图像并处理透明通道"""
        try:
            img = Image.open(image_path)
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            
            img_array = np.array(img)
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            return img_array
        except Exception as e:
            logger.error(f"加载图像失败 {image_path}: {e}")
            return None
    
    @staticmethod
    def create_equipment_mask(image: np.ndarray, radius: int = 55, tolerance: int = 23, erode_iterations: int = 2) -> np.ndarray:
        """创建装备本体掩码（精确版：只去除紫色背景，保留装备细节）"""
        try:
            height, width = image.shape[:2]
            if height != 116 or width != 116:
                image = cv2.resize(image, (116, 116))
                height, width = 116, 116
            
            center_x, center_y = width // 2, height // 2
            max_radius = min(center_x, center_y)
            radius = min(radius, max_radius)
            
            circle_mask = np.zeros((height, width), dtype=np.uint8)
            cv2.circle(circle_mask, (center_x, center_y), radius, 255, -1)
            
            # 检测紫色区域 (BGR: 46, 33, 46) - 扩大范围以覆盖所有紫色变体
            purple_mask = cv2.inRange(image, np.array([25, 15, 25]), np.array([70, 55, 70]))
            
            # 关键：只在圆形边缘区域去除紫色，保留中心装备的所有颜色
            # 创建边缘环形区域（外圈35像素，大幅扩大边缘区域）
            inner_circle = np.zeros((height, width), dtype=np.uint8)
            # 内圈半径缩小到20，这样边缘区域从半径20到55，宽度35像素
            cv2.circle(inner_circle, (center_x, center_y), 0, 255, -1)
            
            # 边缘区域 = 圆形掩码 - 内圈
            edge_region = cv2.subtract(circle_mask, inner_circle)
            
            # 只在边缘区域去除紫色
            purple_in_edge = cv2.bitwise_and(purple_mask, edge_region)
            
            # 最终掩码 = 圆形区域 - 边缘紫色
            equipment_mask = cv2.bitwise_and(circle_mask, cv2.bitwise_not(purple_in_edge))
            
            # 轻微形态学处理
            kernel = np.ones((5, 8), np.uint8)
            equipment_mask = cv2.morphologyEx(equipment_mask, cv2.MORPH_CLOSE, kernel, iterations=1)
            
            # 轻微羽化
            equipment_mask = cv2.GaussianBlur(equipment_mask.astype(np.float32), (7, 7), 4)
            _, equipment_mask = cv2.threshold(equipment_mask, 200, 255, cv2.THRESH_BINARY)
            
            return equipment_mask.astype(np.uint8)
        except Exception as e:
            logger.error(f"装备掩码创建失败: {e}")
            return np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)


# ==================== 匹配器类 ====================
class EquipmentMatcher:
    """装备匹配器类 - 使用LAB色彩空间"""
    
    def __init__(self, config: MatchConfig = None):
        self.config = config or MatchConfig()
        self.processor = ImageProcessor()
    
    def template_matching_lab(self, template: np.ndarray, scene: np.ndarray) -> Tuple[float, str]:
        """使用LAB色彩空间三通道加权匹配"""
        try:
            if template.shape[0] > scene.shape[0] or template.shape[1] > scene.shape[1]:
                scene = cv2.resize(scene, (template.shape[1], template.shape[0]))
            
            template_lab = cv2.cvtColor(template, cv2.COLOR_BGR2LAB) if len(template.shape) == 3 else template
            scene_lab = cv2.cvtColor(scene, cv2.COLOR_BGR2LAB) if len(scene.shape) == 3 else scene
            
            # 使用LAB三通道加权匹配
            scores = []
            weights = [0.5, 0.25, 0.25]  # L, A, B 通道权重
            
            for i, weight in enumerate(weights):
                if len(template_lab.shape) == 3:
                    template_channel = template_lab[:, :, i]
                    scene_channel = scene_lab[:, :, i]
                else:
                    template_channel = template_lab
                    scene_channel = scene_lab
                
                result = cv2.matchTemplate(scene_channel, template_channel, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                scores.append(max_val * weight)
            
            # 加权平均
            final_score = sum(scores) * 100
            return final_score, "TM_LAB_WEIGHTED"
        except Exception as e:
            logger.error(f"LAB模板匹配失败: {e}")
            return 0.0, ""
    
    def calculate_histogram_similarity(self, img1: np.ndarray, img2: np.ndarray, mask: np.ndarray) -> float:
        """
        计算直方图相似度（对边缘锯齿不敏感）
        
        Args:
            img1: 第一张图像
            img2: 第二张图像
            mask: 掩码
            
        Returns:
            直方图相似度（0-1）
        """
        try:
            # 计算LAB空间的直方图
            lab1 = cv2.cvtColor(img1, cv2.COLOR_BGR2LAB)
            lab2 = cv2.cvtColor(img2, cv2.COLOR_BGR2LAB)
            
            # 使用8x8x8的bins
            hist1 = cv2.calcHist([lab1], [0, 1, 2], mask, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            hist2 = cv2.calcHist([lab2], [0, 1, 2], mask, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            
            # 归一化
            cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            
            # 使用相关性方法比较（返回值范围-1到1，1表示完全相同）
            similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            # 转换为0-1范围
            similarity = (similarity + 1) / 2
            
            return max(0, min(1, similarity))
        except Exception as e:
            logger.error(f"直方图相似度计算失败: {e}")
            return 0.0
    
    def calculate_color_similarity_lab(self, img1: np.ndarray, img2: np.ndarray) -> Tuple[float, Dict]:
        """计算颜色相似度（LAB色彩空间像素级欧氏距离 + 直方图）"""
        try:
            target_size = (116, 116)
            img1_resized = cv2.resize(img1, target_size)
            img2_resized = cv2.resize(img2, target_size)
            
            # 创建掩码（改进版：去除紫色、透明部分和边缘）
            if self.config.use_circle_mask:
                equipment_mask1 = self.processor.create_equipment_mask(img1_resized, self.config.circle_radius, erode_iterations=2)
                equipment_mask2 = self.processor.create_equipment_mask(img2_resized, self.config.circle_radius, erode_iterations=2)
            else:
                # 不使用圆形掩码，但仍然去除紫色和白色
                equipment_mask1 = self.processor.create_equipment_mask(img1_resized, radius=58, erode_iterations=2)
                equipment_mask2 = self.processor.create_equipment_mask(img2_resized, radius=58, erode_iterations=2)
            
            combined_mask = cv2.bitwise_and(equipment_mask1, equipment_mask2)
            
            equipment_pixels = np.sum(combined_mask == 255)
            total_pixels = target_size[0] * target_size[1]
            equipment_ratio = equipment_pixels / total_pixels
            
            # 调试信息
            debug_info = {
                'equipment_pixels': int(equipment_pixels),
                'total_pixels': int(total_pixels),
                'equipment_ratio': float(equipment_ratio)
            }
            
            if equipment_ratio < self.config.equipment_ratio_threshold:
                logger.warning(f"装备区域过小: {equipment_ratio:.2%} (阈值: {self.config.equipment_ratio_threshold:.2%})")
            
            # 方法1：像素级LAB欧氏距离
            lab1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2LAB)
            lab2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2LAB)
            
            equipment_coords = np.where(combined_mask == 255)
            if len(equipment_coords[0]) == 0:
                logger.warning("没有找到装备像素")
                return 0.0, debug_info
            
            pixels1 = lab1[equipment_coords[0], equipment_coords[1]]
            pixels2 = lab2[equipment_coords[0], equipment_coords[1]]
            distances = np.linalg.norm(pixels1 - pixels2, axis=1)
            avg_distance = np.mean(distances)
            std_distance = np.std(distances)
            
            pixel_similarity = max(0, 1 - avg_distance / self.config.max_color_distance)
            
            # 方法2：直方图相似度（对边缘锯齿不敏感）
            hist_similarity = self.calculate_histogram_similarity(img1_resized, img2_resized, combined_mask)
            
            # 动态权重：像素少时更依赖直方图，像素多时更依赖像素级匹配
            # equipment_ratio范围：0.02-0.5，映射到权重：0.3-0.7
            pixel_weight = min(0.7, max(0.3, 0.3 + equipment_ratio * 0.8))
            hist_weight = 1.0 - pixel_weight
            
            # 综合两种方法：动态权重
            final_similarity = pixel_similarity * pixel_weight + hist_similarity * hist_weight
            
            debug_info.update({
                'avg_distance': float(avg_distance),
                'std_distance': float(std_distance),
                'min_distance': float(np.min(distances)),
                'max_distance': float(np.max(distances)),
                'pixel_similarity': float(pixel_similarity),
                'hist_similarity': float(hist_similarity),
                'pixel_weight': float(pixel_weight),
                'hist_weight': float(hist_weight),
                'final_similarity': float(final_similarity)
            })
            
            return final_similarity, debug_info
        except Exception as e:
            logger.error(f"颜色相似度计算失败: {e}")
            return 0.0, {}
    
    def calculate_composite_score(self, template_score: float, color_score: float) -> float:
        """计算综合得分（直接相加）"""
        color_score_100 = color_score * 100
        # 直接相加：模板分数(0-100) + 颜色分数(0-100) = 总分(0-200)
        return template_score + color_score_100
    
    def match_single_image(self, compare_image: np.ndarray, compare_name: str, base_images: Dict[str, np.ndarray]) -> Optional[MatchResult]:
        """匹配单张图像"""
        template_candidates = []
        for base_name, base_image in base_images.items():
            template_score, method = self.template_matching_lab(base_image, compare_image)
            template_candidates.append({'name': base_name, 'image': base_image, 'score': template_score, 'method': method})
        
        template_candidates.sort(key=lambda x: x['score'], reverse=True)
        high_score_candidates = [c for c in template_candidates if c['score'] >= self.config.template_threshold]
        
        best_match = None
        best_score = 0.0
        
        if high_score_candidates:
            for candidate in high_score_candidates:
                # 计算颜色相似度
                color_score, debug_info = self.calculate_color_similarity_lab(
                    candidate['image'], compare_image
                )
                composite_score = self.calculate_composite_score(candidate['score'], color_score)
                
                if composite_score > best_score:
                    best_score = composite_score
                    best_match = MatchResult(
                        base_image=candidate['name'], compare_image=compare_name,
                        template_score=candidate['score'], template_method=candidate['method'],
                        color_score=color_score, composite_score=composite_score,
                        debug_info=debug_info
                    )
        elif template_candidates:
            best = template_candidates[0]
            best_match = MatchResult(
                base_image=best['name'], compare_image=compare_name,
                template_score=best['score'], template_method=best['method'],
                color_score=0.0, composite_score=best['score']
            )
        
        return best_match
    
    def create_comparison_image(self, base_image: np.ndarray, compare_image: np.ndarray, match_result: MatchResult) -> np.ndarray:
        """创建对比图像（显示完整文件名，使用去除紫色背景后的图像）"""
        # 先调整到116x116创建掩码
        mask_size = (116, 116)
        base_116 = cv2.resize(base_image, mask_size)
        compare_116 = cv2.resize(compare_image, mask_size)
        
        # 创建掩码（去除紫色背景）
        base_mask_116 = self.processor.create_equipment_mask(base_116, self.config.circle_radius, erode_iterations=2)
        compare_mask_116 = self.processor.create_equipment_mask(compare_116, self.config.circle_radius, erode_iterations=2)
        
        # 应用掩码到116x116图像
        base_masked_116 = cv2.bitwise_and(base_116, base_116, mask=base_mask_116)
        compare_masked_116 = cv2.bitwise_and(compare_116, compare_116, mask=compare_mask_116)
        
        # 将掩码外的区域设为白色
        base_masked_116[base_mask_116 == 0] = [255, 255, 255]
        compare_masked_116[compare_mask_116 == 0] = [255, 255, 255]
        
        # 再放大到250x250用于显示
        target_size = (250, 250)
        base_masked = cv2.resize(base_masked_116, target_size, interpolation=cv2.INTER_LINEAR)
        compare_masked = cv2.resize(compare_masked_116, target_size, interpolation=cv2.INTER_LINEAR)
        
        # 创建更大的画布以容纳文字
        canvas_height = target_size[0] + 80
        comparison = np.zeros((canvas_height, target_size[1] * 2, 3), dtype=np.uint8)
        comparison[:] = [255, 255, 255]  # 白色背景
        comparison[80:80+target_size[0], :target_size[1]] = base_masked
        comparison[80:80+target_size[0], target_size[1]:] = compare_masked
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.4
        thickness = 1
        color = (255, 255, 255)
        
        # 左侧（基准图像）
        y_offset = 15
        cv2.putText(comparison, "Base:", (10, y_offset), font, font_scale, color, thickness)
        cv2.putText(comparison, match_result.base_image[:30], (10, y_offset + 15), font, font_scale, color, thickness)
        if len(match_result.base_image) > 30:
            cv2.putText(comparison, match_result.base_image[30:], (10, y_offset + 30), font, font_scale, color, thickness)
        cv2.putText(comparison, f"Composite: {match_result.composite_score:.1f}%", (10, y_offset + 50), font, font_scale, (0, 255, 0), thickness)
        
        # 右侧（对比图像）
        cv2.putText(comparison, "Compare:", (target_size[1] + 10, y_offset), font, font_scale, color, thickness)
        cv2.putText(comparison, match_result.compare_image[:30], (target_size[1] + 10, y_offset + 15), font, font_scale, color, thickness)
        if len(match_result.compare_image) > 30:
            cv2.putText(comparison, match_result.compare_image[30:], (target_size[1] + 10, y_offset + 30), font, font_scale, color, thickness)
        cv2.putText(comparison, f"Template: {match_result.template_score:.1f}%", (target_size[1] + 10, y_offset + 50), font, font_scale, (0, 255, 255), thickness)
        cv2.putText(comparison, f"Color: {match_result.color_score:.3f}", (target_size[1] + 10, y_offset + 65), font, font_scale, (255, 0, 255), thickness)
        
        return comparison


# ==================== 文件管理器类 ====================
class FileManager:
    """文件管理器类"""
    
    @staticmethod
    def get_image_files(directory: Path) -> Generator[Path, None, None]:
        """获取目录中的图像文件（生成器）"""
        if not directory.exists():
            logger.error(f"目录不存在: {directory}")
            return
        
        image_extensions = {'.png', '.jpg', '.jpeg', '.webp'}
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                yield file_path
    
    @staticmethod
    def load_images_batch(directory: Path) -> Dict[str, np.ndarray]:
        """批量加载图像"""
        images = {}
        processor = ImageProcessor()
        for file_path in FileManager.get_image_files(directory):
            image = processor.load_image(file_path)
            if image is not None:
                images[file_path.name] = image
        return images
    
    @staticmethod
    def ensure_directory(directory: Path) -> None:
        """确保目录存在"""
        directory.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def save_results(results: List[MatchResult], output_dir: Path, compare_dir: Path, save_comparisons: bool = True,
                    base_images: Dict[str, np.ndarray] = None, compare_images: Dict[str, np.ndarray] = None,
                    matcher: EquipmentMatcher = None) -> Tuple[Path, Path, Path]:
        """保存匹配结果（最小化文件输出 + CSV导出）"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 清空并创建comparisons文件夹（在保存任何文件之前）
        comparison_dir = output_dir / "comparisons"
        if comparison_dir.exists():
            import shutil
            shutil.rmtree(comparison_dir)
            logger.info(f"已清空对比图像文件夹: {comparison_dir}")
        
        FileManager.ensure_directory(comparison_dir)
        
        # 保存CSV文件（高置信度匹配结果）到compare_dir目录
        csv_file = compare_dir / f"matching_results_{timestamp}.csv"
        high_confidence_threshold = 90
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['原始名称', '匹配装备名称'])
            
            # 获取所有原始文件名（按数字排序）
            all_original_names = sorted(set(result.compare_image.rsplit('.', 1)[0] for result in results))
            
            # 创建匹配结果字典
            match_dict = {}
            for result in results:
                original_name = result.compare_image.rsplit('.', 1)[0]
                if result.composite_score > high_confidence_threshold:
                    matched_name = result.base_image.rsplit('.', 1)[0]
                    match_dict[original_name] = matched_name
            
            # 写入所有原始文件
            for original_name in all_original_names:
                matched_name = match_dict.get(original_name, '')
                writer.writerow([original_name, matched_name])
        
        logger.info(f"已保存CSV匹配结果到: {csv_file}")
        
        # 保存JSON结果文件
        json_file = comparison_dir / f"matching_results_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([r.to_dict() for r in results], f, indent=2, ensure_ascii=False)
        
        # 保存汇总报告
        summary_file = comparison_dir / f"matching_summary_{timestamp}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("装备图片匹配结果汇总\n")
            f.write("=" * 50 + "\n")
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"匹配方法: LAB色彩空间两阶段匹配\n")
            f.write(f"总匹配次数: {len(results)}\n")
            f.write(f"基准图像数量: {len(set(r.base_image for r in results))}\n")
            f.write(f"对比图像数量: {len(set(r.compare_image for r in results))}\n\n")
            
            compare_groups = {}
            for result in results:
                if result.compare_image not in compare_groups:
                    compare_groups[result.compare_image] = []
                compare_groups[result.compare_image].append(result)
            
            f.write("各对比图像的最佳匹配结果:\n")
            f.write("-" * 50 + "\n")
            
            for compare_img, group_results in compare_groups.items():
                best = max(group_results, key=lambda x: x.composite_score)
                f.write(f"{compare_img}:\n")
                if best.composite_score > 90:
                    f.write(f"  ✓ 高置信度匹配: {best.base_image}\n")
                else:
                    f.write(f"  最佳匹配: {best.base_image}\n")
                f.write(f"  综合得分: {best.composite_score:.2f}%\n")
                f.write(f"  模板匹配: {best.template_score:.2f}% ({best.template_method})\n")
                f.write(f"  颜色相似度: {best.color_score:.3f}\n")
                
                # 添加调试信息
                if best.debug_info:
                    debug = best.debug_info
                    f.write(f"  【调试信息】\n")
                    f.write(f"    装备像素: {debug.get('equipment_pixels', 0)}/{debug.get('total_pixels', 0)} ")
                    f.write(f"({debug.get('equipment_ratio', 0):.2%})\n")
                    if 'avg_distance' in debug:
                        f.write(f"    平均颜色距离: {debug.get('avg_distance', 0):.2f}\n")
                        f.write(f"    距离标准差: {debug.get('std_distance', 0):.2f}\n")
                        f.write(f"    像素相似度: {debug.get('pixel_similarity', 0):.3f} (权重: {debug.get('pixel_weight', 0):.2f})\n")
                        f.write(f"    直方图相似度: {debug.get('hist_similarity', 0):.3f} (权重: {debug.get('hist_weight', 0):.2f})\n")
                        f.write(f"    最终相似度: {debug.get('final_similarity', 0):.3f}\n")
                f.write("\n")
        
        # 保存对比图像
        if save_comparisons and base_images and compare_images and matcher:
            
            saved_count = 0
            for result in results:
                if result.base_image in base_images and result.compare_image in compare_images:
                    comparison_img = matcher.create_comparison_image(
                        base_images[result.base_image], compare_images[result.compare_image], result
                    )
                    # 生成文件名：原文件名_匹配装备名.png
                    # 例如：10_circle.png → 10_circle_t5instrument.png
                    compare_name = result.compare_image.rsplit('.', 1)[0]  # 去除扩展名
                    base_name = result.base_image.rsplit('.', 1)[0]  # 去除扩展名
                    comparison_file = comparison_dir / f"{compare_name}_{base_name}.png"
                    cv2.imwrite(str(comparison_file), comparison_img)
                    saved_count += 1
            
            logger.info(f"已保存 {saved_count} 张对比图像到: {comparison_dir}")
        
        return json_file, summary_file, csv_file


# ==================== 主执行类 ====================
class EquipmentMatchingPipeline:
    """装备匹配流程类"""
    
    def __init__(self, config: MatchConfig = None):
        self.config = config or MatchConfig()
        self.matcher = EquipmentMatcher(self.config)
        self.file_manager = FileManager()
    
    def _rename_high_confidence_files(self, results: List[MatchResult], compare_dir: Path) -> None:
        """重命名高置信度匹配的原始文件"""
        try:
            renamed_count = 0
            high_confidence_threshold = 90  # 高置信度阈值
            
            logger.info("\n开始重命名高置信度匹配的文件...")
            
            for result in results:
                if result.composite_score > high_confidence_threshold:
                    # 原始文件路径
                    original_file = compare_dir / result.compare_image
                    
                    if original_file.exists():
                        # 生成新文件名：原文件名_匹配装备名.png
                        compare_name = result.compare_image.rsplit('.', 1)[0]  # 去除扩展名
                        base_name = result.base_image.rsplit('.', 1)[0]  # 去除扩展名
                        new_filename = f"{compare_name}_{base_name}.png"
                        new_file = compare_dir / new_filename
                        
                        # 重命名文件
                        original_file.rename(new_file)
                        renamed_count += 1
                        logger.info(f"  ✓ {result.compare_image} → {new_filename}")
            
            if renamed_count > 0:
                logger.info(f"已重命名 {renamed_count} 个高置信度匹配的文件")
            else:
                logger.info("没有高置信度匹配的文件需要重命名")
                
        except Exception as e:
            logger.error(f"重命名文件时出错: {e}")
    
    def run(self, base_dir: Path, compare_dir: Path, output_dir: Path) -> bool:
        """执行匹配流程"""
        try:
            logger.info("=" * 60)
            logger.info("开始装备图片匹配（LAB色彩空间两阶段策略）")
            logger.info("=" * 60)
            
            if not base_dir.exists():
                logger.error(f"基准图像目录不存在: {base_dir}")
                return False
            
            if not compare_dir.exists():
                logger.error(f"对比图像目录不存在: {compare_dir}")
                return False
            
            self.file_manager.ensure_directory(output_dir)
            
            logger.info(f"加载基准图像: {base_dir}")
            base_images = self.file_manager.load_images_batch(base_dir)
            
            if not base_images:
                logger.error("未找到基准图像")
                return False
            
            logger.info(f"✓ 已加载 {len(base_images)} 个基准图像")
            
            logger.info(f"加载对比图像: {compare_dir}")
            compare_images = self.file_manager.load_images_batch(compare_dir)
            
            if not compare_images:
                logger.error("未找到对比图像")
                return False
            
            logger.info(f"✓ 已加载 {len(compare_images)} 个对比图像")
            logger.info("开始匹配处理...")
            
            all_results = []
            failed_images = []
            total_files = len(compare_images)
            
            for idx, (compare_name, compare_image) in enumerate(compare_images.items(), 1):
                try:
                    result = self.matcher.match_single_image(compare_image, compare_name, base_images)
                    
                    if result:
                        all_results.append(result)
                        status = "✓ 高置信度" if result.composite_score > 90 else "○ 最佳匹配"
                        logger.info(
                            f"[{idx}/{total_files}] {status}: {result.compare_image} → "
                            f"{result.base_image} (得分: {result.composite_score:.1f}%)"
                        )
                    else:
                        failed_images.append((compare_name, "无匹配结果"))
                        
                except Exception as e:
                    failed_images.append((compare_name, str(e)))
                    logger.error(f"处理失败 {compare_name}: {e}")
            
            if all_results:
                json_file, summary_file, csv_file = self.file_manager.save_results(
                    all_results, output_dir, compare_dir, save_comparisons=self.config.save_comparison_images,
                    base_images=base_images, compare_images=compare_images, matcher=self.matcher
                )
                
                logger.info("=" * 60)
                logger.info("匹配完成")
                logger.info(f"✓ 成功匹配: {len(all_results)} 个")
                if failed_images:
                    logger.warning(f"✗ 失败: {len(failed_images)} 个")
                    for name, reason in failed_images[:5]:
                        logger.warning(f"  - {name}: {reason}")
                    if len(failed_images) > 5:
                        logger.warning(f"  ... 还有 {len(failed_images) - 5} 个失败")
                logger.info(f"CSV结果: {csv_file}")
                logger.info(f"详细结果: {json_file}")
                logger.info(f"汇总报告: {summary_file}")
                logger.info("=" * 60)
                
                # 自动重命名高置信度匹配的原始文件
                self._rename_high_confidence_files(all_results, compare_dir)
                
                return True
            else:
                logger.error("未产生任何匹配结果")
                return False
                
        except Exception as e:
            logger.error(f"匹配流程出错: {e}", exc_info=True)
            return False


# ==================== 主函数 ====================
def step3_match_equipment(auto_mode: bool = True, base_dir: Optional[str] = None,
                         compare_dir: Optional[str] = None, output_dir: Optional[str] = None,
                         save_comparisons: bool = True, use_circle_mask: bool = True) -> bool:
    """步骤3：装备图片匹配主函数"""
    base_path = Path(base_dir) if base_dir else Path("images/base_equipment")
    compare_path = Path(compare_dir) if compare_dir else Path(r"images\equipment_transparent")
    output_path = Path(output_dir) if output_dir else Path("images")
    
    config = MatchConfig(
        save_comparison_images=save_comparisons,
        use_circle_mask=use_circle_mask
    )
    pipeline = EquipmentMatchingPipeline(config)
    return pipeline.run(base_path, compare_path, output_path)


def main():
    """主函数"""
    try:
        import argparse
        
        parser = argparse.ArgumentParser(description='步骤3：装备图片匹配功能（LAB色彩空间优化版）')
        parser.add_argument('--base-dir', type=str, default=None, help='基准图像目录路径')
        parser.add_argument('--compare-dir', type=str, default=None, help='对比图像目录路径')
        parser.add_argument('--output-dir', type=str, default=None, help='输出目录路径')
        parser.add_argument('--no-comparisons', action='store_true', help='不保存对比图像')
        parser.add_argument('--no-circle-mask', action='store_true', help='禁用圆形掩码（使用全图）')
        
        args = parser.parse_args()
        
        success = step3_match_equipment(
            auto_mode=True, base_dir=args.base_dir, compare_dir=args.compare_dir,
            output_dir=args.output_dir, save_comparisons=not args.no_comparisons,
            use_circle_mask=not args.no_circle_mask
        )
        
        if not success:
            logger.error("步骤3执行失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"发生错误: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()