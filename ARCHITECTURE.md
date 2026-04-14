# TennisDaily 技术架构文档

## 1. 架构总览

采用前后端分离架构，单台云服务器部署，通过 Docker Compose 统一管理所有服务。

```
                        ┌─── 云服务器 ──────────────────────────────────────┐
                        │                                                   │
  用户浏览器 ──HTTPS──→ │  Nginx (443/80)                                   │
                        │    ├── /           → Next.js (3000)  [前端SSR]     │
                        │    ├── /api/       → FastAPI (8000)  [后端API]     │
                        │    └── /static/    → 本地文件系统     [图片缓存]    │
                        │                                                   │
                        │  ┌─────────────────────────────────────────────┐  │
                        │  │  FastAPI 后端                                │  │
                        │  │    ├── API 服务层 (uvicorn, 多worker)        │  │
                        │  │    ├── Scraper 爬虫引擎                      │  │
                        │  │    └── APScheduler 定时调度                  │  │
                        │  └──────────┬──────────────────────────────────┘  │
                        │             │                                     │
                        │  ┌──────────▼──────────┐  ┌──────────────────┐   │
                        │  │  PostgreSQL (5432)   │  │  Redis (6379)    │   │
                        │  │  持久化存储           │  │  缓存 + 任务队列  │   │
                        │  └─────────────────────┘  └──────────────────┘   │
                        └───────────────────────────────────────────────────┘
```

## 2. 技术选型与决策理由

### 2.1 后端：FastAPI (Python 3.12+)

| 候选 | 优势 | 劣势 | 结论 |
|------|------|------|------|
| **FastAPI** | 原生 async、自动 OpenAPI 文档、Python 生态爬虫库丰富 | 单语言性能上限低于 Go | **选用** |
| Django | 管理后台开箱即用 | 异步支持弱，框架偏重 | 不选 |
| Express/Nest.js | JS 全栈统一 | 爬虫生态不如 Python | 不选 |

**关键依赖：**

```
fastapi          # Web 框架
uvicorn          # ASGI 服务器
sqlalchemy[asyncio]  # 异步 ORM
asyncpg          # PostgreSQL 异步驱动
alembic          # 数据库迁移
httpx            # 异步 HTTP 客户端（爬虫用）
beautifulsoup4   # HTML 解析
lxml             # 高性能 XML/HTML 解析器
apscheduler      # 定时任务调度
redis[hiredis]   # Redis 客户端
pydantic         # 数据校验（FastAPI 内置）
```

### 2.2 前端：Next.js 14+ (App Router)

| 候选 | 优势 | 劣势 | 结论 |
|------|------|------|------|
| **Next.js** | SSR/SSG/ISR 灵活切换、SEO 友好、React 生态 | Node 运行时占用内存 | **选用** |
| Nuxt.js | Vue 生态、上手快 | 社区规模和组件库不如 React | 不选 |
| Astro | 极致静态性能 | 交互组件支持弱 | 不选 |

**关键依赖：**

```
next             # 框架
react / react-dom
tailwindcss      # 原子化 CSS
@tanstack/react-query  # 数据请求与缓存
dayjs            # 日期处理
recharts         # 排名趋势图表
```

**渲染策略：**

| 页面 | 策略 | 理由 |
|------|------|------|
| 首页 | ISR (revalidate: 600) | 每 10 分钟重新生成，平衡实时性和性能 |
| 新闻列表 | ISR (revalidate: 300) | 新闻更新较频繁，5 分钟刷新 |
| 新闻详情 | SSG + on-demand | 文章内容不变，发布时触发生成 |
| 比赛中心 | SSR | 赛事期间需要最新数据 |
| 排名页 | ISR (revalidate: 3600) | 每周才更新，1 小时足够 |
| 球员档案 | ISR (revalidate: 86400) | 数据变动极少，每天重校验 |

### 2.3 数据库：PostgreSQL 16

| 候选 | 优势 | 劣势 | 结论 |
|------|------|------|------|
| **PostgreSQL** | JSON 字段原生支持、全文检索、扩展性强 | 配置略复杂 | **选用** |
| MySQL | 普及率高 | JSON 支持和全文检索不如 PG | 不选 |
| MongoDB | 灵活 schema | 关系查询弱，比赛数据天然是关系型 | 不选 |

**选用理由：**
- 比赛统计数据结构复杂但有固定关系（球员-赛事-比赛），关系型数据库天然适配
- `JSONB` 字段存储比赛详细统计（ACE、双误、破发点等），灵活且可索引
- `tsvector` 全文检索支持新闻搜索，不需要额外引入 Elasticsearch
- 物化视图可以预计算排名变动，减少实时查询压力

