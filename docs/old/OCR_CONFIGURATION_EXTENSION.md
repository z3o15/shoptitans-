# OCR金额识别工具 - 配置管理扩展方案

## 1. 配置文件扩展

### 1.1 完整配置结构

在现有`config.json`基础上添加OCR相关配置：

```json
{
  "recognition": {
    "default_threshold": 80,
    "enable_masking": true,
    "enable_histogram": true,
    "algorithm_description": "高级彩色模板匹配算法，使用掩码直方图和颜色信息提供精确的装备识别"
  },
  "cutting": {
    "default_method": "fixed",
    "fixed_grid": [5, 2],
    "fixed_item_width": 210,
    "fixed_item_height": 160,
    "fixed_margin_left": 10,
    "fixed_margin_top": 275,
    "fixed_h_spacing": 15,
    "fixed_v_spacing": 20,
    "contour_min_area": 800,
    "contour_max_area": 50000
  },
  "paths": {
    "images_dir": "images",
    "base_equipment_dir": "base_equipment",
    "game_screenshots_dir": "game_screenshots",
    "cropped_equipment_dir": "cropped_equipment",
    "cropped_equipment_marker_dir": "cropped_equipment_marker",
    "logs_dir": "recognition_logs",
    "ocr_output_dir": "ocr_output",
    "ocr_logs_dir": "ocr_logs"
  },
  "logging": {
    "enable_logging": true,
    "log_level": "INFO",
    "include_algorithm_info": true,
    "include_performance_metrics": true
  },
  "performance": {
    "enable_caching": true,
    "cache_size": 100,
    "parallel_processing": false,
    "max_workers": 4
  },
  "ui": {
    "show_algorithm_selection": true,
    "show_performance_info": true,
    "show_detailed_results": true
  },
  "annotation": {
    "enable_annotation": true,
    "circle_color": "red",
    "circle_width": 3,
    "font_size": 12,
    "show_similarity_text": true,
    "auto_generate_annotation": false,
    "annotation_output_dir": "annotated_screenshots"
  },
  "ocr": {
    "enabled": true,
    "engine": "easyocr",
    "languages": ["en"],
    "gpu_enabled": false,
    "confidence_threshold": 0.5,
    "batch_processing": {
      "enabled": true,
      "batch_size": 10,
      "parallel_workers": 2
    },
    "image_preprocessing": {
      "resize_max_dimension": 1000,
      "enhance_contrast": true,
      "denoise": true,
      "sharpen": false,
      "convert_to_grayscale": true
    },
    "text_detection": {
      "min_confidence": 0.3,
      "text_threshold": 0.5,
      "low_text": 0.4,
      "link_threshold": 0.4,
      "canvas_size": 2560,
      "mag_ratio": 1.0
    },
    "amount_extraction": {
      "patterns": [
        "\\d+",
        "\\d+[.,]\\d{1,2}",
        "\\d+[kKmM]",
        "\\$\\s*\\d+",
        "\\d+\\s*gold",
        "\\d+\\s*g"
      ],
      "min_amount": 0,
      "max_amount": 999999999,
      "decimal_separator": ".",
      "thousands_separator": ",",
      "currency_symbols": ["$", "€", "£", "¥"],
      "unit_keywords": ["gold", "g", "coins", "coin"]
    },
    "file_naming": {
      "separator": "_",
      "amount_prefix": "",
      "amount_suffix": "",
      "case_sensitive": false,
      "max_length": 255,
      "handle_conflicts": "timestamp",
      "preserve_extension": true
    },
    "csv_output": {
      "enabled": true,
      "filename": "ocr_rename_records.csv",
      "include_timestamp": true,
      "include_confidence": true,
      "include_recognized_text": true,
      "include_processing_time": true,
      "overwrite_existing": false,
      "encoding": "utf-8",
      "date_format": "%Y-%m-%d %H:%M:%S"
    },
    "logging": {
      "enabled": true,
      "log_level": "INFO",
      "log_file": "ocr_recognition.log",
      "max_file_size": "10MB",
      "backup_count": 5,
      "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    },
    "error_handling": {
      "max_retries": 3,
      "retry_delay": 1.0,
      "continue_on_error": true,
      "save_failed_images": true,
      "failed_images_dir": "failed_ocr_images"
    },
    "performance": {
      "enable_caching": true,
      "cache_size": 50,
      "cache_ttl": 3600,
      "memory_limit": "512MB",
      "timeout_seconds": 30
    }
  }
}
```

