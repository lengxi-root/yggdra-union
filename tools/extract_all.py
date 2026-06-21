#!/usr/bin/env python3
"""
extract_all.py - 一键提取 Yggdra Union 全部游戏资源

流程:
  1. 使用 YggdraDecode 解密解包 .bin 数据文件 (XOR + zlib)
  2. 使用 extract_pck.py 解包二级 .pck 打包文件
  3. 将最终资源文件整理到输出目录

前置条件:
  - 编译 YggdraDecode: cd tools/YggdraDecode && g++ -O2 -o ../../yggdra_decode main.cpp md5.c -lz
  - Python 3.6+

用法:
    python3 tools/extract_all.py [--decode-bin] [--extract-pck] [--all]

选项:
    --decode-bin   只执行第一步: 解密 .bin 文件
    --extract-pck  只执行第二步: 解包 .pck 文件并整理资源
    --all          执行全部步骤 (默认)
"""

import os
import subprocess
import sys
from pathlib import Path

# Import extract_pck from same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_pck import extract_pck


REPO_ROOT = Path(__file__).parent.parent
YGGDRA_DECODE = REPO_ROOT / 'yggdra_decode'
ASSETS_DIR = REPO_ROOT / 'assets'

# Map of source bin -> output directory name
DATA_FILES = {
    'data_tc.bin': 'data',          # 繁体中文版图片/UI/脚本
    'data_sound.bin': 'data_sound', # 全部音频资源
    'data.bin': 'data_jp',          # 日语版图片/动画/视频
    'data_en.bin': 'data_en',       # 英语版资源 (如果存在)
}


def decode_bin_files():
    """Step 1: Use YggdraDecode to decrypt and unpack .bin archives."""
    if not YGGDRA_DECODE.exists():
        print("Error: yggdra_decode binary not found.")
        print("Please compile it first:")
        print("  cd tools/YggdraDecode && g++ -O2 -o ../../yggdra_decode main.cpp md5.c -lz")
        sys.exit(1)

    for bin_name in DATA_FILES:
        bin_path = ASSETS_DIR / bin_name
        if not bin_path.exists():
            print(f"  Skipping {bin_name} (not found)")
            continue

        ex_path = bin_path.parent / f"{bin_name}.ex"
        if ex_path.exists():
            print(f"  Skipping {bin_name} (already extracted to {ex_path})")
            continue

        print(f"  Decrypting {bin_name}...")
        result = subprocess.run(
            [str(YGGDRA_DECODE), str(bin_path)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"    ERROR: {result.stderr}")
        else:
            print(f"    Done -> {ex_path}")


def extract_pck_and_organize():
    """Step 2: Extract .pck files and organize resources."""
    for bin_name, out_dir_name in DATA_FILES.items():
        ex_path = ASSETS_DIR / f"{bin_name}.ex" / "data"
        if not ex_path.exists():
            continue

        out_dir = REPO_ROOT / out_dir_name
        print(f"\n  Processing {bin_name} -> {out_dir_name}/")

        total_files = 0
        for root, dirs, files in os.walk(ex_path):
            for fname in sorted(files):
                fpath = os.path.join(root, fname)
                rel_path = os.path.relpath(fpath, ex_path)
                rel_dir = os.path.dirname(rel_path)

                if fname.endswith('.pck'):
                    pck_name = os.path.splitext(fname)[0]
                    pck_out_dir = os.path.join(str(out_dir), rel_dir, pck_name)
                    extracted = extract_pck(fpath, pck_out_dir)
                    total_files += len(extracted)
                    if extracted:
                        print(f"    Extracted {len(extracted)} files from {rel_path}")
                    else:
                        # Copy unextractable pck as-is
                        dest_dir = os.path.join(str(out_dir), rel_dir)
                        os.makedirs(dest_dir, exist_ok=True)
                        dest = os.path.join(dest_dir, fname)
                        with open(fpath, 'rb') as f_in:
                            with open(dest, 'wb') as f_out:
                                f_out.write(f_in.read())
                        total_files += 1
                else:
                    dest_dir = os.path.join(str(out_dir), rel_dir)
                    os.makedirs(dest_dir, exist_ok=True)
                    dest = os.path.join(dest_dir, fname)
                    with open(fpath, 'rb') as f_in:
                        with open(dest, 'wb') as f_out:
                            f_out.write(f_in.read())
                    total_files += 1

        print(f"    Total: {total_files} files")


def main():
    args = sys.argv[1:]
    do_all = not args or '--all' in args

    print("=== Yggdra Union Resource Extractor ===\n")

    if do_all or '--decode-bin' in args:
        print("[Step 1] Decrypting .bin data files...")
        decode_bin_files()

    if do_all or '--extract-pck' in args:
        print("\n[Step 2] Extracting .pck archives and organizing resources...")
        extract_pck_and_organize()

    print("\n=== Done! ===")


if __name__ == '__main__':
    main()
