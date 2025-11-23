#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
背景去除模块
专门用于去除游戏装备图标的圆形背景
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw
from typing import Tuple, Optional


class BackgroundRemover:
    """背景去除器类
    
    专门处理游戏装备图标的圆形背景去除
    """
    
    def __init__(self):
        """初始化背景去除器"""
        print(f"✓ 背景去除器初始化完成")
    
    def remove_circular_background(self, image: np.ndarray) -> np.ndarray:
        """去除圆形背景
        
        Args:
            image: 输入图像（BGR格式）
            
        Returns:
            去除背景后的图像
        """
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # 应用高斯模糊减少噪声
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # 使用Canny边缘检测
            edges = cv2.Canny(blurred, 50, 150)
            
            # 查找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                print("⚠️ 未检测到轮廓，返回原图像")
                return image
            
            # 找到最大的轮廓（假设为装备图标）
            largest_contour = max(contours, key=cv2.contourArea)
            
            # 创建掩码
            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.fillPoly(mask, [largest_contour], 255)
            
            # 应用形态学操作优化掩码
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # 使用掩码提取前景
            result = cv2.bitwise_and(image, image, mask=mask)
            
            return result
            
        except Exception as e:
            print(f"❌ 圆形背景去除失败: {e}")
            return image
    
    def detect_circular_region(self, image: np.ndarray) -> Optional[Tuple[int, int, int]]:
        """检测圆形区域
        
        Args:
            image: 输入图像
            
        Returns:
            (center_x, center_y, radius) 的元组，如果检测失败则返回None
        """
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # 应用高斯模糊
            blurred = cv2.GaussianBlur(gray, (9, 9), 2)
            
            # 使用霍夫圆检测
            circles = cv2.HoughCircles(
                blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=100,
                param1=50, param2=30, minRadius=20, maxRadius=100
            )
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                if len(circles) > 0:
                    # 返回第一个检测到的圆
                    x, y, r = circles[0]
                    return x, y, r
            
            return None
            
        except Exception as e:
            print(f"❌ 圆形区域检测失败: {e}")
            return None
    
    def create_circular_mask(self, image_shape: Tuple[int, int], 
                         center: Tuple[int, int], radius: int) -> np.ndarray:
        """创建圆形掩码
        
        Args:
            image_shape: 图像形状 (height, width)
            center: 圆心坐标 (x, y)
            radius: 圆半径
            
        Returns:
            圆形掩码
        """
        height, width = image_shape
        mask = np.zeros((height, width), dtype=np.uint8)
        
        # 绘制圆形
        cv2.circle(mask, center, radius, 255, -1)
        
        return mask
    
    def refine_mask_with_grabcut(self, image: np.ndarray, 
                              initial_mask: np.ndarray) -> np.ndarray:
        """使用GrabCut算法优化掩码
        
        Args:
            image: 输入图像
            initial_mask: 初始掩码
            
        Returns:
            优化后的掩码
        """
        try:
            # 确定GrabCut的参数
            bgd_model = np.zeros((1, 65), np.float64)
            fgd_model = np.zeros((1, 65), np.float64)
            
            # 应用GrabCut
            cv2.grabCut(image, initial_mask, None, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_MASK)
            
            # 提取前景掩码
            mask = np.where((initial_mask == 2) | (initial_mask == 0), 0, 1).astype('uint8')
            
            return mask
            
        except Exception as e:
            print(f"❌ GrabCut优化失败: {e}")
            return initial_mask


def test_background_remover():
    """测试背景去除器"""
    print("=" * 60)
    print("背景去除器测试")
    print("=" * 60)
    
    # 创建测试图像
    test_image = np.zeros((200, 200, 3), dtype=np.uint8)
    test_image[:] = (100, 150, 200)  # 蓝色背景
    
    # 添加一个圆形装备图标
    center = (100, 100)
    radius = 80
    cv2.circle(test_image, center, radius, (255, 255, 255), -1)  # 白色圆形
    cv2.circle(test_image, center, radius-20, (0, 0, 255), -1)  # 蓝色内圆
    cv2.circle(test_image, center, radius-40, (255, 0, 0), -1)  # 红色核心
    
    # 保存测试图像
    test_path = "test_background.png"
    cv2.imwrite(test_path, test_image)
    print(f"创建测试图像: {test_path}")
    
    # 创建背景去除器
    remover = BackgroundRemover()
    
    # 处理测试图像
    result = remover.remove_circular_background(test_image)
    
    if result is not None:
        # 保存结果
        result_path = "test_background_removed.png"
        cv2.imwrite(result_path, result)
        
        print(f"\n✓ 测试成功")
        print(f"  - 原始图像: {test_path}")
        print(f"  - 处理结果: {result_path}")
        print(f"  - 结果尺寸: {result.shape}")
    else:
        print("\n✗ 测试失败")
    
    # 清理测试文件
    try:
        if os.path.exists(test_path):
            os.remove(test_path)
        if os.path.exists("test_background_removed.png"):
            os.remove("test_background_removed.png")
    except:
        pass


if __name__ == "__main__":
    test_background_remover()