from __future__ import annotations

import statistics

from scorepad.signals.base import GameContext, Signal


class FranchiseSignal(Signal):
    name = "franchise"

    def __init__(self, success_threshold: float = 70.0):
        self._threshold = success_threshold

    def compute(self, ctx: GameContext) -> float | None:
        if ctx.is_new_ip or not ctx.franchise_ratings:
            return None

        ratings = [r for r in ctx.franchise_ratings if r is not None]
        if not ratings:
            return None

        avg = statistics.mean(ratings)
        base = avg / 100.0

        # Penalidade progressiva apenas abaixo do threshold (70)
        # Acima de 70: sem penalidade. Em 0: penalidade máxima de 0.3.
        if avg < self._threshold:
            deficit_ratio = (self._threshold - avg) / self._threshold
            penalty = deficit_ratio * 0.3
        else:
            penalty = 0.0

        return max(0.0, base - penalty)

    def _explain(self, ctx: GameContext, score: float | None) -> str:
        if score is None:
            return "nova IP ou sem histórico de franquia"
        avg = statistics.mean(ctx.franchise_ratings)
        return f"média da franquia {avg:.1f} — score {score:.2f}"
