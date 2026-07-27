# WuMen Medical Graph API

## 后端用途

本服务负责：
- 用户认证与权限控制
- Neo4j 图谱查询与导入
- MySQL 用户体系管理
- 管理端节点、关系、导入任务接口

## 依赖软件

启动后端前，请先确认以下软件已启动：

### 1. phpStudy MySQL
必须启动 MySQL。

默认配置：
- Host：`127.0.0.1`
- Port：`3307`
- Database：`wumen_graph`

### 2. Docker Desktop + Neo4j
必须启动：
- `Docker Desktop`
- `Neo4j` 容器

默认配置：
- Browser：`http://localhost:7474`
- Bolt：`bolt://localhost:7687`

## 首次初始化

### 1. 导入 MySQL 初始化脚本
导入文件：
- `backend/sql/init_mysql.sql`

### 2. 配置环境变量
复制并检查：
- `backend/.env.example`
- `backend/.env`

推荐最少配置：

```env
APP_NAME=WuMen Medical Graph API
APP_VERSION=0.1.0
API_PREFIX=/api/v1
DEBUG=true
DEMO_MODE=false

JWT_SECRET_KEY=请设置长随机密钥
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=120

ADMIN_USERNAME=admin
ADMIN_PASSWORD=请设置强密码

NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=你的Neo4j密码
NEO4J_DATABASE=neo4j

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307
MYSQL_DATABASE=wumen_graph
MYSQL_USERNAME=你的MySQL用户名
MYSQL_PASSWORD=你的MySQL密码
```

## 启动命令
conda activate KG
### 后端

```powershell
conda activate KG
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端

```powershell
conda activate KG
cd frontend
npm run dev
```

## 启动成功后验证

打开：
- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

## 当前导入策略

当前真实导入为：
- 追加导入
- 不做实体名称合并
- 不同批次使用批次前缀隔离节点/关系 ID
- 管理端只接收单个三列表 CSV
- 导入时由后端使用 `LOAD CSV + Cypher` 写入 Neo4j

例如：
- `2026Q1-卷一::case-001`
- `2026Q2-卷二::case-001`

因此：
- 多批次导入不会互相覆盖
- 同名实体会作为不同批次节点共同存在

## 常见问题

### 1. Application startup failed
优先检查：
- MySQL 是否已启动
- Neo4j 是否已启动
- `.env` 中 MySQL / Neo4j 用户名密码是否正确
- `DEMO_MODE` 是否符合当前联调目标

### 2. `wumen_graph.users` 不存在
说明：
- 还没有导入 `backend/sql/init_mysql.sql`

### 3. bcrypt 相关报错
执行：

```powershell
pip install -r requirements.txt --force-reinstall
```

## 本地开发说明

- 本地开发阶段不需要单独启动 Nginx
- 前端默认从 `http://127.0.0.1:8000/api/v1` 请求后端
- 如需修改端口，请同步调整前端环境变量或接口基础地址
