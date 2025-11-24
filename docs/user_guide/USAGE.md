# 使用说明

## 📁 目录结构

根据实际使用需求，项目已调整为以下目录结构：

```
shoptitans 图片分隔和匹配/
├── run_recognition.py             # 简化主程序（推荐使用）
├── src/                           # 源代码
│   ├── equipment_recognizer.py    # 装备识别核心类（包含增强版识别器）
│   ├── screenshot_cutter.py       # 图像切割工具
│   ├── config_manager.py          # 配置管理模块
│   └── main.py                    # 完整主程序
├── standalone_modules/             # 独立模块
│   ├── advanced_matcher_standalone.py  # 高级装备识别器独立实现
│   └── __init__.py                     # 模块初始化
├── images/                        # 图片总目录
│   ├── base_equipment/            # 基准装备图目录
│   │   └── target_equipment_1.webp # 目标基准装备图像
│   ├── game_screenshots/          # 游戏截图目录
│   │   └── [待放置游戏截图]
│   └── cropped_equipment/         # 切割后装备保存目录
├── recognition_logs/              # 日志保存目录
├── tests/                         # 测试文件目录
│   └── test_system.py             # 系统测试脚本
├── examples/                      # 使用示例
│   ├── basic_usage.py             # 基础使用示例
│   ├── advanced_usage.py          # 高级使用示例
│   └── enhanced_recognizer_usage.py # 增强版识别器示例
├── config.json                    # 配置文件
├── USAGE.md                       # 使用说明
├── PROJECT.md                     # 技术文档
├── README.md                      # 项目简介
├── TECHNICAL_SPECIFICATION.md    # 技术规格文档
├── CHANGELOG.md                  # 更新日志
├── requirements.txt               # 依赖包列表
└── start.py                      # 交互式启动脚本
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt
```

### 2. 准备数据文件

1. **基准装备图**：将目标装备图像放入 `images/base_equipment/` 目录
   - 支持任意文件名：`.webp`, `.png`, `.jpg`, `.jpeg` 格式
   - 程序会自动检测该目录中的第一个图像文件
   
2. **游戏截图**：将包含多个装备的截图放入 `images/game_screenshots/` 目录
   - 支持任意文件名：`.webp`, `.png`, `.jpg`, `.jpeg` 格式
   - 程序会自动检测该目录中的第一个图像文件

### 3. 运行主程序

**方法1：使用简化主程序（推荐）**
```bash
python run_recognition.py
```

**方法2：使用交互式启动脚本**
```bash
python start.py
```

**方法3：使用完整主程序**
```bash
cd src
python main.py
```

### 4. 查看结果

- 切割后的单个装备将保存在 `images/cropped_equipment/` 目录
- 识别日志和结果将显示在控制台
- 详细日志可保存在 `recognition_logs/` 目录

## ⚙️ 配置说明

### 配置文件系统

项目使用统一的配置文件 `config.json` 管理所有参数，无需修改代码即可调整系统行为。

#### 配置文件结构

```json
{
  "recognition": {
    "default_threshold": 80,
    "use_advanced_algorithm": true,
    "enable_masking": true,
    "enable_histogram": true,
    "algorithm_description": "高级模板匹配算法提供更精确的装备识别，传统dHash算法提供更快的处理速度"
  },
  "cutting": {
    "default_method": "fixed",
    "fixed_grid": [6, 2],
    "fixed_item_width": 100,
    "fixed_item_height": 120,
    "fixed_margin_left": 20,
    "fixed_margin_top": 350,
    "contour_min_area": 800,
    "contour_max_area": 50000
  },
  "paths": {
    "images_dir": "images",
    "base_equipment_dir": "base_equipment",
    "game_screenshots_dir": "game_screenshots",
    "cropped_equipment_dir": "cropped_equipment",
    "logs_dir": "recognition_logs"
  },
  "logging": {
    "enable_logging": true,
    "log_level": "INFO",
    "include_algorithm_info": true,
    "include_performance_metrics": true
  },
  "performance": {
    "enable_caching": true,
    "cache_size": 100,
    "parallel_processing": false,
    "max_workers": 4
  },
  "ui": {
    "show_algorithm_selection": true,
    "show_performance_info": true,
    "show_detailed_results": true
  }
}
```

### 算法配置

#### 识别算法选择
- **use_advanced_algorithm**: `true`（高级模板匹配）/ `false`（传统dHash）
- **enable_masking**: 启用掩码匹配（仅高级算法有效）
- **enable_histogram**: 启用直方图验证（仅高级算法有效）

#### 算法特点对比
| 算法 | 速度 | 精度 | 适用场景 |
|------|------|------|----------|
| 传统dHash | 快（< 10ms） | 中等（> 95%） | 大批量处理 |
| 高级模板匹配 | 中等（< 50ms） | 高（> 98%） | 高精度识别 |

