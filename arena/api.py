"""OthelloArena の REST API (自作プログラムが使うものだけ)。

座標は [x, y] (x = 列・左から、y = 行・上から)、盤面は board[y][x]。黒 -1 / 白 1 / 空き 0。
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from . import net


class ArenaApi:
    def __init__(self, api_url: str, token: str | None = None):
        self.api_url = api_url
        self.token = token

    def _url(self, path: str) -> str:
        return self.api_url + path

    # --- サインイン (デバイスフロー。認証なし) ---

    def device_code(self) -> dict[str, Any]:
        """{"deviceCode", "userCode", "expiresIn", "interval"}"""
        return net.request("POST", self._url("/auth/device/code"))

    def device_token(self, device_code: str) -> dict[str, Any]:
        """承認済みなら {"token", "expiresIn"}。まだなら ApiError(400, body={"error": "authorization_pending"...})。"""
        return net.request("POST", self._url("/auth/device/token"), body={"deviceCode": device_code})

    # --- 対局 ---

    def me_room(self) -> dict[str, Any]:
        """参加中のルーム {"roomId", "seat"}。無ければ roomId "" / seat 0。seat は 1 = 黒、2 = 白。"""
        return net.request("GET", self._url("/me/room"), token=self.token)

    def ready(self, room_id: str) -> dict[str, Any]:
        return net.request("POST", self._url(f"/games/{quote(room_id)}/ready"), token=self.token)

    def state(self, room_id: str) -> dict[str, Any]:
        """{"board", "legalMoves", "turn", "ready1", "ready2", "result"?, "version"}。turn は -1 / 1 / 0 = 終局。"""
        return net.request("GET", self._url(f"/games/{quote(room_id)}/state"))

    def play(self, room_id: str, move: list[int]) -> dict[str, Any]:
        """{"board", "legalMoves", "turn", "passed", "result"?, "version", "room"}"""
        return net.request("POST", self._url(f"/games/{quote(room_id)}/play"), token=self.token, body={"move": move})
