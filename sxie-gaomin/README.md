# LCF-DEIM 数据划分与复现材料

这里提供 VisDrone、UAVDT 和 CODrone 的九份训练、验证和测试参考清单，每份都有 CSV 和 TXT 两种格式。UAVDT 清单包含逐图序列编号，CODrone 清单包含逐图 64 位感知哈希和相似组编号。

**[浏览九份划分清单](./reproducibility/splits) · [查看三份完整 Python 脚本](./reproducibility/scripts) · [下载完整仓库 ZIP](https://github.com/GoCVPR/LCF-DEIM/archive/refs/heads/main.zip)**

| 数据集 | 第 3.1 节报告的实验划分（训练 / 验证 / 测试） | 此处发布的参考清单（训练 / 验证 / 测试） |
|---|---:|---:|
| VisDrone | 6,903 / 863 / 863 | 6,903 / 863 / 863 |
| UAVDT | 62,375 / 7,612 / 7,832 | 63,292 / 9,003 / 5,524 |
| CODrone | 8,021 / 987 / 996 | 8,002 / 1,002 / 1,000 |

完整运行说明和依赖版本见 [reproducibility/README.md](./reproducibility/README.md)。数据划分随机种子为 0。VisDrone 按单张图像划分，UAVDT 按完整视频序列划分，CODrone 按基于汉明距离 ≤10 的感知哈希相似组划分。论文检测指标对应第 3.1 节报告的实验划分。新实验应注明所用的具体清单。

The repository contains all nine reference image splits, per-image sequence or perceptual group identifiers, CODrone hashes, runnable scripts, source provenance and SHA-256 checksums. For command-line examples, open the [reproducibility guide](./reproducibility/README.md).
