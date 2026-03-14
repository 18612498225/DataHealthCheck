# 数据质量平台 PC 版技术文档

**文档名称**：DataHealthCheck 数据质量平台 PC 版技术方案  
**文档版本**：V1.1  
**编写日期**：2025-03  
**更新日期**：2025-03  
**文档依据**：PRD_数据质量评估产品需求文档.md  
**目标**：可研发落地的技术架构与实现方案  
**实现状态**：核心功能已实现（数据源、规则集、任务、报告、剖析、用户管理）  

---

## 一、技术选型与 rationale

### 1.1 总体技术栈

| 层级 | 技术选型 | 版本建议 | 选型理由 |
|------|----------|----------|----------|
| **后端框架** | FastAPI | 0.109+ | 异步高性能、自动 OpenAPI 文档、Pydantic 原生支持、Python 生态 |
| **数据处理** | Pandas | 2.0+ | 行业标准、与现有 DataHealthCheck 引擎兼容、易扩展 |
| **ORM / 数据库** | SQLAlchemy 2.0 + SQLite/PostgreSQL | 2.0+ | 轻量可先 SQLite，生产可切 PostgreSQL；SQLAlchemy 与 FastAPI 生态成熟 |
| **任务队列** | Celery + Redis / 或 APScheduler | - | 长任务异步化；小规模可用 APScheduler 内置 |
| **前端框架** | Vue 3 + TypeScript + Vite | Vue 3.4+, Vite 5 | 与 FastAPI 社区案例多、Element Plus 组件成熟、适合 PC 管理端 |
| **UI 组件** | Element Plus | 2.5+ | 表格、表单、图表丰富，适合数据类管理后台 |
| **图表** | ECharts / Apache ECharts | 5.x | 报告可视化、质量趋势图、饼图/柱状图 |
| **认证** | JWT + OAuth2 | - | FastAPI 内置支持，满足 RBAC 扩展 |

### 1.2 与 PRD 及行业实践的对应

| PRD 能力 | 技术实现 |
|----------|----------|
| 数据接入 | Pandas + SQLAlchemy（数据库源）+ openpyxl（Excel） |
| 规则引擎 | 复用现有 `data_quality_tool` + FastAPI 封装 |
| 数据剖析 | Pandas `describe()` + 自定义 Profiling 模块 |
| 报告输出 | Jinja2 渲染 HTML / FastAPI 返回 JSON |
| Checkpoint | 数据库存储 checkpoint 配置，API 触发执行 |
| Web 控制台 | Vue 3 + Element Plus 单页应用 |

---

## 二、系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              数据质量平台 PC 版                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         前端 (Vue 3 + Vite + Element Plus)                 │   │
│  │  数据源管理 | 规则管理 | 任务执行 | 报告查看 | 质量仪表盘 | 用户/权限          │   │
│  └───────────────────────────────────────┬─────────────────────────────────┘   │
│                                          │ HTTP/WebSocket                        │
│  ┌───────────────────────────────────────▼─────────────────────────────────┐   │
│  │                        FastAPI 后端 (API Gateway)                         │   │
│  │  /api/datasources  /api/rules  /api/tasks  /api/reports  /api/profiling  │   │
│  └───────────────────────────────────────┬─────────────────────────────────┘   │
│                                          │                                       │
│  ┌───────────────────────┬───────────────┴───────────────┬─────────────────────┐ │
│  │ 数据质量核心引擎       │ 任务调度 / 异步执行            │ 持久化               │ │
│  │ (data_quality_tool)   │ Celery / APScheduler          │ SQLite / PostgreSQL │ │
│  │ • loaders             │ • 定时任务                     │ • 数据源、规则       │ │
│  │ • assessment_engine   │ • 异步评估任务                 │ • 任务、结果、报告   │ │
│  │ • checks              │                               │                     │ │
│  │ • profiling (新增)    │                               │                     │ │
│  └───────────────────────┴───────────────────────────────┴─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 分层说明

| 层 | 职责 | 主要技术 |
|----|------|----------|
| 表现层 | PC Web 控制台、API 调用、认证 | Vue 3, Element Plus, Axios |
| 接口层 | REST API、请求校验、鉴权 | FastAPI, Pydantic |
| 业务层 | 数据接入、规则执行、剖析、报告生成 | Pandas, data_quality_tool |
| 调度层 | 定时任务、异步任务 | APScheduler / Celery |
| 持久层 | 元数据、任务记录、报告存储 | SQLAlchemy, SQLite/PostgreSQL |

---

## 三、项目结构

