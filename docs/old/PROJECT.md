# 游戏装备图像识别系统

## 项目概述

这是一个基于图像识别技术的游戏装备自动识别系统，采用双重算法架构，能够从游戏截图中自动识别出与基准装备图相匹配的装备。系统支持传统dHash算法和高级模板匹配算法，提供灵活的算法选择和配置管理，支持固定坐标切割和轮廓检测两种图像分割方式，无需人工干预，高效且准确。

## 功能特性

### 核心识别功能
- **双重算法架构**：支持传统dHash算法和高级模板匹配算法
- **智能算法选择**：根据精度和速度需求自动选择最佳算法
- **动态算法切换**：支持运行时切换识别算法
- **高精度匹配**：高级算法支持掩码匹配和直方图验证
- **算法对比分析**：提供两种算法的性能对比和结果分析

### 图像处理功能
- **智能图像切割**：支持固定坐标和轮廓检测两种切割方式
- **自动模式选择**：根据截图特征自动选择最佳切割方式
- **智能筛选**：基于形状和大小特征进行精确切割
- **图像预处理**：标准化尺寸、格式转换和背景处理

### 系统管理功能
- **统一配置管理**：通过config.json管理所有系统参数
- **动态配置更新**：支持运行时修改配置
- **批量处理能力**：可同时处理多个装备图像
- **结果导出**：支持JSON格式的结果导出
- **详细日志输出**：提供完整的处理过程信息
- **性能优化**：支持缓存和并行处理

### 扩展功能
- **独立模块**：提供独立的高级识别器模块
- **插件架构**：支持特殊装备处理的插件系统
- **兼容性层**：确保向后兼容和渐进式迁移

## 技术架构

### 核心技术栈

- **Python 3.8+**：主要编程语言
- **OpenCV**：计算机视觉库，用于图像处理、模板匹配和轮廓检测
- **Pillow (PIL)**：图像处理库，用于图像格式转换和尺寸调整
- **NumPy**：数值计算库，用于数组操作
- **JSON**：配置文件和数据交换格式

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    游戏装备识别系统                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   配置管理模块    │  │   图像切割模块    │  │   识别算法模块    │ │
│  │                │  │                │  │                │ │
│  │ • 统一配置管理   │  │ • 固定坐标切割   │  │ • 传统dHash算法  │ │
│  │ • 动态配置更新   │  │ • 轮廓检测切割   │  │ • 高级模板匹配   │ │
│  │ • 配置分类管理   │  │ • 自动模式选择   │  │ • 算法动态切换   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   独立模块系统    │  │   主程序集成      │  │   日志和输出系统  │ │
│  │                │  │                │  │                │ │
│  │ • 高级识别器     │  │ • 批量处理流程   │  │ • 详细日志记录   │ │
│  │ • 插件架构      │  │ • 结果导出      │  │ • 性能监控      │ │
│  │ • 兼容性层      │  │ • 错误处理      │  │ • JSON格式输出  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 算法原理

#### 传统dHash算法
dHash（difference hash）是一种快速图像哈希算法，通过比较相邻像素的亮度差异来生成图像的指纹表示：

1. 将图像缩放到8x8像素
2. 转换为灰度图
3. 比较每行相邻像素的亮度
4. 生成64位二进制哈希值
5. 通过汉明距离计算相似度

#### 高级模板匹配算法
基于OpenCV的高精度图像匹配算法，结合多种验证机制：

1. **模板匹配**：使用TM_SQDIFF_NORMED算法进行精确匹配
2. **掩码匹配**：通过轮廓掩码排除背景干扰
3. **直方图验证**：使用巴氏距离比较颜色分布
4. **综合评分**：结合多个指标计算最终置信度

#### 图像切割方法

1. **固定坐标切割**：适用于装备位置固定的界面
2. **轮廓检测切割**：适用于装备位置不固定但有明显边界的界面
3. **智能筛选**：基于形状和大小特征进行精确切割

## 项目结构

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
│   ├── equipment_recognizer.py         # 装备识别核心类
│   ├── main.py                         # 主程序入口
│   └── screenshot_cutter.py            # 图像切割工具类
├── standalone_modules/                  # 独立模块目录
│   ├── __init__.py                     # 模块初始化
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

## 安装与使用

### 环境要求

- Python 3.8 或更高版本
- pip 包管理器

### 安装步骤

1. 克隆或下载项目代码
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```

### 基本使用

#### 1. 准备数据

将基准装备图和游戏截图放入相应目录：
- `images/base_equipment/` - 要识别的目标装备
- `images/game_screenshots/` - 包含多个装备的游戏截图

#### 2. 运行主程序

```bash
# 使用简化主程序（推荐）
python run_recognition.py

