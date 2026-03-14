# -*- coding: utf-8 -*-
"""中国标准数据质量评估报告 (GB/T 36344-2018)."""
from datetime import datetime
from jinja2 import Template
from markupsafe import Markup

RULE_TO_INDICATOR = {
    "completeness": "完整性",
    "uniqueness": "准确性",
    "data_type": "规范性",
    "validity_regex_match_check": "规范性",
    "accuracy_range_check": "准确性",
    "consistency_date_order_check": "一致性",
    "timeliness_fixed_range_check": "时效性",
    "accessibility": "可访问性",  # reserved for future rules
}


def _grade(rate: float) -> str:
    if rate >= 0.95:
        return "优"
    if rate >= 0.80:
        return "良"
    if rate >= 0.60:
        return "中"
    return "差"


def build_report_cn(by_datasource: dict, ds_names: dict, task_name: str = "数据质量评估") -> dict:
    from app.services.report import build_report_json

    base = build_report_json([], by_datasource=by_datasource, ds_names=ds_names)
    summary = base["summary"]
    details = base.get("details", [])

    total = summary.get("total", 0)
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    rate = passed / total if total else 0

    indicators = {}
    for r in details:
        rt = r.get("rule_type", "")
        ind = RULE_TO_INDICATOR.get(rt, "规范性")
        if ind not in indicators:
            indicators[ind] = {"total": 0, "passed": 0, "failed": 0}
        indicators[ind]["total"] += 1
        if r.get("status") == "passed":
            indicators[ind]["passed"] += 1
        else:
            indicators[ind]["failed"] += 1

    problems = [r for r in details if r.get("status") != "passed"]
    fail_types = set(r.get("rule_type") for r in problems)
    suggestions = []
    if "completeness" in fail_types:
        suggestions.append("建议补充缺失数据，确保关键字段完整。")
    if "uniqueness" in fail_types:
        suggestions.append("建议去重或修正主键/业务键重复问题。")
    if "data_type" in fail_types or "validity_regex_match_check" in fail_types:
        suggestions.append("建议按数据标准规范字段格式与类型。")
    if "accuracy_range_check" in fail_types:
        suggestions.append("建议校验数值是否在合理范围内。")
    if "consistency_date_order_check" in fail_types:
        suggestions.append("建议检查日期顺序逻辑（如开始日期≤结束日期）。")
    if "timeliness_fixed_range_check" in fail_types:
        suggestions.append("建议检查数据时效性，确保在有效时间窗口内。")
    if not suggestions:
        suggestions.append("数据质量良好，建议定期复查以保持。")

    # 执行摘要（专业分析报告）
    execution_summary = (
        f"本次评估共检查 {total} 项规则，通过 {passed} 项，失败 {failed} 项，"
        f"整体通过率 {round(rate * 100, 2)}%，质量等级为「{_grade(rate)}」。"
    )
    if problems:
        execution_summary += f" 共发现 {len(problems)} 个问题项，需重点关注并整改。"
    else:
        execution_summary += " 各维度检查均通过，数据质量良好。"

    # 六维指标分析
    indicator_analysis = []
    for ind_name, ind_stat in indicators.items():
        t = ind_stat["total"]
        p = ind_stat["passed"]
        f = ind_stat["failed"]
        ir = (p / t * 100) if t else 0
        ig = _grade(p / t if t else 0)
        indicator_analysis.append({
            "name": ind_name,
            "total": t,
            "passed": p,
            "failed": f,
            "rate": round(ir, 2),
            "grade": ig,
            "comment": f"通过率 {ir:.1f}%，等级「{ig}」。"
        })

    # Default indicator weights (GB/T 36344 six dimensions)
    indicator_weights = {
        "完整性": 0.18,
        "准确性": 0.18,
        "规范性": 0.18,
        "一致性": 0.16,
        "时效性": 0.16,
        "可访问性": 0.14,
    }
    table_weights = {name: 1.0 / max(len(ds_names), 1) for name in ds_names.values()}

    rule_detail = []
    seen = set()
    for r in details:
        key = (r.get("rule_type"), r.get("column") or r.get("column_a"), r.get("column_b"))
        if key not in seen:
            seen.add(key)
            rule_detail.append({
                "rule_type": r.get("rule_type"),
                "column": r.get("column") or f"{r.get('column_a', '')}/{r.get('column_b', '')}",
                "indicator": RULE_TO_INDICATOR.get(r.get("rule_type", ""), "规范性"),
            })

    appendix = {
        "data_description": [{"name": n, "scope": "评估对象"} for n in ds_names.values()],
        "rule_detail": rule_detail[:50],
        "sample_records": [{"datasource": r.get("datasource", ""), "rule_type": r.get("rule_type", ""), "message": r.get("message", "")} for r in problems[:10]],
    }

    # Per-sample scores: score_i = (passed_i / total_i) * 100
    by_ds = summary.get("by_datasource", {})
    sample_scores = []
    for ds_id, ds_name in ds_names.items():
        stats = by_ds.get(ds_id, {"total": 0, "passed": 0, "failed": 0})
        t = stats.get("total", 0)
        p = stats.get("passed", 0)
        score = round((p / t * 100), 2) if t else 0
        sample_scores.append({
            "datasource_id": ds_id,
            "name": ds_name,
            "total": t,
            "passed": p,
            "failed": stats.get("failed", 0),
            "score": score,
            "grade": _grade(p / t if t else 0),
        })

    return {
        "meta": {
            "title": "数据质量评估报告",
            "standard": "GB/T 36344-2018 信息技术 数据质量评价指标",
            "task_name": task_name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "evaluation_scope": list(ds_names.values()),
            "indicator_weights": indicator_weights,
            "table_weights": table_weights,
            "criteria": "检查通过率≥95%为优，≥80%为良，≥60%为中，低于60%为差。",
        },
        "summary": summary,
        "quality_grade": _grade(rate),
        "quality_rate": round(rate * 100, 2),
        "indicators": indicators,
        "tables": summary.get("by_datasource", {}),
        "details": details,
        "problems": problems,
        "suggestions": suggestions,
        "details_by_datasource": base.get("details_by_datasource"),
        "datasource_names": ds_names,
        "appendix": appendix,
        "sample_scores": sample_scores,
        "execution_summary": execution_summary,
        "indicator_analysis": indicator_analysis,
    }


