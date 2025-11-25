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
        
        # 创建透明背景的RGBA图像
        circle_img_rgba = Image.new('RGBA', (circle_size, circle_size), (0, 0, 0, 0))
        
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
        
        # 将切割区域粘贴到透明背景上
        circle_img_rgba.paste(crop_region, (paste_x, paste_y))
        
        # 创建圆形遮罩
        mask = Image.new('L', (circle_size, circle_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([(0, 0), (circle_size, circle_size)], fill=255)
        
        # 应用遮罩，使圆形外部透明
        circle_img_rgba.putalpha(mask)
        
        # 创建一个副本用于处理右下角区域（保留透明度）
        circle_img_processed = circle_img_rgba.copy()
        draw = ImageDraw.Draw(circle_img_processed)
        
        # 创建圆形遮罩，确保黑色矩形只在圆形内部
        circle_mask = Image.new('L', (circle_size, circle_size), 0)
        mask_draw = ImageDraw.Draw(circle_mask)
        mask_draw.ellipse([(0, 0), (circle_size, circle_size)], fill=255)
        
        # 创建临时图像用于绘制黑色矩形
        temp_img = Image.new('RGBA', (circle_size, circle_size), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # 将右下角28*60像素区域设置为黑色（避免影响后续匹配）
        # 从右下角开始计算位置
        right_x = circle_size - 1  # 最右边的像素
        bottom_y = circle_size - 1  # 最下边的像素
        left_x = right_x - 28 + 1  # 左边界
        top_y = bottom_y - 60 + 1  # 上边界
        
        # 确保坐标在有效范围内
        left_x = max(0, left_x)
        top_y = max(0, top_y)
        
        # 在临时图像上绘制紫色矩形 (57, 34, 42)
        temp_draw.rectangle([(left_x, top_y), (right_x, bottom_y)], fill=(57, 34, 42, 255))
        
        # 使用圆形遮罩将黑色矩形限制在圆形内
        # 将临时图像合成到圆形图像上，但只在圆形区域内
        for y in range(circle_size):
            for x in range(circle_size):
                if circle_mask.getpixel((x, y)) == 255:  # 在圆形内
                    pixel = temp_img.getpixel((x, y))
                    if pixel[3] > 0:  # 如果临时图像的该像素不透明
                        circle_img_processed.putpixel((x, y), pixel)
        
        # 使用RGBA图像作为最终结果（保留透明度）
        circle_img = circle_img_processed
        
        return img_with_circle, circle_img
    
    @staticmethod
    def cut_fixed(screenshot_path, output_folder, grid=(5, 2), item_width=210, item_height=160,
                 margin_left=10, margin_top=275, h_spacing=15, v_spacing=20, draw_circle=True,
                 save_original=True, marker_output_folder=None):
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
            marker_output_folder: 带圆形标记副本的保存目录，如果为None则不保存副本
        """
        try:
            with Image.open(screenshot_path) as img:
                # 创建输出目录
                os.makedirs(output_folder, exist_ok=True)
                
                # 创建标记副本目录（如果指定）
                if marker_output_folder:
                    os.makedirs(marker_output_folder, exist_ok=True)
                
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
                            
                            # 如果指定了标记副本目录，先保存第一次处理的图片（带圆形标记）
                            if marker_output_folder:
                                marker_path = os.path.join(marker_output_folder, f"item_{row}_{col}.jpg")
                                # 确保图像是RGB模式，不是RGBA
                                if img_with_circle.mode == 'RGBA':
                                    rgb_img = Image.new('RGB', img_with_circle.size, (255, 255, 255))
                                    rgb_img.paste(img_with_circle, mask=img_with_circle.split()[-1])
                                    rgb_img.save(marker_path, format='JPEG', quality=95)
                                else:
                                    img_with_circle.save(marker_path, format='JPEG', quality=95)
                            
                            # 根据参数决定保存内容到主目录
                            if save_original:
                                # 保存带圆形标记的原图到主目录（第二次处理）
                                crop_path = os.path.join(output_folder, f"item_{row}_{col}.jpg")
                                # 确保图像是RGB模式，不是RGBA
                                if img_with_circle.mode == 'RGBA':
                                    rgb_img = Image.new('RGB', img_with_circle.size, (255, 255, 255))
                                    rgb_img.paste(img_with_circle, mask=img_with_circle.split()[-1])
                                    rgb_img.save(crop_path, format='JPEG', quality=95)
                                else:
                                    img_with_circle.save(crop_path, format='JPEG', quality=95)
                            
                            # 保存圆形区域为PNG格式（保留透明度）
                            circle_path = os.path.join(output_folder, f"item_{row}_{col}_circle.png")
                            # 直接保存为PNG格式，保留透明度
                            circle_region.save(circle_path, format='PNG')
                            
                            # 注意：marker目录不保存圆形区域文件，只保存完整的带圆形标记的图片
                        else:
                            # 只保存原图
                            crop_path = os.path.join(output_folder, f"item_{row}_{col}.jpg")
                            # 确保图像是RGB模式，不是RGBA
                            if crop_img.mode == 'RGBA':
                                rgb_img = Image.new('RGB', crop_img.size, (255, 255, 255))
                                rgb_img.paste(crop_img, mask=crop_img.split()[-1])
                                rgb_img.save(crop_path, format='JPEG', quality=95)
                            else:
                                crop_img.save(crop_path, format='JPEG', quality=95)
                            
                            # 如果指定了标记副本目录，也保存一份到该目录
                            if marker_output_folder:
                                marker_path = os.path.join(marker_output_folder, f"item_{row}_{col}.jpg")
                                # 确保图像是RGB模式，不是RGBA
                                if crop_img.mode == 'RGBA':
                                    rgb_img = Image.new('RGB', crop_img.size, (255, 255, 255))
                                    rgb_img.paste(crop_img, mask=crop_img.split()[-1])
                                    rgb_img.save(marker_path, format='JPEG', quality=95)
                                else:
                                    crop_img.save(marker_path, format='JPEG', quality=95)
                        
                        count += 1
                
                # 移除详细输出，只返回结果
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