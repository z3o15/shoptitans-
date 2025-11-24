# 游戏装备识别项目

这是一个用于识别游戏装备的项目，支持多种识别算法和OCR金额识别功能。

## 项目结构

```
项目根目录/
├── src/                          # 核心源代码目录
│   ├── core/                     # 核心业务逻辑
│   │   ├── equipment_recognizer.py      # 装备识别器主模块
│   │   ├── screenshot_cutter.py         # 截图切割工具
│   │   ├── main.py                   # 主程序入口
│   │   ├── advanced_matcher_standalone.py  # 高级匹配器独立版本
│   │   ├── feature_matcher.py         # 特征匹配器
│   │   └── enhanced_feature_matcher.py  # 增强特征匹配器
│   ├── logging/                   # 日志系统
│   │   ├── unified_logger.py        # 统一日志管理器
│   │   ├── step_logger.py          # 步骤日志记录器
│   │   ├── node_logger.py          # 节点日志记录器
│   │   ├── logger_adapter.py      # 日志适配器
│   │   └── report_generator.py     # 报告生成器
│   ├── image_processing/          # 图像处理
│   │   └── image_annotator.py      # 图像注释工具
│   ├── ocr/                      # OCR功能
│   │   ├── enhanced_ocr_recognizer.py  # 增强OCR识别器
│   │   ├── csv_record_manager.py       # CSV记录管理器
│   │   └── file_renamer.py           # 文件重命名工具
│   ├── preprocessing/             # 预处理
│   │   ├── enhanced_preprocess_start.py  # 增强预处理启动
│   │   ├── base_equipment_preprocessor.py  # 基准装备预处理器
│   │   ├── background_remover.py      # 背景移除器
│   │   ├── enhancer.py                # 图像增强器
│   │   ├── resizer.py                # 图像缩放器
│   │   └── preprocess_pipeline.py    # 预处理管道
│   ├── cache/                    # 缓存
│   │   ├── feature_cache_manager.py  # 特征缓存管理器
│   │   ├── build_feature_cache.py   # 特征缓存构建
│   │   ├── feature_cache_usage.py   # 特征缓存使用
│   │   └── auto_cache_updater.py   # 自动缓存更新器
│   ├── debug/                    # 调试
│   │   └── visual_debugger.py      # 可视化调试器
│   ├── quality/                  # 质量检查
│   │   └── equipment_detector.py   # 装备检测器
│   └── utils/                    # 工具函数
│       ├── background_mask.py       # 背景掩码工具
│       └── image_hash.py          # 图像哈希工具
├── config/                       # 统一配置目录
│   ├── unified_config.json       # 统一配置文件
│   ├── unified_config_manager.py # 统一配置管理器
│   └── output_manager.py        # 输出管理器
├── docs/                         # 文档目录
│   ├── technical/               # 技术文档
│   ├── user_guide/              # 用户指南
│   ├── CONFIG_DUPLICATION_ANALYSIS.md    # 配置重复问题分析
│   ├── STEP_TESTS_OUTPUT_OVERLAP_ANALYSIS.md  # 输出重叠问题分析
│   ├── RESTRUCTURE_REPORT.md     # 重构报告
│   └── README.md               # 项目说明文档
├── tests/                        # 测试代码目录（重构后）
│   ├── test_step1_helper.py     # 辅助函数测试
│   ├── test_step2_cut.py        # 截图切割测试
│   ├── test_step3_match.py      # 装备匹配测试
│   └── test_step4_ocr.py       # OCR金额识别测试
├── step_tests/                    # 步骤测试目录（待迁移）
├── output/                       # 标准化输出目录
│   └── [timestamp]/             # 时间戳目录
│       ├── step1_preprocessing/  # 步骤1输出
│       │   ├── images/          # 图像文件
│       │   ├── logs/            # 日志文件
│       │   ├── reports/         # 报告文件
│       │   └── temp/            # 临时文件
│       ├── step2_cutting/       # 步骤2输出
│       ├── step3_matching/      # 步骤3输出
│       └── step4_ocr/          # 步骤4输出
├── images/                       # 图像目录
│   ├── base_equipment/        # 基准装备图像
│   ├── game_screenshots/      # 游戏截图
│   ├── cropped_equipment/      # 切割后的装备
│   ├── cropped_equipment_marker/ # 带标记的装备
│   └── cache/                # 缓存目录
├── requirements.txt              # 依赖包列表
└── .gitignore                  # Git忽略文件
```

