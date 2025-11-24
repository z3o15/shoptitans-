# 装备名称和金额整合实现计划

## 概述

本文档详细描述了如何将装备名称识别和金额识别整合到统一的CSV记录中，实现全流程自动化。

## 当前系统分析

### 现有数据流程
1. **图像切割**：游戏截图 → 装备图片 (images/cropped_equipment)
2. **装备识别**：装备图片 → 装备名称匹配
3. **金额识别**：带标记装备图片 → 金额识别 (images/cropped_equipment_marker)
4. **CSV记录**：仅记录金额信息

### 现有CSV结构
```csv
original_filename,new_filename,confidence
01.png,"01_617,650.png",0.9967337706099908
```

### 文件命名规则
- 装备图片：`01.png`, `02.png`, ...
- 金额图片：`01_617,650.png`, `02_415,000.png`, ...

## 整合方案

### 1. 新数据流程
```
游戏截图 → 图像切割 → 装备识别 → 装备名称匹配 → OCR金额识别 → CSV整合记录
```

### 2. 新CSV结构
```csv
original_filename,new_filename,equipment_name,amount,confidence
01.png,"01_noblering_617,650.png","noblering","617,650",0.9967337706099908
```

## 实现细节

### 1. 修改CSV记录管理器 (src/csv_record_manager.py)

#### 1.1 更新CSVRecord数据类
```python
@dataclass
class CSVRecord:
    """CSV记录数据类"""
    timestamp: str
    original_filename: str
    new_filename: str
    equipment_name: str  # 新增：装备名称
    amount: str  # 新增：金额
    processing_time: float
    status: str
    error_message: Optional[str] = None
    recognized_text: Optional[str] = None
    confidence: Optional[float] = None
    original_path: Optional[str] = None
    new_path: Optional[str] = None
```

#### 1.2 更新CSV表头
```python
def _get_csv_headers(self) -> List[str]:
    """获取CSV表头"""
    return [
        'original_filename',
        'new_filename',
        'equipment_name',  # 新增
        'amount',  # 新增
        'confidence'
    ]
```

#### 1.3 更新记录数据准备
```python
# 准备记录数据
record_data = {
    'original_filename': record.original_filename,
    'new_filename': record.new_filename,
    'equipment_name': record.equipment_name,  # 新增
    'amount': record.amount,  # 新增
    'confidence': record.confidence or ""
}
```

### 2. 修改增强OCR识别器 (src/enhanced_ocr_recognizer.py)

#### 2.1 添加装备名称识别功能
```python
def recognize_equipment_name(self, image_path: str) -> Optional[str]:
    """识别装备名称
    
    Args:
        image_path: 装备图像路径
        
    Returns:
        识别到的装备名称，如果未识别到则返回None
    """
    try:
        from .equipment_recognizer import EnhancedEquipmentRecognizer
        from .config_manager import get_config_manager
        
        # 获取配置管理器
        config_manager = get_config_manager()
        
        # 创建装备识别器
        recognizer = EnhancedEquipmentRecognizer(
            default_threshold=config_manager.get_default_threshold(),
            algorithm_type="feature"
        )
        
        # 获取基准装备目录
        base_equipment_dir = "images/base_equipment"
        
        # 遍历所有基准装备进行匹配
        for base_filename in os.listdir(base_equipment_dir):
            if base_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                base_path = os.path.join(base_equipment_dir, base_filename)
                equipment_name = os.path.splitext(base_filename)[0]
                
                # 比较图像
                similarity, is_match = recognizer.compare_images(base_path, image_path)
                
                if is_match:
                    self.logger.info(f"识别到装备: {equipment_name}, 相似度: {similarity}%")
                    return equipment_name
        
        self.logger.warning(f"未识别到装备名称: {image_path}")
        return None
        
    except Exception as e:
        self.logger.error(f"装备名称识别失败: {image_path}, 错误: {e}")
        return None
```

