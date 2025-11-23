# 项目结构说明

本文档说明了"shoptitans 图片分隔和匹配"项目的目录结构和各部分的功能。

## 目录结构

```
shoptitans 图片分隔和匹配/
├── README.md                    # 项目主要说明文档
├── README_CLEANED.md           # 清理后的说明文档
├── requirements.txt             # 项目依赖列表
├── run_recognition_start.py     # 主启动脚本（推荐使用）
├── start.py                    # 备用启动脚本
├── test_integration.py          # 集成测试脚本
│
├── config/                     # 配置文件目录
│   ├── config.json             # 主配置文件
│   └── optimized_ocr_config.json # OCR优化配置
│
├── src/                        # 源代码目录
│   ├── __init__.py
│   ├── main.py                 # 主程序入口
│   ├── config_manager.py       # 配置管理器
│   ├── equipment_recognizer.py # 装备识别器
│   ├── feature_matcher.py      # 特征匹配器
│   ├── feature_cache_manager.py # 特征缓存管理器
│   ├── enhanced_feature_matcher.py # 增强特征匹配器
│   ├── screenshot_cutter.py    # 截图切割器
│   ├── image_annotator.py     # 图像注释器
│   ├── enhanced_ocr_recognizer.py # 增强OCR识别器
│   ├── enhanced_ocr_recognizer_fixed.py # 修复版OCR识别器
│   ├── ocr_config_manager.py  # OCR配置管理器
│   ├── csv_record_manager.py  # CSV记录管理器
│   ├── file_renamer.py       # 文件重命名器
│   ├── node_logger.py          # 节点日志管理器
│   ├── advanced_matcher_standalone.py # 独立高级匹配器
│   └── standalone_modules_README.md # 独立模块说明
│
├── tools/                      # 工具脚本目录
│   └── build_feature_cache.py  # 特征缓存构建脚本
│
├── tests/                      # 测试文件目录
│   ├── __init__.py
│   ├── config.json             # 测试配置
│   ├── test_system.py          # 系统测试
│   ├── test_feature_cache.py   # 特征缓存测试
│   ├── test_performance_improvement.py # 性能改进测试
│   ├── test_integration.py     # 集成测试
│   ├── test_image_annotator.py # 图像注释器测试
│   ├── debug_feature_matching.py # 特征匹配调试脚本
│   ├── debug_matching_detailed.py # 详细匹配调试脚本
│   ├── feature_cache_performance_test.json # 性能测试结果
│   ├── test_integration_output.csv # 集成测试输出
│   ├── install_dependencies.py # 依赖安装脚本
│   ├── run_mvp_test.py        # MVP测试脚本
│   └── test_unified.py        # 统一测试脚本
│
├── examples/                   # 示例代码目录
│   └── feature_cache_usage.py # 特征缓存使用示例
│
├── docs/                       # 文档目录
│   ├── PROJECT.md              # 项目主要文档
│   ├── TECHNICAL_SPECIFICATION.md # 技术规范
│   ├── USAGE.md               # 使用说明
│   ├── PROJECT_STRUCTURE.md    # 项目结构说明（本文件）
│   ├── CHANGELOG.md            # 变更日志
│   ├── IMPLEMENTATION_PLAN.md  # 实现计划
│   ├── INTEGRATION_IMPLEMENTATION_PLAN.md # 集成实现计划
│   ├── INTEGRATION_TEST_REPORT.md # 集成测试报告
│   ├── MVP_TEST_REPORT.md     # MVP测试报告
│   ├── MVP_USAGE.md           # MVP使用说明
│   ├── MARKER_FUNCTIONALITY.md # 标记功能说明
│   ├── NODE_OUTPUT_IMPLEMENTATION_SUMMARY.md # 节点输出实现摘要
│   ├── OCR_COMPLETE_ARCHITECTURE_SUMMARY.md # OCR完整架构摘要
│   ├── OCR_MVP_DESIGN.md      # OCR MVP设计
│   ├── OCR_CONFIGURATION_EXTENSION.md # OCR配置扩展
│   ├── OCR_OPTIMIZATION_SUMMARY.md # OCR优化摘要
│   ├── OUTPUT_SIMPLIFICATION_SUMMARY.md # 输出简化摘要
│   ├── CLEANUP_REPORT.md      # 清理报告
│   ├── CODE_EXAMPLES.md       # 代码示例
│   ├── CONSOLE_OUTPUT_SIMPLIFICATION.md # 控制台输出简化
│   ├── ANNOTATION_USAGE.md    # 注释使用说明
│   ├── FEATURE_CACHE_IMPLEMENTATION_PLAN.md # 特征缓存实现计划
│   ├── FEATURE_CACHE_ARCHITECTURE_SUMMARY.md # 特征缓存架构摘要
│   ├── ENHANCED_FEATURE_MATCHER_DESIGN.md # 增强特征匹配器设计
│   └── CACHE_BUILD_SCRIPT_EXAMPLE.md # 缓存构建脚本示例
│
├── images/                     # 图像文件目录
│   ├── base_equipment/        # 基准装备图像
│   ├── game_screenshots/      # 游戏截图
│   ├── cropped_equipment/      # 切割后的装备图像
│   ├── cropped_equipment_marker/ # 带标记的切割装备图像
│   └── cache/                 # 特征缓存文件
│
├── output/                     # 输出文件目录
│   ├── final_ocr_output.csv   # 最终OCR输出
│   └── ocr_rename_records.csv # OCR重命名记录
│
└── recognition_logs/           # 识别日志目录
```

