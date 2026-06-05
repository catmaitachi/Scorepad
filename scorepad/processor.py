from __future__ import annotations

import statistics
from dataclasses import dataclass

import pandas as pd

from config import FetchConfig, ScoringConfig


@dataclass
class StudioProfile:
    company_id: int
    name: str
    game_count: int
    success_rate: float
    avg_rating: float
    std_rating: float
    history: list[float]


def process(
    upcoming_raw: list[dict],
    history_by_studio: dict[int, list[dict]],
    company_names: dict[int, str],
    fetch_cfg: FetchConfig,
    scoring_cfg: ScoringConfig,
) -> tuple[pd.DataFrame, dict[int, StudioProfile]]:
    studio_profiles = _build_studio_profiles(
        history_by_studio, company_names, fetch_cfg, scoring_cfg
    )

    _img_base = "https://images.igdb.com/igdb/image/upload"

    rows = []
    for game in upcoming_raw:
        studio_id = _primary_studio(game)
        company_info = company_names.get(studio_id, {}) if studio_id else {}
        studio_name = company_info.get("name", "Desconhecido")
        studio_logo_url = company_info.get("logo_url")

        cover = game.get("cover")
        cover_url = (
            f"{_img_base}/t_cover_big/{cover['image_id']}.jpg"
            if cover else None
        )

        franchise_ratings = _franchise_ratings(game, upcoming_raw, history_by_studio)
        is_new_ip = not bool(game.get("franchises"))

        simultaneous = sum(
            1 for g in upcoming_raw
            if g["id"] != game["id"] and _primary_studio(g) == studio_id
        ) if studio_id else None

        studio_history: list[float] = []
        if studio_id and studio_id in studio_profiles:
            studio_history = studio_profiles[studio_id].history

        release_date = game.get("first_release_date")

        rows.append({
            "game_id": game["id"],
            "name": game.get("name", ""),
            "studio_id": studio_id,
            "studio": studio_name,
            "release_date": pd.to_datetime(release_date, unit="s", errors="coerce") if release_date else None,
            "hypes": game.get("hypes"),
            "is_new_ip": is_new_ip,
            "franchise_ratings": franchise_ratings,
            "studio_history": studio_history,
            "simultaneous_projects": simultaneous,
            "cover_url": cover_url,
            "studio_logo_url": studio_logo_url,
        })

    games_df = pd.DataFrame(rows)
    return games_df, studio_profiles


def _primary_studio(game: dict) -> int | None:
    involved = game.get("involved_companies")
    if not involved:
        return None
    first = involved[0]
    if isinstance(first, dict):
        return first.get("company")
    return first


def _build_studio_profiles(
    history_by_studio: dict[int, list[dict]],
    company_names: dict[int, dict],
    fetch_cfg: FetchConfig,
    cfg: ScoringConfig,
) -> dict[int, StudioProfile]:
    profiles: dict[int, StudioProfile] = {}

    for company_id, games in history_by_studio.items():
        ratings = [
            g["total_rating"]
            for g in games
            if g.get("total_rating") is not None
            and (g.get("total_rating_count") or 0) >= fetch_cfg.min_rating_count
        ]

        if len(ratings) < cfg.min_studio_games:
            continue

        success_rate = sum(1 for r in ratings if r >= cfg.success_threshold) / len(ratings)
        avg_rating = statistics.mean(ratings)
        std_rating = statistics.stdev(ratings) if len(ratings) >= 2 else 0.0

        name = company_names.get(company_id, {}).get("name", "Desconhecido")

        profiles[company_id] = StudioProfile(
            company_id=company_id,
            name=name,
            game_count=len(ratings),
            success_rate=success_rate,
            avg_rating=avg_rating,
            std_rating=std_rating,
            history=ratings,
        )

    return profiles


def _franchise_ratings(
    game: dict,
    all_upcoming: list[dict],
    history_by_studio: dict[int, list[dict]],
) -> list[tuple[float, int | None]]:
    franchise_ids = set(game.get("franchises") or [])
    if not franchise_ids:
        return []

    studio_id = _primary_studio(game)
    history = history_by_studio.get(studio_id, []) if studio_id else []

    return [
        (g["total_rating"], g.get("first_release_date"))
        for g in history
        if g.get("total_rating") is not None
        and franchise_ids.intersection(g.get("franchises") or [])
    ]
