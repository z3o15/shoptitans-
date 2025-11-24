#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
节点日志管理器
提供统一的控制台输出管理，支持节点式输出结构
"""

import sys
import time
from typing import Optional, Dict, Any

class NodeLogger:
    """节点日志管理器，提供结构化的控制台输出"""
    
    def __init__(self, show_debug: bool = False, compact_mode: bool = True):
        """初始化节点日志管理器
        
        Args:
            show_debug: 是否显示调试信息
            compact_mode: 是否使用紧凑模式
        """
        self.show_debug = show_debug
        self.compact_mode = compact_mode
        self.current_level = 0
        self.node_stack = []
        self.start_times = {}
        
        # 默认图标配置
        self.icons = {
            'init': '🚀',
            'step1': '🖼️',
            'step2': '✂️',
            'step3': '🔍',
            'step4': '📊',
            'complete': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'success': '✅',
            'processing': '⏳',
            'node': '├──',
            'last_node': '└──',
            'sub_node': '│  ├─',
            'last_sub_node': '│  └─',
            'indent': '│   ',
            'last_indent': '    '
        }
    
    def start_node(self, name: str, icon: str = "📋") -> None:
        """开始一个新节点
        
        Args:
            name: 节点名称
            icon: 节点图标
        """
        prefix = self._get_prefix(is_last=False)
        print(f"{prefix} {icon} {name}")
        
        self.node_stack.append((name, icon))
        self.current_level += 1
        self.start_times[name] = time.time()
    
    def end_node(self, status: str = "✅", show_time: bool = True) -> None:
        """结束当前节点
        
        Args:
            status: 结束状态
            show_time: 是否显示耗时
        """
        if not self.node_stack:
            return
        
        name, icon = self.node_stack.pop()
        self.current_level -= 1
        
        if show_time and name in self.start_times:
            elapsed = time.time() - self.start_times[name]
            time_str = f" ({elapsed:.2f}s)"
        else:
            time_str = ""
        
        prefix = self._get_prefix(is_last=True)
        print(f"{prefix} {status} 完成{time_str}")
    
    def log_info(self, message: str, level: int = 1) -> None:
        """记录信息
        
        Args:
            message: 信息内容
            level: 信息级别
        """
        if level > 1 and self.compact_mode:
            return
        
        prefix = self._get_sub_prefix()
        print(f"{prefix} {message}")
    
    def log_success(self, message: str, level: int = 1) -> None:
        """记录成功信息
        
        Args:
            message: 信息内容
            level: 信息级别
        """
        if level > 1 and self.compact_mode:
            return
        
        prefix = self._get_sub_prefix()
        print(f"{prefix} ✅ {message}")
    
    def log_error(self, message: str, level: int = 1) -> None:
        """记录错误信息
        
        Args:
            message: 错误信息
            level: 信息级别
        """
        prefix = self._get_sub_prefix()
        print(f"{prefix} ❌ {message}")
    
    def log_warning(self, message: str, level: int = 1) -> None:
        """记录警告信息
        
        Args:
            message: 警告信息
            level: 信息级别
        """
        if level > 1 and self.compact_mode:
            return
        
        prefix = self._get_sub_prefix()
        print(f"{prefix} ⚠️ {message}")
    
    def log_debug(self, message: str, level: int = 2) -> None:
        """记录调试信息
        
        Args:
            message: 调试信息
            level: 信息级别
        """
        if not self.show_debug or (level > 2 and self.compact_mode):
            return
        
        prefix = self._get_sub_prefix()
        print(f"{prefix} 🔍 {message}")
    
    def log_progress(self, current: int, total: int, message: str = "") -> None:
        """记录进度信息
        
        Args:
            current: 当前进度
            total: 总数
            message: 附加信息
        """
        percentage = (current / total) * 100 if total > 0 else 0
        progress_bar = self._create_progress_bar(percentage)
        
        prefix = self._get_sub_prefix()
        if message:
            print(f"{prefix} {progress_bar} {current}/{total} - {message}")
        else:
            print(f"{prefix} {progress_bar} {current}/{total}")
    
    def _get_prefix(self, is_last: bool = False) -> str:
        """获取节点前缀
        
        Args:
            is_last: 是否为最后一个节点
            
        Returns:
            节点前缀字符串
        """
        if self.current_level == 0:
            return ""
        elif self.current_level == 1:
            return self.icons['last_node'] if is_last else self.icons['node']
        else:
            # 多层级处理
            prefix = ""
            for i in range(self.current_level - 1):
                prefix += self.icons['indent']
            return prefix + (self.icons['last_sub_node'] if is_last else self.icons['sub_node'])
    
    def _get_sub_prefix(self) -> str:
        """获取子项前缀
        
        Returns:
            子项前缀字符串
        """
        if self.current_level == 0:
            return ""
        elif self.current_level == 1:
            return self.icons['last_indent']
        else:
            prefix = ""
            for i in range(self.current_level - 1):
                prefix += self.icons['indent']
            return prefix + self.icons['last_indent']
    
    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """创建进度条
        
        Args:
            percentage: 完成百分比
            width: 进度条宽度
            
        Returns:
            进度条字符串
        """
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {percentage:.1f}%"

# 全局日志管理器实例
_global_logger: Optional[NodeLogger] = None

def get_logger() -> NodeLogger:
    """获取全局日志管理器实例
    
    Returns:
        全局日志管理器实例
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = NodeLogger()
    return _global_logger

def set_logger(logger: NodeLogger) -> None:
    """设置全局日志管理器实例
    
    Args:
        logger: 日志管理器实例
    """
    global _global_logger
    _global_logger = logger

def init_logger_from_config(config_manager) -> NodeLogger:
    """从配置管理器初始化日志管理器
    
    Args:
        config_manager: 配置管理器实例
        
    Returns:
        初始化后的日志管理器实例
    """
    console_config = config_manager.get_console_output_config()
    
    logger = NodeLogger(
        show_debug=console_config.get("show_debug", False),
        compact_mode=console_config.get("compact_mode", True)
    )
    
    # 更新图标配置
    if "node_icons" in console_config:
        logger.icons.update(console_config["node_icons"])
    
    set_logger(logger)
    return logger