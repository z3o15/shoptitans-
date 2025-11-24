#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强特征匹配器 - 集成特征缓存功能的ORB特征匹配器
继承自FeatureEquipmentRecognizer，添加缓存支持，显著提升性能
"""

import cv2
import numpy as np
from PIL import Image
import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

# 导入特征缓存管理器
from src.cache.feature_cache_manager import FeatureCacheManager

# 导入原始特征匹配器
from src.core.feature_matcher import (
    FeatureType,
    FeatureMatchResult,
    FeatureEquipmentRecognizer
)

class EnhancedFeatureEquipmentRecognizer(FeatureEquipmentRecognizer):
    """增强的特征匹配器，支持特征缓存
    
    继承自FeatureEquipmentRecognizer，添加缓存支持，
    优先使用预计算的基准装备特征，避免重复计算
    """
    
    def __init__(self, feature_type: FeatureType = FeatureType.ORB, 
                 min_match_count: int = 10, match_ratio_threshold: float = 0.75,
                 min_homography_inliers: int = 8, use_cache=True,
                 cache_dir="images/cache", target_size=(116, 116), nfeatures=1000):
        """
        初始化增强特征匹配识别器
        
        Args:
            feature_type: 特征提取算法类型
            min_match_count: 最少特征匹配数量
            match_ratio_threshold: 匹配比例阈值
            min_homography_inliers: 最小单应性内点数量
            use_cache: 是否使用特征缓存
            cache_dir: 缓存目录路径
            target_size: 目标图像尺寸
            nfeatures: ORB特征点数量
        """
        # 先设置子类属性，再调用父类初始化
        self.use_cache = use_cache
        self.target_size = target_size
        self.nfeatures = nfeatures
        
        # 调用父类初始化
        super().__init__(feature_type, min_match_count, match_ratio_threshold, min_homography_inliers)
        
        # 简化输出，不显示初始化信息
        
        if use_cache:
            self.cache_manager = FeatureCacheManager(
                cache_dir=cache_dir, 
                target_size=target_size, 
                nfeatures=nfeatures
            )
            cache_loaded = self.cache_manager.load_feature_cache()
            if cache_loaded and self.cache_manager.is_cache_valid():
                pass  # 简化输出
            else:
                self.use_cache = False
        else:
            self.cache_manager = None
        
        # 创建标准尺寸的检测器（用于目标图像）
        self.standard_detector = self._create_detector()
    
    def _create_detector(self):
        """创建增强的特征检测器"""
        if self.feature_type == FeatureType.SIFT:
            return cv2.SIFT_create()
        elif self.feature_type == FeatureType.ORB:
            return cv2.ORB_create(
                nfeatures=self.nfeatures,  # 使用配置的特征点数量
                scaleFactor=1.1,
                edgeThreshold=15,
                patchSize=31
            )
        elif self.feature_type == FeatureType.AKAZE:
            return cv2.AKAZE_create()
        else:
            raise ValueError(f"不支持的特征类型: {self.feature_type}")
    
    def build_cache_if_needed(self, base_equipment_dir):
        """
        如果需要，构建特征缓存
        
        Args:
            base_equipment_dir: 基准装备目录路径
            
        Returns:
            bool: 构建是否成功
        """
        if not self.cache_manager:
            print("缓存管理器未初始化")
            return False
        
        if self.cache_manager.is_cache_valid():
            return True
        
        # 简化输出
        success = self.cache_manager.build_feature_cache(base_equipment_dir)
        
        if success:
            # 重新加载缓存
            self.cache_manager.load_feature_cache()
            if self.cache_manager.is_cache_valid():
                self.use_cache = True
                print("✓ 特征缓存构建并加载成功")
            else:
                self.use_cache = False
                print("❌ 特征缓存构建后验证失败")
        else:
            self.use_cache = False
            print("❌ 特征缓存构建失败")
        
        return success
    
    def recognize_equipment(self, base_image_path: str, target_image_path: str) -> FeatureMatchResult:
        """
        识别装备 - 优先使用缓存特征
        
        Args:
            base_image_path: 基准装备图像路径
            target_image_path: 目标图像路径
            
        Returns:
            特征匹配结果
        """
        try:
            # 获取基准装备名称
            base_name = os.path.splitext(os.path.basename(base_image_path))[0]
            
            # 如果启用缓存且缓存有效，使用缓存特征
            if self.use_cache and self.cache_manager and self.cache_manager.is_cache_valid():
                return self._recognize_with_cache(base_name, target_image_path)
            else:
                # 回退到原始方法
                return self._recognize_with_extraction(base_image_path, target_image_path)
                
        except Exception as e:
            print(f"特征匹配识别失败: {e}")
            return FeatureMatchResult(
                item_name=Path(target_image_path).stem,
                item_base=Path(base_image_path).stem,
                match_count=0,
                good_match_count=0,
                match_ratio=0.0,
                confidence=0.0,
                homography_inliers=0,
                algorithm_used=self.feature_type.value,
                is_valid_match=False
            )
    
    def _recognize_with_cache(self, base_name: str, target_image_path: str) -> FeatureMatchResult:
        """
        使用缓存特征进行识别
        
        Args:
            base_name: 基准装备名称（不含扩展名）
            target_image_path: 目标图像路径
            
        Returns:
            特征匹配结果
        """
        try:
            # 简化输出，不显示每个匹配的详细信息
            
            # 从缓存获取基准特征
            kp1, desc1 = self.cache_manager.get_cached_features(base_name)
            
            if kp1 is None or desc1 is None:
                # 简化错误输出
                # 回退到原始方法
                return self._recognize_with_extraction(f"{base_name}.webp", target_image_path)
            
            # 预处理目标图像
            target_image = self.preprocess_image(target_image_path, standardize_size=True)
            
            if target_image is None:
                return self._create_failure_result(base_name, target_image_path)
            
            # 简化特征点信息输出
            
            # 提取目标图像特征
            kp2, desc2 = self.extract_features(target_image)
            
            if desc2 is None or len(kp2) < 10:
                # 简化错误输出
                return self._create_failure_result(base_name, target_image_path)
            
            # 匹配特征
            matches = self.match_features(desc1, desc2)
            match_count = len(matches)
            
            if match_count < self.min_match_count:
                # 简化错误输出
                return self._create_failure_result(base_name, target_image_path, match_count)
            
            # 验证单应性
            homography_inliers, is_valid = self.verify_homography(kp1, kp2, matches)
            
            # 简化几何一致性输出
            
            # 计算置信度
            confidence = self.calculate_confidence(match_count, match_count, homography_inliers)
            
            # 计算匹配比例
            match_ratio = match_count / max(len(kp1), len(kp2))
            
            # 简化匹配比例和置信度输出
            
            # 创建结果
            result = FeatureMatchResult(
                item_name=Path(target_image_path).stem,
                item_base=base_name,
                match_count=match_count,
                good_match_count=match_count,
                match_ratio=match_ratio,
                confidence=confidence,
                homography_inliers=homography_inliers,
                algorithm_used=f"{self.feature_type.value}_cached",
                is_valid_match=is_valid and confidence >= 60  # 60%置信度阈值
            )
            
            # 简化输出，不显示每个匹配结果
            
            return result
            
        except Exception as e:
            # 简化错误输出
            return self._create_failure_result(base_name, target_image_path)
    
    def _recognize_with_extraction(self, base_image_path: str, target_image_path: str) -> FeatureMatchResult:
        """
        使用原始特征提取方法进行识别
        
        Args:
            base_image_path: 基准装备图像路径
            target_image_path: 目标图像路径
            
        Returns:
            特征匹配结果
        """
        try:
            print(f"开始原始特征匹配: {base_image_path} vs {target_image_path}")
            
            # 预处理图像
            base_image = self.preprocess_image(base_image_path, standardize_size=True)
            target_image = self.preprocess_image(target_image_path, standardize_size=True)
            
            if base_image is None or target_image is None:
                return self._create_failure_result(
                    Path(base_image_path).stem, 
                    target_image_path
                )
            
            print(f"  基准图像尺寸: {base_image.shape}")
            print(f"  目标图像尺寸: {target_image.shape}")
            
            # 提取特征
            kp1, desc1 = self.extract_features(base_image)
            kp2, desc2 = self.extract_features(target_image)
            
            print(f"  基准图像特征点: {len(kp1)}")
            print(f"  目标图像特征点: {len(kp2)}")
            
            if desc1 is None or desc2 is None or len(kp1) < 10 or len(kp2) < 10:
                print("  ❌ 特征点不足，无法进行有效匹配")
                return self._create_failure_result(
                    Path(base_image_path).stem, 
                    target_image_path
                )
            
            # 匹配特征
            matches = self.match_features(desc1, desc2)
            match_count = len(matches)
            
            print(f"  初步匹配数量: {match_count}")
            
            if match_count < self.min_match_count:
                print(f"  ❌ 匹配数量不足（最少需要{self.min_match_count}个）")
                return self._create_failure_result(
                    Path(base_image_path).stem, 
                    target_image_path, 
                    match_count
                )
            
            # 验证单应性
            homography_inliers, is_valid = self.verify_homography(kp1, kp2, matches)
            
            print(f"  单应性内点: {homography_inliers}")
            print(f"  几何一致性: {'✓ 有效' if is_valid else '❌ 无效'}")
            
            # 计算置信度
            confidence = self.calculate_confidence(match_count, match_count, homography_inliers)
            
            # 计算匹配比例
            match_ratio = match_count / max(len(kp1), len(kp2))
            
            print(f"  匹配比例: {match_ratio:.4f}")
            print(f"  置信度: {confidence:.2f}%")
            
            # 创建结果
            result = FeatureMatchResult(
                item_name=Path(target_image_path).stem,
                item_base=Path(base_image_path).stem,
                match_count=match_count,
                good_match_count=match_count,
                match_ratio=match_ratio,
                confidence=confidence,
                homography_inliers=homography_inliers,
                algorithm_used=f"{self.feature_type.value}_extracted",
                is_valid_match=is_valid and confidence >= 60  # 60%置信度阈值
            )
            
            print(f"识别完成: {result.item_name}, 置信度: {result.confidence:.2f}%, 有效匹配: {result.is_valid_match}")
            
            return result
            
        except Exception as e:
            print(f"原始特征匹配失败: {e}")
            return self._create_failure_result(
                Path(base_image_path).stem, 
                target_image_path
            )
    
    def preprocess_image(self, image_path: str, standardize_size=True) -> Optional[np.ndarray]:
        """
        预处理图像，可选标准化尺寸
        
        Args:
            image_path: 图像路径
            standardize_size: 是否标准化尺寸
            
        Returns:
            预处理后的灰度图像数组
        """
        try:
            # 加载图像
            # 确保路径格式正确
            image_path = os.path.normpath(image_path)
            image = Image.open(image_path)
            
            # 转换为RGB格式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 转换为numpy数组
            image_array = np.array(image)
            
            # 转换为灰度图（特征匹配通常使用灰度图）
            if len(image_array.shape) == 3:
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = image_array
            
            # 应用预处理增强（针对游戏装备图标）
            # 1. 直方图均衡化增强对比度
            gray = cv2.equalizeHist(gray)
            
            # 2. 高斯模糊减少噪声
            blur = cv2.GaussianBlur(gray, (3,3), 0)
            
            # 3. Canny边缘检测增强特征
            enhanced = cv2.Canny(blur, 30, 120)
            
            # 对于游戏装备图标，使用Canny边缘检测结果
            # 如果特征点仍然太少，可以回退到使用增强后的灰度图
            processed = enhanced
            
            # 标准化尺寸（如果需要）
            if standardize_size:
                processed = self._standardize_image_size(processed)
            
            return processed
            
        except Exception as e:
            print(f"图像预处理失败 {image_path}: {e}")
            return None
    
    def _standardize_image_size(self, image):
        """
        标准化图像尺寸到目标尺寸
        
        Args:
            image: 输入图像
            
        Returns:
            调整尺寸后的图像
        """
        if image.shape[:2] == self.target_size:
            return image
        
        # 使用INTER_AREA保持图像质量
        return cv2.resize(image, self.target_size, interpolation=cv2.INTER_AREA)
    
    def _create_failure_result(self, base_name: str, target_image_path: str, match_count=0):
        """
        创建失败结果
        
        Args:
            base_name: 基准装备名称
            target_image_path: 目标图像路径
            match_count: 匹配数量（默认为0）
            
        Returns:
            特征匹配结果（失败状态）
        """
        return FeatureMatchResult(
            item_name=Path(target_image_path).stem,
            item_base=base_name,
            match_count=match_count,
            good_match_count=0,
            match_ratio=0.0,
            confidence=0.0,
            homography_inliers=0,
            algorithm_used=self.feature_type.value,
            is_valid_match=False
        )
    
    def get_cache_info(self):
        """
        获取缓存信息
        
        Returns:
            Dict[str, Any]: 缓存信息字典
        """
        if self.cache_manager:
            return self.cache_manager.get_cache_info()
        else:
            return {"valid": False, "message": "缓存管理器未初始化"}
    
    def batch_recognize_with_cache(self, base_image_path: str, target_folder: str, 
                                 threshold: float = 60.0) -> List[FeatureMatchResult]:
        """
        批量识别装备（使用缓存）
        
        Args:
            base_image_path: 基准装备图像路径
            target_folder: 目标图像文件夹
            threshold: 置信度阈值
            
        Returns:
            识别结果列表
        """
        results = []
        
        try:
            # 获取基准装备名称
            base_name = os.path.splitext(os.path.basename(base_image_path))[0]
            
            # 如果使用缓存，从缓存获取基准特征
            if self.use_cache and self.cache_manager and self.cache_manager.is_cache_valid():
                kp1, desc1 = self.cache_manager.get_cached_features(base_name)
                
                if kp1 is None or desc1 is None:
                    print(f"缓存中未找到装备: {base_name}")
                    return []
                
                # 获取所有目标图像
                target_files = []
                for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
                    target_files.extend(Path(target_folder).glob(ext))
                
                print(f"找到 {len(target_files)} 个目标图像进行批量特征识别（使用缓存）")
                
                # 对每个目标图像进行识别
                for target_file in target_files:
                    result = self._recognize_single_with_cache(
                        base_name, kp1, desc1, str(target_file)
                    )
                    if result.confidence >= threshold:
                        results.append(result)
            else:
                # 回退到原始批量识别方法
                return self.batch_recognize(base_image_path, target_folder, threshold)
            
            # 按置信度排序
            results.sort(key=lambda x: x.confidence, reverse=True)
            
            print(f"批量特征识别完成，{len(results)} 个结果超过阈值 {threshold}%")
            
            return results
            
        except Exception as e:
            print(f"批量特征识别失败: {e}")
            return []
    
    def _recognize_single_with_cache(self, base_name: str, kp1: List, desc1: np.ndarray, 
                                  target_image_path: str) -> FeatureMatchResult:
        """
        使用缓存特征进行单个图像识别
        
        Args:
            base_name: 基准装备名称
            kp1: 基准图像关键点
            desc1: 基准图像描述符
            target_image_path: 目标图像路径
            
        Returns:
            特征匹配结果
        """
        try:
            # 预处理目标图像
            target_image = self.preprocess_image(target_image_path, standardize_size=True)
            
            if target_image is None:
                return self._create_failure_result(base_name, target_image_path)
            
            # 提取目标图像特征
            kp2, desc2 = self.extract_features(target_image)
            
            if desc2 is None or len(kp2) < 10:
                return self._create_failure_result(base_name, target_image_path)
            
            # 匹配特征
            matches = self.match_features(desc1, desc2)
            match_count = len(matches)
            
            if match_count < self.min_match_count:
                return self._create_failure_result(base_name, target_image_path, match_count)
            
            # 验证单应性
            homography_inliers, is_valid = self.verify_homography(kp1, kp2, matches)
            
            # 计算置信度
            confidence = self.calculate_confidence(match_count, match_count, homography_inliers)
            
            # 计算匹配比例
            match_ratio = match_count / max(len(kp1), len(kp2))
            
            # 创建结果
            result = FeatureMatchResult(
                item_name=Path(target_image_path).stem,
                item_base=base_name,
                match_count=match_count,
                good_match_count=match_count,
                match_ratio=match_ratio,
                confidence=confidence,
                homography_inliers=homography_inliers,
                algorithm_used=f"{self.feature_type.value}_cached",
                is_valid_match=is_valid and confidence >= 60  # 60%置信度阈值
            )
            
            return result
            
        except Exception as e:
            print(f"单个图像识别失败: {e}")
            return self._create_failure_result(base_name, target_image_path)
 

# 为了向后兼容，创建别名
class EnhancedFeatureMatcher(EnhancedFeatureEquipmentRecognizer):
    """增强特征匹配器的兼容性包装器"""
    
    def __init__(self, cache_manager=None, use_cache=True, **kwargs):
        """
        初始化增强特征匹配器（兼容性包装器）
        
        Args:
            cache_manager: 缓存管理器实例（为了兼容性，忽略此参数）
            use_cache: 是否使用缓存
            **kwargs: 其他参数
        """
        # 调用父类初始化
        super().__init__(use_cache=use_cache, **kwargs)
 

# 为了向后兼容，已创建EnhancedFeatureMatcher类

if __name__ == "__main__":
    # 示例用法
    pass
