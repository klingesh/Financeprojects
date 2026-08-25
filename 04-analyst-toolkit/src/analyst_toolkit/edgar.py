"""SEC EDGAR XBRL client.

Uses ``urllib`` from the standard library rather than ``requests`` so the
toolkit has no install step.

SEC access rules that this client respects:
  * A descriptive ``User-Agent`` including contact information is mandatory.
    Requests without one are refused.
  * Traffic is capped at 10 requests/second. A conservative delay is applied.

Set your contact string before making live calls::

    export SEC_USER_AGENT="Your Name your.email@example.com"
"""

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

REQUEST_DELAY_SECONDS = 0.15  # ~6.7 req/s, comfortably inside the SEC limit
DEFAULT_TIMEOUT = 30


class EdgarError(RuntimeError):
    """Raised when EDGAR cannot satisfy a request."""


def _user_agent() -> str:
    ua = os.environ.get("SEC_USER_AGENT", "").strip()
    if not ua:
        raise EdgarError(
            "SEC_USER_AGENT is not set. The SEC requires a descriptive User-Agent "
            "with contact details for all API access.\n\n"
            '  export SEC_USER_AGENT="Your Name your.email@example.com"\n\n'
            "To work without network access, use --offline to run from the "
            "bundled fixtures in data/sample/."
        )
    return ua


def _get_json(url: str) -> Dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": _user_agent(),
            "Accept-Encoding": "gzip, deflate",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
            payload = response.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            raise EdgarError(
                "EDGAR returned 403 Forbidden. This almost always means the "
                "User-Agent was rejected. Use a real name and email address."
            ) from exc
        if exc.code == 404:
            raise EdgarError("EDGAR returned 404 Not Found for {0}".format(url)) from exc
        if exc.code == 429:
            raise EdgarError(
                "EDGAR returned 429 Too Many Requests. Slow down and retry; "
                "consider enabling the local cache."
            ) from exc
        raise EdgarError("EDGAR HTTP {0} for {1}".format(exc.code, url)) from exc
    except urllib.error.URLError as exc:
        raise EdgarError(
            "Could not reach EDGAR ({0}). If you have no network access, "
            "use --offline.".format(exc.reason)
        ) from exc

    time.sleep(REQUEST_DELAY_SECONDS)
    return json.loads(payload.decode("utf-8"))


class EdgarClient:
    """Fetches company facts from EDGAR, with an optional on-disk cache."""

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir
        self._ticker_to_cik: Optional[Dict[str, str]] = None
        if cache_dir and not os.path.isdir(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)

    # -- ticker resolution -------------------------------------------------

    def _load_ticker_map(self) -> Dict[str, str]:
        if self._ticker_to_cik is not None:
            return self._ticker_to_cik

        cache_path = None
        if self.cache_dir:
            cache_path = os.path.join(self.cache_dir, "company_tickers.json")
            if os.path.isfile(cache_path):
                with open(cache_path, "r", encoding="utf-8") as handle:
                    raw = json.load(handle)
                self._ticker_to_cik = self._parse_ticker_map(raw)
                return self._ticker_to_cik

        raw = _get_json(TICKER_MAP_URL)
        if cache_path:
            with open(cache_path, "w", encoding="utf-8") as handle:
                json.dump(raw, handle)
        self._ticker_to_cik = self._parse_ticker_map(raw)
        return self._ticker_to_cik

    @staticmethod
    def _parse_ticker_map(raw: Dict[str, Any]) -> Dict[str, str]:
        """EDGAR returns a dict keyed by row index, not by ticker."""
        mapping = {}
        for entry in raw.values():
            ticker = str(entry.get("ticker", "")).upper()
            cik = str(entry.get("cik_str", "")).zfill(10)
            if ticker:
                mapping[ticker] = cik
        return mapping

    def resolve_cik(self, ticker: str) -> str:
        mapping = self._load_ticker_map()
        cik = mapping.get(ticker.upper())
        if cik is None:
            raise EdgarError(
                "Ticker {0!r} not found in the EDGAR ticker map. Note that "
                "non-US issuers (for example Indian listed companies) do not "
                "file with the SEC and are not available here.".format(ticker)
            )
        return cik

    # -- company facts -----------------------------------------------------

    def fetch_companyfacts(self, ticker: str) -> Dict[str, Any]:
        """Fetch the full companyfacts payload for a ticker."""
        cache_path = None
        if self.cache_dir:
            cache_path = os.path.join(
                self.cache_dir, "companyfacts_{0}.json".format(ticker.upper())
            )
            if os.path.isfile(cache_path):
                with open(cache_path, "r", encoding="utf-8") as handle:
                    return json.load(handle)

        cik = self.resolve_cik(ticker)
        payload = _get_json(COMPANYFACTS_URL.format(cik=cik))

        if cache_path:
            with open(cache_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle)
        return payload


class OfflineClient:
    """Serves companyfacts payloads from local fixtures.

    Lets the whole pipeline be exercised and tested with no network access.
    """

    def __init__(self, fixture_dir: str):
        self.fixture_dir = fixture_dir

    def fetch_companyfacts(self, ticker: str) -> Dict[str, Any]:
        path = os.path.join(
            self.fixture_dir, "companyfacts_{0}.json".format(ticker.upper())
        )
        if not os.path.isfile(path):
            raise EdgarError(
                "No offline fixture for {0!r} at {1}. Available fixtures: {2}".format(
                    ticker, path, ", ".join(sorted(self.available())) or "none"
                )
            )
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def available(self):
        if not os.path.isdir(self.fixture_dir):
            return []
        return [
            name[len("companyfacts_"):-len(".json")]
            for name in os.listdir(self.fixture_dir)
            if name.startswith("companyfacts_") and name.endswith(".json")
        ]
