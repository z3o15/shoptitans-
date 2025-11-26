#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
装备特征缓存系统
用于缓存基准装备的特征数据，避免重复计算
"""

import os
import pickle
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np
from dataclasses import dataclass

@dataclass
class ImageFeatures:
    """图像特征数据类"""
    file_path: str
    file_hash: str
    lab_image: np.ndarray
    histogram: np.ndarray
    shape: Tuple[int, int, int]
    computed_at: str

    def to_dict(self) -> Dict:
        """转换为字典格式（用于序列化）"""
        return {
            'file_path': self.file_path,
            'file_hash': self.file_hash,
            'lab_image': self.lab_image,
            'histogram': self.histogram,
            'shape': self.shape,
            'computed_at': self.computed_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ImageFeatures':
        """从字典格式创建实例（用于反序列化）"""
        return cls(
            file_path=data['file_path'],
            file_hash=data['file_hash'],
            lab_image=data['lab_image'],
            histogram=data['histogram'],
            shape=tuple(data['shape']),
            computed_at=data['computed_at']
        )

class FeatureCache:
    """特征缓存管理器"""

    def __init__(self, cache_dir: Path = None):
        """
        初始化特征缓存管理器

        Args:
            cache_dir: 缓存目录路径，默认为 output_enter_image/feature_cache
        """
        if cache_dir is None:
            project_root = Path(__file__).parent.parent.parent
            cache_dir = project_root / "output_enter_image" / "feature_cache"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 缓存索引文件
        self.index_file = self.cache_dir / "cache_index.json"

        # 特征缓存
        self.features: Dict[str, ImageFeatures] = {}

        # 加载缓存索引
        self._load_cache_index()

    def _get_file_hash(self, file_path: Path) -> str:
        """计算文件的MD5哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _get_cache_file_path(self, file_path: Path) -> Path:
        """获取缓存文件路径"""
        # 使用文件路径和目录名创建唯一缓存文件名
        relative_path = str(file_path.relative_to(file_path.anchor))
        safe_name = hashlib.md5(relative_path.encode()).hexdigest()
        return self.cache_dir / f"{safe_name}.pkl"

    def _load_cache_index(self) -> None:
        """加载缓存索引"""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)

                # 加载所有特征文件
                for cache_info in index_data['features']:
                    cache_file = self.cache_dir / cache_info['cache_file']
                    if cache_file.exists():
                        try:
                            with open(cache_file, 'rb') as f:
                                feature_data = pickle.load(f)
                                features = ImageFeatures.from_dict(feature_data)
                                self.features[features.file_path] = features
                        except Exception as e:
                            print(f"警告: 无法加载缓存文件 {cache_file}: {e}")

                print(f"[OK] 从缓存加载了 {len(self.features)} 个特征")
            else:
                print("缓存索引不存在，将创建新缓存")
        except Exception as e:
            print(f"加载缓存索引时出错: {e}")

    def _save_cache_index(self) -> None:
        """保存缓存索引"""
        try:
            index_data = {
                'last_updated': datetime.now().isoformat(),
                'total_features': len(self.features),
                'features': []
            }

            # 为每个特征创建索引条目
            for file_path, features in self.features.items():
                cache_file = self._get_cache_file_path(Path(file_path))
                index_data['features'].append({
                    'file_path': file_path,
                    'file_hash': features.file_hash,
                    'cache_file': cache_file.name
                })

            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"保存缓存索引时出错: {e}")

    def _save_features(self, features: ImageFeatures) -> None:
        """保存特征数据到缓存文件"""
        try:
            cache_file = self._get_cache_file_path(Path(features.file_path))
            with open(cache_file, 'wb') as f:
                pickle.dump(features.to_dict(), f)
        except Exception as e:
            print(f"保存特征数据时出错: {e}")

    def compute_features(self, image_path: Path) -> ImageFeatures:
        """
        计算图像的特征

        Args:
            image_path: 图像文件路径

        Returns:
            图像特征对象
        """
        print(f"计算特征: {image_path}")

        # 检查文件是否存在
        if not image_path.exists():
            raise FileNotFoundError(f"图像文件不存在: {image_path}")

        # 计算文件哈希
        file_hash = self._get_file_hash(image_path)

        # 加载图像
        try:
            # 支持中文路径的图像读取
            image_array = np.fromfile(str(image_path), dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            if image is None:
                raise ValueError(f"无法加载图像: {image_path}")

        except Exception as e:
            raise ValueError(f"加载图像失败 {image_path}: {e}")

        # 转换为LAB色彩空间
        lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

        # 计算LAB空间的直方图
        hist_l = cv2.calcHist([lab_image], [0], None, [256], [0, 256])
        hist_a = cv2.calcHist([lab_image], [1], None, [256], [0, 256])
        hist_b = cv2.calcHist([lab_image], [2], None, [256], [0, 256])

        # 合并三个通道的直方图
        histogram = np.vstack([hist_l, hist_a, hist_b])

        # 创建特征对象
        features = ImageFeatures(
            file_path=str(image_path),
            file_hash=file_hash,
            lab_image=lab_image,
            histogram=histogram,
            shape=image.shape,
            computed_at=datetime.now().isoformat()
        )

        return features

    def get_or_compute_features(self, image_path: Path, force_recompute: bool = False) -> Optional[ImageFeatures]:
        """
        获取图像特征，如果缓存中不存在则计算新特征

        Args:
            image_path: 图像文件路径
            force_recompute: 是否强制重新计算

        Returns:
            图像特征对象，如果出错则返回None
        """
        file_path_str = str(image_path)

        # 检查缓存中是否存在
        if not force_recompute and file_path_str in self.features:
            cached_features = self.features[file_path_str]

            # 验证文件是否已修改
            current_hash = self._get_file_hash(image_path)
            if cached_features.file_hash == current_hash:
                print(f"[OK] 使用缓存特征: {image_path.name}")
                return cached_features
            else:
                print(f"文件已修改，重新计算特征: {image_path.name}")
                # 从缓存中移除过期特征
                del self.features[file_path_str]

        try:
            # 计算新特征
            features = self.compute_features(image_path)

            # 保存到内存缓存
            self.features[file_path_str] = features

            # 保存到文件缓存
            self._save_features(features)

            return features

        except Exception as e:
            print(f"计算特征失败 {image_path}: {e}")
            return None

    def batch_compute_features(self, image_dir: Path, force_recompute: bool = False,
                             progress_callback: callable = None) -> Dict[str, ImageFeatures]:
        """
        批量计算目录中所有图像的特征

        Args:
            image_dir: 图像目录路径
            force_recompute: 是否强制重新计算
            progress_callback: 进度回调函数

        Returns:
            特征字典 {文件路径: 特征对象}
        """
        if not image_dir.exists():
            raise FileNotFoundError(f"图像目录不存在: {image_dir}")

        # 查找所有图像文件
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
        image_files = []

        for ext in image_extensions:
            image_files.extend(image_dir.glob(f"*{ext}"))
            image_files.extend(image_dir.glob(f"*{ext.upper()}"))

        print(f"找到 {len(image_files)} 个图像文件")

        features_dict = {}
        processed_count = 0

        for image_file in image_files:
            features = self.get_or_compute_features(image_file, force_recompute)
            if features:
                features_dict[str(image_file)] = features
                processed_count += 1

            # 调用进度回调
            if progress_callback:
                progress_callback(processed_count, len(image_files), image_file.name)

        # 保存缓存索引
        self._save_cache_index()

        print(f"[OK] 完成特征计算，成功处理 {len(features_dict)} 个图像")
        return features_dict

    def clear_cache(self) -> None:
        """清空所有缓存"""
        try:
            # 删除所有缓存文件
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()

            # 删除索引文件
            if self.index_file.exists():
                self.index_file.unlink()

            # 清空内存缓存
            self.features.clear()

            print("[OK] 缓存已清空")

        except Exception as e:
            print(f"清空缓存时出错: {e}")

    def get_cache_info(self) -> Dict:
        """获取缓存信息"""
        return {
            'cache_dir': str(self.cache_dir),
            'total_features': len(self.features),
            'cache_exists': self.index_file.exists(),
            'last_updated': None
        }

def build_feature_cache(base_dir: str, force_recompute: bool = False) -> FeatureCache:
    """
    构建基准装备的特征缓存

    Args:
        base_dir: 基准装备目录
        force_recompute: 是否强制重新计算

    Returns:
        特征缓存管理器
    """
    print("=" * 60)
    print("构建装备特征缓存")
    print("=" * 60)

    cache = FeatureCache()

    def progress_callback(current, total, filename):
        progress = (current / total) * 100
        print(f"进度: {current}/{total} ({progress:.1f}%) - {filename}")

    try:
        base_path = Path(base_dir)
        features = cache.batch_compute_features(base_path, force_recompute, progress_callback)

        print(f"\n[OK] 特征缓存构建完成!")
        print(f"缓存目录: {cache.cache_dir}")
        print(f"缓存特征数: {len(features)}")

        return cache

    except Exception as e:
        print(f"构建特征缓存失败: {e}")
        return cache

if __name__ == "__main__":
    # 示例用法
    import sys

    if len(sys.argv) < 2:
        print("用法: python feature_cache.py <基准装备目录> [--force]")
        sys.exit(1)

    base_dir = sys.argv[1]
    force_recompute = "--force" in sys.argv

    build_feature_cache(base_dir, force_recompute)