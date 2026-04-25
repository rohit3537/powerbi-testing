"""
Output formatting for test results.

Supports:
  - Color-coded console output (ANSI)
  - JSON report file
  - Baseline snapshot save/compare
"""

import json
import os
from datetime import datetime


# ANSI color codes (disabled if NO_COLOR env var is set or not a terminal)
def _supports_color():
    if os.environ.get("NO_COLOR"):
        return False
    return True


_COLOR = _supports_color()
GREEN = "\033[92m" if _COLOR else ""
RED = "\033[91m" if _COLOR else ""
YELLOW = "\033[93m" if _COLOR else ""
RESET = "\033[0m" if _COLOR else ""
BOLD = "\033[1m" if _COLOR else ""
DIM = "\033[2m" if _COLOR else ""


def print_result(result, verbose=False):
    """Print a single test result line."""
    if result.test_type == "filter_matrix" and hasattr(result, "sub_results"):
        # Print sub-results instead of the summary
        return

    # Dispatch to specialized printer for ground_truth
    if result.test_type == "ground_truth":
        print_ground_truth_result(result, verbose)
        return

    if result.status == "PASS":
        icon = f"{GREEN}  PASS{RESET}"
    elif result.status == "FAIL":
        icon = f"{RED}  FAIL{RESET}"
    else:
        icon = f"{YELLOW}  ERROR{RESET}"

    ms = f"[{result.duration_ms:.0f}ms]"
    print(f"{icon}  {result.name:<55} {DIM}{ms}{RESET}")

    if not result.passed and result.message:
        print(f"        {result.message}")

    if verbose and result.dax_query:
        print(f"        {DIM}DAX: {result.dax_query}{RESET}")


def print_summary(results, suite_name="", port=None):
    """Print the final summary block."""
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    errors = sum(1 for r in results if r.status == "ERROR")
    total = len(results)
    total_ms = sum(r.duration_ms for r in results)

    # Collect all tags
    all_tags = set()
    for r in results:
        all_tags.update(r.tags)

    print()
    print("-" * 65)

    parts = []
    if passed:
        parts.append(f"{GREEN}{passed} passed{RESET}")
    if failed:
        parts.append(f"{RED}{failed} failed{RESET}")
    if errors:
        parts.append(f"{YELLOW}{errors} error{'s' if errors != 1 else ''}{RESET}")

    status_str = ", ".join(parts)
    print(f"Results: {status_str}  (Total: {total}, {total_ms:.0f}ms)")

    if all_tags:
        print(f"Tags tested: {', '.join(sorted(all_tags))}")


def print_header(suite_name, port, test_count):
    """Print the suite header."""
    print()
    print(f"{BOLD}DAX Measure Test Suite: {suite_name}{RESET}")
    if port:
        print(f"Connected to Power BI Desktop on port {port}")
    print(f"Running {test_count} tests...")
    print()


def save_json_report(results, suite_name, port, output_path):
    """Save results as a JSON report file."""
    data = {
        "suite": suite_name,
        "timestamp": datetime.now().isoformat(),
        "port": port,
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r.status == "PASS"),
            "failed": sum(1 for r in results if r.status == "FAIL"),
            "errors": sum(1 for r in results if r.status == "ERROR"),
        },
        "duration_ms": sum(r.duration_ms for r in results),
        "results": [
            {
                "name": r.name,
                "type": r.test_type,
                "passed": r.passed,
                "status": r.status,
                "actual": _serialize(r.actual),
                "expected": _serialize(r.expected),
                "message": r.message,
                "duration_ms": round(r.duration_ms, 1),
                "tags": r.tags,
                "dax_query": r.dax_query,
            }
            for r in results
        ],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)

    print(f"\nJSON report saved to: {output_path}")


def save_snapshot(results, output_path):
    """Save current measure values as a baseline snapshot."""
    snapshot = {}
    for r in results:
        if r.actual is not None:
            snapshot[r.name] = _serialize(r.actual)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, default=str)

    print(f"\nBaseline snapshot saved to: {output_path} ({len(snapshot)} values)")


def load_baseline(baseline_path):
    """Load a previously saved baseline snapshot."""
    with open(baseline_path, "r", encoding="utf-8") as f:
        return json.load(f)


