#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一路径管理模块
负责管理项目中所有路径，避免硬编码路径和路径冲突问题
"""

import os
import re
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path


class PathManager:
    """统一路径管理器，负责管理项目中所有路径"""
    
    def __init__(self, config=None):
        """初始化路径管理器
        
        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        self.config = config
        self._base_dir = None
        self._paths_cache = {}
        
        # 初始化基础路径
        self._initialize_base_paths()
    
    def _initialize_base_paths(self):
        """初始化基础路径"""
        # 获取项目根目录
        self._base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # 定义默认路径配置
        self.default_paths = {
            'images_dir': 'images',
            'base_equipment_dir': 'images/base_equipment',
            'game_screenshots_dir': 'images/game_screenshots',
            'cropped_equipment_dir': 'images/cropped_equipment',
            'cropped_equipment_original_dir': 'images/cropped_equipment_original',
            'cropped_equipment_marker_dir': 'images/cropped_equipment_marker',
            'cache_dir': 'images/cache',
            'logs_dir': 'recognition_logs',
            'debug_dir': 'debug',
            'output_dir': 'output',
            'tests_dir': 'tests',
            'annotation_output_dir': 'annotated_screenshots'
        }
    
    def get_base_dir(self) -> str:
        """获取项目根目录
        
        Returns:
            项目根目录的绝对路径
        """
        return self._base_dir
    
    def get_path(self, path_key: str, create_if_not_exists: bool = False) -> str:
        """获取指定键的路径
        
        Args:
            path_key: 路径键名
            create_if_not_exists: 如果目录不存在是否创建
            
        Returns:
            路径字符串
            
        Raises:
            KeyError: 如果路径键不存在
        """
        # 检查缓存
        if path_key in self._paths_cache:
            path = self._paths_cache[path_key]
        else:
            # 从配置中获取路径
            if self.config and hasattr(self.config, 'get_paths_config'):
                paths_config = self.config.get_paths_config()
                path = paths_config.get(path_key, self.default_paths.get(path_key))
            else:
                path = self.default_paths.get(path_key)
            
            if path is None:
                raise KeyError(f"路径键 '{path_key}' 不存在")
            
            # 转换为绝对路径
            if not os.path.isabs(path):
                path = os.path.join(self._base_dir, path)
            
            # 规范化路径
            path = os.path.normpath(path)
            
            # 缓存路径
            self._paths_cache[path_key] = path
        
        # 如果需要，创建目录
        if create_if_not_exists and not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        
        return path
    
    def get_relative_path(self, path_key: str) -> str:
        """获取相对于项目根目录的路径
        
        Args:
            path_key: 路径键名
            
        Returns:
            相对路径字符串
        """
        abs_path = self.get_path(path_key)
        return os.path.relpath(abs_path, self._base_dir)
    
    def join_path(self, base_key: str, *path_parts: str, create_if_not_exists: bool = False) -> str:
        """连接路径部分
        
        Args:
            base_key: 基础路径键名
            *path_parts: 路径部分
            create_if_not_exists: 如果目录不存在是否创建
            
        Returns:
            连接后的路径
        """
        base_path = self.get_path(base_key)
        result_path = os.path.join(base_path, *path_parts)
        result_path = os.path.normpath(result_path)
        
        if create_if_not_exists and not os.path.exists(result_path):
            os.makedirs(result_path, exist_ok=True)
        
        return result_path
    
    def get_timestamp_dir(self, base_key: str, timestamp: str = None, create_if_not_exists: bool = True) -> str:
        """获取时间戳目录路径
        
        Args:
            base_key: 基础路径键名
            timestamp: 时间戳字符串，如果为None则使用当前时间
            create_if_not_exists: 如果目录不存在是否创建
            
        Returns:
            时间戳目录路径
        """
        if timestamp is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return self.join_path(base_key, timestamp, create_if_not_exists=create_if_not_exists)
    
    def get_latest_timestamp_dir(self, base_key: str) -> Optional[str]:
        """获取最新的时间戳目录
        
        Args:
            base_key: 基础路径键名
            
        Returns:
            最新时间戳目录的路径，如果没有找到则返回None
        """
        base_path = self.get_path(base_key)
        
        if not os.path.exists(base_path):
            return None
        
        # 查找时间戳目录
        timestamp_dirs = []
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path) and self._is_timestamp_dir(item):
                timestamp_dirs.append((item, item_path))
        
        if not timestamp_dirs:
            return None
        
        # 按时间戳排序，返回最新的
        latest_dir = sorted(timestamp_dirs, key=lambda x: x[0], reverse=True)[0]
        return latest_dir[1]
    
    def _is_timestamp_dir(self, dirname: str) -> bool:
        """检查目录名是否是时间戳格式
        
        Args:
            dirname: 目录名
            
        Returns:
            是否是时间戳格式
        """
        # 时间戳格式：YYYYMMDD_HHMMSS
        # 移除下划线和冒号后应该全是数字
        cleaned = dirname.replace('_', '').replace(':', '')
        return cleaned.isdigit() and len(cleaned) >= 8
    
    def find_file_by_extensions(self, base_key: str, filename: str, extensions: List[str] = None) -> Optional[str]:
        """根据文件名和扩展名查找文件
        
        Args:
            base_key: 基础路径键名
            filename: 文件名（不含扩展名）
            extensions: 可能的扩展名列表，如果为None则使用默认列表
            
        Returns:
            找到的文件路径，如果没有找到则返回None
        """
        if extensions is None:
            extensions = ['.webp', '.png', '.jpg', '.jpeg', '.bmp', '.tiff']
        
        base_path = self.get_path(base_key)
        
        for ext in extensions:
            file_path = os.path.join(base_path, f"{filename}{ext}")
            if os.path.exists(file_path):
                return file_path
        
        return None
    
    def ensure_dir_exists(self, path_key: str) -> bool:
        """确保目录存在
        
        Args:
            path_key: 路径键名
            
        Returns:
            目录是否存在或创建成功
        """
        try:
            path = self.get_path(path_key, create_if_not_exists=True)
            return os.path.exists(path)
        except Exception:
            return False
    
    def validate_path(self, path_key: str) -> Dict[str, Any]:
        """验证路径
        
        Args:
            path_key: 路径键名
            
        Returns:
            验证结果字典
        """
        result = {
            'valid': False,
            'exists': False,
            'is_dir': False,
            'is_file': False,
            'readable': False,
            'writable': False,
            'error': None
        }
        
        try:
            path = self.get_path(path_key)
            result['exists'] = os.path.exists(path)
            
            if result['exists']:
                result['is_dir'] = os.path.isdir(path)
                result['is_file'] = os.path.isfile(path)
                result['readable'] = os.access(path, os.R_OK)
                result['writable'] = os.access(path, os.W_OK)
                result['valid'] = True
            else:
                result['error'] = "路径不存在"
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_all_paths_info(self) -> Dict[str, Dict[str, Any]]:
        """获取所有路径的信息
        
        Returns:
            所有路径的信息字典
        """
        all_paths = {}
        
        # 获取所有默认路径键
        for key in self.default_paths.keys():
            all_paths[key] = self.validate_path(key)
        
        return all_paths
    
    def validate_all_paths(self) -> Dict[str, Dict[str, Any]]:
        """验证所有关键路径
        
        Returns:
            所有路径的验证结果字典
        """
        results = {}
        
        # 验证所有默认路径
        for key in self.default_paths.keys():
            results[key] = self.validate_path(key)
        
        return results
    
    def ensure_path_valid(self, path_key: str, create_if_missing: bool = True) -> bool:
        """确保路径有效
        
        Args:
            path_key: 路径键名
            create_if_missing: 如果路径不存在是否创建
            
        Returns:
            路径是否有效或创建成功
        """
        try:
            validation = self.validate_path(path_key)
            
            if validation['valid']:
                return True
            
            if not validation['exists'] and create_if_missing:
                path = self.get_path(path_key, create_if_not_exists=True)
                return os.path.exists(path)
            
            return False
        except Exception:
            return False
    
    def get_path_validation_report(self) -> str:
        """获取路径验证报告
        
        Returns:
            格式化的验证报告字符串
        """
        validations = self.validate_all_paths()
        
        report = ["路径验证报告", "=" * 50]
        
        valid_count = 0
        total_count = len(validations)
        
        for key, validation in validations.items():
            status = "✓ 有效" if validation['valid'] else "✗ 无效"
            report.append(f"{key}: {status}")
            
            if validation['valid']:
                valid_count += 1
                details = []
                if validation['is_dir']:
                    details.append("目录")
                if validation['is_file']:
                    details.append("文件")
                if validation['readable']:
                    details.append("可读")
                if validation['writable']:
                    details.append("可写")
                
                if details:
                    report.append(f"  - {', '.join(details)}")
            else:
                report.append(f"  - 错误: {validation['error']}")
        
        report.append("-" * 50)
        report.append(f"总计: {valid_count}/{total_count} 个路径有效")
        
        return "\n".join(report)
    
    def clear_cache(self):
        """清除路径缓存"""
        self._paths_cache.clear()
    
    def update_config(self, config):
        """更新配置
        
        Args:
            config: 新的配置对象
        """
        self.config = config
        self.clear_cache()


