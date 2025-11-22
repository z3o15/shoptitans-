#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
装备名称和金额整合功能测试脚本
"""

import os
import sys
from src.enhanced_ocr_recognizer import EnhancedOCRRecognizer
from src.ocr_config_manager import OCRConfigManager
from src.config_manager import get_config_manager

def test_integration():
    """测试装备名称和金额整合功能"""
    print("=" * 60)
    print("测试装备名称和金额整合功能")
    print("=" * 60)
    
    try:
        # 初始化配置管理器
        base_config_manager = get_config_manager("optimized_ocr_config.json")
        ocr_config_manager = OCRConfigManager(base_config_manager)
        
        # 初始化增强版OCR识别器
        recognizer = EnhancedOCRRecognizer(ocr_config_manager)
        
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
            print("❌ 未找到切割装备目录")
            return False
        
        latest_dir = sorted(subdirs)[-1]
        equipment_folder = os.path.join(cropped_equipment_dir, latest_dir)
        marker_folder = os.path.join(cropped_equipment_marker_dir, latest_dir)
        
        print(f"✓ 找到时间目录: {latest_dir}")
        print(f"  装备目录: {equipment_folder}")
        print(f"  金额目录: {marker_folder}")
        
        # 执行整合处理
        records = recognizer.process_and_integrate_results(
            equipment_folder=equipment_folder,
            marker_folder=marker_folder,
            csv_output_path="test_integration_output.csv"
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
        
        # 检查CSV文件是否生成
        if os.path.exists("test_integration_output.csv"):
            print(f"\n✓ CSV文件已生成: test_integration_output.csv")
            
            # 读取并显示CSV内容
            with open("test_integration_output.csv", "r", encoding="utf-8-sig") as f:
                lines = f.readlines()
                print(f"\nCSV文件内容 ({len(lines)} 行):")
                for i, line in enumerate(lines[:10]):  # 只显示前10行
                    print(f"  {i+1}: {line.strip()}")
                if len(lines) > 10:
                    print(f"  ... 还有 {len(lines) - 10} 行")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_integration()
    if success:
        print("\n✅ 测试成功！")
    else:
        print("\n❌ 测试失败！")
    
    sys.exit(0 if success else 1)