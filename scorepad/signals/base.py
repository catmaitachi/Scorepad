from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class GameContext:
    game_id: int
    name: str
    hypes: int | None
    is_new_ip: bool
    franchise_ratings: list[tuple[float, int | None]] = field(default_factory=list)
    studio_history: list[float] = field(default_factory=list)
    simultaneous_projects: int | None = None
    market_value: float | None = None
    gptw_score: float | None = None


@dataclass
class SignalResult:
    name: str
    score: float
    weight: float
    available: bool
    explanation: str


class Signal(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def compute(self, ctx: GameContext) -> float | None: ...

    def evaluate(self, ctx: GameContext, weight: float) -> SignalResult:
        score = self.compute(ctx)
        available = score is not None
        return SignalResult(
            name=self.name,
            score=score if available else 0.0,
            weight=weight,
            available=available,
            explanation=self._explain(ctx, score),
        )

    def _explain(self, ctx: GameContext, score: float | None) -> str:
        if score is None:
            return "dados insuficientes"
        return f"{score:.2f}"
