from dataclasses import dataclass, field
from pathlib import Path

ROOT_DIR = Path(__file__).parent
OUTPUT_DIR = ROOT_DIR / "output"
DATA_RAW = ROOT_DIR / "data" / "raw"
DATA_PROCESSED = ROOT_DIR / "data" / "processed"


@dataclass
class FetchConfig:
    # Mínimo de hypes para um jogo entrar na busca (filtra títulos sem engajamento)
    min_hype: int = 1

    # Campo usado para ordenar os resultados da IGDB: "hype" ou "date"
    order_by: str = "hype"

    # Quantidade máxima de jogos futuros retornados por execução
    max_upcoming: int = 200

    # Máximo de jogos históricos buscados por estúdio (limita chamadas à API)
    max_history_per_studio: int = 50

    # Mínimo de avaliações que um jogo precisa ter para entrar no perfil do estúdio
    min_rating_count: int = 10

    # Pausa em segundos entre páginas de resultados (respeita rate limit da IGDB)
    request_delay: float = 0.25

    # Janela máxima de lançamentos futuros em dias (730 = até 2 anos à frente)
    max_future_days: int = 730


@dataclass
class ScoringConfig:
    # Nota mínima (0–100) para considerar um jogo "bem-sucedido" no histórico do estúdio
    success_threshold: float = 70.0

    # Mínimo de jogos com nota válida para construir o perfil de um estúdio
    min_studio_games: int = 2

    # Teto de hypes para normalização — valores acima são tratados como iguais ao cap
    hype_cap: int = 600

    # A partir de quantos projetos simultâneos o estúdio começa a ser penalizado
    simultaneous_penalty_start: int = 2

    # Número de projetos simultâneos em que a penalidade atinge o máximo (score → 0)
    simultaneous_max: int = 4

    # Peso de cada signal no score final — coloque 0.0 para desativar um signal
    signal_weights: dict = field(default_factory=lambda: {
        "studio_history":           3.0, # histórico de qualidade do estúdio
        "hype_franchise":           4.0, # franquia ponderada por recência + hype da comunidade
        "simultaneous_projects":    0.0, # ToDo: revisar lógica do signal — contagem de simultâneos não está funcionando corretamente
        "market_value":             0.0, # ToDO — aguardando fonte de dados
        "gptw":                     0.0, # ToDO — aguardando fonte de dados
    })


@dataclass
class OutputConfig:
    # Nome do arquivo exportado em output/
    csv_filename: str = "predictions.csv"

    # Colunas que aparecem no CSV final (ordem preservada)
    csv_columns: list = field(default_factory=lambda: [
        "game_id",
        "name",
        "studio",
        "release_date",
        "hypes",
        "is_new_ip",
        "chance_success",
        "confidence",
        "confidence_label",
        "cover_url",
        "studio_logo_url",
    ])

    # Coluna usada para ordenar o CSV (descendente)
    sort_by: str = "chance_success"

    # Se True, adiciona colunas com o score e a nota de cada signal individualmente
    include_signal_detail: bool = True


@dataclass
class Config:
    fetch: FetchConfig = field(default_factory=FetchConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    output: OutputConfig = field(default_factory=OutputConfig)


config = Config()
