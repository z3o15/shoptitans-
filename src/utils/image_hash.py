#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像哈希工具模块
提供dHash算法实现，用于图像相似度计算
"""

import cv2
import numpy as np
from PIL import Image
from typing import Optional, Union


def get_dhash(image: Union[str, np.ndarray], hash_size: int = 8) -> Optional[int]:
    """
    计算图像的dHash值
    
    Args:
        image: 图像路径或numpy数组
        hash_size: 哈希大小，默认为8
        
    Returns:
        dHash整数值，如果出错则返回None
    """
    try:
        # 如果输入是字符串路径，加载图像
        if isinstance(image, str):
            img = Image.open(image)
            # 转换为RGB格式
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # 转换为numpy数组
            image_array = np.array(img)
        else:
            image_array = image
            
        # 转换为灰度图
        if len(image_array.shape) == 3:
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_array
            
        # 调整尺寸
        resized = cv2.resize(gray, (hash_size + 1, hash_size))
        
        # 计算差异
        diff = resized[:, 1:] > resized[:, :-1]
        
        # 转换为整数值
        dhash_value = sum([2**i for (i, v) in enumerate(diff.flatten()) if v])
        
        return dhash_value
        
    except Exception as e:
        print(f"dHash计算失败: {e}")
        return None


def get_dhash_string(image: Union[str, np.ndarray], hash_size: int = 8) -> Optional[str]:
    """
    计算图像的dHash字符串
    
    Args:
        image: 图像路径或numpy数组
        hash_size: 哈希大小，默认为8
        
    Returns:
        dHash字符串，如果出错则返回None
    """
    try:
        # 如果输入是字符串路径，加载图像
        if isinstance(image, str):
            img = Image.open(image)
            # 转换为RGB格式
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # 转换为numpy数组
            image_array = np.array(img)
        else:
            image_array = image
            
        # 转换为灰度图
        if len(image_array.shape) == 3:
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_array
            
        # 调整尺寸
        resized = cv2.resize(gray, (hash_size + 1, hash_size))
        
        # 计算差异
        diff = resized[:, 1:] > resized[:, :-1]
        
        # 转换为字符串
        dhash_str = ''.join(['1' if v else '0' for v in diff.flatten()])
        
        return dhash_str
        
    except Exception as e:
        print(f"dHash字符串计算失败: {e}")
        return None


def calculate_hamming_distance(hash1: Union[str, int], hash2: Union[str, int]) -> int:
    """
    计算两个dHash值之间的汉明距离
    
    Args:
        hash1: 第一个哈希值（字符串或整数）
        hash2: 第二个哈希值（字符串或整数）
        
    Returns:
        汉明距离
    """
    try:
        # 如果是整数，转换为二进制字符串
        if isinstance(hash1, int):
            hash1_str = bin(hash1)[2:].zfill(64)  # 假设8x8=64位
        else:
            hash1_str = hash1
            
        if isinstance(hash2, int):
            hash2_str = bin(hash2)[2:].zfill(64)
        else:
            hash2_str = hash2
            
        # 确保长度一致
        max_len = max(len(hash1_str), len(hash2_str))
        hash1_str = hash1_str.zfill(max_len)
        hash2_str = hash2_str.zfill(max_len)
        
        # 计算汉明距离
        distance = sum(c1 != c2 for c1, c2 in zip(hash1_str, hash2_str))
        
        return distance
        
    except Exception as e:
        print(f"汉明距离计算失败: {e}")
        return 0


def calculate_similarity(hash1: Union[str, int], hash2: Union[str, int]) -> float:
    """
    计算两个dHash值的相似度百分比
    
    Args:
        hash1: 第一个哈希值（字符串或整数）
        hash2: 第二个哈希值（字符串或整数）
        
    Returns:
        相似度百分比（0-100）
    """
    try:
        # 计算汉明距离
        distance = calculate_hamming_distance(hash1, hash2)
        
        # 如果是整数，转换为二进制字符串获取长度
        if isinstance(hash1, int):
            hash_length = len(bin(hash1)[2:])
        else:
            hash_length = len(hash1)
            
        if isinstance(hash2, int):
            hash_length = max(hash_length, len(bin(hash2)[2:]))
        else:
            hash_length = max(hash_length, len(hash2))
            
        if hash_length == 0:
            return 100.0
            
        # 计算相似度
        similarity = (1 - distance / hash_length) * 100
        
        return round(similarity, 2)
        
    except Exception as e:
        print(f"相似度计算失败: {e}")
        return 0.0


def test_dhash():
    """测试dHash功能"""
    print("测试dHash功能...")
    
    # 创建测试图像
    test_img1 = np.zeros((100, 100), dtype=np.uint8)
    test_img1[:50, :] = 255  # 上半部分白色
    
    test_img2 = np.zeros((100, 100), dtype=np.uint8)
    test_img2[:50, :] = 255  # 上半部分白色
    test_img2[25:75, 25:75] = 128  # 中间灰色区域
    
    # 计算dHash
    dhash1 = get_dhash(test_img1)
    dhash2 = get_dhash(test_img2)
    
    print(f"图像1 dHash: {dhash1}")
    print(f"图像2 dHash: {dhash2}")
    
    # 计算相似度
    similarity = calculate_similarity(dhash1, dhash2)
    print(f"相似度: {similarity}%")
    
    print("dHash功能测试完成")


if __name__ == "__main__":
    test_dhash()