### 1.2 MVP简化配置

```json
{
  "ocr": {
    "enabled": true,
    "input_folder": "images/cropped_equipment_marker",
    "output_csv": "ocr_rename_records.csv",
    "confidence_threshold": 0.3,
    "rename_separator": "_",
    "supported_formats": [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]
  }
}
```

## 2. 配置管理器扩展

### 2.1 OCRConfigManager类设计

```python
import json
import os
from typing import Dict, Any, Optional, List
from .config_manager import ConfigManager

class OCRConfigManager:
    """OCR配置管理器，扩展现有配置管理器功能"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None, 
                 config_path: str = "config.json"):
        """初始化OCR配置管理器
        
        Args:
            config_manager: 基础配置管理器实例，如果为None则创建新实例
            config_path: 配置文件路径
        """
        self.config_manager = config_manager or ConfigManager(config_path)
        self.config_path = config_path
        self.ocr_config = self._load_ocr_config()
    
    def _load_ocr_config(self) -> Dict[str, Any]:
        """加载OCR相关配置"""
        base_config = self.config_manager.config
        ocr_config = base_config.get("ocr", {})
        
        # 合并默认配置
        default_ocr_config = self._get_default_ocr_config()
        return self._merge_configs(default_ocr_config, ocr_config)
    
    def _get_default_ocr_config(self) -> Dict[str, Any]:
        """获取默认OCR配置"""
        return {
            "enabled": True,
            "engine": "easyocr",
            "languages": ["en"],
            "gpu_enabled": False,
            "confidence_threshold": 0.5,
            "batch_processing": {
                "enabled": True,
                "batch_size": 10,
                "parallel_workers": 2
            },
            "image_preprocessing": {
                "resize_max_dimension": 1000,
                "enhance_contrast": True,
                "denoise": True,
                "sharpen": False,
                "convert_to_grayscale": True
            },
            "text_detection": {
                "min_confidence": 0.3,
                "text_threshold": 0.5,
                "low_text": 0.4,
                "link_threshold": 0.4,
                "canvas_size": 2560,
                "mag_ratio": 1.0
            },
            "amount_extraction": {
                "patterns": [
                    "\\d+",
                    "\\d+[.,]\\d{1,2}",
                    "\\d+[kKmM]",
                    "\\$\\s*\\d+",
                    "\\d+\\s*gold",
                    "\\d+\\s*g"
                ],
                "min_amount": 0,
                "max_amount": 999999999,
                "decimal_separator": ".",
                "thousands_separator": ",",
                "currency_symbols": ["$", "€", "£", "¥"],
                "unit_keywords": ["gold", "g", "coins", "coin"]
            },
            "file_naming": {
                "separator": "_",
                "amount_prefix": "",
                "amount_suffix": "",
                "case_sensitive": False,
                "max_length": 255,
                "handle_conflicts": "timestamp",
                "preserve_extension": True
            },
            "csv_output": {
                "enabled": True,
                "filename": "ocr_rename_records.csv",
                "include_timestamp": True,
                "include_confidence": True,
                "include_recognized_text": True,
                "include_processing_time": True,
                "overwrite_existing": False,
                "encoding": "utf-8",
                "date_format": "%Y-%m-%d %H:%M:%S"
            },
            "logging": {
                "enabled": True,
                "log_level": "INFO",
                "log_file": "ocr_recognition.log",
                "max_file_size": "10MB",
                "backup_count": 5,
                "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "error_handling": {
                "max_retries": 3,
                "retry_delay": 1.0,
                "continue_on_error": True,
                "save_failed_images": True,
                "failed_images_dir": "failed_ocr_images"
            },
            "performance": {
                "enable_caching": True,
                "cache_size": 50,
                "cache_ttl": 3600,
                "memory_limit": "512MB",
                "timeout_seconds": 30
            }
        }
    
    def _merge_configs(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """合并配置字典，保留默认值中不存在于加载配置中的项"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def get_ocr_config(self) -> Dict[str, Any]:
        """获取OCR主配置"""
        return self.ocr_config
    
    def is_enabled(self) -> bool:
        """检查OCR功能是否启用"""
        return self.ocr_config.get("enabled", True)
    
    def get_engine_config(self) -> Dict[str, Any]:
        """获取OCR引擎配置"""
        return {
            "engine": self.ocr_config.get("engine", "easyocr"),
            "languages": self.ocr_config.get("languages", ["en"]),
            "gpu_enabled": self.ocr_config.get("gpu_enabled", False),
            "confidence_threshold": self.ocr_config.get("confidence_threshold", 0.5)
        }
    
    def get_batch_processing_config(self) -> Dict[str, Any]:
        """获取批量处理配置"""
        return self.ocr_config.get("batch_processing", {
            "enabled": True,
            "batch_size": 10,
            "parallel_workers": 2
        })
    
    def get_image_preprocessing_config(self) -> Dict[str, Any]:
        """获取图像预处理配置"""
        return self.ocr_config.get("image_preprocessing", {
            "resize_max_dimension": 1000,
            "enhance_contrast": True,
            "denoise": True,
            "sharpen": False,
            "convert_to_grayscale": True
        })
    
    def get_text_detection_config(self) -> Dict[str, Any]:
        """获取文本检测配置"""
        return self.ocr_config.get("text_detection", {
            "min_confidence": 0.3,
            "text_threshold": 0.5,
            "low_text": 0.4,
            "link_threshold": 0.4,
            "canvas_size": 2560,
            "mag_ratio": 1.0
        })
    
    def get_amount_extraction_config(self) -> Dict[str, Any]:
        """获取金额提取配置"""
        return self.ocr_config.get("amount_extraction", {
            "patterns": ["\\d+", "\\d+[.,]\\d{1,2}", "\\d+[kKmM]"],
            "min_amount": 0,
            "max_amount": 999999999,
            "decimal_separator": ".",
            "thousands_separator": ",",
            "currency_symbols": ["$", "€", "£", "¥"],
            "unit_keywords": ["gold", "g", "coins", "coin"]
        })
    
    def get_file_naming_config(self) -> Dict[str, Any]:
        """获取文件命名配置"""
        return self.ocr_config.get("file_naming", {
            "separator": "_",
            "amount_prefix": "",
            "amount_suffix": "",
            "case_sensitive": False,
            "max_length": 255,
            "handle_conflicts": "timestamp",
            "preserve_extension": True
        })
    
    def get_csv_output_config(self) -> Dict[str, Any]:
        """获取CSV输出配置"""
        return self.ocr_config.get("csv_output", {
            "enabled": True,
            "filename": "ocr_rename_records.csv",
            "include_timestamp": True,
            "include_confidence": True,
            "include_recognized_text": True,
            "include_processing_time": True,
            "overwrite_existing": False,
            "encoding": "utf-8",
            "date_format": "%Y-%m-%d %H:%M:%S"
        })
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.ocr_config.get("logging", {
            "enabled": True,
            "log_level": "INFO",
            "log_file": "ocr_recognition.log",
            "max_file_size": "10MB",
            "backup_count": 5,
            "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        })
    
    def get_error_handling_config(self) -> Dict[str, Any]:
        """获取错误处理配置"""
        return self.ocr_config.get("error_handling", {
            "max_retries": 3,
            "retry_delay": 1.0,
            "continue_on_error": True,
            "save_failed_images": True,
            "failed_images_dir": "failed_ocr_images"
        })
    
    def get_performance_config(self) -> Dict[str, Any]:
        """获取性能配置"""
        return self.ocr_config.get("performance", {
            "enable_caching": True,
            "cache_size": 50,
            "cache_ttl": 3600,
            "memory_limit": "512MB",
            "timeout_seconds": 30
        })
    
    def get_input_folder(self) -> str:
        """获取输入文件夹路径"""
        paths_config = self.config_manager.get_paths_config()
        base_dir = paths_config.get("images_dir", "images")
        marker_dir = self.ocr_config.get("input_folder", "cropped_equipment_marker")
        
        # 如果是相对路径，则与images_dir组合
        if not os.path.isabs(marker_dir):
            return os.path.join(base_dir, marker_dir)
        return marker_dir
    
    def get_output_csv_path(self) -> str:
        """获取输出CSV文件路径"""
        csv_config = self.get_csv_output_config()
        csv_filename = csv_config.get("filename", "ocr_rename_records.csv")
        
        # 如果是相对路径，则放在项目根目录
        if not os.path.isabs(csv_filename):
            return csv_filename
        return csv_filename
    
    def update_ocr_config(self, **kwargs) -> None:
        """更新OCR配置
        
        Args:
            **kwargs: 要更新的配置项
        """
        # 更新内存中的配置
        for key, value in kwargs.items():
            if isinstance(value, dict) and key in self.ocr_config and isinstance(self.ocr_config[key], dict):
                self.ocr_config[key].update(value)
            else:
                self.ocr_config[key] = value
        
        # 更新基础配置管理器中的配置
        self.config_manager.config["ocr"] = self.ocr_config
        self.config_manager._save_config(self.config_manager.config)
        
        print("OCR配置已更新")
    
    def save_ocr_config(self) -> None:
        """保存OCR配置到文件"""
        self.config_manager.config["ocr"] = self.ocr_config
        self.config_manager._save_config(self.config_manager.config)
        print(f"OCR配置已保存到: {self.config_path}")
    
    def validate_ocr_config(self) -> List[str]:
        """验证OCR配置的有效性
        
        Returns:
            错误信息列表，如果配置有效则返回空列表
        """
        errors = []
        
        # 验证基本配置
        if not isinstance(self.ocr_config.get("enabled"), bool):
            errors.append("ocr.enabled 必须是布尔值")
        
        confidence_threshold = self.ocr_config.get("confidence_threshold")
        if not isinstance(confidence_threshold, (int, float)) or not 0 <= confidence_threshold <= 1:
            errors.append("ocr.confidence_threshold 必须是0-1之间的数字")
        
        # 验证路径配置
        input_folder = self.get_input_folder()
        if not os.path.exists(input_folder):
            errors.append(f"输入文件夹不存在: {input_folder}")
        
        # 验证文件命名配置
        file_naming = self.get_file_naming_config()
        max_length = file_naming.get("max_length", 255)
        if not isinstance(max_length, int) or max_length <= 0:
            errors.append("ocr.file_naming.max_length 必须是正整数")
        
        # 验证金额提取配置
        amount_extraction = self.get_amount_extraction_config()
        patterns = amount_extraction.get("patterns", [])
        if not isinstance(patterns, list) or not patterns:
            errors.append("ocr.amount_extraction.patterns 必须是非空列表")
        
        min_amount = amount_extraction.get("min_amount", 0)
        max_amount = amount_extraction.get("max_amount", 999999999)
        if not isinstance(min_amount, (int, float)) or not isinstance(max_amount, (int, float)):
            errors.append("ocr.amount_extraction.min_amount 和 max_amount 必须是数字")
        elif min_amount > max_amount:
            errors.append("ocr.amount_extraction.min_amount 不能大于 max_amount")
        
        return errors
    
    def print_ocr_config_summary(self) -> None:
        """打印OCR配置摘要"""
        print("\n" + "=" * 50)
        print("OCR配置摘要")
        print("=" * 50)
        
        print(f"OCR功能: {'启用' if self.is_enabled() else '禁用'}")
        
        engine_config = self.get_engine_config()
        print(f"OCR引擎: {engine_config['engine']}")
        print(f"支持语言: {', '.join(engine_config['languages'])}")
        print(f"GPU加速: {'启用' if engine_config['gpu_enabled'] else '禁用'}")
        print(f"置信度阈值: {engine_config['confidence_threshold']}")
        
        batch_config = self.get_batch_processing_config()
        print(f"批量处理: {'启用' if batch_config['enabled'] else '禁用'}")
        if batch_config['enabled']:
            print(f"批处理大小: {batch_config['batch_size']}")
            print(f"并行工作数: {batch_config['parallel_workers']}")
        
        file_naming = self.get_file_naming_config()
        print(f"文件命名分隔符: '{file_naming['separator']}'")
        print(f"冲突处理方式: {file_naming['handle_conflicts']}")
        
        csv_config = self.get_csv_output_config()
        print(f"CSV记录: {'启用' if csv_config['enabled'] else '禁用'}")
        if csv_config['enabled']:
            print(f"CSV文件名: {csv_config['filename']}")
        
        print(f"输入文件夹: {self.get_input_folder()}")
        print(f"输出CSV路径: {self.get_output_csv_path()}")
        
        print("=" * 50)
```