### 2.4 缓存：Redis 7

用途：
- **API 响应缓存**：高频查询（首页数据、当日赛果）缓存 5-10 分钟
- **爬虫去重**：URL 指纹存入 Redis Set，快速判断是否已抓取
- **限流**：API 请求频率限制

### 2.5 反向代理：Nginx

- HTTPS 终止（Let's Encrypt 免费证书）
- 静态资源缓存（图片、字体、CSS/JS）
- Gzip/Brotli 压缩
- 请求路由分发（前端 / API / 静态文件）

## 3. 服务器配置建议

### 3.1 最低配置

| 资源 | 建议 | 说明 |
|------|------|------|
| CPU | 2 核 | 爬虫 + API + SSR 并行需要 |
| 内存 | 4 GB | PostgreSQL 1G + Next.js 512M + FastAPI 512M + Redis 256M + 系统 |
| 磁盘 | 40 GB SSD | 数据库 + 图片缓存 + 日志 |
| 带宽 | 3-5 Mbps | 图片加载是主要带宽消耗 |
| 系统 | Ubuntu 22.04 LTS / Debian 12 | Docker 兼容性最佳 |

### 3.2 推荐配置（日均 UV > 1000）

| 资源 | 建议 |
|------|------|
| CPU | 4 核 |
| 内存 | 8 GB |
| 磁盘 | 80 GB SSD |
| 带宽 | 5-10 Mbps |

## 4. 后端架构详细设计

### 4.1 目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI 应用入口
│   ├── config.py                # 配置管理 (pydantic-settings)
│   ├── database.py              # 数据库连接与会话管理
│   │
│   ├── models/                  # SQLAlchemy ORM 模型
│   │   ├── article.py
│   │   ├── match.py
│   │   ├── player.py
│   │   ├── tournament.py
│   │   └── ranking.py
│   │
│   ├── schemas/                 # Pydantic 请求/响应模型
│   │   ├── article.py
│   │   ├── match.py
│   │   ├── player.py
│   │   └── ranking.py
│   │
│   ├── api/                     # API 路由
│   │   ├── __init__.py          # 路由注册
│   │   ├── news.py
│   │   ├── matches.py
│   │   ├── rankings.py
│   │   ├── players.py
│   │   └── tournaments.py
│   │
│   ├── services/                # 业务逻辑层
│   │   ├── news_service.py
│   │   ├── match_service.py
│   │   ├── ranking_service.py
│   │   └── player_service.py
│   │
│   ├── scrapers/                # 爬虫模块
│   │   ├── base.py              # 爬虫基类 (重试、限速、UA轮换)
│   │   ├── news/
│   │   │   ├── sina_tennis.py       # 新浪网球
│   │   │   ├── tencent_tennis.py    # 腾讯体育
│   │   │   └── espn_tennis.py       # ESPN
│   │   ├── matches/
│   │   │   └── flashscore.py        # 比赛数据
│   │   ├── rankings/
│   │   │   └── atp_wta.py           # 排名数据
│   │   └── players/
│   │       └── atp_wta_profile.py   # 球员档案
│   │
│   ├── scheduler/               # 定时任务
│   │   └── jobs.py              # 任务定义与注册
│   │
│   └── utils/
│       ├── cache.py             # Redis 缓存装饰器
│       ├── logger.py            # 日志配置
│       └── translation.py       # 翻译工具
│
├── alembic/                     # 数据库迁移
│   ├── versions/
│   └── env.py
├── alembic.ini
├── requirements.txt
├── Dockerfile
└── .env.example
```

### 4.2 爬虫引擎设计

```python
# 爬虫基类核心能力
class BaseScraper:
    """
    所有爬虫继承此基类，统一提供：
    - 自动重试（指数退避，最多 3 次）
    - 请求限速（同域名间隔 2-5 秒随机延迟）
    - User-Agent 轮换
    - 代理支持（可选）
    - 响应缓存（Redis，避免短时间重复请求）
    - 统一的错误上报与日志记录
    """
```

**爬虫调度策略：**

```
┌──────────────┬──────────────────┬───────────────────────┐
│ 任务         │ Cron 表达式       │ 说明                  │
├──────────────┼──────────────────┼───────────────────────┤
│ 新闻抓取     │ 0 6,12,18,22 * * * │ 每日 4 次            │
│ 比赛数据     │ 0 */2 * * *       │ 赛事期间每 2 小时     │
│ 排名更新     │ 0 8 * * 1         │ 每周一早 8 点         │
│ 球员信息     │ 0 3 1 * *         │ 每月 1 号凌晨 3 点    │
│ 数据清理     │ 0 4 * * 0         │ 每周日清理 90 天前数据 │
└──────────────┴──────────────────┴───────────────────────┘
```

### 4.3 API 分层架构

```
请求 → Router (参数校验) → Service (业务逻辑) → Repository (数据访问) → DB
                                                     ↕
                                                   Redis Cache
