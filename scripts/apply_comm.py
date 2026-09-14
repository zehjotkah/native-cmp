import json, re, subprocess, time
import ws, comm
from ui import T
from rich import txt

def retry(tool, payload):
    for attempt in range(5):
        try:
            return ws.call(tool, payload)
        except RuntimeError as e:
            if "MCP_TOOL_FAILED" not in str(e) or attempt == 4: raise
            time.sleep(4)

def delete(iid):
    for attempt in range(4):
        args = ["npx", "--yes", "webstudio@latest", "delete-instance", json.dumps({"instanceIds": [iid]})]
        out = subprocess.run(args, capture_output=True, text=True, cwd="..").stdout
        token = re.search(r'"token":\s*"([^"]+)"', out)
        if not token:
            if "not found" in out.lower() or "NOT_FOUND" in out: return "gone"
            time.sleep(4); continue
        args[-1] = json.dumps({"instanceIds": [iid], "confirmDestructive": True, "confirmationToken": token.group(1)})
        if '"ok": true' in subprocess.run(args, capture_output=True, text=True, cwd="..").stdout: return True
        time.sleep(4)
    return False

def sync():
    subprocess.run(["npx", "webstudio@latest", "sync"], capture_output=True, cwd="..")
    d = json.load(open("../.webstudio/data.json"))["build"]
    vals = lambda x: [i[1] if isinstance(i, list) else i for i in (x if isinstance(x, list) else x.values())]
    inst = {i["id"]: i for i in vals(d["instances"])}
    return d, inst, vals

def text(inst, iid):
    return "".join(c["value"] if c["type"] == "text" else (text(inst, c["value"]) if c["type"] == "id" else "") for c in inst[iid]["children"])

def insert_once(parent, index, fragment, marker):
    """Insert unless a child of parent already contains marker text (inserts are not repeatable)."""
    for attempt in range(6):
        d, inst, vals = sync()
        if any(marker in text(inst, c["value"]) for c in inst[parent]["children"] if c["type"] == "id"):
            return "present"
        try:
            payload = {"parentInstanceId": parent, "conflictResolution": "ours", "fragment": fragment}
            payload.update({"mode": "append"} if index is None else {"insertIndex": index})
            ws.call("insert-fragment", payload)
            return "inserted"
        except RuntimeError as e:
            if "MCP_TOOL_FAILED" not in str(e) and "outside parent" not in str(e): raise
            time.sleep(10)
    raise RuntimeError("insert failed " + marker)

step = __import__("sys").argv[1]
d, inst, vals = sync()
if step == "hero":
    retry("update-text", {"instanceId": "h5p00AXOkqGqo0RVvK4bI", "childIndex": 0, "text": comm.HERO_LEAD})
    parent = "EOugXO30M0X39XAkfJzTS"
    if "_QG2vVvCGPiA68XzmKWx5" in inst:
        idx = [c["value"] for c in inst[parent]["children"]].index("_QG2vVvCGPiA68XzmKWx5")
        print("old actions deleted", delete("_QG2vVvCGPiA68XzmKWx5"))
    else:
        idx = 3
    print(insert_once(parent, idx, comm.hero_actions(), "Install with AI"))
elif step == "install":
    retry("update-text", {"instanceId": "OdPtGg8s-EpiwllUntnsl", "childIndex": 0, "text": comm.INSTALL_HEADING})
    retry("update-text", {"instanceId": "jAopHSNW_P6kLkAjQGcZT", "childIndex": 0, "text": comm.INSTALL_LEAD})
    for iid in ["oIbYxOsmc_ADkl5KfsE5D", "AHxvd6ge50fmFcbc7lVdf", "Jo2ncYl-Ae7CD373SFPVt"]:
        if iid in inst: print("deleted", iid, delete(iid))
    print(insert_once("iAheASm5B4T83jbMw7vBp", 1, comm.install_ways(), "AI agent via Webstudio MCP"))
elif step == "faq":
    faq_section = "DW_aoEv9BvYTQVQGmA0AY"
    container = [c["value"] for c in inst[faq_section]["children"] if c["type"] == "id"][0]
    lists = [c["value"] for c in inst[container]["children"] if c["type"] == "id" and any(inst[g["value"]].get("tag") == "details" for g in inst[c["value"]]["children"] if g["type"] == "id")]
    q, a = comm.FAQ_ITEM
    frag = f"<details {T('site-faq')}><summary {T('site-faq-question')}>{txt(q)}</summary><p {T('site-text')}>{txt(a)}</p></details>"
    print(insert_once(lists[0], 0, frag, q))
elif step == "docs":
    items = ws.instances("/docs")
    callout = [i for i in items if i.get("label") == "Agent Install"]
    if callout:
        c = callout[0]
        print("docs callout deleted", delete(c["id"]))
        print(insert_once(c["parentId"], c["indexWithinParent"], comm.docs_blocks(), "Install with an AI agent (recommended)"))
    else:
        print("no callout; checking blocks")
elif step == "intros":
    for path in ["/generator", "/examples"]:
        items = ws.instances(path, 4)
        intro = [i for i in items if i.get("label") == "Page Intro"]
        if not intro:
            print(path, "no Page Intro"); continue
        byparent = lambda pid: sorted([i for i in items if i.get("parentId") == pid], key=lambda i: i["indexWithinParent"])
        container = byparent(intro[0]["id"])[0]
        stack = byparent(container["id"])[0]
        print(path, insert_once(stack["id"], None, comm.agent_callout(), "Install with AI"))
