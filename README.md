# 游戏装备图像识别系统

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![OpenCV](https://img.shields.io/badge/opencv-4.8.0+-red.svg)](https://opencv.org)

一个基于图像识别技术的游戏装备自动识别系统，采用双重算法架构，支持传统dHash算法和高级模板匹配算法，能够从游戏截图中自动识别出与基准装备图相匹配的装备。

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
   # 使用简化主程序（推荐）
   python run_recognition.py
   
   # 或使用交互式启动脚本
   python start.py
   
   # 或直接运行主程序
   python src/main.py
   ```

## 📁 项目结构

```
shoptitans 图片分隔和匹配/
├── README.md                           # 项目说明（外层仅保留此文档）
├── config.json                         # 系统配置文件
├── requirements.txt                    # 依赖包列表
├── run_recognition.py                  # 简化主程序（日常使用）
├── start.py                            # 交互式启动脚本
├── src/                               # 源代码目录
│   ├── __init__.py                     # 模块初始化
│   ├── config_manager.py               # 配置管理模块
│   ├── equipment_recognizer.py         # 装备识别核心类（包含增强版识别器）
│   ├── main.py                         # 主程序入口
│   └── screenshot_cutter.py            # 图像切割工具
├── src/                                # 核心模块目录
│   ├── advanced_matcher_standalone.py   # 高级装备识别器独立实现
│   ├── feature_matcher.py              # 特征匹配器
│   ├── advanced_matcher_standalone.py  # 高级装备识别器独立实现
│   └── README.md                       # 独立模块说明文档
├── images/                             # 图像资源目录
│   ├── base_equipment/                 # 基准装备图目录
│   ├── game_screenshots/               # 游戏截图目录
│   └── cropped_equipment/              # 切割后装备目录
├── tests/                              # 测试文件目录
│   ├── __init__.py                     # 测试模块初始化
│   ├── test_unified.py                 # 统一测试程序
│   ├── examples/                       # 示例代码
│   │   ├── basic_usage.py              # 基础使用示例
│   │   ├── advanced_usage.py           # 高级使用示例
│   │   └── enhanced_recognizer_usage.py # 增强版识别器示例
│   └── debug/                          # 调试文件
├── recognition_logs/                   # 日志目录
└── docs/                              # 文档目录
    ├── PROJECT.md                      # 详细项目文档
    ├── USAGE.md                        # 使用说明
    ├── TECHNICAL_SPECIFICATION.md      # 技术规格文档
    ├── MVP_USAGE.md                    # MVP使用指南
    ├── CHANGELOG.md                    # 更新日志
    └── [其他文档文件]                   # 其他相关文档
```

## 🎯 核心功能

### 🔍 双重算法识别
- **传统dHash算法**：快速图像相似度计算，适合大批量处理
- **高级模板匹配算法**：基于OpenCV的高精度匹配，支持掩码和直方图验证
- **智能算法选择**：根据精度和速度需求自动选择最佳算法
- **算法切换**：支持运行时动态切换识别算法

### ✂️ 智能切割
- **固定坐标切割**：适用于装备位置固定的界面
- **轮廓检测切割**：适用于装备位置不固定的界面
- **自动模式选择**：根据截图特征自动选择最佳切割方式
- **智能筛选**：基于形状和大小特征进行精确切割
- **圆形标记**：在切割后的装备图片上添加圆形标记，便于识别

### 🎯 图像注释
- **原图标记**：在原始游戏截图上标注匹配的装备位置
- **相似度显示**：可选显示每个匹配项的相似度百分比
- **自定义样式**：支持自定义圆形颜色、大小和字体
- **详细报告**：自动生成包含所有匹配信息的JSON报告
- **批量处理**：支持同时处理多个截图

### 📊 批量处理
- 支持同时处理多个装备图像
- 自动生成详细的匹配报告
- JSON格式的结果导出
- 性能优化和并行处理支持

### ⚙️ 配置管理
- **统一配置系统**：通过config.json管理所有参数
- **动态配置更新**：支持运行时修改配置
- **配置分类管理**：识别、切割、路径、日志、注释等分类配置
- **默认配置**：提供开箱即用的默认设置

## 📖 使用示例

### 基本使用

```python
from src.equipment_recognizer import EnhancedEquipmentRecognizer
from src.screenshot_cutter import ScreenshotCutter

# 初始化增强版识别器（默认使用高级算法）
recognizer = EnhancedEquipmentRecognizer(
    default_threshold=80,
    use_advanced_algorithm=True,
    enable_masking=True,
    enable_histogram=True
)

# 比较两张图像
similarity, is_match = recognizer.compare_images("img1.png", "img2.png")
print(f"相似度: {similarity}%, 匹配: {is_match}")

# 切割截图
cutter = ScreenshotCutter()
cutter.cut_fixed("screenshot.png", "output/", grid=(6, 2))
```

### 使用配置管理器

```python
from src.config_manager import get_config_manager, create_recognizer_from_config

# 获取配置管理器
config_manager = get_config_manager()

# 从配置创建识别器
recognizer = create_recognizer_from_config(config_manager)

# 获取当前算法信息
info = recognizer.get_algorithm_info()
print(f"当前算法: {info['current_algorithm']}")
print(f"掩码匹配: {info.get('masking_enabled', False)}")
print(f"直方图验证: {info.get('histogram_enabled', False)}")
```

### 完整流程

```python
from src.main import EquipmentMatcher
from src.config_manager import get_config_manager

# 初始化配置管理器和匹配器
config_manager = get_config_manager()
matcher = EquipmentMatcher(config_manager)

# 处理截图
matched_items = matcher.process_screenshot(
    screenshot_path="images/game_screenshots/screenshot.png",
    base_img_path="images/base_equipment/target_equipment.webp",
    output_folder="output",
    cutting_method='auto',
    threshold=80
)

print(f"识别到 {len(matched_items)} 个匹配的装备")
```

### 高级算法示例

```python
from src.advanced_matcher_standalone import AdvancedEquipmentRecognizer

# 使用独立的高级识别器
recognizer = AdvancedEquipmentRecognizer(
    enable_masking=True,
    enable_histogram=True
)

# 执行识别
result = recognizer.recognize_equipment("base.png", "target.png")
print(f"装备名称: {result.item_name}")
print(f"置信度: {result.confidence:.2f}%")
print(f"匹配方式: {result.matched_by.name}")
```

### 图像注释示例

```python
from src.image_annotator import ImageAnnotator
from src.config_manager import get_config_manager

# 获取配置
config_manager = get_config_manager()

# 创建注释器
annotator = ImageAnnotator(
    circle_color=config_manager.get_circle_color(),
    circle_width=config_manager.get_circle_width(),
    font_size=config_manager.get_font_size(),
    show_similarity_text=config_manager.get_show_similarity_text()
)

# 定义匹配项
matched_items = [("item_0_0.png", 95.2), ("item_0_3.png", 87.5)]

# 切割参数
cutting_params = {
    'grid': (5, 2),
    'item_width': 210,
    'item_height': 160,
    'margin_left': 10,
    'margin_top': 275,
    'h_spacing': 15,
    'v_spacing': 20
}

# 生成注释图像
annotated_path = annotator.annotate_screenshot_with_matches(
    screenshot_path="images/game_screenshots/screenshot.png",
    matched_items=matched_items,
    cutting_params=cutting_params
)

print(f"注释图像已保存到: {annotated_path}")
```

## ⚙️ 参数配置

### 配置文件系统

项目使用统一的配置文件 `config.json` 管理所有参数：

```json
{
  "recognition": {
    "default_threshold": 80,
    "use_advanced_algorithm": true,
    "enable_masking": true,
    "enable_histogram": true
  },
  "cutting": {
    "default_method": "fixed",
    "fixed_grid": [6, 2],
    "fixed_item_width": 100,
    "fixed_item_height": 120,
    "fixed_margin_left": 20,
    "fixed_margin_top": 350
  },
  "paths": {
    "images_dir": "images",
    "base_equipment_dir": "base_equipment",
    "game_screenshots_dir": "game_screenshots",
    "cropped_equipment_dir": "cropped_equipment"
  }
}
```

### 算法选择配置

- **use_advanced_algorithm**: true（高级模板匹配）/ false（传统dHash）
- **enable_masking**: 启用掩码匹配（仅高级算法有效）
- **enable_histogram**: 启用直方图验证（仅高级算法有效）

### 匹配阈值
- **范围**: 0-100
- **推荐值**: 75-85
- **说明**: 越高越严格，越低越宽松

### 切割参数

#### 固定坐标切割
```python
cutter.cut_fixed(
    screenshot_path="screenshot.png",
    output_folder="output/",
    grid=(6, 2),           # 网格布局（列数，行数）
    item_width=100,        # 装备宽度
    item_height=120,       # 装备高度
    margin_left=20,        # 左边距
    margin_top=350         # 上边距
)
```

#### 轮廓检测切割
```python
cutter.cut_contour(
    screenshot_path="screenshot.png",
    output_folder="output/",
    min_area=800,          # 最小轮廓面积
    max_area=50000         # 最大轮廓面积
)
```

## 📊 性能特点

- **双重算法**: 传统dHash算法（< 10ms）和高级模板匹配算法（< 50ms）
- **高准确率**: 高级算法在理想条件下准确率 > 98%，传统算法 > 95%
- **批量处理**: 支持同时处理数百张图像
- **内存优化**: 低内存占用，适合长时间运行
- **智能缓存**: 支持模板缓存和结果缓存，提升重复识别效率

## 🔧 高级功能

### 算法对比分析
```python
# 对比两种算法的性能
recognizer = EnhancedEquipmentRecognizer()
recognizer.set_algorithm_mode(True)  # 高级算法
similarity1, match1 = recognizer.compare_images("img1.png", "img2.png")

recognizer.set_algorithm_mode(False)  # 传统算法
similarity2, match2 = recognizer.compare_images("img1.png", "img2.png")

print(f"高级算法: {similarity1:.2f}%")
print(f"传统算法: {similarity2:.2f}%")
```

### 批量处理多个截图
```python
# 运行高级示例
python examples/advanced_usage.py
```

### 阈值优化分析
```python
# 多阈值分析，找出最佳匹配阈值
results = matcher.multi_threshold_analysis(
    base_img_path="base.png",
    crop_folder="cropped/",
    thresholds=[60, 70, 80, 90]
)
```

### 性能基准测试
```python
# 测试系统性能
matcher.benchmark_performance(
    base_img_path="base.png",
    test_images_folder="test_images/"
)
```

### 独立模块使用
```python
# 使用独立的高级识别器
from src.advanced_matcher_standalone import AdvancedEquipmentRecognizer

recognizer = AdvancedEquipmentRecognizer(enable_masking=True, enable_histogram=True)
result = recognizer.recognize_equipment("base.png", "target.png")
```

## 🛠️ 故障排除

### 常见问题

**Q: 识别准确率不高？**
A:
1. 尝试切换到高级模板匹配算法
2. 调整匹配阈值
3. 确保基准装备图清晰
4. 启用掩码匹配和直方图验证
5. 尝试不同的切割方式

**Q: 高级算法不可用？**
A:
1. 检查src目录中是否存在advanced_matcher_standalone.py
2. 确保OpenCV正确安装
3. 查看错误日志中的具体信息

**Q: 切割效果不好？**
A:
1. 调整切割参数
2. 检查截图质量
3. 使用自动模式
4. 调整轮廓检测的最小/最大面积

**Q: 处理速度慢？**
A:
1. 切换到传统dHash算法（更快但精度略低）
2. 降低图像分辨率
3. 使用更小的切割区域
4. 启用缓存功能
5. 启用并行处理（在配置中设置）

### 调试模式

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 扩展开发

### 添加新的识别算法
```python
class ExtendedEquipmentRecognizer(EquipmentRecognizer):
    def get_phash(self, image_path):
        """实现pHash算法"""
        pass
    
    def get_ahash(self, image_path):
        """实现aHash算法"""
        pass
```

### 自定义切割策略
```python
class CustomCutter(ScreenshotCutter):
    @staticmethod
    def cut_ml_based(screenshot_path, output_folder):
        """基于机器学习的切割"""
        pass
```

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
- 查看 [详细文档](PROJECT.md)

## 🚀 快速开始

### 1. 环境准备
```bash
# 安装依赖
pip install -r requirements.txt
```

### 2. 准备数据
- 将基准装备图放入 `images/base_equipment/` 目录
- 将游戏截图放入 `images/game_screenshots/` 目录

### 3. 运行程序
```bash
# 使用简化主程序（推荐）
python run_recognition.py

# 或使用交互式启动脚本
python start.py

# 或直接运行主程序
python src/main.py
```

### 4. 查看结果
- 切割后的装备保存在 `images/cropped_equipment/` 目录
- 识别日志保存在 `recognition_logs/` 目录

### 5. 运行测试
```bash
# 运行统一测试程序
python tests/test_unified.py
```

## 📚 更多文档

- [详细使用说明](USAGE.md)
- [技术规格文档](TECHNICAL_SPECIFICATION.md)
- [项目架构文档](PROJECT.md)
- [图像注释功能指南](docs/ANNOTATION_USAGE.md)
- [更新日志](CHANGELOG.md)

---

**注意**: 本项目仅用于学习和研究目的，请遵守相关游戏的使用条款。

*最后更新: 2025年11月*