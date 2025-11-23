#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化调试器功能测试
从 enhanced_recognition_start.py 提取的独立测试模块
专门用于测试可视化调试器功能
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
    
    required_packages = ['cv2', 'PIL', 'numpy', 'matplotlib']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            elif package == 'numpy':
                import numpy
            elif package == 'matplotlib':
                import matplotlib
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

def test_visual_debugger():
    """测试可视化调试器功能"""
    print("\n" + "=" * 60)
    print("测试可视化调试器功能")
    print("=" * 60)
    print("验证可视化调试和报告生成功能")
    print("-" * 60)
    
    test_results = []
    temp_dir = None
    
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        print(f"创建临时测试目录: {temp_dir}")
        
        # 创建测试目录结构
        debug_dir = os.path.join(temp_dir, "debug_output")
        os.makedirs(debug_dir, exist_ok=True)
        
        # 测试1：创建测试图像
        print("\n1. 创建测试图像...")
        test_images = []
        
        # 创建基准图像
        base_img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        cv2.rectangle(base_img, (20, 20), (80, 80), (255, 0, 0), -1)  # 红色矩形
        base_img_path = os.path.join(temp_dir, "base_image.png")
        cv2.imwrite(base_img_path, base_img)
        test_images.append(("基准图像", base_img_path))
        
        # 创建目标图像
        target_img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        cv2.rectangle(target_img, (20, 20), (80, 80), (255, 0, 0), -1)  # 红色矩形
        target_img_path = os.path.join(temp_dir, "target_image.png")
        cv2.imwrite(target_img_path, target_img)
        test_images.append(("目标图像", target_img_path))
        
        # 创建相似但不同的图像
        similar_img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        cv2.rectangle(similar_img, (25, 25), (75, 75), (255, 0, 0), -1)  # 红色矩形，位置稍有不同
        similar_img_path = os.path.join(temp_dir, "similar_image.png")
        cv2.imwrite(similar_img_path, similar_img)
        test_images.append(("相似图像", similar_img_path))
        
        # 创建不同的图像
        different_img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        cv2.rectangle(different_img, (20, 20), (80, 80), (0, 0, 255), -1)  # 蓝色矩形
        different_img_path = os.path.join(temp_dir, "different_image.png")
        cv2.imwrite(different_img_path, different_img)
        test_images.append(("不同图像", different_img_path))
        
        print("✓ 测试图像创建成功")
        for name, path in test_images:
            print(f"  - {name}: {os.path.basename(path)}")
        test_results.append(("测试图像创建", True))
        
        # 测试2：初始化可视化调试器
        print("\n2. 初始化可视化调试器...")
        try:
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
            from debug.visual_debugger import VisualDebugger
            
            # 创建调试器
            debugger = VisualDebugger(
                debug_dir=debug_dir,
                enable_debug=True
            )
            
            print("✓ 可视化调试器初始化成功")
            test_results.append(("可视化调试器初始化", True))
            
        except ImportError as e:
            print(f"❌ 导入可视化调试器失败: {e}")
            test_results.append(("可视化调试器初始化", False))
        except Exception as e:
            print(f"❌ 可视化调试器初始化失败: {e}")
            test_results.append(("可视化调试器初始化", False))
        
        # 测试3：生成匹配报告
        print("\n3. 测试生成匹配报告...")
        try:
            # 创建调试数据
            debug_data = []
            similarities = [95.5, 88.2, 75.3, 45.1]  # 对应测试图像的相似度
            
            for i, (name, path) in enumerate(test_images[1:]):  # 跳过基准图像
                img = cv2.imread(path)
                debug_item = {
                    'filename': os.path.basename(path),
                    'similarity': similarities[i],
                    'target_image': img,
                    'base_image': base_img,
                    'file_path': path
                }
                debug_data.append(debug_item)
            
            # 生成匹配报告
            report_path = debugger.generate_matching_report(
                base_image_path=base_img_path,
                matching_results=debug_data,
                threshold=80.0
            )
            
            if os.path.exists(report_path):
                print("✓ 匹配报告生成成功")
                print(f"  报告路径: {report_path}")
                test_results.append(("匹配报告生成", True))
            else:
                print("❌ 匹配报告生成失败")
                test_results.append(("匹配报告生成", False))
                
        except Exception as e:
            print(f"❌ 匹配报告生成失败: {e}")
            test_results.append(("匹配报告生成", False))
        
        # 测试4：生成详细分析报告
        print("\n4. 测试生成详细分析报告...")
        try:
            # 生成详细分析报告
            analysis_path = debugger.generate_detailed_analysis(debug_data)
            
            if os.path.exists(analysis_path):
                print("✓ 详细分析报告生成成功")
                print(f"  分析报告路径: {analysis_path}")
                test_results.append(("详细分析报告生成", True))
            else:
                print("❌ 详细分析报告生成失败")
                test_results.append(("详细分析报告生成", False))
                
        except Exception as e:
            print(f"❌ 详细分析报告生成失败: {e}")
            test_results.append(("详细分析报告生成", False))
        
        # 测试5：生成热力图
        print("\n5. 测试生成热力图...")
        try:
            # 生成热力图
            heatmap_path = debugger.generate_heatmap(
                base_image=base_img,
                target_images=[item['target_image'] for item in debug_data],
                similarities=[item['similarity'] for item in debug_data]
            )
            
            if os.path.exists(heatmap_path):
                print("✓ 热力图生成成功")
                print(f"  热力图路径: {heatmap_path}")
                test_results.append(("热力图生成", True))
            else:
                print("❌ 热力图生成失败")
                test_results.append(("热力图生成", False))
                
        except Exception as e:
            print(f"❌ 热力图生成失败: {e}")
            test_results.append(("热力图生成", False))
        
        # 测试6：生成特征点可视化
        print("\n6. 测试生成特征点可视化...")
        try:
            # 生成特征点可视化
            keypoints_path = debugger.generate_keypoints_visualization(
                base_image=base_img,
                target_images=[item['target_image'] for item in debug_data[:2]]  # 只使用前两个目标图像
            )
            
            if os.path.exists(keypoints_path):
                print("✓ 特征点可视化生成成功")
                print(f"  特征点可视化路径: {keypoints_path}")
                test_results.append(("特征点可视化生成", True))
            else:
                print("❌ 特征点可视化生成失败")
                test_results.append(("特征点可视化生成", False))
                
        except Exception as e:
            print(f"❌ 特征点可视化生成失败: {e}")
            test_results.append(("特征点可视化生成", False))
        
        # 测试7：验证调试目录结构
        print("\n7. 验证调试目录结构...")
        try:
            # 检查调试目录结构
            expected_subdirs = ['matches', 'heatmaps', 'alignments']
            found_subdirs = []
            
            for subdir in expected_subdirs:
                subdir_path = os.path.join(debug_dir, subdir)
                if os.path.exists(subdir_path):
                    found_subdirs.append(subdir)
            
            if len(found_subdirs) >= 2:  # 至少有两个子目录认为通过
                print(f"✓ 调试目录结构正确: 找到 {len(found_subdirs)} 个子目录")
                for subdir in found_subdirs:
                    print(f"  - {subdir}")
                test_results.append(("调试目录结构", True))
            else:
                print(f"❌ 调试目录结构不完整: 只找到 {len(found_subdirs)} 个子目录")
                test_results.append(("调试目录结构", False))
                
        except Exception as e:
            print(f"❌ 验证调试目录结构失败: {e}")
            test_results.append(("调试目录结构", False))
        
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
    print("可视化调试器测试结果汇总")
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
        print("🎉 可视化调试器功能测试全部通过！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")
        return False

