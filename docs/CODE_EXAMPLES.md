# 控制台输出简化代码示例

## 1. 节点日志管理器实现

### src/node_logger.py

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
节点日志管理器
提供统一的控制台输出管理，支持节点式输出结构
"""

import sys
import time
from typing import Optional, Dict, Any

class NodeLogger:
    """节点日志管理器，提供结构化的控制台输出"""
    
    def __init__(self, show_debug: bool = False, compact_mode: bool = True):
        """初始化节点日志管理器
        
        Args:
            show_debug: 是否显示调试信息
            compact_mode: 是否使用紧凑模式
        """
        self.show_debug = show_debug
        self.compact_mode = compact_mode
        self.current_level = 0
        self.node_stack = []
        self.start_times = {}
        
        # 默认图标配置
        self.icons = {
            'init': '🚀',
            'step1': '🖼️',
            'step2': '✂️',
            'step3': '🔍',
            'step4': '📊',
            'complete': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'success': '✅',
            'processing': '⏳',
            'node': '├──',
            'last_node': '└──',
            'sub_node': '│  ├─',
            'last_sub_node': '│  └─',
            'indent': '│   ',
            'last_indent': '    '
        }
    
    def start_node(self, name: str, icon: str = "📋") -> None:
        """开始一个新节点
        
        Args:
            name: 节点名称
            icon: 节点图标
        """
        prefix = self._get_prefix(is_last=False)
        print(f"{prefix} {icon} {name}")
        
        self.node_stack.append((name, icon))
        self.current_level += 1
        self.start_times[name] = time.time()
    
    def end_node(self, status: str = "✅", show_time: bool = True) -> None:
        """结束当前节点
        
        Args:
            status: 结束状态
            show_time: 是否显示耗时
        """
        if not self.node_stack:
            return
        
        name, icon = self.node_stack.pop()
        self.current_level -= 1
        
        if show_time and name in self.start_times:
            elapsed = time.time() - self.start_times[name]
            time_str = f" ({elapsed:.2f}s)"
        else:
            time_str = ""
        
        prefix = self._get_prefix(is_last=True)
        print(f"{prefix} {status} 完成{time_str}")
    
    def log_info(self, message: str, level: int = 1) -> None:
        """记录信息
        
        Args:
            message: 信息内容
            level: 信息级别
        """
        if level > 1 and self.compact_mode:
            return
        
        prefix = self._get_sub_prefix()
        print(f"{prefix} {message}")
    
    def log_success(self, message: str, level: int = 1) -> None:
        """记录成功信息
        
        Args:
            message: 信息内容
            level: 信息级别
        """
        if level > 1 and self.compact_mode:
            return
        
        prefix = self._get_sub_prefix()
        print(f"{prefix} ✅ {message}")
    
    def log_error(self, message: str, level: int = 1) -> None:
        """记录错误信息
        
        Args:
            message: 错误信息
            level: 信息级别
        """
        prefix = self._get_sub_prefix()
        print(f"{prefix} ❌ {message}")
    
    def log_warning(self, message: str, level: int = 1) -> None:
        """记录警告信息
        
        Args:
            message: 警告信息
            level: 信息级别
        """
        if level > 1 and self.compact_mode:
            return
        
        prefix = self._get_sub_prefix()
        print(f"{prefix} ⚠️ {message}")
    
    def log_debug(self, message: str, level: int = 2) -> None:
        """记录调试信息
        
        Args:
            message: 调试信息
            level: 信息级别
        """
        if not self.show_debug or (level > 2 and self.compact_mode):
            return
        
        prefix = self._get_sub_prefix()
        print(f"{prefix} 🔍 {message}")
    
    def log_progress(self, current: int, total: int, message: str = "") -> None:
        """记录进度信息
        
        Args:
            current: 当前进度
            total: 总数
            message: 附加信息
        """
        percentage = (current / total) * 100 if total > 0 else 0
        progress_bar = self._create_progress_bar(percentage)
        
        prefix = self._get_sub_prefix()
        if message:
            print(f"{prefix} {progress_bar} {current}/{total} - {message}")
        else:
            print(f"{prefix} {progress_bar} {current}/{total}")
    
    def _get_prefix(self, is_last: bool = False) -> str:
        """获取节点前缀
        
        Args:
            is_last: 是否为最后一个节点
            
        Returns:
            节点前缀字符串
        """
        if self.current_level == 0:
            return ""
        elif self.current_level == 1:
            return self.icons['last_node'] if is_last else self.icons['node']
        else:
            # 多层级处理
            prefix = ""
            for i in range(self.current_level - 1):
                prefix += self.icons['indent']
            return prefix + (self.icons['last_sub_node'] if is_last else self.icons['sub_node'])
    
    def _get_sub_prefix(self) -> str:
        """获取子项前缀
        
        Returns:
            子项前缀字符串
        """
        if self.current_level == 0:
            return ""
        elif self.current_level == 1:
            return self.icons['last_indent']
        else:
            prefix = ""
            for i in range(self.current_level - 1):
                prefix += self.icons['indent']
            return prefix + self.icons['last_indent']
    
    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """创建进度条
        
        Args:
            percentage: 完成百分比
            width: 进度条宽度
            
        Returns:
            进度条字符串
        """
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {percentage:.1f}%"

# 全局日志管理器实例
_global_logger: Optional[NodeLogger] = None

def get_logger() -> NodeLogger:
    """获取全局日志管理器实例
    
    Returns:
        全局日志管理器实例
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = NodeLogger()
    return _global_logger

