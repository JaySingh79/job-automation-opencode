"""Application memory graph — node/edge store.

Plain JSON, no database. `graph.json` is the record of truth; `events.jsonl` is an
append-only observation log that is never rewritten, so provenance survives any
later merge or correction.

Contradictions are not overwritten. When a node's attrs change materially, the old
node is kept and linked with a `superseded_by` edge, so a tenant that silently
changes its DOM leaves a visible trail.
"""

import json
from difflib import SequenceMatcher
from pathlib import Path

KB_DIR = Path(__file__).parent
GRAPH = KB_DIR / "graph.json"
EVENTS = KB_DIR / "events.jsonl"

NODE_TYPES = {
    "ats", "tenant", "step", "field", "selector", "option", "constraint",
    "pitfall", "guard", "answer", "host", "tool_fact", "application", "profile_field",
}

# Calibrated against the observed spread: genuine rewordings of the same question score
# >= 0.80, unrelated screening questions <= 0.68. 0.78 sits in that gap with margin.
THRESHOLD = 0.78

EDGE_RELS = {
    "has_tenant", "has_step", "has_field", "located_by", "accepts_option", "maps_to",
    "constrained_by", "caused", "prevented_by", "answered_by", "observed_in",
    "conflicts_with", "superseded_by", "not_asked", "is_terminal_submit",
}


class Graph:
    def __init__(self, path=None):
        # Resolved at call time, not definition time, so tests can point the store
        # at a scratch file without the real graph being touched.
        self.path = Path(path) if path else GRAPH
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            data = {"nodes": [], "edges": []}
        self.nodes = {n["id"]: n for n in data["nodes"]}
        self.edges = data["edges"]

    # ------------------------------------------------------------------ write

    def add_node(self, id, type, label="", confidence="high", seen=None, app=None, **attrs):
        if type not in NODE_TYPES:
            raise ValueError(f"unknown node type: {type}")
        existing = self.nodes.get(id)
        if existing is None:
            self.nodes[id] = {
                "id": id, "type": type, "label": label, "confidence": confidence,
                "first_seen": seen, "last_confirmed": seen,
                "applications": [app] if app else [],
                "attrs": attrs,
            }
            return self.nodes[id]

        if existing["attrs"] and attrs and existing["attrs"] != attrs:
            # Material change: keep the old observation, point it at the new one.
            stale = f"{id}@{existing['last_confirmed']}"
            if stale not in self.nodes:
                self.nodes[stale] = dict(existing, id=stale)
                self.add_edge(stale, id, "superseded_by", app=app)
        existing["attrs"] = {**existing["attrs"], **attrs}
        existing["last_confirmed"] = seen or existing["last_confirmed"]
        if app and app not in existing["applications"]:
            existing["applications"].append(app)
        return existing

    def add_edge(self, src, dst, rel, app=None, **attrs):
        if rel not in EDGE_RELS:
            raise ValueError(f"unknown edge rel: {rel}")
        for e in self.edges:
            if (e["from"], e["to"], e["rel"]) == (src, dst, rel):
                if app and app not in e["seen_in"]:
                    e["seen_in"].append(app)
                e["attrs"].update(attrs)
                return e
        edge = {"from": src, "to": dst, "rel": rel,
                "seen_in": [app] if app else [], "attrs": attrs}
        self.edges.append(edge)
        return edge

    def save(self):
        payload = {
            "_comment": "Application memory graph. Generated and maintained by kb/. "
                        "Nodes are never deleted; contradictions get a superseded_by edge.",
            "nodes": sorted(self.nodes.values(), key=lambda n: (n["type"], n["id"])),
            "edges": sorted(self.edges, key=lambda e: (e["rel"], e["from"], e["to"])),
        }
        self.path.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")

    # ------------------------------------------------------------------- read

    def query(self, type=None, prefix=None, **attr_filters):
        out = []
        for n in self.nodes.values():
            if type and n["type"] != type:
                continue
            if prefix and not n["id"].startswith(prefix):
                continue
            if any(n["attrs"].get(k) != v for k, v in attr_filters.items()):
                continue
            out.append(n)
        return sorted(out, key=lambda n: n["id"])

    def neighbors(self, id, rel=None, reverse=False):
        key, other = ("to", "from") if reverse else ("from", "to")
        ids = [e[other] for e in self.edges
               if e[key] == id and (rel is None or e["rel"] == rel)]
        return [self.nodes[i] for i in ids if i in self.nodes]

    def one(self, id):
        return self.nodes.get(id)

    # ------------------------------------------------- the compounding lever

    def find_answer(self, question, tenant=None, threshold=THRESHOLD):
        """Screening questions repeat across employers, but rarely verbatim — the same
        question is asked long by one ATS and short by another. Whole-string similarity
        misses those, so score on content-word containment too and take the better.

        Questions naming a specific employer ("Are you currently employed by Gartner?")
        score high against the same question naming a different one, and answering from
        the wrong employer's entry would be a factual error. Those are only reused for
        the tenant they were observed on.

        Returns (answer_node, similarity) or (None, best_similarity).
        """
        best, best_score = None, 0.0
        for n in self.query(type="answer"):
            owners = self._employer_scope(n["id"])
            if owners and tenant not in owners:
                continue
            score = similarity(question, n["label"])
            if score > best_score:
                best, best_score = n, score
        return (best, best_score) if best_score >= threshold else (None, best_score)

    def _employer_scope(self, answer_id):
        """Tenants this answer is locked to, empty if it transfers freely."""
        return {e["to"] for e in self.edges
                if e["from"] == answer_id and e["attrs"].get("employer_specific")}

    def constraints_for(self, ats_id):
        return self.neighbors(ats_id, rel="constrained_by")


STOPWORDS = {
    "a", "an", "the", "you", "your", "yours", "are", "is", "was", "be", "been", "being",
    "do", "does", "did", "have", "has", "had", "will", "would", "can", "could", "should",
    "of", "to", "in", "on", "at", "for", "with", "within", "by", "from", "as", "and",
    "or", "if", "that", "this", "these", "those", "it", "its", "any", "all", "please",
    "which", "who", "whom", "what", "we", "us", "our", "i", "me", "my", "now", "ever",
}


def _normalize(text):
    return " ".join("".join(c.lower() if c.isalnum() or c.isspace() else " "
                            for c in text).split())


def _content_words(text):
    return {w for w in _normalize(text).split() if w not in STOPWORDS and len(w) > 1}


def similarity(a, b, min_content=3):
    """max(whole-string ratio, content-word containment).

    Containment is what catches "Will you, now or in the future, require
    Visa/Sponsorship within the country for which you are applying?" against
    "Will you now or in the future require visa sponsorship for employment?" —
    the short form's content words sit almost entirely inside the long one.

    Containment is only trusted once there are enough content words that the overlap
    means something; below that it degenerates into matching on one shared noun.
    """
    seq = SequenceMatcher(None, _normalize(a), _normalize(b)).ratio()
    ca, cb = _content_words(a), _content_words(b)
    if min(len(ca), len(cb)) < min_content:
        return seq
    containment = len(ca & cb) / min(len(ca), len(cb))
    return max(seq, containment)


# ------------------------------------------------------------------- events

def log_event(kind, **payload):
    """Append-only. Never rewritten, so a bad merge can always be reconstructed."""
    with EVENTS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"kind": kind, **payload}, ensure_ascii=False) + "\n")


def read_events():
    if not EVENTS.exists():
        return []
    return [json.loads(line) for line in EVENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
