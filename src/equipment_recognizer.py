import cv2
import numpy as np
from PIL import Image
import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

# 导入图像哈希工具
try:
    from .utils.image_hash import get_dhash
except ImportError:
    try:
        from utils.image_hash import get_dhash
    except ImportError:
        print("警告: 无法导入图像哈希工具，dHash功能将不可用")
        get_dhash = None

# 导入独立模块的高级识别器
ADVANCED_MATCHER_AVAILABLE = False
AdvancedEquipmentRecognizer = None
AdvancedMatchResult = None
MatchedBy = None
ItemTemplate = None

# 导入特征匹配器
FEATURE_MATCHER_AVAILABLE = False
FeatureEquipmentRecognizer = None
FeatureMatchResult = None
FeatureType = None

# 导入增强特征匹配器
ENHANCED_FEATURE_MATCHER_AVAILABLE = False
EnhancedFeatureEquipmentRecognizer = None

try:
    # 尝试从项目根目录导入
    import sys
    from pathlib import Path
    
    # 获取项目根目录（src的上一级）
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    from src.advanced_matcher_standalone import (
        AdvancedEquipmentRecognizer,
        AdvancedMatchResult,
        MatchedBy,
        ItemTemplate
    )
    ADVANCED_MATCHER_AVAILABLE = True
    
    # 导入特征匹配器
    from src.feature_matcher import (
        FeatureEquipmentRecognizer,
        FeatureMatchResult,
        FeatureType
    )
    FEATURE_MATCHER_AVAILABLE = True
    
    # 导入增强特征匹配器
    from src.enhanced_feature_matcher import (
        EnhancedFeatureEquipmentRecognizer
    )
    ENHANCED_FEATURE_MATCHER_AVAILABLE = True
    
except ImportError as e:
    print(f"警告: 无法导入高级匹配器，将仅使用传统dHash算法: {e}")
    ADVANCED_MATCHER_AVAILABLE = False
    FEATURE_MATCHER_AVAILABLE = False
    ENHANCED_FEATURE_MATCHER_AVAILABLE = False

class EquipmentRecognizer:
    """游戏装备识别器，使用dHash算法进行图像相似度比较"""
    
    def __init__(self, default_threshold=80):
        """初始化装备识别器
        
        Args:
            default_threshold: 默认匹配阈值，相似度高于此值视为匹配
        """
        self.default_threshold = default_threshold
    
    def preprocess_image(self, image_path, size=(8, 8)):
        """预处理图像：转为灰度图并调整尺寸
        
        Args:
            image_path: 图像路径
            size: 调整后的尺寸，默认8x8用于dHash计算
        
        Returns:
            处理后的图像数组
        """
        try:
            with Image.open(image_path) as img:
                # 转为灰度图
                img_gray = img.convert('L')
                # 调整尺寸，使用LANCZOS算法保持图像质量
                img_resized = img_gray.resize(size, Image.Resampling.LANCZOS)
                return np.array(img_resized)
        except Exception as e:
            print(f"图像预处理出错: {e}")
            return None
    
    def get_dhash(self, image_path):
        """计算图像的dHash哈希值
        
        Args:
            image_path: 图像路径
        
        Returns:
            图像的dHash哈希字符串，若出错则返回None
        """
        img = self.preprocess_image(image_path)
        if img is None:
            return None
            
        # 计算相邻像素的差值
        diff = img[:, 1:] > img[:, :-1]
        # 转换为哈希字符串
        return ''.join(str(int(x)) for x in diff.flatten())
    
    def calculate_similarity(self, hash1, hash2):
        """计算两个哈希值的相似度
        
        Args:
            hash1: 第一个哈希值
            hash2: 第二个哈希值
        
        Returns:
            相似度百分比（0-100），若哈希值无效则返回0
        """
        if not hash1 or not hash2 or len(hash1) != len(hash2):
            return 0
            
        # 计算汉明距离：不同位的数量
        hamming_distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
        # 转换为相似度百分比
        similarity = (1 - hamming_distance / len(hash1)) * 100
        return round(similarity, 2)
    
    def compare_images(self, image_path1, image_path2, threshold=None):
        """比较两张图像的相似度
        
        Args:
            image_path1: 第一张图像路径
            image_path2: 第二张图像路径
            threshold: 匹配阈值，若为None则使用默认阈值
        
        Returns:
            (相似度, 是否匹配) 的元组
        """
        hash1 = self.get_dhash(image_path1)
        hash2 = self.get_dhash(image_path2)
        
        if not hash1 or not hash2:
            return 0, False
            
        similarity = self.calculate_similarity(hash1, hash2)
        current_threshold = threshold if threshold is not None else self.default_threshold
        
        return similarity, similarity >= current_threshold


