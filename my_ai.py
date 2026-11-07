"""あなたの AI。このファイルの get_action を書き換えてください。
"""

import random


def get_action(board, moves):
    """次の一手を返す。

    board: 盤面。board[y][x] で、自分の石 = 1、相手の石 = -1、空き = 0。
           (黒番でも白番でも、自分の石が 1 になるようにそろえて渡されます)
    moves: 今打てる場所の一覧。[[x, y], [x, y], ...]
           x は列 (左から 0, 1, 2, ...)、y は行 (上から 0, 1, 2, ...)。

    戻り値: moves の中の 1 つ ([x, y])。
    """
    # 見本: 合法手の中からランダムに選ぶ
    return random.choice(moves)
