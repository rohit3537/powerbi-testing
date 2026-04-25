"""
Pandas-based aggregation logic for ground truth validation.

Pure functions — no PBI dependencies. Takes a DataFrame of raw data,
applies date filters + row filters, aggregates, and returns the result
with a human-readable description of what was computed.
"""

import pandas as pd


AGGREGATION_FUNCTIONS = {
    "SUM": lambda s: s.sum(),
    "COUNT": lambda s: len(s),
    "DISTINCTCOUNT": lambda s: s.nunique(),
    "AVG": lambda s: s.mean(),
    "MIN": lambda s: s.min(),
    "MAX": lambda s: s.max(),
}


def aggregate(df, column, agg_type, date_column=None, start_date=None,
              end_date=None, filters=None):
    """
    Filter DataFrame by date range and row filters, then aggregate.

    Args:
        df: pandas DataFrame of raw data (column names already lowercase)
        column: column name to aggregate (lowercase)
        agg_type: one of SUM, COUNT, DISTINCTCOUNT, AVG, MIN, MAX
        date_column: column name for date filtering (lowercase), or None
        start_date: start date string/datetime, or None
        end_date: end date string/datetime, or None
        filters: dict of {column_name: value} for row-level filtering

    Returns:
        (result_value, metadata_dict) where metadata has row counts etc.
    """
    agg_type = agg_type.upper()
    if agg_type not in AGGREGATION_FUNCTIONS:
        raise ValueError(f"Unknown aggregation: {agg_type}. "
                         f"Supported: {list(AGGREGATION_FUNCTIONS.keys())}")

    total_rows = len(df)
    filtered = df.copy()

    # Apply date filter
    if date_column and start_date is not None and end_date is not None:
        filtered[date_column] = pd.to_datetime(filtered[date_column], errors="coerce")
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        filtered = filtered[
            (filtered[date_column] >= start) & (filtered[date_column] <= end)
        ]

    # Apply row-level filters
    applied_filters = {}
    if filters:
        for col, val in filters.items():
            col_lower = col.lower()
            if col_lower in filtered.columns:
                filtered = filtered[filtered[col_lower] == val]
                applied_filters[col] = val

    filtered_rows = len(filtered)

    # Aggregate
    agg_fn = AGGREGATION_FUNCTIONS[agg_type]
    if agg_type == "COUNT":
        result = filtered_rows
    elif agg_type == "DISTINCTCOUNT":
        result = agg_fn(filtered[column])
    else:
        series = pd.to_numeric(filtered[column], errors="coerce")
        result = agg_fn(series)

    # Convert numpy types to Python native for comparison
    if hasattr(result, "item"):
        result = result.item()

    metadata = {
        "total_rows": total_rows,
        "filtered_rows": filtered_rows,
        "applied_filters": applied_filters,
        "date_start": str(start_date) if start_date else None,
        "date_end": str(end_date) if end_date else None,
    }

    return result, metadata


def describe_logic(source_table, column, agg_type, start_date=None,
                   end_date=None, filters=None, total_rows=0,
                   filtered_rows=0):
    """
    Return a human-readable description of the Python computation.

    Example output:
        Source: EOD Data (LV) (2,847 rows pulled)
        Date filter: 2025-12-24 to 2026-03-24
        Row filter: Hospital = "Grady Memorial Hospital"
        Aggregation: SUM of [net revenue]
        Rows after filter: 47
    """
    lines = [f"Source: {source_table} ({total_rows:,} rows pulled)"]

    if start_date and end_date:
        lines.append(f"Date filter: {start_date} to {end_date}")

    if filters:
        for col, val in filters.items():
            lines.append(f"Row filter: {col} = \"{val}\"")

    lines.append(f"Aggregation: {agg_type.upper()} of [{column}]")
    lines.append(f"Rows after filter: {filtered_rows:,}")

    return "\n    ".join(lines)
