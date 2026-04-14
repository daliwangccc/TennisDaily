#!/bin/bash
# ============================================================================
#  TennisDaily 一键环境安装脚本
#  适用系统: Ubuntu 22.04 / 24.04 LTS, Debian 12
#  用法: chmod +x setup.sh && sudo ./setup.sh
# ============================================================================

set -e

# ── 颜色定义 ─────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# ── 配置 ─────────────────────────────────────────────────────────────────────
PROJECT_DIR="/opt/tennis-daily"
PYTHON_VERSION="3.12"
NODE_VERSION="20"
PG_VERSION="16"

# ── 工具函数 ─────────────────────────────────────────────────────────────────
log_info()    { echo -e "${CYAN}[INFO]${NC}  $1"; }
log_ok()      { echo -e "${GREEN}[  OK]${NC}  $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error()   { echo -e "${RED}[FAIL]${NC}  $1"; }
separator()   { echo -e "${CYAN}──────────────────────────────────────────────────────────${NC}"; }

check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用 root 权限运行: sudo ./setup.sh"
        exit 1
    fi
}

check_os() {
    if [ ! -f /etc/os-release ]; then
        log_error "无法识别操作系统"
        exit 1
    fi
    . /etc/os-release
    if [[ "$ID" != "ubuntu" && "$ID" != "debian" ]]; then
        log_warn "当前系统: $ID $VERSION_ID — 脚本针对 Ubuntu/Debian 优化，其他发行版可能需要手动调整"
    fi
    log_ok "操作系统: $PRETTY_NAME"
}

# ── 安装计数 ─────────────────────────────────────────────────────────────────
STEP=0
TOTAL=10
step() {
    STEP=$((STEP + 1))
    echo ""
    separator
    echo -e "${GREEN}[$STEP/$TOTAL]${NC} $1"
    separator
}

# ============================================================================
#  开始安装
# ============================================================================

echo ""
echo "========================================================"
echo "   TennisDaily 服务器环境一键安装"
echo "   目标目录: $PROJECT_DIR"
echo "========================================================"
echo ""

check_root
check_os

# ── 1. 系统更新与基础工具 ────────────────────────────────────────────────────
step "系统更新 & 基础工具"

apt-get update -y
apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    build-essential \
    libffi-dev \
    libssl-dev \
    logrotate \
    htop \
    vim

log_ok "基础工具安装完成"

# ── 2. Docker & Docker Compose ───────────────────────────────────────────────
step "Docker & Docker Compose"

if command -v docker &> /dev/null; then
    DOCKER_VER=$(docker --version)
    log_warn "Docker 已安装: $DOCKER_VER — 跳过"
else
    # 添加 Docker 官方 GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/$(. /etc/os-release && echo "$ID")/gpg \
        | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    # 添加 Docker 仓库
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
      https://download.docker.com/linux/$(. /etc/os-release && echo "$ID") \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    systemctl enable docker
    systemctl start docker
    log_ok "Docker 安装完成: $(docker --version)"
fi

# Docker Compose 验证
if docker compose version &> /dev/null; then
    log_ok "Docker Compose: $(docker compose version --short)"
else
    log_error "Docker Compose 插件未安装"
    exit 1
fi

# ── 3. Nginx ─────────────────────────────────────────────────────────────────
step "Nginx"

if command -v nginx &> /dev/null; then
    log_warn "Nginx 已安装: $(nginx -v 2>&1) — 跳过"
else
    apt-get install -y nginx
    systemctl enable nginx
    systemctl start nginx
    log_ok "Nginx 安装完成: $(nginx -v 2>&1)"
fi

# ── 4. Python 3.12 ───────────────────────────────────────────────────────────
step "Python ${PYTHON_VERSION}"

if command -v python${PYTHON_VERSION} &> /dev/null; then
    log_warn "Python ${PYTHON_VERSION} 已安装: $(python${PYTHON_VERSION} --version) — 跳过"
else
    add-apt-repository -y ppa:deadsnakes/ppa 2>/dev/null || true
    apt-get update -y
    apt-get install -y \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-venv \
        python${PYTHON_VERSION}-dev
    log_ok "Python 安装完成: $(python${PYTHON_VERSION} --version)"
fi

# pip
if ! python${PYTHON_VERSION} -m pip --version &> /dev/null; then
    curl -sS https://bootstrap.pypa.io/get-pip.py | python${PYTHON_VERSION}
