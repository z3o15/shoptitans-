#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
特征缓存管理器 - 预计算和缓存基准装备的ORB特征
避免每次识别时重复计算，显著提升性能
"""

import cv2
import os
import pickle
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path


class FeatureCacheManager:
    """特征缓存管理器，负责预计算、加载和管理基准装备特征"""
    
    def __init__(self, cache_dir="images/cache", target_size=(116, 116), nfeatures=1000):
        """
        初始化特征缓存管理器
        
        Args:
            cache_dir: 缓存目录路径
            target_size: 目标图像尺寸 (宽度, 高度)
            nfeatures: ORB特征点数量
        """
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "equipment_features.pkl")
        self.target_size = target_size
        self.nfeatures = nfeatures
        self.cache_data = None
        self.detector = cv2.ORB_create(nfeatures=nfeatures)
        
        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        print(f"✓ 特征缓存管理器初始化完成")
        print(f"  - 缓存目录: {cache_dir}")
        print(f"  - 缓存文件: {self.cache_file}")
        print(f"  - 目标尺寸: {target_size}")
        print(f"  - 特征点数: {nfeatures}")
    
    def build_feature_cache(self, base_equipment_dir):
        """
        构建基准装备特征缓存
        
        Args:
            base_equipment_dir: 基准装备目录路径
            
        Returns:
            bool: 构建是否成功
        """
        print("开始构建基准装备特征缓存...")
        print(f"基准装备目录: {base_equipment_dir}")
        print(f"缓存文件: {self.cache_file}")
        print(f"目标尺寸: {self.target_size}")
        
        # 初始化缓存字典
        cache = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "feature_type": "ORB",
            "target_size": self.target_size,
            "nfeatures": self.nfeatures,
            "features": {}
        }
        
        # 处理所有基准装备图像
        processed_count = 0
        skipped_count = 0
        
        for filename in os.listdir(base_equipment_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                file_path = os.path.join(base_equipment_dir, filename)
                equipment_name = os.path.splitext(filename)[0]
                
                print(f"处理: {filename}")
                
                try:
                    # 读取并预处理图像
                    img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
                    if img is None:
                        print(f"  ❌ 无法读取图像")
                        skipped_count += 1
                        continue
                    
                    # 记录原始尺寸
                    original_shape = img.shape
                    
                    # 调整图像尺寸到目标尺寸
                    img_resized = self._standardize_image_size(img)
                    
                    # 应用直方图均衡化增强对比度
                    img_resized = cv2.equalizeHist(img_resized)
                    
                    # 提取ORB特征
                    kp, des = self.detector.detectAndCompute(img_resized, None)
                    
                    if des is None:
                        print(f"  ❌ 无法提取特征")
                        skipped_count += 1
                        continue
                    
                    # 序列化关键点
                    kp_serialized = self._serialize_keypoints(kp)
                    
                    # 保存到缓存
                    cache["features"][filename] = {
                        "keypoints": kp_serialized,
                        "descriptors": des,
                        "image_shape": img_resized.shape,
                        "original_shape": original_shape
                    }
                    
                    print(f"  ✓ 提取了 {len(kp)} 个特征点")
                    processed_count += 1
                    
                except Exception as e:
                    print(f"  ❌ 处理失败: {e}")
                    skipped_count += 1
        
        # 保存缓存到文件
        try:
            with open(self.cache_file, "wb") as f:
                pickle.dump(cache, f)
            
            print(f"\n✅ 缓存构建完成!")
            print(f"  处理成功: {processed_count} 个文件")
            print(f"  跳过文件: {skipped_count} 个")
            print(f"  缓存文件: {self.cache_file}")
            print(f"  缓存大小: {os.path.getsize(self.cache_file) / 1024 / 1024:.2f} MB")
            
            # 加载到内存
            self.cache_data = cache
            return True
            
        except Exception as e:
            print(f"\n❌ 保存缓存失败: {e}")
            return False
    
    def build_cache(self, base_equipment_dir=None):
        """
        构建缓存（别名方法，为了向后兼容）
        
        Args:
            base_equipment_dir: 基准装备目录路径
            
        Returns:
            bool: 构建是否成功
        """
        if base_equipment_dir is None:
            base_equipment_dir = "images/base_equipment"
        return self.build_feature_cache(base_equipment_dir)
    
    def load_feature_cache(self):
        """
        加载特征缓存
        
        Returns:
            bool: 加载是否成功
        """
        if not os.path.exists(self.cache_file):
            print(f"缓存文件不存在: {self.cache_file}")
            return False
        
        try:
            with open(self.cache_file, "rb") as f:
                self.cache_data = pickle.load(f)
            
            print(f"✅ 特征缓存加载成功!")
            print(f"  版本: {self.cache_data.get('version', '未知')}")
            print(f"  创建时间: {self.cache_data.get('created_at', '未知')}")
            print(f"  特征类型: {self.cache_data.get('feature_type', '未知')}")
            print(f"  目标尺寸: {self.cache_data.get('target_size', '未知')}")
            print(f"  装备数量: {len(self.cache_data.get('features', {}))}")
            
            return True
            
        except Exception as e:
            print(f"❌ 加载缓存失败: {e}")
            self.cache_data = None
            return False
    
    def is_cache_valid(self):
        """
        检查缓存是否有效
        
        Returns:
            bool: 缓存是否有效
        """
        if self.cache_data is None:
            return False
        
        # 检查基本结构
        required_keys = ["version", "features", "target_size", "feature_type"]
        for key in required_keys:
            if key not in self.cache_data:
                print(f"缓存缺少必要字段: {key}")
                return False
        
        # 检查目标尺寸是否匹配
        if self.cache_data.get("target_size") != self.target_size:
            print(f"缓存目标尺寸不匹配: 缓存={self.cache_data.get('target_size')}, 期望={self.target_size}")
            return False
        
        # 检查特征类型是否匹配
        if self.cache_data.get("feature_type") != "ORB":
            print(f"缓存特征类型不匹配: {self.cache_data.get('feature_type')}")
            return False
        
        # 检查是否有特征数据
        features = self.cache_data.get("features", {})
        if not features:
            print("缓存中没有特征数据")
            return False
        
        return True
    
    def get_cached_features(self, equipment_name):
        """
        获取指定装备的缓存特征
        
        Args:
            equipment_name: 装备名称（不含扩展名）
            
        Returns:
            Tuple[List, np.ndarray]: (关键点列表, 描述符数组)，如果未找到返回(None, None)
        """
        if not self.is_cache_valid():
            return None, None
        
        features = self.cache_data.get("features", {})
        
        # 尝试多种可能的文件名
        possible_names = [
            f"{equipment_name}.webp",
            f"{equipment_name}.png",
            f"{equipment_name}.jpg",
            f"{equipment_name}.jpeg"
        ]
        
        for name in possible_names:
            if name in features:
                feature_data = features[name]
                
                # 反序列化关键点
                kp = self._deserialize_keypoints(feature_data["keypoints"])
                des = feature_data["descriptors"]
                
                return kp, des
        
        return None, None
    
    def get_all_equipment_names(self):
        """
        获取缓存中所有装备的名称
        
        Returns:
            List[str]: 装备名称列表（不含扩展名）
        """
        if not self.is_cache_valid():
            return []
        
        features = self.cache_data.get("features", {})
        names = []
        
        for filename in features.keys():
            name = os.path.splitext(filename)[0]
            if name not in names:
                names.append(name)
        
        return names
    
    def _serialize_keypoints(self, keypoints):
        """
        序列化关键点对象为可pickle的格式
        
        Args:
            keypoints: OpenCV关键点列表
            
        Returns:
            List[Tuple]: 序列化的关键点列表
        """
        return [(kp.pt, kp.size, kp.angle, kp.response, kp.octave, kp.class_id) for kp in keypoints]
    
    def _deserialize_keypoints(self, serialized_kp):
        """
        反序列化关键点对象
        
        Args:
            serialized_kp: 序列化的关键点列表
            
        Returns:
            List[cv2.KeyPoint]: OpenCV关键点列表
        """
        kp_list = []
        for (pt, size, angle, response, octave, class_id) in serialized_kp:
            kp = cv2.KeyPoint(
                x=pt[0], y=pt[1],
                size=size, angle=angle,
                response=response, octave=octave,
                class_id=class_id
            )
            kp_list.append(kp)
        return kp_list
    
    def _standardize_image_size(self, image):
        """
        标准化图像尺寸到目标尺寸
        
        Args:
            image: 输入图像
            
        Returns:
            np.ndarray: 调整尺寸后的图像
        """
        if image.shape[:2] == self.target_size:
            return image
        
        # 使用INTER_AREA保持图像质量
        return cv2.resize(image, self.target_size, interpolation=cv2.INTER_AREA)
    
    def get_cache_info(self):
        """
        获取缓存信息
        
        Returns:
            Dict[str, Any]: 缓存信息字典
        """
        if not self.is_cache_valid():
            return {"valid": False}
        
        features = self.cache_data.get("features", {})
        
        info = {
            "valid": True,
            "version": self.cache_data.get("version"),
            "created_at": self.cache_data.get("created_at"),
            "feature_type": self.cache_data.get("feature_type"),
            "target_size": self.cache_data.get("target_size"),
            "nfeatures": self.cache_data.get("nfeatures"),
            "equipment_count": len(features),
            "cache_file": self.cache_file,
            "cache_size": os.path.getsize(self.cache_file) if os.path.exists(self.cache_file) else 0
        }
        
        # 统计特征点数量
        total_keypoints = 0
        for filename, feature_data in features.items():
            keypoints = feature_data.get("keypoints", [])
            total_keypoints += len(keypoints)
        
        info["total_keypoints"] = total_keypoints
        info["avg_keypoints"] = total_keypoints / len(features) if features else 0
        
        return info
    
    def get_cache_stats(self):
        """
        获取缓存统计信息（别名方法，为了向后兼容）
        
        Returns:
            Dict[str, Any]: 缓存信息字典
        """
        return self.get_cache_info()


def test_feature_cache_manager():
    """测试特征缓存管理器"""
    print("=" * 60)
    print("特征缓存管理器测试")
    print("=" * 60)
    
    # 创建缓存管理器
    cache_manager = FeatureCacheManager(
        cache_dir="images/cache",
        target_size=(116, 116),
        nfeatures=1000
    )
    
    # 测试构建缓存
    base_equipment_dir = "images/base_equipment"
    if os.path.exists(base_equipment_dir):
        print("\n1. 构建特征缓存")
        success = cache_manager.build_feature_cache(base_equipment_dir)
        print(f"构建结果: {'成功' if success else '失败'}")
    
    # 测试加载缓存
    print("\n2. 加载特征缓存")
    success = cache_manager.load_feature_cache()
    print(f"加载结果: {'成功' if success else '失败'}")
    
    # 测试缓存有效性
    print("\n3. 检查缓存有效性")
    is_valid = cache_manager.is_cache_valid()
    print(f"缓存有效: {'是' if is_valid else '否'}")
    
    # 测试获取特征
    print("\n4. 测试获取特征")
    if is_valid:
        equipment_names = cache_manager.get_all_equipment_names()
        print(f"装备数量: {len(equipment_names)}")
        
        if equipment_names:
            test_name = equipment_names[0]
            kp, des = cache_manager.get_cached_features(test_name)
            print(f"测试装备: {test_name}")
            print(f"特征点数: {len(kp) if kp else 0}")
            print(f"描述符形状: {des.shape if des is not None else 'None'}")
    
    # 显示缓存信息
    print("\n5. 缓存信息")
    cache_info = cache_manager.get_cache_info()
    for key, value in cache_info.items():
        print(f"  {key}: {value}")
    
    print("\n✅ 特征缓存管理器测试完成")


if __name__ == "__main__":
    test_feature_cache_manager()