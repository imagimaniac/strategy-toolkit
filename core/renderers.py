from __future__ import annotations
from typing import Dict, Any
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os


TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


class Renderer:
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def to_markdown(self, cfg) -> str:
        mod = cfg.module
        if mod == "issue_tree":
            return self.env.get_template("issue_tree.md.j2").render(cfg=cfg)
        if mod == "decision_matrix":
            return self.env.get_template("decision_matrix.md.j2").render(cfg=cfg)
        if mod == "strategy_canvas":
            return self.env.get_template("strategy_canvas.md.j2").render(cfg=cfg)
        raise ValueError(f"Unknown module: {mod}")

    def to_dict(self, cfg) -> Dict[str, Any]:
        return cfg.model_dump()

    def to_json(self, cfg) -> str:
        return json.dumps(cfg.model_dump(), indent=2)

    def to_csv(self, cfg) -> str:
        mod = cfg.module
        if mod == "decision_matrix":
            rows = []
            crit_names = [c.name for c in cfg.criteria]
            rows.append(["option"] + crit_names + ["weighted_score(approx)"])
            for opt in cfg.options:
                ws = 0.0
                for c in cfg.criteria:
                    s = float(opt.scores.get(c.name, 0))
                    ws += s * c.weight_pct / 100.0
                row = [opt.name] + [str(opt.scores.get(cn, "")) for cn in crit_names] + [f"{ws:.2f}"]
                rows.append(row)
            return "\n".join(",".join(r) for r in rows)
        if mod == "strategy_canvas":
            fact_names = [f.factor for f in cfg.factors]
            rows = [["profile"] + fact_names]
            for p in cfg.profiles:
                rows.append([p.name] + [str(p.values.get(fn, "")) for fn in fact_names])
            return "\n".join(",".join(r) for r in rows)
        if mod == "issue_tree":
            # simple flattened CSV
            rows = [["objective", cfg.objective]]
            def walk(n, parent=""):
                rows.append([n.id, n.label, parent])
                for ch in n.children:
                    walk(ch, n.id)
            for n in cfg.nodes:
                walk(n, "")
            # header
            out = [["id", "label", "parent"]] + rows[1:]
            return "\n".join(",".join(str(x) for x in r) for r in out)
        raise ValueError(f"CSV not implemented for {mod}")