# 全局路径管理器实例
_path_manager = None


def get_path_manager(config=None) -> PathManager:
    """获取全局路径管理器实例
    
    Args:
        config: 配置对象
        
    Returns:
        路径管理器实例
    """
    global _path_manager
    if _path_manager is None:
        _path_manager = PathManager(config)
    elif config is not None:
        _path_manager.update_config(config)
    
    return _path_manager


def get_path(path_key: str, create_if_not_exists: bool = False) -> str:
    """便捷函数：获取指定键的路径
    
    Args:
        path_key: 路径键名
        create_if_not_exists: 如果目录不存在是否创建
        
    Returns:
        路径字符串
    """
    return get_path_manager().get_path(path_key, create_if_not_exists)


def join_path(base_key: str, *path_parts: str, create_if_not_exists: bool = False) -> str:
    """便捷函数：连接路径部分
    
    Args:
        base_key: 基础路径键名
        *path_parts: 路径部分
        create_if_not_exists: 如果目录不存在是否创建
        
    Returns:
        连接后的路径
    """
    return get_path_manager().join_path(base_key, *path_parts, create_if_not_exists=create_if_not_exists)


def get_timestamp_dir(base_key: str, timestamp: str = None, create_if_not_exists: bool = True) -> str:
    """便捷函数：获取时间戳目录路径
    
    Args:
        base_key: 基础路径键名
        timestamp: 时间戳字符串，如果为None则使用当前时间
        create_if_not_exists: 如果目录不存在是否创建
        
    Returns:
        时间戳目录路径
    """
    return get_path_manager().get_timestamp_dir(base_key, timestamp, create_if_not_exists)


