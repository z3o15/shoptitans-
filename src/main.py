import os
import json
import time
from datetime import datetime
from .equipment_recognizer import EnhancedEquipmentRecognizer
from .screenshot_cutter import ScreenshotCutter
from .config_manager import get_config_manager, create_recognizer_from_config

class EquipmentMatcher:
    """装备匹配器，整合切割和识别功能"""
    
    def __init__(self, config_manager=None):
        """初始化装备匹配器
        
        Args:
            config_manager: 配置管理器实例，如果为None则使用默认配置
        """
        if config_manager is None:
            config_manager = get_config_manager()
        
        self.config_manager = config_manager
        self.recognizer = create_recognizer_from_config(config_manager)
        self.cutter = ScreenshotCutter()
        self.results = []
    
    def batch_compare(self, base_img_path, crop_folder, threshold=None):
        """批量对比切割后的装备与基准装备
        
        Args:
            base_img_path: 基准装备图像路径
            crop_folder: 存放切割后装备图像的文件夹
            threshold: 匹配阈值，若为None则使用默认阈值
        
        Returns:
            匹配结果列表，每个元素包含(文件名, 相似度)
        """
        # 确定使用的阈值
        current_threshold = threshold if threshold is not None else self.recognizer.default_threshold
        
        # 遍历所有切割后的装备图像
        matched_items = []
        all_items = []
        all_match_details = []
        
        print(f"\n开始批量对比，基准图像: {base_img_path}")
        print(f"匹配阈值: {current_threshold}%")
        algorithm_info = self.recognizer.get_algorithm_info()
        algorithm_name = algorithm_info.get('algorithm_name', '未知算法')
        print(f"使用算法: {algorithm_name}")
        print("-" * 50)
        
        for filename in sorted(os.listdir(crop_folder)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                item_path = os.path.join(crop_folder, filename)
                
                # 使用增强版识别器的compare_images方法
                similarity, is_match = self.recognizer.compare_images(base_img_path, item_path, current_threshold)
                all_items.append((filename, similarity))
                
                # 获取详细的匹配信息
                match_details = self._get_match_details(base_img_path, item_path, similarity, is_match)
                all_match_details.append((filename, match_details))
                
                if is_match:
                    matched_items.append((filename, similarity))
                    print(f"【匹配成功】{filename} - 相似度：{similarity}%")
                else:
                    print(f"【未匹配】{filename} - 相似度：{similarity}%")
        
        # 保存结果
        result_data = {
            'timestamp': datetime.now().isoformat(),
            'base_image': base_img_path,
            'threshold': current_threshold,
            'total_items': len(all_items),
            'matched_items': len(matched_items),
            'all_results': all_items,
            'matched_results': matched_items,
            'algorithm_used': algorithm_info.get('current_algorithm', 'unknown')
        }
        
        self.results.append(result_data)
        
        # 输出汇总信息
        print("-" * 50)
        print(f"处理完成！总计 {len(all_items)} 个装备，匹配 {len(matched_items)} 个")
        
        if matched_items:
            print("\n匹配结果汇总：")
            for filename, similarity in matched_items:
                print(f"- {filename}: {similarity}%")
        else:
            print("\n未找到匹配的装备")
        
        # 生成综合匹配报告
        # self._generate_comprehensive_report(crop_folder, base_img_path, all_match_details, matched_items, current_threshold)
        
        return matched_items
    
    def _generate_comprehensive_report(self, crop_folder, base_img_path, all_match_details, matched_items, threshold):
        """生成综合匹配报告
        
        Args:
            crop_folder: 切割装备文件夹路径
            base_img_path: 基准图像路径
            all_match_details: 所有匹配详情列表
            matched_items: 匹配项列表
            threshold: 匹配阈值
        """
        try:
            # 获取基准图片名称
            base_name = os.path.splitext(os.path.basename(base_img_path))[0]
            
            # 创建报告文件路径
            report_path = os.path.join(crop_folder, f"匹配报告_{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
            
            # 准备报告内容
            report_content = f"""# {base_name} - 装备匹配综合报告

## 基本信息
- **基准装备**: {os.path.basename(base_img_path)}
- **匹配阈值**: {threshold}%
- **使用算法**: {self.recognizer.get_algorithm_info().get('algorithm_name', '未知算法')}
- **处理时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **总装备数**: {len(all_match_details)}
- **匹配装备数**: {len(matched_items)}
- **匹配率**: {len(matched_items)/len(all_match_details)*100:.1f}%

## 匹配结果汇总

### ✅ 匹配成功的装备
"""
            
            # 添加匹配成功的装备
            if matched_items:
                for i, (filename, details) in enumerate([(f, d) for f, d in all_match_details if d['is_match']], 1):
                    report_content += f"""
#### {i}. {filename}
- **相似度**: {details['similarity']:.2f}%
"""
                    if details.get('algorithm') == 'advanced':
                        report_content += f"""- **匹配方式**: {details.get('matched_by', 'N/A')}
- **模板相似度**: {details.get('template_similarity', 0):.2f}%
- **置信度**: {details.get('confidence', 0):.2f}%
"""
            else:
                report_content += "无匹配成功的装备\n"
            
            report_content += """
### ❌ 未匹配的装备
"""
            
            # 添加未匹配的装备
            unmatched_items = [(f, d) for f, d in all_match_details if not d['is_match']]
            if unmatched_items:
                for i, (filename, details) in enumerate(unmatched_items, 1):
                    report_content += f"""
#### {i}. {filename}
- **相似度**: {details['similarity']:.2f}%
"""
                    if details.get('algorithm') == 'advanced':
                        report_content += f"""- **匹配方式**: {details.get('matched_by', 'N/A')}
- **模板相似度**: {details.get('template_similarity', 0):.2f}%
- **置信度**: {details.get('confidence', 0):.2f}%
"""
            else:
                report_content += "无未匹配的装备（所有装备都匹配成功）\n"
            
            # 添加详细数据表格
            report_content += """
## 详细数据表格

| 序号 | 装备名称 | 相似度(%) | 匹配结果 | 匹配方式 | 模板相似度(%) | 置信度(%) |
|------|----------|------------|----------|----------|----------------|------------|
"""
            
            # 添加所有装备的详细数据
            for i, (filename, details) in enumerate(all_match_details, 1):
                match_result = "✅ 成功" if details['is_match'] else "❌ 失败"
                # 根据算法类型显示不同的信息
                algorithm = details.get('algorithm', 'traditional')
                if algorithm == 'advanced':
                    matched_by = details.get('matched_by', 'N/A')
                    template_sim = f"{details.get('template_similarity', 0):.2f}"
                    confidence = f"{details.get('confidence', 0):.2f}"
                elif algorithm == 'feature':
                    matched_by = details.get('matched_by', 'N/A')
                    template_sim = f"匹配数量: {details.get('match_count', 0)}"
                    confidence = f"{details.get('confidence', 0):.2f}%"
                else:
                    matched_by = 'DHASH'
                    template_sim = 'N/A'
                    confidence = 'N/A'
                
                report_content += f"| {i} | {filename} | {details['similarity']:.2f} | {match_result} | {matched_by} | {template_sim} | {confidence} |\n"
            
            # 添加总结
            report_content += f"""
## 总结

本次匹配处理共分析了 {len(all_match_details)} 个装备，其中 {len(matched_items)} 个装备与基准装备 **{base_name}** 匹配成功。

"""
            
            if matched_items:
                report_content += f"""### 匹配成功的装备：
"""
                for filename, _ in matched_items:
                    report_content += f"- {filename}\n"
            
            if len(matched_items) < len(all_match_details):
                report_content += f"""
### 建议：
1. 考虑降低匹配阈值（当前：{threshold}%）
2. 检查基准装备是否正确
3. 检查切割装备的清晰度
4. 尝试使用不同的算法模式
"""
            
            report_content += f"""
---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*算法: {self.recognizer.get_algorithm_info().get('algorithm_name', '未知算法')}*
"""
            
            # 写入报告文件
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"✓ 综合匹配报告已生成: {report_path}")
            
            # 删除单独的MD文件（如果存在）
            self._cleanup_individual_md_files(crop_folder, all_match_details)
            
        except Exception as e:
            print(f"生成综合报告失败: {e}")
    
    def _cleanup_individual_md_files(self, crop_folder, all_match_details):
        """清理单独的MD文件
        
        Args:
            crop_folder: 切割装备文件夹路径
            all_match_details: 所有匹配详情列表
        """
        try:
            for filename, _ in all_match_details:
                # 构造单独MD文件的路径
                img_name = os.path.splitext(filename)[0]
                md_file = os.path.join(crop_folder, f"{img_name}_match_details.md")
                
                # 删除文件
                if os.path.exists(md_file):
                    os.remove(md_file)
                    print(f"✓ 已删除单独的MD文件: {md_file}")
        except Exception as e:
            print(f"清理单独MD文件时出错: {e}")
    
    def _get_match_details(self, base_img_path, target_img_path, similarity, is_match):
        """获取匹配详情
        
        Args:
            base_img_path: 基准图像路径
            target_img_path: 目标图像路径
            similarity: 相似度
            is_match: 是否匹配
            
        Returns:
            包含匹配详情的字典
        """
        try:
            # 获取高级识别器的详细信息
            if hasattr(self.recognizer, 'advanced_recognizer') and self.recognizer.advanced_recognizer:
                advanced_result = self.recognizer.advanced_recognizer.recognize_equipment(base_img_path, target_img_path)
                
                return {
                    'base_image': os.path.basename(base_img_path),
                    'target_image': os.path.basename(target_img_path),
                    'similarity': similarity,
                    'is_match': is_match,
                    'matched_by': advanced_result.matched_by.name,
                    'template_similarity': advanced_result.similarity,
                    'confidence': advanced_result.confidence,
                    'min_val': advanced_result.min_val,
                    'hist_val': advanced_result.hist_val,
                    'algorithm': 'advanced_color_matching'
                }
            else:
                return {
                    'base_image': os.path.basename(base_img_path),
                    'target_image': os.path.basename(target_img_path),
                    'similarity': similarity,
                    'is_match': is_match,
                    'algorithm': 'traditional_dhash'
                }
        except Exception as e:
            print(f"获取匹配详情失败: {e}")
            return {
                'base_image': os.path.basename(base_img_path),
                'target_image': os.path.basename(target_img_path),
                'similarity': similarity,
                'is_match': is_match,
                'error': str(e)
            }
    
    def save_results(self, output_path):
        """保存匹配结果到JSON文件
        
        Args:
            output_path: 输出文件路径
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            print(f"结果已保存到: {output_path}")
        except Exception as e:
            print(f"保存结果出错: {e}")
    
    def process_screenshot(self, screenshot_path, base_img_path, output_folder, 
                          cutting_method='auto', threshold=None, **cutting_params):
        """处理完整的截图识别流程
        
        Args:
            screenshot_path: 游戏截图路径
            base_img_path: 基准装备图像路径
            output_folder: 输出文件夹
            cutting_method: 切割方式 ('fixed', 'contour', 'auto')
            threshold: 匹配阈值
            **cutting_params: 切割参数
        
        Returns:
            匹配结果列表
        """
        print(f"开始处理截图: {screenshot_path}")
        start_time = time.time()
        
        # 创建输出文件夹
        crop_folder = os.path.join(output_folder, "cropped_items")
        
        # 选择切割方式
        if cutting_method == 'auto':
            # 自动分析截图选择最佳切割方式
            analysis = self.cutter.analyze_screenshot(screenshot_path)
            if analysis.get('suggested_cutting_method') == 'contour':
                cutting_method = 'contour'
                print("自动选择：轮廓检测切割")
            else:
                cutting_method = 'fixed'
                print("自动选择：固定坐标切割")
        
        # 执行切割
        success = False
        if cutting_method == 'fixed':
            # 设置默认参数
            params = {
                'grid': (6, 2),
                'item_width': 100,
                'item_height': 120,
                'margin_left': 20,
                'margin_top': 350
            }
            params.update(cutting_params)
            success = self.cutter.cut_fixed(screenshot_path, crop_folder, **params)
            
        elif cutting_method == 'contour':
            # 设置默认参数
            params = {
                'min_area': 800,
                'max_area': 50000
            }
            params.update(cutting_params)
            success = self.cutter.cut_contour(screenshot_path, crop_folder, **params)
        
        if not success:
            print("截图切割失败")
            return []
        
        # 执行批量对比
        matched_items = self.batch_compare(base_img_path, crop_folder, threshold)
        
        # 保存结果
        result_file = os.path.join(output_folder, f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        self.save_results(result_file)
        
        end_time = time.time()
        print(f"\n处理完成！耗时: {end_time - start_time:.2f} 秒")
        
        return matched_items

def batch_compare(recognizer, base_img_path, crop_folder, threshold=None):
    """批量对比切割后的装备与基准装备
    
    Args:
        recognizer: EnhancedEquipmentRecognizer实例
        base_img_path: 基准装备图像路径
        crop_folder: 存放切割后装备图像的文件夹
        threshold: 匹配阈值，若为None则使用recognizer的默认阈值
    """
    # 确定使用的阈值
    current_threshold = threshold if threshold is not None else recognizer.default_threshold
    
    # 遍历所有切割后的装备图像
    matched_items = []
    for filename in os.listdir(crop_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            item_path = os.path.join(crop_folder, filename)
            
            # 使用增强版识别器的compare_images方法
            similarity, is_match = recognizer.compare_images(base_img_path, item_path, current_threshold)
            
            if is_match:
                matched_items.append((filename, similarity))
                print(f"【匹配成功】{filename} - 相似度：{similarity}%")
            else:
                print(f"【未匹配】{filename} - 相似度：{similarity}%")
    
    if matched_items:
        print("\n匹配结果汇总：")
        for filename, similarity in matched_items:
            print(f"- {filename}: {similarity}%")
    else:
        print("\n未找到匹配的装备")

def main():
    """主程序入口"""
    # 初始化配置管理器
    config_manager = get_config_manager()
    config_manager.print_config_summary()
    
    # 从配置获取路径
    paths_config = config_manager.get_paths_config()
    IMAGES_DIR = paths_config.get("images_dir", "images")
    BASE_EQUIPMENT_DIR = paths_config.get("base_equipment_dir", "base_equipment")
    BASE_EQUIPMENT_NAME = "target_equipment_1.webp"  # 目标基准装备文件名
    BASE_EQUIPMENT_PATH = os.path.join(IMAGES_DIR, BASE_EQUIPMENT_DIR, BASE_EQUIPMENT_NAME)
    
    GAME_SCREENSHOTS_DIR = paths_config.get("game_screenshots_dir", "game_screenshots")
    SCREENSHOT_NAME = "backpack_screenshot_20240520.png"  # 待处理的游戏截图文件名
    SCREENSHOT_PATH = os.path.join(IMAGES_DIR, GAME_SCREENSHOTS_DIR, SCREENSHOT_NAME)
    
    CROPPED_EQUIPMENT_DIR = paths_config.get("cropped_equipment_dir", "cropped_equipment")
    CROPPED_FOLDER = os.path.join(IMAGES_DIR, CROPPED_EQUIPMENT_DIR)  # 切割后装备保存目录
    LOG_FOLDER = paths_config.get("logs_dir", "recognition_logs")  # 日志保存目录（可选）
    
    # 创建必要目录（若不存在）
    os.makedirs(CROPPED_FOLDER, exist_ok=True)
    os.makedirs(LOG_FOLDER, exist_ok=True)
    
    # 初始化工具
    recognizer = create_recognizer_from_config(config_manager)
    cutter = ScreenshotCutter()
    
    # 步骤1：切割游戏截图
    cutter.cut_fixed(
        screenshot_path=SCREENSHOT_PATH,
        output_folder=CROPPED_FOLDER,
        grid=(6, 2),        # 装备排列：6列2行（根据实际截图调整）
        item_width=100,     # 单个装备宽度（实测调整）
        item_height=120,    # 单个装备高度（实测调整）
        margin_left=20,     # 左侧边距（实测调整）
        margin_top=350      # 顶部边距（实测调整）
    )
    
    # 步骤2：批量对比装备
    batch_compare(
        recognizer=recognizer,
        base_img_path=BASE_EQUIPMENT_PATH,
        crop_folder=CROPPED_FOLDER,
        threshold=80
    )

if __name__ == "__main__":
    main()