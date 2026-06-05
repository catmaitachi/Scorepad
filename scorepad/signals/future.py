from __future__ import annotations

from scorepad.signals.base import GameContext, Signal


class MarketValueSignal(Signal):
    """Stub — aguardando fonte de dados de valor de mercado."""

    name = "market_value"

    def compute(self, ctx: GameContext) -> float | None:
        return None

    def _explain(self, ctx: GameContext, score: float | None) -> str:
        return "fonte de dados não disponível"


class GPTWSignal(Signal):
    """Stub — aguardando integração com Great Place to Work."""

    name = "gptw"

    def compute(self, ctx: GameContext) -> float | None:
        return None

    def _explain(self, ctx: GameContext, score: float | None) -> str:
        return "fonte de dados não disponível"
