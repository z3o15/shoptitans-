#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输出目录清理工具模块

提供统一的输出目录清理功能，确保每次运行程序时自动清理残留内容。
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Union
import logging

# 设置日志
logger = logging.getLogger(__name__)

class OutputCleaner:
    """输出目录清理��"""

    def __init__(self, project_root: Optional[Path] = None):
        """初始化清理器

        Args:
            project_root: 项目根目录，如果为None则自动检测
        """
        if project_root is None:
            # 自动检测项目根目录
            self.project_root = Path(__file__).resolve().parent.parent
        else:
            self.project_root = Path(project_root)

    def get_output_directories(self) -> List[Path]:
        """获取所有需要清理的输出目录"""
        return [
            self.project_root / "output" / "matching",
            self.project_root / "output" / "ocr",
            self.project_root / "output" / "comparisons",
            self.project_root / "output_enter_image" / "equipment_crop",
            self.project_root / "output_enter_image" / "equipment_transparent",
            self.project_root / "output_enter_image" / "feature_cache",
        ]

    def clean_directory(self, directory: Union[str, Path], recreate: bool = True) -> bool:
        """清理指定目录

        Args:
            directory: 要清理的目录路径
            recreate: 是否重新创建空目录

        Returns:
            bool: 清理是否成功
        """
        dir_path = Path(directory)

        try:
            if dir_path.exists():
                # 删除目录中的所有内容
                for item in dir_path.iterdir():
                    try:
                        if item.is_file() or item.is_symlink():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                    except Exception as e:
                        logger.warning(f"删除项目失败 {item}: {e}")

                logger.info(f"已清理目录: {dir_path}")

            # 重新创建空目录
            if recreate:
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"已重新创建目录: {dir_path}")

            return True

        except Exception as e:
            logger.error(f"清理目录失败 {dir_path}: {e}")
            return False

    def clean_all_outputs(self, exclude_patterns: Optional[List[str]] = None) -> bool:
        """清理所有输出目录

        Args:
            exclude_patterns: 要排除的目录模式列表

        Returns:
            bool: 是否全部清理成功
        """
        if exclude_patterns is None:
            exclude_patterns = []

        directories = self.get_output_directories()
        all_success = True

        logger.info("开始清理所有输出目录...")

        for dir_path in directories:
            # 检查是否需要排除
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern in str(dir_path):
                    should_exclude = True
                    break

            if should_exclude:
                logger.info(f"跳过排除的目录: {dir_path}")
                continue

            success = self.clean_directory(dir_path, recreate=True)
            if not success:
                all_success = False

        if all_success:
            logger.info("所有输出目录清理完成")
        else:
            logger.warning("部分目录清理失败")

        return all_success

    def clean_step_outputs(self, step_name: str) -> bool:
        """清理特定步骤的输出

        Args:
            step_name: 步骤名称 ('cut', 'match', 'ocr')

        Returns:
            bool: 清理是否成功
        """
        step_directories = {
            'cut': [
                self.project_root / "output_enter_image" / "equipment_crop",
                self.project_root / "output_enter_image" / "equipment_transparent",
            ],
            'match': [
                self.project_root / "output" / "matching",
                self.project_root / "output" / "comparisons",
            ],
            'ocr': [
                self.project_root / "output" / "ocr",
            ]
        }

        if step_name not in step_directories:
            logger.error(f"未知的步骤名称: {step_name}")
            return False

        directories = step_directories[step_name]
        all_success = True

        logger.info(f"清理步骤 {step_name} 的输出目录...")

        for dir_path in directories:
            success = self.clean_directory(dir_path, recreate=True)
            if not success:
                all_success = False

        return all_success

    def ensure_output_structure(self) -> bool:
        """确保输出目录结构存在

        Returns:
            bool: 是否成功
        """
        directories = self.get_output_directories()

        for dir_path in directories:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"创建目录失败 {dir_path}: {e}")
                return False

        logger.debug("输出目录结构已确保存在")
        return True

# 便利函数
def clean_all_outputs(project_root: Optional[Path] = None) -> bool:
    """清理所有输出目录的便利函数"""
    cleaner = OutputCleaner(project_root)
    return cleaner.clean_all_outputs()

def clean_step_outputs(step_name: str, project_root: Optional[Path] = None) -> bool:
    """清理特定步骤输出的便利函数"""
    cleaner = OutputCleaner(project_root)
    return cleaner.clean_step_outputs(step_name)

def ensure_directories(project_root: Optional[Path] = None) -> bool:
    """确保输出目录结构的便利函数"""
    cleaner = OutputCleaner(project_root)
    return cleaner.ensure_output_structure()

if __name__ == "__main__":
    # 测试模式
    logging.basicConfig(level=logging.INFO)

    cleaner = OutputCleaner()
    print("测试清理功能...")

    # 列出将要清理的目录
    directories = cleaner.get_output_directories()
    print("将清理以下目录:")
    for dir_path in directories:
        print(f"  - {dir_path}")

    # 询问用户确认
    response = input("\n确认清理所有输出目录? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        success = cleaner.clean_all_outputs()
        if success:
            print("✓ 清理完成")
        else:
            print("✗ 清理失败")
    else:
        print("已取消清理操作")