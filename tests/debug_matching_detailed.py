#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细调试特征匹配问题
分析为什么特征匹配数量为0
"""

import cv2
import numpy as np
from PIL import Image
import os
from pathlib import Path

# 导入特征匹配相关模块
from src.feature_matcher import FeatureEquipmentRecognizer, FeatureType
from src.feature_cache_manager import FeatureCacheManager

def debug_feature_matching_detailed():
    """详细调试特征匹配问题"""
    print("=== 详细调试特征匹配问题 ===\n")
    
    # 测试图像路径
    base_image_path = "images/base_equipment/1000bp.webp"
    target_image_path = "images/base_equipment/abyssal.webp"
    
    if not os.path.exists(base_image_path) or not os.path.exists(target_image_path):
        print("❌ 测试图像不存在")
        return
    
    print(f"基准图像: {base_image_path}")
    print(f"目标图像: {target_image_path}\n")
    
    # 1. 加载并显示原始图像信息
    print("1. 原始图像信息:")
    base_image_pil = Image.open(base_image_path)
    target_image_pil = Image.open(target_image_path)
    
    print(f"  基准图像尺寸: {base_image_pil.size}, 模式: {base_image_pil.mode}")
    print(f"  目标图像尺寸: {target_image_pil.size}, 模式: {target_image_pil.mode}")
    
    # 转换为numpy数组
    base_array = np.array(base_image_pil)
    target_array = np.array(target_image_pil)
    
    print(f"  基准数组形状: {base_array.shape}")
    print(f"  目标数组形状: {target_array.shape}\n")
    
    # 2. 转换为灰度图
    print("2. 灰度转换:")
    if len(base_array.shape) == 3:
        base_gray = cv2.cvtColor(base_array, cv2.COLOR_RGB2GRAY)
    else:
        base_gray = base_array
    
    if len(target_array.shape) == 3:
        target_gray = cv2.cvtColor(target_array, cv2.COLOR_RGB2GRAY)
    else:
        target_gray = target_array
    
    print(f"  基准灰度图形状: {base_gray.shape}")
    print(f"  目标灰度图形状: {target_gray.shape}")
    print(f"  基准灰度图数据类型: {base_gray.dtype}, 范围: [{base_gray.min()}, {base_gray.max()}]")
    print(f"  目标灰度图数据类型: {target_gray.dtype}, 范围: [{target_gray.min()}, {target_gray.max()}]\n")
    
    # 3. 标准化尺寸
    print("3. 标准化尺寸:")
    target_size = (116, 116)
    
    base_resized = cv2.resize(base_gray, target_size, interpolation=cv2.INTER_AREA)
    target_resized = cv2.resize(target_gray, target_size, interpolation=cv2.INTER_AREA)
    
    print(f"  调整后基准图形状: {base_resized.shape}")
    print(f"  调整后目标图形状: {target_resized.shape}\n")
    
    # 4. 创建ORB检测器并提取特征
    print("4. 特征提取:")
    nfeatures = 1000
    orb = cv2.ORB_create(nfeatures=nfeatures)
    
    # 提取基准图像特征
    kp1, desc1 = orb.detectAndCompute(base_resized, None)
    print(f"  基准图像关键点数量: {len(kp1)}")
    print(f"  基准图像描述符形状: {desc1.shape if desc1 is not None else 'None'}")
    
    # 提取目标图像特征
    kp2, desc2 = orb.detectAndCompute(target_resized, None)
    print(f"  目标图像关键点数量: {len(kp2)}")
    print(f"  目标图像描述符形状: {desc2.shape if desc2 is not None else 'None'}\n")
    
    if desc1 is None or desc2 is None:
        print("❌ 描述符为空，无法进行匹配")
        return
    
    # 5. 分析描述符
    print("5. 描述符分析:")
    print(f"  基准描述符数据类型: {desc1.dtype}")
    print(f"  目标描述符数据类型: {desc2.dtype}")
    print(f"  基准描述符范围: [{desc1.min()}, {desc1.max()}]")
    print(f"  目标描述符范围: [{desc2.min()}, {desc2.max()}]")
    print(f"  基准描述符样本: {desc1[0] if len(desc1) > 0 else 'None'}")
    print(f"  目标描述符样本: {desc2[0] if len(desc2) > 0 else 'None'}\n")
    
    # 6. 尝试不同的匹配方法
    print("6. 特征匹配测试:")
    
    # 6.1 暴力匹配器
    print("  6.1 暴力匹配器:")
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(desc1, desc2)
    print(f"    暴力匹配数量: {len(matches)}")
    
    if len(matches) > 0:
        distances = [m.distance for m in matches]
        print(f"    距离统计: 最小={min(distances):.2f}, 最大={max(distances):.2f}, 平均={np.mean(distances):.2f}")
    
    # 6.2 暴力匹配器（knn）
    print("  6.2 暴力匹配器(k=2):")
    bf_knn = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    matches_knn = bf_knn.knnMatch(desc1, desc2, k=2)
    print(f"    KNN匹配对数: {len(matches_knn)}")
    
    # 应用比例测试
    good_matches = []
    for match_pair in matches_knn:
        if len(match_pair) == 2:
            m, n = match_pair
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)
    
    print(f"    比例测试后匹配数: {len(good_matches)}")
    
    if len(good_matches) > 0:
        distances = [m.distance for m in good_matches]
        print(f"    距离统计: 最小={min(distances):.2f}, 最大={max(distances):.2f}, 平均={np.mean(distances):.2f}")
    
    # 6.3 FLANN匹配器
    print("  6.3 FLANN匹配器:")
    try:
        FLANN_INDEX_LSH = 6
        index_params = dict(algorithm=FLANN_INDEX_LSH,
                           table_number=6,
                           key_size=12,
                           multi_probe_level=1)
        search_params = dict(checks=50)
        
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        flann_matches = flann.knnMatch(desc1, desc2, k=2)
        
        flann_good_matches = []
        for match_pair in flann_matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < 0.75 * n.distance:
                    flann_good_matches.append(m)
        
        print(f"    FLANN匹配对数: {len(flann_matches)}")
        print(f"    FLANN比例测试后匹配数: {len(flann_good_matches)}")
        
    except Exception as e:
        print(f"    FLANN匹配失败: {e}")
    
    print("\n7. 测试不同参数:")
    
    # 7.1 测试不同的ORB参数
    print("  7.1 不同ORB参数:")
    for nfeat in [500, 1000, 2000]:
        for scale in [1.2, 1.4, 1.6]:
            orb_test = cv2.ORB_create(nfeatures=nfeat, scaleFactor=scale)
            kp1_test, desc1_test = orb_test.detectAndCompute(base_resized, None)
            kp2_test, desc2_test = orb_test.detectAndCompute(target_resized, None)
            
            if desc1_test is not None and desc2_test is not None:
                bf_test = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
                matches_test = bf_test.match(desc1_test, desc2_test)
                
                print(f"    nfeatures={nfeat}, scaleFactor={scale}: 关键点({len(kp1_test)},{len(kp2_test)}), 匹配数={len(matches_test)}")
    
    # 7.2 测试不同的图像预处理
    print("  7.2 不同图像预处理:")
    
    # 直方图均衡化
    base_eq = cv2.equalizeHist(base_resized)
    target_eq = cv2.equalizeHist(target_resized)
    
    kp1_eq, desc1_eq = orb.detectAndCompute(base_eq, None)
    kp2_eq, desc2_eq = orb.detectAndCompute(target_eq, None)
    
    if desc1_eq is not None and desc2_eq is not None:
        matches_eq = bf.match(desc1_eq, desc2_eq)
        print(f"    直方图均衡化: 关键点({len(kp1_eq)},{len(kp2_eq)}), 匹配数={len(matches_eq)}")
    
    # 高斯模糊
    base_blur = cv2.GaussianBlur(base_resized, (3, 3), 0)
    target_blur = cv2.GaussianBlur(target_resized, (3, 3), 0)
    
    kp1_blur, desc1_blur = orb.detectAndCompute(base_blur, None)
    kp2_blur, desc2_blur = orb.detectAndCompute(target_blur, None)
    
    if desc1_blur is not None and desc2_blur is not None:
        matches_blur = bf.match(desc1_blur, desc2_blur)
        print(f"    高斯模糊: 关键点({len(kp1_blur)},{len(kp2_blur)}), 匹配数={len(matches_blur)}")
    
    # 8. 测试使用原始尺寸图像
    print("\n8. 测试原始尺寸图像:")
    kp1_orig, desc1_orig = orb.detectAndCompute(base_gray, None)
    kp2_orig, desc2_orig = orb.detectAndCompute(target_gray, None)
    
    print(f"  原始尺寸关键点: 基准={len(kp1_orig)}, 目标={len(kp2_orig)}")
    
    if desc1_orig is not None and desc2_orig is not None:
        matches_orig = bf.match(desc1_orig, desc2_orig)
        print(f"  原始尺寸匹配数: {len(matches_orig)}")
        
        if len(matches_orig) > 0:
            distances = [m.distance for m in matches_orig]
            print(f"  距离统计: 最小={min(distances):.2f}, 最大={max(distances):.2f}, 平均={np.mean(distances):.2f}")
    
    print("\n=== 调试完成 ===")

if __name__ == "__main__":
    debug_feature_matching_detailed()