# 或使用交互式启动脚本
python start.py

# 或直接运行主程序
python src/main.py
```

#### 3. 查看结果

程序将在相应目录下生成：
- `images/cropped_equipment/` - 切割后的单个装备图像
- `recognition_logs/` - 识别日志和结果详情

### 高级使用

#### 使用配置管理器

```python
from src.config_manager import get_config_manager, create_recognizer_from_config

# 获取配置管理器
config_manager = get_config_manager()

# 修改配置
config_manager.set_algorithm_mode(True)  # 使用高级算法
config_manager.set_default_threshold(85)  # 设置阈值

# 从配置创建识别器
recognizer = create_recognizer_from_config(config_manager)
```

#### 双算法使用

```python
from src.equipment_recognizer import EnhancedEquipmentRecognizer

# 创建增强版识别器
recognizer = EnhancedEquipmentRecognizer(
    default_threshold=80,
    use_advanced_algorithm=True,
    enable_masking=True,
    enable_histogram=True
)

# 算法对比
recognizer.set_algorithm_mode(True)  # 高级算法
similarity1, match1 = recognizer.compare_images("img1.png", "img2.png")

recognizer.set_algorithm_mode(False)  # 传统算法
similarity2, match2 = recognizer.compare_images("img1.png", "img2.png")

print(f"高级算法: {similarity1:.2f}%")
print(f"传统算法: {similarity2:.2f}%")
```

#### 使用独立模块

```python
from standalone_modules import AdvancedEquipmentRecognizer

# 创建独立的高级识别器
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

#### 自定义参数

可以通过修改 `config.json` 中的参数来调整识别行为：

```json
{
  "recognition": {
    "default_threshold": 85,
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
  }
}
```

#### 单独使用组件

```python
from src.equipment_recognizer import EnhancedEquipmentRecognizer
from src.screenshot_cutter import ScreenshotCutter

# 单独使用识别器
recognizer = EnhancedEquipmentRecognizer()
similarity, is_match = recognizer.compare_images("img1.png", "img2.png")

# 单独使用切割器
cutter = ScreenshotCutter()
cutter.cut_fixed("screenshot.png", "output/", grid=(3, 4))
cutter.cut_contour("screenshot.png", "output/", min_area=500)
```

## 参数说明

### 配置文件参数

#### recognition 配置
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| default_threshold | int | 80 | 默认匹配阈值（0-100） |
| use_advanced_algorithm | bool | true | 是否使用高级算法 |
| enable_masking | bool | true | 是否启用掩码匹配（仅高级算法） |
| enable_histogram | bool | true | 是否启用直方图验证（仅高级算法） |

#### cutting 配置
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| default_method | str | "fixed" | 默认切割方法 |
| fixed_grid | array | [6, 2] | 固定切割网格布局 |
| fixed_item_width | int | 100 | 单个装备宽度 |
| fixed_item_height | int | 120 | 单个装备高度 |
| fixed_margin_left | int | 20 | 左边距 |
| fixed_margin_top | int | 350 | 上边距 |
| contour_min_area | int | 800 | 最小轮廓面积 |
| contour_max_area | int | 50000 | 最大轮廓面积 |

#### paths 配置
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| images_dir | str | "images" | 图像根目录 |
| base_equipment_dir | str | "base_equipment" | 基准装备目录 |
| game_screenshots_dir | str | "game_screenshots" | 游戏截图目录 |
| cropped_equipment_dir | str | "cropped_equipment" | 切割装备目录 |
| logs_dir | str | "recognition_logs" | 日志目录 |

### EnhancedEquipmentRecognizer 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| default_threshold | int | 80 | 默认匹配阈值（0-100） |
| use_advanced_algorithm | bool | true | 是否使用高级算法 |
| enable_masking | bool | true | 是否启用掩码匹配 |
| enable_histogram | bool | true | 是否启用直方图验证 |

### AdvancedEquipmentRecognizer 参数（独立模块）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| enable_masking | bool | true | 是否启用掩码匹配 |
| enable_histogram | bool | true | 是否启用直方图验证 |

## 性能优化建议

1. **算法选择**：
   - 速度优先：使用传统dHash算法（< 10ms/图像）
   - 精度优先：使用高级模板匹配算法（< 50ms/图像）
   - 批量处理：传统算法更适合大批量处理

2. **图像尺寸优化**：
   - 确保截图分辨率适中，过大的图像会降低处理速度
   - 高级算法会自动调整图像尺寸到标准大小（113x113）

