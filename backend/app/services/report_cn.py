# -*- coding: utf-8 -*-
"""
文件名: report_cn.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 中国标准(GB/T 36344-2018)数据质量评估报告生成模块
"""
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
    "accessibility": "可访问性",
}

# 规则类型中文名称（表格展示用）
RULE_TYPE_CN = {
    "completeness": "完整性检查",
    "uniqueness": "唯一性检查",
    "data_type": "数据类型检查",
    "validity_regex_match_check": "正则格式检查",
    "accuracy_range_check": "数值范围检查",
    "consistency_date_order_check": "日期顺序检查",
    "timeliness_fixed_range_check": "时效性检查",
    "accessibility": "可访问性检查",
}

# 状态中文
STATUS_CN = {"passed": "通过", "failed": "失败", "error": "错误"}


def _translate_message(msg: str, rule_type: str = "") -> str:
    """将英文消息翻译为中文，覆盖常见检查结果表述"""
    import re
    if not msg or not isinstance(msg, str):
        return msg or ""
    m = msg.strip()
    # 完整性
    if "No missing values found" in m:
        return "未发现缺失值。"
    if "Found " in m and " missing values" in m:
        n = re.search(r"Found (\d+) missing", m)
        return f"发现 {n.group(1)} 个缺失值。" if n else m
    # 唯一性
    if "No duplicate values found" in m:
        return "未发现重复值。"
    if "Found " in m and " duplicate values" in m:
        n = re.search(r"Found (\d+) duplicate", m)
        return f"发现 {n.group(1)} 个重复值。" if n else m
    # 数据类型
    if "Data type matches expected type" in m:
        return "数据类型符合预期。"
    if "Data type mismatch" in m:
        return "数据类型不匹配。"
    # 数值范围
    if "values out of range" in m:
        n = re.search(r"(\d+) values out of range", m)
        return f"{n.group(1)} 个值超出规定范围。" if n else m
    if "All numeric values are within range" in m:
        return "所有数值均在规定范围内。"
    if "values were non-numeric" in m:
        n = re.search(r"(\d+) values were non-numeric", m)
        return f"{n.group(1)} 个值非数值类型。" if n else m
    if "No valid numeric data" in m:
        n = re.search(r"(\d+) values were non-numeric", m)
        if n:
            return f"无法校验：{n.group(1)} 个值为非数值。"
        return "无有效数值可校验。"
    if "numeric values are within the specified range" in m or "out of" in m and "numeric values" in m:
        import re
        n1 = re.search(r"(\d+) out of (\d+) numeric", m)
        if n1:
            return f"共 {n1.group(2)} 个数值，其中 {n1.group(1)} 个在指定范围内。"
    # 日期顺序
    if "valid date pairs violated the order" in m:
        n = re.search(r"(\d+) out of (\d+) valid date pairs", m)
        if n:
            return f"在 {n.group(2)} 组有效日期对中，{n.group(1)} 组违反顺序（开始日期>结束日期）。"
        return m
    if "valid date pairs satisfy the order" in m:
        n = re.search(r"All (\d+) valid", m)
        return f"全部 {n.group(1)} 组日期对均满足顺序要求。" if n else "所有日期对顺序正确。"
    if "invalid/unparseable date" in m:
        n = re.search(r"(\d+) pairs had", m)
        return f"{n.group(1)} 组日期至少有一方无法解析。" if n else m
    if "No valid date pairs to compare" in m:
        return "无有效日期对可比较。"
    # 正则
    if "matched the pattern" in m and "did not match" in m:
        n = re.search(r"(\d+) out of (\d+).*?(\d+) did not match", m)
        if n:
            return f"共 {n.group(2)} 个可校验值，{n.group(1)} 个符合格式，{n.group(3)} 个不符合。"
    if "matched the pattern" in m and "did not match" not in m:
        n = re.search(r"(\d+) out of (\d+) applicable", m)
        if n:
            return f"共 {n.group(2)} 个可校验值，{n.group(1)} 个符合格式。"
    if "Column contains only null" in m or "No applicable string data" in m:
        return "列为空或仅含空值，无法校验。"
    # 时效性
    if "out of the specified range" in m and "parseable dates" in m:
        n = re.search(r"(\d+) parseable dates were out", m)
        return f"{n.group(1)} 个可解析日期超出规定时间范围。" if n else m
    if "could not be parsed as dates" in m:
        n = re.search(r"(\d+) values in the column", m)
        return f"{n.group(1)} 个值无法解析为日期。" if n else m
    if "All " in m and " parseable dates are within" in m:
        n = re.search(r"All (\d+) parseable", m)
        return f"全部 {n.group(1)} 个可解析日期均在规定范围内。" if n else "所有日期均在有效时间窗口内。"
    if "No parseable dates found" in m:
        return "未找到可解析的日期数据。"
    if "No dates to check" in m or "Column contains only null" in m:
        return "无日期数据可校验。"
    # 列不存在等错误
    if "not found in DataFrame" in m or ("Column '" in m and " not found" in m):
        c = re.search(r"Column\('([^']+)'\) not found", m)
        if c:
            return f"未找到列「{c.group(1)}」。"
        c2 = re.search(r"Column\(s\) '([^']+)' not found", m)
        if c2:
            return f"未找到列：{c2.group(1)}。"
    if "Invalid regular expression" in m:
        return "正则表达式格式无效。"
    if "Start date cannot be after end date" in m:
        return "开始日期不能晚于结束日期。"
    if "Invalid start_date or end_date" in m:
        return "开始/结束日期格式无效。"
    if "min_value" in m and "cannot be greater than max_value" in m:
        return "最小值不能大于最大值。"
    if "Missing " in m and " in " in m and "rule" in m:
        return "规则配置缺少必要参数。"
    if "No data to assess" in m:
        return "无数据可评估。"
    if "Unsupported rule type" in m:
        return "不支持的规则类型。"
    return m


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
            rt = r.get("rule_type", "")
            rule_detail.append({
                "rule_type": rt,
                "rule_type_cn": RULE_TYPE_CN.get(rt, rt),
                "column": r.get("column") or f"{r.get('column_a', '')}/{r.get('column_b', '')}",
                "indicator": RULE_TO_INDICATOR.get(rt, "规范性"),
            })

    # 为 details/problems 添加中文字段，供报告展示
    details_cn = []
    for r in details:
        rt = r.get("rule_type", "")
        st = r.get("status", "")
        details_cn.append({
            **r,
            "rule_type_cn": RULE_TYPE_CN.get(rt, rt),
            "status_cn": STATUS_CN.get(st, st),
            "message_cn": _translate_message(r.get("message", ""), rt),
        })
    problems_cn = [d for d in details_cn if d.get("status") != "passed"]

    appendix = {
        "data_description": [{"name": n, "scope": "评估对象"} for n in ds_names.values()],
        "rule_detail": rule_detail[:50],
        "sample_records": [
            {"datasource": r.get("datasource", ""), "rule_type_cn": r.get("rule_type_cn", ""), "message_cn": r.get("message_cn", r.get("message", ""))}
            for r in problems_cn[:10]
        ],
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
        "details_cn": details_cn,
        "problems": problems,
        "problems_cn": problems_cn,
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
    details_cn = report.get("details_cn", report.get("details", []))
    problems_cn = report.get("problems_cn", report.get("problems", []))
    suggestions = report.get("suggestions", [])
    appendix = report.get("appendix", {})
    execution_summary = report.get("execution_summary", "")
    indicator_analysis = report.get("indicator_analysis", [])

    def _col_val(row: dict) -> str:
        return row.get("column") or (str(row.get("column_a", "")) + " / " + str(row.get("column_b", "")))

    ind_rows = "".join(
        f"<tr><td>{n}</td><td>{s['total']}</td><td>{s['passed']}</td><td>{s['failed']}</td></tr>"
        for n, s in indicators.items()
    )
    # 检查明细表：使用中文规则类型、状态、说明
    det_rows = "".join(
        f'<tr><td>{r.get("datasource","")}</td><td>{r.get("rule_type_cn", r.get("rule_type",""))}</td>'
        f'<td>{_col_val(r)}</td>'
        f'<td class="status-{r.get("status","")}">{r.get("status_cn", r.get("status",""))}</td>'
        f'<td>{r.get("message_cn", r.get("message",""))}</td></tr>'
        for r in details_cn
    )
    # 问题统计表
    prob_rows = "".join(
        f'<tr><td>{r.get("datasource","")}</td><td>{r.get("rule_type_cn", r.get("rule_type",""))}</td>'
        f'<td>{r.get("column") or _col_val(r)}</td><td>{r.get("message_cn", r.get("message",""))}</td></tr>'
        for r in problems_cn[:20]
    )
    sugg_html = "".join(f"<li>{s}</li>" for s in suggestions)
    app_data_desc = "".join(f"<tr><td>{d.get('name','')}</td><td>{d.get('scope','')}</td></tr>" for d in appendix.get("data_description", []))
    # 附录规则明细：规则类型用中文
    app_rule_detail = "".join(
        f"<tr><td>{r.get('rule_type_cn', r.get('rule_type',''))}</td><td>{r.get('column','')}</td><td>{r.get('indicator','')}</td></tr>"
        for r in appendix.get("rule_detail", [])
    )
    app_samples = "".join(
        f"<tr><td>{s.get('datasource','')}</td><td>{s.get('rule_type_cn', s.get('rule_type',''))}</td><td>{s.get('message_cn', s.get('message',''))}</td></tr>"
        for s in appendix.get("sample_records", [])
    )

    tpl = Template("""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{{ meta.title }}</title>
  <style>
    :root{--primary:#1976d2;--success:#2e7d32;--danger:#c62828;--warning:#ed6c02;--gray:#666;}
    *{box-sizing:border-box;}
    body{font-family:"Microsoft YaHei","PingFang SC","SimHei",sans-serif;padding:32px;max-width:960px;margin:0 auto;line-height:1.6;color:#333;}
    .cover{text-align:center;padding:100px 24px;page-break-after:always;border-bottom:1px solid #eee;}
    .cover h1{font-size:28px;margin-bottom:24px;color:var(--primary);}
    .cover .meta{font-size:14px;color:var(--gray);line-height:2;}
    h1{font-size:22px;border-bottom:2px solid var(--primary);padding-bottom:10px;margin-top:0;}
    h2{font-size:17px;margin-top:32px;margin-bottom:12px;color:#333;}
    h3{font-size:15px;margin-top:20px;color:var(--gray);}
    table{border-collapse:collapse;width:100%;margin:16px 0;font-size:14px;box-shadow:0 1px 3px rgba(0,0,0,.08);border-radius:4px;overflow:hidden;}
    th,td{border:1px solid #e0e0e0;padding:10px 12px;text-align:left;}
    th{background:linear-gradient(180deg,#f8f9fa 0%,#eef0f2 100%);font-weight:600;color:#37474f;}
    tr:nth-child(even){background:#fafafa;}
    tr:hover{background:#f5f5f5;}
    .status-passed{color:var(--success);font-weight:600;}
    .status-failed,.status-error{color:var(--danger);font-weight:600;}
    .grade{font-size:26px;font-weight:bold;color:var(--primary);}
    .grade-优{color:var(--success);}
    .grade-良{color:var(--primary);}
    .grade-中{color:var(--warning);}
    .grade-差{color:var(--danger);}
    .summary-box{background:#f8f9fa;padding:20px;border-radius:8px;margin:16px 0;border-left:4px solid var(--primary);}
    .score-flex{display:flex;align-items:center;gap:32px;margin:20px 0;flex-wrap:wrap;}
    .suggestions ul{margin:12px 0;padding-left:24px;}
    .suggestions li{margin:8px 0;}
    @media print{body{padding:16px;}tr:hover{background:transparent;}}
  </style>
</head>
<body>
<div class="cover">
  <h1>{{ meta.title }}</h1>
  <div class="meta">
    <p>编制时间：{{ meta.created_at }}</p>
    <p>依据标准：{{ meta.standard }}</p>
    <p>评估任务：{{ meta.task_name }}</p>
    <p>评估范围：{{ meta.evaluation_scope | join("、") if meta.evaluation_scope else "-" }}</p>
  </div>
</div>

<h1>{{ meta.title }}</h1>
<p style="color:var(--gray);font-size:14px;">编制时间：{{ meta.created_at }} · 依据标准：{{ meta.standard }} · 评估范围：{{ meta.evaluation_scope | join("、") if meta.evaluation_scope else "-" }}</p>

<h2>一、执行摘要</h2>
<div class="summary-box">
  <p style="margin:0;">{{ execution_summary }}</p>
</div>
<div class="score-flex">
  {{ svg_gauge | safe }}
  <div>
    <p style="font-size:1.4rem;font-weight:bold;margin:0;">总评分：<span class="grade grade-{{ grade }}">{{ rate }}</span> 分</p>
    <p style="margin:10px 0 0;">质量等级：<span class="grade grade-{{ grade }}">{{ grade }}</span></p>
    <p style="color:var(--gray);margin:6px 0 0;font-size:14px;">总检查项 {{ summary.total }} · 通过 <span style="color:var(--success)">{{ summary.passed }}</span> · 失败 <span style="color:var(--danger)">{{ summary.failed }}</span></p>
  </div>
</div>

<h2>二、参与评估的数据样板及得分</h2>
{{ svg_bars | safe }}
<table><thead><tr><th>数据样板</th><th>得分</th><th>等级</th><th>通过</th><th>失败</th></tr></thead><tbody>
{% for s in sample_scores %}
<tr><td>{{ s.name }}</td><td>{{ s.score }}</td><td>{{ s.grade }}</td><td>{{ s.passed }}</td><td>{{ s.failed }}</td></tr>
{% endfor %}
</tbody></table>

<h2>三、评价指标体系与六维分析</h2>
<table><thead><tr><th>指标</th><th>检查数</th><th>通过</th><th>失败</th><th>通过率</th><th>等级</th><th>说明</th></tr></thead><tbody>
{% for ia in indicator_analysis %}
<tr><td>{{ ia.name }}</td><td>{{ ia.total }}</td><td>{{ ia.passed }}</td><td>{{ ia.failed }}</td><td>{{ ia.rate }}%</td><td>{{ ia.grade }}</td><td>{{ ia.comment }}</td></tr>
{% endfor %}
</tbody></table>

<h2>四、检查明细</h2>
<table><thead><tr><th>数据源</th><th>规则类型</th><th>列</th><th>状态</th><th>说明</th></tr></thead><tbody>{{ det_rows }}</tbody></table>

<h2>五、问题统计</h2>
<table><thead><tr><th>数据源</th><th>规则类型</th><th>列</th><th>问题描述</th></tr></thead><tbody>{{ prob_rows }}</tbody></table>

<h2>六、改进建议</h2>
<div class="suggestions"><ul>{{ sugg_html }}</ul></div>

<h2>附录</h2>
<h3>附录A 数据说明</h3>
<table><thead><tr><th>数据对象</th><th>说明</th></tr></thead><tbody>{{ app_data_desc }}</tbody></table>
<h3>附录B 规则明细</h3>
<table><thead><tr><th>规则类型</th><th>列</th><th>评价指标</th></tr></thead><tbody>{{ app_rule_detail }}</tbody></table>
<h3>附录C 问题样例</h3>
<table><thead><tr><th>数据源</th><th>规则类型</th><th>问题描述</th></tr></thead><tbody>{{ app_samples }}</tbody></table>
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
