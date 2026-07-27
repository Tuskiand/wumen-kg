# 吴门医案知识图谱管理系统

## 项目结构

- `frontend`：Vue 3 + Element Plus + G6 前端
- `backend`：FastAPI + Neo4j + MySQL 后端
- `backend/sql/init_mysql.sql`：phpStudy MySQL 初始化脚本

## 本地启动前需要启动的软件

### 1. phpStudy
必须启动：
- `Apache` 或 `Nginx`：非必须，仅在你需要用 phpMyAdmin 时方便
- `MySQL`：必须启动

当前项目默认 MySQL 配置：
- 主机：`127.0.0.1`
- 端口：`3307`
- 数据库：`wumen_graph`

### 2. Docker Desktop
必须启动：
- `Docker Desktop`
- `Neo4j` 容器

当前项目默认 Neo4j 配置：
- Browser：`http://localhost:7474`
- Bolt：`bolt://localhost:7687`

如果你的 Neo4j 容器端口不是这组，需要同步修改 `backend/.env`。

## 首次初始化

### 1. 初始化 MySQL
在 phpStudy 的 MySQL 中导入：
- `backend/sql/init_mysql.sql`

导入完成后应存在：
- 数据库：`wumen_graph`
- 表：`users`

### 2. 配置后端环境变量
检查文件：
- `backend/.env`

至少确认以下配置正确：

```env
DEMO_MODE=false

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307
MYSQL_DATABASE=wumen_graph
MYSQL_USERNAME=你的MySQL用户名
MYSQL_PASSWORD=你的MySQL密码

NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=你的Neo4j密码
NEO4J_DATABASE=neo4j
NEO4J_IMPORT_HOST_DIR=neo4j_import
NEO4J_IMPORT_CONTAINER_DIR=/import

ADMIN_USERNAME=admin
ADMIN_PASSWORD=请设置强密码
```

说明：
- `ADMIN_USERNAME` 和 `ADMIN_PASSWORD` 会在后端启动时用于初始化/修正管理员账号
- 如果 `DEMO_MODE=true`，后端会优先走演示数据，不适合当前真实导入联调

## 启动顺序

建议严格按这个顺序启动：

1. 启动 `phpStudy` 的 `MySQL`
2. 启动 `Docker Desktop`
3. 启动 `Neo4j` 容器
4. 启动后端 `FastAPI`
5. 启动前端 `Vite`

## 启动 Neo4j（Docker）

如果你还没有运行容器，可参考：

```powershell
docker run -d --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/你的密码 \
  -e NEO4J_server_directories_import=/import \
  -v ${PWD}/backend/neo4j_import:/import:ro \
  neo4j:5
```

如果容器已存在，直接启动：

```powershell
docker start neo4j
```

检查容器状态：

```powershell
docker ps
```

## 启动后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动成功后访问：
- 接口文档：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 健康检查：[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

## 启动前端

```powershell
cd frontend
npm install
npm run dev
```

前端默认地址：
- [http://localhost:5173](http://localhost:5173)

常用页面：
- 登录页：[http://localhost:5173/login](http://localhost:5173/login)
- 用户端检索：[http://localhost:5173/portal/home](http://localhost:5173/portal/home)
- 图谱探索：[http://localhost:5173/portal/graph](http://localhost:5173/portal/graph)
- 管理端控制台：[http://localhost:5173/admin/dashboard](http://localhost:5173/admin/dashboard)

## 当前本地开发是否需要启动 Nginx

本地开发阶段：
- **不需要** 单独启动 Nginx

只有在下面场景才需要：
- 前后端统一反向代理
- Docker Compose 部署
- 生产环境发布

## 当前导入方式说明

当前图谱导入为：
- `追加导入`
- 不做“同类型同名称合并”
- 管理端只接收单个三列表 CSV
- 后端会把三列表转成 Neo4j 可读的标准化临时 CSV，再通过 `LOAD CSV + Cypher` 导入

所以：
- 不会覆盖上一批图谱
- 不同批次即使同名实体也会同时保留

## 导入验证步骤

1. 登录管理端
2. 打开导入任务页
3. 选择单个三列表 CSV，表头必须严格为 `subject,relation,object`
4. 填写：
   - 来源医案
   - 导入批次
   - 可选 schema；不填则按通用图谱导入
5. 先点“开始校验”
6. 再点“执行导入”
7. 到用户端图谱探索页查看结果

## 常见问题

### 1. 后端启动报 MySQL 连接错误
先检查：
- phpStudy 的 MySQL 是否已启动
- `backend/.env` 中 `MYSQL_PORT` 是否为 `3307`
- 用户名密码是否正确
- `wumen_graph.users` 表是否存在

### 2. 后端启动报 Neo4j 连接错误
先检查：
- Docker Desktop 是否启动
- Neo4j 容器是否启动
- `7687` 是否已映射
- `backend/.env` 中 `NEO4J_URI`、用户名、密码是否正确

### 2.1 导入时提示 Neo4j 读不到 CSV
先检查：
- `backend/.env` 中 `NEO4J_IMPORT_HOST_DIR` 是否指向宿主机真实目录
- Neo4j 容器是否把该目录挂载到了 `NEO4J_IMPORT_CONTAINER_DIR`
- 启动容器时是否显式设置了 `NEO4J_server_directories_import=/import`
- 宿主机目录里是否确实生成了临时 CSV 文件

### 3. 前端页面打开但没有数据
先检查：
- 后端是否正常运行在 `8000`
- 浏览器是否能打开 `/docs`
- 是否已经导入真实 CSV
- 当前页面筛选条件是否过窄

### 4. 导入后图谱没显示
先检查：
- 是否点了“执行导入”，而不是只做“开始校验”
- 导入任务表里是否出现新增节点/关系统计
- 图谱页是否设置了来源医案筛选，导致当前批次被过滤掉