### 3.1 目录结构

```
DataHealthCheck/
├── backend/                      # FastAPI 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI 入口
│   │   ├── config.py             # 配置
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── datasources.py
│   │   │   │   ├── rule_sets.py
│   │   │   │   ├── tasks.py
│   │   │   │   ├── reports.py
│   │   │   │   ├── profiling.py
│   │   │   │   ├── auth.py
│   │   │   │   └── users.py
│   │   │   └── deps.py           # 依赖注入
│   │   ├── core/
│   │   │   ├── security.py       # JWT
│   │   │   └── exceptions.py
│   │   ├── models/               # SQLAlchemy 模型
│   │   │   ├── datasource.py
│   │   │   ├── rule_set.py
│   │   │   ├── task.py
│   │   │   ├── assessment_result.py
│   │   │   ├── user.py
│   │   │   └── role.py
│   │   ├── schemas/              # Pydantic 模型
│   │   ├── services/
│   │   │   ├── data_loader.py    # 多源加载（CSV/Excel/PostgreSQL/MySQL）
│   │   │   ├── assessment.py     # 调用 data_quality_tool
│   │   │   ├── profiling.py
│   │   │   ├── report.py         # 英文报告
│   │   │   └── report_cn.py      # 中国标准报告格式（GB/T 36344）
│   │   └── db/                   # 数据库
│   │       ├── database.py
│   │       └── base.py
│   ├── data_quality_tool/        # 复用/迁移现有引擎
│   │   ├── data_loader.py
│   │   ├── assessment_engine.py
│   │   ├── checks.py
│   │   ├── reporter.py
│   │   └── profiling.py          # 新增
│   ├── requirements.txt
│   └── alembic/                  # 迁移（可选）
│
├── frontend/                     # Vue 3 前端
│   ├── src/
│   │   ├── api/
│   │   ├── views/
│   │   │   ├── Datasource/
│   │   │   ├── Rule/
│   │   │   ├── Task/
│   │   │   ├── Report/
│   │   │   └── Dashboard/
│   │   ├── components/
│   │   ├── router/
│   │   ├── store/
│   │   └── App.vue
│   ├── package.json
│   └── vite.config.ts
│
├── docs/
├── docker-compose.yml            # 本地开发
└── README.md
```

### 3.2 与现有 DataHealthCheck 的关系

- **复用**：`data_quality_tool` 下 `data_loader`、`assessment_engine`、`checks`、`reporter` 作为核心引擎，通过 `services.assessment` 调用
- **扩展**：新增 `profiling.py`、多数据源 Loader、Checkpoint 逻辑
- **封装**：FastAPI 提供 REST API，CLI 仍可独立使用

---

## 四、数据模型设计

### 4.1 核心表结构

#### 数据源 (datasource)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| name | VARCHAR(128) | 名称 |
| source_type | VARCHAR(32) | csv / excel / postgres / mysql / sqlite |
| config | JSONB | 连接配置（路径、连接串等） |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

#### 规则集 (rule_set)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| name | VARCHAR(128) | 规则集名称 |
| description | TEXT | 描述 |
| rules | JSONB | 规则数组（与现有 JSON 结构一致） |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

#### 任务 (task)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| name | VARCHAR(128) | 任务名称 |
| datasource_id | UUID | FK |
| rule_set_id | UUID | FK |
| status | VARCHAR(32) | pending / running / completed / failed |
| trigger_type | VARCHAR(32) | manual / schedule |
| started_at | TIMESTAMP | 开始时间 |
| finished_at | TIMESTAMP | 结束时间 |
| created_at | TIMESTAMP | |

#### 评估结果 (assessment_result)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| task_id | UUID | FK |
| summary | JSONB | 总览 {total, passed, failed} |
| details | JSONB | 每条规则的检查结果 |
| report_html | TEXT | HTML 报告（可选存储） |
| created_at | TIMESTAMP | |

### 4.2 简化的 SQLAlchemy 示例

