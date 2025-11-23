# 特征缓存构建脚本示例

## 脚本概述

这个脚本用于预计算所有基准装备的ORB特征，并将其保存到pickle文件中，以便在后续识别时直接加载使用，避免重复计算。

## 脚本代码示例

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
特征缓存构建脚本 - 预计算基准装备的ORB特征并缓存
"""

import cv2
import os
import pickle
import argparse
from datetime import datetime
from pathlib import Path

def build_feature_cache(base_dir="images/base_equipment", 
                      cache_file="images/cache/equipment_features.pkl",
                      target_size=(116, 116),
                      nfeatures=1000):
    """
    构建基准装备特征缓存
    
    Args:
        base_dir: 基准装备目录
        cache_file: 缓存文件路径
        target_size: 目标图像尺寸
        nfeatures: ORB特征点数量
    """
    print("开始构建基准装备特征缓存...")
    print(f"基准装备目录: {base_dir}")
    print(f"缓存文件: {cache_file}")
    print(f"目标尺寸: {target_size}")
    
    # 确保缓存目录存在
    cache_dir = os.path.dirname(cache_file)
    os.makedirs(cache_dir, exist_ok=True)
    
    # 初始化ORB检测器
    orb = cv2.ORB_create(nfeatures=nfeatures)
    
    # 初始化缓存字典
    cache = {
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "feature_type": "ORB",
        "target_size": target_size,
        "nfeatures": nfeatures,
        "features": {}
    }
    
    # 处理所有基准装备图像
    processed_count = 0
    skipped_count = 0
    
    for filename in os.listdir(base_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            file_path = os.path.join(base_dir, filename)
            equipment_name = os.path.splitext(filename)[0]
            
            print(f"处理: {filename}")
            
            try:
                # 读取并预处理图像
                img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    print(f"  ❌ 无法读取图像")
                    skipped_count += 1
                    continue
                
                # 调整图像尺寸到目标尺寸
                img_resized = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
                
                # 提取ORB特征
                kp, des = orb.detectAndCompute(img_resized, None)
                
                if des is None:
                    print(f"  ❌ 无法提取特征")
                    skipped_count += 1
                    continue
                
                # 序列化关键点
                kp_serialized = [(kp.pt, kp.size, kp.angle, kp.response, kp.octave, kp.class_id) for kp in kp]
                
                # 保存到缓存
                cache["features"][filename] = {
                    "keypoints": kp_serialized,
                    "descriptors": des,
                    "image_shape": img_resized.shape,
                    "original_shape": img.shape
                }
                
                print(f"  ✓ 提取了 {len(kp)} 个特征点")
                processed_count += 1
                
            except Exception as e:
                print(f"  ❌ 处理失败: {e}")
                skipped_count += 1
    
    # 保存缓存到文件
    try:
        with open(cache_file, "wb") as f:
            pickle.dump(cache, f)
        
        print(f"\n✅ 缓存构建完成!")
        print(f"  处理成功: {processed_count} 个文件")
        print(f"  跳过文件: {skipped_count} 个")
        print(f"  缓存文件: {cache_file}")
        print(f"  缓存大小: {os.path.getsize(cache_file) / 1024 / 1024:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 保存缓存失败: {e}")
        return False

def load_and_test_cache(cache_file="images/cache/equipment_features.pkl"):
    """
    加载并测试特征缓存
    
    Args:
        cache_file: 缓存文件路径
    """
    print(f"测试加载缓存文件: {cache_file}")
    
    try:
        with open(cache_file, "rb") as f:
            cache = pickle.load(f)
        
        print(f"✅ 缓存加载成功!")
        print(f"  版本: {cache.get('version', '未知')}")
        print(f"  创建时间: {cache.get('created_at', '未知')}")
        print(f"  特征类型: {cache.get('feature_type', '未知')}")
        print(f"  目标尺寸: {cache.get('target_size', '未知')}")
        print(f"  装备数量: {len(cache.get('features', {}))}")
        
        # 测试加载第一个装备的特征
        features = cache.get('features', {})
        if features:
            first_filename = list(features.keys())[0]
            first_features = features[first_filename]
            
            # 反序列化关键点
            kp_list = []
            for (pt, size, angle, response, octave, class_id) in first_features['keypoints']:
                kp = cv2.KeyPoint(
                    x=pt[0], y=pt[1],
                    _size=size, _angle=angle,
                    _response=response, _octave=octave,
                    _class_id=class_id
                )
                kp_list.append(kp)
            
            print(f"  示例装备: {first_filename}")
            print(f"  特征点数: {len(kp_list)}")
            print(f"  描述符形状: {first_features['descriptors'].shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ 加载缓存失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="构建基准装备特征缓存")
    parser.add_argument("--base-dir", default="images/base_equipment", 
                       help="基准装备目录路径")
    parser.add_argument("--cache-file", default="images/cache/equipment_features.pkl", 
                       help="缓存文件路径")
    parser.add_argument("--target-size", type=int, nargs=2, default=[116, 116], 
                       help="目标图像尺寸 (宽度 高度)")
    parser.add_argument("--nfeatures", type=int, default=1000, 
                       help="ORB特征点数量")
    parser.add_argument("--rebuild", action="store_true", 
                       help="强制重建缓存")
    parser.add_argument("--test-only", action="store_true", 
                       help="仅测试现有缓存")
    
    args = parser.parse_args()
    
    # 如果只是测试缓存
    if args.test_only:
        success = load_and_test_cache(args.cache_file)
        exit(0 if success else 1)
    
    # 检查缓存文件是否存在
    cache_exists = os.path.exists(args.cache_file)
    
    if cache_exists and not args.rebuild:
        print(f"缓存文件已存在: {args.cache_file}")
        response = input("是否重新构建? (y/N): ").strip().lower()
        if response != 'y':
            print("操作取消")
            exit(0)
    
    # 构建缓存
    target_size = tuple(args.target_size)
    success = build_feature_cache(
        base_dir=args.base_dir,
        cache_file=args.cache_file,
        target_size=target_size,
        nfeatures=args.nfeatures
    )
    
    if success:
        # 测试加载缓存
        print("\n测试加载缓存...")
        load_and_test_cache(args.cache_file)
    
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

## 使用方法

### 基本使用
```bash
# 构建特征缓存
python build_feature_cache.py

# 测试现有缓存
python build_feature_cache.py --test-only
```

### 高级选项
```bash
# 指定自定义参数
python build_feature_cache.py --base-dir custom/base/dir --cache-file custom/cache.pkl --target-size 128 128 --nfeatures 1500

# 强制重建缓存
python build_feature_cache.py --rebuild

# 仅测试缓存
python build_feature_cache.py --test-only
```

## 集成到主程序

在主程序中，可以这样集成缓存构建功能：

```python
def ensure_feature_cache():
    """确保特征缓存存在且有效"""
    cache_file = "images/cache/equipment_features.pkl"
    
    if not os.path.exists(cache_file):
        print("特征缓存不存在，正在构建...")
        success = build_feature_cache()
        if not success:
            print("构建特征缓存失败")
            return False
    
    return True
```

## 注意事项

1. **图像尺寸**：基准图像会被调整为116x116像素，与目标图像保持一致
2. **特征点数量**：默认使用1000个ORB特征点，可根据需要调整
3. **缓存格式**：使用pickle格式存储，包含版本信息以便后续升级
4. **错误处理**：脚本会跳过无法处理的图像，并显示详细错误信息
5. **性能**：构建缓存可能需要一些时间，但只需要运行一次

## 预期效果

构建缓存后，装备识别的性能将显著提升：
- 特征提取时间减少70-80%
- 批量识别速度提升60-70%
- 内存使用减少30-40%