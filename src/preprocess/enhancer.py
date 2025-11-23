#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像增强模块
提供针对游戏装备图标的图像增强功能
"""

import cv2
import numpy as np
from typing import Optional


class ImageEnhancer:
    """图像增强器类
    
    提供针对游戏装备图标的图像增强功能
    """
    
    def __init__(self):
        """初始化图像增强器"""
        print(f"✓ 图像增强器初始化完成")
    
    def enhance_for_feature_detection(self, image: np.ndarray) -> np.ndarray:
        """为特征检测优化图像
        
        Args:
            image: 输入图像（BGR或灰度）
            
        Returns:
            增强后的图像
        """
        try:
            # 确保是灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # 1. 直方图均衡化增强对比度
            equalized = cv2.equalizeHist(gray)
            
            # 2. 高斯模糊减少噪声
            blurred = cv2.GaussianBlur(equalized, (3, 3), 0)
            
            # 3. Canny边缘检测增强特征
            canny = cv2.Canny(blurred, 30, 120)
            
            # 4. 形态学操作增强边缘
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            morphed = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)
            
            # 5. 结合原图像和边缘信息
            enhanced = cv2.addWeighted(equalized, 0.7, morphed, 0.3, 0)
            
            return enhanced
            
        except Exception as e:
            print(f"❌ 图像增强失败: {e}")
            return image
    
    def enhance_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """为OCR识别优化图像
        
        Args:
            image: 输入图像（BGR）
            
        Returns:
            增强后的图像
        """
        try:
            # 确保是BGR图像
            if len(image.shape) != 3:
                # 如果是灰度图，转换为BGR
                enhanced = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            else:
                enhanced = image.copy()
            
            # 1. 亮度调整
            hsv = cv2.cvtColor(enhanced, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            
            # 增加亮度
            v = cv2.add(v, 20)
            v = np.clip(v, 0, 255)
            
            enhanced = cv2.merge([h, s, v])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_HSV2BGR)
            
            # 2. 对比度增强
            lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # 应用CLAHE对比度增强
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            # 3. 锐化
            kernel = np.array([[-1, -1, -1],
                              [-1,  9, -1],
                              [-1, -1, -1]])
            enhanced = cv2.filter2D(enhanced, -1, kernel)
            
            return enhanced
            
        except Exception as e:
            print(f"❌ OCR图像增强失败: {e}")
            return image
    
    def enhance_contrast(self, image: np.ndarray, method: str = "histogram") -> np.ndarray:
        """增强图像对比度
        
        Args:
            image: 输入图像
            method: 增强方法 ("histogram", "clahe")
            
        Returns:
            增强后的图像
        """
        try:
            # 确保是灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            if method == "histogram":
                # 直方图均衡化
                enhanced = cv2.equalizeHist(gray)
            elif method == "clahe":
                # CLAHE对比度受限自适应直方图均衡化
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                enhanced = clahe.apply(gray)
            else:
                print(f"⚠️ 未知的对比度增强方法: {method}")
                return gray
            
            return enhanced
            
        except Exception as e:
            print(f"❌ 对比度增强失败: {e}")
            return image
    
    def enhance_sharpness(self, image: np.ndarray, method: str = "unsharp_mask") -> np.ndarray:
        """增强图像锐度
        
        Args:
            image: 输入图像
            method: 锐化方法 ("unsharp_mask", "gaussian")
            
        Returns:
            锐化后的图像
        """
        try:
            if method == "unsharp_mask":
                # 反锐化掩码
                blurred = cv2.GaussianBlur(image, (0, 0), 2.0)
                enhanced = cv2.addWeighted(image, 1.5, blurred, -0.5, 0)
            elif method == "gaussian":
                # 高斯锐化
                kernel = np.array([[-1, -1, -1],
                                  [-1,  9, -1],
                                  [-1, -1, -1]])
                enhanced = cv2.filter2D(image, -1, kernel)
            else:
                print(f"⚠️ 未知的锐化方法: {method}")
                return image
            
            return enhanced
            
        except Exception as e:
            print(f"❌ 图像锐化失败: {e}")
            return image
    
    def denoise(self, image: np.ndarray, method: str = "gaussian") -> np.ndarray:
        """图像去噪
        
        Args:
            image: 输入图像
            method: 去噪方法 ("gaussian", "median", "bilateral")
            
        Returns:
            去噪后的图像
        """
        try:
            if method == "gaussian":
                # 高斯模糊去噪
                denoised = cv2.GaussianBlur(image, (3, 3), 0)
            elif method == "median":
                # 中值滤波去噪
                denoised = cv2.medianBlur(image, 3)
            elif method == "bilateral":
                # 双边滤波去噪（保持边缘）
                denoised = cv2.bilateralFilter(image, 9, 75, 75)
            else:
                print(f"⚠️ 未知的去噪方法: {method}")
                return image
            
            return denoised
            
        except Exception as e:
            print(f"❌ 图像去噪失败: {e}")
            return image
    
    def adaptive_enhance(self, image: np.ndarray) -> np.ndarray:
        """自适应图像增强
        
        根据图像特征自动选择最佳增强方法
        
        Args:
            image: 输入图像
            
        Returns:
            增强后的图像
        """
        try:
            # 分析图像质量
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # 计算图像质量指标
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            contrast = gray.std()
            
            # 根据图像质量选择增强策略
            if laplacian_var < 100:  # 低对比度图像
                print("检测到低对比度图像，应用强对比度增强")
                enhanced = self.enhance_contrast(gray, "clahe")
                enhanced = self.enhance_sharpness(enhanced, "unsharp_mask")
            elif contrast < 30:  # 低对比度图像
                print("检测到低对比度图像，应用对比度增强")
                enhanced = self.enhance_contrast(gray, "histogram")
                enhanced = self.enhance_sharpness(enhanced, "gaussian")
            else:  # 正常对比度图像
                print("检测到正常对比度图像，应用轻度增强")
                enhanced = self.denoise(gray, "gaussian")
                enhanced = self.enhance_sharpness(enhanced, "unsharp_mask")
            
            return enhanced
            
        except Exception as e:
            print(f"❌ 自适应增强失败: {e}")
            return image


def test_image_enhancer():
    """测试图像增强器"""
    print("=" * 60)
    print("图像增强器测试")
    print("=" * 60)
    
    # 创建测试图像
    test_image = np.zeros((200, 200), dtype=np.uint8)
    test_image[:] = 100  # 灰色背景
    
    # 添加一些几何图形
    cv2.rectangle(test_image, (50, 50), (150, 150), 150, -1)  # 白色矩形
    cv2.circle(test_image, (100, 100), 30, 200, -1)  # 白色圆形
    
    # 保存测试图像
    test_path = "test_enhancer.png"
    cv2.imwrite(test_path, test_image)
    print(f"创建测试图像: {test_path}")
    
    # 创建图像增强器
    enhancer = ImageEnhancer()
    
    # 测试特征检测增强
    enhanced = enhancer.enhance_for_feature_detection(test_image)
    enhanced_path = "test_enhanced.png"
    cv2.imwrite(enhanced_path, enhanced)
    
    print(f"\n✓ 测试完成")
    print(f"  - 原始图像: {test_path}")
    print(f"  - 增强图像: {enhanced_path}")
    
    # 清理测试文件
    try:
        if os.path.exists(test_path):
            os.remove(test_path)
        if os.path.exists(enhanced_path):
            os.remove(enhanced_path)
    except:
        pass


if __name__ == "__main__":
    import os
    test_image_enhancer()