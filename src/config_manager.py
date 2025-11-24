#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
负责读取和管理系统配置，支持算法选择和其他参数配置
"""

import json
import os
from typing import Dict, Any, Optional

class ConfigManager:
    """配置管理器，负责加载和管理系统配置"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化配置管理器
        
        Args:
            config_path: 配置文件路径，默认为项目根目录下的config.json
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件
        
        Returns:
            配置字典，如果文件不存在则返回默认配置
        """
        default_config = {
            "recognition": {
                "default_threshold": 80,
                "algorithm_type": "feature",  # 改为默认使用特征匹配算法
                "feature_type": "ORB",  # 默认使用ORB特征
                "min_match_count": 8,  # 最少特征匹配数量
                "match_ratio_threshold": 0.75,  # 特征匹配比例阈值
                "min_homography_inliers": 6,  # 最小单应性内点数量
                "use_advanced_algorithm": True,  # 保留兼容性
                "enable_masking": True,
                "enable_histogram": True,
                "algorithm_description": "特征匹配算法(ORB)提供最准确的装备识别，高级模板匹配提供彩色匹配，传统dHash算法提供更快的处理速度"
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
                "logs_dir": "recognition_logs"
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
            }
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # 合并默认配置和加载的配置
                config = self._merge_configs(default_config, loaded_config)
                # 不输出配置加载信息
                return config
            except Exception as e:
                print(f"⚠️ 配置文件加载失败，使用默认配置: {e}")
                return default_config
        else:
            print(f"⚠️ 配置文件不存在，使用默认配置: {self.config_path}")
            # 创建默认配置文件
            self._save_config(default_config)
            return default_config
    
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
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"✓ 配置文件已保存: {self.config_path}")
        except Exception as e:
            print(f"❌ 配置文件保存失败: {e}")
    
    def get_recognition_config(self) -> Dict[str, Any]:
        """获取识别相关配置
        
        Returns:
            识别配置字典
        """
        return self.config.get("recognition", {})
    
    def get_cutting_config(self) -> Dict[str, Any]:
        """获取切割相关配置
        
        Returns:
            切割配置字典
        """
        return self.config.get("cutting", {})
    
    def get_cutting_params(self) -> Dict[str, Any]:
        """获取切割参数
        
        Returns:
            包含所有切割参数的字典
        """
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
    
    def get_paths_config(self) -> Dict[str, Any]:
        """获取路径相关配置
        
        Returns:
            路径配置字典
        """
        return self.config.get("paths", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志相关配置
        
        Returns:
            日志配置字典
        """
        return self.config.get("logging", {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """获取性能相关配置
        
        Returns:
            性能配置字典
        """
        return self.config.get("performance", {})
    
    def get_ui_config(self) -> Dict[str, Any]:
        """获取UI相关配置
        
        Returns:
            UI配置字典
        """
        return self.config.get("ui", {})
    
    def get_annotation_config(self) -> Dict[str, Any]:
        """获取注释相关配置
        
        Returns:
            注释配置字典
        """
        return self.config.get("annotation", {})
    
    def get_console_output_config(self) -> Dict[str, Any]:
        """获取控制台输出配置
        
        Returns:
            控制台输出配置字典
        """
        return self.config.get("console_output", {})
    
    def get_feature_cache_config(self) -> Dict[str, Any]:
        """获取特征缓存配置
        
        Returns:
            特征缓存配置字典
        """
        return self.config.get("feature_cache", {})
    
    def get_preprocessing_config(self) -> Dict[str, Any]:
        """获取图像预处理配置
        
        Returns:
            图像预处理配置字典
        """
        return self.config.get("preprocessing", {
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
    
    def get_quality_config(self) -> Dict[str, Any]:
        """获取质量检测配置
        
        Returns:
            质量检测配置字典
        """
        return self.config.get("quality", {
            "min_resolution": [50, 50],
            "max_blur_score": 100.0,
            "min_brightness": 30.0,
            "max_brightness": 200.0
        })
    
    def get_background_removal_config(self) -> Dict[str, Any]:
        """获取背景去除配置
        
        Returns:
            背景去除配置字典
        """
        return self.config.get("background_removal", {
            "gaussian_blur_kernel": [3, 3],
            "canny_threshold1": 30,
            "canny_threshold2": 100,
            "morph_kernel_size": [3, 3]
        })
    
    def get_target_size(self) -> list:
        """获取目标图像尺寸
        
        Returns:
            目标尺寸列表 [宽度, 高度]
        """
        return self.get_preprocessing_config().get("target_size", [116, 116])
    
    def update_recognition_config(self, **kwargs) -> None:
        """更新识别配置
        
        Args:
            **kwargs: 要更新的配置项
        """
        recognition_config = self.config.get("recognition", {})
        recognition_config.update(kwargs)
        self.config["recognition"] = recognition_config
        self._save_config(self.config)
    
    def update_annotation_config(self, **kwargs) -> None:
        """更新注释配置
        
        Args:
            **kwargs: 要更新的配置项
        """
        annotation_config = self.config.get("annotation", {})
        annotation_config.update(kwargs)
        self.config["annotation"] = annotation_config
        self._save_config(self.config)
    
    def update_console_output_config(self, **kwargs) -> None:
        """更新控制台输出配置
        
        Args:
            **kwargs: 要更新的配置项
        """
        console_config = self.config.get("console_output", {})
        console_config.update(kwargs)
        self.config["console_output"] = console_config
        self._save_config(self.config)
    
    def get_algorithm_mode(self) -> bool:
        """获取算法模式
        
        Returns:
            True表示使用高级算法，False表示使用传统算法
        """
        return self.get_recognition_config().get("use_advanced_algorithm", True)
    
    def set_algorithm_mode(self, use_advanced: bool) -> None:
        """设置算法模式
        
        Args:
            use_advanced: True表示使用高级算法，False表示使用传统算法
        """
        self.update_recognition_config(use_advanced_algorithm=use_advanced)
        print(f"算法模式已更新为: {'高级模板匹配' if use_advanced else '传统dHash'}")
    
    def get_default_threshold(self) -> float:
        """获取默认阈值
        
        Returns:
            默认匹配阈值
        """
        return self.get_recognition_config().get("default_threshold", 80)
    
    def set_default_threshold(self, threshold: float) -> None:
        """设置默认阈值
        
        Args:
            threshold: 新的默认阈值
        """
        self.update_recognition_config(default_threshold=threshold)
        print(f"默认阈值已更新为: {threshold}%")
    
    def get_masking_enabled(self) -> bool:
        """获取掩码匹配是否启用
        
        Returns:
            True表示启用掩码匹配，False表示禁用
        """
        return self.get_recognition_config().get("enable_masking", True)
    
    def set_masking_enabled(self, enabled: bool) -> None:
        """设置掩码匹配是否启用
        
        Args:
            enabled: True表示启用，False表示禁用
        """
        self.update_recognition_config(enable_masking=enabled)
        print(f"掩码匹配已{'启用' if enabled else '禁用'}")
    
    def get_histogram_enabled(self) -> bool:
        """获取直方图验证是否启用
        
        Returns:
            True表示启用直方图验证，False表示禁用
        """
        return self.get_recognition_config().get("enable_histogram", True)
    
    def set_histogram_enabled(self, enabled: bool) -> None:
        """设置直方图验证是否启用
        
        Args:
            enabled: True表示启用，False表示禁用
        """
        self.update_recognition_config(enable_histogram=enabled)
        print(f"直方图验证已{'启用' if enabled else '禁用'}")
    
    def get_annotation_enabled(self) -> bool:
        """获取注释功能是否启用
        
        Returns:
            True表示启用注释功能，False表示禁用
        """
        return self.get_annotation_config().get("enable_annotation", True)
    
    def set_annotation_enabled(self, enabled: bool) -> None:
        """设置注释功能是否启用
        
        Args:
            enabled: True表示启用，False表示禁用
        """
        self.update_annotation_config(enable_annotation=enabled)
        print(f"注释功能已{'启用' if enabled else '禁用'}")
    
    def get_circle_color(self) -> str:
        """获取圆形标记颜色
        
        Returns:
            圆形标记颜色字符串
        """
        return self.get_annotation_config().get("circle_color", "red")
    
    def set_circle_color(self, color: str) -> None:
        """设置圆形标记颜色
        
        Args:
            color: 颜色字符串，如'red', 'blue', 'green'等
        """
        self.update_annotation_config(circle_color=color)
        print(f"圆形标记颜色已更新为: {color}")
    
    def get_circle_width(self) -> int:
        """获取圆形边框宽度
        
        Returns:
            圆形边框宽度（像素）
        """
        return self.get_annotation_config().get("circle_width", 3)
    
    def set_circle_width(self, width: int) -> None:
        """设置圆形边框宽度
        
        Args:
            width: 圆形边框宽度（像素）
        """
        self.update_annotation_config(circle_width=width)
        print(f"圆形边框宽度已更新为: {width}像素")
    
    def get_font_size(self) -> int:
        """获取注释文字大小
        
        Returns:
            注释文字大小（像素）
        """
        return self.get_annotation_config().get("font_size", 12)
    
    def set_font_size(self, size: int) -> None:
        """设置注释文字大小
        
        Args:
            size: 注释文字大小（像素）
        """
        self.update_annotation_config(font_size=size)
        print(f"注释文字大小已更新为: {size}像素")
    
    def get_show_similarity_text(self) -> bool:
        """获取是否显示相似度文字
        
        Returns:
            True表示显示相似度文字，False表示不显示
        """
        return self.get_annotation_config().get("show_similarity_text", True)
    
    def set_show_similarity_text(self, show: bool) -> None:
        """设置是否显示相似度文字
        
        Args:
            show: True表示显示，False表示不显示
        """
        self.update_annotation_config(show_similarity_text=show)
        print(f"相似度文字显示已{'启用' if show else '禁用'}")
    
    def get_auto_generate_annotation(self) -> bool:
        """获取是否自动生成注释
        
        Returns:
            True表示自动生成，False表示手动生成
        """
        return self.get_annotation_config().get("auto_generate_annotation", False)
    
    def set_auto_generate_annotation(self, auto: bool) -> None:
        """设置是否自动生成注释
        
        Args:
            auto: True表示自动生成，False表示手动生成
        """
        self.update_annotation_config(auto_generate_annotation=auto)
        print(f"自动生成注释已{'启用' if auto else '禁用'}")
    
    def print_config_summary(self) -> None:
        """打印配置摘要"""
        print("\n" + "=" * 50)
        print("当前配置摘要")
        print("=" * 50)
        
        # 识别配置
        rec_config = self.get_recognition_config()
        print(f"算法模式: {'高级模板匹配' if rec_config.get('use_advanced_algorithm') else '传统dHash'}")
        print(f"默认阈值: {rec_config.get('default_threshold', 80)}%")
        print(f"掩码匹配: {'启用' if rec_config.get('enable_masking') else '禁用'}")
        print(f"直方图验证: {'启用' if rec_config.get('enable_histogram') else '禁用'}")
        
        # 路径配置
        paths_config = self.get_paths_config()
        print(f"\n图像目录: {paths_config.get('images_dir', 'images')}")
        print(f"基准装备目录: {paths_config.get('base_equipment_dir', 'base_equipment')}")
        print(f"游戏截图目录: {paths_config.get('game_screenshots_dir', 'game_screenshots')}")
        print(f"切割装备目录: {paths_config.get('cropped_equipment_dir', 'cropped_equipment')}")
        
        # 注释配置
        ann_config = self.get_annotation_config()
        print(f"注释功能: {'启用' if ann_config.get('enable_annotation') else '禁用'}")
        print(f"圆形标记颜色: {ann_config.get('circle_color', 'red')}")
        print(f"圆形边框宽度: {ann_config.get('circle_width', 3)}像素")
        print(f"注释文字大小: {ann_config.get('font_size', 12)}像素")
        print(f"显示相似度文字: {'是' if ann_config.get('show_similarity_text') else '否'}")
        print(f"自动生成注释: {'是' if ann_config.get('auto_generate_annotation') else '否'}")
        
        print("=" * 50)


# 全局配置管理器实例
_config_manager = None

def get_config_manager(config_path: str = "config.json") -> ConfigManager:
    """获取全局配置管理器实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置管理器实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    return _config_manager


def create_recognizer_from_config(config_manager: Optional[ConfigManager] = None) -> 'EnhancedEquipmentRecognizer':
    """根据配置创建识别器实例
    
    Args:
        config_manager: 配置管理器实例，如果为None则使用全局实例
        
    Returns:
        配置好的识别器实例
    """
    if config_manager is None:
        config_manager = get_config_manager()
    
    rec_config = config_manager.get_recognition_config()
    
    try:
        from .equipment_recognizer import EnhancedEquipmentRecognizer
    except ImportError:
        from equipment_recognizer import EnhancedEquipmentRecognizer
    
    # 获取算法类型，默认使用特征匹配
    algorithm_type = rec_config.get("algorithm_type", "feature")
    
    if algorithm_type == "feature":
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
    # 测试配置管理器
    config_manager = ConfigManager()
    config_manager.print_config_summary()
    
    # 测试创建识别器
    recognizer = create_recognizer_from_config(config_manager)
    print(f"\n识别器创建成功:")
    info = recognizer.get_algorithm_info()
    for key, value in info.items():
        print(f"  {key}: {value}")