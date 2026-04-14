# TennisDaily - 每日网球资讯站

## 1. 项目概述

TennisDaily 是一个自动化网球资讯网站，每日抓取并聚合全球职业网球新闻、比赛数据和排名信息，为网球爱好者提供一站式的中文信息平台。

## 2. 核心功能

### 2.1 每日新闻聚合
- 抓取国内外主流网球媒体的新闻报道
- 自动翻译英文新闻摘要为中文
- 按时间线展示，支持分类筛选（赛事新闻 / 球员动态 / 转会伤病 / 评论分析）

### 2.2 比赛数据中心
- **实时/近期赛果**：展示 ATP / WTA / 大满贯等赛事的每日比赛结果
- **赛程预告**：未来 7 天的重要比赛日程
- **比分详情**：每场比赛的逐盘比分、ACE数、破发点等关键统计
- **对阵记录**：球员历史交手数据

### 2.3 排名追踪
- ATP / WTA 单打及双打最新排名
- 排名变动趋势（周对比、月对比）
- Race to Turin / Race to Finals 积分榜

### 2.4 球员档案
- 球员基本信息（国籍、年龄、身高、打法、教练）
- 本赛季战绩统计
- 职业生涯里程碑

## 3. 技术架构

```
TennisDaily/
├── backend/              # 后端服务
│   ├── app/
│   │   ├── main.py           # FastAPI 入口
│   │   ├── api/              # API 路由
│   │   ├── models/           # 数据模型
│   │   ├── services/         # 业务逻辑
│   │   ├── scrapers/         # 数据抓取模块
│   │   │   ├── news.py           # 新闻抓取
│   │   │   ├── matches.py        # 比赛数据抓取
│   │   │   ├── rankings.py       # 排名抓取
│   │   │   └── players.py        # 球员信息抓取
│   │   └── scheduler/        # 定时任务调度
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/             # 前端
│   ├── src/
│   │   ├── pages/            # 页面组件
│   │   ├── components/       # 通用组件
│   │   ├── api/              # API 请求封装
│   │   └── styles/           # 样式
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml    # 容器编排
└── PROJECT.md            # 本文档
```

### 3.1 技术选型

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | Next.js (React) | SSR/SSG 支持，SEO 友好 |
| **UI 框架** | Tailwind CSS | 快速构建响应式界面 |
| **后端** | FastAPI (Python) | 高性能异步 API 服务 |
| **数据库** | SQLite → PostgreSQL | 开发阶段用 SQLite，生产迁移 PostgreSQL |
| **ORM** | SQLAlchemy | 数据库操作抽象层 |
| **爬虫** | httpx + BeautifulSoup | 异步 HTTP 请求 + HTML 解析 |
| **定时任务** | APScheduler | 定时触发数据抓取 |
| **部署** | Docker + Nginx | 容器化部署，反向代理 |

### 3.2 数据流

```
[数据源网站] 
    ↓  (APScheduler 定时触发, 每日 06:00 / 12:00 / 22:00)
[Scrapers 抓取模块]
    ↓  (解析、清洗、去重)
[SQLite/PostgreSQL 数据库]
    ↓  (FastAPI 提供 RESTful API)
[Next.js 前端渲染展示]
```

## 4. 数据源规划

| 数据类型 | 来源 | 抓取频率 |
|----------|------|----------|
| 新闻 | 新浪体育网球、腾讯体育、ESPN Tennis | 每日 3 次 |
| 比赛数据 | Flashscore、ATP/WTA 官网 | 赛事期间每 2 小时 |
| 排名 | ATP/WTA 官网 | 每周一 |
| 球员信息 | ATP/WTA 官网 | 每月更新 |

> **注意**：正式开发前需调研各数据源的反爬策略和 robots.txt 合规性，优先使用公开 API（如有）。

## 5. 数据库设计（核心表）

### articles（新闻文章）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| title | TEXT | 标题 |
| summary | TEXT | 摘要 |
| content | TEXT | 正文 |
| source | TEXT | 来源 |
| source_url | TEXT | 原文链接 |
| category | TEXT | 分类 |
| image_url | TEXT | 配图 |
| published_at | DATETIME | 发布时间 |
| created_at | DATETIME | 入库时间 |

### matches（比赛记录）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| tournament_id | INTEGER FK | 所属赛事 |
| player1_id | INTEGER FK | 球员1 |
| player2_id | INTEGER FK | 球员2 |
| score | TEXT | 比分 (如 "6-4, 3-6, 7-5") |
| round | TEXT | 轮次 |
| surface | TEXT | 场地类型 |
| match_date | DATE | 比赛日期 |
| stats | JSON | 详细统计数据 |
| status | TEXT | 状态 (scheduled/live/finished) |

### players（球员）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| name_en | TEXT | 英文名 |
| name_cn | TEXT | 中文名 |
| country | TEXT | 国籍 |
| birth_date | DATE | 出生日期 |
| hand | TEXT | 持拍手 (R/L) |
| backhand | TEXT | 反手 (one/two) |
| height_cm | INTEGER | 身高 |
| turned_pro | INTEGER | 转职业年份 |
| coach | TEXT | 教练 |
| photo_url | TEXT | 头像 |

