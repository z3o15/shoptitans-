#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一配置管理模块
整合所有配置管理功能，提供统一的配置访问接口
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime


class UnifiedConfigManager:
    """统一配置管理器，负责管理所有系统配置"""
    
    def __init__(self, config_path: str = "config/unified_config.json"):
        """初始化统一配置管理器
        
        Args:
            config_path: 统一配置文件路径，默认为config/unified_config.json
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件
        
        Returns:
            配置字典，如果文件不存在则返回默认配置
        """
        default_config = self._get_default_config()
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # 合并默认配置和加载的配置
                config = self._merge_configs(default_config, loaded_config)
                return config
            except Exception as e:
                print(f"⚠️ 配置文件加载失败，使用默认配置: {e}")
                return default_config
        else:
            print(f"⚠️ 配置文件不存在，使用默认配置: {self.config_path}")
            # 创建默认配置文件
            self._save_config(default_config)
            return default_config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置
        
        Returns:
            默认配置字典
        """
        return {
            "recognition": {
                "default_threshold": 80,
                "algorithm_type": "enhanced_feature",
                "feature_type": "ORB",
                "min_match_count": 8,
                "match_ratio_threshold": 0.75,
                "min_homography_inliers": 6,
                "use_advanced_algorithm": True,
                "enable_masking": True,
                "enable_histogram": True,
                "algorithm_description": "增强特征匹配算法，使用预计算缓存提供高性能的装备识别"
            },
            "cutting": {
                "default_method": "fixed",
                "fixed_grid": [5, 2],
                "fixed_item_width": 210,
                "fixed_item_height": 160,
                "fixed_margin_left": 10,
                "fixed_margin_top": 275,
                "fixed_h_spacing": 15,
                "fixed_v_spacing": 20,
                "contour_min_area": 800,
                "contour_max_area": 50000
            },
            "paths": {
                "images_dir": "images",
                "base_equipment_dir": "base_equipment",
                "game_screenshots_dir": "game_screenshots",
                "cropped_equipment_dir": "cropped_equipment",
                "logs_dir": "recognition_logs",
                "output_dir": "output",
                "tests_dir": "tests"
            },
            "logging": {
                "enable_logging": True,
                "log_level": "INFO",
                "include_algorithm_info": True,
                "include_performance_metrics": True
            },
            "performance": {
                "enable_caching": True,
                "cache_size": 100,
                "parallel_processing": False,
                "max_workers": 4
            },
            "ui": {
                "show_algorithm_selection": True,
                "show_performance_info": True,
                "show_detailed_results": True
            },
            "annotation": {
                "enable_annotation": True,
                "circle_color": "red",
                "circle_width": 3,
                "font_size": 12,
                "show_similarity_text": True,
                "auto_generate_annotation": False,
                "annotation_output_dir": "annotated_screenshots"
            },
            "ocr": {
                "enabled": True,
                "engine": "easyocr",
                "language": ["en"],
                "price_pattern": "\\d+",
                "confidence_threshold": 0.8,
                "preprocessing": {
                    "grayscale": True,
                    "threshold": True,
                    "denoise": True
                },
                "input_folder": "images/cropped_equipment_marker",
                "output_csv": "ocr_rename_records.csv",
                "rename_separator": "_",
                "supported_formats": [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]
            },
            "output_structure": {
                "use_timestamp_dirs": True,
                "timestamp_format": "%Y%m%d_%H%M%S",
                "step_subdirs": {
                    "step1": "preprocessing",
                    "step2": "cutting",
                    "step3": "matching",
                    "step4": "ocr"
                },
                "standard_subdirs": ["images", "logs", "reports", "temp"]
            }
        }
    
    def _merge_configs(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """合并配置字典，保留默认值中不存在于加载配置中的项
        
        Args:
            default: 默认配置
            loaded: 加载的配置
            
        Returns:
            合并后的配置
        """
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """保存配置到文件
        
        Args:
            config: 要保存的配置字典
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"✓ 配置文件已保存: {self.config_path}")
        except Exception as e:
            print(f"❌ 配置文件保存失败: {e}")
    
    def get_config(self, section: str, default: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取指定配置节
        
        Args:
            section: 配置节名称
            default: 默认值，如果节不存在则返回此值
            
        Returns:
            配置节字典
        """
        return self.config.get(section, default or {})
    
    def update_config(self, section: str, **kwargs) -> None:
        """更新指定配置节
        
        Args:
            section: 配置节名称
            **kwargs: 要更新的配置项
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section].update(kwargs)
        self._save_config(self.config)
        print(f"✓ {section}配置已更新")
    
    # 识别配置相关方法
    def get_recognition_config(self) -> Dict[str, Any]:
        """获取识别相关配置"""
        return self.get_config("recognition")
    
    def update_recognition_config(self, **kwargs) -> None:
        """更新识别配置"""
        self.update_config("recognition", **kwargs)
    
    def get_algorithm_mode(self) -> bool:
        """获取算法模式"""
        return self.get_recognition_config().get("use_advanced_algorithm", True)
    
    def set_algorithm_mode(self, use_advanced: bool) -> None:
        """设置算法模式"""
        self.update_recognition_config(use_advanced_algorithm=use_advanced)
        print(f"算法模式已更新为: {'高级算法' if use_advanced else '传统算法'}")
    
    def get_default_threshold(self) -> float:
        """获取默认阈值"""
        return self.get_recognition_config().get("default_threshold", 80)
    
    def set_default_threshold(self, threshold: float) -> None:
        """设置默认阈值"""
        self.update_recognition_config(default_threshold=threshold)
        print(f"默认阈值已更新为: {threshold}%")
    
    # 切割配置相关方法
    def get_cutting_config(self) -> Dict[str, Any]:
        """获取切割相关配置"""
        return self.get_config("cutting")
    
    def get_cutting_params(self) -> Dict[str, Any]:
        """获取切割参数"""
        cutting_config = self.get_cutting_config()
        return {
            'grid': tuple(cutting_config.get("fixed_grid", [5, 2])),
            'item_width': cutting_config.get("fixed_item_width", 210),
            'item_height': cutting_config.get("fixed_item_height", 160),
            'margin_left': cutting_config.get("fixed_margin_left", 10),
            'margin_top': cutting_config.get("fixed_margin_top", 275),
            'h_spacing': cutting_config.get("fixed_h_spacing", 15),
            'v_spacing': cutting_config.get("fixed_v_spacing", 20)
        }
    
    # 路径配置相关方法
    def get_paths_config(self) -> Dict[str, Any]:
        """获取路径相关配置"""
        return self.get_config("paths")
    
    def get_output_path(self, step: str, create_timestamp: bool = True) -> str:
        """获取输出路径
        
        Args:
            step: 步骤名称 (step1, step2, step3, step4)
            create_timestamp: 是否创建时间戳目录
            
        Returns:
            输出路径
        """
        paths_config = self.get_paths_config()
        output_config = self.get_config("output_structure")
        
        base_output_dir = paths_config.get("output_dir", "output")
        
        if create_timestamp and output_config.get("use_timestamp_dirs", True):
            timestamp = datetime.now().strftime(output_config.get("timestamp_format", "%Y%m%d_%H%M%S"))
            base_output_dir = os.path.join(base_output_dir, timestamp)
        
        step_subdirs = output_config.get("step_subdirs", {})
        step_name = step_subdirs.get(step, step)
        
        return os.path.join(base_output_dir, step_name)
    
    def ensure_output_dirs(self, step: str) -> Dict[str, str]:
        """确保输出目录存在并返回各子目录路径
        
        Args:
            step: 步骤名称
            
        Returns:
            包含各子目录路径的字典
        """
        base_path = self.get_output_path(step)
        output_config = self.get_config("output_structure")
        standard_subdirs = output_config.get("standard_subdirs", ["images", "logs", "reports", "temp"])
        
        dirs = {}
        for subdir in standard_subdirs:
            dir_path = os.path.join(base_path, subdir)
            os.makedirs(dir_path, exist_ok=True)
            dirs[subdir] = dir_path
        
        return dirs
    
    # OCR配置相关方法
    def get_ocr_config(self) -> Dict[str, Any]:
        """获取OCR相关配置"""
        return self.get_config("ocr")
    
    def update_ocr_config(self, **kwargs) -> None:
        """更新OCR配置"""
        self.update_config("ocr", **kwargs)
    
    def is_ocr_enabled(self) -> bool:
        """检查OCR功能是否启用"""
        return self.get_ocr_config().get("enabled", True)
    
    def set_ocr_enabled(self, enabled: bool) -> None:
        """设置OCR功能是否启用"""
        self.update_ocr_config(enabled=enabled)
        print(f"OCR功能已{'启用' if enabled else '禁用'}")
    
    def get_confidence_threshold(self) -> float:
        """获取OCR置信度阈值"""
        return self.get_ocr_config().get("confidence_threshold", 0.8)
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """设置OCR置信度阈值"""
        if not (0 <= threshold <= 1):
            raise ValueError("置信度阈值必须在0-1之间")
        self.update_ocr_config(confidence_threshold=threshold)
        print(f"OCR置信度阈值已更新为: {threshold}")
    
    # 注释配置相关方法
    def get_annotation_config(self) -> Dict[str, Any]:
        """获取注释相关配置"""
        return self.get_config("annotation")
    
    def update_annotation_config(self, **kwargs) -> None:
        """更新注释配置"""
        self.update_config("annotation", **kwargs)
    
    def is_annotation_enabled(self) -> bool:
        """检查注释功能是否启用"""
        return self.get_annotation_config().get("enable_annotation", True)
    
    def set_annotation_enabled(self, enabled: bool) -> None:
        """设置注释功能是否启用"""
        self.update_annotation_config(enable_annotation=enabled)
        print(f"注释功能已{'启用' if enabled else '禁用'}")
    
    # 控制台输出配置相关方法
    def get_console_output_config(self) -> Dict[str, Any]:
        """获取控制台输出配置"""
        return self.get_config("console_output", {})
    
    def update_console_output_config(self, **kwargs) -> None:
        """更新控制台输出配置"""
        self.update_config("console_output", **kwargs)
    
    # 特征缓存配置相关方法
    def get_feature_cache_config(self) -> Dict[str, Any]:
        """获取特征缓存配置"""
        return self.get_config("feature_cache", {})
    
    def update_feature_cache_config(self, **kwargs) -> None:
        """更新特征缓存配置"""
        self.update_config("feature_cache", **kwargs)
    
    # 预处理配置相关方法
    def get_preprocessing_config(self) -> Dict[str, Any]:
        """获取图像预处理配置"""
        return self.get_config("preprocessing", {
            "target_size": [116, 116],
            "enable_enhancement": True,
            "save_intermediate": False,
            "histogram_equalization": False,
            "clahe_enhancement": True,
            "clahe_clip_limit": 2.0,
            "clahe_grid_size": [8, 8],
            "gaussian_blur": True,
            "gaussian_kernel": [5, 5],
            "gaussian_sigma": 0,
            "canny_edges": True,
            "canny_low_threshold": 50,
            "canny_high_threshold": 150
        })
    
    def update_preprocessing_config(self, **kwargs) -> None:
        """更新预处理配置"""
        self.update_config("preprocessing", **kwargs)
    
    # 质量检测配置相关方法
    def get_quality_config(self) -> Dict[str, Any]:
        """获取质量检测配置"""
        return self.get_config("quality_check", {
            "min_resolution": [50, 50],
            "max_blur_score": 100.0,
            "min_brightness": 30.0,
            "max_brightness": 200.0
        })
    
    def update_quality_config(self, **kwargs) -> None:
        """更新质量检测配置"""
        self.update_config("quality_check", **kwargs)
    
    # 背景去除配置相关方法
    def get_background_removal_config(self) -> Dict[str, Any]:
        """获取背景去除配置"""
        return self.get_config("background_removal", {
            "gaussian_blur_kernel": [3, 3],
            "canny_threshold1": 30,
            "canny_threshold2": 100,
            "morph_kernel_size": [3, 3]
        })
    
    def update_background_removal_config(self, **kwargs) -> None:
        """更新背景去除配置"""
        self.update_config("background_removal", **kwargs)
    
    def get_target_size(self) -> list:
        """获取目标图像尺寸"""
        return self.get_preprocessing_config().get("target_size", [116, 116])
    
    def set_target_size(self, size: list) -> None:
        """设置目标图像尺寸"""
        if len(size) != 2 or not all(isinstance(x, int) and x > 0 for x in size):
            raise ValueError("目标尺寸必须是包含两个正整数的列表")
        self.update_preprocessing_config(target_size=size)
        print(f"目标图像尺寸已更新为: {size}")
    
    # 日志配置相关方法
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志相关配置"""
        return self.get_config("logging")
    
    def update_logging_config(self, **kwargs) -> None:
        """更新日志配置"""
        self.update_config("logging", **kwargs)
    
    # 性能配置相关方法
    def get_performance_config(self) -> Dict[str, Any]:
        """获取性能相关配置"""
        return self.get_config("performance")
    
    def update_performance_config(self, **kwargs) -> None:
        """更新性能配置"""
        self.update_config("performance", **kwargs)
    
    # UI配置相关方法
    def get_ui_config(self) -> Dict[str, Any]:
        """获取UI相关配置"""
        return self.get_config("ui")
    
    def update_ui_config(self, **kwargs) -> None:
        """更新UI配置"""
        self.update_config("ui", **kwargs)
    
    # 调试配置相关方法
    def get_debug_config(self) -> Dict[str, Any]:
        """获取调试相关配置"""
        return self.get_config("debug", {})
    
    def update_debug_config(self, **kwargs) -> None:
        """更新调试配置"""
        self.update_config("debug", **kwargs)
    
    def is_visual_debug_enabled(self) -> bool:
        """检查可视化调试是否启用"""
        return self.get_debug_config().get("enable_visual_debug", False)
    
    def set_visual_debug_enabled(self, enabled: bool) -> None:
        """设置可视化调试是否启用"""
        self.update_debug_config(enable_visual_debug=enabled)
        print(f"可视化调试已{'启用' if enabled else '禁用'}")
    
    # 输出结构配置相关方法
    def get_output_structure_config(self) -> Dict[str, Any]:
        """获取输出结构配置"""
        return self.get_config("output_structure", {})
    
    def update_output_structure_config(self, **kwargs) -> None:
        """更新输出结构配置"""
        self.update_config("output_structure", **kwargs)
    
    def print_config_summary(self) -> None:
        """打印配置摘要"""
        print("\n" + "=" * 50)
        print("统一配置摘要")
        print("=" * 50)
        
        # 识别配置
        rec_config = self.get_recognition_config()
        print(f"算法类型: {rec_config.get('algorithm_type', 'unknown')}")
        print(f"算法模式: {'高级算法' if rec_config.get('use_advanced_algorithm') else '传统算法'}")
        print(f"默认阈值: {rec_config.get('default_threshold', 80)}%")
        print(f"掩码匹配: {'启用' if rec_config.get('enable_masking') else '禁用'}")
        print(f"直方图验证: {'启用' if rec_config.get('enable_histogram') else '禁用'}")
        
        # 路径配置
        paths_config = self.get_paths_config()
        print(f"\n图像目录: {paths_config.get('images_dir', 'images')}")
        print(f"基准装备目录: {paths_config.get('base_equipment_dir', 'base_equipment')}")
        print(f"游戏截图目录: {paths_config.get('game_screenshots_dir', 'game_screenshots')}")
        print(f"切割装备目录: {paths_config.get('cropped_equipment_dir', 'cropped_equipment')}")
        print(f"输出目录: {paths_config.get('output_dir', 'output')}")
        
        # OCR配置
        ocr_config = self.get_ocr_config()
        print(f"\nOCR功能: {'启用' if ocr_config.get('enabled') else '禁用'}")
        print(f"OCR引擎: {ocr_config.get('engine', 'easyocr')}")
        print(f"置信度阈值: {ocr_config.get('confidence_threshold', 0.8)}")
        
        # 注释配置
        ann_config = self.get_annotation_config()
        print(f"\n注释功能: {'启用' if ann_config.get('enable_annotation') else '禁用'}")
        print(f"圆形标记颜色: {ann_config.get('circle_color', 'red')}")
        print(f"圆形边框宽度: {ann_config.get('circle_width', 3)}像素")
        
        # 输出结构配置
        output_config = self.get_output_structure_config()
        print(f"\n使用时间戳目录: {'是' if output_config.get('use_timestamp_dirs') else '否'}")
        
        print("=" * 50)


# 全局统一配置管理器实例
_unified_config_manager = None


def get_unified_config_manager(config_path: str = "config/unified_config.json") -> UnifiedConfigManager:
    """获取全局统一配置管理器实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        统一配置管理器实例
    """
    global _unified_config_manager
    if _unified_config_manager is None:
        _unified_config_manager = UnifiedConfigManager(config_path)
    return _unified_config_manager


def create_recognizer_from_config(config_manager: Optional[UnifiedConfigManager] = None) -> 'EnhancedEquipmentRecognizer':
    """根据配置创建识别器实例
    
    Args:
        config_manager: 配置管理器实例，如果为None则使用全局实例
        
    Returns:
        配置好的识别器实例
    """
    if config_manager is None:
        config_manager = get_unified_config_manager()
    
    rec_config = config_manager.get_recognition_config()
    
    try:
        from src.core.equipment_recognizer import EnhancedEquipmentRecognizer
    except ImportError:
        from equipment_recognizer import EnhancedEquipmentRecognizer
    
    # 获取算法类型，默认使用增强特征匹配
    algorithm_type = rec_config.get("algorithm_type", "enhanced_feature")
    
    if algorithm_type == "enhanced_feature":
        # 使用增强特征匹配算法
        return EnhancedEquipmentRecognizer(
            default_threshold=rec_config.get("default_threshold", 80),
            algorithm_type="enhanced_feature",
            feature_type=rec_config.get("feature_type", "ORB"),
            min_match_count=rec_config.get("min_match_count", 8),
            match_ratio_threshold=rec_config.get("match_ratio_threshold", 0.75),
            use_cache=rec_config.get("use_cache", True),
            cache_dir=rec_config.get("cache_dir", "images/cache"),
            target_size=tuple(rec_config.get("target_size", [116, 116])),
            nfeatures=rec_config.get("nfeatures", 1000),
            auto_update_cache=rec_config.get("auto_update_cache", True),
            base_equipment_dir=rec_config.get("base_equipment_dir", "images/base_equipment")
        )
    elif algorithm_type == "feature":
        # 使用特征匹配算法
        return EnhancedEquipmentRecognizer(
            default_threshold=rec_config.get("default_threshold", 80),
            algorithm_type="feature",
            feature_type=rec_config.get("feature_type", "ORB"),
            min_match_count=rec_config.get("min_match_count", 8),
            match_ratio_threshold=rec_config.get("match_ratio_threshold", 0.75)
        )
    elif algorithm_type == "advanced":
        # 使用高级彩色模板匹配算法
        return EnhancedEquipmentRecognizer(
            default_threshold=rec_config.get("default_threshold", 80),
            algorithm_type="advanced",
            enable_masking=rec_config.get("enable_masking", True),
            enable_histogram=rec_config.get("enable_histogram", True)
        )
    else:
        # 使用传统dHash算法
        return EnhancedEquipmentRecognizer(
            default_threshold=rec_config.get("default_threshold", 80),
            algorithm_type="traditional"
        )


if __name__ == "__main__":
    # 测试统一配置管理器
    config_manager = UnifiedConfigManager()
    config_manager.print_config_summary()
    
    # 测试创建识别器
    recognizer = create_recognizer_from_config(config_manager)
    print(f"\n识别器创建成功:")
    info = recognizer.get_algorithm_info()
    for key, value in info.items():
        print(f"  {key}: {value}")