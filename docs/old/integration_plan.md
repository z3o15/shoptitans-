# 图片匹配方法集成计划

## 概述
将 `template_matching_test.py` 中的图片匹配方法集成到 `3_step2_cut_screenshots.py` 中，使切割后的装备图片能够自动进行匹配。

## 分析结果

### 3_step2_cut_screenshots.py 功能分析
1. **图片切割功能**：
   - 从游戏截图目录读取截图
   - 使用 `ScreenshotCutter.cut_fixed()` 方法将截图切割成装备图片
   - 保存圆形带填充的装备图片到 `images/cropped_equipment_original`
   - 保存带圆形标记的副本到 `images/cropped_equipment_marker`
   - 将文件重命名为顺序编号（01.png, 02.png...）

2. **透明背景处理功能**：
   - 使用 `process_circular_to_transparent()` 函数将圆形带填充的装备图片改为透明背景PNG
   - 将圆形范围内的黑色区域替换为颜色 #39212e
   - 保存处理后的图片到 `images/cropped_equipment_transparent`

### template_matching_test.py 功能分析
1. **核心匹配函数**：
   - `load_image()` - 加载图像并处理透明通道
   - `template_matching()` - 使用cv2.matchTemplate进行模板匹配
   - `calculate_color_similarity_with_euclidean()` - 使用LAB色彩空间欧氏距离计算颜色相似度
   - `calculate_composite_score()` - 计算综合得分（模板匹配+颜色相似度）

2. **掩码处理函数**：
   - `create_background_mask()` - 创建背景掩码，排除指定背景色
   - `apply_mask_to_image()` - 将掩码应用到图像

3. **主要测试函数**：
   - `run_template_matching_test()` - 运行模板匹配测试，比较基准图像和对比图像

## 集成方案

### 1. 需要提取的函数
从 `template_matching_test.py` 中提取以下核心函数：
- `load_image()` - 加载图像并处理透明通道
- `template_matching()` - 使用cv2.matchTemplate进行模板匹配
- `create_background_mask()` - 创建背景掩码，排除指定背景色
- `calculate_color_similarity_with_euclidean()` - 计算颜色相似度
- `calculate_composite_score()` - 计算综合得分
- `log_message()` - 统一日志输出格式

### 2. 修改方案
1. **添加导入**：
   ```python
   import json
   from datetime import datetime
   ```

2. **添加匹配函数**：
   - 将上述函数复制到 `3_step2_cut_screenshots.py` 中

3. **添加匹配流程函数**：
   ```python
   def match_equipment_images(base_dir, compare_dir, output_dir):
       """执行装备图片匹配"""
       # 实现匹配逻辑
   ```

4. **修改 step2_cut_screenshots() 函数**：
   - 添加参数：`enable_matching=False`
   - 在透明背景处理完成后，如果启用匹配，则执行匹配流程
   - 输出匹配结果

### 3. 匹配流程设计
1. 读取基准图像目录：`images/base_equipment_new`
2. 读取对比图像目录：`images/cropped_equipment_transparent`（透明背景处理后的图片）
3. 对每个对比图像，与所有基准图像进行匹配
4. 计算综合得分（模板匹配得分 + 颜色相似度得分）
5. 输出最佳匹配结果

### 4. 输出格式
- 综合得分 > 94%：显示"对应装备"
- 综合得分 ≤ 94%：显示"最佳匹配"
- 输出包含：基准图像名称、对比图像名称、综合得分、模板匹配得分、颜色相似度

### 5. 保存结果
- 将匹配结果保存到 JSON 文件：`images/matching_results_{timestamp}.json`
- 生成汇总报告：`images/matching_summary_{timestamp}.txt`

## 实现步骤
1. 添加必要的导入
2. 添加匹配相关函数
3. 添加匹配流程函数
4. 修改主函数，添加匹配参数和流程
5. 测试修改后的代码

## 注意事项
1. 确保所有函数的参数和返回值保持一致
2. 保持原有的日志输出格式
3. 确保匹配功能不影响原有的切割和透明背景处理功能
4. 匹配功能应该是可选的，通过参数控制是否启用