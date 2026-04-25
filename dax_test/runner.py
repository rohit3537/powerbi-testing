"""
CLI entry point for the DAX testing framework.

Usage:
  python -m dax_test.runner tests/my_tests.yaml
  python -m dax_test.runner tests/my_tests.yaml --tags smoke critical
  python -m dax_test.runner tests/my_tests.yaml --name "RS_*"
  python -m dax_test.runner --auto-generate "./path/to/SemanticModel" --output tests/auto.yaml
  python -m dax_test.runner --list-measures "./path/to/SemanticModel"
  python -m dax_test.runner tests/my_tests.yaml --snapshot baselines/snap.json
  python -m dax_test.runner tests/my_tests.yaml --baseline baselines/snap.json
"""

import argparse
import sys
import os

# Ensure the project root is on the path so pbi_query can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml

import pbi_query
from dax_test import engine, report


def load_test_file(path):
    """Load and parse a YAML test file."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


def make_run_query(port):
    """Create a run_query function bound to a specific port."""
    conn_str = f'Provider=MSOLAP;Data Source=localhost:{port};'
    from pyadomd import Pyadomd

    def _run(dax):
        with Pyadomd(conn_str) as conn:
            with conn.cursor().execute(dax) as cur:
                return cur.fetchall()
    return _run


def cmd_run_tests(args):
    """Run test suite from a YAML file."""
    data = load_test_file(args.test_file)
    suite_name = data.get("project", os.path.basename(args.test_file))
    defaults = data.get("defaults", {})
    test_defs = data.get("tests", [])

    if not test_defs:
        print("No tests found in file.")
        sys.exit(0)

    # Connect
    port = args.port or pbi_query.find_pbi_port()

    # Verify connection
    try:
        run_query = make_run_query(port)
        run_query('EVALUATE ROW("ok", 1)')
    except Exception as e:
        print(f"Failed to connect to Power BI on port {port}: {e}")
        sys.exit(1)

    # Filter and run
    tag_filter = set(args.tags) if args.tags else None
    name_filter = args.name

    # Count tests that will run (for header)
    filtered = _filter_tests(test_defs, tag_filter, name_filter)
    report.print_header(suite_name, port, len(filtered))

    results = engine.run_suite(
        test_defs, run_query, defaults,
        tag_filter=tag_filter, name_filter=name_filter,
    )

    # Print results
    for r in results:
        report.print_result(r, verbose=args.verbose)

    report.print_summary(results, suite_name, port)

    # Save JSON report
    if args.report:
        report.save_json_report(results, suite_name, port, args.report)

    # Save snapshot
    if args.snapshot:
        report.save_snapshot(results, args.snapshot)

    # Compare baseline
    if args.baseline:
        _compare_baseline(results, args.baseline, defaults)

    # Exit code
    if any(not r.passed for r in results):
        sys.exit(1)


def cmd_auto_generate(args):
    """Auto-generate sanity tests from TMDL files."""
    from dax_test import autogen
    output = args.output or "tests/auto_generated.yaml"
    autogen.generate_sanity_tests(args.auto_generate, output)
    print(f"Generated test file: {output}")


def cmd_list_measures(args):
    """List all measures discovered in TMDL files."""
    from dax_test import tmdl_parser
    measures = tmdl_parser.discover_measures(args.list_measures)

    visible = [m for m in measures if not m.is_hidden]
    hidden = [m for m in measures if m.is_hidden]

    print(f"\nDiscovered {len(measures)} measures ({len(visible)} visible, {len(hidden)} hidden)")
    print()
    for m in sorted(visible, key=lambda x: (x.table, x.name)):
        fmt = f"  [{m.format_string}]" if m.format_string else ""
        print(f"  [{m.table}] {m.name}{fmt}")

    if hidden:
        print(f"\n  ({len(hidden)} hidden measures not shown)")


def _filter_tests(test_defs, tag_filter, name_filter):
    """Return the subset of tests that would run."""
    import fnmatch
    result = []
    for td in test_defs:
        if tag_filter:
            test_tags = set(td.get("tags", []))
            if not test_tags.intersection(tag_filter):
                continue
        if name_filter and not fnmatch.fnmatch(td["name"], name_filter):
            continue
        result.append(td)
    return result


def _compare_baseline(results, baseline_path, defaults):
    """Compare current results against a stored baseline."""
    baseline = report.load_baseline(baseline_path)
    tolerance = defaults.get("tolerance", 0.01)
    tolerance_pct = defaults.get("tolerance_pct")

    print(f"\n--- Baseline Comparison (vs {baseline_path}) ---")
    regressions = 0
    for r in results:
        if r.name in baseline and r.actual is not None:
            expected = baseline[r.name]
            try:
                passed, msg = engine.compare_numeric(
                    r.actual, expected, tolerance, tolerance_pct
                )
                if not passed:
                    regressions += 1
                    print(f"  REGRESSION  {r.name}")
                    print(f"              Baseline: {expected}  Current: {r.actual}")
            except Exception:
                pass

    if regressions == 0:
        print("  No regressions detected.")
    else:
        print(f"\n  {regressions} regression(s) detected!")


def cmd_review(args):
    """Review DAX measures from TMDL files."""
    from dax_test import review
    from dax_test import report as rpt

    reviews = review.review_all(
        args.review,
        requirements_path=args.requirements,
        measure_filter=args.review_measure,
    )

    if not reviews:
        print("No measures found to review.")
        sys.exit(0)

    rpt.print_review_report(reviews)

    if args.review_output:
        rpt.save_review_markdown(reviews, args.review_output)


def main():
    parser = argparse.ArgumentParser(
        description="DAX Measure Testing Framework for Power BI"
    )
    parser.add_argument("test_file", nargs="?", help="Path to YAML test file")
    parser.add_argument("--tags", nargs="+", help="Run only tests with these tags")
    parser.add_argument("--name", help="Run tests matching this name (glob pattern)")
    parser.add_argument(
        "--auto-generate", metavar="MODEL_PATH",
        help="Generate sanity tests from TMDL files at this SemanticModel path"
    )
    parser.add_argument("--output", help="Output path for auto-generated tests")
    parser.add_argument("--report", help="Save JSON report to this path")
    parser.add_argument(
        "--list-measures", metavar="MODEL_PATH",
        help="List all measures from TMDL files"
    )
    parser.add_argument("--snapshot", help="Save current values as baseline snapshot")
    parser.add_argument("--baseline", help="Compare results against stored baseline")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show DAX queries")
    parser.add_argument("--port", type=int, help="Override auto-detected PBI port")

    # DAX Review arguments
    parser.add_argument(
        "--review", metavar="MODEL_PATH",
        help="Review DAX measures from TMDL files for common issues"
    )
    parser.add_argument(
        "--review-measure", metavar="NAME",
        help="Review a specific measure by name (used with --review)"
    )
    parser.add_argument(
        "--requirements", metavar="PATH",
        help="Path to requirements.yaml for review alignment checking"
    )
    parser.add_argument(
        "--review-output", metavar="PATH",
        help="Save review report as markdown file"
    )

    args = parser.parse_args()

    # Dispatch
    if args.review:
        cmd_review(args)
    elif args.auto_generate:
        cmd_auto_generate(args)
    elif args.list_measures:
        cmd_list_measures(args)
    elif args.test_file:
        cmd_run_tests(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
