# 数据质量评估产品需求文档 (PRD)

**产品名称**：DataHealthCheck 数据质量评估工具  
**文档版本**：V1.2  
**编写日期**：2025-03  
**更新日期**：2025-03  
**文档状态**：持续更新（Web 平台核心功能已实现）  
**角色**：产品经理 / 研发工程师  

---

## 行业对标说明

本章节基于 GitHub 上成熟数据质量产品的实践，对本 PRD 提出升级与优化建议。主要参考产品：

| 产品 | GitHub Stars | 核心能力 | 参考来源 |
|------|--------------|----------|----------|
| [Great Expectations](https://github.com/great-expectations/great_expectations) | 11k+ | Expectations、Data Docs、Checkpoint、CI/CD | 行业标杆 |
| [Soda Core](https://github.com/sodadata/soda-core) | 1.8k+ | Data Contracts、多源、SodaCL 语法 | 现代数据栈 |
| [ydata-quality](https://github.com/ydataai/ydata-quality) | 440+ | 一行评估、画像、漂移、偏差 | 快速评估 |
| [Pandera](https://github.com/pandera-dev/pandera) | 4k+ | Schema 校验、Pipeline 装饰器、多后端 | 工程集成 |
| [DQOps](https://github.com/dqops/dqo) | 140+ | UI、YAML 配置、自动化调度 | 企业可观测 |

---

## 一、文档说明

### 1.1 文档目的

本 PRD 描述数据质量评估产品的完整需求，作为研发、测试和交付的依据，确保产品符合数据健康检查行业规范及数据要素市场建设要求。

### 1.2 适用范围

- 数据治理团队
- 数据工程师 / 数据分析师
- 数据产品研发团队
- 数据要素流通相关方

### 1.3 参考标准

| 标准/规范 | 说明 |
|----------|------|
| DAMA-DMBOK 2.0 | 数据管理知识体系，六维数据质量框架 |
| ISO 8000 | 主数据质量管理国际标准 |
| GB/T 36344-2018 | 信息技术 数据质量评价指标 |
| 《数据要素流通标准化白皮书》 | 数据要素市场相关规范 |
| 《数据管理能力成熟度评估模型》(DCMM) | 数据管理成熟度评估 |

---

## 二、产品概述

### 2.1 产品定位

DataHealthCheck 是一款**可配置、规则驱动、自动化**的数据质量评估工具，面向结构化数据（以 CSV 为代表），对数据进行多维度质量检查，并输出可读、可追溯的评估报告，支持数据治理、数据入湖、数据流通前的质量把关场景。

### 2.2 产品愿景

- **短期**：成为轻量、易用的本地化数据质量评估工具，支撑中小规模数据集的质量检查
- **中期**：支持多数据源、多报告格式、可扩展规则库，满足企业级数据治理需求
- **长期**：支持与数据目录、数据血缘、数据安全等平台集成，形成完整的数据健康管理体系

### 2.3 核心价值

- **降本**：通过自动化规则引擎，减少人工逐条核查成本
- **合规**：按行业标准定义质量维度与指标，支持监管与审计
- **增效**：规则可复用、可编排，快速适配不同数据域和业务场景
- **可追溯**：报告留痕，支持质量问题的定位与复盘

---

## 三、目标用户与使用场景

### 3.1 目标用户

| 角色 | 描述 | 典型诉求 |
|------|------|----------|
| 数据工程师 | 负责数据加工、入库与治理 | 批量校验数据质量，定位问题列/行 |
| 数据分析师 | 使用数据做分析或建模 | 快速了解数据可用性与可信度 |
| 数据治理专员 | 制定和执行数据标准 | 落地质量规则，监控质量趋势 |
| 数据产品经理 | 管理数据产品与数据资产 | 评估数据资产健康度，支撑定价与流通 |

### 3.2 使用场景

| 场景 | 描述 | 典型流程 |
|------|------|----------|
| 数据入湖前校验 | 数据从业务系统导出后，入湖前做质量检查 | 导出 CSV → 配置规则 → 执行检查 → 修复问题 → 再校验 |
| 数据流通前置检查 | 数据要素登记、上架前的合规与质量审核 | 配置流通规则集 → 执行评估 → 生成报告 → 提交审核 |
| 定期质量巡检 | 对存量数据做周期性质量扫描 | 定时任务 + 规则集 → 生成报告 → 问题工单 |
| 数据标准落地 | 将企业数据标准转换为可执行规则 | 标准文档 → 规则 JSON → 集成到评估流程 |
| 数据质量培训与演示 | 作为教学或演示工具 | 示例数据 + 示例规则 → 生成报告 → 讲解质量维度 |

---

## 四、数据质量维度与行业映射

### 4.1 行业标准维度（DAMA-DMBOK 六维）

| 维度 | 英文 | 定义 | 本产品支持情况 |
|------|------|------|----------------|
| 完整性 | Completeness | 数据是否存在缺失、空值 | ✅ 已支持：`completeness` |
| 唯一性 | Uniqueness | 是否存在重复记录或重复键 | ✅ 已支持：`uniqueness` |
| 有效性 | Validity | 数据是否符合格式、枚举、正则等约束 | ✅ 已支持：`validity_regex_match_check`、`data_type` |
| 准确性 | Accuracy | 数据是否正确、是否在合理范围内 | ✅ 已支持：`accuracy_range_check` |
| 一致性 | Consistency | 多列、多表之间的逻辑关系是否一致 | ✅ 已支持：`consistency_date_order_check` |
| 及时性 | Timeliness | 数据是否在预期时间范围内 | ✅ 已支持：`timeliness_fixed_range_check` |

### 4.2 规则类型与质量维度映射

| 规则类型 (type) | 对应质量维度 | 业务含义 |
|-----------------|--------------|----------|
| completeness | 完整性 | 检查列中空值/缺失值数量 |
| uniqueness | 唯一性 | 检查列值是否唯一，识别重复 |
| data_type | 有效性 | 检查列数据类型是否符合预期 |
| accuracy_range_check | 准确性 | 检查数值是否在合理区间 |
| validity_regex_match_check | 有效性 | 检查字符串是否符合格式规范 |
| consistency_date_order_check | 一致性 | 检查两日期列先后关系（如 start ≤ end） |
| timeliness_fixed_range_check | 及时性 | 检查日期是否落在指定区间内 |

---

## 五、功能需求

### 5.1 功能架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                      DataHealthCheck 产品架构                      │
├──────────────┬──────────────┬──────────────┬─────────────────────┤
│  数据接入层   │  规则引擎层   │  检查执行层   │     报告输出层       │
├──────────────┼──────────────┼──────────────┼─────────────────────┤
│ • CSV 加载   │ • 规则解析   │ • 完整性     │ • 文本报告           │
│ • 编码支持   │ • 参数校验   │ • 唯一性     │ • HTML 报告（规划）   │
│ • Excel(规划)│ • Schema校验 │ • 有效性     │ • JSON 报告（规划）   │
│ • DB(规划)   │              │ • 准确性     │ • 控制台输出         │
│              │              │ • 一致性     │                     │
│              │              │ • 及时性     │                     │
└──────────────┴──────────────┴──────────────┴─────────────────────┘
```

### 5.2 数据接入

| 需求 ID | 需求描述 | 优先级 | 实现状态 |
|---------|----------|--------|----------|
| FR-DA-001 | 支持从本地 CSV 文件加载数据 | P0 | ✅ 已实现 |
| FR-DA-002 | 支持指定 CSV 编码（默认 UTF-8） | P1 | 规划中 |
| FR-DA-003 | 支持 Excel (xlsx/xls) 作为数据源 | P2 | ✅ 已实现 |
| FR-DA-004 | 支持关系型数据库作为数据源（PostgreSQL/MySQL） | P2 | ✅ 已实现 |
| FR-DA-005 | 对空文件、解析失败给出明确错误提示 | P0 | ✅ 已实现 |

### 5.3 规则管理

| 需求 ID | 需求描述 | 优先级 | 实现状态 |
|---------|----------|--------|----------|
| FR-RU-001 | 规则以 JSON 数组形式配置，每条规则包含 type、column 等字段 | P0 | ✅ 已实现 |
| FR-RU-002 | 支持 completeness 完整性检查 | P0 | ✅ 已实现 |
| FR-RU-003 | 支持 uniqueness 唯一性检查 | P0 | ✅ 已实现 |
| FR-RU-004 | 支持 data_type 数据类型检查 | P0 | ✅ 已实现 |
| FR-RU-005 | 支持 accuracy_range_check 数值范围检查 | P0 | ✅ 已实现 |
| FR-RU-006 | 支持 validity_regex_match_check 正则有效性检查 | P0 | ✅ 已实现 |
| FR-RU-007 | 支持 consistency_date_order_check 日期顺序一致性检查 | P0 | ✅ 已实现 |
| FR-RU-008 | 支持 timeliness_fixed_range_check 日期及时性检查 | P0 | ✅ 已实现 |
| FR-RU-009 | 规则加载前进行 Schema 校验，提前发现配置错误 | P1 | 规划中 |
| FR-RU-010 | 支持规则分组、启用/禁用（可选） | P2 | 规划中 |

### 5.4 规则参数规范

| 规则类型 | 必需参数 | 可选参数 | 说明 |
|----------|----------|----------|------|
| completeness | column | - | 检查 column 非空 |
| uniqueness | column | - | 检查 column 唯一 |
| data_type | column, expected_type | - | 检查 column 类型为 expected_type |
| accuracy_range_check | column, min_value, max_value | - | 检查 column 数值在 [min, max] |
| validity_regex_match_check | column, pattern | - | 检查 column 字符串匹配 pattern |
| consistency_date_order_check | column_a, column_b | - | 检查 column_a ≤ column_b |
| timeliness_fixed_range_check | column, start_date, end_date | - | 检查 column 日期在 [start, end] |

### 5.5 检查执行

| 需求 ID | 需求描述 | 优先级 | 实现状态 |
|---------|----------|--------|----------|
| FR-CH-001 | 按规则顺序依次执行检查 | P0 | ✅ 已实现 |
| FR-CH-002 | 单条规则失败不影响后续规则执行 | P0 | ✅ 已实现 |
| FR-CH-003 | 检查结果包含 rule_type、column、status、message、details | P0 | ✅ 已实现 |
| FR-CH-004 | status 支持 passed / failed / error 三种状态 | P0 | ✅ 已实现 |
| FR-CH-005 | 对 consistency_date_order_check 正确展示 column_a/column_b | P0 | ✅ 已实现 |
| FR-CH-006 | 列不存在、参数缺失等配置问题返回 error 且给出明确信息 | P0 | ✅ 已实现 |
| FR-CH-007 | 支持规则并行执行（大批量规则时） | P2 | 规划中 |

### 5.6 报告输出

| 需求 ID | 需求描述 | 优先级 | 实现状态 |
|---------|----------|--------|----------|
| FR-RP-001 | 输出总结信息：总检查数、通过数、失败数 | P0 | ✅ 已实现 |
| FR-RP-002 | 输出每条检查的详细结果（规则类型、列、状态、消息、明细） | P0 | ✅ 已实现 |
| FR-RP-003 | 支持将报告输出到控制台 | P0 | ✅ 已实现 |
| FR-RP-004 | 支持将报告输出到指定文件（-o） | P0 | ✅ 已实现 |
| FR-RP-005 | 支持 HTML 格式报告 | P1 | ✅ 已实现 |
| FR-RP-006 | 支持 JSON 格式报告，便于系统集成 | P1 | ✅ 已实现 |
| FR-RP-007 | 对 failed 检查可选输出违规行样例 | P2 | 规划中 |

### 5.7 命令行与交互

| 需求 ID | 需求描述 | 优先级 | 实现状态 |
|---------|----------|--------|----------|
| FR-CL-001 | 支持必选参数：数据文件路径、规则文件路径 | P0 | ✅ 已实现 |
| FR-CL-002 | 支持可选参数：-o 报告输出路径 | P0 | ✅ 已实现 |
| FR-CL-003 | 规则文件或数据文件不存在时，给出明确错误并退出码非 0 | P0 | ✅ 已实现 |
| FR-CL-004 | 支持 --encoding 指定 CSV 编码 | P1 | 规划中 |
| FR-CL-005 | 支持 --format text\|html\|json 指定报告格式 | P1 | 规划中 |
| FR-CL-006 | 支持 --validate-rules-only 仅校验规则文件 | P2 | 规划中 |

---

## 六、非功能需求

### 6.1 性能

| 需求 ID | 需求描述 | 目标 |
|---------|----------|------|
| NFR-PF-001 | 10 万行 × 20 列 CSV 加载时间 | < 5 秒 |
| NFR-PF-002 | 单次执行 50 条规则耗时 | < 30 秒 |
| NFR-PF-003 | 单进程内存占用 | < 500MB（常规数据规模） |

### 6.2 可靠性

| 需求 ID | 需求描述 |
|---------|----------|
| NFR-RL-001 | 单条规则执行异常不影响其他规则，异常规则记为 error |
| NFR-RL-002 | 支持 Python 3.8+，依赖版本固定，避免兼容性问题 |

### 6.3 可维护性

| 需求 ID | 需求描述 |
|---------|----------|
| NFR-MT-001 | 模块化设计，数据加载、规则引擎、检查逻辑、报告生成分离 |
| NFR-MT-002 | 新增规则类型仅需在 checks 中实现并在 engine 中注册 |
| NFR-MT-003 | 核心逻辑具备单元测试，覆盖率 > 80% |

### 6.4 可用性

| 需求 ID | 需求描述 |
|---------|----------|
| NFR-US-001 | 提供 README 与示例规则，新用户 10 分钟内完成首次运行 |
| NFR-US-002 | 错误信息清晰、可操作（如：列不存在、参数缺失等） |
| NFR-US-003 | 报告文本易读，支持中文 |

---

## 七、数据与接口

### 7.1 规则文件 Schema（JSON）

```json
{
  "type": "array",
  "items": {
    "type": "object",
    "required": ["type"],
    "properties": {
      "type": {
        "type": "string",
        "enum": [
          "completeness",
          "uniqueness",
          "data_type",
          "accuracy_range_check",
          "validity_regex_match_check",
          "consistency_date_order_check",
          "timeliness_fixed_range_check"
        ]
      },
      "column": { "type": "string" },
      "column_a": { "type": "string" },
      "column_b": { "type": "string" },
      "expected_type": { "type": "string" },
      "min_value": { "type": "number" },
      "max_value": { "type": "number" },
      "pattern": { "type": "string" },
      "start_date": { "type": "string", "format": "date" },
      "end_date": { "type": "string", "format": "date" }
    }
  }
}
```

### 7.2 检查结果结构

| 字段 | 类型 | 说明 |
|------|------|------|
| rule_type | string | 规则类型 |
| column | string \| null | 目标列（单列规则） |
| column_a | string \| null | 第一列（日期顺序规则） |
| column_b | string \| null | 第二列（日期顺序规则） |
| status | string | passed / failed / error |
| message | string | 检查结果描述 |
| details | object \| null | 详细统计信息 |
| expected_type | string \| null | 期望类型（data_type） |
| actual_type | string \| null | 实际类型（data_type） |

---

## 八、验收标准与成功指标

### 8.1 验收标准

- 所有 P0 功能需求已实现且通过测试
- 单元测试全部通过
- 使用示例数据与示例规则可完整跑通并生成报告
- 文档（README、PRD）与代码同步

### 8.2 成功指标

| 指标 | 目标 |
|------|------|
| 规则类型覆盖 | 覆盖 DAMA 六维数据质量（完整性、唯一性、有效性、准确性、一致性、及时性） |
| 规则配置方式 | 纯 JSON 配置，无需改代码即可扩展规则集 |
| 报告可读性 | 用户能在 1 分钟内理解报告结构与问题所在 |

---

## 九、迭代规划

### 9.1 当前版本（V0.x）

- 已完成：阶段一 Bug 修复与基础能力夯实
- 能力：CSV 加载、7 类规则、文本报告、CLI

### 9.2 短期（V1.0）— 部分已实现

- 日志与编码参数
- 规则 Schema 校验
- HTML / JSON 报告 ✅ 已实现
- 规则参数解析器重构

### 9.3 中期（V1.x）— 部分已实现

- 多数据源（Excel、PostgreSQL、MySQL）✅ 已实现
- 规则分组与模板
- 违规行样例输出

### 9.4 长期（V2.x）— 部分已实现

- 与数据目录、任务调度集成
- 质量分与趋势分析（仪表盘）✅ 已实现
- Web 控制台 ✅ 已实现（数据源、规则集、任务、报告、剖析、用户管理）

---

## 十、对标行业产品与 PRD 升级建议

本节基于 Great Expectations、Soda Core、ydata-quality、Pandera、DQOps 等成熟产品的实践，对本 PRD 提出深度优化与升级方向。

### 10.1 能力差距与升级矩阵

| 能力域 | 当前状态 | 行业标杆实践 | 升级建议 | 优先级 |
|--------|----------|--------------|----------|--------|
| **数据画像/剖析** | 无 | ydata-quality、Great Expectations 提供自动 Profiling | 增加数据剖析模块：列统计、分布、唯一值、空值率等 | P1 |
| **Schema 校验** | 部分（data_type） | Pandera 的类 Pydantic Schema、Soda Data Contracts | 支持 Schema 文件定义整表约束，批量校验 | P1 |
| **Checkpoint / 工作流** | 单次 CLI 执行 | Great Expectations Checkpoint  bundling | 支持 checkpoint 配置：数据源+规则集+动作，可复用执行 | P1 |
| **Data Docs / 报告** | 仅文本 | Great Expectations HTML Data Docs、Pointblank 交互报告 | 增强 HTML 报告：可折叠、筛选、图表、历史对比 | P0 |
| **违规行与样例** | 无 | Soda Failed Rows、Great Expectations 可采样 | 支持 `violation_samples` 输出违规行索引/样例（可限 N 条） | P1 |
| **规则 Severity** | 无 | Soda warn/error、部分阻断 | 规则支持 severity（critical/warning/info），按级别汇总 | P2 |
| **CI/CD 集成** | 无 | Great Expectations Action、Soda GitHub Action | 提供 exit code、JSON 输出，便于流水线集成 | P1 |
| **规则推荐/自发现** | 无 | ydata-quality 画像后推荐、Great Expectations Profiler | 基于剖析结果自动推荐规则（可选执行） | P2 |
| **多后端** | 仅 Pandas | Pandera 支持 Polars/PySpark/Dask | 抽象数据源接口，支持 Polars、PySpark | P2 |
| **数据漂移** | 无 | ydata-quality Drift、Great Expectations 参考数据 | 支持与基准数据比对，检测分布漂移 | P2 |
| **YAML 配置** | 仅 JSON | Soda、DQOps 使用 YAML | 支持 YAML 规则文件，便于可读与版本管理 | P2 |
| **Python API** | 仅 CLI | Pandera 装饰器、ydata-quality 一行调用 | 提供 `DataQuality(df).evaluate(rules)` 等 Python API | P1 |

### 10.2 新增功能需求（升级版）

#### 10.2.1 数据剖析模块

| 需求 ID | 需求描述 | 参考产品 | 优先级 |
|---------|----------|----------|--------|
| FR-UP-PR-001 | 支持对数据执行自动剖析，输出列级统计（类型、非空数、唯一值数、分布概览） | ydata-quality, ydata-profiling | P1 |
| FR-UP-PR-002 | 剖析结果可导出为 JSON/HTML，供人工或规则推荐使用 | Great Expectations Profiler | P1 |
| FR-UP-PR-003 | 提供 `--profile-only` 模式，仅做剖析不执行规则 | - | P2 |

#### 10.2.2 规则增强

| 需求 ID | 需求描述 | 参考产品 | 优先级 |
|---------|----------|----------|--------|
| FR-UP-RU-001 | 规则支持 `severity` 字段：critical / warning / info | Soda Core | P2 |
| FR-UP-RU-002 | 规则支持 `name`、`description` 便于追溯与文档化 | Great Expectations | P2 |
| FR-UP-RU-003 | 新增 `value_in_list`：枚举值检查 | Soda, Great Expectations | P1 |
| FR-UP-RU-004 | 新增 `referential_integrity`：外键/跨表一致性（多数据源时） | 行业通用 | P2 |
| FR-UP-RU-005 | 支持 YAML 格式规则文件 | Soda, DQOps | P2 |

#### 10.2.3 报告与输出增强

| 需求 ID | 需求描述 | 参考产品 | 优先级 |
|---------|----------|----------|--------|
| FR-UP-RP-001 | HTML 报告支持按 status 筛选、可折叠详情、简单图表（通过率饼图等） | Great Expectations, Pointblank | P1 |
| FR-UP-RP-002 | 对 failed 规则输出违规行样例（可配置 limit，如 10 条） | Soda Failed Rows | P1 |
| FR-UP-RP-003 | JSON 输出包含机器可读结构，支持 `--fail-on` critical 等 | CI/CD 集成 | P1 |
| FR-UP-RP-004 | 支持 `--exit-code-on-fail`：有失败时返回非 0 便于流水线 | Great Expectations Action | P1 |

#### 10.2.4 Checkpoint 与工作流

| 需求 ID | 需求描述 | 参考产品 | 优先级 |
|---------|----------|----------|--------|
| FR-UP-CP-001 | 支持 Checkpoint 配置：数据源 + 规则集 + 输出动作 | Great Expectations | P1 |
| FR-UP-CP-002 | 支持从 Checkpoint 文件一键执行，减少重复参数 | Great Expectations | P1 |

#### 10.2.5 Python API

| 需求 ID | 需求描述 | 参考产品 | 优先级 |
|---------|----------|----------|--------|
| FR-UP-API-001 | 提供 `from data_quality_tool import DataQuality; dq = DataQuality(df); results = dq.evaluate(rules)` | ydata-quality | P1 |
| FR-UP-API-002 | 支持 Pipeline 装饰器集成：`@validate_data(rules_file)` | Pandera | P2 |

#### 10.2.6 数据漂移（长期）

| 需求 ID | 需求描述 | 参考产品 | 优先级 |
|---------|----------|----------|--------|
| FR-UP-DR-001 | 支持指定基准数据，与当前数据做分布对比 | ydata-quality Drift | P2 |
| FR-UP-DR-002 | 输出漂移检测结果（列级/表级） | - | P2 |

### 10.3 架构升级示意

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DataHealthCheck 升级后架构（目标）                       │
├──────────────┬──────────────┬──────────────┬──────────────┬─────────────┤
│  数据接入层   │  剖析层(新增) │  规则引擎层   │  检查执行层   │  报告/集成层  │
├──────────────┼──────────────┼──────────────┼──────────────┼─────────────┤
│ CSV/Excel   │ Profiling    │ Schema 校验  │ 7类+扩展规则 │ Text/HTML   │
│ DB / Polars │ 列统计/分布   │ Checkpoint   │ Severity     │ JSON        │
│              │ 规则推荐     │ YAML/JSON   │ 违规行样例   │ CI/CD 退出码 │
└──────────────┴──────────────┴──────────────┴──────────────┴─────────────┘
```

### 10.4 迭代规划更新（对标后）

| 阶段 | 原规划 | 对标后补充 |
|------|--------|------------|
| **V1.0** | 日志、编码、Schema 校验、HTML/JSON | + 违规行样例、Python API、`--fail-on` 退出码 |
| **V1.5** | - | 数据剖析、Checkpoint、value_in_list、报告增强 |
| **V2.0** | 多数据源、规则分组 | + Severity、YAML、CI/CD 示例、数据漂移（可选） |
| **V2.5+** | 与数据目录集成 | + 规则推荐、多后端（Polars）、Web 控制台 |

### 10.5 参考链接

- [Great Expectations](https://github.com/great-expectations/great_expectations) — 数据验证与文档化
- [Soda Core](https://github.com/sodadata/soda-core) — 数据质量测试与 Data Contracts
- [ydata-quality](https://github.com/ydataai/ydata-quality) — 数据质量评估与画像
- [Pandera](https://github.com/pandera-dev/pandera) — Schema 校验与 Pipeline 集成
- [DQOps](https://github.com/dqops/dqo) — 数据质量可观测平台

---

## 十一、附录

### 11.1 术语表

| 术语 | 定义 |
|------|------|
| 数据质量 | 数据满足规定用途要求的程度 |
| 规则 | 对数据实施检查的配置项，包含类型与参数 |
| 完整性 | 数据无缺失、无不应存在的空值 |
| passed | 检查通过，满足规则 |
| failed | 检查未通过，数据不符合规则 |
| error | 规则配置错误或执行异常 |

### 11.2 参考文档

- DAMA-DMBOK 2.0, DAMA International
- GB/T 36344-2018 信息技术 数据质量评价指标
- 本项目 README.md、sample_rules.json
- 第十节「对标行业产品与 PRD 升级建议」中的各开源项目链接

---

*文档结束*
