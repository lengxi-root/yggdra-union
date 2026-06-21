#!/usr/bin/env python3
"""
extract_pck.py - 从 Yggdra Union 的 .pck 二级打包文件中提取资源

.pck 格式:
  [0..3]   文件数量 (uint32 LE)
  [4..7]   保留/对齐
  [8..]    文件条目表 (每条目 72 字节)
           - [0..63]  文件名 (UTF-8, null-terminated, 零填充)
           - [64..67] 文件大小 (uint32 LE)
           - [68..71] 数据偏移 (uint32 LE, 相对于文件开头)
  [...]    文件数据区

用法:
    python3 extract_pck.py <input.pck> [output_dir]
    python3 extract_pck.py --batch <directory>  # 递归提取目录下所有 .pck
"""

import os
import struct
import sys


def extract_pck(pck_path, output_dir):
    """Extract files from a .pck archive.
    
    Returns list of extracted file paths, or empty list if extraction failed.
    """
    with open(pck_path, 'rb') as f:
        data = f.read()

    if len(data) < 8:
        return []

    count = struct.unpack_from('<I', data, 0)[0]

    # Sanity checks
    if count == 0 or count > 10000:
        return []

    expected_header_size = 8 + count * 72
    if expected_header_size > len(data):
        return []

    os.makedirs(output_dir, exist_ok=True)
    extracted = []

    for i in range(count):
        entry_offset = 8 + i * 72
        name_bytes = data[entry_offset:entry_offset + 64]
        name = name_bytes.split(b'\x00')[0].decode('utf-8', errors='replace')
        size = struct.unpack_from('<I', data, entry_offset + 64)[0]
        file_offset = struct.unpack_from('<I', data, entry_offset + 68)[0]

        # Generate name for unnamed entries
        if not name:
            name = f'{i:03d}.bin'

        if file_offset + size > len(data):
            continue

        # Skip zero-size files
        if size == 0:
            continue

        file_data = data[file_offset:file_offset + size]
        out_path = os.path.join(output_dir, name)

        with open(out_path, 'wb') as f:
            f.write(file_data)
        extracted.append(out_path)

    return extracted


def batch_extract(base_dir, output_base=None):
    """Recursively find and extract all .pck files in a directory."""
    if output_base is None:
        output_base = base_dir

    total_files = 0
    total_pcks = 0

    for root, dirs, files in os.walk(base_dir):
        for fname in sorted(files):
            if not fname.endswith('.pck'):
                continue

            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, base_dir)
            rel_dir = os.path.dirname(rel_path)
            pck_name = os.path.splitext(fname)[0]
            out_dir = os.path.join(output_base, rel_dir, pck_name)

            extracted = extract_pck(fpath, out_dir)
            total_pcks += 1

            if extracted:
                total_files += len(extracted)
                print(f"  [{total_pcks}] {rel_path} -> {len(extracted)} files")
            else:
                print(f"  [{total_pcks}] {rel_path} -> FAILED (not a valid .pck or empty)")

    print(f"\nDone: {total_pcks} .pck files processed, {total_files} files extracted")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == '--batch':
        if len(sys.argv) < 3:
            print("Usage: extract_pck.py --batch <directory> [output_dir]")
            sys.exit(1)
        base_dir = sys.argv[2]
        output_base = sys.argv[3] if len(sys.argv) > 3 else None
        batch_extract(base_dir, output_base)
    else:
        pck_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(pck_path)[0]
        extracted = extract_pck(pck_path, output_dir)
        if extracted:
            print(f"Extracted {len(extracted)} files to {output_dir}")
        else:
            print(f"Failed to extract {pck_path}")
            sys.exit(1)


if __name__ == '__main__':
    main()
