#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤2（修订版）：你指定的最终行为
====================================================
1. 所有裁剪出的圆形透明图（*_circle.png）必须保存到：
      images/cropped_equipment_marker/transparent/
2. 不再使用时间戳文件夹，所有输出直接放在主目录（扁平结构）。
3. 保留你提供的优化重构代码结构，不改动现有框架接口。

只做你要求的两项变更：
- 圆形透明图输出到 marker/transparent
- 移除时间戳目录，改为直接输出嗯
"""

from __future__ import annotations
import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw

# Project root
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

LOGGER_AVAILABLE = False

# ============================================================
# 工具函数
# ============================================================
def check_dependencies() -> bool:
    try:
        import cv2  # noqa
        import numpy  # noqa
        return True
    except Exception as e:
        print(f"依赖异常: {e}")
        return False


def clean_dir(path: Path) -> None:
    if not path.exists(): return
    for p in path.iterdir():
        try:
            if p.is_file() or p.is_symlink(): p.unlink()
            else: shutil.rmtree(p)
        except Exception:
            pass


def rename_sequence(folder: Path, exclude_suffix: str = '_circle.png') -> None:
    if not folder.exists(): return

    files = list(folder.iterdir())
    circle = sorted([p for p in files if p.name.endswith('_circle.png')])
    regular = sorted([p for p in files if p.suffix.lower() in ('.png','.jpg','.jpeg','.webp') and not p.name.endswith('_circle.png')])

    # 圆形文件仍重命名，但留在临时目录，随后会被移到 transparent
    for i,p in enumerate(circle,1):
        dst = folder / f"{i:02d}_circle.png"
        if p != dst:
            try: p.rename(dst)
            except: pass

    for i,p in enumerate(regular,1):
        dst = folder / f"{i:02d}.jpg"
        if p != dst:
            try: p.rename(dst)
            except: pass


# ============================================================
# 主流程 - 修改实现你的要求
# ============================================================
def step2_cut_screenshots(auto_mode=True, auto_clear_old=True, save_original=True) -> bool:
    import os
    import sys
    # Fix Windows console encoding
    if sys.platform == 'win32':
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        elif hasattr(sys.stdout, 'buffer'):
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')

    print("开始步骤2：裁剪并处理装备图标…")

    if not check_dependencies():
        return False

    # 使用项目根目录构建绝对路径
    game_dir = project_root / 'output_enter_image' / 'game_screenshots'
    if not game_dir.exists():
        print(f"ERROR: 缺少 {game_dir}")
        return False

    screenshots = sorted([p for p in game_dir.iterdir() if p.suffix.lower() in ('.png','.jpg','.jpeg','.webp')])
    if not screenshots:
        print("ERROR: 未找到截图")
        return False

    # 自动清理输出目录（使用统一的清理工具）
    if auto_clear_old:
        try:
            from src.utils.output_cleaner import clean_step_outputs
            print("清理步骤2的输出目录…")
            clean_step_outputs('cut', project_root)
            print("[OK] 清理完成")
        except ImportError:
            # 回退到原来的清理方法
            print("使用备用清理方法…")

    # 主输出：不再使用时间戳文件夹
    # 原来：
    # marker_dir = Path('images/cropped_equipment_marker')
    # transparent_subdir = marker_dir / 'transparent'

    # 修改后：使用项目根目录构建绝对路径
    marker_dir = project_root / 'output_enter_image' / 'equipment_crop'                 # 矩形图输出
    marker_dir.mkdir(parents=True, exist_ok=True)

    transparent_subdir = project_root / 'output_enter_image' / 'equipment_transparent'  # 圆形透明图输出
    transparent_subdir.mkdir(parents=True, exist_ok=True)

    if auto_clear_old and 'clean_step_outputs' not in globals():
        print("清理输出目录…")
        clean_dir(marker_dir)
        clean_dir(transparent_subdir)
        marker_dir.mkdir(parents=True, exist_ok=True)
        transparent_subdir.mkdir(parents=True, exist_ok=True)
        print("清理完成")

    try:
        from src.core.screenshot_cutter import ScreenshotCutter
    except Exception as e:
        print(f"ERROR: 导入 cutter 失败: {e}")
        return False

    cutter = ScreenshotCutter()

    processed = 0
    total_cropped = 0

    for shot in screenshots:
        print(f"处理截图: {shot.name}")

        # 直接输出到主目录（不再创建时间戳文件夹）
        output_folder = marker_dir

        # 使用您指定的分割参数
        cutting_params = {
            'grid': (5, 2),  # 2行，每行5个
            'item_width': 210,  # 装备宽度：210像素
            'item_height': 160,  # 装备高度：160像素
            'margin_left': 10,  # 左侧间隔：10像素
            'margin_top': 275,  # 顶部：275像素
            'h_spacing': 15,  # 横向间隔：15像素
            'v_spacing': 20,  # 纵向间隔：20像素
            'draw_circle': True,
            'save_original': save_original,
            'marker_output_folder': str(output_folder)
        }

        ok = cutter.cut_fixed(
            screenshot_path=str(shot),
            output_folder=str(output_folder),
            **cutting_params
        )
        if not ok:
            print(f"ERROR: 切割失败: {shot.name}")
            continue

        processed += 1

        # 重命名输出（按原逻辑）
        rename_sequence(output_folder)

        # 移动所有 *_circle.png 到 transparent 子目录
        circle_files = list(output_folder.glob('*_circle.png'))
        for f in circle_files:
            dst = transparent_subdir / f.name
            try:
                f.rename(dst)
            except Exception as e:
                print(f"[WARNING] 移动圆形文件失败 {f} -> {dst}: {e}")

        cropped_items = sum(1 for p in output_folder.iterdir()
                             if p.is_file() and p.suffix.lower() in ('.png','.jpg','.jpeg','.webp')
                             and '_circle' not in p.name)
        total_cropped += cropped_items
        print(f"截图 {shot.name} 已完成：{cropped_items} 个矩形装备图 + {len(circle_files)} 个圆形透明图")
    return True


# ============================================================
# 测试流程
# ============================================================
def test_step2_cutting():
    print("开始测试 Step2 …")
    tmp = Path(tempfile.mkdtemp())
    try:
        test_img = tmp / "test.png"
        img = Image.new('RGB',(600,400),'gray')
        draw = ImageDraw.Draw(img)
        for i in range(4):
            x=30+i*120; y=200
            draw.rectangle([x,y,x+100,y+120], fill='red', outline='black')
        img.save(test_img)

        game_dir = project_root / 'output_enter_image' / 'game_screenshots'
        game_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(test_img, game_dir / 'test.png')

        step2_cut_screenshots()

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ============================================================
# 主入口
# ============================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true')
    a = parser.parse_args()
    if a.test:
        test_step2_cutting()
    else:
        step2_cut_screenshots()

if __name__ == '__main__':
    main()
