#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成器
用于生成各步骤的Markdown报告，支持收集处理统计信息
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class ReportGenerator:
    """报告生成器，用于生成各步骤的Markdown报告"""
    
    def __init__(self, base_output_dir: str = "output"):
        """初始化报告生成器
        
        Args:
            base_output_dir: 输出基础目录
        """
        self.base_output_dir = Path(base_output_dir)
        
        # 步骤配置
        self.step_configs = {
            "step1_helper": {
                "name": "辅助工具",
                "icon": "🔧",
                "description": "辅助工具处理步骤"
            },
            "step2_cut": {
                "name": "图片裁剪",
                "icon": "✂️",
                "description": "截图裁剪和预处理步骤"
            },
            "step3_match": {
                "name": "装备匹配",
                "icon": "🔍",
                "description": "装备特征匹配步骤"
            },
            "step5_ocr": {
                "name": "OCR识别",
                "icon": "📝",
                "description": "文字识别和数量提取步骤"
            }
        }
    
    def generate_step_report(self, step_id: str, stats: Dict[str, Any], 
                           additional_info: Optional[Dict[str, Any]] = None) -> str:
        """生成步骤报告
        
        Args:
            step_id: 步骤ID
            stats: 统计信息
            additional_info: 额外信息
            
        Returns:
            报告文件路径
        """
        if step_id not in self.step_configs:
            raise ValueError(f"未知的步骤ID: {step_id}")
        
        config = self.step_configs[step_id]
        step_dir = self.base_output_dir / step_id
        report_file = step_dir / "report.md"
        
        # 生成报告内容
        report_content = self._generate_report_content(step_id, config, stats, additional_info)
        
        # 写入报告文件
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        return str(report_file)
    
    def _generate_report_content(self, step_id: str, config: Dict[str, Any],
                                stats: Dict[str, Any],
                                additional_info: Optional[Dict[str, Any]]) -> str:
        """生成报告内容
        
        Args:
            step_id: 步骤ID
            config: 步骤配置
            stats: 统计信息
            additional_info: 额外信息
            
        Returns:
            报告内容字符串
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"# {config['icon']} {config['name']} 流程说明报告\n\n"
        content += f"**步骤ID**: {step_id}\n\n"
        content += f"**生成时间**: {now}\n\n"
        content += f"**描述**: {config['description']}\n\n"
        
        # 生成流程说明内容
        content += self._generate_process_description(step_id)
        
        # 处理时间信息
        content += "## 📅 处理时间\n\n"
        if "start_time" in stats:
            content += f"- **开始时间**: {stats['start_time']}\n"
        if "end_time" in stats:
            content += f"- **结束时间**: {stats['end_time']}\n"
        if "elapsed_time" in stats:
            content += f"- **总耗时**: {stats['elapsed_time']}\n"
        content += "\n"
        
        # 处理统计信息
        content += "## 📊 处理统计\n\n"
        content += "| 项目 | 数量 |\n"
        content += "|------|------|\n"
        
        if "processed_items" in stats:
            content += f"| 处理项目 | {stats['processed_items']} |\n"
        if "success_items" in stats:
            content += f"| 成功项目 | {stats['success_items']} |\n"
        if "error_items" in stats:
            content += f"| 失败项目 | {stats['error_items']} |\n"
        if "warnings" in stats:
            content += f"| 警告数量 | {stats['warnings']} |\n"
        
        # 计算成功率
        if "processed_items" in stats and "success_items" in stats and stats["processed_items"] > 0:
            success_rate = (stats["success_items"] / stats["processed_items"]) * 100
            content += f"| 成功率 | {success_rate:.1f}% |\n"
        
        content += "\n"
        
        # 输出文件信息
        content += "## 📁 输出文件说明\n\n"
        content += "本步骤的处理结果保存在以下文件中：\n\n"
        step_dir = self.base_output_dir / step_id
        if step_dir.exists():
            content += self._generate_file_tree(step_dir, step_dir)
        
        # 报告尾部
        content += "\n---\n"
        content += f"*流程说明报告由系统自动生成于 {now}*\n"
        content += "*具体处理结果请查看对应的txt文件*\n"
        
        return content
    
    def _generate_process_description(self, step_id: str) -> str:
        """生成步骤流程说明
        
        Args:
            step_id: 步骤ID
            
        Returns:
            流程说明字符串
        """
        if step_id == "step1_helper":
            return """## 🔧 辅助工具流程说明

### 步骤目的和功能说明
辅助工具步骤是整个装备识别系统的准备阶段，主要负责：
- 检查系统环境和依赖
- 验证数据文件完整性
- 清理之前的处理结果
- 测试V2.0优化功能

### 使用的算法和方法
1. **依赖检查**：通过Python的importlib模块检查所需依赖包
2. **文件验证**：使用os.path模块检查文件和目录存在性
3. **测试框架**：使用临时目录和模拟数据进行功能测试