### 2.2 MVP简化配置管理器

```python
import json
import os
from typing import Dict, Any, Optional

class MVPOCRConfig:
    """MVP版本的OCR配置读取器"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化配置读取器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件不存在: {self.config_path}，使用默认配置")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "ocr": {
                "enabled": True,
                "input_folder": "images/cropped_equipment_marker",
                "output_csv": "ocr_rename_records.csv",
                "confidence_threshold": 0.3,
                "rename_separator": "_",
                "supported_formats": [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]
            }
        }
    
    def get_ocr_config(self) -> Dict[str, Any]:
        """获取OCR配置"""
        return self.config.get("ocr", self._get_default_config()["ocr"])
    
    def is_enabled(self) -> bool:
        """检查OCR功能是否启用"""
        return self.get_ocr_config().get("enabled", True)
    
    def get_input_folder(self) -> str:
        """获取输入文件夹路径"""
        return self.get_ocr_config().get("input_folder", "images/cropped_equipment_marker")
    
    def get_output_csv_path(self) -> str:
        """获取输出CSV文件路径"""
        return self.get_ocr_config().get("output_csv", "ocr_rename_records.csv")
    
    def get_confidence_threshold(self) -> float:
        """获取置信度阈值"""
        return self.get_ocr_config().get("confidence_threshold", 0.3)
    
    def get_rename_separator(self) -> str:
        """获取重命名分隔符"""
        return self.get_ocr_config().get("rename_separator", "_")
    
    def get_supported_formats(self) -> list:
        """获取支持的文件格式"""
        return self.get_ocr_config().get("supported_formats", [".png", ".jpg", ".jpeg", ".bmp", ".tiff"])
```

