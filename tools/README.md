# 逆向工具 / Reverse Engineering Tools

本目录包含 Yggdra Union PC 版游戏资源的逆向提取工具。

## 快速开始

```bash
# 1. 编译解密工具
cd tools/YggdraDecode
g++ -O2 -o ../../yggdra_decode main.cpp md5.c -lz
cd ../..

# 2. 一键提取全部资源
python3 tools/extract_all.py
```

## 工具说明

| 工具 | 用途 |
|------|------|
| `YggdraDecode/` | 解密/打包 .bin 数据文件（XOR+zlib加密） |
| `extract_pck.py` | 解包 .pck 二级打包文件 |
| `extract_all.py` | 一键提取全部资源（调用以上两个工具） |

## 游戏数据文件

| 文件 | 内容 | 大小 |
|------|------|------|
| `assets/data_tc.bin` | 繁体中文版图片/UI/脚本 | 49MB |
| `assets/data_sound.bin` | 全部音频（BGM/SE/语音） | 253MB |
| `assets/data.bin` | 日语版图片/动画/视频 | 196MB |
| `assets/data_en.bin` | 英语版资源 | 36MB |

## 提取结果目录

| 目录 | 来源 | 文件数 |
|------|------|--------|
| `data/` | data_tc.bin | 2187 |
| `data_sound/` | data_sound.bin | 12411 |
| `data_jp/` | data.bin | 2747 |
