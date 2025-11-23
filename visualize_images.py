#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化两张图片的内容
"""

import os
import sys
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入模板匹配测试中的函数
from step_tests.template_matching_test import load_image

def log_message(tag, message):
    """统一日志输出格式"""
    print(f"[{tag}] {message}")

def visualize_images(image_path1, image_path2):
    """
    可视化两张图片的内容
    """
    log_message("INIT", f"开始可视化图片内容")
    log_message("INFO", f"图片1: {image_path1}")
    log_message("INFO", f"图片2: {image_path2}")
    
    # 加载图片
    img1 = load_image(image_path1)
    img2 = load_image(image_path2)
    
    if img1 is None:
        log_message("ERROR", f"无法加载图片1: {image_path1}")
        return
    
    if img2 is None:
        log_message("ERROR", f"无法加载图片2: {image_path2}")
        return
    
    # 转换为RGB用于matplotlib显示
    img1_rgb = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
    img2_rgb = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
    
    # 分析图片的颜色分布
    log_message("ANALYSIS", "分析图片1的颜色分布")
    analyze_color_distribution(img1_rgb, "图片1")
    
    log_message("ANALYSIS", "分析图片2的颜色分布")
    analyze_color_distribution(img2_rgb, "图片2")
    
    # 创建可视化
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # 显示原始图片
    axes[0, 0].imshow(img1_rgb)
    axes[0, 0].set_title('图片1 (07.png)')
    axes[0, 0].axis('off')
    
    axes[0, 1].imshow(img2_rgb)
    axes[0, 1].set_title('图片2 (08.png)')
    axes[0, 1].axis('off')
    
    # 显示颜色直方图
    plot_color_histogram(img1_rgb, axes[0, 2], "图片1颜色分布")
    plot_color_histogram(img2_rgb, axes[1, 0], "图片2颜色分布")
    
    # 显示HSV通道
    plot_hsv_channels(img1_rgb, axes[1, 1], "图片1 HSV通道")
    plot_hsv_channels(img2_rgb, axes[1, 2], "图片2 HSV通道")
    
    plt.tight_layout()
    
    # 保存可视化结果
    output_path = "image_comparison_visualization.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    log_message("RESULT", f"可视化结果已保存到: {output_path}")
    
    # 尝试显示图片（如果在支持的环境中）
    try:
        plt.show()
    except:
        log_message("INFO", "无法直接显示图片，请查看保存的文件")

def analyze_color_distribution(img, name):
    """分析图片的颜色分布"""
    # 计算主要颜色
    pixels = img.reshape(-1, 3)
    unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
    
    # 获取前5种最常见的颜色
    top_indices = np.argsort(counts)[-5:][::-1]
    
    log_message("INFO", f"{name} 主要颜色（前5种）:")
    for i, idx in enumerate(top_indices):
        color = unique_colors[idx]
        count = counts[idx]
        percentage = count / len(pixels) * 100
        log_message("INFO", f"  {i+1}. RGB({color[0]}, {color[1]}, {color[2]}) - {percentage:.2f}%")

def plot_color_histogram(img, ax, title):
    """绘制颜色直方图"""
    colors = ['red', 'green', 'blue']
    for i, color in enumerate(colors):
        hist, bins = np.histogram(img[:, :, i], bins=50, range=(0, 256))
        ax.plot(bins[:-1], hist, color=color, alpha=0.7, label=color.capitalize())
    
    ax.set_title(title)
    ax.set_xlabel('像素值')
    ax.set_ylabel('频次')
    ax.legend()

def plot_hsv_channels(img, ax, title):
    """绘制HSV通道"""
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    
    # 创建一个3通道的图像，其中每个通道显示不同的HSV分量
    h_channel = hsv[:, :, 0] / 179.0  # 归一化到0-1
    s_channel = hsv[:, :, 1] / 255.0
    v_channel = hsv[:, :, 2] / 255.0
    
    # 创建一个合并图像
    hsv_display = np.stack([h_channel, s_channel, v_channel], axis=2)
    
    ax.imshow(hsv_display)
    ax.set_title(title)
    ax.axis('off')

def main():
    """主函数"""
    image_path1 = "test/compare_masked/07.png"
    image_path2 = "test/compare_masked/08.png"
    
    visualize_images(image_path1, image_path2)

if __name__ == "__main__":
    main()