### tournaments（赛事）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| name | TEXT | 赛事名称 |
| category | TEXT | 级别 (Grand Slam/Masters 1000/ATP 500 等) |
| surface | TEXT | 场地 |
| location | TEXT | 举办地 |
| start_date | DATE | 开始日期 |
| end_date | DATE | 结束日期 |

### rankings（排名）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| player_id | INTEGER FK | 球员 |
| rank | INTEGER | 排名 |
| points | INTEGER | 积分 |
| tour | TEXT | ATP/WTA |
| type | TEXT | singles/doubles |
| week_date | DATE | 排名周 |

## 6. API 设计

```
GET  /api/news                    # 新闻列表（分页、分类筛选）
GET  /api/news/:id                # 新闻详情

GET  /api/matches                 # 比赛列表（按日期、赛事筛选）
GET  /api/matches/:id             # 比赛详情
GET  /api/matches/live            # 进行中的比赛

GET  /api/rankings?tour=atp&type=singles  # 排名查询
GET  /api/rankings/changes        # 排名变动

GET  /api/players                 # 球员列表
GET  /api/players/:id             # 球员详情
GET  /api/players/:id/matches     # 球员比赛记录
GET  /api/players/:id1/vs/:id2    # 交手记录

GET  /api/tournaments             # 赛事列表
GET  /api/tournaments/:id         # 赛事详情及赛签
```

## 7. 前端页面规划

| 页面 | 路径 | 说明 |
|------|------|------|
| 首页 | `/` | 今日要闻 + 近期赛果 + 排名速览 |
| 新闻列表 | `/news` | 全部新闻，分类标签筛选 |
| 新闻详情 | `/news/[id]` | 文章正文 |
| 比赛中心 | `/matches` | 按日期查看比赛，日历切换 |
| 排名 | `/rankings` | ATP/WTA 排名表，支持搜索 |
| 球员档案 | `/players/[id]` | 球员详细信息及历史战绩 |
| 赛事页 | `/tournaments/[id]` | 赛事赛签、赛程、结果 |

### 首页布局草图

```
┌─────────────────────────────────────────────────┐
│  TennisDaily  [新闻] [比赛] [排名] [赛事]        │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─── 今日头条 ──────────────────────────────┐  │
│  │  [大图新闻卡片]                            │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌─ 最新新闻 ─────┐  ┌─ 今日赛果 ──────────┐  │
│  │ · 新闻标题1     │  │ Djokovic 2-1 Alcaraz│  │
│  │ · 新闻标题2     │  │ Sinner   2-0 Rune   │  │
│  │ · 新闻标题3     │  │ Sabalenka 2-1 Gauff │  │
│  │ · 更多 →        │  │ 更多 →              │  │
│  └────────────────┘  └─────────────────────┘  │
│                                                 │
│  ┌─ ATP 排名 ─────┐  ┌─ WTA 排名 ─────────┐  │
│  │ 1. Sinner  11k  │  │ 1. Sabalenka  10k  │  │
│  │ 2. Djokovic 9k  │  │ 2. Gauff      8k   │  │
│  │ 3. Alcaraz  8k  │  │ 3. Swiatek    7k   │  │
│  └────────────────┘  └─────────────────────┘  │
│                                                 │
│  ┌─ 近期赛事 ──────────────────────────────┐   │
│  │ 🏆 Roland Garros  5/25-6/8  红土        │   │
│  │ 🏆 Wimbledon      6/30-7/13 草地        │   │
│  └───────────────────────────────────────────┘  │
│                                                 │
├─────────────────────────────────────────────────┤
│  © 2026 TennisDaily                             │
└─────────────────────────────────────────────────┘
```

## 8. 开发计划

### Phase 1 — 基础框架（1-2 周）
- [x] 编写项目文档
- [ ] 初始化后端项目（FastAPI + SQLAlchemy + SQLite）
- [ ] 初始化前端项目（Next.js + Tailwind CSS）
- [ ] 设计并创建数据库表
- [ ] 搭建基础 API 框架

### Phase 2 — 数据抓取（2-3 周）
- [ ] 实现新闻抓取模块（至少 2 个数据源）
- [ ] 实现比赛数据抓取模块
- [ ] 实现排名数据抓取模块
- [ ] 实现球员信息抓取模块
- [ ] 配置 APScheduler 定时任务
- [ ] 数据去重和清洗逻辑

### Phase 3 — 前端开发（2-3 周）
- [ ] 首页布局与组件
- [ ] 新闻列表与详情页
- [ ] 比赛中心页面
- [ ] 排名页面
- [ ] 球员档案页面
- [ ] 响应式适配（移动端）

### Phase 4 — 完善与部署（1-2 周）
- [ ] Docker 容器化
- [ ] Nginx 反向代理配置
- [ ] 日志与错误监控
- [ ] 性能优化（缓存策略、ISR）
- [ ] 上线部署

## 9. 注意事项

1. **合规性**：遵守各数据源的 robots.txt 和使用条款，控制抓取频率，设置合理的 User-Agent
2. **容错**：爬虫模块需具备重试机制和异常告警，单个数据源失败不影响整体服务
3. **缓存**：对排名、球员信息等低频变动数据做缓存，减少数据库压力
4. **国际化**：球员中文名需维护映射表，新闻翻译可后续接入 AI 翻译服务
