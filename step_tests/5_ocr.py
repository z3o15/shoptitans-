#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金额识别OCR功能

此模块专注于金额识别OCR功能，负责处理分割后的金额图片、识别金额文本并记录结果。
"""

import os
import sys
import cv2
import numpy as np
import logging
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Generator
from datetime import datetime
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont

# 添加项目根目录到sys.path
sys.path.append(str(Path(__file__).parent.parent))

# ============================================================================
# 配置日志系统
# ============================================================================

def setup_logging(log_file: Optional[Path] = None) -> logging.Logger:
    """配置日志系统"""
    logger = logging.getLogger('ocr_processor')
    logger.setLevel(logging.INFO)
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 控制台处理器 - 只显示关键信息
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器 - 记录详细信息
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


# ============================================================================
# 数据类
# ============================================================================

@dataclass
class ProcessingResult:
    """处理结果数据类"""
    filename: str
    success: bool
    recognized_text: str = ""
    formatted_amount: str = ""
    confidence: float = 0.0
    error_message: str = ""


@dataclass
class ProcessingSummary:
    """处理摘要数据类"""
    total: int
    success: int
    failed: int
    failed_files: List[Tuple[str, str]]  # (filename, error_message)
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        return (self.success / self.total * 100) if self.total > 0 else 0.0


# ============================================================================
# 图像处理工具类
# ============================================================================

class ImageProcessor:
    """图像处理工具类"""
    
    @staticmethod
    def load_image(image_path: Path) -> Optional[np.ndarray]:
        """加载图像并处理透明通道"""
        try:
            img = Image.open(image_path)
            
            # 处理RGBA图像
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            
            # 转换为numpy数组
            img_array = np.array(img)
            
            # 转换为BGR格式
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            return img_array
        except Exception as e:
            logging.getLogger('ocr_processor').error(f"加载图像失败 {image_path}: {e}")
            return None
    
    @staticmethod
    def create_background_mask(image: np.ndarray) -> np.ndarray:
        """创建背景掩码"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        return closing
    
    @staticmethod
    def apply_mask(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """应用掩码到图像"""
        mask_binary = np.where(mask > 127, 255, 0).astype(np.uint8)
        
        if len(mask_binary.shape) == 2:
            mask_3channel = cv2.merge([mask_binary, mask_binary, mask_binary])
        else:
            mask_3channel = mask_binary
        
        inverted_mask = 255 - mask_3channel
        return cv2.bitwise_and(image, inverted_mask)
    
    @staticmethod
    def create_comparison_image(original: np.ndarray, masked: np.ndarray, 
                               filename: str) -> np.ndarray:
        """创建对比图像"""
        try:
            target_height = 200
            orig_resized = cv2.resize(
                original, 
                (int(original.shape[1] * target_height / original.shape[0]), target_height)
            )
            mask_resized = cv2.resize(
                masked,
                (int(masked.shape[1] * target_height / masked.shape[0]), target_height)
            )
            
            width = orig_resized.shape[1] + mask_resized.shape[1] + 20
            comparison = np.zeros((target_height + 60, width, 3), dtype=np.uint8)
            comparison[:] = (255, 255, 255)
            
            y_offset = 40
            comparison[y_offset:y_offset+orig_resized.shape[0], 0:orig_resized.shape[1]] = orig_resized
            
            x_offset = orig_resized.shape[1] + 20
            comparison[y_offset:y_offset+mask_resized.shape[0], x_offset:x_offset+mask_resized.shape[1]] = mask_resized
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(comparison, f"Original: {filename}", (10, 25), font, 0.6, (0, 0, 0), 2)
            cv2.putText(comparison, f"Masked: {filename}", (x_offset + 10, 25), font, 0.6, (0, 0, 0), 2)
            
            return comparison
        except Exception:
            return np.hstack([original, masked]) if original.shape == masked.shape else original


# ============================================================================
# 文本处理工具类
# ============================================================================

class TextProcessor:
    """文本处理工具类"""
    
    @staticmethod
    def format_amount(text: str) -> str:
        """格式化金额文本"""
        text = text.strip().replace('$', '').replace(',', '').replace(' ', '')
        
        if 'k' in text.lower():
            try:
                value = float(text.lower().replace('k', ''))
                return str(int(value * 1000))
            except ValueError:
                return text
        
        return text


# ============================================================================
# 目录管理器
# ============================================================================

class DirectoryManager:
    """目录管理器"""
    
    def __init__(self, base_output_dir: Path):
        self.base_output_dir = base_output_dir
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def setup_output_directories(self) -> Dict[str, Path]:
        """设置输出目录结构"""
        # 直接使用基础目录，不创建子目录
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        
        dirs = {
            'base': self.base_output_dir,
            'csv': self.base_output_dir  # CSV文件直接放在基础目录
        }
        
        return dirs
    
    @staticmethod
    def find_latest_input_directory(base_dir: Path) -> Optional[Path]:
        """查找最新的输入目录"""
        if not base_dir.exists() or not base_dir.is_dir():
            return None
        
        # 查找时间命名的子目录
        time_dirs = []
        for item in base_dir.iterdir():
            if item.is_dir():
                # 检查是否为时间命名格式
                name = item.name.replace('_', '').replace(':', '').replace('-', '')
                if name.isdigit():
                    time_dirs.append((item, item.stat().st_mtime))
        
        if time_dirs:
            # 返回最新的目录
            time_dirs.sort(key=lambda x: x[1], reverse=True)
            return time_dirs[0][0]
        
        # 如果没有时间目录，返回基础目录
        return base_dir
    
    @staticmethod
    def get_image_files(directory: Path) -> Generator[Path, None, None]:
        """获取目录中的图像文件（生成器）"""
        if not directory.exists():
            return
        
        image_extensions = {'.png', '.jpg', '.jpeg', '.webp'}
        for file_path in sorted(directory.iterdir()):
            if file_path.suffix.lower() in image_extensions:
                yield file_path


# ============================================================================
# OCR处理器
# ============================================================================

class OCRProcessor:
    """OCR处理器主类"""
    
    def __init__(self, output_dir: Path, logger: logging.Logger):
        self.output_dir = output_dir
        self.logger = logger
        self.dir_manager = DirectoryManager(output_dir)
        self.image_processor = ImageProcessor()
        self.text_processor = TextProcessor()
        
        # 延迟导入OCR模块
        self.recognizer = None
        self.record_manager = None
        self.csv_file = None
        
    def initialize_ocr_modules(self) -> bool:
        """初始化OCR模块"""
        try:
            from src.ocr.enhanced_ocr_recognizer import EnhancedOCRRecognizer
            from src.config.ocr_config_manager import OCRConfigManager
            from src.config.config_manager import get_config_manager
            from src.ocr.csv_record_manager import CSVRecordManager, CSVRecord
            
            base_config_manager = get_config_manager()
            ocr_config_manager = OCRConfigManager(base_config_manager)
            self.recognizer = EnhancedOCRRecognizer(ocr_config_manager)
            self.record_manager = CSVRecordManager(ocr_config_manager)
            
            # 设置CSV文件路径 - 直接在输出目录
            self.csv_file = self.output_dir / f"amount_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            self.record_manager.create_csv_file(str(self.csv_file))
            
            self.logger.info("OCR模块初始化成功")
            return True
            
        except ImportError as e:
            self.logger.error(f"无法导入OCR模块: {e}")
            return False
        except Exception as e:
            self.logger.error(f"初始化OCR模块失败: {e}")
            return False
    
    def process_single_image(self, image_path: Path, output_dirs: Dict[str, Path]) -> ProcessingResult:
        """处理单个图像"""
        filename = image_path.name
        
        try:
            # 直接进行OCR识别，不保存任何图片
            self.logger.debug(f"开始OCR识别: {image_path}")
            result = self.recognizer.recognize_with_fallback(str(image_path))
            recognized_text = result.recognized_text.strip() if result and hasattr(result, 'recognized_text') else ""
            formatted_amount = self.text_processor.format_amount(recognized_text) if recognized_text else ""
            confidence = result.confidence if result and hasattr(result, 'confidence') else 0.0
            
            # 保存CSV记录
            from src.ocr.csv_record_manager import CSVRecord
            record = CSVRecord(
                timestamp=datetime.now().isoformat(),
                original_filename=filename,
                new_filename=filename,  # 不重命名文件
                equipment_name="",
                amount=formatted_amount,
                processing_time=0.0,
                status="成功" if recognized_text else "失败",
                recognized_text=recognized_text,
                confidence=confidence
            )
            self.record_manager.add_record(str(self.csv_file), record)
            
            # 如果没有识别到文本，记录为失败但不是错误
            if not recognized_text:
                error_msg = "OCR未识别到文本"
                self.logger.warning(f"处理图像 {filename}: {error_msg}")
                return ProcessingResult(
                    filename=filename,
                    success=False,
                    error_message=error_msg,
                    confidence=confidence
                )
            
            return ProcessingResult(
                filename=filename,
                success=True,
                recognized_text=recognized_text,
                formatted_amount=formatted_amount,
                confidence=confidence
            )
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.logger.error(f"处理图像 {filename} 失败: {error_msg}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return ProcessingResult(filename, False, error_message=error_msg)
    
    def process_batch(self, input_dir: Path) -> ProcessingSummary:
        """批量处理图像"""
        # 设置输出目录
        output_dirs = self.dir_manager.setup_output_directories()
        
        # 收集图像文件
        image_files = list(self.dir_manager.get_image_files(input_dir))
        total_files = len(image_files)
        
        if total_files == 0:
            self.logger.warning(f"在目录 {input_dir} 中未找到图像文件")
            return ProcessingSummary(0, 0, 0, [])
        
        print(f"\n开始处理 {total_files} 个图像文件...")
        
        # 处理图像
        success_count = 0
        failed_files = []
        results_list = []
        
        for idx, image_path in enumerate(image_files, 1):
            result = self.process_single_image(image_path, output_dirs)
            results_list.append(result)
            
            if result.success:
                success_count += 1
                self.logger.info(
                    f"[{idx}/{total_files}] {result.filename}: "
                    f"{result.recognized_text} -> {result.formatted_amount} "
                    f"(置信度: {result.confidence:.2f})"
                )
            else:
                failed_files.append((result.filename, result.error_message))
                self.logger.error(f"[{idx}/{total_files}] {result.filename}: {result.error_message}")
        
        # 生成报告
        summary = ProcessingSummary(total_files, success_count, len(failed_files), failed_files)
        self._generate_report(output_dirs['csv'], results_list, summary)
        
        return summary
    
    def _generate_report(self, output_dir: Path, results: List[ProcessingResult], summary: ProcessingSummary) -> None:
        """生成处理报告"""
        report_path = output_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("OCR金额识别处理报告\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"CSV文件: {self.csv_file.name}\n\n")
                
                f.write("=" * 80 + "\n")
                f.write("处理摘要\n")
                f.write("=" * 80 + "\n")
                f.write(f"总文件数: {summary.total}\n")
                f.write(f"成功识别: {summary.success} ({summary.success_rate:.1f}%)\n")
                f.write(f"识别失败: {summary.failed}\n\n")
                
                if results:
                    f.write("=" * 80 + "\n")
                    f.write("详细结果\n")
                    f.write("=" * 80 + "\n")
                    f.write(f"{'序号':<6} {'文件名':<20} {'识别文本':<15} {'格式化金额':<15} {'置信度':<10} {'状态'}\n")
                    f.write("-" * 80 + "\n")
                    
                    for idx, result in enumerate(results, 1):
                        status = "成功" if result.success else "失败"
                        f.write(f"{idx:<6} {result.filename:<20} {result.recognized_text:<15} "
                               f"{result.formatted_amount:<15} {result.confidence:<10.2f} {status}\n")
                
                if summary.failed_files:
                    f.write("\n" + "=" * 80 + "\n")
                    f.write("失败文件详情\n")
                    f.write("=" * 80 + "\n")
                    for filename, error in summary.failed_files:
                        f.write(f"- {filename}: {error}\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write("报告结束\n")
                f.write("=" * 80 + "\n")
            
            self.logger.info(f"报告已生成: {report_path}")
            print(f"\n报告已生成: {report_path}")
            
        except Exception as e:
            self.logger.error(f"生成报告失败: {e}")


# ============================================================================
# 主要功能函数
# ============================================================================

def process_amount_images(input_dir: Optional[str] = None,
                         output_dir: Optional[str] = None) -> bool:
    """
    处理金额图片
    
    Args:
        input_dir: 输入目录路径，默认为 'images/equipment_crop'
        output_dir: 输出目录路径，默认为 'ocr_output'
    
    Returns:
        bool: 处理是否成功
    """
    # 设置默认路径
    if input_dir is None:
        input_dir = "images/equipment_crop"
    if output_dir is None:
        output_dir = "ocr_output"
    
    # 转换为Path对象
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # 清空输出目录
    if output_path.exists():
        print(f"清空输出目录: {output_path}")
        shutil.rmtree(output_path)
    
    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 设置日志
    log_file = output_path / "log.txt"
    logger = setup_logging(log_file)
    
    print("=" * 60)
    print("金额图片OCR处理")
    print("=" * 60)
    
    # 查找输入目录
    latest_input_dir = DirectoryManager.find_latest_input_directory(input_path)
    if latest_input_dir is None:
        print(f"错误: 输入目录不存在: {input_path}")
        logger.error(f"输入目录不存在: {input_path}")
        return False
    
    print(f"输入目录: {latest_input_dir}")
    print(f"输出目录: {output_path}")
    print(f"日志文件: {log_file}")
    
    # 初始化处理器
    processor = OCRProcessor(output_path, logger)
    
    if not processor.initialize_ocr_modules():
        print("错误: OCR模块初始化失败")
        return False
    
    # 批量处理
    summary = processor.process_batch(latest_input_dir)
    
    # 输出摘要
    print("\n" + "=" * 60)
    print("处理完成")
    print("=" * 60)
    print(f"总计: {summary.total} 个文件")
    print(f"成功: {summary.success} 个 ({summary.success_rate:.1f}%)")
    print(f"失败: {summary.failed} 个")
    
    if summary.failed_files:
        print("\n失败文件列表:")
        for filename, error in summary.failed_files[:10]:  # 只显示前10个
            print(f"  - {filename}: {error}")
        if len(summary.failed_files) > 10:
            print(f"  ... 还有 {len(summary.failed_files) - 10} 个失败文件")
    
    print(f"\n结果已保存到: {output_path}")
    print(f"CSV记录: {processor.csv_file}")
    
    logger.info(f"处理完成: 成功 {summary.success}/{summary.total}")
    
    return summary.success > 0


# ============================================================================
# 主程序入口
# ============================================================================

def main():
    """主函数 - 自动执行OCR处理"""
    try:
        # 直接执行处理，不需要用户选择
        success = process_amount_images()
        
        if success:
            print("\n✓ OCR处理完成")
            return 0
        else:
            print("\n✗ OCR处理失败")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        return 130
    except Exception as e:
        print(f"\n错误: {e}")
        logging.getLogger('ocr_processor').exception("程序异常")
        return 1


if __name__ == "__main__":
    exit(main())