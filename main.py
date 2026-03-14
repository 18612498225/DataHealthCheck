# -*- coding: utf-8 -*-
"""
文件名: main.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 数据质量评估工具命令行入口
"""
import argparse
import json
import logging
import sys

# CLI 场景：初始化简化日志（仅控制台、INFO 级别）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

from data_quality_tool.data_loader import load_csv_data
from data_quality_tool.assessment_engine import AssessmentEngine
from data_quality_tool.reporter import generate_text_report

def main():
    parser = argparse.ArgumentParser(description="数据质量评估工具")
    parser.add_argument("data_file", help="输入 CSV 数据文件路径")
    parser.add_argument("rules_file", help="包含评估规则的 JSON 文件路径")
    parser.add_argument(
        "--output_report_file",
        "-o",
        help="可选，报告保存路径；不提供则输出到控制台",
        default=None,
    )

    args = parser.parse_args()

    # Load rules
    logger = logging.getLogger(__name__)
    try:
        with open(args.rules_file, 'r', encoding='utf-8') as f:
            rules = json.load(f)
    except FileNotFoundError:
        logger.error("错误：规则文件不存在 %s", args.rules_file)
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error("错误：规则文件 JSON 解析失败 %s", args.rules_file)
        sys.exit(1)
    except Exception as e:
        logger.exception("加载规则时发生异常: %s", e)
        sys.exit(1)

    if not isinstance(rules, list):
        logger.error("错误：规则文件 %s 必须为 JSON 数组格式", args.rules_file)
        sys.exit(1)

    # Load data
    dataframe = load_csv_data(args.data_file)
    if dataframe is None:
        # Error message is printed by load_csv_data
        sys.exit(1)

    # Perform assessment
    engine = AssessmentEngine(dataframe)
    results = engine.run_checks(rules)

    # Generate report
    generate_text_report(results, args.output_report_file)

if __name__ == "__main__":
    main()
