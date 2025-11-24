# 配置文件重复问题分析与解决方案

## 问题概述

当前项目存在多个配置文件和配置目录，导致以下问题：

1. **config目录重复**：
   - 根目录 `config/`
   - `src/config/`

2. **配置文件重复**：
   - 根目录 `config.json`
   - `config/config.json`
   - `config/optimized_ocr_config.json`

3. **配置管理代码分散**：
   - `src/config/config_manager.py`
   - `src/config/ocr_config_manager.py`

## 详细分析

### 1. 配置文件内容对比

#### 根目录 config.json
- 包含完整的系统配置
- 有preprocessing、background_removal、feature_cache等高级配置
- OCR配置较为基础

#### config/config.json
- 配置较为简化
- 缺少一些高级配置项
- OCR配置与根目录有所不同

#### config/optimized_ocr_config.json
- 专门针对OCR优化的配置
- 包含更多OCR相关的高级选项
- 有integration配置节

### 2. 配置管理代码分析

#### src/config/config_manager.py
- 负责主配置文件管理
- 包含各种配置的获取和更新方法
- 默认配置较为完整

#### src/config/ocr_config_manager.py
- 专门管理OCR相关配置
- 依赖于config_manager.py
- 提供OCR配置的专门方法

## 解决方案

### 方案一：统一配置目录（推荐）

1. **保留根目录config/作为唯一配置目录**
2. **将src/config/合并到根目录config/**
3. **整合所有配置文件为一个统一配置结构**
4. **更新所有引用路径**

### 方案二：分离配置类型

1. **根目录config/存放系统级配置**
2. **src/config/存放代码级配置**
3. **明确区分配置用途**

## 推荐实施步骤

1. **创建统一的配置结构**
2. **迁移配置管理代码**
3. **更新所有引用**
4. **清理重复文件**
5. **更新文档**

## 配置文件整合建议

### 新的配置结构
```
config/
├── config.json              # 主配置文件
├── ocr_config.json           # OCR专用配置
├── algorithm_config.json     # 算法配置
└── paths_config.json         # 路径配置
```

### 或者单一配置文件
```
config/
└── unified_config.json       # 统一配置文件，包含所有配置节
```

## 代码整合建议

1. **保留ConfigManager作为主配置管理器**
2. **将OCRConfigManager集成到ConfigManager中**
3. **提供统一的配置访问接口**
4. **保持向后兼容性**