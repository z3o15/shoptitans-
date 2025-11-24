#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基准装备图像检测器
检测空图、低分辨率图像、特征点不足的图像，并提供自动报告功能
"""

import os
import cv2
import json
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import matplotlib.pyplot as plt

from ..utils.image_hash import get_dhash


class EquipmentDetector:
    """基准装备图像检测器类
    
    检测空图、低分辨率图像、特征点不足的图像，并提供自动报告功能
    """
    
    def __init__(self, target_size=(116, 116), min_resolution=50, 
                 min_keypoints=10, min_dhash_distance=5):
        """初始化基准装备图像检测器
        
        Args:
            target_size: 目标图像尺寸
            min_resolution: 最小分辨率（宽度和高度的最小值）
            min_keypoints: 最少特征点数量
            min_dhash_distance: 最小dHash距离（用于检测重复图像）
        """
        self.target_size = target_size
        self.min_resolution = min_resolution
        self.min_keypoints = min_keypoints
        self.min_dhash_distance = min_dhash_distance
        
        # 创建ORB检测器
        self.detector = cv2.ORB_create(
            nfeatures=3000,
            scaleFactor=1.1,
            edgeThreshold=15,
            patchSize=31
        )
        
        print(f"✓ 基准装备图像检测器初始化完成")
        print(f"  - 目标尺寸: {target_size}")
        print(f"  - 最小分辨率: {min_resolution}")
        print(f"  - 最少特征点: {min_keypoints}")
        print(f"  - 最小dHash距离: {min_dhash_distance}")
    
    def _load_image(self, image_path: str) -> Optional[np.ndarray]:
        """加载图像
        
        Args:
            image_path: 图像路径
            
        Returns:
            图像数组，加载失败返回None
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                print(f"❌ 无法加载图像: {image_path}")
                return None
            return image
        except Exception as e:
            print(f"❌ 加载图像失败: {image_path}, 错误: {e}")
            return None
    
    def _is_empty_image(self, image: np.ndarray) -> bool:
        """检查是否为空图像
        
        Args:
            image: 图像数组
            
        Returns:
            是否为空图像
        """
        # 检查图像是否为None
        if image is None:
            return True
        
        # 检查图像尺寸
        if len(image.shape) == 0:
            return True
        
        # 检查图像是否全黑或全白
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 计算图像的标准差，如果很小则可能是空图像
        std_dev = np.std(gray)
        if std_dev < 5:  # 阈值可调整
            return True
        
        # 检查图像是否为纯色
        unique_values = np.unique(gray)
        if len(unique_values) == 1:
            return True
        
        return False
    
    def _check_resolution(self, image: np.ndarray) -> Dict[str, Any]:
        """检查图像分辨率
        
        Args:
            image: 图像数组
            
        Returns:
            分辨率检查结果
        """
        height, width = image.shape[:2]
        
        is_low_resolution = width < self.min_resolution or height < self.min_resolution
        
        return {
            "width": width,
            "height": height,
            "is_low_resolution": is_low_resolution,
            "min_width": self.min_resolution,
            "min_height": self.min_resolution
        }
    
    def _extract_keypoints(self, image: np.ndarray) -> Tuple[List, Optional[np.ndarray]]:
        """提取图像特征点
        
        Args:
            image: 图像数组
            
        Returns:
            (关键点列表, 描述符数组) 的元组
        """
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # 应用预处理增强
            gray = cv2.equalizeHist(gray)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # 提取ORB特征
            keypoints, descriptors = self.detector.detectAndCompute(gray, None)
            
            return keypoints, descriptors
            
        except Exception as e:
            print(f"❌ 特征点提取失败: {e}")
            return [], None
    
    def _check_keypoints(self, image: np.ndarray) -> Dict[str, Any]:
        """检查图像特征点
        
        Args:
            image: 图像数组
            
        Returns:
            特征点检查结果
        """
        keypoints, descriptors = self._extract_keypoints(image)
        
        keypoint_count = len(keypoints)
        has_insufficient_keypoints = keypoint_count < self.min_keypoints
        
        return {
            "keypoint_count": keypoint_count,
            "min_keypoints": self.min_keypoints,
            "has_insufficient_keypoints": has_insufficient_keypoints,
            "descriptors_shape": descriptors.shape if descriptors is not None else None
        }
    
    def _calculate_dhash(self, image: np.ndarray) -> str:
        """计算图像dHash值
        
        Args:
            image: 图像数组
            
        Returns:
            dHash字符串
        """
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # 调整尺寸
            gray = cv2.resize(gray, (9, 8), interpolation=cv2.INTER_AREA)
            
            # 计算dHash
            dhash = get_dhash(gray)
            
            return dhash
            
        except Exception as e:
            print(f"❌ 计算dHash失败: {e}")
            return ""
    
    def _calculate_hamming_distance(self, hash1: str, hash2: str) -> int:
        """计算汉明距离
        
        Args:
            hash1: 哈希值1
            hash2: 哈希值2
            
        Returns:
            汉明距离
        """
        if not isinstance(hash1, str) or not isinstance(hash2, str):
            return max(len(str(hash1)), len(str(hash2)))
        
        if len(hash1) != len(hash2):
            return max(len(hash1), len(hash2))
        
        return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
    
    def detect_image_quality(self, image_path: str) -> Dict[str, Any]:
        """检测单个图像的质量
        
        Args:
            image_path: 图像路径
            
        Returns:
            图像质量检测结果
        """
        result = {
            "file_path": image_path,
            "file_name": os.path.basename(image_path),
            "timestamp": datetime.now().isoformat(),
            "issues": [],
            "is_valid": True,
            "recommendations": []
        }
        
        # 加载图像
        image = self._load_image(image_path)
        if image is None:
            result["issues"].append("无法加载图像")
            result["is_valid"] = False
            result["recommendations"].append("检查文件是否存在或是否为有效图像")
            return result
        
        # 检查是否为空图像
        if self._is_empty_image(image):
            result["issues"].append("图像为空或接近空")
            result["is_valid"] = False
            result["recommendations"].append("替换为有效图像")
            return result
        
        # 检查分辨率
        resolution_result = self._check_resolution(image)
        result["resolution"] = resolution_result
        if resolution_result["is_low_resolution"]:
            result["issues"].append(f"分辨率过低: {resolution_result['width']}x{resolution_result['height']}")
            result["recommendations"].append(f"使用至少 {self.min_resolution}x{self.min_resolution} 的图像")
        
        # 检查特征点
        keypoint_result = self._check_keypoints(image)
        result["keypoints"] = keypoint_result
        if keypoint_result["has_insufficient_keypoints"]:
            result["issues"].append(f"特征点不足: {keypoint_result['keypoint_count']} < {self.min_keypoints}")
            result["recommendations"].append("使用纹理更丰富的图像")
        
        # 计算dHash
        dhash = self._calculate_dhash(image)
        result["dhash"] = dhash
        
        # 如果有任何问题，标记为无效
        if result["issues"]:
            result["is_valid"] = False
        
        return result
    
    def detect_directory(self, directory_path: str, output_dir: str = None) -> Dict[str, Any]:
        """检测目录中所有图像的质量
        
        Args:
            directory_path: 目录路径
            output_dir: 输出目录，用于保存报告和可视化
            
        Returns:
            目录检测结果
        """
        print(f"开始检测目录: {directory_path}")
        
        # 获取所有图像文件
        image_files = []
        for filename in os.listdir(directory_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                image_files.append(os.path.join(directory_path, filename))
        
        print(f"找到 {len(image_files)} 个图像文件")
        
        # 检测每个图像
        results = []
        dhash_map = {}  # 用于检测重复图像
        
        for image_path in image_files:
            print(f"检测: {os.path.basename(image_path)}")
            result = self.detect_image_quality(image_path)
            results.append(result)
            
            # 检查重复图像
            if "dhash" in result and result["dhash"]:
                for existing_path, existing_dhash in dhash_map.items():
                    distance = self._calculate_hamming_distance(result["dhash"], existing_dhash)
                    if distance < self.min_dhash_distance:
                        result["issues"].append(f"可能与 {os.path.basename(existing_path)} 重复 (dHash距离: {distance})")
                        result["recommendations"].append("检查是否为重复图像，考虑删除")
                        result["is_valid"] = False
                        break
                
                dhash_map[image_path] = result["dhash"]
        
        # 统计结果
        total_count = len(results)
        valid_count = sum(1 for r in results if r["is_valid"])
        invalid_count = total_count - valid_count
        
        # 按问题类型分类
        issue_types = {}
        for result in results:
            for issue in result["issues"]:
                if issue not in issue_types:
                    issue_types[issue] = 0
                issue_types[issue] += 1
        
        # 创建目录检测结果
        directory_result = {
            "directory_path": directory_path,
            "timestamp": datetime.now().isoformat(),
            "total_count": total_count,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "valid_rate": valid_count / total_count if total_count > 0 else 0,
            "issue_types": issue_types,
            "results": results
        }
        
        # 生成报告
        if output_dir:
            self._generate_report(directory_result, output_dir)
        
        # 打印摘要
        print(f"\n检测完成:")
        print(f"  - 总图像数: {total_count}")
        print(f"  - 有效图像: {valid_count}")
        print(f"  - 无效图像: {invalid_count}")
        print(f"  - 有效率: {directory_result['valid_rate']:.2%}")
        
        if issue_types:
            print(f"\n问题类型统计:")
            for issue, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {issue}: {count} 个")
        
        return directory_result
    
    def _generate_report(self, directory_result: Dict[str, Any], output_dir: str):
        """生成检测报告
        
        Args:
            directory_result: 目录检测结果
            output_dir: 输出目录
        """
        try:
            from src.utils.path_manager import ensure_path_valid
            if not ensure_path_valid(os.path.dirname(output_dir)):
                os.makedirs(os.path.dirname(output_dir), exist_ok=True)
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成JSON报告
            report_file = os.path.join(output_dir, "equipment_quality_report.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(directory_result, f, ensure_ascii=False, indent=2)
            
            # 生成文本报告
            text_report_file = os.path.join(output_dir, "equipment_quality_report.txt")
            with open(text_report_file, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("基准装备图像质量检测报告\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"检测目录: {directory_result['directory_path']}\n")
                f.write(f"检测时间: {directory_result['timestamp']}\n\n")
                
                f.write(f"总图像数: {directory_result['total_count']}\n")
                f.write(f"有效图像: {directory_result['valid_count']}\n")
                f.write(f"无效图像: {directory_result['invalid_count']}\n")
                f.write(f"有效率: {directory_result['valid_rate']:.2%}\n\n")
                
                if directory_result['issue_types']:
                    f.write("问题类型统计:\n")
                    for issue, count in sorted(directory_result['issue_types'].items(), key=lambda x: x[1], reverse=True):
                        f.write(f"  - {issue}: {count} 个\n")
                    f.write("\n")
                
                f.write("详细结果:\n")
                f.write("-" * 60 + "\n")
                
                for result in directory_result['results']:
                    f.write(f"文件: {result['file_name']}\n")
                    f.write(f"状态: {'有效' if result['is_valid'] else '无效'}\n")
                    
                    if "resolution" in result:
                        res = result["resolution"]
                        f.write(f"分辨率: {res['width']}x{res['height']}\n")
                    
                    if "keypoints" in result:
                        kp = result["keypoints"]
                        f.write(f"特征点数: {kp['keypoint_count']}\n")
                    
                    if result['issues']:
                        f.write("问题:\n")
                        for issue in result['issues']:
                            f.write(f"  - {issue}\n")
                    
                    if result['recommendations']:
                        f.write("建议:\n")
                        for rec in result['recommendations']:
                            f.write(f"  - {rec}\n")
                    
                    f.write("\n")
            
            # 生成可视化图表
            self._generate_visualization(directory_result, output_dir)
            
            print(f"\n✓ 报告已生成到: {output_dir}")
            print(f"  - JSON报告: {report_file}")
            print(f"  - 文本报告: {text_report_file}")
            
        except Exception as e:
            print(f"❌ 生成报告失败: {e}")
    
    def _generate_visualization(self, directory_result: Dict[str, Any], output_dir: str):
        """生成可视化图表
        
        Args:
            directory_result: 目录检测结果
            output_dir: 输出目录
        """
        try:
            # 创建有效/无效图像饼图
            plt.figure(figsize=(10, 6))
            
            # 饼图
            plt.subplot(1, 2, 1)
            labels = ['有效图像', '无效图像']
            sizes = [directory_result['valid_count'], directory_result['invalid_count']]
            colors = ['lightgreen', 'lightcoral']
            explode = (0, 0.1)
            
            plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
            plt.axis('equal')
            plt.title('图像质量分布')
            
            # 问题类型柱状图
            if directory_result['issue_types']:
                plt.subplot(1, 2, 2)
                issues = list(directory_result['issue_types'].keys())
                counts = list(directory_result['issue_types'].values())
                
                # 截断长标签
                issues = [issue[:20] + '...' if len(issue) > 20 else issue for issue in issues]
                
                plt.barh(issues, counts, color='skyblue')
                plt.xlabel('数量')
                plt.title('问题类型分布')
                plt.tight_layout()
            
            # 保存图表
            chart_file = os.path.join(output_dir, "equipment_quality_chart.png")
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"  - 可视化图表: {chart_file}")
            
        except Exception as e:
            print(f"❌ 生成可视化图表失败: {e}")


def test_equipment_detector():
    """测试基准装备图像检测器"""
    print("=" * 60)
    print("基准装备图像检测器测试")
    print("=" * 60)
    
    # 创建测试目录
    test_dir = "test_equipment_quality"
    output_dir = "test_quality_output"
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建测试图像
    test_images = [
        ("valid_image.png", np.random.randint(50, 200, (116, 116, 3), dtype=np.uint8)),
        ("low_resolution.png", np.random.randint(50, 200, (30, 30, 3), dtype=np.uint8)),
        ("empty_image.png", np.zeros((116, 116, 3), dtype=np.uint8)),
        ("duplicate_image.png", np.random.randint(50, 200, (116, 116, 3), dtype=np.uint8))
    ]
    
    # 保存测试图像
    for filename, image in test_images:
        cv2.imwrite(os.path.join(test_dir, filename), image)
        print(f"创建测试图像: {filename}")
    
    # 创建重复图像
    cv2.imwrite(os.path.join(test_dir, "duplicate_image_copy.png"), test_images[-1][1])
    print(f"创建重复图像: duplicate_image_copy.png")
    
    # 创建检测器
    detector = EquipmentDetector()
    
    # 检测目录
    result = detector.detect_directory(test_dir, output_dir)
    
    # 清理测试文件
    try:
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
    except:
        pass
    
    print(f"\n✓ 测试完成")


if __name__ == "__main__":
    test_equipment_detector()