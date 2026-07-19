#!/usr/bin/env python3
"""
📁 dirsize - 项目目录结构及空间统计工具
自动读取 .gitignore（支持递归读取子目录），忽略匹配的文件/目录，输出美观的树形结构
"""

import os
import sys
import fnmatch
from pathlib import Path
from datetime import datetime


class Colors:
    """终端颜色"""
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    END = '\033[0m'


class GitIgnoreParser:
    """递归 .gitignore 解析器，支持子目录的 .gitignore"""

    def __init__(self, base_path):
        self.base = os.path.abspath(base_path)
        self.rules = []  # [(rel_prefix, is_negation, pattern, is_dir_only)]
        self._load_recursive(self.base, '')

    def _load_recursive(self, current_path, rel_prefix):
        """递归加载当前目录及所有子目录的 .gitignore"""
        gi_path = os.path.join(current_path, '.gitignore')
        if os.path.exists(gi_path):
            self._load_file(gi_path, rel_prefix)

        try:
            for entry in os.scandir(current_path):
                if entry.is_dir():
                    check_name = (rel_prefix + entry.name) if rel_prefix else entry.name
                    if self._check_ignored(check_name, is_dir=True):
                        continue

                    new_prefix = (rel_prefix + entry.name + '/') if rel_prefix else (entry.name + '/')
                    self._load_recursive(entry.path, new_prefix)
        except PermissionError:
            pass

    def _load_file(self, gitignore_path, rel_prefix):
        """加载单个 .gitignore 文件"""
        if not os.path.exists(gitignore_path):
            return

        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n').rstrip('\r')
                line = line.rstrip()
                if not line or line.startswith('#'):
                    continue

                negation = line.startswith('!')
                if negation:
                    line = line[1:]

                is_dir_only = line.endswith('/')
                if is_dir_only:
                    line = line[:-1]

                self.rules.append((rel_prefix, negation, line, is_dir_only))

    def is_ignored(self, rel_path, is_dir=False):
        """判断相对路径是否被忽略（考虑所有 .gitignore 规则）"""
        rel_path = rel_path.replace(os.sep, '/')
        ignored = False

        for prefix, negation, pattern, dir_only in self.rules:
            if prefix and not rel_path.startswith(prefix):
                continue

            if dir_only and not is_dir:
                continue

            check_path = rel_path[len(prefix):] if prefix else rel_path

            if self._match(check_path, pattern):
                ignored = not negation

        return ignored

    def _check_ignored(self, rel_path, is_dir=False):
        """内部检查，用于递归时判断是否跳过子目录"""
        return self.is_ignored(rel_path, is_dir)

    def _match(self, rel_path, pattern):
        """匹配逻辑"""
        if pattern.startswith('/'):
            pattern = pattern[1:]
            if rel_path == pattern or rel_path.startswith(pattern + '/'):
                return True
            return False

        if '/' in pattern:
            if fnmatch.fnmatch(rel_path, pattern):
                return True
            if rel_path.endswith('/' + pattern) or rel_path == pattern:
                return True
            return False

        basename = os.path.basename(rel_path)
        if fnmatch.fnmatch(basename, pattern):
            return True

        parts = rel_path.split('/')
        for part in parts:
            if fnmatch.fnmatch(part, pattern):
                return True

        return False


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


def get_dir_size(path, gitignore=None, base_path=None):
    """递归计算目录总大小（支持 gitignore 过滤）"""
    total = 0
    try:
        for entry in os.scandir(path):
            if gitignore and base_path:
                rel = os.path.relpath(entry.path, base_path).replace(os.sep, '/')
                if entry.is_dir():
                    if gitignore.is_ignored(rel, is_dir=True):
                        continue
                    total += get_dir_size(entry.path, gitignore, base_path)
                else:
                    if gitignore.is_ignored(rel, is_dir=False):
                        continue
                    total += entry.stat().st_size
            else:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += get_dir_size(entry.path)
    except PermissionError:
        pass
    return total


def count_files(path, gitignore=None, base_path=None):
    """递归计算目录下文件数量（支持 gitignore 过滤）"""
    count = 0
    try:
        for entry in os.scandir(path):
            if gitignore and base_path:
                rel = os.path.relpath(entry.path, base_path).replace(os.sep, '/')
                if entry.is_dir():
                    if gitignore.is_ignored(rel, is_dir=True):
                        continue
                    count += count_files(entry.path, gitignore, base_path)
                else:
                    if gitignore.is_ignored(rel, is_dir=False):
                        continue
                    count += 1
            else:
                if entry.is_file():
                    count += 1
                elif entry.is_dir():
                    count += count_files(entry.path)
    except PermissionError:
        pass
    return count


