#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输出管理模块
负责管理项目的输出结构和文件组织
"""

import os
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from .unified_config_manager import get_unified_config_manager


class OutputManager:
    """输出管理器，负责管理项目的输出结构和文件组织"""
    
    def __init__(self, config_manager=None):
        """初始化输出管理器
        
        Args:
            config_manager: 配置管理器实例，如果为None则使用全局实例
        """
        self.config_manager = config_manager or get_unified_config_manager()
        self.output_config = self.config_manager.get_output_structure_config()
        self.paths_config = self.config_manager.get_paths_config()
    
    def get_timestamp(self) -> str:
        """获取当前时间戳字符串
        
        Returns:
            格式化的时间戳字符串
        """
        timestamp_format = self.output_config.get("timestamp_format", "%Y%m%d_%H%M%S")
        return datetime.now().strftime(timestamp_format)
    
    def get_base_output_dir(self, use_timestamp: bool = True) -> str:
        """获取基础输出目录
        
        Args:
            use_timestamp: 是否使用时间戳目录
            
        Returns:
            基础输出目录路径
        """
        base_dir = self.paths_config.get("output_dir", "output")
        
        if use_timestamp and self.output_config.get("use_timestamp_dirs", True):
            timestamp = self.get_timestamp()
            base_dir = os.path.join(base_dir, timestamp)
        
        return base_dir
    
    def get_step_output_dir(self, step: str, use_timestamp: bool = True) -> str:
        """获取指定步骤的输出目录
        
        Args:
            step: 步骤名称 (step1, step2, step3, step4)
            use_timestamp: 是否使用时间戳目录
            
        Returns:
            步骤输出目录路径
        """
        base_dir = self.get_base_output_dir(use_timestamp)
        step_subdirs = self.output_config.get("step_subdirs", {})
        step_name = step_subdirs.get(step, step)
        
        return os.path.join(base_dir, step_name)
    
    def ensure_step_dirs(self, step: str, use_timestamp: bool = True) -> Dict[str, str]:
        """确保步骤输出目录存在并返回各子目录路径
        
        Args:
            step: 步骤名称
            use_timestamp: 是否使用时间戳目录
            
        Returns:
            包含各子目录路径的字典
        """
        step_dir = self.get_step_output_dir(step, use_timestamp)
        standard_subdirs = self.output_config.get("standard_subdirs", ["images", "logs", "reports", "temp"])
        
        dirs = {}
        for subdir in standard_subdirs:
            dir_path = os.path.join(step_dir, subdir)
            os.makedirs(dir_path, exist_ok=True)
            dirs[subdir] = dir_path
        
        return dirs
    
    def get_file_path(self, step: str, subdir: str, filename: str, use_timestamp: bool = True) -> str:
        """获取文件路径
        
        Args:
            step: 步骤名称
            subdir: 子目录名称
            filename: 文件名
            use_timestamp: 是否使用时间戳目录
            
        Returns:
            完整的文件路径
        """
        step_dir = self.get_step_output_dir(step, use_timestamp)
        return os.path.join(step_dir, subdir, filename)
    
    def save_image(self, step: str, filename: str, image_data, use_timestamp: bool = True) -> str:
        """保存图像文件
        
        Args:
            step: 步骤名称
            filename: 文件名
            image_data: 图像数据
            use_timestamp: 是否使用时间戳目录
            
        Returns:
            保存的文件路径
        """
        dirs = self.ensure_step_dirs(step, use_timestamp)
        file_path = os.path.join(dirs["images"], filename)
        
        # 根据图像数据类型保存
        if hasattr(image_data, 'save'):  # PIL Image
            image_data.save(file_path)
        elif hasattr(image_data, 'imwrite'):  # OpenCV
            import cv2
            cv2.imwrite(file_path, image_data)
        else:
            raise ValueError("不支持的图像数据类型")
        
        return file_path
    
    def save_log(self, step: str, log_content: str, filename: str = None, use_timestamp: bool = True) -> str:
        """保存日志文件
        
        Args:
            step: 步骤名称
            log_content: 日志内容
            filename: 文件名，如果为None则使用默认名称
            use_timestamp: 是否使用时间戳目录
            
        Returns:
            保存的文件路径
        """
        dirs = self.ensure_step_dirs(step, use_timestamp)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"log_{timestamp}.txt"
        
        file_path = os.path.join(dirs["logs"], filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(log_content)
        
        return file_path
    
    def save_report(self, step: str, report_content: str, filename: str = None, use_timestamp: bool = True) -> str:
        """保存报告文件
        
        Args:
            step: 步骤名称
            report_content: 报告内容
            filename: 文件名，如果为None则使用默认名称
            use_timestamp: 是否使用时间戳目录
            
        Returns:
            保存的文件路径
        """
        dirs = self.ensure_step_dirs(step, use_timestamp)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.md"
        
        file_path = os.path.join(dirs["reports"], filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return file_path
    
    def get_temp_file_path(self, step: str, filename: str, use_timestamp: bool = True) -> str:
        """获取临时文件路径
        
        Args:
            step: 步骤名称
            filename: 文件名
            use_timestamp: 是否使用时间戳目录
            
        Returns:
            临时文件路径
        """
        dirs = self.ensure_step_dirs(step, use_timestamp)
        return os.path.join(dirs["temp"], filename)
    
    def cleanup_temp_files(self, step: str, use_timestamp: bool = True) -> None:
        """清理临时文件
        
        Args:
            step: 步骤名称
            use_timestamp: 是否使用时间戳目录
        """
        dirs = self.ensure_step_dirs(step, use_timestamp)
        temp_dir = dirs["temp"]
        
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"⚠️ 清理临时文件失败: {file_path}, 错误: {e}")
    
    def list_step_files(self, step: str, subdir: str = None, use_timestamp: bool = True) -> List[str]:
        """列出步骤输出目录中的文件
        
        Args:
            step: 步骤名称
            subdir: 子目录名称，如果为None则列出所有子目录
            use_timestamp: 是否使用时间戳目录
            
        Returns:
            文件路径列表
        """
        step_dir = self.get_step_output_dir(step, use_timestamp)
        
        if subdir:
            target_dir = os.path.join(step_dir, subdir)
            if os.path.exists(target_dir):
                return [os.path.join(target_dir, f) for f in os.listdir(target_dir)]
            return []
        else:
            files = []
            for root, dirs, filenames in os.walk(step_dir):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
            return files
    
    def get_latest_output_dir(self, step: str) -> str:
        """获取最新的输出目录
        
        Args:
            step: 步骤名称
            
        Returns:
            最新的输出目录路径
        """
        base_dir = self.paths_config.get("output_dir", "output")
        
        if not os.path.exists(base_dir):
            return self.get_step_output_dir(step, use_timestamp=False)
        
        # 获取所有时间戳目录
        timestamp_dirs = []
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path):
                try:
                    # 尝试解析时间戳
                    timestamp_format = self.output_config.get("timestamp_format", "%Y%m%d_%H%M%S")
                    datetime.strptime(item, timestamp_format)
                    timestamp_dirs.append((item, item_path))
                except ValueError:
                    # 不是时间戳目录，跳过
                    continue
        
        if not timestamp_dirs:
            return self.get_step_output_dir(step, use_timestamp=False)
        
        # 按时间戳排序，获取最新的
        timestamp_dirs.sort(key=lambda x: x[0], reverse=True)
        latest_dir = timestamp_dirs[0][1]
        
        step_subdirs = self.output_config.get("step_subdirs", {})
        step_name = step_subdirs.get(step, step)
        
        return os.path.join(latest_dir, step_name)
    
    def migrate_old_output(self, old_step_dir: str, new_step: str, use_timestamp: bool = True) -> str:
        """迁移旧的输出文件到新结构
        
        Args:
            old_step_dir: 旧的步骤目录路径
            new_step: 新的步骤名称
            use_timestamp: 是否使用时间戳目录
            
        Returns:
            新的输出目录路径
        """
        if not os.path.exists(old_step_dir):
            print(f"⚠️ 旧目录不存在: {old_step_dir}")
            return self.get_step_output_dir(new_step, use_timestamp)
        
        new_dirs = self.ensure_step_dirs(new_step, use_timestamp)
        
        # 迁移文件
        for item in os.listdir(old_step_dir):
            old_path = os.path.join(old_step_dir, item)
            
            # 确定目标子目录
            if item.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')):
                target_dir = new_dirs["images"]
            elif item.lower().endswith(('.txt', '.log')):
                target_dir = new_dirs["logs"]
            elif item.lower().endswith(('.md', '.html', '.pdf')):
                target_dir = new_dirs["reports"]
            else:
                target_dir = new_dirs["temp"]
            
            new_path = os.path.join(target_dir, item)
            
            try:
                if os.path.isfile(old_path):
                    shutil.copy2(old_path, new_path)
                elif os.path.isdir(old_path):
                    if not os.path.exists(new_path):
                        shutil.copytree(old_path, new_path)
                print(f"✓ 已迁移: {old_path} -> {new_path}")
            except Exception as e:
                print(f"⚠️ 迁移失败: {old_path}, 错误: {e}")
        
        return self.get_step_output_dir(new_step, use_timestamp)
    
    def create_summary_report(self, steps: List[str], use_timestamp: bool = True) -> str:
        """创建汇总报告
        
        Args:
            steps: 步骤列表
            use_timestamp: 是否使用时间戳目录
            
        Returns:
            汇总报告文件路径
        """
        base_dir = self.get_base_output_dir(use_timestamp)
        report_path = os.path.join(base_dir, "summary_report.md")
        
        report_content = f"# 📋 处理流程汇总报告\n\n"
        report_content += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report_content += "## 📊 总体统计\n\n"
        report_content += "| 步骤 | 状态 | 处理项目 | 成功项目 | 失败项目 | 成功率 | 耗时 |\n"
        report_content += "|------|------|----------|----------|----------|--------|------|\n"
        
        for step in steps:
            step_dir = self.get_step_output_dir(step, use_timestamp)
            log_file = os.path.join(step_dir, "logs", "log.txt")
            report_file = os.path.join(step_dir, "reports", "report.md")
            
            # 这里可以添加更详细的统计信息
            report_content += f"| {step} | ✅ 完成 | - | - | - | - | - |\n"
        
        report_content += "\n## 📋 详细报告\n\n"
        
        for step in steps:
            report_file = os.path.join(self.get_step_output_dir(step, use_timestamp), "reports", "report.md")
            if os.path.exists(report_file):
                report_content += f"- {step} [详细报告]({os.path.relpath(report_file, base_dir)})\n"
        
        report_content += f"\n---\n*汇总报告由系统自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return report_path


# 全局输出管理器实例
_output_manager = None


def get_output_manager(config_manager=None) -> OutputManager:
    """获取全局输出管理器实例
    
    Args:
        config_manager: 配置管理器实例
        
    Returns:
        输出管理器实例
    """
    global _output_manager
    if _output_manager is None:
        _output_manager = OutputManager(config_manager)
    return _output_manager


if __name__ == "__main__":
    # 测试输出管理器
    output_manager = OutputManager()
    
    # 测试创建目录
    dirs = output_manager.ensure_step_dirs("step1")
    print("创建的目录:")
    for name, path in dirs.items():
        print(f"  {name}: {path}")
    
    # 测试保存文件
    log_path = output_manager.save_log("step1", "测试日志内容")
    print(f"\n日志文件已保存: {log_path}")
    
    report_path = output_manager.save_report("step1", "# 测试报告\n\n这是一个测试报告。")
    print(f"报告文件已保存: {report_path}")
    
    # 测试创建汇总报告
    summary_path = output_manager.create_summary_report(["step1", "step2", "step3"])
    print(f"汇总报告已保存: {summary_path}")