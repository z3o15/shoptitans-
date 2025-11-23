#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主测试运行文件
用于统一管理和运行所有步骤的测试
"""

import os
import sys
import subprocess
import importlib.util
from datetime import datetime

def load_module_from_file(file_path, module_name):
    """从文件路径加载模块"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def run_step_test(step_number):
    """运行指定步骤的测试"""
    test_file = f"{step_number}_"
    
    # 确定测试文件名
    if step_number == 1:
        test_file += "helper_functions.py"
    elif step_number == 2:
        test_file += "step2_cut_screenshots.py"
    elif step_number == 3:
        test_file += "step3_match_equipment.py"
    elif step_number == 4:
        test_file += "ocr_amount_recognition.py"
    elif step_number == 5:
        test_file += "step4_integrate_results.py"
    elif step_number == 6:
        test_file += "generate_annotated_screenshots.py"
    elif step_number == 7:
        test_file += "visual_debugger.py"
    else:
        print(f"❌ 无效的步骤编号: {step_number}")
        return False
    
    test_path = os.path.join(os.path.dirname(__file__), test_file)
    
    if not os.path.exists(test_path):
        print(f"❌ 测试文件不存在: {test_path}")
        return False
    
    try:
        print(f"\n{'='*60}")
        print(f"运行步骤{step_number}测试: {test_file}")
        print(f"{'='*60}")
        
        # 加载并运行测试模块
        module_name = f"step{step_number}_test"
        test_module = load_module_from_file(test_path, module_name)
        
        # 调用测试函数
        if step_number == 1:
            result = test_module.test_v2_optimizations()
        elif step_number == 2:
            result = test_module.test_step2_cutting()
        elif step_number == 3:
            result = test_module.test_step3_matching()
        elif step_number == 4:
            result = test_module.test_ocr_amount_recognition()
        elif step_number == 5:
            result = test_module.test_step4_integration()
        elif step_number == 6:
            result = test_module.test_generate_annotated_screenshots()
        elif step_number == 7:
            result = test_module.test_visual_debugger()
        
        if result:
            print(f"\n✅ 步骤{step_number}测试通过")
        else:
            print(f"\n❌ 步骤{step_number}测试失败")
        
        return result
        
    except Exception as e:
        print(f"❌ 运行步骤{step_number}测试时出错: {e}")
        return False

