# LCF-DEIM 数据划分与复现材料

这里提供 VisDrone、UAVDT 和 CODrone 的九份训练、验证和测试参考清单，每份都有 CSV 和 TXT 两种格式。UAVDT 清单包含逐图序列编号，CODrone 清单包含逐图 64 位感知哈希和相似组编号。

**[浏览九份划分清单](./reproducibility/splits) · [查看三份完整 Python 脚本](./reproducibility/scripts) · [下载完整仓库 ZIP](https://github.com/GoCVPR/LCF-DEIM/archive/refs/heads/main.zip)**

数据划分采用固定随机种子 0。VisDrone 以单张图像为单位，UAVDT 以完整视频序列为单位，CODrone 以感知哈希相似组为单位。CODrone 的相似组由汉明距离不超过 10 的图像对通过连通关系构成。各图像的子集归属见相应清单。

公开清单供按第 3.1 节的划分方法开展复现实验。论文检测指标对应文中报告的实验划分。依赖版本和运行命令见 [复现指南](./reproducibility/README.md)。

The repository contains all nine reference image splits, per-image sequence or perceptual group identifiers, CODrone hashes, runnable scripts, source provenance and SHA-256 checksums. For command-line examples, open the [reproducibility guide](./reproducibility/README.md).
