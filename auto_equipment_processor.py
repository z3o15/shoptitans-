#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化装备处理主控制器
实现从游戏截图到最终表格输出的完全自动化处理
"""

import os
import sys
import time
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, asdict

import cv2
import numpy as np
from PIL import Image

# 项目路径设置
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

@dataclass
class ProcessingResult:
    """处理结果数据类"""
    step: str
    status: str  # success, error, warning
    message: str
    processed_count: int = 0
    output_files: List[str] = None
    duration: float = 0.0

    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []

class AutoEquipmentProcessor:
    """自动化装备处理器主控制器"""

    def __init__(self, config_path: Optional[Path] = None):
        """初始化处理器"""
        self.project_root = project_root
        self.config_path = config_path or project_root / "config.json"
        self.config = self._load_config()

        # 路径配置
        self.paths = {
            'screenshots': self.project_root / "output_enter_image" / "game_screenshots",
            'base_equipment': self.project_root / "output_enter_image" / "base_equipment",
            'equipment_crop': self.project_root / "output_enter_image" / "equipment_crop",
            'equipment_transparent': self.project_root / "output_enter_image" / "equipment_transparent",
            'ocr_output': self.project_root / "output/ocr",
            'matching_output': self.project_root / "output/matching"
        }

        # 创建必要的目录
        for path in self.paths.values():
            path.mkdir(parents=True, exist_ok=True)

        self.results: List[ProcessingResult] = []
        self.start_time = None

    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 默认配置
                return {
                    "cutting": {"grid_cols": 6, "grid_rows": 4},
                    "matching": {"similarity_threshold": 0.7},
                    "ocr": {"min_confidence": 0.8}
                }
        except Exception as e:
            print(f"配置加载失败，使用默认配置: {e}")
            return {"cutting": {"grid_cols": 6, "grid_rows": 4}, "matching": {"similarity_threshold": 0.7}, "ocr": {"min_confidence": 0.8}}

    def _log_result(self, step: str, status: str, message: str, processed_count: int = 0,
                    output_files: List[str] = None, duration: float = 0.0):
        """记录处理结果"""
        result = ProcessingResult(
            step=step,
            status=status,
            message=message,
            processed_count=processed_count,
            output_files=output_files or [],
            duration=duration
        )
        self.results.append(result)

        # 同时输出到控制台
        status_icon = "[OK]" if status == "success" else "[WARNING]" if status == "warning" else "[ERROR]"
        print(f"[{step}] {status_icon} {message}")

    def _run_module(self, module_path: str, args: List[str] = None) -> Tuple[bool, str]:
        """运行指定的模块"""
        try:
            cmd = [sys.executable, module_path]
            if args:
                cmd.extend(args)

            print(f"执行命令: {' '.join(cmd)}")
            # Fix Windows encoding issues by using None for encoding (auto-detect)
            # and handle output separately to avoid encoding errors
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=False  # Get bytes instead of text to avoid encoding issues
            )

            # Decode output safely with fallback encoding
            try:
                stdout = result.stdout.decode('utf-8', errors='replace') if result.stdout else ""
                stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ""
            except Exception:
                # Fallback to system encoding if UTF-8 fails
                stdout = result.stdout.decode('gbk', errors='replace') if result.stdout else ""
                stderr = result.stderr.decode('gbk', errors='replace') if result.stderr else ""

            output = stdout + stderr
            return result.returncode == 0, output
        except Exception as e:
            return False, str(e)

    def step1_environment_check(self) -> bool:
        """步骤1: 环境检查"""
        print("\n" + "="*50)
        print("[INFO] 步骤1: 环境和依赖检查")
        print("="*50)

        start_time = time.time()

        try:
            # 检查核心依赖
            print("检查Python依赖包...")
            required_packages = ['cv2', 'PIL', 'numpy']
            missing_packages = []

            for package in required_packages:
                try:
                    if package == 'PIL':
                        __import__('PIL')
                    else:
                        __import__(package)
                    print(f"[OK] {package}")
                except ImportError:
                    print(f"[ERROR] {package} - 未安装")
                    missing_packages.append(package)

            if missing_packages:
                print(f"[ERROR] 缺少依赖包: {', '.join(missing_packages)}")
                duration = time.time() - start_time
                self._log_result("环境检查", "error", f"缺少依赖包: {', '.join(missing_packages)}", duration=duration)
                return False

            # 检查必要目录
            print("检查目录结构...")
            required_dirs = [
                self.paths['screenshots'],
                self.paths['base_equipment']
            ]

            for dir_path in required_dirs:
                if not dir_path.exists():
                    print(f"[ERROR] 目录不存在: {dir_path}")
                    duration = time.time() - start_time
                    self._log_result("环境检查", "error", f"目录不存在: {dir_path}", duration=duration)
                    return False
                else:
                    print(f"[OK] {dir_path}")

            # 检查是否有文件
            screenshot_files = list(self.paths['screenshots'].glob("*.png")) + \
                              list(self.paths['screenshots'].glob("*.jpg")) + \
                              list(self.paths['screenshots'].glob("*.jpeg"))

            base_files = list(self.paths['base_equipment'].glob("*.png")) + \
                        list(self.paths['base_equipment'].glob("*.jpg")) + \
                        list(self.paths['base_equipment'].glob("*.jpeg"))

            if not screenshot_files:
                print(f"[WARNING] {self.paths['screenshots']} 目录为空")
            else:
                print(f"[OK] 找到 {len(screenshot_files)} 个截图文件")

            if not base_files:
                print(f"[WARNING] {self.paths['base_equipment']} 目录为空")
            else:
                print(f"[OK] 找到 {len(base_files)} 个基准装备文件")

            duration = time.time() - start_time
            self._log_result("环境检查", "success", "环境检查通过", duration=duration)
            return True

        except Exception as e:
            duration = time.time() - start_time
            self._log_result("环境检查", "error", f"环境检查异常: {str(e)}", duration=duration)
            return False

    def step2_screenshot_cutting(self, auto_clean: bool = True) -> bool:
        """步骤2: 截图裁剪"""
        print("\n" + "="*50)
        print("[INFO] 步骤2: 游戏截图裁剪")
        print("="*50)

        start_time = time.time()

        # 自动清理输出目录
        if auto_clean:
            try:
                from src.utils.output_cleaner import clean_step_outputs
                print("清理步骤2的输出目录…")
                clean_step_outputs('cut', self.project_root)
                print("[OK] 清理完成")
            except ImportError:
                print("警告: 无法使用统一清理工具，将依赖模块内部清理")

        # 检查输入文件
        screenshot_files = list(self.paths['screenshots'].glob("*.png")) + \
                          list(self.paths['screenshots'].glob("*.jpg")) + \
                          list(self.paths['screenshots'].glob("*.jpeg"))

        if not screenshot_files:
            self._log_result("截图裁剪", "error", "未找到游戏截图文件")
            return False

        print(f"找到 {len(screenshot_files)} 个截图文件")

        # 运行裁剪模块
        success, output = self._run_module("step_tests/2_cut.py")

        duration = time.time() - start_time
        if success:
            # 统计输出文件数量
            crop_files = list(self.paths['equipment_crop'].glob("*.png")) + list(self.paths['equipment_crop'].glob("*.jpg"))
            transparent_files = list(self.paths['equipment_transparent'].glob("*.png"))

            self._log_result(
                "截图裁剪",
                "success",
                f"裁剪完成: 生成{len(crop_files)}个矩形图, {len(transparent_files)}个透明图",
                processed_count=len(crop_files) + len(transparent_files),
                duration=duration
            )
            return True
        else:
            self._log_result("截图裁剪", "error", f"裁剪失败: {output}", duration=duration)
            return False

    def step3_equipment_matching(self, auto_clean: bool = True) -> bool:
        """步骤3: 装备匹配（缓存优化版）"""
        print("\n" + "="*50)
        print("[INFO] 步骤3: 装备图片匹配（缓存优化版）")
        print("="*50)

        start_time = time.time()

        # 自动清理输出目录
        if auto_clean:
            try:
                from src.utils.output_cleaner import clean_step_outputs
                print("清理步骤3的输出目录…")
                clean_step_outputs('match', self.project_root)
                print("[OK] 清理完成")
            except ImportError:
                print("警告: 无法使用统一清理工具，将依赖模块内部清理")

        # 检查基准装备图片
        base_files = list(self.paths['base_equipment'].glob("*.png")) + \
                    list(self.paths['base_equipment'].glob("*.jpg")) + \
                    list(self.paths['base_equipment'].glob("*.jpeg"))

        if not base_files:
            self._log_result("装备匹配", "error", "未找到基准装备图片")
            return False

        # 检查裁剪后的装备图片
        equip_files = list(self.paths['equipment_transparent'].glob("*.png"))

        if not equip_files:
            self._log_result("装备匹配", "error", "未找到裁剪后的装备图片")
            return False

        print(f"找到 {len(base_files)} 个基准装备, {len(equip_files)} 个待匹配装备")
        print("使用装备匹配模块...")
        print("正在启动装备匹配模块，请稍候...")
        print("正在匹配中，请稍候...")

        # 运行装备匹配模块
        success, output = self._run_module("step_tests/3_match.py", [
            "--base-dir", str(self.paths['base_equipment']),
            "--compare-dir", str(self.paths['equipment_transparent']),
            "--output-dir", str(self.paths['matching_output'])
        ])

        duration = time.time() - start_time
        if success:
            # 查找生成的CSV文件（从output/matching目录）
            csv_files = list(self.paths['matching_output'].glob("*match*.csv"))
            self._log_result(
                "装备匹配",
                "success",
                f"匹配完成",
                processed_count=len(equip_files),
                output_files=[str(f) for f in csv_files],
                duration=duration
            )
            return True
        else:
            self._log_result("装备匹配", "error", f"匹配失败: {output}", duration=duration)
            return False

    def step4_ocr_recognition(self, auto_clean: bool = True) -> bool:
        """步骤4: OCR金额识别"""
        print("\n" + "="*50)
        print("[INFO] 步骤4: OCR金额识别")
        print("="*50)

        start_time = time.time()

        # 自动清理输出目录
        if auto_clean:
            try:
                from src.utils.output_cleaner import clean_step_outputs
                print("清理步骤4的输出目录…")
                clean_step_outputs('ocr', self.project_root)
                print("[OK] 清理完成")
            except ImportError:
                print("警告: 无法使用统一清理工具，将依赖模块内部清理")

        # 运行OCR模块
        success, output = self._run_module("step_tests/4_ocr.py")

        duration = time.time() - start_time
        if success:
            # 查找生成的OCR结果文件
            csv_files = list(self.paths['ocr_output'].glob("*.csv"))
            report_files = list(self.paths['ocr_output'].glob("report_*.txt"))

            self._log_result(
                "OCR识别",
                "success",
                f"OCR识别完成: 生成{len(csv_files)}个CSV文件, {len(report_files)}个报告文件",
                processed_count=len(csv_files),
                output_files=[str(f) for f in csv_files + report_files],
                duration=duration
            )
            return True
        else:
            self._log_result("OCR识别", "error", f"OCR识别失败: {output}", duration=duration)
            return False

    def generate_final_report(self) -> str:
        """生成最终处理报告"""
        print("\n" + "="*50)
        print("生成最终报告")
        print("="*50)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.paths['ocr_output'] / f"auto_processing_report_{timestamp}.txt"

        total_duration = time.time() - self.start_time if self.start_time else 0

        report_content = f"""
