"""
Create a duplicate of the Buyer Supplier Report page with redesigned visuals
following the SpendMend/Trulla design system.

Colors:
  Teal: #5BBFB5 (primary)
  Teal Dark: #3EA89D
  Gold: #D4C94A (secondary)
  Charcoal: #2D3436 (table headers, text)
  Light Gray: #F7F8FA (page bg)
  Border: #E2E8F0
"""

import json
import os
import copy

REPORT_DIR = (
    r"D:\Agentic Development v2\projects\powerbi-testing\workbooks"
    r"\PSJH Retail Purchasing\PSJH.Report\definition\pages"
)

OLD_PAGE_ID = "c49630fd3e73dd147997"
NEW_PAGE_ID = "buyer_supplier_v2_redesign"

# Read original page.json
with open(os.path.join(REPORT_DIR, OLD_PAGE_ID, "page.json"), "r", encoding="utf-8") as f:
    old_page = json.load(f)

# Create new page directory and visuals directory
new_page_dir = os.path.join(REPORT_DIR, NEW_PAGE_ID)
new_vis_dir = os.path.join(new_page_dir, "visuals")
os.makedirs(new_vis_dir, exist_ok=True)

# New page.json — same filters, new name
new_page = copy.deepcopy(old_page)
new_page["name"] = NEW_PAGE_ID
new_page["displayName"] = "Buyer Supplier Report v2"
# Set page background to light gray #F7F8FA
new_page["background"] = {
    "color": {"expr": {"Literal": {"Value": "'#F7F8FA'"}}},
    "transparency": {"expr": {"Literal": {"Value": "0D"}}},
    "show": {"expr": {"Literal": {"Value": "true"}}}
}

with open(os.path.join(new_page_dir, "page.json"), "w", encoding="utf-8") as f:
    json.dump(new_page, f, indent=2, ensure_ascii=False)

SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json"


def lit(val):
    return {"expr": {"Literal": {"Value": val}}}


def color_lit(hex_color):
    return {"solid": {"color": {"expr": {"Literal": {"Value": f"'{hex_color}'"}}}}}


def write_visual(name, data):
    vis_dir = os.path.join(new_vis_dir, name)
    os.makedirs(vis_dir, exist_ok=True)
    with open(os.path.join(vis_dir, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Created: {name}")


# ─── 1. HEADER BACKGROUND SHAPE (teal bottom border) ───
write_visual("hdr_bg_shape_001", {
    "$schema": SCHEMA,
    "name": "hdr_bg_shape_001",
    "position": {"x": 0, "y": 0, "z": 0, "height": 54, "width": 1280, "tabOrder": 0},
    "visual": {
        "visualType": "shape",
        "objects": {
            "line": [{"properties": {"show": lit("false")}}],
            "fill": [{"properties": {"fillColor": color_lit("#FFFFFF"), "transparency": lit("0D")}}],
            "rotation": [{"properties": {"angle": lit("0D")}}]
        },
        "drillFilterOtherVisuals": True
    }
})

# ─── 2. TEAL ACCENT LINE UNDER HEADER ───
write_visual("hdr_accent_line_002", {
    "$schema": SCHEMA,
    "name": "hdr_accent_line_002",
    "position": {"x": 0, "y": 52, "z": 100, "height": 3, "width": 1280, "tabOrder": 100},
    "visual": {
        "visualType": "shape",
        "objects": {
            "line": [{"properties": {"show": lit("false")}}],
            "fill": [{"properties": {"fillColor": color_lit("#5BBFB5"), "transparency": lit("0D")}}],
            "rotation": [{"properties": {"angle": lit("0D")}}]
        },
        "drillFilterOtherVisuals": True
    }
})

# ─── 3. BACK BUTTON ───
write_visual("back_btn_003", {
    "$schema": SCHEMA,
    "name": "back_btn_003",
    "position": {"x": 12, "y": 10, "z": 1000, "height": 34, "width": 34, "tabOrder": 1000},
    "visual": {
        "visualType": "actionButton",
        "objects": {
            "icon": [{"properties": {
                "shapeType": lit("'Back'"),
                "padding": lit("4D"),
                "lineColor": color_lit("#5BBFB5")
            }}],
            "outline": [{"properties": {
                "show": lit("true"),
                "weight": lit("1D"),
                "color": color_lit("#E2E8F0"),
                "roundEdge": lit("6D")
            }}],
            "fill": [{"properties": {"show": lit("true"), "fillColor": color_lit("#F0FAF8"), "transparency": lit("0D")}}]
        },
        "drillFilterOtherVisuals": True
    }
})

# ─── 4. PAGE TITLE ───
write_visual("page_title_004", {
    "$schema": SCHEMA,
    "name": "page_title_004",
    "position": {"x": 56, "y": 8, "z": 2000, "height": 40, "width": 280, "tabOrder": 2000},
    "visual": {
        "visualType": "textbox",
        "objects": {
            "general": [{"properties": {
                "paragraphs": [{
                    "textRuns": [{
                        "value": "Buyer Supplier Report",
                        "textStyle": {
                            "fontWeight": "bold",
                            "fontSize": "16pt",
                            "color": "#2D3436"
                        }
                    }]
                }]
            }}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {"show": lit("false")}}],
            "visualHeader": [{"properties": {"show": lit("false")}}]
        },
        "drillFilterOtherVisuals": True
    }
})

# ─── 5. CLIENT NAME CARD ───
write_visual("client_name_005", {
    "$schema": SCHEMA,
    "name": "client_name_005",
    "position": {"x": 300, "y": 12, "z": 2100, "height": 32, "width": 200, "tabOrder": 2100},
    "visual": {
        "visualType": "multiRowCard",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [{
                        "field": {
                            "Aggregation": {
                                "Expression": {"Column": {"Expression": {"SourceRef": {"Entity": "client"}}, "Property": "client_name"}},
                                "Function": 3
                            }
                        },
                        "queryRef": "Min(client.client_name)"
                    }]
                }
            }
        },
        "objects": {
            "categoryLabels": [{"properties": {"show": lit("false")}}],
            "card": [{"properties": {"barShow": lit("false")}}],
            "dataLabels": [{"properties": {
                "fontSize": lit("'11'"),
                "fontFamily": lit("'''Segoe UI'', wf_segoe-ui_normal, helvetica, arial, sans-serif'"),
                "color": color_lit("#636E72")
            }}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {"show": lit("false")}}],
            "visualHeader": [{"properties": {"show": lit("false")}}]
        },
        "drillFilterOtherVisuals": True
    }
})

