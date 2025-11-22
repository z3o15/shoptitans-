# 高级装备识别器 MVP 使用指南

## 🚀 快速开始

### 1. 环境准备

确保您的项目目录包含以下文件：
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
│   ├── equipment_recognizer.py         # 传统dHash识别器
│   ├── main.py                         # 主程序
│   └── screenshot_cutter.py            # 截图切割工具
├── standalone_modules/                  # 独立模块目录
│   ├── __init__.py                     # 模块初始化
│   ├── advanced_matcher_standalone.py  # 独立版本的高级识别器
│   └── README.md                       # 独立模块说明文档
├── images/                             # 图像资源目录
│   ├── base_equipment/                 # 基准装备图目录
│   │   └── target_equipment_1.webp   # 基准装备图像
│   ├── game_screenshots/               # 游戏截图目录
│   │   └── MuMu-20251122-085551-742.png  # 游戏截图
│   └── cropped_equipment/              # 切割后的装备图像
├── tests/                              # 测试文件目录
│   ├── __init__.py                     # 测试模块初始化
│   ├── test_unified.py                 # 统一测试程序
│   ├── test_mvp.py                     # MVP测试程序
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

### 2. 运行MVP测试

#### 方法一：使用独立版本（推荐）

```bash
# 直接运行独立的高级识别器
python standalone_modules/advanced_matcher_standalone.py
```

#### 方法二：安装依赖后运行

```bash
# 1. 安装必要依赖
python install_dependencies.py

# 2. 运行MVP测试
python run_mvp_test.py
```

## 🔧 核心功能

### ✅ 已实现的高级功能

1. **模板匹配系统**
   - OpenCV `cv2.matchTemplate()` 函数
   - `cv2.TM_SQDIFF_NORMED` 算法
   - 支持掩码匹配

2. **辅助验证机制**
   - HSV颜色直方图比较
   - 巴氏距离计算 (`cv2.HISTCMP_BHATTACHARYYA`)
   - 智能算法切换

3. **图像预处理**
   - 标准化尺寸 (104x208)
   - 灰度转换
   - 轮廓掩码生成

4. **多种匹配算法**
   - DEFAULT: 标准模板匹配
   - HISTOGRAM: 直方图优先匹配
   - VARIANTS_ONLY: 仅变体模板匹配

5. **性能对比功能**
   - 与传统dHash算法对比
   - 性能提升统计
   - 推荐使用建议

## 📊 测试结果说明

### 输出信息

MVP测试会输出以下信息：

1. **环境检查结果**
   - 依赖包安装状态
   - 测试图像文件存在性

2. **单个识别测试**
   - 传统dHash方法结果
   - 高级识别方法结果
   - 性能对比数据

3. **批量识别测试**
   - 批量处理统计
   - 匹配结果列表

4. **配置性能测试**
   - 不同配置下的性能对比
   - 处理时间统计

### 预期效果

- **更高精度**: 双重验证机制减少误识别
- **更强适应性**: 支持复杂背景和装备变体
- **性能提升**: 相比传统方法有显著改进
- **易于集成**: 完全兼容现有项目结构

## 🔍 故障排除

### 常见问题

**Q: 导入错误 "No module named 'loguru'"**
A: 运行 `python install_dependencies.py` 安装缺失的依赖包

**Q: 无法导入unique-matcher模块**
A: 确保unique-matcher项目在D:/unique-matcher路径下，或使用独立版本

**Q: 找不到测试图像**
A: 检查images目录中的文件是否存在，路径是否正确

**Q: 识别结果为空**
A: 检查图像质量和匹配阈值设置

### 调试建议

1. **降低匹配阈值**: 从60%开始测试
2. **检查图像预处理**: 确保图像清晰度和尺寸正确
3. **启用详细日志**: 查看具体的匹配过程信息
4. **对比不同配置**: 测试启用/禁用不同功能的效果

## 🚀 下一步

1. **集成到主流程**: 将高级识别器集成到主要的识别流程中
2. **参数优化**: 根据实际测试结果调整匹配阈值
3. **扩展装备支持**: 添加更多装备类型和特殊处理
4. **性能优化**: 实现缓存和并行处理

---

*最后更新: 2025年11月*