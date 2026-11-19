# 图论研究 | Graph Theory Research

本仓库的主要研究是**结构支配的极值、等号图与稳定性**。基础两稿先求出最大度受限时的精确支配比例，再将森林支配和二部支配纳入统一的退化支配框架。方向 A 研究哪些图达到或接近这个极值。方向 B 和 C 在同一问题上进一步限制原图，分别考察最小度、退化度、树宽或禁团条件如何改变精确常数与等号图。

The structural domination program starts with exact maximum-degree bounds and continues in three directions: equality and stability (A), minimum degree at least two (B), and additional restrictions on the host graph (C). The repository also includes a separate zero-forcing counting counterexample and a companion Lean formalization.

## 研究路线与阅读入口

| 阶段 | 承接的问题 | 手稿 |
| --- | --- | --- |
| 基础Ⅰ · 森林与二部支配 | 最大度受限时，两类支配集的最坏比例各是多少？ | [精确常数与整数通项（PDF）](output/pdf/forest_bipartite_domination_theorem.pdf) |
| 基础Ⅱ · 结构支配转移 | 如何用同一方法处理独立支配、森林支配和一般退化支配？ | [转移原理、退化层级与性质夹逼（PDF）](output/pdf/domination_transfer_hierarchy.pdf) |
| A · 等号与稳定性 | 固定基础Ⅱ的图类和常数，刻画取等图并估计接近等号时的删点距离。 | [方向 A 研究稿（PDF）](output/pdf/direction_A_equality_stability_proof.pdf) |
| B · 最小度至少二 | 加入最小度条件后，原有叶冠锐例被排除，半数范围和等号图如何变化？ | [方向 B 研究稿（PDF）](output/pdf/direction_B_min_degree_two_proof.pdf) |
| C · 退化度、树宽与禁团 | 保留最大度约束，再限制原图的结构，哪些比例可以进一步精确求出？ | [方向 C 研究稿（PDF）](output/pdf/direction_C_research_paper.pdf) |

## 共同基础 · 精确常数与加权核心

设原图非空、有限、简单且无孤立顶点。支配集覆盖所有未入选顶点。用 Δ 表示原图最大度的上界，用 k 表示支配集所诱导子图的退化度上界。对每张图先最小化支配集大小，再对整个图类取相对大小的最坏值，得到极值常数。k = 0 对应独立支配，k = 1 对应森林支配。基础Ⅰ证明森林与二部支配的极值常数相同，基础Ⅱ给出对所有 k 的精确公式和性质夹逼。在原图只受最大度限制时，精确常数为 1/2 当且仅当 Δ ≤ 2k + 3。

共同的证明方法从**最大匹配与唯一归属**出发。给每个核心顶点分配相邻的外部顶点，再以分配数量减一作为权重。加权选择在核心中保留所需的诱导结构，随后用极大独立集补全未支配的外部顶点。已选核心与补全集合之间无边，因而补全保持诱导结构。反过来，完全图叶冠以专属叶子给出紧下界。这套归属、加权选择与叶冠构造，提供了 A 追踪取等以及 C 重新约束加权核心的起点。

<details>
<summary>展开基础公式和叶冠例子</summary>

```math
C_{\Delta,k}=
\max\left(\frac{1}{2},\;
\max_{1\le a\le\Delta-k-1}
\frac{k+1+a(\Delta-a-k)}{(\Delta-a+1)(a+1)}
\right).
```

内层只取整数 a。范围为空时只保留 1/2。对 k = 1，取 1 至 Δ − 2 中任一个最优 a，并给完全图的 Δ − a + 1 个顶点各挂 a 个专属叶子，即得相应叶冠等号图。比如 Δ = 6 时取 a = 2，叶冠有 15 个顶点，两种最小支配集均有 8 个顶点。精确的取整公式、小度数和孤立顶点修正见[森林与二部支配手稿](output/pdf/forest_bipartite_domination_theorem.md)。一般 k 的整数优化、渐近式和性质夹逼见[转移原理扩展手稿](output/pdf/domination_transfer_hierarchy.md)。

</details>

## 方向 A · 从一个等号例到完整分类

基础两稿用叶冠证明上界可达。A 保持相同的图类与极值常数，逐步追问加权选择、补全和局部预算何时同时取等。严格高于半数时，稿件刻画达到极值的叶冠结构。半数范围有自己的等号分类，临界点需要单独分析。

A 还把**极值亏损**与**顶点删除距离**联系起来。前者是极值上界允许的支配集大小与图的实际最小支配集大小之差。后者是删到相应等号图族所需的最少顶点数。稳定性定理用亏损定量控制删点数，把“达到上界的图是什么”延伸到“接近上界的图离等号结构有多远”。 [方向 A PDF](output/pdf/direction_A_equality_stability_proof.pdf) · [半数范围专题稿](output/pdf/domination_half_range.md)

## 方向 B · 最小度条件将半数范围延长一级

B 继续研究同一个退化支配比，但将原图最小度提高到至少 2。这样会排除含专属叶子的基础锐例，需要在新图类中重做上界和等号分析。B 使用普通最小支配集提供新的核心，仍对归属顶点作预算估计。森林支配的证明也调用 A 所整理的无孤立、最大度至多 5 图的半数界，处理部分外围结构。

