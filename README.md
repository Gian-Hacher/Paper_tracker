# Paper Tracker (MVP)

面向“机器人 / 具身智能 / 机器人操作”方向的论文自动追踪系统。  
使用更广覆盖学术元数据源（OpenAlex）实现最新前沿高质量论文自动抓取

## 1. 项目简介

本项目实现了一个轻量可扩展的论文跟踪流水线：

1. 先在 OpenAlex 的 `sources` 中解析白名单会议/期刊来源。
2. 用 OpenAlex 的 `works` 端点按 `时间窗 + source.id` 全量抓取目标来源中的论文。
3. 对返回结果做去重、主题筛选、噪声排除和来源标准化校验。
4. 使用规则评分（新近性、关键词相关性、来源分）。
5. 存入 SQLite 并基于分数排序。
6. 输出日报到 `outputs/daily/YYYY-MM-DD.md`。

设计上保留了扩展边界，后续可接入 OpenReview / Semantic Scholar / 会议官网等。

## 2. 安装方式

Python 版本建议：`3.11+`

```bash
pip install -r requirements.txt
```

## 3. 本地运行方式

在项目根目录 `Paper_tracker` 下执行：

```bash
python -m src.main --days-back 365 --top-n 20
```

运行后会产生：

- SQLite 数据库：`data/tracker.db`
- 每日报告：`outputs/daily/YYYY-MM-DD.md`

## 4. 目录说明

```text
Paper_tracker/
  README.md
  requirements.txt
  .gitignore
  config/
    keywords.yaml      # include / exclude 关键词配置
    sources.yaml       # 数据源配置（OpenAlex endpoint / 分页大小 / 超时）
    venues.yaml        # 会议/期刊白名单（canonical/aliases/tier/type）
    scoring.yaml       # 评分规则配置
  data/
    raw/
    normalized/
    tracker.db         # 运行后自动生成
  outputs/
    daily/
    weekly/
  src/
    main.py
    fetchers/
      arxiv_fetcher.py
    processors/
      normalize.py
      filter.py
      score.py
      dedup.py
    storage/
      sqlite_store.py
    renderers/
      markdown_report.py
    models/
      paper.py
    utils/
      logging_utils.py
      text_utils.py
  tests/
    test_filter.py
    test_score.py
    test_dedup.py
  .github/workflows/
    daily_digest.yml
```

## 5. 评分规则（MVP）

- `recency_score`：在配置窗口期内越新越高。
- `keyword_score`：命中 include 关键词越多越高（有最大命中数上限）。
- `source_score`：当前 OpenAlex 基础分，可扩展会议/期刊加权。
- `total_score`：按权重汇总并预留未来扩展项（venue/citation/code）。

相关配置位于 `config/scoring.yaml`。

## 6. 来源白名单策略（严格）

系统当前只抓取并保留 `config/venues.yaml` 中定义的来源，包含你指定的第一、二梯队会议与期刊：

- 来源名称先做标准化（忽略大小写、空格、标点）
- 支持别名映射（如 `CVPR`, `ICCV`, `ECCV`, `RSS`, `ICRA`, `IROS`, `T-RO`, `IJRR`, `RA-L` 等）
- 若无法明确匹配到白名单 `canonical_name`，该论文会被直接丢弃
- OpenAlex 当前采用“来源内全量抓取”模式：
  - 先到 `sources` 端点解析白名单 venue 对应的 `source.id`
  - 再到 `works` 端点使用 `from_publication_date + primary_location.source.id` 抓取固定时间窗内的全部论文
  - 本地再根据 `config/keywords.yaml` 做主题相关性筛选
  - 相关配置位于 `config/sources.yaml`

## 7. GitHub Actions 自动化

已提供工作流：`.github/workflows/daily_digest.yml`

- 支持手动触发（`workflow_dispatch`）
- 支持定时触发（每天一次，UTC 时间）
- 自动上传日报产物

## 8. 运行测试

```bash
pytest
```

## 9. 后续扩展建议

1. 增加数据源插件接口：OpenReview / OpenAlex / Semantic Scholar。
2. 增加更细粒度噪声过滤（如 “SLAM-only” 规则模板 + 分类器）。
3. 增加多维评分：`venue_score`, `citation_score`, `code_score`, `reproducibility_score`。
4. 增加周报聚合（趋势关键词、主题聚类、跨天去重）。
5. 增加通知渠道（邮件、飞书、Slack、企业微信）。
