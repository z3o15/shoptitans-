#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辅助功能测试模块
提供基础的环境检查、依赖验证和数据文件确认功能
仅包含核心辅助功能，不包含其他步骤专用的功能
"""

import os
import sys
import subprocess

# 添加项目根目录到Python路径，以便能够导入src模块
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入统一日志管理器（如果可用）
try:
    from unified_logger import get_unified_logger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False

def check_dependencies():
    """检查核心依赖是否已安装"""
    required_packages = ['cv2', 'PIL', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            elif package == 'numpy':
                import numpy
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"缺少依赖包: {', '.join(missing_packages)}")
        print("正在安装依赖...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✓ 依赖安装完成")
            return True
        except subprocess.CalledProcessError:
            print("✗ 依赖安装失败，请手动运行: pip install -r requirements.txt")
            return False
    else:
        print("✓ 所有依赖已安装")
        return True

def check_data_files():
    """检查基础数据文件是否存在 - 仅检查核心目录结构"""
    # 检查基准装备图目录
    base_equipment_dir = os.path.join(project_root, "images", "base_equipment")
    if not os.path.exists(base_equipment_dir):
        os.makedirs(base_equipment_dir, exist_ok=True)
    
    # 检查游戏截图目录
    game_screenshots_dir = os.path.join(project_root, "images", "game_screenshots")
    if not os.path.exists(game_screenshots_dir):
        os.makedirs(game_screenshots_dir, exist_ok=True)
    
    # 检查输出目录
    output_dir = os.path.join(project_root, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    print("✓ 目录结构检查完成")
    return True

def clear_previous_results():
    """清理之前的日志和结果文件"""
    # 确认操作
    confirm = input("确认清理旧文件吗？(y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消清理操作")
        return
    
    # 清理日志目录
    logs_dir = os.path.join(project_root, "recognition_logs")
    if os.path.exists(logs_dir):
        try:
            import shutil
            shutil.rmtree(logs_dir)
            os.makedirs(logs_dir, exist_ok=True)
        except Exception as e:
            print(f"清理日志目录时出错: {e}")
    
    # 清理输出目录（保留目录结构）
    output_dir = os.path.join(project_root, "output")
    if os.path.exists(output_dir):
        try:
            # 只清理文件，保留目录结构
            for root, dirs, files in os.walk(output_dir, topdown=False):
                for file in files:
                    try:
                        os.remove(os.path.join(root, file))
                    except Exception:
                        pass
        except Exception as e:
            print(f"清理输出目录时出错: {e}")
    
    print("✓ 清理完成")

def test_basic_functions():
    """测试基础工具功能"""
    # 测试基本导入
    try:
        import cv2
        import numpy as np
        from PIL import Image
        
        # 测试简单的图像处理
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img = cv2.rectangle(img, (20, 20), (80, 80), (0, 255, 0), 2)
        
        print("✓ 基础功能测试通过")
        return True
    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 功能测试失败: {e}")
        return False

def main():
    """主函数"""
    print("辅助功能测试模块")
    print("1. 检查环境和依赖")
    print("2. 检查数据文件")
    print("3. 清理旧文件")
    print("4. 测试基础功能")
    print("0. 退出")
    
    while True:
        try:
            choice = input("请选择操作 (0-4): ").strip()
            
            if choice == '0':
                print("感谢使用，再见！")
                break
            elif choice == '1':
                check_dependencies()
            elif choice == '2':
                check_data_files()
            elif choice == '3':
                clear_previous_results()
            elif choice == '4':
                test_basic_functions()
            else:
                print("无效选择，请输入0-4之间的数字")
                
        except KeyboardInterrupt:
            print("\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()