def run_visual_debugger():
    """运行可视化调试器"""
    print("\n" + "=" * 60)
    print("运行可视化调试器")
    print("=" * 60)
    print("此功能将生成装备匹配的可视化调试报告")
    print("-" * 60)
    
    # 检查依赖
    if not check_dependencies():
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
    
    # 执行匹配和调试
    try:
        try:
            from src.main import EquipmentMatcher
            from src.config_manager import get_config_manager
            from src.debug.visual_debugger import VisualDebugger
        except ImportError as e:
            print(f"❌ 导入错误: {e}")
            print("尝试直接导入模块...")
            try:
                import sys
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
                from main import EquipmentMatcher
                from config_manager import get_config_manager
                from debug.visual_debugger import VisualDebugger
            except ImportError as e2:
                print(f"❌ 无法导入必要模块: {e2}")
                return False
        
        # 获取配置管理器
        config_manager = get_config_manager()
        
        # 创建匹配器
        matcher = EquipmentMatcher(config_manager)
        
        # 创建调试器
        debugger = VisualDebugger(
            debug_dir="debug_output",
            enable_debug=True
        )
        
        print(f"使用调试配置:")
        print(f"  - 调试目录: debug_output")
        print(f"  - 调试启用: True")
        
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
            print("❌ 未找到匹配的装备，无法生成调试报告")
            return False
        
        print(f"\n✅ 找到 {len(matched_items)} 个匹配项")
        
        # 收集调试数据
        debug_data = []
        for filename, similarity in matched_items:
            file_path = os.path.join(cropped_equipment_dir, filename)
            if os.path.exists(file_path):
                try:
                    target_img = cv2.imread(file_path)
                    base_img = cv2.imread(base_image_path)
                    
                    debug_item = {
                        'filename': filename,
                        'similarity': similarity,
                        'target_image': target_img,
                        'base_image': base_img,
                        'file_path': file_path
                    }
                    debug_data.append(debug_item)
                except Exception as e:
                    print(f"⚠️ 处理调试数据失败 {filename}: {e}")
        
        # 生成调试报告
        if debug_data:
            report_path = debugger.generate_matching_report(
                base_image_path=base_image_path,
                matching_results=debug_data,
                threshold=threshold
            )
            print(f"\n✓ 可视化调试报告已生成: {report_path}")
            
            # 生成详细分析报告
            analysis_path = debugger.generate_detailed_analysis(debug_data)
            print(f"✓ 详细分析报告已生成: {analysis_path}")
            
            # 生成热力图
            heatmap_path = debugger.generate_heatmap(
                base_image=base_img,
                target_images=[item['target_image'] for item in debug_data],
                similarities=[item['similarity'] for item in debug_data]
            )
            print(f"✓ 热力图已生成: {heatmap_path}")
        else:
            print("⚠️ 没有可用的调试数据")
        
        return True
        
    except Exception as e:
        print(f"❌ 调试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("可视化调试器功能模块")
    print("=" * 50)
    print("1. 运行可视化调试器")
    print("2. 测试可视化调试器功能")
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
                
                run_visual_debugger()
            elif choice == '2':
                test_visual_debugger()
            else:
                print("无效选择，请输入0-2之间的数字")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()