## 3. 配置验证和错误处理

### 3.1 配置验证器

```python
class OCRConfigValidator:
    """OCR配置验证器"""
    
    @staticmethod
    def validate_engine_config(config: Dict[str, Any]) -> List[str]:
        """验证OCR引擎配置"""
        errors = []
        
        if "engine" not in config:
            errors.append("缺少OCR引擎配置")
        elif config["engine"] not in ["easyocr", "tesseract", "paddleocr"]:
            errors.append(f"不支持的OCR引擎: {config['engine']}")
        
        if "languages" not in config or not config["languages"]:
            errors.append("缺少或空的OCR语言配置")
        
        confidence_threshold = config.get("confidence_threshold", 0.5)
        if not isinstance(confidence_threshold, (int, float)) or not 0 <= confidence_threshold <= 1:
            errors.append("置信度阈值必须是0-1之间的数字")
        
        return errors
    
    @staticmethod
    def validate_amount_extraction_config(config: Dict[str, Any]) -> List[str]:
        """验证金额提取配置"""
        errors = []
        
        patterns = config.get("patterns", [])
        if not isinstance(patterns, list) or not patterns:
            errors.append("金额提取模式必须是非空列表")
        
        min_amount = config.get("min_amount", 0)
        max_amount = config.get("max_amount", 999999999)
        if not isinstance(min_amount, (int, float)) or not isinstance(max_amount, (int, float)):
            errors.append("最小和最大金额必须是数字")
        elif min_amount > max_amount:
            errors.append("最小金额不能大于最大金额")
        
        return errors
    
    @staticmethod
    def validate_file_naming_config(config: Dict[str, Any]) -> List[str]:
        """验证文件命名配置"""
        errors = []
        
        max_length = config.get("max_length", 255)
        if not isinstance(max_length, int) or max_length <= 0:
            errors.append("文件名最大长度必须是正整数")
        
        handle_conflicts = config.get("handle_conflicts", "timestamp")
        if handle_conflicts not in ["timestamp", "counter", "skip"]:
            errors.append("冲突处理方式必须是: timestamp, counter, skip 之一")
        
        return errors
```

