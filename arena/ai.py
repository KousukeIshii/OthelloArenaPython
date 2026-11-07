"""AI (get_action を持つ .py ファイル) の読み込みと呼び出し。"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Callable

GetAction = Callable[[list, list], list]

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


class InvalidAction(Exception):
    """AI が合法手でない手を返した。"""


def load_ai(spec: str) -> GetAction:
    """.py ファイルのパスから get_action を読み込む。"""
    path = Path(spec)
    if not path.is_file() and not path.is_absolute():
        path = _PROJECT_ROOT / spec  # 別のフォルダから実行されたときは、このリポジトリの直下を探す
    if not path.is_file():
        raise SystemExit(f"AI のファイルが見つかりません: {spec}")
    module_spec = importlib.util.spec_from_file_location(f"user_ai_{path.stem}", path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    fn = getattr(module, "get_action", None)
    if not callable(fn):
        raise SystemExit(f"{spec} に get_action(board, moves) 関数がありません。")
    return fn


def call_ai(get_action: GetAction, board: list[list[int]], moves: list[list[int]], color: int) -> list[int]:
    """盤面を「自分 = 1」にそろえて AI に渡し、返ってきた手を確かめて [x, y] で返す。

    盤面と合法手はコピーを渡すので、AI が書き換えても元には影響しない。
    合法手でなければ InvalidAction (サーバーに送ると反則負けになるため、送らずに止める)。
    """
    oriented = [[cell * color for cell in row] for row in board]
    action = get_action(oriented, [list(m) for m in moves])
    try:
        move = [int(action[0]), int(action[1])]
        if len(action) != 2:
            raise ValueError
    except (TypeError, ValueError, IndexError):
        raise InvalidAction(f"get_action の戻り値が [x, y] の形ではありません: {action!r}") from None
    if move not in [list(m) for m in moves]:
        raise InvalidAction(f"合法手ではない手が返されました: {move} (合法手: {moves})")
    return move
