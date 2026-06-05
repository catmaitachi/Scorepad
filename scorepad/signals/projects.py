from __future__ import annotations

from scorepad.signals.base import GameContext, Signal


class SimultaneousProjectsSignal(Signal):
    name = "simultaneous_projects"

    def __init__(self, penalty_start: int = 2, max_simultaneous: int = 4):
        self._penalty_start = penalty_start
        self._max_simultaneous = max_simultaneous

    def compute(self, ctx: GameContext) -> float | None:
        if ctx.simultaneous_projects is None:
            return None

        if ctx.simultaneous_projects <= self._penalty_start:
            return 1.0

        excess = ctx.simultaneous_projects - self._penalty_start
        max_excess = self._max_simultaneous - self._penalty_start
        penalty = excess / max(max_excess, 1)

        return max(0.0, 1.0 - penalty)

    def _explain(self, ctx: GameContext, score: float | None) -> str:
        if score is None:
            return "projetos simultâneos não informados"
        return f"{ctx.simultaneous_projects} projetos simultâneos — score {score:.2f}"