## 4. 配置迁移工具

### 4.1 配置迁移器

```python
class OCRConfigMigrator:
    """OCR配置迁移器"""
    
    @staticmethod
    def migrate_v1_to_v2(old_config: Dict[str, Any]) -> Dict[str, Any]:
        """从v1配置迁移到v2配置"""
        new_config = old_config.copy()
        
        # 如果存在旧的OCR配置，迁移到新的结构
        if "ocr" in old_config:
            old_ocr = old_config["ocr"]
            
            # 迁移重命名配置
            if "rename_separator" in old_ocr:
                if "file_naming" not in new_config["ocr"]:
                    new_config["ocr"]["file_naming"] = {}
                new_config["ocr"]["file_naming"]["separator"] = old_ocr["rename_separator"]
            
            # 迁移置信度阈值
            if "confidence_threshold" in old_ocr:
                new_config["ocr"]["confidence_threshold"] = old_ocr["confidence_threshold"]
        
        return new_config
    
    @staticmethod
    def backup_config(config_path: str) -> str:
        """备份配置文件"""
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{config_path}.backup_{timestamp}"
        shutil.copy2(config_path, backup_path)
        return backup_path
```

## 5. 配置使用示例

### 5.1 基本使用

```python
# 创建配置管理器
config_manager = ConfigManager()
ocr_config_manager = OCRConfigManager(config_manager)

# 获取配置
ocr_config = ocr_config_manager.get_ocr_config()
engine_config = ocr_config_manager.get_engine_config()
file_naming_config = ocr_config_manager.get_file_naming_config()

# 检查配置有效性
errors = ocr_config_manager.validate_ocr_config()
if errors:
    print("配置错误:")
    for error in errors:
        print(f"  - {error}")
else:
    print("配置验证通过")
```

### 5.2 配置更新

```python
# 更新OCR配置
ocr_config_manager.update_ocr_config(
    confidence_threshold=0.7,
    file_naming={"separator": "-", "max_length": 200}
)

# 保存配置
ocr_config_manager.save_ocr_config()
```

### 5.3 MVP使用

```python
# MVP版本使用
mvp_config = MVPOCRConfig()

# 获取基本配置
input_folder = mvp_config.get_input_folder()
output_csv = mvp_config.get_output_csv_path()
confidence_threshold = mvp_config.get_confidence_threshold()
```

## 6. 总结

配置管理扩展方案提供了：

1. **完整的配置结构**：支持OCR功能的所有配置需求
2. **向后兼容**：扩展现有配置系统，保持一致性
3. **灵活的配置管理**：支持配置读取、更新、验证
4. **MVP简化版本**：提供最小可行产品的配置支持
5. **配置验证**：确保配置的有效性和一致性
6. **配置迁移**：支持配置版本的升级和迁移

这个设计确保了OCR金额识别工具能够灵活配置，同时保持与现有系统的一致性。