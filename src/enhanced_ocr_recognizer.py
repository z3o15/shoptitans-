#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版OCR金额识别器模块
支持多种预处理配置回退机制和图像增强功能
"""

import os
import re
import time
import cv2
import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

# 导入基础OCR识别器
from .ocr_amount_recognizer import OCRAmountRecognizer, OCRResult
from .ocr_config_manager import OCRConfigManager


@dataclass
class EnhancedOCRResult:
    """增强版OCR识别结果数据类"""
    image_path: str
    original_filename: str
    recognized_text: str
    extracted_amount: Optional[str]
    confidence: float
    processing_time: float
    success: bool
    error_message: Optional[str] = None
    preprocessing_used: str = ""
    fallback_attempts: int = 0


class EnhancedOCRRecognizer:
    """增强版OCR金额识别器，支持多种预处理配置回退机制"""
    
    def __init__(self, config_manager: OCRConfigManager = None):
        """初始化增强版OCR识别器
        
        Args:
            config_manager: OCR配置管理器实例
        """
        # 初始化基础识别器
        self.base_recognizer = OCRAmountRecognizer(config_manager)
        self.config_manager = self.base_recognizer.config_manager
        
        # 设置日志记录
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _enhance_image(self, image: np.ndarray) -> np.ndarray:
        """增强图像质量
        
        Args:
            image: 输入图像
            
        Returns:
            增强后的图像
        """
        enhanced_image = image.copy()
        
        # 获取增强配置
        ocr_config = self.config_manager.get_ocr_config()
        
        # 亮度调整
        brightness_config = ocr_config.get("brightness_adjustment", {})
        if brightness_config.get("enabled", False):
            target_brightness = brightness_config.get("target_brightness", 120)
            adjustment_method = brightness_config.get("adjustment_method", "gamma")
            
            if len(enhanced_image.shape) == 3:
                enhanced_image = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2GRAY)
            
            current_brightness = np.mean(enhanced_image)
            
            if adjustment_method == "gamma":
                # 使用伽马校正调整亮度
                gamma = np.log(target_brightness / 255.0) / np.log(current_brightness / 255.0)
                gamma = np.clip(gamma, 0.1, 3.0)
                enhanced_image = np.power(enhanced_image / 255.0, gamma) * 255.0
                enhanced_image = np.uint8(enhanced_image)
                
            elif adjustment_method == "linear":
                # 使用线性调整
                alpha = target_brightness / current_brightness if current_brightness > 0 else 1.0
                alpha = np.clip(alpha, 0.5, 2.0)
                enhanced_image = cv2.convertScaleAbs(enhanced_image, alpha=alpha, beta=0)
            
            self.logger.debug(f"应用亮度调整: {current_brightness:.2f} -> {np.mean(enhanced_image):.2f}")
        
        # 对比度增强
        contrast_config = ocr_config.get("contrast_enhancement", {})
        if contrast_config.get("enabled", False):
            method = contrast_config.get("method", "histogram_equalization")
            
            if len(enhanced_image.shape) == 3:
                enhanced_image = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2GRAY)
            
            if method == "histogram_equalization":
                enhanced_image = cv2.equalizeHist(enhanced_image)
                self.logger.debug("应用直方图均衡化")
            
            elif method == "clahe":
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                enhanced_image = clahe.apply(enhanced_image)
                self.logger.debug("应用CLAHE对比度增强")
        
        return enhanced_image
    
    def _apply_preprocessing_config(self, image_path: str, config: Dict[str, Any]) -> np.ndarray:
        """应用指定的预处理配置
        
        Args:
            image_path: 图像文件路径
            config: 预处理配置
            
        Returns:
            预处理后的图像
        """
        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"无法读取图像: {image_path}")
        
        # 应用预处理
        processed_image = image.copy()
        
        if config.get("grayscale", False):
            processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
        
        if config.get("threshold", False):
            if len(processed_image.shape) == 3:
                processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
            processed_image = cv2.adaptiveThreshold(
                processed_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
        
        if config.get("denoise", False):
            processed_image = cv2.medianBlur(processed_image, 3)
        
        return processed_image
    
    def recognize_with_fallback(self, image_path: str) -> EnhancedOCRResult:
        """使用回退机制进行OCR识别
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            增强版OCR识别结果
        """
        start_time = time.time()
        original_filename = os.path.basename(image_path)
        
        try:
            # 检查OCR是否启用
            if not self.config_manager.is_ocr_enabled():
                return EnhancedOCRResult(
                    image_path=image_path,
                    original_filename=original_filename,
                    recognized_text="",
                    extracted_amount=None,
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message="OCR功能已禁用"
                )
            
            # 获取配置
            ocr_config = self.config_manager.get_ocr_config()
            confidence_threshold = ocr_config.get("confidence_threshold", 0.7)
            
            # 获取回退预处理配置列表
            fallback_configs = ocr_config.get("fallback_preprocessing", [])
            
            # 如果没有回退配置，使用默认配置
            if not fallback_configs:
                fallback_configs = [
                    {"name": "默认配置", "grayscale": True, "threshold": False, "denoise": False}
                ]
            
            # 尝试每种预处理配置
            best_result = None
            best_confidence = 0.0
            
            for i, config in enumerate(fallback_configs):
                config_name = config.get("name", f"配置{i+1}")
                self.logger.debug(f"尝试预处理配置: {config_name}")
                
                try:
                    # 应用预处理
                    processed_image = self._apply_preprocessing_config(image_path, config)
                    
                    # 图像增强
                    if ocr_config.get("brightness_adjustment", {}).get("enabled", False) or \
                       ocr_config.get("contrast_enhancement", {}).get("enabled", False):
                        processed_image = self._enhance_image(processed_image)
                    
                    # OCR识别
                    results = self.base_recognizer.ocr_reader.readtext(processed_image)
                    
                    if results:
                        # 提取文本和置信度
                        recognized_text = " ".join([result[1] for result in results])
                        avg_confidence = sum([result[2] for result in results]) / len(results)
                        
                        # 提取金额
                        extracted_amount = self.base_recognizer._extract_amount_from_text(recognized_text)
                        
                        # 判断是否成功
                        success = extracted_amount is not None and avg_confidence >= confidence_threshold
                        
                        # 如果这是最好的结果，保存它
                        if avg_confidence > best_confidence:
                            best_confidence = avg_confidence
                            best_result = {
                                "recognized_text": recognized_text,
                                "extracted_amount": extracted_amount,
                                "confidence": avg_confidence,
                                "success": success,
                                "preprocessing_used": config_name,
                                "fallback_attempts": i + 1
                            }
                        
                        # 如果已经成功，可以提前结束
                        if success:
                            self.logger.debug(f"使用配置 '{config_name}' 成功识别")
                            break
                    
                except Exception as e:
                    self.logger.warning(f"配置 '{config_name}' 处理失败: {e}")
                    continue
            
            # 如果没有找到任何结果
            if best_result is None:
                return EnhancedOCRResult(
                    image_path=image_path,
                    original_filename=original_filename,
                    recognized_text="",
                    extracted_amount=None,
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message="所有预处理配置都无法识别文本",
                    fallback_attempts=len(fallback_configs)
                )
            
            processing_time = time.time() - start_time
            self.logger.info(f"识别完成: {original_filename}, 文本: '{best_result['recognized_text']}', "
                           f"金额: {best_result['extracted_amount']}, 置信度: {best_result['confidence']:.2f}, "
                           f"配置: {best_result['preprocessing_used']}, 耗时: {processing_time:.2f}s")
            
            return EnhancedOCRResult(
                image_path=image_path,
                original_filename=original_filename,
                recognized_text=best_result["recognized_text"],
                extracted_amount=best_result["extracted_amount"],
                confidence=best_result["confidence"],
                processing_time=processing_time,
                success=best_result["success"],
                error_message=None if best_result["success"] else f"识别置信度过低: {best_result['confidence']:.2f}",
                preprocessing_used=best_result["preprocessing_used"],
                fallback_attempts=best_result["fallback_attempts"]
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_message = f"识别过程中发生错误: {str(e)}"
            self.logger.error(f"识别失败: {image_path}, 错误: {error_message}")
            
            return EnhancedOCRResult(
                image_path=image_path,
                original_filename=original_filename,
                recognized_text="",
                extracted_amount=None,
                confidence=0.0,
                processing_time=processing_time,
                success=False,
                error_message=error_message
            )
    
    def batch_recognize_with_fallback(self, image_folder: str) -> List[EnhancedOCRResult]:
        """批量识别文件夹中的图片金额（使用回退机制）
        
        Args:
            image_folder: 图片文件夹路径
            
        Returns:
            增强版OCR识别结果列表
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
            result = self.recognize_with_fallback(image_path)
            results.append(result)
        
        # 统计结果
        success_count = sum(1 for r in results if r.success)
        self.logger.info(f"批量识别完成，成功: {success_count}/{len(results)}")
        
        return results
    
    def process_and_rename_with_fallback(self, image_folder: str, csv_output_path: str = None) -> List[Dict]:
        """处理文件夹中的图片并重命名（使用回退机制）
        
        Args:
            image_folder: 图片文件夹路径
            csv_output_path: CSV输出文件路径，如果为None则使用配置中的路径
            
        Returns:
            处理记录列表
        """
        # 批量识别
        enhanced_results = self.batch_recognize_with_fallback(image_folder)
        
        # 转换为基础识别器可处理的格式
        base_results = []
        for enhanced_result in enhanced_results:
            base_result = OCRResult(
                image_path=enhanced_result.image_path,
                original_filename=enhanced_result.original_filename,
                recognized_text=enhanced_result.recognized_text,
                extracted_amount=enhanced_result.extracted_amount,
                confidence=enhanced_result.confidence,
                processing_time=enhanced_result.processing_time,
                success=enhanced_result.success,
                error_message=enhanced_result.error_message
            )
            base_results.append(base_result)
        
        # 使用基础识别器进行文件重命名和CSV记录
        rename_records = []
        
        for enhanced_result, base_result in zip(enhanced_results, base_results):
            if enhanced_result.success and enhanced_result.extracted_amount:
                # 使用新的文件重命名器
                rename_result = self.base_recognizer.rename_file_with_amount(
                    base_result.image_path, enhanced_result.extracted_amount
                )
                
                # 创建CSV记录
                from .csv_record_manager import CSVRecord
                from datetime import datetime
                
                csv_record = CSVRecord(
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    original_filename=enhanced_result.original_filename,
                    new_filename=rename_result.new_filename,
                    recognized_amount=enhanced_result.extracted_amount,
                    processing_time=enhanced_result.processing_time,
                    status="成功" if rename_result.success else "失败",
                    error_message=rename_result.error_message,
                    recognized_text=enhanced_result.recognized_text,
                    confidence=enhanced_result.confidence,
                    original_path=enhanced_result.image_path,
                    new_path=rename_result.new_path
                )
                
                # 添加到CSV记录管理器缓存
                self.base_recognizer.csv_record_manager.add_record_to_cache(csv_record)
                
                # 创建处理记录
                record = {
                    "original_filename": enhanced_result.original_filename,
                    "new_filename": rename_result.new_filename,
                    "extracted_amount": enhanced_result.extracted_amount,
                    "success": rename_result.success,
                    "preprocessing_used": enhanced_result.preprocessing_used,
                    "fallback_attempts": enhanced_result.fallback_attempts,
                    "confidence": enhanced_result.confidence
                }
                
                rename_records.append(record)
            else:
                # 创建失败记录
                from .csv_record_manager import CSVRecord
                from datetime import datetime
                
                csv_record = CSVRecord(
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    original_filename=enhanced_result.original_filename,
                    new_filename=enhanced_result.original_filename,
                    recognized_amount="",
                    processing_time=enhanced_result.processing_time,
                    status="失败",
                    error_message=enhanced_result.error_message,
                    recognized_text=enhanced_result.recognized_text,
                    confidence=enhanced_result.confidence,
                    original_path=enhanced_result.image_path,
                    new_path=enhanced_result.image_path
                )
                
                # 添加到CSV记录管理器缓存
                self.base_recognizer.csv_record_manager.add_record_to_cache(csv_record)
                
                # 创建处理记录
                record = {
                    "original_filename": enhanced_result.original_filename,
                    "new_filename": enhanced_result.original_filename,
                    "extracted_amount": "",
                    "success": False,
                    "preprocessing_used": enhanced_result.preprocessing_used,
                    "fallback_attempts": enhanced_result.fallback_attempts,
                    "confidence": enhanced_result.confidence,
                    "error_message": enhanced_result.error_message
                }
                
                rename_records.append(record)
        
        # 保存记录到CSV
        self.base_recognizer.save_records_to_csv(csv_output_path)
        
        # 统计结果
        success_count = sum(1 for r in rename_records if r["success"])
        self.logger.info(f"处理完成，成功重命名: {success_count}/{len(rename_records)}")
        
        return rename_records


