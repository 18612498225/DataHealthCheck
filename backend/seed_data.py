# -*- coding: utf-8 -*-
"""
文件名: seed_data.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 数据库种子脚本，初始化示例数据源、规则集、角色与用户
"""
import logging
import os
import sys
from pathlib import Path

# Ensure backend is in path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

os.chdir(backend_dir)

from app.db.database import SessionLocal
from app.db.init_db import init_db
from app.models import Datasource, RuleSet, Task, AssessmentResult, Role, User
from app.core.security import hash_password
import json

# Rules for good_data.csv (id, name, age, email)
GOOD_DATA_RULES = [
    {"type": "completeness", "column": "id"},
    {"type": "completeness", "column": "name"},
    {"type": "uniqueness", "column": "id"},
    {"type": "data_type", "column": "age", "expected_type": "int64"},
    {"type": "validity_regex_match_check", "column": "email", "pattern": r".+@.+\..+"},
]

# Rules for data_with_nulls.csv (id, name, value)
NULLS_RULES = [
    {"type": "completeness", "column": "id"},
    {"type": "completeness", "column": "value"},
]

# Rules for data_with_duplicates.csv (id, name)
DUPLICATES_RULES = [
    {"type": "uniqueness", "column": "id"},
    {"type": "uniqueness", "column": "name"},
]

# Rules for employees_demo.csv
EMPLOYEES_RULES = [
    {"type": "completeness", "column": "id"},
    {"type": "completeness", "column": "name"},
    {"type": "completeness", "column": "email"},
    {"type": "uniqueness", "column": "id"},
    {"type": "data_type", "column": "age", "expected_type": "int64"},
    {"type": "accuracy_range_check", "column": "age", "min_value": 18, "max_value": 65},
    {"type": "accuracy_range_check", "column": "salary", "min_value": 40000, "max_value": 100000},
    {"type": "validity_regex_match_check", "column": "email", "pattern": r".+@.+\..+"},
]

# Rules for all_rules_pass.csv - 全规则通过
ALL_RULES_PASS_RULES = [
    {"type": "completeness", "column": "id"},
    {"type": "completeness", "column": "name"},
    {"type": "completeness", "column": "age"},
    {"type": "completeness", "column": "email"},
    {"type": "uniqueness", "column": "id"},
    {"type": "data_type", "column": "age", "expected_type": "int64"},
    {"type": "accuracy_range_check", "column": "age", "min_value": 18, "max_value": 65},
    {"type": "accuracy_range_check", "column": "salary", "min_value": 40000, "max_value": 100000},
    {"type": "validity_regex_match_check", "column": "email", "pattern": r".+@.+\..+"},
    {"type": "consistency_date_order_check", "column_a": "hire_date", "column_b": "end_date"},
    {"type": "timeliness_fixed_range_check", "column": "hire_date", "start_date": "2023-01-01", "end_date": "2023-12-31"},
]

# Rules for dates_order_sample.csv
DATES_ORDER_RULES = [
    {"type": "consistency_date_order_check", "column_a": "start_date", "column_b": "end_date"},
]

# Rules for timeliness_sample.csv
TIMELINESS_RULES = [
    {"type": "timeliness_fixed_range_check", "column": "event_date", "start_date": "2023-01-01", "end_date": "2023-12-31"},
]

# Rules for dates_order_violations.csv
DATES_ORDER_VIOLATIONS_RULES = [
    {"type": "consistency_date_order_check", "column_a": "start_date", "column_b": "end_date"},
]

# Rules for timeliness_violations.csv
TIMELINESS_VIOLATIONS_RULES = [
    {"type": "timeliness_fixed_range_check", "column": "event_date", "start_date": "2023-01-01", "end_date": "2023-12-31"},
]

