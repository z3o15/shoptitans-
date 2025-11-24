#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志系统适配器
提供新旧日志系统的兼容性接口，使现有模块能够无缝使用新的日志系统
"""

import sys
import time
from typing import Optional, Dict, Any, Union
from pathlib import Path

# 导入新的日志系统
try:
    from .unified_logger import get_unified_logger, init_unified_logger_from_config
except ImportError:
    try:
        from unified_logger import get_unified_logger, init_unified_logger_from_config
    except ImportError:
        print("警告: 无法导入unified_logger模块")
        get_unified_logger = None
        init_unified_logger_from_config = None

# 导入旧的日志系统
try:
    from .node_logger import get_logger as get_node_logger
    NODE_LOGGER_AVAILABLE = True
except ImportError:
    try:
        from node_logger import get_logger as get_node_logger
        NODE_LOGGER_AVAILABLE = True
    except ImportError:
        NODE_LOGGER_AVAILABLE = False


class LoggerAdapter:
    """日志系统适配器，提供新旧日志系统的统一接口"""
    
    def __init__(self, use_new_logger: bool = True, logger_config: Optional[Dict[str, Any]] = None):
        """初始化日志适配器
        
        Args:
            use_new_logger: 是否使用新的日志系统
            logger_config: 日志配置
        """
        self.use_new_logger = use_new_logger
        
        if use_new_logger:
            # 初始化新的日志系统
            if logger_config:
                self.unified_logger = init_unified_logger_from_config(logger_config)
            else:
                self.unified_logger = get_unified_logger()
            self.node_logger = None
        else:
            # 使用旧的日志系统
            self.unified_logger = None
            if NODE_LOGGER_AVAILABLE:
                self.node_logger = get_node_logger()
            else:
                self.node_logger = None
    
    def start_step(self, step_id: str, description: str = "") -> None:
        """开始一个步骤
        
        Args:
            step_id: 步骤ID
            description: 步骤描述
        """
        if self.use_new_logger and self.unified_logger:
            self.unified_logger.start_step(step_id, description)
        elif self.node_logger:
            # 将步骤ID映射到节点名称
            step_names = {
                "step1_helper": "辅助工具",
                "step2_cut": "图片裁剪", 
                "step3_match": "装备匹配",
                "step5_ocr": "OCR识别"
            }
            step_name = step_names.get(step_id, step_id)
            self.node_logger.start_node(step_name)
    
    def end_step(self, step_id: Optional[str] = None, status: str = "完成") -> None:
        """结束当前步骤
        
        Args:
            step_id: 步骤ID，如果为None则结束当前步骤
            status: 结束状态
        """
        if self.use_new_logger and self.unified_logger:
            self.unified_logger.end_step(step_id, status)
        elif self.node_logger:
            self.node_logger.end_node("✅" if status == "完成" else "❌")
    
    def log_info(self, message: str, step_id: Optional[str] = None, 
                 show_in_console: Optional[bool] = None) -> None:
        """记录信息日志
        
        Args:
            message: 日志信息
            step_id: 步骤ID，如果为None则使用当前步骤
            show_in_console: 是否在控制台显示
        """
        if self.use_new_logger and self.unified_logger:
            self.unified_logger.log_info(message, step_id, show_in_console)
        elif self.node_logger:
            self.node_logger.log_info(message)
    
    def log_warning(self, message: str, step_id: Optional[str] = None, 
                   show_in_console: Optional[bool] = None) -> None:
        """记录警告日志
        
        Args:
            message: 警告信息
            step_id: 步骤ID，如果为None则使用当前步骤
            show_in_console: 是否在控制台显示
        """
        if self.use_new_logger and self.unified_logger:
            self.unified_logger.log_warning(message, step_id, show_in_console)
        elif self.node_logger:
            self.node_logger.log_warning(message)
    
    def log_error(self, message: str, step_id: Optional[str] = None, 
                 show_in_console: Optional[bool] = None) -> None:
        """记录错误日志
        
        Args:
            message: 错误信息
            step_id: 步骤ID，如果为None则使用当前步骤
            show_in_console: 是否在控制台显示
        """
        if self.use_new_logger and self.unified_logger:
            self.unified_logger.log_error(message, step_id, show_in_console)
        elif self.node_logger:
            self.node_logger.log_error(message)
    
    def log_success(self, message: str, step_id: Optional[str] = None, 
                   show_in_console: Optional[bool] = None) -> None:
        """记录成功日志
        
        Args:
            message: 成功信息
            step_id: 步骤ID，如果为None则使用当前步骤
            show_in_console: 是否在控制台显示
        """
        if self.use_new_logger and self.unified_logger:
            self.unified_logger.log_success(message, step_id, show_in_console)
        elif self.node_logger:
            self.node_logger.log_success(message)
    
    def log_progress(self, current: int, total: int, message: str = "", 
                    step_id: Optional[str] = None) -> None:
        """记录进度信息
        
        Args:
            current: 当前进度
            total: 总数
            message: 附加信息
            step_id: 步骤ID，如果为None则使用当前步骤
        """
        if self.use_new_logger and self.unified_logger:
            self.unified_logger.log_progress(current, total, message, step_id)
        elif self.node_logger:
            self.node_logger.log_progress(current, total, message)
    
    def log_file_processed(self, file_path: str, step_id: Optional[str] = None, 
                           success: bool = True, details: str = "") -> None:
        """记录文件处理信息
        
        Args:
            file_path: 文件路径
            step_id: 步骤ID，如果为None则使用当前步骤
            success: 是否处理成功
            details: 详细信息
        """
        if self.use_new_logger and self.unified_logger:
            self.unified_logger.log_file_processed(file_path, step_id, success, details)
        elif self.node_logger:
            file_name = Path(file_path).name
            if success:
                self.node_logger.log_success(f"处理成功: {file_name}")
            else:
                self.node_logger.log_error(f"处理失败: {file_name}")
    
    def log_performance_metric(self, metric_name: str, value: Union[str, int, float], 
                              step_id: Optional[str] = None) -> None:
        """记录性能指标
        
        Args:
            metric_name: 指标名称
            value: 指标值
            step_id: 步骤ID，如果为None则使用当前步骤
        """
        if self.use_new_logger and self.unified_logger:
            self.unified_logger.log_performance_metric(metric_name, value, step_id)
        elif self.node_logger:
            self.node_logger.log_info(f"性能指标: {metric_name} = {value}")
    
    def get_step_dir(self, step_id: Optional[str] = None) -> Optional[Path]:
        """获取步骤目录路径
        
        Args:
            step_id: 步骤ID，如果为None则使用当前步骤
            
        Returns:
            步骤目录路径
        """
        if self.use_new_logger and self.unified_logger:
            return self.unified_logger.get_step_dir(step_id)
        else:
            return None
    
    def get_step_stats(self, step_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取步骤统计信息
        
        Args:
            step_id: 步骤ID，如果为None则使用当前步骤
            
        Returns:
            统计信息字典
        """
        if self.use_new_logger and self.unified_logger:
            return self.unified_logger.get_step_stats(step_id)
        else:
            return None
    
    def generate_summary_report(self, additional_info: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """生成汇总报告
        
        Args:
            additional_info: 额外信息
            
        Returns:
            汇总报告文件路径
        """
        if self.use_new_logger and self.unified_logger:
            return self.unified_logger.generate_summary_report(additional_info)
        else:
            return None
    
    def close_all_logs(self) -> None:
        """关闭所有日志文件"""
        if self.use_new_logger and self.unified_logger:
            self.unified_logger.close_all_logs()


class ScreenshotCutterWithAdapter:
    """集成日志适配器的截图裁剪器"""
    
    def __init__(self, logger_adapter: Optional[LoggerAdapter] = None):
        """初始化截图裁剪器
        
        Args:
            logger_adapter: 日志适配器实例
        """
        try:
            from .screenshot_cutter import ScreenshotCutter
        except ImportError:
            from screenshot_cutter import ScreenshotCutter
        self.cutter = ScreenshotCutter()
        self.logger = logger_adapter or LoggerAdapter()
    
    def cut_screenshots(self, screenshot_path: str, output_folder: str, **kwargs) -> bool:
        """裁剪截图
        
        Args:
            screenshot_path: 截图路径
            output_folder: 输出文件夹
            **kwargs: 其他参数
            
        Returns:
            是否成功
        """
        # 开始步骤
        self.logger.start_step("step2_cut", "裁剪游戏截图")
        
        try:
            # 记录开始信息
            self.logger.log_info(f"开始裁剪截图: {screenshot_path}", show_in_console=True)
            
            # 执行裁剪
            start_time = time.time()
            success = self.cutter.cut_fixed(screenshot_path, output_folder, **kwargs)
            elapsed_time = time.time() - start_time
            
            if success:
                # 记录成功信息
                self.logger.log_success(f"截图裁剪完成，耗时: {elapsed_time:.2f}s", show_in_console=True)
                self.logger.log_performance_metric("裁剪时间", f"{elapsed_time:.2f}s")
                
                # 统计输出文件数量
                output_path = Path(output_folder)
                if output_path.exists():
                    file_count = len(list(output_path.glob("*.jpg")) + list(output_path.glob("*.png")))
                    self.logger.log_info(f"生成文件数量: {file_count}")
            else:
                self.logger.log_error("截图裁剪失败")
            
            # 结束步骤
            self.logger.end_step("step2_cut", "完成" if success else "失败")
            
            return success
            
        except Exception as e:
            self.logger.log_error(f"截图裁剪过程中出错: {str(e)}")
            self.logger.end_step("step2_cut", "失败")
            return False


class FeatureMatcherWithAdapter:
    """集成日志适配器的特征匹配器"""
    
    def __init__(self, logger_adapter: Optional[LoggerAdapter] = None, **kwargs):
        """初始化特征匹配器
        
        Args:
            logger_adapter: 日志适配器实例
            **kwargs: 其他参数
        """
        try:
            from .feature_matcher import FeatureEquipmentRecognizer
        except ImportError:
            from feature_matcher import FeatureEquipmentRecognizer
        self.matcher = FeatureEquipmentRecognizer(**kwargs)
        self.logger = logger_adapter or LoggerAdapter()
    
    def match_equipment(self, base_image_path: str, target_folder: str, 
                       threshold: float = 60.0) -> list:
        """匹配装备
        
        Args:
            base_image_path: 基准图像路径
            target_folder: 目标文件夹
            threshold: 置信度阈值
            
        Returns:
            匹配结果列表
        """
        # 开始步骤
        self.logger.start_step("step3_match", "装备特征匹配")
        
        try:
            # 记录开始信息
            self.logger.log_info(f"开始装备匹配: {base_image_path} vs {target_folder}", show_in_console=True)
            
            # 执行匹配
            start_time = time.time()
            results = self.matcher.batch_recognize(base_image_path, target_folder, threshold)
            elapsed_time = time.time() - start_time
            
            # 记录结果
            self.logger.log_info(f"匹配完成，找到 {len(results)} 个匹配结果", show_in_console=True)
            self.logger.log_performance_metric("匹配时间", f"{elapsed_time:.2f}s")
            self.logger.log_performance_metric("匹配数量", len(results))
            
            # 记录每个匹配结果
            for result in results:
                file_name = Path(result.item_base).name
                self.logger.log_file_processed(file_name, success=result.is_valid_match, 
                                             details=f"置信度: {result.confidence:.2f}%")
            
            # 结束步骤
            self.logger.end_step("step3_match", "完成")
            
            return results
            
        except Exception as e:
            self.logger.log_error(f"装备匹配过程中出错: {str(e)}")
            self.logger.end_step("step3_match", "失败")
            return []


class OCRRecognizerWithAdapter:
    """集成日志适配器的OCR识别器"""
    
    def __init__(self, logger_adapter: Optional[LoggerAdapter] = None, config_manager=None):
        """初始化OCR识别器
        
        Args:
            logger_adapter: 日志适配器实例
            config_manager: 配置管理器
        """
        try:
            from .enhanced_ocr_recognizer import EnhancedOCRRecognizer
        except ImportError:
            from enhanced_ocr_recognizer import EnhancedOCRRecognizer
        self.ocr = EnhancedOCRRecognizer(config_manager)
        self.logger = logger_adapter or LoggerAdapter()
    
    def recognize_amounts(self, image_folder: str, process_subfolders: bool = True) -> list:
        """识别数量
        
        Args:
            image_folder: 图片文件夹
            process_subfolders: 是否处理子文件夹
            
        Returns:
            识别结果列表
        """
        # 开始步骤
        self.logger.start_step("step5_ocr", "OCR数量识别")
        
        try:
            # 记录开始信息
            self.logger.log_info(f"开始OCR识别: {image_folder}", show_in_console=True)
            
            # 执行识别
            start_time = time.time()
            results = self.ocr.batch_recognize_with_fallback(image_folder, process_subfolders)
            elapsed_time = time.time() - start_time
            
            # 统计结果
            success_count = sum(1 for r in results if r.success)
            
            # 记录结果
            self.logger.log_info(f"OCR识别完成，成功: {success_count}/{len(results)}", show_in_console=True)
            self.logger.log_performance_metric("识别时间", f"{elapsed_time:.2f}s")
            self.logger.log_performance_metric("识别数量", len(results))
            self.logger.log_performance_metric("成功率", f"{success_count/len(results)*100:.1f}%" if results else "0%")
            
            # 记录每个识别结果
            for result in results:
                file_name = Path(result.image_path).name
                self.logger.log_file_processed(file_name, success=result.success, 
                                             details=f"文本: '{result.recognized_text}', 置信度: {result.confidence:.2f}")
            
            # 结束步骤
            self.logger.end_step("step5_ocr", "完成")
            
            return results
            
        except Exception as e:
            self.logger.log_error(f"OCR识别过程中出错: {str(e)}")
            self.logger.end_step("step5_ocr", "失败")
            return []


def create_logger_adapter(use_new_logger: bool = True, 
                         logger_config: Optional[Dict[str, Any]] = None) -> LoggerAdapter:
    """创建日志适配器
    
    Args:
        use_new_logger: 是否使用新的日志系统
        logger_config: 日志配置
        
    Returns:
        日志适配器实例
    """
    return LoggerAdapter(use_new_logger, logger_config)


def run_complete_pipeline_with_adapter(screenshot_path: str, template_path: str, 
                                     use_new_logger: bool = True) -> Dict[str, Any]:
    """使用适配器运行完整的处理流水线
    
    Args:
        screenshot_path: 截图路径
        template_path: 模板路径
        use_new_logger: 是否使用新的日志系统
        
    Returns:
        处理结果
    """
    # 创建日志适配器
    logger_config = {
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
    
    adapter = create_logger_adapter(use_new_logger, logger_config)
    
    # 创建处理器
    cutter = ScreenshotCutterWithAdapter(adapter)
    matcher = FeatureMatcherWithAdapter(adapter)
    ocr = OCRRecognizerWithAdapter(adapter)
    
    # 运行处理流水线
    start_time = time.time()
    
    # 步骤1: 截图裁剪
    output_folder = "output/step2_cut/images"
    cut_result = cutter.cut_screenshots(screenshot_path, output_folder)
    
    # 步骤2: 装备匹配
    match_result = matcher.match_equipment(template_path, output_folder)
    
    # 步骤3: OCR识别
    ocr_result = ocr.recognize_amounts(output_folder)
    
    # 生成汇总报告
    summary_report = adapter.generate_summary_report({
        "system_info": {
            "screenshot_path": screenshot_path,
            "template_path": template_path,
            "use_new_logger": use_new_logger
        }
    })
    
    total_time = time.time() - start_time
    
    # 关闭日志
    adapter.close_all_logs()
    
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
    print("🧪 测试日志适配器...")
    
    # 测试新日志系统
    print("\n📝 测试新日志系统:")
    adapter = create_logger_adapter(use_new_logger=True)
    adapter.start_step("step2_cut", "测试新日志系统")
    adapter.log_info("这是一条测试信息", show_in_console=True)
    adapter.log_warning("这是一条测试警告", show_in_console=True)
    adapter.log_success("测试完成", show_in_console=True)
    adapter.end_step("step2_cut", "完成")
    
    # 测试旧日志系统
    if NODE_LOGGER_AVAILABLE:
        print("\n📝 测试旧日志系统:")
        adapter = create_logger_adapter(use_new_logger=False)
        adapter.start_step("step2_cut", "测试旧日志系统")
        adapter.log_info("这是一条测试信息")
        adapter.log_warning("这是一条测试警告")
        adapter.log_success("测试完成")
        adapter.end_step("step2_cut", "完成")
    else:
        print("\n⚠️ 旧日志系统不可用，跳过测试")
    
    print("\n✅ 日志适配器测试完成")