## 主要组件说明

### 1. 核心脚本
- **run_recognition_start.py**: 推荐的主启动脚本，提供完整的自动化工作流程
- **start.py**: 备用启动脚本，提供基本的交互式界面

### 2. 源代码 (src/)
- **main.py**: 主程序入口，协调各个组件
- **config_manager.py**: 管理系统配置
- **equipment_recognizer.py**: 装备识别核心逻辑
- **feature_matcher.py**: 基础特征匹配功能
- **feature_cache_manager.py**: 特征缓存管理，提高匹配性能
- **enhanced_feature_matcher.py**: 增强的特征匹配器，集成缓存功能
- **screenshot_cutter.py**: 游戏截图切割功能
- **enhanced_ocr_recognizer.py**: OCR文字识别功能

### 3. 工具 (tools/)
- **build_feature_cache.py**: 构建特征缓存的独立工具

### 4. 测试 (tests/)
- 包含各种测试脚本，用于验证系统功能
- 调试脚本帮助诊断问题
- 性能测试脚本评估系统性能

### 5. 示例 (examples/)
- **feature_cache_usage.py**: 特征缓存系统使用示例

### 6. 文档 (docs/)
- 包含完整的项目文档，从设计到使用说明
- 技术规范和实现细节
- 变更日志和测试报告

### 7. 图像 (images/)
- **base_equipment/**: 基准装备图像，用于匹配
- **game_screenshots/**: 游戏截图，需要处理的原始图像
- **cropped_equipment/**: 切割后的装备图像
- **cache/**: 特征缓存文件，提高匹配速度

### 8. 输出 (output/)
- **final_ocr_output.csv**: 最终的OCR识别结果
- **ocr_rename_records.csv**: 文件重命名记录

### 9. 日志 (recognition_logs/)
- 系统运行日志，用于调试和监控

## 使用流程

1. **准备阶段**:
   - 将游戏截图放入 `images/game_screenshots/`
   - 确保基准装备图像在 `images/base_equipment/`

2. **执行阶段**:
   - 运行 `python run_recognition_start.py` 进行自动化处理
   - 或使用 `python start.py` 进行交互式操作

3. **结果查看**:
   - 查看切割结果在 `images/cropped_equipment/`
   - 查看识别结果在 `output/`
   - 查看运行日志在 `recognition_logs/`

## 配置说明

主要配置文件位于 `config/config.json`，包含：
- 特征匹配参数
- OCR识别参数
- 缓存设置
- 切割参数

可通过修改配置文件调整系统行为，无需修改代码。