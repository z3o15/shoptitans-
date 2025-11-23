#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
特征缓存系统使用示例
演示如何使用特征缓存管理器和增强特征匹配器
"""

import os
import sys
import time

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from feature_cache_manager import FeatureCacheManager
from enhanced_feature_matcher import EnhancedFeatureMatcher
from config_manager import get_config_manager

def main():
    """主函数"""
    print("特征缓存系统使用示例")
    print("=" * 50)
    
    # 获取配置管理器
    config_manager = get_config_manager()
    feature_cache_config = config_manager.get_feature_cache_config()
    
    # 初始化特征缓存管理器
    cache_manager = FeatureCacheManager(
        cache_dir=feature_cache_config.get('cache_dir', 'images/cache'),
        target_size=tuple(feature_cache_config.get('target_size', [116, 116])),
        nfeatures=feature_cache_config.get('nfeatures', 1000)
    )
    
    # 检查缓存状态
    if not cache_manager.is_cache_valid():
        print("缓存无效或不存在，正在构建...")
        cache_manager.build_cache()
        print("缓存构建完成！")
    else:
        print("缓存有效，直接使用...")
        cache_info = cache_manager.get_cache_info()
        print(f"缓存信息: {cache_info}")
    
    # 初始化增强特征匹配器
    matcher = EnhancedFeatureMatcher(
        cache_manager=cache_manager,
        feature_type=feature_cache_config.get('feature_type', 'ORB'),
        min_match_count=feature_cache_config.get('min_match_count', 3),
        match_ratio_threshold=feature_cache_config.get('match_ratio_threshold', 0.5)
    )
    
    # 示例：比较两个图像
    base_image_path = "images/base_equipment/1000bp.webp"
    target_image_path = "images/base_equipment/abyssal.webp"
    
    if os.path.exists(base_image_path) and os.path.exists(target_image_path):
        print(f"\n比较图像: {base_image_path} vs {target_image_path}")
        
        start_time = time.time()
        result = matcher.compare_images(base_image_path, target_image_path)
        end_time = time.time()
        
        print(f"匹配结果: {result}")
        print(f"匹配时间: {end_time - start_time:.4f}秒")
    else:
        print("示例图像不存在，跳过比较示例")
    
    print("\n示例完成！")

if __name__ == "__main__":
    main()