def _svg_gauge(rate: float, size: int = 120) -> str:
    """Simple SVG gauge (semi-circle). rate 0-100."""
    r = size // 2 - 4
    cx, cy = size // 2, size - 4
    # arc from 180deg to 0deg, stroke-dasharray for progress
    circumference = 3.14159 * r
    filled = circumference * (rate / 100)
    color = "#2e7d32" if rate >= 95 else "#1976d2" if rate >= 80 else "#ed6c02" if rate >= 60 else "#c62828"
    return f'<svg width="{size}" height="{size//2+20}" xmlns="http://www.w3.org/2000/svg"><path d="M 4 {cy} A {r} {r} 0 0 1 {size-4} {cy}" fill="none" stroke="#eee" stroke-width="10"/>' \
           f'<path d="M 4 {cy} A {r} {r} 0 0 1 {size-4} {cy}" fill="none" stroke="{color}" stroke-width="10" stroke-dasharray="{filled} {circumference}" stroke-linecap="round"/>' \
           f'<text x="{size//2}" y="{size//2+10}" text-anchor="middle" font-size="20" font-weight="bold">{rate}</text>' \
           f'<text x="{size//2}" y="{size//2+28}" text-anchor="middle" font-size="11" fill="#666">分</text></svg>'


def _svg_bars(sample_scores: list, width: int = 400, height: int = 200) -> str:
    """Simple SVG bar chart for sample scores."""
    if not sample_scores:
        return ""
    n = len(sample_scores)
    bar_w = max(20, (width - 60) // n - 10)
    gap = 10
    max_h = height - 50
    bars = []
    for i, s in enumerate(sample_scores):
        h = max(4, (s.get("score", 0) / 100) * max_h)
        x = 40 + i * (bar_w + gap)
        y = height - 30 - h
        color = "#2e7d32" if s.get("score", 0) >= 95 else "#1976d2" if s.get("score", 0) >= 80 else "#ed6c02" if s.get("score", 0) >= 60 else "#c62828"
        name = (s.get("name", "")[:8] + "…") if len(s.get("name", "")) > 8 else s.get("name", "")
        bars.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{h}" fill="{color}" rx="2"/>')
        bars.append(f'<text x="{x+bar_w//2}" y="{height-8}" text-anchor="middle" font-size="9" fill="#333">{name}</text>')
        bars.append(f'<text x="{x+bar_w//2}" y="{y-4}" text-anchor="middle" font-size="10" font-weight="bold">{s.get("score",0)}</text>')
    return f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg"><line x1="30" y1="{height-30}" x2="{width-20}" y2="{height-30}" stroke="#999"/>' + "".join(bars) + "</svg>"


def build_report_html_cn(report: dict) -> str:
    meta = report.get("meta", {})
    summary = report.get("summary", {})
    grade = report.get("quality_grade", "")
    rate = report.get("quality_rate", 0)
    indicators = report.get("indicators", {})
    sample_scores = report.get("sample_scores", [])
    details = report.get("details", [])
    problems = report.get("problems", [])
    suggestions = report.get("suggestions", [])
    appendix = report.get("appendix", {})
    execution_summary = report.get("execution_summary", "")
    indicator_analysis = report.get("indicator_analysis", [])

    ind_rows = "".join(
        f"<tr><td>{n}</td><td>{s['total']}</td><td>{s['passed']}</td><td>{s['failed']}</td></tr>"
        for n, s in indicators.items()
    )
    def _col_val(row: dict) -> str:
        return row.get("column") or (str(row.get("column_a", "")) + "/" + str(row.get("column_b", "")))

    det_rows = "".join(
        f'<tr><td>{r.get("datasource","")}</td><td>{r.get("rule_type","")}</td>'
        f'<td>{_col_val(r)}</td>'
        f'<td style="color:{"green" if r.get("status")=="passed" else "red"}">{r.get("status","")}</td>'
        f'<td>{r.get("message","")}</td></tr>'
        for r in details
    )
    prob_rows = "".join(
        f'<tr><td>{r.get("datasource","")}</td><td>{r.get("rule_type","")}</td>'
        f'<td>{r.get("column") or ""}</td><td>{r.get("message","")}</td></tr>'
        for r in problems[:20]
    )
    sugg_html = "".join(f"<li>{s}</li>" for s in suggestions)
    app_data_desc = "".join(f"<tr><td>{d.get('name','')}</td><td>{d.get('scope','')}</td></tr>" for d in appendix.get("data_description", []))
    app_rule_detail = "".join(f"<tr><td>{r.get('rule_type','')}</td><td>{r.get('column','')}</td><td>{r.get('indicator','')}</td></tr>" for r in appendix.get("rule_detail", []))
    app_samples = "".join(f"<tr><td>{s.get('datasource','')}</td><td>{s.get('rule_type','')}</td><td>{s.get('message','')}</td></tr>" for s in appendix.get("sample_records", []))

    tpl = Template("""
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>{{ meta.title }}</title>
<style>body{font-family:"Microsoft YaHei",sans-serif;padding:24px;max-width:900px;margin:0 auto;}
.cover{text-align:center;padding:80px 24px;page-break-after:always;}
.cover h1{font-size:26px;margin-bottom:16px;}
.cover p{font-size:14px;color:#666;}
h1{font-size:22px;border-bottom:2px solid #1976d2;padding-bottom:8px;}
h2{font-size:16px;margin-top:24px;}table{border-collapse:collapse;width:100%;}
th,td{border:1px solid #ddd;padding:8px;text-align:left;}
th{background:#f5f5f5;}.grade{font-size:24px;font-weight:bold;color:#1976d2;}</style>
</head>
<body>
<div class="cover">
<h1>{{ meta.title }}</h1>
<p>编制时间：{{ meta.created_at }}</p>
<p>依据标准：{{ meta.standard }}</p>
<p>评估任务：{{ meta.task_name }}</p>
<p>评估范围：{{ meta.evaluation_scope | join("、") if meta.evaluation_scope else "-" }}</p>
</div>
<h1>{{ meta.title }}</h1>
<p>编制时间：{{ meta.created_at }} | 依据标准：{{ meta.standard }}</p>
<p>评估任务：{{ meta.task_name }} | 评估范围：{{ meta.evaluation_scope | join("、") if meta.evaluation_scope else "-" }}</p>
<h2>一、执行摘要</h2>
<p style="margin:16px 0;line-height:1.6;color:#333;">{{ execution_summary }}</p>
<div style="display:flex;align-items:center;gap:24px;margin:16px 0;">
  {{ svg_gauge | safe }}
  <div>
    <p style="font-size:1.5rem;font-weight:bold;margin:0;">总评分：<span class="grade">{{ rate }}</span> 分</p>
    <p style="margin:8px 0 0;">质量等级：<span class="grade">{{ grade }}</span></p>
    <p style="color:#666;margin:4px 0 0;">总检查项 {{ summary.total }}，通过 <span style="color:green">{{ summary.passed }}</span>，失败 <span style="color:red">{{ summary.failed }}</span></p>
  </div>
</div>
<h2>二、参与评估的数据样板及得分</h2>
{{ svg_bars | safe }}
<table style="margin-top:16px;"><tr><th>数据样板</th><th>得分</th><th>等级</th><th>通过</th><th>失败</th></tr>
{% for s in sample_scores %}
<tr><td>{{ s.name }}</td><td>{{ s.score }}</td><td>{{ s.grade }}</td><td>{{ s.passed }}</td><td>{{ s.failed }}</td></tr>
{% endfor %}
</table>
<h2>三、评价指标体系与六维分析</h2>
<table><tr><th>指标</th><th>检查数</th><th>通过</th><th>失败</th><th>通过率</th><th>等级</th><th>说明</th></tr>
{% for ia in indicator_analysis %}
<tr><td>{{ ia.name }}</td><td>{{ ia.total }}</td><td>{{ ia.passed }}</td><td>{{ ia.failed }}</td><td>{{ ia.rate }}%</td><td>{{ ia.grade }}</td><td>{{ ia.comment }}</td></tr>
{% endfor %}
</table>
<h2>四、检查明细</h2>
<table><tr><th>数据源</th><th>规则类型</th><th>列</th><th>状态</th><th>说明</th></tr>{{ det_rows }}</table>
<h2>五、问题统计</h2>
<table><tr><th>数据源</th><th>规则类型</th><th>列</th><th>问题</th></tr>{{ prob_rows }}</table>
<h2>六、改进建议</h2><ul>{{ sugg_html }}</ul>
<h2>附录</h2>
<h3>附录A 数据说明</h3>
<table><tr><th>数据对象</th><th>说明</th></tr>{{ app_data_desc }}</table>
<h3>附录B 规则明细</h3>
<table><tr><th>规则类型</th><th>列</th><th>指标</th></tr>{{ app_rule_detail }}</table>
<h3>附录C 问题样例</h3>
<table><tr><th>数据源</th><th>规则类型</th><th>说明</th></tr>{{ app_samples }}</table>
</body></html>
""")
    ind_analysis_rows = "".join(
        f"<tr><td>{ia['name']}</td><td>{ia['total']}</td><td>{ia['passed']}</td><td>{ia['failed']}</td>"
        f"<td>{ia['rate']}%</td><td>{ia['grade']}</td><td>{ia['comment']}</td></tr>"
        for ia in indicator_analysis
    )
    return tpl.render(
        meta=meta, summary=summary, grade=grade, rate=rate,
        execution_summary=execution_summary, indicator_analysis=indicator_analysis,
        svg_gauge=Markup(_svg_gauge(rate)), svg_bars=Markup(_svg_bars(sample_scores)),
        sample_scores=sample_scores,
        ind_rows=Markup(ind_analysis_rows if indicator_analysis else ind_rows), det_rows=Markup(det_rows), prob_rows=Markup(prob_rows), sugg_html=Markup(sugg_html),
        app_data_desc=Markup(app_data_desc), app_rule_detail=Markup(app_rule_detail), app_samples=Markup(app_samples),
    )
