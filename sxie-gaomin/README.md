# LCF-DEIM

LCF-DEIM 自定义数据划分的参考清单与可运行脚本。完整数据包包含 VisDrone、UAVDT、CODrone 三套数据集的九份训练、验证和测试清单，每份提供 CSV 和 TXT 两种格式，同时提供逐图序列或相似组信息、CODrone 的 64 位感知哈希、数据来源、运行说明和 SHA-256 校验值。

**[下载完整复现材料 / Download reproducibility package](./LCF-DEIM-reproducibility.zip)**

解压后进入 `reproducibility/`，按其中的 `README.md` 运行。数据划分种子为 0。VisDrone 以单张静态图像为单位，UAVDT 按完整视频序列分配，CODrone 按 64 位感知哈希和汉明距离 ≤10 形成的相似组分配。

| 训练 / 验证 / 测试图像数 | 第 3.1 节报告的实验划分 | 此处发布的参考清单 |
|---|---:|---:|
| VisDrone | 6,903 / 863 / 863 | 6,903 / 863 / 863 |
| UAVDT | 62,375 / 7,612 / 7,832 | 63,292 / 9,003 / 5,524 |
| CODrone | 8,021 / 987 / 996 | 8,002 / 1,002 / 1,000 |

公开清单用于复现上表右列的参考划分。论文检测指标对应第 3.1 节报告的实验划分。采用本清单开展比较时，应使用同一训练、验证和测试集，并注明采用自定义划分。

The archive contains all nine reference split lists, the image inventory, per-image CODrone perceptual hashes and group IDs, runnable scripts, pinned dependencies, source provenance, and checksums. The reported paper metrics refer to the experimental splits in Section 3.1; the regenerated lists are separately identified above.
