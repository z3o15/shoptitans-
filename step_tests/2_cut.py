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
                
                # 合并掩码
                mask_combined = cv2.bitwise_or(mask_bg, mask_light_purple)
                
                # 应用轻微高斯模糊
                mask_combined = cv2.GaussianBlur(mask_combined, (3, 3), 0.1)
                
                # 二值化
                _, mask_combined = cv2.threshold(mask_combined, 200, 255, cv2.THRESH_BINARY)
                
                return mask_combined
            except Exception as e:
                print(f"[ERROR] 背景掩码创建失败: {e}")
                return np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)

# 导入新的统一日志管理器
try:
    from src.unified_logger import get_unified_logger
    LOGGER_AVAILABLE = True
except ImportError:
    try:
        from unified_logger import get_unified_logger
        LOGGER_AVAILABLE = True
    except ImportError:
        LOGGER_AVAILABLE = False
        print("⚠️ 统一日志管理器不可用，使用默认输出")

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

def step2_cut_screenshots(auto_mode=True, auto_clear_old=True, auto_select_all=True, save_original=True, enable_preprocessing=False, enable_matching=False):
    """步骤2：分割原始图片 - 仅负责图片切割功能，不涉及匹配和OCR"""
    # 初始化日志系统
    if LOGGER_AVAILABLE:
        logger = get_unified_logger()
        logger.start_step("step2_cut", "图片裁剪")
    else:
        print("开始图片裁剪步骤")
    
    # 检查依赖
    if not check_dependencies():
        if LOGGER_AVAILABLE:
            logger.end_step("step2_cut", "失败")
        return False
    
    # 检查游戏截图
    game_screenshots_dir = "images/game_screenshots"
    screenshot_files = []
    for filename in os.listdir(game_screenshots_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            screenshot_files.append(filename)
    
    if not screenshot_files:
        if LOGGER_AVAILABLE:
            logger.log_error("未找到游戏截图，请先完成步骤1")
            logger.end_step("step2_cut", "失败")
        else:
            print("❌ 未找到游戏截图，请先完成步骤1")
        return False
    
    if LOGGER_AVAILABLE:
        logger.log_info(f"找到 {len(screenshot_files)} 个游戏截图文件")
    
    # 确保输出目录存在
    if LOGGER_AVAILABLE:
        output_dir = logger.get_step_dir("step2_cut") / "images"
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = "images/cropped_equipment_original"
        os.makedirs(output_dir, exist_ok=True)
    
    # 检查是否需要清理旧文件（仅清理步骤2相关的目录）
    if LOGGER_AVAILABLE:
        marker_output_dir = logger.get_step_dir("step2_cut") / "images"
        transparent_output_dir = logger.get_step_dir("step2_cut") / "images"
    else:
        marker_output_dir = "images/cropped_equipment_marker"
        transparent_output_dir = "images/cropped_equipment_transparent"
    existing_files_main = []
    existing_files_marker = []
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
    
    # 检查透明背景目录
    if os.path.exists(transparent_output_dir):
        for item in os.listdir(transparent_output_dir):
            item_path = os.path.join(transparent_output_dir, item)
            if os.path.isfile(item_path) and item.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                existing_files_transparent.append(item)
            elif os.path.isdir(item_path):
                existing_files_transparent.append(item)
    
    all_existing_files = existing_files_main + existing_files_marker + existing_files_transparent
    
    if LOGGER_AVAILABLE:
        logger.log_info(f"检测到 {len(all_existing_files)} 个已存在文件，将进行清理")
    
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
                    if LOGGER_AVAILABLE:
                        logger.log_warning(f"删除主目录 {item_path} 时出错: {e}")
                    else:
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
                    if LOGGER_AVAILABLE:
                        logger.log_warning(f"删除marker目录 {item_path} 时出错: {e}")
                    else:
                        print(f"删除marker目录 {item_path} 时出错: {e}")
        
        # 注释掉预处理目录的清理，这不应该由步骤2负责
        # # 清理预处理目录
        # if os.path.exists(processed_output_dir):
        #     for item in os.listdir(processed_output_dir):
        #         item_path = os.path.join(processed_output_dir, item)
        #         try:
        #             if os.path.isfile(item_path):
        #                 os.unlink(item_path)
        #             elif os.path.isdir(item_path):
        #                 shutil.rmtree(item_path)
        #         except Exception as e:
        #             if LOGGER_AVAILABLE:
        #                 logger.log_warning(f"删除预处理目录 {item_path} 时出错: {e}")
        #             else:
        #                 print(f"删除预处理目录 {item_path} 时出错: {e}")
        
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
                    if LOGGER_AVAILABLE:
                        logger.log_warning(f"删除透明背景目录 {item_path} 时出错: {e}")
                    else:
                        print(f"删除透明背景目录 {item_path} 时出错: {e}")
        
        if LOGGER_AVAILABLE:
            logger.log_info("清理完成")
    except Exception as e:
        if LOGGER_AVAILABLE:
            logger.log_error(f"清理过程中出错: {e}")
        else:
            print(f"清理过程中出错: {e}")
    
    # 自动选择所有截图进行切割
    screenshots_to_process = sorted(screenshot_files)
    if LOGGER_AVAILABLE:
        logger.log_info(f"将处理 {len(screenshots_to_process)} 个截图文件")
    
    # 执行切割
    try:
        from src.core.screenshot_cutter import ScreenshotCutter
        from src.config.config_manager import get_config_manager
    except ImportError as e:
        if LOGGER_AVAILABLE:
            logger.log_error(f"导入错误: {e}")
            logger.log_info("尝试直接导入模块...")
        else:
            print(f"❌ 导入错误: {e}")
            print("尝试直接导入模块...")
        try:
            from src.core.screenshot_cutter import ScreenshotCutter
            from src.config.config_manager import get_config_manager
        except ImportError as e2:
            if LOGGER_AVAILABLE:
                logger.log_error(f"无法导入必要模块: {e2}")
                logger.end_step("step2_cut", "失败")
            else:
                print(f"❌ 无法导入必要模块: {e2}")
            return False
    
    # 获取配置管理器和切割参数
    config_manager = get_config_manager()
    cutting_params = config_manager.get_cutting_params()
    
    try:
        total_cropped = 0
        processed_count = 0
        
        for screenshot in screenshots_to_process:
            screenshot_path = os.path.join(game_screenshots_dir, screenshot)
            
            # 创建时间命名的输出目录
            time_folder = datetime.now().strftime('%Y%m%d_%H%M%S')
            if LOGGER_AVAILABLE:
                output_folder = logger.get_step_dir("step2_cut") / "images" / time_folder
                output_folder.mkdir(parents=True, exist_ok=True)
                marker_output_folder = logger.get_step_dir("step2_cut") / "images" / f"marker_{time_folder}"
                marker_output_folder.mkdir(parents=True, exist_ok=True)
            else:
                output_folder = os.path.join(output_dir, time_folder)
                os.makedirs(output_folder, exist_ok=True)
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
                if LOGGER_AVAILABLE:
                    logger.log_error(f"切截图 {screenshot} 失败")
                    logger.update_stats("step2_cut", error_items=1)
                else:
                    print(f"❌ 切截图 {screenshot} 失败")
                continue
            
            processed_count += 1
            if LOGGER_AVAILABLE:
                logger.update_stats("step2_cut", processed_items=1, success_items=1)
            
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
                if LOGGER_AVAILABLE:
                    logger.log_warning(f"重命名文件时出错: {e}")
                else:
                    print(f"⚠️ 重命名文件时出错: {e}")
            
            matched_items = []  # 不进行匹配，只切割
            
            # 统计切割的装备数量（只统计矩形版本，不包含"_circle"后缀的文件）
            cropped_items = 0
            for filename in os.listdir(output_folder):
                if (filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) and
                    "_circle" not in filename):
                    cropped_items += 1
            
            total_cropped += cropped_items
            if LOGGER_AVAILABLE:
                logger.log_info(f"截图 {screenshot} 切割完成，生成 {cropped_items} 个装备图片")
        
        # 应用新的透明背景处理流程
        try:
            # 定义输出目录
            if LOGGER_AVAILABLE:
                transparent_output_dir = logger.get_step_dir("step2_cut") / "images"
                txt_output_dir = logger.get_step_dir("step2_cut") / "txt"
                txt_output_dir.mkdir(parents=True, exist_ok=True)
            else:
                transparent_output_dir = "images/cropped_equipment_transparent"
                os.makedirs(transparent_output_dir, exist_ok=True)
            
            if LOGGER_AVAILABLE:
                logger.log_info(f"共切割出 {total_cropped} 个装备图片")
                logger.log_info("开始透明背景处理")
                logger.log_info("处理方式: 圆形背景透明化，黑色区域替换为 #39212e")
            else:
                print(f"\n共切割出 {total_cropped} 个装备图片已分别保存")
                print("1.带有圆形标记图片（images\\cropped_equipment_marker）")
                print("2.圆形带填充的装备图片(images/cropped_equipment_original)")
                print("3. 透明背景处理开始...(images/cropped_equipment_transparent)")
                print("  - 处理方式: 圆形背景透明化，黑色区域替换为 #39212e")
            
            # 批量处理每个时间目录中的图像
            for time_folder in os.listdir(output_dir):
                folder_path = os.path.join(output_dir, time_folder)
                if os.path.isdir(folder_path):
                    if LOGGER_AVAILABLE:
                        logger.log_info(f"处理目录: {time_folder}")
                    else:
                        print(f"\n开始处理...")
                    
                    # 获取要处理的文件列表
                    files_to_process = []
                    for filename in os.listdir(folder_path):
                        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                            files_to_process.append(filename)
                    
                    # 显示要处理的文件列表
                    if LOGGER_AVAILABLE:
                        logger.log_info(f"待处理文件: {', '.join(files_to_process)}")
                    else:
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
                                if LOGGER_AVAILABLE:
                                    logger.log_success(f"处理成功: {filename} -> {output_filename}")
                                    logger.update_stats("step2_cut", success_items=1)
                                else:
                                    print(f"✓ 处理成功: {filename} -> {output_filename}")
                            else:
                                if LOGGER_AVAILABLE:
                                    logger.log_error(f"处理失败: {filename}")
                                    logger.update_stats("step2_cut", error_items=1)
                                else:
                                    print(f"❌ 处理失败: {filename}")
                        except Exception as e:
                            if LOGGER_AVAILABLE:
                                logger.log_error(f"处理失败: {filename}, 错误: {e}")
                                logger.update_stats("step2_cut", error_items=1)
                            else:
                                print(f"❌ 处理失败: {filename}, 错误: {e}")
                        
                        total_count += 1
                    
                    if LOGGER_AVAILABLE:
                        logger.log_info(f"批量处理完成: 总计 {total_count} 个文件，成功 {success_count} 个文件，失败 {total_count - success_count} 个文件")
                    else:
                        print(f"\n批量处理完成:")
                        print(f"  - 总计: {total_count} 个文件")
                        print(f"  - 成功: {success_count} 个文件")
                        print(f"  - 失败: {total_count - success_count} 个文件")
            
            if LOGGER_AVAILABLE:
                logger.log_success(f"透明背景处理完成，处理后的图片已保存到: {transparent_output_dir}")
            else:
                print(f"\n✓ 透明背景处理完成，处理后的图片已保存到: {transparent_output_dir}")
        except Exception as e:
            print(f"⚠️ 透明背景处理过程中出错: {e}")
            import traceback
            traceback.print_exc()
        
        # 注释掉图片匹配功能，这属于步骤3的功能
        # 执行图片匹配（如果启用）
        # if enable_matching:
        #     try:
        #         if LOGGER_AVAILABLE:
        #             logger.log_info("开始执行装备图片匹配")
        #         else:
        #             print(f"\n开始执行装备图片匹配...")
        #
        #         # 设置路径
        #         base_dir = "images/base_equipment_new"
        #         compare_dir = transparent_output_dir  # 使用透明背景处理后的图片
        #
        #         if LOGGER_AVAILABLE:
        #             output_dir = logger.get_step_dir("step2_cut") / "images"
        #         else:
        #             output_dir = "images/matching_results"
        #
        #         # 执行匹配
        #         match_results = match_equipment_images(base_dir, compare_dir, str(output_dir))
        #
        #         if match_results:
        #             if LOGGER_AVAILABLE:
        #                 logger.log_success(f"图片匹配完成，共处理 {len(match_results)} 次匹配")
        #                 logger.log_info(f"基准图像: {len(set(r['base_image'] for r in match_results))} 个")
        #                 logger.log_info(f"对比图像: {len(set(r['compare_image'] for r in match_results))} 个")
        #                 logger.log_info(f"结果已保存到: {output_dir}")
        #             else:
        #                 print(f"\n✓ 图片匹配完成，共处理 {len(match_results)} 次匹配")
        #                 print(f"  - 基准图像: {len(set(r['base_image'] for r in match_results))} 个")
        #                 print(f"  - 对比图像: {len(set(r['compare_image'] for r in match_results))} 个")
        #                 print(f"  - 结果已保存到: {output_dir}")
        #         else:
        #             if LOGGER_AVAILABLE:
        #                 logger.log_warning("图片匹配未产生结果")
        #             else:
        #                 print(f"\n⚠️ 图片匹配未产生结果")
        #
        #     except Exception as e:
        #         if LOGGER_AVAILABLE:
        #             logger.log_error(f"图片匹配过程中出错: {e}")
        #         else:
        #             print(f"⚠️ 图片匹配过程中出错: {e}")
        #         import traceback
        #         traceback.print_exc()
        
        # 生成处理报告
        if LOGGER_AVAILABLE:
            stats = logger.get_step_stats("step2_cut")
            additional_info = {
                "files_processed": screenshots_to_process,
                "total_cropped": total_cropped,
                "output_directories": [str(output_dir), str(transparent_output_dir)]
            }
            
            report_generator.generate_step_report("step2_cut", stats, additional_info)
            logger.end_step("step2_cut", "完成")
            
            logger.log_info(f"Total images: {len(screenshots_to_process)}, Processed: {processed_count}")
        
        return True
        
    except Exception as e:
        if LOGGER_AVAILABLE:
            logger.log_error(f"切割过程中出错: {e}")
            logger.end_step("step2_cut", "失败")
        else:
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

