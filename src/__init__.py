#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏装备识别系统
包含装备识别、截图切割、OCR识别等核心功能
"""

# 导入核心模块
from . import core
from . import config
from . import logging
from . import image_processing
from . import ocr
from . import preprocessing
from . import cache
from . import debug
from . import quality
from . import utils

# 导入主要类和函数
from .core import (
    EquipmentRecognizer, 
    EnhancedEquipmentRecognizer,
    ScreenshotCutter,
    EquipmentMatcher
)

from .config import (
    ConfigManager,
    get_config_manager,
    create_recognizer_from_config
)

from .logging import (
    get_unified_logger,
    get_step_logger,
    get_logger
)

__version__ = "2.0.0"
__author__ = "ShopTitans Team"
__description__ = "游戏装备识别系统"

__all__ = [
    # 核心模块
    'core',
    'config',
    'logging',
    'image_processing',
    'ocr',
    'preprocessing',
    'cache',
    'debug',
    'quality',
    'utils',
    
    # 主要类和函数
    'EquipmentRecognizer',
    'EnhancedEquipmentRecognizer',
    'ScreenshotCutter',
    'EquipmentMatcher',
    'ConfigManager',
    'get_config_manager',
    'create_recognizer_from_config',
    'get_unified_logger',
    'get_step_logger',
    'get_logger',
    
    # 元信息
    '__version__',
    '__author__',
    '__description__'
]