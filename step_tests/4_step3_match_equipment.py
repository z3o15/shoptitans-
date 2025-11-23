#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤3：装备识别匹配功能测试
使用ORB特征匹配算法，仅支持基准装备缓存
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

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def log_message(tag, message):
    """统一日志输出格式"""
    # 简化标签显示
    if tag in ['INIT', 'INFO']:
        print(f"[INFO] {message}")
    elif tag == 'CACHE':
        print(f"[CACHE] {message}")
    elif tag == 'MATCH':
        print(f"[MATCH] {message}")
    elif tag == 'RESULT':
        print(f"[RESULT] {message}")
    elif tag == 'ERROR':
        print(f"[ERROR] {message}")

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
        log_message("ERROR", f"缺少依赖包: {', '.join(missing_packages)}")
        log_message("ERROR", "正在安装依赖...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            log_message("INIT", "依赖安装完成")
            return True
        except subprocess.CalledProcessError:
            log_message("ERROR", "依赖安装失败，请手动运行: pip install -r requirements.txt")
            return False
    
    return True

def step3_match_equipment(auto_mode=True, auto_threshold=None, enable_debug=False):
    """步骤3：装备识别匹配"""
    log_message("INIT", "开始装备识别匹配")
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 检查基准装备
    base_equipment_dir = "images/base_equipment"
    if not os.path.exists(base_equipment_dir):
        log_message("ERROR", f"基准装备目录不存在: {base_equipment_dir}")
        return False
    
    base_image_files = [f for f in os.listdir(base_equipment_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    if not base_image_files:
        log_message("ERROR", "未找到基准装备图片")
        return False
    
    # 导入必要模块
    try:
        from src.config_manager import get_config_manager
        from src.feature_cache_manager import FeatureCacheManager
        from src.equipment_recognizer import EnhancedEquipmentRecognizer
    except ImportError as e:
        log_message("ERROR", f"导入模块失败: {e}")
        return False
    
    # 获取配置
    config_manager = get_config_manager()
    feature_cache_config = config_manager.get_feature_cache_config()
    recognition_config = config_manager.get_recognition_config()
    
    # 获取算法类型
    algorithm_type = recognition_config.get("algorithm_type", "enhanced_feature")
    log_message("INIT", f"使用算法: {algorithm_type}")
    
    # 检查切割装备
    # 根据算法类型选择不同的图像源
    if algorithm_type == "advanced":
        # 高级彩色模板匹配使用原始彩色图像
        cropped_equipment_dir = "images/cropped_equipment_original/20251123_214236"
        log_message("INIT", "高级算法：使用原始彩色图像")
    else:
        # 其他算法使用预处理后的图像
        cropped_equipment_dir = "images/cropped_equipment"
        log_message("INIT", f"其他算法：使用预处理图像")
        
    if not os.path.exists(cropped_equipment_dir):
        log_message("ERROR", f"切割装备目录不存在: {cropped_equipment_dir}")
        return False
    
    # 查找最新的时间目录（仅对非高级算法）
    if algorithm_type != "advanced":
        subdirs = [d for d in os.listdir(cropped_equipment_dir)
                  if os.path.isdir(os.path.join(cropped_equipment_dir, d))]
        
        if subdirs:
            latest_dir = sorted(subdirs)[-1]
            latest_dir_path = os.path.join(cropped_equipment_dir, latest_dir)
            log_message("INIT", f"使用时间目录: {latest_dir}")
            cropped_files = [os.path.abspath(os.path.join(latest_dir_path, f)) for f in os.listdir(latest_dir_path)
                           if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        else:
            cropped_files = [os.path.abspath(os.path.join(cropped_equipment_dir, f)) for f in os.listdir(cropped_equipment_dir)
                           if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    else:
        # 高级算法直接使用指定目录
        cropped_files = [os.path.abspath(os.path.join(cropped_equipment_dir, f)) for f in os.listdir(cropped_equipment_dir)
                       if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    if not cropped_files:
        log_message("ERROR", "未找到切割装备图片，请先完成步骤2")
        return False
    
    # 设置阈值
    if auto_threshold is not None:
        threshold = auto_threshold
    else:
        threshold = config_manager.get_default_threshold()
    
    log_message("INIT", f"匹配阈值: {threshold}%")
    log_message("INIT", f"基准装备数量: {len(base_image_files)}")
    log_message("INIT", f"切割装备数量: {len(cropped_files)}")
    
    # 获取配置
    config_manager = get_config_manager()
    feature_cache_config = config_manager.get_feature_cache_config()
    recognition_config = config_manager.get_recognition_config()
    
    # 获取算法类型
    algorithm_type = recognition_config.get("algorithm_type", "enhanced_feature")
    log_message("INIT", f"使用算法: {algorithm_type}")
    
    # 设置阈值
    if auto_threshold is not None:
        threshold = auto_threshold
    else:
        threshold = config_manager.get_default_threshold()
    
    log_message("INIT", f"匹配阈值: {threshold}%")
    log_message("INIT", f"基准装备数量: {len(base_image_files)}")
    
    # 初始化特征缓存管理器（仅用于基准装备）
    # 简化缓存初始化输出
    
    # 临时禁用详细输出，只显示关键信息
    os.environ['CACHE_VERBOSE'] = 'false'
    
    cache_manager = FeatureCacheManager(
        cache_dir=feature_cache_config.get('cache_dir', 'images/cache'),
        target_size=tuple(feature_cache_config.get('target_size', [116, 116])),
        nfeatures=feature_cache_config.get('nfeatures', 3000)
    )
    
    # 构建或验证缓存（仅基准装备）
    if not cache_manager.is_cache_valid():
        cache_manager.build_cache()
        log_message("CACHE", "特征缓存构建完成")
    
    # 创建识别器（根据配置选择算法）
    # 简化初始化输出
    
    # 临时禁用详细输出
    os.environ['RECOGNIZER_VERBOSE'] = 'false'
    
    recognizer = EnhancedEquipmentRecognizer(
        algorithm_type=algorithm_type,
        feature_type=recognition_config.get("feature_type", "ORB"),
        min_match_count=recognition_config.get('min_match_count', 8),
        match_ratio_threshold=recognition_config.get('match_ratio_threshold', 0.75),
        use_cache=recognition_config.get('use_cache', True),
        cache_dir=feature_cache_config.get('cache_dir', 'images/cache'),
        target_size=tuple(recognition_config.get('target_size', [116, 116])),
        nfeatures=recognition_config.get('nfeatures', 3000),
        enable_masking=recognition_config.get('enable_masking', True),
        enable_histogram=recognition_config.get('enable_histogram', True)
    )
    
    # 执行匹配
    total_matches = 0
    match_results = []
    
    # 简化匹配开始信息
    
    # 根据算法类型获取基准装备信息
    equipment_names = []
    if algorithm_type == "enhanced_feature" and hasattr(recognizer, 'enhanced_feature_recognizer') and recognizer.enhanced_feature_recognizer:
        equipment_names = recognizer.enhanced_feature_recognizer.cache_manager.get_all_equipment_names()
        if len(equipment_names) > 0:
            log_message("MATCH", f"缓存中有 {len(equipment_names)} 个基准装备")
    elif algorithm_type == "advanced" and hasattr(recognizer, 'advanced_recognizer') and recognizer.advanced_recognizer:
        # 高级算法直接从基准装备目录获取文件列表
        equipment_names = [os.path.splitext(f)[0] for f in base_image_files]
        log_message("MATCH", f"找到 {len(equipment_names)} 个基准装备")
    elif algorithm_type == "feature" and hasattr(recognizer, 'feature_recognizer') and recognizer.feature_recognizer:
        equipment_names = [os.path.splitext(f)[0] for f in base_image_files]
        log_message("MATCH", f"找到 {len(equipment_names)} 个基准装备")
    else:
        log_message("ERROR", f"未知的算法类型或识别器未初始化: {algorithm_type}")
        return False
    
    # 简化缓存信息输出
    
    # 对每个切割图片进行匹配
    for cropped_file in cropped_files:
        cropped_filename = os.path.basename(cropped_file)
        # 提取原始序号（不带扩展名）
        original_name = os.path.splitext(cropped_filename)[0]
        
        # 简化匹配输出
        
        best_match = None
        best_confidence = 0
        
        # 遍历所有基准装备进行匹配
        for equipment_name in equipment_names:
            try:
                # 确保路径格式正确
                normalized_path = os.path.normpath(cropped_file)
                
                # 根据算法类型使用不同的匹配方法
                if algorithm_type == "enhanced_feature" and hasattr(recognizer, 'enhanced_feature_recognizer') and recognizer.enhanced_feature_recognizer:
                    # 使用缓存特征进行匹配
                    result = recognizer.enhanced_feature_recognizer._recognize_with_cache(
                        equipment_name, normalized_path
                    )
                elif algorithm_type == "advanced" and hasattr(recognizer, 'advanced_recognizer') and recognizer.advanced_recognizer:
                    # 使用高级彩色模板匹配
                    base_image_path = os.path.join(base_equipment_dir, f"{equipment_name}.webp")
                    if not os.path.exists(base_image_path):
                        # 尝试其他扩展名
                        for ext in ['.png', '.jpg', '.jpeg']:
                            test_path = os.path.join(base_equipment_dir, f"{equipment_name}{ext}")
                            if os.path.exists(test_path):
                                base_image_path = test_path
                                break
                    
                    if os.path.exists(base_image_path):
                        result = recognizer.advanced_recognizer.recognize_equipment(
                            base_image_path, normalized_path
                        )
                        # 转换结果格式以保持兼容性
                        result = type('MatchResult', (), {
                            'item_base': result.item_base,
                            'confidence': result.confidence,
                            'item_name': result.item_name
                        })()
                    else:
                        continue
                elif algorithm_type == "feature" and hasattr(recognizer, 'feature_recognizer') and recognizer.feature_recognizer:
                    # 使用特征匹配
                    base_image_path = os.path.join(base_equipment_dir, f"{equipment_name}.webp")
                    if not os.path.exists(base_image_path):
                        # 尝试其他扩展名
                        for ext in ['.png', '.jpg', '.jpeg']:
                            test_path = os.path.join(base_equipment_dir, f"{equipment_name}{ext}")
                            if os.path.exists(test_path):
                                base_image_path = test_path
                                break
                    
                    if os.path.exists(base_image_path):
                        result = recognizer.feature_recognizer.recognize_equipment(
                            base_image_path, normalized_path
                        )
                    else:
                        continue
                else:
                    continue
                
                if result.confidence > best_confidence:
                    best_confidence = result.confidence
                    best_match = result
                    
            except Exception as e:
                # 简化错误记录
                pass
        
        # 无论是否超过阈值都进行重命名，但只记录超过阈值的匹配
        if best_match:
            # 保存匹配结果
            match_results.append({
                'cropped_file': cropped_filename,
                'matched_equipment': best_match.item_base,
                'confidence': best_match.confidence
            })
            
            # 重命名文件：保留序号，添加装备名称，使用jpg格式
            try:
                old_path = cropped_file
                dir_path = os.path.dirname(old_path)
                new_name = f"{original_name}_{best_match.item_base}.jpg"
                new_path = os.path.join(dir_path, new_name)
                
                # 如果原文件是jpg格式，直接重命名；如果是其他格式，转换格式
                if old_path.lower().endswith('.jpg') or old_path.lower().endswith('.jpeg'):
                    if old_path != new_path:
                        os.rename(old_path, new_path)
                else:
                    # 转换图片格式为jpg
                    img = Image.open(old_path)
                    if img.mode == 'RGBA':
                        # 处理透明背景，转换为白色背景
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    img.save(new_path, 'JPEG', quality=95)
                    os.remove(old_path)
                
                # 只有超过阈值的匹配才计入总数
                if best_match.confidence >= threshold:
                    total_matches += 1
                    log_message("MATCH", f"匹配成功: {cropped_filename} → {new_name} (置信度: {best_match.confidence:.1f}%)")
                else:
                    log_message("MATCH", f"低置信度匹配: {cropped_filename} → {new_name} (置信度: {best_match.confidence:.1f}%)")
                    
            except Exception as e:
                log_message("ERROR", f"重命名文件失败 {cropped_filename}: {e}")
        else:
            log_message("MATCH", f"匹配切割图片: {cropped_filename} → 无匹配结果")
    
    # 输出最终结果
    log_message("RESULT", f"匹配完成，总共找到 {total_matches} 个匹配项")
    
    if enable_debug and match_results:
        try:
            from src.debug.visual_debugger import VisualDebugger
            log_message("INIT", "生成可视化调试报告")
            
            debugger = VisualDebugger(
                debug_dir="debug_output",
                enable_debug=True
            )
            
            # 生成调试报告
            report_path = debugger.generate_matching_report(
                base_image_path=os.path.join(base_equipment_dir, sorted(base_image_files)[0]),
                matching_results=match_results[:10],  # 只显示前10个结果
                threshold=threshold
            )
            log_message("RESULT", f"可视化调试报告已生成: {report_path}")
        except ImportError:
            log_message("ERROR", "可视化调试器不可用")
        except Exception as e:
            log_message("ERROR", f"生成调试报告失败: {e}")
    
    return True

def main():
    """主函数"""
    log_message("INIT", "步骤3：装备识别匹配功能测试模块")
    
    try:
        step3_match_equipment(auto_mode=False)
    except KeyboardInterrupt:
        log_message("INIT", "程序被用户中断")
    except Exception as e:
        log_message("ERROR", f"发生错误: {e}")

if __name__ == "__main__":
    main()