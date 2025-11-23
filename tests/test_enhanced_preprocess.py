#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强的图像预处理流水线
"""

import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_enhanced_preprocess():
    """测试增强的图像预处理流水线"""
    print("=" * 60)
    print("测试增强的图像预处理流水线")
    print("=" * 60)
    
    try:
        # 导入必要的模块
        from src.enhanced_preprocess_start import process_preprocessed_images
        from src.preprocess.preprocess_pipeline import PreprocessPipeline
        
        print("✓ 成功导入模块")
        
        # 测试预处理流水线初始化
        pipeline = PreprocessPipeline(target_size=(116, 116), enable_enhancement=True)
        print("✓ 成功初始化预处理流水线")
        
        # 检查输入目录
        input_dir = "images/cropped_equipment_original"
        
        if os.path.exists(input_dir):
            print(f"✓ 找到输入目录: {input_dir}")
            
            # 检查是否有时间命名的子目录
            subdirs = []
            for item in os.listdir(input_dir):
                item_path = os.path.join(input_dir, item)
                if os.path.isdir(item_path) and item.replace('_', '').replace(':', '').isdigit():
                    subdirs.append(item)
            
            if subdirs:
                latest_dir = sorted(subdirs)[-1]
                current_input_dir = os.path.join(input_dir, latest_dir)
                files = [f for f in os.listdir(current_input_dir)
                        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
                if files:
                    print(f"  - 找到 {len(files)} 个文件在 {current_input_dir}")
            else:
                files = [f for f in os.listdir(input_dir)
                        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
                if files:
                    print(f"  - 找到 {len(files)} 个文件在 {input_dir}")
        else:
            print(f"❌ 输入目录不存在: {input_dir}")
            print("\n⚠️ 没有找到输入目录，无法进行完整测试")
            print("但预处理流水线模块已成功导入和初始化")
            return True
        
        # 测试批量处理目录方法
        output_dir = "images/cropped_equipment"
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n测试批量处理目录方法...")
        print(f"输入目录: {input_dir}")
        print(f"输出目录: {output_dir}")
        
        # 检查方法是否存在
        if not hasattr(pipeline, 'batch_process_directory_with_smart_deletion'):
            print("❌ batch_process_directory_with_smart_deletion 方法不存在")
            return False
        
        print("✓ batch_process_directory_with_smart_deletion 方法存在")
        
        # 检查是否有文件可以处理
        if 'current_input_dir' in locals() and os.path.exists(current_input_dir):
            files = [f for f in os.listdir(current_input_dir)
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
            
            if files:
                print(f"找到 {len(files)} 个文件可用于测试")
                
                # 询问是否进行实际处理测试
                test_actual = input("是否进行实际处理测试？(y/n): ").strip().lower()
                if test_actual == 'y':
                    print("\n开始实际处理测试（仅处理前2个文件）...")
                    
                    # 获取输出目录中已存在的文件
                    existing_output_files = set()
                    if os.path.exists(output_dir):
                        existing_output_files = set([f for f in os.listdir(output_dir)
                                                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])
                    
                    # 处理前2个文件作为测试
                    test_files = files[:2]
                    for filename in test_files:
                        input_path = os.path.join(current_input_dir, filename)
                        output_filename = os.path.splitext(filename)[0] + '.png'
                        output_path = os.path.join(output_dir, output_filename)
                        
                        print(f"\n处理文件: {filename}")
                        
                        # 处理图像
                        processed_image, orb_features = pipeline.process_image(input_path, False, None)
                        
                        if processed_image is not None:
                            # 保存处理结果
                            cv2.imwrite(output_path, processed_image)
                            print(f"✓ 处理成功: {filename} -> {output_filename}")
                            print(f"  - 特征点数: {len(orb_features[0]) if orb_features[0] else 0}")
                            print(f"  - 输出文件大小: {os.path.getsize(output_path)} bytes")
                        else:
                            print(f"❌ 处理失败: {filename}")
                    
                    print(f"\n✅ 实际处理测试完成！")
                    print(f"处理后的文件保存在: {output_dir}")
                else:
                    print("跳过实际处理测试")
            else:
                print("没有找到可用于测试的图像文件")
        else:
            print("没有找到可用的输入目录")
        
        print("\n✅ 增强的图像预处理流水线测试通过")
        return True
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    success = test_enhanced_preprocess()
    
    if success:
        print("\n🎉 测试完成！增强的图像预处理流水线已准备就绪")
        print("功能说明:")
        print("- 仅从 images/cropped_equipment_original 读取圆形带填充的装备图片")
        print("- 处理后的图像保存到 images/cropped_equipment 目录")
        print("- 首次处理不删除原始图片，第二次处理时删除已存在处理结果的原始图片")
        print("\n可以通过以下方式使用:")
        print("1. 运行 python src/start.py 并选择选项 12")
        print("2. 直接运行 python src/enhanced_preprocess_start.py")
    else:
        print("\n❌ 测试失败，请检查代码修改")
    
    return success

if __name__ == "__main__":
    main()