fi
log_ok "pip: $(python${PYTHON_VERSION} -m pip --version)"

# ── 5. Node.js 20 LTS ───────────────────────────────────────────────────────
step "Node.js ${NODE_VERSION} LTS"

if command -v node &> /dev/null; then
    CURRENT_NODE=$(node --version | cut -d'.' -f1 | tr -d 'v')
    if [ "$CURRENT_NODE" -ge "$NODE_VERSION" ]; then
        log_warn "Node.js 已安装: $(node --version) — 跳过"
    else
        log_info "Node.js 版本过低 ($(node --version))，升级中..."
    fi
fi

if ! command -v node &> /dev/null || [ "$(node --version | cut -d'.' -f1 | tr -d 'v')" -lt "$NODE_VERSION" ]; then
    curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash -
    apt-get install -y nodejs
    log_ok "Node.js 安装完成: $(node --version)"
fi

# corepack (启用 pnpm/yarn 可选)
corepack enable 2>/dev/null || true
log_ok "npm: $(npm --version)"
npm config set legacy-peer-deps true

# ── 6. PostgreSQL 16 客户端工具 ──────────────────────────────────────────────
step "PostgreSQL ${PG_VERSION} 客户端工具"

if command -v psql &> /dev/null; then
    log_warn "psql 已安装: $(psql --version) — 跳过"
else
    # 添加 PostgreSQL 官方仓库
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc \
        | gpg --dearmor -o /etc/apt/keyrings/postgresql.gpg
    echo "deb [signed-by=/etc/apt/keyrings/postgresql.gpg] \
        http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" \
        | tee /etc/apt/sources.list.d/pgdg.list > /dev/null
    apt-get update -y
    apt-get install -y postgresql-client-${PG_VERSION}
    log_ok "psql 安装完成: $(psql --version)"
fi

# ── 7. Redis 客户端工具 ──────────────────────────────────────────────────────
step "Redis 客户端工具"

if command -v redis-cli &> /dev/null; then
    log_warn "redis-cli 已安装 — 跳过"
else
    apt-get install -y redis-tools
    log_ok "redis-cli 安装完成"
fi

# ── 8. Certbot (Let's Encrypt HTTPS) ─────────────────────────────────────────
step "Certbot (Let's Encrypt)"

if command -v certbot &> /dev/null; then
    log_warn "Certbot 已安装: $(certbot --version 2>&1) — 跳过"
else
    apt-get install -y certbot python3-certbot-nginx
    log_ok "Certbot 安装完成: $(certbot --version 2>&1)"
fi

# ── 9. 项目目录初始化 ────────────────────────────────────────────────────────
step "项目目录初始化"

mkdir -p ${PROJECT_DIR}/{backend,frontend,nginx,logs,backups}

# 后端 Python 虚拟环境
if [ ! -d "${PROJECT_DIR}/backend/venv" ]; then
    python${PYTHON_VERSION} -m venv ${PROJECT_DIR}/backend/venv
    log_ok "Python 虚拟环境创建完成"
else
    log_warn "虚拟环境已存在 — 跳过"
fi

# 安装后端 Python 依赖
cat > ${PROJECT_DIR}/backend/requirements.txt << 'PYEOF'
# ── Web 框架 ──
fastapi==0.115.*
uvicorn[standard]==0.34.*
pydantic-settings==2.*

# ── 数据库 ──
sqlalchemy[asyncio]==2.0.*
asyncpg==0.30.*
alembic==1.15.*

# ── 爬虫 ──
httpx==0.28.*
beautifulsoup4==4.13.*
lxml==5.*

# ── 缓存 ──
redis[hiredis]==5.*

# ── 定时任务 ──
apscheduler==3.11.*

# ── 工具 ──
python-dotenv==1.*
PYEOF

${PROJECT_DIR}/backend/venv/bin/pip install --upgrade pip
${PROJECT_DIR}/backend/venv/bin/pip install -r ${PROJECT_DIR}/backend/requirements.txt
log_ok "Python 依赖安装完成"

# 前端 package.json
if [ ! -f "${PROJECT_DIR}/frontend/package.json" ]; then
cat > ${PROJECT_DIR}/frontend/package.json << 'JSEOF'
{
  "name": "tennis-daily-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "@tanstack/react-query": "^5.60.0",
    "dayjs": "^1.11.0",
    "recharts": "^2.15.0"
  },
  "devDependencies": {
    "typescript": "^5.6.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@types/node": "^22.0.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "eslint": "^9.0.0",
    "eslint-config-next": "^14.2.0"
  }
}
JSEOF
    log_ok "package.json 已创建"
