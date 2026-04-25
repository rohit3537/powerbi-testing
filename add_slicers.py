"""
Add Retail Item Rank, FeatureCode, and SeasonCode slicers to
report pages that use Sales_Inv visuals but are missing these slicers.

Operates on the .pbip report layout JSON files directly.
"""

import json
import os
import uuid

REPORT_DIR = (
    r"D:\Agentic Development v2\projects\powerbi-testing\workbooks"
    r"\Sales Performance Dashboard - Ulta-LV"
    r"\Sales Performance Dashboard - Ulta-LV.Report\definition\pages"
)

# Slicer templates (copied from Overview page, positions will be adjusted)
SLICER_TEMPLATES = {
    "Retail Item Rank": {
        "Property": "Retail Item Rank",
        "queryRef": "Sales_Inv.Retail Item Rank",
        "nativeQueryRef": "Retail Item Rank",
        "headerText": "'Retail Item Rank'",
        "hasInvertedSelection": True,
    },
    "FeatureCode": {
        "Property": "FeatureCode",
        "queryRef": "Sales_Inv.FeatureCode",
        "nativeQueryRef": "FeatureCode",
        "headerText": "'Feature Code'",
        "hasInvertedSelection": False,
    },
    "SeasonCode": {
        "Property": "SeasonCode",
        "queryRef": "Sales_Inv.SeasonCode",
        "nativeQueryRef": "SeasonCode",
        "headerText": "'Season Code'",
        "hasInvertedSelection": False,
    },
}

# Pages to add slicers to, and which slicers they already have
PAGES = {
    "425d1dff65b75f4cbb1e": {"name": "NETWORK INVENTORY", "has": []},
    "15c72efda0334bbd2783": {"name": "DC INVENTORY", "has": []},
    "e2fcbe233b5e613dc0bf": {"name": "STORE INVENTORY", "has": []},
    "b2f8fb88e16e723560e6": {"name": "Rank Code Retail", "has": ["Retail Item Rank"]},
    "6fde49397dc0dc46007b": {"name": "Page 1", "has": ["Retail Item Rank"]},
    "3e0a27e5c7c4423beee3": {"name": "Source Link", "has": []},
}

# Position: same x/y as Overview, stacked vertically
POSITIONS = {
    "Retail Item Rank": {"x": 11.25, "y": 715, "width": 220, "height": 80},
    "FeatureCode": {"x": 11.25, "y": 802.5, "width": 220, "height": 80},
    "SeasonCode": {"x": 13.75, "y": 890, "width": 213.75, "height": 80},
}


def make_slicer_visual(slicer_key: str, z_base: int, tab_base: int) -> dict:
    """Build a complete slicer visual JSON from template."""
    tmpl = SLICER_TEMPLATES[slicer_key]
    pos = POSITIONS[slicer_key]
    vis_id = uuid.uuid4().hex[:20]

    data_properties = {
        "mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}},
    }
    if tmpl["hasInvertedSelection"]:
        data_properties["isInvertedSelectionMode"] = {
            "expr": {"Literal": {"Value": "true"}}
        }

    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
        "name": vis_id,
        "position": {
            "x": pos["x"],
            "y": pos["y"],
            "z": z_base,
            "height": pos["height"],
            "width": pos["width"],
            "tabOrder": tab_base,
        },
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {
                                            "SourceRef": {"Entity": "Sales_Inv"}
                                        },
                                        "Property": tmpl["Property"],
                                    }
                                },
                                "queryRef": tmpl["queryRef"],
                                "nativeQueryRef": tmpl["nativeQueryRef"],
                                "active": True,
                            }
                        ]
                    }
                }
            },
            "expansionStates": [
                {
                    "roles": ["Values"],
                    "levels": [
                        {
                            "queryRefs": [tmpl["queryRef"]],
                            "isCollapsed": True,
                            "isPinned": True,
                        }
                    ],
                    "root": {},
                }
            ],
            "objects": {
                "data": [{"properties": data_properties}],
                "selection": [
                    {
                        "properties": {
                            "singleSelect": {
                                "expr": {"Literal": {"Value": "false"}}
                            },
                            "selectAllCheckboxEnabled": {
                                "expr": {"Literal": {"Value": "true"}}
                            },
                        }
                    }
                ],
                "general": [
                    {
                        "properties": {
                            "selfFilterEnabled": {
                                "expr": {"Literal": {"Value": "true"}}
                            }
                        }
                    }
                ],
                "header": [
                    {
                        "properties": {
                            "text": {
                                "expr": {
                                    "Literal": {"Value": tmpl["headerText"]}
                                }
                            },
                            "fontColor": {
                                "solid": {
                                    "color": {
                                        "expr": {
                                            "ThemeDataColor": {
                                                "ColorId": 0,
                                                "Percent": 0,
                                            }
                                        }
                                    }
                                }
                            },
                        }
                    }
                ],
                "items": [
                    {
                        "properties": {
                            "background": {
                                "solid": {
                                    "color": {
                                        "expr": {
                                            "Literal": {"Value": "'#ffffff'"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                ],
            },
            "visualContainerObjects": {
                "background": [
                    {
                        "properties": {
                            "show": {
                                "expr": {"Literal": {"Value": "false"}}
                            }
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": True,
        },
    }


def add_slicers_to_page(page_id: str, page_info: dict):
    """Add missing slicers to a page."""
    page_dir = os.path.join(REPORT_DIR, page_id, "visuals")
    added = []

    z_base = 60002
    tab_base = 59002

    for slicer_key in ["Retail Item Rank", "FeatureCode", "SeasonCode"]:
        if slicer_key in page_info["has"]:
            z_base += 1
            tab_base += 1
            continue

        visual = make_slicer_visual(slicer_key, z_base, tab_base)
        vis_dir = os.path.join(page_dir, visual["name"])
        os.makedirs(vis_dir, exist_ok=True)

        vis_path = os.path.join(vis_dir, "visual.json")
        with open(vis_path, "w", encoding="utf-8") as f:
            json.dump(visual, f, indent=2, ensure_ascii=False)

        added.append(slicer_key)
        z_base += 1
        tab_base += 1

    return added


def main():
    total = 0
    for page_id, page_info in PAGES.items():
        added = add_slicers_to_page(page_id, page_info)
        if added:
            print(f"  {page_info['name']}: added {', '.join(added)}")
            total += len(added)
        else:
            print(f"  {page_info['name']}: all slicers already present")

    print(f"\nDone. Added {total} slicer(s) across {len(PAGES)} pages.")
    print("Reload the .pbip in Power BI Desktop to see the changes.")


if __name__ == "__main__":
    main()
