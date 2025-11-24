#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级装备识别器 - 独立版本
不依赖unique-matcher项目，实现模板匹配与辅助验证机制结合的识别方法
"""

import cv2
import numpy as np
from PIL import Image
import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class MatchingAlgorithm(Enum):
    """匹配算法枚举"""
    DEFAULT = 0
    VARIANTS_ONLY = 1
    HISTOGRAM = 2


class MatchedBy(Enum):
    """匹配方式枚举"""
    TEMPLATE_MATCH = 0
    HISTOGRAM_MATCH = 1
    ONLY_UNIQUE_FOR_BASE = 2
    ITEM_NAME = 3
    SOLARIS_CIRCLET = 4


@dataclass
class ItemTemplate:
    """装备模板数据类"""
    image: Image.Image
    sockets: int


@dataclass
class AdvancedMatchResult:
    """高级匹配结果数据类"""
    item_name: str
    item_base: str
    matched_by: MatchedBy
    min_val: float
    hist_val: float
    similarity: float
    confidence: float
    template: Optional[ItemTemplate] = None
    location: Optional[Tuple[int, int]] = None


class AdvancedEquipmentRecognizer:
    """高级装备识别器
    
    独立实现模板匹配与辅助验证机制结合的识别方法
    """
    
    def __init__(self, enable_masking=True, enable_histogram=True):
        """初始化高级装备识别器
        
        Args:
            enable_masking: 是否启用掩码匹配
            enable_histogram: 是否启用直方图验证
        """
        self.enable_masking = enable_masking
        self.enable_histogram = enable_histogram
        self.item_max_size = (113, 113)  # 修改：适应新的截图尺寸 (113*113)
        self.threshold_result_distance = 0.05  # 结果距离阈值
        
        print("✓ 高级装备识别器初始化完成")
        print(f"  - 掩码匹配: {'启用' if enable_masking else '禁用'}")
        print(f"  - 直方图验证: {'启用' if enable_histogram else '禁用'}")
        print(f"  - 标准尺寸: {self.item_max_size}")
    
    def preprocess_image(self, image_path: str, target_size: Tuple[int, int] = None, remove_background: bool = False) -> np.ndarray:
        """预处理图像：标准化尺寸和格式
        
        Args:
            image_path: 图像路径
            target_size: 目标尺寸，默认使用标准尺寸
            remove_background: 是否移除背景色（默认False，保留颜色信息）
            
        Returns:
            预处理后的图像数组（保留RGB颜色）
        """
        if target_size is None:
            target_size = self.item_max_size
            
        try:
            # 加载图像
            image = Image.open(image_path)
            
            # 转换为RGB格式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 轻微背景处理（可选）
            if remove_background:
                image_array = np.array(image)
                # 只处理明显的背景色，避免过度处理
                background_color = np.array([87, 47, 66])
                # 创建更严格的掩码，只移除纯背景色
                mask = np.all(np.abs(image_array - background_color) < 20, axis=2)
                # 将纯背景色设为浅灰色，保留一些信息
                image_array[mask] = [200, 200, 200]
                image = Image.fromarray(image_array)
            
            # 调整尺寸，保持颜色信息
            image = image.resize(target_size, Image.Resampling.LANCZOS)
            
            # 转换为numpy数组，保留RGB
            image_array = np.array(image)
                
            return image_array
            
        except Exception as e:
            print(f"图像预处理失败 {image_path}: {e}")
            return None
    
    def calc_color_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """计算两个图像的颜色相似度（参考unique-matcher的HSV方法）
        
        Args:
            img1: 第一个图像（RGB）
            img2: 第二个图像（RGB）
            
        Returns:
            颜色相似度（0-1，1表示完全相同）
        """
        try:
            # 确保图像是RGB格式
            if len(img1.shape) == 2:
                img1 = cv2.cvtColor(img1, cv2.COLOR_GRAY2RGB)
            if len(img2.shape) == 2:
                img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2RGB)
            
            # 参考unique-matcher：使用HSV空间的直方图比较
            # 转换为HSV
            hsv1 = cv2.cvtColor(img1, cv2.COLOR_RGB2HSV)
            hsv2 = cv2.cvtColor(img2, cv2.COLOR_RGB2HSV)
            
            # 计算HSV直方图（参考unique-matcher的参数）
            hist1 = cv2.calcHist([hsv1], [0, 1], None, [50, 60], [0, 180, 0, 256], accumulate=False)
            hist2 = cv2.calcHist([hsv2], [0, 1], None, [50, 60], [0, 180, 0, 256], accumulate=False)
            
            # 归一化
            cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            
            # 计算巴氏距离
            distance = cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)
            
            # 检查是否有NaN值
            if np.isnan(distance):
                print("  ⚠️ 警告：颜色相似度计算出现NaN值，使用默认值")
                return 0.3  # 返回一个合理的默认值
            
            # 转换为相似度
            similarity = 1 - distance
            
            # 确保返回值在合理范围内
            similarity = max(0.0, min(1.0, similarity))
            
            return similarity
            
        except Exception as e:
            print(f"颜色相似度计算失败: {e}")
            return 0.3  # 返回一个合理的默认值而不是0.0
    
    def create_mask(self, image: np.ndarray, threshold: int = 200) -> np.ndarray:
        """创建图像掩码（参考unique-matcher的掩码方法）
        
        Args:
            image: 输入图像
            threshold: 阈值
            
        Returns:
            掩码数组
        """
        try:
            # 参考unique-matcher的掩码创建方法
            # 如果是RGB图像，提取alpha通道信息
            if len(image.shape) == 3:
                # 检查是否有alpha通道
                if image.shape[2] == 4:
                    # 如果有alpha通道，直接使用alpha通道作为掩码
                    alpha_channel = image[:, :, 3]
                    # 将非零像素设为255
                    mask = np.where(alpha_channel > 0, 255, 0).astype(np.uint8)
                else:
                    # 如果没有alpha通道，基于颜色信息创建掩码
                    # 参考unique-matcher：检查透明度（alpha通道）
                    # 假设背景色是某种特定颜色，创建反掩码
                    background_color = np.array([87, 47, 66])  # 常见背景色
                    color_diff = np.abs(image.astype(np.int16) - background_color.astype(np.int16))
                    mask = np.any(color_diff > 30, axis=2).astype(np.uint8) * 255
                    
                    # 形态学操作改善掩码质量
                    kernel = np.ones((3, 3), np.uint8)
                    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            else:
                # 灰度图像处理
                mask = image.copy()
                _, mask = cv2.threshold(mask, threshold, 255, cv2.THRESH_BINARY)
            
            return mask
            
        except Exception as e:
            print(f"创建掩码失败: {e}")
            return None
    
    def template_match(self, template: np.ndarray, target: np.ndarray, mask: np.ndarray = None) -> Tuple[float, Tuple[int, int]]:
        """执行模板匹配（参考unique-matcher的优化方法）
        
        Args:
            template: 模板图像
            target: 目标图像
            mask: 可选的掩码
            
        Returns:
            (匹配值, 匹配位置) 的元组
        """
        try:
            # 确保输入是彩色图像
            if len(template.shape) != 3 or len(target.shape) != 3:
                raise ValueError("模板匹配需要RGB彩色图像")
            
            # 保存原始彩色图像
            template_color = template.copy()
            target_color = target.copy()
            
            # 参考unique-matcher：不进行缩放，直接使用原始尺寸
            # 确保模板不大于目标图像
            if template_color.shape[0] > target_color.shape[0] or template_color.shape[1] > target_color.shape[1]:
                # 调整模板尺寸，使其不大于目标图像
                scale = min(target_color.shape[0] / template_color.shape[0], target_color.shape[1] / template_color.shape[1])
                new_size = (int(template_color.shape[1] * scale), int(template_color.shape[0] * scale))
                template_color = cv2.resize(template_color, new_size)
                
                # 如果使用了掩码，也需要调整掩码尺寸
                if mask is not None:
                    mask = cv2.resize(mask, new_size)
            
            print(f"  执行彩色模板匹配，模板尺寸: {template_color.shape}")
            
            # 参考unique-matcher：转换为灰度图进行匹配，但保留彩色信息用于相似度计算
            template_gray = cv2.cvtColor(template_color, cv2.COLOR_RGB2GRAY)
            target_gray = cv2.cvtColor(target_color, cv2.COLOR_RGB2GRAY)
            
            # 执行模板匹配（使用灰度图，但保留彩色信息）
            if mask is not None:
                result = cv2.matchTemplate(target_gray, template_gray, cv2.TM_SQDIFF_NORMED, mask=mask)
            else:
                result = cv2.matchTemplate(target_gray, template_gray, cv2.TM_SQDIFF_NORMED)
            
            min_val, _, min_loc, _ = cv2.minMaxLoc(result)
            
            print(f"  彩色匹配值: {min_val:.6f}")
            
            return min_val, min_loc
            
        except Exception as e:
            print(f"彩色模板匹配失败: {e}")
            return 1.0, (0, 0)
    
    def recognize_equipment(self, base_image_path: str, target_image_path: str) -> AdvancedMatchResult:
        """识别装备
        
        Args:
            base_image_path: 基准装备图像路径
            target_image_path: 目标图像路径
            
        Returns:
            识别结果
        """
        try:
            print(f"开始识别装备: {base_image_path} vs {target_image_path}")
            
            # 预处理图像
            base_image = self.preprocess_image(base_image_path)
            target_image = self.preprocess_image(target_image_path)
            
            # 添加调试信息：图像尺寸和基本信息
            if base_image is not None and target_image is not None:
                print(f"  基准图像尺寸: {base_image.shape}")
                print(f"  目标图像尺寸: {target_image.shape}")
                print(f"  目标文件名: {Path(target_image_path).name}")
            
            if base_image is None or target_image is None:
                return AdvancedMatchResult(
                    item_name="Unknown",
                    item_base="Unknown",
                    matched_by=MatchedBy.TEMPLATE_MATCH,
                    min_val=1.0,
                    hist_val=1.0,
                    similarity=0.0,
                    confidence=0.0
                )
            
            # 创建掩码
            mask = None
            if self.enable_masking:
                mask = self.create_mask(base_image)
            
            # 执行模板匹配
            template_match_val, template_match_loc = self.template_match(base_image, target_image, mask)
            
            # 计算颜色相似度
            color_similarity = 0.0
            if self.enable_histogram:
                color_similarity = self.calc_color_similarity(base_image, target_image)
            
            # 计算综合相似度
            # 对于TM_SQDIFF_NORMED，值越小表示匹配越好，所以需要反转
            template_similarity = max(0, (1 - template_match_val) * 100)
            
            # 添加调试信息：匹配详情
            print(f"  🔍 调试信息 - 模板匹配值: {template_match_val:.6f}")
            print(f"  🔍 调试信息 - 模板相似度: {template_similarity:.2f}%")
            print(f"  🔍 调试信息 - 颜色相似度: {color_similarity:.4f}")
            
            # 问题诊断：检查是否存在逻辑矛盾
            # 对于TM_SQDIFF_NORMED，匹配值低表示匹配好，所以条件需要调整
            if template_similarity < 30 and template_match_val < 0.3:
                print(f"  ⚠️ 警告：检测到逻辑矛盾！模板相似度低({template_similarity:.2f}%)但匹配值高({template_match_val:.6f})")
            
            # 更合理的匹配标准：避免过度降权
            # 模板匹配阈值：低于60%认为不匹配
            if template_similarity < 60:
                template_similarity = template_similarity * 0.5  # 适度降低低匹配结果
                print(f"  🔧 调整：模板相似度低于60%，应用降权因子0.5")
            
            # 颜色相似度阈值：低于50%认为不匹配
            if color_similarity < 0.5:
                color_similarity = color_similarity * 0.3  # 适度降低低匹配结果
                print(f"  🔧 调整：颜色相似度低于50%，应用降权因子0.3")
            
            # 改进的得分计算：增加更多区分度
            # 1. 模板匹配得分（主要）
            template_score = template_similarity
            
            # 2. 颜色相似度得分（辅助）
            color_score = color_similarity * 100 if self.enable_histogram else 0
            
            # 3. 增加模板匹配值的权重放大差异
            # 将微小的模板匹配差异放大，但要有区分度
            # 对于TM_SQDIFF_NORMED，值越小越好，所以直接使用template_match_val
            template_diff_factor = template_match_val  # 直接使用匹配值
            template_diff_score = min(100, (1 - template_diff_factor) * 100 * 0.1)  # 转换为相似度并缩放
            
            # 问题诊断：检查差异放大是否过度
            # 对于TM_SQDIFF_NORMED，条件需要调整
            if template_diff_score > 50 and template_similarity < 30:
                print(f"  ⚠️ 警告：差异放大过度！模板相似度低({template_similarity:.2f}%)但差异得分高({template_diff_score:.2f}%)")
            
            # 综合得分计算：
            # - 基础模板匹配：40%
            # - 差异放大得分：30%
            # - 颜色匹配：30%（提高颜色权重）
            if self.enable_histogram:
                combined_score = template_score * 0.4 + template_diff_score * 0.3 + color_score * 0.3
            else:
                combined_score = template_score * 0.7 + template_diff_score * 0.3
            
            # 检查是否有NaN值
            if np.isnan(combined_score):
                print("  ⚠️ 警告：综合得分计算出现NaN值，使用模板相似度")
                combined_score = template_score
            
            # 添加调试信息：综合得分计算
            print(f"  🔍 调试信息 - 模板匹配得分: {template_score:.2f}%")
            print(f"  🔍 调试信息 - 差异放大得分: {template_diff_score:.2f}%")
            print(f"  🔍 调试信息 - 颜色匹配得分: {color_score:.2f}%")
            print(f"  🔍 调试信息 - 综合得分(处理前): {combined_score:.2f}%")
            
            # 确保得分在合理范围内
            combined_score = max(0, min(100, combined_score))
            
            print(f"  综合得分(处理后): {combined_score:.2f}%")
            
            # 确定匹配方式
            if self.enable_histogram and color_similarity > template_similarity * 0.8:
                matched_by = MatchedBy.HISTOGRAM_MATCH
            else:
                matched_by = MatchedBy.TEMPLATE_MATCH
            
            # 创建结果 - 修正：应该使用目标图像的名称，而不是基准图像的名称
            target_name = Path(target_image_path).stem
            result = AdvancedMatchResult(
                item_name=target_name,  # 修正：使用目标图像名称
                item_base=Path(base_image_path).stem,
                matched_by=matched_by,
                min_val=template_match_val,
                hist_val=1 - color_similarity,  # 转换为距离格式
                similarity=template_similarity,
                confidence=combined_score
            )
            
            print(f"识别完成: {result.item_name}, 相似度: {result.similarity:.2f}%, 置信度: {result.confidence:.2f}%")
            print(f"匹配方式: {matched_by.name}")
            
            return result
            
        except Exception as e:
            print(f"装备识别失败: {e}")
            return AdvancedMatchResult(
                item_name="Error",
                item_base="Error",
                matched_by=MatchedBy.TEMPLATE_MATCH,
                min_val=1.0,
                hist_val=1.0,
                similarity=0.0,
                confidence=0.0
            )
    
    def batch_recognize(self, base_image_path: str, target_folder: str, threshold: float = 60.0) -> List[AdvancedMatchResult]:
        """批量识别装备
        
        Args:
            base_image_path: 基准装备图像路径
            target_folder: 目标图像文件夹
            threshold: 相似度阈值
            
        Returns:
            识别结果列表
        """
        results = []
        
        try:
            # 获取所有目标图像
            target_files = []
            for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
                target_files.extend(Path(target_folder).glob(ext))
            
            print(f"找到 {len(target_files)} 个目标图像进行批量识别")
            
            # 对每个目标图像进行识别
            for target_file in target_files:
                result = self.recognize_equipment(base_image_path, str(target_file))
                if result.confidence >= threshold:
                    results.append(result)
            
            # 按置信度排序
            results.sort(key=lambda x: x.confidence, reverse=True)
            
            print(f"批量识别完成，{len(results)} 个结果超过阈值 {threshold}%")
            
            return results
            
        except Exception as e:
            print(f"批量识别失败: {e}")
            return []
    
    def compare_with_traditional(self, base_image_path: str, target_image_path: str, 
                                   traditional_threshold: float = 80.0) -> Dict[str, Any]:
        """与传统dHash算法对比
        
        Args:
            base_image_path: 基准装备图像路径
            target_image_path: 目标图像路径
            traditional_threshold: 传统dHash算法阈值
            
        Returns:
            包含两种算法结果的字典
        """
        try:
            # 使用高级识别器
            advanced_result = self.recognize_equipment(base_image_path, target_image_path)
            
            # 简化的传统dHash实现
            def simple_dhash(image):
                """简化的dHash实现"""
                # 缩放到8x8
                small = cv2.resize(image, (8, 8))
                
                # 计算水平差异
                diff = small[:, 1:] > small[:, :-1]
                
                # 转换为二进制字符串
                dhash = ''.join(['1' if d else '0' for d in diff.flatten()])
                return dhash
            
            def hamming_distance(hash1, hash2):
                """计算汉明距离"""
                return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
            
            def similarity_from_distance(distance):
                """从距离计算相似度"""
                return (64 - distance) / 64 * 100
            
            # 加载图像
            base_img = cv2.imread(base_image_path, cv2.IMREAD_GRAYSCALE)
            target_img = cv2.imread(target_image_path, cv2.IMREAD_GRAYSCALE)
            
            if base_img is None or target_img is None:
                return {
                    'error': '无法加载图像'
                }
            
            # 计算dHash
            base_hash = simple_dhash(base_img)
            target_hash = simple_dhash(target_img)
            
            # 计算汉明距离和相似度
            distance = hamming_distance(base_hash, target_hash)
            traditional_similarity = similarity_from_distance(distance)
            traditional_match = traditional_similarity >= traditional_threshold
            
            # 返回对比结果
            return {
                'advanced_result': advanced_result,
                'traditional_similarity': traditional_similarity,
                'traditional_match': traditional_match,
                'improvement': advanced_result.confidence - traditional_similarity,
                'recommendation': 'advanced' if advanced_result.confidence > traditional_similarity else 'traditional'
            }
            
        except Exception as e:
            return {
                'error': str(e)
            }




def batch_test():
    """批量测试"""
    print("\n" + "=" * 60)
    print("批量识别测试")
    print("=" * 60)
    
    # 创建识别器实例
    recognizer = AdvancedEquipmentRecognizer(enable_masking=True, enable_histogram=True)
    
    # 测试路径
    base_image_path = "images/base_equipment/target_equipment_1.webp"
    target_folder = "images/cropped_equipment"
    
    # 检查文件是否存在
    if not os.path.exists(base_image_path):
        print(f"⚠️ 基准图像不存在: {base_image_path}")
        return
    
    if not os.path.exists(target_folder):
        print(f"⚠️ 目标文件夹不存在: {target_folder}")
        return
    
    # 执行批量识别
    results = recognizer.batch_recognize(base_image_path, target_folder, threshold=60.0)
    
    # 输出结果
    print(f"\n批量识别结果 (阈值: 60.0%):")
    print(f"匹配数量: {len(results)}")
    
    if results:
        print("\n匹配结果:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.item_name} - 置信度: {result.confidence:.2f}%")
    else:
        print("没有找到匹配的装备")


def comprehensive_test():
    """综合测试：测试所有基准装备图"""
    print("=" * 80)
    print("综合装备识别测试")
    print("=" * 80)
    
    # 创建识别器实例
    recognizer = AdvancedEquipmentRecognizer(enable_masking=True, enable_histogram=True)
    
    # 获取所有基准装备图
    base_folder = "images/base_equipment"
    target_folder = "images/cropped_equipment"
    
    # 查找最新的时间目录
    target_dir = target_folder
    cropped_dir = Path(target_folder)
    if cropped_dir.exists():
        subdirs = [d for d in cropped_dir.iterdir() if d.is_dir() and d.name.replace('_', '').replace(':', '').isdigit()]
        if subdirs:
            # 使用最新的时间目录
            latest_dir = sorted(subdirs)[-1]
            target_dir = str(latest_dir)
            print(f"使用最新的时间目录: {latest_dir.name}")
    
    base_files = []
    for ext in ['*.webp', '*.png', '*.jpg', '*.jpeg']:
        base_files.extend(Path(base_folder).glob(ext))
    
    print(f"找到 {len(base_files)} 个基准装备图")
    print(f"目标文件夹: {target_dir}")
    print("\n" + "=" * 80)
    
    # 对每个基准装备图进行测试
    for base_file in base_files:
        base_path = str(base_file)
        base_name = base_file.stem
        
        print(f"\n🎯 测试基准装备: {base_name}")
        print(f"   路径: {base_path}")
        print("-" * 60)
        
        # 执行批量识别（降低阈值以显示所有结果）
        results = recognizer.batch_recognize(base_path, target_dir, threshold=20.0)
        
        # 输出详细结果
        print(f"\n📊 {base_name} 识别结果汇总:")
        print(f"   匹配数量: {len(results)}")
        
        if results:
            print(f"   匹配装备名称: {', '.join([r.item_name for r in results])}")
            print(f"   最佳匹配: {results[0].item_name} (置信度: {results[0].confidence:.2f}%)")
            
            print(f"\n📋 详细匹配列表:")
            for i, result in enumerate(results, 1):
                print(f"   {i:2d}. {result.item_name:15s} - 置信度: {result.confidence:6.2f}% - "
                      f"模板: {result.similarity:5.2f}% - 颜色: {(1-result.hist_val)*100:5.2f}%")
        else:
            print("   ❌ 没有找到匹配的装备")
        
        print("\n" + "=" * 80)
    
    print("🎉 综合测试完成！")


if __name__ == "__main__":
    print("独立高级装备识别器")
    print("实现模板匹配与辅助验证机制结合的识别方法")
    print("=" * 60)
    
    # 选择测试模式
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--comprehensive":
        # 综合测试模式
        comprehensive_test()
    else:
        # 原有的单个测试模式
        # 测试单个识别
        test_standalone_matcher()
        
        print("\n" + "=" * 60)
        
        # 测试批量识别
        batch_test()
        
        print("\n" + "=" * 60)
        print("测试完成！")
        
        print("\n💡 提示: 使用 'python src/advanced_matcher_standalone.py --comprehensive' 进行综合测试")