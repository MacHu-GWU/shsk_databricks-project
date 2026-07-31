# Databricks Docs (中文版)

> 这是 [SKILL.md](SKILL.md) 的中文翻译, 只供人阅读。**英文版是权威版本**, 两者不一致时以英文版为准,
> 并把这份翻译改过来。
>
> 这条约定只写在这里。`SKILL.md` 是正式产物, 也是真正被 Claude Code 加载进上下文的那份, 所以它里面
> 不提翻译的存在 —— 那对 agent 干活没有任何帮助。维护是单向的: 改了 `SKILL.md` 就回来同步这份,
> 反过来不成立。

英文版的 frontmatter 如下 (`name`、`description`、`argument-hint`、`allowed-tools`), 其中
`description` 里的中文触发词是手写的, 重建时必须保留:

```yaml
name: databricks-docs
allowed-tools: Bash(python3 *), WebFetch
```

`description` 覆盖的领域: 核心平台、Unity Catalog 数据治理与安全、数据工程 (Lakeflow Jobs 与
Declarative Pipelines)、SQL 与分析、机器学习与 AI (agents、MLflow、model serving)、开发者工具
(CLI、SDK、asset bundles)、计算资源、管理、集成、迁移、故障排查。中文触发词: 数砖 / Databricks 文档 /
官方文档 / 怎么配置 / 如何设置 / 报错 / 数据血缘 / 权限 / 作业调度 / 流水线。

---

按需从官方文档回答 Databricks 问题: 在缓存下来的 47 KB `llms.txt` 索引上按分区或正则搜索, 再用
WebFetch 读命中的页面。永远优先用这个 skill, 不要凭记忆回答文档问题 —— Databricks 改名和重组的速度
很快 (`dlt/` 变成了 `ldp/`, "Delta Live Tables" 变成了 "Lakeflow Declarative Pipelines",
"Workflows" 变成了 "Lakeflow Jobs")。

如果用户传了参数 (`$ARGUMENTS`), 就当作主题; 否则自己推断。

## 什么时候用这个 skill

索引自带的 15 个分区, 按体量从大到小:

- **Machine learning and AI** —— agents、MLflow、model serving、feature store、Genie
- **Core platform** —— Unity Catalog、catalog、schema、volume、workspace、compute、notebook
- **Developer tools** —— CLI、SDK、asset bundles、VS Code 扩展、REST API、CI/CD
- **Data governance and security** —— 权限、行过滤与列掩码、数据血缘、审计
- **Data engineering** —— Lakeflow Jobs、Lakeflow Declarative Pipelines、数据接入、Auto Loader
- **SQL and analytics** —— SQL warehouse、查询、看板、告警
- **Data sources and formats** —— Delta Lake、表、外部数据、连接器
- **Overview and getting started**、**Administration**、**Reference and language-specific
  guides**、**Integrations and connectors**、**Migration and best practices**、**Specialized
  features**、**Additional resources**、**Troubleshooting and support**

不在范围内:

- **Azure Databricks。** `docs.databricks.com/azure/…` 根本不存在; 那部分文档由微软托管在
  `learn.microsoft.com`。本索引覆盖的是 AWS (默认) 和 GCP。
- **DevHub** (`developers.databricks.com`) —— 独立站点, 有自己的 19 KB `llms.txt`, 不在这里覆盖。
- **你工作区里的实际数据。** 读表、跑 SQL、查 Unity Catalog 对象要用 Databricks CLI 或 Databricks
  MCP server, 不是这个 skill。

## 这个站是怎么回事

实测于 2026-07-30; 数字和推理过程见 [references/mechanism.md](references/mechanism.md) 的顶部条目。

- **索引**: `https://docs.databricks.com/llms.txt` —— 47,150 字节 (约 11,787 tokens), 252 条目,
  15 个分区, 98% 带散文式描述。
- **覆盖率**: 252 个索引条目 vs 5,645 个 sitemap URL (**4.5%**) —— **领域级**。很多条目指向的是
  某个领域的落地页而不是叶子页。具体问题要预期多跳一次。
- **正文**: 只有 HTML。所有纯文本约定都 404 (`.md`、`/index.md`、`.txt`, 以及
  `Accept: text/markdown` 请求头全部失败)。页面原始大小 21 KB–51 KB —— 用 WebFetch, 它会先转成
  markdown。永远不要 curl 页面正文。
- **坑**:
  - 索引里的 URL 不带云和语言前缀 (`/jobs/scheduled`), 会 **301 跳到 `/aws/en/…`**。跟着跳转走,
    引用时用真正返回内容的那个 URL。
  - `www.databricks.com/llms.txt` 是**市场宣传**索引 (36 条目, 基本都是产品页), 不是这份索引。
    它的 "Databricks-owned LLM manifests" 分区才是指向这里的那个入口。
  - 文档站本身不发布 `llms-full.txt`。市场站链了一份 —— 永远不要去取。
  - 文档只有英语、日语、葡萄牙语三种。**没有中文版。**

