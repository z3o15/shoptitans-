#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤2：分割原始图片功能测试
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
import cv2
import numpy as np
from PIL import Image, ImageDraw

# 添加项目根目录到Python路径，以便能够导入src模块
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"缺少依赖包: {', '.join(missing_packages)}")
        print("正在安装依赖...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            return True
        except subprocess.CalledProcessError:
            print("依赖安装失败，请手动运行: pip install -r requirements.txt")
            return False
    
    return True

def step2_cut_screenshots(auto_mode=True, auto_clear_old=True, auto_select_all=True, save_original=True, enable_preprocessing=False):
    """步骤2：分割原始图片"""
    # 简化输出，不显示标题和描述
    
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
        print("❌ 未找到游戏截图，请先完成步骤1")
        return False
    
    # 确保输出目录存在
    output_dir = "images/cropped_equipment_original"
    os.makedirs(output_dir, exist_ok=True)
    
    # 检查是否需要清理旧文件（主目录、marker目录、预处理目录和透明背景目录）
    marker_output_dir = "images/cropped_equipment_marker"
    processed_output_dir = "images/cropped_equipment"
    transparent_output_dir = "images/cropped_equipment_transparent"
    existing_files_main = []
    existing_files_marker = []
    existing_files_processed = []
    existing_files_transparent = []
    
    # 检查主目录
    if os.path.exists(output_dir):
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if os.path.isfile(item_path) and item.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                existing_files_main.append(item)
            elif os.path.isdir(item_path):
                existing_files_main.append(item)
    
    # 检查marker目录
    if os.path.exists(marker_output_dir):
        for item in os.listdir(marker_output_dir):
            item_path = os.path.join(marker_output_dir, item)
            if os.path.isfile(item_path) and item.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                existing_files_marker.append(item)
            elif os.path.isdir(item_path):
                existing_files_marker.append(item)
    
    # 检查预处理目录
    if os.path.exists(processed_output_dir):
        for item in os.listdir(processed_output_dir):
            item_path = os.path.join(processed_output_dir, item)
            if os.path.isfile(item_path) and item.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                existing_files_processed.append(item)
            elif os.path.isdir(item_path):
                existing_files_processed.append(item)
    
    # 检查透明背景目录
    if os.path.exists(transparent_output_dir):
        for item in os.listdir(transparent_output_dir):
            item_path = os.path.join(transparent_output_dir, item)
            if os.path.isfile(item_path) and item.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                existing_files_transparent.append(item)
            elif os.path.isdir(item_path):
                existing_files_transparent.append(item)
    
    all_existing_files = existing_files_main + existing_files_marker + existing_files_processed + existing_files_transparent
    
    # 不输出文件检测信息
    
    try:
        # 清理主目录
        if os.path.exists(output_dir):
            for item in os.listdir(output_dir):
                item_path = os.path.join(output_dir, item)
                try:
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f"删除主目录 {item_path} 时出错: {e}")
        
        # 清理marker目录
        if os.path.exists(marker_output_dir):
            for item in os.listdir(marker_output_dir):
                item_path = os.path.join(marker_output_dir, item)
                try:
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f"删除marker目录 {item_path} 时出错: {e}")
        
        # 清理预处理目录
        if os.path.exists(processed_output_dir):
            for item in os.listdir(processed_output_dir):
                item_path = os.path.join(processed_output_dir, item)
                try:
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f"删除预处理目录 {item_path} 时出错: {e}")
        
        # 清理透明背景目录
        if os.path.exists(transparent_output_dir):
            for item in os.listdir(transparent_output_dir):
                item_path = os.path.join(transparent_output_dir, item)
                try:
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f"删除透明背景目录 {item_path} 时出错: {e}")
        
        # 不输出清理信息
    except Exception as e:
        print(f"清理过程中出错: {e}")
    
    # 自动选择所有截图进行切割
    screenshots_to_process = sorted(screenshot_files)
    
    # 执行切割
    try:
        from src.screenshot_cutter import ScreenshotCutter
        from src.config_manager import get_config_manager
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("尝试直接导入模块...")
        try:
            from src.screenshot_cutter import ScreenshotCutter
            from src.config_manager import get_config_manager
        except ImportError as e2:
            print(f"❌ 无法导入必要模块: {e2}")
            return False
    
    # 获取配置管理器和切割参数
    config_manager = get_config_manager()
    cutting_params = config_manager.get_cutting_params()
    
    try:
        total_cropped = 0
        for screenshot in screenshots_to_process:
            screenshot_path = os.path.join(game_screenshots_dir, screenshot)
            
            # 创建时间命名的输出目录
            time_folder = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_folder = os.path.join(output_dir, time_folder)
            os.makedirs(output_folder, exist_ok=True)
            
            # 创建带圆形标记副本的目录
            marker_output_dir = "images/cropped_equipment_marker"
            marker_output_folder = os.path.join(marker_output_dir, time_folder)
            os.makedirs(marker_output_folder, exist_ok=True)
            
            # 使用从配置文件读取的切割参数
            params = cutting_params
            
            current_save_original = False  # 只保存圆形，不保存矩形
            
            # 执行截图切割，保存圆形带填充的图片
            success = ScreenshotCutter.cut_fixed(
                screenshot_path=screenshot_path,
                output_folder=output_folder,
                draw_circle=True,  # 启用圆形绘制功能
                save_original=False,  # 不保存原始矩形，只保存圆形
                marker_output_folder=marker_output_folder,  # 保存带圆形标记的副本到marker目录
                **params
            )
            
            if not success:
                print(f"❌ 切截图 {screenshot} 失败")
                continue
            
            # 重命名文件为顺序编号（01.png, 02.png...）
            try:
                files = os.listdir(output_folder)
                image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
                image_files.sort()  # 确保按顺序处理
                
                for i, filename in enumerate(image_files, 1):
                    old_path = os.path.join(output_folder, filename)
                    # 统一使用JPG格式
                    new_name = f"{i:02d}.jpg"  # JPG格式
                    new_path = os.path.join(output_folder, new_name)
                    
                    if old_path != new_path:  # 避免重命名到同一个文件
                        os.rename(old_path, new_path)
                
                # 不输出重命名信息
                
                # 同时重命名marker目录中的文件
                marker_files = os.listdir(marker_output_folder)
                marker_image_files = [f for f in marker_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) and not f.endswith('_circle.jpg')]
                marker_image_files.sort()  # 确保按顺序处理
                
                for i, filename in enumerate(marker_image_files, 1):
                    old_path = os.path.join(marker_output_folder, filename)
                    # 统一使用JPG格式
                    new_name = f"{i:02d}.jpg"  # JPG格式
                    new_path = os.path.join(marker_output_folder, new_name)
                    
                    if old_path != new_path:  # 避免重命名到同一个文件
                        os.rename(old_path, new_path)
                
                # 不输出重命名信息
            except Exception as e:
                print(f"⚠️ 重命名文件时出错: {e}")
            
            matched_items = []  # 不进行匹配，只切割
            
            # 统计切割的装备数量（只统计矩形版本，不包含"_circle"后缀的文件）
            cropped_items = 0
            for filename in os.listdir(output_folder):
                if (filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) and
                    "_circle" not in filename):
                    cropped_items += 1
            
            total_cropped += cropped_items
        
        # 应用新的透明背景处理流程
        try:
            # 定义输出目录
            transparent_output_dir = "images/cropped_equipment_transparent"
            os.makedirs(transparent_output_dir, exist_ok=True)
            
            print(f"\n共切割出 {total_cropped} 个装备图片已分别保存")
            print("1.带有圆形标记图片（images\\cropped_equipment_marker）")
            print("2.圆形带填充的装备图片(images/cropped_equipment_original)")
            print("3. 透明背景处理开始...(images/cropped_equipment_transparent)")
            print("  - 处理方式: 圆形背景透明化，黑色区域替换为 #39212e")
            
            # 批量处理每个时间目录中的图像
            for time_folder in os.listdir(output_dir):
                folder_path = os.path.join(output_dir, time_folder)
                if os.path.isdir(folder_path):
                    print(f"\n开始处理...")
                    
                    # 获取要处理的文件列表
                    files_to_process = []
                    for filename in os.listdir(folder_path):
                        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                            files_to_process.append(filename)
                    
                    # 显示要处理的文件列表
                    print("    " + "\\".join(files_to_process))
                    
                    # 处理每个文件
                    success_count = 0
                    total_count = 0
                    
                    for filename in files_to_process:
                        input_path = os.path.join(folder_path, filename)
                        output_filename = os.path.splitext(filename)[0] + '.png'  # 输出为PNG格式以支持透明背景
                        output_path = os.path.join(transparent_output_dir, output_filename)
                        
                        try:
                            # 使用新的透明背景处理函数
                            if process_circular_to_transparent(input_path, output_path):
                                success_count += 1
                                print(f"✓ 处理成功: {filename} -> {output_filename}")
                            else:
                                print(f"❌ 处理失败: {filename}")
                        except Exception as e:
                            print(f"❌ 处理失败: {filename}, 错误: {e}")
                        
                        total_count += 1
                    
                    print(f"\n批量处理完成:")
                    print(f"  - 总计: {total_count} 个文件")
                    print(f"  - 成功: {success_count} 个文件")
                    print(f"  - 失败: {total_count - success_count} 个文件")
            
            print(f"\n✓ 透明背景处理完成，处理后的图片已保存到: {transparent_output_dir}")
        except Exception as e:
            print(f"⚠️ 透明背景处理过程中出错: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ 切割过程中出错: {e}")
        return False

