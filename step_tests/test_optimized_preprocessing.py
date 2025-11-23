#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的图像预处理效果
"""

import os
import sys
import cv2
import numpy as np
from datetime import datetime
import json

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_optimized_preprocessing():
    """测试优化后的图像预处理效果"""
    print("=" * 60)
    print("测试优化后的图像预处理效果")
    print("=" * 60)
    
    try:
        # 导入优化后的模块
        from src.preprocess.background_remover import BackgroundRemover
        from src.preprocess.enhancer import ImageEnhancer
        from src.preprocess.resizer import ImageResizer
        from src.config_manager import get_config_manager
        
        # 获取配置
        config_manager = get_config_manager()
        preprocess_config = config_manager.get_preprocessing_config()
        background_config = config_manager.get_background_removal_config()
        
        print("✓ 配置加载成功")
        print(f"  - CLAHE裁剪限制: {preprocess_config.get('clahe_clip_limit', 'N/A')}")
        print(f"  - CLAHE网格大小: {preprocess_config.get('clahe_grid_size', 'N/A')}")
        print(f"  - 自适应阈值: {preprocess_config.get('canny_use_adaptive_threshold', 'N/A')}")
        print(f"  - 形态学后处理: {preprocess_config.get('morphology_post_process', 'N/A')}")
        print(f"  - 背景去除Canny阈值: {background_config.get('canny_threshold1', 'N/A')}/{background_config.get('canny_threshold2', 'N/A')}")
        
        # 初始化处理组件
        background_remover = BackgroundRemover(background_config)
        enhancer = ImageEnhancer(preprocess_config)
        resizer = ImageResizer(tuple(preprocess_config.get('target_size', [116, 116])))
        
        print("\n✓ 处理组件初始化完成")
        
        # 查找测试图像
        test_image_path = None
        possible_paths = [
            "images/cropped_equipment_original",
            "images/game_screenshots",
            "images/cropped_equipment_marker"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                for filename in os.listdir(path):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        test_image_path = os.path.join(path, filename)
                        break
                if test_image_path:
                    break
        
        if not test_image_path:
            print("❌ 未找到测试图像，创建合成测试图像")
            # 创建合成测试图像
            test_img = np.zeros((200, 200, 3), dtype=np.uint8)
            test_img[:] = (50, 100, 150)  # 蓝色背景
            
            # 添加装备图标
            center = (100, 100)
            radius = 80
            cv2.circle(test_img, center, radius, (255, 255, 255), -1)  # 白色圆形
            cv2.circle(test_img, center, radius-20, (0, 0, 255), -1)  # 蓝色内圆
            cv2.circle(test_img, center, radius-40, (255, 0, 0), -1)  # 红色核心
            
            # 保存测试图像
            test_image_path = "test_equipment.png"
            cv2.imwrite(test_image_path, test_img)
        
        print(f"\n✓ 使用测试图像: {test_image_path}")
        
        # 加载原始图像
        original_image = cv2.imread(test_image_path)
        if original_image is None:
            print(f"❌ 无法加载图像: {test_image_path}")
            return False
        
        print(f"  - 原始尺寸: {original_image.shape}")
        
        # 创建输出目录
        output_dir = "test_optimized_preprocessing"
        os.makedirs(output_dir, exist_ok=True)
        
        # 步骤1：背景去除
        print("\n1. 背景去除...")
        no_bg_image = background_remover.remove_circular_background(original_image)
        cv2.imwrite(os.path.join(output_dir, "01_no_background.jpg"), no_bg_image)
        print(f"  ✓ 背景去除完成，输出尺寸: {no_bg_image.shape}")
        
        # 步骤2：padding到正方形
        print("\n2. Padding到正方形...")
        height, width = no_bg_image.shape[:2]
        if height == width:
            squared_image = no_bg_image
        else:
            if height > width:
                padding = (height - width) // 2
                squared_image = cv2.copyMakeBorder(no_bg_image, 0, 0, padding, padding,
                                                cv2.BORDER_CONSTANT, value=[0, 0, 0])
            else:
                padding = (width - height) // 2
                squared_image = cv2.copyMakeBorder(no_bg_image, padding, padding, 0, 0,
                                                cv2.BORDER_CONSTANT, value=[0, 0, 0])
        
        cv2.imwrite(os.path.join(output_dir, "02_squared.jpg"), squared_image)
        print(f"  ✓ Padding完成，输出尺寸: {squared_image.shape}")
        
        # 步骤3：调整尺寸
        print("\n3. 调整尺寸...")
        resized_image = resizer.resize(squared_image)
        cv2.imwrite(os.path.join(output_dir, "03_resized.jpg"), resized_image)
        print(f"  ✓ 尺寸调整完成，输出尺寸: {resized_image.shape}")
        
        # 步骤4：图像增强
        print("\n4. 图像增强...")
        enhanced_image = enhancer.enhance_for_feature_detection(resized_image)
        cv2.imwrite(os.path.join(output_dir, "04_enhanced.jpg"), enhanced_image)
        print(f"  ✓ 图像增强完成，输出尺寸: {enhanced_image.shape}")
        
        # 步骤5：特征提取测试
        print("\n5. 特征提取测试...")
        if len(enhanced_image.shape) == 3:
            gray = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = enhanced_image
        
        orb = cv2.ORB_create(nfeatures=3000, scaleFactor=1.1, edgeThreshold=15, patchSize=31)
        keypoints, descriptors = orb.detectAndCompute(gray, None)
        
        print(f"  ✓ 特征提取完成")
        print(f"    - 检测到特征点数: {len(keypoints)}")
        print(f"    - 描述符维度: {descriptors.shape if descriptors is not None else 'None'}")
        
        # 保存特征点可视化
        feature_image = cv2.drawKeypoints(enhanced_image, keypoints, None, color=(0, 255, 0), flags=0)
        cv2.imwrite(os.path.join(output_dir, "05_features.jpg"), feature_image)
        
        # 性能对比测试
        print("\n6. 性能对比测试...")
        
        # 创建传统配置用于对比
        traditional_config = {
            'clahe_clip_limit': 2.0,
            'clahe_grid_size': [8, 8],
            'gaussian_blur': True,
            'gaussian_kernel': [5, 5],
            'gaussian_sigma': 0,
            'canny_edges': True,
            'canny_use_adaptive_threshold': False,
            'canny_low_threshold': 50,
            'canny_high_threshold': 150,
            'morphology_post_process': False
        }
        
        traditional_enhancer = ImageEnhancer(traditional_config)
        traditional_enhanced = traditional_enhancer.enhance_for_feature_detection(resized_image)
        
        # 提取传统方法的特征
        traditional_gray = cv2.cvtColor(traditional_enhanced, cv2.COLOR_BGR2GRAY) if len(traditional_enhanced.shape) == 3 else traditional_enhanced
        traditional_keypoints, traditional_descriptors = orb.detectAndCompute(traditional_gray, None)
        
        print(f"  传统方法特征点数: {len(traditional_keypoints)}")
        print(f"  优化方法特征点数: {len(keypoints)}")
        print(f"  特征点提升: {((len(keypoints) - len(traditional_keypoints)) / len(traditional_keypoints) * 100):.1f}%" if len(traditional_keypoints) > 0 else "N/A")
        
        cv2.imwrite(os.path.join(output_dir, "06_traditional_enhanced.jpg"), traditional_enhanced)
        traditional_feature_image = cv2.drawKeypoints(traditional_enhanced, traditional_keypoints, None, color=(0, 255, 0), flags=0)
        cv2.imwrite(os.path.join(output_dir, "07_traditional_features.jpg"), traditional_feature_image)
        
        # 输出结果总结
        print("\n" + "=" * 60)
        print("测试结果总结")
        print("=" * 60)
        print(f"✓ 优化后的图像预处理测试完成")
        print(f"  - 输出目录: {output_dir}")
        print(f"  - 特征点数量对比: 传统({len(traditional_keypoints)}) vs 优化({len(keypoints)})")
        
        improvement = len(keypoints) - len(traditional_keypoints)
        if improvement > 0:
            print(f"  🎉 特征检测性能提升: +{improvement} 个特征点 ({(improvement/len(traditional_keypoints)*100):.1f}%)")
        elif improvement < 0:
            print(f"  ⚠️ 特征检测性能下降: {improvement} 个特征点 ({(improvement/len(traditional_keypoints)*100):.1f}%)")
        else:
            print(f"  ➡️ 特征检测性能持平")
        
        print(f"\n生成的文件:")
        for i, filename in enumerate(sorted(os.listdir(output_dir)), 1):
            print(f"  {i}. {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    success = test_optimized_preprocessing()
    
    if success:
        print("\n🎉 优化后的图像预处理测试成功完成！")
    else:
        print("\n❌ 优化后的图像预处理测试失败！")

if __name__ == "__main__":
    main()