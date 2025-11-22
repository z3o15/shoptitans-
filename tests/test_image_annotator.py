#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像注释功能测试脚本
测试原图圆形标记功能
"""

import os
import sys
import json
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_image_annotator():
    """测试图像注释器功能"""
    print("=" * 60)
    print("图像注释功能测试")
    print("=" * 60)
    
    try:
        from src.image_annotator import ImageAnnotator
        from src.config_manager import get_config_manager
        
        # 获取配置管理器
        config_manager = get_config_manager()
        
        # 创建注释器
        annotator = ImageAnnotator(
            circle_color=config_manager.get_circle_color(),
            circle_width=config_manager.get_circle_width(),
            font_size=config_manager.get_font_size(),
            show_similarity_text=config_manager.get_show_similarity_text()
        )
        
        print(f"注释器配置:")
        print(f"  - 圆形颜色: {config_manager.get_circle_color()}")
        print(f"  - 圆形宽度: {config_manager.get_circle_width()}像素")
        print(f"  - 字体大小: {config_manager.get_font_size()}像素")
        print(f"  - 显示相似度: {'是' if config_manager.get_show_similarity_text() else '否'}")
        
        # 测试参数
        screenshot_path = "images/game_screenshots/MuMu-20251122-085551-742.png"
        matched_items = [("item_0_0.png", 95.2), ("item_0_3.png", 87.5), ("item_1_2.png", 91.3)]
        
        cutting_params = {
            'grid': (5, 2),
            'item_width': 210,
            'item_height': 160,
            'margin_left': 10,
            'margin_top': 275,
            'h_spacing': 15,
            'v_spacing': 20
        }
        
        # 检查测试截图是否存在
        if not os.path.exists(screenshot_path):
            print(f"⚠️ 测试截图不存在: {screenshot_path}")
            print("请确保游戏截图目录中有测试截图")
            return False
        
        # 创建输出目录
        output_dir = "test_annotation_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # 执行注释
        print(f"\n正在注释截图: {os.path.basename(screenshot_path)}")
        annotated_path = annotator.annotate_screenshot_with_matches(
            screenshot_path=screenshot_path,
            matched_items=matched_items,
            cutting_params=cutting_params,
            output_path=os.path.join(output_dir, "test_annotated.png")
        )
        
        # 创建注释报告
        report_path = annotator.create_annotation_report(
            screenshot_path=screenshot_path,
            matched_items=matched_items,
            annotated_image_path=annotated_path,
            output_dir=output_dir
        )
        
        print(f"\n✅ 注释测试完成!")
        print(f"  - 注释图像: {annotated_path}")
        print(f"  - 注释报告: {report_path}")
        
        # 验证输出文件
        if os.path.exists(annotated_path):
            print(f"✅ 注释图像文件已创建")
            
            # 检查图像大小
            from PIL import Image
            with Image.open(annotated_path) as img:
                print(f"  - 图像尺寸: {img.size[0]}x{img.size[1]} 像素")
                print(f"  - 图像模式: {img.mode}")
        else:
            print(f"❌ 注释图像文件未创建")
            return False
        
        if os.path.exists(report_path):
            print(f"✅ 注释报告文件已创建")
            
            # 检查报告内容
            with open(report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
                print(f"  - 报告包含 {len(report_data.get('matches', []))} 个匹配项")
        else:
            print(f"❌ 注释报告文件未创建")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_annotation_config():
    """测试注释配置功能"""
    print("\n" + "=" * 60)
    print("注释配置功能测试")
    print("=" * 60)
    
    try:
        from src.config_manager import get_config_manager
        
        # 获取配置管理器
        config_manager = get_config_manager()
        
        # 测试配置获取
        print("当前注释配置:")
        print(f"  - 启用注释: {config_manager.get_annotation_enabled()}")
        print(f"  - 圆形颜色: {config_manager.get_circle_color()}")
        print(f"  - 圆形宽度: {config_manager.get_circle_width()}像素")
        print(f"  - 字体大小: {config_manager.get_font_size()}像素")
        print(f"  - 显示相似度: {'是' if config_manager.get_show_similarity_text() else '否'}")
        print(f"  - 自动生成注释: {'是' if config_manager.get_auto_generate_annotation() else '否'}")
        
        # 测试配置更新
        print("\n测试配置更新...")
        
        # 保存原始配置
        original_color = config_manager.get_circle_color()
        original_width = config_manager.get_circle_width()
        original_font_size = config_manager.get_font_size()
        original_show_text = config_manager.get_show_similarity_text()
        
        # 更新配置
        config_manager.set_circle_color("blue")
        config_manager.set_circle_width(5)
        config_manager.set_font_size(14)
        config_manager.set_show_similarity_text(False)
        
        # 验证更新
        print("\n更新后的配置:")
        print(f"  - 圆形颜色: {config_manager.get_circle_color()}")
        print(f"  - 圆形宽度: {config_manager.get_circle_width()}像素")
        print(f"  - 字体大小: {config_manager.get_font_size()}像素")
        print(f"  - 显示相似度: {'是' if config_manager.get_show_similarity_text() else '否'}")
        
        # 恢复原始配置
        config_manager.set_circle_color(original_color)
        config_manager.set_circle_width(original_width)
        config_manager.set_font_size(original_font_size)
        config_manager.set_show_similarity_text(original_show_text)
        
        print("\n✅ 配置已恢复为原始值")
        return True
        
    except Exception as e:
        print(f"❌ 配置测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_with_main_workflow():
    """测试与主工作流程的集成"""
    print("\n" + "=" * 60)
    print("主工作流程集成测试")
    print("=" * 60)
    
    try:
        from src.main import EquipmentMatcher
        from src.config_manager import get_config_manager
        from src.image_annotator import ImageAnnotator
        
        # 获取配置管理器
        config_manager = get_config_manager()
        
        # 检查必要文件
        base_image_path = "images/base_equipment/target_equipment_1.webp"
        screenshot_path = "images/game_screenshots/MuMu-20251122-085551-742.png"
        
        if not os.path.exists(base_image_path):
            print(f"⚠️ 基准装备图不存在: {base_image_path}")
            return False
        
        if not os.path.exists(screenshot_path):
            print(f"⚠️ 游戏截图不存在: {screenshot_path}")
            return False
        
        # 创建匹配器
        matcher = EquipmentMatcher(config_manager)
        
        # 模拟切割装备目录
        cropped_dir = "images/cropped_equipment"
        cropped_files = []
        
        # 检查是否有时间命名的子目录
        subdirs = []
        for item in os.listdir(cropped_dir):
            item_path = os.path.join(cropped_dir, item)
            if os.path.isdir(item_path) and item.replace('_', '').replace(':', '').isdigit():
                subdirs.append(item)
        
        if subdirs:
            # 如果有时间命名的子目录，使用最新的一个
            latest_dir = sorted(subdirs)[-1]
            latest_dir_path = os.path.join(cropped_dir, latest_dir)
            print(f"✓ 找到时间目录: {latest_dir}")
            
            for filename in os.listdir(latest_dir_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    cropped_files.append(os.path.join(latest_dir, filename))
            
            # 更新切割装备目录为最新的时间目录
            cropped_equipment_dir = latest_dir_path
        else:
            # 如果没有时间命名的子目录，直接在主目录中查找
            for filename in os.listdir(cropped_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    cropped_files.append(filename)
            cropped_equipment_dir = cropped_dir
        
        if not cropped_files:
            print("⚠️ 未找到切割装备图片，请先执行步骤2")
            return False
        
        # 执行匹配
        print(f"\n执行装备匹配...")
        matched_items = matcher.batch_compare(
            base_img_path=base_image_path,
            crop_folder=cropped_equipment_dir,
            threshold=80.0
        )
        
        if not matched_items:
            print("⚠️ 未找到匹配的装备，无法测试注释功能")
            return False
        
        print(f"✅ 找到 {len(matched_items)} 个匹配项")
        
        # 创建注释器
        annotator = ImageAnnotator(
            circle_color=config_manager.get_circle_color(),
            circle_width=config_manager.get_circle_width(),
            font_size=config_manager.get_font_size(),
            show_similarity_text=config_manager.get_show_similarity_text()
        )
        
        # 切割参数
        cutting_params = {
            'grid': (5, 2),
            'item_width': 210,
            'item_height': 160,
            'margin_left': 10,
            'margin_top': 275,
            'h_spacing': 15,
            'v_spacing': 20
        }
        
        # 生成注释
        print(f"\n生成注释图像...")
        output_dir = "test_annotation_output"
        os.makedirs(output_dir, exist_ok=True)
        
        annotated_path = annotator.annotate_screenshot_with_matches(
            screenshot_path=screenshot_path,
            matched_items=matched_items,
            cutting_params=cutting_params,
            output_path=os.path.join(output_dir, "integration_test_annotated.png")
        )
        
        # 创建注释报告
        report_path = annotator.create_annotation_report(
            screenshot_path=screenshot_path,
            matched_items=matched_items,
            annotated_image_path=annotated_path,
            output_dir=output_dir
        )
        
        print(f"\n✅ 集成测试完成!")
        print(f"  - 注释图像: {annotated_path}")
        print(f"  - 注释报告: {report_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 集成测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("图像注释功能测试套件")
    print("=" * 60)
    
    # 执行各项测试
    tests = [
        ("图像注释器功能测试", test_image_annotator),
        ("注释配置功能测试", test_annotation_config),
        ("主工作流程集成测试", test_integration_with_main_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n执行测试: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"✅ {test_name}: {'通过' if result else '失败'}")
        except Exception as e:
            print(f"❌ {test_name}: 异常 - {e}")
            results.append((test_name, False))
    
    # 输出测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！图像注释功能工作正常。")
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")
    
    return passed == total

if __name__ == "__main__":
    main()