### 动态配置更新

```python
from src.config_manager import get_config_manager

# 获取配置管理器
config_manager = get_config_manager()

# 动态修改配置
config_manager.set_algorithm_mode(True)  # 切换到高级算法
config_manager.set_default_threshold(85)  # 调整阈值

# 查看当前配置
config_manager.print_config_summary()
```

### 参数调整指南

#### 切割参数调整

1. **网格布局 (fixed_grid)**：
   - 根据实际截图中的装备排列调整
   - 格式：[列数, 行数]

2. **装备尺寸 (fixed_item_width, fixed_item_height)**：
   - 测量截图中单个装备的实际像素尺寸
   - 确保包含完整的装备图像

3. **边距 (fixed_margin_left, fixed_margin_top)**：
   - 测量从截图左上角到第一个装备的距离
   - 确保切割位置准确

4. **轮廓检测参数 (contour_min_area, contour_max_area)**：
   - 调整最小/最大轮廓面积以过滤干扰
   - 根据装备实际大小调整范围

#### 识别参数调整

1. **匹配阈值 (default_threshold)**：
   - 范围：0-100
   - 建议：75-85
   - 越高越严格，越低越宽松

2. **算法选择 (use_advanced_algorithm)**：
   - 开发测试：建议使用高级算法
   - 生产环境：根据性能需求选择
   - 批量处理：建议使用传统算法

3. **高级算法参数**：
   - **enable_masking**: 启用掩码匹配，提高精度但增加计算量
   - **enable_histogram**: 启用直方图验证，提供颜色信息对比

## 📝 使用流程

### 步骤1：准备基准装备图
1. 获取清晰的目标装备图像
2. 使用任意文件名（支持 `.webp`, `.png`, `.jpg`, `.jpeg` 格式）
3. 放入 `images/base_equipment/` 目录

### 步骤2：准备游戏截图
1. 截取包含多个装备的游戏界面
2. 确保装备清晰可见
3. 使用任意文件名（支持 `.webp`, `.png`, `.jpg`, `.jpeg` 格式）
4. 放入 `images/game_screenshots/` 目录

### 步骤3：配置系统
1. 根据需求修改 `config.json` 文件
2. 选择合适的识别算法
3. 调整切割和识别参数

### 步骤4：运行识别

**推荐使用简化主程序：**
```bash
python run_recognition.py
```

**或使用交互式启动脚本：**
```bash
python start.py
```

**或使用完整主程序：**
```bash
cd src
python main.py
```

### 步骤5：查看结果
1. 检查 `images/cropped_equipment/` 目录中的切割结果
2. 查看控制台输出的匹配结果
3. 查看详细日志（保存在 `recognition_logs/` 目录）
4. 必要时调整参数重新运行

## 🔧 故障排除

### 常见问题

**Q: 切割位置不准确？**
A: 调整 `fixed_margin_left`、`fixed_margin_top`、`fixed_item_width`、`fixed_item_height` 参数

**Q: 识别准确率低？**
A:
1. 尝试切换到高级模板匹配算法
2. 启用掩码匹配和直方图验证
3. 降低匹配阈值
4. 确保基准装备图清晰
5. 检查切割结果是否完整

**Q: 高级算法不可用？**
A:
1. 检查 `standalone_modules` 目录是否存在
2. 确保OpenCV正确安装
3. 查看错误日志中的具体信息

**Q: 找不到文件？**
A: 检查文件路径和文件名是否正确

**Q: 配置修改无效？**
A:
1. 确认修改的是正确的 `config.json` 文件
2. 检查JSON格式是否正确
3. 重启程序使配置生效

### 调试技巧

1. **查看切割结果**：检查 `cropped_equipment/` 目录中的图像是否正确
2. **算法对比测试**：使用两种算法对比识别结果
3. **调整阈值**：从高到低逐步调整匹配阈值
4. **单步测试**：先测试切割，再测试识别
5. **查看详细日志**：启用详细日志记录获取更多信息

## 📊 扩展使用

### 简化主程序特点

[`run_recognition.py`](run_recognition.py) 是专门设计的主运行程序，具有以下特点：

1. **自动清理**：每次运行时自动清理之前的结果
2. **日志记录**：自动生成详细的识别日志
3. **错误处理**：完善的错误检查和提示
4. **简洁输出**：清晰的步骤显示和结果汇总
5. **配置集成**：自动加载和使用配置文件

### 交互式启动脚本

[`start.py`](start.py) 提供友好的交互式界面：

1. **菜单选择**：提供多种操作选项
2. **参数配置**：交互式配置系统参数
3. **算法选择**：动态切换识别算法
4. **结果预览**：实时显示处理结果