def scan_directory(base_path, gitignore, prefix="", is_last=True):
    """扫描目录，返回树形结构数据（目录大小通过子项累加，不重复计算）"""
    items = []

    try:
        entries = list(os.scandir(base_path))
    except PermissionError:
        return items

    dirs = []
    files = []
    for entry in entries:
        rel = os.path.relpath(entry.path, gitignore.base).replace(os.sep, '/')

        if entry.is_dir():
            if gitignore.is_ignored(rel, is_dir=True):
                continue
            dirs.append(entry)
        else:
            if gitignore.is_ignored(rel, is_dir=False):
                continue
            files.append(entry)

    dirs.sort(key=lambda e: e.name.lower())
    files.sort(key=lambda e: e.name.lower())

    all_entries = dirs + files

    for idx, entry in enumerate(all_entries):
        is_last_item = idx == len(all_entries) - 1

        if entry.is_dir():
            # 递归扫描子目录
            sub_items = scan_directory(entry.path, gitignore, prefix + ("    " if is_last else "│   "), is_last_item)
            # 目录大小 = 所有子项累加（不重复调用 get_dir_size）
            size = sum(item.get('size', 0) for item in sub_items)
            file_count = sum(1 for item in sub_items if item['type'] == 'file')
            file_count += sum(item.get('count', 0) for item in sub_items if item['type'] == 'dir')
            items.append({
                'type': 'dir',
                'name': entry.name,
                'size': size,
                'count': file_count,
                'prefix': prefix,
                'is_last': is_last_item,
                'children': sub_items
            })
        else:
            try:
                size = entry.stat().st_size
            except:
                size = 0
            items.append({
                'type': 'file',
                'name': entry.name,
                'size': size,
                'prefix': prefix,
                'is_last': is_last_item
            })

    return items


def print_tree(items, parent_prefix=""):
    """打印树形结构"""
    for idx, item in enumerate(items):
        is_last = item['is_last']
        connector = "└── " if is_last else "├── "

        if item['type'] == 'dir':
            name = f"{Colors.CYAN}{Colors.BOLD}{item['name']}/{Colors.END}"
            size_str = f"{Colors.YELLOW}{format_size(item['size']):>10}{Colors.END}"
            count_str = f"{Colors.GRAY}({item['count']} files){Colors.END}"
            print(f"{parent_prefix}{connector}{name}  {size_str}  {count_str}")

            child_prefix = parent_prefix + ("    " if is_last else "│   ")
            print_tree(item['children'], child_prefix)
        else:
            name = f"{Colors.END}{item['name']}{Colors.END}"
            size_str = f"{Colors.GREEN}{format_size(item['size']):>10}{Colors.END}"
            print(f"{parent_prefix}{connector}{name}  {size_str}")


