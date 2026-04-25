"""
Core test execution engine.

Runs DAX queries against a live Power BI model, compares results,
and returns structured TestResult objects.
"""

import time
from dataclasses import dataclass, field

from . import dax_builder


@dataclass
class TestResult:
    name: str
    passed: bool
    test_type: str
    actual: object = None
    expected: object = None
    message: str = ""
    duration_ms: float = 0
    dax_query: str = ""
    tags: list = field(default_factory=list)
    status: str = "PASS"  # PASS, FAIL, ERROR


def compare_values(actual, expected, tolerance=0.01, tolerance_pct=None):
    """Compare two values — handles dates, strings, and numerics.

    Returns (passed: bool, message: str).
    """
    if actual is None:
        return False, f"Actual is blank/null, expected {expected}"
    if expected is None:
        return True, ""

    # Date/datetime comparison
    import datetime
    if isinstance(actual, (datetime.date, datetime.datetime)) or isinstance(expected, (datetime.date, datetime.datetime)):
        if str(actual) == str(expected):
            return True, ""
        return False, f"Expected: {expected}  Actual: {actual}"

    # String comparison
    if isinstance(actual, str) and isinstance(expected, str):
        if actual == expected:
            return True, ""
        return False, f"Expected: '{expected}'  Actual: '{actual}'"

    return compare_numeric(actual, expected, tolerance, tolerance_pct)


def compare_numeric(actual, expected, tolerance=0.01, tolerance_pct=None):
    """Compare two numeric values with tolerance.

    Returns (passed: bool, message: str).
    """
    if actual is None:
        return False, f"Actual is blank/null, expected {expected}"
    if expected is None:
        return True, ""

    try:
        a = float(actual)
        e = float(expected)
    except (TypeError, ValueError):
        return False, f"Cannot compare non-numeric: actual={actual}, expected={expected}"

    diff = abs(a - e)

    if tolerance_pct is not None and e != 0:
        rel_diff = diff / abs(e)
        if rel_diff <= tolerance_pct:
            return True, ""
        return False, f"Expected: {e}  Actual: {a}  Diff: {diff} ({rel_diff:.4%} > {tolerance_pct:.4%})"

    if diff <= tolerance:
        return True, ""
    return False, f"Expected: {e}  Actual: {a}  Diff: {diff}"


def _run_dax(run_query_fn, dax):
    """Execute a DAX query and return the first row, or raise."""
    rows = run_query_fn(dax)
    if not rows:
        return None
    return rows[0]


