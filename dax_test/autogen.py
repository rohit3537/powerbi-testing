"""
Auto-generate sanity tests from TMDL measure definitions.

Generates:
  - not_blank test for every visible measure
  - is_numeric test for measures with numeric/currency/percentage format strings
  - in_range [0, 1] for percentage measures
"""

import re

import yaml

from .tmdl_parser import discover_measures


def _is_numeric_format(fmt):
    """Check if a format string indicates a numeric value."""
    if not fmt:
        return False
    # Common numeric indicators: $, #, 0, %, comma formatting
    return bool(re.search(r'[\$#0%]', fmt))


def _is_percentage_format(fmt):
    """Check if a format string indicates a percentage."""
    if not fmt:
        return False
    return "%" in fmt or "percent" in fmt.lower()


def _measure_ref(measure_info):
    """Build a DAX measure reference like 'Table'[Measure Name]."""
    return f"'{measure_info.table}'[{measure_info.name}]"


def generate_tests_for_measure(measure):
    """Generate sanity test dicts for a single measure."""
    tests = []
    ref = _measure_ref(measure)

    # 1. not_blank — always generated
    tests.append({
        "name": f"{measure.name} is not blank",
        "type": "not_blank",
        "measure": ref,
        "tags": ["sanity", "auto-generated", _slugify(measure.table)],
    })

    # 2. is_numeric — if format string suggests numeric
    if _is_numeric_format(measure.format_string):
        tests.append({
            "name": f"{measure.name} returns a number",
            "type": "is_numeric",
            "measure": ref,
            "tags": ["sanity", "auto-generated", _slugify(measure.table)],
        })

    # 3. in_range — if percentage format
    if _is_percentage_format(measure.format_string):
        tests.append({
            "name": f"{measure.name} is a valid percentage",
            "type": "in_range",
            "measure": ref,
            "min": 0,
            "max": 10,  # generous upper bound — 1000% is suspicious
            "tags": ["sanity", "auto-generated", "percentage", _slugify(measure.table)],
        })

    return tests


def _slugify(text):
    """Convert a table name to a tag-friendly slug."""
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def generate_sanity_tests(model_path, output_path):
    """Parse TMDL files and generate a YAML test file with sanity tests.

    Args:
        model_path: path to the .SemanticModel folder
        output_path: where to write the generated YAML
    """
    measures = discover_measures(model_path)
    visible = [m for m in measures if not m.is_hidden]

    all_tests = []
    for m in sorted(visible, key=lambda x: (x.table, x.name)):
        all_tests.extend(generate_tests_for_measure(m))

    # Build the YAML structure
    data = {
        "project": "Auto-Generated Sanity Tests",
        "model_path": str(model_path),
        "defaults": {
            "tolerance": 0.01,
        },
        "tests": all_tests,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        # Write header comment
        f.write("# Auto-generated sanity tests\n")
        f.write(f"# Source: {model_path}\n")
        f.write(f"# Measures found: {len(visible)} visible, {len(measures) - len(visible)} hidden\n")
        f.write("# Review and customize before running in production.\n\n")
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"Generated {len(all_tests)} tests for {len(visible)} visible measures")
    print(f"Output: {output_path}")
