#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR配置管理模块
负责管理和验证OCR相关的配置参数
"""

import json
import os
from typing import Dict, Any, Optional, List


class OCRConfigManager:
    """OCR配置管理器，负责管理OCR相关的配置参数"""
    
    def __init__(self, config_manager=None):
        """初始化OCR配置管理器
        
        Args:
            config_manager: 现有的配置管理器实例，如果为None则创建新实例
        """
        if config_manager is None:
            from .config_manager import get_config_manager
            self.base_config_manager = get_config_manager()
        else:
            self.base_config_manager = config_manager
        
        # 确保OCR配置存在
        self._ensure_ocr_config()
    
    def _ensure_ocr_config(self) -> None:
        """确保OCR配置存在于配置文件中"""
        config = self.base_config_manager.config
        
        # 如果没有OCR配置，添加默认配置
        if "ocr" not in config:
            default_ocr_config = self._get_default_ocr_config()
            config["ocr"] = default_ocr_config
            self.base_config_manager._save_config(config)
            print("✓ 已添加默认OCR配置")
    
    def _get_default_ocr_config(self) -> Dict[str, Any]:
        """获取默认OCR配置
        
        Returns:
            默认OCR配置字典
        """
        return {
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
        }
    
    def get_ocr_config(self) -> Dict[str, Any]:
        """获取OCR配置
        
        Returns:
            OCR配置字典
        """
        return self.base_config_manager.config.get("ocr", {})
    
    def get_engine_config(self) -> Dict[str, Any]:
        """获取OCR引擎配置
        
        Returns:
            OCR引擎配置字典
        """
        ocr_config = self.get_ocr_config()
        return {
            "engine": ocr_config.get("engine", "easyocr"),
            "language": ocr_config.get("language", ["en"]),
            "confidence_threshold": ocr_config.get("confidence_threshold", 0.8)
        }
    
    def get_preprocessing_config(self) -> Dict[str, Any]:
        """获取图像预处理配置
        
        Returns:
            图像预处理配置字典
        """
        ocr_config = self.get_ocr_config()
        return ocr_config.get("preprocessing", {
            "grayscale": True,
            "threshold": True,
            "denoise": True
        })
    
    def get_amount_extraction_config(self) -> Dict[str, Any]:
        """获取金额提取配置
        
        Returns:
            金额提取配置字典
        """
        ocr_config = self.get_ocr_config()
        return {
            "price_pattern": ocr_config.get("price_pattern", "\\d+"),
            "confidence_threshold": ocr_config.get("confidence_threshold", 0.8)
        }
    
    def get_file_naming_config(self) -> Dict[str, Any]:
        """获取文件命名配置
        
        Returns:
            文件命名配置字典
        """
        ocr_config = self.get_ocr_config()
        return {
            "separator": ocr_config.get("rename_separator", "_"),
            "supported_formats": ocr_config.get("supported_formats", 
                                             [".png", ".jpg", ".jpeg", ".bmp", ".tiff"])
        }
    
    def get_csv_output_config(self) -> Dict[str, Any]:
        """获取CSV输出配置
        
        Returns:
            CSV输出配置字典
        """
        ocr_config = self.get_ocr_config()
        return {
            "enabled": ocr_config.get("enabled", True),
            "filename": ocr_config.get("output_csv", "ocr_rename_records.csv"),
            "include_timestamp": True,
            "include_confidence": True,
            "include_recognized_text": True,
            "include_processing_time": True,
            "overwrite_existing": False,
            "encoding": "utf-8",
            "date_format": "%Y-%m-%d %H:%M:%S"
        }
    
    def get_paths_config(self) -> Dict[str, Any]:
        """获取路径配置
        
        Returns:
            路径配置字典
        """
        ocr_config = self.get_ocr_config()
        return {
            "input_folder": ocr_config.get("input_folder", "images/cropped_equipment_marker"),
            "output_csv": ocr_config.get("output_csv", "ocr_rename_records.csv")
        }
    
    def validate_ocr_config(self) -> List[str]:
        """验证OCR配置的有效性
        
        Returns:
            错误信息列表，如果配置有效则返回空列表
        """
        errors = []
        ocr_config = self.get_ocr_config()
        
        # 验证引擎配置
        engine = ocr_config.get("engine", "")
        if engine not in ["easyocr"]:
            errors.append(f"不支持的OCR引擎: {engine}")
        
        # 验证语言配置
        languages = ocr_config.get("language", [])
        if not isinstance(languages, list) or not languages:
            errors.append("语言配置必须是非空列表")
        
        # 验证置信度阈值
        confidence_threshold = ocr_config.get("confidence_threshold", 0.8)
        if not isinstance(confidence_threshold, (int, float)) or not (0 <= confidence_threshold <= 1):
            errors.append("置信度阈值必须是0-1之间的数字")
        
        # 验证价格模式
        price_pattern = ocr_config.get("price_pattern", "")
        if not price_pattern:
            errors.append("价格模式不能为空")
        
        # 验证预处理配置
        preprocessing = ocr_config.get("preprocessing", {})
        if not isinstance(preprocessing, dict):
            errors.append("预处理配置必须是字典")
        
        # 验证路径配置
        input_folder = ocr_config.get("input_folder", "")
        if not input_folder:
            errors.append("输入文件夹路径不能为空")
        
        output_csv = ocr_config.get("output_csv", "")
        if not output_csv:
            errors.append("输出CSV文件路径不能为空")
        
        # 验证支持的格式
        supported_formats = ocr_config.get("supported_formats", [])
        if not isinstance(supported_formats, list) or not supported_formats:
            errors.append("支持的文件格式必须是非空列表")
        
        return errors
    
    def update_ocr_config(self, **kwargs) -> None:
        """更新OCR配置
        
        Args:
            **kwargs: 要更新的配置项
        """
        ocr_config = self.get_ocr_config()
        ocr_config.update(kwargs)
        self.base_config_manager.config["ocr"] = ocr_config
        self.base_config_manager._save_config(self.base_config_manager.config)
        print("✓ OCR配置已更新")
    
    def is_ocr_enabled(self) -> bool:
        """检查OCR功能是否启用
        
        Returns:
            True表示启用，False表示禁用
        """
        return self.get_ocr_config().get("enabled", True)
    
    def set_ocr_enabled(self, enabled: bool) -> None:
        """设置OCR功能是否启用
        
        Args:
            enabled: True表示启用，False表示禁用
        """
        self.update_ocr_config(enabled=enabled)
        print(f"OCR功能已{'启用' if enabled else '禁用'}")
    
    def get_confidence_threshold(self) -> float:
        """获取置信度阈值
        
        Returns:
            置信度阈值
        """
        return self.get_ocr_config().get("confidence_threshold", 0.8)
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """设置置信度阈值
        
        Args:
            threshold: 新的置信度阈值(0-1)
        """
        if not (0 <= threshold <= 1):
            raise ValueError("置信度阈值必须在0-1之间")
        self.update_ocr_config(confidence_threshold=threshold)
        print(f"置信度阈值已更新为: {threshold}")
    
    def get_price_pattern(self) -> str:
        """获取价格模式
        
        Returns:
            价格模式正则表达式
        """
        return self.get_ocr_config().get("price_pattern", "\\d+")
    
    def set_price_pattern(self, pattern: str) -> None:
        """设置价格模式
        
        Args:
            pattern: 新的价格模式正则表达式
        """
        self.update_ocr_config(price_pattern=pattern)
        print(f"价格模式已更新为: {pattern}")
    
    def get_input_folder(self) -> str:
        """获取输入文件夹路径
        
        Returns:
            输入文件夹路径
        """
        return self.get_ocr_config().get("input_folder", "images/cropped_equipment_marker")
    
    def set_input_folder(self, folder_path: str) -> None:
        """设置输入文件夹路径
        
        Args:
            folder_path: 新的输入文件夹路径
        """
        self.update_ocr_config(input_folder=folder_path)
        print(f"输入文件夹已更新为: {folder_path}")
    
    def get_output_csv_path(self) -> str:
        """获取输出CSV文件路径
        
        Returns:
            输出CSV文件路径
        """
        return self.get_ocr_config().get("output_csv", "ocr_rename_records.csv")
    
    def set_output_csv_path(self, csv_path: str) -> None:
        """设置输出CSV文件路径
        
        Args:
            csv_path: 新的输出CSV文件路径
        """
        self.update_ocr_config(output_csv=csv_path)
        print(f"输出CSV文件路径已更新为: {csv_path}")
    
    def print_ocr_config_summary(self) -> None:
        """打印OCR配置摘要"""
        print("\n" + "=" * 50)
        print("OCR配置摘要")
        print("=" * 50)
        
        ocr_config = self.get_ocr_config()
        print(f"OCR功能: {'启用' if ocr_config.get('enabled', True) else '禁用'}")
        print(f"OCR引擎: {ocr_config.get('engine', 'easyocr')}")
        print(f"识别语言: {ocr_config.get('language', ['en'])}")
        print(f"置信度阈值: {ocr_config.get('confidence_threshold', 0.8)}")
        print(f"价格模式: {ocr_config.get('price_pattern', '\\d+')}")
        
        preprocessing = ocr_config.get('preprocessing', {})
        print(f"\n图像预处理:")
        print(f"  灰度化: {'启用' if preprocessing.get('grayscale', True) else '禁用'}")
        print(f"  二值化: {'启用' if preprocessing.get('threshold', True) else '禁用'}")
        print(f"  降噪: {'启用' if preprocessing.get('denoise', True) else '禁用'}")
        
        print(f"\n文件处理:")
        print(f"  输入文件夹: {ocr_config.get('input_folder', 'images/cropped_equipment_marker')}")
        print(f"  输出CSV: {ocr_config.get('output_csv', 'ocr_rename_records.csv')}")
        print(f"  重命名分隔符: {ocr_config.get('rename_separator', '_')}")
        print(f"  支持格式: {', '.join(ocr_config.get('supported_formats', ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']))}")
        
        print("=" * 50)


# 全局OCR配置管理器实例
_ocr_config_manager = None


def get_ocr_config_manager(config_manager=None) -> OCRConfigManager:
    """获取全局OCR配置管理器实例
    
    Args:
        config_manager: 基础配置管理器实例
        
    Returns:
        OCR配置管理器实例
    """
    global _ocr_config_manager
    if _ocr_config_manager is None:
        _ocr_config_manager = OCRConfigManager(config_manager)
    return _ocr_config_manager


if __name__ == "__main__":
    # 测试OCR配置管理器
    ocr_config_manager = OCRConfigManager()
    ocr_config_manager.print_ocr_config_summary()
    
    # 验证配置
    errors = ocr_config_manager.validate_ocr_config()
    if errors:
        print("\n配置验证错误:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✓ OCR配置验证通过")