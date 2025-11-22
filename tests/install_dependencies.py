#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖安装脚本
安装MVP测试所需的Python包
"""

import subprocess
import sys
import os

def install_package(package):
    """安装单个包"""
    try:
        print(f"正在安装 {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} 安装成功")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ {package} 安装失败")
        return False

def main():
    """主安装函数"""
    print("=" * 60)
    print("MVP测试依赖安装")
    print("=" * 60)
    
    # 需要安装的包列表
    required_packages = [
        "opencv-python",
        "Pillow",
        "numpy",
        "loguru"
    ]
    
    print("检测并安装以下依赖包:")
    for package in required_packages:
        install_package(package)
    
    print("\n" + "=" * 60)
    print("依赖安装完成！")
    print("现在可以运行MVP测试：")
    print("python src/advanced_matcher_standalone.py")
    print("=" * 60)

if __name__ == "__main__":
    main()