```

- **Router 层**：仅负责参数接收、校验、调用 Service、返回响应
- **Service 层**：业务逻辑编排，缓存策略判断，多数据源聚合
- **Repository 层**：SQLAlchemy 查询封装，通过 Service 调用，不直接暴露给 Router

## 5. 前端架构详细设计

### 5.1 目录结构

```
frontend/
├── src/
│   ├── app/                     # Next.js App Router
│   │   ├── layout.tsx               # 全局布局（导航栏+页脚）
│   │   ├── page.tsx                 # 首页
│   │   ├── news/
│   │   │   ├── page.tsx             # 新闻列表
│   │   │   └── [id]/page.tsx        # 新闻详情
│   │   ├── matches/
│   │   │   └── page.tsx             # 比赛中心
│   │   ├── rankings/
│   │   │   └── page.tsx             # 排名页
│   │   ├── players/
│   │   │   └── [id]/page.tsx        # 球员档案
│   │   └── tournaments/
│   │       ├── page.tsx             # 赛事列表
│   │       └── [id]/page.tsx        # 赛事详情
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Navbar.tsx
│   │   │   └── Footer.tsx
│   │   ├── news/
│   │   │   ├── NewsCard.tsx
│   │   │   └── NewsList.tsx
│   │   ├── matches/
│   │   │   ├── MatchCard.tsx
│   │   │   ├── ScoreBoard.tsx
│   │   │   └── DatePicker.tsx
│   │   ├── rankings/
│   │   │   ├── RankingTable.tsx
│   │   │   └── RankingChart.tsx
│   │   └── common/
│   │       ├── Loading.tsx
│   │       ├── Pagination.tsx
│   │       └── PlayerAvatar.tsx
│   │
│   ├── lib/
│   │   ├── api.ts               # axios/fetch 封装，统一 baseURL 和错误处理
│   │   └── utils.ts             # 工具函数
│   │
│   ├── hooks/
│   │   ├── useNews.ts           # react-query hooks
│   │   ├── useMatches.ts
│   │   └── useRankings.ts
│   │
│   └── types/                   # TypeScript 类型定义
│       ├── news.ts
│       ├── match.ts
│       ├── player.ts
│       └── ranking.ts
│
├── public/
│   ├── fonts/
│   └── images/
├── next.config.js
├── tailwind.config.ts
├── package.json
├── Dockerfile
└── .env.example
```

### 5.2 状态与数据流

```
┌─ 服务端组件 (Server Components) ─────────────────────┐
│                                                       │
│  页面首次加载：服务端直接查询 FastAPI，返回完整 HTML    │
│  · 首页新闻列表                                       │
│  · 排名表格                                           │
│  · 球员档案                                           │
│                                                       │
└───────────────────────────────────────────────────────┘
          │
          ▼
┌─ 客户端组件 (Client Components) ─────────────────────┐
│                                                       │
│  交互场景：@tanstack/react-query 管理                  │
│  · 比赛中心日期切换 → 重新请求该日赛果                 │
│  · 排名搜索/筛选                                      │
│  · 新闻列表分页加载                                    │
│  · 排名趋势图表渲染                                    │
│                                                       │
│  缓存策略：                                            │
│  · staleTime: 5min（与后端 ISR 周期对齐）              │
│  · gcTime: 30min                                      │
│                                                       │
└───────────────────────────────────────────────────────┘
```

## 6. 数据库详细设计

### 6.1 ER 关系图

```
                    ┌──────────────┐
                    │  tournaments │
                    ├──────────────┤
                    │  id (PK)     │
                    │  name        │
                    │  category    │
                    │  surface     │
                    │  location    │
                    │  start_date  │
                    │  end_date    │
                    └──────┬───────┘
                           │ 1:N
                           ▼
┌───────────┐      ┌──────────────┐      ┌───────────┐
│  players  │──N:M─│   matches    │──N:M─│  players  │
├───────────┤      ├──────────────┤      └───────────┘
│  id (PK)  │      │  id (PK)     │
│  name_en  │      │  tournament  │──FK
│  name_cn  │      │  player1     │──FK
│  country  │      │  player2     │──FK
│  ...      │      │  winner      │──FK
└─────┬─────┘      │  score       │
      │            │  stats (JSON)│
      │ 1:N        │  match_date  │
      ▼            │  round       │