# 注释掉匹配相关的函数，这些属于步骤3的功能
# 以下函数从 template_matching_test.py 中提取，用于图片匹配

# def log_message(tag, message):
#     """统一日志输出格式"""
#     if LOGGER_AVAILABLE:
#         logger = get_step_logger()
#         if tag == "ERROR":
#             logger.log_error(message)
#         elif tag == "WARNING":
#             logger.log_warning(message)
#         elif tag == "RESULT":
#             logger.log_info(message)
#         else:
#             logger.log_info(f"[{tag}] {message}")
#     else:
#         print(f"[{tag}] {message}")

# def load_image(image_path):
#     """加载图像并处理透明通道"""
#     try:
#         # 使用PIL加载图像以正确处理透明通道
#         img = Image.open(image_path)
#
#         # 如果是RGBA图像，转换为RGB（白色背景）
#         if img.mode == 'RGBA':
#             background = Image.new('RGB', img.size, (255, 255, 255))
#             background.paste(img, mask=img.split()[-1])
#             img = background
#
#         # 转换为numpy数组
#         img_array = np.array(img)
#
#         # 转换为BGR格式（OpenCV格式）
#         if len(img_array.shape) == 3 and img_array.shape[2] == 3:
#             img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
#
#         return img_array
#     except Exception as e:
#         log_message("ERROR", f"加载图像失败 {image_path}: {e}")
#         return None

