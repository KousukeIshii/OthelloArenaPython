"""オンライン対戦の流れ。

    サインイン → 参加中のルームと席 (GET /api/me/room) → 準備完了 (POST ready)
    → 盤面をポーリング (GET state) → 自分の手番なら AI を呼んで着手 (POST play) → 終局
"""

from __future__ import annotations

import time

from . import auth
from .ai import GetAction, call_ai
from .api import ArenaApi
from .config import Config
from .display import color_name, print_board
from .net import ApiError, NetworkError, Unauthorized

ROOM_WAIT_INTERVAL = 3.0  # ルームに入るのを待つ間の問い合わせ間隔 (秒)
MAX_NETWORK_RETRIES = 5  # 通信エラーが続いたら諦める回数


class GameAborted(Exception):
    """対局を続けられない (ルームが消えた・backend が古いなど)。"""


class Runner:
    def __init__(self, config: Config, get_action: GetAction, poll_interval: float = 1.0):
        self.config = config
        self.get_action = get_action
        self.poll_interval = poll_interval
        self.api = ArenaApi(config.api_url)

    # --- 入口 ---

    def run(self) -> None:
        self.api.token = auth.get_token(self.config)
        room_id, color = self._wait_for_room()
        print(f"ルーム {room_id} に {color_name(color)} として参加します。")
        self._call(self.api.ready, room_id)
        self._play(room_id, color)

    # --- 各段階 ---

    def _wait_for_room(self) -> tuple[str, int]:
        notified = False
        while True:
            res = self._call(self.api.me_room)
            if "seat" not in res:
                raise GameAborted("サーバーが席 (seat) を返しませんでした。このクライアントに対応していない古いサーバーです。")
            room_id, seat = res.get("roomId") or "", res["seat"]
            if room_id and seat in (1, 2):
                return room_id, (-1 if seat == 1 else 1)
            if not notified:
                print("参加中のルームがありません。ブラウザでルームを作成するか、ルームに入ってください。(Ctrl+C で終了)")
                notified = True
            time.sleep(ROOM_WAIT_INTERVAL)

    def _play(self, room_id: str, color: int) -> None:
        shown_version = None  # 最後に表示した盤面の version
        acted_version = None  # 最後に AI を呼んだ盤面の version (同じ局面で 2 回打たない)
        waiting_notified = False
        while True:
            st = self._call(self.api.state, room_id)
            version = st.get("version")

            if not (st.get("ready1") and st.get("ready2")):
                if not waiting_notified:
                    print("相手の準備完了を待っています…")
                    waiting_notified = True
                time.sleep(self.poll_interval)
                continue

            if version != shown_version:
                self._show(st, color)
                shown_version = version

            if st.get("result") or st.get("turn") == 0:
                self._show_result(st.get("result"), color)
                return

            moves = st.get("legalMoves") or []
            if st.get("turn") == color and moves and version != acted_version:
                move = call_ai(self.get_action, st["board"], moves, color)
                acted_version = version
                print(f"着手: {move}")
                try:
                    res = self._call(self.api.play, room_id, move)
                except ApiError as e:
                    if e.status == 409:  # 手番の入れ替わりと行き違った。最新の盤面で判断し直す
                        print(f"着手が受け付けられませんでした: {e.message}")
                        continue
                    raise
                if res.get("passed"):
                    print("相手は打てる場所がないためパスです。")
                continue  # 打った直後は待たずに次の局面を取る (パスで続けて打つ場合がある)

            time.sleep(self.poll_interval)

    # --- 表示 ---

    def _show(self, st: dict, color: int) -> None:
        print()
        print_board(st["board"])
        turn = st.get("turn")
        if turn in (-1, 1):
            who = "あなた" if turn == color else "相手"
            print(f"手番: {color_name(turn)} ({who})")

    def _show_result(self, result: dict | None, color: int) -> None:
        print()
        if not result:
            print("対局が終了しました。")
            return
        winner = result.get("winner")
        black, white = result.get("black"), result.get("white")
        if winner == 0:
            outcome = "引き分け"
        elif winner == color:
            outcome = "あなたの勝ち"
        else:
            outcome = "あなたの負け"
        reason = "（反則）" if result.get("reason") == "illegal" else ""
        print(f"対局終了: {outcome}{reason}  黒 {black} - 白 {white}")

    # --- 通信 (401 はサインインし直し、通信エラーは再試行) ---

    def _call(self, fn, *args):
        failures = 0
        reauthed = False
        while True:
            try:
                return fn(*args)
            except Unauthorized:
                if reauthed:
                    raise
                print("サインインが無効になりました。もう一度サインインします。")
                auth.forget_token(self.config)
                self.api.token = auth.sign_in(self.config)
                reauthed = True
            except ApiError as e:
                if e.status == 404:
                    raise GameAborted(f"ルームが見つかりません (解散したか、期限が切れました)。{e.message}") from None
                if e.status >= 500 and failures < MAX_NETWORK_RETRIES:
                    failures += 1
                    time.sleep(min(2 ** failures, 30))
                    continue
                raise
            except NetworkError as e:
                if failures >= MAX_NETWORK_RETRIES:
                    raise
                failures += 1
                wait = min(2 ** failures, 30)
                print(f"{e} ({wait} 秒後に再試行します)")
                time.sleep(wait)


def run(config: Config, get_action: GetAction, poll_interval: float = 1.0) -> None:
    Runner(config, get_action, poll_interval).run()
