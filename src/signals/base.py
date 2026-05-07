from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class GameContext:

    """
    Tudo que os signals precisam saber sobre um jogo futuro.
    Campos ausentes devem ser None, o signal correspondente será ignorado.
    """

    game_id:               int
    name:                  str
    hypes:                 int          | None = None
    is_new_ip:             bool         | None = None
    franchise_ratings:     list[float]  | None = None  # ? notas anteriores da franquia
    studio_history:        list[float]  | None = None  # ? notas históricas do estúdio
    simultaneous_projects: int          | None = None  # ? projetos ativos do estúdio
    market_value:          float        | None = None  # ToDo
    gptw_score:            float        | None = None  # ToDo

@dataclass
class SignalResult:

    """
    Resultado de um signal após computação.
    """

    name:        str
    score:       float        # 0.0 a 1.0
    weight:      float        # peso configurado
    available:   bool = True  # False se dados insuficientes
    explanation: str  = ""

class Signal(ABC):

    """
    Classe base para qualquer signal de scoring.
 
    compute() deve:
      - Retornar float entre 0.0 (pior) e 1.0 (melhor)
      - Retornar None se não houver dados suficientes
    """

    name: str = "base_signal"
 
    @abstractmethod
    def compute(self, ctx: GameContext) -> float | None:
        pass