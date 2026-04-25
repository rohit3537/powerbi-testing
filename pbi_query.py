"""
Power BI Desktop connection helper.
Finds the open PBI file's Analysis Services port and connects via pyadomd.

Usage:
  uvx --python 3.12 --with pyadomd python pbi_query.py
  uvx --python 3.12 --with pyadomd python pbi_query.py "EVALUATE TOPN(10, sales)"

Requirements:
  - Power BI Desktop must be open with a file loaded
  - ADOMD client DLL installed (On-premises Data Gateway, Power BI Desktop, or SSAS)
  - Optional: set PBI_ADOMD_PATH env var to override the default DLL search paths
"""

import sys
import subprocess
import re
import os
import glob as _glob


def _find_adomd_path():
    """Auto-detect the ADOMD client DLL directory."""
    env_path = os.environ.get("PBI_ADOMD_PATH")
    if env_path and os.path.isdir(env_path):
        return env_path

    dll_name = "Microsoft.AnalysisServices.AdomdClient.dll"
    candidates = [
        r"C:\Program Files\On-premises data gateway",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces"),
        r"C:\Program Files\Microsoft Power BI Desktop\bin",
        r"C:\Program Files\Microsoft SQL Server\MSAS*\OLAP\bin",
    ]
    for c in candidates:
        if "*" in c:
            for m in _glob.glob(c):
                if os.path.isfile(os.path.join(m, dll_name)):
                    return m
        elif os.path.isfile(os.path.join(c, dll_name)):
            return c

    raise RuntimeError(
        f"Cannot find {dll_name}. Install the On-premises Data Gateway or "
        f"set PBI_ADOMD_PATH to the folder containing it."
    )


# Add ADOMD client DLL before importing pyadomd
sys.path.append(_find_adomd_path())

import clr
clr.AddReference('Microsoft.AnalysisServices.AdomdClient')

from pyadomd import Pyadomd


def find_pbi_port():
    """Auto-detect the port Power BI Desktop's Analysis Services is using."""
    # Get msmdsrv.exe PID
    result = subprocess.run(
        ['tasklist', '/fi', 'imagename eq msmdsrv.exe', '/fo', 'csv', '/nh'],
        capture_output=True, text=True
    )
    pids = re.findall(r'"msmdsrv\.exe","(\d+)"', result.stdout, re.IGNORECASE)
    if not pids:
        raise RuntimeError("Power BI Desktop does not appear to be open (msmdsrv.exe not found)")

    # Find LISTENING port for each PID
    netstat = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
    for pid in pids:
        for line in netstat.stdout.splitlines():
            if 'LISTENING' in line and line.strip().endswith(pid):
                match = re.search(r':(\d+)\s', line)
                if match:
                    port = int(match.group(1))
                    if port > 1024:
                        return port

    raise RuntimeError(f"Could not find listening port for msmdsrv.exe (PIDs: {pids})")


def connect(port=None):
    """Return a connected Pyadomd connection. Caller must use as context manager."""
    if port is None:
        port = find_pbi_port()
    conn_str = f'Provider=MSOLAP;Data Source=localhost:{port};'
    print(f"Connecting to Power BI Desktop on port {port}...")
    return Pyadomd(conn_str)


def run_query(dax, port=None):
    """Run a DAX query and return rows as a list of tuples."""
    with connect(port) as conn:
        with conn.cursor().execute(dax) as cur:
            return cur.fetchall()


def list_tables(port=None):
    rows = run_query(
        'EVALUATE SELECTCOLUMNS(INFO.VIEW.TABLES(), "Name", [Name], "IsHidden", [IsHidden])',
        port
    )
    visible = [r[0] for r in rows if not r[1]]
    hidden = [r[0] for r in rows if r[1]]
    print(f"\n=== TABLES ({len(visible)} visible, {len(hidden)} hidden) ===")
    for t in visible:
        print(f"  {t}")
    if hidden:
        print(f"\n  [hidden: {', '.join(hidden)}]")


def list_measures(port=None):
    rows = run_query(
        'EVALUATE SELECTCOLUMNS(INFO.VIEW.MEASURES(), "Table", [TableName], "Name", [Name], "Hidden", [IsHidden])',
        port
    )
    print(f"\n=== MEASURES ({len(rows)}) ===")
    for r in rows:
        hidden_tag = " [hidden]" if r[2] else ""
        print(f"  [{r[0]}] {r[1]}{hidden_tag}")


if __name__ == '__main__':
    dax = sys.argv[1] if len(sys.argv) > 1 else None

    if dax:
        rows = run_query(dax)
        print(f"\n{len(rows)} rows returned:")
        for row in rows:
            print(row)
    else:
        # Default: show model overview
        list_tables()
        list_measures()
