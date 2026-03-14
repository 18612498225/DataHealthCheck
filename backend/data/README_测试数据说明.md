# 数据健康平台 - 测试数据集说明

存放于 `backend/data/` 目录，供平台评估使用。

## 数据集清单


| 文件                             | 说明       | 覆盖规则                                       | 预期结果     |
| ------------------------------ | -------- | ------------------------------------------ | -------- |
| **good_data.csv**              | 基础良好数据   | completeness, uniqueness, data_type, regex | 全部通过     |
| **data_with_nulls.csv**        | 含空值      | completeness                               | 部分失败     |
| **data_with_duplicates.csv**   | 含重复      | uniqueness                                 | 失败       |
| **employees_demo.csv**         | 员工示例（混合） | 完整性、唯一性、类型、范围、邮箱                           | 部分失败     |
| **all_rules_pass.csv**         | 全规则通过    | 7 类规则全覆盖                                   | **全部通过** |
| **dates_order_sample.csv**     | 日期顺序     | consistency_date_order_check               | 全部通过     |
| **timeliness_sample.csv**      | 时效性      | timeliness_fixed_range_check               | 全部通过     |
| **dates_order_violations.csv** | 日期顺序违规   | consistency_date_order_check               | 部分失败     |
| **timeliness_violations.csv**  | 时效性违规    | timeliness_fixed_range_check               | 部分失败     |
| **all_rules_violations.csv**   | 综合违规     | 多种规则                                       | 多项失败     |


## 规则类型

1. **completeness** - 完整性（无空值）
2. **uniqueness** - 唯一性（无重复）
3. **data_type** - 数据类型
4. **accuracy_range_check** - 数值范围
5. **validity_regex_match_check** - 正则匹配
6. **consistency_date_order_check** - 日期顺序（column_a ≤ column_b）
7. **timeliness_fixed_range_check** - 时效性（日期在指定范围内）