### 处理流程的详细步骤
1. **环境检查**
   - 检查Python依赖包（cv2, PIL, numpy等）
   - 自动安装缺失的依赖包
   - 验证安装结果

2. **数据文件验证**
   - 检查基准装备图目录（images/base_equipment）
   - 验证游戏截图目录（images/game_screenshots）
   - 确认切割装备目录（images/cropped_equipment）

3. **清理功能**
   - 清理切割后的装备文件
   - 清理带圆形标记副本目录
   - 清理旧的日志文件（保留最新的）

4. **V2.0功能测试**
   - 测试图像预处理流水线
   - 测试自动缓存更新器
   - 测试图像哈希工具
   - 测试质量检测器
   - 测试可视化调试器
   - 测试增强特征匹配器
   - 测试ORB特征点优化

### 配置参数和选项说明
- **依赖包列表**：cv2, PIL, numpy, pytesseract, pandas
- **测试临时目录**：自动创建和清理
- **日志保留策略**：保留最新的日志文件

### 输入输出格式说明
- **输入**：系统环境、配置文件、数据目录
- **输出**：环境检查报告、测试结果、清理日志

### 可能的异常情况处理
- 依赖包安装失败：提示手动安装
- 数据文件缺失：创建必要目录结构
- 测试失败：记录详细错误信息

"""
        elif step_id == "step2_cut":
            return """## ✂️ 图片裁剪流程说明

### 步骤目的和功能说明
图片裁剪步骤是装备识别系统的核心预处理阶段，主要负责：
- 从游戏截图中分割出单个装备图片
- 应用背景掩码和透明化处理
- 生成标准化的装备图片用于后续匹配

### 使用的算法和方法
1. **固定坐标切割**：使用预定义的网格参数进行精确切割
2. **背景掩码**：使用颜色范围检测创建背景掩码
3. **圆形掩码**：创建圆形区域保留装备，去除背景
4. **透明化处理**：将圆形背景设为透明，替换黑色区域

### 处理流程的详细步骤
1. **截图分析**
   - 加载游戏截图
   - 验证图像尺寸和格式
   - 确定切割参数

2. **固定坐标切割**
   - 使用6列2行的网格布局
   - 按预定义坐标切割装备
   - 生成矩形装备图片

3. **圆形标记处理**
   - 在装备图片上绘制圆形标记
   - 保存带标记的副本用于对比
   - 生成圆形填充版本

4. **透明背景处理**
   - 创建圆形掩码（半径55像素）
   - 检测并去除背景色（深紫色、浅紫色）
   - 将圆形外设为透明
   - 替换圆形内黑色区域为指定颜色

5. **文件重命名**
   - 按顺序重命名为01.png, 02.png...
   - 统一文件格式和命名规范

### 配置参数和选项说明
- **网格参数**：6列2行，间距120x140像素
- **圆形半径**：55像素
- **背景色范围**：深紫色(46,33,46)、浅紫色(241,240,241)
- **替换颜色**：#39212e (57,33,46)
- **输出格式**：PNG（支持透明背景）

### 输入输出格式说明
- **输入**：游戏截图（PNG/JPG/JPEG/WEBP）
- **输出**：透明背景装备图片（PNG）、带标记图片（JPG）

### 可能的异常情况处理
- 截图尺寸不符：自动调整切割参数
- 背景色检测失败：使用默认掩码
- 文件命名冲突：自动覆盖旧文件

"""
        elif step_id == "step3_match":
            return """## 🔍 装备匹配流程说明

### 步骤目的和功能说明
装备匹配步骤是识别系统的核心阶段，主要负责：
- 将切割后的装备图片与基准装备库进行匹配
- 使用多阶段匹配策略提高准确性
- 生成匹配结果和相似度评分

### 使用的算法和方法
1. **两阶段匹配策略**：
   - 阶段1：模板匹配筛选候选
   - 阶段2：颜色匹配区分高分候选
2. **模板匹配**：使用OpenCV的TM_CCOEFF_NORMED算法
3. **颜色相似度**：使用LAB色彩空间欧氏距离
4. **综合评分**：加权平均模板匹配和颜色相似度

### 处理流程的详细步骤
1. **图像预处理**
   - 加载基准装备图片和对比图片
   - 调整图像尺寸为116x116像素
   - 创建背景掩码

2. **阶段1：模板匹配**
   - 对所有基准图像进行TM_CCOEFF_NORMED匹配
   - 计算匹配相似度（0-100%）
   - 筛选高分候选（阈值70%）

3. **阶段2：颜色匹配**
   - 对高分候选进行颜色相似度计算
   - 使用圆形掩码策略（半径55像素）
   - 计算LAB色彩空间欧氏距离
   - 生成颜色相似度评分（0-1）

