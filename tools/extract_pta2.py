#!/usr/bin/env python3
"""
extract_pta2.py - 从 Yggdra Union 的 .pta2 精灵动画包中提取 PNG 图片

.pta2 格式:
  [0..3]   子文件数量 (uint32 LE)
  [4..7]   条目偏移起始 (uint32 LE, 通常=8)
  [8..]    子文件条目表 (每条目 72 字节)
           - [0..63]  文件名 (UTF-8, null-terminated)
           - [64..67] 文件大小 (uint32 LE)
           - [68..71] 数据偏移 (uint32 LE, 相对于文件开头)
  [...]    子文件数据区

每个 .pta2 通常包含:
  - .anm  动画帧序列定义
  - .pxb  像素缓冲区 (引擎原生格式)
  - .png  精灵图集 (可直接查看)

用法:
    python3 extract_pta2.py <input.pta2> [output_dir]
    python3 extract_pta2.py --batch <directory> [output_dir]
    python3 extract_pta2.py --png-only --batch <directory> [output_dir]

选项:
    --png-only  只提取 .png 文件 (默认)
    --all       提取所有子文件 (.anm, .pxb, .png)
    --batch     递归处理目录下所有 .pta2 文件
"""

import os
import struct
import sys


def extract_pta2(pta2_path, output_dir, png_only=True):
    """Extract files from a .pta2 archive.
    
    Returns list of extracted file paths.
    """
    with open(pta2_path, 'rb') as f:
        data = f.read()

    if len(data) < 8:
        return []

    count = struct.unpack_from('<I', data, 0)[0]

    if count == 0 or count > 100:
        return []

    os.makedirs(output_dir, exist_ok=True)
    extracted = []

    for i in range(count):
        entry_offset = 8 + i * 72
        if entry_offset + 72 > len(data):
            break

        name_bytes = data[entry_offset:entry_offset + 64]
        name = name_bytes.split(b'\x00')[0].decode('utf-8', errors='replace')
        size = struct.unpack_from('<I', data, entry_offset + 64)[0]
        file_offset = struct.unpack_from('<I', data, entry_offset + 68)[0]

        if not name:
            continue
        if file_offset + size > len(data):
            continue

        # Filter by extension if png_only
        if png_only and not name.lower().endswith('.png'):
            continue

        file_data = data[file_offset:file_offset + size]

        # Handle subdirectory in name (e.g. "00a\01Fencer.png")
        name = name.replace('\\', '/')
        out_path = os.path.join(output_dir, os.path.basename(name))

        with open(out_path, 'wb') as f:
            f.write(file_data)
        extracted.append(out_path)

    return extracted


def batch_extract(base_dir, output_base=None, png_only=True):
    """Recursively find and extract all .pta2 files."""
    if output_base is None:
        output_base = base_dir + '_sprites'

    total_files = 0
    total_pta2 = 0

    for root, dirs, files in os.walk(base_dir):
        for fname in sorted(files):
            if not fname.endswith('.pta2'):
                continue

            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, base_dir)
            rel_dir = os.path.dirname(rel_path)
            pta2_name = os.path.splitext(fname)[0]

            out_dir = os.path.join(output_base, rel_dir, pta2_name)
            extracted = extract_pta2(fpath, out_dir, png_only=png_only)
            total_pta2 += 1

            if extracted:
                total_files += len(extracted)
                print(f"  [{total_pta2}] {rel_path} -> {len(extracted)} files")

    print(f"\nDone: {total_pta2} .pta2 files processed, {total_files} images extracted")
    return total_files


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    png_only = True
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = [a for a in sys.argv[1:] if a.startswith('--')]

    if '--all' in flags:
        png_only = False

    if '--batch' in flags:
        if not args:
            print("Usage: extract_pta2.py --batch <directory> [output_dir]")
            sys.exit(1)
        base_dir = args[0]
        output_base = args[1] if len(args) > 1 else None
        batch_extract(base_dir, output_base, png_only=png_only)
    else:
        if not args:
            print("Usage: extract_pta2.py <input.pta2> [output_dir]")
            sys.exit(1)
        pta2_path = args[0]
        output_dir = args[1] if len(args) > 1 else os.path.splitext(pta2_path)[0]
        extracted = extract_pta2(pta2_path, output_dir, png_only=png_only)
        if extracted:
            print(f"Extracted {len(extracted)} files to {output_dir}")
            for f in extracted:
                print(f"  {f}")
        else:
            print(f"No files extracted from {pta2_path}")
            sys.exit(1)


if __name__ == '__main__':
    main()
