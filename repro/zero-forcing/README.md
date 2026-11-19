# 396 点零强制配置计数反例

从根顶点连接 5 个中心，再给每个中心接 26 条互不相交的三边臂，得到一个有 396 个顶点的树。手稿给出直接计数下界，证书包含边表和用于比较的整数。

- [PDF](../../output/pdf/zero-forcing-396-vertex-counterexample.pdf)
- [直接计数证明](counterexample_proof.md)
- [边表与计算证书](counterexample_certificate.json)

从仓库根目录运行 `python repro/zero-forcing/counterexample_verify.py`。脚本用 Python 标准库重新生成证书，复核整数不等式，并在三个不同的根上复算树动态规划。
