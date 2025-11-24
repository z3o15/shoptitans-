# 图像注释功能使用指南

## 概述

图像注释功能允许在原始游戏截图上添加圆形标记，标识识别到的装备位置。这个功能可以帮助用户直观地查看哪些装备被成功识别，以及它们的相似度分数。

## 功能特点

- 🎯 **精确标记**: 在原图上准确标记匹配的装备位置
- 📊 **相似度显示**: 可选显示每个匹配项的相似度百分比
- 🎨 **自定义样式**: 支持自定义圆形颜色、大小和字体
- 📝 **详细报告**: 自动生成包含所有匹配信息的JSON报告
- ⚙️ **配置管理**: 通过配置文件管理所有注释设置

## 使用方法

### 方法1: 通过主菜单使用

1. 运行启动脚本:
   ```bash
   python start.py
   ```

2. 选择 "11. 生成带圆形标记的原图注释"

3. 按照提示选择:
   - 要注释的截图（可选择单个或全部）
   - 基准装备图
   - 匹配阈值

4. 查看生成的注释图像和报告

### 方法2: 通过代码直接使用

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

# 定义匹配项和切割参数
matched_items = [("item_0_0.png", 95.2), ("item_0_3.png", 87.5)]
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

## 配置选项

在 `config.json` 文件中，可以自定义以下注释设置:

```json
{
  "annotation": {
    "enable_annotation": true,        // 启用/禁用注释功能
    "circle_color": "red",           // 圆形标记颜色
    "circle_width": 3,               // 圆形边框宽度(像素)
    "font_size": 12,                 // 文字大小(像素)
    "show_similarity_text": true,      // 是否显示相似度文字
    "auto_generate_annotation": false,  // 是否自动生成注释
    "annotation_output_dir": "annotated_screenshots"  // 注释输出目录
  }
}
```

### 配置说明

| 设置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `enable_annotation` | 布尔值 | `true` | 是否启用注释功能 |
| `circle_color` | 字符串 | `"red"` | 圆形标记颜色，支持常见颜色名称 |
| `circle_width` | 整数 | `3` | 圆形边框宽度，单位为像素 |
| `font_size` | 整数 | `12` | 相似度文字大小，单位为像素 |
| `show_similarity_text` | 布尔值 | `true` | 是否在圆形上方显示相似度百分比 |
| `auto_generate_annotation` | 布尔值 | `false` | 是否在匹配后自动生成注释 |
| `annotation_output_dir` | 字符串 | `"annotated_screenshots"` | 注释图像的默认输出目录 |

### 支持的颜色

圆形标记支持以下常见颜色名称:
- `red` (红色)
- `blue` (蓝色)
- `green` (绿色)
- `yellow` (黄色)
- `purple` (紫色)
- `orange` (橙色)
- `black` (黑色)
- `white` (白色)

## 输出文件

### 注释图像

- 文件名格式: `{原截图名}_annotated_{时间戳}.png`
- 保存位置: 与原截图相同目录或配置指定的输出目录
- 内容: 原始截图 + 圆形标记 + 相似度文字（可选）

### 注释报告

- 文件名格式: `annotation_report_{时间戳}.json`
- 保存位置: `recognition_logs` 目录
- 内容: 包含匹配详情的JSON报告

#### 报告示例

```json
{
  "timestamp": "2025-11-22T14:30:00.000Z",
  "screenshot_path": "images/game_screenshots/screenshot.png",
  "annotated_image_path": "images/game_screenshots/screenshot_annotated_20251122_143000.png",
  "total_matches": 3,
  "matches": [
    {
      "filename": "item_0_0.png",
      "similarity": 95.2
    },
    {
      "filename": "item_0_3.png",
      "similarity": 87.5
    },
    {
      "filename": "item_1_2.png",
      "similarity": 91.3
    }
  ]
}
```

## 工作流程

### 完整工作流程

1. **准备数据**
   - 将基准装备图放入 `images/base_equipment/`
   - 将游戏截图放入 `images/game_screenshots/`

2. **切割截图**
   - 使用步骤2切割游戏截图
   - 确保切割参数正确

3. **匹配装备**
   - 使用步骤3进行装备匹配
   - 调整匹配阈值以获得最佳结果

4. **生成注释**
   - 使用步骤11生成注释图像
   - 查看标记的装备位置和相似度

### 批量处理

注释功能支持批量处理多个截图:

1. 在主菜单选择 "11. 生成带圆形标记的原图注释"
2. 输入 `all` 选择所有截图
3. 系统将为每个截图生成注释图像和报告

## 测试功能

运行测试脚本验证注释功能:

```bash
python tests/test_image_annotator.py
```

测试包括:
- 图像注释器功能测试
- 注释配置功能测试
- 主工作流程集成测试

## 故障排除

### 常见问题

**Q: 注释图像中圆形位置不正确**
A: 检查切割参数是否与实际切割时使用的参数一致，特别是 `margin_left`、`margin_top`、`item_width` 和 `item_height`

**Q: 相似度文字不显示**
A: 检查配置文件中的 `show_similarity_text` 设置是否为 `true`

**Q: 圆形颜色不生效**
A: 确保使用支持的颜色名称，如 "red"、"blue" 等

**Q: 字体显示异常**
A: 系统会尝试加载合适的字体，如果失败将使用默认字体

### 调试步骤

1. 检查配置文件是否正确
2. 确认切割装备目录存在且包含匹配结果
3. 验证基准装备图和游戏截图路径
4. 运行测试脚本检查功能状态
5. 查看控制台输出的错误信息

## 技术细节

### 位置计算

注释器使用以下公式计算装备在原图中的位置:

```
x1 = margin_left + col * (item_width + h_spacing)
y1 = margin_top + row * (item_height + v_spacing)
x2 = x1 + item_width
y2 = y1 + item_height

center_x = (x1 + x2) // 2
center_y = (y1 + y2) // 2
radius = min(item_width, item_height) // 2 - 5
```

### 文件名解析

注释器支持两种文件名格式:
1. `item_row_col.png` - 从文件名直接提取行列信息
2. `01.png`, `02.png` - 按顺序计算行列位置

## 更新日志

### v1.0.0 (2025-11-22)
- ✨ 初始版本发布
- 🎯 支持在原图上添加圆形标记
- 📊 支持显示相似度百分比
- ⚙️ 支持配置文件管理
- 📝 支持生成详细JSON报告
- 🧪 完整的测试套件

---

*最后更新: 2025年11月22日*