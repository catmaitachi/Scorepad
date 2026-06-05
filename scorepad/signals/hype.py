from __future__ import annotations

import math

from scorepad.signals.base import GameContext, Signal


class HypeSignal(Signal):
    name = "hype"

    def __init__(self, hype_cap: int = 500):
        self._hype_cap = hype_cap

    def compute(self, ctx: GameContext) -> float | None:
        if ctx.hypes is None:
            return None

        capped = min(ctx.hypes, self._hype_cap)
        return math.sqrt(capped / self._hype_cap)

    def _explain(self, ctx: GameContext, score: float | None) -> str:
        if score is None:
            return "hype não informado"
        return f"{ctx.hypes} hypes (cap {self._hype_cap}) — score {score:.2f}"
