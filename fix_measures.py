"""
Fix 7 DAX measures that use boolean expressions as CALCULATE filter arguments.
This breaks on Power BI Service refresh but works locally in PBI Desktop.

Uses TOM (Tabular Object Model) via pythonnet to modify measures in-place.
"""
import sys
import os

# Load DLLs
sys.path.append(r"C:\Program Files\On-premises data gateway")
sys.path.append(r"C:\Program Files\On-premises data gateway\FabricIntegrationRuntime\5.0\Gateway")

import clr
clr.AddReference("Microsoft.AnalysisServices.Tabular")
from Microsoft.AnalysisServices.Tabular import Server

# Connect
server = Server()
server.Connect("Provider=MSOLAP;Data Source=localhost:61836;")
db = server.Databases[0]
model = db.Model

TABLE_SALES = "PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines"
TABLE_INVOICE = "PowerBI_Factuurtermijnen_Invoice Terms"

t_sales = model.Tables.Find(TABLE_SALES)
t_invoice = model.Tables.Find(TABLE_INVOICE)

# =============================================
# FIX 1: Customer > 10k (in 12m)
# =============================================
m = t_sales.Measures.Find("Customer > 10k (in 12m)")
m.Expression = (
    "\n"
    "VAR _E = TODAY()\n"
    "VAR _S = EDATE(_E,-12)\n"
    "VAR _10k = \n"
    "CALCULATE(\n"
    "    COUNTROWS(\n"
    "        FILTER(\n"
    "            SUMMARIZE(\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines,\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Verkooprelatie_Sales relationship],\n"
    '                "TotalTurnover", SUM(PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Regelbedrag])\n'
    "            ),\n"
    "            [TotalTurnover] >= 10000\n"
    "        )\n"
    "    ),\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] > _S,\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] <= _E\n"
    ")\n"
    "VAR Total = CALCULATE(\n"
    "    DISTINCTCOUNT(PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Verkooprelatie_Sales relationship]),\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] > _S,\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] <= _E\n"
    ")\n"
    "RETURN\n"
    "_10k"
)
print("1/7 Customer > 10k (in 12m) - updated")

# =============================================
# FIX 2: Customer > 10k (12-24m)
# =============================================
m = t_sales.Measures.Find("Customer > 10k (12-24m)")
m.Expression = (
    "\n"
    "VAR _E = EDATE(TODAY(),-12)\n"
    "VAR _S = EDATE(_E,-12)\n"
    "VAR _10k = \n"
    "CALCULATE(\n"
    "    COUNTROWS(\n"
    "        FILTER(\n"
    "            SUMMARIZE(\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines,\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Verkooprelatie_Sales relationship],\n"
    '                "TotalTurnover", SUM(PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Regelbedrag])\n'
    "            ),\n"
    "            [TotalTurnover] >= 10000\n"
    "        )\n"
    "    ),\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] > _S,\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] <= _E\n"
    ")\n"
    "VAR Total = CALCULATE(\n"
    "    DISTINCTCOUNT(PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Verkooprelatie_Sales relationship]),\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] > _S,\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] <= _E\n"
    ")\n"
    "RETURN\n"
    "_10k"
)
print("2/7 Customer > 10k (12-24m) - updated")

# =============================================
# FIX 3: Customer 40k (in 12m)
# =============================================
m = t_sales.Measures.Find("Customer 40k (in 12m)")
m.Expression = (
    "\n"
    "VAR _E = TODAY()\n"
    "VAR _S = EDATE(_E,-12)\n"
    "VAR _40k = \n"
    "CALCULATE(\n"
    "    COUNTROWS(\n"
    "        FILTER(\n"
    "            SUMMARIZE(\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines,\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Verkooprelatie_Sales relationship],\n"
    '                "TotalTurnover", SUM(PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Regelbedrag])\n'
    "            ),\n"
    "            [TotalTurnover] >= 40000\n"
    "        )\n"
    "    ),\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] > _S,\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] <= _E\n"
    ")\n"
    "VAR Total = CALCULATE(\n"
    "    COUNTROWS(\n"
    "        FILTER(\n"
    "            SUMMARIZE(\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines,\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Verkooprelatie_Sales relationship],\n"
    '                "TotalTurnover", SUM(PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Regelbedrag])\n'
    "            ),\n"
    "            [TotalTurnover] >= 10000\n"
    "        )\n"
    "    ),\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] > _S,\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] <= _E\n"
    ")\n"
    "RETURN\n"
    "_40k/Total"
)
print("3/7 Customer 40k (in 12m) - updated")