## 如何运行项目

### 环境要求

- Python 3.8+
- 依赖包见 `requirements.txt`

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行主程序

```bash
python src/core/main.py
```

### 运行步骤测试

1. 运行辅助函数测试：
```bash
python tests/test_step1_helper.py
```

2. 运行截图切割测试：
```bash
python tests/test_step2_cut.py
```

3. 运行装备匹配测试：
```bash
python tests/test_step3_match.py
```

4. 运行OCR金额识别测试：
```bash
python tests/test_step4_ocr.py
```

### 使用新的配置管理系统

```python
# 使用统一配置管理器
from config.unified_config_manager import get_unified_config_manager

# 获取配置管理器实例
config_manager = get_unified_config_manager()

# 获取配置
recognition_config = config_manager.get_recognition_config()
ocr_config = config_manager.get_ocr_config()

# 更新配置
config_manager.set_default_threshold(85)
config_manager.set_ocr_enabled(True)

# 使用输出管理器
from config.output_manager import get_output_manager

# 获取输出管理器实例
output_manager = get_output_manager()

# 创建标准输出目录
dirs = output_manager.ensure_step_dirs("step1")
print(f"图像目录: {dirs['images']}")
print(f"日志目录: {dirs['logs']}")

# 保存文件
log_path = output_manager.save_log("step1", "测试日志内容")
report_path = output_manager.save_report("step1", "# 测试报告")
```

## 重构后的项目特点

1. **统一配置管理**：使用单一配置文件和统一配置管理器，消除配置重复
2. **标准化输出结构**：清晰的目录结构，支持时间戳目录和文件分类存储
3. **模块化设计**：将代码按功能划分为多个模块，便于维护和扩展
4. **分离的关注点**：核心功能、工具/辅助模块、配置/文档分层明确
5. **优化的导入路径**：使用绝对导入，避免模块间的循环依赖
6. **统一的日志系统**：提供统一的日志接口，支持多种输出格式
7. **完整的测试结构**：分离测试代码和输出文件，便于管理和维护
8. **自动化文件管理**：输出管理器自动创建目录结构，简化文件操作

## 核心功能

1. **装备识别**：支持多种算法（dHash、特征匹配、高级模板匹配）
2. **截图切割**：自动识别并切割游戏截图中的装备
3. **OCR金额识别**：识别装备图片中的金额信息
4. **特征缓存**：预计算和缓存基准装备特征，提升性能
5. **批量处理**：支持批量处理多个图像

## 配置说明

### 新的配置系统

主要配置文件：
- `config/unified_config.json`：统一配置文件，包含所有系统配置
- `config/unified_config_manager.py`：统一配置管理器
- `config/output_manager.py`：输出管理器

### 配置节说明

- **recognition**：识别算法配置
- **preprocessing**：图像预处理配置
- **ocr**：OCR识别配置
- **cutting**：图像切割配置
- **paths**：路径配置
- **output_structure**：输出结构配置
- **logging**：日志配置
- **performance**：性能配置
- **ui**：界面配置
- **annotation**：注释配置

### 旧配置文件（待废弃）

- `config.json`：根配置文件（将被unified_config.json替代）
- `config/config.json`：重复的配置文件
- `config/optimized_ocr_config.json`：OCR配置（已整合到unified_config.json）

## 技术架构

- 采用模块化设计，各功能模块职责清晰
- 支持多种识别算法，可根据需要选择
- 提供统一的日志系统，便于调试和问题追踪
- 支持特征缓存，提升识别性能

## 注意事项

1. 确保图像路径正确
2. 根据需要调整配置文件中的参数
3. 查看各步骤的日志文件以获取详细信息
4. 使用适当的算法以获得最佳识别效果