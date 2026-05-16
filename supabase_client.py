from __future__ import annotations
 
from functools import lru_cache
from typing import Any
 
import requests
 
 
class _SupabaseRESTResponse:
    def __init__(self, data: Any):
        self.data = data
 
 
class _SupabaseQueryBuilder:
    def __init__(
        self,
        table: str,
        http: requests.Session,
        url: str,
        api_key: str,
    ):
        self._table = table
        self._http = http
        self._url = url.rstrip("/")
        self._api_key = api_key
 
        self._select: str | None = None
        self._method: str | None = None
        self._payload: dict[str, Any] | None = None
 
    def select(self, columns: str) -> "_SupabaseQueryBuilder":
        self._select = columns
        return self
 
    def insert(self, payload: dict[str, Any]) -> "_SupabaseQueryBuilder":
        self._payload = payload
        return self
 
    def execute(self) -> _SupabaseRESTResponse:
        """Execute the prepared query.
 
        Supported operations (the only ones used in this repo):
        - select(...).execute() (reads)   — paginated, fetches all rows
        - insert(...).execute() (writes)
        """
        # ── Writes ────────────────────────────────────────────────────────────
        if self._payload is not None:
            endpoint = f"{self._url}/rest/v1/{self._table}"
            r = self._http.post(
                endpoint,
                json=[self._payload],
                headers={
                    "apikey": self._api_key,
                    "Authorization": f"Bearer {self._api_key}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                },
                timeout=30,
            )
            r.raise_for_status()
            return _SupabaseRESTResponse(r.json())
 
        # ── Reads (paginated) ─────────────────────────────────────────────────
        if self._select is None:
            raise ValueError("select(...) must be called before execute()")
 
        endpoint  = f"{self._url}/rest/v1/{self._table}"
        page_size = 1000
        offset    = 0
        all_rows: list[dict[str, Any]] = []
 
        read_headers = {
            "apikey": self._api_key,
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
        }
 
        while True:
            r = self._http.get(
                endpoint,
                params={
                    "select": self._select,
                    "limit":  page_size,
                    "offset": offset,
                },
                headers=read_headers,
                timeout=30,
            )
            r.raise_for_status()
            page = r.json()
            all_rows.extend(page)
 
            # Supabase returns fewer rows than page_size on the last page
            if len(page) < page_size:
                break
 
            offset += page_size
 
        return _SupabaseRESTResponse(all_rows)
 
    def __call__(self) -> _SupabaseRESTResponse:  # pragma: no cover
        return self.execute()
 
 
class _SupabaseRESTClient:
    def __init__(self, url: str, api_key: str):
        self._url = url
        self._api_key = api_key
        self._http = requests.Session()
 
    def table(self, table: str) -> "_SupabaseTable":
        return _SupabaseTable(table, self._http, self._url, self._api_key)
 
 
class _SupabaseTable(_SupabaseQueryBuilder):
    pass
 
 
@lru_cache(maxsize=1)
def get_supabase() -> Any:
    """Return a minimal Supabase REST client.
 
    Avoids the external `supabase` Python library so the app works on Python 3.14.
    Credentials are loaded from environment variables.
    Supports optional `.env` loading via `python-dotenv` (if installed).
    """
    import os
 
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
    except Exception:
        pass
 
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
 
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_KEY must be set as environment variables"
        )
 
    return _SupabaseRESTClient(SUPABASE_URL, SUPABASE_KEY)


