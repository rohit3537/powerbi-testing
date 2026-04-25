"""
Update all Retail Item Rank / FeatureCode / SeasonCode slicers
to source from 'Item Info' instead of 'Sales_Inv'.

This ensures the slicers work across all pages since Item Info
is a shared dimension related to both Sales_Inv and DC Inventory.
"""

import json
import os
import glob

REPORT_DIR = (
    r"D:\Agentic Development v2\projects\powerbi-testing\workbooks"
    r"\Sales Performance Dashboard - Ulta-LV"
    r"\Sales Performance Dashboard - Ulta-LV.Report\definition\pages"
)

FIELDS = {"Retail Item Rank", "FeatureCode", "SeasonCode"}


def update_slicer(filepath: str) -> bool:
    """Update a slicer visual.json to use Item Info instead of Sales_Inv."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    visual = data.get("visual", {})
    if visual.get("visualType") != "slicer":
        return False

    # Check if this slicer uses one of our 3 fields
    try:
        proj = visual["query"]["queryState"]["Values"]["projections"][0]
        prop = proj["field"]["Column"]["Property"]
        if prop not in FIELDS:
            return False
    except (KeyError, IndexError):
        return False

    # Update Entity from Sales_Inv to Item Info
    proj["field"]["Column"]["Expression"]["SourceRef"]["Entity"] = "Item Info"

    # Update queryRef and nativeQueryRef
    proj["queryRef"] = f"Item Info.{prop}"
    # nativeQueryRef stays the same (just the field name)

    # Update expansionStates queryRefs
    for es in visual.get("expansionStates", []):
        for level in es.get("levels", []):
            level["queryRefs"] = [f"Item Info.{prop}"]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return True


def main():
    updated = 0
    for filepath in glob.glob(os.path.join(REPORT_DIR, "*/visuals/*/visual.json")):
        if update_slicer(filepath):
            # Extract page and visual folder names
            parts = filepath.replace("\\", "/").split("/")
            page_idx = parts.index("pages") + 1
            vis_idx = parts.index("visuals") + 1
            page_id = parts[page_idx]
            vis_id = parts[vis_idx]

            # Get page name
            page_json = os.path.join(REPORT_DIR, page_id, "page.json")
            with open(page_json, "r", encoding="utf-8") as f:
                page_data = json.load(f)
            page_name = page_data.get("displayName", page_id)

            # Get field name
            with open(filepath, "r", encoding="utf-8") as f:
                d = json.load(f)
            prop = d["visual"]["query"]["queryState"]["Values"]["projections"][0]["field"]["Column"]["Property"]

            print(f"  {page_name}: {prop} -> Item Info")
            updated += 1

    print(f"\nDone. Updated {updated} slicer(s) to source from 'Item Info'.")


if __name__ == "__main__":
    main()