def print_ground_truth_result(result, verbose=False):
    """Print a detailed ground truth validation result."""
    if result.status == "PASS":
        icon = f"{GREEN}  PASS{RESET}"
    elif result.status == "FAIL":
        icon = f"{RED}  FAIL{RESET}"
    else:
        icon = f"{YELLOW}  ERROR{RESET}"

    ms = f"[{result.duration_ms:,.0f}ms]"
    print(f"{icon}  {result.name:<55} {DIM}{ms}{RESET}")

    if result.status == "ERROR":
        print(f"        {result.message}")
        return

    # Show DAX vs Python values
    dax_val = _format_value(result.expected)
    py_val = _format_value(result.actual)

    if result.passed:
        print(f"        DAX Result:     {dax_val}")
        print(f"        Python Result:  {py_val}  {GREEN}MATCH{RESET}")
    else:
        print(f"        DAX Result:     {dax_val}")
        print(f"        Python Result:  {py_val}  {RED}MISMATCH{RESET}")
        if result.message:
            print(f"        {result.message}")

    # Show Python logic description
    if result.python_logic:
        print()
        print(f"        {DIM}Python Logic:{RESET}")
        for line in result.python_logic.split("\n"):
            print(f"        {DIM}  {line.strip()}{RESET}")

    if verbose and result.dax_query:
        print(f"        {DIM}DAX: {result.dax_query}{RESET}")

    print()


def print_review_report(reviews):
    """Print DAX review results to console."""
    for review in reviews:
        m = review.measure
        print()
        print(f"{BOLD}=== {m.name} ==={RESET}")
        print(f"Table: {m.table}")
        print(f"DAX: {DIM}{m.expression[:120]}{'...' if len(m.expression) > 120 else ''}{RESET}")

        # Dependencies
        deps = review.dependencies
        if deps.get("measures"):
            print(f"  Measures: {', '.join(deps['measures'])}")
        if deps.get("tables"):
            print(f"  Tables: {', '.join(deps['tables'])}")

        # Findings
        if review.findings:
            print()
            for f in review.findings:
                if f.severity == "WARNING":
                    icon = f"{YELLOW}  WARNING{RESET}"
                elif f.severity == "ERROR":
                    icon = f"{RED}  ERROR{RESET}"
                else:
                    icon = f"{DIM}  INFO{RESET}"
                print(f"  {icon}  [{f.category}] {f.message}")
                if f.suggestion:
                    print(f"          {DIM}{f.suggestion}{RESET}")
        else:
            print(f"  {GREEN}  No issues found{RESET}")

        # Requirement alignment
        if review.requirement:
            print()
            print(f"  Requirement: {DIM}{review.requirement[:100]}{'...' if len(review.requirement) > 100 else ''}{RESET}")
            print(f"  Alignment: {review.alignment}")

    # Summary
    total = len(reviews)
    with_warnings = sum(1 for r in reviews if any(f.severity == "WARNING" for f in r.findings))
    with_errors = sum(1 for r in reviews if any(f.severity == "ERROR" for f in r.findings))
    print()
    print("-" * 65)
    print(f"Reviewed {total} measures: {with_warnings} with warnings, {with_errors} with errors")


def save_review_markdown(reviews, output_path):
    """Save review results as a markdown file."""
    lines = ["# DAX Measure Review Report", ""]

    for review in reviews:
        m = review.measure
        lines.append(f"## {m.name}")
        lines.append(f"**Table:** {m.table}")
        lines.append(f"```dax\n{m.expression}\n```")

        deps = review.dependencies
        if deps.get("measures"):
            lines.append(f"**Depends on:** {', '.join(deps['measures'])}")

        if review.findings:
            lines.append("\n### Findings")
            for f in review.findings:
                icon = {"WARNING": "⚠️", "ERROR": "❌", "INFO": "ℹ️"}.get(f.severity, "")
                lines.append(f"- {icon} **{f.severity}** [{f.category}]: {f.message}")
                if f.suggestion:
                    lines.append(f"  - *Suggestion:* {f.suggestion}")
        else:
            lines.append("\n✅ No issues found")

        if review.requirement:
            lines.append(f"\n**Requirement:** {review.requirement}")
            lines.append(f"**Alignment:** {review.alignment}")

        lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nReview report saved to: {output_path}")


def _format_value(value):
    """Format a value for display."""
    if value is None:
        return "NULL"
    if isinstance(value, float):
        if abs(value) >= 1000:
            return f"{value:,.2f}"
        return f"{value:.4f}"
    return str(value)


def _serialize(value):
    """Convert a value to JSON-safe format."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return value
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)
