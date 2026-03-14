# -*- coding: utf-8 -*-
"""
文件名: report.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 数据质量报告生成，支持 JSON 与 HTML 格式
"""

# -*- coding: utf-8 -*-
"""
文件名: report.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 数据质量报告生成服务，支持 JSON 与 HTML 格式输出
"""
from jinja2 import Template
from markupsafe import Markup


def build_report_json(
    results: list, by_datasource: dict[str, list] | None = None, ds_names: dict[str, str] | None = None
) -> dict:
    """Build report. If by_datasource given, produces multi-source structure."""
    if by_datasource is None:
        total = len(results)
        passed = sum(1 for r in results if r.get("status") == "passed")
        failed = total - passed
        return {
            "summary": {"total": total, "passed": passed, "failed": failed},
            "details": results,
        }
    all_details = []
    by_summary = {}
    grand_total, grand_passed, grand_failed = 0, 0, 0
    for ds_id, ds_results in by_datasource.items():
        t = len(ds_results)
        p = sum(1 for r in ds_results if r.get("status") == "passed")
        f = t - p
        grand_total += t
        grand_passed += p
        grand_failed += f
        by_summary[ds_id] = {"total": t, "passed": p, "failed": f}
        name = (ds_names or {}).get(ds_id, ds_id)
        for r in ds_results:
            row = dict(r)
            row["datasource_id"] = ds_id
            row["datasource"] = name
            all_details.append(row)
    return {
        "summary": {
            "total": grand_total,
            "passed": grand_passed,
            "failed": grand_failed,
            "by_datasource": by_summary,
        },
        "details": all_details,
        "details_by_datasource": by_datasource,
    }


def build_report_html(results: list, by_datasource: dict[str, list] | None = None, ds_names: dict[str, str] | None = None) -> str:
    ds_names = ds_names or {}
    if by_datasource:
        total = sum(len(v) for v in by_datasource.values())
        passed = sum(
            sum(1 for r in v if r.get("status") == "passed") for v in by_datasource.values()
        )
        failed = total - passed
        rows_html = ""
        for ds_id, ds_results in by_datasource.items():
            label = ds_names.get(ds_id, ds_id)
            rows_html += f'<tr><td colspan="5" style="background:#f0f0f0;font-weight:bold;">数据源: {label}</td></tr>'
            for r in ds_results:
                status = r.get("status", "unknown")
                status_color = "green" if status == "passed" else ("red" if status == "failed" else "orange")
                col = r.get("column") or f"{r.get('column_a', '')} / {r.get('column_b', '')}"
                details = r.get("details")
                details_str = str(details) if details else ""
                rows_html += f"""
                <tr>
                    <td>{r.get('rule_type', '')}</td>
                    <td>{col}</td>
                    <td><span style="color:{status_color}">{status}</span></td>
                    <td>{r.get('message', '')}</td>
                    <td><small>{details_str}</small></td>
                </tr>
                """
    else:
        total = len(results)
        passed = sum(1 for r in results if r.get("status") == "passed")
        failed = total - passed
        rows_html = ""
        for r in results:
            status = r.get("status", "unknown")
            status_color = "green" if status == "passed" else ("red" if status == "failed" else "orange")
            col = r.get("column") or f"{r.get('column_a', '')} / {r.get('column_b', '')}"
            details = r.get("details")
            details_str = str(details) if details else ""
            rows_html += f"""
        <tr>
            <td>{r.get('rule_type', '')}</td>
            <td>{col}</td>
            <td><span style="color:{status_color}">{status}</span></td>
            <td>{r.get('message', '')}</td>
            <td><small>{details_str}</small></td>
        </tr>
        """

    tpl = Template("""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Data Quality Report</title></head>
<body style="font-family: sans-serif; padding: 20px;">
<h1>Data Quality Report</h1>
<h2>Summary</h2>
<table border="1" cellpadding="8">
<tr><th>Total</th><th>Passed</th><th>Failed</th></tr>
<tr><td>{{ total }}</td><td style="color:green">{{ passed }}</td><td style="color:red">{{ failed }}</td></tr>
</table>
<h2>Details</h2>
<table border="1" cellpadding="8" style="border-collapse: collapse;">
<tr><th>Rule Type</th><th>Column</th><th>Status</th><th>Message</th><th>Details</th></tr>
{{ rows_html }}
</table>
</body>
</html>
    """)
    return tpl.render(total=total, passed=passed, failed=failed, rows_html=Markup(rows_html))
