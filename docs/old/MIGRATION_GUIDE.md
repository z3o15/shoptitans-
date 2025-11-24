# 项目结构迁移指南

## 概述

本指南帮助用户从旧的项目结构迁移到新的统一配置和输出结构。

## 迁移步骤

### 第一步：备份现有数据

在开始迁移之前，请备份以下重要数据：

1. **配置文件**
   - `config.json`
   - `config/config.json`
   - `config/optimized_ocr_config.json`

2. **输出数据**
   - `step_tests/` 目录下的所有输出文件
   - `output/` 目录下的所有文件

3. **自定义配置**
   - 任何修改过的配置参数
   - 自定义的路径设置

### 第二步：更新配置引用

#### 旧代码示例
```python
# 旧的配置管理方式
from src.config.config_manager import get_config_manager
from src.config.ocr_config_manager import get_ocr_config_manager

config_manager = get_config_manager()
ocr_config_manager = get_ocr_config_manager()

# 获取配置
threshold = config_manager.get_default_threshold()
ocr_enabled = ocr_config_manager.is_ocr_enabled()
```

#### 新代码示例
```python
# 新的统一配置管理方式
from config.unified_config_manager import get_unified_config_manager

config_manager = get_unified_config_manager()

# 获取配置
threshold = config_manager.get_default_threshold()
ocr_enabled = config_manager.is_ocr_enabled()

# 或者直接获取配置节
recognition_config = config_manager.get_recognition_config()
ocr_config = config_manager.get_ocr_config()
```

### 第三步：更新输出路径

#### 旧代码示例
```python
# 旧的输出路径方式
output_path = "step_tests/step1_helper/"
log_file = os.path.join(output_path, "log.txt")
report_file = os.path.join(output_path, "report.md")
```

#### 新代码示例
```python
# 新的输出管理方式
from config.output_manager import get_output_manager

output_manager = get_output_manager()

# 创建标准输出目录
dirs = output_manager.ensure_step_dirs("step1")

# 获取文件路径
log_file = os.path.join(dirs["logs"], "log.txt")
report_file = os.path.join(dirs["reports"], "report.md")

# 或者使用便捷方法
log_file = output_manager.save_log("step1", "日志内容")
report_file = output_manager.save_report("step1", "# 报告内容")
```

### 第四步：迁移配置文件

#### 自动迁移脚本
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置迁移脚本
将旧的配置文件迁移到新的统一配置结构
"""

import json
import os
from config.unified_config_manager import get_unified_config_manager

def migrate_configs():
    """迁移配置文件"""
    config_manager = get_unified_config_manager()
    
    # 读取旧配置文件
    old_configs = {}
    
    # 读取根目录config.json
    if os.path.exists("config.json"):
        with open("config.json", 'r', encoding='utf-8') as f:
            old_configs["root"] = json.load(f)
    
    # 读取config/config.json
    if os.path.exists("config/config.json"):
        with open("config/config.json", 'r', encoding='utf-8') as f:
            old_configs["config"] = json.load(f)
    
    # 读取config/optimized_ocr_config.json
    if os.path.exists("config/optimized_ocr_config.json"):
        with open("config/optimized_ocr_config.json", 'r', encoding='utf-8') as f:
            old_configs["ocr"] = json.load(f)
    
    # 合并配置（优先级：ocr > config > root）
    merged_config = {}
    
    # 从根配置开始
    if "root" in old_configs:
        merged_config.update(old_configs["root"])
    
    # 覆盖config配置
    if "config" in old_configs:
        for key, value in old_configs["config"].items():
            if key in merged_config and isinstance(merged_config[key], dict) and isinstance(value, dict):
                merged_config[key].update(value)
            else:
                merged_config[key] = value
    
    # 覆盖OCR配置
    if "ocr" in old_configs:
        for key, value in old_configs["ocr"].items():
            if key == "ocr":
                # OCR配置节特殊处理
                if "ocr" not in merged_config:
                    merged_config["ocr"] = {}
                merged_config["ocr"].update(value)
            else:
                if key in merged_config and isinstance(merged_config[key], dict) and isinstance(value, dict):
                    merged_config[key].update(value)
                else:
                    merged_config[key] = value
    
    # 保存新配置
    config_manager.config = merged_config
    config_manager._save_config(merged_config)
    
    print("✓ 配置文件迁移完成")
    print(f"新配置文件路径: {config_manager.config_path}")

if __name__ == "__main__":
    migrate_configs()
```

### 第五步：迁移输出文件

#### 自动迁移脚本
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输出文件迁移脚本
将旧的输出文件迁移到新的输出结构
"""

import os
import shutil
from config.output_manager import get_output_manager

