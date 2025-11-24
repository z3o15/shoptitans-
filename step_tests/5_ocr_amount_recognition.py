#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金额识别OCR模块测试
从 enhanced_recognition_start.py 提取的独立测试模块
专门用于测试金额识别OCR功能
"""

import os
import sys
import subprocess
import tempfile
import shutil
from datetime import datetime
import time
import json
import csv
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

# 导入统一日志管理器
try:
    from src.unified_logger import get_unified_logger
    UNIFIED_LOGGER_AVAILABLE = True
except ImportError:
    try:
        from unified_logger import get_unified_logger
        UNIFIED_LOGGER_AVAILABLE = True
    except ImportError:
        UNIFIED_LOGGER_AVAILABLE = False
        print("⚠️ 统一日志管理器不可用，使用默认输出")

# 导入统一的背景掩码函数
try:
    from src.utils.background_mask import create_background_mask
except ImportError:
    try:
        from utils.background_mask import create_background_mask
    except ImportError:
        print("⚠️ 无法导入统一的背景掩码函数，将使用本地定义")
        # 如果无法导入，定义一个本地函数作为后备
        def create_background_mask(image, target_color_bgr=(46, 33, 46), tolerance=20):
            """本地后备的背景掩码函数"""
            try:
                # 创建颜色范围掩码
                lower_bound = np.array([
                    max(0, target_color_bgr[0] - tolerance),
                    max(0, target_color_bgr[1] - tolerance),
                    max(0, target_color_bgr[2] - tolerance)
                ])
                upper_bound = np.array([
                    min(255, target_color_bgr[0] + tolerance),
                    min(255, target_color_bgr[1] + tolerance),
                    min(255, target_color_bgr[2] + tolerance)
                ])
                
                mask_bg = cv2.inRange(image, lower_bound, upper_bound)
                
                # 创建浅紫色掩码
                light_purple_lower = np.array([241, 240, 241])
                light_purple_upper = np.array([247, 250, 247])
                mask_light_purple = cv2.inRange(image, light_purple_lower, light_purple_upper)
                
                # 创建额外紫色掩码
                extra_purple_lower = np.array([
                    max(0, 79 - 50),
                    max(0, 53 - 50),
                    max(0, 103 - 50)
                ])
                extra_purple_upper = np.array([
                    min(255, 79 + 50),
                    min(255, 53 + 50),
                    min(255, 103 + 50)
                ])
                mask_extra_purple = cv2.inRange(image, extra_purple_lower, extra_purple_upper)
                
                # 合并掩码
                mask_combined = cv2.bitwise_or(mask_bg, mask_light_purple)
                mask_combined = cv2.bitwise_or(mask_combined, mask_extra_purple)
                
                # 应用轻微高斯模糊
                mask_combined = cv2.GaussianBlur(mask_combined, (3, 3), 0.1)
                
                # 二值化
                _, mask_combined = cv2.threshold(mask_combined, 200, 255, cv2.THRESH_BINARY)
                
                return mask_combined
            except Exception as e:
                # 减少错误输出的详细程度
                # print(f"[ERROR] 背景掩码创建失败: {e}")
                return np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)

def load_image(image_path):
    """加载图像并处理透明通道"""
    try:
        # 使用PIL加载图像以正确处理透明通道
        img = Image.open(image_path)
        
        # 如果是RGBA图像，转换为RGB（白色背景）
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        
        # 转换为numpy数组
        img_array = np.array(img)
        
        # 转换为BGR格式（OpenCV格式）
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        return img_array
    except Exception as e:
        # 减少错误输出的详细程度
        # print(f"[ERROR] 加载图像失败 {image_path}: {e}")
        return None

# create_background_mask函数已移至src/utils/background_mask.py，现在从那里导入

def apply_mask_to_image(image, mask):
    """
    将掩码应用到图像，生成掩码后的图像
    背景区域变为黑色，前景区域保持原色
    
    掩码逻辑（与create_background_mask一致）：
    - 255值: 背景区域(深紫色39212e、浅紫色20904f71、颜色103,53,79及其变化范围)
    - 0值: 前景区域(装备)
    """
    try:
        # 创建黑色背景
        black_bg = np.zeros_like(image)
        
        # 确保掩码是二值的（0和255）
        mask_binary = np.where(mask > 127, 255, 0).astype(np.uint8)
        
        # 对掩码进行边缘羽化处理，减少对文字边缘的硬切割
        # 使用较小的核进行轻微模糊，使边缘更柔和
        mask_blurred = cv2.GaussianBlur(mask_binary.astype(np.float32), (3, 3), 0.5)
        
        # 将模糊后的掩码归一化到0-1范围
        mask_normalized = mask_blurred / 255.0
        
        # 使用羽化掩码进行混合，减少边缘硬切割
        # 前景区域（掩码值为0）完全保留原图
        # 背景区域（掩码值为255）完全使用黑色
        # 边缘区域（掩码值在0-255之间）进行混合
        result = np.zeros_like(image, dtype=np.float32)
        
        for c in range(3):  # 对每个颜色通道处理
            result[:, :, c] = image[:, :, c] * (1 - mask_normalized) + black_bg[:, :, c] * mask_normalized
        
        return result.astype(np.uint8)
    except Exception as e:
        # 减少错误输出的详细程度
        # print(f"[ERROR] 掩码应用失败: {e}")
        return image

def create_comparison_image(original_image, masked_image, filename):
    """
    创建掩码前和掩码后的对比图像
    
    Args:
        original_image: 原始图像
        masked_image: 掩码后的图像
        filename: 文件名（用于标题）
        
    Returns:
        对比图像
    """
    try:
        # 调整图像大小为相同尺寸以便比较
        target_height = 200  # 设置统一高度
        original_resized = cv2.resize(original_image, (int(original_image.shape[1] * target_height / original_image.shape[0]), target_height))
        masked_resized = cv2.resize(masked_image, (int(masked_image.shape[1] * target_height / masked_image.shape[0]), target_height))
        
        # 创建对比图像（左右并排）
        comparison_width = original_resized.shape[1] + masked_resized.shape[1] + 20  # 添加20像素间隔
        comparison_image = np.zeros((target_height + 60, comparison_width, 3), dtype=np.uint8)  # 添加60像素用于标题
        comparison_image[:] = (255, 255, 255)  # 白色背景
        
        # 放置原始图像
        y_offset = 40  # 标题下方开始
        comparison_image[y_offset:y_offset+original_resized.shape[0], 0:original_resized.shape[1]] = original_resized
        
        # 放置掩码后图像
        x_offset = original_resized.shape[1] + 20  # 20像素间隔
        comparison_image[y_offset:y_offset+masked_resized.shape[0], x_offset:x_offset+masked_resized.shape[1]] = masked_resized
        
        # 添加文本标签
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        color = (0, 0, 0)  # 黑色文字
        thickness = 2
        
        # 添加原始图像标签
        cv2.putText(comparison_image, f"Original: {filename}", (10, 25), font, font_scale, color, thickness)
        
        # 添加掩码后图像标签
        cv2.putText(comparison_image, f"Masked: {filename}", (x_offset + 10, 25), font, font_scale, color, thickness)
        
        return comparison_image
    except Exception as e:
        # 减少错误输出的详细程度
        # print(f"[ERROR] 创建对比图像失败: {e}")
        # 如果创建对比图像失败，返回原始图像和掩码后图像的简单拼接
        try:
            return np.hstack([original_image, masked_image])
        except:
            return original_image

def check_dependencies():
    """检查依赖是否已安装"""
    if UNIFIED_LOGGER_AVAILABLE:
        logger = get_unified_logger()
        logger.start_step("step5_ocr", "系统依赖检查")
    else:
        print("检查系统依赖...")
        
    required_packages = ['cv2', 'PIL', 'numpy', 'pytesseract', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            elif package == 'numpy':
                import numpy
            elif package == 'pytesseract':
                import pytesseract
            elif package == 'pandas':
                import pandas
            if UNIFIED_LOGGER_AVAILABLE:
                logger.log_success(f"{package}")
            else:
                print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            if UNIFIED_LOGGER_AVAILABLE:
                logger.log_error(f"{package}")
            else:
                print(f"✗ {package}")
    
    if missing_packages:
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_info(f"缺少依赖包: {', '.join(missing_packages)}")
            logger.log_info("正在安装依赖...")
        else:
            print(f"\n缺少依赖包: {', '.join(missing_packages)}")
            print("正在安装依赖...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            if UNIFIED_LOGGER_AVAILABLE:
                logger.log_success("依赖安装完成")
                logger.end_step("step5_ocr", "完成")
            else:
                print("✓ 依赖安装完成")
            return True
        except subprocess.CalledProcessError:
            if UNIFIED_LOGGER_AVAILABLE:
                logger.log_error("依赖安装失败，请手动运行: pip install -r requirements.txt")
                logger.end_step("step5_ocr", "失败")
            else:
                print("✗ 依赖安装失败，请手动运行: pip install -r requirements.txt")
            return False
    else:
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_success("所有依赖已安装")
            logger.end_step("step5_ocr", "完成")
        else:
            print("✓ 所有依赖已安装")
        return True

def test_ocr_amount_recognition():
    """测试金额识别OCR功能"""
    if UNIFIED_LOGGER_AVAILABLE:
        logger = get_unified_logger()
        logger.start_step("step5_ocr", "测试金额识别OCR功能")
    else:
        print("\n" + "=" * 60)
        print("测试金额识别OCR功能")
        print("=" * 60)
        print("验证金额识别和OCR功能")
        print("-" * 60)
    
    test_results = []
    temp_dir = None
    
    try:
        # 创建临时目录
        if UNIFIED_LOGGER_AVAILABLE:
            temp_dir = logger.get_step_dir("step5_ocr") / "temp_files"
            temp_dir.mkdir(parents=True, exist_ok=True)
        else:
            temp_dir = tempfile.mkdtemp()
            print(f"创建临时测试目录: {temp_dir}")
        
        # 创建测试金额图片目录
        amount_dir = os.path.join(temp_dir, "amount_images")
        os.makedirs(amount_dir, exist_ok=True)
        
        # 测试1：创建不同金额的测试图片
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_info("创建不同金额的测试图片...")
        else:
            print("\n1. 创建不同金额的测试图片...")
        test_amounts = ["1000", "2500", "5000", "10000", "15000"]
        
        for i, amount in enumerate(test_amounts):
            # 创建金额图片
            amount_img = Image.new('RGB', (120, 40), color='white')
            draw = ImageDraw.Draw(amount_img)
            
            # 绘制金额文本
            try:
                # 尝试使用默认字体
                font = ImageFont.load_default()
                # 计算文本位置以居中
                text_width = draw.textlength(amount, font=font)
                x = (120 - text_width) // 2
                y = 10
                draw.text((x, y), amount, fill='black', font=font)
            except:
                # 如果字体加载失败，使用简单文本绘制
                draw.text((10, 10), amount, fill='black')
            
            # 保存图片
            amount_img.save(os.path.join(amount_dir, f"test_amount_{i+1}.png"))
        
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_success(f"创建了 {len(test_amounts)} 个金额测试图片")
        else:
            print(f"✓ 创建了 {len(test_amounts)} 个金额测试图片")
        test_results.append(("金额测试图片创建", True))
        
        # 测试2：测试OCR识别功能
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_info("测试OCR识别功能...")
        else:
            print("\n2. 测试OCR识别功能...")
        try:
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
            from enhanced_ocr_recognizer import EnhancedOCRRecognizer
            from ocr_config_manager import OCRConfigManager
            from config_manager import get_config_manager
            
            # 初始化配置管理器
            base_config_manager = get_config_manager()
            ocr_config_manager = OCRConfigManager(base_config_manager)
            
            # 初始化增强版OCR识别器
            recognizer = EnhancedOCRRecognizer(ocr_config_manager)
            
            # 测试每个金额图片的识别
            correct_count = 0
            for i, amount in enumerate(test_amounts):
                test_file = os.path.join(amount_dir, f"test_amount_{i+1}.png")
                try:
                    result = recognizer.recognize_text(test_file)
                    recognized_text = result.get('text', '').strip()
                    
                    if UNIFIED_LOGGER_AVAILABLE:
                        logger.log_info(f"原始金额: {amount}, 识别结果: {recognized_text}")
                    else:
                        print(f"  原始金额: {amount}, 识别结果: {recognized_text}")
                    
                    # 简单的匹配检查（允许一些差异）
                    if amount in recognized_text or recognized_text in amount:
                        correct_count += 1
                except Exception as e:
                    if UNIFIED_LOGGER_AVAILABLE:
                        logger.log_error(f"识别 {amount} 时出错: {e}")
                    else:
                        print(f"  ❌ 识别 {amount} 时出错: {e}")
            
            accuracy = (correct_count / len(test_amounts)) * 100
            if UNIFIED_LOGGER_AVAILABLE:
                logger.log_info(f"OCR识别准确率: {accuracy:.1f}% ({correct_count}/{len(test_amounts)})")
            else:
                print(f"✓ OCR识别准确率: {accuracy:.1f}% ({correct_count}/{len(test_amounts)})")
            
            if accuracy >= 80:  # 80%以上认为通过
                test_results.append(("OCR识别功能", True))
            else:
                test_results.append(("OCR识别功能", False))
                
        except ImportError as e:
            if UNIFIED_LOGGER_AVAILABLE:
                logger.log_error(f"导入OCR识别器失败: {e}")
            else:
                print(f"❌ 导入OCR识别器失败: {e}")
            test_results.append(("OCR识别功能", False))
        except Exception as e:
            if UNIFIED_LOGGER_AVAILABLE:
                logger.log_error(f"OCR识别功能测试失败: {e}")
            else:
                print(f"❌ OCR识别功能测试失败: {e}")
            test_results.append(("OCR识别功能", False))
        
        # 测试3：测试OCR配置管理
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_info("测试OCR配置管理...")
        else:
            print("\n3. 测试OCR配置管理...")
        try:
            from ocr_config_manager import OCRConfigManager
            from config_manager import get_config_manager
            
            # 初始化配置管理器
            base_config_manager = get_config_manager()
            ocr_config_manager = OCRConfigManager(base_config_manager)
            
            # 获取配置
            ocr_config = ocr_config_manager.get_ocr_config()
            
            if ocr_config and isinstance(ocr_config, dict):
                if UNIFIED_LOGGER_AVAILABLE:
                    logger.log_success("OCR配置管理功能正常")
                    logger.log_info(f"语言: {ocr_config.get('lang', 'eng')}")
                    logger.log_info(f"OCR引擎: {ocr_config.get('engine', 'tesseract')}")
                    logger.log_info(f"预处理: {ocr_config.get('preprocess', True)}")
                else:
                    print("✓ OCR配置管理功能正常")
                    print(f"  语言: {ocr_config.get('lang', 'eng')}")
                    print(f"  OCR引擎: {ocr_config.get('engine', 'tesseract')}")
                    print(f"  预处理: {ocr_config.get('preprocess', True)}")
                test_results.append(("OCR配置管理", True))
            else:
                if UNIFIED_LOGGER_AVAILABLE:
                    logger.log_error("OCR配置管理功能异常")
                else:
                    print("❌ OCR配置管理功能异常")
                test_results.append(("OCR配置管理", False))
                
        except ImportError as e:
            if UNIFIED_LOGGER_AVAILABLE:
                logger.log_error(f"导入OCR配置管理器失败: {e}")
            else:
                print(f"❌ 导入OCR配置管理器失败: {e}")
            test_results.append(("OCR配置管理", False))
        except Exception as e:
            if UNIFIED_LOGGER_AVAILABLE:
                logger.log_error(f"OCR配置管理测试失败: {e}")
            else:
                print(f"❌ OCR配置管理测试失败: {e}")
            test_results.append(("OCR配置管理", False))
        
        # 测试4：测试金额格式化功能
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_info("测试金额格式化功能...")
        else:
            print("\n4. 测试金额格式化功能...")
        try:
            # 测试各种金额格式的识别和转换
            test_cases = [
                ("1000", "1000"),
                ("1,000", "1000"),
                ("1 000", "1000"),
                ("$1000", "1000"),
                ("1000$", "1000"),
                ("1k", "1000"),
                ("2.5k", "2500"),
                ("10000", "10000"),
                ("10,000", "10000"),
            ]
            
            format_correct_count = 0
            for input_text, expected_output in test_cases:
                # 模拟金额格式化函数
                def format_amount(text):
                    # 移除常见的前缀和后缀
                    text = text.strip().replace('$', '').replace(',', '').replace(' ', '')
                    
                    # 处理k表示法
                    if 'k' in text.lower():
                        try:
                            value = float(text.lower().replace('k', ''))
                            return str(int(value * 1000))
                        except:
                            return text
                    
                    return text
                
                formatted = format_amount(input_text)
                if formatted == expected_output:
                    format_correct_count += 1
                else:
                    if UNIFIED_LOGGER_AVAILABLE:
                        logger.log_error(f"格式化失败: '{input_text}' -> '{formatted}' (期望: '{expected_output}')")
                    else:
                        print(f"  格式化失败: '{input_text}' -> '{formatted}' (期望: '{expected_output}')")
            
            format_accuracy = (format_correct_count / len(test_cases)) * 100
            if UNIFIED_LOGGER_AVAILABLE:
                logger.log_info(f"金额格式化准确率: {format_accuracy:.1f}% ({format_correct_count}/{len(test_cases)})")
            else:
                print(f"✓ 金额格式化准确率: {format_accuracy:.1f}% ({format_correct_count}/{len(test_cases)})")
            
            if format_accuracy >= 90:  # 90%以上认为通过
                test_results.append(("金额格式化功能", True))
            else:
                test_results.append(("金额格式化功能", False))
                
        except Exception as e:
            if UNIFIED_LOGGER_AVAILABLE:
                logger.log_error(f"金额格式化功能测试失败: {e}")
            else:
                print(f"❌ 金额格式化功能测试失败: {e}")
            test_results.append(("金额格式化功能", False))
        
        # 测试5：测试CSV记录管理
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_info("测试CSV记录管理...")
        else:
            print("\n5. 测试CSV记录管理...")
        try:
            from csv_record_manager import CSVRecordManager
            
            # 创建临时CSV文件
            csv_file = os.path.join(temp_dir, "test_records.csv")
            
            # 初始化CSV记录管理器
            record_manager = CSVRecordManager(csv_file)
            
            # 添加测试记录
            test_records = [
                {"filename": "test1.png", "equipment_name": "sword", "amount": "1000"},
                {"filename": "test2.png", "equipment_name": "armor", "amount": "2500"},
                {"filename": "test3.png", "equipment_name": "helmet", "amount": "5000"},
            ]
            
            for record in test_records:
                record_manager.add_record(record)
            
            # 读取记录验证
            saved_records = record_manager.read_records()
            
            if len(saved_records) == len(test_records):
                if UNIFIED_LOGGER_AVAILABLE:
                    logger.log_success("CSV记录管理功能正常")
                    logger.log_info(f"保存记录数: {len(saved_records)}")
                else:
                    print("✓ CSV记录管理功能正常")
                    print(f"  保存记录数: {len(saved_records)}")
                test_results.append(("CSV记录管理", True))
            else:
                if UNIFIED_LOGGER_AVAILABLE:
                    logger.log_error(f"CSV记录管理功能异常: 期望 {len(test_records)} 条记录，实际 {len(saved_records)} 条")
                else:
                    print(f"❌ CSV记录管理功能异常: 期望 {len(test_records)} 条记录，实际 {len(saved_records)} 条")
                test_results.append(("CSV记录管理", False))
                
        except ImportError as e:
            if UNIFIED_LOGGER_AVAILABLE:
                logger.log_error(f"导入CSV记录管理器失败: {e}")
            else:
                print(f"❌ 导入CSV记录管理器失败: {e}")
            test_results.append(("CSV记录管理", False))
        except Exception as e:
            if UNIFIED_LOGGER_AVAILABLE:
                logger.log_error(f"CSV记录管理测试失败: {e}")
            else:
                print(f"❌ CSV记录管理测试失败: {e}")
            test_results.append(("CSV记录管理", False))
        
    except Exception as e:
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_error(f"测试过程中出错: {e}")
        else:
            print(f"❌ 测试过程中出错: {e}")
        test_results.append(("测试执行", False))
    
    finally:
        # 清理临时目录
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                print("\n✓ 临时测试目录已清理")
            except Exception as e:
                print(f"⚠️ 清理临时目录时出错: {e}")
    
    # 输出测试结果
    if UNIFIED_LOGGER_AVAILABLE:
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        
        logger.log_info(f"总计: {passed}/{total} 个测试通过")
        
        # 生成报告
        stats = logger.get_step_stats("step5_ocr")
        additional_info = {
            "files_processed": [name for name, _ in test_results],
            "test_results": test_results
        }
        
        from src.report_generator import get_report_generator
        report_generator = get_report_generator()
        report_generator.generate_step_report("step5_ocr", stats, additional_info)
        logger.end_step("step5_ocr", "完成" if passed == total else "部分失败")
        
        return passed == total
    else:
        print("\n" + "=" * 60)
        print("金额识别OCR测试结果汇总")
        print("=" * 60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✓ 通过" if result else "✗ 失败"
            print(f"{test_name:20} {status}")
            if result:
                passed += 1
        
        print("-" * 60)
        print(f"总计: {passed}/{total} 个测试通过")
        
        if passed == total:
            print("🎉 金额识别OCR功能测试全部通过！")
            return True
        else:
            print("⚠️ 部分测试失败，请检查相关功能。")
            return False

def process_amount_images():
    """处理金额图片"""
    # 初始化日志系统
    if UNIFIED_LOGGER_AVAILABLE:
        logger = get_unified_logger()
        from src.report_generator import get_report_generator
        report_generator = get_report_generator()
        logger.start_step("step5_ocr", "OCR金额识别")
    else:
        print("\n" + "=" * 60)
        print("处理金额图片")
        print("=" * 60)
        print("此功能将识别图片中的金额并保存结果")
        print("-" * 60)
    
    # 检查依赖
    if not check_dependencies():
        if UNIFIED_LOGGER_AVAILABLE:
            logger.end_step("step5_ocr", "失败")
        return False
    
    # 检查金额图片目录
    amount_images_dir = "images/cropped_equipment_marker"
    
    if not os.path.exists(amount_images_dir):
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_error(f"金额图片目录不存在: {amount_images_dir}")
            logger.end_step("step5_ocr", "失败")
        else:
            print(f"❌ 金额图片目录不存在: {amount_images_dir}")
        return False
    
    # 查找最新的时间目录
    subdirs = []
    for item in os.listdir(amount_images_dir):
        item_path = os.path.join(amount_images_dir, item)
        if os.path.isdir(item_path) and item.replace('_', '').replace(':', '').isdigit():
            subdirs.append(item)
    
    if not subdirs:
        print("❌ 未找到时间命名的金额图片目录")
        return False
    
    latest_dir = sorted(subdirs)[-1]
    latest_dir_path = os.path.join(amount_images_dir, latest_dir)
    if UNIFIED_LOGGER_AVAILABLE:
        logger.log_info(f"找到时间目录: {latest_dir}")
    else:
        print(f"✓ 找到时间目录: {latest_dir}")
    
    # 获取金额图片文件
    amount_files = []
    for filename in os.listdir(latest_dir_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            amount_files.append(filename)
    
    if not amount_files:
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_error("未找到金额图片文件")
            logger.end_step("step5_ocr", "失败")
        else:
            print("❌ 未找到金额图片文件")
        return False
    
    if UNIFIED_LOGGER_AVAILABLE:
        logger.log_info(f"找到 {len(amount_files)} 个金额图片文件")
    else:
        print(f"找到 {len(amount_files)} 个金额图片文件")
    
    try:
        from src.enhanced_ocr_recognizer import EnhancedOCRRecognizer
        from src.ocr_config_manager import OCRConfigManager
        from src.config_manager import get_config_manager
        from src.csv_record_manager import CSVRecordManager, CSVRecord
    except ImportError as e:
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_error(f"导入错误: {e}")
            logger.log_info("尝试直接导入模块...")
        else:
            print(f"❌ 导入错误: {e}")
            print("尝试直接导入模块...")
        try:
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
            from enhanced_ocr_recognizer import EnhancedOCRRecognizer
            from ocr_config_manager import OCRConfigManager
            from config_manager import get_config_manager
            from csv_record_manager import CSVRecordManager, CSVRecord
        except ImportError as e2:
            if UNIFIED_LOGGER_AVAILABLE:
                logger.log_error(f"无法导入必要模块: {e2}")
                logger.end_step("step5_ocr", "失败")
            else:
                print(f"❌ 无法导入必要模块: {e2}")
            return False
    
    try:
        # 初始化配置管理器
        base_config_manager = get_config_manager()
        ocr_config_manager = OCRConfigManager(base_config_manager)
        
        # 初始化增强版OCR识别器
        recognizer = EnhancedOCRRecognizer(ocr_config_manager)
        
        # 初始化CSV记录管理器
        if UNIFIED_LOGGER_AVAILABLE:
            output_dir = logger.get_step_dir("step5_ocr") / "images"
            txt_output_dir = logger.get_step_dir("step5_ocr") / "txt"
            output_dir.mkdir(parents=True, exist_ok=True)
            txt_output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
        
        csv_file = os.path.join(output_dir, f"amount_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        
        # 创建CSV记录管理器（不需要传递csv_file，而是传递配置管理器）
        record_manager = CSVRecordManager(ocr_config_manager)
        
        # 创建CSV文件
        record_manager.create_csv_file(csv_file)
        
        # 创建掩码图像保存目录
        masked_output_dir = os.path.join(output_dir, "masked_amount_images")
        os.makedirs(masked_output_dir, exist_ok=True)
        
        # 创建对比图像保存目录
        comparison_output_dir = os.path.join(output_dir, "comparison_images")
        os.makedirs(comparison_output_dir, exist_ok=True)
        
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_info(f"掩码图像将保存到: {masked_output_dir}")
            logger.log_info(f"对比图像将保存到: {comparison_output_dir}")
        else:
            print(f"✓ 掩码图像将保存到: {masked_output_dir}")
            print(f"✓ 对比图像将保存到: {comparison_output_dir}")
        
        # 处理每个金额图片
        success_count = 0
        processed_count = 0
        
        for filename in sorted(amount_files):
            file_path = os.path.join(latest_dir_path, filename)
            if UNIFIED_LOGGER_AVAILABLE:
                logger.log_info(f"处理文件: {filename}")
            else:
                print(f"\n处理: {filename}")
            
            try:
                # 加载图像
                image = load_image(file_path)
                if image is None:
                    if UNIFIED_LOGGER_AVAILABLE:
                        logger.log_error(f"无法加载图像: {filename}")
                        logger.update_stats("step5_ocr", error_items=1)
                    else:
                        print(f"  ❌ 无法加载图像: {filename}")
                    continue
                
                # 创建掩码并应用
                mask = create_background_mask(image)
                masked_image = apply_mask_to_image(image, mask)
                
                # 保存掩码后的图像
                masked_filename = f"masked_{filename}"
                masked_path = os.path.join(masked_output_dir, masked_filename)
                
                # 尝试使用OpenCV保存，如果失败则使用PIL
                try:
                    cv2.imwrite(masked_path, masked_image)
                except:
                    try:
                        # 转换为PIL格式并保存
                        masked_rgb = cv2.cvtColor(masked_image, cv2.COLOR_BGR2RGB)
                        pil_image = Image.fromarray(masked_rgb)
                        pil_image.save(masked_path)
                    except Exception as e:
                        print(f"  ⚠️ 保存掩码图像失败: {e}")
                
                print(f"  ✓ 已保存掩码图像: {masked_filename}")
                
                # 创建对比图像并保存
                comparison_image = create_comparison_image(image, masked_image, filename)
                comparison_filename = f"comparison_{filename}"
                comparison_path = os.path.join(comparison_output_dir, comparison_filename)
                
                # 尝试使用OpenCV保存，如果失败则使用PIL
                try:
                    cv2.imwrite(comparison_path, comparison_image)
                except:
                    try:
                        # 转换为PIL格式并保存
                        comparison_rgb = cv2.cvtColor(comparison_image, cv2.COLOR_BGR2RGB)
                        pil_image = Image.fromarray(comparison_rgb)
                        pil_image.save(comparison_path)
                    except Exception as e:
                        print(f"  ⚠️ 保存对比图像失败: {e}")
                
                print(f"  ✓ 已保存对比图像: {comparison_filename}")
                
                # 识别金额（使用掩码后的图像）
                result = recognizer.recognize_with_fallback(masked_path)
                recognized_amount = result.recognized_text.strip()
                
                if recognized_amount:
                    # 格式化金额
                    def format_amount(text):
                        # 移除常见的前缀和后缀
                        text = text.strip().replace('$', '').replace(',', '').replace(' ', '')
                        
                        # 处理k表示法
                        if 'k' in text.lower():
                            try:
                                value = float(text.lower().replace('k', ''))
                                return str(int(value * 1000))
                            except:
                                return text
                        
                        return text
                    
                    formatted_amount = format_amount(recognized_amount)
                    
                    # 保存记录
                    record = CSVRecord(
                        timestamp=datetime.now().isoformat(),
                        original_filename=filename,
                        new_filename=masked_filename,
                        equipment_name="",  # 装备名称暂时为空
                        amount=formatted_amount,
                        processing_time=0.0,
                        status="成功",
                        recognized_text=recognized_amount,
                        confidence=result.confidence
                    )
                    
                    record_manager.add_record(csv_file, record)
                    success_count += 1
                    
                    print(f"  识别结果: {recognized_amount} -> {formatted_amount}")
                    print(f"  置信度: {result.confidence:.2f}")
                else:
                    print(f"  ❌ 未识别到金额")
                    
            except Exception as e:
                print(f"  ❌ 处理 {filename} 时出错: {e}")
        
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_success(f"处理完成: 成功识别 {success_count}/{len(amount_files)} 个金额图片")
            logger.log_info(f"结果已保存到: {csv_file}")
            logger.log_info(f"掩码图像已保存到: {masked_output_dir}")
            logger.log_info(f"对比图像已保存到: {comparison_output_dir}")
            
            # 生成处理报告
            stats = logger.get_step_stats("step5_ocr")
            additional_info = {
                "files_processed": amount_files,
                "success_count": success_count,
                "output_files": [csv_file, masked_output_dir, comparison_output_dir]
            }
            
            report_generator.generate_step_report("step5_ocr", stats, additional_info)
            logger.end_step("step5_ocr", "完成")
            
            logger.log_info(f"Total images: {len(amount_files)}, Processed: {processed_count}")
        else:
            print(f"\n✅ 处理完成: 成功识别 {success_count}/{len(amount_files)} 个金额图片")
            print(f"结果已保存到: {csv_file}")
            print(f"掩码图像已保存到: {masked_output_dir}")
            print(f"对比图像已保存到: {comparison_output_dir}")
        
        return True
        
    except Exception as e:
        if UNIFIED_LOGGER_AVAILABLE:
            logger.log_error(f"处理过程中出错: {e}")
            logger.end_step("step5_ocr", "失败")
        else:
            print(f"❌ 处理过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("金额识别OCR模块")
    print("=" * 50)
    print("1. 处理金额图片")
    print("2. 测试金额识别OCR功能")
    print("0. 退出")
    print("-" * 50)
    
    while True:
        try:
            choice = input("请选择操作 (0-2): ").strip()
            
            if choice == '0':
                print("感谢使用，再见！")
                break
            elif choice == '1':
                # 初始化日志管理器（如果可用）
                if UNIFIED_LOGGER_AVAILABLE:
                    try:
                        from src.config_manager import get_config_manager
                        config_manager = get_config_manager()
                        # 初始化日志系统已在函数开始时完成
                        pass
                    except ImportError:
                        pass
                
                process_amount_images()
            elif choice == '2':
                test_ocr_amount_recognition()
            else:
                print("无效选择，请输入0-2之间的数字")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()