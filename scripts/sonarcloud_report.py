import os
import sys
import csv
import json
import ssl
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode

SONARCLOUD_URL = "https://sonarcloud.io"
PAGE_SIZE = 500

METRIC_KEYS = [
    "alert_status", "quality_gate_details",
    "bugs", "reliability_rating", "reliability_remediation_effort",
    "vulnerabilities", "security_rating", "security_remediation_effort",
    "security_hotspots", "security_review_rating", "security_review_remediation_effort",
    "code_smells", "sqale_rating", "sqale_index", "debt_ratio",
    "coverage", "line_coverage", "branch_coverage",
    "duplicated_lines_density", "duplicated_blocks",
    "ncloc", "files", "directories",
    "effort_to_reach_maintainability_rating_a",
    "tests", "test_execution_time", "test_failures", "test_errors",
    "complexity", "cognitive_complexity",
    "last_commit_date",
]


def api_get(token, endpoint, params=None):
    url = f"{SONARCLOUD_URL}{endpoint}"
    if params:
        url += "?" + urlencode(params, doseq=True)
    req = Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    })
    ctx = ssl.create_default_context()
    with urlopen(req, context=ctx, timeout=30) as resp:
        return json.loads(resp.read().decode())


def fetch_all_issues(token, project_key):
    params = {"componentKeys": project_key, "ps": str(PAGE_SIZE)}
    all_issues = []
    total = None
    page = 1

    while True:
        params["p"] = str(page)
        data = api_get(token, "/api/issues/search", params)
        issues = data.get("issues", [])
        all_issues.extend(issues)

        if total is None:
            total = data.get("total", 0)
        total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

        sys.stderr.write(f"  Page {page}/{total_pages} ({len(all_issues)}/{total} issues)\n")

        if len(all_issues) >= total:
            break
        page += 1

    return all_issues


def get_measures(token, project_key):
    data = api_get(token, "/api/measures/component", {
        "component": project_key,
        "metricKeys": ",".join(METRIC_KEYS),
    })
    measures = {}
    for m in data.get("component", {}).get("measures", []):
        measures[m["metric"]] = m.get("value", "N/A")
    return measures


def get_quality_gate(token, project_key):
    try:
        data = api_get(token, "/api/qualitygates/project_status", {
            "projectKey": project_key,
        })
        return data.get("projectStatus", {})
    except Exception:
        return None


def get_component(token, project_key):
    data = api_get(token, "/api/components/show", {"component": project_key})
    return data.get("component", {}).get("name", project_key)


def rating_stars(rating_val):
    if not rating_val or rating_val == "N/A":
        return "N/A"
    try:
        r = int(rating_val)
        return "⭐" * (6 - r) if 1 <= r <= 5 else str(r)
    except (ValueError, TypeError):
        return str(rating_val)