def set_logger(logger: NodeLogger) -> None:
    """设置全局日志管理器实例
    
    Args:
        logger: 日志管理器实例
    """
    global _global_logger
    _global_logger = logger
```

## 2. 配置管理器修改

### src/config_manager.py 添加内容

```python
def get_console_output_config(self) -> Dict[str, Any]:
    """获取控制台输出配置
    
    Returns:
        控制台输出配置字典
    """
    return self.config.get("console_output", {})

def update_console_output_config(self, **kwargs) -> None:
    """更新控制台输出配置
    
    Args:
        **kwargs: 要更新的配置项
    """
    console_config = self.config.get("console_output", {})
    console_config.update(kwargs)
    self.config["console_output"] = console_config
    self._save_config(self.config)
```

## 3. run_recognition_start.py 修改示例

### 修改 check_dependencies() 函数

```python
def check_dependencies():
    """检查依赖是否已安装"""
    logger = get_logger()
    logger.start_node("系统依赖检查", "🔍")
    
    required_packages = ['cv2', 'PIL', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            elif package == 'numpy':
                import numpy
            logger.log_success(f"{package}")
        except ImportError:
            missing_packages.append(package)
            logger.log_error(f"{package}")
    
    if missing_packages:
        logger.log_info(f"缺少依赖包: {', '.join(missing_packages)}")
        logger.log_info("正在安装依赖...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            logger.log_success("依赖安装完成")
            logger.end_node("✅")
            return True
        except subprocess.CalledProcessError:
            logger.log_error("依赖安装失败，请手动运行: pip install -r requirements.txt")
            logger.end_node("❌")
            return False
    else:
        logger.log_success("所有依赖已安装")
        logger.end_node("✅")
        return True
```

### 修改 step1_get_screenshots() 函数

```python
def step1_get_screenshots(auto_mode=True):
    """步骤1：获取原始图片"""
    logger = get_logger()
    logger.start_node("步骤1：获取原始图片", "🖼️")
    
    # 检查游戏截图目录
    game_screenshots_dir = "images/game_screenshots"
    
    if not os.path.exists(game_screenshots_dir):
        logger.log_error(f"游戏截图目录不存在: {game_screenshots_dir}")
        if not auto_mode:
            logger.log_info("请将游戏截图放入该目录后重试")
        logger.end_node("❌")
        return False
    
    # 列出所有截图
    screenshot_files = []
    for filename in os.listdir(game_screenshots_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            screenshot_files.append(filename)
    
    if not screenshot_files:
        logger.log_error(f"游戏截图目录为空: {game_screenshots_dir}")
        if not auto_mode:
            logger.log_info("请将游戏截图放入该目录后重试")
        logger.end_node("❌")
        return False
    
    logger.log_info(f"找到 {len(screenshot_files)} 个游戏截图")
    if not auto_mode or logger.show_debug:
        for i, filename in enumerate(sorted(screenshot_files), 1):
            logger.log_debug(f"{i}. {filename}")
    
    logger.log_success("步骤1完成")
    logger.end_node("✅")
    return True
```

## 4. src/main.py 修改示例

### 修改 batch_compare() 方法

```python
def batch_compare(self, base_img_path, crop_folder, threshold=None):
    """批量对比切割后的装备与基准装备"""
    logger = get_logger()
    logger.start_node(f"装备匹配: {os.path.basename(base_img_path)}", "🔍")
    
    # 确定使用的阈值
    current_threshold = threshold if threshold is not None else self.recognizer.default_threshold
    
    # 遍历所有切割后的装备图像
    matched_items = []
    all_items = []
    
    # 获取所有装备文件
    equipment_files = [f for f in os.listdir(crop_folder) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    total_files = len(equipment_files)
    
    logger.log_info(f"匹配阈值: {current_threshold}%")
    logger.log_info(f"待处理装备: {total_files} 个")
    
    for i, filename in enumerate(sorted(equipment_files)):
        item_path = os.path.join(crop_folder, filename)
        
        # 使用增强版识别器的compare_images方法
        similarity, is_match = self.recognizer.compare_images(base_img_path, item_path, current_threshold)
        all_items.append((filename, similarity))
        
        if is_match:
            matched_items.append((filename, similarity))
            logger.log_success(f"{filename} - 相似度：{similarity:.2f}%")
        else:
            logger.log_info(f"{filename} - 相似度：{similarity:.2f}%")
        
        # 显示进度
        if i % 5 == 0 or i == total_files - 1:
            logger.log_progress(i + 1, total_files, "匹配进度")
    
    # 输出汇总信息
    logger.log_info(f"处理完成！总计 {len(all_items)} 个装备，匹配 {len(matched_items)} 个")
    
    if matched_items:
        logger.log_info("匹配结果:")
        for filename, similarity in matched_items:
            logger.log_info(f"- {filename}: {similarity:.2f}%")
    else:
        logger.log_warning("未找到匹配的装备")
    
    logger.end_node("✅")
    return matched_items
```

## 5. src/enhanced_ocr_recognizer.py 修改示例

### 修改 recognize_with_fallback() 方法

```python
def recognize_with_fallback(self, image_path: str) -> EnhancedOCRResult:
    """使用回退机制进行OCR识别"""
    logger = get_logger()
    start_time = time.time()
    original_filename = os.path.basename(image_path)
    
    try:
        # 检查OCR是否启用
        if not self.config_manager.is_ocr_enabled():
            logger.log_error(f"OCR功能已禁用: {original_filename}")
            return EnhancedOCRResult(
                image_path=image_path,
                original_filename=original_filename,
                recognized_text="",
                extracted_amount=None,
                confidence=0.0,
                processing_time=time.time() - start_time,
                success=False,
                error_message="OCR功能已禁用"
            )
        
        # 获取配置
        ocr_config = self.config_manager.get_ocr_config()
        confidence_threshold = ocr_config.get("confidence_threshold", 0.7)
        
        # 获取回退预处理配置列表
        fallback_configs = ocr_config.get("fallback_preprocessing", [])
        
        # 如果没有回退配置，使用默认配置
        if not fallback_configs:
            fallback_configs = [
                {"name": "默认配置", "grayscale": True, "threshold": True, "denoise": False},
                {"name": "自适应二值化配置", "grayscale": True, "threshold": True, "denoise": False}
            ]
        
        # 尝试每种预处理配置
        best_result = None
        best_confidence = 0.0
        
        for i, config in enumerate(fallback_configs):
            config_name = config.get("name", f"配置{i+1}")
            logger.log_debug(f"尝试预处理配置: {config_name}")
            
            try:
                # 应用预处理
                processed_image = self._apply_preprocessing_config(image_path, config)
                
                # 图像增强
                if ocr_config.get("brightness_adjustment", {}).get("enabled", False) or \
                   ocr_config.get("contrast_enhancement", {}).get("enabled", False):
                    processed_image = self._enhance_image(processed_image)
                
                # OCR识别
                results = self.ocr_reader.readtext(processed_image)
                
                if results:
                    # 提取文本和置信度
                    recognized_text = " ".join([result[1] for result in results])
                    # 过滤只保留数字和逗号
                    recognized_text = re.sub(r'[^\d,]', '', recognized_text)
                    avg_confidence = sum([result[2] for result in results]) / len(results)
                    
                    # 提取金额
                    extracted_amount = self._extract_amount_from_text(recognized_text)
                    
                    # 判断是否成功（使用原始置信度阈值）
                    success = extracted_amount is not None and avg_confidence >= confidence_threshold
                    
                    # 如果这是最好的结果，保存它
                    if avg_confidence > best_confidence:
                        best_confidence = avg_confidence
                        best_result = {
                            "recognized_text": recognized_text,
                            "extracted_amount": extracted_amount,
                            "confidence": avg_confidence,
                            "success": success,
                            "preprocessing_used": config_name,
                            "fallback_attempts": i + 1
                        }
                    
                    # 如果已经成功，可以提前结束
                    if success:
                        logger.log_debug(f"使用配置 '{config_name}' 成功识别")
                        break
                
            except Exception as e:
                logger.log_warning(f"配置 '{config_name}' 处理失败: {e}")
                continue
        
        # 如果第一次尝试没有成功，尝试降低置信度阈值
        if best_result and not best_result["success"] and best_result["confidence"] > 0.6:
            logger.log_info(f"尝试降低置信度阈值到0.6")
            
            # 使用降低的置信度阈值重新判断
            low_threshold_success = best_result["extracted_amount"] is not None and best_result["confidence"] >= 0.6
            
            if low_threshold_success:
                best_result["success"] = True
                best_result["fallback_attempts"] += 1  # 标记为使用了低阈值
                logger.log_success(f"使用降低的置信度阈值(0.6)成功识别: {best_result['recognized_text']}")
        
        # 如果没有找到任何结果
        if best_result is None:
            logger.log_error(f"所有预处理配置都无法识别文本: {original_filename}")
            return EnhancedOCRResult(
                image_path=image_path,
                original_filename=original_filename,
                recognized_text="",
                extracted_amount=None,
                confidence=0.0,
                processing_time=time.time() - start_time,
                success=False,
                error_message="所有预处理配置都无法识别文本",
                fallback_attempts=len(fallback_configs)
            )
        
        processing_time = time.time() - start_time
        
        # 简化输出格式
        if best_result["success"]:
            logger.log_success(f"{original_filename} | 文本: '{best_result['recognized_text']}' | 置信度: {best_result['confidence']:.2f}")
        else:
            logger.log_info(f"{original_filename} | 文本: '{best_result['recognized_text']}' | 置信度: {best_result['confidence']:.2f}")
        
        return EnhancedOCRResult(
            image_path=image_path,
            original_filename=original_filename,
            recognized_text=best_result["recognized_text"],
            extracted_amount=best_result["extracted_amount"],
            confidence=best_result["confidence"],
            processing_time=processing_time,
            success=best_result["success"],
            error_message=None if best_result["success"] else f"识别置信度过低: {best_result['confidence']:.2f}",
            preprocessing_used=best_result["preprocessing_used"],
            fallback_attempts=best_result["fallback_attempts"]
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_message = f"识别过程中发生错误: {str(e)}"
        logger.log_error(f"识别失败: {image_path}, 错误: {error_message}")
        
        return EnhancedOCRResult(
            image_path=image_path,
            original_filename=original_filename,
            recognized_text="",
            extracted_amount=None,
            confidence=0.0,
            processing_time=processing_time,
            success=False,
            error_message=error_message
        )
```

## 6. 使用示例

### 在 run_full_auto_workflow() 中使用

```python
def run_full_auto_workflow(auto_clear_old=True, auto_select_all=True, save_original=True,
                       auto_select_base=True, auto_threshold=None, auto_generate_annotation=False):
    """运行全自动工作流程，无需任何手动操作"""
    logger = get_logger()
    logger.start_node("装备识别系统", "🚀")
    
    # 步骤1：获取原始图片
    if not step1_get_screenshots(auto_mode=True):
        logger.log_error("步骤1失败，终止自动流程")
        logger.end_node("❌")
        return False
    
    # 步骤2：分割原始图片
    if not step2_cut_screenshots(auto_mode=True, auto_clear_old=auto_clear_old,
                                auto_select_all=auto_select_all, save_original=save_original):
        logger.log_error("步骤2失败，终止自动流程")
        logger.end_node("❌")
        return False
    
    # 步骤3：装备识别匹配
    if not step3_match_equipment(auto_mode=True, auto_select_base=auto_select_base,
                               auto_threshold=auto_threshold, auto_match_all=True):
        logger.log_error("步骤3失败，终止自动流程")
        logger.end_node("❌")
        return False
    
    # 步骤4：整合装备名称和金额识别结果
    if not step4_integrate_results(auto_mode=True):
        logger.log_error("步骤4失败，终止自动流程")
        logger.end_node("❌")
        return False
    
    logger.end_node("✅")
    return True
```

## 7. 配置文件更新

### config.json 添加内容

```json
{
  "console_output": {
    "show_debug": false,
    "show_progress": true,
    "compact_mode": true,
    "node_icons": {
      "init": "🚀",
      "step1": "🖼️",
      "step2": "✂️",
      "step3": "🔍",
      "step4": "📊",
      "complete": "✅"
    }
  }
}
```

## 8. 输出示例

### 简化前的输出
```
检查系统依赖...
✓ cv2
✓ PIL
✓ numpy
✓ 所有依赖已安装

检查数据文件...
✓ 找到 2 个基准装备图文件:
  - noblering.webp
  - target_equipment_1.webp
✓ 找到 2 个游戏截图文件:
  - MuMu-20251122-085551-742.png
  - MuMu-20251122-201210-068.png

步骤 1/3：获取原始图片
============================================================
此步骤用于检查和选择游戏截图
------------------------------------------------------------
找到 2 个游戏截图:
  1. MuMu-20251122-085551-742.png
  2. MuMu-20251122-201210-068.png

✅ 步骤1完成：已找到 2 个游戏截图
下一步：将这些截图分割成单个装备图片
... (大量详细输出)
```

### 简化后的输出
```
🚀 装备识别系统
├── 🔍 系统依赖检查
│  ├─ ✅ cv2
│  ├─ ✅ PIL
│  ├─ ✅ numpy
│  └─ ✅ 所有依赖已安装
├── 🖼️ 步骤1：获取原始图片
│  ├─ 找到 2 个游戏截图
│  └─ ✅ 完成
├── ✂️ 步骤2：分割原始图片
│  ├─ 处理截图: MuMu-20251122-085551-742.png
│  ├─ 切割装备: 12个
│  └─ ✅ 完成
├── 🔍 步骤3：装备识别匹配
│  ├─ 基准装备: noblering.webp
│  ├─ [████████████████████] 100.0% 12/12 - 匹配进度
│  ├─ 匹配装备: 2/12
│  └─ ✅ 完成
├── 📊 步骤4：整合识别结果
│  ├─ 处理文件: 12个
│  ├─ [████████████████████] 100.0% 12/12 - 处理进度
│  ├─ 成功整合: 10个
│  └─ ✅ 完成
└── ✅ 处理完成: 总计12个文件，成功10个
```

这些代码示例展示了如何实现节点式输出结构，简化控制台输出，同时保留必要的信息。通过使用统一的日志管理器，可以确保整个系统的输出风格一致，提高用户体验。