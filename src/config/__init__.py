#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
包含系统配置、OCR配置等管理功能
"""

from .config_manager import ConfigManager, get_config_manager, create_recognizer_from_config
from .ocr_config_manager import OCRConfigManager, get_ocr_config_manager

__all__ = [
    'ConfigManager',
    'get_config_manager',
    'create_recognizer_from_config',
    'OCRConfigManager',
    'get_ocr_config_manager'
]