# -*- coding: utf-8 -*-
"""
文件名: init_db.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 创建数据库表，执行迁移脚本
"""
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)
from app.db.database import engine, Base
from app.models import Datasource, RuleSet, Task, AssessmentResult, Role, User


def _migrate_rule_sets():
    """Add industry, quality_dimensions, standard_ref columns if missing."""
    db_url = str(engine.url)
    try:
        with engine.connect() as conn:
            if "sqlite" in db_url:
                r = conn.execute(text("PRAGMA table_info(rule_sets)"))
                cols = [row[1] for row in r.fetchall()]
                for col, defn in [
                    ("industry", "VARCHAR(64)"),
                    ("quality_dimensions", "TEXT"),
                    ("standard_ref", "VARCHAR(128)"),
                ]:
                    if col not in cols:
                        conn.execute(text(f"ALTER TABLE rule_sets ADD COLUMN {col} {defn}"))
            else:
                for sql in [
                    "ALTER TABLE rule_sets ADD COLUMN IF NOT EXISTS industry VARCHAR(64)",
                    "ALTER TABLE rule_sets ADD COLUMN IF NOT EXISTS quality_dimensions TEXT",
                    "ALTER TABLE rule_sets ADD COLUMN IF NOT EXISTS standard_ref VARCHAR(128)",
                ]:
                    try:
                        conn.execute(text(sql))
                    except Exception:
                        pass
            conn.commit()
    except Exception:
        pass


def _migrate_tasks():
    """Add datasource_ids column; migrate datasource_id -> datasource_ids."""
    db_url = str(engine.url)
    try:
        with engine.connect() as conn:
            if "sqlite" in db_url:
                r = conn.execute(text("PRAGMA table_info(tasks)"))
                cols = [row[1] for row in r.fetchall()]
                if "datasource_ids" not in cols:
                    conn.execute(text("ALTER TABLE tasks ADD COLUMN datasource_ids VARCHAR(512)"))
                    conn.execute(
                        text(
                            "UPDATE tasks SET datasource_ids = '[\"' || datasource_id || '\"]' WHERE datasource_id IS NOT NULL"
                        )
                    )
            else:
                try:
                    conn.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS datasource_ids VARCHAR(512)"))
                except Exception:
                    pass
            conn.commit()
    except Exception:
        pass


def _migrate_tasks_mappings():
    try:
        with engine.connect() as conn:
            db_url = str(engine.url)
            if "sqlite" in db_url:
                r = conn.execute(text("PRAGMA table_info(tasks)"))
                cols = [row[1] for row in r.fetchall()]
                if "datasource_rule_mappings" not in cols:
                    conn.execute(text("ALTER TABLE tasks ADD COLUMN datasource_rule_mappings VARCHAR(2048)"))
            else:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS datasource_rule_mappings VARCHAR(2048)"))
            conn.commit()
    except Exception:
        pass


def _migrate_datasource_business():
    try:
        with engine.connect() as conn:
            db_url = str(engine.url)
            if "sqlite" in db_url:
                r = conn.execute(text("PRAGMA table_info(datasources)"))
                cols = [row[1] for row in r.fetchall()]
                if "business_scenario" not in cols:
                    conn.execute(text("ALTER TABLE datasources ADD COLUMN business_scenario VARCHAR(64)"))
            else:
                conn.execute(text("ALTER TABLE datasources ADD COLUMN IF NOT EXISTS business_scenario VARCHAR(64)"))
            conn.commit()
    except Exception:
        pass


def init_db():
    Base.metadata.create_all(bind=engine)
    db_url = str(engine.url)
    if "sqlite" in db_url:
        _migrate_rule_sets()
    _migrate_tasks()
    _migrate_tasks_mappings()
    _migrate_datasource_business()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    init_db()
    logger.info("Database tables created.")
