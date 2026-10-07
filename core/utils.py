from __future__ import annotations
import yaml
from pydantic import ValidationError
from .schemas import IssueTreeConfig, DecisionMatrixConfig, StrategyCanvasConfig


def load_config(text: str):
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("YAML must be a mapping")
    mod = data.get("module")
    try:
        if mod == "issue_tree":
            return IssueTreeConfig(**data)
        if mod == "decision_matrix":
            return DecisionMatrixConfig(**data)
        if mod == "strategy_canvas":
            return StrategyCanvasConfig(**data)
    except ValidationError as e:
        raise ValueError(str(e))
    raise ValueError("module must be one of: issue_tree, decision_matrix, strategy_canvas")
