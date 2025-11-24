#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基准装备预处理管理器 - 持久化预处理后的基准装备图像
避免重复处理，提高系统效率
"""

import os
import cv2
import numpy as np
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

from .background_remover import BackgroundRemover
from .enhancer import ImageEnhancer
from .resizer import ImageResizer
from ..config.config_manager import get_config_manager


class BaseEquipmentPreprocessor:
    """基准装备预处理管理器
    
    负责预处理基准装备图像并持久保存，
    只有在配置参数变化时才重新处理
    """
    
    def __init__(self, base_dir="images/base_equipment", 
                 processed_dir="images/base_equipment_equipment",
                 config_file="images/base_equipment_equipment/config.json"):
        """初始化基准装备预处理管理器
        
        Args:
            base_dir: 原始基准装备目录
            processed_dir: 预处理后装备目录
            config_file: 配置文件路径
        """
        self.base_dir = base_dir
        self.processed_dir = processed_dir
        self.config_file = config_file
        
        # 确保目录存在
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # 初始化配置
        self.current_config = None
        self.saved_config = None
        self._load_configs()
        
        # 初始化预处理组件
        self._init_preprocessing_components()
    
    def _load_configs(self):
        """加载当前配置和已保存的配置"""
        try:
            # 加载当前配置
            config_manager = get_config_manager()
            self.current_config = {
                'preprocessing': config_manager.get_preprocessing_config(),
                'background_removal': config_manager.get_background_removal_config(),
                'target_size': config_manager.get_target_size()
            }
            
            # 加载已保存的配置
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.saved_config = json.load(f)
            else:
                self.saved_config = None
                
        except Exception as e:
            print(f"❌ 配置加载失败: {e}")
            self.current_config = {
                'preprocessing': {},
                'background_removal': {},
                'target_size': [116, 116]
            }
            self.saved_config = {}
    
    def _init_preprocessing_components(self):
        """初始化预处理组件"""
        try:
            if self.current_config:
                background_config = self.current_config.get('background_removal', {})
                preprocess_config = self.current_config.get('preprocessing', {})
                target_size = tuple(self.current_config.get('target_size', [116, 116]))
                
                self.background_remover = BackgroundRemover(background_config)
                self.enhancer = ImageEnhancer(preprocess_config)
                self.resizer = ImageResizer(target_size)
                self.target_size = target_size
            else:
                raise Exception("配置未加载")
                
        except Exception as e:
            print(f"❌ 预处理组件初始化失败: {e}")
            # 使用默认配置初始化组件
            self.background_remover = BackgroundRemover({})
            self.enhancer = ImageEnhancer({})
            self.resizer = ImageResizer((116, 116))
            self.target_size = (116, 116)
    
    def _config_changed(self) -> bool:
        """检查配置是否发生变化"""
        if self.saved_config is None:
            return True
        
        # 生成当前配置的哈希值
        current_hash = self._generate_config_hash(self.current_config)
        saved_hash = self.saved_config.get('config_hash', '')
        
        return current_hash != saved_hash
    
    def _generate_config_hash(self, config: Dict) -> str:
        """生成配置的哈希值"""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()
    
    def _save_config(self):
        """保存当前配置"""
        try:
            config_data = {
                'config_hash': self._generate_config_hash(self.current_config),
                'saved_at': datetime.now().isoformat(),
                'config': self.current_config
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
    
    def _process_single_image(self, input_path: str, output_path: str) -> bool:
        """处理单个基准装备图像
        
        Args:
            input_path: 输入图像路径
            output_path: 输出图像路径
            
        Returns:
            bool: 处理是否成功
        """
        try:
            # 读取原始图像
            original_image = cv2.imread(input_path)
            if original_image is None:
                print(f"❌ 无法读取图像: {input_path}")
                return False
            
            # 1. 背景去除
            no_bg_image = self.background_remover.remove_circular_background(original_image)
            
            # 2. Padding到正方形
            height, width = no_bg_image.shape[:2]
            if height == width:
                squared_image = no_bg_image
            else:
                if height > width:
                    padding = (height - width) // 2
                    squared_image = cv2.copyMakeBorder(no_bg_image, 0, 0, padding, padding,
                                                    cv2.BORDER_CONSTANT, value=[0, 0, 0])
                else:
                    padding = (width - height) // 2
                    squared_image = cv2.copyMakeBorder(no_bg_image, padding, padding, 0, 0,
                                                    cv2.BORDER_CONSTANT, value=[0, 0, 0])
            
            # 3. 调整尺寸
            resized_image = self.resizer.resize(squared_image)
            
            # 4. 图像增强
            enhanced_image = self.enhancer.enhance_for_feature_detection(resized_image)
            
            # 5. 保存处理后的图像
            cv2.imwrite(output_path, enhanced_image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            
            return True
            
        except Exception as e:
            print(f"❌ 图像处理失败: {input_path}, 错误: {e}")
            return False
    
    def process_all_images(self, force_reprocess: bool = False) -> Dict[str, Any]:
        """处理所有基准装备图像
        
        Args:
            force_reprocess: 是否强制重新处理所有图像
            
        Returns:
            Dict: 处理结果统计
        """
        # 检查是否需要重新处理
        need_reprocess = force_reprocess or self._config_changed()
        
        if not need_reprocess:
            print("✓ 配置未变化，跳过预处理")
            return self._get_existing_stats()
        
        print("🔄 配置已变化，开始重新预处理基准装备...")
        
        # 清理旧的处理结果
        self._clean_processed_dir()
        
        # 处理所有图像
        results = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'failed_files': []
        }
        
        # 获取所有基准装备图像
        if not os.path.exists(self.base_dir):
            print(f"❌ 基准装备目录不存在: {self.base_dir}")
            return results
        
        image_files = [f for f in os.listdir(self.base_dir) 
                     if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        
        results['total'] = len(image_files)
        
        for filename in image_files:
            input_path = os.path.join(self.base_dir, filename)
            output_filename = os.path.splitext(filename)[0] + '.jpg'  # 统一转换为JPG
            output_path = os.path.join(self.processed_dir, output_filename)
            
            print(f"处理: {filename}")
            
            if self._process_single_image(input_path, output_path):
                results['success'] += 1
                print(f"  ✓ 成功")
            else:
                results['failed'] += 1
                results['failed_files'].append(filename)
                print(f"  ❌ 失败")
        
        # 保存新配置
        self._save_config()
        
        # 输出统计信息
        print(f"\n✅ 基准装备预处理完成!")
        print(f"  总计: {results['total']} 个文件")
        print(f"  成功: {results['success']} 个文件")
        print(f"  失败: {results['failed']} 个文件")
        print(f"  输出目录: {self.processed_dir}")
        
        return results
    
    def _clean_processed_dir(self):
        """清理已处理的目录"""
        try:
            if os.path.exists(self.processed_dir):
                for filename in os.listdir(self.processed_dir):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        file_path = os.path.join(self.processed_dir, filename)
                        os.remove(file_path)
        except Exception as e:
            print(f"⚠️ 清理目录失败: {e}")
    
    def _get_existing_stats(self) -> Dict[str, Any]:
        """获取已存在文件的统计信息"""
        if not os.path.exists(self.processed_dir):
            return {'total': 0, 'success': 0, 'failed': 0, 'failed_files': []}
        
        processed_files = [f for f in os.listdir(self.processed_dir) 
                       if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        
        return {
            'total': len(processed_files),
            'success': len(processed_files),
            'failed': 0,
            'failed_files': []
        }
    
    def get_processed_image_path(self, original_filename: str) -> Optional[str]:
        """获取预处理后的图像路径
        
        Args:
            original_filename: 原始文件名
            
        Returns:
            str: 预处理后的文件路径，如果不存在返回None
        """
        # 确保预处理已完成
        if self._config_changed():
            return None
        
        # 转换为JPG格式
        processed_filename = os.path.splitext(original_filename)[0] + '.jpg'
        processed_path = os.path.join(self.processed_dir, processed_filename)
        
        if os.path.exists(processed_path):
            return processed_path
        
        return None
    
    def get_all_processed_images(self) -> List[str]:
        """获取所有预处理后的图像路径
        
        Returns:
            List[str]: 预处理后的图像路径列表
        """
        if self._config_changed():
            return []
        
        if not os.path.exists(self.processed_dir):
            return []
        
        processed_files = []
        for filename in os.listdir(self.processed_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                processed_files.append(os.path.join(self.processed_dir, filename))
        
        return processed_files


def test_base_equipment_preprocessor():
    """测试基准装备预处理管理器"""
    print("=" * 60)
    print("基准装备预处理管理器测试")
    print("=" * 60)
    
    # 创建预处理管理器
    preprocessor = BaseEquipmentPreprocessor()
    
    # 测试处理所有图像
    print("\n1. 处理所有基准装备图像")
    results = preprocessor.process_all_images(force_reprocess=True)
    
    print(f"\n处理结果:")
    print(f"  总计: {results['total']}")
    print(f"  成功: {results['success']}")
    print(f"  失败: {results['failed']}")
    
    # 测试获取处理后的图像路径
    print("\n2. 测试获取处理后的图像路径")
    test_files = ['1000bp.webp', 'abyssal.webp', 'aegiraxe.webp']
    
    for filename in test_files:
        processed_path = preprocessor.get_processed_image_path(filename)
        if processed_path:
            print(f"  {filename} -> {processed_path}")
        else:
            print(f"  {filename} -> 未找到")
    
    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_base_equipment_preprocessor()