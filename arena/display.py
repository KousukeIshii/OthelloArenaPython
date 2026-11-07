"""盤面のコンソール表示。"""

from __future__ import annotations

BLACK, WHITE = -1, 1
STONES = {BLACK: "●", WHITE: "○"}
EMPTY_MARK = "・"
COLOR_NAMES = {BLACK: "黒(●)", WHITE: "白(○)"}


def color_name(color: int) -> str:
    return COLOR_NAMES.get(color, "?")


def format_board(board: list[list[int]], last_move: list[int] | None = None) -> str:
    """盤面を文字列にする。左に行番号 y、上に列番号 x。直前の手は [ ] で囲む。"""
    size = len(board)
    lines = ["    " + " ".join(f"{x:>2}" for x in range(size))]
    for y, row in enumerate(board):
        cells = []
        for x, cell in enumerate(row):
            mark = STONES.get(cell, EMPTY_MARK)
            cells.append(f"[{mark}]" if last_move and [x, y] == list(last_move) else f" {mark}")
        lines.append(f"{y:>2}  " + "".join(c.ljust(3) for c in cells).rstrip())
    black = sum(row.count(BLACK) for row in board)
    white = sum(row.count(WHITE) for row in board)
    lines.append(f"    {STONES[BLACK]} {black}  {STONES[WHITE]} {white}")
    return "\n".join(lines)


def print_board(board: list[list[int]], last_move: list[int] | None = None) -> None:
    print(format_board(board, last_move))
