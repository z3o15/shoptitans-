#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
特征匹配器 - 使用SIFT/ORB算法进行装备识别
替代模板匹配，提供更准确的形状和结构特征匹配
"""

import cv2
import numpy as np
from PIL import Image
import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class FeatureType(Enum):
    """特征类型枚举"""
    SIFT = "SIFT"
    ORB = "ORB"
    AKAZE = "AKAZE"


@dataclass
class FeatureMatchResult:
    """特征匹配结果数据类"""
    item_name: str
    item_base: str
    match_count: int
    good_match_count: int
    match_ratio: float
    confidence: float
    homography_inliers: int
    algorithm_used: str
    is_valid_match: bool


class FeatureEquipmentRecognizer:
    """基于特征匹配的装备识别器
    
    使用SIFT/ORB等特征提取算法，通过关键点匹配进行装备识别
    相比模板匹配，能更好地处理形状、结构差异
    """
    
    def __init__(self, feature_type: FeatureType = FeatureType.ORB, 
                 min_match_count: int = 10, match_ratio_threshold: float = 0.75,
                 min_homography_inliers: int = 8):
        """初始化特征匹配识别器
        
        Args:
            feature_type: 特征提取算法类型
            min_match_count: 最少特征匹配数量
            match_ratio_threshold: 匹配比例阈值
            min_homography_inliers: 最小单应性内点数量
        """
        self.feature_type = feature_type
        self.min_match_count = min_match_count
        self.match_ratio_threshold = match_ratio_threshold
        self.min_homography_inliers = min_homography_inliers
        
        # 初始化特征检测器
        self.detector = self._create_detector()
        
        print(f"✓ 特征匹配识别器初始化完成")
        print(f"  - 特征算法: {feature_type.value}")
        print(f"  - 最少匹配数: {min_match_count}")
        print(f"  - 匹配比例阈值: {match_ratio_threshold}")
        print(f"  - 最小单应性内点: {min_homography_inliers}")
    
    def _create_detector(self):
        """创建特征检测器"""
        if self.feature_type == FeatureType.SIFT:
            return cv2.SIFT_create()
        elif self.feature_type == FeatureType.ORB:
            return cv2.ORB_create(nfeatures=1000)
        elif self.feature_type == FeatureType.AKAZE:
            return cv2.AKAZE_create()
        else:
            raise ValueError(f"不支持的特征类型: {self.feature_type}")
    
    def preprocess_image(self, image_path: str) -> Optional[np.ndarray]:
        """预处理图像
        
        Args:
            image_path: 图像路径
            
        Returns:
            预处理后的灰度图像数组
        """
        try:
            # 加载图像
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
            
            return gray
            
        except Exception as e:
            print(f"图像预处理失败 {image_path}: {e}")
            return None
    
    def extract_features(self, image: np.ndarray) -> Tuple[List, np.ndarray]:
        """提取图像特征
        
        Args:
            image: 输入图像（灰度）
            
        Returns:
            (关键点列表, 描述符数组) 的元组
        """
        try:
            keypoints, descriptors = self.detector.detectAndCompute(image, None)
            return keypoints, descriptors
        except Exception as e:
            print(f"特征提取失败: {e}")
            return [], None
    
    def match_features(self, desc1: np.ndarray, desc2: np.ndarray) -> List:
        """匹配两组特征描述符
        
        Args:
            desc1: 第一组描述符
            desc2: 第二组描述符
            
        Returns:
            匹配结果列表
        """
        if desc1 is None or desc2 is None:
            return []
        
        try:
            # 根据特征类型选择匹配器
            if self.feature_type == FeatureType.SIFT:
                matcher = cv2.BFMatcher(cv2.NORM_L2)
            else:  # ORB, AKAZE使用汉明距离
                matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
            
            # 使用k近邻匹配（k=2）
            matches = matcher.knnMatch(desc1, desc2, k=2)
            
            # 应用比例测试筛选好的匹配
            good_matches = []
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance < self.match_ratio_threshold * n.distance:
                        good_matches.append(m)
            
            return good_matches
            
        except Exception as e:
            print(f"特征匹配失败: {e}")
            return []
    
    def verify_homography(self, kp1: List, kp2: List, matches: List) -> Tuple[int, bool]:
        """使用单应性矩阵验证匹配质量
        
        Args:
            kp1: 第一张图的关键点
            kp2: 第二张图的关键点
            matches: 匹配结果
            
        Returns:
            (内点数量, 是否有效匹配) 的元组
        """
        if len(matches) < 4:  # 单应性矩阵至少需要4个点
            return 0, False
        
        try:
            # 提取匹配点坐标
            src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
            
            # 计算单应性矩阵
            homography, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            
            if homography is None:
                return 0, False
            
            # 计算内点数量
            inlier_count = np.sum(mask)
            
            return int(inlier_count), inlier_count >= self.min_homography_inliers
            
        except Exception as e:
            print(f"单应性验证失败: {e}")
            return 0, False
    
    def calculate_confidence(self, match_count: int, good_match_count: int, 
                          homography_inliers: int) -> float:
        """计算匹配置信度
        
        Args:
            match_count: 总匹配数量
            good_match_count: 好匹配数量
            homography_inliers: 单应性内点数量
            
        Returns:
            置信度分数（0-100）
        """
        if match_count == 0:
            return 0.0
        
        # 1. 好匹配比例（40%权重）
        good_match_ratio = good_match_count / max(match_count, 1)
        good_score = min(100, good_match_ratio * 100)
        
        # 2. 单应性内点比例（40%权重）
        homography_ratio = homography_inliers / max(good_match_count, 1)
        homography_score = min(100, homography_ratio * 100)
        
        # 3. 绝对匹配数量（20%权重）
        count_score = min(100, (good_match_count / 50) * 100)  # 假设50个匹配为满分
        
        # 综合得分
        confidence = good_score * 0.4 + homography_score * 0.4 + count_score * 0.2
        
        return round(confidence, 2)
    
    def recognize_equipment(self, base_image_path: str, target_image_path: str) -> FeatureMatchResult:
        """识别装备
        
        Args:
            base_image_path: 基准装备图像路径
            target_image_path: 目标图像路径
            
        Returns:
            特征匹配结果
        """
        try:
            print(f"开始特征匹配: {base_image_path} vs {target_image_path}")
            
            # 预处理图像
            base_image = self.preprocess_image(base_image_path)
            target_image = self.preprocess_image(target_image_path)
            
            if base_image is None or target_image is None:
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
            
            print(f"  基准图像尺寸: {base_image.shape}")
            print(f"  目标图像尺寸: {target_image.shape}")
            
            # 提取特征
            kp1, desc1 = self.extract_features(base_image)
            kp2, desc2 = self.extract_features(target_image)
            
            print(f"  基准图像特征点: {len(kp1)}")
            print(f"  目标图像特征点: {len(kp2)}")
            
            if desc1 is None or desc2 is None or len(kp1) < 10 or len(kp2) < 10:
                print("  ❌ 特征点不足，无法进行有效匹配")
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
            
            # 匹配特征
            matches = self.match_features(desc1, desc2)
            match_count = len(matches)
            
            print(f"  初步匹配数量: {match_count}")
            
            if match_count < self.min_match_count:
                print(f"  ❌ 匹配数量不足（最少需要{self.min_match_count}个）")
                return FeatureMatchResult(
                    item_name=Path(target_image_path).stem,
                    item_base=Path(base_image_path).stem,
                    match_count=match_count,
                    good_match_count=0,
                    match_ratio=0.0,
                    confidence=0.0,
                    homography_inliers=0,
                    algorithm_used=self.feature_type.value,
                    is_valid_match=False
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
                algorithm_used=self.feature_type.value,
                is_valid_match=is_valid and confidence >= 60  # 60%置信度阈值
            )
            
            print(f"识别完成: {result.item_name}, 置信度: {result.confidence:.2f}%, 有效匹配: {result.is_valid_match}")
            
            return result
            
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
    
    def batch_recognize(self, base_image_path: str, target_folder: str, 
                       threshold: float = 60.0) -> List[FeatureMatchResult]:
        """批量识别装备
        
        Args:
            base_image_path: 基准装备图像路径
            target_folder: 目标图像文件夹
            threshold: 置信度阈值
            
        Returns:
            识别结果列表
        """
        results = []
        
        try:
            # 获取所有目标图像
            target_files = []
            for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
                target_files.extend(Path(target_folder).glob(ext))
            
            print(f"找到 {len(target_files)} 个目标图像进行批量特征识别")
            
            # 对每个目标图像进行识别
            for target_file in target_files:
                result = self.recognize_equipment(base_image_path, str(target_file))
                if result.confidence >= threshold:
                    results.append(result)
            
            # 按置信度排序
            results.sort(key=lambda x: x.confidence, reverse=True)
            
            print(f"批量特征识别完成，{len(results)} 个结果超过阈值 {threshold}%")
            
            return results
            
        except Exception as e:
            print(f"批量特征识别失败: {e}")
            return []


def test_feature_matcher():
    """测试特征匹配器"""
    print("=" * 60)
    print("特征匹配器测试")
    print("=" * 60)
    
    # 创建识别器实例
    recognizer = FeatureEquipmentRecognizer(
        feature_type=FeatureType.ORB,
        min_match_count=8,
        match_ratio_threshold=0.75,
        min_homography_inliers=6
    )
    
    # 测试图像路径
    base_image_path = "images/base_equipment/noblering.webp"
    target_image_path = "images/cropped_equipment/20251122_160114/08.png"
    
    # 检查文件是否存在
    if not os.path.exists(base_image_path):
        print(f"⚠️ 基准图像不存在: {base_image_path}")
        return
    
    if not os.path.exists(target_image_path):
        print(f"⚠️ 目标图像不存在: {target_image_path}")
        return
    
    # 执行识别
    result = recognizer.recognize_equipment(base_image_path, target_image_path)
    
    # 输出结果
    print("\n识别结果:")
    print(f"装备名称: {result.item_name}")
    print(f"匹配数量: {result.match_count}")
    print(f"匹配比例: {result.match_ratio:.4f}")
    print(f"单应性内点: {result.homography_inliers}")
    print(f"置信度: {result.confidence:.2f}%")
    print(f"有效匹配: {result.is_valid_match}")
    print(f"使用算法: {result.algorithm_used}")


if __name__ == "__main__":
    test_feature_matcher()