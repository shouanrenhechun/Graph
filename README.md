# 图论研究 | Graph Theory Research

本仓库收录图论手稿、显式反例和计算复核材料。[首个发布版本 `v0.1.0`](https://github.com/shouanrenhechun/Graph/releases/tag/v0.1.0) 聚焦两个问题。第一，在最大度受限的图中，要求支配集诱导森林或二部图，最坏情况下要选多大比例的顶点？第二，零强制二分配置的计数上界 `8^(n/2)` 是否对所有图成立？

The first release determines sharp worst-case ratios for induced forest and bipartite domination under a maximum-degree bound, extends the result to induced degeneracy and related graph properties, and gives a 396-vertex tree counterexample to a zero-forcing configuration counting conjecture. It includes manuscripts, scripts, and machine-readable records. A companion Lean repository covers the case of maximum degree at most six.

## 阅读入口

| 成果 | 建议从这里开始 | 复核材料 |
| --- | --- | --- |
| 诱导森林支配与二部支配的精确常数 | [PDF](output/pdf/forest_bipartite_domination_theorem.pdf) · [Markdown](output/pdf/forest_bipartite_domination_theorem.md) | [二部支配记录](repro/domination/general_cn_results.json) · [森林支配记录](repro/domination/acyclic_results.json) |
| 结构支配转移原理、退化层级与性质夹逼 | [PDF](output/pdf/domination_transfer_hierarchy.pdf) · [含附录的扩展手稿](output/pdf/domination_transfer_hierarchy.md) | [一般转移与公式记录](repro/domination/output/pdf/domination_chain_checks.json) · [等号条件复核记录](repro/domination/equality/domination_equality_checks.json) |
| 零强制二分配置计数的 396 点树反例 | [PDF](output/pdf/zero-forcing-396-vertex-counterexample.pdf) · [直接计数证明](repro/zero-forcing/counterexample_proof.md) | [边表和整数证书](repro/zero-forcing/counterexample_certificate.json) · [核验说明](repro/zero-forcing/README.md) |

## 1. 最大度下的森林支配与二部支配

设 $G$ 是非空、无孤立顶点的有限简单图。若每个 $D$ 外的顶点都在 $D$ 中有邻点，则 $D$ 是支配集。要求诱导子图 $G[D]$ 为森林或二部图，分别得到森林支配数 $\gamma_{\mathrm{acyclic}}(G)$ 和二部支配数 $\gamma_{\mathrm{bip}}(G)$。两者都是满足相应条件的支配集的最小大小。

对固定的整数 $\Delta\ge 1$，在所有最大度至多 $\Delta$ 的上述图上取支配数与顶点数之比的上确界，得到对应的极值常数。两种约束共享同一常数。对 $\Delta\ge 4$，精确值为

$$
C_\Delta=
\max_{a\in\{1,\ldots,\Delta-2\}}
\frac{2+a(\Delta-a-1)}{(\Delta-a+1)(a+1)}.
$$

当 $\Delta=1,2,3$ 时，常数为 $1/2$。上式中的一个最优整数参数可以直接取为

$$
a_\Delta=\left\lceil
\frac{\sqrt{8\Delta(\Delta-2)+1}-2\Delta+1}{2}
\right\rceil.
$$

这里 $\operatorname{cor}(K_m,a)$ 表示给完全图 $K_m$ 的每个顶点各接上 $a$ 个专属叶子。取 $m=\Delta-a+1$ 和任一个最优 $a$，叶冠图同时达到两种支配约束的极值。限制图连通，或要求最大度恰为 $\Delta$，常数仍相同。

| 最大度上界 $\Delta$ | 最优 $a$ | 精确常数 | 一个等号图 |
| ---: | ---: | ---: | --- |
| 4 | 1 | $1/2$ | $\operatorname{cor}(K_4,1)$ |
| 5 | 1 或 2 | $1/2$ | $\operatorname{cor}(K_5,1)$ |
| 6 | 2 | $8/15$ | $\operatorname{cor}(K_5,2)$ |
| 8 | 3 | $7/12$ | $\operatorname{cor}(K_6,3)$ |
| 10 | 4 | $22/35$ | $\operatorname{cor}(K_7,4)$ |
| 12 | 4 或 5 | $2/3$ | $\operatorname{cor}(K_9,4)$ |

极值相等仍允许单张图上的参数不同。例如，给四圈的每个顶点各接两个专属叶子得到的图，二部支配数为 4，森林支配数为 5。若原图有 $h$ 个孤立顶点，任何支配集都须选这 $h$ 个点，上界相应为 $h+C_\Delta(\lvert V(G)\rvert-h)$。这些例子及低度数情形见[手稿第 6 至 7 节](output/pdf/forest_bipartite_domination_theorem.md)。

## 2. 退化层级与性质夹逼

若一张图的每个非空诱导子图都有一个度数至多 $k$ 的顶点，则称它为 $k$ 退化。要求支配集诱导 $k$ 退化图时，在同一最大度图类上的精确极值常数为

$$
C_{\Delta,k}=
\max\left\{\frac12,\;
\max_{1\le a\le\Delta-k-1}
\frac{k+1+a(\Delta-a-k)}{(\Delta-a+1)(a+1)}
\right\}.
$$

内层只取整数 $a$。范围为空时只保留 $1/2$。常数恰为 $1/2$ 当且仅当 $\Delta\le 2k+3$。同一常数也适用于包含所有 $k$ 退化图、且其成员都不含 $K_{k+2}$ 的图性质，例如 $(k+1)$ 可着色。取 $k=0$ 得到独立支配的情形，取 $k=1$ 得到森林、二部和无三角形三种支配约束的共同极值。

证明的上界和下界有四个主要步骤。

1. 由最大匹配构造支配核心 $C$，将每个核心外顶点唯一分配给某个相邻的核心顶点，每个核心顶点至少获得一个分配点。
2. 将获得 $a_v$ 个分配点的核心顶点 $v$ 赋权 $a_v-1$。随机排列核心顶点，选取至多有 $k$ 个邻点排在自身之前的顶点，得到加权的诱导 $k$ 退化选择下界。
3. 将所选顶点扩充为支配核心的集合，再在尚未覆盖的外部顶点中取极大独立集。核心与补全集合之间无边，因此可用同一套局部预算控制支配集大小。
4. 用完全图叶冠给出紧的下界。若每个核心有 $a$ 个叶子，任取一个未入选的核心，它的所有专属叶子都必须入选。这将下界化为有限的整数优化。

[扩展手稿](output/pdf/domination_transfer_hierarchy.md)还给出最优整数参数、固定 $k$ 的渐近式以及等号和稳定性附录。[半数范围研究稿](output/pdf/domination_half_range.md)单独整理 $\Delta\le 2k+3$ 的等号图和定量稳定性。

## 3. 零强制配置计数的 396 点树反例

设 $\tau(G)$ 为手稿定义的零强制二分配置数。一个配置记录独立集 $J$、边界选择 $S$、$G[J\cup S]$ 的正常二着色，以及闭邻域之外的选择 $T$，其中 $V(G)\setminus J$ 必须是零强制集。

反例由一个根、与根相邻的 5 个分支中心，以及接在每个中心上的 26 条互不相交的三边臂构成。它有 $1+5(1+3\cdot26)=396$ 个顶点、395 条边，最大度为 27。手稿直接构造一个合法配置子族，证明其大小已经超过 $8^{198}$，所以 $\tau(G)\le 8^{\lvert V(G)\rvert/2}$ 在树上即告失败。

可从[边表与整数证书](repro/zero-forcing/counterexample_certificate.json)重建此树。核验程序还在三个不同的根上复算树动态规划。直接计数和整数不等式见[反例证明](repro/zero-forcing/counterexample_proof.md)。

## 运行计算复核

Python 脚本使用 Python 3.10 或更新版本及标准库。等号结构的 JavaScript 复核另需 Node.js。以下命令检出固定的发布版本，再从仓库根目录运行相应脚本。

```sh
git clone --branch v0.1.0 https://github.com/shouanrenhechun/Graph.git
cd Graph
python repro/domination/prove_general_cn.py
python repro/domination/prove_acyclic_extension.py
python repro/domination/verify_domination_chain.py
node repro/domination/equality/verify_domination_equality.js
python repro/zero-forcing/counterexample_verify.py
```

| 复核 | 范围与输出 |
| --- | --- |
| 二部支配、森林支配 | 两项分别检查了 28,263 张二至六点的无孤立标号图，另有随机实例与 15 个叶冠等号构造。结果以 JSON 输出。 |
| 一般转移与公式 | 穷举 $k=0,1,2,3$ 的 113,052 个图与参数组合，并对 3,200 组最大度与退化度参数做精确算术检查。输出 [JSON 记录](repro/domination/output/pdf/domination_chain_checks.json)。 |
| 等号结构 | 用有限图检查加权选择的等号条件、增加外围边的严格性及最优参数公式，输出 JSON。 |
| 零强制计数 | 重新生成 [396 点证书](repro/zero-forcing/counterexample_certificate.json)，检查精确整数不等式及三个根的计算结果。 |

这些脚本核对有限实例、算式及反例证书。一般性上界、下界和等号推导见相应手稿。各脚本的说明见[结构支配复核目录](repro/domination/README.md)和[零强制复核目录](repro/zero-forcing/README.md)。

## Lean 形式化范围

配套仓库 [Myproofone v0.1.0](https://github.com/shouanrenhechun/Myproofone/releases/tag/v0.1.0) 收录最大度至多六的二部支配工程，包括上界、达到上界的五核心叶冠图，以及极值 $c_6=8/15$ 的 Lean 陈述和证明代码。Lean 与 mathlib 版本由项目文件固定，构建命令见[配套仓库 README](https://github.com/shouanrenhechun/Myproofone#readme)。

一般转移原理的 [Lean 笔记](https://github.com/shouanrenhechun/Myproofone/blob/v0.1.0/notes/DominationTransfer.lean)覆盖补全、预算和若干候选公式的恒等式，作为独立的部分形式化收录。笔记的编译待核验，全参数定理的形式化仍待完成。

## 其他研究方向

[研究索引](research/README.md)追踪最大度八、零强制、Vizing、控制理论，以及树自动机与谱理论等方向。最大度八与禁团方向的一般 $14/25$ 目标仍开放。

## 引用与版本

引用某个结论时，请写明手稿标题、相关定理或章节及所用版本。引用计算代码或数据时，请注明 [`v0.1.0` 发布版本](https://github.com/shouanrenhechun/Graph/releases/tag/v0.1.0)与脚本或证书名称。机器可读引用信息见 [CITATION.cff](CITATION.cff)。
