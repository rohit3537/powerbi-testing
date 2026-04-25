"""
Generates DAX EVALUATE statements from test definitions.

Each test type maps to a specific DAX pattern:
  - Single measure:      EVALUATE ROW("Result", <measure>)
  - Two measures:         EVALUATE ROW("A", <measure_a>, "B", <measure_b>)
  - With filters:         EVALUATE CALCULATETABLE(ROW(...), filter1, filter2, ...)
"""


def _format_filter_value(value):
    """Format a Python value as a DAX literal."""
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    return str(value)


def _wrap_with_filters(inner_dax, filters):
    """Wrap a DAX expression with CALCULATETABLE if filters are provided."""
    if not filters:
        return f"EVALUATE {inner_dax}"

    filter_clauses = []
    for col_ref, value in filters.items():
        lit = _format_filter_value(value)
        filter_clauses.append(f"{col_ref} = {lit}")

    filters_str = ",\n    ".join(filter_clauses)
    return f"EVALUATE CALCULATETABLE(\n    {inner_dax},\n    {filters_str}\n)"


def build_single_measure(measure, filters=None):
    """Build DAX for evaluating a single measure.

    Returns: DAX string
    """
    inner = f'ROW("Result", {measure})'
    return _wrap_with_filters(inner, filters)


def build_measure_vs_measure(measure_a, measure_b, filters=None):
    """Build DAX for comparing two measures side by side.

    Returns: DAX string
    """
    inner = f'ROW("A", {measure_a}, "B", {measure_b})'
    return _wrap_with_filters(inner, filters)


def build_for_test(test_def):
    """Build the DAX query for a test definition dict.

    Args:
        test_def: dict with keys like type, measure, measure_a, measure_b, filters, etc.

    Returns: DAX query string
    """
    test_type = test_def["type"]
    filters = test_def.get("filters")

    if test_type == "measure_vs_measure":
        return build_measure_vs_measure(
            test_def["measure_a"], test_def["measure_b"], filters
        )
    elif test_type in ("expected_value", "not_blank", "is_numeric", "in_range"):
        return build_single_measure(test_def["measure"], filters)
    elif test_type == "filter_matrix":
        # filter_matrix is handled by the engine — it calls build_single_measure
        # per context. This returns the unfiltered version as a fallback.
        return build_single_measure(test_def["measure"], filters)
    else:
        raise ValueError(f"Unknown test type: {test_type}")