def generate_markdown(project_key, project_name, measures, qg, issues, output_dir):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    qg_status = qg.get("status", "N/A") if qg else "N/A"

    lines = [
        f"# SonarCloud Report - {project_name}",
        "",
        f"**Project:** {project_key}  ",
        f"**Generated:** {now}  ",
        f"**Quality Gate:** {'✅ PASSED' if qg_status == 'OK' else '❌ FAILED' if qg_status == 'ERROR' else '⏳ ' + qg_status}  ",
        f"**Total Issues:** {len(issues)}  ",
        "",
        "---",
        "",
        "## Key Metrics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
    ]

    metric_labels = {
        "ncloc": "Lines of Code (NCLOC)",
        "bugs": "Bugs",
        "vulnerabilities": "Vulnerabilities",
        "code_smells": "Code Smells",
        "coverage": "Coverage",
        "duplicated_lines_density": "Duplicated Lines (%)",
        "complexity": "Complexity",
        "cognitive_complexity": "Cognitive Complexity",
        "files": "Files",
        "directories": "Directories",
        "tests": "Tests",
        "test_failures": "Test Failures",
        "test_errors": "Test Errors",
        "security_hotspots": "Security Hotspots",
        "reliability_remediation_effort": "Reliability Remediation Effort (min)",
        "security_remediation_effort": "Security Remediation Effort (min)",
    }

    for key, label in metric_labels.items():
        val = measures.get(key, "N/A")
        suffix = "%" if key in ("coverage", "duplicated_lines_density") else ""
        lines.append(f"| {label} | {val}{suffix} |")

    lines += ["", "### Ratings", "", "| Metric | Rating |", "|--------|--------|"]
    for key, label in [
        ("reliability_rating", "Reliability"),
        ("security_rating", "Security"),
        ("sqale_rating", "Maintainability"),
        ("security_review_rating", "Security Review"),
    ]:
        lines.append(f"| {label} | {rating_stars(measures.get(key, 'N/A'))} |")

    lines += ["", "---", ""]

    severity_counts = {"BLOCKER": 0, "CRITICAL": 0, "MAJOR": 0, "MINOR": 0, "INFO": 0}
    type_counts = {}
    status_counts = {}

    for issue in issues:
        sev = issue.get("severity", "UNKNOWN")
        typ = issue.get("type", "UNKNOWN")
        stat = issue.get("status", "UNKNOWN")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        type_counts[typ] = type_counts.get(typ, 0) + 1
        status_counts[stat] = status_counts.get(stat, 0) + 1

    lines += ["## Issues by Severity", "", "| Severity | Count |", "|----------|-------|"]
    for sev in ["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO"]:
        count = severity_counts.get(sev, 0)
        if count > 0:
            lines.append(f"| {sev} | {count} |")

    lines += ["", "## Issues by Type", "", "| Type | Count |", "|------|-------|"]
    for typ, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {typ} | {count} |")

    lines += ["", "## Issues by Status", "", "| Status | Count |", "|--------|-------|"]
    for stat, count in sorted(status_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {stat} | {count} |")

    lines += ["", "---", ""]

    if issues:
        lines += ["## All Issues", "", "| # | Severity | Type | Status | File | Line | Message |",
                   "|---|----------|------|--------|------|------|---------|"]
        for i, issue in enumerate(issues[:200], 1):
            sev = issue.get("severity", "")
            typ = issue.get("type", "")
            stat = issue.get("status", "")
            component = issue.get("component", "")
            line = issue.get("line", "")
            message = issue.get("message", "")
            short_comp = "/".join(component.split("/")[-2:]) if component else ""
            msg_escaped = message.replace("|", "\\|") if message else ""
            lines.append(f"| {i} | {sev} | {typ} | {stat} | {short_comp} | {line} | {msg_escaped} |")

        if len(issues) > 200:
            lines.append(f"| ... | *{len(issues) - 200} more issues* | | | | | |")
        lines.append("")

    lines += [
        "---", "",
        f"*Report generated by SonarCloud Report Script on {now}*",
        "",
    ]

    report = "\n".join(lines)
    report_path = Path(output_dir) / "sonarcloud_report.md"
    report_path.write_text(report, encoding="utf-8")
    sys.stderr.write(f"  Report saved to {report_path}\n")
    return report_path


def generate_csv(issues, output_dir):
    csv_path = Path(output_dir) / "sonarcloud_issues.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Severity", "Type", "Status", "Component", "Line", "Message", "Rule", "Effort", "Creation Date"])
        for issue in issues:
            writer.writerow([
                issue.get("severity", ""),
                issue.get("type", ""),
                issue.get("status", ""),
                issue.get("component", ""),
                issue.get("line", ""),
                issue.get("message", ""),
                issue.get("rule", ""),
                issue.get("effort", ""),
                issue.get("creationDate", ""),
            ])
    sys.stderr.write(f"  CSV saved to {csv_path}\n")
    return csv_path


def main():
    token = os.environ.get("SONAR_TOKEN")
    project_key = os.environ.get("SONAR_PROJECT_KEY", "jhosue-pstr_All-In-One-Backend")
    output_dir = os.environ.get("REPORT_OUTPUT", "./cnes-report")

    if not token:
        sys.stderr.write("ERROR: SONAR_TOKEN environment variable is required\n")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    print(f"Project: {project_key}")

    print("Fetching component info...")
    try:
        project_name = get_component(token, project_key)
    except Exception as e:
        print(f"  WARNING: Could not fetch component: {e}")
        project_name = project_key

    print("Fetching quality gate...")
    qg = get_quality_gate(token, project_key)
    if qg:
        print(f"  Quality Gate: {qg.get('status', 'N/A')}")

    print("Fetching measures...")
    measures = get_measures(token, project_key)
    if measures:
        print(f"  Bugs: {measures.get('bugs', 'N/A')}")
        print(f"  Vulnerabilities: {measures.get('vulnerabilities', 'N/A')}")
        print(f"  Code Smells: {measures.get('code_smells', 'N/A')}")
        print(f"  Coverage: {measures.get('coverage', 'N/A')}%")

    print("Fetching all issues...")
    issues = fetch_all_issues(token, project_key)
    print(f"  Total issues fetched: {len(issues)}")

    print("Generating markdown report...")
    md_path = generate_markdown(project_key, project_name, measures, qg, issues, output_dir)

    print("Generating CSV...")
    csv_path = generate_csv(issues, output_dir)

    summary = {
        "project": project_key,
        "name": project_name,
        "quality_gate": qg.get("status") if qg else "unknown",
        "total_issues": len(issues),
        "measures": {k: v for k, v in measures.items() if v != "N/A"},
    }
    summary_path = Path(output_dir) / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"\nReport generated successfully!")
    print(f"  Markdown: {md_path}")
    print(f"  CSV: {csv_path}")
    print(f"  Summary: {summary_path}")


if __name__ == "__main__":
    main()
