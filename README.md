# 自动化装备处理系统

从游戏截图到最终表格的完全自动化处理。

## 快速开始

### 一键启动（推荐）
双击 `start.bat` 文件即可启动完整的自动化处理流程

### 命令行启动
```bash
python auto_equipment_processor.py
```

**自动化流程：**
1. **环境检查** - 验证依赖和配置
2. **截图裁剪** - 从游戏截图提取装备图标
3. **装备匹配** - 使用LAB色彩空间匹配装备
4. **OCR识别** - 识别金额信息生成表格

**功能特点：**
- ✅ 完全自动化，一键处理
- ✅ 从截图到表格的完整流程
- ✅ 生成CSV数据表格
- ✅ 详细的处理报告

**输出位置：** `output/ocr/`
- CSV表格文件 - 匹配和识别结果
- 处理报告 - 详细的处理过程记录

## 项目结构

```
项目根目录/
├── src/                          # 核心源代码目录
│   ├── core/                     # 核心业务逻辑
│   │   ├── equipment_recognizer.py      # 装备识别器主模块
│   │   ├── screenshot_cutter.py         # 截图切割工具
│   │   ├── main.py                      # 主程序入口
│   │   ├── feature_matcher.py           # 特征匹配器
│   │   └── enhanced_feature_matcher.py  # 增强特征匹配器
│   ├── logging/                   # 日志系统
│   │   ├── unified_logger.py        # 统一日志管理器
│   │   ├── step_logger.py          # 步骤日志记录器
│   │   ├── node_logger.py          # 节点日志记录器
│   │   └── report_generator.py     # 报告生成器
│   ├── ocr/                      # OCR功能
│   │   ├── enhanced_ocr_recognizer.py  # 增强OCR识别器（支持中文路径）
│   │   ├── csv_record_manager.py       # CSV记录管理器
│   │   └── file_renamer.py            # 文件重命名工具
│   ├── preprocessing/             # 预处理
│   │   ├── enhanced_preprocess_start.py  # 增强预处理启动
│   │   ├── base_equipment_preprocessor.py  # 基准装备预处理器
│   │   ├── background_remover.py      # 背景移除器
│   │   ├── enhancer.py               # 图像增强器
│   │   └── resizer.py               # 图像缩放器
│   ├── cache/                    # 缓存
│   │   ├── feature_cache_manager.py  # 特征缓存管理器
│   │   └── build_feature_cache.py   # 特征缓存构建
│   ├── config/                   # 配置管理
│   │   ├── config_manager.py       # 配置管理器
│   │   └── ocr_config_manager.py   # OCR配置管理器
│   └── utils/                    # 工具函数
│       ├── path_manager.py         # 路径管理器
│       ├── background_mask.py      # 背景掩码工具
│       └── image_hash.py          # 图像哈希工具
├── config/                       # 配置目录
│   └── unified_config.json       # 统一配置文件
├── docs/                         # 文档目录
├── step_tests/                   # 步骤测试脚本
│   ├── 1_helper.py              # 辅助函数
│   ├── 2_cut.py                 # 截图切割
│   ├── 3_match.py               # 装备匹配
│   └── 5_ocr.py                 # OCR金额识别（主要功能）
├── output/                       # 输出目录（自动生成）
│   ├── ocr/                      # OCR输出目录
│   └── matching/                 # 装备匹配输出目录
├── output_enter_image/          # 图像输入目录
│   ├── base_equipment/          # 基准装备图像
│   ├── game_screenshots/        # 游戏截图
│   ├── equipment_crop/          # 切割后的金额图像
│   ├── equipment_transparent/   # 透明背景装备图
│   └── feature_cache/           # 装备特征缓存
├── requirements.txt              # 依赖包列表
└── README.md                    # 项目说明
```

## 环境要求

- Python 3.8+
- OpenCV
- EasyOCR
- NumPy
- Pillow

## 安装依赖

```bash
pip install -r requirements.txt
```

## 核心功能

### 1. OCR金额识别（主要功能）

**功能说明：**
- 自动识别游戏装备图片中的金额
- 支持包含中文字符的文件路径
- 每次运行自动清空旧数据
- 生成CSV和报告文件

**使用方法：**
```bash
python step_tests\5_ocr.py
```

**输入：** `images/equipment_crop/` 目录中的图片
**输出：** `output/ocr/` 目录
- CSV文件：包含文件名、金额、置信度
- 报告文件：包含处理摘要和详细结果
- 日志文件：包含完整的调试信息

**技术特点：**
- 使用EasyOCR引擎进行文本识别
- 支持多种预处理配置的回退机制
- 自动调整置信度阈值以提高识别率
- 使用`np.fromfile + cv2.imdecode`支持中文路径

### 2. 装备识别

支持多种算法：
- dHash算法
- 特征匹配
- 高级模板匹配

### 3. 截图切割

自动识别并切割游戏截图中的装备区域。

### 4. 特征缓存

