import cv2
import numpy as np
from PIL import Image, ImageDraw
import os

class ScreenshotCutter:
    """游戏截图切割工具，仅支持固定坐标切割方式"""
    
    @staticmethod
    def draw_circle_on_image(img, circle_size=116):
        """在图片顶部居中位置绘制圆形并返回圆形区域
        
        Args:
            img: PIL图像对象
            circle_size: 圆形直径，默认为116像素
            
        Returns:
            tuple: (带圆形标记的原图像, 圆形区域图像)
        """
        # 创建图像副本
        img_with_circle = img.copy()
        draw = ImageDraw.Draw(img_with_circle)
        
        # 获取图像尺寸
        img_width, img_height = img.size
        
        # 计算圆形位置（顶部居中）
        radius = circle_size // 2
        center_x = img_width // 2
        center_y = radius  # 顶部居中，圆心距离顶部为半径
        
        # 确保圆形在图像范围内
        if center_y + radius > img_height:
            center_y = radius  # 如果超出图像底部，调整到顶部
        
        # 绘制圆形边框（红色，3像素宽度）
        draw.ellipse(
            [(center_x - radius, center_y - radius),
             (center_x + radius, center_y + radius)],
            outline='red', width=3
        )
        
        # 创建真正的圆形图像（带透明背景）
        circle_img = Image.new('RGBA', (circle_size, circle_size), (0, 0, 0, 0))
        
        # 计算圆形区域的边界
        left = max(0, center_x - radius)
        top = max(0, center_y - radius)
        right = min(img_width, center_x + radius)
        bottom = min(img_height, center_y + radius)
        
        # 切割原图中的圆形区域
        crop_region = img.crop((left, top, right, bottom))
        
        # 计算在新图像中的粘贴位置
        paste_x = (circle_size - (right - left)) // 2
        paste_y = (circle_size - (bottom - top)) // 2
        
        # 将切割的区域粘贴到新图像上
        circle_img.paste(crop_region, (paste_x, paste_y))
        
        # 创建圆形遮罩
        mask = Image.new('L', (circle_size, circle_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([(0, 0), (circle_size, circle_size)], fill=255)
        
        # 应用遮罩，使圆形外部透明
        circle_img.putalpha(mask)
        
        return img_with_circle, circle_img
    
    @staticmethod
    def cut_fixed(screenshot_path, output_folder, grid=(5, 2), item_width=210, item_height=160,
                 margin_left=10, margin_top=275, h_spacing=15, v_spacing=20, draw_circle=True,
                 save_original=True):
        """按固定坐标切割游戏截图中的装备
        
        适用于装备位置固定的截图，如按网格排列的背包界面
        
        Args:
            screenshot_path: 游戏截图路径
            output_folder: 切割后装备的保存目录
            grid: 装备网格布局，(列数, 行数)
            item_width: 单个装备宽度
            item_height: 单个装备高度
            margin_left: 左侧边距
            margin_top: 顶部边距
            h_spacing: 装备横向间隔
            v_spacing: 装备纵向间隔
            draw_circle: 是否在切割后的图片上绘制圆形，默认为True
            save_original: 是否保存原图，默认为True
        """
        try:
            with Image.open(screenshot_path) as img:
                # 创建输出目录
                os.makedirs(output_folder, exist_ok=True)
                
                cols, rows = grid
                total_items = cols * rows
                count = 0
                
                for row in range(rows):
                    for col in range(cols):
                        # 计算切割坐标（包含间隔）
                        x1 = margin_left + col * (item_width + h_spacing)
                        y1 = margin_top + row * (item_height + v_spacing)
                        x2 = x1 + item_width
                        y2 = y1 + item_height
                        
                        # 确保坐标在图像范围内
                        img_width, img_height = img.size
                        x1 = max(0, min(x1, img_width))
                        y1 = max(0, min(y1, img_height))
                        x2 = max(0, min(x2, img_width))
                        y2 = max(0, min(y2, img_height))
                        
                        # 切割图片
                        crop_img = img.crop((x1, y1, x2, y2))
                        
                        # 如果需要绘制圆形
                        if draw_circle:
                            # 在切割后的图片上绘制圆形并获取圆形区域
                            img_with_circle, circle_region = ScreenshotCutter.draw_circle_on_image(crop_img, 116)
                            
                            # 根据参数决定保存内容
                            if save_original:
                                # 保存带圆形标记的原图
                                crop_path = os.path.join(output_folder, f"item_{row}_{col}.png")
                                img_with_circle.save(crop_path)
                                print(f"✓ 已保存装备 {row+1}-{col+1}（带圆形标记）")
                            
                            # 保存圆形区域
                            circle_path = os.path.join(output_folder, f"item_{row}_{col}_circle.png")
                            circle_region.save(circle_path)
                            print(f"✓ 已保存装备 {row+1}-{col+1} 的圆形区域")
                        else:
                            # 只保存原图
                            crop_path = os.path.join(output_folder, f"item_{row}_{col}.png")
                            crop_img.save(crop_path)
                            print(f"✓ 已保存装备 {row+1}-{col+1}")
                        
                        count += 1
                
                if draw_circle:
                    if save_original:
                        print(f"成功切割 {count}/{total_items} 个装备到 {output_folder}（包含原图和圆形区域）")
                    else:
                        print(f"成功切割 {count}/{total_items} 个装备到 {output_folder}（仅圆形区域）")
                else:
                    print(f"成功切割 {count}/{total_items} 个装备到 {output_folder}")
                return True
                
        except Exception as e:
            print(f"固定坐标切割出错: {e}")
            return False
    
    @staticmethod
    def analyze_screenshot(screenshot_path):
        """分析截图，提供切割建议
        
        Args:
            screenshot_path: 游戏截图路径
            
        Returns:
            包含分析结果的字典
        """
        try:
            with Image.open(screenshot_path) as img:
                width, height = img.size
            
            # 简化分析，只返回基本信息，不再使用轮廓检测
            analysis = {
                'image_size': (width, height),
                'suggested_cutting_method': 'fixed'  # 只支持固定坐标切割
            }
            
            return analysis
            
        except Exception as e:
            print(f"截图分析出错: {e}")
            return {}