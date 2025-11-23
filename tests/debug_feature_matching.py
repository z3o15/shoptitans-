#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试特征匹配 - 测试匹配算法是否正常工作
"""

import cv2
import numpy as np
from PIL import Image
import os
import sys

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.feature_matcher import FeatureEquipmentRecognizer, FeatureType

def test_simple_matching():
    """测试简单特征匹配"""
    print("=" * 60)
    print("调试特征匹配")
    print("=" * 60)
    
    # 创建识别器
    recognizer = FeatureEquipmentRecognizer(
        feature_type=FeatureType.ORB,
        min_match_count=1,  # 设置为1，只看能否找到任何匹配
        match_ratio_threshold=0.9,  # 更宽松的比例阈值
        min_homography_inliers=1
    )
    
    # 测试同一图像的匹配（应该有很多匹配）
    base_dir = "images/base_equipment"
    if not os.path.exists(base_dir):
        print("❌ 基准装备目录不存在")
        return
    
    # 获取测试图像
    equipment_files = [f for f in os.listdir(base_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    if len(equipment_files) < 1:
        print("❌ 需要至少1个基准装备图像进行测试")
        return
    
    # 测试同一图像的自匹配
    test_file = equipment_files[0]
    test_path = os.path.join(base_dir, test_file)
    
    print(f"测试图像: {test_file}")
    
    # 预处理图像
    image = recognizer.preprocess_image(test_path)
    if image is None:
        print("❌ 图像预处理失败")
        return
    
    # 提取特征
    kp1, desc1 = recognizer.extract_features(image)
    kp2, desc2 = recognizer.extract_features(image)  # 同一张图
    
    print(f"特征点数量: {len(kp1)}")
    
    if desc1 is None or desc2 is None:
        print("❌ 特征描述符为空")
        return
    
    # 匹配特征
    matches = recognizer.match_features(desc1, desc2)
    print(f"自匹配数量: {len(matches)}")
    
    # 显示前几个匹配的距离信息
    if matches:
        print("前5个匹配的距离:")
        for i, match in enumerate(matches[:5]):
            print(f"  匹配 {i+1}: 距离 = {match.distance}")
    
    # 测试两个不同图像的匹配
    if len(equipment_files) >= 2:
        test_file2 = equipment_files[1]
        test_path2 = os.path.join(base_dir, test_file2)
        
        print(f"\n测试图像2: {test_file2}")
        
        # 预处理图像
        image2 = recognizer.preprocess_image(test_path2)
        if image2 is None:
            print("❌ 图像2预处理失败")
            return
        
        # 提取特征
        kp3, desc3 = recognizer.extract_features(image2)
        
        print(f"特征点数量: {len(kp3)}")
        
        if desc3 is None:
            print("❌ 特征描述符2为空")
            return
        
        # 匹配特征
        matches2 = recognizer.match_features(desc1, desc3)
        print(f"不同图像匹配数量: {len(matches2)}")
        
        # 显示前几个匹配的距离信息
        if matches2:
            print("前5个匹配的距离:")
            for i, match in enumerate(matches2[:5]):
                print(f"  匹配 {i+1}: 距离 = {match.distance}")

if __name__ == "__main__":
    test_simple_matching()