# def template_matching(template, scene):
#     """
#     使用cv2.matchTemplate进行模板匹配
#     返回匹配相似度（0-100%）
#     """
#     try:
#         # 确保模板不大于场景
#         if template.shape[0] > scene.shape[0] or template.shape[1] > scene.shape[1]:
#             # 如果模板大于场景，调整场景大小
#             scene = cv2.resize(scene, (template.shape[1], template.shape[0]))
#
#         # 转换为灰度图像进行匹配
#         if len(template.shape) == 3:
#             template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
#         else:
#             template_gray = template
#
#         if len(scene.shape) == 3:
#             scene_gray = cv2.cvtColor(scene, cv2.COLOR_BGR2GRAY)
#         else:
#             scene_gray = scene
#
#         # 使用多种匹配方法并取最佳结果
#         methods = [
#             cv2.TM_CCOEFF_NORMED,
#             cv2.TM_CCORR_NORMED,
#             cv2.TM_SQDIFF_NORMED
#         ]
#
#         best_score = 0
#         best_method = ""
#
#         for method in methods:
#             result = cv2.matchTemplate(scene_gray, template_gray, method)
#
#             if method == cv2.TM_SQDIFF_NORMED:
#                 # 对于SQDIFF，值越小越好
#                 min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
#                 score = (1 - min_val) * 100  # 转换为0-100%
#                 if score > best_score:
#                     best_score = score
#                     best_method = "SQDIFF_NORMED"
#             else:
#                 # 对于其他方法，值越大越好
#                 min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
#                 score = max_val * 100  # 转换为0-100%
#                 if score > best_score:
#                     best_score = score
#                     best_method = "CCOEFF_NORMED" if method == cv2.TM_CCOEFF_NORMED else "CCORR_NORMED"
#
#         return best_score, best_method
#     except Exception as e:
#         log_message("ERROR", f"模板匹配失败: {e}")
#         return 0, ""

