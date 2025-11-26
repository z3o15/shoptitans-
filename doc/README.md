# 图片分隔和匹配 - 测试模块使用说明

## 📋 项目概述

本项目专注于装备图片的分割、匹配和OCR识别功能，提供4个核心测试模块。已完成代码清理，移除所有历史模块和无用依赖。

## 🗂️ 目录结构

```
shoptitans 图片分隔和匹配/
├── step_tests/                          # 测试模块目录（当前使用）
│   ├── 1_helper.py                     # 辅助功能测试模块
│   ├── 2_cut.py                        # 图片裁剪模块
│   ├── 3_match.py                      # 装备图片匹配模块
│   ├── 5_ocr.py                        # OCR金额识别模块
│   ├── README.md                       # 本说明文档
│   └── summary_report.md               # 处理流程汇总报告
├── src/                                # 源代码模块（依赖）
├── images/                             # 图片资源目录
├── config.json                         # 配置文件
└── requirements.txt                    # 依赖包列表
```

## 🚀 核心模块说明

### 1️⃣ 1_helper.py - 辅助功能测试模块

**功能**: 提供基础的环境检查、依赖验证和数据文件确认功能

**主要功能**:
- 检查核心依赖包（cv2, PIL, numpy）
- 验证数据文件目录结构
- 清理之前的日志和结果文件
- 测试基础工具功能

**使用方法**:
```bash
cd step_tests
python 1_helper.py
```

### 2️⃣ 2_cut.py - 图片裁剪模块

**功能**: 从游戏截图中裁剪出装备图标，支持矩形和圆形透明图输出

**主要特性**:
- 支持固定网格切割
- 生成矩形装备图到 `images/equipment_crop/`
- 生成圆形透明图到 `images/equipment_transparent/`
- 自动重命名和文件管理

**使用方法**:
```bash
cd step_tests
python 2_cut.py
# 或测试模式
python 2_cut.py --test
```

### 3️⃣ 3_match.py - 装备图片匹配模块

**功能**: 使用LAB色彩空间进行两阶段装备匹配，输出CSV结果和对比图

**主要特性**:
- LAB色彩空间模板匹配
- 像素级颜色相似度计算
- 高置信度文件自动重命名
- CSV表格导出匹配结果

**使用方法**:
```bash
cd step_tests
python 3_match.py
# 或指定参数
python 3_match.py --base-dir images/base_equipment --compare-dir images/equipment_transparent
```

### 4️⃣ 5_ocr.py - OCR金额识别模块

**功能**: 对装备图片进行OCR文字识别，提取金额信息

**主要特性**:
- 增强型OCR识别器
- CSV记录管理
- 处理报告生成
- 自动格式化金额文本

**使用方法**:
```bash
cd step_tests
python 5_ocr.py
```

## 📁 目录说明

### 输入目录
- `images/game_screenshots/` - 游戏截图文件
- `images/base_equipment/` - 基准装备图片

### 输出目录
- `images/equipment_crop/` - 裁剪的矩形装备图
- `images/equipment_transparent/` - 圆形透明装备图
- `output/ocr/` - OCR识别结果和CSV文件
- `recognition_logs/` - 日志文件

## 🔄 推荐使用流程

1. **环境准备**: 运行 `python 1_helper.py` 检查环境和依赖
2. **图片裁剪**: 运行 `python 2_cut.py` 裁剪游戏截图
3. **装备匹配**: 运行 `python 3_match.py` 匹配装备图片
4. **OCR识别**: 运行 `python 5_ocr.py` 识别金额文字

## ⚙️ 配置文件

项目使用 `config.json` 统一配置，主要配置项：
- 切割参数（网格布局、尺寸、边距）
- 匹配参数（阈值、算法选择）
- OCR参数（识别引擎、格式化规则）
- 路径配置（输入输出目录）

## 🔧 故障排除

### 常见问题

**Q: 依赖包缺失**
```bash
pip install -r requirements.txt
```

**Q: 找不到图片文件**
- 检查 `images/` 目录下的文件是否存在
- 确认文件格式支持（.png, .jpg, .jpeg, .webp）

**Q: 匹配结果不准确**
- 调整 `config.json` 中的匹配阈值
- 检查基准图片质量
- 尝试不同的算法参数

**Q: OCR识别失败**
- 确保图片文字清晰
- 调整OCR配置参数
- 检查输入图片路径

## 📊 输出结果

各模块会生成相应的输出文件：
- **裁剪模块**: 生成装备图片文件
- **匹配模块**: 生成CSV匹配结果和对比图
- **OCR模块**: 生成金额识别记录和报告

## 📝 开发说明

本项目采用模块化设计，每个测试模块都是独立可运行的。如果需要修改功能，请：
1. 修改对应的测试模块
2. 更新相关的依赖模块（src/目录下）
3. 调整 `config.json` 配置

---

*最后更新: 2025-11-26*