#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像尺寸调整模块
提供统一的图像尺寸调整功能
"""

import cv2
import numpy as np
from PIL import Image
from typing import Tuple


class ImageResizer:
    """图像尺寸调整器类
    
    提供统一的图像尺寸调整功能
    """
    
    def __init__(self, target_size=(116, 116), interpolation=cv2.INTER_AREA):
        """初始化图像尺寸调整器
        
        Args:
            target_size: 目标尺寸 (宽度, 高度)
            interpolation: 插值方法
        """
        self.target_size = target_size
        self.interpolation = interpolation
        
        print(f"✓ 图像尺寸调整器初始化完成")
        print(f"  - 目标尺寸: {target_size}")
        print(f"  - 插值方法: {interpolation}")
    
    def resize(self, image: np.ndarray, maintain_aspect_ratio=False) -> np.ndarray:
        """调整图像尺寸
        
        Args:
            image: 输入图像
            maintain_aspect_ratio: 是否保持宽高比
            
        Returns:
            调整尺寸后的图像
        """
        try:
            target_width, target_height = self.target_size
            
            if maintain_aspect_ratio:
                # 保持宽高比的尺寸调整
                h, w = image.shape[:2]
                aspect_ratio = w / h
                
                if aspect_ratio > target_width / target_height:
                    # 以宽度为准
                    new_width = target_width
                    new_height = int(target_width / aspect_ratio)
                else:
                    # 以高度为准
                    new_height = target_height
                    new_width = int(target_height * aspect_ratio)
                
                resized = cv2.resize(image, (new_width, new_height), interpolation=self.interpolation)
                
                # 创建目标尺寸的画布并居中放置图像
                canvas = np.zeros((target_height, target_width), dtype=image.dtype)
                
                # 计算居中位置
                x_offset = (target_width - new_width) // 2
                y_offset = (target_height - new_height) // 2
                
                # 将图像放置到画布中心
                canvas[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized
                
                return canvas
            else:
                # 直接调整到目标尺寸
                return cv2.resize(image, self.target_size, interpolation=self.interpolation)
                
        except Exception as e:
            print(f"❌ 图像尺寸调整失败: {e}")
            return image
    
    def resize_with_padding(self, image: np.ndarray, padding_color=(0, 0, 0)) -> np.ndarray:
        """调整图像尺寸并添加padding
        
        Args:
            image: 输入图像
            padding_color: padding颜色 (B, G, R)
            
        Returns:
            调整尺寸后的图像
        """
        try:
            # 先调整图像尺寸
            resized = self.resize(image, maintain_aspect_ratio=True)
            
            # 创建目标尺寸的画布
            h, w = resized.shape[:2]
            target_h, target_w = self.target_size
            
            canvas = np.full((target_h, target_w), padding_color, dtype=image.dtype)
            
            # 计算居中位置
            x_offset = (target_w - w) // 2
            y_offset = (target_h - h) // 2
            
            # 将图像放置到画布中心
            canvas[y_offset:y_offset+h, x_offset:x_offset+w] = resized
            
            return canvas
            
        except Exception as e:
            print(f"❌ 带padding的图像尺寸调整失败: {e}")
            return image
    
    def resize_letterbox(self, image: np.ndarray, background_color=(0, 0, 0)) -> np.ndarray:
        """使用letterbox方式调整图像尺寸
        
        Args:
            image: 输入图像
            background_color: 背景颜色 (B, G, R)
            
        Returns:
            调整尺寸后的图像
        """
        try:
            h, w = image.shape[:2]
            target_h, target_w = self.target_size
            
            # 计算缩放比例
            scale = min(target_w / w, target_h / h)
            
            # 计算letterbox尺寸
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            # 调整图像尺寸
            resized = cv2.resize(image, (new_w, new_h), interpolation=self.interpolation)
            
            # 创建目标尺寸的画布
            canvas = np.full((target_h, target_w), background_color, dtype=image.dtype)
            
            # 计算居中位置
            x_offset = (target_w - new_w) // 2
            y_offset = (target_h - new_h) // 2
            
            # 将图像放置到画布中心
            canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
            
            return canvas
            
        except Exception as e:
            print(f"❌ Letterbox图像尺寸调整失败: {e}")
            return image
    
    def resize_pil(self, image_path: str, output_path: str) -> bool:
        """使用PIL调整图像尺寸
        
        Args:
            image_path: 输入图像路径
            output_path: 输出图像路径
            
        Returns:
            是否成功
        """
        try:
            with Image.open(image_path) as img:
                # 调整尺寸
                resized = img.resize(self.target_size, Image.Resampling.LANCZOS)
                
                # 保存结果
                resized.save(output_path)
                
            return True
            
        except Exception as e:
            print(f"❌ PIL图像尺寸调整失败: {e}")
            return False
    
    def batch_resize_directory(self, input_dir: str, output_dir: str, 
                           maintain_aspect_ratio=False) -> dict:
        """批量调整目录中的图像尺寸
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            maintain_aspect_ratio: 是否保持宽高比
            
        Returns:
            处理结果统计
        """
        import os
        import glob
        
        results = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'failed_files': []
        }
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取所有图像文件
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.webp', '*.bmp']
        image_files = []
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(input_dir, ext)))
        
        # 处理每个图像
        for image_file in image_files:
            filename = os.path.basename(image_file)
            output_path = os.path.join(output_dir, filename)
            
            try:
                # 读取图像
                image = cv2.imread(image_file)
                if image is None:
                    raise ValueError(f"无法读取图像: {image_file}")
                
                # 调整尺寸
                resized = self.resize(image, maintain_aspect_ratio)
                
                # 保存结果
                cv2.imwrite(output_path, resized)
                
                results['success'] += 1
                print(f"✓ 处理成功: {filename}")
                
            except Exception as e:
                results['failed'] += 1
                results['failed_files'].append(filename)
                print(f"❌ 处理失败: {filename}, 错误: {e}")
            
            results['total'] += 1
        
        # 输出统计结果
        print(f"\n批量尺寸调整完成:")
        print(f"  - 总计: {results['total']} 个文件")
        print(f"  - 成功: {results['success']} 个文件")
        print(f"  - 失败: {results['failed']} 个文件")
        
        if results['failed_files']:
            print(f"  - 失败文件: {', '.join(results['failed_files'])}")
        
        return results


def test_image_resizer():
    """测试图像尺寸调整器"""
    print("=" * 60)
    print("图像尺寸调整器测试")
    print("=" * 60)
    
    # 创建测试图像
    test_image = np.zeros((200, 300, 3), dtype=np.uint8)
    test_image[:] = (100, 150, 200)  # 蓝绿色背景
    
    # 添加一个矩形
    cv2.rectangle(test_image, (50, 50), (150, 250), (255, 0, 0), -1)  # 红色矩形
    
    # 保存测试图像
    test_path = "test_resizer.png"
    cv2.imwrite(test_path, test_image)
    print(f"创建测试图像: {test_path}")
    print(f"  原始尺寸: {test_image.shape}")
    
    # 创建图像尺寸调整器
    resizer = ImageResizer(target_size=(116, 116))
    
    # 测试不同的调整方法
    methods = [
        ("直接调整", lambda img: resizer.resize(img)),
        ("保持宽高比", lambda img: resizer.resize(img, maintain_aspect_ratio=True)),
        ("添加padding", lambda img: resizer.resize_with_padding(img, padding_color=(50, 50, 50))),
        ("Letterbox", lambda img: resizer.resize_letterbox(img, background_color=(50, 50, 50)))
    ]
    
    for i, (method_name, method_func) in enumerate(methods, 1):
        print(f"\n测试方法 {i}: {method_name}")
        result = method_func(test_image)
        output_path = f"test_resizer_{i}.png"
        cv2.imwrite(output_path, result)
        print(f"  - 输出: {output_path}")
        print(f"  - 结果尺寸: {result.shape}")
    
    # 清理测试文件
    try:
        import os
        if os.path.exists(test_path):
            os.remove(test_path)
        for i in range(1, len(methods) + 1):
            test_file = f"test_resizer_{i}.png"
            if os.path.exists(test_file):
                os.remove(test_file)
    except:
        pass
    
    print(f"\n✓ 测试完成")


if __name__ == "__main__":
    test_image_resizer()