def run_test(test_def, run_query_fn, defaults=None):
    """Execute a single test and return a TestResult.

    Args:
        test_def: dict from YAML with name, type, measure, etc.
        run_query_fn: callable(dax_string) -> list of tuples
        defaults: dict with default tolerance, tolerance_pct, etc.
    """
    defaults = defaults or {}
    name = test_def["name"]
    test_type = test_def["type"]
    tags = test_def.get("tags", [])
    tolerance = test_def.get("tolerance", defaults.get("tolerance", 0.01))
    tolerance_pct = test_def.get("tolerance_pct", defaults.get("tolerance_pct"))

    start = time.time()

    # Handle filter_matrix by dispatching sub-tests
    if test_type == "filter_matrix":
        return _run_filter_matrix(test_def, run_query_fn, defaults)

    # Handle ground_truth via dedicated module
    if test_type == "ground_truth":
        from . import ground_truth
        return ground_truth.run_ground_truth_test(test_def, run_query_fn, defaults)

    # Build DAX
    try:
        dax = dax_builder.build_for_test(test_def)
    except Exception as e:
        return TestResult(
            name=name, passed=False, test_type=test_type, tags=tags,
            message=f"DAX build error: {e}", status="ERROR",
            duration_ms=(time.time() - start) * 1000,
        )

    # Execute
    try:
        row = _run_dax(run_query_fn, dax)
    except Exception as e:
        return TestResult(
            name=name, passed=False, test_type=test_type, tags=tags,
            dax_query=dax, message=f"DAX Error: {e}", status="ERROR",
            duration_ms=(time.time() - start) * 1000,
        )

    elapsed = (time.time() - start) * 1000

    # Evaluate based on type
    if test_type == "expected_value":
        actual = row[0] if row else None
        expected = test_def["expected"]
        passed, msg = compare_values(actual, expected, tolerance, tolerance_pct)
        return TestResult(
            name=name, passed=passed, test_type=test_type, actual=actual,
            expected=expected, message=msg, duration_ms=elapsed,
            dax_query=dax, tags=tags, status="PASS" if passed else "FAIL",
        )

    elif test_type == "measure_vs_measure":
        a_val = row[0] if row else None
        b_val = row[1] if row and len(row) > 1 else None
        passed, msg = compare_values(a_val, b_val, tolerance, tolerance_pct)
        return TestResult(
            name=name, passed=passed, test_type=test_type, actual=a_val,
            expected=b_val, message=msg, duration_ms=elapsed,
            dax_query=dax, tags=tags, status="PASS" if passed else "FAIL",
        )

    elif test_type == "not_blank":
        actual = row[0] if row else None
        passed = actual is not None
        msg = "" if passed else "Measure returned blank/null"
        return TestResult(
            name=name, passed=passed, test_type=test_type, actual=actual,
            message=msg, duration_ms=elapsed, dax_query=dax, tags=tags,
            status="PASS" if passed else "FAIL",
        )

    elif test_type == "is_numeric":
        actual = row[0] if row else None
        passed = isinstance(actual, (int, float))
        msg = "" if passed else f"Expected numeric, got {type(actual).__name__}: {actual}"
        return TestResult(
            name=name, passed=passed, test_type=test_type, actual=actual,
            message=msg, duration_ms=elapsed, dax_query=dax, tags=tags,
            status="PASS" if passed else "FAIL",
        )

    elif test_type == "in_range":
        actual = row[0] if row else None
        lo = test_def.get("min")
        hi = test_def.get("max")
        try:
            val = float(actual) if actual is not None else None
        except (TypeError, ValueError):
            val = None

        if val is None:
            passed, msg = False, f"Actual is blank/null"
        elif lo is not None and val < lo:
            passed, msg = False, f"Actual: {val} < min: {lo}"
        elif hi is not None and val > hi:
            passed, msg = False, f"Actual: {val} > max: {hi}"
        else:
            passed, msg = True, ""

        return TestResult(
            name=name, passed=passed, test_type=test_type, actual=actual,
            expected=f"[{lo}, {hi}]", message=msg, duration_ms=elapsed,
            dax_query=dax, tags=tags, status="PASS" if passed else "FAIL",
        )

    else:
        return TestResult(
            name=name, passed=False, test_type=test_type, tags=tags,
            message=f"Unknown test type: {test_type}", status="ERROR",
            duration_ms=elapsed, dax_query=dax,
        )


def _run_filter_matrix(test_def, run_query_fn, defaults):
    """Run a filter_matrix test — multiple sub-contexts for the same measure."""
    name = test_def["name"]
    tags = test_def.get("tags", [])
    measure = test_def["measure"]
    contexts = test_def.get("contexts", [])

    results = []
    all_passed = True
    total_ms = 0

    for ctx in contexts:
        label = ctx.get("label", "unnamed")
        sub_name = f"{name} / {label}"
        check_type = ctx.get("check", "not_blank")

        sub_def = {
            "name": sub_name,
            "type": check_type,
            "measure": measure,
            "filters": ctx.get("filters", {}),
            "tags": tags,
        }
        # Carry over expected/min/max if the check type needs them
        for key in ("expected", "min", "max", "tolerance", "tolerance_pct"):
            if key in ctx:
                sub_def[key] = ctx[key]

        result = run_test(sub_def, run_query_fn, defaults)
        results.append(result)
        total_ms += result.duration_ms
        if not result.passed:
            all_passed = False

    # Return a summary result; individual sub-results are in .sub_results
    summary = TestResult(
        name=name, passed=all_passed, test_type="filter_matrix",
        message=f"{sum(1 for r in results if r.passed)}/{len(results)} contexts passed",
        duration_ms=total_ms, tags=tags,
        status="PASS" if all_passed else "FAIL",
    )
    summary.sub_results = results
    return summary


def run_suite(test_defs, run_query_fn, defaults=None, tag_filter=None, name_filter=None):
    """Run a list of test definitions and return all TestResults.

    Args:
        test_defs: list of test definition dicts
        run_query_fn: callable(dax) -> list of tuples
        defaults: dict of default settings
        tag_filter: list of tags — only run tests that have at least one matching tag
        name_filter: glob pattern for test names (fnmatch)
    """
    import fnmatch

    results = []
    for td in test_defs:
        # Filter by tags
        if tag_filter:
            test_tags = set(td.get("tags", []))
            if not test_tags.intersection(tag_filter):
                continue

        # Filter by name
        if name_filter and not fnmatch.fnmatch(td["name"], name_filter):
            continue

        result = run_test(td, run_query_fn, defaults)
        results.append(result)

        # Flatten filter_matrix sub-results into the main list for reporting
        if hasattr(result, "sub_results"):
            results.extend(result.sub_results)

    return results
