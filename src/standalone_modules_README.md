# 独立模块包

## 概述

该包包含可独立使用的模块，不依赖于项目的其他部分。目前主要包含高级装备识别器模块。

## 模块列表

### advanced_matcher_standalone.py

高级装备识别器 - 独立版本，实现模板匹配与辅助验证机制结合的识别方法。

## 功能特点

- **独立运行**：不依赖项目的其他部分，可以单独使用
- **高级匹配算法**：结合模板匹配和颜色直方图验证
- **掩码支持**：可选的掩码匹配功能，提高匹配精度
- **批量处理**：支持批量识别多个目标图像
- **传统算法对比**：提供与传统dHash算法的对比功能

## 依赖项

- Python 3.7+
- OpenCV (cv2)
- NumPy
- Pillow (PIL)

安装依赖：
```bash
pip install opencv-python numpy pillow
```

## 使用方法

### 基本使用

```python
from src.advanced_matcher_standalone import AdvancedEquipmentRecognizer

# 创建识别器实例
recognizer = AdvancedEquipmentRecognizer(enable_masking=True, enable_histogram=True)

# 单个图像识别
base_image = 'path/to/base/equipment.webp'
target_image = 'path/to/target/image.png'

result = recognizer.recognize_equipment(base_image, target_image)
print(f"装备名称: {result.item_name}")
print(f"置信度: {result.confidence:.2f}%")
print(f"匹配方式: {result.matched_by.name}")
```

### 批量识别

```python
from src.advanced_matcher_standalone import AdvancedEquipmentRecognizer

# 创建识别器实例
recognizer = AdvancedEquipmentRecognizer(enable_masking=True, enable_histogram=True)

# 批量识别
base_image = 'path/to/base/equipment.webp'
target_folder = 'path/to/target/folder'

results = recognizer.batch_recognize(base_image, target_folder, threshold=60.0)

for i, result in enumerate(results, 1):
    print(f"{i}. {result.item_name} - 置信度: {result.confidence:.2f}%")
```

### 与传统算法对比

```python
from src.advanced_matcher_standalone import AdvancedEquipmentRecognizer

# 创建识别器实例
recognizer = AdvancedEquipmentRecognizer()

# 与传统dHash算法对比
base_image = 'path/to/base/equipment.webp'
target_image = 'path/to/target/image.png'

comparison = recognizer.compare_with_traditional(base_image, target_image)
print(f"高级算法置信度: {comparison['advanced_result'].confidence:.2f}%")
print(f"传统dHash相似度: {comparison['traditional_similarity']:.2f}%")
print(f"推荐方法: {comparison['recommendation']}")
```

## API 参考

### AdvancedEquipmentRecognizer

#### 构造函数

```python
AdvancedEquipmentRecognizer(enable_masking=True, enable_histogram=True)
```

参数：
- `enable_masking`: 是否启用掩码匹配（默认：True）
- `enable_histogram`: 是否启用直方图验证（默认：True）

#### 主要方法

##### recognize_equipment(base_image_path, target_image_path)

识别单个装备图像。

参数：
- `base_image_path`: 基准装备图像路径
- `target_image_path`: 目标图像路径

返回：`AdvancedMatchResult` 对象

##### batch_recognize(base_image_path, target_folder, threshold=60.0)

批量识别装备图像。

参数：
- `base_image_path`: 基准装备图像路径
- `target_folder`: 目标图像文件夹
- `threshold`: 相似度阈值（默认：60.0）

返回：`AdvancedMatchResult` 对象列表

##### compare_with_traditional(base_image_path, target_image_path, traditional_threshold=80.0)

与传统dHash算法对比。

参数：
- `base_image_path`: 基准装备图像路径
- `target_image_path`: 目标图像路径
- `traditional_threshold`: 传统dHash算法阈值（默认：80.0）

返回：包含对比结果的字典

### 数据类

#### AdvancedMatchResult

识别结果数据类，包含以下字段：
- `item_name`: 装备名称
- `item_base`: 基准装备名称
- `matched_by`: 匹配方式枚举值
- `min_val`: 模板匹配最小值
- `hist_val`: 直方图距离
- `similarity`: 模板相似度（百分比）
- `confidence`: 综合置信度（百分比）
- `template`: 装备模板（可选）
- `location`: 匹配位置（可选）

#### ItemTemplate

装备模板数据类，包含以下字段：
- `image`: PIL图像对象
- `sockets`: 插槽数量

## 枚举类型

### MatchingAlgorithm

匹配算法枚举：
- `DEFAULT`: 默认算法
- `VARIANTS_ONLY`: 仅变体匹配
- `HISTOGRAM`: 直方图匹配

### MatchedBy

匹配方式枚举：
- `TEMPLATE_MATCH`: 模板匹配
- `HISTOGRAM_MATCH`: 直方图匹配
- `ONLY_UNIQUE_FOR_BASE`: 仅基准唯一匹配
- `ITEM_NAME`: 按名称匹配
- `SOLARIS_CIRCLET`: 特殊装备匹配

## 示例项目

在项目根目录下运行以下命令进行测试：

```bash
# 单个测试
python src/advanced_matcher_standalone.py

# 综合测试
python src/advanced_matcher_standalone.py --comprehensive
```

## 注意事项

1. 图像路径可以是相对路径或绝对路径
2. 支持的图像格式：PNG, JPG, JPEG, WEBP
3. 建议图像尺寸为113x113像素以获得最佳匹配效果
4. 匹配结果按置信度降序排列

## 版本历史

- v1.0.0: 初始版本，包含高级装备识别器功能