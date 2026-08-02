"""Project the memory graph down to what the orchestrator consumes.

    graph.json  --project.py-->  field_map.json + guards.json  -->  apply_orchestrator.py

The orchestrator's contract does not change: it still reads field_map.json. The only
difference is that the file is now generated, so hand-edits are lost on the next run
(hence the _generated_from banner).

Usage:
    python kb/project.py                       # default tenant
    python kb/project.py tenant:gartner.wd5/EXT
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from kb import Graph  # noqa: E402

ROOT = Path(__file__).parent.parent
DEFAULT_TENANT = "tenant:gartner.wd5/EXT"


def project(tenant_id=DEFAULT_TENANT, root=ROOT):
    g = Graph()
    tenant = g.one(tenant_id)
    if tenant is None:
        sys.exit(f"unknown tenant: {tenant_id}")

    ats = next((e["from"] for e in g.edges
                if e["rel"] == "has_tenant" and e["to"] == tenant_id), None)

    steps = sorted(g.neighbors(tenant_id, rel="has_step"),
                   key=lambda n: n["attrs"]["index"])
    terminal = next((s for s in steps if s["attrs"].get("is_terminal_submit")), None)

    fields = {}
    for step in steps:
        for f in g.neighbors(step["id"], rel="has_field"):
            sel = next(iter(g.neighbors(f["id"], rel="located_by")), None)
            if sel is None:
                continue
            a = sel["attrs"]
            entry = {
                "step": step["attrs"]["index"],
                "label": f["label"],
                "type": a["interaction"],
                "selector": _selector_for(a),
                "automation_id": a["automation_id"],
            }
            if a.get("value_used") is not None:
                entry["value"] = a["value_used"]
            if a.get("recipe"):
                entry["recipe"] = a["recipe"]

            options = [o["label"] for o in g.neighbors(f["id"], rel="accepts_option")]
            if options:
                entry["options"] = sorted(options)

            profile = next(iter(g.neighbors(f["id"], rel="maps_to")), None)
            if profile:
                entry["source"] = profile["label"]

            for c in g.query(type="constraint"):
                if c["attrs"].get("applies_to") in (f["id"], _kind(a["interaction"])):
                    entry.setdefault("constraints", []).append(c["id"])

            fields[f["attrs"]["canonical"]] = entry

    # Screening questions become q.* entries, which is the shape the orchestrator
    # already greps for when it builds its answer list.
    for ans in g.query(type="answer"):
        aid = _question_automation_id(g, ans, tenant_id)
        if not aid:
            continue
        key = "q." + _slug(ans["label"])
        fields[key] = {
            "step": 3,
            "label": ans["label"],
            "type": "prompt_dropdown",
            "aid": aid,
            "value": ans["attrs"]["value"],
            "confidence": ans["confidence"],
            "decided_by": ans["attrs"]["decided_by"],
            "reasoning": ans["attrs"]["reasoning"],
        }

    field_map = {
        "_generated_from": "kb/graph.json — do not hand-edit; run `python kb/project.py`",
        "_tenant": tenant_id,
        "_ats": ats,
        "flow": {
            "steps": [s["label"] for s in steps],
            "auth": tenant["attrs"].get("auth"),
            "entry_choices": tenant["attrs"].get("entry_choices"),
            "SUBMIT_WARNING": (
                f"There is NO separate Submit button. pageFooterNextButton on step "
                f"{terminal['attrs']['index']} ({terminal['label']}) SUBMITS the application."
                if terminal else "terminal step unknown — treat every continue as destructive"
            ),
            "terminal_submit_step": terminal["attrs"]["index"] if terminal else None,
        },
        "fields": fields,
        "not_present_in_this_ats": sorted(
            p["label"] for p in g.neighbors(tenant_id, rel="not_asked")
        ),
    }

    guards = {
        "_generated_from": "kb/graph.json",
        "guards": {
            gd["id"].split(":", 1)[1]: {"label": gd["label"],
                                        "rule": gd["attrs"]["description"]}
            for gd in g.query(type="guard")
        },
        "constraints": {c["id"]: c["attrs"] | {"label": c["label"]}
                        for c in g.query(type="constraint")},
        "terminal_submit_step": terminal["attrs"]["index"] if terminal else None,
        "ambiguous_profile_keys": [
            p["label"] for p in g.query(type="profile_field")
            if p["attrs"].get("ambiguous")
        ],
        "upload_hosts": [
            {"host": h["label"], "status": h["attrs"]["status"],
             "recipe": h["attrs"]["fetch_recipe"]}
            for h in sorted(g.query(type="host"),
                            key=lambda h: (h["attrs"]["status"] != "ok", h["label"]))
        ],
        "option_aliases": {
            e["from"].split(":", 1)[1]: e["to"].split(":", 1)[1]
            for e in g.edges
            if e["rel"] == "maps_to" and e["from"].startswith("option:")
        },
    }

    (root / "field_map.json").write_text(
        json.dumps(field_map, indent=1, ensure_ascii=False), encoding="utf-8")
    (root / "guards.json").write_text(
        json.dumps(guards, indent=1, ensure_ascii=False), encoding="utf-8")
    return field_map, guards


def _selector_for(attrs):
    aid, interaction = attrs["automation_id"], attrs["interaction"]
    if interaction in ("checkbox",) and not aid.startswith("formField-"):
        return f"input[data-automation-id='{aid}']"
    if interaction == "file":
        return f"input[data-automation-id='{aid}']"
    if interaction in ("text_bare", "password_bare"):
        return f"input[data-automation-id='{aid}']"
    if interaction in ("button_bare", "button_indexed"):
        return f"button[data-automation-id='{aid}']"
    tail = {
        "text": " input", "text_indexed": " input", "textarea_indexed": " textarea",
        "radio": " input[type=radio]", "checkbox": " input[type=checkbox]",
        "attestation_checkbox": " input[type=checkbox]",
        "prompt_dropdown": " button", "searchable_prompt": "", "multiselect": "",
        "date_mm_yyyy": "",
    }.get(interaction, "")
    return f"[data-automation-id='{aid}']{tail}"


def _kind(interaction):
    return "free_text" if interaction in ("textarea_indexed", "text_indexed") else interaction


def _question_automation_id(g, answer_node, tenant_id):
    """Screening question automation-ids are per-requisition GUIDs, so they live on the
    edge between the answer and the tenant rather than on the answer itself."""
    for e in g.edges:
        if e["from"] == answer_node["id"] and e["to"] == tenant_id and e["attrs"].get("aid"):
            return e["attrs"]["aid"]
    return answer_node["attrs"].get("aid")


def _slug(text):
    words = "".join(c if c.isalnum() or c.isspace() else " " for c in text).split()
    return "_".join(w.lower() for w in words[:6])


if __name__ == "__main__":
    tenant = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TENANT
    fm, gd = project(tenant)
    print(f"field_map.json: {len(fm['fields'])} fields, "
          f"terminal submit step = {fm['flow']['terminal_submit_step']}")
    print(f"guards.json:    {len(gd['guards'])} guards, "
          f"{len(gd['constraints'])} constraints, "
          f"{len(gd['upload_hosts'])} hosts, "
          f"{len(gd['option_aliases'])} option aliases")
