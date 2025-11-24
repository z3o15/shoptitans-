#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤日志管理器
提供按步骤分类的日志管理，支持将日志写入对应的步骤文件夹
"""

import os
import sys
import time
from datetime import datetime
from typing import Optional, Dict, Any, TextIO
from pathlib import Path


class StepLogger:
    """步骤日志管理器，支持按步骤分类的日志记录"""
    
    def __init__(self, base_output_dir: str = "output", console_mode: bool = True):
        """初始化步骤日志管理器
        
        Args:
            base_output_dir: 输出基础目录
            console_mode: 是否启用控制台输出
        """
        self.base_output_dir = Path(base_output_dir)
        self.console_mode = console_mode
        self.current_step = None
        self.log_files = {}  # 存储各步骤的日志文件句柄
        self.step_stats = {}  # 存储各步骤的统计信息
        self.step_start_times = {}  # 存储各步骤的开始时间
        
        # 确保基础目录存在
        self.base_output_dir.mkdir(exist_ok=True)
        
        # 步骤配置
        self.step_configs = {
            "step1_helper": {
                "name": "辅助工具",
                "icon": "🔧",
                "subdirs": ["temp_files"]
            },
            "step2_cut": {
                "name": "图片裁剪",
                "icon": "✂️",
                "subdirs": ["images", "txt"]
            },
            "step3_match": {
                "name": "装备匹配",
                "icon": "🔍",
                "subdirs": ["images", "txt"]
            },
            "step5_ocr": {
                "name": "OCR识别",
                "icon": "📝",
                "subdirs": ["images", "txt"]
            }
        }
        
        # 初始化目录结构
        self._init_directory_structure()
    
    def _init_directory_structure(self):
        """初始化目录结构"""
        for step_id, config in self.step_configs.items():
            step_dir = self.base_output_dir / step_id
            step_dir.mkdir(exist_ok=True)
            
            # 创建子目录
            for subdir in config["subdirs"]:
                (step_dir / subdir).mkdir(exist_ok=True)
            
            # 创建日志文件
            log_file = step_dir / "log.txt"
            if not log_file.exists():
                log_file.touch()
    
    def start_step(self, step_id: str, description: str = "") -> None:
        """开始一个步骤
        
        Args:
            step_id: 步骤ID
            description: 步骤描述
        """
        if step_id not in self.step_configs:
            raise ValueError(f"未知的步骤ID: {step_id}")
        
        self.current_step = step_id
        self.step_start_times[step_id] = time.time()
        self.step_stats[step_id] = {
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "processed_items": 0,
            "success_items": 0,
            "error_items": 0,
            "warnings": 0
        }
        
        # 打开日志文件
        step_dir = self.base_output_dir / step_id
        log_file = step_dir / "log.txt"
        self.log_files[step_id] = open(log_file, "a", encoding="utf-8")
        
        config = self.step_configs[step_id]
        step_name = config["name"]
        icon = config["icon"]
        
        log_msg = f"\n{'='*60}\n"
        log_msg += f"{icon} 开始步骤: {step_name} ({step_id})\n"
        log_msg += f"时间: {self.step_stats[step_id]['start_time']}\n"
        if description:
            log_msg += f"描述: {description}\n"
        log_msg += f"{'='*60}\n"
        
        self._write_log(step_id, log_msg)
        
        # 控制台输出
        if self.console_mode:
            print(f"\n{icon} 开始步骤: {step_name}")
    
    def end_step(self, step_id: Optional[str] = None, status: str = "完成") -> None:
        """结束当前步骤
        
        Args:
            step_id: 步骤ID，如果为None则结束当前步骤
            status: 结束状态
        """
        if step_id is None:
            step_id = self.current_step
        
        if step_id is None or step_id not in self.step_configs:
            return
        
        # 计算耗时
        elapsed_time = 0
        if step_id in self.step_start_times:
            elapsed_time = time.time() - self.step_start_times[step_id]
        
        # 更新统计信息
        if step_id in self.step_stats:
            self.step_stats[step_id]["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.step_stats[step_id]["elapsed_time"] = f"{elapsed_time:.2f}s"
        
        config = self.step_configs[step_id]
        step_name = config["name"]
        icon = config["icon"]
        
        log_msg = f"\n{'='*60}\n"
        log_msg += f"{icon} 步骤结束: {step_name} ({step_id}) - {status}\n"
        log_msg += f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        log_msg += f"总耗时: {elapsed_time:.2f}秒\n"
        
        if step_id in self.step_stats:
            stats = self.step_stats[step_id]
            log_msg += f"处理项目: {stats['processed_items']}\n"
            log_msg += f"成功项目: {stats['success_items']}\n"
            log_msg += f"失败项目: {stats['error_items']}\n"
            log_msg += f"警告数量: {stats['warnings']}\n"
        
        log_msg += f"{'='*60}\n"
        
        self._write_log(step_id, log_msg)
        
        # 关闭日志文件
        if step_id in self.log_files:
            self.log_files[step_id].close()
            del self.log_files[step_id]
        
        # 控制台输出
        if self.console_mode:
            print(f"{icon} 步骤结束: {step_name} - {status} ({elapsed_time:.2f}s)")
            if step_id in self.step_stats:
                stats = self.step_stats[step_id]
                print(f"  处理: {stats['processed_items']} | 成功: {stats['success_items']} | 失败: {stats['error_items']}")
        
        if self.current_step == step_id:
            self.current_step = None
    
    def log_info(self, message: str, step_id: Optional[str] = None, show_in_console: bool = False) -> None:
        """记录信息日志
        
        Args:
            message: 日志信息
            step_id: 步骤ID，如果为None则使用当前步骤
            show_in_console: 是否在控制台显示
        """
        if step_id is None:
            step_id = self.current_step
        
        if step_id is None:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [INFO] {message}\n"
        
        self._write_log(step_id, log_msg)
        
        # 控制台输出 - 默认不显示INFO级别的日志，除非明确指定
        if self.console_mode and show_in_console:
            print(f"  ℹ️ {message}")
    
    def log_warning(self, message: str, step_id: Optional[str] = None, show_in_console: bool = True) -> None:
        """记录警告日志
        
        Args:
            message: 警告信息
            step_id: 步骤ID，如果为None则使用当前步骤
            show_in_console: 是否在控制台显示
        """
        if step_id is None:
            step_id = self.current_step
        
        if step_id is None:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [WARN] {message}\n"
        
        self._write_log(step_id, log_msg)
        
        # 更新统计信息
        if step_id in self.step_stats:
            self.step_stats[step_id]["warnings"] += 1
        
        # 控制台输出
        if self.console_mode and show_in_console:
            print(f"  ⚠️ {message}")
    
    def log_error(self, message: str, step_id: Optional[str] = None, show_in_console: bool = True) -> None:
        """记录错误日志
        
        Args:
            message: 错误信息
            step_id: 步骤ID，如果为None则使用当前步骤
            show_in_console: 是否在控制台显示
        """
        if step_id is None:
            step_id = self.current_step
        
        if step_id is None:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [ERROR] {message}\n"
        
        self._write_log(step_id, log_msg)
        
        # 更新统计信息
        if step_id in self.step_stats:
            self.step_stats[step_id]["error_items"] += 1
        
        # 控制台输出
        if self.console_mode and show_in_console:
            print(f"  ❌ {message}")
    
    def log_success(self, message: str, step_id: Optional[str] = None, show_in_console: bool = False) -> None:
        """记录成功日志
        
        Args:
            message: 成功信息
            step_id: 步骤ID，如果为None则使用当前步骤
            show_in_console: 是否在控制台显示
        """
        if step_id is None:
            step_id = self.current_step
        
        if step_id is None:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [SUCCESS] {message}\n"
        
        self._write_log(step_id, log_msg)
        
        # 更新统计信息
        if step_id in self.step_stats:
            self.step_stats[step_id]["success_items"] += 1
        
        # 控制台输出 - 默认显示SUCCESS级别的日志
        if self.console_mode and show_in_console:
            print(f"  ✅ {message}")
    
    def update_stats(self, step_id: Optional[str] = None, **kwargs) -> None:
        """更新统计信息
        
        Args:
            step_id: 步骤ID，如果为None则使用当前步骤
            **kwargs: 要更新的统计字段
        """
        if step_id is None:
            step_id = self.current_step
        
        if step_id is None or step_id not in self.step_stats:
            return
        
        for key, value in kwargs.items():
            if key in self.step_stats[step_id]:
                if isinstance(self.step_stats[step_id][key], int) and isinstance(value, int):
                    self.step_stats[step_id][key] += value
                else:
                    self.step_stats[step_id][key] = value
    
    def increment_processed(self, step_id: Optional[str] = None) -> None:
        """增加处理计数
        
        Args:
            step_id: 步骤ID，如果为None则使用当前步骤
        """
        self.update_stats(step_id, processed_items=1)
    
    def get_step_dir(self, step_id: Optional[str] = None) -> Optional[Path]:
        """获取步骤目录路径
        
        Args:
            step_id: 步骤ID，如果为None则使用当前步骤
            
        Returns:
            步骤目录路径
        """
        if step_id is None:
            step_id = self.current_step
        
        if step_id is None or step_id not in self.step_configs:
            return None
        
        return self.base_output_dir / step_id
    
    def get_step_stats(self, step_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取步骤统计信息
        
        Args:
            step_id: 步骤ID，如果为None则使用当前步骤
            
        Returns:
            统计信息字典
        """
        if step_id is None:
            step_id = self.current_step
        
        if step_id is None or step_id not in self.step_stats:
            return None
        
        return self.step_stats[step_id].copy()
    
    def _write_log(self, step_id: str, message: str) -> None:
        """写入日志到文件
        
        Args:
            step_id: 步骤ID
            message: 日志消息
        """
        if step_id in self.log_files:
            self.log_files[step_id].write(message)
            self.log_files[step_id].flush()
    
    def close_all_logs(self) -> None:
        """关闭所有日志文件"""
        for step_id in list(self.log_files.keys()):
            if step_id in self.log_files:
                self.log_files[step_id].close()
                del self.log_files[step_id]
        
        self.current_step = None
    
    def __del__(self):
        """析构函数，确保关闭所有日志文件"""
        self.close_all_logs()


# 全局步骤日志管理器实例
_global_step_logger: Optional[StepLogger] = None


def get_step_logger() -> StepLogger:
    """获取全局步骤日志管理器实例
    
    Returns:
        全局步骤日志管理器实例
    """
    global _global_step_logger
    if _global_step_logger is None:
        _global_step_logger = StepLogger()
    return _global_step_logger


def set_step_logger(logger: StepLogger) -> None:
    """设置全局步骤日志管理器实例
    
    Args:
        logger: 步骤日志管理器实例
    """
    global _global_step_logger
    _global_step_logger = logger