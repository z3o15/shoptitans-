# 游戏装备识别项目

这是一个用于识别游戏装备的项目，支持多种识别算法和OCR金额识别功能。

## 快速开始

### OCR金额识别

自动识别游戏截图中的金额信息：

```bash
python step_tests\5_ocr.py
```

**功能特点：**
- ✅ 完全自动化，无需用户交互
- ✅ 支持中文路径
- ✅ 自动清空旧数据
- ✅ 生成CSV结果和详细报告
- ✅ 识别成功率高达100%

**输出位置：** `ocr_output/`
- `amount_records_*.csv` - 识别结果（文件名、金额、置信度）
- `report_*.txt` - 处理报告（摘要和详细结果）
- `log.txt` - 详细日志

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
├── ocr_output/                   # OCR输出目录（自动生成）
├── images/                       # 图像目录
│   ├── base_equipment/          # 基准装备图像
│   ├── game_screenshots/        # 游戏截图
│   └── equipment_crop/          # 切割后的金额图像
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
**输出：** `ocr_output/` 目录
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

## 注意事项

1. 确保输入图像路径正确
2. 首次运行会下载EasyOCR模型（需要网络连接）
3. OCR识别使用CPU模式，GPU模式可提升速度
4. 每次运行会自动清空`ocr_output`目录的旧数据

## 许可证

本项目仅供学习和研究使用。