预计算和缓存基准装备特征，提升识别性能。

## 配置说明

主要配置文件：
- `config/unified_config.json` - 统一配置文件

配置节包括：
- **recognition** - 识别算法配置
- **preprocessing** - 图像预处理配置
- **ocr** - OCR识别配置
- **paths** - 路径配置
- **logging** - 日志配置

## 技术架构

- **模块化设计**：各功能模块职责清晰
- **多算法支持**：可根据需要选择不同的识别算法
- **统一日志系统**：便于调试和问题追踪
- **特征缓存**：提升识别性能
- **中文路径支持**：完美支持包含中文字符的文件路径

## 问题修复记录

### OCR中文路径支持

**问题：** OpenCV的`cv2.imread()`无法读取包含中文字符的路径

**解决方案：** 
在`src/ocr/enhanced_ocr_recognizer.py`中使用`np.fromfile + cv2.imdecode`替代`cv2.imread()`

```python
# 支持中文路径的图像读取
image_array = np.fromfile(image_path, dtype=np.uint8)
image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
```

### OCR识别优化

**优化：** 跳过背景掩码处理，直接对原始图像进行OCR识别

**效果：** 识别成功率从0%提升到100%

### 路径结构重构 (2025-11-26)

**问题：** 项目中存在多个不一致的路径引用，导致运行时找不到目录

**修复内容：**

1. **输出目录统一化**
   - OCR输出：`ocr_output/` → `output/ocr/`
   - 匹配输出：`output/matching/`
   - 特征缓存：`images/feature_cache/` → `output_enter_image/feature_cache/`

2. **修复文件重复问题**
   - 问题：`step_tests/3_match_cached.py` 中文件加载导致重复输出
   - 原因：Windows文件系统大小写不敏感，但glob()同时搜索大小写扩展名
   - 解决：使用`set()`去重

3. **修正CSV保存路径**
   - 问题：匹配结果CSV保存到错误的 `output_enter_image/equipment_transparent/` 目录
   - 解决：修正为 `output/matching/` 目录

4. **更新所有脚本和文档**
   - `step_tests/3_match.py`, `step_tests/3_match_cached.py` - 默认路径
   - `build_cache.py` - ��助文档示例
   - `demo/test_cache_match.py` - 测试脚本路径
   - 所有文档文件中的路径引用

**效果：** 消除了路径不一致导致的运行错误，项目结构更加清晰

### 匹配状态显示优化 (2025-11-26)

**问题：** 只有高置信度匹配的文件才会显示，低置信度文件被忽略

**改进：** 修改 `step_tests/3_match.py` 的重命名逻辑，现在显示所有文件的匹配状态

**新增功能：**
- 显示所有文件的匹配状态表格
- 包含文件名、匹配装备、置信度得分、状态信息
- 高置信度（>90%）显示"已匹配"，其他显示"未匹配"
- 保持原有文件重命名功能

**输出示例：**
```
所有文件匹配状态：
--------------------------------------------------------------------------------
文件名                       匹配装备                 置信度得分      状态
--------------------------------------------------------------------------------
01_circle.png             yulescroll             58.1% 未匹配
02_circle.png             zweihander             62.7% 未匹配
03_circle.png             yggdrasilbranch        92.1% 已匹配
--------------------------------------------------------------------------------
```

## 故障排除

### 常见问题

1. **"基准图像目录不存在"错误**
   - **原因：** 使用了旧的路径或运行了错误的脚本版本
   - **解决：** 确保使用 `3_match.py` 或 `3_match_cached.py`，它们会自动使用正确的 `output_enter_image/base_equipment` 路径

2. **输出文件重复**
   - **原因：** Windows文件系统大小写不敏感导致的文件重复加载
   - **解决：** 已在最新版本中修复，使用 `set()` 去重

3. **CSV文件保存位置错误**
   - **原因：** 旧版本将匹配结果保存到输入目录
   - **解决：** 新版本将所有匹配结果保存到 `output/matching/` 目录

4. **缓存文件位置错误**
   - **原因：** 特征缓存保存到了 `images/feature_cache/`
   - **解决：** 新版本缓存位置为 `output_enter_image/feature_cache/`

### 推荐使用方式

**单步运行：**
```bash
# 装备匹配（带完整状态显示）
python step_tests/3_match.py

# 装备匹配（缓存优化版）
python step_tests/3_match_cached.py

# OCR金额识别
python step_tests/5_ocr.py
```

**缓存管理：**
```bash
# 构建特征缓存
python build_cache.py output_enter_image/base_equipment

# 强制重建缓存
python build_cache.py output_enter_image/base_equipment --force
```

## 注意事项

1. 确保输入图像路径正确
2. 首次运行会下载EasyOCR模型（需要网络连接）
3. OCR识别使用CPU模式，GPU模式可提升速度
4. 每次运行会自动清空`output/ocr`目录的旧数据

## 许可证

本项目仅供学习和研究使用。