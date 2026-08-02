"""Fold a completed run back into the memory graph, then regenerate GRAPH.md.

Every observation is appended to events.jsonl first, then merged into graph.json.
The event log is never rewritten, so a bad merge can always be reconstructed.

Usage:
    python kb/harvest.py runs/<run>.json
    python kb/harvest.py --render-only
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from kb import Graph, log_event  # noqa: E402

KB_DIR = Path(__file__).parent


def harvest(run_path):
    """A run file records what a single application observed. Shape:

    {"application": "app:acme-4471", "date": "2026-08-15",
     "ats": "ats:greenhouse", "tenant": "tenant:acme.greenhouse.io",
     "steps": [{"index": 1, "label": "Basic Info", "is_terminal_submit": false}],
     "fields": [{"canonical": "identity.first_name", "label": "First Name", "step": 1,
                 "automation_id": "first_name", "interaction": "text", "value": "Jay",
                 "options": [], "profile_key": "personal_information.first_name"}],
     "answers": [{"question": "...", "value": "No", "confidence": "high",
                  "decided_by": "graph", "reasoning": "...", "aid": "..."}],
     "pitfalls": [{"id": "G1-near-miss", "severity": "low", "what": "..."}],
     "constraints": [{"id": "constraint:max_len_2000", "label": "...", "applies_to": "free_text"}],
     "not_asked": ["personal_information.github"],
     "outcome": {"submitted": false, "credits_spent": 41}}
    """
    run = json.loads(Path(run_path).read_text(encoding="utf-8"))
    g = Graph()

    app, day = run["application"], run["date"]
    ats, tenant = run["ats"], run["tenant"]
    N = lambda *a, **k: g.add_node(*a, seen=day, app=app, **k)
    E = lambda *a, **k: g.add_edge(*a, app=app, **k)

    before = (len(g.nodes), len(g.edges))

    N(ats, "ats", ats.split(":", 1)[1])
    N(tenant, "tenant", run.get("tenant_label", tenant.split(":", 1)[1]),
      **run.get("tenant_attrs", {}))
    E(ats, tenant, "has_tenant")

    for s in run.get("steps", []):
        sid = f"step:{tenant}#{s['index']}"
        N(sid, "step", s["label"], index=s["index"],
          is_terminal_submit=s.get("is_terminal_submit", False))
        E(tenant, sid, "has_step")
        if s.get("is_terminal_submit"):
            E(sid, "guard:G1", "is_terminal_submit")

    for f in run.get("fields", []):
        node = f"field:{f['canonical']}"          # canonical layer: shared across every ATS
        N(node, "field", f["label"], canonical=f["canonical"])
        E(f"step:{tenant}#{f['step']}", node, "has_field")

        sel = f"selector:{tenant}#{f['automation_id']}"   # selector layer: tenant-local
        N(sel, "selector", f["automation_id"], automation_id=f["automation_id"],
          interaction=f["interaction"], recipe=f.get("recipe", ""),
          value_used=f.get("value"))
        E(node, sel, "located_by")

        for o in f.get("options", []):
            N(f"option:{o}", "option", o)
            E(node, f"option:{o}", "accepts_option")
        for wanted, actual in f.get("option_aliases", {}).items():
            N(f"option:{wanted}", "option", wanted, exists_in_ats=False)
            E(f"option:{wanted}", f"option:{actual}", "maps_to")
        if f.get("profile_key"):
            N(f"profile_field:{f['profile_key']}", "profile_field", f["profile_key"])
            E(node, f"profile_field:{f['profile_key']}", "maps_to")

    for a in run.get("answers", []):
        aid = f"answer:{a['question'][:60]}"      # answer layer: shared across every employer
        # A reworded version of a question already answered is a distinct observation,
        # but it should point at the original so provenance chains instead of forking.
        prior, score = g.find_answer(a["question"], tenant=tenant)
        N(aid, "answer", a["question"], confidence=a.get("confidence", "medium"),
          value=a["value"], decided_by=a.get("decided_by", "graph"),
          reasoning=a.get("reasoning", ""))
        if prior and prior["id"] != aid:
            E(aid, prior["id"], "maps_to", similarity=round(score, 3))
            if str(prior["attrs"]["value"]).lower() != str(a["value"]).lower():
                E(aid, prior["id"], "conflicts_with",
                  note=f"same question answered '{prior['attrs']['value']}' before")
        E(aid, app, "observed_in")
        if a.get("aid"):
            E(aid, tenant, "observed_in", aid=a["aid"])

    for c in run.get("constraints", []):
        N(c["id"], "constraint", c["label"], **{k: v for k, v in c.items()
                                                if k not in ("id", "label")})
        E(ats, c["id"], "constrained_by")

    for p in run.get("pitfalls", []):
        N(f"pitfall:{p['id']}", "pitfall", p["what"], severity=p.get("severity", "low"))
        E(f"pitfall:{p['id']}", app, "observed_in")
        if p.get("guard"):
            E(f"pitfall:{p['id']}", f"guard:{p['guard']}", "prevented_by")

    for pkey in run.get("not_asked", []):
        N(f"profile_field:{pkey}", "profile_field", pkey)
        E(tenant, f"profile_field:{pkey}", "not_asked")

    N(app, "application", run.get("label", app), **run.get("outcome", {}))
    E(app, tenant, "observed_in")

    g.save()
    after = (len(g.nodes), len(g.edges))
    log_event("harvest", application=app, day=day, source=str(run_path),
              nodes_added=after[0] - before[0], edges_added=after[1] - before[1])
    print(f"harvested {app}: +{after[0]-before[0]} nodes, +{after[1]-before[1]} edges")
    return g


# ------------------------------------------------------------------ render

def render(out=KB_DIR / "GRAPH.md"):
    g = Graph()
    by_type = defaultdict(list)
    for n in g.nodes.values():
        by_type[n["type"]].append(n)

    L = []
    L.append("# Application Memory Graph\n")
    L.append("> Generated by `kb/harvest.py --render-only`. Source of truth is `kb/graph.json`.\n")
    L.append(f"**{len(g.nodes)} nodes · {len(g.edges)} edges · "
             f"{len(by_type['application'])} application(s) · "
             f"{len(by_type['tenant'])} tenant(s)**\n")

    L.append("## Reuse layers\n")
    L.append("| Layer | Scope | Count | Reused by |")
    L.append("|---|---|---|---|")
    L.append(f"| Canonical fields | universal | {len(by_type['field'])} | every application |")
    L.append(f"| Answer bank | universal | {len(by_type['answer'])} | every application |")
    L.append(f"| Constraints | per ATS product | {len(by_type['constraint'])} | every tenant of that ATS |")
    L.append(f"| Selectors | per tenant | {len(by_type['selector'])} | every req in that tenant |")
    L.append(f"| Guards | global | {len(by_type['guard'])} | every run |\n")

    L.append("## Submit boundaries — read before clicking anything\n")
    for t in sorted(by_type["tenant"], key=lambda n: n["id"]):
        steps = sorted(g.neighbors(t["id"], rel="has_step"), key=lambda s: s["attrs"]["index"])
        term = next((s for s in steps if s["attrs"].get("is_terminal_submit")), None)
        where = (f"**step {term['attrs']['index']} — {term['label']}**" if term
                 else "_unknown — treat every continue as destructive_")
        L.append(f"- `{t['id']}` → continue submits at {where}")
    L.append("")

    L.append("## Guards\n")
    L.append("| ID | Guard | Rule |")
    L.append("|---|---|---|")
    for gd in sorted(by_type["guard"], key=lambda n: _gnum(n["id"])):
        prevented = [p for p in g.neighbors(gd["id"], rel="prevented_by", reverse=True)]
        L.append(f"| {gd['id'].split(':')[1]} ({len(prevented)}) | {gd['label']} | "
                 f"{gd['attrs']['description']} |")
    L.append("")

    L.append("## Pitfalls by severity\n")
    for sev in ("fatal", "high", "medium", "low"):
        rows = [p for p in by_type["pitfall"] if p["attrs"].get("severity") == sev]
        if not rows:
            continue
        L.append(f"### {sev} ({len(rows)})\n")
        for p in sorted(rows, key=lambda n: n["id"]):
            guard = next(iter(g.neighbors(p["id"], rel="prevented_by")), None)
            gtag = f" → `{guard['id'].split(':')[1]}`" if guard else ""
            L.append(f"- **{p['id'].split(':')[1]}**{gtag} — {p['label']}")
        L.append("")

    L.append("## Answer bank\n")
    L.append("| Question | Answer | Confidence | Decided by |")
    L.append("|---|---|---|---|")
    for a in sorted(by_type["answer"], key=lambda n: n["label"]):
        q = a["label"] if len(a["label"]) <= 90 else a["label"][:87] + "…"
        L.append(f"| {q} | **{a['attrs']['value']}** | {a['confidence']} | "
                 f"{a['attrs']['decided_by']} |")
    L.append("")

    L.append("## Upload hosts\n")
    L.append("| Host | Status | Last ok | Last fail |")
    L.append("|---|---|---|---|")
    for h in sorted(by_type["host"], key=lambda n: (n["attrs"]["status"] != "ok", n["label"])):
        a = h["attrs"]
        L.append(f"| {h['label']} | {a['status']} | {a.get('last_ok') or '—'} | "
                 f"{a.get('last_fail') or '—'} |")
    L.append("")

    L.append("## Tool facts\n")
    for f in sorted(by_type["tool_fact"], key=lambda n: n["id"]):
        L.append(f"- `{f['id'].split(':',1)[1]}` — {f['label']}")
    L.append("")

    L.append("## Shape\n")
    L.append("```mermaid")
    L.append("graph LR")
    for t in sorted(by_type["tenant"], key=lambda n: n["id"]):
        ats = next((e["from"] for e in g.edges
                    if e["rel"] == "has_tenant" and e["to"] == t["id"]), "?")
        L.append(f'  {_m(ats)}["{ats}"] --> {_m(t["id"])}["{t["label"]}"]')
        for s in sorted(g.neighbors(t["id"], rel="has_step"), key=lambda s: s["attrs"]["index"]):
            mark = " ⛔SUBMIT" if s["attrs"].get("is_terminal_submit") else ""
            L.append(f'  {_m(t["id"])} --> {_m(s["id"])}["{s["attrs"]["index"]}. {s["label"]}{mark}"]')
    L.append("```")

    Path(out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(L)} lines)")


def _gnum(gid):
    digits = "".join(c for c in gid if c.isdigit())
    return int(digits) if digits else 0


def _m(node_id):
    return "".join(c if c.isalnum() else "_" for c in node_id)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] != "--render-only":
        harvest(args[0])
    render()
