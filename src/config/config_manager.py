#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的配置管理模块
专门为step测试模块提供基本配置功能
"""

import json
import os
from typing import Dict, Any, Optional

class SimpleConfigManager:
    """简化的配置管理器"""

    def __init__(self, config_path: str = "config.json"):
        """初始化配置管理器"""
        # 计算项目根目录
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.project_root, config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "cutting": {
                "default_method": "fixed",
                "fixed_grid": [6, 2],
                "fixed_item_width": 100,
                "fixed_item_height": 120,
                "fixed_margin_left": 20,
                "fixed_margin_top": 350,
                "contour_min_area": 800,
                "contour_max_area": 50000
            },
            "recognition": {
                "default_threshold": 80,
                "use_advanced_algorithm": True,
                "enable_masking": True,
                "enable_histogram": True
            },
            "paths": {
                "images_dir": "images",
                "base_equipment_dir": "base_equipment",
                "game_screenshots_dir": "game_screenshots",
                "cropped_equipment_dir": "equipment_crop",
                "equipment_transparent_dir": "equipment_transparent",
                "logs_dir": "recognition_logs"
            }
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # 合并配置
                return {**default_config, **loaded_config}
            except Exception as e:
                print(f"警告：无法加载配置文件 {self.config_path}：{e}")
                print("使用默认配置")

        return default_config

    def get_cutting_params(self) -> Dict[str, Any]:
        """获取切割参数"""
        return self.config.get("cutting", {})

    def get_recognition_params(self) -> Dict[str, Any]:
        """获取识别参数"""
        return self.config.get("recognition", {})

    def get_paths(self) -> Dict[str, Any]:
        """获取路径配置"""
        return self.config.get("paths", {})

    def get_full_path(self, path_key: str) -> str:
        """获取完整路径"""
        paths = self.get_paths()
        path_value = paths.get(path_key, "")

        if os.path.isabs(path_value):
            return path_value

        # 相对于项目根目录
        return os.path.join(self.project_root, path_value)

    def _save_config(self, config: Dict[str, Any]) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def set_config_value(self, section: str, key: str, value: Any) -> None:
        """设置配置值"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self._save_config(self.config)

# 全局配置管理器实例
_config_manager = None

def get_config_manager() -> SimpleConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = SimpleConfigManager()
    return _config_manager

def create_recognizer_from_config(config_manager: SimpleConfigManager):
    """从配置创建识别器（保留接口兼容性）"""
    # 由于我们简化了模块，这里返回None
    # 实际的识别逻辑在各个测试模块中实现
    return None