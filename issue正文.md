# 1113李如清20265203044

## 基础信息

- 所属小组名称：地
- 作业/议题名称：第 4 章练手 4.1（边塞诗 LDA 主题模型）与练手 4.8（李白 × 杜甫 TF-IDF 对照）
- 个人github主页：https://github.com/amooseyy-eng

## 作业内容

md 报告（仓库链接）：

https://github.com/amooseyy-eng/DSDH/blob/main/实践作业/第4章文本挖掘/docs/REPORT.md

代码、图表、原始结果在同一目录：

https://github.com/amooseyy-eng/DSDH/tree/main/实践作业/第4章文本挖掘

做法一句话：从《全唐诗》里按种子词筛出 50 首边塞诗做 LDA（k=3/4/5 对照，并换随机种子看主题稳不稳定）；李白、杜甫各 40 首做 TF-IDF，各取 Top 20 关键词画条形图与词云，再用 TF-IDF 均值之差看谁更爱用哪些词。6 张图在 `output/figures/`，参数记录与逐条原文抽查在 `docs/复现与抽查记录.md`。

一键复现：

```
pip install -r requirements.txt
python run_all.py
```

## 自查清单

- [x] 文档可以正常打开
- [ ] Pages网页可以正常访问（如果有）
- [x] 已经按要求完成全部作业任务

## 备注（选填）

语料用 chinese-poetry 的公有领域《全唐诗》分片，原始 json 不入库、运行时自动下载。报告第六节写了 5 条妥协：繁体转简体、语料只有 50/80 首、单字意象字表是自定的、停用词表自编、原文抽查只能发现明显错误、不能证明没错误。