# =============================================
# FIX 4: Customer 40k (12-24m)
# =============================================
m = t_sales.Measures.Find("Customer 40k (12-24m)")
m.Expression = (
    "\n"
    "VAR _E = EDATE(TODAY(),-12)\n"
    "VAR _S = EDATE(_E,-12)\n"
    "VAR _40k = \n"
    "CALCULATE(\n"
    "    COUNTROWS(\n"
    "        FILTER(\n"
    "            SUMMARIZE(\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines,\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Verkooprelatie_Sales relationship],\n"
    '                "TotalTurnover", SUM(PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Regelbedrag])\n'
    "            ),\n"
    "            [TotalTurnover] >= 40000\n"
    "        )\n"
    "    ),\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] > _S,\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] <= _E\n"
    ")\n"
    "VAR Total = CALCULATE(\n"
    "    COUNTROWS(\n"
    "        FILTER(\n"
    "            SUMMARIZE(\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines,\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Verkooprelatie_Sales relationship],\n"
    '                "TotalTurnover", SUM(PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Regelbedrag])\n'
    "            ),\n"
    "            [TotalTurnover] >= 10000\n"
    "        )\n"
    "    ),\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] > _S,\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] <= _E\n"
    ")\n"
    "RETURN\n"
    "_40k/Total"
)
print("4/7 Customer 40k (12-24m) - updated")

# =============================================
# FIX 5: Customer 100k (in 12m)
# =============================================
m = t_sales.Measures.Find("Customer 100k (in 12m)")
m.Expression = (
    "\n"
    "VAR _E = TODAY()\n"
    "VAR _S = EDATE(_E,-12)\n"
    "VAR _100k = \n"
    "CALCULATE(\n"
    "    COUNTROWS(\n"
    "        FILTER(\n"
    "            SUMMARIZE(\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines,\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Verkooprelatie_Sales relationship],\n"
    '                "TotalTurnover", SUM(PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Regelbedrag])\n'
    "            ),\n"
    "            [TotalTurnover] >= 100000\n"
    "        )\n"
    "    ),\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] > _S,\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] <= _E\n"
    ")\n"
    "VAR Total = CALCULATE(\n"
    "    COUNTROWS(\n"
    "        FILTER(\n"
    "            SUMMARIZE(\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines,\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Verkooprelatie_Sales relationship],\n"
    '                "TotalTurnover", SUM(PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Regelbedrag])\n'
    "            ),\n"
    "            [TotalTurnover] >= 10000\n"
    "        )\n"
    "    ),\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] > _S,\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] <= _E\n"
    ")\n"
    "RETURN\n"
    "_100k/Total"
)
print("5/7 Customer 100k (in 12m) - updated")

# =============================================
# FIX 6: Customer 100k (12-24m)
# =============================================
m = t_sales.Measures.Find("Customer 100k (12-24m)")
m.Expression = (
    "\n"
    "VAR _E = EDATE(TODAY(),-12)\n"
    "VAR _S = EDATE(_E,-12)\n"
    "VAR _100k = \n"
    "CALCULATE(\n"
    "    COUNTROWS(\n"
    "        FILTER(\n"
    "            SUMMARIZE(\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines,\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Verkooprelatie_Sales relationship],\n"
    '                "TotalTurnover", SUM(PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Regelbedrag])\n'
    "            ),\n"
    "            [TotalTurnover] >= 100000\n"
    "        )\n"
    "    ),\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] > _S,\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] <= _E\n"
    ")\n"
    "VAR Total = CALCULATE(\n"
    "    COUNTROWS(\n"
    "        FILTER(\n"
    "            SUMMARIZE(\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines,\n"
    "                PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Verkooprelatie_Sales relationship],\n"
    '                "TotalTurnover", SUM(PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Regelbedrag])\n'
    "            ),\n"
    "            [TotalTurnover] >= 10000\n"
    "        )\n"
    "    ),\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] > _S,\n"
    "    PowerBI_Verkoopfactuurregels_Sales_Invoice_Lines[rows.Factuurdatum] <= _E\n"
    ")\n"
    "RETURN\n"
    "_100k/Total"
)
print("6/7 Customer 100k (12-24m) - updated")

# =============================================
# FIX 7: Production (count)
# =============================================
m = t_invoice.Measures.Find("Production (count)")
m.Expression = (
    "CALCULATE(\n"
    "    COUNT('PowerBI_Factuurtermijnen_Invoice Terms'[Code]),\n"
    "    FILTER(\n"
    "        ALL('PowerBI_Factuurtermijnen_Invoice Terms'),\n"
    "        'PowerBI_Factuurtermijnen_Invoice Terms'[rows.Vervaldatum_2_Expiration] < TODAY()\n"
    "    )\n"
    ")"
)
print("7/7 Production (count) - updated")

# Save all changes at once
print()
print("Saving changes to model...")
model.SaveChanges()
print("ALL 7 MEASURES SAVED SUCCESSFULLY!")

server.Disconnect()
