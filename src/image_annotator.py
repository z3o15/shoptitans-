#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像注释模块
用于在原图上添加圆形标记，标识识别到的装备位置
"""

import os
import json
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont


class ImageAnnotator:
    """图像注释器，用于在原图上添加圆形标记和注释"""
    
    def __init__(self, circle_color='red', circle_width=3, font_size=12, show_similarity_text=True):
        """初始化图像注释器
        
        Args:
            circle_color: 圆形标记颜色，默认为红色
            circle_width: 圆形边框宽度，默认为3像素
            font_size: 文字注释字体大小，默认为12像素
            show_similarity_text: 是否显示相似度文字，默认为True
        """
        self.circle_color = circle_color
        self.circle_width = circle_width
        self.font_size = font_size
        self.show_similarity_text = show_similarity_text
        self.font = None
        self._load_font()
    
    def _load_font(self):
        """加载字体，尝试使用系统字体"""
        try:
            # 尝试加载系统字体
            self.font = ImageFont.truetype("arial.ttf", self.font_size)
        except:
            try:
                # Windows系统
                self.font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", self.font_size)
            except:
                try:
                    # Linux系统
                    self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", self.font_size)
                except:
                    # 使用默认字体
                    self.font = ImageFont.load_default()
                    print("⚠️ 无法加载系统字体，使用默认字体")
    
    def annotate_screenshot_with_matches(self, screenshot_path: str, matched_items: List[Tuple[str, float]], 
                                      cutting_params: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """在游戏截图上标注匹配的装备位置
        
        Args:
            screenshot_path: 游戏截图路径
            matched_items: 匹配的装备列表，每个元素为(文件名, 相似度)
            cutting_params: 切割参数，用于计算装备在原图中的位置
            output_path: 输出路径，如果为None则自动生成
            
        Returns:
            注释后的图像路径
        """
        try:
            # 打开原图
            with Image.open(screenshot_path) as img:
                # 创建图像副本用于标注
                annotated_img = img.copy()
                draw = ImageDraw.Draw(annotated_img)
                
                # 获取切割参数
                grid = cutting_params.get('grid', (5, 2))
                item_width = cutting_params.get('item_width', 210)
                item_height = cutting_params.get('item_height', 160)
                margin_left = cutting_params.get('margin_left', 10)
                margin_top = cutting_params.get('margin_top', 275)
                h_spacing = cutting_params.get('h_spacing', 15)
                v_spacing = cutting_params.get('v_spacing', 20)
                
                cols, rows = grid
                
                # 为每个匹配的装备绘制圆形标记
                for filename, similarity in matched_items:
                    # 从文件名提取行列信息
                    # 文件名格式可能是 "item_row_col.png" 或 "01.png"
                    try:
                        if filename.startswith('item_'):
                            # 格式: item_row_col.png
                            parts = filename.replace('.png', '').split('_')
                            if len(parts) >= 3:
                                row = int(parts[1])
                                col = int(parts[2])
                            else:
                                continue
                        else:
                            # 格式: 01.png, 02.png...
                            item_num = int(filename.replace('.png', '')) - 1
                            row = item_num // cols
                            col = item_num % cols
                    except:
                        print(f"⚠️ 无法解析文件名: {filename}")
                        continue
                    
                    # 计算装备在原图中的位置
                    x1 = margin_left + col * (item_width + h_spacing)
                    y1 = margin_top + row * (item_height + v_spacing)
                    x2 = x1 + item_width
                    y2 = y1 + item_height
                    
                    # 计算圆形参数（在装备中心绘制圆形）
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    radius = min(item_width, item_height) // 2 - 5  # 留出5像素边距
                    
                    # 绘制圆形标记
                    draw.ellipse(
                        [(center_x - radius, center_y - radius),
                         (center_x + radius, center_y + radius)],
                        outline=self.circle_color, width=self.circle_width
                    )
                    
                    # 添加相似度注释
                    text = f"{similarity:.1f}%"
                    text_bbox = draw.textbbox((0, 0), text, font=self.font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                    
                    # 将文字放在圆形上方
                    text_x = center_x - text_width // 2
                    text_y = center_y - radius - text_height - 5
                    
                    # 绘制文字背景
                    draw.rectangle(
                        [(text_x - 2, text_y - 2),
                         (text_x + text_width + 2, text_y + text_height + 2)],
                        fill='white', outline='black'
                    )
                    
                    # 绘制文字
                    draw.text((text_x, text_y), text, fill='black', font=self.font)
                
                # 保存注释后的图像
                if output_path is None:
                    # 自动生成输出路径
                    base_name = os.path.splitext(os.path.basename(screenshot_path))[0]
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    output_dir = os.path.dirname(screenshot_path)
                    output_path = os.path.join(output_dir, f"{base_name}_annotated_{timestamp}.png")
                
                annotated_img.save(output_path)
                print(f"✓ 已保存注释图像: {output_path}")
                
                return output_path
                
        except Exception as e:
            print(f"❌ 图像注释失败: {e}")
            return screenshot_path
    
    def create_annotation_report(self, screenshot_path: str, matched_items: List[Tuple[str, float]], 
                              annotated_image_path: str, output_dir: str) -> str:
        """创建注释报告
        
        Args:
            screenshot_path: 原始截图路径
            matched_items: 匹配的装备列表
            annotated_image_path: 注释后的图像路径
            output_dir: 输出目录
            
        Returns:
            报告文件路径
        """
        try:
            # 创建报告数据
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'screenshot_path': screenshot_path,
                'annotated_image_path': annotated_image_path,
                'total_matches': len(matched_items),
                'matches': []
            }
            
            # 添加匹配项详情
            for filename, similarity in matched_items:
                report_data['matches'].append({
                    'filename': filename,
                    'similarity': similarity
                })
            
            # 生成报告文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_path = os.path.join(output_dir, f"annotation_report_{timestamp}.json")
            
            # 保存报告
            os.makedirs(output_dir, exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 已保存注释报告: {report_path}")
            return report_path
            
        except Exception as e:
            print(f"❌ 创建注释报告失败: {e}")
            return ""
    
    def annotate_multiple_screenshots(self, screenshot_matches: List[Dict[str, Any]], 
                                   output_dir: str, cutting_params: Dict[str, Any]) -> List[str]:
        """批量注释多个截图
        
        Args:
            screenshot_matches: 截图匹配信息列表，每个元素包含'screenshot_path'和'matched_items'
            output_dir: 输出目录
            cutting_params: 切割参数
            
        Returns:
            注释后的图像路径列表
        """
        annotated_images = []
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            for match_info in screenshot_matches:
                screenshot_path = match_info.get('screenshot_path')
                matched_items = match_info.get('matched_items', [])
                
                if not os.path.exists(screenshot_path):
                    print(f"⚠️ 截图不存在: {screenshot_path}")
                    continue
                
                if not matched_items:
                    print(f"⚠️ 截图 {screenshot_path} 没有匹配项")
                    continue
                
                # 注释单个截图
                annotated_path = self.annotate_screenshot_with_matches(
                    screenshot_path=screenshot_path,
                    matched_items=matched_items,
                    cutting_params=cutting_params,
                    output_path=None  # 自动生成路径
                )
                
                annotated_images.append(annotated_path)
                
                # 创建注释报告
                self.create_annotation_report(
                    screenshot_path=screenshot_path,
                    matched_items=matched_items,
                    annotated_image_path=annotated_path,
                    output_dir=output_dir
                )
            
            print(f"✓ 批量注释完成，共处理 {len(annotated_images)} 个截图")
            return annotated_images
            
        except Exception as e:
            print(f"❌ 批量注释失败: {e}")
            return annotated_images


def test_annotator():
    """测试图像注释器功能"""
    print("测试图像注释器...")
    
    # 创建注释器
    annotator = ImageAnnotator(circle_color='red', circle_width=3, font_size=12)
    
    # 测试参数
    screenshot_path = "images/game_screenshots/MuMu-20251122-085551-742.png"
    matched_items = [("item_0_0.png", 95.2), ("item_0_3.png", 87.5), ("item_1_2.png", 91.3)]
    
    cutting_params = {
        'grid': (5, 2),
        'item_width': 210,
        'item_height': 160,
        'margin_left': 10,
        'margin_top': 275,
        'h_spacing': 15,
        'v_spacing': 20
    }
    
    # 执行注释
    if os.path.exists(screenshot_path):
        annotated_path = annotator.annotate_screenshot_with_matches(
            screenshot_path=screenshot_path,
            matched_items=matched_items,
            cutting_params=cutting_params
        )
        print(f"注释完成: {annotated_path}")
    else:
        print(f"测试截图不存在: {screenshot_path}")


if __name__ == "__main__":
    test_annotator()