def run_all_step_tests():
    """运行所有步骤的测试"""
    print("\n" + "=" * 60)
    print("运行所有步骤测试")
    print("=" * 60)
    print("将依次执行所有步骤的测试功能")
    print("-" * 60)
    
    results = {}
    
    # 运行所有步骤测试
    for step in range(1, 8):
        print(f"\n开始执行步骤{step}测试...")
        results[step] = run_step_test(step)
        
        if not results[step]:
            print(f"⚠️ 步骤{step}测试失败，但继续执行其他测试")
    
    # 输出测试结果汇总
    print("\n" + "=" * 60)
    print("所有步骤测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for step, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        step_name = f"步骤{step}"
        if step == 1:
            step_name += ": 辅助功能"
        elif step == 2:
            step_name += ": 分割原始图片"
        elif step == 3:
            step_name += ": 装备识别匹配"
        elif step == 4:
            step_name += ": 金额识别OCR"
        elif step == 5:
            step_name += ": 整合结果"
        
        print(f"{step_name:25} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有步骤测试全部通过！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")
        return False

def run_step_function(step_number):
    """运行指定步骤的功能"""
    test_file = f"{step_number}_"
    
    # 确定测试文件名
    if step_number == 1:
        test_file += "helper_functions.py"
    elif step_number == 2:
        test_file += "step2_cut_screenshots.py"
    elif step_number == 3:
        test_file += "step3_match_equipment.py"
    elif step_number == 4:
        test_file += "ocr_amount_recognition.py"
    elif step_number == 5:
        test_file += "step4_integrate_results.py"
    elif step_number == 6:
        test_file += "generate_annotated_screenshots.py"
    elif step_number == 7:
        test_file += "visual_debugger.py"
    else:
        print(f"❌ 无效的步骤编号: {step_number}")
        return False
    
    test_path = os.path.join(os.path.dirname(__file__), test_file)
    
    if not os.path.exists(test_path):
        print(f"❌ 测试文件不存在: {test_path}")
        return False
    
    try:
        print(f"\n{'='*60}")
        print(f"运行步骤{step_number}功能: {test_file}")
        print(f"{'='*60}")
        
        # 加载并运行测试模块
        module_name = f"step{step_number}_func"
        test_module = load_module_from_file(test_path, module_name)
        
        # 调用功能函数
        if step_number == 1:
            # 对于辅助功能，运行主菜单
            test_module.main()
            return True
        elif step_number == 2:
            result = test_module.step2_cut_screenshots(auto_mode=False)
        elif step_number == 3:
            result = test_module.step3_match_equipment(auto_mode=False)
        elif step_number == 4:
            # 对于金额识别OCR，运行主菜单
            test_module.main()
            return True
        elif step_number == 5:
            result = test_module.step4_integrate_results(auto_mode=False)
        elif step_number == 6:
            # 对于生成带圆形标记的原图注释，运行主菜单
            test_module.main()
            return True
        elif step_number == 7:
            # 对于可视化调试器，运行主菜单
            test_module.main()
            return True
        
        if result:
            print(f"\n✅ 步骤{step_number}功能执行成功")
        else:
            print(f"\n❌ 步骤{step_number}功能执行失败")
        
        return result
        
    except Exception as e:
        print(f"❌ 运行步骤{step_number}功能时出错: {e}")
        return False

def run_full_workflow():
    """运行完整工作流程"""
    print("\n" + "=" * 60)
    print("运行完整工作流程")
    print("=" * 60)
    print("将依次执行四个步骤：获取截图 → 分割图片 → 装备匹配 → 整合结果")
    print("-" * 60)
    
    results = {}
    
    # 步骤1：辅助功能（环境检查）
    print("\n步骤1：辅助功能（环境检查）")
    results[1] = run_step_function(1)
    
    # 询问是否继续
    print("\n是否继续执行步骤2？(y/n)")
    if input().strip().lower() != 'y':
        print("用户选择终止工作流程")
        return False
    
    # 步骤2：分割原始图片
    print("\n步骤2：分割原始图片")
    results[2] = run_step_function(2)
    
    if not results[2]:
        print("❌ 步骤2失败，终止工作流程")
        return False
    
    # 询问是否继续
    print("\n是否继续执行步骤3？(y/n)")
    if input().strip().lower() != 'y':
        print("用户选择终止工作流程")
        return False
    
    # 步骤3：装备识别匹配
    print("\n步骤3：装备识别匹配")
    results[3] = run_step_function(3)
    
    if not results[4]:
        print("❌ 步骤4失败，终止工作流程")
        return False
    
    # 询问是否继续
    print("\n是否继续执行步骤4？(y/n)")
    if input().strip().lower() != 'y':
        print("用户选择终止工作流程")
        return False
    
    # 步骤4：OCR金额识别
    print("\n步骤4：OCR金额识别")
    results[4] = run_step_function(4)
    
    # 询问是否继续
    print("\n是否继续执行步骤5？(y/n)")
    if input().strip().lower() != 'y':
        print("用户选择终止工作流程")
        return False
    
    # 步骤5：整合结果
    print("\n步骤5：整合结果")
    results[5] = run_step_function(5)
    
    if not results[3]:
        print("❌ 步骤3失败，终止工作流程")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 完整工作流程执行完成！")
    print("=" * 60)
    return True

def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 60)
    print("步骤测试管理器 - 主菜单")
    print("=" * 60)
    print("【步骤功能】")
    print("1. 步骤1：辅助功能（环境检查）")
    print("2. 步骤2：分割原始图片")
    print("3. 步骤3：装备识别匹配")
    print("4. 步骤4：金额识别OCR")
    print("5. 步骤5：整合装备名称和金额识别结果")
    print("6. 步骤6：生成带圆形标记的原图注释")
    print("7. 步骤7：可视化调试器")
    print("-" * 60)
    print("【步骤测试】")
    print("8. 测试步骤1：辅助功能")
    print("9. 测试步骤2：分割图片功能")
    print("10. 测试步骤3：装备匹配功能")
    print("11. 测试步骤4：金额识别OCR功能")
    print("12. 测试步骤5：整合结果功能")
    print("-" * 60)
    print("【批量操作】")
    print("15. 运行所有步骤测试")
    print("16. 运行完整工作流程（交互式）")
    print("-" * 60)
    print("【其他】")
    print("0. 退出")
    print("-" * 60)

def main():
    """主函数"""
    print("步骤测试管理器")
    print("用于管理和运行 enhanced_recognition_start.py 中的各个步骤功能")
    
    while True:
        show_menu()
        
        try:
            choice = input("请选择操作 (0-14): ").strip()
            
            if choice == '0':
                print("感谢使用，再见！")
                break
            elif choice == '1':
                run_step_function(1)
            elif choice == '2':
                run_step_function(2)
            elif choice == '3':
                run_step_function(3)
            elif choice == '4':
                run_step_function(4)
            elif choice == '5':
                run_step_function(5)
            elif choice == '6':
                run_step_function(6)
            elif choice == '7':
                run_step_function(7)
            elif choice == '8':
                run_step_test(1)
            elif choice == '9':
                run_step_test(2)
            elif choice == '10':
                run_step_test(3)
            elif choice == '11':
                run_step_test(4)
            elif choice == '12':
                run_step_test(5)
            elif choice == '13':
                run_step_test(6)
            elif choice == '14':
                run_all_step_tests()
            elif choice == '15':
                run_full_workflow()
            else:
                print("无效选择，请输入0-15之间的数字")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()