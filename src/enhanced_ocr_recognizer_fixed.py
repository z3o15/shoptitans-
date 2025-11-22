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

# 导入配置管理器
try:
    from .ocr_config_manager import OCRConfigManager
except ImportError:
    from ocr_config_manager import OCRConfigManager

# 导入其他依赖模块
try:
    from .file_renamer import FileRenamer, RenameResult
    from .csv_record_manager import CSVRecordManager, CSVRecord
except ImportError:
    from file_renamer import FileRenamer, RenameResult
    from csv_record_manager import CSVRecordManager, CSVRecord

# 导入OCR引擎
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("⚠️ EasyOCR未安装，请运行: pip install easyocr>=1.6.0")


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
            # 使用标准初始化方式，字符过滤将在识别后处理
            self.ocr_reader = easyocr.Reader(languages, gpu=False)
            self.logger.info("✓ EasyOCR引擎初始化成功")
        except Exception as e:
            self.logger.error(f"EasyOCR引擎初始化失败: {e}")
            raise
    
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
    
    def rename_file_with_text(self, file_path: str, text: str) -> RenameResult:
        """为文件添加识别文本后缀
        
        Args:
            file_path: 原文件路径
            text: 识别到的文本
            
        Returns:
            重命名结果对象
        """
        # 获取文件名（不含扩展名）
        dir_path = os.path.dirname(file_path)
        original_filename = os.path.basename(file_path)
        name, ext = os.path.splitext(original_filename)
        
        # 生成新文件名：装备名称+识别文本
        # 清理文本中的特殊字符，只保留数字和逗号
        cleaned_text = re.sub(r'[^\d,]', '', text)
        new_filename = f"{name}_{cleaned_text}{ext}"
        new_path = os.path.join(dir_path, new_filename)
        
        # 执行重命名
        try:
            os.rename(file_path, new_path)
            return RenameResult(
                original_path=file_path,
                new_path=new_path,
                original_filename=original_filename,
                new_filename=new_filename,
                amount=cleaned_text,  # 使用文本作为金额字段
                success=True,
                error_message=None
            )
        except Exception as e:
            return RenameResult(
                original_path=file_path,
                new_path=file_path,
                original_filename=original_filename,
                new_filename=original_filename,
                amount=cleaned_text,
                success=False,
                error_message=f"重命名失败: {str(e)}"
            )
    
    def save_records_to_csv(self, csv_path: str = None) -> bool:
        """保存记录到CSV文件（只保存简化格式的四个字段）
        
        Args:
            csv_path: CSV文件路径，如果为None则使用配置中的路径
            
        Returns:
            是否保存成功
        """
        if csv_path is None:
            csv_path = self.config_manager.get_output_csv_path()
        
        # 只保存简化格式的新式记录（四个字段：original_filename, new_filename, recognized_text, confidence）
        success_count = self.csv_record_manager.flush_cache_to_csv(csv_path)
        
        # 清空旧式记录（不再转换和保存）
        self.csv_records = []
        
        if success_count > 0:
            self.logger.info(f"简化格式记录已保存到CSV文件: {csv_path}, 共 {success_count} 条记录")
            return True
        else:
            self.logger.info("没有记录需要保存")
            return False
    
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
            
            # 关闭图像灰度化 - 如果是彩色图像，转换为灰度图进行亮度调整
            # 但在调整后不保持灰度图，而是转换回彩色图像
            is_color = len(enhanced_image.shape) == 3
            if is_color:
                gray_image = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2GRAY)
            else:
                gray_image = enhanced_image
            
            current_brightness = np.mean(gray_image)
            
            if adjustment_method == "gamma":
                # 使用伽马校正调整亮度
                gamma = np.log(target_brightness / 255.0) / np.log(current_brightness / 255.0)
                gamma = np.clip(gamma, 0.1, 3.0)
                adjusted_gray = np.power(gray_image / 255.0, gamma) * 255.0
                adjusted_gray = np.uint8(adjusted_gray)
                
                # 如果原图是彩色的，将调整后的灰度图转换回彩色
                if is_color:
                    enhanced_image = cv2.cvtColor(adjusted_gray, cv2.COLOR_GRAY2BGR)
                else:
                    enhanced_image = adjusted_gray
                
            elif adjustment_method == "linear":
                # 使用线性调整
                alpha = target_brightness / current_brightness if current_brightness > 0 else 1.0
                alpha = np.clip(alpha, 0.5, 2.0)
                adjusted_gray = cv2.convertScaleAbs(gray_image, alpha=alpha, beta=0)
                
                # 如果原图是彩色的，将调整后的灰度图转换回彩色
                if is_color:
                    enhanced_image = cv2.cvtColor(adjusted_gray, cv2.COLOR_GRAY2BGR)
                else:
                    enhanced_image = adjusted_gray
            
            self.logger.debug(f"应用亮度调整: {current_brightness:.2f} -> {np.mean(gray_image if not is_color else cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2GRAY)):.2f}")
        
        # 对比度增强
        contrast_config = ocr_config.get("contrast_enhancement", {})
        if contrast_config.get("enabled", False):
            method = contrast_config.get("method", "histogram_equalization")
            
            # 关闭图像灰度化 - 如果是彩色图像，转换为灰度图进行对比度增强
            # 但在增强后不保持灰度图，而是转换回彩色图像
            is_color = len(enhanced_image.shape) == 3
            if is_color:
                gray_image = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2GRAY)
            else:
                gray_image = enhanced_image
            
            if method == "histogram_equalization":
                enhanced_gray = cv2.equalizeHist(gray_image)
                self.logger.debug("应用直方图均衡化")
                
                # 如果原图是彩色的，将增强后的灰度图转换回彩色
                if is_color:
                    enhanced_image = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)
                else:
                    enhanced_image = enhanced_gray
            
            elif method == "clahe":
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                enhanced_gray = clahe.apply(gray_image)
                self.logger.debug("应用CLAHE对比度增强")
                
                # 如果原图是彩色的，将增强后的灰度图转换回彩色
                if is_color:
                    enhanced_image = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)
                else:
                    enhanced_image = enhanced_gray
        
        # 图像锐化
        sharpen_config = ocr_config.get("sharpening", {})
        if sharpen_config.get("enabled", False):
            # 创建锐化核
            kernel = np.array([[-1, -1, -1],
                              [-1,  9, -1],
                              [-1, -1, -1]])
            
            # 应用锐化
            enhanced_image = cv2.filter2D(enhanced_image, -1, kernel)
            self.logger.debug("应用图像锐化")
        
        # 图像缩放
        scaling_config = ocr_config.get("scaling", {})
        if scaling_config.get("enabled", False):
            scale_factor = scaling_config.get("scale_factor", 1.5)
            # 确保缩放因子在合理范围内
            scale_factor = max(1.0, min(2.0, scale_factor))
            
            # 获取原始尺寸
            height, width = enhanced_image.shape[:2]
            
            # 计算新尺寸
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            
            # 应用缩放
            enhanced_image = cv2.resize(enhanced_image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            self.logger.debug(f"应用图像缩放: {scale_factor}x")
        
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
        
        # 获取OCR配置中的区域设置
        ocr_config = self.config_manager.get_ocr_config()
        region_config = ocr_config.get("recognition_region", {})
        
        # 如果设置了识别区域，则裁剪图像
        if region_config.get("enabled", False):
            left = region_config.get("left", 0)
            right = region_config.get("right", image.shape[1])
            top = region_config.get("top", 0)
            bottom = region_config.get("bottom", image.shape[0])
            
            # 确保坐标在有效范围内
            left = max(0, min(left, image.shape[1] - 1))
            right = max(left + 1, min(right, image.shape[1]))
            top = max(0, min(top, image.shape[0] - 1))
            bottom = max(top + 1, min(bottom, image.shape[0]))
            
            # 裁剪图像
            image = image[top:bottom, left:right]
            self.logger.debug(f"应用识别区域裁剪: 左={left}, 右={right}, 上={top}, 下={bottom}")
        
        # 应用预处理
        processed_image = image.copy()
        
        # 调试日志：显示配置中的灰度化设置
        grayscale_enabled = config.get("grayscale", False)
        self.logger.debug(f"配置中的灰度化设置: {grayscale_enabled}")
        
        # 关闭图像灰度化 - 注释掉灰度化处理
        # if config.get("grayscale", False):
        #     processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
        #     self.logger.debug("已应用灰度化处理")
        # else:
        #     self.logger.debug("未应用灰度化处理")
        
        # 临时禁用自适应二值化 - 注释掉以测试
        # if config.get("threshold", False):
        #     if len(processed_image.shape) == 3:
        #         processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
        #     processed_image = cv2.adaptiveThreshold(
        #         processed_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        #         cv2.THRESH_BINARY, 11, 2
        #     )
        
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
                    {"name": "默认配置", "grayscale": True, "threshold": True, "denoise": False},
                    {"name": "自适应二值化配置", "grayscale": True, "threshold": True, "denoise": False}
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
                    results = self.ocr_reader.readtext(processed_image)
                    
                    if results:
                        # 提取文本和置信度
                        recognized_text = " ".join([result[1] for result in results])
                        # 过滤只保留数字和逗号
                        recognized_text = re.sub(r'[^\d,]', '', recognized_text)
                        avg_confidence = sum([result[2] for result in results]) / len(results)
                        
                        # 提取金额
                        extracted_amount = self._extract_amount_from_text(recognized_text)
                        
                        # 判断是否成功（使用原始置信度阈值）
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
            
            # 如果第一次尝试没有成功，尝试降低置信度阈值
            if best_result and not best_result["success"] and best_result["confidence"] > 0.6:
                self.logger.info(f"第一次尝试未成功，置信度{best_result['confidence']:.2f}低于阈值{confidence_threshold}，尝试降低阈值到0.6")
                
                # 使用降低的置信度阈值重新判断
                low_threshold_success = best_result["extracted_amount"] is not None and best_result["confidence"] >= 0.6
                
                if low_threshold_success:
                    best_result["success"] = True
                    best_result["fallback_attempts"] += 1  # 标记为使用了低阈值
                    self.logger.info(f"使用降低的置信度阈值(0.6)成功识别: {best_result['recognized_text']}")
            
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
            # 简化输出格式：只显示文本、置信度（删除金额列）
            self.logger.info(f"{original_filename} | 文本: '{best_result['recognized_text']}' | 置信度: {best_result['confidence']:.2f}")
            
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
    
    def get_subfolders(self, parent_folder: str) -> List[str]:
        """获取父文件夹下的所有子文件夹
        
        Args:
            parent_folder: 父文件夹路径
            
        Returns:
            子文件夹路径列表
        """
        if not os.path.exists(parent_folder):
            self.logger.error(f"文件夹不存在: {parent_folder}")
            return []
        
        subfolders = []
        try:
            for item in os.listdir(parent_folder):
                item_path = os.path.join(parent_folder, item)
                if os.path.isdir(item_path):
                    subfolders.append(item_path)
        except Exception as e:
            self.logger.error(f"获取子文件夹失败: {e}")
            return []
        
        return sorted(subfolders)
    
    def batch_recognize_with_fallback(self, image_folder: str, process_subfolders: bool = True) -> List[EnhancedOCRResult]:
        """批量识别文件夹中的图片金额（使用回退机制）
        
        Args:
            image_folder: 图片文件夹路径
            process_subfolders: 是否处理子文件夹，默认为True
            
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
        
        # 收集所有要处理的文件夹
        folders_to_process = [image_folder]
        
        # 如果需要处理子文件夹，则添加所有子文件夹
        if process_subfolders:
            subfolders = self.get_subfolders(image_folder)
            if subfolders:
                self.logger.info(f"发现 {len(subfolders)} 个子文件夹")
                folders_to_process.extend(subfolders)
        
        # 收集所有图像文件
        all_image_files = []
        for folder in folders_to_process:
            try:
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    if os.path.isfile(file_path):
                        _, ext = os.path.splitext(filename.lower())
                        if ext in supported_formats:
                            all_image_files.append(file_path)
            except Exception as e:
                self.logger.error(f"读取文件夹失败 {folder}: {e}")
        
        if not all_image_files:
            self.logger.warning(f"文件夹中没有找到支持的图像文件: {image_folder}")
            return []
        
        self.logger.info(f"开始批量识别，共 {len(all_image_files)} 个文件")
        
        results = []
        for i, image_path in enumerate(all_image_files, 1):
            self.logger.info(f"处理进度: {i}/{len(all_image_files)} - {os.path.basename(image_path)}")
            result = self.recognize_with_fallback(image_path)
            results.append(result)
        
        # 统计结果
        success_count = sum(1 for r in results if r.success)
        self.logger.info(f"批量识别完成，成功: {success_count}/{len(results)}")
        
        return results
    
    def process_and_rename_with_fallback(self, image_folder: str, csv_output_path: str = None, process_subfolders: bool = True) -> List[Dict]:
        """处理文件夹中的图片并重命名（使用回退机制）
        
        Args:
            image_folder: 图片文件夹路径
            csv_output_path: CSV输出文件路径，如果为None则使用配置中的路径
            process_subfolders: 是否处理子文件夹，默认为True
            
        Returns:
            处理记录列表
        """
        # 获取CSV文件路径
        if csv_output_path is None:
            csv_output_path = self.config_manager.get_output_csv_path()
        
        # 清理CSV文件内容（保留表头）
        self.csv_record_manager.clear_csv_file(csv_output_path)
        
        # 批量识别
        enhanced_results = self.batch_recognize_with_fallback(image_folder, process_subfolders)
        
        # 使用增强版识别器进行文件重命名和CSV记录
        rename_records = []
        
        for enhanced_result in enhanced_results:
            if enhanced_result.success and enhanced_result.recognized_text:
                # 使用文件重命名器 - 使用识别文本而不是提取的金额
                rename_result = self.rename_file_with_text(
                    enhanced_result.image_path, enhanced_result.recognized_text
                )
                
                # 创建简化的CSV记录 - 保留三个字段：original_filename、new_filename和confidence
                csv_record = CSVRecord(
                    timestamp="",  # 不需要时间戳
                    original_filename=enhanced_result.original_filename,  # 未修改的装备名称
                    new_filename=rename_result.new_filename,  # 修改过的装备名称
                    recognized_amount="",  # 不需要单独的金额字段
                    processing_time=0.0,  # 不需要处理时间
                    status="",  # 不需要状态
                    error_message=None,
                    recognized_text="",  # 不需要识别文本
                    confidence=enhanced_result.confidence,  # 保留置信度
                    original_path="",  # 不需要路径
                    new_path=""
                )
                
                # 添加到CSV记录管理器缓存
                self.csv_record_manager.add_record_to_cache(csv_record)
                
                # 创建处理记录
                record = {
                    "original_filename": enhanced_result.original_filename,
                    "new_filename": rename_result.new_filename,
                    "extracted_amount": enhanced_result.recognized_text,  # 使用识别文本
                    "success": rename_result.success,
                    "preprocessing_used": enhanced_result.preprocessing_used,
                    "fallback_attempts": enhanced_result.fallback_attempts,
                    "confidence": enhanced_result.confidence
                }
                
                rename_records.append(record)
            else:
                # 创建失败记录 - 保留三个字段：original_filename、new_filename和confidence
                csv_record = CSVRecord(
                    timestamp="",  # 不需要时间戳
                    original_filename=enhanced_result.original_filename,  # 未修改的装备名称
                    new_filename=enhanced_result.original_filename,  # 未修改的装备名称（失败时）
                    recognized_amount="",  # 不需要单独的金额字段
                    processing_time=0.0,  # 不需要处理时间
                    status="",  # 不需要状态
                    error_message=None,
                    recognized_text="",  # 不需要识别文本
                    confidence=enhanced_result.confidence,  # 保留置信度
                    original_path="",  # 不需要路径
                    new_path=""
                )
                
                # 添加到CSV记录管理器缓存
                self.csv_record_manager.add_record_to_cache(csv_record)
                
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
        self.save_records_to_csv(csv_output_path)
        
        # 统计结果
        success_count = sum(1 for r in rename_records if r["success"])
        self.logger.info(f"处理完成，成功重命名: {success_count}/{len(rename_records)}")
        
        return rename_records


def run_enhanced_ocr(config_path: str = "optimized_ocr_config.json", process_subfolders: bool = True) -> None:
    """运行增强版OCR金额识别工具
    
    Args:
        config_path: 配置文件路径
        process_subfolders: 是否处理子文件夹，默认为True
    """
    try:
        # 初始化配置管理器
        try:
            from .config_manager import get_config_manager
        except ImportError:
            from config_manager import get_config_manager
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
        
        # 如果启用子文件夹处理，显示将要处理的子文件夹
        if process_subfolders:
            subfolders = recognizer.get_subfolders(input_folder)
            if subfolders:
                print(f"发现 {len(subfolders)} 个子文件夹:")
                for folder in subfolders:
                    print(f"  - {os.path.basename(folder)}")
            else:
                print("未发现子文件夹，仅处理主文件夹")
        
        # 处理并重命名文件
        records = recognizer.process_and_rename_with_fallback(input_folder, process_subfolders=process_subfolders)
        
        # 输出结果摘要
        success_count = sum(1 for r in records if r["success"])
        print(f"\n处理完成:")
        print(f"  总文件数: {len(records)}")
        print(f"  成功重命名: {success_count}")
        print(f"  失败数量: {len(records) - success_count}")
        
        # 去除成功重命名文件的输出，只保留处理失败文件的输出
        if len(records) - success_count > 0:
            print(f"\n处理失败的文件:")
            for record in records:
                if not record["success"]:
                    print(f"  {record['original_filename']}: {record.get('error_message', '未知错误')}")
        
    except Exception as e:
        print(f"运行增强版OCR工具时发生错误: {e}")
        import traceback
        traceback.print_exc()


    def recognize_equipment_name(self, image_path: str) -> Optional[str]:
        """识别装备名称
        
        Args:
            image_path: 装备图像路径
            
        Returns:
            识别到的装备名称，如果未识别到则返回None
        """
        try:
            from .equipment_recognizer import EnhancedEquipmentRecognizer
            from .config_manager import get_config_manager
            
            # 获取配置管理器
            config_manager = get_config_manager()
            
            # 创建装备识别器
            recognizer = EnhancedEquipmentRecognizer(
                default_threshold=config_manager.get_default_threshold(),
                algorithm_type="feature"
            )
            
            # 获取基准装备目录
            base_equipment_dir = "images/base_equipment"
            
            # 遍历所有基准装备进行匹配
            for base_filename in os.listdir(base_equipment_dir):
                if base_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    base_path = os.path.join(base_equipment_dir, base_filename)
                    equipment_name = os.path.splitext(base_filename)[0]
                    
                    # 比较图像
                    similarity, is_match = recognizer.compare_images(base_path, image_path)
                    
                    if is_match:
                        self.logger.info(f"识别到装备: {equipment_name}, 相似度: {similarity}%")
                        return equipment_name
            
            self.logger.warning(f"未识别到装备名称: {image_path}")
            return None
            
        except Exception as e:
            self.logger.error(f"装备名称识别失败: {image_path}, 错误: {e}")
            return None
    
    def process_and_integrate_results(self, equipment_folder: str, marker_folder: str,
                                     csv_output_path: str = None) -> List[Dict]:
        """处理并整合装备名称和金额识别结果
        
        Args:
            equipment_folder: 装备图片文件夹
            marker_folder: 带标记的装备图片文件夹
            csv_output_path: CSV输出文件路径
            
        Returns:
            整合后的处理记录列表
        """
        # 获取CSV文件路径
        if csv_output_path is None:
            csv_output_path = self.config_manager.get_output_csv_path()
        
        # 清理CSV文件内容（保留表头）
        self.csv_record_manager.clear_csv_file(csv_output_path)
        
        # 获取装备图片列表
        equipment_files = []
        for filename in sorted(os.listdir(equipment_folder)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                equipment_files.append(filename)
        
        # 获取金额图片列表
        marker_files = []
        for filename in sorted(os.listdir(marker_folder)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                marker_files.append(filename)
        
        # 整合处理记录
        integrated_records = []
        
        for i, equipment_file in enumerate(equipment_files):
            # 提取文件序号
            equipment_number = os.path.splitext(equipment_file)[0]
            
            # 识别装备名称
            equipment_path = os.path.join(equipment_folder, equipment_file)
            equipment_name = self.recognize_equipment_name(equipment_path)
            
            # 查找对应的金额文件
            amount = ""
            confidence = 0.0
            new_filename = equipment_file
            
            for marker_file in marker_files:
                marker_number = os.path.splitext(marker_file)[0].split('_')[0]
                if marker_number == equipment_number:
                    # 提取金额信息
                    marker_path = os.path.join(marker_folder, marker_file)
                    ocr_result = self.recognize_with_fallback(marker_path)
                    
                    if ocr_result.success:
                        amount = ocr_result.extracted_amount or ""
                        confidence = ocr_result.confidence
                        
                        # 生成新的文件名（包含装备名称和金额）
                        if equipment_name and amount:
                            new_filename = f"{equipment_number}_{equipment_name}_{amount}.png"
                        elif equipment_name:
                            new_filename = f"{equipment_number}_{equipment_name}.png"
                        elif amount:
                            new_filename = f"{equipment_number}_{amount}.png"
                    
                    break
            
            # 创建CSV记录
            csv_record = CSVRecord(
                timestamp="",
                original_filename=equipment_file,
                new_filename=new_filename,
                equipment_name=equipment_name or "未知装备",
                amount=amount,
                processing_time=0.0,
                status="成功" if (equipment_name or amount) else "失败",
                confidence=confidence
            )
            
            # 添加到CSV记录管理器缓存
            self.csv_record_manager.add_record_to_cache(csv_record)
            
            # 创建处理记录
            record = {
                "original_filename": equipment_file,
                "new_filename": new_filename,
                "equipment_name": equipment_name or "未知装备",
                "amount": amount,
                "confidence": confidence,
                "success": bool(equipment_name or amount)
            }
            
            integrated_records.append(record)
        
        # 保存记录到CSV
        self.save_records_to_csv(csv_output_path)
        
        # 统计结果
        success_count = sum(1 for r in integrated_records if r["success"])
        self.logger.info(f"整合处理完成，成功: {success_count}/{len(integrated_records)}")
        
        return integrated_records


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="增强版OCR金额识别工具")
    parser.add_argument("--config", default="optimized_ocr_config.json", help="配置文件路径")
    parser.add_argument("--input-dir", help="输入图片目录")
    parser.add_argument("--output-csv", help="输出CSV文件路径")
    parser.add_argument("--no-subfolders", action="store_true", help="不处理子文件夹，仅处理指定目录")
    parser.add_argument("--integrate", action="store_true", help="整合装备名称和金额识别结果")
    
    args = parser.parse_args()
    
    # 如果提供了输入目录，更新配置
    if args.input_dir:
        try:
            from .config_manager import get_config_manager
        except ImportError:
            from config_manager import get_config_manager
        base_config_manager = get_config_manager(args.config)
        ocr_config_manager = OCRConfigManager(base_config_manager)
        ocr_config_manager.set_input_folder(args.input_dir)
    
    # 如果提供了输出CSV路径，更新配置
    if args.output_csv:
        try:
            from .config_manager import get_config_manager
        except ImportError:
            from config_manager import get_config_manager
        base_config_manager = get_config_manager(args.config)
        ocr_config_manager = OCRConfigManager(base_config_manager)
        ocr_config_manager.set_output_csv_path(args.output_csv)
    
    # 如果指定了整合模式
    if args.integrate:
        try:
            # 初始化配置管理器
            try:
                from .config_manager import get_config_manager
            except ImportError:
                from config_manager import get_config_manager
            base_config_manager = get_config_manager(args.config)
            ocr_config_manager = OCRConfigManager(base_config_manager)
            
            # 初始化增强版OCR识别器
            recognizer = EnhancedOCRRecognizer(ocr_config_manager)
            
            # 获取最新的时间目录
            cropped_equipment_dir = "images/cropped_equipment"
            cropped_equipment_marker_dir = "images/cropped_equipment_marker"
            
            # 查找最新的时间目录
            subdirs = []
            for item in os.listdir(cropped_equipment_dir):
                item_path = os.path.join(cropped_equipment_dir, item)
                if os.path.isdir(item_path) and item.replace('_', '').replace(':', '').isdigit():
                    subdirs.append(item)
            
            if not subdirs:
                print("❌ 未找到切割装备目录")
                sys.exit(1)
            
            latest_dir = sorted(subdirs)[-1]
            equipment_folder = os.path.join(cropped_equipment_dir, latest_dir)
            marker_folder = os.path.join(cropped_equipment_marker_dir, latest_dir)
            
            print(f"✓ 找到时间目录: {latest_dir}")
            print(f"  装备目录: {equipment_folder}")
            print(f"  金额目录: {marker_folder}")
            
            # 执行整合处理
            records = recognizer.process_and_integrate_results(
                equipment_folder=equipment_folder,
                marker_folder=marker_folder
            )
            
            # 输出结果摘要
            success_count = sum(1 for r in records if r["success"])
            print(f"\n处理完成:")
            print(f"  总文件数: {len(records)}")
            print(f"  成功整合: {success_count}")
            print(f"  失败数量: {len(records) - success_count}")
            
            # 显示成功整合的记录
            if success_count > 0:
                print(f"\n成功整合的记录:")
                for record in records:
                    if record["success"]:
                        print(f"  {record['original_filename']} -> {record['new_filename']}")
                        print(f"    装备名称: {record['equipment_name']}")
                        print(f"    金额: {record['amount']}")
        except Exception as e:
            print(f"❌ 整合过程中出错: {e}")
            import traceback
            traceback.print_exc()
    else:
        # 运行增强版OCR识别
        process_subfolders = not args.no_subfolders
        run_enhanced_ocr(args.config, process_subfolders)