┌───────────┐      │  status      │
│ rankings  │      └──────────────┘
├───────────┤
│  id (PK)  │      ┌──────────────┐
│  player   │──FK  │  articles    │
│  rank     │      ├──────────────┤
│  points   │      │  id (PK)     │
│  tour     │      │  title       │
│  type     │      │  content     │
│  week_date│      │  source      │
└───────────┘      │  category    │
                   │  published_at│
                   └──────────────┘
```

### 6.2 索引策略

```sql
-- 高频查询场景对应索引

-- 按日期查比赛（比赛中心页面核心查询）
CREATE INDEX idx_matches_date ON matches (match_date DESC);

-- 按赛事+轮次查比赛
CREATE INDEX idx_matches_tournament_round ON matches (tournament_id, round);

-- 球员的比赛记录
CREATE INDEX idx_matches_player1 ON matches (player1_id, match_date DESC);
CREATE INDEX idx_matches_player2 ON matches (player2_id, match_date DESC);

-- 新闻按时间排序 + 分类筛选
CREATE INDEX idx_articles_published ON articles (published_at DESC);
CREATE INDEX idx_articles_category ON articles (category, published_at DESC);

-- 新闻全文搜索
CREATE INDEX idx_articles_search ON articles USING GIN (search_vector);

-- 排名查询（按周 + 巡回赛类型）
CREATE INDEX idx_rankings_week ON rankings (week_date DESC, tour, type);

-- 球员排名历史
CREATE INDEX idx_rankings_player ON rankings (player_id, week_date DESC);

-- 去重：同一来源不重复入库
CREATE UNIQUE INDEX idx_articles_source_url ON articles (source_url);
```

### 6.3 物化视图（预计算）

```sql
-- 排名变动视图：每周排名与上周对比
CREATE MATERIALIZED VIEW ranking_changes AS
SELECT
    r1.player_id,
    r1.tour,
    r1.type,
    r1.week_date,
    r1.rank AS current_rank,
    r1.points AS current_points,
    r2.rank AS prev_rank,
    r2.points AS prev_points,
    COALESCE(r2.rank - r1.rank, 0) AS rank_change,
    r1.points - COALESCE(r2.points, 0) AS points_change
FROM rankings r1
LEFT JOIN rankings r2
    ON r1.player_id = r2.player_id
    AND r1.tour = r2.tour
    AND r1.type = r2.type
    AND r2.week_date = (
        SELECT MAX(week_date) FROM rankings
        WHERE week_date < r1.week_date AND tour = r1.tour AND type = r1.type
    )
WHERE r1.week_date = (
    SELECT MAX(week_date) FROM rankings WHERE tour = r1.tour AND type = r1.type
);

-- 每周一排名更新后刷新
-- REFRESH MATERIALIZED VIEW CONCURRENTLY ranking_changes;
```

## 7. 缓存策略

### 7.1 多级缓存

```
┌─────────────────────────────────────────────────────────────┐
│                       缓存层级                               │
├───────┬───────────────────┬─────────┬───────────────────────┤
│ 层级  │ 技术               │ TTL     │ 场景                  │
├───────┼───────────────────┼─────────┼───────────────────────┤
│ L1    │ Next.js ISR       │ 5-60min │ 页面级缓存，CDN 可分发 │
│ L2    │ React Query       │ 5min    │ 客户端请求级缓存       │
│ L3    │ Redis             │ 5-60min │ API 响应缓存           │
│ L4    │ PostgreSQL        │ -       │ 持久化存储             │
└───────┴───────────────────┴─────────┴───────────────────────┘
```

### 7.2 Redis 缓存 Key 设计

```
tennis:news:list:{page}:{category}       → 新闻列表    TTL 5min
tennis:news:detail:{id}                  → 新闻详情    TTL 30min
tennis:matches:date:{YYYY-MM-DD}         → 当日赛果    TTL 5min (赛事期间)
tennis:rankings:{tour}:{type}            → 排名数据    TTL 60min
tennis:player:{id}                       → 球员信息    TTL 24h
tennis:player:{id1}:vs:{id2}             → 交手记录    TTL 24h
tennis:scraper:seen_urls                 → 已抓URL集合  无TTL
```

## 8. 部署架构

### 8.1 Docker Compose 服务编排

```yaml
# docker-compose.yml 结构
services:
  nginx:        # 反向代理 + HTTPS
    ports: ["80:80", "443:443"]
    depends_on: [frontend, backend]

  frontend:     # Next.js SSR
    build: ./frontend
    expose: ["3000"]
    environment:
      - API_URL=http://backend:8000

  backend:      # FastAPI
    build: ./backend
    expose: ["8000"]
    environment:
      - DATABASE_URL=postgresql+asyncpg://...
      - REDIS_URL=redis://redis:6379/0
    depends_on: [postgres, redis]

  postgres:     # 数据库
    image: postgres:16-alpine
    volumes: ["pgdata:/var/lib/postgresql/data"]
    environment:
      - POSTGRES_DB=tennis_daily
      - POSTGRES_USER=tennis
      - POSTGRES_PASSWORD=${DB_PASSWORD}

  redis:        # 缓存
    image: redis:7-alpine
    volumes: ["redisdata:/data"]
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru

volumes:
  pgdata:
  redisdata:
```

### 8.2 Nginx 配置要点

```nginx
server {
    listen 443 ssl http2;
    server_name tennisdaily.example.com;

    # SSL (Let's Encrypt / Certbot)
    ssl_certificate     /etc/letsencrypt/live/.../fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/.../privkey.pem;

    # 前端
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # API 限流: 30 请求/秒/IP
        limit_req zone=api burst=50 nodelay;
    }

    # 静态资源长缓存
    location /_next/static/ {
        proxy_pass http://frontend:3000;
        expires 365d;
        add_header Cache-Control "public, immutable";
    }

    # Gzip
    gzip on;
    gzip_types text/css application/javascript application/json;
    gzip_min_length 1024;
}
```

### 8.3 部署流程

```
本地开发机                              云服务器
    │                                     │
    │  1. git push                        │
    │─────────────────────────────────→   │
    │                                     │  2. git pull
    │                                     │  3. docker compose build
    │                                     │  4. docker compose up -d
    │                                     │  5. alembic upgrade head (DB迁移)
    │                                     │  6. 健康检查通过
    │                                     │
```

**首次部署步骤：**

```bash
# 1. 服务器初始化
apt update && apt install -y docker.io docker-compose-v2 git
systemctl enable docker

# 2. 拉取代码
git clone <repo-url> /opt/tennis-daily
cd /opt/tennis-daily

# 3. 配置环境变量
cp .env.example .env
vim .env  # 填写 DB_PASSWORD, SECRET_KEY 等

# 4. 启动服务
docker compose up -d

# 5. 初始化数据库
docker compose exec backend alembic upgrade head

# 6. 配置 HTTPS (Let's Encrypt)
apt install certbot
certbot certonly --standalone -d tennisdaily.example.com

# 7. 手动触发首次数据抓取
docker compose exec backend python -m app.scrapers.run_all
```

## 9. 监控与运维

### 9.1 日志管理

```
所有服务日志 → Docker 日志驱动 → /var/log/tennis-daily/
    ├── nginx_access.log      (Nginx 访问日志，logrotate 每日轮转)
    ├── nginx_error.log
    ├── backend.log           (FastAPI 应用日志)
    └── scraper.log           (爬虫专用日志，含抓取成功率统计)
```

### 9.2 健康检查

```
GET /api/health  →  返回各组件状态
{
  "status": "ok",
  "database": "connected",
  "redis": "connected",
  "last_scrape": "2026-04-14T06:00:00Z",
  "article_count": 1523,
  "uptime": "3d 14h 22m"
}
```

### 9.3 告警机制

通过简单的 cron 脚本检查：
- 爬虫连续 2 次执行失败 → 发送通知（邮件/微信/Telegram Bot）
- 磁盘使用率 > 80% → 告警
- API 5xx 错误率 > 5% → 告警
- 数据库连接池耗尽 → 告警

## 10. 安全措施

| 层面 | 措施 |
|------|------|
| 传输 | 全站 HTTPS，HSTS 头 |
| API | 请求限流（Nginx + FastAPI middleware），防止爬虫滥用 |
| 数据库 | 不暴露外部端口，仅 Docker 内网访问；定期 pg_dump 备份 |
| 容器 | 非 root 用户运行，只暴露必要端口 |
| 环境变量 | 敏感配置通过 .env 注入，不入版本库 |
| 依赖 | 定期 `pip audit` / `npm audit` 检查漏洞 |
| 备份 | 每日自动 pg_dump 到独立目录，保留最近 30 天 |

## 11. 性能预估

基于单台 4C8G 服务器：

| 指标 | 预估值 |
|------|--------|
| API 平均响应时间 | < 100ms (缓存命中) / < 300ms (缓存未命中) |
| 首页加载时间 | < 1.5s (ISR 缓存命中) |
| 并发支持 | ~500 QPS (Nginx + uvicorn 4 workers) |
| 数据库容量 | ~10GB/年 (含索引) |
| 日均爬取量 | ~200-500 条数据 |
