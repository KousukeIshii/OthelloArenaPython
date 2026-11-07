"""サインイン (デバイスフロー、RFC 8628) とクライアントトークンの保存。

1. サーバーからコードを受け取り、ブラウザで <サイト>/device?code=<コード> を開いてもらう
2. ブラウザで「許可する」が押されるまでサーバーに問い合わせる
3. 受け取ったトークン (10 日で失効) を .othello_token.json に保存し、次からはそれを使う
"""

from __future__ import annotations

import json
import time
import webbrowser
from urllib.parse import quote

from .api import ArenaApi
from .config import TOKEN_PATH, Config
from .net import ApiError

EXPIRY_MARGIN = 60  # 期限の少し前から切れたものとして扱う (秒)


class AuthError(Exception):
    """サインインできなかった (キャンセル・期限切れ)。"""


def get_token(config: Config) -> str:
    """保存済みのトークンを返す。無い・期限切れならサインインする。"""
    token = _load(config.base_url)
    if token:
        return token
    return sign_in(config)


def forget_token(config: Config) -> None:
    """保存済みのトークンを消す (401 が返ったとき)。"""
    data = _read_file()
    if data.pop(config.base_url, None) is not None:
        _write_file(data)


def sign_in(config: Config) -> str:
    api = ArenaApi(config.api_url)
    d = api.device_code()
    device_code, user_code = d["deviceCode"], d["userCode"]
    interval = max(1, int(d.get("interval", 5)))
    deadline = time.monotonic() + int(d.get("expiresIn", 600))
    url = f"{config.site_url}/device?code={quote(user_code)}"

    print("OthelloArena にサインインします。")
    print(f"  ブラウザで次のページを開き、コード {user_code} を確かめて「許可する」を押してください。")
    print(f"  {url}")
    try:
        webbrowser.open(url)
    except Exception:  # Colab や SSH 先などブラウザが無い環境では、上の URL を手で開いてもらう
        pass

    while time.monotonic() < deadline:
        time.sleep(interval)
        try:
            t = api.device_token(device_code)
        except ApiError as e:
            code = e.body.get("error")
            if code == "authorization_pending":
                continue
            if code == "slow_down":
                interval += 5
                continue
            if code in ("access_denied", "expired_token"):
                raise AuthError(e.message or code) from None
            raise
        token = t["token"]
        expires_at = time.time() + int(t.get("expiresIn", 0))
        _save(config.base_url, token, expires_at)
        print("サインインしました。")
        return token
    raise AuthError("サインインの期限が切れました。もう一度実行してください。")


# --- 保存 ({base_url: {"token", "expiresAt"}}。接続先ごとに分けて持つ) ---


def _load(base_url: str) -> str | None:
    entry = _read_file().get(base_url)
    if not isinstance(entry, dict):
        return None
    token, expires_at = entry.get("token"), entry.get("expiresAt", 0)
    if not token or time.time() > expires_at - EXPIRY_MARGIN:
        return None
    return token


def _save(base_url: str, token: str, expires_at: float) -> None:
    data = _read_file()
    data[base_url] = {"token": token, "expiresAt": int(expires_at)}
    _write_file(data)


def _read_file() -> dict:
    try:
        data = json.loads(TOKEN_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_file(data: dict) -> None:
    TOKEN_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
