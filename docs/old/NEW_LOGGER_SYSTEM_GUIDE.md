# 新日志系统使用指南

## 概述

本文档介绍了新的日志系统，该系统提供了按步骤分类的日志管理、统一的日志格式和自动报告生成功能。

## 系统架构

### 核心组件

1. **StepLogger** (`src/step_logger.py`) - 步骤日志管理器
   - 按步骤分类记录日志
   - 自动创建和管理目录结构
   - 提供统计信息收集

2. **ReportGenerator** (`src/report_generator.py`) - 报告生成器
   - 生成Markdown格式的步骤报告
   - 生成汇总报告
   - 支持自定义报告内容

3. **UnifiedLogger** (`src/unified_logger.py`) - 统一日志管理器
   - 整合步骤日志和终端输出策略
   - 提供统一的日志接口
   - 支持可配置的输出策略

4. **LoggerAdapter** (`src/logger_adapter.py`) - 日志适配器
   - 提供新旧日志系统的兼容性接口
   - 支持无缝切换日志系统
   - 集成现有模块

## 目录结构

```
output/
├─ step1_helper/
│   ├─ log.txt          # 步骤日志文件
│   ├─ report.md        # 步骤报告
│   └─ temp_files/      # 临时文件目录
├─ step2_cut/
│   ├─ log.txt          # 步骤日志文件
│   ├─ report.md        # 步骤报告
│   ├─ images/          # 输出图片目录
│   └─ txt/             # 输出文本目录
├─ step3_match/
│   ├─ log.txt          # 步骤日志文件
│   ├─ report.md        # 步骤报告
│   ├─ images/          # 输出图片目录
│   └─ txt/             # 输出文本目录
└─ step5_ocr/
    ├─ log.txt          # 步骤日志文件
    ├─ report.md        # 步骤报告
    ├─ images/          # 输出图片目录
    └─ txt/             # 输出文本目录
```

## 使用方法

### 1. 基本使用

```python
from src.unified_logger import get_unified_logger, init_unified_logger_from_config

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

# 开始步骤
logger.start_step("step2_cut", "裁剪游戏截图")

# 记录日志
logger.log_info("开始处理截图", show_in_console=True)
logger.log_warning("发现异常情况", show_in_console=True)
logger.log_error("处理失败", show_in_console=True)
logger.log_success("处理完成", show_in_console=True)

# 记录文件处理
logger.log_file_processed("image1.png", success=True, details="尺寸: 800x600")

# 记录进度
logger.log_progress(5, 10, "处理进度")

# 记录性能指标
logger.log_performance_metric("处理速度", "2.5 files/sec")

# 结束步骤
logger.end_step("step2_cut", "完成")

# 生成汇总报告
summary_report = logger.generate_summary_report()

# 关闭日志
logger.close_all_logs()
```

### 2. 使用日志适配器

```python
from src.logger_adapter import create_logger_adapter, ScreenshotCutterWithAdapter

# 创建日志适配器
adapter = create_logger_adapter(use_new_logger=True)

# 使用适配器包装现有模块
cutter = ScreenshotCutterWithAdapter(adapter)

# 执行操作（会自动记录日志）
success = cutter.cut_screenshots("screenshot.png", "output/images")
```

### 3. 集成现有模块

```python
from src.logger_adapter import (
    create_logger_adapter,
    ScreenshotCutterWithAdapter,
    FeatureMatcherWithAdapter,
    OCRRecognizerWithAdapter
)

# 创建适配器
adapter = create_logger_adapter(use_new_logger=True)

# 创建处理器
cutter = ScreenshotCutterWithAdapter(adapter)
matcher = FeatureMatcherWithAdapter(adapter)
ocr = OCRRecognizerWithAdapter(adapter)

# 运行完整流水线
cutter.cut_screenshots("screenshot.png", "output/step2_cut/images")
matcher.match_equipment("template.png", "output/step2_cut/images")
ocr.recognize_amounts("output/step2_cut/images")
```

## 配置选项

### 日志配置

```python
config = {
    "base_output_dir": "output",        # 输出基础目录
    "console_mode": True,               # 是否启用控制台输出
    
    # 输出策略配置
    "output": {
        "show_step_progress": True,       # 显示步骤进度
        "show_item_details": False,       # 显示每个项目的详细信息
        "show_warnings": True,           # 显示警告
        "show_errors": True,             # 显示错误
        "show_success_summary": True,     # 显示成功摘要
        "show_performance_metrics": True  # 显示性能指标
    }
}
```

