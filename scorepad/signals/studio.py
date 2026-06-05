from __future__ import annotations

import statistics

from scorepad.signals.base import GameContext, Signal


class StudioHistorySignal(Signal):
    name = "studio_history"

    def __init__(self, success_threshold: float = 70.0, min_games: int = 2):
        self._threshold = success_threshold
        self._min_games = min_games

    def compute(self, ctx: GameContext) -> float | None:
        history = [r for r in ctx.studio_history if r is not None]
        if len(history) < self._min_games:
            return None

        success_rate = sum(1 for r in history if r >= self._threshold) / len(history)

        if len(history) >= 2:
            std = statistics.stdev(history)
            consistency = max(0.0, 1.0 - (std / 100.0))
        else:
            consistency = 1.0

        return success_rate * 0.7 + consistency * 0.3

    def _explain(self, ctx: GameContext, score: float | None) -> str:
        if score is None:
            return f"histórico insuficiente ({len(ctx.studio_history)} jogos)"
        n = len(ctx.studio_history)
        ok = sum(1 for r in ctx.studio_history if r >= self._threshold)
        return f"{ok}/{n} jogos acima do threshold — score {score:.2f}"