def migrate_output_files():
    """迁移输出文件"""
    output_manager = get_output_manager()
    
    # 迁移step_tests目录
    if os.path.exists("step_tests"):
        for item in os.listdir("step_tests"):
            item_path = os.path.join("step_tests", item)
            
            if os.path.isdir(item_path):
                # 确定步骤名称
                if "step1" in item.lower() or "helper" in item.lower():
                    step = "step1"
                elif "step2" in item.lower() or "cut" in item.lower():
                    step = "step2"
                elif "step3" in item.lower() or "match" in item.lower():
                    step = "step3"
                elif "step4" in item.lower() or "ocr" in item.lower():
                    step = "step4"
                else:
                    continue
                
                # 迁移目录
                new_dir = output_manager.migrate_old_output(item_path, step, use_timestamp=False)
                print(f"✓ 已迁移 {item_path} -> {new_dir}")
    
    # 迁移output目录
    if os.path.exists("output"):
        for item in os.listdir("output"):
            item_path = os.path.join("output", item)
            
            if os.path.isdir(item_path):
                # 确定步骤名称
                if "step1" in item.lower() or "helper" in item.lower():
                    step = "step1"
                elif "step2" in item.lower() or "cut" in item.lower():
                    step = "step2"
                elif "step3" in item.lower() or "match" in item.lower():
                    step = "step3"
                elif "step4" in item.lower() or "ocr" in item.lower():
                    step = "step4"
                else:
                    continue
                
                # 迁移目录
                new_dir = output_manager.migrate_old_output(item_path, step, use_timestamp=False)
                print(f"✓ 已迁移 {item_path} -> {new_dir}")
    
    print("✓ 输出文件迁移完成")

if __name__ == "__main__":
    migrate_output_files()
```

### 第六步：更新主程序

#### 更新主程序配置引用
```python
# 在 src/core/main.py 中更新导入
# 旧代码
# from src.config.config_manager import get_config_manager

# 新代码
from config.unified_config_manager import get_unified_config_manager

# 更新配置管理器获取
# 旧代码
# config_manager = get_config_manager()

# 新代码
config_manager = get_unified_config_manager()
```

#### 更新输出路径管理
```python
# 在主程序中添加输出管理
from config.output_manager import get_output_manager

# 获取输出管理器
output_manager = get_output_manager(config_manager)

# 创建输出目录
dirs = output_manager.ensure_step_dirs("step1")

# 保存日志和报告
log_path = output_manager.save_log("step1", log_content)
report_path = output_manager.save_report("step1", report_content)
```

## 常见问题

### Q: 如何保留自定义配置？

A: 迁移脚本会自动合并所有配置文件，保留所有自定义设置。如果有冲突，优先级为：
1. `config/optimized_ocr_config.json`
2. `config/config.json`
3. `config.json`

### Q: 如何处理自定义路径？

A: 新的配置系统支持路径配置的完全自定义。在 `config/unified_config.json` 的 `paths` 节中设置您的自定义路径。

### Q: 迁移后如何验证配置？

A: 使用以下代码验证配置：
```python
from config.unified_config_manager import get_unified_config_manager

config_manager = get_unified_config_manager()
config_manager.print_config_summary()
```

### Q: 如何回滚迁移？

A: 如果需要回滚，请恢复备份的配置文件和输出文件，并使用旧的导入路径。

## 迁移检查清单

- [ ] 备份现有配置和输出文件
- [ ] 运行配置迁移脚本
- [ ] 运行输出文件迁移脚本
- [ ] 更新代码中的配置引用
- [ ] 更新代码中的输出路径
- [ ] 测试新配置系统
- [ ] 验证输出文件结构
- [ ] 更新文档和注释

## 迁移后验证

### 验证配置系统
```python
# 测试配置管理器
from config.unified_config_manager import get_unified_config_manager

config_manager = get_unified_config_manager()
config_manager.print_config_summary()

# 测试配置更新
config_manager.set_default_threshold(85)
print(f"新阈值: {config_manager.get_default_threshold()}")
```

### 验证输出系统
```python
# 测试输出管理器
from config.output_manager import get_output_manager

output_manager = get_output_manager()

# 测试目录创建
dirs = output_manager.ensure_step_dirs("step1")
print("创建的目录:", dirs)

# 测试文件保存
log_path = output_manager.save_log("step1", "测试日志")
report_path = output_manager.save_report("step1", "# 测试报告")
print(f"日志文件: {log_path}")
print(f"报告文件: {report_path}")
```

## 获取帮助

如果在迁移过程中遇到问题，请：

1. 查看详细的重构报告：`docs/RESTRUCTURE_REPORT.md`
2. 检查配置分析文档：`docs/CONFIG_DUPLICATION_ANALYSIS.md`
3. 查看输出结构分析：`docs/STEP_TESTS_OUTPUT_OVERLAP_ANALYSIS.md`
4. 运行验证脚本确认迁移成功

## 迁移完成后的清理

迁移成功后，可以删除以下旧文件：

1. **旧配置文件**
   - `config.json`（根目录）
   - `src/config/config_manager.py`
   - `src/config/ocr_config_manager.py`

2. **旧输出目录**
   - `step_tests/`（确认所有文件已迁移）
   - `output/` 中的旧结构目录

3. **旧测试文件**
   - `step_tests/` 中的Python文件（已迁移到 `tests/`）

请谨慎执行清理操作，确保所有重要数据已正确迁移。