# ─── 6. LOGO IMAGE ───
write_visual("logo_image_006", {
    "$schema": SCHEMA,
    "name": "logo_image_006",
    "position": {"x": 1110, "y": 10, "z": 3000, "height": 34, "width": 160, "tabOrder": 3000},
    "visual": {
        "visualType": "image",
        "objects": {
            "general": [{"properties": {
                "imageUrl": {"expr": {"ResourcePackageItem": {
                    "PackageName": "RegisteredResources",
                    "PackageType": 1,
                    "ItemName": "SMRX_Trulla_Logo__Yellow_and_B34113121120693735.png"
                }}}
            }}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {"show": lit("false")}}]
        },
        "drillFilterOtherVisuals": True
    }
})

# ─── 7. FILTER STRIP BACKGROUND ───
write_visual("filter_strip_bg_007", {
    "$schema": SCHEMA,
    "name": "filter_strip_bg_007",
    "position": {"x": 0, "y": 55, "z": 200, "height": 76, "width": 1280, "tabOrder": 200},
    "visual": {
        "visualType": "shape",
        "objects": {
            "line": [{"properties": {"show": lit("false")}}],
            "fill": [{"properties": {"fillColor": color_lit("#FFFFFF"), "transparency": lit("0D")}}],
            "rotation": [{"properties": {"angle": lit("0D")}}]
        },
        "drillFilterOtherVisuals": True
    }
})

# ─── 8. FILTER STRIP BOTTOM BORDER ───
write_visual("filter_strip_border_008", {
    "$schema": SCHEMA,
    "name": "filter_strip_border_008",
    "position": {"x": 0, "y": 130, "z": 300, "height": 1, "width": 1280, "tabOrder": 300},
    "visual": {
        "visualType": "shape",
        "objects": {
            "line": [{"properties": {"show": lit("false")}}],
            "fill": [{"properties": {"fillColor": color_lit("#E2E8F0"), "transparency": lit("0D")}}],
            "rotation": [{"properties": {"angle": lit("0D")}}]
        },
        "drillFilterOtherVisuals": True
    }
})