对于 k ≥ 1，一般图类的半数阈值是 Δ ≤ 2k + 3。加入最小度条件后，B 将半数精确常数的范围延伸至 Δ ≤ 2k + 4。在证明覆盖的范围内，等号图恰为若干四圈的不交并，并有相应的顶点删除稳定性。例如 k = 1、Δ = 6 时，允许叶子的基础图类给出森林支配常数 8/15，最小度至少 2 的 B 图类给出 1/2。五分之二的部分结果另有明确适用范围，一般五分之二命题仍开放。 [方向 B PDF](output/pdf/direction_B_min_degree_two_proof.pdf)

## 方向 C · 限制原图结构后的精确值与开放区间

C 继续使用同一支配参数，保留最大度上界 Δ，再加入**原图**的退化度、树宽或禁团条件。原图的退化度界记为 q，支配集诱导子图的退化度界仍记为 k。稿件允许核心的不同顶点附着不同数量的叶子，使适用的加权核心能由实际叶冠图反向实现。在这一归约上，C 求出宿主退化度与最大度条件下的半数阈值，以及树宽受限子类的精确公式。

几个具体范围可以直接和基础结果对照。

| 森林支配的原图范围 | 从基础结果到 C 的推进 |
| --- | --- |
| 最大度至多 7，再要求禁 K₆ | 共同基础给出仅限最大度时的精确比例 5/9。加入禁团条件后，C 求出精确比例 11/20，刻画五团叶冠的不交并等号图，并证明线性删点稳定性。 |
| 最大度至多 8，树宽至多 4 | C 求出精确比例 14/25，五团叶冠给出等号。 |
| 最大度至多 8，分别要求四退化或禁 K₆ | C 对两个图类都给出下界 14/25 和上界 2281/4000，并证明一些达到目标上界的充分条件以及对最小反例的结构归约。两个图类的精确常数是否为 14/25 仍开放。 |

[方向 C PDF](output/pdf/direction_C_research_paper.pdf)

## 独立研究 · 零强制配置计数

396 点树反例属于零强制计数问题。构造从一个根连出 5 个分支中心，并在每个中心接 26 条三边臂。直接计数得到的合法配置子族已超过 8 的 198 次方，否定手稿所述的配置计数上界。证书含边表和整数不等式，程序还从三个不同的根复算树动态规划。 [反例 PDF](output/pdf/zero-forcing-396-vertex-counterexample.pdf) · [直接计数证明](repro/zero-forcing/counterexample_proof.md) · [边表与整数证书](repro/zero-forcing/counterexample_certificate.json)

## 运行计算复核

以下命令复核 [`v0.1.0` 首版](https://github.com/shouanrenhechun/Graph/releases/tag/v0.1.0)所附的基础定理实例、部分等号结构和零强制反例。Python 脚本使用 Python 3.10 或更新版本及标准库，等号结构复核另需 Node.js。

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
| 二部支配、森林支配 | 两项分别检查了 28,263 张二至六点的无孤立标号图，另有随机实例与 15 个叶冠等号构造。 [二部支配记录](repro/domination/general_cn_results.json) · [森林支配记录](repro/domination/acyclic_results.json) |
| 一般转移与公式 | 穷举 $k=0,1,2,3$ 的 113,052 个图与参数组合，并对 3,200 组最大度与退化度参数做精确算术检查。输出 [JSON 记录](repro/domination/output/pdf/domination_chain_checks.json)。 |
| 等号结构 | 用有限图检查加权选择的等号条件、增加外围边的严格性及最优参数公式。 [计算记录](repro/domination/equality/domination_equality_checks.json) |
| 零强制计数 | 重新生成 [396 点证书](repro/zero-forcing/counterexample_certificate.json)，检查精确整数不等式及三个根的计算结果。 |

这些脚本的覆盖范围见各自的[结构支配说明](repro/domination/README.md)与[零强制说明](repro/zero-forcing/README.md)。A、B、C 各稿中的一般性定理和有限计算分别以稿内说明为准。

## Lean 形式化范围

配套仓库 [Myproofone v0.1.0](https://github.com/shouanrenhechun/Myproofone/releases/tag/v0.1.0) 收录最大度至多六的二部支配工程，包括上界、达到上界的五核心叶冠图，以及极值 $c_6=8/15$ 的 Lean 陈述和证明代码。Lean 与 mathlib 版本由项目文件固定，构建命令见[配套仓库 README](https://github.com/shouanrenhechun/Myproofone#readme)。

一般转移原理的 [Lean 笔记](https://github.com/shouanrenhechun/Myproofone/blob/v0.1.0/notes/DominationTransfer.lean)覆盖补全、预算和若干候选公式的恒等式，作为独立的部分形式化收录。笔记的编译待核验，全参数定理的形式化仍待完成。

## 其他研究方向

[研究索引](research/README.md)汇集方向 A、B、C 的公开稿件，并追踪零强制、Vizing、控制理论，以及树自动机与谱理论等方向。

## 引用与版本

引用某个结论时，请写明手稿标题、相关定理或章节及所用版本。方向 A、B、C 的研究稿可按 PDF 首页日期和 GitHub 文件的固定链接引用。引用首版的计算代码或数据时，请注明 [`v0.1.0` 发布版本](https://github.com/shouanrenhechun/Graph/releases/tag/v0.1.0)与脚本或证书名称。机器可读引用信息见 [CITATION.cff](CITATION.cff)。