### 算法对比使用

```python
from src.equipment_recognizer import EnhancedEquipmentRecognizer

# 创建增强版识别器
recognizer = EnhancedEquipmentRecognizer()

# 测试两种算法
base_image = "images/base_equipment/target.webp"
target_image = "images/cropped_equipment/item.png"

# 高级算法
recognizer.set_algorithm_mode(True)
similarity1, match1 = recognizer.compare_images(base_image, target_image)
print(f"高级算法: {similarity1:.2f}%")

# 传统算法
recognizer.set_algorithm_mode(False)
similarity2, match2 = recognizer.compare_images(base_image, target_image)
print(f"传统算法: {similarity2:.2f}%")

# 性能对比
print(f"算法差异: {similarity1 - similarity2:.2f}%")
```

### 独立模块使用

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

# 批量识别
results = recognizer.batch_recognize("base.png", "target_folder/", threshold=60.0)
for result in results:
    print(f"{result.item_name}: {result.confidence:.2f}%")
```

### 批量处理多个截图

可以修改主程序来处理多个截图文件：

```python
import glob
from src.main import EquipmentMatcher
from src.config_manager import get_config_manager

# 获取配置管理器和匹配器
config_manager = get_config_manager()
matcher = EquipmentMatcher(config_manager)

# 获取所有截图文件
screenshot_files = glob.glob("images/game_screenshots/*.png")

for screenshot_path in screenshot_files:
    print(f"处理截图: {screenshot_path}")
    
    # 处理单个截图
    matched_items = matcher.process_screenshot(
        screenshot_path=screenshot_path,
        base_img_path="images/base_equipment/target.webp",
        output_folder="output",
        cutting_method='auto',
        threshold=80
    )
    
    print(f"识别到 {len(matched_items)} 个匹配的装备")
```

### 轮廓检测切割（优化版）

程序现在使用智能轮廓检测切割，具有以下优势：

1. **自适应**：自动识别装备边界，无需手动调整坐标
2. **智能筛选**：只保留符合装备特征的轮廓
3. **高精度**：基于形状和大小特征进行精确切割
4. **去干扰**：自动过滤背景和UI元素

**智能筛选条件**：
- **面积筛选**：只保留面积大于配置中最小轮廓面积的轮廓
- **形状筛选**：只保留宽高比在合理范围内的轮廓
- **边框检测**：使用阈值处理识别装备边框

**参数配置**：
在 `config.json` 中调整轮廓检测参数：
```json
{
  "cutting": {
    "contour_min_area": 800,
    "contour_max_area": 50000
  }
}
```

### 运行系统测试

```bash
# 运行统一测试程序
python tests/test_unified.py

# 或运行特定测试
python tests/test_system.py
```

### 性能基准测试

```python
from src.equipment_recognizer import EnhancedEquipmentRecognizer
import time

# 创建识别器
recognizer = EnhancedEquipmentRecognizer()

# 性能测试
start_time = time.time()
for i in range(100):
    similarity, match = recognizer.compare_images("img1.png", "img2.png")
end_time = time.time()

print(f"100次识别耗时: {end_time - start_time:.2f}秒")
print(f"平均每次识别耗时: {(end_time - start_time) / 100 * 1000:.2f}毫秒")
```

## 🔧 高级配置示例

### 高精度配置

```json
{
  "recognition": {
    "default_threshold": 85,
    "use_advanced_algorithm": true,
    "enable_masking": true,
    "enable_histogram": true
  },
  "cutting": {
    "default_method": "contour",
    "contour_min_area": 5000,
    "contour_max_area": 50000
  },
  "performance": {
    "enable_caching": true,
    "cache_size": 200
  }
}
```

### 高速度配置

```json
{
  "recognition": {
    "default_threshold": 75,
    "use_advanced_algorithm": false,
    "enable_masking": false,
    "enable_histogram": false
  },
  "cutting": {
    "default_method": "fixed"
  },
  "performance": {
    "enable_caching": false,
    "parallel_processing": true,
    "max_workers": 4
  }
}
```

### 开发调试配置

```json
{
  "logging": {
    "enable_logging": true,
    "log_level": "DEBUG",
    "include_algorithm_info": true,
    "include_performance_metrics": true
  },
  "ui": {
    "show_algorithm_selection": true,
    "show_performance_info": true,
    "show_detailed_results": true
  }
}
```

## 📚 更多资源

- [技术规格文档](TECHNICAL_SPECIFICATION.md) - 详细的技术实现说明
- [项目架构文档](PROJECT.md) - 系统架构和设计理念
- [更新日志](CHANGELOG.md) - 版本更新记录
- [示例代码](examples/) - 各种使用场景的示例代码

---

*如有问题，请查看详细文档 PROJECT.md 或提交 Issue*