# # create_background_mask函数已移至src/utils/background_mask.py，现在从那里导入

# def apply_mask_to_image(image, mask):
#     """
#     将掩码应用到图像，生成掩码后的图像
#     背景区域变为白色，前景区域保持原色
#
#     掩码逻辑（与create_background_mask一致）：
#     - 255值: 背景区域(深紫色39212e、浅紫色20904f71及其变化范围)
#     - 0值: 前景区域(装备)
#     """
#     try:
#         # 创建白色背景
#         white_bg = np.ones_like(image) * 255
#
#         # 确保掩码是二值的（0和255）
#         mask_binary = np.where(mask > 127, 255, 0).astype(np.uint8)
#
#         # 将前景区域复制到白色背景上
#         # 掩码中255是背景，0是前景（与create_background_mask的输出一致）
#         result = np.where(mask_binary[:, :, np.newaxis] == 0, image, white_bg)
#
#         return result
#     except Exception as e:
#         log_message("ERROR", f"掩码应用失败: {e}")
#         return image

# def calculate_color_similarity_with_euclidean(img1, img2):
#     """
#     使用LAB色彩空间欧氏距离计算两张图片的颜色相似度
#     使用指定的掩码策略排除背景色，只计算装备区域的颜色相似度
#     LAB色彩空间更接近人类视觉感知
#     返回相似度（0-1）
#     """
#     try:
#         # 调整图像大小为相同尺寸
#         target_size = (100, 100)  # 使用较小的尺寸提高性能
#         img1_resized = cv2.resize(img1, target_size)
#         img2_resized = cv2.resize(img2, target_size)
#
#         # 使用指定的掩码策略
#         log_message("DEBUG", "使用掩码策略计算颜色相似度（背景色39212e、浅紫色20904f71）")
#
#         # 创建背景掩码（深紫色39212e和浅紫色20904f71）
#         bg_mask1 = create_background_mask(img1_resized)
#         bg_mask2 = create_background_mask(img2_resized)
#
#         # 创建装备区域掩码（非背景区域）
#         equipment_mask1 = cv2.bitwise_not(bg_mask1)
#         equipment_mask2 = cv2.bitwise_not(bg_mask2)
#
#         # 创建组合装备掩码（两张图片都有装备的区域）
#         combined_equipment_mask = cv2.bitwise_and(equipment_mask1, equipment_mask2)
#
#         # 检查是否有足够的装备区域进行比较
#         equipment_pixels = np.sum(combined_equipment_mask == 255)
#         total_pixels = target_size[0] * target_size[1]
#         equipment_ratio = equipment_pixels / total_pixels
#
#         if equipment_ratio < 0.05:  # 少于5%的装备区域
#             log_message("WARNING", "装备区域过小，颜色相似度可能不准确")
#
#         # 转换为LAB色彩空间（更接近人类视觉感知）
#         lab1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2LAB)
#         lab2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2LAB)
#
#         # 获取装备区域的像素
#         equipment_pixels1 = lab1[combined_equipment_mask == 255]
#         equipment_pixels2 = lab2[combined_equipment_mask == 255]
#
#         if len(equipment_pixels1) == 0 or len(equipment_pixels2) == 0:
#             log_message("WARNING", "没有找到装备像素，返回相似度为0")
#             return 0
#
#         # 计算平均颜色
#         mean_color1 = np.mean(equipment_pixels1, axis=0)
#         mean_color2 = np.mean(equipment_pixels2, axis=0)
#
#         # 计算LAB色彩空间的欧氏距离
#         # LAB色彩空间的感知差异更符合人类视觉
#         color_distance = np.linalg.norm(mean_color1 - mean_color2)
#
#         # 转换为相似度（距离越小，相似度越高）
#         # 增加最大距离阈值，使颜色相似度计算更加合理
#         # LAB空间中，距离30已经是较大的差异，使用30作为最大距离
#         max_distance = 30.0  # 增加最大距离，使相似度计算更加合理
#         similarity = max(0, 1 - color_distance / max_distance)
#
#         # 记录详细的颜色差异信息（用于调试）
#         if color_distance > 10:  # 调整阈值，记录更多差异信息
#             l_diff = mean_color1[0] - mean_color2[0]  # 亮度差异
#             a_diff = mean_color1[1] - mean_color2[1]  # 红-绿差异
#             b_diff = mean_color1[2] - mean_color2[2]  # 黄-蓝差异
#
#             log_message("DEBUG", f"LAB颜色距离: {color_distance:.2f}")
#             log_message("DEBUG", f"图片1平均颜色 (LAB): {mean_color1}")
#             log_message("DEBUG", f"图片2平均颜色 (LAB): {mean_color2}")
#             log_message("DEBUG", f"LAB差异: L{l_diff:+.2f}, A{a_diff:+.2f}, B{b_diff:+.2f}")
#             log_message("DEBUG", f"颜色相似度: {similarity:.3f}")
#
#         return similarity
#     except Exception as e:
#         log_message("ERROR", f"颜色相似度计算失败: {e}")
#         return 0

