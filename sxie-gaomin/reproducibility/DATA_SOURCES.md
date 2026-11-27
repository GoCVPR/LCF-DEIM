# 数据来源及清单说明

`inventories/` 中的路径均以相应数据集的原始解压目录为根目录。路径内的 `train`、`val`、`test` 表示图像在数据发布包中的位置。此次参考划分的子集归属见 `splits/<数据集>/{train,val,test}.csv` 的 `split` 列。同目录 TXT 文件每行列出一个图像路径；CSV 保留必要的序列或相似组信息。

图像索引和 CODrone 分组表沿用[原参考版本](https://github.com/GoCVPR/LCF-DEIM/tree/51003459d90c8547dcc7c66f8866a2344b399586/sxie-gaomin/reproducibility)。各数据集的划分规则见[复现指南](README.md)。

## VisDrone

合并 VisDrone2019-DET 的官方 train、val 和 test-dev 子集，分别包含 6,471、548、1,610 张有标注图像，共 8,629 张；test-challenge 未纳入。核对了发布包中每个 JPG 与同名标注文件的对应关系。`inventories/visdrone.csv` 中的 `official_source_subset` 标识官方来源子集。参考划分以单张图像为单位。[数据集项目主页](https://github.com/VisDrone/VisDrone-Dataset)

| 实际读取的发布镜像 | 字节数 | 压缩包 SHA-256 |
|---|---:|---|
| [Train](https://github.com/ultralytics/assets/releases/download/v0.0.0/VisDrone2019-DET-train.zip) | 1,549,875,511 | `86a77eba93137bfc16e4993860de9245b0675c0dba0d3ab98fb458699e256f84` |
| [Val](https://github.com/ultralytics/assets/releases/download/v0.0.0/VisDrone2019-DET-val.zip) | 81,638,851 | `abeea063037e5d20398837deb11084e652402a34ddf4f207bdf541a6f2a35ef9` |
| [Test-dev](https://github.com/ultralytics/assets/releases/download/v0.0.0/VisDrone2019-DET-test-dev.zip) | 311,251,787 | `b28a94b06dfd9e36ce77ff8155fb82b9d2c030f198a76105933bd56c6ea6a68d` |

## UAVDT

采用 Dataset Ninja 发布的 Supervisely 版本。完整统计表列出 77,819 张图像，上游 train 和 test 目录分别有 24,143 和 53,676 张。发布者使用视频序列目录名写入图像的 `sequence` 标签，并以“序列目录名、下划线、原文件名”构造发布文件名。`inventories/uavdt.csv` 逐行列出图像相对路径和 `sequence_id`，覆盖 100 个序列。每个序列完整分配至同一参考子集。[Dataset Ninja 项目介绍](https://datasetninja.com/uavdt)

上游元数据固定在提交 `f098a6271af856444159c9e78002d97e3cb8b6b7`。完整逐图统计文件 SHA-256 为 `a72c0b9c2ec4d33ce0f5b306609777807331483ad7f759d2cab68c56d042e012`。[逐图统计表](https://github.com/dataset-ninja/uavdt/blob/f098a6271af856444159c9e78002d97e3cb8b6b7/stats/classes_per_image.json) · [转换代码](https://github.com/dataset-ninja/uavdt/blob/f098a6271af856444159c9e78002d97e3cb8b6b7/src/convert.py)

## CODrone

使用作者发布的 10,004 张原始 JPG。原始目录 train、val、test 分别含 5,002、2,000、3,002 张。解压后的 `CODrone/` 是图像相对路径的根目录。每张图像均有同名 DOTA 标注。参考分组使用原图像素，各来源子集的图像一起参与分组。[作者代码与数据入口](https://github.com/AHideoKuzeA/CODrone-A-Comprehensive-Oriented-Object-Detection-benchmark-for-UAV) · [作者发布的归档](https://drive.google.com/file/d/1FQ6mUaOr_kATDaH7N2bObD5SRRkV7qJy/view?usp=sharing)

`inventories/codrone.csv` 中的 `archive_crc32` 和 `uncompressed_bytes` 分别表示原 JPG 的 CRC32 和文件大小。二者均已逐图核对。`groups/codrone.csv` 列出同一批图像的 `phash64` 和 `group_id`，分组依据是 64 位感知哈希的汉明距离。请按文本读取校验值、哈希和组编号，以保留前导零。

| 核验对象 | SHA-256 |
|---|---|
| 官方 CODrone.zip（7,233,513,058 字节） | `3af9cf6deac09883c5643a8726f8a2a9bf820e244c639ac2ec9fd572789a4dc4` |
| 原始图像清单 | `607d38a27c2e0e08c68ad5b0d30f10fbe84df89d7ca3444181a6f673b297011c` |
| 本次计算的逐图哈希和组员表 | `1e35594b0af133e2ac5fd4ffbd3188880f38f7068020e0311d189c5839e5a262` |