def get_latest_timestamp_dir(base_key: str) -> Optional[str]:
    """便捷函数：获取最新的时间戳目录
    
    Args:
        base_key: 基础路径键名
        
    Returns:
        最新时间戳目录的路径，如果没有找到则返回None
    """
    return get_path_manager().get_latest_timestamp_dir(base_key)


def find_file_by_extensions(base_key: str, filename: str, extensions: List[str] = None) -> Optional[str]:
    """便捷函数：根据文件名和扩展名查找文件
    
    Args:
        base_key: 基础路径键名
        filename: 文件名（不含扩展名）
        extensions: 可能的扩展名列表，如果为None则使用默认列表
        
    Returns:
        找到的文件路径，如果没有找到则返回None
    """
    return get_path_manager().find_file_by_extensions(base_key, filename, extensions)


def validate_path(path_key: str) -> Dict[str, Any]:
    """便捷函数：验证路径
    
    Args:
        path_key: 路径键名
        
    Returns:
        验证结果字典
    """
    return get_path_manager().validate_path(path_key)


def ensure_path_valid(path_key: str, create_if_missing: bool = True) -> bool:
    """便捷函数：确保路径有效
    
    Args:
        path_key: 路径键名
        create_if_missing: 如果路径不存在是否创建
        
    Returns:
        路径是否有效或创建成功
    """
    return get_path_manager().ensure_path_valid(path_key, create_if_missing)


def get_path_validation_report() -> str:
    """便捷函数：获取路径验证报告
    
    Returns:
        格式化的验证报告字符串
    """
    return get_path_manager().get_path_validation_report()


if __name__ == "__main__":
    # 测试路径管理器
    print("测试路径管理器")
    print("=" * 50)
    
    # 创建路径管理器实例
    path_manager = PathManager()
    
    # 测试获取路径
    print("\n1. 测试获取路径:")
    for key in ['images_dir', 'base_equipment_dir', 'cache_dir']:
        path = path_manager.get_path(key)
        rel_path = path_manager.get_relative_path(key)
        print(f"  {key}: {path}")
        print(f"  相对路径: {rel_path}")
    
    # 测试连接路径
    print("\n2. 测试连接路径:")
    test_path = path_manager.join_path('images_dir', 'test', 'subdir')
    print(f"  连接路径: {test_path}")
    
    # 测试时间戳目录
    print("\n3. 测试时间戳目录:")
    timestamp_dir = path_manager.get_timestamp_dir('cropped_equipment_dir', '20231124_120000')
    print(f"  时间戳目录: {timestamp_dir}")
    
    # 测试文件查找
    print("\n4. 测试文件查找:")
    test_file = path_manager.find_file_by_extensions('base_equipment_dir', 'test_equipment')
    print(f"  查找结果: {test_file}")
    
    # 测试路径验证
    print("\n5. 测试路径验证:")
    for key in ['images_dir', 'base_equipment_dir']:
        validation = path_manager.validate_path(key)
        print(f"  {key}: {validation}")
    
    print("\n✅ 路径管理器测试完成")