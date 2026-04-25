"""
DAX measure review engine.

Static analysis of DAX expressions from TMDL files:
- Dependency extraction (referenced measures, columns, tables)
- Pattern-based checks for common pitfalls
- Alignment with business requirements (optional requirements.yaml)
"""

import re
from dataclasses import dataclass, field

import yaml

from . import tmdl_parser, review_checks


@dataclass
class MeasureReview:
    """Review result for a single measure."""
    measure: object     # tmdl_parser.MeasureInfo
    findings: list = field(default_factory=list)
    dependencies: dict = field(default_factory=dict)
    requirement: str = ""
    alignment: str = "NOT DOCUMENTED"


def review_all(model_path, requirements_path=None, measure_filter=None):
    """
    Review all visible measures in a semantic model.

    Args:
        model_path: path to .SemanticModel directory
        requirements_path: optional path to requirements.yaml
        measure_filter: optional measure name to review (single measure)

    Returns:
        list of MeasureReview objects
    """
    measures = tmdl_parser.discover_measures(model_path)
    all_measure_names = {m.name for m in measures}

    # Load requirements if provided
    requirements = {}
    if requirements_path:
        requirements = _load_requirements(requirements_path)

    reviews = []
    for m in measures:
        if m.is_hidden:
            continue
        if measure_filter and m.name != measure_filter:
            continue

        review = review_measure(m, all_measure_names, requirements)
        reviews.append(review)

    return reviews


def review_measure(measure_info, all_measure_names=None, requirements=None):
    """
    Run all review checks on a single measure.

    Args:
        measure_info: tmdl_parser.MeasureInfo
        all_measure_names: set of all measure names in the model
        requirements: dict of measure_name -> requirement dict

    Returns:
        MeasureReview
    """
    all_measure_names = all_measure_names or set()
    requirements = requirements or {}
    expr = measure_info.expression

    # Extract dependencies
    deps = extract_dependencies(expr, all_measure_names)

    # Run pattern checks
    findings = review_checks.run_all_checks(expr)

    # Check requirement alignment
    req_text = ""
    alignment = "NOT DOCUMENTED"
    if measure_info.name in requirements:
        req_data = requirements[measure_info.name]
        req_text = req_data.get("description", "")
        alignment = _check_alignment(expr, req_text, deps)

    return MeasureReview(
        measure=measure_info,
        findings=findings,
        dependencies=deps,
        requirement=req_text,
        alignment=alignment,
    )


def extract_dependencies(expression, all_measure_names=None):
    """
    Extract referenced tables, columns, and measures from a DAX expression.

    Returns dict with keys: measures, columns, tables
    """
    all_measure_names = all_measure_names or set()

    # Tables: 'Table Name' pattern (before [)
    tables = set()
    for match in re.finditer(r"'([^']+)'\s*\[", expression):
        tables.add(match.group(1))

    # Qualified columns: 'Table'[Column]
    columns = set()
    for match in re.finditer(r"'([^']+)'\[([^\]]+)\]", expression):
        columns.add(f"'{match.group(1)}'[{match.group(2)}]")

    # Unqualified references: [Name] — could be measure or column in context
    unqualified = set()
    for match in re.finditer(r"(?<!')\[([^\]]+)\]", expression):
        name = match.group(1)
        # Skip DAX string literals inside quotes
        if name not in ("Result", "A", "B"):
            unqualified.add(name)

    # Classify unqualified as measures or columns
    measures_found = set()
    columns_unqualified = set()
    for name in unqualified:
        if name in all_measure_names:
            measures_found.add(name)
        else:
            columns_unqualified.add(name)

    # Merge qualified columns with unqualified ones
    all_columns = columns | {f"[{c}]" for c in columns_unqualified}

    return {
        "measures": sorted(measures_found),
        "columns": sorted(all_columns),
        "tables": sorted(tables),
    }


def _load_requirements(path):
    """Load requirements.yaml and return dict of measure_name -> requirement."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("measures", {})


def _check_alignment(expression, requirement_text, dependencies):
    """
    Simple heuristic alignment check between DAX expression and requirement.

    Returns one of: LIKELY MATCH, POSSIBLE MISMATCH, NEEDS REVIEW, NOT DOCUMENTED
    """
    if not requirement_text:
        return "NOT DOCUMENTED"

    req_lower = requirement_text.lower()
    expr_lower = expression.lower()
    score = 0
    reasons = []

    # Check aggregation alignment
    agg_keywords = {
        "sum": r"\bSUM\s*\(",
        "count": r"\bCOUNT(?:ROWS|A|X|BLANK)?\s*\(",
        "average": r"\b(?:AVERAGE|AVG)\s*\(",
        "distinct count": r"\bDISTINCTCOUNT\s*\(",
        "max": r"\bMAX\s*\(",
        "min": r"\bMIN\s*\(",
    }
    for keyword, pattern in agg_keywords.items():
        if keyword in req_lower and re.search(pattern, expr_lower):
            score += 2
            reasons.append(f"aggregation '{keyword}' matches")

    # Check if referenced columns appear in requirement
    for col in dependencies.get("columns", []):
        col_name = re.sub(r"['\[\]]", "", col).lower()
        if col_name in req_lower:
            score += 1
            reasons.append(f"column '{col_name}' mentioned in requirement")

    # Check date-related keywords
    date_keywords = ["date", "quarter", "month", "year", "rolling", "period"]
    for kw in date_keywords:
        if kw in req_lower and kw in expr_lower:
            score += 1

    # Check for filter-related keywords
    filter_keywords = ["filter", "where", "exclude", "include", "only"]
    req_has_filter = any(kw in req_lower for kw in filter_keywords)
    expr_has_filter = bool(re.search(r"\bFILTER\s*\(|\bCALCULATE\s*\(", expr_lower))
    if req_has_filter and expr_has_filter:
        score += 1
    elif req_has_filter and not expr_has_filter:
        score -= 1
        reasons.append("requirement mentions filtering but no FILTER/CALCULATE in DAX")

    if score >= 3:
        return f"LIKELY MATCH — {', '.join(reasons[:3])}"
    elif score >= 1:
        return f"NEEDS REVIEW — {', '.join(reasons[:3])}"
    else:
        detail = reasons[0] if reasons else "no matching patterns found"
        return f"POSSIBLE MISMATCH — {detail}"
