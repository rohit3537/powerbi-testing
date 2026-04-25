"""
Pattern-matching check functions for DAX measure review.

Each check function takes a DAX expression string and returns a list
of ReviewFinding objects. Checks are regex-based heuristics — not a
full DAX parser — so false positives are possible.
"""

import re
from dataclasses import dataclass


@dataclass
class ReviewFinding:
    """A single finding from a DAX review check."""
    severity: str       # INFO | WARNING | ERROR
    category: str       # e.g. "divide-by-zero", "filter-context"
    message: str
    suggestion: str = ""


def run_all_checks(expression):
    """Run all review checks on a DAX expression. Returns list of ReviewFinding."""
    findings = []
    for check_fn in _ALL_CHECKS:
        findings.extend(check_fn(expression))
    return findings


def check_divide_by_zero(expression):
    """Flag raw division (/) without DIVIDE() or IF zero-guard."""
    findings = []

    # Look for raw / operator (not inside comments or strings)
    # Simple heuristic: if expression has / but no DIVIDE(
    has_raw_div = bool(re.search(r'(?<!\w)/(?!\w)', expression))
    has_divide_fn = bool(re.search(r'\bDIVIDE\s*\(', expression, re.IGNORECASE))

    if has_raw_div and not has_divide_fn:
        # Check if there's an IF guard nearby
        has_if_zero = bool(re.search(r'\bIF\s*\([^)]*=\s*0', expression, re.IGNORECASE))
        if not has_if_zero:
            findings.append(ReviewFinding(
                severity="WARNING",
                category="divide-by-zero",
                message="Raw division (/) without DIVIDE() or IF zero-guard",
                suggestion="Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely",
            ))

    return findings


def check_divide_no_alternate(expression):
    """Flag DIVIDE() with only 2 arguments (no alternate result for zero)."""
    findings = []

    # Find DIVIDE( calls and check argument count
    # Simple heuristic: DIVIDE(x, y) has exactly one comma between parens
    for match in re.finditer(r'\bDIVIDE\s*\(', expression, re.IGNORECASE):
        start = match.end()
        # Count commas at depth 0 until closing paren
        depth = 1
        commas = 0
        i = start
        while i < len(expression) and depth > 0:
            ch = expression[i]
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            elif ch == ',' and depth == 1:
                commas += 1
            i += 1

        if commas == 1:
            findings.append(ReviewFinding(
                severity="INFO",
                category="divide-by-zero",
                message="DIVIDE() has only 2 arguments — returns BLANK on zero denominator",
                suggestion="Add a 3rd argument: DIVIDE(x, y, 0) to return 0 instead of BLANK",
            ))

    return findings


def check_filter_full_table(expression):
    """Flag FILTER('TableName', ...) — may iterate entire table."""
    findings = []

    # FILTER( followed by a table name (quoted or unquoted)
    pattern = r"\bFILTER\s*\(\s*'[^']+'"
    matches = re.findall(pattern, expression, re.IGNORECASE)

    for match in matches:
        # Check it's not FILTER(VALUES(...)) or FILTER(ALL(...))
        if not re.search(r'FILTER\s*\(\s*(?:VALUES|ALL|ALLSELECTED|DISTINCT)\s*\(', match, re.IGNORECASE):
            table_name = re.search(r"'([^']+)'", match).group(1)
            findings.append(ReviewFinding(
                severity="WARNING",
                category="performance",
                message=f"FILTER iterates entire '{table_name}' table",
                suggestion="Consider FILTER(VALUES(...)) or KEEPFILTERS() for better performance",
            ))

    return findings


def check_nested_calculate(expression):
    """Flag nested CALCULATE calls."""
    findings = []

    # Count CALCULATE occurrences
    calc_count = len(re.findall(r'\bCALCULATE\s*\(', expression, re.IGNORECASE))
    if calc_count >= 2:
        findings.append(ReviewFinding(
            severity="INFO",
            category="complexity",
            message=f"Nested CALCULATE detected ({calc_count} levels)",
            suggestion="Review filter context transitions — nested CALCULATE can behave unexpectedly",
        ))

    return findings


