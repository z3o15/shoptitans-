#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的图像预处理启动脚本
从 cropped_equipment_original 和 cropped_equipment_marker 读取图像，
处理后的图像保存到 images/cropped_equipment 目录
"""

import os
import sys
from datetime import datetime
from .preprocess_pipeline import PreprocessPipeline
from ..config.config_manager import get_config_manager


def process_preprocessed_images():
    """处理预处理图像"""
    print("=" * 60)
    print("增强的图像预处理流水线")
    print("=" * 60)
    print("此脚本将从以下目录读取图像:")
    print("1. images/cropped_equipment_original (圆形带填充的装备图片)")
    print("处理后的图像将保存到 images/cropped_equipment 目录")
    print("删除逻辑: 首次处理不删除原始图片，第二次处理时删除已存在处理结果的原始图片")
    print("-" * 60)
    
    # 获取配置管理器
    config_manager = get_config_manager()
    
    # 获取路径配置
    paths_config = config_manager.get_paths_config()
    images_dir = paths_config.get("images_dir", "images")
    
    # 定义输入和输出目录
    from src.utils.path_manager import get_path
    input_dir = get_path("cropped_equipment_original_dir")
    output_dir = get_path("cropped_equipment_dir")
    
    # 检查输入目录是否存在
    if not os.path.exists(input_dir):
        print(f"\n❌ 输入目录不存在: {input_dir}")
        print("请先完成前置步骤")
        return False
    
    print(f"✓ 找到输入目录: {input_dir}")
    
    # 检查输入目录中是否有文件
    # 检查是否有时间命名的子目录
    subdirs = []
    # 使用路径管理器处理时间戳目录
    from src.utils.path_manager import get_path_manager
    path_manager = get_path_manager()
    
    for item in os.listdir(input_dir):
        item_path = os.path.join(input_dir, item)
        if os.path.isdir(item_path) and path_manager._is_timestamp_dir(item):
            subdirs.append(item)
    
    if subdirs:
        # 如果有时间命名的子目录，使用最新的一个
        latest_dir = sorted(subdirs)[-1]
        current_input_dir = os.path.join(input_dir, latest_dir)
        
        files = [f for f in os.listdir(current_input_dir)
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        if files:
            print(f"✓ 找到 {len(files)} 个文件在 {current_input_dir}")
        else:
            print("\n❌ 输入目录中没有找到图像文件")
            return False
    else:
        # 如果没有时间命名的子目录，直接在主目录中查找
        current_input_dir = input_dir
        files = [f for f in os.listdir(input_dir)
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        if files:
            print(f"✓ 找到 {len(files)} 个文件在 {input_dir}")
        else:
            print("\n❌ 输入目录中没有找到图像文件")
            return False
    
    # 检查输出目录中已存在的文件
    existing_output_files = set()
    if os.path.exists(output_dir):
        existing_output_files = set([f for f in os.listdir(output_dir)
                                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])
        if existing_output_files:
            print(f"✓ 输出目录中已存在 {len(existing_output_files)} 个文件")
    
    # 询问用户是否继续
    print(f"\n处理后的图像将保存到: {output_dir}")
    print("删除逻辑: 首次处理不删除原始图片，第二次处理时删除已存在处理结果的原始图片")
    confirm = input("确认继续处理？(y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消操作")
        return False
    
    try:
        # 创建预处理流水线
        target_size = tuple(config_manager.get_recognition_config().get('target_size', [116, 116]))
        enable_enhancement = config_manager.get_preprocessing_config().get('enable_enhancement', True)
        
        pipeline = PreprocessPipeline(target_size=target_size, enable_enhancement=enable_enhancement)
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 清理输出目录中的旧文件（可选）
        existing_files = [f for f in os.listdir(output_dir) 
                         if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        
        if existing_files:
            print(f"\n输出目录中已存在 {len(existing_files)} 个文件")
            clean_output = input("是否清理输出目录中的旧文件？(y/n): ").strip().lower()
            if clean_output == 'y':
                for filename in existing_files:
                    file_path = os.path.join(output_dir, filename)
                    try:
                        os.remove(file_path)
                        print(f"✓ 已删除: {filename}")
                    except Exception as e:
                        print(f"❌ 删除失败 {filename}: {e}")
        
        # 批量处理图像
        print(f"\n开始处理图像...")
        results = pipeline.batch_process_directory_with_smart_deletion(
            input_dir=current_input_dir,
            output_dir=output_dir,
            existing_output_files=existing_output_files,
            save_intermediate=False
        )
        
        # 输出结果
        print(f"\n✅ 处理完成！")
        print(f"  - 总计处理: {results['stats']['total']} 个文件")
        print(f"  - 成功处理: {results['stats']['success']} 个文件")
        print(f"  - 处理失败: {results['stats']['failed']} 个文件")
        print(f"  - 同步删除: {results['stats']['deleted']} 个文件")
        print(f"  - 输出目录: {output_dir}")
        
        # 列出处理后的文件
        output_files = [f for f in os.listdir(output_dir) 
                       if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        
        if output_files:
            print(f"\n处理后的文件:")
            for i, filename in enumerate(sorted(output_files), 1):
                file_path = os.path.join(output_dir, filename)
                file_size = os.path.getsize(file_path)
                print(f"  {i}. {filename} ({file_size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 处理过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("增强的图像预处理流水线")
    print("用于处理圆形带填充的装备图片和带有圆形标记图片")
    
    success = process_preprocessed_images()
    
    if success:
        print("\n🎉 预处理流水线执行完成！")
        print("现在可以继续进行装备识别匹配步骤")
    else:
        print("\n❌ 预处理流水线执行失败")
    
    return success


if __name__ == "__main__":
    main()