#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏装备图像识别系统 - 启动脚本
提供清晰的交互式界面，按照三步工作流程引导用户使用系统
"""

import os
import sys
import subprocess
from datetime import datetime
import shutil

def check_dependencies():
    """检查依赖是否已安装"""
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
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package}")
    
    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        print("正在安装依赖...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✓ 依赖安装完成")
            return True
        except subprocess.CalledProcessError:
            print("✗ 依赖安装失败，请手动运行: pip install -r requirements.txt")
            return False
    else:
        print("✓ 所有依赖已安装")
        return True

def check_data_files():
    """检查数据文件是否存在"""
    print("\n检查数据文件...")
    
    # 检查基准装备图目录
    base_equipment_dir = "images/base_equipment"
    if not os.path.exists(base_equipment_dir):
        print(f"✗ 缺少基准装备图目录: {base_equipment_dir}")
        return False
    
    # 检查目录中的基准装备图文件
    base_image_files = []
    for filename in os.listdir(base_equipment_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            base_image_files.append(filename)
    
    if not base_image_files:
        print(f"✗ 基准装备图目录为空: {base_equipment_dir}")
        return False
    else:
        print(f"✓ 找到 {len(base_image_files)} 个基准装备图文件:")
        for filename in sorted(base_image_files):
            print(f"  - {filename}")
    
    # 检查游戏截图目录
    game_screenshots_dir = "images/game_screenshots"
    if not os.path.exists(game_screenshots_dir):
        print(f"✗ 缺少游戏截图目录: {game_screenshots_dir}")
        return False
    
    # 检查目录中的游戏截图文件
    screenshot_files = []
    for filename in os.listdir(game_screenshots_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            screenshot_files.append(filename)
    
    if not screenshot_files:
        print(f"⚠️ 游戏截图目录为空: {game_screenshots_dir}")
    else:
        print(f"✓ 找到 {len(screenshot_files)} 个游戏截图文件:")
        for filename in sorted(screenshot_files):
            print(f"  - {filename}")
    
    # 检查切割装备目录
    cropped_equipment_dir = "images/cropped_equipment"
    if not os.path.exists(cropped_equipment_dir):
        print(f"⚠️ 切割装备目录不存在，将在步骤2中创建: {cropped_equipment_dir}")
        os.makedirs(cropped_equipment_dir, exist_ok=True)
    else:
        cropped_files = []
        for filename in os.listdir(cropped_equipment_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                cropped_files.append(filename)
        
        if not cropped_files:
            print(f"⚠️ 切割装备目录为空: {cropped_equipment_dir}")
        else:
            print(f"✓ 找到 {len(cropped_files)} 个切割装备文件:")
            for filename in sorted(cropped_files)[:5]:  # 只显示前5个
                print(f"  - {filename}")
            if len(cropped_files) > 5:
                print(f"  ... 还有 {len(cropped_files) - 5} 个文件")
    
    return True

def step1_get_screenshots(auto_mode=True):
    """步骤1：获取原始图片"""
    print("\n" + "=" * 60)
    print("步骤 1/3：获取原始图片")
    print("=" * 60)
    print("此步骤用于检查和选择游戏截图")
    print("-" * 60)
    
    # 检查游戏截图目录
    game_screenshots_dir = "images/game_screenshots"
    
    if not os.path.exists(game_screenshots_dir):
        print(f"❌ 游戏截图目录不存在: {game_screenshots_dir}")
        if not auto_mode:
            print("请将游戏截图放入该目录后重试")
        return False
    
    # 列出所有截图
    screenshot_files = []
    for filename in os.listdir(game_screenshots_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            screenshot_files.append(filename)
    
    if not screenshot_files:
        print(f"❌ 游戏截图目录为空: {game_screenshots_dir}")
        if not auto_mode:
            print("请将游戏截图放入该目录后重试")
        return False
    
    print(f"✓ 找到 {len(screenshot_files)} 个游戏截图:")
    for i, filename in enumerate(sorted(screenshot_files), 1):
        print(f"  {i}. {filename}")
    
    print(f"\n✅ 步骤1完成：已找到 {len(screenshot_files)} 个游戏截图")
    print("下一步：将这些截图分割成单个装备图片")
    return True

def step2_cut_screenshots(auto_mode=True, auto_clear_old=True, auto_select_all=True, save_original=True):
    """步骤2：分割原始图片"""
    print("\n" + "=" * 60)
    print("步骤 2/3：分割原始图片")
    print("=" * 60)
    print("此步骤将游戏截图分割成单个装备图片")
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
        print("❌ 未找到游戏截图，请先完成步骤1")
        return False
    
    # 确保输出目录存在
    output_dir = "images/cropped_equipment"
    os.makedirs(output_dir, exist_ok=True)
    
    # 检查是否需要清理旧文件
    existing_files = []
    for item in os.listdir(output_dir):
        item_path = os.path.join(output_dir, item)
        if os.path.isfile(item_path) and item.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            existing_files.append(item)
        elif os.path.isdir(item_path):
            existing_files.append(item)
    
    if existing_files:
        print(f"\n检测到 {len(existing_files)} 个已存在的文件/目录:")
        for i, item in enumerate(sorted(existing_files)[:5], 1):
            print(f"  {i}. {item}")
        if len(existing_files) > 5:
            print(f"  ... 还有 {len(existing_files) - 5} 个文件/目录")
        
        if auto_mode:
            if auto_clear_old:
                print("\n自动模式：正在清理旧文件...")
                try:
                    for item in os.listdir(output_dir):
                        item_path = os.path.join(output_dir, item)
                        try:
                            if os.path.isfile(item_path):
                                os.unlink(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                        except Exception as e:
                            print(f"删除 {item_path} 时出错: {e}")
                    print("✓ 已清理所有旧文件和目录")
                except Exception as e:
                    print(f"清理过程中出错: {e}")
            else:
                print("\n自动模式：保留旧文件，继续创建新目录")
        else:
            print("\n是否在切割前清理这些旧文件？")
            print("1. 清理所有旧文件和目录")
            print("2. 保留旧文件，继续创建新目录")
            print("3. 取消操作")
            
            choice = input("请选择 (1-3): ").strip()
            
            if choice == '1':
                print("\n正在清理旧文件...")
                try:
                    for item in os.listdir(output_dir):
                        item_path = os.path.join(output_dir, item)
                        try:
                            if os.path.isfile(item_path):
                                os.unlink(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                        except Exception as e:
                            print(f"删除 {item_path} 时出错: {e}")
                    print("✓ 已清理所有旧文件和目录")
                except Exception as e:
                    print(f"清理过程中出错: {e}")
            elif choice == '3':
                print("已取消操作")
                return False
            # choice == '2' 则不清理，继续执行
    
    # 选择截图进行切割
    print(f"\n找到 {len(screenshot_files)} 个游戏截图，选择要切割的截图:")
    for i, filename in enumerate(sorted(screenshot_files), 1):
        print(f"  {i}. {filename}")
    
    if auto_mode:
        if auto_select_all:
            print("\n自动模式：选择所有截图进行切割")
            screenshots_to_process = sorted(screenshot_files)
        else:
            # 自动选择第一个截图
            print("\n自动模式：选择第一个截图进行切割")
            screenshots_to_process = [sorted(screenshot_files)[0]]
    else:
        print(f"\n请输入截图编号 (1-{len(screenshot_files)})，或输入 'all' 切割所有截图:")
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
    
    # 使用固定坐标切割方法
    print("\n使用固定坐标切割方法...")
    
    # 执行切割
    try:
        from src.screenshot_cutter import ScreenshotCutter
        from src.config_manager import get_config_manager
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("尝试直接导入模块...")
        try:
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
            from screenshot_cutter import ScreenshotCutter
            from config_manager import get_config_manager
        except ImportError as e2:
            print(f"❌ 无法导入必要模块: {e2}")
            return False
    
    # 获取配置管理器和切割参数
    config_manager = get_config_manager()
    cutting_params = config_manager.get_cutting_params()
    print(f"使用切割参数: {cutting_params}")
    
    try:
        total_cropped = 0
        for screenshot in screenshots_to_process:
            screenshot_path = os.path.join(game_screenshots_dir, screenshot)
            print(f"\n正在处理截图: {screenshot}")
            
            # 创建时间命名的输出目录
            time_folder = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_folder = os.path.join(output_dir, time_folder)
            os.makedirs(output_folder, exist_ok=True)
            
            # 使用从配置文件读取的切割参数
            params = cutting_params
            
            if auto_mode:
                print(f"\n自动模式：保存原图和圆形区域")
                current_save_original = save_original
            else:
                # 询问用户是否只保存圆形区域
                print("\n请选择保存方式:")
                print("1. 保存原图和圆形区域")
                print("2. 仅保存圆形区域")
                
                save_choice = input("请选择 (1-2): ").strip()
                current_save_original = save_choice != '2'
            
            # 执行截图切割，并启用圆形绘制功能
            # draw_circle=True 表示在每个切割后的装备图片上绘制圆形标记
            # 这有助于识别和标记装备的位置，便于后续处理和分析
            success = ScreenshotCutter.cut_fixed(
                screenshot_path=screenshot_path,
                output_folder=output_folder,
                draw_circle=True,  # 启用圆形绘制功能，在切割后的装备图片上添加红色圆形标记
                save_original=current_save_original,  # 根据用户选择决定是否保存原图
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
                    new_name = f"{i:02d}.png"  # 格式化为两位数，如01.png, 02.png
                    new_path = os.path.join(output_folder, new_name)
                    
                    if old_path != new_path:  # 避免重命名到同一个文件
                        os.rename(old_path, new_path)
                
                print(f"✓ 已重命名文件为顺序编号格式")
            except Exception as e:
                print(f"⚠️ 重命名文件时出错: {e}")
            
            matched_items = []  # 不进行匹配，只切割
            
            # 统计切割的装备数量
            cropped_items = 0
            for filename in os.listdir(output_folder):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    cropped_items += 1
            
            print(f"✓ 从 {screenshot} 切割出 {cropped_items} 个装备到 {time_folder}/")
            total_cropped += cropped_items
        
        print(f"\n✅ 步骤2完成：共切割出 {total_cropped} 个装备图片")
        print("下一步：使用基准装备对比这些切割后的图片")
        return True
        
    except Exception as e:
        print(f"❌ 切割过程中出错: {e}")
        return False

def step3_match_equipment(auto_mode=True, auto_select_base=True, auto_threshold=None, auto_match_all=False):
    """步骤3：装备识别匹配"""
    print("\n" + "=" * 60)
    print("步骤 3/3：装备识别匹配")
    print("=" * 60)
    print("此步骤使用基准装备对比切割后的图片")
    print("-" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 检查基准装备
    base_equipment_dir = "images/base_equipment"
    base_image_files = []
    for filename in os.listdir(base_equipment_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            base_image_files.append(filename)
    
    if not base_image_files:
        print("❌ 未找到基准装备图片")
        return False
    
    # 检查切割装备
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
        print("❌ 未找到切割装备图片，请先完成步骤2")
        return False
    
    # 选择基准装备
    print(f"找到 {len(base_image_files)} 个基准装备:")
    for i, filename in enumerate(sorted(base_image_files), 1):
        print(f"  {i}. {filename}")
    
    if auto_mode:
        if auto_match_all:
            # 自动模式：遍历所有基准装备
            print(f"\n自动模式：遍历所有 {len(base_image_files)} 个基准装备进行匹配")
            all_matched_items = []
            
            for base_image in sorted(base_image_files):
                base_image_path = os.path.join(base_equipment_dir, base_image)
                base_name = os.path.splitext(base_image)[0]
                
                print(f"\n开始匹配，使用基准装备: {base_image}")
                
                # 获取匹配阈值
                if auto_threshold is not None:
                    threshold = auto_threshold
                else:
                    # 从配置管理器获取默认阈值
                    try:
                        from src.config_manager import get_config_manager
                        config_manager = get_config_manager()
                    except ImportError:
                        import sys
                        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
                        from config_manager import get_config_manager
                        config_manager = get_config_manager()
                    threshold = config_manager.get_default_threshold()
                
                print(f"匹配阈值: {threshold}%")
                print("-" * 60)
                
                # 创建匹配器
                try:
                    from src.main import EquipmentMatcher
                    matcher = EquipmentMatcher(config_manager)
                except ImportError as e:
                    print(f"❌ 导入错误: {e}")
                    print("尝试直接导入模块...")
                    try:
                        import sys
                        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
                        from main import EquipmentMatcher
                        matcher = EquipmentMatcher(config_manager)
                    except ImportError as e2:
                        print(f"❌ 无法导入必要模块: {e2}")
                        return False
                
                matched_items = matcher.batch_compare(
                    base_img_path=base_image_path,
                    crop_folder=cropped_equipment_dir,
                    threshold=threshold
                )
                
                if matched_items:
                    print(f"\n✅ 基准装备 {base_image} 找到 {len(matched_items)} 个匹配项")
                    
                    # 保存结果到tests目录
                    # os.makedirs("tests", exist_ok=True)
                    # result_file = f"tests/match_results_{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    # matcher.save_results(result_file)
                    # print(f"\n✓ 详细结果已保存到: {result_file}")
                    
                    # 重命名匹配的图片为基准装备名称
                    print(f"\n正在重命名匹配的图片为基准装备名称: {base_name}")
                    
                    for i, (filename, similarity) in enumerate(matched_items):
                        # 获取原始文件路径
                        if os.path.sep in filename:  # 如果是子目录中的文件
                            subdir = os.path.dirname(filename)
                            old_path = os.path.join(cropped_equipment_dir, subdir, os.path.basename(filename))
                            # 为每个匹配的文件添加序号，避免重名
                            new_name = f"{base_name}_{i+1}.png" if len(matched_items) > 1 else f"{base_name}.png"
                            new_path = os.path.join(cropped_equipment_dir, subdir, new_name)
                        else:
                            old_path = os.path.join(cropped_equipment_dir, filename)
                            # 为每个匹配的文件添加序号，避免重名
                            new_name = f"{base_name}_{i+1}.png" if len(matched_items) > 1 else f"{base_name}.png"
                            new_path = os.path.join(cropped_equipment_dir, new_name)
                        
                        try:
                            # 重命名文件
                            os.rename(old_path, new_path)
                            print(f"✓ 已重命名: {filename} -> {new_name}")
                        except Exception as e:
                            print(f"✗ 重命名失败 {filename}: {e}")
                    
                    print(f"\n✓ 基准装备 {base_name} 的匹配图片已重命名")
                    all_matched_items.extend(matched_items)
                else:
                    print(f"\n❌ 基准装备 {base_image} 未找到匹配项")
            
            print(f"\n✅ 步骤3完成：在 {len(cropped_files)} 个装备中总共找到 {len(all_matched_items)} 个匹配项")
            return True
        elif auto_select_base:
            print("\n自动模式：选择第一个基准装备")
            base_image = sorted(base_image_files)[0]
        else:
            # 可以根据需要添加其他自动选择逻辑
            print("\n自动模式：选择第一个基准装备")
            base_image = sorted(base_image_files)[0]
    else:
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
    if auto_mode:
        if auto_threshold is not None:
            threshold = auto_threshold
            print(f"\n自动模式：使用预设阈值 {threshold}%")
        else:
            # 从配置管理器获取默认阈值
            try:
                from src.config_manager import get_config_manager
                config_manager = get_config_manager()
            except ImportError:
                import sys
                sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
                from config_manager import get_config_manager
                config_manager = get_config_manager()
            threshold = config_manager.get_default_threshold()
            print(f"\n自动模式：使用配置文件中的默认阈值 {threshold}%")
    else:
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
    
    # 执行匹配
    try:
        from src.main import EquipmentMatcher
        from src.config_manager import get_config_manager
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("尝试直接导入模块...")
        try:
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
            from main import EquipmentMatcher
            from config_manager import get_config_manager
        except ImportError as e2:
            print(f"❌ 无法导入必要模块: {e2}")
            return False
    
    try:
        config_manager = get_config_manager()
        matcher = EquipmentMatcher(config_manager)
        
        print(f"\n开始匹配，使用基准装备: {base_image}")
        print(f"匹配阈值: {threshold}%")
        print("-" * 60)
        
        matched_items = matcher.batch_compare(
            base_img_path=base_image_path,
            crop_folder=cropped_equipment_dir,
            threshold=threshold
        )
        
        print(f"\n✅ 步骤3完成：在 {len(cropped_files)} 个装备中找到 {len(matched_items)} 个匹配项")
        
        if matched_items:
            print("\n匹配结果:")
            for i, (filename, similarity) in enumerate(matched_items, 1):
                print(f"  {i}. {filename} - 相似度: {similarity}%")
            
            # 保存结果到tests目录
            # os.makedirs("tests", exist_ok=True)
            # result_file = f"tests/match_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            # matcher.save_results(result_file)
            # print(f"\n✓ 详细结果已保存到: {result_file}")
            
            # 重命名匹配的图片为基准装备名称
            base_name = os.path.splitext(base_image)[0]  # 获取基准装备名称（不含扩展名）
            
            print(f"\n正在重命名匹配的图片为基准装备名称: {base_name}")
            
            for i, (filename, similarity) in enumerate(matched_items):
                # 获取原始文件路径
                if os.path.sep in filename:  # 如果是子目录中的文件
                    subdir = os.path.dirname(filename)
                    old_path = os.path.join(cropped_equipment_dir, subdir, os.path.basename(filename))
                    # 为每个匹配的文件添加序号，避免重名
                    new_name = f"{base_name}_{i+1}.png" if len(matched_items) > 1 else f"{base_name}.png"
                    new_path = os.path.join(cropped_equipment_dir, subdir, new_name)
                else:
                    old_path = os.path.join(cropped_equipment_dir, filename)
                    # 为每个匹配的文件添加序号，避免重名
                    new_name = f"{base_name}_{i+1}.png" if len(matched_items) > 1 else f"{base_name}.png"
                    new_path = os.path.join(cropped_equipment_dir, new_name)
                
                try:
                    # 重命名文件
                    os.rename(old_path, new_path)
                    print(f"✓ 已重命名: {filename} -> {new_name}")
                except Exception as e:
                    print(f"✗ 重命名失败 {filename}: {e}")
            
            print(f"\n✓ 所有匹配的图片已重命名为: {base_name}.png")
        else:
            print("\n未找到匹配的装备，建议：")
            print("  1. 降低匹配阈值")
            print("  2. 检查基准装备是否正确")
            print("  3. 检查切割装备是否清晰")
        
        return True
        
    except Exception as e:
        print(f"❌ 匹配过程中出错: {e}")
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
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
            from main import EquipmentMatcher
            from config_manager import get_config_manager
            from image_annotator import ImageAnnotator
        
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

def run_full_workflow():
    """运行完整工作流程"""
    print("\n" + "=" * 60)
    print("运行完整工作流程")
    print("=" * 60)
    print("将依次执行三个步骤：获取截图 → 分割图片 → 装备匹配")
    print("-" * 60)
    
    # 步骤1：获取原始图片
    if not step1_get_screenshots(auto_mode=False):
        return False
    
    # 询问是否继续
    print("\n是否继续执行步骤2？(y/n)")
    if input().strip().lower() != 'y':
        return False
    
    # 步骤2：分割原始图片
    if not step2_cut_screenshots(auto_mode=False):
        return False
    
    # 询问是否继续
    print("\n是否继续执行步骤3？(y/n)")
    if input().strip().lower() != 'y':
        return False
    
    # 步骤3：装备识别匹配
    if not step3_match_equipment(auto_mode=False):
        return False
    
    print("\n" + "=" * 60)
    print("🎉 完整工作流程执行完成！")
    print("=" * 60)
    return True

def run_full_auto_workflow(auto_clear_old=True, auto_select_all=True, save_original=True,
                           auto_select_base=True, auto_threshold=None, auto_generate_annotation=False):
    """运行全自动工作流程，无需任何手动操作"""
    print("\n" + "=" * 60)
    print("🚀 运行全自动工作流程")
    print("=" * 60)
    print("自动依次执行三个步骤：获取截图 → 分割图片 → 装备匹配")
    print("-" * 60)
    
    # 步骤1：获取原始图片
    if not step1_get_screenshots(auto_mode=True):
        print("❌ 步骤1失败，终止自动流程")
        return False
    
    # 步骤2：分割原始图片
    if not step2_cut_screenshots(auto_mode=True, auto_clear_old=auto_clear_old,
                                auto_select_all=auto_select_all, save_original=save_original):
        print("❌ 步骤2失败，终止自动流程")
        return False
    
    # 步骤3：装备识别匹配
    if not step3_match_equipment(auto_mode=True, auto_select_base=auto_select_base,
                               auto_threshold=auto_threshold, auto_match_all=True):
        print("❌ 步骤3失败，终止自动流程")
        return False
    
    # 如果启用，自动生成注释
    if auto_generate_annotation:
        print("\n" + "=" * 60)
        print("🎨 自动生成带标记的原图注释")
        print("=" * 60)
        
        try:
            # 检查是否有匹配结果
            cropped_equipment_dir = "images/cropped_equipment"
            subdirs = []
            for item in os.listdir(cropped_equipment_dir):
                item_path = os.path.join(cropped_equipment_dir, item)
                if os.path.isdir(item_path) and item.replace('_', '').replace(':', '').isdigit():
                    subdirs.append(item)
            
            if subdirs:
                latest_dir = sorted(subdirs)[-1]
                latest_dir_path = os.path.join(cropped_equipment_dir, latest_dir)
                
                # 检查是否有匹配结果文件
                test_files = os.listdir("tests")
                match_files = [f for f in test_files if f.startswith("match_results_") and f.endswith(".json")]
                
                if match_files:
                    latest_match_file = sorted(match_files)[-1]
                    print(f"✓ 找到匹配结果文件: {latest_match_file}")
                    
                    # 自动生成注释
                    try:
                        from src.image_annotator import ImageAnnotator
                        from src.config_manager import get_config_manager
                    except ImportError as e:
                        print(f"❌ 导入错误: {e}")
                        print("尝试直接导入模块...")
                        import sys
                        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
                        from image_annotator import ImageAnnotator
                        from config_manager import get_config_manager
                    import json
                    
                    config_manager = get_config_manager()
                    
                    # 检查注释功能是否启用
                    if not config_manager.get_annotation_enabled():
                        print("⚠️ 注释功能未启用，跳过注释生成")
                    else:
                        # 创建注释器
                        annotator = ImageAnnotator(
                            circle_color=config_manager.get_circle_color(),
                            circle_width=config_manager.get_circle_width(),
                            font_size=config_manager.get_font_size(),
                            show_similarity_text=config_manager.get_show_similarity_text()
                        )
                        
                        # 读取匹配结果
                        with open(os.path.join("tests", latest_match_file), 'r', encoding='utf-8') as f:
                            match_results = json.load(f)
                        
                        matched_items = []
                        for item in match_results.get('matches', []):
                            filename = item.get('filename', '')
                            similarity = item.get('similarity', 0)
                            matched_items.append((filename, similarity))
                        
                        if matched_items:
                            # 获取切割参数
                            cutting_params = config_manager.get_cutting_params()
                            
                            # 处理所有游戏截图
                            game_screenshots_dir = "images/game_screenshots"
                            screenshot_files = []
                            for filename in os.listdir(game_screenshots_dir):
                                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                                    screenshot_files.append(filename)
                            
                            annotated_images = []
                            for screenshot in sorted(screenshot_files):
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
                            
                            print(f"\n✅ 注释完成！共生成 {len(annotated_images)} 个注释图像")
                            for i, path in enumerate(annotated_images, 1):
                                print(f"  {i}. {path}")
                        else:
                            print("⚠️ 未找到匹配项，跳过注释生成")
                else:
                    print("⚠️ 未找到匹配结果文件，跳过注释生成")
            else:
                print("⚠️ 未找到切割装备目录，跳过注释生成")
                
        except Exception as e:
            print(f"⚠️ 自动生成注释时出错: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 全自动工作流程执行完成！")
    print("=" * 60)
    return True

def run_test():
    """运行系统测试"""
    print("\n运行系统测试...")
    print("=" * 50)
    
    try:
        subprocess.check_call([sys.executable, "tests/test_system.py"])
        return True
    except subprocess.CalledProcessError:
        print("系统测试失败")
        return False

def run_basic_example():
    """运行基础示例"""
    print("\n运行基础使用示例...")
    print("=" * 50)
    
    try:
        subprocess.check_call([sys.executable, "tests/examples/basic_usage.py"])
        return True
    except subprocess.CalledProcessError:
        print("基础示例运行失败")
        return False

def run_advanced_example():
    """运行高级示例"""
    print("\n运行高级使用示例...")
    print("=" * 50)
    
    try:
        subprocess.check_call([sys.executable, "tests/examples/advanced_usage.py"])
        return True
    except subprocess.CalledProcessError:
        print("高级示例运行失败")
        return False

def run_main_program():
    """运行主程序"""
    print("\n运行主程序...")
    print("=" * 50)
    
    try:
        subprocess.check_call([sys.executable, "src/main.py"])
        return True
    except subprocess.CalledProcessError:
        print("主程序运行失败")
        return False

def clear_previous_results():
    """清理之前的结果，保留主文件"""
    print("\n" + "=" * 60)
    print("清理切割结果和日志")
    print("=" * 60)
    print("此操作将清理切割后的装备和旧的日志文件")
    print("-" * 60)
    
    # 确认操作
    print("确认要清理以下内容吗？")
    print("1. 切割装备目录 (images/cropped_equipment)")
    print("2. 旧的日志文件 (recognition_logs)")
    print("注意：最新的日志文件将被保留")
    
    confirm = input("\n确认清理？(y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消清理操作")
        return
    
    # 清理切割后的装备
    cropped_dir = "images/cropped_equipment"
    if os.path.exists(cropped_dir):
        try:
            for filename in os.listdir(cropped_dir):
                file_path = os.path.join(cropped_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"删除文件 {file_path} 时出错: {e}")
            print(f"✓ 已清理 {cropped_dir} 目录")
        except Exception as e:
            print(f"清理 {cropped_dir} 目录时出错: {e}")
    
    # 清理日志目录（保留最近的一个日志文件）
    logs_dir = "recognition_logs"
    if os.path.exists(logs_dir):
        try:
            log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
            if len(log_files) > 1:
                # 按修改时间排序，保留最新的
                log_files.sort(key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)), reverse=True)
                for log_file in log_files[1:]:
                    try:
                        os.remove(os.path.join(logs_dir, log_file))
                    except Exception as e:
                        print(f"删除日志文件 {log_file} 时出错: {e}")
                print(f"✓ 已清理旧日志文件，保留最新的: {log_files[0]}")
            elif log_files:
                print(f"✓ 只有一个日志文件，保留: {log_files[0]}")
            else:
                print("✓ 日志目录为空")
        except Exception as e:
            print(f"清理日志目录时出错: {e}")
    
    print("\n✅ 清理完成！")

def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 60)
    print("游戏装备图像识别系统")
    print("=" * 60)
    print("【三步工作流程】")
    print("1. 步骤1：获取原始图片")
    print("2. 步骤2：分割原始图片")
    print("3. 步骤3：装备识别匹配")
    print("4. 运行完整工作流程")
    print("5. 🚀 运行全自动工作流程（推荐）")
    print("-" * 60)
    print("【其他功能】")
    print("6. 检查环境和依赖")
    print("7. 运行系统测试")
    print("8. 运行基础示例")
    print("9. 运行高级示例")
    print("10. 查看项目文档")
    print("11. 清理切割结果和日志")
    print("12. 生成带圆形标记的原图注释")
    print("0. 退出")
    print("-" * 60)

def main():
    """主函数"""
    print("欢迎使用游戏装备图像识别系统！")
    print("本系统按照三步工作流程进行：")
    print("1. 获取原始图片 → 2. 分割原始图片 → 3. 装备识别匹配")
    print("\n🚀 系统将自动执行完整工作流程，无需手动操作...")
    
    # 直接执行全自动工作流程
    print("\n🚀 启动全自动工作流程...")
    success = run_full_auto_workflow(auto_clear_old=True, auto_select_all=True, save_original=False,
                                     auto_select_base=True, auto_threshold=None, auto_generate_annotation=False)
    
    if success:
        print("\n✅ 全自动工作流程执行完成！")
    else:
        print("\n❌ 全自动工作流程执行失败！")
    
    print("\n感谢使用，再见！")

if __name__ == "__main__":
    main()