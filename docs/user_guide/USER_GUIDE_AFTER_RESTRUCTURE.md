# 游戏装备图像识别系统 - 用户指南（重构版）

## 概述

欢迎使用重构后的游戏装备图像识别系统！本指南将帮助您了解和使用重构后的系统，享受更加清晰、高效的装备识别体验。重构后的系统提供了简化的输出、统一的日志管理和优化的性能，让您的使用体验更加流畅。

## 系统简介

### 主要功能

1. **游戏截图切割**：将游戏界面截图自动分割成单个装备图片
2. **装备识别匹配**：使用多种算法匹配装备图片与基准装备库
3. **OCR金额识别**：识别装备图片中的金额信息
4. **结果整合**：整合装备名称和金额识别结果，生成统一报告
5. **日志管理**：提供详细的处理日志和报告，便于跟踪和调试

### 系统特点

- **简化输出**：控制台只显示关键信息，减少信息过载
- **结构化日志**：按步骤分类记录日志，自动生成报告
- **智能算法**：支持多种匹配算法，自动选择最佳方案
- **批量处理**：支持批量处理多个截图和装备
- **灵活配置**：提供丰富的配置选项，满足不同需求

## 安装与设置

### 环境要求

- Python 3.8 或更高版本
- pip 包管理器
- 足够的磁盘空间存储图片和日志

### 安装步骤

1. **克隆或下载项目代码**
   ```bash
   git clone <项目地址>
   cd shoptitans 图片分隔和匹配
   ```

2. **安装依赖包**
   ```bash
   pip install -r requirements.txt
   ```

3. **准备数据文件**
   - 将基准装备图放入 `images/base_equipment/` 目录
   - 将游戏截图放入 `images/game_screenshots/` 目录

4. **验证安装**
   ```bash
   python run_optimized_system.py
   ```

## 快速开始

### 方式一：全自动运行（推荐）

最简单的方式是运行全自动流程，系统会自动完成所有步骤：

```bash
python run_optimized_system.py
```

系统将依次执行：
1. 获取原始图片
2. 分割原始图片
3. 装备识别匹配
4. 整合装备名称和金额识别结果

### 方式二：使用交互式界面

如果需要更多控制，可以使用交互式界面：

```bash
python src/run_recognition_start.py
```

系统将显示菜单，让您选择要执行的步骤。

### 方式三：分步执行

如果需要更精细的控制，可以分步执行各个功能：

```python
from src.run_recognition_start import step1_get_screenshots, step2_cut_screenshots, step3_match_equipment, step4_integrate_results

# 步骤1：获取原始图片
step1_get_screenshots(auto_mode=True)

# 步骤2：分割原始图片
step2_cut_screenshots(auto_mode=True)

# 步骤3：装备识别匹配
step3_match_equipment(auto_mode=True)

# 步骤4：整合结果
step4_integrate_results(auto_mode=True)
```

## 使用指南

### 1. 准备工作

#### 1.1 准备基准装备图

将您要识别的目标装备图片放入 `images/base_equipment/` 目录：

```
images/base_equipment/
├─ equipment1.png
├─ equipment2.webp
└─ equipment3.jpg
```

**注意事项**：
- 支持的格式：PNG、JPG、JPEG、WEBP
- 建议使用清晰、无背景的装备图标
- 文件名将作为装备名称，建议使用有意义的名称

#### 1.2 准备游戏截图

将包含装备的游戏界面截图放入 `images/game_screenshots/` 目录：

```
images/game_screenshots/
├─ screenshot1.png
├─ screenshot2.webp
└─ screenshot3.jpg
```

**注意事项**：
- 确保截图包含完整的装备界面
- 截图分辨率建议与游戏原始分辨率一致
- 避免截图模糊或有遮挡

### 2. 运行系统

#### 2.1 全自动运行

最简单的运行方式，系统会自动完成所有步骤：

```bash
python run_optimized_system.py
```

**输出示例**：
```
============================================================
优化后的游戏装备图像识别系统
============================================================
本演示展示优化后的终端输出效果
只显示关键信息，详细信息保存在日志文件中
============================================================

🚀 执行: 步骤1：获取原始图片
✅ 找到 2 个游戏截图

🚀 执行: 步骤2：分割原始图片
  [████████████████████] 100.0% 2/2
✅ 共切割出 24 个装备图片

🚀 执行: 步骤3：装备识别匹配
  [████████████████████] 100.0% 24/24
✅ 在 24 个装备中找到 8 个匹配项

🚀 执行: 步骤4：整合装备名称和金额识别结果
✅ 成功整合装备名称和金额识别结果

✅ 所有步骤执行完成！总耗时: 12.45秒

📊 详细报告已生成: output/summary_report.md
============================================================
🎉 优化后的系统演示完成！
============================================================
```