# ─── 9. SUPPLIER SLICER (restyled) ───
write_visual("supplier_slicer_009", {
    "$schema": SCHEMA,
    "name": "supplier_slicer_009",
    "position": {"x": 20, "y": 62, "z": 5000, "height": 60, "width": 160, "tabOrder": 5000},
    "visual": {
        "visualType": "slicer",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [{
                        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "supplier_min_in_med_text rs"}},
                        "queryRef": "order_edi_invoice.supplier_min_in_med_text rs",
                        "nativeQueryRef": "Supplier to Purchase From:",
                        "active": True,
                        "displayName": "Supplier"
                    }]
                }
            }
        },
        "objects": {
            "data": [{"properties": {"mode": lit("'Dropdown'")}}],
            "selection": [{"properties": {
                "singleSelect": lit("true"),
                "strictSingleSelect": lit("false"),
                "selectAllCheckboxEnabled": lit("false")
            }}],
            "general": [{"properties": {
                "filter": {
                    "filter": {
                        "Version": 2,
                        "From": [{"Name": "o", "Entity": "order_edi_invoice", "Type": 0}],
                        "Where": [{"Condition": {"In": {
                            "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "o"}}, "Property": "supplier_min_in_med_text rs"}}],
                            "Values": [[{"Literal": {"Value": "'MMCAP'"}}]]
                        }}}]
                    }
                }
            }}],
            "header": [{"properties": {
                "fontColor": color_lit("#5BBFB5"),
                "textSize": lit("9D")
            }}],
            "items": [{"properties": {
                "fontColor": color_lit("#2D3436"),
                "textSize": lit("11D"),
                "background": color_lit("#F7F8FA")
            }}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {"show": lit("false")}}],
            "visualHeader": [{"properties": {"show": lit("false")}}]
        },
        "drillFilterOtherVisuals": True
    }
})

# ─── 10. FACILITY SLICER (restyled) ───
write_visual("facility_slicer_010", {
    "$schema": SCHEMA,
    "name": "facility_slicer_010",
    "position": {"x": 190, "y": 62, "z": 5100, "height": 60, "width": 170, "tabOrder": 5100},
    "visual": {
        "visualType": "slicer",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [{
                        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "master_facility"}},
                        "queryRef": "order_edi_invoice.master_facility",
                        "nativeQueryRef": "Facility",
                        "active": True,
                        "displayName": "Facility"
                    }]
                }
            }
        },
        "objects": {
            "data": [{"properties": {"mode": lit("'Dropdown'")}}],
            "selection": [{"properties": {"selectAllCheckboxEnabled": lit("true")}}],
            "header": [{"properties": {
                "fontColor": color_lit("#5BBFB5"),
                "textSize": lit("9D")
            }}],
            "items": [{"properties": {
                "fontColor": color_lit("#2D3436"),
                "textSize": lit("11D"),
                "background": color_lit("#F7F8FA")
            }}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {"show": lit("false")}}],
            "visualHeader": [{"properties": {"show": lit("false")}}]
        },
        "drillFilterOtherVisuals": True
    }
})

# ─── 11. TIME FRAME SLICER (restyled) ───
write_visual("timeframe_slicer_011", {
    "$schema": SCHEMA,
    "name": "timeframe_slicer_011",
    "position": {"x": 370, "y": 62, "z": 5200, "height": 60, "width": 250, "tabOrder": 5200},
    "visual": {
        "visualType": "slicer",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [{
                        "field": {"Column": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "invoice_date"}},
                        "queryRef": "order_edi_invoice.invoice_date",
                        "nativeQueryRef": "Time Frame",
                        "active": True,
                        "displayName": "Time Frame"
                    }]
                }
            },
            "sortDefinition": {"sort": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "invoice_date"}}, "direction": "Ascending"}], "isDefaultSort": True}
        },
        "objects": {
            "data": [{"properties": {
                "mode": lit("'Relative'"),
                "relativeRange": lit("'Last'"),
                "relativeDuration": lit("12D"),
                "relativePeriod": lit("'Months'")
            }}],
            "general": [{"properties": {
                "orientation": lit("0D"),
                "filter": {
                    "filter": {
                        "Version": 2,
                        "From": [{"Name": "o", "Entity": "order_edi_invoice", "Type": 0}],
                        "Where": [{"Condition": {"Between": {
                            "Expression": {"Column": {"Expression": {"SourceRef": {"Source": "o"}}, "Property": "invoice_date"}},
                            "LowerBound": {"DateSpan": {"Expression": {"DateAdd": {"Expression": {"DateAdd": {"Expression": {"Now": {}}, "Amount": 1, "TimeUnit": 0}}, "Amount": -12, "TimeUnit": 2}}, "TimeUnit": 0}},
                            "UpperBound": {"DateSpan": {"Expression": {"Now": {}}, "TimeUnit": 0}}
                        }}}]
                    }
                }
            }}],
            "dateRange": [{"properties": {"includeToday": lit("true")}}],
            "header": [{"properties": {
                "fontColor": color_lit("#5BBFB5"),
                "textSize": lit("9D")
            }}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {"show": lit("false")}}],
            "visualHeader": [{"properties": {"show": lit("false")}}]
        },
        "drillFilterOtherVisuals": True
    }
})