def check_blank_propagation(expression):
    """Flag arithmetic expressions that may propagate BLANK."""
    findings = []

    # If expression uses +, -, * on measures (not inside DIVIDE/IF/SWITCH)
    has_arithmetic = bool(re.search(r'\]\s*[-+*]\s*\[', expression))
    has_blank_guard = bool(re.search(
        r'\b(?:ISBLANK|IF|COALESCE|BLANK)\s*\(', expression, re.IGNORECASE
    ))

    if has_arithmetic and not has_blank_guard:
        findings.append(ReviewFinding(
            severity="INFO",
            category="blank-handling",
            message="Arithmetic on measures without BLANK guard — BLANK propagates through +, -, *",
            suggestion="Wrap with IF(ISBLANK([Measure]), 0, [Measure]) or use COALESCE()",
        ))

    return findings


def check_all_without_scope(expression):
    """Flag ALL('TableName') which removes all filters."""
    findings = []

    for match in re.finditer(r"\bALL\s*\(\s*'([^']+)'\s*\)", expression, re.IGNORECASE):
        table = match.group(1)
        findings.append(ReviewFinding(
            severity="INFO",
            category="filter-context",
            message=f"ALL('{table}') removes all filters on this table",
            suggestion="Verify this is intentional — slicers on this table will be ignored",
        ))

    return findings


def check_selectedvalue_no_alternate(expression):
    """Flag SELECTEDVALUE with no fallback argument."""
    findings = []

    for match in re.finditer(r'\bSELECTEDVALUE\s*\(', expression, re.IGNORECASE):
        start = match.end()
        depth = 1
        commas = 0
        i = start
        while i < len(expression) and depth > 0:
            ch = expression[i]
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            elif ch == ',' and depth == 1:
                commas += 1
            i += 1

        if commas == 0:
            findings.append(ReviewFinding(
                severity="WARNING",
                category="blank-handling",
                message="SELECTEDVALUE() without fallback — returns BLANK when multiple values selected",
                suggestion="Add a default: SELECTEDVALUE(Column, \"default\") or handle multi-select",
            ))

    return findings


def check_time_intelligence_context(expression):
    """Flag time intelligence functions without ALL on date table."""
    findings = []

    time_fns = [
        "DATESINPERIOD", "DATESBETWEEN", "DATESYTD", "DATESMTD",
        "DATESQTD", "SAMEPERIODLASTYEAR", "PREVIOUSMONTH",
        "PREVIOUSQUARTER", "PREVIOUSYEAR",
    ]

    for fn in time_fns:
        if re.search(rf'\b{fn}\s*\(', expression, re.IGNORECASE):
            has_all_date = bool(re.search(
                r"\bALL\s*\(\s*(?:'[^']*Date[^']*'|DateTable)", expression, re.IGNORECASE
            ))
            if not has_all_date:
                findings.append(ReviewFinding(
                    severity="INFO",
                    category="time-intelligence",
                    message=f"{fn}() used — ensure date slicer context is handled correctly",
                    suggestion="Typically used inside CALCULATE with appropriate date table context",
                ))
            break  # Only flag once per expression

    return findings


def check_iterators_on_large_tables(expression):
    """Flag SUMX/AVERAGEX/COUNTX on full tables."""
    findings = []

    iter_fns = ["SUMX", "AVERAGEX", "COUNTX", "MAXX", "MINX", "RANKX"]
    for fn in iter_fns:
        match = re.search(rf"\b{fn}\s*\(\s*'([^']+)'", expression, re.IGNORECASE)
        if match:
            table = match.group(1)
            findings.append(ReviewFinding(
                severity="INFO",
                category="performance",
                message=f"{fn}() iterates over '{table}' — may be slow on large tables",
                suggestion=f"Consider if a non-iterator pattern (e.g., CALCULATE + SUM) can achieve the same result",
            ))

    return findings


# Registry of all check functions
_ALL_CHECKS = [
    check_divide_by_zero,
    check_divide_no_alternate,
    check_filter_full_table,
    check_nested_calculate,
    check_blank_propagation,
    check_all_without_scope,
    check_selectedvalue_no_alternate,
    check_time_intelligence_context,
    check_iterators_on_large_tables,
]