## 流程

### 1. 找候选页面

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/docs_query.py search '<词>|<同义词>|<文档会用的那个词>'
```

索引只下载一次并缓存 24 小时, 所以重复查询不产生请求。只有命中的行会进入上下文 —— 永远不要加载
整个索引。

路由命令, 从便宜到贵:

| 命令 | 实测成本 | 什么时候用 |
| :--- | :--- | :--- |
| `search '<正则>'` | 约 60–1,300 tok | 永远从这里开始 |
| `sections` | 约 253 tok | 搜索没命中, 需要看地图 |
| `section '<名字>'` | 222–1,617 tok | 在某一个领域内做完整召回 |

Databricks 经常改名, 所以把新旧两个名字写成一个 alternation 一起搜 ——
`'Delta Live Tables|declarative pipeline|ldp'`、`'Workflows|Lakeflow Jobs'`。

### 2. 如果搜索是空的

**不要**直接下"文档里没有"的结论。按顺序升级:

1. 换同义词扩大范围 —— 文档用的词往往不是用户用的词。本站实测: `cron` 得到 0 命中,
   `'schedul|orchestrat|trigger|recurring'` 找到 **Job scheduling**。`row-level security` 得到
   0 命中, `'row filter|column mask|fine-grained'` 找到 **Row and column filters**。
2. 如果查询不是英文, 换成英文重试。这份索引是纯英文的, 而且 Databricks 根本没有中文版文档 ——
   `数据血缘` 得到 0 命中, `lineage` 才能找到页面。非英文没命中, 完全说明不了覆盖情况。
3. `sections`, 然后 `section '<最可能的那个>'`, 在其中做完整召回。
4. **下钻落地页。** 索引只覆盖全站 4.5%, 所以你要找的叶子页经常根本没被列出来, 列出来的只是它所在
   领域的落地页。用 WebFetch 抓落地页, 读它自己的子链接。实测: `vacuum|retention` 在索引里 0 命中,
   但 `/delta/` 落地页直接链到 `/tables/operations/vacuum`。
5. 走完以上才可以说文档里没有, 并且要讲清楚搜过什么。

### 3. 读页面

```
WebFetch url=<搜索结果里的 URL>
        prompt="<用户真正的问题, 不要写"总结这一页">"
```

页面只有 HTML (原始 21 KB–51 KB)。WebFetch 会在内容进入上下文之前转成 markdown —— 不要 curl。
`docs_query.py get <url>` 也存在, 但它只会打印这条提示, 因为把 Databricks 的原始 HTML 灌进上下文
纯属浪费 token。

**每批取 1–3 页**, 然后判断够不够回答问题。不够就继续, 上限 **9 页**。到了 9 页还不够就停下来,
告诉用户你读了什么、还缺什么 —— 不要闷头继续, 也不要用猜测填空。

## 上下文预算

| 步骤 | 实测成本 | 备注 |
| :--- | :--- | :--- |
| `search` (窄) | 约 58 tok | `row filter\|column mask\|fine-grained` → 230 字节 |
| `search` (典型) | 约 160–200 tok | `lineage` → 643 字节; `schedul\|...` → 781 字节 |
| `search` (宽) | 约 1,290 tok | `Unity Catalog` → 5,147 字节, 23 命中 |
| `sections` | 约 253 tok | 1,013 字节 |
| `section` | 222–1,617 tok | Troubleshooting 890 字节 … ML and AI 6,468 字节 |
| 用 WebFetch 读页面 | 约 0.3–1k tok | 来自 21–51 KB 原始 HTML |

一个典型问题: 搜索 + 1–2 页 ≈ **1–2k tokens**。整体加载索引要约 11,787 tokens, 这就是为什么这里
任何一步都不那么干。一次只读**一个**分区; 如果你判断不出该读哪个分区, 那说明该换更好的词再搜一次,
而不是把好几个分区都读进来。

## 规则

- **永远不要编造文档 URL。** 索引里没有就扩大搜索, 或者下钻落地页。Databricks 会改 slug
  (`dlt/` → `ldp/`), 编出来的 URL 就是一个自信的 404。
- **永远不要加载整个索引**, 也永远不要碰市场站的 `llms-full.txt`。
- **引用真正返回内容的那个 URL** —— 即跳转之后的 `/aws/en/…`。
- **页面 URL 返回 404 说明索引过期了** —— 重新跑
  `/docs-skill-builder check .claude/skills/databricks/skills/databricks-docs`。
- **说清楚你回答的是哪个云。** 默认是 AWS; GCP 的页面在 `/gcp/en/` 下, 内容可能不同。Azure 根本
  不在这个域名上。
- **原样传达文档说了什么。** 用户要的是当前的权威行为, 不是你拿旧知识揉出来的综合版本。
