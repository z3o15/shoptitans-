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

# 导入统一的背景掩码函数
try:
    from ..utils.background_mask import create_background_mask
except ImportError:
    try:
        from utils.background_mask import create_background_mask
    except ImportError:
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
                
                # 合并掩码
                mask_combined = cv2.bitwise_or(mask_bg, mask_light_purple)
                
                # 应用轻微高斯模糊
                mask_combined = cv2.GaussianBlur(mask_combined, (3, 3), 0.1)
                
                # 二值化
                _, mask_combined = cv2.threshold(mask_combined, 200, 255, cv2.THRESH_BINARY)
                
                return mask_combined
            except Exception as e:
                print(f"[ERROR] 背景掩码创建失败: {e}")
                return np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)


class BackgroundRemover:
    """背景去除器类
    
    专门处理游戏装备图标的圆形背景去除
    """
    
    def __init__(self, config=None):
        """初始化背景去除器
        
        Args:
            config: 背景去除配置字典
        """
        self.config = config or {}
        print(f"✓ 背景去除器初始化完成")
    
    def remove_circular_background(self, image: np.ndarray) -> np.ndarray:
        """去除圆形背景
        
        Args:
            image: 输入图像（BGR格式）
            
        Returns:
            去除背景后的图像
        """
        try:
            # 1. 转为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # 2. 高斯模糊（减小核大小，避免边缘模糊）
            kernel = tuple(self.config.get('gaussian_blur_kernel', [3, 3]))
            blurred = cv2.GaussianBlur(gray, kernel, 0)
            
            # 3. Canny边缘检测（调整阈值，保留装备边缘）
            edges = cv2.Canny(blurred, self.config.get('canny_threshold1', 40),
                             self.config.get('canny_threshold2', 120))
            
            # 4. 形态学优化（先闭运算填补缺口，再开运算去噪声）
            morph_kernel = np.ones(tuple(self.config.get('morph_kernel_size', [5, 5])), np.uint8)
            # 闭运算：填补背景中的小缺口（避免装备内部被误判为背景）
            closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, morph_kernel,
                                     iterations=self.config.get('morph_close_iterations', 2))
            # 开运算：去除背景中的微小噪声（不影响装备轮廓）
            opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, morph_kernel,
                                     iterations=self.config.get('morph_open_iterations', 1))
            
            # 5. 提取掩码并去除背景
            mask = cv2.threshold(opened, 127, 255, cv2.THRESH_BINARY)[1]
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


if __name__ == "__main__":
    # 简单的示例用法
    import os
    
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