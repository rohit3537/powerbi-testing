"""
Update all Retail Item Rank / FeatureCode / SeasonCode slicers
to source from the new dedicated lookup tables.
"""

import json
import os
import glob

REPORT_DIR = (
    r"D:\Agentic Development v2\projects\powerbi-testing\workbooks"
    r"\Sales Performance Dashboard - Ulta-LV"
    r"\Sales Performance Dashboard - Ulta-LV.Report\definition\pages"
)

# Map field name -> lookup table entity name and queryRef prefix
FIELD_MAP = {
    "Retail Item Rank": {
        "entity": "_Retail Item Rank",
        "queryRef": "_Retail Item Rank.Retail Item Rank",
    },
    "FeatureCode": {
        "entity": "_FeatureCode",
        "queryRef": "_FeatureCode.FeatureCode",
    },
    "SeasonCode": {
        "entity": "_SeasonCode",
        "queryRef": "_SeasonCode.SeasonCode",
    },
}


def update_slicer(filepath: str) -> str | None:
    """Update a slicer visual.json to use the lookup table."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    visual = data.get("visual", {})
    if visual.get("visualType") != "slicer":
        return None

    try:
        proj = visual["query"]["queryState"]["Values"]["projections"][0]
        prop = proj["field"]["Column"]["Property"]
        if prop not in FIELD_MAP:
            return None
    except (KeyError, IndexError):
        return None

    mapping = FIELD_MAP[prop]

    # Update Entity
    proj["field"]["Column"]["Expression"]["SourceRef"]["Entity"] = mapping["entity"]
    # Update queryRef
    proj["queryRef"] = mapping["queryRef"]
    # nativeQueryRef stays as the field name

    # Update expansionStates queryRefs
    for es in visual.get("expansionStates", []):
        for level in es.get("levels", []):
            level["queryRefs"] = [mapping["queryRef"]]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return prop


def main():
    updated = 0
    for filepath in glob.glob(os.path.join(REPORT_DIR, "*/visuals/*/visual.json")):
        prop = update_slicer(filepath)
        if prop:
            parts = filepath.replace("\\", "/").split("/")
            page_idx = parts.index("pages") + 1
            page_id = parts[page_idx]
            page_json = os.path.join(REPORT_DIR, page_id, "page.json")
            with open(page_json, "r", encoding="utf-8") as f:
                page_name = json.load(f).get("displayName", page_id)
            target = FIELD_MAP[prop]["entity"]
            print(f"  {page_name}: {prop} -> {target}")
            updated += 1

    print(f"\nDone. Updated {updated} slicer(s).")


if __name__ == "__main__":
    main()
