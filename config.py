from dataclasses import dataclass, field
from __future__ import annotations
from pathlib import Path

# * Rotas ───────────────────────────────────────────────────────────

ROOT_DIR        = Path(__file__).parent
OUTPUT_DIR      = ROOT_DIR / 'output'
DATA_RAW        = ROOT_DIR / 'data' / 'raw'
DATA_PROCESSED  = ROOT_DIR / 'data' / 'processed'

# * Configurações de coleta ─────────────────────────────────────────

@dataclass
class FetchConfig:
    
    # Hype mínimo para incluir um jogo na busca
    min_hype: int = 5
 
    # Ordenação dos resultados: "date" | "hype"
    order_by: str = "hype"
 
    # Máximo de jogos futuros a buscar
    max_upcoming: int = 200
 
    # Máximo de jogos históricos por estúdio
    max_history_per_studio: int = 50
 
    # Mínimo de avaliações para um jogo histórico ser considerado
    min_rating_count: int = 10
 
    # Pausa entre requisições à API (respeita limite de 4 req/s)
    request_delay: float = 0.25

# * Configurações de scoring ────────────────────────────────────────

@dataclass
class ScoringConfig:

    # Nota mínima para um jogo ser considerado "sucesso" no histórico
    success_threshold: float = 70.0
 
    # Mínimo de jogos no histórico do estúdio para o sinal ser válido
    min_studio_games: int = 2
 
    # Valor de hype considerado "máximo" para normalização (acima = 1.0)
    hype_cap: int = 500
 
    # A partir de quantos projetos simultâneos começa a penalizar
    simultaneous_penalty_start: int = 2
 
    # Acima deste número de projetos, penalidade máxima
    simultaneous_max: int = 4
 
    # Pesos dos sinais — mude aqui para rebalancear o modelo
    signal_weights: dict[str, float] = field(default_factory=lambda: {
        "studio_history":         3.0,
        "franchise":              2.5,
        "hype":                   1.5,
        "simultaneous_projects":  2.0,
        "budget":                 1.5,
        "market_value":           0.0,  # ToDo
        "gptw":                   0.0,  # ToDo
    })

# * Configurações de saída ───────────────────────────────────────────────

@dataclass
class OutputConfig:

    # Nome do arquivo CSV exportado para o Power BI
    csv_filename: str = "predictions.csv"
 
    # Colunas incluídas no CSV final
    csv_columns: list[str] = field(default_factory=lambda: [
        "game_id", "name", "studio", "release_date",
        "hypes", "is_new_ip", "chance_success",
        "confidence", "confidence_label",
    ])
 
    # Ordenação padrão do CSV: "chance_success" | "release_date" | "hypes"
    sort_by: str = "chance_success"
 
    # Mostrar detalhes de cada sinal no CSV (adiciona colunas por sinal)
    include_signal_detail: bool = False

# * Instâncias das configurações ─────────────────────────────────────────

fetch    = FetchConfig()
output   = OutputConfig()
scoring  = ScoringConfig()