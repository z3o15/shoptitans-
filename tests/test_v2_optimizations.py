#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v2.0优化功能综合测试脚本
测试所有修复和新增功能
"""

import os
import sys
import cv2
import numpy as np
import json
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 导入测试模块
try:
    from src.utils.image_hash import get_dhash, calculate_hamming_distance
    from src.equipment_recognizer import EnhancedEquipmentRecognizer
    from src.feature_matcher import FeatureEquipmentRecognizer
    from src.enhanced_feature_matcher import EnhancedFeatureEquipmentRecognizer
    from src.cache.auto_cache_updater import AutoCacheUpdater
    from src.quality.equipment_detector import EquipmentDetector
    from src.debug.visual_debugger import VisualDebugger
    from src.preprocess.preprocess_pipeline import PreprocessPipeline
    from src.preprocess.background_remover import BackgroundRemover
    from src.preprocess.enhancer import ImageEnhancer
    from src.preprocess.resizer import ImageResizer
    print("✓ 所有模块导入成功")
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    sys.exit(1)


def test_image_hash():
    """测试图像哈希功能"""
    print("\n" + "="*60)
    print("测试图像哈希功能")
    print("="*60)
    
    try:
        # 创建测试图像
        test_image = np.random.randint(0, 255, (116, 116), dtype=np.uint8)
        
        # 计算dHash
        dhash = get_dhash(test_image)
        print(f"✓ dHash计算成功: {dhash} (类型: {type(dhash)})")
        
        # 测试汉明距离
        test_image2 = np.random.randint(0, 255, (116, 116), dtype=np.uint8)
        dhash2 = get_dhash(test_image2)
        distance = calculate_hamming_distance(dhash, dhash2)
        print(f"✓ 汉明距离计算成功: {distance}")
        
        return True
    except Exception as e:
        print(f"❌ 图像哈希测试失败: {e}")
        return False


def test_enhanced_feature_matching():
    """测试增强特征匹配功能"""
    print("\n" + "="*60)
    print("测试增强特征匹配功能")
    print("="*60)
    
    try:
        # 创建测试图像
        template_img = np.random.randint(50, 200, (116, 116, 3), dtype=np.uint8)
        query_img = np.random.randint(50, 200, (116, 116, 3), dtype=np.uint8)
        
        # 创建临时测试目录
        test_dir = "test_enhanced_feature"
        os.makedirs(test_dir, exist_ok=True)
        
        template_path = os.path.join(test_dir, "template.png")
        query_path = os.path.join(test_dir, "query.png")
        
        cv2.imwrite(template_path, template_img)
        cv2.imwrite(query_path, query_img)
        
        # 创建增强特征匹配器
        from src.feature_matcher import FeatureType
        recognizer = EnhancedFeatureEquipmentRecognizer(
            feature_type=FeatureType.ORB,
            min_match_count=5,
            match_ratio_threshold=0.7,
            use_cache=False,  # 测试时不使用缓存
            nfeatures=1000
        )
        
        # 进行匹配
        result = recognizer.recognize_equipment(template_path, query_path)
        print(f"✓ 增强特征匹配成功")
        print(f"  - 匹配数量: {result.match_count}")
        print(f"  - 单应性内点: {result.homography_inliers}")
        print(f"  - 匹配比例: {result.match_ratio:.4f}")
        print(f"  - 置信度: {result.confidence:.2f}%")
        
        # 清理测试文件
        import shutil
        shutil.rmtree(test_dir)
        
        return True
    except Exception as e:
        print(f"❌ 增强特征匹配测试失败: {e}")
        return False


def test_enhanced_equipment_recognizer():
    """测试增强装备识别器"""
    print("\n" + "="*60)
    print("测试增强装备识别器")
    print("="*60)
    
    try:
        # 创建测试图像
        template_img = np.random.randint(50, 200, (116, 116, 3), dtype=np.uint8)
        query_img = np.random.randint(50, 200, (116, 116, 3), dtype=np.uint8)
        
        # 创建临时测试目录
        test_dir = "test_enhanced_recognizer"
        os.makedirs(test_dir, exist_ok=True)
        
        template_path = os.path.join(test_dir, "template.png")
        query_path = os.path.join(test_dir, "query.png")
        
        cv2.imwrite(template_path, template_img)
        cv2.imwrite(query_path, query_img)
        
        # 创建增强装备识别器
        recognizer = EnhancedEquipmentRecognizer(
            default_threshold=50,
            algorithm_type="enhanced_feature",
            use_cache=False,  # 测试时不使用缓存
            auto_update_cache=False,
            nfeatures=1000
        )
        
        # 测试get_dhash方法
        if hasattr(recognizer, 'get_dhash'):
            dhash = recognizer.get_dhash(template_path)
            if isinstance(dhash, int):
                # 如果是整数，转换为二进制字符串
                dhash_str = bin(dhash)[2:]  # 去掉'0b'前缀
                print(f"✓ get_dhash方法可用: {dhash_str[:20]}...")
            else:
                print(f"✓ get_dhash方法可用: {str(dhash)[:20]}...")
        else:
            print("❌ get_dhash方法不可用")
            return False
        
        # 测试图像比较
        similarity, is_match = recognizer.compare_images(template_path, query_path)
        print(f"✓ 图像比较成功")
        print(f"  - 相似度: {similarity:.2f}%")
        print(f"  - 是否匹配: {is_match}")
        
        # 测试算法信息
        info = recognizer.get_algorithm_info()
        print(f"✓ 算法信息获取成功")
        print(f"  - 当前算法: {info['algorithm_name']}")
        
        # 清理测试文件
        import shutil
        shutil.rmtree(test_dir)
        
        return True
    except Exception as e:
        print(f"❌ 增强装备识别器测试失败: {e}")
        return False


def test_auto_cache_updater():
    """测试自动缓存更新器"""
    print("\n" + "="*60)
    print("测试自动缓存更新器")
    print("="*60)
    
    try:
        # 创建测试目录
        test_dir = "test_cache_equipment"
        cache_dir = "test_cache"
        os.makedirs(test_dir, exist_ok=True)
        
        # 创建测试图像
        test_images = [
            ("equipment1.png", np.random.randint(50, 200, (116, 116, 3), dtype=np.uint8)),
            ("equipment2.png", np.random.randint(50, 200, (116, 116, 3), dtype=np.uint8)),
            ("equipment3.png", np.random.randint(50, 200, (116, 116, 3), dtype=np.uint8))
        ]
        
        for filename, image in test_images:
            cv2.imwrite(os.path.join(test_dir, filename), image)
        
        # 创建自动缓存更新器
        updater = AutoCacheUpdater(cache_dir=cache_dir, auto_update=True)
        
        # 测试更新缓存
        success = updater.update_cache(test_dir, incremental_only=False)
        print(f"✓ 缓存更新结果: {'成功' if success else '失败'}")
        
        # 测试缓存状态
        status = updater.get_cache_status()
        print(f"✓ 缓存状态获取成功")
        print(f"  - 缓存存在: {status['cache_exists']}")
        print(f"  - 装备数量: {status['equipment_count']}")
        
        # 测试检查更新
        check_result = updater.check_for_updates(test_dir)
        print(f"✓ 更新检查成功")
        print(f"  - 需要更新: {check_result['needs_update']}")
        
        # 添加新图像测试增量更新
        new_image = np.random.randint(50, 200, (116, 116, 3), dtype=np.uint8)
        cv2.imwrite(os.path.join(test_dir, "equipment4.png"), new_image)
        
        success = updater.update_cache(test_dir, incremental_only=True)
        print(f"✓ 增量更新结果: {'成功' if success else '失败'}")
        
        # 清理测试文件
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
        
        return True
    except Exception as e:
        print(f"❌ 自动缓存更新器测试失败: {e}")
        return False


def test_equipment_detector():
    """测试装备图像检测器"""
    print("\n" + "="*60)
    print("测试装备图像检测器")
    print("="*60)
    
    try:
        # 创建测试目录
        test_dir = "test_quality_equipment"
        output_dir = "test_quality_output"
        os.makedirs(test_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建测试图像
        test_images = [
            ("valid_image.png", np.random.randint(50, 200, (116, 116, 3), dtype=np.uint8)),
            ("low_resolution.png", np.random.randint(50, 200, (30, 30, 3), dtype=np.uint8)),
            ("empty_image.png", np.zeros((116, 116, 3), dtype=np.uint8)),
            ("duplicate_image.png", np.random.randint(50, 200, (116, 116, 3), dtype=np.uint8))
        ]
        
        for filename, image in test_images:
            cv2.imwrite(os.path.join(test_dir, filename), image)
        
        # 创建重复图像
        cv2.imwrite(os.path.join(test_dir, "duplicate_image_copy.png"), test_images[-1][1])
        
        # 创建检测器
        detector = EquipmentDetector()
        
        # 测试单个图像检测
        result = detector.detect_image_quality(os.path.join(test_dir, "valid_image.png"))
        print(f"✓ 单个图像检测成功")
        print(f"  - 图像有效: {result['is_valid']}")
        print(f"  - 问题数量: {len(result['issues'])}")
        
        # 测试目录检测
        directory_result = detector.detect_directory(test_dir, output_dir)
        print(f"✓ 目录检测成功")
        print(f"  - 总图像数: {directory_result['total_count']}")
        print(f"  - 有效图像: {directory_result['valid_count']}")
        print(f"  - 无效图像: {directory_result['invalid_count']}")
        
        # 清理测试文件
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        
        return True
    except Exception as e:
        print(f"❌ 装备图像检测器测试失败: {e}")
        return False


def test_visual_debugger():
    """测试可视化调试器"""
    print("\n" + "="*60)
    print("测试可视化调试器")
    print("="*60)
    
    try:
        # 创建测试目录
        test_dir = "test_debug_equipment"
        debug_dir = "test_debug_output"
        os.makedirs(test_dir, exist_ok=True)
        
        # 创建测试图像
        template_img = np.random.randint(50, 200, (116, 116, 3), dtype=np.uint8)
        query_img = np.random.randint(50, 200, (116, 116, 3), dtype=np.uint8)
        
        template_path = os.path.join(test_dir, "template.png")
        query_path = os.path.join(test_dir, "query.png")
        
        cv2.imwrite(template_path, template_img)
        cv2.imwrite(query_path, query_img)
        
        # 创建测试关键点
        template_kp = [
            cv2.KeyPoint(x=20, y=20, size=10, angle=45, response=0.8),
            cv2.KeyPoint(x=50, y=50, size=8, angle=30, response=0.7),
            cv2.KeyPoint(x=80, y=80, size=12, angle=60, response=0.9)
        ]
        
        query_kp = [
            cv2.KeyPoint(x=25, y=25, size=10, angle=50, response=0.8),
            cv2.KeyPoint(x=55, y=55, size=8, angle=35, response=0.7),
            cv2.KeyPoint(x=85, y=85, size=12, angle=65, response=0.9)
        ]
        
        # 序列化关键点
        template_kp_serialized = [(kp.pt, kp.size, kp.angle, kp.response, kp.octave, kp.class_id) for kp in template_kp]
        query_kp_serialized = [(kp.pt, kp.size, kp.angle, kp.response, kp.octave, kp.class_id) for kp in query_kp]
        
        # 创建测试匹配
        matches = [
            cv2.DMatch(_queryIdx=0, _trainIdx=0, _distance=0.1),
            cv2.DMatch(_queryIdx=1, _trainIdx=1, _distance=0.2),
            cv2.DMatch(_queryIdx=2, _trainIdx=2, _distance=0.15)
        ]
        
        # 创建测试单应性矩阵
        H = np.array([[1.0, 0.0, 5.0], [0.0, 1.0, 5.0], [0.0, 0.0, 1.0]])
        
        # 创建调试器
        debugger = VisualDebugger(debug_dir=debug_dir, enable_debug=True)
        
        # 测试单个匹配结果调试
        result_paths = debugger.debug_match_result(
            template_path=template_path,
            query_path=query_path,
            template_kp_serialized=template_kp_serialized,
            query_kp_serialized=query_kp_serialized,
            matches=matches,
            H=H,
            match_score=0.85,
            equipment_name="test_equipment"
        )
        
        print(f"✓ 单个匹配调试成功")
        print(f"  - 生成文件数: {len(result_paths)}")
        
        # 测试批量结果调试
        batch_results = [
            {"equipment_name": f"equipment_{i}", "match_score": 0.5 + i * 0.05}
            for i in range(10)
        ]
        
        batch_report_path = debugger.debug_batch_results(batch_results)
        print(f"✓ 批量调试成功")
        print(f"  - 报告路径: {batch_report_path}")
        
        # 清理测试文件
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        if os.path.exists(debug_dir):
            shutil.rmtree(debug_dir)
        
        return True
    except Exception as e:
        print(f"❌ 可视化调试器测试失败: {e}")
        return False


def test_preprocess_pipeline():
    """测试预处理流水线"""
    print("\n" + "="*60)
    print("测试预处理流水线")
    print("="*60)
    
    try:
        # 创建测试图像
        test_image = np.random.randint(50, 200, (200, 200, 3), dtype=np.uint8)
        
        # 创建临时测试目录
        test_dir = "test_preprocess"
        os.makedirs(test_dir, exist_ok=True)
        
        input_path = os.path.join(test_dir, "input.png")
        output_path = os.path.join(test_dir, "output.png")
        
        cv2.imwrite(input_path, test_image)
        
        # 测试背景去除器
        remover = BackgroundRemover()
        image = cv2.imread(input_path)
        result = remover.remove_circular_background(image)
        print(f"✓ 背景去除器测试成功: {type(result)}")
        
        # 测试图像增强器
        enhancer = ImageEnhancer()
        image = cv2.imread(input_path)
        result = enhancer.enhance_for_feature_detection(image)
        cv2.imwrite(output_path, result)
        print(f"✓ 图像增强器测试成功: {type(result)}")
        
        # 测试图像尺寸调整器
        resizer = ImageResizer(target_size=(116, 116))
        image = cv2.imread(input_path)
        result = resizer.resize(image)
        cv2.imwrite(output_path, result)
        print(f"✓ 图像尺寸调整器测试成功: {result.shape}")
        
        # 测试预处理流水线
        pipeline = PreprocessPipeline()
        result_image, orb_features = pipeline.process_image(input_path)
        print(f"✓ 预处理流水线测试成功: {type(result_image)}, 特征点数: {len(orb_features[0]) if orb_features[0] else 0}")
        
        # 清理测试文件
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        return True
    except Exception as e:
        print(f"❌ 预处理流水线测试失败: {e}")
        return False


def test_config_loading():
    """测试配置加载"""
    print("\n" + "="*60)
    print("测试配置加载")
    print("="*60)
    
    try:
        # 检查配置文件是否存在
        config_path = "config.json"
        if not os.path.exists(config_path):
            print(f"❌ 配置文件不存在: {config_path}")
            return False
        
        # 加载配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"✓ 配置文件加载成功")
        
        # 检查关键配置项
        required_sections = ['recognition', 'preprocessing', 'feature_cache', 'quality_check', 'debug']
        for section in required_sections:
            if section in config:
                print(f"  - {section} 配置存在")
            else:
                print(f"  - {section} 配置缺失")
        
        # 检查算法类型
        algorithm_type = config.get('recognition', {}).get('algorithm_type', 'unknown')
        print(f"  - 算法类型: {algorithm_type}")
        
        # 检查目标尺寸
        target_size = config.get('recognition', {}).get('target_size', [116, 116])
        print(f"  - 目标尺寸: {target_size}")
        
        return True
    except Exception as e:
        print(f"❌ 配置加载测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("开始运行v2.0优化功能综合测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试列表
    tests = [
        ("图像哈希功能", test_image_hash),
        ("增强特征匹配功能", test_enhanced_feature_matching),
        ("增强装备识别器", test_enhanced_equipment_recognizer),
        ("自动缓存更新器", test_auto_cache_updater),
        ("装备图像检测器", test_equipment_detector),
        ("可视化调试器", test_visual_debugger),
        ("预处理流水线", test_preprocess_pipeline),
        ("配置加载", test_config_loading)
    ]
    
    # 运行测试
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果摘要
    print("\n" + "="*60)
    print("测试结果摘要")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, success in results:
        status = "✓ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {len(results)} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    print(f"通过率: {passed/len(results)*100:.1f}%")
    
    # 保存测试报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(results),
        "passed": passed,
        "failed": failed,
        "pass_rate": passed/len(results)*100,
        "results": [{"name": name, "passed": success} for name, success in results]
    }
    
    with open("v2_optimization_test_report.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试报告已保存到: v2_optimization_test_report.json")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)