# Rules for all_rules_violations.csv - 综合违规
ALL_RULES_VIOLATIONS_RULES = [
    {"type": "completeness", "column": "name"},
    {"type": "uniqueness", "column": "id"},
    {"type": "accuracy_range_check", "column": "age", "min_value": 18, "max_value": 65},
    {"type": "accuracy_range_check", "column": "salary", "min_value": 40000, "max_value": 100000},
    {"type": "validity_regex_match_check", "column": "email", "pattern": r".+@.+\..+"},
    {"type": "consistency_date_order_check", "column_a": "hire_date", "column_b": "end_date"},
    {"type": "timeliness_fixed_range_check", "column": "hire_date", "start_date": "2023-01-01", "end_date": "2023-12-31"},
]


def seed():
    init_db()
    db = SessionLocal()
    try:
        # Clear existing (order: FK dependencies first)
        db.query(AssessmentResult).delete()
        db.query(Task).delete()
        db.query(Datasource).delete()
        db.query(RuleSet).delete()
        db.query(User).delete()
        db.query(Role).delete()
        db.commit()

        # Roles
        role_admin = Role(name="管理员")
        role_eval = Role(name="评估员")
        role_viewer = Role(name="查看者")
        db.add_all([role_admin, role_eval, role_viewer])
        db.commit()
        db.refresh(role_admin)

        # Users (admin / admin123)
        u_admin = User(
            username="admin",
            password_hash=hash_password("admin123"),
            real_name="系统管理员",
            role_id=role_admin.id,
            org="数据质量平台",
        )
        db.add(u_admin)
        db.commit()

        # Datasources
        ds_good = Datasource(
            name="良好数据示例 (good_data)",
            source_type="csv",
            config=json.dumps({"path": "good_data.csv"}),
        )
        ds_nulls = Datasource(
            name="含空值数据 (data_with_nulls)",
            source_type="csv",
            config=json.dumps({"path": "data_with_nulls.csv"}),
        )
        ds_dups = Datasource(
            name="含重复数据 (data_with_duplicates)",
            source_type="csv",
            config=json.dumps({"path": "data_with_duplicates.csv"}),
        )
        ds_emp = Datasource(
            name="员工示例 (employees_demo)",
            source_type="csv",
            config=json.dumps({"path": "employees_demo.csv"}),
        )
        ds_all_pass = Datasource(
            name="全规则通过 (all_rules_pass)",
            source_type="csv",
            config=json.dumps({"path": "all_rules_pass.csv"}),
        )
        ds_dates = Datasource(
            name="日期顺序 (dates_order_sample)",
            source_type="csv",
            config=json.dumps({"path": "dates_order_sample.csv"}),
        )
        ds_timeliness = Datasource(
            name="时效性 (timeliness_sample)",
            source_type="csv",
            config=json.dumps({"path": "timeliness_sample.csv"}),
        )
        ds_dates_viol = Datasource(
            name="日期顺序违规 (dates_order_violations)",
            source_type="csv",
            config=json.dumps({"path": "dates_order_violations.csv"}),
        )
        ds_timeliness_viol = Datasource(
            name="时效性违规 (timeliness_violations)",
            source_type="csv",
            config=json.dumps({"path": "timeliness_violations.csv"}),
        )
        ds_all_viol = Datasource(
            name="综合违规 (all_rules_violations)",
            source_type="csv",
            config=json.dumps({"path": "all_rules_violations.csv"}),
        )
        db.add_all([ds_good, ds_nulls, ds_dups, ds_emp, ds_all_pass, ds_dates, ds_timeliness, ds_dates_viol, ds_timeliness_viol, ds_all_viol])
        db.commit()
        db.refresh(ds_good)
        db.refresh(ds_nulls)
        db.refresh(ds_dups)
        db.refresh(ds_emp)

        # Rule sets (按行业/标准建模，与数据源解耦)
        rs_good = RuleSet(
            name="通用完整性规则集",
            description="DAMA 完整性、唯一性、有效性维度。适用于含 id/name/age/email 的主数据表",
            rules=json.dumps(GOOD_DATA_RULES),
            industry="通用",
            quality_dimensions=json.dumps(["completeness", "uniqueness", "validity"]),
            standard_ref="DAMA-DMBOK",
        )
        rs_nulls = RuleSet(
            name="完整性检测规则集",
            description="GB/T 36344 完整性指标：检测主键及关键指标列空值",
            rules=json.dumps(NULLS_RULES),
            industry="通用",
            quality_dimensions=json.dumps(["completeness"]),
            standard_ref="GB/T 36344-2018",
        )
        rs_dups = RuleSet(
            name="唯一性检测规则集",
            description="DAMA 唯一性维度：检测主键及业务键重复",
            rules=json.dumps(DUPLICATES_RULES),
            industry="通用",
            quality_dimensions=json.dumps(["uniqueness"]),
            standard_ref="DAMA-DMBOK",
        )
        rs_emp = RuleSet(
            name="人力资源数据质量规则集",
            description="人事数据六维检查：完整性、唯一性、有效性、准确性、一致性、及时性",
            rules=json.dumps(EMPLOYEES_RULES),
            industry="人力资源",
            quality_dimensions=json.dumps(["completeness", "uniqueness", "validity", "accuracy"]),
            standard_ref="DAMA-DMBOK",
        )
        rs_all_pass = RuleSet(
            name="通用六维全覆盖规则集",
            description="DAMA 六维 + GB/T 36344 全规则，适用于人事/业务主数据",
            rules=json.dumps(ALL_RULES_PASS_RULES),
            industry="通用",
            quality_dimensions=json.dumps(["completeness", "uniqueness", "validity", "accuracy", "consistency", "timeliness"]),
            standard_ref="DAMA-DMBOK, GB/T 36344-2018",
        )
        rs_dates = RuleSet(
            name="一致性-日期顺序规则集",
            description="DAMA 一致性：检查 start_date <= end_date",
            rules=json.dumps(DATES_ORDER_RULES),
            industry="通用",
            quality_dimensions=json.dumps(["consistency"]),
            standard_ref="DAMA-DMBOK",
        )
        rs_timeliness = RuleSet(
            name="及时性规则集",
            description="DAMA 及时性：日期落在指定区间内",
            rules=json.dumps(TIMELINESS_RULES),
            industry="通用",
            quality_dimensions=json.dumps(["timeliness"]),
            standard_ref="DAMA-DMBOK",
        )
        rs_dates_viol = RuleSet(
            name="一致性-日期顺序（违规检测）",
            description="一致性维度：检测 start_date > end_date 违规",
            rules=json.dumps(DATES_ORDER_VIOLATIONS_RULES),
            industry="通用",
            quality_dimensions=json.dumps(["consistency"]),
            standard_ref="DAMA-DMBOK",
        )
        rs_timeliness_viol = RuleSet(
            name="及时性（违规检测）",
            description="及时性维度：检测日期超出范围",
            rules=json.dumps(TIMELINESS_VIOLATIONS_RULES),
            industry="通用",
            quality_dimensions=json.dumps(["timeliness"]),
            standard_ref="DAMA-DMBOK",
        )
        rs_all_viol = RuleSet(
            name="综合违规检测规则集",
            description="六维违规综合检测，适用于质量审计场景",
            rules=json.dumps(ALL_RULES_VIOLATIONS_RULES),
            industry="通用",
            quality_dimensions=json.dumps(["completeness", "uniqueness", "validity", "accuracy", "consistency", "timeliness"]),
            standard_ref="DAMA-DMBOK, DCMM",
        )
        db.add_all([rs_good, rs_nulls, rs_dups, rs_emp, rs_all_pass, rs_dates, rs_timeliness, rs_dates_viol, rs_timeliness_viol, rs_all_viol])
        db.commit()

        logger = logging.getLogger(__name__)
        logger.info("Seed completed. Datasources: 10, Rule sets: 10, Users: 1 (admin/admin123)")
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    seed()
