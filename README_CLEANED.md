# OCR金额识别器项目

## 项目概述

这是一个基于EasyOCR的金额识别系统，能够自动识别图像中的金额信息并重命名文件。

## 主要特性

- ✅ **高准确率金额识别**：支持带逗号的金额格式（如"315,000"）
- ✅ **多配置回退机制**：自动尝试不同预处理配置
- ✅ **文件自动重命名**：根据识别的金额重命名文件
- ✅ **CSV记录保存**：详细记录识别结果和处理信息
- ✅ **增强版识别器**：提供更高的识别成功率

## 核心文件

### 配置文件
- `config.json` - 主配置文件（已优化）

### 核心模块
- `src/ocr_amount_recognizer.py` - 基础OCR金额识别器
- `src/enhanced_ocr_recognizer.py` - 增强版OCR识别器（推荐）
- `src/ocr_config_manager.py` - OCR配置管理器
- `src/file_renamer.py` - 文件重命名器
- `src/csv_record_manager.py` - CSV记录管理器

## 使用方法

### 推荐方式（使用增强版识别器）
```bash
python -m src.enhanced_ocr_recognizer --config config.json
```

### 基础方式
```bash
python -m src.ocr_amount_recognizer --config config.json
```

### 直接运行方式（不推荐，仅用于调试）
```bash
python src/enhanced_ocr_recognizer.py
```

### 集成测试
```bash
python test_ocr_integration.py
```

## 优化成果

- **金额提取准确率**：从33%提升到100%
- **整体识别成功率**：从20%提升到90%
- **支持复杂金额格式**：如"315,000"、"180,000"等
- **智能预处理**：自动选择最佳预处理配置

## 项目结构

```
d:/shoptitans 图片分隔和匹配/
├── config.json                    # 主配置文件
├── README.md                     # 项目说明
├── README_CLEANED.md             # 简洁版说明（本文件）
├── requirements.txt              # Python依赖
├── test_ocr_integration.py       # 集成测试
├── ocr_rename_records.csv        # 识别记录
├── run_recognition_start.py       # 启动脚本
├── start.py                     # 主启动脚本
├── docs/                        # 详细文档
├── images/                      # 图像文件
├── recognition_logs/            # 识别日志
├── src/                        # 源代码
└── tests/                      # 测试文件
```

## 配置说明

主要配置项（在config.json中）：
- `ocr.enabled`: 启用/禁用OCR功能
- `ocr.price_pattern`: 金额匹配正则表达式（已优化为`\d{1,3}(?:,\d{3})*`）
- `ocr.confidence_threshold`: 置信度阈值（已优化为0.7）
- `ocr.input_folder`: 输入图像文件夹
- `ocr.output_csv`: 输出CSV文件路径

## 注意事项

1. 确保已安装所需依赖：`pip install -r requirements.txt`
2. 图像文件应放置在配置指定的输入文件夹中
3. 建议使用增强版识别器以获得最佳效果
4. 识别结果会自动保存到CSV文件中

## 技术支持

如需了解更多技术细节，请参考`docs/`目录中的详细文档。