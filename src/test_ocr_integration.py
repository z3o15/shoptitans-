#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR集成功能测试脚本
测试文件重命名和CSV记录功能
"""

import os
import sys
import shutil
import tempfile
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, 'src')

# 导入需要测试的模块
from src.ocr_config_manager import OCRConfigManager
from src.file_renamer import FileRenamer
from src.csv_record_manager import CSVRecordManager, CSVRecord
from src.ocr_amount_recognizer import OCRAmountRecognizer


def create_test_images(test_dir: str, num_images: int = 5) -> list:
    """创建测试图像文件
    
    Args:
        test_dir: 测试目录
        num_images: 创建的图像数量
        
    Returns:
        创建的图像文件路径列表
    """
    # 创建简单的测试图像（使用PIL创建带有文本的图像）
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        image_paths = []
        
        for i in range(1, num_images + 1):
            # 创建图像
            img = Image.new('RGB', (200, 100), color='white')
            draw = ImageDraw.Draw(img)
            
            # 添加文本（金额）
            amount = str(1000 + i * 100)
            draw.text((10, 10), amount, fill='black')
            
            # 保存图像
            image_path = os.path.join(test_dir, f"{i:02d}.png")
            img.save(image_path)
            image_paths.append(image_path)
        
        print(f"✓ 创建了 {len(image_paths)} 个测试图像")
        return image_paths
        
    except ImportError:
        print("⚠️ PIL未安装，无法创建测试图像")
        return []


def test_file_renamer():
    """测试文件重命名器"""
    print("\n" + "="*50)
    print("测试文件重命名器")
    print("="*50)
    
    # 创建临时目录和测试文件
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.png")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # 初始化配置管理器和文件重命名器
        config_manager = OCRConfigManager()
        renamer = FileRenamer(config_manager)
        
        # 测试生成新文件名
        try:
            new_filename = renamer.generate_new_filename(test_file, "1500")
            print(f"✓ 生成新文件名成功: {new_filename}")
        except Exception as e:
            print(f"✗ 生成新文件名失败: {e}")
        
        # 测试文件重命名
        try:
            result = renamer.rename_file(test_file, "1500")
            if result.success:
                print(f"✓ 文件重命名成功: {result.original_filename} -> {result.new_filename}")
            else:
                print(f"✗ 文件重命名失败: {result.error_message}")
        except Exception as e:
            print(f"✗ 文件重命名异常: {e}")


def test_csv_record_manager():
    """测试CSV记录管理器"""
    print("\n" + "="*50)
    print("测试CSV记录管理器")
    print("="*50)
    
    # 创建临时目录和CSV文件
    with tempfile.TemporaryDirectory() as temp_dir:
        csv_path = os.path.join(temp_dir, "test_records.csv")
        
        # 初始化配置管理器和CSV记录管理器
        config_manager = OCRConfigManager()
        csv_manager = CSVRecordManager(config_manager)
        
        # 测试创建CSV文件
        try:
            success = csv_manager.create_csv_file(csv_path)
            if success:
                print("✓ CSV文件创建成功")
            else:
                print("✗ CSV文件创建失败")
        except Exception as e:
            print(f"✗ CSV文件创建异常: {e}")
        
        # 测试添加记录
        try:
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
            
            success = csv_manager.add_record(csv_path, test_record)
            if success:
                print("✓ 记录添加成功")
            else:
                print("✗ 记录添加失败")
        except Exception as e:
            print(f"✗ 记录添加异常: {e}")
        
        # 测试加载记录
        try:
            records = csv_manager.load_existing_records(csv_path)
            print(f"✓ 加载记录成功，共 {len(records)} 条记录")
        except Exception as e:
            print(f"✗ 加载记录异常: {e}")
        
        # 测试统计信息
        try:
            stats = csv_manager.get_record_statistics(csv_path)
            print(f"✓ 统计信息获取成功: {stats}")
        except Exception as e:
            print(f"✗ 统计信息获取异常: {e}")


def test_ocr_integration():
    """测试OCR集成功能"""
    print("\n" + "="*50)
    print("测试OCR集成功能")
    print("="*50)
    
    # 创建临时目录和测试图像
    with tempfile.TemporaryDirectory() as temp_dir:
        image_paths = create_test_images(temp_dir, 3)
        
        if not image_paths:
            print("⚠️ 跳过OCR集成测试，因为没有测试图像")
            return
        
        # 初始化OCR识别器
        try:
            config_manager = OCRConfigManager()
            recognizer = OCRAmountRecognizer(config_manager)
            print("✓ OCR识别器初始化成功")
        except Exception as e:
            print(f"✗ OCR识别器初始化失败: {e}")
            return
        
        # 测试单个图像识别
        try:
            result = recognizer.recognize_amount(image_paths[0])
            if result.success:
                print(f"✓ 单个图像识别成功: {result.original_filename}, 金额: {result.extracted_amount}")
            else:
                print(f"✗ 单个图像识别失败: {result.error_message}")
        except Exception as e:
            print(f"✗ 单个图像识别异常: {e}")
        
        # 测试批量识别
        try:
            results = recognizer.batch_recognize_amounts(temp_dir)
            success_count = sum(1 for r in results if r.success)
            print(f"✓ 批量识别完成，成功: {success_count}/{len(results)}")
        except Exception as e:
            print(f"✗ 批量识别异常: {e}")
        
        # 测试处理和重命名
        try:
            csv_path = os.path.join(temp_dir, "ocr_results.csv")
            rename_records = recognizer.process_and_rename(temp_dir, csv_path)
            success_count = sum(1 for r in rename_records if r.success)
            print(f"✓ 处理和重命名完成，成功: {success_count}/{len(rename_records)}")
            
            # 检查CSV文件是否创建
            if os.path.exists(csv_path):
                print(f"✓ CSV文件创建成功: {csv_path}")
                
                # 获取统计信息
                stats = recognizer.get_processing_statistics(csv_path)
                print(f"✓ 处理统计信息: {stats}")
            else:
                print("✗ CSV文件未创建")
        except Exception as e:
            print(f"✗ 处理和重命名异常: {e}")


def main():
    """主测试函数"""
    print("开始OCR集成功能测试")
    print("="*50)
    
    # 检查依赖
    try:
        import easyocr
        print("✓ EasyOCR已安装")
    except ImportError:
        print("✗ EasyOCR未安装，请运行: pip install easyocr>=1.6.0")
        return
    
    try:
        from PIL import Image
        print("✓ PIL已安装")
    except ImportError:
        print("✗ PIL未安装，请运行: pip install Pillow")
        return
    
    # 运行测试
    test_file_renamer()
    test_csv_record_manager()
    test_ocr_integration()
    
    print("\n" + "="*50)
    print("测试完成")
    print("="*50)


if __name__ == "__main__":
    main()