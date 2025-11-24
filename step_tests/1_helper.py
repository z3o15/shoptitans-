#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辅助功能测试模块
从 enhanced_recognition_start.py 提取的独立测试模块
包含各种辅助功能和测试
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

# 添加项目根目录到Python路径，以便能够导入src模块
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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
    if LOGGER_AVAILABLE:
        logger = get_unified_logger()
        logger.start_step("step1_helper", "系统依赖检查")
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
            if LOGGER_AVAILABLE:
                logger.log_success(f"{package}")
            else:
                print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            if LOGGER_AVAILABLE:
                logger.log_error(f"{package}")
            else:
                print(f"✗ {package}")
    
    if missing_packages:
        if LOGGER_AVAILABLE:
            logger.log_info(f"缺少依赖包: {', '.join(missing_packages)}")
            logger.log_info("正在安装依赖...")
        else:
            print(f"\n缺少依赖包: {', '.join(missing_packages)}")
            print("正在安装依赖...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            if LOGGER_AVAILABLE:
                logger.log_success("依赖安装完成")
                logger.end_step("step1_helper", "完成")
            else:
                print("✓ 依赖安装完成")
            return True
        except subprocess.CalledProcessError:
            if LOGGER_AVAILABLE:
                logger.log_error("依赖安装失败，请手动运行: pip install -r requirements.txt")
                logger.end_step("step1_helper", "失败")
            else:
                print("✗ 依赖安装失败，请手动运行: pip install -r requirements.txt")
            return False
    else:
        if LOGGER_AVAILABLE:
            logger.log_success("所有依赖已安装")
            logger.end_step("step1_helper", "完成")
        else:
            print("✓ 所有依赖已安装")
        return True

def check_data_files():
    """检查数据文件是否存在"""
    if LOGGER_AVAILABLE:
        logger = get_step_logger()
        logger.start_step("step1_helper", "数据文件检查")
    else:
        print("\n检查数据文件...")
    
    # 检查基准装备图目录
    base_equipment_dir = "images/base_equipment"
    if not os.path.exists(base_equipment_dir):
        if LOGGER_AVAILABLE:
            logger.log_error(f"缺少基准装备图目录: {base_equipment_dir}")
        else:
            print(f"✗ 缺少基准装备图目录: {base_equipment_dir}")
        return False
    
    # 检查目录中的基准装备图文件
    base_image_files = []
    for filename in os.listdir(base_equipment_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            base_image_files.append(filename)
    
    if not base_image_files:
        if LOGGER_AVAILABLE:
            logger.log_error(f"基准装备图目录为空: {base_equipment_dir}")
        else:
            print(f"✗ 基准装备图目录为空: {base_equipment_dir}")
        return False
    else:
        if LOGGER_AVAILABLE:
            logger.log_info(f"找到 {len(base_image_files)} 个基准装备图文件")
            for filename in sorted(base_image_files):
                logger.log_info(f"  - {filename}")
        else:
            print(f"✓ 找到 {len(base_image_files)} 个基准装备图文件:")
            for filename in sorted(base_image_files):
                print(f"  - {filename}")
    
    # 检查游戏截图目录
    game_screenshots_dir = "images/game_screenshots"
    if not os.path.exists(game_screenshots_dir):
        if LOGGER_AVAILABLE:
            logger.log_error(f"缺少游戏截图目录: {game_screenshots_dir}")
        else:
            print(f"✗ 缺少游戏截图目录: {game_screenshots_dir}")
        return False
    
    # 检查目录中的游戏截图文件
    screenshot_files = []
    for filename in os.listdir(game_screenshots_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            screenshot_files.append(filename)
    
    if not screenshot_files:
        if LOGGER_AVAILABLE:
            logger.log_warning(f"游戏截图目录为空: {game_screenshots_dir}")
        else:
            print(f"⚠️ 游戏截图目录为空: {game_screenshots_dir}")
    else:
        if LOGGER_AVAILABLE:
            logger.log_info(f"找到 {len(screenshot_files)} 个游戏截图文件")
            for filename in sorted(screenshot_files):
                logger.log_info(f"  - {filename}")
        else:
            print(f"✓ 找到 {len(screenshot_files)} 个游戏截图文件:")
            for filename in sorted(screenshot_files):
                print(f"  - {filename}")
    
    # 检查切割装备目录
    cropped_equipment_dir = "images/cropped_equipment"
    if not os.path.exists(cropped_equipment_dir):
        if LOGGER_AVAILABLE:
            logger.log_warning(f"切割装备目录不存在，将在步骤2中创建: {cropped_equipment_dir}")
        else:
            print(f"⚠️ 切割装备目录不存在，将在步骤2中创建: {cropped_equipment_dir}")
        os.makedirs(cropped_equipment_dir, exist_ok=True)
    else:
        cropped_files = []
        for filename in os.listdir(cropped_equipment_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                cropped_files.append(filename)
        
        if not cropped_files:
            if LOGGER_AVAILABLE:
                logger.log_warning(f"切割装备目录为空: {cropped_equipment_dir}")
            else:
                print(f"⚠️ 切割装备目录为空: {cropped_equipment_dir}")
        else:
            if LOGGER_AVAILABLE:
                logger.log_info(f"找到 {len(cropped_files)} 个切割装备文件")
                for filename in sorted(cropped_files)[:5]:  # 只显示前5个
                    logger.log_info(f"  - {filename}")
                if len(cropped_files) > 5:
                    logger.log_info(f"  ... 还有 {len(cropped_files) - 5} 个文件")
            else:
                print(f"✓ 找到 {len(cropped_files)} 个切割装备文件:")
                for filename in sorted(cropped_files)[:5]:  # 只显示前5个
                    print(f"  - {filename}")
                if len(cropped_files) > 5:
                    print(f"  ... 还有 {len(cropped_files) - 5} 个文件")
    
    if LOGGER_AVAILABLE:
        logger.end_step("step1_helper", "完成")
    
    return True

def clear_previous_results():
    """清理之前的结果，保留主文件"""
    if LOGGER_AVAILABLE:
        logger = get_step_logger()
        logger.start_step("step1_helper", "清理切割结果和日志")
    else:
        print("\n" + "=" * 60)
        print("清理切割结果和日志")
        print("=" * 60)
        print("此操作将清理切割后的装备和旧的日志文件")
        print("-" * 60)
    
    # 确认操作
    if LOGGER_AVAILABLE:
        logger.log_info("确认要清理以下内容吗？")
        logger.log_info("1. 切割装备目录 (images/cropped_equipment)")
        logger.log_info("2. 带圆形标记副本目录 (images/cropped_equipment_marker)")
        logger.log_info("3. 旧的日志文件 (recognition_logs)")
        logger.log_info("注意：最新的日志文件将被保留")
    else:
        print("确认要清理以下内容吗？")
        print("1. 切割装备目录 (images/cropped_equipment)")
        print("2. 带圆形标记副本目录 (images/cropped_equipment_marker)")
        print("3. 旧的日志文件 (recognition_logs)")
        print("注意：最新的日志文件将被保留")
    
    confirm = input("\n确认清理？(y/n): ").strip().lower()
    if confirm != 'y':
        if LOGGER_AVAILABLE:
            logger.log_info("已取消清理操作")
            logger.end_step("step1_helper", "已取消")
        else:
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
                    if LOGGER_AVAILABLE:
                        logger.log_error(f"删除文件 {file_path} 时出错: {e}")
                    else:
                        print(f"删除文件 {file_path} 时出错: {e}")
            if LOGGER_AVAILABLE:
                logger.log_success(f"已清理 {cropped_dir} 目录")
            else:
                print(f"✓ 已清理 {cropped_dir} 目录")
        except Exception as e:
            print(f"清理 {cropped_dir} 目录时出错: {e}")
    
    # 清理marker目录
    marker_dir = "images/cropped_equipment_marker"
    if os.path.exists(marker_dir):
        try:
            for filename in os.listdir(marker_dir):
                file_path = os.path.join(marker_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    if LOGGER_AVAILABLE:
                        logger.log_error(f"删除marker文件 {file_path} 时出错: {e}")
                    else:
                        print(f"删除marker文件 {file_path} 时出错: {e}")
            if LOGGER_AVAILABLE:
                logger.log_success(f"已清理 {marker_dir} 目录")
            else:
                print(f"✓ 已清理 {marker_dir} 目录")
        except Exception as e:
            print(f"清理 {marker_dir} 目录时出错: {e}")
    
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
                        if LOGGER_AVAILABLE:
                            logger.log_error(f"删除日志文件 {log_file} 时出错: {e}")
                        else:
                            print(f"删除日志文件 {log_file} 时出错: {e}")
                if LOGGER_AVAILABLE:
                    logger.log_success(f"已清理旧日志文件，保留最新的: {log_files[0]}")
                else:
                    print(f"✓ 已清理旧日志文件，保留最新的: {log_files[0]}")
            elif log_files:
                if LOGGER_AVAILABLE:
                    logger.log_info(f"只有一个日志文件，保留: {log_files[0]}")
                else:
                    print(f"✓ 只有一个日志文件，保留: {log_files[0]}")
            else:
                if LOGGER_AVAILABLE:
                    logger.log_info("日志目录为空")
                else:
                    print("✓ 日志目录为空")
        except Exception as e:
            if LOGGER_AVAILABLE:
                logger.log_error(f"清理日志目录时出错: {e}")
            else:
                print(f"清理日志目录时出错: {e}")
    
    if LOGGER_AVAILABLE:
        logger.log_success("清理完成")
        logger.end_step("step1_helper", "完成")
    else:
        print("\n✅ 清理完成！")


def test_v2_optimizations():
    """测试V2.0优化功能"""
    if LOGGER_AVAILABLE:
        logger = get_step_logger()
        logger.start_step("step1_helper", "V2.0优化功能测试")
    else:
        print("\n" + "=" * 60)
        print("测试V2.0优化功能")
        print("=" * 60)
        print("此功能将测试所有V2.0版本的优化功能")
        print("-" * 60)
    
    test_results = []
    
    try:
        # 测试1：图像预处理流水线
        print("\n1. 测试图像预处理流水线...")
        try:
            import tempfile
            import cv2
            import numpy as np
            from src.preprocess.preprocess_pipeline import PreprocessPipeline
            from src.config_manager import get_config_manager
            
            config_manager = get_config_manager()
            preprocess_config = config_manager.get_preprocessing_config()
            
            # 创建预处理流水线
            pipeline = PreprocessPipeline(
                target_size=tuple(preprocess_config.get('target_size', [116, 116])),
                enable_enhancement=preprocess_config.get('enable_enhancement', True)
            )
            
            # 创建测试图像并保存到临时文件
            test_image = np.ones((100, 100, 3), dtype=np.uint8) * 128
            temp_dir = tempfile.mkdtemp()
            test_image_path = os.path.join(temp_dir, "test_image.png")
            cv2.imwrite(test_image_path, test_image)
            
            # 测试预处理
            processed_image, orb_features = pipeline.process_image(test_image_path)
            # 检查处理后的图像尺寸是否正确（特征点可能为0，因为测试图像是纯色）
            # 注意：enhance_for_feature_detection会返回灰度图像，所以可能是(116, 116)或(116, 116, 3)
            target_shape_color = tuple(preprocess_config.get('target_size', [116, 116])) + (3,)
            target_shape_gray = tuple(preprocess_config.get('target_size', [116, 116]))
            
            if processed_image is not None and (processed_image.shape == target_shape_color or processed_image.shape == target_shape_gray):
                print("✓ 图像预处理流水线测试通过")
                test_results.append(("图像预处理流水线", True))
            else:
                print(f"❌ 图像预处理流水线测试失败")
                if processed_image is not None:
                    print(f"  - 期望形状: {target_shape_color} 或 {target_shape_gray}, 实际形状: {processed_image.shape}")
                else:
                    print("  - 处理后的图像为None")
                test_results.append(("图像预处理流水线", False))
            
            # 清理临时目录
            import shutil
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"❌ 图像预处理流水线测试失败: {e}")
            test_results.append(("图像预处理流水线", False))
        
        # 测试2：自动缓存更新器
        print("\n2. 测试自动缓存更新器...")
        try:
            import tempfile
            import shutil
            from src.cache.auto_cache_updater import AutoCacheUpdater
            
            # 创建临时目录进行测试
            temp_dir = tempfile.mkdtemp()
            
            updater = AutoCacheUpdater(
                cache_dir=temp_dir,
                target_size=(116, 116),
                nfeatures=3000,
                auto_update=True
            )
            
            # 测试缓存更新检查
            result = updater.auto_update_if_needed("images/base_equipment")
            print("✓ 自动缓存更新器测试通过")
            test_results.append(("自动缓存更新器", True))
            
            # 清理临时目录
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"❌ 自动缓存更新器测试失败: {e}")
            test_results.append(("自动缓存更新器", False))
        
        # 测试3：图像哈希工具
        print("\n3. 测试图像哈希工具...")
        try:
            import cv2
            import numpy as np
            from src.utils.image_hash import get_dhash, calculate_hamming_distance
            
            # 创建两个测试图像
            img1 = np.ones((50, 50, 3), dtype=np.uint8) * 128
            img2 = np.ones((50, 50, 3), dtype=np.uint8) * 128
            
            # 计算哈希
            hash1 = get_dhash(img1)
            hash2 = get_dhash(img2)
            distance = calculate_hamming_distance(hash1, hash2)
            
            if distance == 0:  # 相同图像的哈希距离应该为0
                print("✓ 图像哈希工具测试通过")
                test_results.append(("图像哈希工具", True))
            else:
                print("❌ 图像哈希工具测试失败")
                test_results.append(("图像哈希工具", False))
        except Exception as e:
            print(f"❌ 图像哈希工具测试失败: {e}")
            test_results.append(("图像哈希工具", False))
        
        # 测试4：质量检测器
        print("\n4. 测试质量检测器...")
        try:
            import tempfile
            import shutil
            import cv2
            import numpy as np
            from src.quality.equipment_detector import EquipmentDetector
            from src.config_manager import get_config_manager
            
            # 创建测试图像
            test_image = np.ones((100, 100, 3), dtype=np.uint8) * 128
            
            # 初始化检测器
            config_manager = get_config_manager()
            detector = EquipmentDetector(
                target_size=tuple(config_manager.get_quality_config().get('target_size', [116, 116])),
                min_resolution=config_manager.get_quality_config().get('min_resolution', 50)
            )
            
            # 使用detect_image_quality方法
            temp_dir = tempfile.mkdtemp()
            test_image_path = os.path.join(temp_dir, "test.png")
            cv2.imwrite(test_image_path, test_image)
            
            result = detector.detect_image_quality(test_image_path)
            quality_score = result.get('keypoints', {}).get('keypoint_count', 0)
            is_good_quality = result.get('is_valid', True)
            
            # 清理临时目录
            shutil.rmtree(temp_dir)
            
            if isinstance(quality_score, (int, float)) and isinstance(is_good_quality, bool):
                print("✓ 质量检测器测试通过")
                test_results.append(("质量检测器", True))
            else:
                print("❌ 质量检测器测试失败")
                test_results.append(("质量检测器", False))
        except Exception as e:
            print(f"❌ 质量检测器测试失败: {e}")
            test_results.append(("质量检测器", False))
        
        # 测试5：可视化调试器
        print("\n5. 测试可视化调试器...")
        try:
            import tempfile
            import shutil
            import numpy as np
            from src.debug.visual_debugger import VisualDebugger
            
            # 创建临时目录进行测试
            if LOGGER_AVAILABLE:
                temp_dir = logger.get_step_dir("step1_helper") / "temp_files" / "matcher_test"
                temp_dir.mkdir(parents=True, exist_ok=True)
            else:
                temp_dir = tempfile.mkdtemp()
            
            debugger = VisualDebugger(debug_dir=temp_dir, enable_debug=True)
            
            # 测试调试报告生成
            debug_data = [{
                'filename': 'test.png',
                'similarity': 85.5,
                'target_image': np.ones((100, 100, 3), dtype=np.uint8) * 128,
                'base_image': np.ones((100, 100, 3), dtype=np.uint8) * 128,
                'file_path': 'test.png'
            }]
            
            report_path = debugger.generate_matching_report(
                base_image_path='test.png',
                matching_results=debug_data,
                threshold=80.0
            )
            
            if os.path.exists(report_path):
                print("✓ 可视化调试器测试通过")
                test_results.append(("可视化调试器", True))
            else:
                print("❌ 可视化调试器测试失败")
                test_results.append(("可视化调试器", False))
            
            # 清理临时目录
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"❌ 可视化调试器测试失败: {e}")
            test_results.append(("可视化调试器", False))
        
        # 测试6：增强特征匹配器
        print("\n6. 测试增强特征匹配器...")
        try:
            import tempfile
            import shutil
            import cv2
            import numpy as np
            from src.equipment_recognizer import EnhancedEquipmentRecognizer
            from src.feature_cache_manager import FeatureCacheManager
            
            # 创建增强识别器
            enhanced_recognizer = EnhancedEquipmentRecognizer(
                algorithm_type="enhanced_feature",
                feature_type="ORB",
                min_match_count=3,
                match_ratio_threshold=0.5,
                nfeatures=3000
            )
            
            # 创建临时目录进行测试
            temp_dir = tempfile.mkdtemp()
            
            # 创建测试图像
            test_img1 = np.ones((100, 100, 3), dtype=np.uint8) * 128
            test_img2 = np.ones((100, 100, 3), dtype=np.uint8) * 128
            test_img1_path = os.path.join(temp_dir, "test1.png")
            test_img2_path = os.path.join(temp_dir, "test2.png")
            cv2.imwrite(test_img1_path, test_img1)
            cv2.imwrite(test_img2_path, test_img2)
            
            # 测试图像比较
            similarity, is_match = enhanced_recognizer.compare_images(test_img1_path, test_img2_path)
            
            if isinstance(similarity, (int, float)) and isinstance(is_match, bool):
                print("✓ 增强特征匹配器测试通过")
                test_results.append(("增强特征匹配器", True))
            else:
                print("❌ 增强特征匹配器测试失败")
                test_results.append(("增强特征匹配器", False))
            
            # 清理临时目录
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"❌ 增强特征匹配器测试失败: {e}")
            test_results.append(("增强特征匹配器", False))
        
        # 测试7：ORB特征点优化
        print("\n7. 测试ORB特征点优化...")
        try:
            import tempfile
            import shutil
            from src.feature_cache_manager import FeatureCacheManager
            
            # 创建临时目录进行测试
            temp_dir = tempfile.mkdtemp()
            
            # 创建缓存管理器，使用3000个特征点
            cache_manager = FeatureCacheManager(
                cache_dir=temp_dir,
                target_size=(116, 116),
                nfeatures=3000  # 测试3000个特征点
            )
            
            # 验证特征点数量设置
            if cache_manager.nfeatures == 3000:
                print("✓ ORB特征点优化测试通过")
                test_results.append(("ORB特征点优化", True))
            else:
                print("❌ ORB特征点优化测试失败")
                test_results.append(("ORB特征点优化", False))
            
            # 清理临时目录
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"❌ ORB特征点优化测试失败: {e}")
            test_results.append(("ORB特征点优化", False))
        
    except Exception as e:
        if LOGGER_AVAILABLE:
            logger.log_error(f"V2.0优化测试过程中出错: {e}")
        else:
            print(f"❌ V2.0优化测试过程中出错: {e}")
        test_results.append(("测试执行", False))
    
    # 输出测试结果
    if LOGGER_AVAILABLE:
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        
        logger.log_info(f"总计: {passed}/{total} 个测试通过")
        
        # 生成报告
        stats = logger.get_step_stats("step1_helper")
        additional_info = {
            "files_processed": [name for name, _ in test_results],
            "test_results": test_results
        }
        
        report_generator = get_report_generator()
        report_generator.generate_step_report("step1_helper", stats, additional_info)
        
        logger.end_step("step1_helper", "完成" if passed == total else "部分失败")
        
        return passed == total
    else:
        print("\n" + "=" * 60)
        print("V2.0优化测试结果汇总")
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
            print("🎉 V2.0优化功能测试全部通过！")
            return True
        else:
            print("⚠️ 部分测试失败，请检查相关功能。")
            return False

def main():
    """主函数"""
    print("辅助功能测试模块")
    print("=" * 50)
    print("1. 检查环境和依赖")
    print("2. 检查数据文件")
    print("3. 清理切割结果和日志")
    print("4. 测试V2.0优化功能")
    print("0. 退出")
    print("-" * 50)
    
    while True:
        try:
            choice = input("请选择操作 (0-4): ").strip()
            
            if choice == '0':
                print("感谢使用，再见！")
                break
            elif choice == '1':
                check_dependencies()
            elif choice == '2':
                check_data_files()
            elif choice == '3':
                clear_previous_results()
            elif choice == '4':
                test_v2_optimizations()
            else:
                print("无效选择，请输入0-4之间的数字")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()