#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建装备特征缓存
用于预先计算所有基准装备的特征，加速后续匹配过程
"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.core.feature_cache import build_feature_cache

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='构建装备特征缓存',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  python build_cache.py output_enter_image/base_equipment                    # 构建缓存
  python build_cache.py output_enter_image/base_equipment --force          # 强制重新构建
        '''
    )

    parser.add_argument('base_dir', type=str, help='基准装备目录路径')
    parser.add_argument('--force', action='store_true', help='强制重新计算所有特征')

    args = parser.parse_args()

    print("=" * 60)
    print("装备特征缓存构建工具")
    print("=" * 60)

    try:
        base_path = Path(args.base_dir)
        if not base_path.exists():
            print(f"错误: 基准装备目录不存在: {base_path}")
            return 1

        if not base_path.is_dir():
            print(f"错误: 指定路径不是目录: {base_path}")
            return 1

        print(f"基准装备目录: {base_path}")
        print(f"强制重新计算: {'是' if args.force else '否'}")
        print()

        # 构建缓存
        cache = build_feature_cache(str(base_path), args.force)

        # 显示缓存信息
        cache_info = cache.get_cache_info()
        print("\n缓存信息:")
        print(f"  缓存目录: {cache_info['cache_dir']}")
        print(f"  缓存特征数: {cache_info['total_features']}")
        print(f"  缓存索引存在: {'是' if cache_info['cache_exists'] else '否'}")

        print("\n[OK] 特征缓存构建完成!")
        print("现在可以使用缓存优化的匹配功能了。")

        return 0

    except KeyboardInterrupt:
        print("\n用户中断了缓存构建")
        return 130
    except Exception as e:
        print(f"构建缓存时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())