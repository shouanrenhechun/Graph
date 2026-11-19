# 结构支配的计算复核

从仓库根目录运行以下命令。脚本使用 Python 3.10 或更高版本及标准库。六点以内的穷举和随机实例可能需要一些时间。

```sh
python repro/domination/prove_general_cn.py
python repro/domination/prove_acyclic_extension.py
python repro/domination/verify_domination_chain.py
```

前两项分别检查二部支配和森林支配的构造，并输出 JSON。第三项检查 k 退化的构造以及阈值和整数公式，同时重新生成 [domination_chain_checks.json](output/pdf/domination_chain_checks.json)。

- [二部支配运行记录](general_cn_results.json)
- [森林支配运行记录](acyclic_results.json)
- [一般转移与公式运行记录](output/pdf/domination_chain_checks.json)

扩展手稿的等号结构另附 [JavaScript 复核脚本](equality/verify_domination_equality.js) 和 [计算记录](equality/domination_equality_checks.json)。运行命令为 `node repro/domination/equality/verify_domination_equality.js`。
