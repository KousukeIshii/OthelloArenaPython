"""標準ライブラリ (urllib) だけで JSON の API を呼ぶ薄いラッパー。"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

USER_AGENT = "OthelloArenaPython/2.0"


class ApiError(Exception):
    """サーバーが 2xx 以外を返した。message はサーバーの文言 (あれば)。"""

    def __init__(self, status: int, message: str, body: Any = None):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.message = message
        self.body = body if isinstance(body, dict) else {}


class Unauthorized(ApiError):
    """401。トークンが無効・期限切れ。サインインし直す。"""


class NetworkError(Exception):
    """サーバーに届かない (接続できない・タイムアウト)。時間をおいて再試行できる。"""


def request(method: str, url: str, *, token: str | None = None, body: Any = None, timeout: float = 15) -> Any:
    """リクエストを送り、応答の JSON を返す (本文が無ければ None)。"""
    data = None
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return _parse(res.read())
    except urllib.error.HTTPError as e:
        payload = _parse(e.read())
        message = payload.get("message", "") if isinstance(payload, dict) else ""
        cls = Unauthorized if e.code == 401 else ApiError
        raise cls(e.code, message or e.reason or "", payload) from None
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        reason = getattr(e, "reason", e)
        raise NetworkError(f"{url} に接続できません: {reason}") from None


def _parse(raw: bytes) -> Any:
    if not raw:
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
