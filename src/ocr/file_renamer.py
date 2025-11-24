#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件重命名器模块
负责根据识别结果重命名文件，处理文件名冲突和验证
"""

import os
import re
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

try:
    from src.config.ocr_config_manager import OCRConfigManager
except ImportError:
    from ocr_config_manager import OCRConfigManager


@dataclass
class RenameResult:
    """文件重命名结果数据类"""
    original_path: str
    new_path: str
    original_filename: str
    new_filename: str
    amount: str
    success: bool
    error_message: Optional[str] = None


class FileRenamer:
    """文件重命名器，负责根据识别结果重命名文件"""
    
    def __init__(self, config_manager: OCRConfigManager):
        """初始化文件重命名器
        
        Args:
            config_manager: OCR配置管理器实例
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # 确保日志级别设置
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def generate_new_filename(self, original_path: str, amount: str) -> str:
        """生成新文件名
        
        Args:
            original_path: 原文件路径
            amount: 识别到的金额
            
        Returns:
            新文件名
            
        Raises:
            ValueError: 当文件名或金额无效时
        """
        # 验证输入参数
        if not original_path or not os.path.exists(original_path):
            raise ValueError(f"原文件路径无效或文件不存在: {original_path}")
        
        if not amount or not amount.strip():
            raise ValueError("金额不能为空")
        
        # 获取文件命名配置
        file_naming_config = self.config_manager.get_file_naming_config()
        separator = file_naming_config.get("separator", "_")
        max_length = file_naming_config.get("max_length", 255)
        
        # 解析文件路径
        dir_path = os.path.dirname(original_path)
        filename = os.path.basename(original_path)
        name, ext = os.path.splitext(filename)
        
        # 清洗金额，移除可能的特殊字符
        clean_amount = self._clean_amount(amount)
        
        # 生成新文件名
        new_filename = f"{name}{separator}{clean_amount}{ext}"
        
        # 检查文件名长度
        if len(new_filename) > max_length:
            # 如果超过最大长度，截断原文件名部分
            available_length = max_length - len(separator) - len(clean_amount) - len(ext)
            if available_length > 0:
                truncated_name = name[:available_length]
                new_filename = f"{truncated_name}{separator}{clean_amount}{ext}"
            else:
                # 如果连金额都放不下，使用最小格式
                new_filename = f"{clean_amount}{ext}"
        
        self.logger.debug(f"生成新文件名: {filename} -> {new_filename}")
        return new_filename
    
    def rename_file(self, original_path: str, amount: str) -> RenameResult:
        """重命名单个文件
        
        Args:
            original_path: 原文件路径
            amount: 识别到的金额
            
        Returns:
            重命名结果
        """
        start_time = time.time()
        original_filename = os.path.basename(original_path)
        
        try:
            # 验证文件名合法性
            self._validate_filename(original_filename)
            
            # 生成新文件名
            new_filename = self.generate_new_filename(original_path, amount)
            dir_path = os.path.dirname(original_path)
            new_path = os.path.join(dir_path, new_filename)
            
            # 处理文件名冲突
            final_path = self._handle_filename_conflict(new_path)
            final_filename = os.path.basename(final_path)
            
            # 执行重命名
            os.rename(original_path, final_path)
            
            processing_time = time.time() - start_time
            self.logger.info(f"文件重命名成功: {original_filename} -> {final_filename} (耗时: {processing_time:.3f}s)")
            
            return RenameResult(
                original_path=original_path,
                new_path=final_path,
                original_filename=original_filename,
                new_filename=final_filename,
                amount=amount,
                success=True,
                error_message=None
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_message = f"文件重命名失败: {str(e)}"
            self.logger.error(f"{error_message} (耗时: {processing_time:.3f}s)")
            
            return RenameResult(
                original_path=original_path,
                new_path=original_path,
                original_filename=original_filename,
                new_filename=original_filename,
                amount=amount,
                success=False,
                error_message=error_message
            )
    
    def batch_rename_files(self, rename_records: List[Dict[str, Any]]) -> List[RenameResult]:
        """批量重命名文件
        
        Args:
            rename_records: 重命名记录列表，每个记录包含文件路径和金额
            
        Returns:
            重命名结果列表
        """
        if not rename_records:
            self.logger.warning("没有文件需要重命名")
            return []
        
        self.logger.info(f"开始批量重命名，共 {len(rename_records)} 个文件")
        results = []
        
        for i, record in enumerate(rename_records, 1):
            file_path = record.get("file_path")
            amount = record.get("amount")
            
            if not file_path or not amount:
                self.logger.warning(f"跳过无效记录: {record}")
                continue
            
            self.logger.info(f"处理进度: {i}/{len(rename_records)} - {os.path.basename(file_path)}")
            result = self.rename_file(file_path, amount)
            results.append(result)
        
        # 统计结果
        success_count = sum(1 for r in results if r.success)
        self.logger.info(f"批量重命名完成，成功: {success_count}/{len(results)}")
        
        return results
    
    def _validate_filename(self, filename: str) -> None:
        """验证文件名合法性
        
        Args:
            filename: 文件名
            
        Raises:
            ValueError: 当文件名不合法时
        """
        if not filename:
            raise ValueError("文件名不能为空")
        
        # 检查是否包含非法字符
        illegal_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in illegal_chars:
            if char in filename:
                raise ValueError(f"文件名包含非法字符 '{char}': {filename}")
        
        # 检查是否为保留名称（Windows）
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        name_without_ext = os.path.splitext(filename)[0].upper()
        if name_without_ext in reserved_names:
            raise ValueError(f"文件名不能使用保留名称: {filename}")
    
    def _handle_filename_conflict(self, new_path: str) -> str:
        """处理文件名冲突
        
        Args:
            new_path: 新文件路径
            
        Returns:
            解决冲突后的最终文件路径
        """
        if not os.path.exists(new_path):
            return new_path
        
        # 文件已存在，添加数字后缀
        dir_path = os.path.dirname(new_path)
        filename = os.path.basename(new_path)
        name, ext = os.path.splitext(filename)
        
        counter = 1
        while True:
            new_filename = f"{name}_{counter}{ext}"
            candidate_path = os.path.join(dir_path, new_filename)
            
            if not os.path.exists(candidate_path):
                self.logger.debug(f"解决文件名冲突: {filename} -> {new_filename}")
                return candidate_path
            
            counter += 1
            
            # 防止无限循环
            if counter > 9999:
                raise RuntimeError(f"无法解决文件名冲突，尝试次数过多: {new_path}")
    
    def _clean_amount(self, amount: str) -> str:
        """清洗金额文本，移除不必要的字符
        
        Args:
            amount: 原始金额文本
            
        Returns:
            清洗后的金额文本
        """
        if not amount:
            return ""
        
        # 移除非数字字符（保留小数点和逗号）
        cleaned = re.sub(r'[^\d.,]', '', amount)
        
        # 移除开头和结尾的标点
        cleaned = cleaned.strip('.,')
        
        # 如果清洗后为空，返回原始值
        if not cleaned:
            return amount
        
        return cleaned
    
    def rollback_rename(self, rename_result: RenameResult) -> bool:
        """回滚重命名操作
        
        Args:
            rename_result: 重命名结果
            
        Returns:
            是否回滚成功
        """
        if not rename_result.success:
            self.logger.warning("重命名操作失败，无需回滚")
            return False
        
        try:
            if os.path.exists(rename_result.new_path):
                os.rename(rename_result.new_path, rename_result.original_path)
                self.logger.info(f"回滚重命名成功: {rename_result.new_filename} -> {rename_result.original_filename}")
                return True
            else:
                self.logger.warning(f"无法回滚，目标文件不存在: {rename_result.new_path}")
                return False
        except Exception as e:
            self.logger.error(f"回滚重命名失败: {e}")
            return False
    
    def batch_rollback(self, rename_results: List[RenameResult]) -> int:
        """批量回滚重命名操作
        
        Args:
            rename_results: 重命名结果列表
            
        Returns:
            成功回滚的数量
        """
        if not rename_results:
            return 0
        
        self.logger.info(f"开始批量回滚，共 {len(rename_results)} 个操作")
        success_count = 0
        
        # 按相反顺序回滚，避免文件名冲突
        for result in reversed(rename_results):
            if self.rollback_rename(result):
                success_count += 1
        
        self.logger.info(f"批量回滚完成，成功: {success_count}/{len(rename_results)}")
        return success_count


if __name__ == "__main__":
    # 测试文件重命名器
    try:
        from src.config.ocr_config_manager import get_ocr_config_manager
    except ImportError:
        from ocr_config_manager import get_ocr_config_manager
    
    # 初始化配置管理器
    config_manager = get_ocr_config_manager()
    
    # 创建文件重命名器
    renamer = FileRenamer(config_manager)
    
    # 测试生成新文件名
    test_path = "test.png"
    test_amount = "1500"
    new_filename = renamer.generate_new_filename(test_path, test_amount)
    print(f"新文件名: {new_filename}")
    
    # 测试文件名验证
    try:
        renamer._validate_filename("valid_filename.png")
        print("文件名验证通过")
    except ValueError as e:
        print(f"文件名验证失败: {e}")
    
    try:
        renamer._validate_filename("invalid<filename>.png")
        print("不应该到达这里")
    except ValueError as e:
        print(f"文件名验证失败（预期）: {e}")
    
    # 测试金额清洗
    print(renamer._clean_amount("1,500"))
    print(renamer._clean_amount("$1,500.00"))
    print(renamer._clean_amount("1500金币"))