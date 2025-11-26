#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏装备识别系统 - 简化版
包含截图切割、OCR识别等核心功能
"""

# 导入核心模块
from . import core
from . import config
from . import ocr

# 导入主要类和函数
from .core import (
    ScreenshotCutter
)

from .config import (
    ConfigManager,
    get_config_manager,
    create_recognizer_from_config
)

__version__ = "2.0.0"
__author__ = "ShopTitans Team"
__description__ = "游戏装备识别系统 - 简化版"

__all__ = [
    # 核心模块
    'core',
    'config',
    'ocr',

    # 主要类和函数
    'ScreenshotCutter',
    'ConfigManager',
    'get_config_manager',
    'create_recognizer_from_config',

    # 元信息
    '__version__',
    '__author__',
    '__description__'
]