3. **参数调整**：
   - 根据实际识别效果调整匹配阈值
   - 高精度场景可启用掩码匹配和直方图验证
   - 速度优先场景可禁用这些验证步骤

4. **系统优化**：
   - 对于大量截图，建议使用批量处理功能
   - 启用缓存功能可提升重复识别效率
   - 如有GPU，可安装OpenCV的GPU版本提升性能

5. **内存管理**：
   - 处理大量图像时注意内存使用
   - 可使用并行处理功能提升吞吐量
   - 及时清理不需要的图像数据

## 常见问题

### Q: 识别准确率不高怎么办？

A: 可以尝试以下方法：
1. 切换到高级模板匹配算法
2. 启用掩码匹配和直方图验证
3. 调整匹配阈值（降低阈值提高召回率，提高阈值提高精确率）
4. 确保基准装备图清晰且与截图中的装备角度一致
5. 尝试不同的切割方式和参数

### Q: 高级算法不可用或出错？

A: 可以尝试：
1. 检查standalone_modules目录是否存在
2. 确保OpenCV正确安装
3. 查看错误日志中的具体信息
4. 尝试切换回传统dHash算法

### Q: 轮廓检测切割效果不好？

A: 可以尝试：
1. 调整 `min_area` 和 `max_area` 参数
2. 检查截图中的装备是否有明显的边界
3. 使用固定坐标切割方式
4. 尝试自动模式选择最佳切割方式

### Q: 如何处理不同分辨率的截图？

A:
1. 固定坐标切割需要根据分辨率调整参数
2. 轮廓检测切割对分辨率变化更鲁棒
3. 建议使用自动模式让程序选择最佳切割方式
4. 高级算法会自动标准化图像尺寸

### Q: 配置文件如何修改？

A:
1. 直接编辑config.json文件
2. 使用ConfigManager类的API动态修改
3. 修改后重启程序或重新加载配置

### Q: 两种算法如何选择？

A:
- **传统dHash算法**：速度快，适合大批量处理，精度略低
- **高级模板匹配**：精度高，支持掩码和直方图验证，速度较慢
- **建议**：开发测试使用高级算法，生产环境根据需求选择

## 扩展开发

### 添加新的识别算法

可以在 `EnhancedEquipmentRecognizer` 类中添加新的识别算法：

```python
def set_custom_algorithm(self, algorithm_func):
    """设置自定义算法"""
    self.custom_algorithm = algorithm_func
    self.use_custom_algorithm = True

def compare_images_custom(self, image_path1, image_path2, threshold=None):
    """使用自定义算法比较图像"""
    if self.use_custom_algorithm and self.custom_algorithm:
        return self.custom_algorithm(image_path1, image_path2, threshold)
    return self.compare_images(image_path1, image_path2, threshold)
```

### 添加新的切割算法

可以在 `ScreenshotCutter` 类中添加新的切割方法：

```python
@staticmethod
def cut_custom(screenshot_path, output_folder, **params):
    """自定义切割算法"""
    # 实现自定义切割逻辑
    pass
```

### 扩展独立模块

可以在 `standalone_modules` 目录中添加新的识别器：

```python
# standalone_modules/custom_recognizer.py
class CustomEquipmentRecognizer:
    def __init__(self, **params):
        # 初始化自定义识别器
        pass
    
    def recognize_equipment(self, base_image_path, target_image_path):
        # 实现自定义识别逻辑
        pass
```

### 添加新的配置项

可以在 `config.json` 中添加新的配置节：

```json
{
  "custom_algorithm": {
    "enabled": true,
    "param1": "value1",
    "param2": 123
  }
}
```

然后在 `ConfigManager` 类中添加对应的访问方法：

```python
def get_custom_config(self):
    """获取自定义算法配置"""
    return self.config.get("custom_algorithm", {})
```

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目！

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至项目维护者

## 系统集成指南

### 与现有系统集成

1. **兼容性保证**：
   - 保持原有API接口不变
   - 提供向后兼容的配置选项
   - 渐进式迁移策略

2. **配置迁移**：
   - 自动检测旧配置格式
   - 提供配置转换工具
   - 保留用户自定义设置

3. **性能监控**：
   - 集成性能指标收集
   - 提供算法对比报告
   - 监控系统资源使用

### 部署建议

1. **开发环境**：
   - 使用高级算法进行开发测试
   - 启用详细日志记录
   - 使用交互式启动脚本

2. **测试环境**：
   - 进行算法对比测试
   - 验证配置参数效果
   - 性能基准测试

3. **生产环境**：
   - 根据实际需求选择算法
   - 优化配置参数
   - 监控系统性能

---

*最后更新：2025年11月*