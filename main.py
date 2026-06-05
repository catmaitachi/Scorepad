from __future__ import annotations

import argparse

import pandas as pd
from dotenv import load_dotenv

from config import OUTPUT_DIR, config
from scorepad.igdb_client import IGDBClient
from scorepad.processor import process, _primary_studio
from scorepad.scorer import score_game
from scorepad.signals import (
    GPTWSignal,
    GameContext,
    HypeFranchiseSignal,
    MarketValueSignal,
    SimultaneousProjectsSignal,
    StudioHistorySignal,
)


# ── helpers ──────────────────────────────────────────────────────────────────

def _build_signals():
    return [
        StudioHistorySignal(
            success_threshold=config.scoring.success_threshold,
            min_games=config.scoring.min_studio_games,
        ),
        HypeFranchiseSignal(
            hype_cap=config.scoring.hype_cap,
            success_threshold=config.scoring.success_threshold,
        ),
        SimultaneousProjectsSignal(
            penalty_start=config.scoring.simultaneous_penalty_start,
            max_simultaneous=config.scoring.simultaneous_max,
        ),
        MarketValueSignal(),
        GPTWSignal(),
    ]


def _setup_client() -> IGDBClient:
    load_dotenv()
    client = IGDBClient(config.fetch)
    print("Autenticando na IGDB...")
    client.authenticate()
    return client


def _score_games(games_raw: list[dict], client: IGDBClient) -> list[dict]:
    if not games_raw:
        return []

    studio_ids = list({_primary_studio(g) for g in games_raw if _primary_studio(g)})

    print(f"Buscando histórico de {len(studio_ids)} estúdios...")
    history_by_studio = {sid: client.fetch_studio_history(sid) for sid in studio_ids}

    print("Resolvendo nomes de empresas...")
    company_names = client.resolve_company_names(studio_ids)

    print("Processando dados...")
    games_df, studio_profiles = process(
        games_raw, history_by_studio, company_names, config.fetch, config.scoring
    )
    print(f"  {len(games_df)} jogos | {len(studio_profiles)} perfis de estúdio")

    signals = _build_signals()
    weights = config.scoring.signal_weights

    print("Calculando scores...")
    results = []
    for _, row in games_df.iterrows():
        ctx = GameContext(
            game_id=row["game_id"],
            name=row["name"],
            hypes=row["hypes"],
            is_new_ip=row["is_new_ip"],
            franchise_ratings=row["franchise_ratings"],
            studio_history=row["studio_history"],
            simultaneous_projects=row["simultaneous_projects"],
        )
        score_data = score_game(ctx, signals, weights)

        entry = {
            "game_id": row["game_id"],
            "name": row["name"],
            "studio": row["studio"],
            "release_date": row["release_date"],
            "hypes": row["hypes"],
            "is_new_ip": row["is_new_ip"],
            "chance_success": score_data["chance_success"],
            "confidence": score_data["confidence"],
            "confidence_label": score_data["confidence_label"],
            "cover_url": row["cover_url"],
            "studio_logo_url": row["studio_logo_url"],
        }

        if config.output.include_signal_detail:
            for r in score_data["_signal_results"]:
                entry[f"signal_{r.name}_score"] = round(r.score, 2) if r.available else None

        results.append(entry)

    return results


def _to_dataframe(results: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(results)
    cols = [c for c in config.output.csv_columns if c in df.columns]
    if config.output.include_signal_detail:
        signal_cols = [c for c in df.columns if c.startswith("signal_") and c.endswith("_score")]
        cols = cols + signal_cols
    return df[cols].sort_values("chance_success", ascending=False)


def _print_table(df: pd.DataFrame, extra_cols: list[str] | None = None) -> None:
    base_cols = ["name", "studio", "chance_success", "confidence_label"]
    display_cols = base_cols + (extra_cols or [])

    signal_cols = [c for c in df.columns if c.startswith("signal_") and c.endswith("_score")]
    display_cols += signal_cols

    display_cols = [c for c in display_cols if c in df.columns]
    rename = {c: c.replace("signal_", "").replace("_score", "") for c in signal_cols}
    print(df[display_cols].rename(columns=rename).to_string(index=False))


# ── modos ─────────────────────────────────────────────────────────────────────

def run_list(args) -> None:
    client = _setup_client()
    offset = (args.page - 1) * args.limit

    print(f"Buscando próximos lançamentos (ordem: {args.order} | limite: {args.limit} | página: {args.page})...")
    games_raw = client.fetch_upcoming_games(
        limit=args.limit, offset=offset, order_by=args.order
    )
    print(f"  {len(games_raw)} jogos encontrados")

    if not games_raw:
        print("Nenhum jogo encontrado.")
        return

    results = _score_games(games_raw, client)
    output_df = _to_dataframe(results)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / config.output.csv_filename
    output_df.to_csv(output_path, index=False)

    print(f"\nExportado: {output_path} ({len(output_df)} jogos)\n")
    _print_table(output_df)


def run_search(args) -> None:
    client = _setup_client()

    print(f'Buscando "{args.query}"...')
    games_raw = client.search_game(args.query)
    print(f"  {len(games_raw)} resultado(s) encontrado(s)")

    if not games_raw:
        print("Nenhum resultado encontrado.")
        return

    results = _score_games(games_raw, client)
    output_df = _to_dataframe(results)

    print()
    _print_table(output_df, extra_cols=["release_date"])

    if args.export:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / "search_result.csv"
        output_df.to_csv(output_path, index=False)
        print(f"\nExportado: {output_path}")


# ── entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scorepad — análise preditiva de jogos",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="mode")

    list_parser = subparsers.add_parser("list", help="Listar próximos lançamentos")
    list_parser.add_argument(
        "--order", choices=["hype", "date"], default="hype",
        help="Ordenação: hype (padrão) ou date (data de lançamento)",
    )
    list_parser.add_argument(
        "--limit", type=int, default=50,
        help="Quantidade de jogos por página (padrão: 50)",
    )
    list_parser.add_argument(
        "--page", type=int, default=1,
        help="Número da página (padrão: 1)",
    )

    search_parser = subparsers.add_parser("search", help="Buscar um jogo pelo nome")
    search_parser.add_argument("query", help="Nome do jogo a buscar")
    search_parser.add_argument(
        "--export", action="store_true",
        help="Exportar resultado para output/search_result.csv",
    )

    args = parser.parse_args()

    if args.mode == "search":
        run_search(args)
    else:
        if args.mode is None:
            args.order = "hype"
            args.limit = config.fetch.max_upcoming
            args.page = 1
        run_list(args)


if __name__ == "__main__":
    main()
