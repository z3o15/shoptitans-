#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
特征缓存自动更新器
当base_equipment下新增装备时自动检测并更新特征缓存
"""

import os
import cv2
import pickle
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from ..utils.image_hash import get_dhash
from ..feature_cache_manager import FeatureCacheManager


class AutoCacheUpdater:
    """特征缓存自动更新器类
    
    当base_equipment下新增装备时自动检测并更新特征缓存
    """
    
    def __init__(self, cache_dir="images/cache", target_size=(116, 116), 
                 nfeatures=3000, auto_update=True):
        """初始化自动缓存更新器
        
        Args:
            cache_dir: 缓存目录
            target_size: 目标图像尺寸
            nfeatures: ORB特征点数量
            auto_update: 是否启用自动更新
        """
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "equipment_features.pkl")
        self.metadata_file = os.path.join(cache_dir, "cache_metadata.json")
        self.target_size = target_size
        self.nfeatures = nfeatures
        self.auto_update = auto_update
        
        # 创建ORB检测器
        self.detector = cv2.ORB_create(
            nfeatures=nfeatures,
            scaleFactor=1.1,
            edgeThreshold=15,
            patchSize=31
        )
        
        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        # 加载缓存元数据
        self.metadata = self._load_metadata()
        
        print(f"✓ 特征缓存自动更新器初始化完成")
        print(f"  - 缓存目录: {cache_dir}")
        print(f"  - 目标尺寸: {target_size}")
        print(f"  - 特征点数: {nfeatures}")
        print(f"  - 自动更新: {'启用' if auto_update else '禁用'}")
    
    def _load_metadata(self) -> Dict[str, Any]:
        """加载缓存元数据
        
        Returns:
            缓存元数据字典
        """
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载缓存元数据失败: {e}")
                return {}
        else:
            return {}
    
    def _save_metadata(self, metadata: Dict[str, Any]) -> bool:
        """保存缓存元数据
        
        Args:
            metadata: 元数据字典
            
        Returns:
            是否保存成功
        """
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 保存缓存元数据失败: {e}")
            return False
    
    def _get_file_hash(self, file_path: str) -> str:
        """计算文件哈希值
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件哈希值
        """
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            return hashlib.md5(file_content).hexdigest()
        except Exception as e:
            print(f"❌ 计算文件哈希失败: {e}")
            return ""
    
    def _extract_features(self, image_path: str) -> Tuple[List, Optional[np.ndarray]]:
        """提取图像特征
        
        Args:
            image_path: 图像路径
            
        Returns:
            (关键点列表, 描述符数组) 的元组
        """
        try:
            # 读取并预处理图像
            image = cv2.imread(image_path)
            if image is None:
                return [], None
            
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # 应用预处理增强
            gray = cv2.equalizeHist(gray)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # 调整尺寸
            gray = cv2.resize(gray, self.target_size, interpolation=cv2.INTER_AREA)
            
            # 提取ORB特征
            keypoints, descriptors = self.detector.detectAndCompute(gray, None)
            
            return keypoints, descriptors
            
        except Exception as e:
            print(f"❌ 特征提取失败: {image_path}, 错误: {e}")
            return [], None
    
    def _serialize_keypoints(self, keypoints: List) -> List[Tuple]:
        """序列化关键点对象
        
        Args:
            keypoints: OpenCV关键点列表
            
        Returns:
            序列化的关键点列表
        """
        return [(kp.pt, kp.size, kp.angle, kp.response, kp.octave, kp.class_id) for kp in keypoints]
    
    def check_for_updates(self, base_equipment_dir: str) -> Dict[str, Any]:
        """检查是否有新文件需要更新缓存
        
        Args:
            base_equipment_dir: 基准装备目录
            
        Returns:
            检查结果字典
        """
        if not self.auto_update:
            return {"needs_update": False, "new_files": [], "updated_files": []}
        
        try:
            # 获取当前目录中的所有图像文件
            current_files = {}
            for filename in os.listdir(base_equipment_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    file_path = os.path.join(base_equipment_dir, filename)
                    file_hash = self._get_file_hash(file_path)
                    current_files[filename] = file_hash
            
            # 获取上次缓存时的文件列表
            cached_files = self.metadata.get("files", {})
            
            # 找出新增文件
            new_files = []
            for filename, file_hash in current_files.items():
                if filename not in cached_files or cached_files[filename] != file_hash:
                    new_files.append(filename)
            
            # 找出已删除或修改的文件
            updated_files = []
            for filename, file_hash in cached_files.items():
                if filename not in current_files:
                    updated_files.append(filename)
            
            needs_update = len(new_files) > 0 or len(updated_files) > 0
            
            result = {
                "needs_update": needs_update,
                "new_files": new_files,
                "updated_files": updated_files,
                "current_files": current_files,
                "cached_files": cached_files
            }
            
            if needs_update:
                print(f"检测到缓存更新需求:")
                print(f"  - 新增文件: {len(new_files)} 个")
                print(f"  - 删除/修改文件: {len(updated_files)} 个")
            
            return result
            
        except Exception as e:
            print(f"❌ 检查缓存更新失败: {e}")
            return {"needs_update": False, "new_files": [], "updated_files": []}
    
    def update_cache(self, base_equipment_dir: str, incremental_only=True) -> bool:
        """更新特征缓存
        
        Args:
            base_equipment_dir: 基准装备目录
            incremental_only: 是否仅增量更新，False则完全重建
            
        Returns:
            是否更新成功
        """
        try:
            print(f"开始更新特征缓存...")
            print(f"  - 基准装备目录: {base_equipment_dir}")
            print(f"  - 增量更新: {incremental_only}")
            
            # 检查更新需求
            check_result = self.check_for_updates(base_equipment_dir)
            
            if not check_result["needs_update"] and incremental_only:
                print("  - 缓存已是最新，无需更新")
                return True
            
            # 加载现有缓存
            cache_data = None
            if incremental_only and os.path.exists(self.cache_file):
                try:
                    with open(self.cache_file, 'rb') as f:
                        cache_data = pickle.load(f)
                    print(f"  - 加载现有缓存，包含 {len(cache_data.get('features', {}))} 个装备")
                except Exception as e:
                    print(f"  - 加载现有缓存失败: {e}")
                    cache_data = None
            
            # 创建新的缓存数据结构
            if cache_data is None:
                cache_data = {
                    "version": "2.0",
                    "created_at": datetime.now().isoformat(),
                    "feature_type": "ORB",
                    "target_size": self.target_size,
                    "nfeatures": self.nfeatures,
                    "features": {}
                }
            
            # 处理所有文件
            processed_count = 0
            skipped_count = 0
            failed_count = 0
            
            for filename in os.listdir(base_equipment_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    file_path = os.path.join(base_equipment_dir, filename)
                    file_hash = self._get_file_hash(file_path)
                    
                    # 检查是否需要处理此文件
                    needs_processing = (
                        not incremental_only or  # 完全重建模式
                        filename in check_result["new_files"] or  # 新增文件
                        filename in check_result["updated_files"]  # 修改文件
                    )
                    
                    if needs_processing:
                        # 提取特征
                        keypoints, descriptors = self._extract_features(file_path)
                        
                        if descriptors is not None and len(keypoints) > 0:
                            # 序列化关键点
                            kp_serialized = self._serialize_keypoints(keypoints)
                            
                            # 保存到缓存
                            cache_data["features"][filename] = {
                                "keypoints": kp_serialized,
                                "descriptors": descriptors,
                                "image_shape": descriptors.shape if descriptors is not None else None,
                                "file_hash": file_hash,
                                "processed_at": datetime.now().isoformat()
                            }
                            processed_count += 1
                            print(f"  ✓ 处理成功: {filename} ({len(keypoints)} 特征点)")
                        else:
                            failed_count += 1
                            print(f"  ❌ 处理失败: {filename} (特征点不足)")
                    else:
                        skipped_count += 1
                        print(f"  - 跳过: {filename} (无需更新)")
            
            # 保存缓存
            try:
                with open(self.cache_file, 'wb') as f:
                    pickle.dump(cache_data, f)
                
                # 更新元数据
                files_dict = {filename: self._get_file_hash(os.path.join(base_equipment_dir, filename))
                             for filename in os.listdir(base_equipment_dir)
                             if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))}
                
                # 创建一个不包含numpy数组的元数据副本用于JSON序列化
                metadata_for_json = {
                    "files": files_dict,
                    "updated_at": datetime.now().isoformat(),
                    "version": cache_data.get("version", "2.0"),
                    "feature_type": cache_data.get("feature_type", "ORB"),
                    "target_size": cache_data.get("target_size", self.target_size),
                    "nfeatures": cache_data.get("nfeatures", self.nfeatures)
                }
                
                self._save_metadata(metadata_for_json)
                
                print(f"\n✓ 缓存更新完成:")
                print(f"  - 处理文件: {processed_count} 个")
                print(f"  - 跳过文件: {skipped_count} 个")
                print(f"  - 失败文件: {failed_count} 个")
                print(f"  - 缓存文件: {self.cache_file}")
                
                return True
                
            except Exception as e:
                print(f"❌ 保存缓存失败: {e}")
                return False
        
        except Exception as e:
            print(f"❌ 缓存更新过程失败: {e}")
            return False
    
    def auto_update_if_needed(self, base_equipment_dir: str) -> bool:
        """如果需要则自动更新缓存
        
        Args:
            base_equipment_dir: 基准装备目录
            
        Returns:
            是否执行了更新
        """
        try:
            # 检查是否需要更新
            check_result = self.check_for_updates(base_equipment_dir)
            
            if check_result["needs_update"]:
                print("检测到缓存更新需求，开始自动更新...")
                return self.update_cache(base_equipment_dir, incremental_only=True)
            else:
                print("缓存已是最新，无需更新")
                return True
                
        except Exception as e:
            print(f"❌ 自动更新检查失败: {e}")
            return False
    
    def get_cache_status(self) -> Dict[str, Any]:
        """获取缓存状态信息
        
        Returns:
            缓存状态字典
        """
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                
                features = cache_data.get("features", {})
                
                status = {
                    "cache_exists": True,
                    "cache_file": self.cache_file,
                    "cache_size": os.path.getsize(self.cache_file) if os.path.exists(self.cache_file) else 0,
                    "equipment_count": len(features),
                    "cache_version": cache_data.get("version", "未知"),
                    "created_at": cache_data.get("created_at", "未知"),
                    "updated_at": cache_data.get("updated_at", "未知"),
                    "target_size": cache_data.get("target_size", "未知"),
                    "nfeatures": cache_data.get("nfeatures", "未知")
                }
            else:
                status = {
                    "cache_exists": False,
                    "cache_file": self.cache_file,
                    "equipment_count": 0,
                    "cache_version": "无",
                    "created_at": "无",
                    "updated_at": "无",
                    "target_size": self.target_size,
                    "nfeatures": self.nfeatures
                }
            
            return status
            
        except Exception as e:
            print(f"❌ 获取缓存状态失败: {e}")
            return {"error": str(e)}


def test_auto_cache_updater():
    """测试自动缓存更新器"""
    print("=" * 60)
    print("自动缓存更新器测试")
    print("=" * 60)
    
    # 创建测试目录
    test_dir = "test_equipment"
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建测试图像
    test_images = [
        ("equipment1.png", np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)),
        ("equipment2.png", np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)),
        ("equipment3.png", np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8))
    ]
    
    # 保存测试图像
    for filename, image in test_images:
        cv2.imwrite(os.path.join(test_dir, filename), image)
        print(f"创建测试图像: {filename}")
    
    # 创建自动缓存更新器
    updater = AutoCacheUpdater(cache_dir="test_cache", auto_update=True)
    
    # 第一次更新（创建缓存）
    print("\n第一次更新（创建缓存）:")
    success = updater.update_cache(test_dir, incremental_only=False)
    print(f"更新结果: {'成功' if success else '失败'}")
    
    # 检查状态
    status = updater.get_cache_status()
    print(f"缓存状态: {status['equipment_count']} 个装备")
    
    # 添加新图像
    new_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    cv2.imwrite(os.path.join(test_dir, "equipment4.png"), new_image)
    print(f"\n添加新图像: equipment4.png")
    
    # 第二次更新（增量更新）
    print("\n第二次更新（增量更新）:")
    success = updater.update_cache(test_dir, incremental_only=True)
    print(f"更新结果: {'成功' if success else '失败'}")
    
    # 检查状态
    status = updater.get_cache_status()
    print(f"缓存状态: {status['equipment_count']} 个装备")
    
    # 清理测试文件
    try:
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        if os.path.exists("test_cache"):
            shutil.rmtree("test_cache")
    except:
        pass
    
    print(f"\n✓ 测试完成")


if __name__ == "__main__":
    test_auto_cache_updater()