# def calculate_composite_score(template_score, color_score, template_weight=0.75, color_weight=0.25):
#     """
#     计算综合得分（简化版本）
#     只使用模板匹配和颜色欧氏距离
#
#     Args:
#         template_score: 模板匹配得分（0-100）
#         color_score: 颜色相似度得分（0-1）
#         template_weight: 模板匹配权重（默认0.75，调整模板匹配权重）
#         color_weight: 颜色相似度权重（默认0.25，调整颜色权重）
#
#     Returns:
#         综合得分（0-100）
#     """
#     # 将颜色相似度转换为0-100范围
#     color_score_100 = color_score * 100
#
#     # 计算加权平均
#     composite_score = template_score * template_weight + color_score_100 * color_weight
#
#     return composite_score

# def match_equipment_images(base_dir, compare_dir, output_dir):
#     """
#     执行装备图片匹配
#
#     Args:
#         base_dir: 基准图像目录
#         compare_dir: 对比图像目录
#         output_dir: 输出目录
#
#     Returns:
#         匹配结果列表
#     """
#     log_message("INIT", "开始装备图片匹配")
#     log_message("CONFIG", f"使用模板匹配+掩码+颜色欧氏距离（背景色39212e、浅紫色20904f71）")
#     log_message("CONFIG", f"模板匹配权重: 75%, 颜色权重: 25%")
#
#     # 检查目录是否存在
#     if not os.path.exists(base_dir):
#         log_message("ERROR", f"基准图像目录不存在: {base_dir}")
#         return []
#
#     if not os.path.exists(compare_dir):
#         log_message("ERROR", f"对比图像目录不存在: {compare_dir}")
#         return []
#
#     # 创建输出目录
#     os.makedirs(output_dir, exist_ok=True)
#
#     # 创建掩码图像保存目录
#     masked_output_dir = os.path.join(output_dir, "masked_images")
#     os.makedirs(masked_output_dir, exist_ok=True)
#
#     # 创建对比图像保存目录
#     comparison_output_dir = os.path.join(output_dir, "comparisons")
#     os.makedirs(comparison_output_dir, exist_ok=True)
#
#     # 获取基准图像列表
#     base_images = [f for f in os.listdir(base_dir)
#                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
#
#     # 获取对比图像列表
#     compare_images = [f for f in os.listdir(compare_dir)
#                     if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
#
#     if not base_images:
#         log_message("ERROR", "未找到基准图像")
#         return []
#
#     if not compare_images:
#         log_message("ERROR", "未找到对比图像")
#         return []
#
#     log_message("INIT", f"找到 {len(base_images)} 个基准图像")
#     log_message("INIT", f"找到 {len(compare_images)} 个对比图像")
#     log_message("INIT", f"掩码图像将保存到: {masked_output_dir}")
#     log_message("INIT", f"对比图像将保存到: {comparison_output_dir}")
#
#     # 存储所有匹配结果
#     all_results = []
#
#     # 对每个对比图像进行匹配
#     for compare_img in compare_images:
#         log_message("MATCH", f"正在处理对比图像: {compare_img}")
#
#         compare_path = os.path.join(compare_dir, compare_img)
#         compare_image = load_image(compare_path)
#
#         if compare_image is None:
#             continue
#
#         # 为对比图像创建掩码并保存
#         compare_mask = create_background_mask(compare_image)
#         compare_masked_image = apply_mask_to_image(compare_image, compare_mask)
#
#         # 保存对比图像的掩码和掩码后图像
#         compare_mask_path = os.path.join(masked_output_dir, f"mask_{compare_img}")
#         compare_masked_path = os.path.join(masked_output_dir, f"masked_{compare_img}")
#
#         cv2.imwrite(compare_mask_path, compare_mask)
#         cv2.imwrite(compare_masked_path, compare_masked_image)
#
#         log_message("DEBUG", f"已保存对比图像掩码: {compare_mask_path}")
#         log_message("DEBUG", f"已保存对比图像掩码后图像: {compare_masked_path}")
#
#         best_match = None
#         best_score = 0
#         best_base_masked = None
#         best_base_mask = None
#
#         # 与每个基准图像进行匹配
#         for base_img in base_images:
#             base_path = os.path.join(base_dir, base_img)
#             base_image = load_image(base_path)
#
#             if base_image is None:
#                 continue
#
#             # 为基准图像创建掩码并保存
#             base_mask = create_background_mask(base_image)
#             base_masked_image = apply_mask_to_image(base_image, base_mask)
#
#             # 保存基准图像的掩码和掩码后图像
#             base_mask_path = os.path.join(masked_output_dir, f"mask_{base_img}")
#             base_masked_path = os.path.join(masked_output_dir, f"masked_{base_img}")
#
#             cv2.imwrite(base_mask_path, base_mask)
#             cv2.imwrite(base_masked_path, base_masked_image)
#
#             log_message("DEBUG", f"已保存基准图像掩码: {base_mask_path}")
#             log_message("DEBUG", f"已保存基准图像掩码后图像: {base_masked_path}")
#
#             # 计算模板匹配相似度
#             template_score, method = template_matching(base_image, compare_image)
#
#             # 计算颜色相似度（使用欧氏距离方法）
#             color_score = calculate_color_similarity_with_euclidean(base_image, compare_image)
#
#             # 计算综合得分（简化版本）
#             composite_score = calculate_composite_score(template_score, color_score)
#
#             # 记录结果
#             result = {
#                 'base_image': base_img,
#                 'compare_image': compare_img,
#                 'template_score': template_score,
#                 'template_method': method,
#                 'color_score': color_score,
#                 'composite_score': composite_score
#             }
#
#             all_results.append(result)
#
#             # 更新最佳匹配
#             if composite_score > best_score:
#                 best_score = composite_score
#                 best_match = result
#                 best_base_masked = base_masked_image
#                 best_base_mask = base_mask
#
#         # 创建对比图像并保存
#         if best_match and best_base_masked is not None:
#             # 调整图像大小为相同尺寸以便比较
#             target_size = (200, 200)  # 增大尺寸以便更好地查看
#             base_resized = cv2.resize(best_base_masked, target_size)
#             compare_resized = cv2.resize(compare_masked_image, target_size)
#
#             # 创建对比图像
#             comparison_image = np.zeros((target_size[0], target_size[1] * 2, 3), dtype=np.uint8)
#             comparison_image[:, :target_size[1]] = base_resized
#             comparison_image[:, target_size[1]:] = compare_resized
#
#             # 在图像上添加文本信息
#             font = cv2.FONT_HERSHEY_SIMPLEX
#             font_scale = 0.5
#             color = (255, 255, 255)
#             thickness = 1
#
#             # 添加基准图像信息
#             base_text = f"{best_match['base_image']}"
#             cv2.putText(comparison_image, base_text, (10, 20), font, font_scale, color, thickness)
#             cv2.putText(comparison_image, f"Score: {best_match['composite_score']:.2f}%", (10, 40), font, font_scale, color, thickness)
#
#             # 添加对比图像信息
#             compare_text = f"{compare_img}"
#             cv2.putText(comparison_image, compare_text, (target_size[1] + 10, 20), font, font_scale, color, thickness)
#             cv2.putText(comparison_image, f"Template: {best_match['template_score']:.2f}%", (target_size[1] + 10, 40), font, font_scale, color, thickness)
#             cv2.putText(comparison_image, f"Color: {best_match['color_score']:.3f}", (target_size[1] + 10, 60), font, font_scale, color, thickness)
#
#             # 保存对比图像
#             comparison_filename = f"comparison_{compare_img}_vs_{best_match['base_image']}.jpg"
#             comparison_path = os.path.join(comparison_output_dir, comparison_filename)
#             cv2.imwrite(comparison_path, comparison_image)
#
#             log_message("DEBUG", f"已保存对比图像: {comparison_path}")
#
#         # 输出最佳匹配结果到终端
#         if best_match:
#             if best_match['composite_score'] > 90:
#                 log_message("RESULT",
#                            f"按照阈值匹配90%：最终筛选出{best_match['base_image']} ← {best_match['compare_image']} "
#                            f"(综合得分: {best_match['composite_score']:.2f}%, "
#                            f"模板匹配: {best_match['template_score']:.2f}%, "
#                            f"颜色相似度: {best_match['color_score']:.3f})")
#             else:
#                 log_message("RESULT",
#                            f"最佳匹配: {best_match['base_image']} → {best_match['compare_image']} "
#                            f"(综合得分: {best_match['composite_score']:.2f}%, "
#                            f"模板匹配: {best_match['template_score']:.2f}%, "
#                            f"颜色相似度: {best_match['color_score']:.3f})")
#
#     # 保存详细结果到JSON文件
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     result_file = os.path.join(output_dir, f"matching_results_{timestamp}.json")
#
#     with open(result_file, 'w', encoding='utf-8') as f:
#         json.dump(all_results, f, indent=2, ensure_ascii=False)
#
#     # 生成汇总报告
#     summary_file = os.path.join(output_dir, f"matching_summary_{timestamp}.txt")
#     with open(summary_file, 'w', encoding='utf-8') as f:
#         f.write("装备图片匹配结果汇总\n")
#         f.write("=" * 50 + "\n")
#         f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
#         f.write(f"基准图像数量: {len(base_images)}\n")
#         f.write(f"对比图像数量: {len(compare_images)}\n")
#         f.write(f"总匹配次数: {len(all_results)}\n")
#         f.write(f"匹配方法: 模板匹配+掩码+颜色欧氏距离\n")
#         f.write(f"掩码策略: 背景色39212e(±20)、浅紫色20904f71(±5)\n")
#         f.write(f"模板匹配权重: 75% (0.75)\n")
#         f.write(f"颜色相似度权重: 25% (0.25)\n")
#         f.write(f"颜色空间: LAB色彩空间\n")
#         f.write(f"最大颜色距离: 30.0\n")
#         f.write("\n")
#
#         # 按对比图像分组显示最佳匹配
#         f.write("各对比图像的最佳匹配结果:\n")
#         f.write("-" * 50 + "\n")
#
#         for compare_img in compare_images:
#             compare_results = [r for r in all_results if r['compare_image'] == compare_img]
#             if compare_results:
#                 best = max(compare_results, key=lambda x: x['composite_score'])
#                 f.write(f"{compare_img}:\n")
#                 if best['composite_score'] > 90:
#                     f.write(f"  按照阈值匹配90%：最终筛选出{best['base_image']}\n")
#                 else:
#                     f.write(f"  最佳匹配: {best['base_image']}\n")
#                 f.write(f"  综合得分: {best['composite_score']:.2f}%\n")
#                 f.write(f"  模板匹配: {best['template_score']:.2f}% ({best['template_method']})\n")
#                 f.write(f"  颜色相似度: {best['color_score']:.3f}\n\n")
#
#     log_message("RESULT", f"匹配完成，结果已保存到: {output_dir}")
#     log_message("RESULT", f"详细结果: {result_file}")
#     log_message("RESULT", f"汇总报告: {summary_file}")
#
#     return all_results

