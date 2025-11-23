#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成带圆形标记的原图注释功能测试
从 enhanced_recognition_start.py 提取的独立测试模块
专门用于测试生成带圆形标记的原图注释功能
"""

import os
import sys
import subprocess
import tempfile
import shutil
from datetime import datetime
import time
import json
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

def test_generate_annotated_screenshots():
    """测试生成带圆形标记的原图注释功能"""
    print("\n" + "=" * 60)
    print("测试生成带圆形标记的原图注释功能")
    print("=" * 60)
    print("验证注释生成和可视化功能")
    print("-" * 60)
    
    test_results = []
    temp_dir = None
    
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        print(f"创建临时测试目录: {temp_dir}")
        
        # 创建测试目录结构
        screenshots_dir = os.path.join(temp_dir, "screenshots")
        cropped_dir = os.path.join(temp_dir, "cropped")
        base_dir = os.path.join(temp_dir, "base")
        output_dir = os.path.join(temp_dir, "output")
        
        os.makedirs(screenshots_dir, exist_ok=True)
        os.makedirs(cropped_dir, exist_ok=True)
        os.makedirs(base_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # 测试1：创建测试游戏截图
        print("\n1. 创建测试游戏截图...")
        test_screenshot = Image.new('RGB', (800, 600), color='lightgray')
        draw = ImageDraw.Draw(test_screenshot)
        
        # 添加背景网格
        for i in range(0, 800, 50):
            draw.line([(i, 0), (i, 600)], fill='gray', width=1)
        for i in range(0, 600, 50):
            draw.line([(0, i), (800, i)], fill='gray', width=1)
        
        # 添加多个装备（6列2行）
        equipment_positions = []
        for row in range(2):
            for col in range(6):
                x = 50 + col * 120
                y = 350 + row * 140
                
                # 创建不同颜色的装备
                colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
                color = colors[col % len(colors)]
                
                # 绘制装备
                draw.rectangle([x, y, x+100, y+120], fill=color, outline='black', width=2)
                
                equipment_positions.append((x, y, x+100, y+120))
        
        test_screenshot_path = os.path.join(screenshots_dir, "test_screenshot.png")
        test_screenshot.save(test_screenshot_path)
        print("✓ 测试游戏截图创建成功")
        test_results.append(("测试游戏截图创建", True))
        
        # 测试2：创建测试基准装备
        print("\n2. 创建测试基准装备...")
        base_img = Image.new('RGB', (50, 50), color='white')
        draw = ImageDraw.Draw(base_img)
        draw.rectangle([10, 10, 40, 40], fill='red')
        base_img_path = os.path.join(base_dir, "test_base_equipment.webp")
        base_img.save(base_img_path)
        print("✓ 测试基准装备创建成功")
        test_results.append(("测试基准装备创建", True))
        
        # 测试3：创建测试切割装备
        print("\n3. 创建测试切割装备...")
        colors = ['red', 'blue', 'green', 'yellow', 'purple']
        for i, color in enumerate(colors):
            item_img = Image.new('RGB', (50, 50), color='white')
            draw = ImageDraw.Draw(item_img)
            draw.rectangle([10, 10, 40, 40], fill=color)
            item_img.save(os.path.join(cropped_dir, f"test_item_{i}.png"))
        
        print(f"✓ 测试切割装备创建成功: {len(colors)} 个")
        test_results.append(("测试切割装备创建", True))
        
        # 测试4：测试图像注释器功能
        print("\n4. 测试图像注释器功能...")
        try:
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
            from image_annotator import ImageAnnotator
            from config_manager import get_config_manager
            
            # 初始化配置管理器
            config_manager = get_config_manager()
            
            # 创建注释器
            annotator = ImageAnnotator(
                circle_color=config_manager.get_circle_color(),
                circle_width=config_manager.get_circle_width(),
                font_size=config_manager.get_font_size(),
                show_similarity_text=config_manager.get_show_similarity_text()
            )
            
            print("✓ 图像注释器初始化成功")
            test_results.append(("图像注释器初始化", True))
            
            # 测试注释配置
            print(f"  - 圆形颜色: {config_manager.get_circle_color()}")
            print(f"  - 圆形宽度: {config_manager.get_circle_width()}像素")
            print(f"  - 字体大小: {config_manager.get_font_size()}像素")
            print(f"  - 显示相似度: {'是' if config_manager.get_show_similarity_text() else '否'}")
            
        except ImportError as e:
            print(f"❌ 导入图像注释器失败: {e}")
            test_results.append(("图像注释器初始化", False))
        except Exception as e:
            print(f"❌ 图像注释器初始化失败: {e}")
            test_results.append(("图像注释器初始化", False))
        
        # 测试5：测试注释生成功能
        print("\n5. 测试注释生成功能...")
        try:
            # 创建模拟匹配结果
            matched_items = [
                ("test_item_0.png", 95.5),
                ("test_item_1.png", 88.2),
                ("test_item_2.png", 92.1),
            ]
            
            # 获取切割参数
            cutting_params = {
                'grid': (6, 2),
                'item_width': 100,
                'item_height': 120,
                'margin_left': 50,
                'margin_top': 350,
                'h_spacing': 15,
                'v_spacing': 20
            }
            
            # 生成注释图像
            annotated_path = annotator.annotate_screenshot_with_matches(
                screenshot_path=test_screenshot_path,
                matched_items=matched_items,
                cutting_params=cutting_params
            )
            
            if os.path.exists(annotated_path):
                print("✓ 注释图像生成成功")
                print(f"  输出路径: {annotated_path}")
                test_results.append(("注释图像生成", True))
            else:
                print("❌ 注释图像生成失败")
                test_results.append(("注释图像生成", False))
                
        except Exception as e:
            print(f"❌ 注释图像生成失败: {e}")
            test_results.append(("注释图像生成", False))
        
        # 测试6：测试注释报告生成
        print("\n6. 测试注释报告生成...")
        try:
            # 创建注释报告
            report_path = annotator.create_annotation_report(
                screenshot_path=test_screenshot_path,
                matched_items=matched_items,
                annotated_image_path=annotated_path,
                output_dir=output_dir
            )
            
            if os.path.exists(report_path):
                print("✓ 注释报告生成成功")
                print(f"  报告路径: {report_path}")
                test_results.append(("注释报告生成", True))
            else:
                print("❌ 注释报告生成失败")
                test_results.append(("注释报告生成", False))
                
        except Exception as e:
            print(f"❌ 注释报告生成失败: {e}")
            test_results.append(("注释报告生成", False))
        
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
    print("生成带圆形标记的原图注释测试结果汇总")
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
        print("🎉 生成带圆形标记的原图注释功能测试全部通过！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")
        return False

def generate_annotated_screenshots():
    """生成带圆形标记的原图注释"""
    print("\n" + "=" * 60)
    print("生成带圆形标记的原图注释")
    print("=" * 60)
    print("此功能将在原始游戏截图上标注匹配的装备位置")
    print("-" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 检查游戏截图
    game_screenshots_dir = "images/game_screenshots"
    screenshot_files = []
    for filename in os.listdir(game_screenshots_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            screenshot_files.append(filename)
    
    if not screenshot_files:
        print("❌ 未找到游戏截图")
        return False
    
    # 选择截图
    print(f"找到 {len(screenshot_files)} 个游戏截图，选择要注释的截图:")
    for i, filename in enumerate(sorted(screenshot_files), 1):
        print(f"  {i}. {filename}")
    
    print(f"\n请输入截图编号 (1-{len(screenshot_files)})，或输入 'all' 注释所有截图:")
    choice = input().strip()
    
    screenshots_to_process = []
    if choice.lower() == 'all':
        screenshots_to_process = sorted(screenshot_files)
    else:
        try:
            index = int(choice) - 1
            if 0 <= index < len(screenshot_files):
                screenshots_to_process = [sorted(screenshot_files)[index]]
            else:
                print("❌ 无效的截图编号")
                return False
        except ValueError:
            print("❌ 无效的输入")
            return False
    
    # 检查是否有匹配结果
    cropped_equipment_dir = "images/cropped_equipment"
    cropped_files = []
    
    # 检查是否有时间命名的子目录
    subdirs = []
    for item in os.listdir(cropped_equipment_dir):
        item_path = os.path.join(cropped_equipment_dir, item)
        if os.path.isdir(item_path) and item.replace('_', '').replace(':', '').isdigit():
            subdirs.append(item)
    
    if subdirs:
        # 如果有时间命名的子目录，使用最新的一个
        latest_dir = sorted(subdirs)[-1]
        latest_dir_path = os.path.join(cropped_equipment_dir, latest_dir)
        print(f"✓ 找到时间目录: {latest_dir}")
        
        for filename in os.listdir(latest_dir_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                cropped_files.append(os.path.join(latest_dir, filename))
        
        # 更新切割装备目录为最新的时间目录
        cropped_equipment_dir = latest_dir_path
    else:
        # 如果没有时间命名的子目录，直接在主目录中查找
        for filename in os.listdir(cropped_equipment_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                cropped_files.append(filename)
    
    if not cropped_files:
        print("❌ 未找到切割装备图片，请先执行步骤2和步骤3")
        return False
    
    # 选择基准装备
    base_equipment_dir = "images/base_equipment"
    base_image_files = []
    for filename in os.listdir(base_equipment_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            base_image_files.append(filename)
    
    if not base_image_files:
        print("❌ 未找到基准装备图片")
        return False
    
    print(f"找到 {len(base_image_files)} 个基准装备:")
    for i, filename in enumerate(sorted(base_image_files), 1):
        print(f"  {i}. {filename}")
    
    print(f"\n请输入基准装备编号 (1-{len(base_image_files)}):")
    try:
        base_index = int(input().strip()) - 1
        if 0 <= base_index < len(base_image_files):
            base_image = sorted(base_image_files)[base_index]
        else:
            print("❌ 无效的基准装备编号")
            return False
    except ValueError:
        print("❌ 无效的输入")
        return False
    
    base_image_path = os.path.join(base_equipment_dir, base_image)
    
    # 设置匹配阈值
    print(f"\n当前默认匹配阈值为 80%")
    print("是否使用自定义阈值？(y/n)")
    use_custom_threshold = input().strip().lower() == 'y'
    
    threshold = 80.0
    if use_custom_threshold:
        try:
            threshold = float(input("请输入匹配阈值 (0-100): ").strip())
            if not 0 <= threshold <= 100:
                print("❌ 阈值必须在0-100之间，将使用默认值80%")
                threshold = 80.0
        except ValueError:
            print("❌ 无效的阈值，将使用默认值80%")
            threshold = 80.0
    
    # 执行匹配和注释
    try:
        try:
            from src.main import EquipmentMatcher
            from src.config_manager import get_config_manager
            from src.image_annotator import ImageAnnotator
        except ImportError as e:
            print(f"❌ 导入错误: {e}")
            print("尝试直接导入模块...")
            try:
                import sys
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
                from main import EquipmentMatcher
                from config_manager import get_config_manager
                from image_annotator import ImageAnnotator
            except ImportError as e2:
                print(f"❌ 无法导入必要模块: {e2}")
                return False
        
        # 获取配置管理器
        config_manager = get_config_manager()
        
        # 检查注释功能是否启用
        if not config_manager.get_annotation_enabled():
            print("❌ 注释功能未启用，请在配置文件中启用")
            return False
        
        # 创建匹配器
        matcher = EquipmentMatcher(config_manager)
        
        # 从配置创建注释器
        annotator = ImageAnnotator(
            circle_color=config_manager.get_circle_color(),
            circle_width=config_manager.get_circle_width(),
            font_size=config_manager.get_font_size(),
            show_similarity_text=config_manager.get_show_similarity_text()
        )
        
        print(f"使用注释配置:")
        print(f"  - 圆形颜色: {config_manager.get_circle_color()}")
        print(f"  - 圆形宽度: {config_manager.get_circle_width()}像素")
        print(f"  - 字体大小: {config_manager.get_font_size()}像素")
        print(f"  - 显示相似度: {'是' if config_manager.get_show_similarity_text() else '否'}")
        
        # 执行匹配
        print(f"\n开始匹配，使用基准装备: {base_image}")
        print(f"匹配阈值: {threshold}%")
        print("-" * 60)
        
        matched_items = matcher.batch_compare(
            base_img_path=base_image_path,
            crop_folder=cropped_equipment_dir,
            threshold=threshold
        )
        
        if not matched_items:
            print("❌ 未找到匹配的装备，无法生成注释")
            return False
        
        print(f"\n✅ 找到 {len(matched_items)} 个匹配项")
        
        # 从配置文件获取切割参数（与step2_cut_screenshots中的参数保持一致）
        cutting_params = config_manager.get_cutting_params()
        print(f"使用切割参数: {cutting_params}")
        
        # 为每个截图生成注释
        annotated_images = []
        for screenshot in screenshots_to_process:
            screenshot_path = os.path.join(game_screenshots_dir, screenshot)
            print(f"\n正在注释截图: {screenshot}")
            
            # 生成注释图像
            annotated_path = annotator.annotate_screenshot_with_matches(
                screenshot_path=screenshot_path,
                matched_items=matched_items,
                cutting_params=cutting_params
            )
            
            annotated_images.append(annotated_path)
            
            # 创建注释报告
            report_path = annotator.create_annotation_report(
                screenshot_path=screenshot_path,
                matched_items=matched_items,
                annotated_image_path=annotated_path,
                output_dir="recognition_logs"
            )
        
        print(f"\n✅ 注释完成！共生成 {len(annotated_images)} 个注释图像:")
        for i, path in enumerate(annotated_images, 1):
            print(f"  {i}. {path}")
        
        print("\n📝 注释说明:")
        print("- 红色圆形标记表示匹配的装备位置")
        print("- 圆形上方的数字表示匹配相似度百分比")
        print("- 详细报告保存在 recognition_logs 目录中")
        
        return True
        
    except Exception as e:
        print(f"❌ 注释过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("生成带圆形标记的原图注释功能模块")
    print("=" * 50)
    print("1. 生成带圆形标记的原图注释")
    print("2. 测试生成带圆形标记的原图注释功能")
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
                
                generate_annotated_screenshots()
            elif choice == '2':
                test_generate_annotated_screenshots()
            else:
                print("无效选择，请输入0-2之间的数字")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()