class EnhancedEquipmentRecognizer:
    """增强版装备识别器，支持多种算法
    
    支持四种算法：
    1. 高级彩色模板匹配（AdvancedEquipmentRecognizer）
    2. 增强特征匹配（EnhancedFeatureEquipmentRecognizer）- 支持缓存
    3. 特征匹配（FeatureEquipmentRecognizer）
    4. 传统dHash算法
    """
    
    def __init__(self, default_threshold=80, algorithm_type="enhanced_feature",
                 enable_masking=True, enable_histogram=True,
                 feature_type="ORB", min_match_count=10, match_ratio_threshold=0.75,
                 use_cache=True, cache_dir="images/cache", target_size=(116, 116), nfeatures=1000,
                 auto_update_cache=True, base_equipment_dir="images/base_equipment"):
        """初始化增强版装备识别器
        
        Args:
            default_threshold: 默认匹配阈值，相似度高于此值视为匹配
            algorithm_type: 算法类型 ("enhanced_feature", "feature", "advanced", "traditional")
            enable_masking: 是否启用掩码匹配（仅高级算法）
            enable_histogram: 是否启用直方图验证（仅高级算法）
            feature_type: 特征类型 ("SIFT", "ORB", "AKAZE")
            min_match_count: 最少特征匹配数量
            match_ratio_threshold: 特征匹配比例阈值
            use_cache: 是否使用特征缓存（仅增强特征匹配）
            cache_dir: 缓存目录路径
            target_size: 目标图像尺寸
            nfeatures: ORB特征点数量
            auto_update_cache: 是否自动更新缓存
            base_equipment_dir: 基准装备目录
        """
        self.default_threshold = default_threshold
        self.algorithm_type = algorithm_type
        self.feature_type = feature_type
        self.min_match_count = min_match_count
        self.match_ratio_threshold = match_ratio_threshold
        self.use_cache = use_cache
        self.cache_dir = cache_dir
        self.target_size = target_size
        self.nfeatures = nfeatures
        self.auto_update_cache = auto_update_cache
        self.base_equipment_dir = base_equipment_dir
        
        # 初始化识别器
        self.advanced_recognizer = None
        self.feature_recognizer = None
        self.enhanced_feature_recognizer = None
        
        # 初始化自动缓存更新器
        self.auto_cache_updater = None
        
        if algorithm_type == "enhanced_feature" and ENHANCED_FEATURE_MATCHER_AVAILABLE:
            try:
                # 转换特征类型字符串为枚举
                feature_enum = FeatureType[feature_type.upper()]
                self.enhanced_feature_recognizer = EnhancedFeatureEquipmentRecognizer(
                    feature_type=feature_enum,
                    min_match_count=min_match_count,
                    match_ratio_threshold=match_ratio_threshold,
                    min_homography_inliers=max(6, min_match_count // 2),
                    use_cache=use_cache,
                    cache_dir=cache_dir,
                    target_size=target_size,
                    nfeatures=nfeatures
                )
                print(f"✓ 增强特征匹配装备识别器已启用（缓存：{'启用' if use_cache else '禁用'}）")
                
                # 初始化自动缓存更新器
                if use_cache and auto_update_cache:
                    try:
                        from .cache.auto_cache_updater import AutoCacheUpdater
                        self.auto_cache_updater = AutoCacheUpdater(
                            cache_dir=cache_dir,
                            target_size=target_size,
                            nfeatures=nfeatures,
                            auto_update=True
                        )
                        
                        # 检查是否需要自动更新缓存
                        self._check_and_update_cache()
                        
                    except Exception as e:
                        print(f"⚠️ 自动缓存更新器初始化失败: {e}")
                        self.auto_cache_updater = None
                
            except Exception as e:
                print(f"❌ 增强特征识别器初始化失败: {e}")
                raise RuntimeError("增强特征识别器初始化失败")
        elif algorithm_type == "advanced" and ADVANCED_MATCHER_AVAILABLE:
            try:
                self.advanced_recognizer = AdvancedEquipmentRecognizer(
                    enable_masking=enable_masking,
                    enable_histogram=enable_histogram
                )
                print(f"✓ 高级彩色装备识别器已启用")
            except Exception as e:
                print(f"❌ 高级识别器初始化失败: {e}")
                raise RuntimeError("高级识别器初始化失败")
        elif algorithm_type == "feature" and FEATURE_MATCHER_AVAILABLE:
            try:
                # 转换特征类型字符串为枚举
                feature_enum = FeatureType[feature_type.upper()]
                self.feature_recognizer = FeatureEquipmentRecognizer(
                    feature_type=feature_enum,
                    min_match_count=min_match_count,
                    match_ratio_threshold=match_ratio_threshold,
                    min_homography_inliers=max(6, min_match_count // 2)
                )
                print(f"✓ 特征匹配装备识别器已启用")
            except Exception as e:
                print(f"❌ 特征识别器初始化失败: {e}")
                raise RuntimeError("特征识别器初始化失败")
        elif algorithm_type == "traditional":
            print(f"✓ 传统dHash算法已启用")
        else:
            if algorithm_type == "enhanced_feature" and not ENHANCED_FEATURE_MATCHER_AVAILABLE:
                raise RuntimeError("增强特征匹配器不可用")
            elif algorithm_type == "advanced" and not ADVANCED_MATCHER_AVAILABLE:
                raise RuntimeError("高级匹配器不可用")
            elif algorithm_type == "feature" and not FEATURE_MATCHER_AVAILABLE:
                raise RuntimeError("特征匹配器不可用")
            else:
                raise ValueError(f"不支持的算法类型: {algorithm_type}")
        
        # 添加get_dhash方法（如果可用）
        if get_dhash is not None:
            self.get_dhash = get_dhash
            print(f"  - dHash功能: 已启用")
        else:
            print(f"  - dHash功能: 不可用（缺少图像哈希工具）")
        
        print(f"✓ 增强版装备识别器初始化完成")
        print(f"  - 当前算法: {self._get_algorithm_name()}")
        print(f"  - 默认阈值: {default_threshold}%")
        if algorithm_type == "enhanced_feature":
            print(f"  - 特征类型: {feature_type}")
            print(f"  - 最少匹配数: {min_match_count}")
            print(f"  - 匹配比例阈值: {match_ratio_threshold}")
            print(f"  - 使用缓存: {'是' if use_cache else '否'}")
            print(f"  - 自动更新缓存: {'是' if auto_update_cache else '否'}")
            print(f"  - 目标尺寸: {target_size}")
            print(f"  - 特征点数: {nfeatures}")
            if self.auto_cache_updater:
                cache_status = self.auto_cache_updater.get_cache_status()
                print(f"  - 缓存状态: {'存在' if cache_status['cache_exists'] else '不存在'}")
                if cache_status['cache_exists']:
                    print(f"  - 缓存装备数: {cache_status['equipment_count']}")
        elif algorithm_type == "advanced":
            print(f"  - 掩码匹配: {'启用' if enable_masking else '禁用'}")
            print(f"  - 直方图验证: {'启用' if enable_histogram else '禁用'}")
        elif algorithm_type == "feature":
            print(f"  - 特征类型: {feature_type}")
            print(f"  - 最少匹配数: {min_match_count}")
            print(f"  - 匹配比例阈值: {match_ratio_threshold}")
    
    def _get_algorithm_name(self) -> str:
        """获取当前算法名称"""
        if self.algorithm_type == "enhanced_feature":
            return f"增强特征匹配({self.feature_type}, 缓存)"
        elif self.algorithm_type == "advanced":
            return "高级彩色模板匹配"
        elif self.algorithm_type == "feature":
            return f"特征匹配({self.feature_type})"
        elif self.algorithm_type == "traditional":
            return "传统dHash"
        else:
            return "未知算法"
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """获取当前算法信息
        
        Returns:
            包含算法信息的字典
        """
        info = {
            'current_algorithm': self.algorithm_type,
            'algorithm_name': self._get_algorithm_name(),
            'default_threshold': self.default_threshold,
            'advanced_available': ADVANCED_MATCHER_AVAILABLE,
            'feature_available': FEATURE_MATCHER_AVAILABLE
        }
        
        if self.algorithm_type == "advanced" and self.advanced_recognizer is not None:
            info.update({
                'masking_enabled': self.advanced_recognizer.enable_masking,
                'histogram_enabled': self.advanced_recognizer.enable_histogram,
                'item_max_size': self.advanced_recognizer.item_max_size
            })
        elif self.algorithm_type == "feature" and self.feature_recognizer is not None:
            info.update({
                'feature_type': self.feature_type,
                'min_match_count': self.min_match_count,
                'match_ratio_threshold': self.match_ratio_threshold,
                'min_homography_inliers': self.feature_recognizer.min_homography_inliers
            })
        
        return info
    
    def _check_and_update_cache(self):
        """检查并自动更新缓存"""
        if not self.auto_cache_updater:
            return
        
        try:
            # 检查基准装备目录是否存在
            if not os.path.exists(self.base_equipment_dir):
                print(f"⚠️ 基准装备目录不存在: {self.base_equipment_dir}")
                return
            
            # 获取基准装备数量
            equipment_files = [f for f in os.listdir(self.base_equipment_dir)
                             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
            equipment_count = len(equipment_files)
            
            # 获取缓存状态
            cache_status = self.auto_cache_updater.get_cache_status()
            
            # 如果缓存不存在或装备数量>=50，自动更新缓存
            if not cache_status['cache_exists'] or equipment_count >= 50:
                print(f"检测到需要更新缓存:")
                print(f"  - 基准装备数: {equipment_count}")
                print(f"  - 缓存存在: {'是' if cache_status['cache_exists'] else '否'}")
                print(f"  - 缓存装备数: {cache_status['equipment_count']}")
                
                # 自动更新缓存
                success = self.auto_cache_updater.auto_update_if_needed(self.base_equipment_dir)
                if success:
                    print("✓ 缓存自动更新成功")
                else:
                    print("❌ 缓存自动更新失败")
            else:
                print(f"缓存已是最新，无需更新")
                
        except Exception as e:
            print(f"❌ 检查和更新缓存失败: {e}")
    
    def update_cache_manually(self, incremental_only=True):
        """手动更新缓存
        
        Args:
            incremental_only: 是否仅增量更新，False则完全重建
            
        Returns:
            是否更新成功
        """
        if not self.auto_cache_updater:
            print("❌ 自动缓存更新器未初始化")
            return False
        
        try:
            print(f"开始手动更新缓存...")
            success = self.auto_cache_updater.update_cache(self.base_equipment_dir, incremental_only)
            if success:
                print("✓ 缓存手动更新成功")
            else:
                print("❌ 缓存手动更新失败")
            return success
        except Exception as e:
            print(f"❌ 手动更新缓存失败: {e}")
            return False
    
    def get_cache_status(self):
        """获取缓存状态信息
        
        Returns:
            缓存状态字典
        """
        if not self.auto_cache_updater:
            return {"error": "自动缓存更新器未初始化"}
        
        try:
            return self.auto_cache_updater.get_cache_status()
        except Exception as e:
            return {"error": f"获取缓存状态失败: {e}"}
    
    def _convert_advanced_result(self, advanced_result: Any) -> Tuple[float, bool]:
        """将高级匹配结果转换为标准格式
        
        Args:
            advanced_result: 高级匹配结果
            
        Returns:
            (相似度, 是否匹配) 的元组
        """
        similarity = advanced_result.confidence
        is_match = similarity >= self.default_threshold
        return similarity, is_match
    
    def _convert_feature_result(self, feature_result: Any) -> Tuple[float, bool]:
        """将特征匹配结果转换为标准格式
        
        Args:
            feature_result: 特征匹配结果
            
        Returns:
            (相似度, 是否匹配) 的元组
        """
        similarity = feature_result.confidence
        is_match = similarity >= self.default_threshold
        return similarity, is_match
    
    def compare_images(self, image_path1, image_path2, threshold=None):
        """比较两张图像的相似度，根据算法类型选择匹配方法
        
        Args:
            image_path1: 第一张图像路径
            image_path2: 第二张图像路径
            threshold: 匹配阈值，若为None则使用默认阈值
            
        Returns:
            (相似度, 是否匹配) 的元组
        """
        current_threshold = threshold if threshold is not None else self.default_threshold
        
        try:
            if self.algorithm_type == "enhanced_feature" and self.enhanced_feature_recognizer is not None:
                # 使用增强特征匹配算法（支持缓存）
                print(f"使用增强特征匹配算法({self.feature_type}, 缓存)比较图像")
                feature_result = self.enhanced_feature_recognizer.recognize_equipment(image_path1, image_path2)
                similarity, is_match = self._convert_feature_result(feature_result)
                
                # 输出详细结果
                print(f"  - 匹配数量: {feature_result.match_count}")
                print(f"  - 单应性内点: {feature_result.homography_inliers}")
                print(f"  - 匹配比例: {feature_result.match_ratio:.4f}")
                print(f"  - 置信度: {feature_result.confidence:.2f}%")
                
            elif self.algorithm_type == "advanced" and self.advanced_recognizer is not None:
                # 使用高级彩色模板匹配算法
                print(f"使用高级彩色模板匹配算法比较图像")
                advanced_result = self.advanced_recognizer.recognize_equipment(image_path1, image_path2)
                similarity, is_match = self._convert_advanced_result(advanced_result)
                
                # 输出详细结果
                print(f"  - 匹配方式: {advanced_result.matched_by.name}")
                print(f"  - 模板相似度: {advanced_result.similarity:.2f}%")
                print(f"  - 综合置信度: {advanced_result.confidence:.2f}%")
                
            elif self.algorithm_type == "feature" and self.feature_recognizer is not None:
                # 使用特征匹配算法
                print(f"使用特征匹配算法({self.feature_type})比较图像")
                feature_result = self.feature_recognizer.recognize_equipment(image_path1, image_path2)
                similarity, is_match = self._convert_feature_result(feature_result)
                
                # 输出详细结果
                print(f"  - 匹配数量: {feature_result.match_count}")
                print(f"  - 单应性内点: {feature_result.homography_inliers}")
                print(f"  - 匹配比例: {feature_result.match_ratio:.4f}")
                print(f"  - 置信度: {feature_result.confidence:.2f}%")
                
            else:
                # 使用传统dHash算法
                print(f"使用传统dHash算法比较图像")
                traditional_recognizer = EquipmentRecognizer(current_threshold)
                similarity, is_match = traditional_recognizer.compare_images(image_path1, image_path2, current_threshold)
            
            # 应用阈值
            is_match = similarity >= current_threshold
            
            return similarity, is_match
            
        except Exception as e:
            print(f"图像比较失败: {e}")
            return 0.0, False
    
    def recognize_equipment_advanced(self, base_image_path: str, target_image_path: str) -> Optional[Any]:
        """使用高级算法识别装备（仅当高级算法可用时）
        
        Args:
            base_image_path: 基准装备图像路径
            target_image_path: 目标图像路径
            
        Returns:
            高级匹配结果，若高级算法不可用则返回None
        """
        if self.advanced_recognizer is None:
            print("错误: 高级识别器不可用")
            return None
            
        try:
            return self.advanced_recognizer.recognize_equipment(base_image_path, target_image_path)
        except Exception as e:
            print(f"高级装备识别失败: {e}")
            return None
    
    def set_algorithm_mode(self, use_advanced: bool) -> None:
        """设置算法模式
        
        Args:
            use_advanced: True表示使用高级算法，False表示使用传统算法
        """
        self.use_advanced_algorithm = use_advanced
        print(f"算法模式已设置为: {'高级彩色模板匹配' if use_advanced else '传统dHash'}")
    
    def batch_recognize(self, base_image_path: str, target_folder: str,
                       threshold: float = None) -> List[Dict[str, Any]]:
        """批量识别装备
        
        Args:
            base_image_path: 基准装备图像路径
            target_folder: 目标图像文件夹
            threshold: 相似度阈值，若为None则使用默认阈值
            
        Returns:
            识别结果列表
        """
        current_threshold = threshold if threshold is not None else self.default_threshold
        results = []
        
        try:
            # 获取所有目标图像
            target_files = []
            for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
                target_files.extend(Path(target_folder).glob(ext))
            
            print(f"找到 {len(target_files)} 个目标图像进行批量识别")
            
            # 对每个目标图像进行识别
            for target_file in target_files:
                target_path = str(target_file)
                
                if self.algorithm_type == "enhanced_feature" and self.enhanced_feature_recognizer is not None:
                    # 使用增强特征匹配算法（支持缓存）
                    feature_result = self.enhanced_feature_recognizer.recognize_equipment(
                        base_image_path, target_path
                    )
                    
                    if feature_result.confidence >= current_threshold:
                        result_dict = {
                            'item_name': feature_result.item_name,
                            'item_path': target_path,
                            'confidence': feature_result.confidence,
                            'similarity': feature_result.confidence,  # 特征匹配使用置信度作为相似度
                            'matched_by': f'ENHANCED_FEATURE_{feature_result.algorithm_used}',
                            'algorithm': 'enhanced_feature',
                            'match_count': feature_result.match_count,
                            'homography_inliers': feature_result.homography_inliers,
                            'match_ratio': feature_result.match_ratio
                        }
                        results.append(result_dict)
                        
                elif self.algorithm_type == "advanced" and self.advanced_recognizer is not None:
                    # 使用高级算法
                    advanced_result = self.advanced_recognizer.recognize_equipment(
                        base_image_path, target_path
                    )
                    
                    if advanced_result.confidence >= current_threshold:
                        result_dict = {
                            'item_name': advanced_result.item_name,
                            'item_path': target_path,
                            'confidence': advanced_result.confidence,
                            'similarity': advanced_result.similarity,
                            'matched_by': advanced_result.matched_by.name,
                            'algorithm': 'advanced'
                        }
                        results.append(result_dict)
                        
                elif self.algorithm_type == "feature" and self.feature_recognizer is not None:
                    # 使用特征匹配算法
                    feature_result = self.feature_recognizer.recognize_equipment(
                        base_image_path, target_path
                    )
                    
                    if feature_result.confidence >= current_threshold:
                        result_dict = {
                            'item_name': feature_result.item_name,
                            'item_path': target_path,
                            'confidence': feature_result.confidence,
                            'similarity': feature_result.confidence,  # 特征匹配使用置信度作为相似度
                            'matched_by': f'FEATURE_{feature_result.algorithm_used}',
                            'algorithm': 'feature',
                            'match_count': feature_result.match_count,
                            'homography_inliers': feature_result.homography_inliers,
                            'match_ratio': feature_result.match_ratio
                        }
                        results.append(result_dict)
                        
                else:
                    # 使用传统算法
                    traditional_recognizer = EquipmentRecognizer(current_threshold)
                    similarity, is_match = traditional_recognizer.compare_images(
                        base_image_path, target_path, current_threshold
                    )
                    
                    if is_match:
                        result_dict = {
                            'item_name': target_file.stem,
                            'item_path': target_path,
                            'confidence': similarity,
                            'similarity': similarity,
                            'matched_by': 'DHASH',
                            'algorithm': 'traditional'
                        }
                        results.append(result_dict)
            
            # 按置信度排序
            results.sort(key=lambda x: x['confidence'], reverse=True)
            
            print(f"批量识别完成，{len(results)} 个结果超过阈值 {current_threshold}%")
            
            return results
            
        except Exception as e:
            print(f"批量识别失败: {e}")
            return []


def test_enhanced_recognizer():
    """测试增强版识别器功能"""
    print("=" * 60)
    print("增强版装备识别器测试")
    print("=" * 60)
    
    # 创建增强版识别器实例
    recognizer = EnhancedEquipmentRecognizer(
        default_threshold=60,
        use_advanced_algorithm=True,
        enable_masking=True,
        enable_histogram=True
    )
    
    # 显示算法信息
    print("\n算法信息:")
    info = recognizer.get_algorithm_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # 测试图像路径
    base_image_path = "images/base_equipment/target_equipment_1.webp"
    target_image_path = "images/cropped_equipment/图层 2.png"
    
    # 检查文件是否存在
    if not os.path.exists(base_image_path):
        print(f"\n⚠️ 基准图像不存在: {base_image_path}")
        return
    
    if not os.path.exists(target_image_path):
        print(f"\n⚠️ 目标图像不存在: {target_image_path}")
        return
    
    # 测试高级算法
    print(f"\n测试高级算法:")
    recognizer.set_algorithm_mode(True)
    similarity1, match1 = recognizer.compare_images(base_image_path, target_image_path)
    print(f"相似度: {similarity1:.2f}%, 匹配: {match1}")
    
    # 测试传统算法
    print(f"\n测试传统算法:")
    recognizer.set_algorithm_mode(False)
    # 创建传统识别器实例进行测试
    traditional_recognizer = EquipmentRecognizer(60)
    similarity2, match2 = traditional_recognizer.compare_images(base_image_path, target_image_path)
    print(f"相似度: {similarity2:.2f}%, 匹配: {match2}")
    
    # 算法对比
    print(f"\n算法对比:")
    print(f"  高级算法: {similarity1:.2f}%")
    print(f"  传统算法: {similarity2:.2f}%")
    print(f"  差异: {similarity1 - similarity2:.2f}%")
    
    # 测试批量识别
    print(f"\n测试批量识别:")
    recognizer.set_algorithm_mode(True)  # 使用高级算法
    batch_results = recognizer.batch_recognize(base_image_path, "images/cropped_equipment", threshold=40.0)
    
    print(f"批量识别结果 (找到 {len(batch_results)} 个匹配):")
    for i, result in enumerate(batch_results[:5], 1):  # 只显示前5个结果
        print(f"{i}. {result['item_name']} - 置信度: {result['confidence']:.2f}% - 算法: {result['algorithm']}")
    
    print("\n✅ 增强版识别器测试完成")


if __name__ == "__main__":
    test_enhanced_recognizer()