#### 2.2 交互式运行

如果需要更多控制，可以使用交互式界面：

```bash
python src/run_recognition_start.py
```

系统将显示菜单，让您选择要执行的步骤：

```
============================================================
游戏装备图像识别系统
============================================================
【四步工作流程】
1. 步骤1：获取原始图片
2. 步骤2：分割原始图片
3. 步骤3：装备识别匹配
4. 步骤4：整合装备名称和金额识别结果
5. 运行完整工作流程
6. 🚀 运行全自动工作流程（推荐）
------------------------------------------------------------
【其他功能】
7. 检查环境和依赖
8. 运行系统测试
9. 运行基础示例
10. 运行高级示例
11. 查看项目文档
12. 清理切割结果和日志
13. 生成带圆形标记的原图注释
0. 退出
------------------------------------------------------------
```

### 3. 查看结果

#### 3.1 控制台输出

重构后的系统在控制台只显示关键信息：
- 步骤开始和结束
- 处理进度（只在关键节点显示）
- 成功/失败摘要
- 错误和警告信息

#### 3.2 详细日志

所有详细信息都记录在日志文件中，位于 `output/` 目录：

```
output/
├─ step1_helper/
│   ├─ log.txt          # 步骤日志
│   ├─ report.md        # 步骤报告
│   └─ temp_files/      # 临时文件
├─ step2_cut/
│   ├─ log.txt          # 步骤日志
│   ├─ report.md        # 步骤报告
│   ├─ images/          # 切割后的装备图片
│   └─ txt/             # 文本输出
├─ step3_match/
│   ├─ log.txt          # 步骤日志
│   ├─ report.md        # 步骤报告
│   ├─ images/          # 匹配结果图片
│   └─ txt/             # 匹配结果文本
├─ step5_ocr/
│   ├─ log.txt          # 步骤日志
│   ├─ report.md        # 步骤报告
│   ├─ images/          # OCR结果图片
│   └─ txt/             # OCR结果文本
└─ summary_report.md     # 汇总报告
```

#### 3.3 汇总报告

系统会自动生成汇总报告 `output/summary_report.md`，包含：
- 总体统计信息
- 各步骤处理时间线
- 详细报告链接
- 系统信息和建议

### 4. 配置系统

#### 4.1 基本配置

系统配置文件为 `config.json`，包含主要配置项：

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
    "cropped_equipment_dir": "cropped_equipment",
    "logs_dir": "recognition_logs"
  }
}
```

#### 4.2 日志配置

重构后的系统支持灵活的日志配置：

```python
from src.unified_logger import init_unified_logger_from_config

logger_config = {
    "base_output_dir": "output",
    "console_mode": True,
    "output": {
        "show_step_progress": True,      # 显示步骤进度
        "show_item_details": False,      # 隐藏每个项目的详细信息
        "show_warnings": True,           # 显示警告
        "show_errors": True,             # 显示错误
        "show_success_summary": True,     # 显示成功摘要
        "show_performance_metrics": False, # 隐藏性能指标
        "console_level": "INFO"          # 控制台日志级别
    }
}

logger = init_unified_logger_from_config(logger_config)
```

## 高级使用

### 1. 使用不同算法

系统支持多种匹配算法，可以根据需求选择：

```python
from src.equipment_recognizer import EnhancedEquipmentRecognizer

# 创建增强版识别器
recognizer = EnhancedEquipmentRecognizer(
    default_threshold=80,
    use_advanced_algorithm=True,  # 使用高级算法
    enable_masking=True,         # 启用掩码匹配
    enable_histogram=True        # 启用直方图验证
)

# 执行匹配
similarity, is_match = recognizer.compare_images("img1.png", "img2.png")
```

### 2. 批量处理

系统支持批量处理多个文件：

```python
from src.run_recognition_start import run_full_auto_workflow