#### 2.2 添加整合处理方法
```python
def process_and_integrate_results(self, equipment_folder: str, marker_folder: str, 
                                 csv_output_path: str = None) -> List[Dict]:
    """处理并整合装备名称和金额识别结果
    
    Args:
        equipment_folder: 装备图片文件夹
        marker_folder: 带标记的装备图片文件夹
        csv_output_path: CSV输出文件路径
        
    Returns:
        整合后的处理记录列表
    """
    # 获取CSV文件路径
    if csv_output_path is None:
        csv_output_path = self.config_manager.get_output_csv_path()
    
    # 清理CSV文件内容（保留表头）
    self.csv_record_manager.clear_csv_file(csv_output_path)
    
    # 获取装备图片列表
    equipment_files = []
    for filename in sorted(os.listdir(equipment_folder)):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            equipment_files.append(filename)
    
    # 获取金额图片列表
    marker_files = []
    for filename in sorted(os.listdir(marker_folder)):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            marker_files.append(filename)
    
    # 整合处理记录
    integrated_records = []
    
    for i, equipment_file in enumerate(equipment_files):
        # 提取文件序号
        equipment_number = os.path.splitext(equipment_file)[0]
        
        # 识别装备名称
        equipment_path = os.path.join(equipment_folder, equipment_file)
        equipment_name = self.recognize_equipment_name(equipment_path)
        
        # 查找对应的金额文件
        amount = ""
        confidence = 0.0
        new_filename = equipment_file
        
        for marker_file in marker_files:
            marker_number = os.path.splitext(marker_file)[0].split('_')[0]
            if marker_number == equipment_number:
                # 提取金额信息
                marker_path = os.path.join(marker_folder, marker_file)
                ocr_result = self.recognize_with_fallback(marker_path)
                
                if ocr_result.success:
                    amount = ocr_result.extracted_amount or ""
                    confidence = ocr_result.confidence
                    
                    # 生成新的文件名（包含装备名称和金额）
                    if equipment_name and amount:
                        new_filename = f"{equipment_number}_{equipment_name}_{amount}.png"
                    elif equipment_name:
                        new_filename = f"{equipment_number}_{equipment_name}.png"
                    elif amount:
                        new_filename = f"{equipment_number}_{amount}.png"
                
                break
        
        # 创建CSV记录
        csv_record = CSVRecord(
            timestamp="",
            original_filename=equipment_file,
            new_filename=new_filename,
            equipment_name=equipment_name or "未知装备",
            amount=amount,
            processing_time=0.0,
            status="成功" if (equipment_name or amount) else "失败",
            confidence=confidence
        )
        
        # 添加到CSV记录管理器缓存
        self.csv_record_manager.add_record_to_cache(csv_record)
        
        # 创建处理记录
        record = {
            "original_filename": equipment_file,
            "new_filename": new_filename,
            "equipment_name": equipment_name or "未知装备",
            "amount": amount,
            "confidence": confidence,
            "success": bool(equipment_name or amount)
        }
        
        integrated_records.append(record)
    
    # 保存记录到CSV
    self.save_records_to_csv(csv_output_path)
    
    # 统计结果
    success_count = sum(1 for r in integrated_records if r["success"])
    self.logger.info(f"整合处理完成，成功: {success_count}/{len(integrated_records)}")
    
    return integrated_records
```

### 3. 修改主启动脚本 (run_recognition_start.py)

#### 3.1 添加新的整合步骤
在`step3_match_equipment`函数后添加新步骤：

```python
def step4_integrate_results(auto_mode=True):
    """步骤4：整合装备名称和金额识别结果"""
    print("\n" + "=" * 60)
    print("步骤 4/4：整合装备名称和金额识别结果")
    print("=" * 60)
    print("此步骤将整合装备名称和金额识别结果到统一CSV文件")
    print("-" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 获取最新的时间目录
    cropped_equipment_dir = "images/cropped_equipment"
    cropped_equipment_marker_dir = "images/cropped_equipment_marker"
    
    # 查找最新的时间目录
    subdirs = []
    for item in os.listdir(cropped_equipment_dir):
        item_path = os.path.join(cropped_equipment_dir, item)
        if os.path.isdir(item_path) and item.replace('_', '').replace(':', '').isdigit():
            subdirs.append(item)
    
    if not subdirs:
        print("❌ 未找到切割装备目录，请先完成步骤2")
        return False
    
    latest_dir = sorted(subdirs)[-1]
    equipment_folder = os.path.join(cropped_equipment_dir, latest_dir)
    marker_folder = os.path.join(cropped_equipment_marker_dir, latest_dir)
    
    print(f"✓ 找到时间目录: {latest_dir}")
    print(f"  装备目录: {equipment_folder}")
    print(f"  金额目录: {marker_folder}")
    
    # 执行整合处理
    try:
        from src.enhanced_ocr_recognizer import EnhancedOCRRecognizer
        from src.ocr_config_manager import OCRConfigManager
        from src.config_manager import get_config_manager
        
        # 初始化配置管理器
        base_config_manager = get_config_manager()
        ocr_config_manager = OCRConfigManager(base_config_manager)
        
        # 初始化增强版OCR识别器
        recognizer = EnhancedOCRRecognizer(ocr_config_manager)
        
        # 执行整合处理
        records = recognizer.process_and_integrate_results(
            equipment_folder=equipment_folder,
            marker_folder=marker_folder
        )
        
        # 输出结果摘要
        success_count = sum(1 for r in records if r["success"])
        print(f"\n处理完成:")
        print(f"  总文件数: {len(records)}")
        print(f"  成功整合: {success_count}")
        print(f"  失败数量: {len(records) - success_count}")
        
        # 显示成功整合的记录
        if success_count > 0:
            print(f"\n成功整合的记录:")
            for record in records:
                if record["success"]:
                    print(f"  {record['original_filename']} -> {record['new_filename']}")
                    print(f"    装备名称: {record['equipment_name']}")
                    print(f"    金额: {record['amount']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 整合过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False
```

