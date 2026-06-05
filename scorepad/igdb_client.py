from __future__ import annotations

import os
import time

import requests

from config import FetchConfig

_AUTH_URL = "https://id.twitch.tv/oauth2/token"
_BASE_URL = "https://api.igdb.com/v4"
_PAGE_SIZE = 500
_GAME_FIELDS = (
    "fields id,name,first_release_date,hypes,"
    "involved_companies.company,franchises,cover.image_id;"
)


class IGDBClient:
    def __init__(self, fetch_config: FetchConfig):
        self._cfg = fetch_config
        self._client_id = os.environ["IGDB_CLIENT_ID"]
        self._client_secret = os.environ["IGDB_CLIENT_SECRET"]
        self._token: str | None = None

    def authenticate(self) -> None:
        resp = requests.post(_AUTH_URL, params={
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "client_credentials",
        })
        resp.raise_for_status()
        self._token = resp.json()["access_token"]

    def _headers(self) -> dict:
        if not self._token:
            raise RuntimeError("Chame authenticate() antes de fazer queries.")
        return {
            "Client-ID": self._client_id,
            "Authorization": f"Bearer {self._token}",
        }

    def _query_once(self, endpoint: str, body: str) -> list[dict]:
        """Executa uma única requisição sem paginação automática."""
        resp = requests.post(
            f"{_BASE_URL}/{endpoint}", data=body, headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json() or []

    def _query(self, endpoint: str, body: str) -> list[dict]:
        """Executa query com paginação automática até esgotar os resultados."""
        url = f"{_BASE_URL}/{endpoint}"
        results: list[dict] = []
        offset = 0

        while True:
            paginated = f"{body}\nlimit {_PAGE_SIZE};\noffset {offset};"
            resp = requests.post(url, data=paginated, headers=self._headers())
            resp.raise_for_status()
            page = resp.json()

            if not page:
                break

            results.extend(page)
            offset += _PAGE_SIZE

            if len(page) < _PAGE_SIZE:
                break

            time.sleep(self._cfg.request_delay)

        return results

    def fetch_upcoming_games(
        self,
        limit: int | None = None,
        offset: int = 0,
        order_by: str = "hype",
    ) -> list[dict]:
        now = int(time.time())
        future_limit = now + self._cfg.max_future_days * 24 * 3600
        sort = "hypes desc" if order_by == "hype" else "first_release_date asc"
        n = limit or self._cfg.max_upcoming

        body = (
            f"{_GAME_FIELDS}"
            f"where hypes >= {self._cfg.min_hype}"
            f" & first_release_date > {now}"
            f" & first_release_date < {future_limit}"
            f" & involved_companies != null;"
            f"sort {sort};"
            f"limit {n};"
            f"offset {offset};"
        )
        return self._query_once("games", body)

    def search_game(self, name: str) -> list[dict]:
        now = int(time.time())
        future_limit = now + self._cfg.max_future_days * 24 * 3600
        body = (
            f'search "{name}";'
            f"{_GAME_FIELDS}"
            f"where involved_companies != null"
            f" & first_release_date > {now}"
            f" & first_release_date < {future_limit};"
            "limit 10;"
        )
        return self._query_once("games", body)

    def fetch_studio_history(self, company_id: int) -> list[dict]:
        now = int(time.time())
        body = (
            "fields id,name,first_release_date,total_rating,total_rating_count,franchises;"
            f"where involved_companies.company = {company_id}"
            f" & first_release_date < {now};"
            "sort first_release_date desc;"
            f"limit {self._cfg.max_history_per_studio};"
        )
        return self._query("games", body)

    def resolve_company_names(self, ids: list[int]) -> dict[int, dict]:
        if not ids:
            return {}

        id_list = ",".join(str(i) for i in ids)
        body = f"fields id,name,logo.image_id;\nwhere id = ({id_list});"
        companies = self._query("companies", body)

        result: dict[int, dict] = {}
        for c in companies:
            logo = c.get("logo")
            logo_url = (
                f"https://images.igdb.com/igdb/image/upload/t_logo_med/{logo['image_id']}.png"
                if logo else None
            )
            result[c["id"]] = {"name": c["name"], "logo_url": logo_url}
        return result
