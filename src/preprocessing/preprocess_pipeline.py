#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图标标准化流水线模块
提供统一的图标处理流程：去背景、标准化尺寸、图像增强、特征提取
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw
from typing import Tuple, Optional
import os

from .background_remover import BackgroundRemover
from .enhancer import ImageEnhancer
from .resizer import ImageResizer


class PreprocessPipeline:
    """图标标准化流水线类
    
    提供统一的图标处理流程：
    1. 去圆形背景
    2. padding到方形
    3. resize到116×116
    4. 增强（Canny/Equalize）
    5. 预提取ORB特征
    """
    
    def __init__(self, config=None):
        """初始化预处理流水线
        
        Args:
            config: 预处理配置字典
        """
        self.config = config or {}
        self.target_size = tuple(self.config.get('target_size', [116, 116]))
        self.enable_enhancement = self.config.get('enable_enhancement', True)
        
        # 初始化处理组件
        self.background_remover = BackgroundRemover(self.config.get('background_removal', {}))
        self.enhancer = ImageEnhancer(self.config.get('preprocessing', {}))
        self.resizer = ImageResizer(self.target_size)
        
        print(f"✓ 图标标准化流水线初始化完成")
        print(f"  - 目标尺寸: {self.target_size}")
        print(f"  - 图像增强: {'启用' if self.enable_enhancement else '禁用'}")
    
    def process_image(self, image_path: str, save_intermediate=False, 
                   output_dir=None) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """处理单个图像
        
        Args:
            image_path: 输入图像路径
            save_intermediate: 是否保存中间处理结果
            output_dir: 输出目录（如果save_intermediate为True）
            
        Returns:
            (处理后的图像, ORB特征) 的元组
        """
        try:
            print(f"开始处理图像: {image_path}")
            
            # 1. 加载原始图像
            original_image = cv2.imread(image_path)
            if original_image is None:
                raise ValueError(f"无法加载图像: {image_path}")
            
            if save_intermediate and output_dir:
                os.makedirs(output_dir, exist_ok=True)
                cv2.imwrite(os.path.join(output_dir, "01_original.png"), original_image)
            
            # 2. 去圆形背景
            no_bg_image = self.background_remover.remove_circular_background(original_image)
            
            if save_intermediate and output_dir:
                cv2.imwrite(os.path.join(output_dir, "02_no_background.png"), no_bg_image)
            
            # 3. Padding到方形
            squared_image = self._pad_to_square(no_bg_image)
            
            if save_intermediate and output_dir:
                cv2.imwrite(os.path.join(output_dir, "03_squared.png"), squared_image)
            
            # 4. 调整尺寸到目标大小
            resized_image = self.resizer.resize(squared_image)
            
            if save_intermediate and output_dir:
                cv2.imwrite(os.path.join(output_dir, "04_resized.png"), resized_image)
            
            # 5. 图像增强
            if self.enable_enhancement:
                enhanced_image = self.enhancer.enhance_for_feature_detection(resized_image)
                
                if save_intermediate and output_dir:
                    cv2.imwrite(os.path.join(output_dir, "05_enhanced.png"), enhanced_image)
            else:
                enhanced_image = resized_image
            
            # 6. 预提取ORB特征（可选）
            orb_features = self._extract_orb_features(enhanced_image)
            
            print(f"✓ 图像处理完成: {image_path}")
            print(f"  - 最终尺寸: {enhanced_image.shape}")
            print(f"  - 特征点数: {len(orb_features[0]) if orb_features[0] else 0}")
            
            return enhanced_image, orb_features
            
        except Exception as e:
            print(f"❌ 图像处理失败: {image_path}, 错误: {e}")
            return None, None
    
    def _pad_to_square(self, image: np.ndarray) -> np.ndarray:
        """将图像padding到正方形
        
        Args:
            image: 输入图像
            
        Returns:
            正方形图像
        """
        height, width = image.shape[:2]
        
        if height == width:
            return image
        
        # 计算需要的padding
        if height > width:
            padding = (height - width) // 2
            padded = cv2.copyMakeBorder(image, 0, 0, padding, padding, 
                                     cv2.BORDER_CONSTANT, value=[0, 0, 0])
        else:
            padding = (width - height) // 2
            padded = cv2.copyMakeBorder(image, padding, padding, 0, 0, 
                                     cv2.BORDER_CONSTANT, value=[0, 0, 0])
        
        return padded
    
    def _extract_orb_features(self, image: np.ndarray) -> Tuple[list, Optional[np.ndarray]]:
        """提取ORB特征
        
        Args:
            image: 输入图像（灰度）
            
        Returns:
            (关键点列表, 描述符数组) 的元组
        """
        try:
            # 转换为灰度图（如果需要）
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # 创建ORB检测器
            orb = cv2.ORB_create(nfeatures=3000, scaleFactor=1.1, 
                                 edgeThreshold=15, patchSize=31)
            
            # 提取特征
            keypoints, descriptors = orb.detectAndCompute(gray, None)
            
            return keypoints, descriptors
            
        except Exception as e:
            print(f"ORB特征提取失败: {e}")
            return [], None
    
    def batch_process_directories(self, input_dirs: list, output_dir: str,
                            save_intermediate=False, sync_deletion=True) -> dict:
        """批量处理多个目录中的图像
        
        Args:
            input_dirs: 输入目录列表
            output_dir: 输出目录
            save_intermediate: 是否保存中间处理结果
            sync_deletion: 是否同步删除输入目录中的文件
            
        Returns:
            处理结果字典
        """
        results = {
            'processed': [],
            'failed': [],
            'deleted': [],
            'stats': {
                'total': 0,
                'success': 0,
                'failed': 0,
                'deleted': 0
            }
        }
        
        # 确保输出目录存在
        from src.utils.path_manager import ensure_path_valid
        if not ensure_path_valid(os.path.dirname(output_dir)):
            os.makedirs(os.path.dirname(output_dir), exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # 处理所有输入目录
        for input_dir in input_dirs:
            if not os.path.exists(input_dir):
                print(f"⚠️ 输入目录不存在: {input_dir}")
                continue
                
            # 检查是否有时间命名的子目录
            subdirs = []
            for item in os.listdir(input_dir):
                item_path = os.path.join(input_dir, item)
                if os.path.isdir(item_path) and item.replace('_', '').replace(':', '').isdigit():
                    subdirs.append(item)
            
            if subdirs:
                # 如果有时间命名的子目录，使用最新的一个
                latest_dir = sorted(subdirs)[-1]
                current_input_dir = os.path.join(input_dir, latest_dir)
                print(f"✓ 找到时间目录: {latest_dir}")
            else:
                # 如果没有时间命名的子目录，直接使用主目录
                current_input_dir = input_dir
            
            # 处理目录中的图像文件
            for filename in os.listdir(current_input_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    input_path = os.path.join(current_input_dir, filename)
                    
                    # 创建单独的输出目录用于中间结果
                    if save_intermediate:
                        intermediate_dir = os.path.join(output_dir,
                                                    f"intermediate_{os.path.splitext(filename)[0]}")
                    else:
                        intermediate_dir = None
                    
                    # 处理图像
                    processed_image, orb_features = self.process_image(
                        input_path, save_intermediate, intermediate_dir
                    )
                    
                    if processed_image is not None:
                        # 保存最终处理结果为JPG格式
                        output_path = os.path.join(output_dir, filename)
                        # 确保文件扩展名为.jpg
                        if not output_path.lower().endswith('.jpg'):
                            output_path = os.path.splitext(output_path)[0] + '.jpg'
                        cv2.imwrite(output_path, processed_image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                        
                        results['processed'].append({
                            'filename': filename,
                            'input_path': input_path,
                            'output_path': output_path,
                            'features_count': len(orb_features[0]) if orb_features[0] else 0,
                            'intermediate_dir': intermediate_dir
                        })
                        results['stats']['success'] += 1
                        
                        # 同步删除输入文件
                        if sync_deletion:
                            try:
                                os.remove(input_path)
                                results['deleted'].append(input_path)
                                results['stats']['deleted'] += 1
                                print(f"✓ 已删除输入文件: {input_path}")
                            except Exception as e:
                                print(f"❌ 删除输入文件失败: {input_path}, 错误: {e}")
                    else:
                        results['failed'].append({
                            'filename': filename,
                            'input_path': input_path,
                            'error': 'Processing failed'
                        })
                        results['stats']['failed'] += 1
                    
                    results['stats']['total'] += 1
        
        # 输出统计信息
        print(f"\n批量处理完成:")
        print(f"  - 总计: {results['stats']['total']} 个文件")
        print(f"  - 成功: {results['stats']['success']} 个文件")
        print(f"  - 失败: {results['stats']['failed']} 个文件")
        print(f"  - 删除: {results['stats']['deleted']} 个文件")
        
        return results

    def batch_process_directory_with_smart_deletion(self, input_dir: str, output_dir: str,
                                           existing_output_files: set, save_intermediate=False) -> dict:
        """批量处理目录中的图像，使用智能删除逻辑
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            existing_output_files: 输出目录中已存在的文件名集合
            save_intermediate: 是否保存中间处理结果
            
        Returns:
            处理结果字典
        """
        results = {
            'processed': [],
            'failed': [],
            'deleted': [],
            'skipped': [],
            'stats': {
                'total': 0,
                'success': 0,
                'failed': 0,
                'deleted': 0,
                'skipped': 0
            }
        }
        
        # 确保输出目录存在
        if not ensure_path_valid(os.path.dirname(output_dir)):
            os.makedirs(os.path.dirname(output_dir), exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # 处理所有图像文件
        for filename in os.listdir(input_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                input_path = os.path.join(input_dir, filename)
                
                # 检查输出目录中是否已存在同名文件
                output_filename = os.path.splitext(filename)[0] + '.jpg'  # 统一转换为JPG格式
                output_path = os.path.join(output_dir, output_filename)
                
                # 创建单独的输出目录用于中间结果
                if save_intermediate:
                    intermediate_dir = os.path.join(output_dir,
                                                f"intermediate_{os.path.splitext(filename)[0]}")
                else:
                    intermediate_dir = None
                
                # 检查是否已存在处理结果
                if output_filename in existing_output_files and os.path.exists(output_path):
                    # 第二次处理：删除原始文件
                    try:
                        os.remove(input_path)
                        results['deleted'].append({
                            'filename': filename,
                            'input_path': input_path,
                            'reason': '已存在处理结果'
                        })
                        results['stats']['deleted'] += 1
                        print(f"✓ 删除已处理的原始文件: {filename}")
                        continue
                    except Exception as e:
                        print(f"❌ 删除原始文件失败: {filename}, 错误: {e}")
                        results['failed'].append({
                            'filename': filename,
                            'input_path': input_path,
                            'error': f'删除失败: {e}'
                        })
                        results['stats']['failed'] += 1
                
                # 处理图像
                processed_image, orb_features = self.process_image(
                    input_path, save_intermediate, intermediate_dir
                )
                
                if processed_image is not None:
                    # 保存最终处理结果为JPG格式
                    cv2.imwrite(output_path, processed_image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                    
                    results['processed'].append({
                        'filename': output_filename,
                        'input_path': input_path,
                        'output_path': output_path,
                        'features_count': len(orb_features[0]) if orb_features[0] else 0,
                        'intermediate_dir': intermediate_dir,
                        'deleted': False  # 首次处理不删除
                    })
                    results['stats']['success'] += 1
                    print(f"✓ 处理成功: {filename} -> {output_filename}")
                else:
                    results['failed'].append({
                        'filename': filename,
                        'input_path': input_path,
                        'error': 'Processing failed'
                    })
                    results['stats']['failed'] += 1
                
                results['stats']['total'] += 1
        
        # 输出统计信息
        print(f"\n批量处理完成:")
        print(f"  - 总计: {results['stats']['total']} 个文件")
        print(f"  - 成功: {results['stats']['success']} 个文件")
        print(f"  - 失败: {results['stats']['failed']} 个文件")
        print(f"  - 删除: {results['stats']['deleted']} 个文件")
        print(f"  - 跳过: {results['stats']['skipped']} 个文件")
        
        return results

    def batch_process_directory(self, input_dir: str, output_dir: str,
                           save_intermediate=False) -> dict:
        """批量处理目录中的图像
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            save_intermediate: 是否保存中间处理结果
            
        Returns:
            处理结果字典
        """
        results = {
            'processed': [],
            'failed': [],
            'stats': {
                'total': 0,
                'success': 0,
                'failed': 0
            }
        }
        
        # 确保输出目录存在
        if not ensure_path_valid(os.path.dirname(output_dir)):
            os.makedirs(os.path.dirname(output_dir), exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # 处理所有图像文件
        for filename in os.listdir(input_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                input_path = os.path.join(input_dir, filename)
                
                # 创建单独的输出目录用于中间结果
                if save_intermediate:
                    intermediate_dir = os.path.join(output_dir, 
                                                f"intermediate_{os.path.splitext(filename)[0]}")
                else:
                    intermediate_dir = None
                
                # 处理图像
                processed_image, orb_features = self.process_image(
                    input_path, save_intermediate, intermediate_dir
                )
                
                if processed_image is not None:
                    # 保存最终处理结果为JPG格式
                    output_path = os.path.join(output_dir, filename)
                    # 确保文件扩展名为.jpg
                    if not output_path.lower().endswith('.jpg'):
                        output_path = os.path.splitext(output_path)[0] + '.jpg'
                    cv2.imwrite(output_path, processed_image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                    
                    results['processed'].append({
                        'filename': filename,
                        'input_path': input_path,
                        'output_path': output_path,
                        'features_count': len(orb_features[0]) if orb_features[0] else 0,
                        'intermediate_dir': intermediate_dir
                    })
                    results['stats']['success'] += 1
                else:
                    results['failed'].append({
                        'filename': filename,
                        'input_path': input_path,
                        'error': 'Processing failed'
                    })
                    results['stats']['failed'] += 1
                
                results['stats']['total'] += 1
        
        # 输出统计信息
        print(f"\n批量处理完成:")
        print(f"  - 总计: {results['stats']['total']} 个文件")
        print(f"  - 成功: {results['stats']['success']} 个文件")
        print(f"  - 失败: {results['stats']['failed']} 个文件")
        
        return results


def test_preprocess_pipeline():
    """测试预处理流水线"""
    print("=" * 60)
    print("图标标准化流水线测试")
    print("=" * 60)
    
    # 创建测试图像
    test_image = np.zeros((200, 150, 3), dtype=np.uint8)
    test_image[:] = (50, 100, 150)  # 蓝色背景
    
    # 添加一个圆形装备图标
    center = (75, 100)
    radius = 60
    cv2.circle(test_image, center, radius, (255, 255, 255), -1)  # 白色圆形
    cv2.circle(test_image, center, radius-10, (0, 0, 255), -1)  # 蓝色内圆
    
    # 保存测试图像
    test_path = "test_equipment.png"
    cv2.imwrite(test_path, test_image)
    print(f"创建测试图像: {test_path}")
    
    # 创建预处理流水线
    pipeline = PreprocessPipeline(target_size=(116, 116), enable_enhancement=True)
    
    # 处理测试图像
    processed_image, orb_features = pipeline.process_image(
        test_path, save_intermediate=True, output_dir="test_output"
    )
    
    if processed_image is not None:
        print(f"\n✓ 测试成功")
        print(f"  - 原始尺寸: {test_image.shape}")
        print(f"  - 处理后尺寸: {processed_image.shape}")
        print(f"  - 特征点数: {len(orb_features[0]) if orb_features[0] else 0}")
    else:
        print("\n✗ 测试失败")
    
    # 清理测试文件
    try:
        if os.path.exists(test_path):
            os.remove(test_path)
        import shutil
        if os.path.exists("test_output"):
            shutil.rmtree("test_output")
    except:
        pass


if __name__ == "__main__":
    test_preprocess_pipeline()