def test_step2_cutting():
    """测试步骤2：分割图片功能"""
    if LOGGER_AVAILABLE:
        logger = get_step_logger()
        logger.start_step("step2_cut", "测试分割图片功能")
    else:
        print("\n" + "=" * 60)
        print("测试步骤2：分割图片功能")
        print("=" * 60)
        print("验证截图切割和标记功能")
        print("-" * 60)
    
    test_results = []
    temp_dir = None
    
    try:
        # 创建临时目录
        if LOGGER_AVAILABLE:
            temp_dir = logger.get_step_dir("step2_cut") / "temp_files"
            temp_dir.mkdir(parents=True, exist_ok=True)
        else:
            temp_dir = tempfile.mkdtemp()
            print(f"创建临时测试目录: {temp_dir}")
        
        # 测试1：创建测试截图
        if LOGGER_AVAILABLE:
            logger.log_info("创建测试截图...")
        else:
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
        if LOGGER_AVAILABLE:
            logger.log_success("测试截图创建成功")
        else:
            print("✓ 测试截图创建成功")
        test_results.append(("测试截图创建", True))
        
        # 测试2：测试截图分析功能
        if LOGGER_AVAILABLE:
            logger.log_info("测试截图分析功能...")
        else:
            print("\n2. 测试截图分析功能...")
        try:
            from src.screenshot_cutter import ScreenshotCutter
            cutter = ScreenshotCutter()
            
            analysis = cutter.analyze_screenshot(test_screenshot_path)
            if analysis and 'image_size' in analysis:
                if LOGGER_AVAILABLE:
                    logger.log_success(f"截图分析成功: {analysis['image_size']}")
                else:
                    print(f"✓ 截图分析成功: {analysis['image_size']}")
                test_results.append(("截图分析功能", True))
            else:
                if LOGGER_AVAILABLE:
                    logger.log_error("截图分析失败")
                else:
                    print("❌ 截图分析失败")
                test_results.append(("截图分析功能", False))
        except ImportError as e:
            if LOGGER_AVAILABLE:
                logger.log_error(f"导入截图切割器失败: {e}")
            else:
                print(f"❌ 导入截图切割器失败: {e}")
            test_results.append(("截图分析功能", False))
        
        # 测试3：测试固定坐标切割
        if LOGGER_AVAILABLE:
            logger.log_info("测试固定坐标切割...")
        else:
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
                    if LOGGER_AVAILABLE:
                        logger.log_success(f"固定坐标切割成功: 切割了 {len(cut_files)} 个装备")
                    else:
                        print(f"✓ 固定坐标切割成功: 切割了 {len(cut_files)} 个装备")
                    test_results.append(("固定坐标切割", True))
                else:
                    if LOGGER_AVAILABLE:
                        logger.log_error(f"固定坐标切割数量不正确: {len(cut_files)} 个装备")
                    else:
                        print(f"❌ 固定坐标切割数量不正确: {len(cut_files)} 个装备")
                    test_results.append(("固定坐标切割", False))
            else:
                if LOGGER_AVAILABLE:
                    logger.log_error("固定坐标切割失败")
                else:
                    print("❌ 固定坐标切割失败")
                test_results.append(("固定坐标切割", False))
        except Exception as e:
            if LOGGER_AVAILABLE:
                logger.log_error(f"固定坐标切割测试失败: {e}")
            else:
                print(f"❌ 固定坐标切割测试失败: {e}")
            test_results.append(("固定坐标切割", False))
        
        # 测试4：测试圆形标记功能
        if LOGGER_AVAILABLE:
            logger.log_info("测试圆形标记功能...")
        else:
            print("\n4. 测试圆形标记功能...")
        try:
            marker_files = [f for f in os.listdir(output_folder) if f.endswith('_circle.jpg')]
            if len(marker_files) == 12:
                if LOGGER_AVAILABLE:
                    logger.log_success(f"圆形标记功能正常: 生成了 {len(marker_files)} 个标记文件")
                else:
                    print(f"✓ 圆形标记功能正常: 生成了 {len(marker_files)} 个标记文件")
                test_results.append(("圆形标记功能", True))
            else:
                if LOGGER_AVAILABLE:
                    logger.log_error(f"圆形标记功能异常: 只生成了 {len(marker_files)} 个标记文件")
                else:
                    print(f"❌ 圆形标记功能异常: 只生成了 {len(marker_files)} 个标记文件")
                test_results.append(("圆形标记功能", False))
        except Exception as e:
            if LOGGER_AVAILABLE:
                logger.log_error(f"圆形标记功能测试失败: {e}")
            else:
                print(f"❌ 圆形标记功能测试失败: {e}")
            test_results.append(("圆形标记功能", False))
        
        # 测试5：测试文件重命名功能
        if LOGGER_AVAILABLE:
            logger.log_info("测试文件重命名功能...")
        else:
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
                if LOGGER_AVAILABLE:
                    logger.log_success(f"文件重命名功能正常: 成功重命名 {len(renamed_files)} 个文件")
                else:
                    print(f"✓ 文件重命名功能正常: 成功重命名 {len(renamed_files)} 个文件")
                test_results.append(("文件重命名功能", True))
            else:
                if LOGGER_AVAILABLE:
                    logger.log_error("文件重命名功能异常: 重命名后文件数量或格式不正确")
                else:
                    print(f"❌ 文件重命名功能异常: 重命名后文件数量或格式不正确")
                test_results.append(("文件重命名功能", False))
        except Exception as e:
            if LOGGER_AVAILABLE:
                logger.log_error(f"文件重命名功能测试失败: {e}")
            else:
                print(f"❌ 文件重命名功能测试失败: {e}")
            test_results.append(("文件重命名功能", False))
        
    except Exception as e:
        if LOGGER_AVAILABLE:
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
    if LOGGER_AVAILABLE:
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        
        logger.log_info(f"总计: {passed}/{total} 个测试通过")
        
        # 生成报告
        stats = logger.get_step_stats("step2_cut")
        additional_info = {
            "files_processed": [name for name, _ in test_results],
            "test_results": test_results
        }
        
        report_generator = get_report_generator()
        report_generator.generate_step_report("step2_cut", stats, additional_info)
        
        logger.end_step("step2_cut", "完成" if passed == total else "部分失败")
        
        return passed == total
    else:
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
        import argparse
        
        # 解析命令行参数
        parser = argparse.ArgumentParser(description='步骤2：分割原始图片功能测试')
        parser.add_argument('--enable-matching', action='store_true',
                           help='启用图片匹配功能')
        
        args = parser.parse_args()
        
        # 自动执行步骤2功能
        success = step2_cut_screenshots(auto_mode=True, enable_matching=args.enable_matching)
        
        if not success:
            print("\n❌ 步骤2自动化执行失败！")
            
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()