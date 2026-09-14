"""Insert the "Used by" marquee on Home after the Hero: section, data sources, two Collections.

python3 scripts/used_by.py [--dry-run]

Run once. Afterwards add sites in the Builder: upload `used-by-<site>.png|svg` in Assets and add an
entry to the `usedBy` variable on the Used By section (see onepager.USED_BY).
"""

import json
import subprocess
import sys

import ws
from onepager import USED_BY, USED_BY_LOGOS, used_by, used_by_item

DRY = "--dry-run" in sys.argv
HOME_MAIN = "kWIS2d3ZZzxqi6Fn7UxwA"  # <main> Onepager


def api_call(command, payload):
    """Assets resource commands are API commands: --input <file> --json instead of --input-file."""
    path = ws.TEMP / f"call-{command}.json"
    path.write_text(json.dumps(payload))
    result = subprocess.run(["npx", "--yes", "webstudio@latest", command, "--input", str(path), "--json"], cwd=ws.ROOT, capture_output=True, text=True)
    data = json.loads(result.stdout)
    if not data.get("ok"):
        raise RuntimeError(f"{command} failed: {json.dumps(data.get('error'))[:2000]}")
    return data["data"]


def insert_collections():
    lists = {i["label"]: i["id"] for i in ws.instances("/") if i.get("label", "").startswith("Used By List")}
    for label, copy in (("Used By List", False), ("Used By List (loop copy)", True)):
        ws.call("insert-collection", {
            "parentInstanceId": lists[label],
            "conflictResolution": "ours",
            "data": {"type": "expression", "value": "usedByLogos.data"},
            "itemFragment": used_by_item(copy),
        })
    return lists


if __name__ == "__main__":
    if any(i.get("label") == "Used By" and i.get("parentId") == HOME_MAIN for i in ws.instances("/", max_depth=2)):
        sys.exit("Used By section already exists on Home")

    section = ws.call("insert-fragment", {
        "parentInstanceId": HOME_MAIN,
        "insertIndex": 1,
        "conflictResolution": "ours",
        "fragment": used_by(),
    }, dry_run=DRY)
    if DRY:
        print("fragment ok (dry run)")
        sys.exit()
    section_id = section["rootInstanceIds"][0]

    ws.call("create-variable", {"scopeInstanceId": section_id, "name": "usedBy", "value": {"type": "json", "value": USED_BY}})
    api_call("create-assets-resource", {**USED_BY_LOGOS, "scopeInstanceId": section_id})
    print("section", section_id, "lists", insert_collections())