```python
# models/datasource.py
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from datetime import datetime

class Datasource(Base):
    __tablename__ = "datasources"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(128), nullable=False)
    source_type = Column(String(32), nullable=False)  # csv, excel, postgres, ...
    config = Column(JSON, nullable=False)  # {"path": "..."} or {"url": "..."}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## 五、API 设计

### 5.1 REST API 一览

| 模块 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 数据源 | GET | /api/v1/datasources | 列表 |
| | POST | /api/v1/datasources | 创建 |
| | GET | /api/v1/datasources/{id} | 详情 |
| | DELETE | /api/v1/datasources/{id} | 删除 |
| 规则集 | GET | /api/v1/rule-sets | 列表 |
| | POST | /api/v1/rule-sets | 创建 |
| | GET | /api/v1/rule-sets/{id} | 详情 |
| | PUT | /api/v1/rule-sets/{id} | 更新 |
| | DELETE | /api/v1/rule-sets/{id} | 删除 |
| 任务 | POST | /api/v1/tasks/run | 立即执行（同步/异步） |
| | GET | /api/v1/tasks | 任务列表 |
| | GET | /api/v1/tasks/{id} | 任务详情 |
| | GET | /api/v1/tasks/{id}/result | 评估结果 |
| 报告 | GET | /api/v1/reports/{task_id} | 获取报告（JSON/HTML/中文标准格式） |
| | GET | /api/v1/reports/{task_id}/download | 下载 HTML/JSON |
| 剖析 | POST | /api/v1/profiling | 对数据源执行剖析 |
| | GET | /api/v1/profiling/{task_id} | 获取剖析结果 |
| 用户 | GET | /api/v1/users | 用户列表（管理员） |
| | POST | /api/v1/users | 创建用户 |
| 认证 | POST | /api/v1/auth/login | 登录获取 JWT |

### 5.2 关键接口示例

#### 5.2.1 立即执行评估

```http
POST /api/v1/tasks/run
Content-Type: application/json

{
  "name": "入湖前校验_20250313",
  "datasource_id": "uuid",
  "rule_set_id": "uuid",
  "async": false
}

Response 200:
{
  "task_id": "uuid",
  "status": "completed",
  "result": {
    "summary": {"total": 7, "passed": 5, "failed": 2},
    "details": [...]
  }
}
```

#### 5.2.2 数据剖析

```http
POST /api/v1/profiling
Content-Type: application/json

{
  "datasource_id": "uuid",
  "sample_size": 10000
}

Response 200:
{
  "columns": [
    {
      "name": "id",
      "dtype": "int64",
      "non_null_count": 1000,
      "null_count": 0,
      "unique_count": 1000,
      "suggested_rules": ["completeness", "uniqueness"]
    },
    ...
  ]
}
```

---

## 六、前端技术方案

### 6.1 技术栈

| 类别 | 选型 | 说明 |
|------|------|------|
| 框架 | Vue 3 + Composition API | 组合式 API，逻辑复用方便 |
| 语言 | TypeScript | 类型安全，与 FastAPI 的 Pydantic 对应 |
| 构建 | Vite 5 | 快速 HMR，与 Vue 3 适配好 |
| UI | Element Plus | 表格、表单、布局、消息提示 |
| 图表 | Apache ECharts | 质量趋势、通过率、分布图 |
| 请求 | Axios | HTTP 客户端，可封装拦截器 |
| 路由 | Vue Router 4 | 单页路由 |
| 状态 | Pinia | Vue 3 推荐，轻量 |

### 6.2 页面与路由

| 路由 | 页面 | 功能 |
|------|------|------|
| /login | 登录 | 用户名密码 / JWT |
| /dashboard | 仪表盘 | 质量概览、最近任务、快捷入口 |
| /datasources | 数据源管理 | 列表、新增、编辑、删除、测试连接 |
| /rules | 规则管理 | 规则集列表、规则编辑器（JSON）、校验 |
| /tasks | 任务中心 | 执行任务、历史列表、结果查看 |
| /reports | 报告中心 | 按任务查看报告、下载 HTML/JSON |
| /profiling | 数据剖析 | 选择数据源、执行剖析、查看列统计、规则推荐 |
| /users | 用户管理 | 用户列表、创建用户（管理员） |

### 6.3 核心组件建议

- `DataTable`：数据源列表、任务列表
- `RuleEditor`：规则 JSON/YAML 编辑 + 高亮
- `ReportViewer`：报告 HTML 展示、筛选、折叠
- `QualityChart`：ECharts 封装（饼图、柱状图）
- `ProfilingResult`：列级统计表格、规则推荐卡片

---

## 七、开发阶段与里程碑

### 7.1 阶段划分

| 阶段 | 周期 | 交付物 | 优先级 |
|------|------|--------|--------|
| **M1：基础后端** | 2 周 | FastAPI 骨架、数据源/规则 CRUD、复用现有引擎执行评估、SQLite | P0 |
| **M2：核心 API** | 1.5 周 | 任务执行 API、报告 API、JSON/HTML 报告 | P0 |
| **M3：前端骨架** | 2 周 | Vue 3 项目、登录、布局、数据源/规则页面 | P0 |
| **M4：任务与报告** | 1.5 周 | 任务执行、报告查看、下载 | P0 |
| **M5：剖析与增强** | 2 周 | 数据剖析 API、前端剖析页、规则推荐 | P1 |
| **M6：优化与部署** | 1 周 | 异步任务、编码参数、Docker、文档 | P1 |

### 7.2 最小可用版本 (MVP)

- 数据源管理（CSV 文件）
- 规则集 CRUD
- 手动触发评估
- 查看评估结果与报告
- 基础登录与权限（可先单用户）

---

## 八、依赖清单

### 8.1 后端 (requirements.txt)

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.0
pydantic-settings>=2.0.0
sqlalchemy>=2.0
pandas>=2.0
python-multipart
jinja2>=3.1
openpyxl>=3.1.0    # Excel
psycopg2-binary    # PostgreSQL
pymysql            # MySQL
bcrypt>=4.0.0
xhtml2pdf          # PDF 报告导出
```

