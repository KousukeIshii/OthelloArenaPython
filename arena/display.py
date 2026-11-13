"""盤面のコンソール表示。

盤面は半角英数字の記号だけで描く (B = 黒、W = 白、- = 空き)。
「・」は全角、「●」「○」は環境によって 1 文字分にも 2 文字分にもなるため、使うと列がずれる。
"""

from __future__ import annotations

BLACK, WHITE = -1, 1
STONES = {BLACK: "B", WHITE: "W"}
EMPTY_MARK = "-"
COLOR_NAMES = {BLACK: "黒(B)", WHITE: "白(W)"}


def color_name(color: int) -> str:
    return COLOR_NAMES.get(color, "?")


def format_board(board: list[list[int]]) -> str:
    """盤面を文字列にする。左に行番号 y、上に列番号 x。"""
    size = len(board)
    lines = ["   " + "".join(f"{x:>3}" for x in range(size))]
    for y, row in enumerate(board):
        lines.append(f"{y:>2} " + "".join(f"{STONES.get(cell, EMPTY_MARK):>3}" for cell in row))
    black = sum(row.count(BLACK) for row in board)
    white = sum(row.count(WHITE) for row in board)
    lines.append(f"   {color_name(BLACK)} {black}  {color_name(WHITE)} {white}")
    return "\n".join(lines)


def print_board(board: list[list[int]]) -> None:
    print(format_board(board))