# ─── 12. TEXT SEARCH (same custom visual) ───
# Read original
with open(os.path.join(REPORT_DIR, OLD_PAGE_ID, "visuals", "d92b86ae923efd6cc58c", "visual.json"), "r", encoding="utf-8") as f:
    search_vis = json.load(f)
search_vis["name"] = "text_search_012"
search_vis["position"] = {"x": 640, "y": 68, "z": 5300, "height": 50, "width": 220, "tabOrder": 5300}
write_visual("text_search_012", search_vis)

# ─── 13. KPI CARD — POTENTIAL SAVINGS ───
write_visual("kpi_savings_013", {
    "$schema": SCHEMA,
    "name": "kpi_savings_013",
    "position": {"x": 892, "y": 62, "z": 6000, "height": 60, "width": 175, "tabOrder": 6000},
    "visual": {
        "visualType": "multiRowCard",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [{
                        "field": {
                            "Aggregation": {
                                "Expression": {"Column": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "supplier_savings rs"}},
                                "Function": 0
                            }
                        },
                        "queryRef": "Sum(order_edi_invoice.supplier_savings rs)",
                        "nativeQueryRef": "Potential Savings",
                        "displayName": "Potential Savings"
                    }]
                }
            }
        },
        "objects": {
            "categoryLabels": [{"properties": {
                "fontSize": lit("'9'"),
                "color": color_lit("#636E72")
            }}],
            "dataLabels": [{"properties": {
                "fontSize": lit("'20'"),
                "color": color_lit("#3EA89D")
            }}],
            "card": [{"properties": {
                "barShow": lit("true"),
                "barColor": color_lit("#5BBFB5"),
                "barWeight": lit("3D")
            }}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {"show": lit("true"), "color": color_lit("#FFFFFF"), "transparency": lit("0D")}}],
            "border": [{"properties": {"show": lit("true"), "color": color_lit("#E2E8F0"), "radius": lit("8D")}}],
            "visualHeader": [{"properties": {"show": lit("false")}}]
        },
        "drillFilterOtherVisuals": True
    },
    "filterConfig": {
        "filters": [{
            "name": "kpi_filter_savings",
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "cost_plus_pack_price"}},
            "type": "Categorical",
            "howCreated": "User",
            "objects": {"general": [{"properties": {"isInvertedSelectionMode": lit("true")}}]}
        }]
    }
})

# ─── 14. KPI CARD — # OF MEDS ───
write_visual("kpi_meds_014", {
    "$schema": SCHEMA,
    "name": "kpi_meds_014",
    "position": {"x": 1080, "y": 62, "z": 6100, "height": 60, "width": 175, "tabOrder": 6100},
    "visual": {
        "visualType": "multiRowCard",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [{
                        "field": {
                            "Aggregation": {
                                "Expression": {"Column": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "medication_id"}},
                                "Function": 2
                            }
                        },
                        "queryRef": "order_edi_invoice.medication_id",
                        "nativeQueryRef": "Count of medication_id",
                        "displayName": "# of Meds"
                    }]
                }
            },
            "sortDefinition": {"sort": [{"field": {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "medication_id"}}, "Function": 2}}, "direction": "Descending"}], "isDefaultSort": True}
        },
        "objects": {
            "categoryLabels": [{"properties": {
                "fontSize": lit("'9'"),
                "color": color_lit("#636E72")
            }}],
            "dataLabels": [{"properties": {
                "fontSize": lit("'20'"),
                "color": color_lit("#2D3436")
            }}],
            "card": [{"properties": {
                "barShow": lit("true"),
                "barColor": color_lit("#D4C94A"),
                "barWeight": lit("3D")
            }}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {"show": lit("true"), "color": color_lit("#FFFFFF"), "transparency": lit("0D")}}],
            "border": [{"properties": {"show": lit("true"), "color": color_lit("#E2E8F0"), "radius": lit("8D")}}],
            "visualHeader": [{"properties": {"show": lit("false")}}]
        },
        "drillFilterOtherVisuals": True
    },
    "filterConfig": {
        "filters": [{
            "name": "kpi_filter_meds",
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "cost_plus_pack_price"}},
            "type": "Categorical",
            "howCreated": "User",
            "objects": {"general": [{"properties": {"isInvertedSelectionMode": lit("true")}}]}
        }]
    }
})

