# databricks-docs

> 这是 [README.md](README.md) 的中文翻译, 只供人阅读。**英文版是权威版本**, 两者不一致时以英文版为准,
> 并把这份翻译改过来。维护是单向的: 改了英文版就回来同步这份, 反过来不成立。

一个按需查询 Databricks 官方文档的 skill。它在提问时实时从 `docs.databricks.com` 取答案, 而不是
依赖训练截止日期之前的记忆 —— 这一点对 Databricks 尤其重要, 因为它改名非常频繁
(`dlt/` → `ldp/`, Delta Live Tables → Lakeflow Declarative Pipelines, Workflows → Lakeflow Jobs)。

---

## 工作原理

两套互相独立的机制, 都是基于实测数据选出来的, 而不是靠猜。完整的实测事实、推理过程以及被否决的
方案都在 [references/mechanism.md](references/mechanism.md) (只追加的日志) 的顶部条目里, 中文版是
[references/mechanism-cn.md](references/mechanism-cn.md)。

### 找到页面 —— T1 分区路由 + T4 二跳下钻

索引是 `https://docs.databricks.com/llms.txt`: 47,150 字节、252 条目、15 个分区, 其中 98% 带有
真正的散文式描述。这是一个不错的索引——但它只覆盖了全站的 **4.5%** (252 条目 vs 5,645 个 sitemap
URL)。也就是说, 它能告诉你*在哪个领域*, 却常常说不出*具体是哪一页*。

所以这个 skill 做两件事:

1. **在模型上下文之外过滤索引**——`search` 只打印命中的行, 因此一次查询花费 60–1,300 tokens,
   而不是整体加载索引所需的 11,787 tokens。索引缓存 24 小时, 重复查询不产生网络请求。
2. **当答案根本不在索引里时, 向下钻取**——抓取该领域的落地页, 再顺着它自己的子链接走。实测:
   `vacuum` 在索引里 0 命中, 但 `/tables/operations/vacuum` 就在 `/delta/` 落地页的一跳之内。

### 读取页面 —— C1, 只用 WebFetch

Databricks 只提供 HTML。`.md`、`/index.md`、`.txt`、`Accept: text/markdown` 请求头以及 `?plain=1`
全部测过: 三个 404, 三个返回完全相同的 HTML。页面原始大小在 21 KB–51 KB, 所以一律用 WebFetch
读取——它会在内容进入上下文*之前*把 HTML 转成 markdown。`docs_query.py get` 会刻意拒绝下载页面
正文, 并提示改用 WebFetch。

### 召回率

文档类 skill 的典型失败是无声的: agent 搜了一下、没结果, 就回答"文档里没有"。`SKILL.md` 里写死了
一条升级阶梯——换同义词扩大搜索、把非英文查询翻译成英文、列出分区、整块读一个分区、下钻落地页——
只有走完这些才能下"没有"的结论, 并且必须说明搜过什么。其中两条在这个站点上尤其关键:

- **词汇错配。** `cron` → 0 命中; `schedul|orchestrat|trigger|recurring` → 找到 **Job scheduling**。
  `row-level security` → 0 命中; `row filter|column mask` → 找到 **Row and column filters**。
- **语言。** Databricks 的文档只有英语、日语、葡萄牙语——**没有中文版**。`数据血缘` 得到 0 命中,
  `lineage` 才能找到页面。非英文查询没命中, 完全不能说明文档没有覆盖。

---

## 使用方式

```
/databricks-docs 怎么用 cron 表达式给作业配置定时调度
```

或者直接提 Databricks 相关的问题——skill 的 description 同时匹配英文和中文表达。

底层命令:

```bash
python3 scripts/docs_query.py search 'schedul|orchestrat|trigger'
python3 scripts/docs_query.py sections
python3 scripts/docs_query.py section 'Data engineering'
python3 scripts/docs_query.py stats
python3 scripts/docs_query.py refresh
```

`scripts/docs_query.py` 是从 `docs-skill-builder` 原样复制过来的; 所有站点相关的配置都放在
`scripts/docs-source.json` 里。不要 fork 这个脚本——要改就改 JSON。

索引缓存写在 `~/.cache/claude-docs-skills/databricks-docs/index.txt`。它是派生产物、可随时丢弃,
永远不要提交到仓库。

---

## 覆盖范围

覆盖: 文档索引的 15 个分区——核心平台与 Unity Catalog、数据工程 (Lakeflow Jobs 与 Declarative
Pipelines)、SQL 与分析、机器学习与 AI、开发者工具、治理与安全、管理、集成、迁移、故障排查。

不覆盖:

| 不在范围内 | 实际位置 |
| :--- | :--- |
| Azure Databricks | `learn.microsoft.com`——`docs.databricks.com/azure/…` 直接 404 |
| DevHub | `developers.databricks.com`, 有自己的 19,085 字节 `llms.txt` |
| 你自己工作区里的数据 | 需要 Databricks CLI 或 Databricks MCP server |

索引覆盖 AWS (所有中性 URL 的默认跳转目标) 和 `/gcp/en/` 下的 GCP。两者的页面内容可能不同;
skill 被要求说明自己回答的是哪个云。

## 与 Databricks 官方 Claude Code 插件的关系

Databricks 自己发布了插件, 内含手写的 CLI、Apps、Lakebase、Model Serving、Lakeflow Jobs、
Spark Declarative Pipelines、DABs 等 skill。那是**互补关系**而非重复: 官方插件沉淀的是有主张的
工作流, 本 skill 读的是实时文档。截至 2026-07-30, Databricks 没有官方的文档 MCP server 或文档
搜索 API——Databricks Managed MCP servers 暴露的是工作区的**数据**, 不是文档。

## 维护

```
/docs-skill-builder check .claude/skills/databricks/skills/databricks-docs
```

会以 [references/mechanism-cn.md](references/mechanism-cn.md) (权威版是
[mechanism.md](references/mechanism.md)) **最顶上那条**为基线重新探测并做 diff, 然后追加自己的
一条 —— 哪怕结论是"什么都没变"也要写, 因为一次不留痕迹的 check 和一次根本没跑过的 check 是分不
出来的。这份日志只追加、不改写, 所以它记录的是当时相信什么、以及后来为什么不成立了。

哪些变化会推翻当前设计 (出现 `.md` 孪生页、覆盖率上升、索引搬家等) 都在顶部条目的
**什么情况下这个结论会被推翻**一节里, 同一条目里还列出了重建时**必须保留**的手写内容。