4. **综合评分**
   - 计算加权平均得分（模板65% + 颜色35%）
   - 选择最佳匹配结果
   - 生成匹配报告

5. **结果输出**
   - 保存匹配结果到JSON文件
   - 生成汇总报告到TXT文件
   - 创建对比图像用于验证

### 配置参数和选项说明
- **模板匹配阈值**：70%
- **权重配置**：模板匹配65%，颜色相似度35%
- **圆形掩码半径**：55像素
- **图像尺寸**：116x116像素
- **颜色空间**：LAB色彩空间
- **最大颜色距离**：300.0

### 输入输出格式说明
- **输入**：透明背景装备图片、基准装备库
- **输出**：匹配结果（JSON）、汇总报告（TXT）、对比图像（JPG）

### 可能的异常情况处理
- 无高分候选：选择模板匹配最高的结果
- 颜色匹配失败：仅使用模板匹配结果
- 图像加载失败：跳过并记录错误

"""
        elif step_id == "step5_ocr":
            return """## 📝 OCR识别流程说明

### 步骤目的和功能说明
OCR识别步骤是装备识别系统的最后阶段，主要负责：
- 从装备图片中识别金额信息
- 应用多种OCR引擎和配置策略
- 格式化和标准化识别结果

### 使用的算法和方法
1. **多引擎OCR识别**：支持Tesseract等多种OCR引擎
2. **配置回退机制**：当主配置失败时自动切换备用配置
3. **图像预处理**：背景掩码、对比度增强、噪声去除
4. **文本后处理**：金额格式化、错误纠正

### 处理流程的详细步骤
1. **图像预处理**
   - 加载装备图片
   - 创建背景掩码去除背景色
   - 应用图像增强算法
   - 生成掩码后图像

2. **OCR识别**
   - 使用主配置进行OCR识别
   - 如果识别失败，切换到备用配置
   - 尝试多种OCR引擎和参数
   - 获取识别文本和置信度

3. **文本后处理**
   - 清理识别结果（去除空格、特殊字符）
   - 格式化金额（处理逗号、空格、k表示法）
   - 验证金额合理性
   - 标准化输出格式

4. **结果记录**
   - 保存识别结果到CSV文件
   - 记录处理时间和置信度
   - 生成对比图像用于验证
   - 创建处理日志

### 配置参数和选项说明
- **OCR引擎**：Tesseract（主引擎）
- **语言配置**：eng（英文）
- **预处理选项**：背景掩码、对比度增强
- **回退策略**：多配置自动切换
- **金额格式**：支持逗号、空格、k表示法
- **置信度阈值**：0.5（可配置）

### 输入输出格式说明
- **输入**：带金额标记的装备图片（JPG/PNG）
- **输出**：识别结果（CSV）、掩码图像（PNG）、对比图像（JPG）

### 可能的异常情况处理
- OCR识别失败：尝试备用配置
- 金额格式错误：应用格式化规则
- 图像加载失败：跳过并记录错误
- 配置文件缺失：使用默认配置

