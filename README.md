# 图论研究 | Graph Theory Research

本仓库汇集图论手稿、反例和可复核运算。首版从最大度下的结构支配出发，并收录一个零强制计数反例。

The first release covers extremal structural domination under a maximum-degree bound and an explicit 396-vertex tree counterexample to a zero-forcing configuration counting conjecture.

## 首批成果 · First release

| 手稿 | 内容 | 复核材料 |
| --- | --- | --- |
| [诱导森林支配与二部支配的最大度极值常数及其精确通项](output/pdf/forest_bipartite_domination_theorem.pdf) | 对非空、无孤立顶点且最大度受限的有限简单图，两种支配约束共享的精确最坏比例和叶冠等号图。 | [Markdown](output/pdf/forest_bipartite_domination_theorem.md) · [计算复核](repro/domination/README.md) |
| [结构支配的转移原理、退化层级与性质夹逼定理](output/pdf/domination_transfer_hierarchy.pdf) | 将精确常数推广到诱导 k 退化支配，及介于 k 退化与禁 Kₖ₊₂ 之间的图性质。 | [扩展手稿](output/pdf/domination_transfer_hierarchy.md) · [计算复核](repro/domination/README.md) |
| [零强制二分配置计数猜想的 396 点树反例](output/pdf/zero-forcing-396-vertex-counterexample.pdf) | 一个显式树构造及直接计数下界，反驳手稿所述的配置计数上界。 | [证明、边表与核验命令](repro/zero-forcing/README.md) |

计算材料覆盖有限图、公式和反例证书。一般结论的证明见相应手稿。

## 研究索引和引用

- [全部研究方向与进度](research/README.md)
- [Lean 形式化仓库](https://github.com/shouanrenhechun/Myproofone) 包含最大度六的二部支配工程及独立的一般转移笔记。
- 引用时请写明手稿标题和所用的 [Release](https://github.com/shouanrenhechun/Graph/releases) 版本。仓库引用信息见 [CITATION.cff](CITATION.cff)。