===========================================
自动化装备处理报告
===========================================

处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
总处理时长: {total_duration:.2f} 秒

处理步骤结果:
-------------------------------------------
"""

        success_count = 0
        total_processed = 0

        for result in self.results:
            status_icon = "[OK]" if result.status == "success" else "[WARNING]" if result.status == "warning" else "[ERROR]"
            report_content += f"{status_icon} {result.step}: {result.message}\n"
            if result.duration:
                report_content += f"   耗时: {result.duration:.2f}秒\n"
            if result.processed_count > 0:
                report_content += f"   处理数量: {result.processed_count}\n"
                total_processed += result.processed_count
            report_content += "\n"

            if result.status == "success":
                success_count += 1

        report_content += f"""
统计信息:
-------------------------------------------
成功步骤: {success_count}/{len(self.results)}
总处理数量: {total_processed}
成功率: {(success_count/len(self.results)*100):.1f}%

输出文件列表:
-------------------------------------------
"""

        # 收集所有输出文件
        all_output_files = []
        for result in self.results:
            all_output_files.extend(result.output_files)

        if all_output_files:
            for file_path in all_output_files:
                report_content += f"• {file_path}\n"
        else:
            report_content += "无输出文件\n"

        report_content += """
===========================================
处理完成!
===========================================
"""

        # 写入报告文件
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"[OK] 报告已生成: {report_file}")
        return str(report_file)

    def run_full_pipeline(self, auto_clean_steps: bool = True) -> bool:
        """运行完整的自动化处理流水线"""
        print("开始自动化装备处理流水线")
        print("="*60)

        self.start_time = time.time()

        # 如果启用了全局清理，先清理所有输出目录
        if auto_clean_steps:
            try:
                from src.utils.output_cleaner import clean_all_outputs
                print("\n[INFO] 清理所有输出目录…")
                clean_all_outputs(self.project_root)
                print("[OK] 全局清理完成")
            except ImportError:
                print("警告: 无法使用统一清理工具")

        # 执行所有步骤
        steps = [
            ("环境检查", self.step1_environment_check),
            ("截图裁剪", lambda: self.step2_screenshot_cutting(auto_clean=False)),  # 已经全局清理过了
            ("装备匹配", lambda: self.step3_equipment_matching(auto_clean=False)),
            ("OCR识别", lambda: self.step4_ocr_recognition(auto_clean=False))
        ]

        all_success = True

        for step_name, step_func in steps:
            try:
                success = step_func()
                if not success:
                    all_success = False
                    print(f"❌ {step_name}失败，终止处理")
                    break

                # 步骤间短暂暂停
                time.sleep(1)

            except KeyboardInterrupt:
                print(f"\n[WARNING] 用户中断了{step_name}")
                all_success = False
                break
            except Exception as e:
                print(f"[ERROR] {step_name}出现异常: {e}")
                all_success = False
                break

        # 生成最终报告
        final_report = self.generate_final_report()

        total_duration = time.time() - self.start_time

        print(f"\n{'='*60}")
        if all_success:
            print("[SUCCESS] 自动化处理完成! 所有步骤都成功执行")
        else:
            print("[WARNING] 自动化处理完成，但部分步骤失败")
        print(f"总耗时: {total_duration:.2f}秒")
        print(f"详细报告: {final_report}")
        print(f"{'='*60}")

        return all_success

def main():
    """主函数"""
    # Fix Windows console encoding
    import sys
    if sys.platform == 'win32':
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        elif hasattr(sys.stdout, 'buffer'):
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
    parser = argparse.ArgumentParser(description="自动化装备处理主控制器")
    parser.add_argument("--config", type=Path, help="配置文件路径")
    parser.add_argument("--step", choices=[1, 2, 3, 4], type=int, help="只执行指定步骤")
    parser.add_argument("--clean", action="store_true", help="清理之前的输出文件")

    args = parser.parse_args()

    # 创建处理器
    processor = AutoEquipmentProcessor(config_path=args.config)

    # 清理选项
    if args.clean:
        print("清理之前的输出文件...")
        for key, path in processor.paths.items():
            if key != 'screenshots' and key != 'base_equipment':
                if path.exists():
                    shutil.rmtree(path)
                    path.mkdir(parents=True, exist_ok=True)
        print("清理完成")

    try:
        if args.step:
            # 执行指定步骤
            step_methods = {
                1: processor.step1_environment_check,
                2: processor.step2_screenshot_cutting,
                3: processor.step3_equipment_matching,
                4: processor.step4_ocr_recognition
            }

            if args.step in step_methods:
                success = step_methods[args.step]()
                exit(0 if success else 1)
            else:
                print(f"❌ 无效步骤: {args.step}")
                exit(1)
        else:
            # 执行完整流水线
            success = processor.run_full_pipeline()
            exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n[WARNING] 用户中断了处理")
        exit(130)
    except Exception as e:
        print(f"[ERROR] 处理过程中发生异常: {e}")
        exit(1)

if __name__ == "__main__":
    main()