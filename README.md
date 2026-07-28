# 吴门医案知识图谱管理系统

一套面向《吴门医案》的知识图谱管理与分析系统，支持图谱检索、实体详情、路径查询、医家比较、图谱维护和 CSV 导入。

项目提供两种运行方式：

- **在线演示**：纯前端模式，适合 GitHub 预览和 Vercel 部署。
- **本地完整运行**：前后端联调，适合真实数据导入和图谱分析。

## 演示

| 项目 | 说明 |
| --- | --- |
| 演示地址 | [https://wumen-kg-a54e.vercel.app](https://wumen-kg-a54e.vercel.app) |
| 管理员账号 | `admin` / 任意密码，如 `123456` |
| 普通用户账号 | `demo` / 任意密码，如 `123456` |
| 注册方式 | 任意用户名和密码，注册后自动登录为普通用户 |
| 数据来源 | 前端内置演示数据 |
| 运行依赖 | 不需要 MySQL，不需要 Neo4j，不需要后端 |

## 功能

| 模块 | 功能 |
| --- | --- |
| 用户端 | 首页概览、知识检索、图谱探索、实体详情、路径查询、医家比较 |
| 管理端 | 节点管理、关系管理、图谱导入、用户管理、版本记录、审计记录 |
| 演示模式 | 登录、注册、页面浏览、图谱查看均可使用 |
| 部署 | 支持 Vercel 前端演示部署 |

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 前端 | Vue 3、TypeScript、Vite、Element Plus、Vue Router、ECharts |
| 后端 | FastAPI、Pydantic、SQLAlchemy、PyMySQL、Neo4j Python Driver、JWT |
| 数据库 | MySQL、Neo4j |
| 图分析 | Neo4j GDS、NetworkX、NumPy |
| 部署 | Vercel、Docker Compose |

## 仓库结构

```text
wumen-kg/
├─ frontend/              # Vue 前端
├─ backend/               # FastAPI 后端
├─ backend/sql/           # MySQL 初始化脚本
├─ test/                  # 后端单元测试
├─ tools/                 # 数据转换辅助脚本
├─ archive/               # 归档文档
├─ compose.yaml           # 本地 Neo4j 容器配置
└─ README.md              # 项目说明
```

## 快速开始

### 在线演示

直接打开演示地址即可：

[https://wumen-kg-a54e.vercel.app](https://wumen-kg-a54e.vercel.app)

### 本地演示模式

只启动前端演示，不依赖数据库：

```powershell
cd frontend
npm install
npm run dev -- --mode demo
```

构建演示版：

```powershell
cd frontend
npm run build:demo
```

### 本地完整运行

1. 复制环境变量示例文件。
2. 启动 MySQL 和 Neo4j。
3. 导入 `backend/sql/init_mysql.sql`。
4. 启动后端服务。
5. 启动前端服务。

```powershell
copy .env.example .env
copy backend\.env.example backend\.env
docker compose up -d neo4j
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
cd ..\frontend
npm install
npm run dev
```

## 环境变量

### 根目录 `.env`

用于 Docker Compose：

```env
NEO4J_AUTH=neo4j/replace-with-neo4j-password
```

### `backend/.env`

后端至少需要以下配置：

```env
APP_NAME=WuMen Medical Graph API
APP_VERSION=0.1.0
API_PREFIX=/api/v1
DEBUG=true
DEMO_MODE=false

JWT_SECRET_KEY=replace-with-long-random-secret
ADMIN_USERNAME=admin
ADMIN_PASSWORD=replace-with-admin-password

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307
MYSQL_DATABASE=wumen_graph
MYSQL_USERNAME=replace-with-mysql-user
MYSQL_PASSWORD=replace-with-mysql-password

NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=replace-with-neo4j-password
NEO4J_DATABASE=neo4j
NEO4J_IMPORT_HOST_DIR=neo4j_import
NEO4J_IMPORT_CONTAINER_DIR=/import
```

## 部署

Vercel 前端演示配置位于 `frontend/vercel.json`：

| 项目 | 配置 |
| --- | --- |
| Root Directory | `frontend` |
| Install Command | `npm ci` |
| Build Command | `npm run build:demo` |
| Output Directory | `dist` |

## 文档归档

历史文档已移动到 `archive/`：

- `archive/DESIGN.md`
- `archive/wumen_requirements_filled.md`
- `archive/physician_compare_plan.md`

## 说明

- `.env`、`backend/.env`、`node_modules`、`dist` 不纳入仓库。
- 真实数据库和私密配置不提交到 GitHub。
- 演示模式只用于展示，不代表后端联调结果。
