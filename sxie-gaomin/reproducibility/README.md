# LCF-DEIM 数据划分与复现材料

本目录提供根据公开图像索引重建的训练、验证和测试参考清单。VisDrone 的划分单元是单张有标注图像，UAVDT 是完整视频序列，CODrone 是感知哈希相似组。三个数据集的初分种子均为 0，划分单元的目标比例为 8∶1∶1。

## 获取具体清单

下表的数字为 CSV 中的图像行数。每个子集提供一份 CSV 和一份 TXT。CSV 的 `image` 列保存数据集根目录下的相对路径，`split` 列保存实际子集。文件路径中原有的 train、val 或 test 是上游来源目录。TXT 每行对应一张图像。

| 数据集 | 训练集 | 验证集 | 测试集 | CSV 中的附加信息 |
|---|---|---|---|---|
| VisDrone | [6,903](splits/visdrone/train.csv) | [863](splits/visdrone/val.csv) | [863](splits/visdrone/test.csv) | 单张图像对应一行 |
| UAVDT | [62,375](splits/uavdt/train.csv) | [7,612](splits/uavdt/val.csv) | [7,832](splits/uavdt/test.csv) | 序列编号 `sequence_id` |
| CODrone | [8,021](splits/codrone/train.csv) | [987](splits/codrone/val.csv) | [996](splits/codrone/test.csv) | 相似组 `group_id`、16 位十六进制 `phash64` |

- 数据集版本、官方来源和原始图像索引见 [DATA_SOURCES.md](DATA_SOURCES.md)。
- 逐图哈希和分组结果见 [groups/codrone.csv](groups/codrone.csv)。组编号从 G000001 开始，同组图像完整归入一个子集。
- 划分种子和取整方式见 [protocol.json](protocol.json)。已发布文件的 SHA-256 值见 [SHA256SUMS](SHA256SUMS)。

## 复算九份清单

在本目录内运行。参考环境为 CPython 3.8.20。仅从现有索引和组表重新划分时，`make_splits.py` 只使用 Python 标准库。输出目录使用未占用的新名称。

```bash
python scripts/make_splits.py visdrone inventories/visdrone.csv out/visdrone
python scripts/make_splits.py uavdt inventories/uavdt.csv out/uavdt
python scripts/make_splits.py codrone groups/codrone.csv out/codrone
```

三个数据集分别对按字符串升序排列的图像路径、序列编号或组编号调用 `random.Random(0).shuffle`。对于 N 个划分单元，取 ⌊8N/10⌋、⌊9N/10⌋ 为累计切点，得到初始子集。论文表 2 和表 3 中用于重复训练的种子 1、2 不参与数据划分。

| 数据集 | 种子 0 初分图像数（训练／验证／测试） | 最终图像数（训练／验证／测试） | 各子集划分单元数（训练／验证／测试） |
|---|---|---|---|
| VisDrone | 6,903／863／863 | 6,903／863／863 | 6,903／863／863 张图像 |
| UAVDT | 63,292／9,003／5,524 | 62,375／7,612／7,832 | 80／10／10 个序列 |
| CODrone | 8,002／1,002／1,000 | 8,021／987／996 | 7,898／987／988 个相似组 |

VisDrone 沿用[初分清单](https://github.com/GoCVPR/LCF-DEIM/tree/51003459d90c8547dcc7c66f8866a2344b399586/sxie-gaomin/reproducibility/splits)。UAVDT 的调整以完整序列为单位，序列编号及其初始、最终子集列在[划分脚本](scripts/make_splits.py)的 `UAVDT_MOVES` 中。CODrone 按打乱后的组顺序，先将验证集的 15 个双图组与训练集的 15 个单图组交换，再以同样方式交换测试集的 4 个双图组与训练集的 4 个单图组。各子集的序列数或相似组数保持不变。

脚本核对各子集的图像数和划分单元数，再按图像路径排序写出 CSV 和 TXT。

## 从官方 CODrone 原图复算感知哈希

`DATA/CODrone` 指解压后直接含 train、val 和 test 文件夹的目录。用源清单生成分组表后，可将新表作为划分脚本的输入。

```bash
python -m pip install -r requirements.txt
python scripts/group_codrone.py --root DATA/CODrone --inventory inventories/codrone.csv --out out/codrone_groups.csv
python scripts/make_splits.py codrone out/codrone_groups.csv out/codrone_from_pixels
```

脚本先核对官方 JPG 的字节数和 CRC32，再使用 ImageHash 的 DCT 感知哈希。原图转为灰度、缩放到 32×32，取二维 DCT 的左上 8×8 系数（含直流项），以中位数二值化，形成 64 位哈希。对全部官方来源子集共同检索，将汉明距离 ≤10 的图像对连边，每个连通分量形成一个相似组。连通关系可以传递。组数由原图和上述规则决定，种子仅用于打乱已经形成的组。三份 CODrone 清单中，汉明距离不超过 10 的 133 对图像均位于同一子集。该统计以图像哈希为依据。

## 转换 CODrone 四点框标注

```bash
python scripts/convert_codrone_boxes.py DATA/CODrone splits/codrone/train.csv out/annotations_train.json
python scripts/convert_codrone_boxes.py DATA/CODrone splits/codrone/val.csv out/annotations_val.json
python scripts/convert_codrone_boxes.py DATA/CODrone splits/codrone/test.csv out/annotations_test.json
```

转换脚本从原图对应的 DOTA 标注读取四个顶点，以各轴最小值和最大值生成 COCO 水平框 `[xmin, ymin, width, height]`。有效目标写入 `annotations`，忽略区域的坐标单列于 `codrone_ignored_regions`，零宽或零高框的源记录保存在 `codrone_degenerate_regions`。所有图像均列入输出。原数据的 12 个前景类别与 ignored 区域分别处理。使用已有模型的类别编号时，通过 `--categories` 传入该模型的 COCO 类别数组。训练和评估程序若需屏蔽忽略区域内的背景损失或预测，应读取上述区域字段；标准 COCOeval 不会自动处理该扩展字段。

这些清单均属于自定义划分。在引用检测结果时，请同时标明划分和标注形式，尤其应区分 CODrone 水平框与原基准旋转框评估。
