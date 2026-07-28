# 吴门医案知识图谱管理系统

面向《吴门医案》知识组织、检索、图谱探索、图谱维护和医家辨证比较的前后端分离系统。

项目包含两种使用方式：

- **在线演示**：[https://wumen-kg-a54e.vercel.app](https://wumen-kg-a54e.vercel.app)，纯前端演示模式，不依赖 MySQL 和 Neo4j，适合答辩展示和 GitHub/Vercel 预览。
- **本地完整运行**：启动前端、后端、MySQL、Neo4j，适合真实数据导入、图谱查询和算法联调。

## 一、用户使用说明

### 1. 演示模式说明

当前 Vercel 部署使用纯前端演示模式：

- 演示地址：[https://wumen-kg-a54e.vercel.app](https://wumen-kg-a54e.vercel.app)
- 管理员演示账号：`admin`，密码可填 `123456` 或任意内容
- 普通用户演示账号：`demo`，密码可填 `123456` 或任意内容
- 也可以点击注册，自定义用户名和密码；注册后会自动登录为普通用户
- 不需要启动后端
- 不需要连接 MySQL
- 不需要连接 Neo4j
- 页面数据来自前端内置演示数据
- 注册和管理操作只用于演示，不会写入线上数据库

### 2. 登录方式

| 角色 | 用户名 | 密码 | 进入页面 |
| --- | --- | --- | --- |
| 管理员 | `admin` | 任意密码，例如 `123456` | 后台管理 |
| 普通用户 | `demo` | 任意密码，例如 `123456` | 用户端 |
| 注册用户 | 自定义用户名 | 自定义密码 | 用户端 |

说明：

- 演示模式下密码不会真实校验。
- 注册成功后会自动登录为普通用户。
- 注册数据只存在当前浏览器页面状态中，不代表真实账号系统。

### 3. 用户端功能

| 功能 | 页面 | 用途 |
| --- | --- | --- |
| 首页概览 | `/portal/home` | 查看图谱统计和快捷入口 |
| 知识检索 | `/portal/home` | 按关键词、实体类型、来源筛选节点 |
| 图谱探索 | `/portal/graph` | 查看节点和关系网络，可缩放、拖拽、筛选 |
| 实体详情 | `/portal/entity/:id` | 查看某个实体的摘要、来源和相邻关系 |
| 路径查询 | `/portal/path` | 查询两个实体之间的关系路径 |
| 医家比较 | `/portal/physician-compare` | 比较不同医家对同一病名的辨证差异 |

### 4. 管理端功能

管理员账号登录后可进入后台：

| 功能 | 页面 | 用途 |
| --- | --- | --- |
| 管理看板 | `/admin/dashboard` | 查看节点、关系、导入任务统计 |
| 实体管理 | `/admin/entities` | 新增、编辑、删除图谱节点 |
| 关系管理 | `/admin/relations` | 新增、编辑、删除图谱关系 |
| 图谱导入 | `/admin/imports` | 上传三列表 CSV，校验并执行导入 |
| 版本记录 | `/admin/versions` | 查看图谱版本记录 |
| 审计记录 | `/admin/audits` | 查看系统操作记录 |
| 用户管理 | `/admin/users` | 管理用户、角色和启用状态 |

### 5. 导入文件格式

真实后端模式下，管理端导入只接收单个三列表 CSV：

```csv
subject,relation,object
薛雪(A医家),病名为,中风(B病名)
中风(B病名),证型为,风痰闭阻证(C证型)
风痰闭阻证(C证型),病机为,痰瘀阻络(E病机)
```

要求：

- 表头必须严格为 `subject,relation,object`
- `subject` 和 `object` 必须使用 `名称(类型)` 格式
- 每次导入需要填写来源医案和导入批次
- 当前导入策略是追加导入，不会覆盖旧图谱

## 二、开发者使用说明

### 1. 技术栈

| 层级 | 技术 |
| --- | --- |
| 前端 | Vue 3、TypeScript、Vite、Element Plus、Vue Router、ECharts |
| 后端 | FastAPI、Pydantic、SQLAlchemy、PyMySQL、Neo4j Python Driver、JWT |
| 数据库 | MySQL、Neo4j |
| 图分析 | Neo4j GDS、NetworkX、NumPy |
| 部署 | Vercel 前端演示部署，Docker Compose 辅助本地 Neo4j |

### 2. 项目结构

```text
wumen-kg/
├─ frontend/              # Vue 前端
├─ backend/               # FastAPI 后端
├─ backend/sql/           # MySQL 初始化脚本
├─ test/                  # 后端单元测试
├─ tools/                 # 数据转换辅助脚本
├─ archive/               # 归档文档：DESIGN / 需求 / 方案
├─ compose.yaml           # 本地 Neo4j/GDS 容器配置
└─ README.md              # 项目说明
```

### 3. 前端演示模式

适合只展示前端，不启动数据库：

```powershell
cd frontend
npm install
npm run dev -- --mode demo
```

构建演示版本：

```powershell
cd frontend
npm run build:demo
```

演示模式由 `frontend/.env.demo` 控制：

```env
VITE_DEMO_MODE=true
```

Vercel 部署配置位于：

```text
frontend/vercel.json
```

当前配置：

- Install Command：`npm ci`
- Build Command：`npm run build:demo`
- Output Directory：`dist`
- Root Directory：`frontend`

### 4. 本地完整运行

完整模式需要同时启动：

1. phpStudy MySQL
2. Docker Desktop
3. Neo4j 容器
4. FastAPI 后端
5. Vite 前端

### 5. 环境变量

复制示例文件后再填写真实密码：

```powershell
copy .env.example .env
copy backend\.env.example backend\.env
```

根目录 `.env` 用于 Docker Compose：

```env
NEO4J_AUTH=neo4j/replace-with-neo4j-password
```

后端 `backend/.env` 至少需要：

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

注意：

- `.env` 和 `backend/.env` 不要提交到 GitHub。
- 公开仓库只保留 `.env.example` 和 `backend/.env.example`。

### 6. 初始化 MySQL

在 phpStudy 的 MySQL 中导入：

```text
backend/sql/init_mysql.sql
```

导入后应存在：

- 数据库：`wumen_graph`
- 表：`users`

### 7. 启动 Neo4j

使用 Docker Compose：

```powershell
docker compose up -d neo4j
```

访问：

- Neo4j Browser：`http://localhost:7474`
- Bolt：`bolt://localhost:7687`

### 8. 启动后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

验证：

- API 文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/health`

### 9. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

默认地址：

```text
http://localhost:5173
```

### 10. 测试

后端测试位于 `test/`：

```powershell
python -m unittest discover -s test
```

前端构建检查：

```powershell
cd frontend
npm run build:demo
```

### 11. 常见问题

| 问题 | 检查项 |
| --- | --- |
| 后端 MySQL 连接失败 | phpStudy MySQL 是否启动；端口是否为 `3307`；账号密码是否正确 |
| 后端 Neo4j 连接失败 | Docker Desktop 是否启动；Neo4j 容器是否运行；`7687` 是否映射 |
| 导入时 Neo4j 读不到 CSV | `backend/neo4j_import` 是否挂载到容器 `/import` |
| 前端没有真实数据 | 后端是否启动；是否导入过 CSV；筛选条件是否过窄 |
| Vercel 部署失败 | Root Directory 是否为 `frontend`；构建命令是否为 `npm run build:demo` |

## 三、公开仓库说明

本仓库是毕业设计项目的安全存档版本：

- 已排除真实 `.env`
- 已排除本地数据库数据、日志、插件目录和构建产物
- 已排除 `node_modules`
- 前端演示模式可直接部署到 Vercel

不应提交：

- 数据库账号密码
- GitHub/Vercel Token
- MySQL/Neo4j 真实数据目录
- `frontend/node_modules`
- `frontend/dist`
- `backend/neo4j_import`

历史文档已归档到 `archive/`。
