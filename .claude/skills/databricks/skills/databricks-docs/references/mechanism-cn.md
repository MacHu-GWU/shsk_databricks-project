# databricks-docs — 机制日志

> 这是 [mechanism.md](mechanism.md) 的中文翻译, 只供人阅读。**英文版是权威版本**, 两者不一致时以英文版为准,
> 并把这份翻译改过来。维护是单向的: 改了英文版就回来同步这份, 反过来不成立。

这个 skill 如何读取 Databricks 的文档, 以及为什么这么读。最新的条目在最上面; 顶部条目描述的就是当前
机制。条目只追加, 不改写。

## 2026-07-30 — build · docs-skill-builder 0.1.1

**结论。** 第一条。确立了机制: 在 `docs.databricks.com/llms.txt` 上做分区路由式正则搜索, 加一跳落地页
下钻, 页面正文用 WebFetch 读。

**这个站怎么读。** 索引是 `https://docs.databricks.com/llms.txt` —— 一份 47,150 字节 (约 11,787
tokens) 的 `llms.txt` 清单, 252 个条目分布在 15 个 `##` 分区里, 其中 98% 带有真正的散文式描述, 没有
一条是裸标题。分区大小从 890 字节 (Troubleshooting and support, 5 条) 到 6,468 字节 (Machine learning
and AI, 32 条)。AWS/英文 sitemap 列出 5,645 个 URL, 所以索引只覆盖全站的 **4.5%**: 它是一份人工精选的
领域索引, 不是页面清单。查询走 `scripts/docs_query.py`, 它把索引缓存 24 小时 (放在
`~/.cache/claude-docs-skills/`), 并且只打印命中的行, 因此一次搜索花费 60–1,300 tokens, 而不是整体加载
所需的 11,787。页面正文只有 HTML 这一种形态 —— `/jobs/scheduled` 21,136 字节, Unity Catalog 落地页
24,639 字节, `/getting-started/concepts` 50,782 字节 —— 一律用 WebFetch 读, 它会在上下文之外把 HTML
压成 markdown。索引里的 URL 不带云和语言前缀, 会 301 跳到 `/aws/en/…`; `/gcp/en/` 是真实存在、内容略有
差异的版本 (同一页 50,298 字节), 而 `/azure/en/` 直接 404, 因为 Azure Databricks 的文档由微软托管在
`learn.microsoft.com`。`robots.txt` 声明了 7 份 sitemap —— aws/gcp × en/ja/pt, 外加 `/api/` ——
所以**没有中文版可退**。

**为什么是这个设计。** 索引层 **T1 + T4**, 内容层 **C1**。47,150 字节落在 40–150 KB 区间内, 有 15 个
真实分区、98% 散文式描述, 远超"≥ 4 个分区 / ≥ 50% 散文"这条分区路由的门槛, 同时保留 `search` 作为
拉平一切的逃生通道。加 T4 的唯一理由就是那个 4.5% 的覆盖率, 而且这是验证过的而非假设: `vacuum|retention`
在索引里 0 命中, 但 `/tables/operations/vacuum` 就在 `/delta/` 落地页的一跳之内。没有这第二跳, 这个
skill 会自信地漏掉全站的大部分内容。定 C1 是因为六种已注册的纯文本约定全部失败 —— `.md`、`/index.md`、
`.txt` 都对着一个已标定的 12,999 字节错误页 404, 而 `Accept: text/markdown` 和 `?plain=1` 返回的是
一模一样的 50,782 字节 HTML; `.md` 和 `/index.md` 又对着规范化后的 `/aws/en/` 路径手工复核了一遍,
同样 404。被否决的方案: T0, 因为每个问题 11,787 tokens, 大约是实测的"搜索 + 取页"路径的十倍; T2,
因为描述质量足够好, 分区路由是真的有信息量, 而 T2 是地图没用时才退守的方案; T3, 因为 sitemap 有 5,645
个 URL 却零描述 —— 它是召回兜底, 不是主索引; T5, 它连 catalog 的第一个条件都不满足 (散文式描述是 98%,
不是低于 30%), 而且会引入一份只会不断腐化的第二真相源。

同样被否决**作为索引**的还有 `www.databricks.com/llms.txt`, 也就是这次构建请求指向的那份。它是市场
宣传用的清单 —— 12,873 字节、36 个条目, 其中 24 个指向 `www` 的产品页, 只有 1 个指进文档站。它的价值
在于**发现**而不是作为索引: 正是它自己的 "Databricks-owned LLM manifests" 分区点名了
`docs.databricks.com/llms.txt`。

厂商已有的工具也查过了, 以免这个 skill 变成无声的重复造轮子。Databricks 官方发布了 Claude Code 插件,
内含手写的 CLI、Apps、Lakebase、Model Serving、Lakeflow Jobs、Spark Declarative Pipelines、DABs 等
skill —— 属于互补关系, 因为它沉淀的是有主张的工作流, 而本 skill 读的是实时正文。Databricks Managed MCP
servers 暴露的是工作区**数据**, 不是文档。不存在官方的文档 MCP server 或文档搜索 API。

**验收测试。** catalog 要求的四项全部实跑并留下了实测数字。简单查询: `Unity Catalog`, 23 命中,
5,147 字节。词汇错配: `cron` → 0 命中, `schedul|orchestrat|trigger|recurring` → 4 命中、781 字节,
落到 **Job scheduling**; 以及 `row-level security` → 0, `row filter|column mask|fine-grained` →
1 命中、230 字节, 落到 **Row and column filters**。落地页下钻: `vacuum|retention` → 0, 经 `/delta/`
落地页找到。非英文: `数据血缘` → 0, `lineage` → 3 命中、643 字节, 落到 **Data lineage**。正文抓取:
对 `/jobs/scheduled` 用 WebFetch, 21,136 字节原始 HTML, 返回了 Quartz cron 语法和两次运行之间 10 秒的
最小间隔。没有任何一项测试需要加载整个索引。

**什么情况下这个结论会被推翻。** 出现 `.md` 孪生页 → C1 变 C0, token 收益巨大, 光凭这一条就值得重建。
覆盖率升到 30% 以上 (索引开始列出叶子页) → 去掉 T4 第二跳, 那次额外抓取不再划算。散文式描述跌破 50%,
或索引涨过 150 KB → T1 塌缩成 T2, `search` 要被写成主路径而不是逃生通道。`robots.txt` 里出现中文
locale (目前只有 en、ja、pt) → 第 2 步的"先翻译成英文"规则需要重新审视。Databricks 发布官方文档 MCP
server 或搜索 API → 本 skill 可能变得多余, 继续维护前先重新评估。索引搬家、404 或被登录墙挡住 →
这不是退化而是坏了, 直接重建。

**重建时必须保留的手写内容。** `description` 里的中文触发词 (数砖、Databricks 文档、官方文档、怎么配置、
如何设置、报错、数据血缘、权限、作业调度、流水线) —— 索引是纯英文的, 任何脚本都推导不出这些; 它们存在
是因为这个用户用中文工作。搜索指引里的改名对照 (`dlt/` → `ldp/`, Delta Live Tables → Lakeflow
Declarative Pipelines, Workflows → Lakeflow Jobs), 这些来自对厂商的观察而不是索引本身, 是这个站点上
价值最高的召回提示。以及范围之外的清单 —— Azure 在 `learn.microsoft.com`, DevHub 在
`developers.databricks.com` (有自己的 19,085 字节 `llms.txt`) —— 两条都来自探测脚本不会做的手工核查。
