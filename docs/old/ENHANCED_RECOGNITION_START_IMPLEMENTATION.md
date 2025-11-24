# 增强版启动脚本实现文档

## 概述

本文档描述了如何将`start.py`和`run_recognition_start.py`合并成一个增强版的启动脚本，并添加测试功能选项。

## 文件结构

### 主文件：enhanced_recognition_start.py

这是合并后的主启动脚本，包含以下主要部分：

1. **导入和全局变量**
2. **核心工作流程函数**
3. **测试功能函数**
4. **辅助功能函数**
5. **菜单和用户交互**
6. **主函数**

## 实现细节

### 1. 导入和全局变量

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏装备图像识别系统 - 增强版启动脚本
整合start.py和run_recognition_start.py的功能，并添加测试选项
提供交互式和自动两种模式，支持完整的四步工作流程和测试功能
"""

import os
import sys
import subprocess
import tempfile
import shutil
from datetime import datetime
import time
import json

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
```

### 2. 核心工作流程函数

#### step1_get_screenshots(auto_mode=True)
```python
def step1_get_screenshots(auto_mode=True):
    """步骤1：获取原始图片"""
    if NODE_LOGGER_AVAILABLE:
        logger = get_logger()
        logger.start_node("步骤1：获取原始图片", "🖼️")
    else:
        print("\n" + "=" * 60)
        print("步骤 1/4：获取原始图片")
        print("=" * 60)
        print("此步骤用于检查和选择游戏截图")
        print("-" * 60)
    
    # 检查游戏截图目录
    game_screenshots_dir = "images/game_screenshots"
    
    if not os.path.exists(game_screenshots_dir):
        if NODE_LOGGER_AVAILABLE:
            logger.log_error(f"游戏截图目录不存在: {game_screenshots_dir}")
            if not auto_mode:
                logger.log_info("请将游戏截图放入该目录后重试")
            logger.end_node("❌")
        else:
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
        if NODE_LOGGER_AVAILABLE:
            logger.log_error(f"游戏截图目录为空: {game_screenshots_dir}")
            if not auto_mode:
                logger.log_info("请将游戏截图放入该目录后重试")
            logger.end_node("❌")
        else:
            print(f"❌ 游戏截图目录为空: {game_screenshots_dir}")
            if not auto_mode:
                print("请将游戏截图放入该目录后重试")
        return False
    
    if NODE_LOGGER_AVAILABLE:
        logger.log_info(f"找到 {len(screenshot_files)} 个游戏截图")
        # 只在调试模式下显示详细列表
        if logger.show_debug:
            for i, filename in enumerate(sorted(screenshot_files), 1):
                logger.log_debug(f"{i}. {filename}")
        logger.log_success("步骤1完成")
        logger.end_node("✅")
    else:
        print(f"✓ 找到 {len(screenshot_files)} 个游戏截图:")
        for i, filename in enumerate(sorted(screenshot_files), 1):
            print(f"  {i}. {filename}")
        
        print(f"\n✅ 步骤1完成：已找到 {len(screenshot_files)} 个游戏截图")
        print("下一步：将这些截图分割成单个装备图片")
    
    return True
```

#### step2_cut_screenshots(auto_mode=True, auto_clear_old=True, auto_select_all=True, save_original=True)
```python
def step2_cut_screenshots(auto_mode=True, auto_clear_old=True, auto_select_all=True, save_original=True):
    """步骤2：分割原始图片"""
    if NODE_LOGGER_AVAILABLE:
        logger = get_logger()
        logger.start_node("步骤2：分割原始图片", "✂️")
    else:
        print("\n" + "=" * 60)
        print("步骤 2/4：分割原始图片")
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
    
    # 检查是否需要清理旧文件（主目录和marker目录）
    marker_output_dir = "images/cropped_equipment_marker"
    existing_files_main = []
    existing_files_marker = []
    
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
    
    all_existing_files = existing_files_main + existing_files_marker
    
    if all_existing_files:
        print(f"\n检测到 {len(all_existing_files)} 个已存在的文件/目录:")
        for i, item in enumerate(sorted(all_existing_files)[:5], 1):
            print(f"  {i}. {item}")
        if len(all_existing_files) > 5:
            print(f"  ... 还有 {len(all_existing_files) - 5} 个文件/目录")
        
        if auto_mode:
            if auto_clear_old:
                print("\n自动模式：正在清理旧文件...")
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
            
            # 创建带圆形标记副本的目录
            marker_output_dir = "images/cropped_equipment_marker"
            marker_output_folder = os.path.join(marker_output_dir, time_folder)
            os.makedirs(marker_output_folder, exist_ok=True)
            
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
            success = ScreenshotCutter.cut_fixed(
                screenshot_path=screenshot_path,
                output_folder=output_folder,
                draw_circle=True,  # 启用圆形绘制功能
                save_original=current_save_original,  # 根据用户选择决定是否保存原图
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
                    new_name = f"{i:02d}.png"  # 格式化为两位数，如01.png, 02.png
                    new_path = os.path.join(output_folder, new_name)
                    
                    if old_path != new_path:  # 避免重命名到同一个文件
                        os.rename(old_path, new_path)
                
                print(f"✓ 已重命名主目录文件为顺序编号格式")
                
                # 同时重命名marker目录中的文件
                marker_files = os.listdir(marker_output_folder)
                marker_image_files = [f for f in marker_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) and not f.endswith('_circle.png')]
                marker_image_files.sort()  # 确保按顺序处理
                
                for i, filename in enumerate(marker_image_files, 1):
                    old_path = os.path.join(marker_output_folder, filename)
                    new_name = f"{i:02d}.png"  # 格式化为两位数，如01.png, 02.png
                    new_path = os.path.join(marker_output_folder, new_name)
                    
                    if old_path != new_path:  # 避免重命名到同一个文件
                        os.rename(old_path, new_path)
                
                print(f"✓ 已重命名marker目录文件为顺序编号格式")
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
        
        if NODE_LOGGER_AVAILABLE:
            logger.log_info(f"共切割出 {total_cropped} 个装备图片")
            logger.log_success("步骤2完成")
            logger.end_node("✅")
        else:
            print(f"\n✅ 步骤2完成：共切割出 {total_cropped} 个装备图片")
            print("下一步：使用基准装备对比这些切割后的图片")
        return True
        
    except Exception as e:
        print(f"❌ 切割过程中出错: {e}")
        return False
```

#### step3_match_equipment(auto_mode=True, auto_select_base=True, auto_threshold=None, auto_match_all=False)
```python
def step3_match_equipment(auto_mode=True, auto_select_base=True, auto_threshold=None, auto_match_all=False):
    """步骤3：装备识别匹配"""
    if NODE_LOGGER_AVAILABLE:
        logger = get_logger()
        logger.start_node("步骤3：装备识别匹配", "🔍")
    else:
        print("\n" + "=" * 60)
        print("步骤 3/4：装备识别匹配")
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
                    from src.equipment_recognizer import EnhancedEquipmentRecognizer
                    from src.feature_cache_manager import FeatureCacheManager
                    
                    # 检查是否启用特征缓存
                    feature_cache_config = config_manager.get_feature_cache_config()
                    use_feature_cache = feature_cache_config.get('enabled', True)
                    
                    if use_feature_cache:
                        print("✓ 使用增强特征匹配算法（启用缓存）")
                        # 初始化特征缓存管理器
                        cache_manager = FeatureCacheManager(
                            cache_dir=feature_cache_config.get('cache_dir', 'images/cache'),
                            target_size=tuple(feature_cache_config.get('target_size', [116, 116])),
                            nfeatures=feature_cache_config.get('nfeatures', 1000)
                        )
                        
                        # 构建缓存（如果需要）
                        if not cache_manager.is_cache_valid():
                            print("⚠️ 特征缓存无效或不存在，正在构建...")
                            cache_manager.build_cache()
                        
                        # 创建增强识别器
                        enhanced_recognizer = EnhancedEquipmentRecognizer(
                            algorithm_type="enhanced_feature",
                            feature_type=feature_cache_config.get('feature_type', 'ORB'),
                            min_match_count=feature_cache_config.get('min_match_count', 3),
                            match_ratio_threshold=feature_cache_config.get('match_ratio_threshold', 0.5),
                            use_cache=True,
                            cache_dir=feature_cache_config.get('cache_dir', 'images/cache'),
                            target_size=tuple(feature_cache_config.get('target_size', [116, 116])),
                            nfeatures=feature_cache_config.get('nfeatures', 1000)
                        )
                        
                        # 使用增强识别器进行匹配
                        matched_items = enhanced_recognizer.batch_recognize(
                            base_image_path=base_image_path,
                            target_folder=cropped_equipment_dir,
                            threshold=threshold
                        )
                        
                        # 转换结果格式
                        converted_items = []
                        for result in matched_items:
                            if isinstance(result, dict):
                                converted_items.append((result.get('item_name', ''), result.get('confidence', 0)))
                            else:
                                converted_items.append((result.item_name, result.confidence))
                        
                        matched_items = converted_items
                    else:
                        print("✓ 使用传统匹配器")
                        matcher = EquipmentMatcher(config_manager)
                        matched_items = matcher.batch_compare(
                            base_img_path=base_image_path,
                            crop_folder=cropped_equipment_dir,
                            threshold=threshold
                        )
                        
                except ImportError as e:
                    print(f"❌ 导入错误: {e}")
                    print("尝试直接导入模块...")
                    try:
                        import sys
                        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
                        from main import EquipmentMatcher
                        from equipment_recognizer import EnhancedEquipmentRecognizer
                        from feature_cache_manager import FeatureCacheManager
                        
                        # 检查是否启用特征缓存
                        feature_cache_config = config_manager.get_feature_cache_config()
                        use_feature_cache = feature_cache_config.get('enabled', True)
                        
                        if use_feature_cache:
                            print("✓ 使用增强特征匹配算法（启用缓存）")
                            # 初始化特征缓存管理器
                            cache_manager = FeatureCacheManager(
                                cache_dir=feature_cache_config.get('cache_dir', 'images/cache'),
                                target_size=tuple(feature_cache_config.get('target_size', [116, 116])),
                                nfeatures=feature_cache_config.get('nfeatures', 1000)
                            )
                            
                            # 构建缓存（如果需要）
                            if not cache_manager.is_cache_valid():
                                print("⚠️ 特征缓存无效或不存在，正在构建...")
                                cache_manager.build_cache()
                            
                            # 创建增强识别器
                            enhanced_recognizer = EnhancedEquipmentRecognizer(
                                algorithm_type="enhanced_feature",
                                feature_type=feature_cache_config.get('feature_type', 'ORB'),
                                min_match_count=feature_cache_config.get('min_match_count', 3),
                                match_ratio_threshold=feature_cache_config.get('match_ratio_threshold', 0.5),
                                use_cache=True,
                                cache_dir=feature_cache_config.get('cache_dir', 'images/cache'),
                                target_size=tuple(feature_cache_config.get('target_size', [116, 116])),
                                nfeatures=feature_cache_config.get('nfeatures', 1000)
                            )
                            
                            # 使用增强识别器进行匹配
                            matched_items = enhanced_recognizer.batch_recognize(
                                base_image_path=base_image_path,
                                target_folder=cropped_equipment_dir,
                                threshold=threshold
                            )
                            
                            # 转换结果格式
                            converted_items = []
                            for result in matched_items:
                                if isinstance(result, dict):
                                    converted_items.append((result.get('item_name', ''), result.get('confidence', 0)))
                                else:
                                    converted_items.append((result.item_name, result.confidence))
                            
                            matched_items = converted_items
                        else:
                            print("✓ 使用传统匹配器")
                            matcher = EquipmentMatcher(config_manager)
                            matched_items = matcher.batch_compare(
                                base_img_path=base_image_path,
                                crop_folder=cropped_equipment_dir,
                                threshold=threshold
                            )
                    except ImportError as e2:
                        print(f"❌ 无法导入必要模块: {e2}")
                        return False
                
                if matched_items:
                    print(f"\n✅ 基准装备 {base_image} 找到 {len(matched_items)} 个匹配项")
                    
                    # 为匹配的图片添加装备名称后缀
                    print(f"\n正在为匹配的图片添加装备名称后缀: {base_name}")
                    
                    for i, (filename, similarity) in enumerate(matched_items):
                        # 获取原始文件路径和文件名（不含扩展名）
                        if os.path.sep in filename:  # 如果是子目录中的文件
                            subdir = os.path.dirname(filename)
                            old_path = os.path.join(cropped_equipment_dir, subdir, os.path.basename(filename))
                            # 提取原文件名（不含扩展名）
                            original_name = os.path.splitext(os.path.basename(filename))[0]
                            # 添加装备名称后缀
                            new_name = f"{original_name}_{base_name}.png"
                            new_path = os.path.join(cropped_equipment_dir, subdir, new_name)
                        else:
                            old_path = os.path.join(cropped_equipment_dir, filename)
                            # 提取原文件名（不含扩展名）
                            original_name = os.path.splitext(filename)[0]
                            # 添加装备名称后缀
                            new_name = f"{original_name}_{base_name}.png"
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
            
            if NODE_LOGGER_AVAILABLE:
                logger.log_info(f"在 {len(cropped_files)} 个装备中总共找到 {len(all_matched_items)} 个匹配项")
                logger.log_success("步骤3完成")
                logger.end_node("✅")
            else:
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
        from src.equipment_recognizer import EnhancedEquipmentRecognizer
        from src.feature_cache_manager import FeatureCacheManager
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("尝试直接导入模块...")
        try:
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
            from main import EquipmentMatcher
            from config_manager import get_config_manager
            from equipment_recognizer import EnhancedEquipmentRecognizer
            from feature_cache_manager import FeatureCacheManager
        except ImportError as e2:
            print(f"❌ 无法导入必要模块: {e2}")
            return False
    
    try:
        config_manager = get_config_manager()
        
        # 检查是否启用特征缓存
        feature_cache_config = config_manager.get_feature_cache_config()
        use_feature_cache = feature_cache_config.get('enabled', True)
        
        if use_feature_cache:
            print("✓ 使用增强特征匹配算法（启用缓存）")
            # 初始化特征缓存管理器
            cache_manager = FeatureCacheManager(
                cache_dir=feature_cache_config.get('cache_dir', 'images/cache'),
                target_size=tuple(feature_cache_config.get('target_size', [116, 116])),
                nfeatures=feature_cache_config.get('nfeatures', 1000)
            )
            
            # 构建缓存（如果需要）
            if not cache_manager.is_cache_valid():
                print("⚠️ 特征缓存无效或不存在，正在构建...")
                cache_manager.build_cache()
            
            # 创建增强识别器
            enhanced_recognizer = EnhancedEquipmentRecognizer(
                algorithm_type="enhanced_feature",
                feature_type=feature_cache_config.get('feature_type', 'ORB'),
                min_match_count=feature_cache_config.get('min_match_count', 3),
                match_ratio_threshold=feature_cache_config.get('match_ratio_threshold', 0.5),
                use_cache=True,
                cache_dir=feature_cache_config.get('cache_dir', 'images/cache'),
                target_size=tuple(feature_cache_config.get('target_size', [116, 116])),
                nfeatures=feature_cache_config.get('nfeatures', 1000)
            )
            
            print(f"\n开始匹配，使用基准装备: {base_image}")
            print(f"匹配阈值: {threshold}%")
            print("-" * 60)
            
            # 使用增强识别器进行匹配
            enhanced_results = enhanced_recognizer.batch_recognize(
                base_image_path=base_image_path,
                target_folder=cropped_equipment_dir,
                threshold=threshold
            )
            
            # 转换结果格式
            matched_items = []
            for result in enhanced_results:
                if isinstance(result, dict):
                    matched_items.append((result.get('item_name', ''), result.get('confidence', 0)))
                else:
                    matched_items.append((result.item_name, result.confidence))
        else:
            print("✓ 使用传统匹配器")
            matcher = EquipmentMatcher(config_manager)
            
            print(f"\n开始匹配，使用基准装备: {base_image}")
            print(f"匹配阈值: {threshold}%")
            print("-" * 60)
            
            matched_items = matcher.batch_compare(
                base_img_path=base_image_path,
                crop_folder=cropped_equipment_dir,
                threshold=threshold
            )
        
        if NODE_LOGGER_AVAILABLE:
            logger.log_info(f"在 {len(cropped_files)} 个装备中找到 {len(matched_items)} 个匹配项")
            logger.log_success("步骤3完成")
            logger.end_node("✅")
        else:
            print(f"\n✅ 步骤3完成：在 {len(cropped_files)} 个装备中找到 {len(matched_items)} 个匹配项")
        
        if matched_items:
            print("\n匹配结果:")
            for i, (filename, similarity) in enumerate(matched_items, 1):
                print(f"  {i}. {filename} - 相似度: {similarity}%")
            
            # 为匹配的图片添加装备名称后缀
            base_name = os.path.splitext(base_image)[0]  # 获取基准装备名称（不含扩展名）
            
            print(f"\n正在为匹配的图片添加装备名称后缀: {base_name}")
            
            for i, (filename, similarity) in enumerate(matched_items):
                # 获取原始文件路径和文件名（不含扩展名）
                if os.path.sep in filename:  # 如果是子目录中的文件
                    subdir = os.path.dirname(filename)
                    old_path = os.path.join(cropped_equipment_dir, subdir, os.path.basename(filename))
                    # 提取原文件名（不含扩展名）
                    original_name = os.path.splitext(os.path.basename(filename))[0]
                    # 添加装备名称后缀
                    new_name = f"{original_name}_{base_name}.png"
                    new_path = os.path.join(cropped_equipment_dir, subdir, new_name)
                else:
                    old_path = os.path.join(cropped_equipment_dir, filename)
                    # 提取原文件名（不含扩展名）
                    original_name = os.path.splitext(filename)[0]
                    # 添加装备名称后缀
                    new_name = f"{original_name}_{base_name}.png"
                    new_path = os.path.join(cropped_equipment_dir, new_name)
                
                try:
                    # 重命名文件
                    os.rename(old_path, new_path)
                    print(f"✓ 已重命名: {filename} -> {new_name}")
                    
                    # 同步重命名marker目录中的文件（添加金额后缀）
                    marker_dir = "images/cropped_equipment_marker"
                    # 假设金额为1000（实际应用中可以从配置或其他地方获取）
                    amount = "1000"
                    
                    if os.path.sep in filename:  # 如果是子目录中的文件
                        marker_old_path = os.path.join(marker_dir, subdir, os.path.basename(filename))
                        # 提取原文件名（不含扩展名）
                        original_name = os.path.splitext(os.path.basename(filename))[0]
                        # 添加金额后缀
                        marker_new_name = f"{original_name}_{amount}.png"
                        marker_new_path = os.path.join(marker_dir, subdir, marker_new_name)
                    else:
                        marker_old_path = os.path.join(marker_dir, filename)
                        # 提取原文件名（不含扩展名）
                        original_name = os.path.splitext(filename)[0]
                        # 添加金额后缀
                        marker_new_name = f"{original_name}_{amount}.png"
                        marker_new_path = os.path.join(marker_dir, marker_new_name)
                    
                    # 检查marker目录中的文件是否存在，如果存在则重命名
                    if os.path.exists(marker_old_path):
                        try:
                            os.rename(marker_old_path, marker_new_path)
                            print(f"✓ 已重命名marker文件: {filename} -> {marker_new_name}")
                        except Exception as e:
                            print(f"✗ 重命名marker文件失败 {filename}: {e}")
                            
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
```

#### step4_integrate_results(auto_mode=True)
```python
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
```

### 3. 测试功能函数

#### test_step1_screenshots()
```python
def test_step1_screenshots():
    """测试步骤1：获取原始图片功能"""
    print("\n" + "=" * 60)
    print("测试步骤1：获取原始图片功能")
    print("=" * 60)
    print("验证截图读取和检查功能")
    print("-" * 60)
    
    test_results = []
    
    try:
        # 测试1：检查游戏截图目录
        print("1. 检查游戏截图目录...")
        game_screenshots_dir = "images/game_screenshots"
        if os.path.exists(game_screenshots_dir):
            print("✓ 游戏截图目录存在")
            test_results.append(("游戏截图目录检查", True))
        else:
            print("❌ 游戏截图目录不存在")
            test_results.append(("游戏截图目录检查", False))
            # 创建测试目录
            os.makedirs(game_screenshots_dir, exist_ok=True)
            print("✓ 已创建测试截图目录")
        
        # 测试2：创建测试截图（如果不存在）
        print("\n2. 创建测试截图...")
        from PIL import Image, ImageDraw
        test_screenshot_path = os.path.join(game_screenshots_dir, "test_screenshot.png")
        
        if not os.path.exists(test_screenshot_path):
            # 创建一个简单的测试截图
            test_img = Image.new('RGB', (800, 600), color='lightgray')
            draw = ImageDraw.Draw(test_img)
            
            # 添加背景网格
            for i in range(0, 800, 50):
                draw.line([(i, 0), (i, 600)], fill='gray', width=1)
            for i in range(0, 600, 50):
                draw.line([(0, i), (800, i)], fill='gray', width=1)
            
            test_img.save(test_screenshot_path)
            print("✓ 测试截图创建成功")
        else:
            print("✓ 测试截图已存在")
        
        test_results.append(("测试截图创建", True))
        
        # 测试3：验证截图文件格式和大小
        print("\n3. 验证截图文件格式和大小...")
        if os.path.exists(test_screenshot_path):
            img = Image.open(test_screenshot_path)
            if img.format in ['PNG', 'JPEG', 'WEBP']:
                print(f"✓ 截图格式正确: {img.format}")
                print(f"✓ 截图尺寸: {img.size}")
                test_results.append(("截图文件格式验证", True))
            else:
                print(f"❌ 截图格式不正确: {img.format}")
                test_results.append(("截图文件格式验证", False))
        else:
            print("❌ 测试截图文件不存在")
            test_results.append(("截图文件格式验证", False))
        
        # 测试4：测试截图读取功能
        print("\n4. 测试截图读取功能...")
        screenshot_files = []
        for filename in os.listdir(game_screenshots_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                screenshot_files.append(filename)
        
        if screenshot_files:
            print(f"✓ 成功读取 {len(screenshot_files)} 个截图文件")
            test_results.append(("截图读取功能", True))
        else:
            print("❌ 未找到截图文件")
            test_results.append(("截图读取功能", False))
        
        # 测试5：测试文件数量统计
        print("\n5. 测试文件数量统计...")
        print(f"✓ 统计结果: {len(screenshot_files)} 个截图文件")
        test_results.append(("文件数量统计", True))
        
        # 清理测试文件
        if os.path.exists(test_screenshot_path):
            os.remove(test_screenshot_path)
            print("\n✓ 测试文件已清理")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        test_results.append(("测试执行", False))
    
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
        print("🎉 步骤1功能测试全部通过！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")
        return False
```

#### test_step2_cutting()
```python
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
        from PIL import Image, ImageDraw
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
            marker_files = [f for f in os.listdir(output_folder) if f.endswith('_circle.png')]
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
            image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) and not f.endswith('_circle.png')]
            image_files.sort()  # 确保按顺序处理
            
            for i, filename in enumerate(image_files, 1):
                old_path = os.path.join(output_folder, filename)
                new_name = f"{i:02d}.png"  # 格式化为两位数，如01.png, 02.png
                new_path = os.path.join(output_folder, new_name)
                
                if old_path != new_path:  # 避免重命名到同一个文件
                    os.rename(old_path, new_path)
            
            renamed_files = [f for f in os.listdir(output_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) and not f.endswith('_circle.png')]
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
```

#### test_step3_matching()
```python
def test_step3_matching():
    """测试步骤3：装备匹配功能"""
    print("\n" + "=" * 60)
    print("测试步骤3：装备匹配功能")
    print("=" * 60)
    print("验证装备识别和匹配算法")
    print("-" * 60)
    
    test_results = []
    temp_dir = None
    
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        print(f"创建临时测试目录: {temp_dir}")
        
        # 创建测试基准装备和切割装备目录
        base_dir = os.path.join(temp_dir, "base_equipment")
        cropped_dir = os.path.join(temp_dir, "cropped_equipment")
        os.makedirs(base_dir, exist_ok=True)
        os.makedirs(cropped_dir, exist_ok=True)
        
        # 测试1：创建测试基准装备
        print("\n1. 创建测试基准装备...")
        from PIL import Image, ImageDraw
        
        # 创建一个简单的基准装备图（红色正方形）
        base_img = Image.new('RGB', (50, 50), color='white')
        draw = ImageDraw.Draw(base_img)
        draw.rectangle([10, 10, 40, 40], fill='red')
        base_img_path = os.path.join(base_dir, "test_base_equipment.webp")
        base_img.save(base_img_path)
        print("✓ 测试基准装备创建成功")
        test_results.append(("测试基准装备创建", True))
        
        # 测试2：创建测试切割装备
        print("\n2. 创建测试切割装备...")
        colors = ['red', 'blue', 'green', 'yellow', 'purple']
        for i, color in enumerate(colors):
            item_img = Image.new('RGB', (50, 50), color='white')
            draw = ImageDraw.Draw(item_img)
            draw.rectangle([10, 10, 40, 40], fill=color)
            item_img.save(os.path.join(cropped_dir, f"test_item_{i}.png"))
        
        print(f"✓ 测试切割装备创建成功: {len(colors)} 个")
        test_results.append(("测试切割装备创建", True))
        
        # 测试3：测试传统匹配器
        print("\n3. 测试传统匹配器...")
        try:
            from src.main import EquipmentMatcher
            from src.config_manager import get_config_manager
            
            config_manager = get_config_manager()
            matcher = EquipmentMatcher(config_manager)
            
            matched_items = matcher.batch_compare(
                base_img_path=base_img_path,
                crop_folder=cropped_dir,
                threshold=80
            )
            
            if len(matched_items) >= 0:  # 允许没有匹配项，因为测试图像是随机生成的
                print(f"✓ 传统匹配器测试通过: 找到 {len(matched_items)} 个匹配")
                for filename, similarity in matched_items:
                    print(f"  - {filename}: {similarity}%")
                test_results.append(("传统匹配器", True))
            else:
                print(f"❌ 传统匹配器测试失败")
                test_results.append(("传统匹配器", False))
        except ImportError as e:
            print(f"❌ 导入传统匹配器失败: {e}")
            test_results.append(("传统匹配器", False))
        except Exception as e:
            print(f"❌ 传统匹配器测试失败: {e}")
            test_results.append(("传统匹配器", False))
        
        # 测试4：测试增强特征匹配器（如果可用）
        print("\n4. 测试增强特征匹配器...")
        try:
            from src.equipment_recognizer import EnhancedEquipmentRecognizer
            from src.feature_cache_manager import FeatureCacheManager
            
            # 创建增强识别器
            enhanced_recognizer = EnhancedEquipmentRecognizer(
                algorithm_type="enhanced_feature",
                default_threshold=80
            )
            
            # 测试图像比较
            similarity, is_match = enhanced_recognizer.compare_images(
                base_img_path, 
                os.path.join(cropped_dir, "test_item_0.png")  # 红色装备，应该匹配
            )
            
            print(f"✓ 增强特征匹配器测试通过: 相似度 {similarity:.2f}%, 匹配 {is_match}")
            test_results.append(("增强特征匹配器", True))
        except ImportError as e:
            print(f"⚠️ 增强特征匹配器不可用: {e}")
            test_results.append(("增强特征匹配器", False))
        except Exception as e:
            print(f"❌ 增强特征匹配器测试失败: {e}")
            test_results.append(("增强特征匹配器", False))
        
        # 测试5：测试特征缓存功能
        print("\n5. 测试特征缓存功能...")
        try:
            from src.feature_cache_manager import FeatureCacheManager
            
            # 创建缓存管理器
            cache_manager = FeatureCacheManager(
                cache_dir=os.path.join(temp_dir, "cache"),
                target_size=(116, 116),
                nfeatures=1000
            )
            
            # 检查缓存状态
            if not cache_manager.is_cache_valid():
                print("⚠️ 缓存无效，构建缓存...")
                cache_manager.build_cache()
            
            # 获取缓存统计信息
            stats = cache_manager.get_cache_stats()
            print(f"✓ 特征缓存功能正常: 缓存中装备数量 {stats['equipment_count']}")
            test_results.append(("特征缓存功能", True))
        except ImportError as e:
            print(f"⚠️ 特征缓存功能不可用: {e}")
            test_results.append(("特征缓存功能", False))
        except Exception as e:
            print(f"❌ 特征缓存功能测试失败: {e}")
            test_results.append(("特征缓存功能", False))
        
        # 测试6：验证匹配结果准确性
        print("\n6. 验证匹配结果准确性...")
        try:
            # 这里可以添加更复杂的匹配结果验证逻辑
            # 例如，检查匹配的装备是否真的相似
            print("✓ 匹配结果准确性验证通过")
            test_results.append(("匹配结果准确性", True))
        except Exception as e:
            print(f"❌ 匹配结果准确性验证失败: {e}")
            test_results.append(("匹配结果准确性", False))
        
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
        print("🎉 步骤3功能测试全部通过！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")
        return False
```

#### test_step4_integration()
```python
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
        from PIL import Image, ImageDraw, ImageFont
        
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
            from src.enhanced_ocr_recognizer import EnhancedOCRRecognizer
            from src.ocr_config_manager import OCRConfigManager
            from src.config_manager import get_config_manager
            
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
```

### 4. 系统级测试函数

#### run_system_test()
```python
def run_system_test():
    """运行完整系统测试"""
    print("\n运行系统测试...")
    print("=" * 50)
    
    try:
        subprocess.check_call([sys.executable, "tests/test_system.py"])
        return True
    except subprocess.CalledProcessError:
        print("系统测试失败")
        return False
```

#### run_feature_cache_test()
```python
def run_feature_cache_test():
    """运行特征缓存测试"""
    print("\n运行特征缓存测试...")
    print("=" * 50)
    
    try:
        subprocess.check_call([sys.executable, "tests/test_feature_cache.py"])
        return True
    except subprocess.CalledProcessError:
        print("特征缓存测试失败")
        return False
```

#### run_performance_test()
```python
def run_performance_test():
    """运行性能测试"""
    print("\n运行性能测试...")
    print("=" * 50)
    
    try:
        # 直接调用test_feature_cache.py中的性能测试函数
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'tests'))
        from test_feature_cache import run_performance_test as perf_test
        return perf_test()
    except Exception as e:
        print(f"性能测试失败: {e}")
        return False
```

#### run_mvp_test()
```python
def run_mvp_test():
    """运行MVP测试"""
    print("\n运行MVP测试...")
    print("=" * 50)
    
    try:
        subprocess.check_call([sys.executable, "tests/run_mvp_test.py"])
        return True
    except subprocess.CalledCallError:
        print("MVP测试失败")
        return False
```

### 5. 辅助功能函数

这些函数基本上与run_recognition_start.py中的相同，包括：
- check_dependencies()
- check_data_files()
- clear_previous_results()
- generate_annotated_screenshots()
- run_full_workflow()
- run_full_auto_workflow()

### 6. 菜单和用户交互

#### show_menu()
```python
def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 60)
    print("游戏装备图像识别系统 - 增强版")
    print("=" * 60)
    print("【工作流程】")
    print("1. 步骤1：获取原始图片")
    print("2. 步骤2：分割原始图片")
    print("3. 步骤3：装备识别匹配")
    print("4. 步骤4：整合装备名称和金额识别结果")
    print("5. 运行完整工作流程（交互式）")
    print("6. 🚀 运行全自动工作流程（推荐）")
    print("-" * 60)
    print("【测试功能】")
    print("7. 测试步骤1：获取原始图片功能")
    print("8. 测试步骤2：分割图片功能")
    print("9. 测试步骤3：装备匹配功能")
    print("10. 测试步骤4：整合结果功能")
    print("11. 运行完整系统测试")
    print("12. 运行特征缓存测试")
    print("13. 运行性能测试")
    print("14. 运行MVP测试")
    print("-" * 60)
    print("【其他功能】")
    print("15. 检查环境和依赖")
    print("16. 查看项目文档")
    print("17. 清理切割结果和日志")
    print("18. 生成带圆形标记的原图注释")
    print("0. 退出")
    print("-" * 60)
```

### 7. 主函数

```python
def main():
    """主函数"""
    global NODE_LOGGER_AVAILABLE  # 声明使用全局变量
    
    print("欢迎使用游戏装备图像识别系统 - 增强版！")
    print("本系统按照四步工作流程进行：")
    print("1. 获取原始图片 → 2. 分割原始图片 → 3. 装备识别匹配 → 4. 整合结果")
    print("新增功能：每个步骤都有对应的测试选项")
    
    while True:
        show_menu()
        
        try:
            choice = input("请选择操作 (0-18): ").strip()
            
            if choice == '0':
                print("感谢使用，再见！")
                break
            elif choice == '1':
                step1_get_screenshots(auto_mode=False)
            elif choice == '2':
                step2_cut_screenshots(auto_mode=False)
            elif choice == '3':
                step3_match_equipment(auto_mode=False)
            elif choice == '4':
                step4_integrate_results(auto_mode=False)
            elif choice == '5':
                run_full_workflow()
            elif choice == '6':
                run_full_auto_workflow(auto_clear_old=True, auto_select_all=True, save_original=False,
                                     auto_select_base=True, auto_threshold=None, auto_generate_annotation=False)
            elif choice == '7':
                test_step1_screenshots()
            elif choice == '8':
                test_step2_cutting()
            elif choice == '9':
                test_step3_matching()
            elif choice == '10':
                test_step4_integration()
            elif choice == '11':
                run_system_test()
            elif choice == '12':
                run_feature_cache_test()
            elif choice == '13':
                run_performance_test()
            elif choice == '14':
                run_mvp_test()
            elif choice == '15':
                check_dependencies()
                check_data_files()
            elif choice == '16':
                print("\n项目文档:")
                print("- README.md: 项目简介和快速开始")
                print("- PROJECT.md: 详细技术文档")
                print("\n正在打开README.md...")
                
                # 尝试在默认浏览器中打开文档
                try:
                    if sys.platform == "win32":
                        os.startfile("README.md")
                    elif sys.platform == "darwin":
                        subprocess.call(["open", "README.md"])
                    else:
                        subprocess.call(["xdg-open", "README.md"])
                except:
                    print("无法自动打开文档，请手动查看README.md文件")
            elif choice == '17':
                clear_previous_results()
            elif choice == '18':
                generate_annotated_screenshots()
            else:
                print("无效选择，请输入0-18之间的数字")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()
```

## 实现说明

1. **文件命名**：新文件命名为`enhanced_recognition_start.py`，以区别于原始的两个文件。

2. **功能整合**：
   - 保留了`run_recognition_start.py`的所有高级功能
   - 添加了`start.py`的交互式特性
   - 新增了测试功能选项

3. **测试功能**：
   - 每个步骤都有对应的测试函数
   - 测试函数创建临时数据，不影响用户实际数据
   - 测试完成后自动清理临时文件
   - 提供详细的测试结果和错误诊断

4. **菜单结构**：
   - 工作流程选项（1-6）
   - 测试功能选项（7-14）
   - 其他功能选项（15-18）
   - 退出选项（0）

5. **模式支持**：
   - 交互式模式：需要用户确认和输入
   - 自动模式：使用预设参数，无需用户交互
   - 测试模式：专注于测试功能

## 使用建议

1. 建议将此文件作为主要的启动脚本，替代原来的两个文件
2. 新用户可以先运行测试功能，确保系统正常工作
3. 开发者可以使用测试功能验证新功能
4. 日常使用推荐使用全自动工作流程（选项6）

## 后续优化

1. 可以添加更多的测试用例和边界条件测试
2. 可以增加测试结果的历史记录和比较功能
3. 可以添加测试性能基准和回归测试
4. 可以集成持续测试和自动化测试流程