#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
识别结果可视化调试器
生成匹配关键点热图、单应性变换对齐图，并保存调试图像到debug/文件夹
"""

import os
import cv2
import numpy as np
import json
import matplotlib.pyplot as plt
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import matplotlib.cm as cm
from matplotlib.colors import Normalize


class VisualDebugger:
    """识别结果可视化调试器类
    
    生成匹配关键点热图、单应性变换对齐图，并保存调试图像到debug/文件夹
    """
    
    def __init__(self, debug_dir="debug", enable_debug=True):
        """初始化可视化调试器
        
        Args:
            debug_dir: 调试图像保存目录
            enable_debug: 是否启用调试功能
        """
        self.debug_dir = debug_dir
        self.enable_debug = enable_debug
        
        # 确保调试目录存在
        if enable_debug:
            os.makedirs(debug_dir, exist_ok=True)
            os.makedirs(os.path.join(debug_dir, "matches"), exist_ok=True)
            os.makedirs(os.path.join(debug_dir, "heatmaps"), exist_ok=True)
            os.makedirs(os.path.join(debug_dir, "alignments"), exist_ok=True)
            os.makedirs(os.path.join(debug_dir, "reports"), exist_ok=True)
        
        print(f"✓ 识别结果可视化调试器初始化完成")
        print(f"  - 调试目录: {debug_dir}")
        print(f"  - 调试功能: {'启用' if enable_debug else '禁用'}")
    
    def _deserialize_keypoints(self, kp_serialized: List) -> List:
        """反序列化关键点对象
        
        Args:
            kp_serialized: 序列化的关键点列表
            
        Returns:
            OpenCV关键点列表
        """
        keypoints = []
        for kp_data in kp_serialized:
            pt, size, angle, response, octave, class_id = kp_data
            kp = cv2.KeyPoint(
                x=pt[0], y=pt[1],
                size=size,
                angle=angle,
                response=response,
                octave=octave,
                class_id=class_id
            )
            keypoints.append(kp)
        return keypoints
    
    def _generate_keypoints_heatmap(self, image: np.ndarray, keypoints: List) -> np.ndarray:
        """生成关键点热图
        
        Args:
            image: 原始图像
            keypoints: 关键点列表
            
        Returns:
            关键点热图
        """
        # 创建热图
        heatmap = np.zeros((image.shape[0], image.shape[1]), dtype=np.float32)
        
        # 为每个关键点添加高斯分布
        for kp in keypoints:
            x, y = int(kp.pt[0]), int(kp.pt[1])
            size = kp.size
            
            # 创建高斯核
            kernel_size = int(size * 3) | 1  # 确保是奇数
            if kernel_size > 1:
                sigma = size / 3
                kernel = cv2.getGaussianKernel(kernel_size, sigma)
                kernel = np.outer(kernel, kernel)
                
                # 将高斯核添加到热图
                x_start = max(0, x - kernel_size // 2)
                y_start = max(0, y - kernel_size // 2)
                x_end = min(image.shape[1], x + kernel_size // 2 + 1)
                y_end = min(image.shape[0], y + kernel_size // 2 + 1)
                
                # 调整核大小以适应边界
                kx_start = max(0, kernel_size // 2 - x)
                ky_start = max(0, kernel_size // 2 - y)
                kx_end = kx_start + (x_end - x_start)
                ky_end = ky_start + (y_end - y_start)
                
                if kx_end > kx_start and ky_end > ky_start:
                    heatmap[y_start:y_end, x_start:x_end] += kernel[ky_start:ky_end, kx_start:kx_end]
            else:
                # 如果核太小，直接添加一个点
                if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
                    heatmap[y, x] = 1.0
        
        return heatmap
    
    def _draw_keypoints(self, image: np.ndarray, keypoints: List, color=(0, 255, 0)) -> np.ndarray:
        """在图像上绘制关键点
        
        Args:
            image: 原始图像
            keypoints: 关键点列表
            color: 关键点颜色
            
        Returns:
            绘制了关键点的图像
        """
        result = image.copy()
        for kp in keypoints:
            x, y = int(kp.pt[0]), int(kp.pt[1])
            size = int(kp.size)
            
            # 绘制圆圈
            cv2.circle(result, (x, y), size, color, 1)
            
            # 绘制中心点
            cv2.circle(result, (x, y), 1, color, -1)
            
            # 绘制方向线
            angle = kp.angle
            if angle != -1:
                rad = np.deg2rad(angle)
                x2 = int(x + size * np.cos(rad))
                y2 = int(y + size * np.sin(rad))
                cv2.line(result, (x, y), (x2, y2), color, 1)
        
        return result
    
    def _draw_matches(self, img1: np.ndarray, kp1: List, img2: np.ndarray, kp2: List, 
                      matches: List, match_mask=None) -> np.ndarray:
        """绘制匹配结果
        
        Args:
            img1: 第一幅图像
            kp1: 第一幅图像的关键点
            img2: 第二幅图像
            kp2: 第二幅图像的关键点
            matches: 匹配结果
            match_mask: 匹配掩码
            
        Returns:
            绘制了匹配结果的图像
        """
        # 确保图像高度相同
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        max_h = max(h1, h2)
        
        # 调整图像大小
        if h1 < max_h:
            img1 = cv2.resize(img1, (int(w1 * max_h / h1), max_h))
            # 调整关键点坐标
            scale_y = max_h / h1
            scale_x = int(w1 * max_h / h1) / w1
            kp1 = [cv2.KeyPoint(
                x=kp.pt[0] * scale_x,
                y=kp.pt[1] * scale_y,
                size=kp.size * min(scale_x, scale_y),
                angle=kp.angle,
                response=kp.response,
                octave=kp.octave,
                class_id=kp.class_id
            ) for kp in kp1]
        
        if h2 < max_h:
            img2 = cv2.resize(img2, (int(w2 * max_h / h2), max_h))
            # 调整关键点坐标
            scale_y = max_h / h2
            scale_x = int(w2 * max_h / h2) / w2
            kp2 = [cv2.KeyPoint(
                x=kp.pt[0] * scale_x,
                y=kp.pt[1] * scale_y,
                size=kp.size * min(scale_x, scale_y),
                angle=kp.angle,
                response=kp.response,
                octave=kp.octave,
                class_id=kp.class_id
            ) for kp in kp2]
        
        # 创建拼接图像
        h, w = max_h, img1.shape[1] + img2.shape[1]
        result = np.zeros((h, w, 3), dtype=np.uint8)
        result[:img1.shape[0], :img1.shape[1]] = img1
        result[:img2.shape[0], img1.shape[1]:] = img2
        
        # 绘制匹配线
        offset = img1.shape[1]
        for i, match in enumerate(matches):
            if match_mask is None or match_mask[i]:
                pt1 = (int(kp1[match.queryIdx].pt[0]), int(kp1[match.queryIdx].pt[1]))
                pt2 = (int(kp2[match.trainIdx].pt[0] + offset), int(kp2[match.trainIdx].pt[1]))
                
                # 根据匹配距离确定颜色
                distance = match.distance
                max_distance = 100.0  # 假设最大距离
                color_intensity = max(0, min(255, int(255 * (1 - distance / max_distance))))
                color = (0, color_intensity, 255 - color_intensity)  # 从红到绿
                
                cv2.line(result, pt1, pt2, color, 1)
                
                # 在关键点位置绘制小圆圈
                cv2.circle(result, pt1, 2, color, -1)
                cv2.circle(result, pt2, 2, color, -1)
        
        return result
    
    def _draw_homography_alignment(self, img1: np.ndarray, kp1: List, img2: np.ndarray, 
                                  kp2: List, matches: List, H: np.ndarray) -> np.ndarray:
        """绘制单应性变换对齐结果
        
        Args:
            img1: 第一幅图像（模板）
            kp1: 第一幅图像的关键点
            img2: 第二幅图像（查询）
            kp2: 第二幅图像的关键点
            matches: 匹配结果
            H: 单应性矩阵
            
        Returns:
            绘制了对齐结果的图像
        """
        # 创建结果图像
        h, w = img1.shape[:2]
        result = np.zeros((h, w * 2, 3), dtype=np.uint8)
        result[:, :w] = img1
        
        # 应用单应性变换
        if H is not None:
            warped_img2 = cv2.warpPerspective(img2, H, (w, h))
            result[:, w:] = warped_img2
        else:
            # 如果没有有效的单应性矩阵，直接放置图像
            resized_img2 = cv2.resize(img2, (w, h))
            result[:, w:] = resized_img2
        
        # 绘制匹配的关键点对
        for match in matches[:50]:  # 只绘制前50个匹配以避免图像过于混乱
            pt1 = (int(kp1[match.queryIdx].pt[0]), int(kp1[match.queryIdx].pt[1]))
            
            # 将第二幅图像的关键点通过单应性变换映射到第一幅图像的坐标系
            if H is not None:
                pt2_homogeneous = np.array([kp2[match.trainIdx].pt[0], kp2[match.trainIdx].pt[1], 1])
                pt2_transformed = H @ pt2_homogeneous
                if abs(pt2_transformed[2]) > 1e-6:
                    pt2_transformed /= pt2_transformed[2]
                    pt2 = (int(pt2_transformed[0] + w), int(pt2_transformed[1]))
                else:
                    continue
            else:
                pt2 = (int(kp2[match.trainIdx].pt[0] + w), int(kp2[match.trainIdx].pt[1]))
            
            # 绘制连接线
            cv2.line(result, pt1, pt2, (0, 255, 0), 1)
            
            # 绘制关键点
            cv2.circle(result, pt1, 2, (255, 0, 0), -1)
            cv2.circle(result, pt2, 2, (0, 0, 255), -1)
        
        # 添加分割线
        cv2.line(result, (w, 0), (w, h), (255, 255, 255), 2)
        
        return result
    
    def debug_match_result(self, template_path: str, query_path: str, 
                          template_kp_serialized: List, query_kp_serialized: List,
                          matches: List, match_mask=None, H: np.ndarray = None,
                          match_score: float = 0.0, equipment_name: str = "unknown") -> Dict[str, str]:
        """调试匹配结果
        
        Args:
            template_path: 模板图像路径
            query_path: 查询图像路径
            template_kp_serialized: 序列化的模板关键点
            query_kp_serialized: 序列化的查询关键点
            matches: 匹配结果
            match_mask: 匹配掩码
            H: 单应性矩阵
            match_score: 匹配分数
            equipment_name: 装备名称
            
        Returns:
            生成的调试图像路径字典
        """
        if not self.enable_debug:
            return {}
        
        try:
            # 读取图像
            template_img = cv2.imread(template_path)
            query_img = cv2.imread(query_path)
            
            if template_img is None or query_img is None:
                print(f"❌ 无法读取图像: {template_path} 或 {query_path}")
                return {}
            
            # 反序列化关键点
            template_kp = self._deserialize_keypoints(template_kp_serialized)
            query_kp = self._deserialize_keypoints(query_kp_serialized)
            
            # 生成时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"{equipment_name}_{timestamp}"
            
            result_paths = {}
            
            # 1. 生成关键点热图
            template_heatmap = self._generate_keypoints_heatmap(template_img, template_kp)
            query_heatmap = self._generate_keypoints_heatmap(query_img, query_kp)
            
            # 归一化热图并应用颜色映射
            template_heatmap_colored = cv2.applyColorMap(
                (template_heatmap * 255).astype(np.uint8), cv2.COLORMAP_JET
            )
            query_heatmap_colored = cv2.applyColorMap(
                (query_heatmap * 255).astype(np.uint8), cv2.COLORMAP_JET
            )
            
            # 拼接热图
            heatmap_combined = np.hstack([template_heatmap_colored, query_heatmap_colored])
            from src.utils.path_manager import get_path
            heatmap_path = os.path.join(get_path("debug_dir"), "heatmaps", f"{base_filename}_heatmap.png")
            cv2.imwrite(heatmap_path, heatmap_combined)
            result_paths["heatmap"] = heatmap_path
            
            # 2. 绘制关键点
            template_with_kp = self._draw_keypoints(template_img, template_kp, (0, 255, 0))
            query_with_kp = self._draw_keypoints(query_img, query_kp, (0, 255, 0))
            
            # 拼接关键点图像
            keypoints_combined = np.hstack([template_with_kp, query_with_kp])
            keypoints_path = os.path.join(get_path("debug_dir"), "matches", f"{base_filename}_keypoints.png")
            cv2.imwrite(keypoints_path, keypoints_combined)
            result_paths["keypoints"] = keypoints_path
            
            # 3. 绘制匹配结果
            if matches:
                matches_img = self._draw_matches(template_img, template_kp, query_img, query_kp, 
                                                matches, match_mask)
                matches_path = os.path.join(get_path("debug_dir"), "matches", f"{base_filename}_matches.png")
                cv2.imwrite(matches_path, matches_img)
                result_paths["matches"] = matches_path
                
                # 4. 绘制单应性变换对齐结果
                alignment_img = self._draw_homography_alignment(template_img, template_kp, 
                                                              query_img, query_kp, matches, H)
                alignment_path = os.path.join(get_path("debug_dir"), "alignments", f"{base_filename}_alignment.png")
                cv2.imwrite(alignment_path, alignment_img)
                result_paths["alignment"] = alignment_path
            
            # 5. 生成调试报告
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "equipment_name": equipment_name,
                "template_path": template_path,
                "query_path": query_path,
                "match_score": match_score,
                "template_keypoints": len(template_kp),
                "query_keypoints": len(query_kp),
                "good_matches": len(matches) if match_mask is None else sum(match_mask),
                "total_matches": len(matches),
                "homography_valid": H is not None,
                "debug_images": result_paths
            }
            
            report_path = os.path.join(self.debug_dir, "reports", f"{base_filename}_report.json")
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            result_paths["report"] = report_path
            
            print(f"✓ 生成调试图像: {equipment_name} (匹配分数: {match_score:.2f})")
            
            return result_paths
            
        except Exception as e:
            print(f"❌ 生成调试图像失败: {e}")
            return {}
    
    def debug_batch_results(self, batch_results: List[Dict[str, Any]], output_filename: str = None) -> str:
        """调试批量匹配结果
        
        Args:
            batch_results: 批量匹配结果列表
            output_filename: 输出文件名，如果为None则自动生成
            
        Returns:
            调试报告文件路径
        """
        if not self.enable_debug or not batch_results:
            return ""
        
        try:
            if output_filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"batch_debug_report_{timestamp}.json"
            
            report_path = os.path.join(get_path("debug_dir"), "reports", output_filename)
            
            # 统计数据
            total_items = len(batch_results)
            successful_matches = sum(1 for r in batch_results if r.get("match_score", 0) > 0.5)
            high_confidence_matches = sum(1 for r in batch_results if r.get("match_score", 0) > 0.8)
            
            # 按匹配分数排序
            sorted_results = sorted(batch_results, key=lambda x: x.get("match_score", 0), reverse=True)
            
            # 生成报告数据
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "statistics": {
                    "total_items": total_items,
                    "successful_matches": successful_matches,
                    "high_confidence_matches": high_confidence_matches,
                    "success_rate": successful_matches / total_items if total_items > 0 else 0,
                    "high_confidence_rate": high_confidence_matches / total_items if total_items > 0 else 0
                },
                "results": sorted_results
            }
            
            # 保存报告
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            # 生成可视化图表
            self._generate_batch_visualization(report_data, output_filename.replace('.json', '.png'))
            
            print(f"✓ 生成批量调试报告: {report_path}")
            print(f"  - 总项目数: {total_items}")
            print(f"  - 成功匹配: {successful_matches} ({successful_matches/total_items:.1%})")
            print(f"  - 高置信度匹配: {high_confidence_matches} ({high_confidence_matches/total_items:.1%})")
            
            return report_path
            
        except Exception as e:
            print(f"❌ 生成批量调试报告失败: {e}")
            return ""
    
    def _generate_batch_visualization(self, report_data: Dict[str, Any], output_filename: str):
        """生成批量结果可视化图表
        
        Args:
            report_data: 报告数据
            output_filename: 输出文件名
        """
        try:
            plt.figure(figsize=(15, 10))
            
            # 1. 匹配分数分布直方图
            plt.subplot(2, 2, 1)
            scores = [r.get("match_score", 0) for r in report_data["results"]]
            plt.hist(scores, bins=20, color='skyblue', edgecolor='black')
            plt.axvline(x=0.5, color='orange', linestyle='--', label='成功阈值')
            plt.axvline(x=0.8, color='red', linestyle='--', label='高置信度阈值')
            plt.xlabel('匹配分数')
            plt.ylabel('数量')
            plt.title('匹配分数分布')
            plt.legend()
            
            # 2. 成功率饼图
            plt.subplot(2, 2, 2)
            stats = report_data["statistics"]
            labels = ['高置信度匹配', '普通成功匹配', '失败匹配']
            sizes = [
                stats["high_confidence_matches"],
                stats["successful_matches"] - stats["high_confidence_matches"],
                stats["total_items"] - stats["successful_matches"]
            ]
            colors = ['lightgreen', 'lightblue', 'lightcoral']
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
            plt.axis('equal')
            plt.title('匹配结果分布')
            
            # 3. 匹配分数排序图
            plt.subplot(2, 2, 3)
            sorted_scores = sorted(scores, reverse=True)
            plt.plot(range(len(sorted_scores)), sorted_scores, 'o-', color='purple')
            plt.axhline(y=0.5, color='orange', linestyle='--', alpha=0.7)
            plt.axhline(y=0.8, color='red', linestyle='--', alpha=0.7)
            plt.xlabel('排名')
            plt.ylabel('匹配分数')
            plt.title('匹配分数排序')
            plt.grid(True, alpha=0.3)
            
            # 4. 统计信息表格
            plt.subplot(2, 2, 4)
            plt.axis('off')
            table_data = [
                ['总项目数', stats["total_items"]],
                ['成功匹配', f"{stats['successful_matches']} ({stats['success_rate']:.1%})"],
                ['高置信度匹配', f"{stats['high_confidence_matches']} ({stats['high_confidence_rate']:.1%})"],
                ['平均匹配分数', f"{np.mean(scores):.3f}"],
                ['最高匹配分数', f"{max(scores):.3f}"],
                ['最低匹配分数', f"{min(scores):.3f}"]
            ]
            
            table = plt.table(cellText=table_data, 
                            colLabels=['指标', '数值'],
                            cellLoc='center',
                            loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 2)
            plt.title('统计信息')
            
            plt.tight_layout()
            
            # 保存图表
            chart_path = os.path.join(get_path("debug_dir"), "reports", output_filename)
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"  - 可视化图表: {chart_path}")
            
        except Exception as e:
            print(f"❌ 生成批量可视化图表失败: {e}")
    
    def generate_matching_report(self, base_image_path, matching_results, threshold):
        """生成匹配报告
        
        Args:
            base_image_path: 基准图像路径
            matching_results: 匹配结果列表
            threshold: 匹配阈值
            
        Returns:
            报告文件路径
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"matching_report_{timestamp}.html"
            report_path = os.path.join(self.debug_dir, "reports", report_filename)
            
            # 创建HTML报告
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>装备匹配报告</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #333; }}
                    table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .high-similarity {{ background-color: #d4edda; }}
                    .medium-similarity {{ background-color: #fff3cd; }}
                    .low-similarity {{ background-color: #f8d7da; }}
                </style>
            </head>
            <body>
                <h1>装备匹配报告</h1>
                <p>基准图像: {base_image_path}</p>
                <p>匹配阈值: {threshold}%</p>
                <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h2>匹配结果</h2>
                <table>
                    <tr>
                        <th>文件名</th>
                        <th>相似度</th>
                        <th>状态</th>
                    </tr>
            """
            
            for result in matching_results:
                filename = result.get('filename', '未知')
                similarity = result.get('similarity', 0)
                
                # 根据相似度设置样式
                if similarity >= 80:
                    status_class = "high-similarity"
                    status_text = "高匹配度"
                elif similarity >= 60:
                    status_class = "medium-similarity"
                    status_text = "中等匹配度"
                else:
                    status_class = "low-similarity"
                    status_text = "低匹配度"
                
                html_content += f"""
                    <tr class="{status_class}">
                        <td>{filename}</td>
                        <td>{similarity:.2f}%</td>
                        <td>{status_text}</td>
                    </tr>
                """
            
            html_content += """
                </table>
            </body>
            </html>
            """
            
            # 保存HTML报告
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return report_path
            
        except Exception as e:
            print(f"❌ 生成匹配报告失败: {e}")
            return ""
    
    def generate_detailed_analysis(self, debug_data):
        """生成详细分析报告
        
        Args:
            debug_data: 调试数据列表
            
        Returns:
            分析报告文件路径
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"detailed_analysis_{timestamp}.html"
            report_path = os.path.join(self.debug_dir, "reports", report_filename)
            
            # 计算统计数据
            total_items = len(debug_data)
            high_similarity_count = sum(1 for item in debug_data if item.get('similarity', 0) >= 80)
            medium_similarity_count = sum(1 for item in debug_data if 60 <= item.get('similarity', 0) < 80)
            low_similarity_count = total_items - high_similarity_count - medium_similarity_count
            
            avg_similarity = sum(item.get('similarity', 0) for item in debug_data) / total_items if total_items > 0 else 0
            max_similarity = max(item.get('similarity', 0) for item in debug_data) if debug_data else 0
            min_similarity = min(item.get('similarity', 0) for item in debug_data) if debug_data else 0
            
            # 创建HTML报告
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>详细分析报告</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #333; }}
                    h2 {{ color: #555; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
                    .stats-container {{ display: flex; flex-wrap: wrap; gap: 20px; margin: 20px 0; }}
                    .stat-box {{ border: 1px solid #ddd; border-radius: 5px; padding: 15px; min-width: 200px; background-color: #f9f9f9; }}
                    .stat-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
                    .stat-label {{ color: #666; margin-top: 5px; }}
                    table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .high-similarity {{ background-color: #d4edda; }}
                    .medium-similarity {{ background-color: #fff3cd; }}
                    .low-similarity {{ background-color: #f8d7da; }}
                </style>
            </head>
            <body>
                <h1>装备匹配详细分析报告</h1>
                <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h2>统计概览</h2>
                <div class="stats-container">
                    <div class="stat-box">
                        <div class="stat-value">{total_items}</div>
                        <div class="stat-label">总项目数</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{avg_similarity:.2f}%</div>
                        <div class="stat-label">平均相似度</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{max_similarity:.2f}%</div>
                        <div class="stat-label">最高相似度</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{min_similarity:.2f}%</div>
                        <div class="stat-label">最低相似度</div>
                    </div>
                </div>
                
                <h2>相似度分布</h2>
                <div class="stats-container">
                    <div class="stat-box">
                        <div class="stat-value">{high_similarity_count}</div>
                        <div class="stat-label">高匹配度 (≥80%)</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{medium_similarity_count}</div>
                        <div class="stat-label">中等匹配度 (60-80%)</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{low_similarity_count}</div>
                        <div class="stat-label">低匹配度 (<60%)</div>
                    </div>
                </div>
                
                <h2>详细结果</h2>
                <table>
                    <tr>
                        <th>文件名</th>
                        <th>相似度</th>
                        <th>状态</th>
                    </tr>
            """
            
            for result in debug_data:
                filename = result.get('filename', '未知')
                similarity = result.get('similarity', 0)
                
                # 根据相似度设置样式
                if similarity >= 80:
                    status_class = "high-similarity"
                    status_text = "高匹配度"
                elif similarity >= 60:
                    status_class = "medium-similarity"
                    status_text = "中等匹配度"
                else:
                    status_class = "low-similarity"
                    status_text = "低匹配度"
                
                html_content += f"""
                    <tr class="{status_class}">
                        <td>{filename}</td>
                        <td>{similarity:.2f}%</td>
                        <td>{status_text}</td>
                    </tr>
                """
            
            html_content += """
                </table>
            </body>
            </html>
            """
            
            # 保存HTML报告
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return report_path
            
        except Exception as e:
            print(f"❌ 生成详细分析报告失败: {e}")
            return ""


def test_visual_debugger():
    """测试可视化调试器"""
    print("=" * 60)
    print("可视化调试器测试")
    print("=" * 60)
    
    # 创建测试目录
    test_dir = "test_debug"
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
    debugger = VisualDebugger(debug_dir="test_debug_output", enable_debug=True)
    
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
    
    print(f"单个匹配调试结果: {len(result_paths)} 个文件")
    
    # 测试批量结果调试
    batch_results = [
        {"equipment_name": f"equipment_{i}", "match_score": 0.5 + i * 0.05}
        for i in range(20)
    ]
    
    batch_report_path = debugger.debug_batch_results(batch_results)
    print(f"批量调试报告: {batch_report_path}")
    
    # 清理测试文件
    try:
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        if os.path.exists("test_debug_output"):
            shutil.rmtree("test_debug_output")
    except:
        pass
    
    print(f"\n✓ 测试完成")


if __name__ == "__main__":
    test_visual_debugger()