# 运行全自动工作流程
success = run_full_auto_workflow(
    auto_clear_old=True,      # 自动清理旧文件
    auto_select_all=True,      # 自动选择所有截图
    save_original=False,        # 不保存原图
    auto_select_base=True,      # 自动选择第一个基准装备
    auto_threshold=None,        # 使用默认阈值
    auto_generate_annotation=False  # 不生成注释
)
```

### 3. 自定义日志

可以使用日志适配器自定义日志行为：

```python
from src.logger_adapter import create_logger_adapter, ScreenshotCutterWithAdapter

# 创建日志适配器
adapter = create_logger_adapter(use_new_logger=True)

# 使用适配器包装现有模块
cutter = ScreenshotCutterWithAdapter(adapter)

# 执行操作（会自动记录日志）
success = cutter.cut_screenshots("screenshot.png", "output/images")
```

## 常见问题

### Q1: 控制台输出太简单，我想看到更详细的信息怎么办？

A: 有两种方式可以查看详细信息：
1. 查看 `output/step*/log.txt` 文件，包含所有详细日志
2. 修改日志配置，设置 `"show_item_details": True` 显示更多细节

### Q2: 如何提高识别准确率？

A: 可以尝试以下方法：
1. 降低匹配阈值（在config.json中调整default_threshold）
2. 使用高级算法（设置use_advanced_algorithm为true）
3. 启用掩码匹配和直方图验证
4. 确保基准装备图清晰且与截图中的装备角度一致

### Q3: 处理速度太慢怎么办？

A: 可以尝试以下优化：
1. 使用传统dHash算法（速度更快，精度略低）
2. 禁用掩码匹配和直方图验证
3. 减少处理的图片数量
4. 确保截图分辨率适中

### Q4: 如何处理不同分辨率的截图？

A: 
1. 固定坐标切割需要根据分辨率调整参数
2. 轮廓检测切割对分辨率变化更鲁棒
3. 建议使用自动模式让程序选择最佳切割方式

### Q5: 如何查看详细的匹配结果？

A: 系统会自动生成详细报告：
1. 查看 `output/step*/report.md` 文件，包含步骤详细报告
2. 查看 `output/summary_report.md` 文件，包含汇总报告
3. 报告中包含匹配结果、统计信息和处理建议

## 故障排除

### 1. 依赖安装问题

**问题**：运行时提示缺少依赖包
```
ImportError: No module named 'cv2'
```

**解决方案**：
```bash
pip install -r requirements.txt
```

如果仍有问题，可以手动安装：
```bash
pip install opencv-python pillow numpy
```

### 2. 文件路径问题

**问题**：提示找不到文件或目录
```
FileNotFoundError: [Errno 2] No such file or directory: 'images/base_equipment'
```

**解决方案**：
1. 确保在项目根目录运行程序
2. 检查 `images/` 目录下是否有 `base_equipment` 和 `game_screenshots` 子目录
3. 确保基准装备图和游戏截图已放入相应目录

### 3. 内存不足问题

**问题**：处理大量图片时出现内存不足错误

**解决方案**：
1. 减少批量处理的图片数量
2. 使用较小的图片分辨率
3. 关闭其他占用内存的程序
4. 分批处理图片

### 4. 识别准确率低

**问题**：识别结果不准确，匹配率低

**解决方案**：
1. 检查基准装备图是否清晰
2. 调整匹配阈值
3. 尝试不同的算法
4. 检查切割参数是否正确

## 最佳实践

### 1. 准备高质量数据

- 使用清晰、无背景的基准装备图
- 确保游戏截图分辨率一致
- 避免截图模糊或有遮挡

### 2. 合理配置参数

- 根据实际需求调整匹配阈值
- 选择合适的算法（速度优先vs精度优先）
- 配置合适的切割参数

### 3. 定期清理结果

- 定期清理旧的切割结果和日志
- 保留重要的结果文件
- 使用系统提供的清理功能

### 4. 查看详细日志

- 遇到问题时查看详细日志
- 利用系统生成的报告进行分析
- 根据报告建议调整配置

## 更新日志

### v2.0.0 (2025-11-24)
- 重构日志系统，提供统一的日志管理
- 优化控制台输出，只显示关键信息
- 改进报告生成，自动生成详细报告
- 提升代码质量，减少重复代码
- 优化系统性能，提高处理效率

### v1.0.0 (2024-05-20)
- 初始版本发布
- 实现基本的图像切割和匹配功能
- 支持多种匹配算法
- 提供配置管理功能

---

*用户指南最后更新：2025年11月24日*