fi
npm config set legacy-peer-deps true
cd ${PROJECT_DIR}/frontend && npm install
log_ok "前端依赖安装完成"

# ── 10. .env 模板 & 验证 ─────────────────────────────────────────────────────
step "环境变量模板 & 最终验证"

if [ ! -f "${PROJECT_DIR}/.env" ]; then
cat > ${PROJECT_DIR}/.env << 'ENVEOF'
# ============================================
#  TennisDaily 环境变量配置
#  首次部署时请修改以下值
# ============================================

# ── PostgreSQL ──
POSTGRES_DB=tennis_daily
POSTGRES_USER=tennis
POSTGRES_PASSWORD=CHANGE_ME_TO_A_STRONG_PASSWORD

# ── Redis ──
REDIS_URL=redis://redis:6379/0

# ── 后端 ──
DATABASE_URL=postgresql+asyncpg://tennis:CHANGE_ME_TO_A_STRONG_PASSWORD@postgres:5432/tennis_daily
SECRET_KEY=CHANGE_ME_TO_A_RANDOM_STRING
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info

# ── 前端 ──
NEXT_PUBLIC_API_URL=http://localhost:8000
API_URL=http://backend:8000

# ── 域名 (HTTPS 证书用) ──
DOMAIN=tennisdaily.example.com
ENVEOF
    log_ok ".env 模板已生成 → 请编辑 ${PROJECT_DIR}/.env 修改密码和域名"
else
    log_warn ".env 已存在 — 跳过"
fi

# ── 最终验证 ─────────────────────────────────────────────────────────────────
echo ""
separator
echo -e "${GREEN}  环境安装验证${NC}"
separator

check_version() {
    local name=$1
    local cmd=$2
    if eval "$cmd" &> /dev/null; then
        local ver=$(eval "$cmd" 2>&1 | head -1)
        echo -e "  ${GREEN}✓${NC}  $name: $ver"
    else
        echo -e "  ${RED}✗${NC}  $name: 未安装"
    fi
}

check_version "Docker"          "docker --version"
check_version "Docker Compose"  "docker compose version"
check_version "Nginx"           "nginx -v"
check_version "Python"          "python${PYTHON_VERSION} --version"
check_version "pip"             "python${PYTHON_VERSION} -m pip --version"
check_version "Node.js"         "node --version"
check_version "npm"             "npm --version"
check_version "psql"            "psql --version"
check_version "redis-cli"       "redis-cli --version"
check_version "Certbot"         "certbot --version"
check_version "Git"             "git --version"

echo ""
separator
echo -e "${GREEN}  Python 包 (venv)${NC}"
separator
${PROJECT_DIR}/backend/venv/bin/pip list --format=columns 2>/dev/null | grep -iE \
    "fastapi|uvicorn|sqlalchemy|asyncpg|alembic|httpx|beautifulsoup|lxml|apscheduler|redis|pydantic" \
    | while read line; do echo "  ${GREEN}✓${NC}  $line"; done

echo ""
separator
echo -e "${GREEN}  Node.js 包${NC}"
separator
cd ${PROJECT_DIR}/frontend && npm ls --depth=0 2>/dev/null | tail -n +2 \
    | while read line; do echo "  ${GREEN}✓${NC} $line"; done

# ── 完成 ─────────────────────────────────────────────────────────────────────
echo ""
echo "========================================================"
echo -e "${GREEN}  安装完成！${NC}"
echo "========================================================"
echo ""
echo "  项目目录:  ${PROJECT_DIR}"
echo "  后端venv:  ${PROJECT_DIR}/backend/venv"
echo "  前端目录:  ${PROJECT_DIR}/frontend"
echo ""
echo "  后续步骤:"
echo "  ────────"
echo "  1. 编辑环境变量:   vim ${PROJECT_DIR}/.env"
echo "  2. 启动服务:       cd ${PROJECT_DIR} && docker compose up -d"
echo "  3. 初始化数据库:   docker compose exec backend alembic upgrade head"
echo "  4. 配置HTTPS:      certbot --nginx -d your-domain.com"
echo ""
echo "========================================================"
