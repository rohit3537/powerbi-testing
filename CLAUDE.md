# Power BI Ongoing Testing — AI OS Project Agent

> **Part of AI OS.** Read `../../CLAUDE.md` for global rules. Read `../../shared/knowledge/` for cross-project learnings.
>
> **⚠ Verify latest state before answering.** Memory, this CLAUDE.md, project-state.yaml,
> and session logs are snapshots in time and go stale. Before recommending any file,
> function, config, or status: read the actual file, grep for the symbol, or run
> `git log -10` to confirm it still exists / is still true. If recalled info conflicts
> with live state, trust live state and update the stale source.
>
> **Shared resources:** `../../shared/knowledge/` (cross-project learnings)
>
> **Global rules (inherited):** CLI first / API last. Always test. Minimize tokens. Build modular. Commit frequently. Self-anneal.
>
> **Status: Experimental** — still exploring. Requires Python 3.12 + Power BI Desktop open.

---

# Power BI Project — Claude Instructions

## Connecting to an Open Power BI File

When the user asks to connect to their open Power BI file, use the following approach **directly** — no discovery needed.

### How to Connect

Use `uvx` with Python 3.12 and `pyadomd`. The helper script auto-detects the ADOMD DLL path.

**Step 1 — Find the port Power BI Desktop is listening on:**

```bash
# Option A: Use PowerShell (recommended, works in any shell)
powershell -Command "Get-Process msmdsrv -ErrorAction SilentlyContinue | Select-Object Id"
powershell -Command "Get-NetTCPConnection -OwningProcess <PID> -State Listen | Select-Object LocalPort"

# Option B: Use cmd
tasklist /fi "imagename eq msmdsrv.exe" /fo csv /nh
netstat -ano | findstr <PID>
# Look for LISTENING port (typically 5-digit, e.g. 64997)
```

**Step 2 — Run a DAX query using the helper script (preferred):**

```bash
uvx --python 3.12 --with pyadomd python pbi_query.py "EVALUATE <DAX_QUERY>"
```

**Step 2 (alt) — Inline DAX query if helper isn't available:**

```bash
uvx --python 3.12 --with pyadomd python -c "
import pbi_query
rows = pbi_query.run_query('EVALUATE <DAX_QUERY>')
for row in rows: print(row)
"
```

### Key Facts
- **uvx:** Must be on PATH, or set `UVX_PATH` env var. Find it with `where uvx` or `Get-Command uvx`
- **Python version:** Must be **3.12** (pythonnet doesn't support 3.14 yet)
- **ADOMD DLL:** Auto-detected by `pbi_query.py` from common install locations. Override with `PBI_ADOMD_PATH` env var if needed
- **Query syntax:** Use DAX `EVALUATE ...` statements, not SQL or DMX
- **List tables:** `EVALUATE SELECTCOLUMNS(INFO.VIEW.TABLES(), "Name", [Name], "IsHidden", [IsHidden])`

### Helper Script

A reusable script is at `pbi_query.py` in this project. It auto-detects both the ADOMD DLL path and the Power BI port:

```bash
# Show model overview (tables + measures)
uvx --python 3.12 --with pyadomd python pbi_query.py

# Run a specific DAX query
uvx --python 3.12 --with pyadomd python pbi_query.py "EVALUATE TOPN(10, sales)"
```

### DAX Test Framework

Run automated tests against live Power BI models:

```bash
# Run YAML-based tests (sanity, expected_value, measure_vs_measure, etc.)
uvx --python 3.12 --with pyadomd --with pyyaml python -m dax_test.runner tests/<test_file>.yaml -v

# Run ground truth validation (compares DAX results vs Python/pandas on raw data)
uvx --python 3.12 --with pyadomd --with pyyaml --with pandas python -m dax_test.runner tests/ztech_gt_tests.yaml -v

# Auto-generate sanity tests from TMDL
uvx --python 3.12 --with pyadomd --with pyyaml python -m dax_test.runner --auto-generate "./path/to/.SemanticModel" --output tests/auto.yaml

# Save snapshot baseline, then compare later
uvx --python 3.12 --with pyadomd --with pyyaml python -m dax_test.runner tests/<file>.yaml --snapshot baselines/snap.json
uvx --python 3.12 --with pyadomd --with pyyaml python -m dax_test.runner tests/<file>.yaml --baseline baselines/snap.json
```

### DAX Review (Static Analysis)

Review DAX measures for common pitfalls without connecting to PBI:

```bash
# Review all measures in a model
uvx --python 3.12 --with pyyaml python -m dax_test.runner --review "./path/to/.SemanticModel"

# Review a specific measure
uvx --python 3.12 --with pyyaml python -m dax_test.runner --review "./path/to/.SemanticModel" --review-measure "RS_Rolling Qtr Rev"

# Review with business requirements alignment check
uvx --python 3.12 --with pyyaml python -m dax_test.runner --review "./path/to/.SemanticModel" --requirements tests/requirements.yaml

# Save review as markdown
uvx --python 3.12 --with pyyaml python -m dax_test.runner --review "./path/to/.SemanticModel" --review-output review_report.md
```

### Setup on a New System

1. Install **Power BI Desktop**
2. Install **uv** — `winget install astral-sh.uv` (or see https://docs.astral.sh/uv/getting-started/installation/)
3. Install the **On-premises Data Gateway** (for the ADOMD client DLL) — or set `PBI_ADOMD_PATH` to wherever `Microsoft.AnalysisServices.AdomdClient.dll` lives
4. Open a `.pbip` file in Power BI Desktop
5. Run: `uvx --python 3.12 --with pyadomd python pbi_query.py`

---

## Project Context

This is an ongoing Power BI testing/development project for MESACO.

**Model tables include:** sales, transaction_line_items, opportunities, opp_lineitems, quotes, quote_lineitems, bookings, companies, contacts, Customers, forecasts, forecastByMonth, salesrepdetails, salesrepsummary, sales_team_names, sales_team_members, parts, Manufacturers, purchase_orders, PO_LineItems, Dates, Key Measures, CG_TimeIntelligence, CG_Relationships, and more.
