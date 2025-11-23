# 游戏装备图像识别系统

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![OpenCV](https://img.shields.io/badge/opencv-4.8.0+-red.svg)](https://opencv.org)

一个基于图像识别技术的游戏装备自动识别系统，采用多重算法架构，支持特征匹配算法、高级模板匹配算法和传统dHash算法，能够从游戏截图中自动识别出与基准装备图相匹配的装备，并识别装备金额。

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- pip 包管理器

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd "shoptitans 图片分隔和匹配"
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **准备数据**
   - 将基准装备图放入 `images/base_equipment/` 目录
   - 将游戏截图放入 `images/game_screenshots/` 目录

4. **运行程序**
   ```bash
   # 使用增强版启动脚本（推荐）
   python enhanced_recognition_start.py
   
   # 或使用基础启动脚本
   python run_recognition_start.py
   ```

## 📁 项目结构

```
shoptitans 图片分隔和匹配/
├── README.md                           # 项目说明
├── config.json                         # 系统配置文件
├── requirements.txt                    # 依赖包列表
├── enhanced_recognition_start.py       # 增强版启动脚本（推荐）
├── run_recognition_start.py            # 基础启动脚本
├── .gitignore                          # Git忽略文件
├── src/                               # 源代码目录
│   ├── __init__.py                     # 模块初始化
│   ├── config_manager.py               # 配置管理模块
│   ├── equipment_recognizer.py         # 装备识别核心类
│   ├── enhanced_ocr_recognizer.py      # OCR识别模块
│   ├── feature_matcher.py              # 特征匹配器
│   ├── screenshot_cutter.py            # 图像切割工具
│   └── [其他模块...]                   # 其他功能模块
├── images/                             # 图像资源目录
│   ├── base_equipment/                 # 基准装备图目录
│   ├── game_screenshots/               # 游戏截图目录
│   ├── cropped_equipment/              # 切割后装备目录
│   └── cropped_equipment_marker/       # 带标记的装备目录
├── tests/                              # 测试文件目录
├── docs/                              # 文档目录
├── recognition_logs/                   # 日志目录
└── output/                             # 输出目录
```

## 🎯 核心功能

### 🔍 多重算法识别
- **特征匹配算法**（默认）：基于ORB特征点匹配，准确率>98%
- **高级彩色模板匹配算法**：保留RGB颜色信息，支持掩码和直方图验证
- **传统dHash算法**：快速图像相似度计算，适合大批量处理
- **增强特征匹配算法**：支持特征缓存的高性能匹配，显著提升识别速度

### ✂️ 智能切割
- **固定坐标切割**：适用于装备位置固定的界面，支持自定义网格布局
- **圆形标记功能**：在切割后的装备图片上添加圆形标记，便于OCR识别
- **自动目录管理**：按时间戳自动创建子目录，避免文件覆盖

### 📊 OCR金额识别
- **EasyOCR引擎**：高精度文字识别
- **智能区域识别**：自动定位装备金额区域
- **结果整合**：将装备名称和金额整合到统一CSV文件

### ⚙️ 配置管理
- **统一配置系统**：通过config.json管理所有参数
- **动态配置更新**：支持运行时修改配置
- **算法参数配置**：支持各种算法的详细参数调整

## 📖 使用流程

系统按照四步工作流程进行：

### 步骤1：获取原始图片
- 检查和选择游戏截图
- 支持多种图片格式（PNG、JPG、WEBP）

### 步骤2：分割原始图片
- 将游戏截图按固定网格切割成单个装备图片
- 添加圆形标记用于OCR识别
- 按时间戳组织结果文件

### 步骤3：装备识别匹配
- 使用基准装备库对比切割后的图片
- 支持多种匹配算法
- 为匹配的装备添加装备名称后缀

### 步骤4：整合装备名称和金额识别结果
- 使用OCR识别圆形标记中的金额
- 整合装备名称和金额到CSV文件
- 重命名文件包含装备名称和金额信息

## ⚙️ 参数配置

### 识别算法配置
```json
{
  "recognition": {
    "default_threshold": 80,           // 默认匹配阈值
    "algorithm_type": "feature",        // 算法类型
    "feature_type": "ORB",             // 特征类型
    "min_match_count": 8,               // 最少特征匹配数量
    "match_ratio_threshold": 0.75        // 特征匹配比例阈值
  }
}
```

### 切割参数配置
```json
{
  "cutting": {
    "fixed_grid": [5, 2],              // 网格布局（列数，行数）
    "fixed_item_width": 210,            // 装备宽度
    "fixed_item_height": 160,            // 装备高度
    "fixed_margin_left": 10,             // 左边距
    "fixed_margin_top": 275,             // 上边距
    "fixed_h_spacing": 15,              // 横向间隔
    "fixed_v_spacing": 20                // 纵向间隔
  }
}
```

### OCR配置
```json
{
  "ocr": {
    "enabled": true,                     // 启用OCR
    "engine": "easyocr",                 // OCR引擎
    "language": ["en"],                  // 识别语言
    "price_pattern": "\\d+",             // 金额模式
    "confidence_threshold": 0.8          // 置信度阈值
  }
}
```

## 📊 性能特点

- **多重算法**：特征匹配算法（< 30ms）、高级模板匹配算法（< 50ms）和传统dHash算法（< 10ms）
- **高准确率**：特征匹配算法在理想条件下准确率 > 98%，高级算法 > 95%，传统算法 > 90%
- **特征缓存优化**：预计算基准装备特征，识别速度提升70-80%
- **批量处理**：支持同时处理数百张图像，自动按时间戳组织结果

## 🔧 高级功能

### 算法对比分析
```python
from src.equipment_recognizer import EnhancedEquipmentRecognizer

# 创建识别器并比较不同算法
recognizer = EnhancedEquipmentRecognizer()

# 特征匹配算法
recognizer.set_algorithm_type("feature")
similarity1, match1 = recognizer.compare_images("img1.png", "img2.png")

# 高级模板匹配算法
recognizer.set_algorithm_type("advanced")
similarity2, match2 = recognizer.compare_images("img1.png", "img2.png")

# 传统dHash算法
recognizer.set_algorithm_type("traditional")
similarity3, match3 = recognizer.compare_images("img1.png", "img2.png")
```

### 自定义配置
```python
from src.config_manager import get_config_manager

# 获取配置管理器
config_manager = get_config_manager()

# 修改配置
config_manager.set_default_threshold(85)
config_manager.set_algorithm_type("feature")
```

## 🛠️ 故障排除

### 常见问题

**Q: 识别准确率不高？**
A:
1. 尝试切换到特征匹配算法（默认最准确）
2. 调整匹配阈值
3. 确保基准装备图清晰
4. 检查切割参数是否正确

**Q: OCR识别不准确？**
A:
1. 调整OCR置信度阈值
2. 检查圆形标记是否清晰
3. 确保金额区域设置正确
4. 尝试不同的OCR引擎参数

**Q: 切割效果不好？**
A:
1. 调整切割参数（grid、item_width、item_height等）
2. 检查截图质量
3. 调整margin_left和margin_top参数
4. 确保h_spacing和v_spacing适合实际装备间隔

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 📞 支持

如有问题或建议：
- 提交 [GitHub Issue](../../issues)
- 查看 [详细文档](docs/PROJECT.md)

---

**注意**: 本项目仅用于学习和研究目的，请遵守相关游戏的使用条款。

*最后更新: 2025年11月*