#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤4：整合装备名称和金额识别结果功能测试
从 enhanced_recognition_start.py 提取的独立测试模块
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
    
    required_packages = ['cv2', 'PIL', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            elif package == 'numpy':
                import numpy
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

def step4_integrate_results(auto_mode=True):
    """步骤4：整合装备名称和金额识别结果"""
    if NODE_LOGGER_AVAILABLE:
        logger = get_logger()
        logger.start_node("步骤4：整合装备名称和金额识别结果", "📊")
    else:
        print("\n" + "=" * 60)
        print("步骤 4/4：整合装备名称和金额识别结果")
        print("=" * 60)
        print("此步骤将整合装备名称和金额识别结果到统一CSV文件")
        print("-" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return False
    
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
        print("❌ 未找到切割装备目录，请先完成步骤2")
        return False
    
    latest_dir = sorted(subdirs)[-1]
    equipment_folder = os.path.join(cropped_equipment_dir, latest_dir)
    marker_folder = os.path.join(cropped_equipment_marker_dir, latest_dir)
    
    print(f"✓ 找到时间目录: {latest_dir}")
    print(f"  装备目录: {equipment_folder}")
    print(f"  金额目录: {marker_folder}")
    
    # 执行整合处理
    try:
        from src.enhanced_ocr_recognizer import EnhancedOCRRecognizer
        from src.ocr_config_manager import OCRConfigManager
        from src.config_manager import get_config_manager
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("尝试直接导入模块...")
        try:
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
            from enhanced_ocr_recognizer import EnhancedOCRRecognizer
            from ocr_config_manager import OCRConfigManager
            from config_manager import get_config_manager
        except ImportError as e2:
            print(f"❌ 无法导入必要模块: {e2}")
            return False
    
    try:
        # 初始化配置管理器
        base_config_manager = get_config_manager()
        ocr_config_manager = OCRConfigManager(base_config_manager)
        
        # 初始化增强版OCR识别器
        recognizer = EnhancedOCRRecognizer(ocr_config_manager)
        
        # 执行整合处理
        records = recognizer.process_and_integrate_results(
            equipment_folder=equipment_folder,
            marker_folder=marker_folder
        )
        
        # 输出结果摘要
        success_count = sum(1 for r in records if r["success"])
        if NODE_LOGGER_AVAILABLE:
            logger.log_info(f"处理文件: {len(records)}个")
            logger.log_info(f"成功整合: {success_count}个")
            logger.log_info(f"失败数量: {len(records) - success_count}个")
            logger.log_success("步骤4完成")
            logger.end_node("✅")
        else:
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
        
        return True
        
    except Exception as e:
        print(f"❌ 整合过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step4_integration():
    """测试步骤4：整合结果功能"""
    print("\n" + "=" * 60)
    print("测试步骤4：整合结果功能")
    print("=" * 60)
    print("验证OCR识别和结果整合")
    print("-" * 60)
    
    test_results = []
    temp_dir = None
    
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        print(f"创建临时测试目录: {temp_dir}")
        
        # 创建测试装备和标记目录
        equipment_dir = os.path.join(temp_dir, "equipment")
        marker_dir = os.path.join(temp_dir, "marker")
        os.makedirs(equipment_dir, exist_ok=True)
        os.makedirs(marker_dir, exist_ok=True)
        
        # 测试1：创建测试装备和标记文件
        print("\n1. 创建测试装备和标记文件...")
        
        # 创建测试装备文件（带装备名称后缀）
        equipment_names = ["sword", "armor", "helmet"]
        for i, name in enumerate(equipment_names):
            # 创建装备图片
            item_img = Image.new('RGB', (100, 100), color='white')
            draw = ImageDraw.Draw(item_img)
            draw.rectangle([10, 10, 90, 90], fill='blue', outline='black', width=2)
            
            # 添加装备名称
            try:
                # 尝试使用默认字体
                font = ImageFont.load_default()
                draw.text((20, 40), name, fill='white', font=font)
            except:
                # 如果字体加载失败，跳过文本绘制
                pass
            
            item_img.save(os.path.join(equipment_dir, f"{i+1:02d}_{name}.png"))
        
        # 创建测试标记文件（带金额后缀）
        amounts = ["1000", "2000", "3000"]
        for i, amount in enumerate(amounts):
            # 创建标记图片
            marker_img = Image.new('RGB', (100, 100), color='white')
            draw = ImageDraw.Draw(marker_img)
            draw.rectangle([10, 10, 90, 90], fill='green', outline='black', width=2)
            
            # 添加金额文本
            try:
                # 尝试使用默认字体
                font = ImageFont.load_default()
                draw.text((20, 40), amount, fill='white', font=font)
            except:
                # 如果字体加载失败，跳过文本绘制
                pass
            
            marker_img.save(os.path.join(marker_dir, f"{i+1:02d}_{amount}.png"))
        
        print(f"✓ 测试文件创建成功: {len(equipment_names)} 个装备, {len(amounts)} 个标记")
        test_results.append(("测试文件创建", True))
        
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
            
            # 测试单个文件识别
            test_file = os.path.join(equipment_dir, "01_sword.png")
            if os.path.exists(test_file):
                result = recognizer.recognize_text(test_file)
                print(f"✓ OCR识别功能正常: 识别结果 '{result.get('text', '')}'")
                test_results.append(("OCR识别功能", True))
            else:
                print("❌ 测试文件不存在")
                test_results.append(("OCR识别功能", False))
        except ImportError as e:
            print(f"⚠️ OCR识别功能不可用: {e}")
            test_results.append(("OCR识别功能", False))
        except Exception as e:
            print(f"❌ OCR识别功能测试失败: {e}")
            test_results.append(("OCR识别功能", False))
        
        # 测试3：测试结果整合功能
        print("\n3. 测试结果整合功能...")
        try:
            # 执行整合处理
            records = recognizer.process_and_integrate_results(
                equipment_folder=equipment_dir,
                marker_folder=marker_dir
            )
            
            if records and len(records) > 0:
                print(f"✓ 结果整合功能正常: 处理了 {len(records)} 个记录")
                test_results.append(("结果整合功能", True))
            else:
                print("❌ 结果整合功能异常: 没有处理任何记录")
                test_results.append(("结果整合功能", False))
        except Exception as e:
            print(f"❌ 结果整合功能测试失败: {e}")
            test_results.append(("结果整合功能", False))
        
        # 测试4：验证CSV输出格式
        print("\n4. 验证CSV输出格式...")
        try:
            # 检查是否生成了CSV文件
            output_dir = "output"
            if os.path.exists(output_dir):
                csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
                if csv_files:
                    print(f"✓ CSV输出格式正常: 生成了 {len(csv_files)} 个CSV文件")
                    for csv_file in csv_files:
                        print(f"  - {csv_file}")
                    test_results.append(("CSV输出格式", True))
                else:
                    print("❌ CSV输出格式异常: 没有生成CSV文件")
                    test_results.append(("CSV输出格式", False))
            else:
                print("⚠️ 输出目录不存在，跳过CSV格式验证")
                test_results.append(("CSV输出格式", False))
        except Exception as e:
            print(f"❌ CSV输出格式验证失败: {e}")
            test_results.append(("CSV输出格式", False))
        
        # 测试5：测试文件重命名功能
        print("\n5. 测试文件重命名功能...")
        try:
            # 检查是否有文件被重命名
            renamed_files = []
            for record in records:
                if record.get("success") and record.get("original_filename") != record.get("new_filename"):
                    renamed_files.append(record)
            
            if renamed_files:
                print(f"✓ 文件重命名功能正常: 重命名了 {len(renamed_files)} 个文件")
                test_results.append(("文件重命名功能", True))
            else:
                print("⚠️ 没有文件被重命名，可能是测试数据问题")
                test_results.append(("文件重命名功能", False))
        except Exception as e:
            print(f"❌ 文件重命名功能测试失败: {e}")
            test_results.append(("文件重命名功能", False))
        
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
    print("测试结果汇总")
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
        print("🎉 步骤4功能测试全部通过！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")
        return False

def main():
    """主函数"""
    print("步骤4：整合装备名称和金额识别结果功能测试模块")
    print("=" * 50)
    print("1. 执行步骤4功能")
    print("2. 测试步骤4功能")
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
                
                step4_integrate_results(auto_mode=False)
            elif choice == '2':
                test_step4_integration()
            else:
                print("无效选择，请输入0-2之间的数字")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()