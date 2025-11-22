#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR金额识别器模块
负责使用EasyOCR引擎识别图像中的金额信息
"""

import os
import re
import time
import csv
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# 图像处理库
import cv2
import numpy as np
from PIL import Image

# OCR引擎
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("⚠️ EasyOCR未安装，请运行: pip install easyocr>=1.6.0")

# 本地导入
from .ocr_config_manager import OCRConfigManager
from .file_renamer import FileRenamer, RenameResult
from .csv_record_manager import CSVRecordManager, CSVRecord


@dataclass
class OCRResult:
    """OCR识别结果数据类"""
    image_path: str
    original_filename: str
    recognized_text: str
    extracted_amount: Optional[str]
    confidence: float
    processing_time: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class RenameRecord:
    """文件重命名记录数据类"""
    timestamp: str
    original_path: str
    new_path: str
    original_filename: str
    new_filename: str
    extracted_amount: str
    confidence: float
    processing_time: float
    success: bool
    error_message: Optional[str] = None


class OCRAmountRecognizer:
    """OCR金额识别器，负责协调所有OCR相关组件"""
    
    def __init__(self, config_manager=None):
        """初始化OCR金额识别器
        
        Args:
            config_manager: OCR配置管理器实例，如果为None则创建新实例
        """
        # 初始化配置管理器
        if config_manager is None:
            self.config_manager = OCRConfigManager()
        else:
            self.config_manager = config_manager
        
        # 初始化OCR引擎
        self.ocr_reader = None
        
        # 设置日志记录
        self._setup_logging()
        
        # 初始化文件重命名器和CSV记录管理器
        self.file_renamer = FileRenamer(self.config_manager)
        self.csv_record_manager = CSVRecordManager(self.config_manager)
        
        # 初始化CSV记录器（保持向后兼容）
        self.csv_records = []
        
        # 在日志设置完成后初始化OCR引擎
        self._initialize_ocr_engine()
    
    def _setup_logging(self) -> None:
        """设置日志记录"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _initialize_ocr_engine(self) -> None:
        """初始化EasyOCR引擎"""
        if not EASYOCR_AVAILABLE:
            raise ImportError("EasyOCR未安装，请运行: pip install easyocr>=1.6.0")
        
        try:
            engine_config = self.config_manager.get_engine_config()
            languages = engine_config.get("language", ["en"])
            
            self.logger.info(f"正在初始化EasyOCR引擎，语言: {languages}")
            self.ocr_reader = easyocr.Reader(languages)
            self.logger.info("✓ EasyOCR引擎初始化成功")
        except Exception as e:
            self.logger.error(f"EasyOCR引擎初始化失败: {e}")
            raise
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """图像预处理
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            预处理后的图像数组
            
        Raises:
            FileNotFoundError: 图像文件不存在
            ValueError: 图像格式不支持或损坏
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图像文件不存在: {image_path}")
        
        try:
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"无法读取图像文件，可能格式不支持或文件损坏: {image_path}")
            
            # 获取预处理配置
            preprocessing_config = self.config_manager.get_preprocessing_config()
            
            # 灰度化
            if preprocessing_config.get("grayscale", True):
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                self.logger.debug(f"图像已灰度化: {image_path}")
            
            # 二值化
            if preprocessing_config.get("threshold", True):
                # 使用自适应阈值
                image = cv2.adaptiveThreshold(
                    image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv2.THRESH_BINARY, 11, 2
                )
                self.logger.debug(f"图像已二值化: {image_path}")
            
            # 降噪
            if preprocessing_config.get("denoise", True):
                # 使用中值滤波降噪
                image = cv2.medianBlur(image, 3)
                self.logger.debug(f"图像已降噪: {image_path}")
            
            return image
            
        except Exception as e:
            self.logger.error(f"图像预处理失败: {image_path}, 错误: {e}")
            raise ValueError(f"图像预处理失败: {e}")
    
    def _extract_amount_from_text(self, text: str) -> Optional[str]:
        """从识别文本中提取金额
        
        Args:
            text: OCR识别的文本
            
        Returns:
            提取的金额字符串，如果未找到则返回None
        """
        if not text or not text.strip():
            return None
        
        # 获取金额提取配置
        amount_config = self.config_manager.get_amount_extraction_config()
        price_pattern = amount_config.get("price_pattern", r"\d{1,3}(?:,\d{3})*")
        confidence_threshold = amount_config.get("confidence_threshold", 0.8)
        
        try:
            # 使用正则表达式匹配金额
            pattern = re.compile(price_pattern)
            matches = pattern.findall(text)
            
            if not matches:
                self.logger.debug(f"未在文本中找到金额模式: {text}")
                return None
            
            # 找到最大的金额（按数字值比较）
            max_amount = None
            max_value = 0
            
            for match in matches:
                # 移除逗号转换为数字进行比较
                numeric_value = int(re.sub(r'[^\d]', '', match))
                if numeric_value > max_value:
                    max_value = numeric_value
                    max_amount = match
            
            self.logger.debug(f"从文本中提取到金额: {max_amount}, 原文本: {text}")
            return max_amount
            
        except Exception as e:
            self.logger.error(f"金额提取失败: {text}, 错误: {e}")
            return None
    
    def recognize_amount(self, image_path: str) -> OCRResult:
        """识别单张图片中的金额
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            OCR识别结果
        """
        start_time = time.time()
        original_filename = os.path.basename(image_path)
        
        try:
            # 检查OCR是否启用
            if not self.config_manager.is_ocr_enabled():
                return OCRResult(
                    image_path=image_path,
                    original_filename=original_filename,
                    recognized_text="",
                    extracted_amount=None,
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message="OCR功能已禁用"
                )
            
            # 图像预处理
            processed_image = self._preprocess_image(image_path)
            
            # OCR识别
            engine_config = self.config_manager.get_engine_config()
            confidence_threshold = engine_config.get("confidence_threshold", 0.8)
            
            results = self.ocr_reader.readtext(processed_image)
            
            if not results:
                self.logger.warning(f"未识别到任何文本: {image_path}")
                return OCRResult(
                    image_path=image_path,
                    original_filename=original_filename,
                    recognized_text="",
                    extracted_amount=None,
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message="未识别到任何文本"
                )
            
            # 提取文本和置信度
            recognized_text = " ".join([result[1] for result in results])
            avg_confidence = sum([result[2] for result in results]) / len(results)
            
            # 检查置信度
            if avg_confidence < confidence_threshold:
                self.logger.warning(f"识别置信度过低: {avg_confidence:.2f}, 阈值: {confidence_threshold}, 文件: {image_path}")
                return OCRResult(
                    image_path=image_path,
                    original_filename=original_filename,
                    recognized_text=recognized_text,
                    extracted_amount=None,
                    confidence=avg_confidence,
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message=f"识别置信度过低: {avg_confidence:.2f}"
                )
            
            # 提取金额
            extracted_amount = self._extract_amount_from_text(recognized_text)
            
            processing_time = time.time() - start_time
            self.logger.info(f"识别完成: {image_path}, 文本: {recognized_text}, 金额: {extracted_amount}, 置信度: {avg_confidence:.2f}, 耗时: {processing_time:.2f}s")
            
            return OCRResult(
                image_path=image_path,
                original_filename=original_filename,
                recognized_text=recognized_text,
                extracted_amount=extracted_amount,
                confidence=avg_confidence,
                processing_time=processing_time,
                success=extracted_amount is not None,
                error_message=None if extracted_amount is not None else "未识别到有效金额"
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_message = f"识别过程中发生错误: {str(e)}"
            self.logger.error(f"识别失败: {image_path}, 错误: {error_message}")
            
            return OCRResult(
                image_path=image_path,
                original_filename=original_filename,
                recognized_text="",
                extracted_amount=None,
                confidence=0.0,
                processing_time=processing_time,
                success=False,
                error_message=error_message
            )
    
    def batch_recognize_amounts(self, image_folder: str) -> List[OCRResult]:
        """批量识别文件夹中的图片金额
        
        Args:
            image_folder: 图片文件夹路径
            
        Returns:
            OCR识别结果列表
        """
        if not os.path.exists(image_folder):
            self.logger.error(f"文件夹不存在: {image_folder}")
            return []
        
        # 获取支持的文件格式
        file_naming_config = self.config_manager.get_file_naming_config()
        supported_formats = file_naming_config.get("supported_formats", 
                                                 [".png", ".jpg", ".jpeg", ".bmp", ".tiff"])
        
        # 获取所有支持的图像文件
        image_files = []
        for filename in os.listdir(image_folder):
            file_path = os.path.join(image_folder, filename)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(filename.lower())
                if ext in supported_formats:
                    image_files.append(file_path)
        
        if not image_files:
            self.logger.warning(f"文件夹中没有找到支持的图像文件: {image_folder}")
            return []
        
        self.logger.info(f"开始批量识别，共 {len(image_files)} 个文件")
        
        results = []
        for i, image_path in enumerate(image_files, 1):
            self.logger.info(f"处理进度: {i}/{len(image_files)} - {os.path.basename(image_path)}")
            result = self.recognize_amount(image_path)
            results.append(result)
        
        # 统计结果
        success_count = sum(1 for r in results if r.success)
        self.logger.info(f"批量识别完成，成功: {success_count}/{len(results)}")
        
        return results
    
    def rename_file_with_amount(self, file_path: str, amount: str) -> RenameResult:
        """为文件添加金额后缀
        
        Args:
            file_path: 原文件路径
            amount: 识别到的金额
            
        Returns:
            重命名结果对象
        """
        return self.file_renamer.rename_file(file_path, amount)
    
    def save_records_to_csv(self, csv_path: str = None) -> bool:
        """保存记录到CSV文件
        
        Args:
            csv_path: CSV文件路径，如果为None则使用配置中的路径
            
        Returns:
            是否保存成功
        """
        if csv_path is None:
            csv_path = self.config_manager.get_output_csv_path()
        
        # 首先保存新式记录
        success_count = self.csv_record_manager.flush_cache_to_csv(csv_path)
        
        # 然后保存旧式记录（保持向后兼容）
        if self.csv_records:
            try:
                # 转换旧式记录为新式记录
                for old_record in self.csv_records:
                    new_record = CSVRecord(
                        timestamp=old_record.timestamp,
                        original_filename=old_record.original_filename,
                        new_filename=old_record.new_filename,
                        recognized_amount=old_record.extracted_amount,
                        processing_time=old_record.processing_time,
                        status="成功" if old_record.success else "失败",
                        error_message=old_record.error_message,
                        recognized_text=getattr(old_record, 'recognized_text', ''),
                        confidence=getattr(old_record, 'confidence', 0.0),
                        original_path=old_record.original_path,
                        new_path=old_record.new_path
                    )
                    self.csv_record_manager.add_record_to_cache(new_record)
                
                # 保存转换后的记录
                additional_count = self.csv_record_manager.flush_cache_to_csv(csv_path)
                success_count += additional_count
                
                # 清空旧式记录
                self.csv_records = []
                
                self.logger.info(f"记录已保存到CSV文件: {csv_path}, 共 {success_count} 条记录")
                return True
                
            except Exception as e:
                self.logger.error(f"保存CSV文件失败: {csv_path}, 错误: {e}")
                return False
        
        return success_count > 0
    
    def process_and_rename(self, image_folder: str, csv_output_path: str = None) -> List[RenameRecord]:
        """处理文件夹中的图片并重命名
        
        Args:
            image_folder: 图片文件夹路径
            csv_output_path: CSV输出文件路径，如果为None则使用配置中的路径
            
        Returns:
            重命名记录列表
        """
        # 批量识别
        ocr_results = self.batch_recognize_amounts(image_folder)
        
        rename_records = []
        
        for result in ocr_results:
            if result.success and result.extracted_amount:
                # 使用新的文件重命名器
                rename_result = self.rename_file_with_amount(
                    result.image_path, result.extracted_amount
                )
                
                # 创建CSV记录
                csv_record = CSVRecord(
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    original_filename=result.original_filename,
                    new_filename=rename_result.new_filename,
                    recognized_amount=result.extracted_amount,
                    processing_time=result.processing_time,
                    status="成功" if rename_result.success else "失败",
                    error_message=rename_result.error_message,
                    recognized_text=result.recognized_text,
                    confidence=result.confidence,
                    original_path=result.image_path,
                    new_path=rename_result.new_path
                )
                
                # 添加到CSV记录管理器缓存
                self.csv_record_manager.add_record_to_cache(csv_record)
                
                # 创建旧式记录（保持向后兼容）
                old_record = RenameRecord(
                    timestamp=csv_record.timestamp,
                    original_path=csv_record.original_path,
                    new_path=csv_record.new_path,
                    original_filename=csv_record.original_filename,
                    new_filename=csv_record.new_filename,
                    extracted_amount=csv_record.recognized_amount,
                    confidence=csv_record.confidence,
                    processing_time=csv_record.processing_time,
                    success=csv_record.status == "成功",
                    error_message=csv_record.error_message
                )
                
                rename_records.append(old_record)
            else:
                # 创建失败记录
                csv_record = CSVRecord(
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    original_filename=result.original_filename,
                    new_filename=result.original_filename,
                    recognized_amount="",
                    processing_time=result.processing_time,
                    status="失败",
                    error_message=result.error_message,
                    recognized_text=result.recognized_text,
                    confidence=result.confidence,
                    original_path=result.image_path,
                    new_path=result.image_path
                )
                
                # 添加到CSV记录管理器缓存
                self.csv_record_manager.add_record_to_cache(csv_record)
                
                # 创建旧式记录（保持向后兼容）
                old_record = RenameRecord(
                    timestamp=csv_record.timestamp,
                    original_path=csv_record.original_path,
                    new_path=csv_record.new_path,
                    original_filename=csv_record.original_filename,
                    new_filename=csv_record.new_filename,
                    extracted_amount=csv_record.recognized_amount,
                    confidence=csv_record.confidence,
                    processing_time=csv_record.processing_time,
                    success=False,
                    error_message=csv_record.error_message
                )
                
                rename_records.append(old_record)
        
        # 保存记录到CSV
        self.save_records_to_csv(csv_output_path)
        
        # 统计结果
        success_count = sum(1 for r in rename_records if r.success)
        self.logger.info(f"处理完成，成功重命名: {success_count}/{len(rename_records)}")
        
        return rename_records
    
    def get_processing_statistics(self, csv_path: str = None) -> Dict[str, Any]:
        """获取处理统计信息
        
        Args:
            csv_path: CSV文件路径，如果为None则使用配置中的路径
            
        Returns:
            统计信息字典
        """
        if csv_path is None:
            csv_path = self.config_manager.get_output_csv_path()
        
        return self.csv_record_manager.get_record_statistics(csv_path)
    
    def backup_csv_records(self, csv_path: str = None) -> bool:
        """备份CSV记录文件
        
        Args:
            csv_path: CSV文件路径，如果为None则使用配置中的路径
            
        Returns:
            是否备份成功
        """
        if csv_path is None:
            csv_path = self.config_manager.get_output_csv_path()
        
        return self.csv_record_manager.backup_csv_file(csv_path)


def run_ocr_standalone(config_path: str = "config.json") -> None:
    """独立运行OCR金额识别工具
    
    Args:
        config_path: 配置文件路径
    """
    try:
        # 初始化配置管理器
        from .config_manager import get_config_manager
        base_config_manager = get_config_manager(config_path)
        ocr_config_manager = OCRConfigManager(base_config_manager)
        
        # 打印配置摘要
        ocr_config_manager.print_ocr_config_summary()
        
        # 验证配置
        errors = ocr_config_manager.validate_ocr_config()
        if errors:
            print("配置验证失败:")
            for error in errors:
                print(f"  - {error}")
            return
        
        # 初始化OCR识别器
        recognizer = OCRAmountRecognizer(ocr_config_manager)
        
        # 获取输入文件夹
        input_folder = ocr_config_manager.get_input_folder()
        print(f"\n开始处理文件夹: {input_folder}")
        
        # 处理并重命名文件
        records = recognizer.process_and_rename(input_folder)
        
        # 输出结果摘要
        success_count = sum(1 for r in records if r.success)
        print(f"\n处理完成:")
        print(f"  总文件数: {len(records)}")
        print(f"  成功重命名: {success_count}")
        print(f"  失败数量: {len(records) - success_count}")
        
        if success_count > 0:
            print(f"\n成功重命名的文件:")
            for record in records:
                if record.success:
                    print(f"  {record.original_filename} -> {record.new_filename} (金额: {record.extracted_amount})")
        
        if len(records) - success_count > 0:
            print(f"\n处理失败的文件:")
            for record in records:
                if not record.success:
                    print(f"  {record.original_filename}: {record.error_message}")
        
    except Exception as e:
        print(f"运行OCR工具时发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="OCR金额识别工具")
    parser.add_argument("--config", default="config.json", help="配置文件路径")
    parser.add_argument("--input-dir", help="输入图片目录")
    parser.add_argument("--output-csv", help="输出CSV文件路径")
    
    args = parser.parse_args()
    
    # 如果提供了输入目录，更新配置
    if args.input_dir:
        from .config_manager import get_config_manager
        base_config_manager = get_config_manager(args.config)
        ocr_config_manager = OCRConfigManager(base_config_manager)
        ocr_config_manager.set_input_folder(args.input_dir)
    
    # 如果提供了输出CSV路径，更新配置
    if args.output_csv:
        from .config_manager import get_config_manager
        base_config_manager = get_config_manager(args.config)
        ocr_config_manager = OCRConfigManager(base_config_manager)
        ocr_config_manager.set_output_csv_path(args.output_csv)
    
    # 运行OCR识别
    run_ocr_standalone(args.config)