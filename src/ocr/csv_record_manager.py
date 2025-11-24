#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV记录管理器模块
负责记录和管理OCR识别和文件重命名的详细信息
"""

import os
import csv
import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    from src.config.ocr_config_manager import OCRConfigManager
except ImportError:
    from ocr_config_manager import OCRConfigManager


@dataclass
class CSVRecord:
    """CSV记录数据类"""
    timestamp: str
    original_filename: str
    new_filename: str
    equipment_name: str  # 新增：装备名称
    amount: str  # 新增：金额
    processing_time: float
    status: str
    error_message: Optional[str] = None
    recognized_text: Optional[str] = None
    confidence: Optional[float] = None
    original_path: Optional[str] = None
    new_path: Optional[str] = None


class CSVRecordManager:
    """CSV记录管理器，负责记录重命名操作的详细信息"""
    
    def __init__(self, config_manager: OCRConfigManager):
        """初始化CSV记录管理器
        
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
        
        # 内存中的记录缓存
        self._records_cache = []
    
    def create_csv_file(self, csv_path: str) -> bool:
        """创建CSV文件并写入表头
        
        Args:
            csv_path: CSV文件路径
            
        Returns:
            是否创建成功
        """
        try:
            # 确保目录存在
            csv_dir = os.path.dirname(csv_path)
            if csv_dir:  # 只有当目录路径不为空时才创建
                os.makedirs(csv_dir, exist_ok=True)
            
            # 获取CSV配置
            csv_config = self.config_manager.get_csv_output_config()
            encoding = csv_config.get("encoding", "utf-8-sig")  # 使用utf-8-sig以支持Excel
            
            # 检查文件是否已存在
            if os.path.exists(csv_path):
                self.logger.info(f"CSV文件已存在: {csv_path}")
                return True
            
            # 创建文件并写入表头
            headers = self._get_csv_headers()
            
            with open(csv_path, 'w', newline='', encoding=encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
            
            self.logger.info(f"CSV文件创建成功: {csv_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"创建CSV文件失败: {csv_path}, 错误: {e}")
            return False
    
    def add_record(self, csv_path: str, record: CSVRecord) -> bool:
        """添加单条记录
        
        Args:
            csv_path: CSV文件路径
            record: 记录数据
            
        Returns:
            是否添加成功
        """
        try:
            # 确保CSV文件存在
            if not self._ensure_csv_exists(csv_path):
                return False
            
            # 获取CSV配置
            csv_config = self.config_manager.get_csv_output_config()
            encoding = csv_config.get("encoding", "utf-8-sig")  # 使用utf-8-sig以支持Excel
            
            # 获取表头
            headers = self._get_csv_headers()
            
            # 准备记录数据 - 包含五个字段：original_filename、new_filename、equipment_name、amount和confidence
            record_data = {
                'original_filename': record.original_filename,
                'new_filename': record.new_filename,
                'equipment_name': record.equipment_name,  # 新增
                'amount': record.amount,  # 新增
                'confidence': record.confidence or ""
            }
            
            # 写入记录
            with open(csv_path, 'a', newline='', encoding=encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writerow(record_data)
            
            self.logger.debug(f"记录已添加到CSV: {record.original_filename} -> {record.new_filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加记录到CSV失败: {csv_path}, 错误: {e}")
            return False
    
    def batch_add_records(self, csv_path: str, records: List[CSVRecord]) -> int:
        """批量添加记录
        
        Args:
            csv_path: CSV文件路径
            records: 记录列表
            
        Returns:
            成功添加的记录数量
        """
        if not records:
            self.logger.warning("没有记录需要添加")
            return 0
        
        self.logger.info(f"开始批量添加记录，共 {len(records)} 条")
        
        # 确保CSV文件存在
        if not self._ensure_csv_exists(csv_path):
            return 0
        
        success_count = 0
        for record in records:
            if self.add_record(csv_path, record):
                success_count += 1
        
        self.logger.info(f"批量添加记录完成，成功: {success_count}/{len(records)}")
        return success_count
    
    def add_record_to_cache(self, record: CSVRecord) -> None:
        """添加记录到内存缓存
        
        Args:
            record: 记录数据
        """
        self._records_cache.append(record)
        self.logger.debug(f"记录已添加到缓存: {record.original_filename}")
    
    def batch_add_records_to_cache(self, records: List[CSVRecord]) -> None:
        """批量添加记录到内存缓存
        
        Args:
            records: 记录列表
        """
        self._records_cache.extend(records)
        self.logger.debug(f"批量添加记录到缓存，共 {len(records)} 条")
    
    def flush_cache_to_csv(self, csv_path: str) -> int:
        """将缓存中的记录写入CSV文件
        
        Args:
            csv_path: CSV文件路径
            
        Returns:
            成功写入的记录数量
        """
        if not self._records_cache:
            self.logger.info("缓存中没有记录需要写入")
            return 0
        
        self.logger.info(f"开始写入缓存记录到CSV，共 {len(self._records_cache)} 条")
        success_count = self.batch_add_records(csv_path, self._records_cache)
        
        if success_count == len(self._records_cache):
            self._records_cache.clear()
            self.logger.info("缓存记录已成功写入CSV并清空")
        else:
            self.logger.warning(f"部分记录写入失败，保留剩余记录在缓存中")
        
        return success_count
    
    def load_existing_records(self, csv_path: str) -> List[CSVRecord]:
        """加载已存在的记录
        
        Args:
            csv_path: CSV文件路径
            
        Returns:
            记录列表
        """
        if not os.path.exists(csv_path):
            self.logger.info(f"CSV文件不存在: {csv_path}")
            return []
        
        try:
            # 获取CSV配置
            csv_config = self.config_manager.get_csv_output_config()
            encoding = csv_config.get("encoding", "utf-8")
            
            records = []
            
            with open(csv_path, 'r', newline='', encoding=encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    record = CSVRecord(
                        timestamp=row.get('timestamp', ''),
                        original_filename=row.get('original_filename', ''),
                        new_filename=row.get('new_filename', ''),
                        equipment_name=row.get('equipment_name', ''),  # 新增
                        amount=row.get('amount', ''),  # 新增
                        processing_time=float(row.get('processing_time', 0)),
                        status=row.get('status', ''),
                        error_message=row.get('error_message') if row.get('error_message') else None,
                        recognized_text=row.get('recognized_text') if row.get('recognized_text') else None,
                        confidence=float(row.get('confidence', 0)) if row.get('confidence') else None,
                        original_path=row.get('original_path') if row.get('original_path') else None,
                        new_path=row.get('new_path') if row.get('new_path') else None
                    )
                    records.append(record)
            
            self.logger.info(f"已加载 {len(records)} 条记录: {csv_path}")
            return records
            
        except Exception as e:
            self.logger.error(f"加载CSV记录失败: {csv_path}, 错误: {e}")
            return []
    
    def get_record_statistics(self, csv_path: str) -> Dict[str, Any]:
        """获取记录统计信息
        
        Args:
            csv_path: CSV文件路径
            
        Returns:
            统计信息字典
        """
        records = self.load_existing_records(csv_path)
        
        if not records:
            return {
                'total_records': 0,
                'successful_renames': 0,
                'failed_renames': 0,
                'success_rate': 0.0,
                'total_processing_time': 0.0,
                'average_processing_time': 0.0
            }
        
        total_records = len(records)
        successful_renames = sum(1 for r in records if r.status == '成功')
        failed_renames = total_records - successful_renames
        success_rate = (successful_renames / total_records) * 100 if total_records > 0 else 0.0
        
        total_processing_time = sum(r.processing_time for r in records)
        average_processing_time = total_processing_time / total_records if total_records > 0 else 0.0
        
        return {
            'total_records': total_records,
            'successful_renames': successful_renames,
            'failed_renames': failed_renames,
            'success_rate': success_rate,
            'total_processing_time': total_processing_time,
            'average_processing_time': average_processing_time
        }
    
    def _ensure_csv_exists(self, csv_path: str) -> bool:
        """确保CSV文件存在
        
        Args:
            csv_path: CSV文件路径
            
        Returns:
            是否确保文件存在成功
        """
        if os.path.exists(csv_path):
            return True
        
        return self.create_csv_file(csv_path)
    
    def _get_csv_headers(self) -> List[str]:
        """获取CSV表头
        
        Returns:
            表头字段列表
        """
        return [
            'original_filename',
            'new_filename',
            'equipment_name',  # 新增
            'amount',  # 新增
            'confidence'
        ]
    
    def backup_csv_file(self, csv_path: str) -> bool:
        """备份CSV文件
        
        Args:
            csv_path: CSV文件路径
            
        Returns:
            是否备份成功
        """
        if not os.path.exists(csv_path):
            self.logger.warning(f"CSV文件不存在，无需备份: {csv_path}")
            return False
        
        try:
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{csv_path}.backup_{timestamp}"
            
            # 复制文件
            import shutil
            shutil.copy2(csv_path, backup_path)
            
            self.logger.info(f"CSV文件备份成功: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"CSV文件备份失败: {csv_path}, 错误: {e}")
            return False
    
    def clear_cache(self) -> int:
        """清空记录缓存
        
        Returns:
            清空的记录数量
        """
        count = len(self._records_cache)
        self._records_cache.clear()
        self.logger.info(f"已清空缓存，共 {count} 条记录")
        return count
    
    def clear_csv_file(self, csv_path: str) -> bool:
        """清理CSV文件内容（保留表头）
        
        Args:
            csv_path: CSV文件路径
            
        Returns:
            是否清理成功
        """
        try:
            # 确保目录存在
            csv_dir = os.path.dirname(csv_path)
            if csv_dir:  # 只有当目录路径不为空时才创建
                os.makedirs(csv_dir, exist_ok=True)
            
            # 获取CSV配置
            csv_config = self.config_manager.get_csv_output_config()
            encoding = csv_config.get("encoding", "utf-8-sig")  # 使用utf-8-sig以支持Excel
            
            # 获取表头
            headers = self._get_csv_headers()
            
            # 重新创建文件并只写入表头
            with open(csv_path, 'w', newline='', encoding=encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
            
            self.logger.info(f"CSV文件内容已清理，保留表头: {csv_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"清理CSV文件失败: {csv_path}, 错误: {e}")
            return False


if __name__ == "__main__":
    # 测试CSV记录管理器
    try:
        from src.config.ocr_config_manager import get_ocr_config_manager
    except ImportError:
        from ocr_config_manager import get_ocr_config_manager
    
    # 初始化配置管理器
    config_manager = get_ocr_config_manager()
    
    # 创建CSV记录管理器
    csv_manager = CSVRecordManager(config_manager)
    
    # 测试创建CSV文件
    test_csv_path = "test_records.csv"
    if csv_manager.create_csv_file(test_csv_path):
        print("CSV文件创建成功")
    
    # 测试添加记录
    test_record = CSVRecord(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        original_filename="test.png",
        new_filename="test_1500.png",
        recognized_amount="1500",
        processing_time=1.23,
        status="成功",
        recognized_text="1500",
        confidence=0.95
    )
    
    if csv_manager.add_record(test_csv_path, test_record):
        print("记录添加成功")
    
    # 测试加载记录
    records = csv_manager.load_existing_records(test_csv_path)
    print(f"加载了 {len(records)} 条记录")
    
    # 测试统计信息
    stats = csv_manager.get_record_statistics(test_csv_path)
    print(f"统计信息: {stats}")
    
    # 清理测试文件
    try:
        os.remove(test_csv_path)
        print("测试文件已清理")
    except:
        pass