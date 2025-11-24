# 项目结构说明

## 目录结构

```
d:/shoptitans 图片分隔和匹配/
├── config.json                    # 主配置文件（已优化）
├── OCR_OPTIMIZATION_SUMMARY.md    # OCR优化过程总结
├── README.md                     # 项目说明文档
├── requirements.txt              # Python依赖包列表
├── run_recognition_start.py       # 识别启动脚本
├── start.py                     # 主启动脚本
├── test_ocr_integration.py       # OCR集成测试脚本
├── ocr_rename_records.csv        # OCR重命名记录
│
├── backup_files/                # 备份文件目录
│   ├── cleanup_project.py        # 项目清理脚本
│   ├── final_optimized_config.json # 最终优化配置
│   ├── invalid_config.json       # 无效配置示例
│   └── optimized_ocr_config.json # 优化配置
│
├── test_results/                # 测试结果目录
│   ├── analyze_failed_ocr.py    # OCR失败分析工具
│   ├── debug_ocr.py            # OCR调试工具
│   ├── final_ocr_output.csv     # 最终测试输出
│   ├── optimized_ocr_output.csv # 优化测试输出
│   ├── test_ocr_output.csv     # 基础测试输出
│   └── test_specific_images.py # 特定图像测试工具
│
├── docs/                       # 文档目录
│   ├── ANNOTATION_USAGE.md     # 注释功能使用说明
│   ├── CHANGELOG.md            # 变更日志
│   ├── CLEANUP_REPORT.md       # 清理报告
│   ├── INTEGRATION_TEST_REPORT.md # 集成测试报告
│   ├── MARKER_FUNCTIONALITY.md # 标记功能说明
│   ├── MVP_TEST_REPORT.md      # MVP测试报告
│   ├── MVP_USAGE.md           # MVP使用说明
│   ├── OCR_AMOUNT_RECOGNITION_ARCHITECTURE.md # OCR金额识别架构
│   ├── OCR_CLASS_DIAGRAM.md    # OCR类图
│   ├── OCR_COMPLETE_ARCHITECTURE_SUMMARY.md # OCR完整架构总结
│   ├── OCR_CONFIGURATION_EXTENSION.md # OCR配置扩展
│   ├── OCR_MVP_DESIGN.md      # OCR MVP设计
│   ├── PROJECT.md             # 项目说明
│   ├── TECHNICAL_SPECIFICATION.md # 技术规范
│   └── USAGE.md              # 使用说明
│
├── images/                     # 图像目录
│   ├── base_equipment/        # 基础装备图像
│   ├── cropped_equipment/     # 裁剪后的装备图像
│   ├── cropped_equipment_marker/ # 带标记的裁剪装备图像
│   │   └── 20251122_183651/ # 特定日期的图像
│   └── game_screenshots/     # 游戏截图
│
├── recognition_logs/           # 识别日志目录
│
├── src/                      # 源代码目录
│   ├── __init__.py
│   ├── advanced_matcher_standalone.py # 高级匹配器独立版
│   ├── config_manager.py      # 配置管理器
│   ├── csv_record_manager.py # CSV记录管理器
│   ├── enhanced_ocr_recognizer.py # 增强版OCR识别器
│   ├── equipment_recognizer.py # 装备识别器
│   ├── feature_matcher.py     # 特征匹配器
│   ├── file_renamer.py      # 文件重命名器
│   ├── image_annotator.py   # 图像注释器
│   ├── main.py             # 主程序
│   ├── ocr_amount_recognizer.py # OCR金额识别器
│   ├── ocr_config_manager.py # OCR配置管理器
│   ├── screenshot_cutter.py # 截图裁剪器
│   └── standalone_modules_README.md # 独立模块说明
│
├── temp_files/               # 临时文件目录
│
└── tests/                   # 测试目录
    ├── __init__.py
    ├── CHANGELOG.md
    ├── config.json
    ├── install_dependencies.py
    ├── run_mvp_test.py
    ├── test_image_annotator.py
    ├── test_system.py
    ├── test_unified.py
    └── examples/
        ├── advanced_usage.py
        ├── basic_usage.py
        └── enhanced_recognizer_usage.py
```

## 核心文件说明

### 主要配置文件
- **config.json**: 项目主配置文件，包含OCR、图像处理、文件路径等配置

### 核心模块
- **src/ocr_amount_recognizer.py**: OCR金额识别器核心模块
- **src/enhanced_ocr_recognizer.py**: 增强版OCR识别器，支持多配置回退
- **src/ocr_config_manager.py**: OCR配置管理器
- **src/file_renamer.py**: 文件重命名器
- **src/csv_record_manager.py**: CSV记录管理器

### 测试和调试工具
- **test_ocr_integration.py**: OCR集成功能测试
- **test_results/**: 包含各种测试和调试工具
  - debug_ocr.py: OCR调试工具
  - analyze_failed_ocr.py: 失败分析工具
  - test_specific_images.py: 特定图像测试

### 文档
- **OCR_OPTIMIZATION_SUMMARY.md**: 详细的OCR优化过程和结果总结
- **docs/**: 完整的项目文档集合

## 使用方法

### 基础OCR识别
```bash
python -m src.ocr_amount_recognizer --config config.json
```

### 增强版OCR识别（推荐）
```bash
python -m src.enhanced_ocr_recognizer --config config.json
```

### 集成测试
```bash
python test_ocr_integration.py
```

## 项目优化成果

1. **金额提取准确率**: 从33%提升到100%
2. **整体识别成功率**: 从20%提升到90%
3. **支持带逗号金额**: 如"315,000"、"180,000"等
4. **多配置回退机制**: 自动尝试不同预处理配置
5. **详细的日志记录**: 便于调试和问题分析

## 注意事项

1. 主要配置文件是 `config.json`，已包含所有优化设置
2. 增强版OCR识别器位于 `src/enhanced_ocr_recognizer.py`
3. 所有测试和调试工具已移至 `test_results/` 目录
4. 备份文件保存在 `backup_files/` 目录中
5. 详细的优化过程记录在 `OCR_OPTIMIZATION_SUMMARY.md` 中