### 步骤配置

系统预定义了以下步骤：

- `step1_helper`: 辅助工具 (🔧)
- `step2_cut`: 图片裁剪 (✂️)
- `step3_match`: 装备匹配 (🔍)
- `step5_ocr`: OCR识别 (📝)

## 日志格式

### 文件日志格式

```
[2025-11-24 12:49:33] [INFO] 开始初始化辅助工具
[2025-11-24 12:49:33] [WARN] 这是一个测试警告
[2025-11-24 12:49:33] [SUCCESS] 处理完成
[2025-11-24 12:49:33] [ERROR] 处理失败
```

### 控制台输出格式

```
✂️ 开始步骤: 图片裁剪
  ℹ️ 开始处理截图
  ⚠️ 发现异常情况
  ❌ 处理失败
  ✅ 处理完成
  [████████████████████] 100.0% 10/10 - 处理完成
  📊 处理速度: 2.5 files/sec
✂️ 步骤结束: 图片裁剪 - 完成 (1.25s)
  处理: 10 | 成功: 8 | 失败: 2
```

## 报告生成

### 步骤报告

每个步骤都会生成详细的Markdown报告，包含：

- 处理时间信息
- 处理统计表格
- 详细信息（文件列表、错误详情、警告详情）
- 性能指标
- 输出文件列表

### 汇总报告

汇总报告包含所有步骤的：

- 总体统计表格
- 处理时间线
- 详细报告链接
- 系统信息
- 改进建议

## 迁移指南

### 从旧日志系统迁移

1. **使用日志适配器**（推荐）
   ```python
   # 旧代码
   from src.node_logger import get_logger
   logger = get_logger()
   
   # 新代码
   from src.logger_adapter import create_logger_adapter
   adapter = create_logger_adapter(use_new_logger=False)  # 保持使用旧系统
   # 或者
   adapter = create_logger_adapter(use_new_logger=True)   # 切换到新系统
   ```

2. **直接使用新日志系统**
   ```python
   # 旧代码
   logger.start_node("节点名称")
   logger.log_info("信息")
   logger.end_node("✅")
   
   # 新代码
   logger.start_step("step_id", "步骤描述")
   logger.log_info("信息")
   logger.end_step("step_id", "完成")
   ```

### 兼容性说明

- 新日志系统完全兼容旧系统的API
- 可以通过配置随时切换日志系统
- 现有代码无需大幅修改即可使用新系统

## 最佳实践

1. **合理使用日志级别**
   - INFO: 一般信息
   - WARNING: 警告信息
   - ERROR: 错误信息
   - SUCCESS: 成功信息

2. **控制台输出策略**
   - 只在控制台显示关键信息
   - 详细信息记录到文件
   - 使用进度条显示处理进度

3. **性能监控**
   - 记录关键性能指标
   - 统计处理时间和成功率
   - 定期生成报告分析

4. **错误处理**
   - 详细记录错误信息
   - 提供错误恢复建议
   - 统计错误类型和频率

## 故障排除

### 常见问题

1. **导入错误**
   ```
   ImportError: attempted relative import with no known parent package
   ```
   解决方案：确保所有模块都在src目录中，并正确设置Python路径

2. **目录创建失败**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   解决方案：检查输出目录的写入权限

3. **日志文件无法写入**
   ```
   FileNotFoundError: [Errno 2] No such file or directory
   ```
   解决方案：确保输出目录存在且有写入权限

### 调试技巧

1. **启用详细日志**
   ```python
   config["output"]["show_item_details"] = True
   ```

2. **检查日志文件**
   - 查看 `output/step*/log.txt` 文件
   - 检查是否有错误或警告信息

3. **验证报告生成**
   - 检查 `output/step*/report.md` 文件
   - 确认统计信息是否正确

## 示例代码

完整的使用示例请参考：

- `test_new_logger.py` - 基本功能测试
- `src/logger_integration_example.py` - 集成示例
- `test_logger_adapter.py` - 适配器测试

## 更新日志

### v1.0.0 (2025-11-24)
- 初始版本发布
- 实现步骤日志管理
- 实现报告生成功能
- 实现日志适配器
- 实现终端输出策略