# ─── 15. TABLE CONTAINER BACKGROUND ───
write_visual("table_card_bg_015", {
    "$schema": SCHEMA,
    "name": "table_card_bg_015",
    "position": {"x": 14, "y": 140, "z": 400, "height": 566, "width": 1252, "tabOrder": 400},
    "visual": {
        "visualType": "shape",
        "objects": {
            "line": [{"properties": {"show": lit("true"), "lineColor": color_lit("#E2E8F0"), "weight": lit("1D"), "roundEdge": lit("8D")}}],
            "fill": [{"properties": {"fillColor": color_lit("#FFFFFF"), "transparency": lit("0D")}}],
            "rotation": [{"properties": {"angle": lit("0D")}}]
        },
        "drillFilterOtherVisuals": True
    }
})

# ─── 16. MAIN TABLE (restyled) ───
write_visual("main_table_016", {
    "$schema": SCHEMA,
    "name": "main_table_016",
    "position": {"x": 20, "y": 150, "z": 7000, "height": 548, "width": 1240, "tabOrder": 7000},
    "visual": {
        "visualType": "tableEx",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [
                        {
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "medication_description"}},
                            "queryRef": "order_edi_invoice.medication_description",
                            "nativeQueryRef": "Description",
                            "displayName": "Description"
                        },
                        {
                            "field": {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "total_eaches"}}, "Function": 0}},
                            "queryRef": "Sum(order_edi_invoice.total_eaches)",
                            "nativeQueryRef": "Total Eaches",
                            "displayName": "Total Eaches"
                        },
                        {
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "supplier_min_in_med_text rs"}},
                            "queryRef": "order_edi_invoice.supplier_min_in_med_text rs",
                            "nativeQueryRef": "Best Price Supplier",
                            "displayName": "Best Price Supplier"
                        },
                        {
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "Selected Supplier Each Price rs"}},
                            "queryRef": "order_edi_invoice.Selected Supplier Each Price rs",
                            "nativeQueryRef": "Supplier Each Price",
                            "displayName": "Supplier Each Price"
                        },
                        {
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "Selected Supplier NDC rs"}},
                            "queryRef": "order_edi_invoice.Selected Supplier NDC rs",
                            "nativeQueryRef": "Supplier NDC",
                            "displayName": "Supplier NDC"
                        }
                    ]
                }
            }
        },
        "objects": {
            "columnWidth": [
                {"properties": {"value": lit("430D")}, "selector": {"metadata": "order_edi_invoice.medication_description"}},
                {"properties": {"value": lit("165D")}, "selector": {"metadata": "Sum(order_edi_invoice.total_eaches)"}},
                {"properties": {"value": lit("160D")}, "selector": {"metadata": "order_edi_invoice.supplier_min_in_med_text rs"}},
                {"properties": {"value": lit("195D")}, "selector": {"metadata": "order_edi_invoice.Selected Supplier Each Price rs"}},
                {"properties": {"value": lit("195D")}, "selector": {"metadata": "order_edi_invoice.Selected Supplier NDC rs"}}
            ],
            "values": [{"properties": {
                "wordWrap": lit("false"),
                "fontColor": color_lit("#2D3436"),
                "fontSize": lit("9D"),
                "fontFamily": lit("'''Segoe UI'', wf_segoe-ui_normal, helvetica, arial, sans-serif'")
            }}],
            "columnHeaders": [{"properties": {
                "bold": lit("true"),
                "alignment": lit("'Center'"),
                "fontColor": color_lit("#FFFFFF"),
                "backColor": color_lit("#2D3436"),
                "fontSize": lit("9D"),
                "fontFamily": lit("'''Segoe UI Semibold'', wf_segoe-ui_semibold, helvetica, arial, sans-serif'")
            }}],
            "columnFormatting": [
                {
                    "properties": {
                        "alignment": lit("'Center'"),
                        "styleHeader": lit("false"),
                        "styleTotal": lit("false")
                    },
                    "selector": {"metadata": "Sum(order_edi_invoice.total_eaches)"}
                },
                {
                    "properties": {
                        "alignment": lit("'Center'"),
                        "styleHeader": lit("false"),
                        "styleTotal": lit("false")
                    },
                    "selector": {"metadata": "order_edi_invoice.Selected Supplier Each Price rs"}
                },
                {
                    "properties": {
                        "alignment": lit("'Center'"),
                        "styleHeader": lit("true")
                    },
                    "selector": {"metadata": "order_edi_invoice.Selected Supplier NDC rs"}
                },
                {
                    "properties": {
                        "alignment": lit("'Center'"),
                        "styleTotal": lit("false")
                    },
                    "selector": {"metadata": "order_edi_invoice.supplier_min_in_med_text rs"}
                }
            ],
            "grid": [{"properties": {
                "gridHorizontal": lit("true"),
                "gridHorizontalColor": color_lit("#F0F3F6"),
                "gridHorizontalWeight": lit("1D"),
                "rowPadding": lit("3D")
            }}],
            "total": [{"properties": {"show": lit("false")}}]
        },
        "visualContainerObjects": {
            "background": [{"properties": {"show": lit("false")}}],
            "border": [{"properties": {"show": lit("false")}}],
            "title": [{"properties": {
                "show": lit("true"),
                "text": lit("'Medication Price Comparison'"),
                "fontColor": color_lit("#2D3436"),
                "fontSize": lit("12D"),
                "fontFamily": lit("'''Segoe UI Semibold'', wf_segoe-ui_semibold, helvetica, arial, sans-serif'")
            }}],
            "stylePreset": [{"properties": {"name": lit("'AlternatingRowsNew'")}}]
        },
        "drillFilterOtherVisuals": True
    },
    "filterConfig": {
        "filters": [
            {"name": "f_desc", "field": {"Column": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "medication_description"}}, "type": "Categorical"},
            {"name": "f_eaches", "field": {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "total_eaches"}}, "Function": 0}}, "type": "Advanced"},
            {"name": "f_supplier", "field": {"Column": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "supplier_min_in_med_text rs"}}, "type": "Categorical"},
            {"name": "f_price", "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "Selected Supplier Each Price rs"}}, "type": "Advanced"},
            {"name": "f_ndc", "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "order_edi_invoice"}}, "Property": "Selected Supplier NDC rs"}}, "type": "Advanced"}
        ]
    }
})

