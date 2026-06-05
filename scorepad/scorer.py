from __future__ import annotations

from scorepad.signals.base import GameContext, Signal, SignalResult


def score_game(
    ctx: GameContext,
    signals: list[Signal],
    weights: dict[str, float],
) -> dict:
    results: list[SignalResult] = [
        signal.evaluate(ctx, weights.get(signal.name, 0.0))
        for signal in signals
    ]

    active = [r for r in results if r.weight > 0]
    available = [r for r in active if r.available]

    total_weight = sum(r.weight for r in available)
    if total_weight == 0:
        chance = 0.0
    else:
        chance = sum(r.score * r.weight for r in available) / total_weight * 100.0

    total_active = len(active)
    confidence_ratio = len(available) / total_active if total_active > 0 else 0.0

    if confidence_ratio >= 0.8:
        label = "Alta"
    elif confidence_ratio >= 0.5:
        label = "Média"
    else:
        label = "Baixa"

    return {
        "chance_success": round(chance, 2),
        "confidence": round(confidence_ratio, 2),
        "confidence_label": label,
        "_signal_results": results,
    }
