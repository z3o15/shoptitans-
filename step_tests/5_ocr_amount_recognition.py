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

# 导入节点日志管理器
try:
    from src.node_logger import get_logger, init_logger_from_config
    from src.config_manager import get_config_manager
    NODE_LOGGER_AVAILABLE = True
except ImportError:
    try:
        from node_logger import get_logger, init_logger_from_config
        from config_manager import get_config_manager
        NODE_LOGGER_AVAILABLE = True
    except ImportError:
        NODE_LOGGER_AVAILABLE = False
        print("⚠️ 节点日志管理器不可用，使用默认输出")

def check_dependencies():
    """检查依赖是否已安装"""
    if NODE_LOGGER_AVAILABLE:
        logger = get_logger()
        logger.start_node("系统依赖检查", "🔍")
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
            if NODE_LOGGER_AVAILABLE:
                logger.log_success(f"{package}")
            else:
                print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            if NODE_LOGGER_AVAILABLE:
                logger.log_error(f"{package}")
            else:
                print(f"✗ {package}")
    
    if missing_packages:
        if NODE_LOGGER_AVAILABLE:
            logger.log_info(f"缺少依赖包: {', '.join(missing_packages)}")
            logger.log_info("正在安装依赖...")
        else:
            print(f"\n缺少依赖包: {', '.join(missing_packages)}")
            print("正在安装依赖...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            if NODE_LOGGER_AVAILABLE:
                logger.log_success("依赖安装完成")
                logger.end_node("✅")
            else:
                print("✓ 依赖安装完成")
            return True
        except subprocess.CalledProcessError:
            if NODE_LOGGER_AVAILABLE:
                logger.log_error("依赖安装失败，请手动运行: pip install -r requirements.txt")
                logger.end_node("❌")
            else:
                print("✗ 依赖安装失败，请手动运行: pip install -r requirements.txt")
            return False
    else:
        if NODE_LOGGER_AVAILABLE:
            logger.log_success("所有依赖已安装")
            logger.end_node("✅")
        else:
            print("✓ 所有依赖已安装")
        return True

def test_ocr_amount_recognition():
    """测试金额识别OCR功能"""
    print("\n" + "=" * 60)
    print("测试金额识别OCR功能")
    print("=" * 60)
    print("验证金额识别和OCR功能")
    print("-" * 60)
    
    test_results = []
    temp_dir = None
    
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        print(f"创建临时测试目录: {temp_dir}")
        
        # 创建测试金额图片目录
        amount_dir = os.path.join(temp_dir, "amount_images")
        os.makedirs(amount_dir, exist_ok=True)
        
        # 测试1：创建不同金额的测试图片
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
        
        print(f"✓ 创建了 {len(test_amounts)} 个金额测试图片")
        test_results.append(("金额测试图片创建", True))
        
        # 测试2：测试OCR识别功能
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
                    
                    print(f"  原始金额: {amount}, 识别结果: {recognized_text}")
                    
                    # 简单的匹配检查（允许一些差异）
                    if amount in recognized_text or recognized_text in amount:
                        correct_count += 1
                except Exception as e:
                    print(f"  ❌ 识别 {amount} 时出错: {e}")
            
            accuracy = (correct_count / len(test_amounts)) * 100
            print(f"✓ OCR识别准确率: {accuracy:.1f}% ({correct_count}/{len(test_amounts)})")
            
            if accuracy >= 80:  # 80%以上认为通过
                test_results.append(("OCR识别功能", True))
            else:
                test_results.append(("OCR识别功能", False))
                
        except ImportError as e:
            print(f"❌ 导入OCR识别器失败: {e}")
            test_results.append(("OCR识别功能", False))
        except Exception as e:
            print(f"❌ OCR识别功能测试失败: {e}")
            test_results.append(("OCR识别功能", False))
        
        # 测试3：测试OCR配置管理
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
                print("✓ OCR配置管理功能正常")
                print(f"  语言: {ocr_config.get('lang', 'eng')}")
                print(f"  OCR引擎: {ocr_config.get('engine', 'tesseract')}")
                print(f"  预处理: {ocr_config.get('preprocess', True)}")
                test_results.append(("OCR配置管理", True))
            else:
                print("❌ OCR配置管理功能异常")
                test_results.append(("OCR配置管理", False))
                
        except ImportError as e:
            print(f"❌ 导入OCR配置管理器失败: {e}")
            test_results.append(("OCR配置管理", False))
        except Exception as e:
            print(f"❌ OCR配置管理测试失败: {e}")
            test_results.append(("OCR配置管理", False))
        
        # 测试4：测试金额格式化功能
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
                    print(f"  格式化失败: '{input_text}' -> '{formatted}' (期望: '{expected_output}')")
            
            format_accuracy = (format_correct_count / len(test_cases)) * 100
            print(f"✓ 金额格式化准确率: {format_accuracy:.1f}% ({format_correct_count}/{len(test_cases)})")
            
            if format_accuracy >= 90:  # 90%以上认为通过
                test_results.append(("金额格式化功能", True))
            else:
                test_results.append(("金额格式化功能", False))
                
        except Exception as e:
            print(f"❌ 金额格式化功能测试失败: {e}")
            test_results.append(("金额格式化功能", False))
        
        # 测试5：测试CSV记录管理
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
                print("✓ CSV记录管理功能正常")
                print(f"  保存记录数: {len(saved_records)}")
                test_results.append(("CSV记录管理", True))
            else:
                print(f"❌ CSV记录管理功能异常: 期望 {len(test_records)} 条记录，实际 {len(saved_records)} 条")
                test_results.append(("CSV记录管理", False))
                
        except ImportError as e:
            print(f"❌ 导入CSV记录管理器失败: {e}")
            test_results.append(("CSV记录管理", False))
        except Exception as e:
            print(f"❌ CSV记录管理测试失败: {e}")
            test_results.append(("CSV记录管理", False))
        
    except Exception as e:
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
    print("\n" + "=" * 60)
    print("处理金额图片")
    print("=" * 60)
    print("此功能将识别图片中的金额并保存结果")
    print("-" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 检查金额图片目录
    amount_images_dir = "images/cropped_equipment_marker"
    
    if not os.path.exists(amount_images_dir):
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
    print(f"✓ 找到时间目录: {latest_dir}")
    
    # 获取金额图片文件
    amount_files = []
    for filename in os.listdir(latest_dir_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            amount_files.append(filename)
    
    if not amount_files:
        print("❌ 未找到金额图片文件")
        return False
    
    print(f"找到 {len(amount_files)} 个金额图片文件")
    
    try:
        from src.enhanced_ocr_recognizer import EnhancedOCRRecognizer
        from src.ocr_config_manager import OCRConfigManager
        from src.config_manager import get_config_manager
        from src.csv_record_manager import CSVRecordManager
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("尝试直接导入模块...")
        try:
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
            from enhanced_ocr_recognizer import EnhancedOCRRecognizer
            from ocr_config_manager import OCRConfigManager
            from config_manager import get_config_manager
            from csv_record_manager import CSVRecordManager
        except ImportError as e2:
            print(f"❌ 无法导入必要模块: {e2}")
            return False
    
    try:
        # 初始化配置管理器
        base_config_manager = get_config_manager()
        ocr_config_manager = OCRConfigManager(base_config_manager)
        
        # 初始化增强版OCR识别器
        recognizer = EnhancedOCRRecognizer(ocr_config_manager)
        
        # 初始化CSV记录管理器
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        csv_file = os.path.join(output_dir, f"amount_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        record_manager = CSVRecordManager(csv_file)
        
        # 处理每个金额图片
        success_count = 0
        for filename in sorted(amount_files):
            file_path = os.path.join(latest_dir_path, filename)
            print(f"\n处理: {filename}")
            
            try:
                # 识别金额
                result = recognizer.recognize_text(file_path)
                recognized_amount = result.get('text', '').strip()
                
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
                    record = {
                        "filename": filename,
                        "recognized_amount": recognized_amount,
                        "formatted_amount": formatted_amount,
                        "confidence": result.get('confidence', 0),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    record_manager.add_record(record)
                    success_count += 1
                    
                    print(f"  识别结果: {recognized_amount} -> {formatted_amount}")
                    print(f"  置信度: {result.get('confidence', 0):.2f}")
                else:
                    print(f"  ❌ 未识别到金额")
                    
            except Exception as e:
                print(f"  ❌ 处理 {filename} 时出错: {e}")
        
        print(f"\n✅ 处理完成: 成功识别 {success_count}/{len(amount_files)} 个金额图片")
        print(f"结果已保存到: {csv_file}")
        
        return True
        
    except Exception as e:
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
                if NODE_LOGGER_AVAILABLE:
                    try:
                        from src.config_manager import get_config_manager
                        config_manager = get_config_manager()
                        init_logger_from_config(config_manager)
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