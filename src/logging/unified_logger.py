#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一日志管理器
整合步骤日志和终端输出策略，提供统一的日志接口
"""

import sys
import time
from typing import Optional, Dict, Any, Union
from pathlib import Path

try:
    from src.logging.step_logger import StepLogger, get_step_logger
    from src.logging.report_generator import ReportGenerator, get_report_generator
except ImportError:
    from step_logger import StepLogger, get_step_logger
    from report_generator import ReportGenerator, get_report_generator


class UnifiedLogger:
    """统一日志管理器，整合步骤日志和终端输出策略"""
    
    def __init__(self, base_output_dir: str = None, console_mode: bool = True):
        """初始化统一日志管理器
        
        Args:
            base_output_dir: 输出基础目录
            console_mode: 是否启用控制台输出
        """
        self.step_logger = StepLogger(base_output_dir, console_mode)
        self.report_generator = ReportGenerator(base_output_dir)
        self.console_mode = console_mode
        
        # 终端输出策略配置 - 优化为只显示关键信息
        self.output_config = {
            "show_step_progress": True,      # 显示步骤进度
            "show_item_details": False,      # 隐藏每个项目的详细信息
            "show_warnings": True,           # 显示警告
            "show_errors": True,             # 显示错误
            "show_success_summary": True,    # 显示成功摘要
            "show_performance_metrics": False, # 隐藏性能指标
            "console_level": "WARNING"       # 控制台日志级别：只显示WARNING及以上级别，减少终端输出
        }
        
        # 统计信息收集
        self.collected_stats = {}
        self.step_additional_info = {}
    
    def configure_output(self, **kwargs) -> None:
        """配置输出策略
        
        Args:
            **kwargs: 输出配置参数
        """
        self.output_config.update(kwargs)
    
    def start_step(self, step_id: str, description: str = "") -> None:
        """开始一个步骤
        
        Args:
            step_id: 步骤ID
            description: 步骤描述
        """
        self.step_logger.start_step(step_id, description)
        
        # 初始化步骤额外信息
        self.step_additional_info[step_id] = {
            "files_processed": [],
            "errors": [],
            "warnings": [],
            "performance_metrics": {}
        }
    
    def end_step(self, step_id: Optional[str] = None, status: str = "完成") -> None:
        """结束当前步骤
        
        Args:
            step_id: 步骤ID，如果为None则结束当前步骤
            status: 结束状态
        """
        if step_id is None:
            step_id = self.step_logger.current_step
        
        if step_id is None:
            return
        
        # 获取统计信息
        stats = self.step_logger.get_step_stats(step_id)
        if stats:
            self.collected_stats[step_id] = stats
        
        # 生成步骤报告
        if step_id in self.step_additional_info:
            additional_info = self.step_additional_info[step_id]
            self.report_generator.generate_step_report(step_id, stats, additional_info)
        
        # 结束步骤
        self.step_logger.end_step(step_id, status)
    
    def log_info(self, message: str, step_id: Optional[str] = None,
                 show_in_console: Optional[bool] = None) -> None:
        """记录信息日志
        
        Args:
            message: 日志信息
            step_id: 步骤ID，如果为None则使用当前步骤
            show_in_console: 是否在控制台显示，如果为None则使用配置策略
        """
        if show_in_console is None:
            # 根据console_level决定是否显示INFO级别的日志
            show_in_console = self.output_config["console_level"] in ["DEBUG"]
        
        self.step_logger.log_info(message, step_id, show_in_console)
    
    def log_warning(self, message: str, step_id: Optional[str] = None, 
                   show_in_console: Optional[bool] = None) -> None:
        """记录警告日志
        
        Args:
            message: 警告信息
            step_id: 步骤ID，如果为None则使用当前步骤
            show_in_console: 是否在控制台显示，如果为None则使用配置策略
        """
        if show_in_console is None:
            show_in_console = self.output_config["show_warnings"]
        
        self.step_logger.log_warning(message, step_id, show_in_console)
        
        # 添加到额外信息中
        if step_id is None:
            step_id = self.step_logger.current_step
        
        if step_id and step_id in self.step_additional_info:
            self.step_additional_info[step_id]["warnings"].append(message)
    
    def log_error(self, message: str, step_id: Optional[str] = None, 
                 show_in_console: Optional[bool] = None) -> None:
        """记录错误日志
        
        Args:
            message: 错误信息
            step_id: 步骤ID，如果为None则使用当前步骤
            show_in_console: 是否在控制台显示，如果为None则使用配置策略
        """
        if show_in_console is None:
            show_in_console = self.output_config["show_errors"]
        
        self.step_logger.log_error(message, step_id, show_in_console)
        
        # 添加到额外信息中
        if step_id is None:
            step_id = self.step_logger.current_step
        
        if step_id and step_id in self.step_additional_info:
            self.step_additional_info[step_id]["errors"].append(message)
    
    def log_success(self, message: str, step_id: Optional[str] = None, 
                   show_in_console: Optional[bool] = None) -> None:
        """记录成功日志
        
        Args:
            message: 成功信息
            step_id: 步骤ID，如果为None则使用当前步骤
            show_in_console: 是否在控制台显示，如果为None则使用配置策略
        """
        if show_in_console is None:
            # 成功日志也只在DEBUG模式下显示，减少终端输出
            show_in_console = self.output_config["console_level"] in ["DEBUG"] and self.output_config["show_success_summary"]
        
        self.step_logger.log_success(message, step_id, show_in_console)
    
    def log_progress(self, current: int, total: int, message: str = "",
                    step_id: Optional[str] = None) -> None:
        """记录进度信息
        
        Args:
            current: 当前进度
            total: 总数
            message: 附加信息
            step_id: 步骤ID，如果为None则使用当前步骤
        """
        if step_id is None:
            step_id = self.step_logger.current_step
        
        if step_id is None:
            return
        
        percentage = (current / total) * 100 if total > 0 else 0
        
        # 文件日志
        log_message = f"进度: {current}/{total} ({percentage:.1f}%)"
        if message:
            log_message += f" - {message}"
        
        self.step_logger.log_info(log_message, step_id, False)
        
        # 控制台输出（根据配置决定是否显示）
        if self.output_config["show_step_progress"] and self.console_mode:
            # 只在关键节点显示进度（每25%或最后一个）
            if percentage % 25 == 0 or current == total:
                progress_bar = self._create_simple_progress_bar(percentage)
                console_message = f"  {progress_bar} {current}/{total}"
                print(console_message)
    
    def log_file_processed(self, file_path: str, step_id: Optional[str] = None,
                           success: bool = True, details: str = "") -> None:
        """记录文件处理信息
        
        Args:
            file_path: 文件路径
            step_id: 步骤ID，如果为None则使用当前步骤
            success: 是否处理成功
            details: 详细信息
        """
        if step_id is None:
            step_id = self.step_logger.current_step
        
        if step_id is None:
            return
        
        file_name = Path(file_path).name
        
        # 文件日志
        status = "成功" if success else "失败"
        log_message = f"处理文件: {file_name} - {status}"
        if details:
            log_message += f" ({details})"
        
        self.step_logger.log_info(log_message, step_id, False)
        
        # 添加到额外信息中
        if step_id in self.step_additional_info:
            file_info = f"{file_name} - {status}"
            if details:
                file_info += f" ({details})"
            self.step_additional_info[step_id]["files_processed"].append(file_info)
        
        # 控制台输出（只显示失败的文件）
        if not success and self.output_config["show_errors"] and self.console_mode:
            console_message = f"  ❌ {file_name}"
            if details:
                console_message += f" - {details}"
            print(console_message)
        
        # 更新统计
        self.step_logger.increment_processed(step_id)
        if success:
            self.step_logger.update_stats(step_id, success_items=1)
        else:
            self.step_logger.update_stats(step_id, error_items=1)
    
    def log_performance_metric(self, metric_name: str, value: Union[str, int, float],
                              step_id: Optional[str] = None) -> None:
        """记录性能指标
        
        Args:
            metric_name: 指标名称
            value: 指标值
            step_id: 步骤ID，如果为None则使用当前步骤
        """
        if step_id is None:
            step_id = self.step_logger.current_step
        
        if step_id is None:
            return
        
        # 文件日志
        log_message = f"性能指标: {metric_name} = {value}"
        self.step_logger.log_info(log_message, step_id, False)
        
        # 添加到额外信息中
        if step_id in self.step_additional_info:
            self.step_additional_info[step_id]["performance_metrics"][metric_name] = value
        
        # 控制台输出（默认不显示性能指标）
        # 性能指标只记录在文件中，不在控制台显示
    
    def generate_summary_report(self, additional_info: Optional[Dict[str, Any]] = None) -> str:
        """生成汇总报告
        
        Args:
            additional_info: 额外信息
            
        Returns:
            汇总报告文件路径
        """
        return self.report_generator.generate_summary_report(self.collected_stats, additional_info)
    
    def get_step_dir(self, step_id: Optional[str] = None) -> Optional[Path]:
        """获取步骤目录路径
        
        Args:
            step_id: 步骤ID，如果为None则使用当前步骤
            
        Returns:
            步骤目录路径
        """
        return self.step_logger.get_step_dir(step_id)
    
    def get_step_stats(self, step_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取步骤统计信息
        
        Args:
            step_id: 步骤ID，如果为None则使用当前步骤
            
        Returns:
            统计信息字典
        """
        return self.step_logger.get_step_stats(step_id)
    
    def _create_simple_progress_bar(self, percentage: float, width: int = 20) -> str:
        """创建简单的进度条
        
        Args:
            percentage: 完成百分比
            width: 进度条宽度
            
        Returns:
            进度条字符串
        """
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {percentage:.1f}%"
    
    def close_all_logs(self) -> None:
        """关闭所有日志文件"""
        self.step_logger.close_all_logs()


# 全局统一日志管理器实例
_global_unified_logger: Optional[UnifiedLogger] = None


def get_unified_logger() -> UnifiedLogger:
    """获取全局统一日志管理器实例
    
    Returns:
        全局统一日志管理器实例
    """
    global _global_unified_logger
    if _global_unified_logger is None:
        _global_unified_logger = UnifiedLogger()
    return _global_unified_logger


def set_unified_logger(logger: UnifiedLogger) -> None:
    """设置全局统一日志管理器实例
    
    Args:
        logger: 统一日志管理器实例
    """
    global _global_unified_logger
    _global_unified_logger = logger


def init_unified_logger_from_config(config: Dict[str, Any]) -> UnifiedLogger:
    """从配置初始化统一日志管理器
    
    Args:
        config: 配置字典
        
    Returns:
        初始化后的统一日志管理器实例
    """
    base_output_dir = config.get("base_output_dir", "output")
    console_mode = config.get("console_mode", True)
    
    logger = UnifiedLogger(base_output_dir, console_mode)
    
    # 配置输出策略
    output_config = config.get("output", {})
    logger.configure_output(**output_config)
    
    set_unified_logger(logger)
    return logger