#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志系统集成示例
展示如何将新的日志系统集成到现有模块中
"""

import time
from typing import List, Dict, Any, Optional
from pathlib import Path

from .unified_logger import get_unified_logger, init_unified_logger_from_config


class ScreenshotCutterWithLogger:
    """集成新日志系统的截图裁剪器示例"""
    
    def __init__(self, logger=None):
        """初始化截图裁剪器
        
        Args:
            logger: 日志管理器实例
        """
        self.logger = logger or get_unified_logger()
    
    def cut_screenshots(self, input_dir: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """裁剪截图
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录，如果为None则使用步骤目录
            
        Returns:
            处理结果统计
        """
        # 开始步骤
        self.logger.start_step("step2_cut", "裁剪游戏截图")
        
        # 获取输出目录
        if output_dir is None:
            step_dir = self.logger.get_step_dir()
            if step_dir:
                output_dir = str(step_dir / "images")
            else:
                output_dir = "output/step2_cut/images"
        
        # 模拟处理过程
        input_path = Path(input_dir)
        if not input_path.exists():
            self.logger.log_error(f"输入目录不存在: {input_dir}")
            self.logger.end_step("step2_cut", "失败")
            return {"success": False, "error": "输入目录不存在"}
        
        # 获取输入文件列表
        image_files = list(input_path.glob("*.png")) + list(input_path.glob("*.jpg"))
        total_files = len(image_files)
        
        if total_files == 0:
            self.logger.log_warning(f"输入目录中没有找到图片文件: {input_dir}")
            self.logger.end_step("step2_cut", "完成")
            return {"success": True, "processed": 0}
        
        self.logger.log_info(f"找到 {total_files} 个图片文件", show_in_console=True)
        
        # 处理每个文件
        processed_count = 0
        start_time = time.time()
        
        for i, image_file in enumerate(image_files):
            try:
                # 模拟处理时间
                time.sleep(0.1)
                
                # 模拟处理结果（90%成功率）
                success = i < total_files * 0.9 or i % 10 != 0
                
                if success:
                    # 模拟成功处理
                    output_file = Path(output_dir) / f"cut_{image_file.name}"
                    # 这里应该是实际的图片处理代码
                    # image.save(output_file)
                    
                    processed_count += 1
                    details = f"尺寸: 800x600"
                    self.logger.log_file_processed(str(image_file), success=True, details=details)
                else:
                    # 模拟处理失败
                    self.logger.log_file_processed(str(image_file), success=False, 
                                                 details="图片格式不支持")
                
                # 更新进度
                self.logger.log_progress(i+1, total_files, f"处理 {image_file.name}")
                
            except Exception as e:
                self.logger.log_error(f"处理文件 {image_file.name} 时出错: {str(e)}")
                self.logger.log_file_processed(str(image_file), success=False, 
                                             details=f"异常: {str(e)}")
        
        # 计算性能指标
        elapsed_time = time.time() - start_time
        avg_time = elapsed_time / total_files if total_files > 0 else 0
        
        self.logger.log_performance_metric("总处理时间", f"{elapsed_time:.2f}s")
        self.logger.log_performance_metric("平均处理时间", f"{avg_time:.3f}s/image")
        self.logger.log_performance_metric("处理速度", f"{total_files/elapsed_time:.2f} images/sec")
        
        # 记录统计信息
        stats = self.logger.get_step_stats()
        self.logger.log_info(f"截图裁剪完成: 成功 {processed_count}/{total_files}", 
                             show_in_console=True)
        
        # 结束步骤
        self.logger.end_step("step2_cut", "完成")
        
        return {
            "success": True,
            "processed": processed_count,
            "total": total_files,
            "elapsed_time": elapsed_time
        }


class EquipmentMatcherWithLogger:
    """集成新日志系统的装备匹配器示例"""
    
    def __init__(self, logger=None):
        """初始化装备匹配器
        
        Args:
            logger: 日志管理器实例
        """
        self.logger = logger or get_unified_logger()
    
    def match_equipment(self, input_dir: str, template_dir: str) -> Dict[str, Any]:
        """匹配装备
        
        Args:
            input_dir: 输入图片目录
            template_dir: 模板目录
            
        Returns:
            匹配结果统计
        """
        # 开始步骤
        self.logger.start_step("step3_match", "装备特征匹配")
        
        # 模拟加载模板
        self.logger.log_info("加载装备模板...", show_in_console=True)
        time.sleep(0.5)
        
        templates = ["sword", "shield", "armor", "helmet", "boots"]
        self.logger.log_info(f"加载了 {len(templates)} 个装备模板", show_in_console=True)
        
        # 获取输入文件列表
        input_path = Path(input_dir)
        image_files = list(input_path.glob("*.png")) + list(input_path.glob("*.jpg"))
        total_files = len(image_files)
        
        if total_files == 0:
            self.logger.log_warning(f"输入目录中没有找到图片文件: {input_dir}")
            self.logger.end_step("step3_match", "完成")
            return {"success": True, "matched": 0}
        
        self.logger.log_info(f"开始匹配 {total_files} 个图片", show_in_console=True)
        
        # 处理每个文件
        matched_count = 0
        start_time = time.time()
        
        for i, image_file in enumerate(image_files):
            try:
                # 模拟匹配时间
                time.sleep(0.2)
                
                # 模拟匹配结果（80%成功率）
                success = i < total_files * 0.8 or i % 5 != 0
                
                if success:
                    # 模拟成功匹配
                    matched_template = templates[i % len(templates)]
                    confidence = 0.7 + (i % 3) * 0.1  # 0.7-0.9之间的置信度
                    
                    matched_count += 1
                    details = f"匹配: {matched_template}, 置信度: {confidence:.2f}"
                    self.logger.log_file_processed(str(image_file), success=True, details=details)
                else:
                    # 模拟匹配失败
                    self.logger.log_file_processed(str(image_file), success=False, 
                                                 details="未找到匹配的装备")
                
                # 更新进度
                self.logger.log_progress(i+1, total_files, f"匹配 {image_file.name}")
                
            except Exception as e:
                self.logger.log_error(f"匹配文件 {image_file.name} 时出错: {str(e)}")
                self.logger.log_file_processed(str(image_file), success=False, 
                                             details=f"异常: {str(e)}")
        
        # 计算性能指标
        elapsed_time = time.time() - start_time
        avg_time = elapsed_time / total_files if total_files > 0 else 0
        match_rate = matched_count / total_files * 100 if total_files > 0 else 0
        
        self.logger.log_performance_metric("总匹配时间", f"{elapsed_time:.2f}s")
        self.logger.log_performance_metric("平均匹配时间", f"{avg_time:.3f}s/image")
        self.logger.log_performance_metric("匹配速度", f"{total_files/elapsed_time:.2f} images/sec")
        self.logger.log_performance_metric("匹配成功率", f"{match_rate:.1f}%")
        
        # 记录统计信息
        stats = self.logger.get_step_stats()
        self.logger.log_info(f"装备匹配完成: 成功 {matched_count}/{total_files} ({match_rate:.1f}%)", 
                             show_in_console=True)
        
        # 结束步骤
        self.logger.end_step("step3_match", "完成")
        
        return {
            "success": True,
            "matched": matched_count,
            "total": total_files,
            "match_rate": match_rate,
            "elapsed_time": elapsed_time
        }


class OCRRecognizerWithLogger:
    """集成新日志系统的OCR识别器示例"""
    
    def __init__(self, logger=None):
        """初始化OCR识别器
        
        Args:
            logger: 日志管理器实例
        """
        self.logger = logger or get_unified_logger()
    
    def recognize_amounts(self, input_dir: str) -> Dict[str, Any]:
        """识别数量
        
        Args:
            input_dir: 输入图片目录
            
        Returns:
            识别结果统计
        """
        # 开始步骤
        self.logger.start_step("step5_ocr", "OCR数量识别")
        
        # 模拟初始化OCR
        self.logger.log_info("初始化OCR引擎...", show_in_console=True)
        time.sleep(0.3)
        
        # 获取输入文件列表
        input_path = Path(input_dir)
        image_files = list(input_path.glob("*.png")) + list(input_path.glob("*.jpg"))
        total_files = len(image_files)
        
        if total_files == 0:
            self.logger.log_warning(f"输入目录中没有找到图片文件: {input_dir}")
            self.logger.end_step("step5_ocr", "完成")
            return {"success": True, "recognized": 0}
        
        self.logger.log_info(f"开始识别 {total_files} 个图片中的数量", show_in_console=True)
        
        # 处理每个文件
        recognized_count = 0
        total_amount = 0
        start_time = time.time()
        
        for i, image_file in enumerate(image_files):
            try:
                # 模拟识别时间
                time.sleep(0.15)
                
                # 模拟识别结果（85%成功率）
                success = i < total_files * 0.85 or i % 7 != 0
                
                if success:
                    # 模拟成功识别
                    amount = (i + 1) * 100  # 模拟识别的数量
                    confidence = 0.8 + (i % 3) * 0.05  # 0.8-0.9之间的置信度
                    
                    recognized_count += 1
                    total_amount += amount
                    details = f"识别: {amount}, 置信度: {confidence:.2f}"
                    self.logger.log_file_processed(str(image_file), success=True, details=details)
                else:
                    # 模拟识别失败
                    self.logger.log_file_processed(str(image_file), success=False, 
                                                 details="无法识别数字")
                
                # 更新进度
                self.logger.log_progress(i+1, total_files, f"识别 {image_file.name}")
                
            except Exception as e:
                self.logger.log_error(f"识别文件 {image_file.name} 时出错: {str(e)}")
                self.logger.log_file_processed(str(image_file), success=False, 
                                             details=f"异常: {str(e)}")
        
        # 计算性能指标
        elapsed_time = time.time() - start_time
        avg_time = elapsed_time / total_files if total_files > 0 else 0
        recognition_rate = recognized_count / total_files * 100 if total_files > 0 else 0
        avg_amount = total_amount / recognized_count if recognized_count > 0 else 0
        
        self.logger.log_performance_metric("总识别时间", f"{elapsed_time:.2f}s")
        self.logger.log_performance_metric("平均识别时间", f"{avg_time:.3f}s/image")
        self.logger.log_performance_metric("识别速度", f"{total_files/elapsed_time:.2f} images/sec")
        self.logger.log_performance_metric("识别成功率", f"{recognition_rate:.1f}%")
        self.logger.log_performance_metric("平均识别数量", f"{avg_amount:.0f}")
        
        # 记录统计信息
        stats = self.logger.get_step_stats()
        self.logger.log_info(f"OCR识别完成: 成功 {recognized_count}/{total_files} ({recognition_rate:.1f}%)", 
                             show_in_console=True)
        self.logger.log_info(f"总识别数量: {total_amount}", show_in_console=True)
        
        # 结束步骤
        self.logger.end_step("step5_ocr", "完成")
        
        return {
            "success": True,
            "recognized": recognized_count,
            "total": total_files,
            "recognition_rate": recognition_rate,
            "total_amount": total_amount,
            "elapsed_time": elapsed_time
        }


def run_complete_pipeline(input_dir: str, template_dir: str) -> Dict[str, Any]:
    """运行完整的处理流水线
    
    Args:
        input_dir: 输入目录
        template_dir: 模板目录
        
    Returns:
        处理结果统计
    """
    # 初始化日志系统
    config = {
        "base_output_dir": "output",
        "console_mode": True,
        "output": {
            "show_step_progress": True,
            "show_item_details": False,
            "show_warnings": True,
            "show_errors": True,
            "show_success_summary": True,
            "show_performance_metrics": True
        }
    }
    
    logger = init_unified_logger_from_config(config)
    
    # 创建处理器
    cutter = ScreenshotCutterWithLogger(logger)
    matcher = EquipmentMatcherWithLogger(logger)
    ocr = OCRRecognizerWithLogger(logger)
    
    # 运行处理流水线
    start_time = time.time()
    
    # 步骤1: 截图裁剪
    cut_result = cutter.cut_screenshots(input_dir)
    
    # 步骤2: 装备匹配
    step_dir = logger.get_step_dir("step2_cut")
    match_result = matcher.match_equipment(str(step_dir / "images") if step_dir else input_dir, 
                                          template_dir)
    
    # 步骤3: OCR识别
    step_dir = logger.get_step_dir("step3_match")
    ocr_result = ocr.recognize_amounts(str(step_dir / "images") if step_dir else input_dir)
    
    # 生成汇总报告
    additional_info = {
        "system_info": {
            "python_version": "3.8+",
            "platform": "Windows",
            "input_directory": input_dir,
            "template_directory": template_dir
        },
        "recommendations": [
            "建议提高图片预处理质量以提高OCR准确率",
            "考虑增加更多的装备特征模板",
            "优化错误处理机制"
        ]
    }
    
    summary_report = logger.generate_summary_report(additional_info)
    
    total_time = time.time() - start_time
    
    # 关闭日志
    logger.close_all_logs()
    
    return {
        "success": True,
        "cut_result": cut_result,
        "match_result": match_result,
        "ocr_result": ocr_result,
        "total_time": total_time,
        "summary_report": summary_report
    }


if __name__ == "__main__":
    # 示例用法
    print("🚀 运行完整处理流水线示例...")
    
    # 这里应该替换为实际的目录路径
    input_directory = "images"  # 输入图片目录
    template_directory = "templates"  # 装备模板目录
    
    result = run_complete_pipeline(input_directory, template_directory)
    
    if result["success"]:
        print(f"\n✅ 处理流水线完成，总耗时: {result['total_time']:.2f}s")
        print(f"📋 汇总报告: {result['summary_report']}")
    else:
        print("\n❌ 处理流水线失败")