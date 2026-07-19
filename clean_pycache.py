#!/usr/bin/env python3
"""
🧹 clean_pycache - Python 缓存清理工具
一键删除 __pycache__ 目录和 .pyc/.pyo 文件，带详细统计
"""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime


class Colors:
    """终端颜色"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    GRAY = '\033[90m'


def format_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB"]
    idx = 0
    size = float(size_bytes)
    while size >= 1024 and idx < len(units) - 1:
        size /= 1024
        idx += 1
    return f"{size:.2f} {units[idx]}"


def format_path(path, base_path):
    """格式化路径，显示相对路径"""
    try:
        rel = os.path.relpath(path, base_path)
        if len(rel) > 60:
            return "..." + rel[-57:]
        return rel
    except:
        return path


def print_header():
    """打印标题"""
    print()
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.CYAN}  🧹 Python 缓存清理工具{Colors.END}")
    print(f"{Colors.GRAY}  扫描目录: {os.path.abspath('.')}{Colors.END}")
    print(f"{Colors.GRAY}  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    print()


def print_section(title, icon="📁"):
    """打印分区标题"""
    print(f"{Colors.YELLOW}{icon} {title}{Colors.END}")
    print(f"{Colors.GRAY}{'-'*70}{Colors.END}")


def print_table_row(cols, widths, colors=None):
    """打印表格行"""
    if colors is None:
        colors = [Colors.END] * len(cols)
    line = ""
    for i, (col, width, color) in enumerate(zip(cols, widths, colors)):
        text = str(col)
        if len(text) > width:
            text = text[:width-3] + "..."
        line += f"{color}{text:<{width}}{Colors.END}"
    print(line)


def clean_pycache(path="."):
    """清理 __pycache__ 和 .pyc 文件"""

    print_header()

    base_path = os.path.abspath(path)

    # 统计数据结构
    pycache_dirs = []      # [(path, size)]
    pyc_files = []         # [(path, size)]
    errors = []            # [(path, error)]

    total_pycache_size = 0
    total_pyc_size = 0

    # ==================== 扫描阶段 ====================
    print_section("正在扫描...", "🔍")

    scanned_dirs = 0
    for root, dirs, files in os.walk(base_path):
        scanned_dirs += 1

        # 跳过 .venv 和 .git
        dirs[:] = [d for d in dirs if d not in ['.venv', '.git', '__pycache__', 'node_modules', '.fastapicloud']]

        # 收集 __pycache__
        pycache_path = os.path.join(root, "__pycache__")
        if os.path.exists(pycache_path) and os.path.isdir(pycache_path):
            try:
                size = get_dir_size(pycache_path)
                pycache_dirs.append((pycache_path, size))
                total_pycache_size += size
            except Exception as e:
                errors.append((pycache_path, str(e)))

        # 收集 .pyc / .pyo 文件
        for file in files:
            if file.endswith(".pyc") or file.endswith(".pyo"):
                filepath = os.path.join(root, file)
                try:
                    size = os.path.getsize(filepath)
                    pyc_files.append((filepath, size))
                    total_pyc_size += size
                except Exception as e:
                    errors.append((filepath, str(e)))

    print(f"  {Colors.GRAY}扫描了 {scanned_dirs} 个目录{Colors.END}")
    print(f"  {Colors.GREEN}发现 {len(pycache_dirs)} 个 __pycache__ 目录{Colors.END}")
    print(f"  {Colors.GREEN}发现 {len(pyc_files)} 个 .pyc/.pyo 文件{Colors.END}")
    print()

    # 如果没有发现，直接退出
    if not pycache_dirs and not pyc_files:
        print(f"{Colors.GREEN}✅ 未发现任何缓存文件，项目已清理！{Colors.END}")
        print()
        return

    # ==================== 删除 __pycache__ ====================
    if pycache_dirs:
        print_section(f"删除 __pycache__ 目录 ({len(pycache_dirs)} 个)", "🗑️")

        # 表头
        widths = [6, 50, 14]
        print_table_row(["序号", "路径", "大小"], widths, 
                        [Colors.GRAY, Colors.GRAY, Colors.GRAY])
        print(f"{Colors.GRAY}{'-'*70}{Colors.END}")

        deleted_count = 0
        for idx, (dirpath, size) in enumerate(pycache_dirs, 1):
            try:
                shutil.rmtree(dirpath)
                deleted_count += 1
                rel_path = format_path(dirpath, base_path)
                print_table_row(
                    [f"#{idx}", rel_path, format_size(size)],
                    widths,
                    [Colors.CYAN, Colors.END, Colors.YELLOW]
                )
            except Exception as e:
                errors.append((dirpath, str(e)))
                print_table_row(
                    [f"#{idx}", format_path(dirpath, base_path), "❌ 失败"],
                    widths,
                    [Colors.CYAN, Colors.RED, Colors.RED]
                )

        print(f"{Colors.GRAY}{'-'*70}{Colors.END}")
        print(f"  {Colors.GREEN}✓ 已删除 {deleted_count}/{len(pycache_dirs)} 个目录{Colors.END}")
        print(f"  {Colors.YELLOW}📦 释放空间: {format_size(total_pycache_size)}{Colors.END}")
        print()

    # ==================== 删除 .pyc 文件 ====================
    if pyc_files:
        print_section(f"删除 .pyc/.pyo 文件 ({len(pyc_files)} 个)", "🗑️")

        widths = [6, 50, 14]
        print_table_row(["序号", "路径", "大小"], widths,
                        [Colors.GRAY, Colors.GRAY, Colors.GRAY])
        print(f"{Colors.GRAY}{'-'*70}{Colors.END}")

        deleted_count = 0
        for idx, (filepath, size) in enumerate(pyc_files, 1):
            try:
                os.remove(filepath)
                deleted_count += 1
                rel_path = format_path(filepath, base_path)
                print_table_row(
                    [f"#{idx}", rel_path, format_size(size)],
                    widths,
                    [Colors.CYAN, Colors.END, Colors.YELLOW]
                )
            except Exception as e:
                errors.append((filepath, str(e)))
                print_table_row(
                    [f"#{idx}", format_path(filepath, base_path), "❌ 失败"],
                    widths,
                    [Colors.CYAN, Colors.RED, Colors.RED]
                )

        print(f"{Colors.GRAY}{'-'*70}{Colors.END}")
        print(f"  {Colors.GREEN}✓ 已删除 {deleted_count}/{len(pyc_files)} 个文件{Colors.END}")
        print(f"  {Colors.YELLOW}📦 释放空间: {format_size(total_pyc_size)}{Colors.END}")
        print()

    # ==================== 统计汇总 ====================
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.CYAN}  📊 清理统计报告{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    print()

    total_items = len(pycache_dirs) + len(pyc_files)
    total_size = total_pycache_size + total_pyc_size
    total_errors = len(errors)

    # 汇总表格
    summary_data = [
        ("📁 __pycache__ 目录", f"{len(pycache_dirs)} 个", format_size(total_pycache_size)),
        ("📄 .pyc/.pyo 文件", f"{len(pyc_files)} 个", format_size(total_pyc_size)),
        ("📊 合计", f"{total_items} 项", format_size(total_size)),
    ]

    if total_errors > 0:
        summary_data.append(("❌ 失败", f"{total_errors} 项", "-"))

    widths = [30, 20, 20]
    print_table_row(["类型", "数量", "占用空间"], widths,
                    [Colors.BOLD, Colors.BOLD, Colors.BOLD])
    print(f"{Colors.GRAY}{'-'*70}{Colors.END}")

    for item, count, size in summary_data:
        color = Colors.RED if "失败" in item else Colors.END
        print_table_row([item, count, size], widths, [color, color, Colors.YELLOW])

    print(f"{Colors.GRAY}{'-'*70}{Colors.END}")
    print()

    # 释放空间高亮
    print(f"  {Colors.GREEN}{'🎉 总计释放空间: ' + format_size(total_size):^66}{Colors.END}")
    print()

    # 错误信息
    if errors:
        print(f"{Colors.RED}⚠️  以下项目删除失败:{Colors.END}")
        for path, err in errors[:10]:
            print(f"  {Colors.RED}  • {format_path(path, base_path)}: {err}{Colors.END}")
        if len(errors) > 10:
            print(f"  {Colors.RED}  ... 还有 {len(errors)-10} 个错误{Colors.END}")
        print()

    # 底部信息
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.GRAY}  完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    print()


def get_dir_size(path):
    """递归计算目录大小"""
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += get_dir_size(entry.path)
    return total


if __name__ == "__main__":
    # 支持命令行参数指定目录
    target = sys.argv[1] if len(sys.argv) > 1 else "."

    if not os.path.exists(target):
        print(f"{Colors.RED}❌ 目录不存在: {target}{Colors.END}")
        sys.exit(1)

    clean_pycache(target)
