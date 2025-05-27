# 数据质量评估工具

## 项目概览

本工具旨在提供一个可配置的、自动化的数据质量评估解决方案。用户可以通过定义一系列规则，对 CSV 格式的数据文件进行质量检查，并生成易于理解的评估报告。

## 主要功能

*   **数据加载**: 从 CSV 文件加载数据。
*   **完整性检查**: 检查指定列中是否存在缺失值 (null/NaN)。
*   **唯一性检查**: 检查指定列中的值是否唯一，识别重复项。
*   **数据类型检查**: 验证指定列的数据类型是否符合预期 (如 `int64`, `float64`, `object` 等)。
*   **报告生成**: 生成文本格式的评估报告，总结检查结果，并可选择输出到文件或控制台。

## 项目结构

```
.
├── data_quality_tool/  # 核心源代码目录
│   ├── __init__.py
│   ├── assessment_engine.py # 评估引擎，执行检查规则
│   ├── checks.py            # 包含各种数据质量检查函数
│   ├── data_loader.py       # 数据加载模块
│   └── reporter.py          # 报告生成模块
├── tests/                # 单元测试目录
│   ├── sample_data/      # 存放测试用的示例数据文件
│   ├── __init__.py
│   ├── test_assessment_engine.py
│   ├── test_checks.py
│   ├── test_data_loader.py
│   └── test_reporter.py
├── main.py               # 命令行界面入口脚本
├── requirements.txt      # 项目依赖包列表
├── sample_rules.json     # 规则文件示例
└── README.md             # 项目说明文件
```

*   `data_quality_tool/`: 包含工具的核心逻辑实现，如数据加载、检查函数、评估引擎和报告生成器。
*   `tests/`: 包含所有单元测试代码，确保工具各模块的正确性和稳定性。`tests/sample_data/` 内含用于测试的各种 CSV 文件。
*   `main.py`: 提供命令行界面，用户通过此脚本与工具交互。
*   `requirements.txt`:列出了运行本项目所需的所有 Python 依赖库。
*   `sample_rules.json`: 提供了一个规则配置文件的示例，用户可以参考此文件创建自己的规则。

## 安装与设置

1.  **克隆代码库 (如果尚未操作)**:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **创建并激活虚拟环境** (推荐):
    *   在 Unix 或 macOS 上:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   在 Windows 上:
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```

3.  **安装依赖**:
    在激活的虚拟环境中，运行以下命令安装项目所需的库：
    ```bash
    pip install -r requirements.txt
    ```

## 使用方法

通过命令行运行 `main.py` 脚本来使用本工具。

### 命令格式

```bash
python main.py <data_file> <rules_file> [-o <output_report_file>]
```

### 参数说明

*   `data_file`: **必需参数**。指定要进行数据质量评估的 CSV 数据文件的路径。
    *   例如: `data/my_dataset.csv`
*   `rules_file`: **必需参数**。指定包含数据质量评估规则的 JSON 文件的路径。
    *   例如: `config/my_rules.json`
*   `--output_report_file` 或 `-o`: **可选参数**。指定评估报告的输出文件名。如果提供了此参数，报告将保存到指定的文件中。如果未提供，报告将直接打印到控制台。
    *   例如: `-o output/dq_report.txt`

### 运行示例

```bash
python main.py path/to/your_data.csv path/to/your_rules.json -o path/to/report.txt
```

例如，使用项目中的示例数据和规则：
```bash
# 假设你在项目根目录，并且 tests/sample_data/good_data.csv 和 sample_rules.json 存在
# 注意: sample_rules.json 中的列名可能需要根据 good_data.csv 的实际列名调整才能有效运行
# 这里我们先创建一个针对 good_data.csv 的规则文件 good_data_rules.json

# 步骤1: 创建 good_data_rules.json (手动或通过脚本)
# 内容示例 (假设 good_data.csv 有 'id', 'name', 'age' 列):
# [
#   {"type": "completeness", "column": "id"},
#   {"type": "uniqueness", "column": "id"},
#   {"type": "data_type", "column": "age", "expected_type": "int64"}
# ]
# 将上述内容保存为 good_data_rules.json

# 步骤2: 运行工具 (假设 good_data_rules.json 已创建)
python main.py tests/sample_data/good_data.csv good_data_rules.json -o good_data_report.txt
```

### 创建规则文件

规则文件是一个 JSON 数组，其中每个对象定义了一条检查规则。

*   `sample_rules.json` 文件提供了一个基础的规则模板。你可以复制并修改此文件来创建你自己的规则集。

#### 规则对象结构

每个规则对象应包含以下字段：

*   `type` (字符串): 指定规则的类型。当前支持的类型有：
    *   `"completeness"`: 检查列的完整性 (非空)。
    *   `"uniqueness"`: 检查列值的唯一性。
    *   `"data_type"`: 检查列的数据类型。
*   `column` (字符串): 指定要应用此规则的数据列的名称。
*   `expected_type` (字符串, 仅当 `type` 为 `"data_type"` 时必需): 指定期望的数据类型。常见的值包括：
    *   `"int64"` (整数)
    *   `"float64"` (浮点数)
    *   `"object"` (通常用于字符串)
    *   `"bool"` (布尔值)
    *   其他 Pandas 支持的数据类型字符串。

#### 自定义规则文件示例

假设你有一个名为 `employees.csv` 的数据文件，包含 `employee_id`, `name`, `department`, `salary`, 和 `hire_date` 列。你可以创建一个名为 `employee_rules.json` 的规则文件，内容如下：

```json
[
    {
        "type": "completeness",
        "column": "employee_id"
    },
    {
        "type": "uniqueness",
        "column": "employee_id"
    },
    {
        "type": "completeness",
        "column": "name"
    },
    {
        "type": "data_type",
        "column": "salary",
        "expected_type": "float64"
    },
    {
        "type": "completeness",
        "column": "department"
    }
]
```

## 运行测试

要运行项目中包含的所有单元测试，请确保已安装 `pytest` (已包含在 `requirements.txt` 中)。然后在项目根目录下执行：

```bash
pytest
```

## (可选) 如何扩展

如果您希望添加新的数据质量检查类型：

1.  **定义新的检查函数**: 在 `data_quality_tool/checks.py` 文件中添加您的新检查逻辑。该函数应接受一个 Pandas DataFrame 和其他必要的参数 (如列名)，并返回一个包含检查结果的字典。
2.  **集成到评估引擎**: 修改 `data_quality_tool/assessment_engine.py` 中的 `AssessmentEngine` 类的 `run_checks` 方法。添加一个新的 `elif` 条件来处理您的新规则类型，并调用您在 `checks.py` 中创建的函数。

确保为您的新检查类型添加相应的单元测试。
```