### 8.2 前端 (package.json 核心)

```json
{
  "dependencies": {
    "vue": "^3.4",
    "vue-router": "^4.2",
    "pinia": "^2.1",
    "element-plus": "^2.5",
    "axios": "^1.6",
    "echarts": "^5.4",
    "@element-plus/icons-vue": "^2.3"
  },
  "devDependencies": {
    "typescript": "^5.3",
    "vite": "^5.0",
    "@vitejs/plugin-vue": "^5.0"
  }
}
```

---

## 九、部署方案

### 9.1 开发环境

```bash
# 后端（Windows 推荐使用 start.ps1）
cd backend
pip install -r requirements.txt
python -m app.db.init_db
python seed_data.py
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 或 Windows PowerShell: .\start.ps1

# 前端
cd frontend && npm install && npm run dev

# 数据库
# SQLite 默认，无需额外启动
```

### 9.2 生产部署（Docker）

```yaml
# docker-compose.yml 示意
version: "3.8"
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [db, redis]
  frontend:
    build: ./frontend
    ports: ["80:80"]
    depends_on: [backend]
  db:
    image: postgres:16-alpine
    volumes: [pgdata:/var/lib/postgresql/data]
  redis:
    image: redis:7-alpine
```

### 9.3 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| DATABASE_URL | 数据库连接串 | sqlite:///./app.db 或 postgresql://... |
| SECRET_KEY | JWT 密钥 | 随机长字符串 |
| CORS_ORIGINS | 允许的前端域名 | http://localhost:5173 |
| REDIS_URL | Redis（Celery 用） | redis://redis:6379/0 |

---

## 十、安全与扩展

### 10.1 安全

- API 鉴权：JWT + OAuth2 密码流
- CORS 配置白名单
- 文件上传：限制类型、大小，路径校验防目录遍历
- SQL 注入：使用 ORM/参数化，避免拼接
- 敏感配置：数据库连接串、密钥等走环境变量

### 10.2 扩展点

- **多数据源**：通过 `Loader` 抽象，新增 ExcelLoader、PostgresLoader 等
- **新规则类型**：在 `checks.py` 增加函数，在 `assessment_engine` 注册
- **报告模板**：Jinja2 模板可配置，支持多语言、多风格
- **插件/钩子**：任务前后、规则执行前后的扩展点（可选）

---

## 十一、与 PRD 的对应关系

| PRD 章节 | 技术实现 |
|----------|----------|
| 五、功能需求 数据接入 | `services.data_loader` + Loader 抽象 |
| 五、规则管理 | `rule_set` 表 + `rules` JSONB |
| 五、检查执行 | `services.assessment` 调用 `AssessmentEngine` |
| 五、报告输出 | `services.report` + Jinja2 HTML + JSON 接口 |
| 十、数据剖析 | `profiling.py` + `/api/v1/profiling` |
| 十、Checkpoint | `task` 表 + 定时任务 / 手动触发 |
| 十、Python API | FastAPI 即提供 HTTP API，可额外封装 `DataQuality` 类供 CLI/SDK 调用 |

---

## 十二、附录

### 12.1 参考项目

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Element Plus](https://element-plus.org/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Vue 3 + Vite](https://vuejs.org/guide/quick-start.html)
- PRD 第十节中的 Great Expectations、Soda、ydata-quality 等

### 12.2 名词对照

| 英文 | 中文 |
|------|------|
| Datasource | 数据源 |
| Rule Set | 规则集 |
| Assessment | 评估 |
| Profiling | 剖析 |
| Checkpoint | 检查点 |

---

*文档结束*
