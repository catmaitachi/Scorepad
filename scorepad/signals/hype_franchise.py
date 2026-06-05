from __future__ import annotations

import math

from scorepad.signals.base import GameContext, Signal


class HypeFranchiseSignal(Signal):
    """
    Nova IP: score puro de hype (sqrt normalizado).
    Franquia: média ponderada por recência + hype como validação (0.7×–1.0×).
    """

    name = "hype_franchise"

    def __init__(
        self,
        hype_cap: int = 500,
        success_threshold: float = 70.0,
        recency_decay: float = 0.7,
    ):
        self._hype_cap = hype_cap
        self._threshold = success_threshold
        self._decay = recency_decay

    def compute(self, ctx: GameContext) -> float | None:
        hype_score = (
            math.sqrt(min(ctx.hypes, self._hype_cap) / self._hype_cap)
            if ctx.hypes is not None else None
        )

        # Nova IP: apenas hype
        if ctx.is_new_ip or not ctx.franchise_ratings:
            return hype_score

        # Franquia: filtra entradas com rating válido
        rated = [(r, d) for r, d in ctx.franchise_ratings if r is not None]
        if not rated:
            return hype_score

        weighted_avg = self._recency_weighted_avg(rated)
        base = weighted_avg / 100.0

        # Penalidade progressiva abaixo do threshold
        if weighted_avg < self._threshold:
            deficit_ratio = (self._threshold - weighted_avg) / self._threshold
            base = max(0.0, base - deficit_ratio * 0.3)

        # Hype como validação: multiplica entre 0.7 (sem hype) e 1.0 (hype máximo)
        if hype_score is not None:
            base = base * (0.7 + 0.3 * hype_score)

        return base

    def _recency_weighted_avg(self, rated: list[tuple[float, int | None]]) -> float:
        # Ordena do mais antigo ao mais recente (None vai para o início)
        sorted_games = sorted(rated, key=lambda x: x[1] or 0)
        n = len(sorted_games)
        weights = [self._decay ** (n - 1 - i) for i in range(n)]
        total = sum(weights)
        return sum(r * w for (r, _), w in zip(sorted_games, weights)) / total

    def _explain(self, ctx: GameContext, score: float | None) -> str:
        if score is None:
            return "sem hype e sem histórico de franquia"
        if ctx.is_new_ip or not ctx.franchise_ratings:
            return f"nova IP — {ctx.hypes} hypes — score {score:.2f}"
        rated = [(r, d) for r, d in ctx.franchise_ratings if r is not None]
        if rated:
            w_avg = self._recency_weighted_avg(rated)
            return f"média ponderada franquia {w_avg:.1f} | {ctx.hypes} hypes — score {score:.2f}"
        return f"{ctx.hypes} hypes — score {score:.2f}"
