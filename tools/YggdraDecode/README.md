# YggdraDecode

Yggdra Union PC 版数据文件解密/打包工具。

原始项目: https://github.com/AdmiralCurtiss/YggdraDecode

本目录包含针对 Linux 适配的版本（将 Windows 特有的 `_fseeki64`/`_ftelli64` 替换为 POSIX 的 `fseeko`/`ftello`）。

## 编译 (Linux)

```bash
g++ -O2 -o yggdra_decode main.cpp md5.c -lz
```

## 编译 (Windows, MSVC)

使用 Visual Studio 打开原始项目的 .vcxproj 文件编译。

## 用法

```bash
# 解包
./yggdra_decode assets/data_tc.bin
# 输出到 assets/data_tc.bin.ex/

# 打包
./yggdra_decode assets/data_tc.bin.ex/data
# 输出到 assets/data_tc.bin.ex/data_new.bin
```

## 加密格式说明

### 外层结构 (data_tc.bin / data_sound.bin / data.bin)

```
[0..3]   InfoData 加密后大小 (uint32 LE)
[4..7]   内容数据总大小 (uint32 LE)
[8..]    加密的 InfoData
[8+N..]  加密的文件内容
```

### 加密方式

- **XOR 密钥生成**: `MD5(ROT13(filename))`，产生 16 字节密钥
- **XOR 加密**: 4 字节一组，循环使用密钥的 4 个 uint32
- **压缩**: zlib (deflate)，压缩数据前 4 字节为解压后大小

### InfoData 结构 (解密解压后)

```
[0..3]   文件表数据长度 (uint32 LE)
[4..7]   字符串表长度 (uint32 LE)
[8..]    文件表 (每条目 12 字节: nameOffset + length + dataOffset)
[...]    字符串表 (null-terminated UTF-8 文件名)
```

### 文件表条目 length 字段

- Bit 31: 是否为文件夹
- Bit 30: 是否已压缩
- Bit 0-29: 实际大小
