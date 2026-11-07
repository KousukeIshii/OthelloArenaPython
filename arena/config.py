"""接続先などの設定。

既定は本番 (https://tdu-othello.com)。環境変数かコマンドライン引数で上書きできる。

    OTHELLO_BASE_URL  API のあるサーバー (例: ローカルの backend なら http://127.0.0.1:8080)
    OTHELLO_SITE_URL  サインインの承認ページを開くサイト (省略時は OTHELLO_BASE_URL と同じ。
                      ローカルで web を vite で動かしているなら http://localhost:5173)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_BASE_URL = "https://tdu-othello.com"

# サインインで受け取ったトークンの保存先 (このリポジトリの直下。.gitignore 済み)
TOKEN_PATH = Path(__file__).resolve().parent.parent / ".othello_token.json"


@dataclass(frozen=True)
class Config:
    base_url: str  # 例: https://tdu-othello.com (末尾の / なし)
    site_url: str  # 承認ページ <site_url>/device?code=... のサイト

    @property
    def api_url(self) -> str:
        return self.base_url + "/api"


def load_config(base_url: str | None = None, site_url: str | None = None) -> Config:
    base = (base_url or os.environ.get("OTHELLO_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    site = (site_url or os.environ.get("OTHELLO_SITE_URL") or base).rstrip("/")
    return Config(base_url=base, site_url=site)