def print_summary(total_size, total_files, total_dirs, ignored_size, ignored_dirs, ignored_files, base_path):
    """打印汇总统计"""
    print()
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.CYAN}{'📊 统计汇总':^70}{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    print()

    raw_total = get_dir_size(base_path)  # 不过滤，包含所有文件

    data = [
        ("📁 目录数", f"{total_dirs} 个", ""),
        ("📄 文件数", f"{total_files} 个", ""),
        ("📦 统计大小", format_size(total_size), f"{Colors.YELLOW}"),
        ("🗑️  忽略大小", format_size(ignored_size), f"{Colors.GRAY}"),
        ("💾 项目总大小", format_size(raw_total), f"{Colors.GREEN}{Colors.BOLD}"),
    ]

    for label, value, color in data:
        padding = 66 - len(label) - len(value)
        print(f"  {label}{' ' * padding}{color}{value}{Colors.END}")

    print()

    if ignored_dirs or ignored_files:
        print(f"  {Colors.GRAY}被 .gitignore 忽略的项目:{Colors.END}")
        for d in ignored_dirs[:5]:
            print(f"    {Colors.GRAY}  📁 {d}{Colors.END}")
        for f in ignored_files[:5]:
            print(f"    {Colors.GRAY}  📄 {f}{Colors.END}")
        remaining = max(0, len(ignored_dirs) + len(ignored_files) - 10)
        if remaining > 0:
            print(f"    {Colors.GRAY}  ... 还有 {remaining} 项{Colors.END}")
        print()

    print(f"{Colors.CYAN}{'='*70}{Colors.END}")


def collect_stats(items):
    """收集统计数据"""
    total_size = 0
    total_files = 0
    total_dirs = 0

    for item in items:
        if item['type'] == 'dir':
            total_dirs += 1
            total_size += item['size']
            f, d = collect_stats_files_dirs(item['children'])
            total_files += f
            total_dirs += d
        else:
            total_files += 1
            total_size += item['size']

    return total_size, total_files, total_dirs


def collect_stats_files_dirs(items):
    """只收集文件数和目录数"""
    files = 0
    dirs = 0
    for item in items:
        if item['type'] == 'dir':
            dirs += 1
            f, d = collect_stats_files_dirs(item['children'])
            files += f
            dirs += d
        else:
            files += 1
    return files, dirs


def find_ignored(base_path, gitignore):
    """找出被忽略的项目（用于展示）"""
    ignored_dirs = []
    ignored_files = []

    for root, dirs, files in os.walk(base_path):
        rel_root = os.path.relpath(root, base_path).replace(os.sep, '/')
        if rel_root == '.':
            rel_root = ''

        for d in dirs:
            rel = (rel_root + '/' + d).lstrip('/') if rel_root else d
            if gitignore.is_ignored(rel, is_dir=True):
                ignored_dirs.append(rel)

        for f in files:
            rel = (rel_root + '/' + f).lstrip('/') if rel_root else f
            if gitignore.is_ignored(rel, is_dir=False):
                ignored_files.append(rel)

    return ignored_dirs, ignored_files


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    base_path = os.path.abspath(target)

    if not os.path.exists(base_path):
        print(f"{Colors.RED}❌ 目录不存在: {target}{Colors.END}")
        sys.exit(1)

    if not os.path.isdir(base_path):
        print(f"{Colors.RED}❌ 不是目录: {target}{Colors.END}")
        sys.exit(1)

    # 解析 .gitignore（递归读取所有子目录）
    gitignore = GitIgnoreParser(base_path)

    # 打印头部
    print()
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.CYAN}{'📁 项目目录结构统计':^70}{Colors.END}")
    print(f"{Colors.GRAY}{'  路径: ' + base_path:^70}{Colors.END}")
    print(f"{Colors.GRAY}{'  时间: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^70}{Colors.END}")
    if gitignore.rules:
        print(f"{Colors.GRAY}{'  已读取 .gitignore (' + str(len(gitignore.rules)) + ' 条规则)':^70}{Colors.END}")
    else:
        print(f"{Colors.GRAY}{'  未找到 .gitignore':^70}{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    print()

    # 扫描
    print(f"{Colors.YELLOW}🔍 正在扫描...{Colors.END}")
    items = scan_directory(base_path, gitignore)

    # 找出被忽略的项
    ignored_dirs, ignored_files = find_ignored(base_path, gitignore)
    ignored_dirs = list(dict.fromkeys(ignored_dirs))[:20]
    ignored_files = list(dict.fromkeys(ignored_files))[:20]

    # 计算忽略大小（通过过滤 vs 不过滤的差异）
    filtered_size = get_dir_size(base_path, gitignore, base_path)
    raw_total = get_dir_size(base_path)
    ignored_size = raw_total - filtered_size

    print(f"  {Colors.GREEN}✓ 扫描完成{Colors.END}")
    print()

    # 打印树
    root_name = os.path.basename(base_path) or base_path
    filtered_files = count_files(base_path, gitignore, base_path)
    _, _, total_dirs = collect_stats(items)
    # total_dirs 已由 collect_stats 获取

    print(f"{Colors.CYAN}{Colors.BOLD}{root_name}/{Colors.END}  {Colors.YELLOW}{format_size(filtered_size):>10}{Colors.END}  {Colors.GRAY}({filtered_files} files){Colors.END}")
    print_tree(items)

    # 打印汇总
    print_summary(filtered_size, filtered_files, total_dirs, ignored_size, ignored_dirs, ignored_files, base_path)


if __name__ == "__main__":
    main()
