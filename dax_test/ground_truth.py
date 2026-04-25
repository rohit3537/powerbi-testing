"""
Ground truth validation engine.

Independently computes expected measure values using Python/pandas on raw
data pulled from the live PBI model, then compares against the DAX measure
result. This validates the measure LOGIC, not just that it returns a value.
"""

import time
from dataclasses import dataclass, field

import pandas as pd

from . import dax_builder, gt_aggregators
from .engine import compare_values


# Default anchor measures for dynamic date ranges
_DATE_ANCHORS = {
    "rolling_quarter": {
        "start": "'EOD Data (LV)'[RS_Rolling Qtr Start]",
        "end": "'EOD Data (LV)'[RS_Reporting Through]",
    },
    "rolling_quarter_minus_1": {
        "start": "'EOD Data (LV)'[RS_Rolling Qtr -1 Start]",
        "end": "'EOD Data (LV)'[RS_Rolling Qtr Start]",
    },
}


@dataclass
class GroundTruthResult:
    """Result of a ground truth validation test."""
    name: str
    passed: bool
    test_type: str = "ground_truth"
    actual: object = None        # Python-computed value
    expected: object = None      # DAX measure value
    message: str = ""
    duration_ms: float = 0
    dax_query: str = ""
    tags: list = field(default_factory=list)
    status: str = "PASS"
    # Ground-truth specific
    python_logic: str = ""
    source_table: str = ""
    row_count: int = 0
    filtered_count: int = 0
    date_start: str = ""
    date_end: str = ""


def run_ground_truth_test(test_def, run_query_fn, defaults=None):
    """
    Execute a ground truth validation test.

    Steps:
        1. Resolve date boundaries (query anchor measures from PBI)
        2. Pull raw data via SELECTCOLUMNS (only needed columns)
        3. Apply pandas aggregation with same filters
        4. Query the DAX measure for its result
        5. Compare Python vs DAX and return GroundTruthResult
    """
    defaults = defaults or {}
    name = test_def["name"]
    tags = test_def.get("tags", [])
    measure = test_def["measure"]
    validation = test_def["validation"]
    tolerance = test_def.get("tolerance", defaults.get("tolerance", 0.01))
    tolerance_pct = test_def.get("tolerance_pct", defaults.get("tolerance_pct"))

    source_table = validation["source_table"]
    column = validation["column"]
    agg_type = validation["aggregation"]
    date_column = validation.get("date_column")
    date_range = validation.get("date_range", {})
    filters = validation.get("filters", {})

    start = time.time()

    try:
        # Step 1: Resolve date boundaries
        date_start, date_end = resolve_date_range(
            date_range, run_query_fn, measure, filters
        )

        # Step 2: Pull raw data
        columns_needed = _columns_needed(column, date_column, filters)
        df = pull_raw_data(run_query_fn, source_table, columns_needed)
        row_count = len(df)

        # Step 3: Pandas aggregation
        python_value, metadata = gt_aggregators.aggregate(
            df, column.lower(), agg_type,
            date_column=date_column.lower() if date_column else None,
            start_date=date_start,
            end_date=date_end,
            filters=filters,
        )
        filtered_count = metadata["filtered_rows"]

        # Step 4: Query DAX measure
        dax_filters = {}
        if filters:
            for col, val in filters.items():
                dax_filters[f"'{source_table}'[{col}]"] = val
        dax = dax_builder.build_single_measure(measure, dax_filters or None)
        dax_rows = run_query_fn(dax)
        dax_value = dax_rows[0][0] if dax_rows and dax_rows[0] else None

        # Step 5: Compare
        passed, msg = compare_values(python_value, dax_value, tolerance, tolerance_pct)
        # For ground truth, we show Python as "actual" and DAX as "expected"
        # (Python is our independent check, DAX is what we're validating)

        logic_desc = gt_aggregators.describe_logic(
            source_table, column, agg_type,
            start_date=date_start, end_date=date_end,
            filters=filters,
            total_rows=row_count,
            filtered_rows=filtered_count,
        )

        elapsed = (time.time() - start) * 1000

        if not passed:
            msg = f"DAX: {dax_value}  Python: {python_value}  {msg}"

        return GroundTruthResult(
            name=name,
            passed=passed,
            actual=python_value,
            expected=dax_value,
            message=msg,
            duration_ms=elapsed,
            dax_query=dax,
            tags=tags,
            status="PASS" if passed else "FAIL",
            python_logic=logic_desc,
            source_table=source_table,
            row_count=row_count,
            filtered_count=filtered_count,
            date_start=str(date_start) if date_start else "",
            date_end=str(date_end) if date_end else "",
        )

    except Exception as e:
        elapsed = (time.time() - start) * 1000
        return GroundTruthResult(
            name=name,
            passed=False,
            message=f"Error: {e}",
            duration_ms=elapsed,
            tags=tags,
            status="ERROR",
            source_table=source_table,
        )


def resolve_date_range(date_range_def, run_query_fn, measure=None, filters=None):
    """
    Query PBI for anchor measure values, return (start_date, end_date).

    For 'fixed' type, returns the dates from the YAML directly.
    For dynamic types, queries the appropriate anchor measures.
    """
    range_type = date_range_def.get("type", "all")

    if range_type == "all":
        return None, None

    if range_type == "fixed":
        return date_range_def["start"], date_range_def["end"]

    # Dynamic types — query anchor measures
    if range_type in _DATE_ANCHORS:
        anchors = _DATE_ANCHORS[range_type]
        start_measure = date_range_def.get("start_measure", anchors["start"])
        end_measure = date_range_def.get("end_measure", anchors["end"])
    else:
        start_measure = date_range_def.get("start_measure")
        end_measure = date_range_def.get("end_measure")

    if not start_measure or not end_measure:
        raise ValueError(
            f"Date range type '{range_type}' requires start_measure and "
            f"end_measure (either built-in or specified in YAML)"
        )

    # Build DAX to query both dates in one call
    dax_filters = {}
    if filters:
        source = measure.split("[")[0].strip("'\" ") if measure else None
        if source:
            for col, val in filters.items():
                dax_filters[f"'{source}'[{col}]"] = val

    dax = f'EVALUATE ROW("Start", {start_measure}, "End", {end_measure})'
    if dax_filters:
        filter_clauses = []
        for k, v in dax_filters.items():
            filter_clauses.append(
                f"{k} = {dax_builder._format_filter_value(v)}"
            )
        filters_str = ", ".join(filter_clauses)
        dax = f"EVALUATE CALCULATETABLE(ROW(\"Start\", {start_measure}, \"End\", {end_measure}), {filters_str})"

    rows = run_query_fn(dax)
    if not rows or not rows[0]:
        raise ValueError(f"Anchor measure query returned no results: {dax}")

    return rows[0][0], rows[0][1]


def pull_raw_data(run_query_fn, table_name, columns):
    """
    Pull raw data from PBI via SELECTCOLUMNS.
    Returns a pandas DataFrame with lowercase column names.
    """
    cols_dax = ", ".join(
        f'"{col}", \'{table_name}\'[{col}]' for col in columns
    )
    dax = f"EVALUATE SELECTCOLUMNS('{table_name}', {cols_dax})"

    rows = run_query_fn(dax)

    df = pd.DataFrame(rows, columns=[c.lower() for c in columns])
    return df


def _columns_needed(column, date_column, filters):
    """Collect the unique set of columns we need to pull from PBI."""
    cols = {column}
    if date_column:
        cols.add(date_column)
    if filters:
        cols.update(filters.keys())
    return sorted(cols)
