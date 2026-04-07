#!/usr/bin/env python3
"""
测试运行脚本
提供便捷的测试执行入口

使用方法:
    python run_tests.py                    # 运行所有测试
    python run_tests.py inventory          # 运行台账模块测试
    python run_tests.py --verbose          # 详细输出模式
    python run_tests.py --html report.html # 生成 HTML 报告
"""
import argparse
import subprocess
import sys
from pathlib import Path


def run_tests(module: str = None, verbose: bool = False, html_report: str = None):
    """运行测试"""
    cmd = ["python", "-m", "pytest"]
    
    # 测试路径
    if module:
        test_path = f"tests/integration/api/test_{module}_api.py"
        if not Path(test_path).exists():
            print(f"❌ 测试文件不存在: {test_path}")
            print("可用的测试模块:")
            for f in Path("tests/integration/api").glob("test_*.py"):
                print(f"  - {f.stem.replace('test_', '')}")
            return 1
        cmd.append(test_path)
    else:
        cmd.append("tests/")
    
    # 详细输出
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-v")
    
    # 显示测试进度
    cmd.append("--tb=short")
    
    # HTML 报告
    if html_report:
        try:
            import pytest_html
            cmd.extend(["--html", html_report, "--self-contained-html"])
        except ImportError:
            print("⚠️  pytest-html 未安装，无法生成 HTML 报告")
            print("    安装: pip install pytest-html")
    
    print(f"\n🧪 运行命令: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="运行后端功能测试",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_tests.py                    # 运行所有测试
  python run_tests.py inventory          # 仅运行台账模块测试
  python run_tests.py --html report.html # 生成 HTML 测试报告
        """
    )
    
    parser.add_argument(
        "module",
        nargs="?",
        help="指定测试模块 (如: inventory, plan, sop_template)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="详细输出模式"
    )
    
    parser.add_argument(
        "--html",
        metavar="FILE",
        help="生成 HTML 测试报告"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有可用的测试"
    )
    
    args = parser.parse_args()
    
    # 列出可用测试
    if args.list:
        print("\n📋 可用的测试模块:")
        test_dir = Path("tests/integration/api")
        if test_dir.exists():
            for f in sorted(test_dir.glob("test_*.py")):
                module_name = f.stem.replace("test_", "").replace("_api", "")
                print(f"  • {module_name}")
        print()
        return 0
    
    # 运行测试
    return run_tests(args.module, args.verbose, args.html)


if __name__ == "__main__":
    sys.exit(main())