def run_enhanced_ocr(config_path: str = "optimized_ocr_config.json") -> None:
    """运行增强版OCR金额识别工具
    
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
        
        # 初始化增强版OCR识别器
        recognizer = EnhancedOCRRecognizer(ocr_config_manager)
        
        # 获取输入文件夹
        input_folder = ocr_config_manager.get_input_folder()
        print(f"\n开始处理文件夹: {input_folder}")
        
        # 处理并重命名文件
        records = recognizer.process_and_rename_with_fallback(input_folder)
        
        # 输出结果摘要
        success_count = sum(1 for r in records if r["success"])
        print(f"\n处理完成:")
        print(f"  总文件数: {len(records)}")
        print(f"  成功重命名: {success_count}")
        print(f"  失败数量: {len(records) - success_count}")
        
        if success_count > 0:
            print(f"\n成功重命名的文件:")
            for record in records:
                if record["success"]:
                    print(f"  {record['original_filename']} -> {record['new_filename']} "
                          f"(金额: {record['extracted_amount']}, 配置: {record['preprocessing_used']}, "
                          f"尝试次数: {record['fallback_attempts']})")
        
        if len(records) - success_count > 0:
            print(f"\n处理失败的文件:")
            for record in records:
                if not record["success"]:
                    print(f"  {record['original_filename']}: {record.get('error_message', '未知错误')} "
                          f"(配置: {record['preprocessing_used']}, 尝试次数: {record['fallback_attempts']})")
        
    except Exception as e:
        print(f"运行增强版OCR工具时发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="增强版OCR金额识别工具")
    parser.add_argument("--config", default="optimized_ocr_config.json", help="配置文件路径")
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
    
    # 运行增强版OCR识别
    run_enhanced_ocr(args.config)