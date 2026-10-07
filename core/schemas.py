from __future__ import annotations
from typing import List, Dict, Any, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class Node(BaseModel):
    id: str
    label: str
    children: List["Node"] = Field(default_factory=list)
    rationale: Optional[str] = None
    evidence: Optional[str] = None


Node.model_rebuild()


class IssueTreeConfig(BaseModel):
    module: Literal["issue_tree"]
    objective: str
    nodes: List[Node]
    assumptions: List[str] = Field(default_factory=list)


class Criterion(BaseModel):
    name: str
    weight_pct: float = Field(ge=0, le=100)
    notes: Optional[str] = None


class Option(BaseModel):
    name: str
    scores: Dict[str, float] = Field(default_factory=dict)  # criterion -> 1-10 or 1-5
    rationale: Optional[str] = None


class DecisionMatrixConfig(BaseModel):
    module: Literal["decision_matrix"]
    title: str
    criteria: List[Criterion]
    options: List[Option]
    scale: Literal["1-5", "1-10"] = "1-10"
    assumptions: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_weights_sum(self) -> "DecisionMatrixConfig":
        total = sum(c.weight_pct for c in self.criteria)
        if abs(total - 100.0) > 0.5:
            raise ValueError(f"Weights must sum to ~100%. Got {total:.2f}%")
        return self

    @model_validator(mode="after")
    def check_scores_cover_criteria(self) -> "DecisionMatrixConfig":
        crit_names = [c.name for c in self.criteria]
        for opt in self.options:
            missing = [c for c in crit_names if c not in opt.scores]
            if missing:
                raise ValueError(f"Option '{opt.name}' missing scores for: {missing}")
        return self


class CanvasFactor(BaseModel):
    factor: str
    notes: Optional[str] = None


class CanvasProfile(BaseModel):
    name: str
    values: Dict[str, float] = Field(default_factory=dict)  # factor -> 0-10


class StrategyCanvasConfig(BaseModel):
    module: Literal["strategy_canvas"]
    title: str
    factors: List[CanvasFactor]
    profiles: List[CanvasProfile]
    assumptions: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_factors_covered(self) -> "StrategyCanvasConfig":
        fact_names = [f.factor for f in self.factors]
        for p in self.profiles:
            missing = [f for f in fact_names if f not in p.values]
            if missing:
                raise ValueError(f"Profile '{p.name}' missing values for: {missing}")
        return self


ConfigUnion = IssueTreeConfig | DecisionMatrixConfig | StrategyCanvasConfig