"""
        else:
            return f"## 📋 {step_id} 流程说明\n\n暂无详细流程说明。\n"
    
    def _generate_file_tree(self, base_dir: Path, current_dir: Path, prefix: str = "") -> str:
        """生成文件树结构
        
        Args:
            base_dir: 基础目录
            current_dir: 当前目录
            prefix: 前缀
            
        Returns:
            文件树字符串
        """
        if not current_dir.exists():
            return ""
        
        content = ""
        items = sorted(current_dir.iterdir(), key=lambda x: (x.is_file(), x.name))
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            
            if item.is_file():
                if item.name != "report.md":  # 不包含报告文件本身
                    content += f"{prefix}{current_prefix}{item.name}\n"
            elif item.is_dir() and item.name not in [".git", "__pycache__"]:
                content += f"{prefix}{current_prefix}{item.name}/\n"
                next_prefix = prefix + ("    " if is_last else "│   ")
                content += self._generate_file_tree(base_dir, item, next_prefix)
        
        return content
    
    def generate_summary_report(self, all_stats: Dict[str, Dict[str, Any]], 
                               additional_info: Optional[Dict[str, Any]] = None) -> str:
        """生成汇总报告
        
        Args:
            all_stats: 所有步骤的统计信息
            additional_info: 额外信息
            
        Returns:
            汇总报告文件路径
        """
        summary_file = self.base_output_dir / "summary_report.md"
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"# 📋 处理流程汇总报告\n\n"
        content += f"**生成时间**: {now}\n\n"
        
        # 总体统计
        content += "## 📊 总体统计\n\n"
        content += "| 步骤 | 状态 | 处理项目 | 成功项目 | 失败项目 | 成功率 | 耗时 |\n"
        content += "|------|------|----------|----------|----------|--------|------|\n"
        
        total_processed = 0
        total_success = 0
        total_errors = 0
        total_time = 0
        
        for step_id, stats in all_stats.items():
            if step_id not in self.step_configs:
                continue
                
            config = self.step_configs[step_id]
            processed = stats.get("processed_items", 0)
            success = stats.get("success_items", 0)
            errors = stats.get("error_items", 0)
            elapsed = stats.get("elapsed_time", "0s")
            
            success_rate = f"{(success/processed*100):.1f}%" if processed > 0 else "N/A"
            status = "✅ 完成" if errors == 0 else "⚠️ 有错误"
            
            content += f"| {config['icon']} {config['name']} | {status} | {processed} | {success} | {errors} | {success_rate} | {elapsed} |\n"
            
            total_processed += processed
            total_success += success
            total_errors += errors
        
        # 汇总行
        total_success_rate = f"{(total_success/total_processed*100):.1f}%" if total_processed > 0 else "N/A"
        content += f"| **总计** | **{'✅ 完成' if total_errors == 0 else '⚠️ 有错误'}** | **{total_processed}** | **{total_success}** | **{total_errors}** | **{total_success_rate}** | **-** |\n\n"
        
        # 时间线
        content += "## ⏱️ 处理时间线\n\n"
        for step_id, stats in all_stats.items():
            if step_id not in self.step_configs:
                continue
                
            config = self.step_configs[step_id]
            if "start_time" in stats:
                content += f"- **{stats['start_time']}**: {config['icon']} 开始{config['name']}\n"
            if "end_time" in stats:
                content += f"- **{stats['end_time']}**: {config['icon']} 完成{config['name']}\n"
        
        content += "\n"
        
        # 详细步骤报告链接
        content += "## 📋 详细报告\n\n"
        for step_id, stats in all_stats.items():
            if step_id not in self.step_configs:
                continue
                
            config = self.step_configs[step_id]
            report_path = self.base_output_dir / step_id / "report.md"
            if report_path.exists():
                relative_path = os.path.relpath(report_path, self.base_output_dir)
                content += f"- {config['icon']} [{config['name']}详细报告]({relative_path})\n"
        
        content += "\n"
        
        # 额外信息
        if additional_info:
            if "system_info" in additional_info:
                content += "## 💻 系统信息\n\n"
                sys_info = additional_info["system_info"]
                if "python_version" in sys_info:
                    content += f"- Python版本: {sys_info['python_version']}\n"
                if "platform" in sys_info:
                    content += f"- 操作系统: {sys_info['platform']}\n"
                if "memory_usage" in sys_info:
                    content += f"- 内存使用: {sys_info['memory_usage']}\n"
                content += "\n"
            
            if "recommendations" in additional_info:
                content += "## 💡 建议\n\n"
                for recommendation in additional_info["recommendations"]:
                    content += f"- {recommendation}\n"
                content += "\n"
        
        # 报告尾部
        content += "---\n"
        content += f"*汇总报告由系统自动生成于 {now}*\n"
        
        # 写入汇总报告文件
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        return str(summary_file)
    
    def add_step_info(self, step_id: str, info_type: str, data: Any) -> None:
        """添加步骤信息到报告
        
        Args:
            step_id: 步骤ID
            info_type: 信息类型
            data: 数据
        """
        step_dir = self.base_output_dir / step_id
        if not step_dir.exists():
            return
        
        info_file = step_dir / f"{info_type}.json"
        
        # 读取现有信息
        existing_info = []
        if info_file.exists():
            try:
                with open(info_file, "r", encoding="utf-8") as f:
                    existing_info = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                existing_info = []
        
        # 添加新信息
        if isinstance(data, list):
            existing_info.extend(data)
        else:
            existing_info.append(data)
        
        # 写入文件
        with open(info_file, "w", encoding="utf-8") as f:
            json.dump(existing_info, f, ensure_ascii=False, indent=2)
    
    def get_step_info(self, step_id: str, info_type: str) -> List[Any]:
        """获取步骤信息
        
        Args:
            step_id: 步骤ID
            info_type: 信息类型
            
        Returns:
            信息列表
        """
        step_dir = self.base_output_dir / step_id
        info_file = step_dir / f"{info_type}.json"
        
        if not info_file.exists():
            return []
        
        try:
            with open(info_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []


# 全局报告生成器实例
_global_report_generator: Optional[ReportGenerator] = None


def get_report_generator() -> ReportGenerator:
    """获取全局报告生成器实例
    
    Returns:
        全局报告生成器实例
    """
    global _global_report_generator
    if _global_report_generator is None:
        _global_report_generator = ReportGenerator()
    return _global_report_generator


def set_report_generator(generator: ReportGenerator) -> None:
    """设置全局报告生成器实例
    
    Args:
        generator: 报告生成器实例
    """
    global _global_report_generator
    _global_report_generator = generator