# ─── 17. BOTTOM ACCENT GRADIENT LINE ───
write_visual("bottom_accent_017", {
    "$schema": SCHEMA,
    "name": "bottom_accent_017",
    "position": {"x": 0, "y": 717, "z": 9999, "height": 3, "width": 1280, "tabOrder": 9999},
    "visual": {
        "visualType": "shape",
        "objects": {
            "line": [{"properties": {"show": lit("false")}}],
            "fill": [{"properties": {"fillColor": color_lit("#5BBFB5"), "transparency": lit("0D")}}],
            "rotation": [{"properties": {"angle": lit("0D")}}]
        },
        "drillFilterOtherVisuals": True
    }
})

# ─── UPDATE pages.json ───
pages_path = os.path.join(REPORT_DIR, "pages.json")
with open(pages_path, "r", encoding="utf-8") as f:
    pages = json.load(f)

# Insert right after the original page
old_idx = pages["pageOrder"].index(OLD_PAGE_ID)
if NEW_PAGE_ID not in pages["pageOrder"]:
    pages["pageOrder"].insert(old_idx + 1, NEW_PAGE_ID)

with open(pages_path, "w", encoding="utf-8") as f:
    json.dump(pages, f, indent=2, ensure_ascii=False)

print(f"\nDone! Created {NEW_PAGE_ID} with 17 visuals.")
print("Open the .pbip in PBI Desktop to see the redesigned page.")