def _pad_to_square(image):
    """将图像padding到正方形"""
    height, width = image.shape[:2]
    
    if height == width:
        return image
    
    # 计算需要的padding
    if height > width:
        padding = (height - width) // 2
        padded = cv2.copyMakeBorder(image, 0, 0, padding, padding,
                                 cv2.BORDER_CONSTANT, value=[0, 0, 0])
    else:
        padding = (width - height) // 2
        padded = cv2.copyMakeBorder(image, padding, padding, 0, 0,
                                 cv2.BORDER_CONSTANT, value=[0, 0, 0])
    
    return padded

def process_circular_to_transparent(input_path, output_path):
    """将圆形带填充的装备图片改为透明背景PNG，并将圆形范围内的黑色覆盖区域改为颜色 #39212e"""
    try:
        # 读取图像
        img = cv2.imread(input_path)
        if img is None:
            print(f"❌ 无法读取图像: {input_path}")
            return False
        
        # 转换为RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 获取图像尺寸
        h, w = img_rgb.shape[:2]
        
        # 创建圆形掩码
        center = (w // 2, h // 2)
        radius = min(w, h) // 2
        
        # 创建透明背景的RGBA图像
        rgba_img = np.zeros((h, w, 4), dtype=np.uint8)
        
        # 将非透明区域的RGB值复制过来
        rgba_img[:, :, :3] = img_rgb
        
        # 创建圆形掩码
        y, x = np.ogrid[:h, :w]
        mask = (x - center[0]) ** 2 + (y - center[1]) ** 2 <= radius ** 2
        
        # 应用圆形掩码 - 圆形外设为透明
        rgba_img[~mask, 3] = 0  # 圆形外设为透明
        rgba_img[mask, 3] = 255  # 圆形内设为不透明
        
        # 将圆形范围内的黑色区域替换为 #39212e
        # RGB值: #39212e = (57, 33, 46)
        target_color = np.array([57, 33, 46])
        
        # 找出圆形范围内的黑色或接近黑色的像素
        # 定义黑色的阈值（BGR格式）
        black_threshold = 30
        black_mask = (
            (img_rgb[:, :, 0] < black_threshold) &  # R通道
            (img_rgb[:, :, 1] < black_threshold) &  # G通道
            (img_rgb[:, :, 2] < black_threshold) &  # B通道
            mask  # 只在圆形范围内
        )
        
        # 将黑色区域替换为目标颜色
        rgba_img[black_mask, :3] = target_color
        
        # 转换为PIL图像并保存为PNG
        pil_img = Image.fromarray(rgba_img, 'RGBA')
        pil_img.save(output_path, 'PNG')
        
        return True
    except Exception as e:
        print(f"❌ 处理图像失败: {input_path}, 错误: {e}")
        return False

def test_step2_cutting():
    """测试步骤2：分割图片功能"""
    print("\n" + "=" * 60)
    print("测试步骤2：分割图片功能")
    print("=" * 60)
    print("验证截图切割和标记功能")
    print("-" * 60)
    
    test_results = []
    temp_dir = None
    
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        print(f"创建临时测试目录: {temp_dir}")
        
        # 测试1：创建测试截图
        print("\n1. 创建测试截图...")
        test_screenshot_path = os.path.join(temp_dir, "test_screenshot.png")
        
        # 创建一个包含多个装备的游戏截图
        test_img = Image.new('RGB', (800, 600), color='lightgray')
        draw = ImageDraw.Draw(test_img)
        
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
        
        test_img.save(test_screenshot_path)
        print("✓ 测试截图创建成功")
        test_results.append(("测试截图创建", True))
        
        # 测试2：测试截图分析功能
        print("\n2. 测试截图分析功能...")
        try:
            from src.screenshot_cutter import ScreenshotCutter
            cutter = ScreenshotCutter()
            
            analysis = cutter.analyze_screenshot(test_screenshot_path)
            if analysis and 'image_size' in analysis:
                print(f"✓ 截图分析成功: {analysis['image_size']}")
                test_results.append(("截图分析功能", True))
            else:
                print("❌ 截图分析失败")
                test_results.append(("截图分析功能", False))
        except ImportError as e:
            print(f"❌ 导入截图切割器失败: {e}")
            test_results.append(("截图分析功能", False))
        
        # 测试3：测试固定坐标切割
        print("\n3. 测试固定坐标切割...")
        try:
            output_folder = os.path.join(temp_dir, "cut_output")
            os.makedirs(output_folder, exist_ok=True)
            
            success = cutter.cut_fixed(
                screenshot_path=test_screenshot_path,
                output_folder=output_folder,
                grid=(6, 2),
                item_width=100,
                item_height=120,
                margin_left=50,
                margin_top=350,
                draw_circle=True
            )
            
            if success:
                cut_files = os.listdir(output_folder)
                if len(cut_files) == 12:  # 6列 × 2行 = 12个装备
                    print(f"✓ 固定坐标切割成功: 切割了 {len(cut_files)} 个装备")
                    test_results.append(("固定坐标切割", True))
                else:
                    print(f"❌ 固定坐标切割数量不正确: {len(cut_files)} 个装备")
                    test_results.append(("固定坐标切割", False))
            else:
                print("❌ 固定坐标切割失败")
                test_results.append(("固定坐标切割", False))
        except Exception as e:
            print(f"❌ 固定坐标切割测试失败: {e}")
            test_results.append(("固定坐标切割", False))
        
        # 测试4：测试圆形标记功能
        print("\n4. 测试圆形标记功能...")
        try:
            marker_files = [f for f in os.listdir(output_folder) if f.endswith('_circle.jpg')]
            if len(marker_files) == 12:
                print(f"✓ 圆形标记功能正常: 生成了 {len(marker_files)} 个标记文件")
                test_results.append(("圆形标记功能", True))
            else:
                print(f"❌ 圆形标记功能异常: 只生成了 {len(marker_files)} 个标记文件")
                test_results.append(("圆形标记功能", False))
        except Exception as e:
            print(f"❌ 圆形标记功能测试失败: {e}")
            test_results.append(("圆形标记功能", False))
        
        # 测试5：测试文件重命名功能
        print("\n5. 测试文件重命名功能...")
        try:
            # 重命名文件为顺序编号（01.png, 02.png...）
            files = os.listdir(output_folder)
            image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) and not f.endswith('_circle.jpg')]
            image_files.sort()  # 确保按顺序处理
            
            for i, filename in enumerate(image_files, 1):
                old_path = os.path.join(output_folder, filename)
                new_name = f"{i:02d}.jpg"  # 格式化为两位数，如01.jpg, 02.jpg
                new_path = os.path.join(output_folder, new_name)
                
                if old_path != new_path:  # 避免重命名到同一个文件
                    os.rename(old_path, new_path)
            
            renamed_files = [f for f in os.listdir(output_folder) if f.lower().endswith(('.jpg', '.jpeg')) and not f.endswith('_circle.jpg')]
            if len(renamed_files) == 12 and all(f.startswith(('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12')) for f in renamed_files):
                print(f"✓ 文件重命名功能正常: 成功重命名 {len(renamed_files)} 个文件")
                test_results.append(("文件重命名功能", True))
            else:
                print(f"❌ 文件重命名功能异常: 重命名后文件数量或格式不正确")
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
        print("🎉 步骤2功能测试全部通过！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")
        return False

def main():
    """主函数"""
    # 简化输出，不显示标题和描述
    
    try:
        # 自动执行步骤2功能
        success = step2_cut_screenshots(auto_mode=True)
        
        if not success:
            print("\n❌ 步骤2自动化执行失败！")
            
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()