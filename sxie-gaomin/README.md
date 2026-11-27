# LCF-DEIM 数据划分与复现材料

这里提供 VisDrone、UAVDT 和 CODrone 的训练、验证和测试参考清单。TXT 每行列出一个图像路径。CSV 还记录子集归属，并提供 UAVDT 的序列编号和 CODrone 的相似组编号及 64 位感知哈希。

[划分清单](./reproducibility/splits) · [Python 脚本](./reproducibility/scripts) · [下载 ZIP](https://github.com/GoCVPR/LCF-DEIM/archive/refs/heads/main.zip)

VisDrone 按图像划分，UAVDT 按视频序列划分，CODrone 按感知哈希相似组划分。每个 UAVDT 序列或 CODrone 相似组中的图像都归入同一子集。初始划分使用随机种子 0。初分后的分组规则和运行命令见[复现指南](./reproducibility/README.md)。

The [reproducibility guide](./reproducibility/README.md) lists the data sources, split rules, and commands for generating the reference manifests.