#### 3.2 更新全自动工作流程
```python
def run_full_auto_workflow(auto_clear_old=True, auto_select_all=True, save_original=True,
                           auto_select_base=True, auto_threshold=None, auto_generate_annotation=False):
    """运行全自动工作流程，无需任何手动操作"""
    print("\n" + "=" * 60)
    print("🚀 运行全自动工作流程")
    print("=" * 60)
    print("自动依次执行四个步骤：获取截图 → 分割图片 → 装备匹配 → 整合结果")
    print("-" * 60)
    
    # 步骤1：获取原始图片
    if not step1_get_screenshots(auto_mode=True):
        print("❌ 步骤1失败，终止自动流程")
        return False
    
    # 步骤2：分割原始图片
    if not step2_cut_screenshots(auto_mode=True, auto_clear_old=auto_clear_old,
                                auto_select_all=auto_select_all, save_original=save_original):
        print("❌ 步骤2失败，终止自动流程")
        return False
    
    # 步骤3：装备识别匹配
    if not step3_match_equipment(auto_mode=True, auto_select_base=auto_select_base,
                               auto_threshold=auto_threshold, auto_match_all=True):
        print("❌ 步骤3失败，终止自动流程")
        return False
    
    # 步骤4：整合装备名称和金额识别结果
    if not step4_integrate_results(auto_mode=True):
        print("❌ 步骤4失败，终止自动流程")
        return False
    
    # 如果启用，自动生成注释
    if auto_generate_annotation:
        # ... 现有的注释生成代码 ...
    
    print("\n" + "=" * 60)
    print("🎉 全自动工作流程执行完成！")
    print("=" * 60)
    return True
```

## 配置更新

### 更新配置文件 (optimized_ocr_config.json)
```json
{
  "integration": {
    "enable_equipment_name_recognition": true,
    "enable_amount_recognition": true,
    "equipment_name_separator": "_",
    "amount_separator": "_",
    "csv_output_format": "extended",
    "equipment_recognition_threshold": 80
  },
  "ocr": {
    "output_csv": "integrated_equipment_records.csv"
  }
}
```

## 测试计划

### 1. 单元测试
- 测试装备名称识别功能
- 测试金额识别功能
- 测试CSV记录生成功能

### 2. 集成测试
- 测试完整的整合流程
- 测试错误处理机制
- 测试不同文件命名格式的处理

### 3. 系统测试
- 测试全自动工作流程
- 测试各种边界情况
- 性能测试

## 预期结果

### 1. 新CSV输出示例
```csv
original_filename,new_filename,equipment_name,amount,confidence
01.png,"01_noblering_617,650.png","noblering","617,650",0.9967337706099908
02.png,"02_noblering_415,000.png","noblering","415,000",0.9901575328020191
03.png,"03_target_equipment_1_325,000.png","target_equipment_1","325,000",0.9999168689475403
```

### 2. 文件重命名
- 装备图片：`01.png` → `01_noblering.png`
- 金额图片：`01_617,650.png`（保持不变）
- 整合记录：在CSV中记录完整信息

## 错误处理

### 1. 装备名称识别失败
- 使用默认名称："未知装备"
- 记录错误信息到日志
- 继续处理其他文件

### 2. 金额识别失败
- 金额字段留空
- 记录错误信息到日志
- 继续处理其他文件

### 3. 文件关联失败
- 尝试通过文件序号匹配
- 如果匹配失败，记录错误信息
- 继续处理其他文件

## 性能优化

### 1. 并行处理
- 装备名称识别和金额识别可以并行进行
- 使用多线程处理大量文件

### 2. 缓存机制
- 缓存装备识别结果
- 缓存OCR识别结果

### 3. 批量处理
- 批量读取文件列表
- 批量写入CSV记录

## 部署说明

### 1. 备份现有数据
- 备份现有的CSV文件
- 备份配置文件

### 2. 更新代码
- 按照本文档修改相关文件
- 确保所有依赖项正确安装

### 3. 测试验证
- 运行单元测试
- 运行集成测试
- 验证输出结果

### 4. 切换到新系统
- 更新配置文件
- 运行完整流程验证
- 监控系统运行状态

---

*文档创建时间：2025年11月22日*
*作者：系统架构师*