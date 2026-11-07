# OthelloArenaPython

[OthelloArena](https://tdu-othello.com) で自作のオセロ AI を対戦させるための Python クライアントです。

- 必要なもの: Python 3.9 以上だけ（標準ライブラリしか使わないので `pip install` は不要です）
- 編集するのは **`my_ai.py` だけ** です。サーバーとの接続は `play.py` と `arena/` が受け持ちます。

## ファイル構成

```
my_ai.py   ★ あなたの AI (get_action を書き換える)
play.py    オンライン対戦を始める
arena/     サーバーとの接続 (編集不要)
```

## AI の書き方

`my_ai.py` の `get_action(board, moves)` を書き換えます。

```python
def get_action(board, moves):
    # board: board[y][x]。自分の石 = 1、相手の石 = -1、空き = 0
    # moves: 打てる場所の一覧 [[x, y], ...]  (x = 列・左から, y = 行・上から)
    return moves[0]  # moves の中から 1 つを返す
```

- 黒番でも白番でも、盤面は **自分の石が 1** になるようにそろえて渡されます。
- `moves` に無い手を返すと、サーバーには送らずに停止します（送ると反則負けになるため）。

## 対戦する

1. ブラウザで OthelloArena にサインインし、ルームを作成するか、ルームに入ります。
   自作プログラムと自分で対戦するときは、作成時のモードを「自作プログラム」にします（ブラウザが黒、プログラムが白）。
2. `python play.py` を実行します。
   - 初回はサインインの承認を求められます。表示されたページをブラウザで開き、コードを確かめて「許可する」を押してください。
     ブラウザが自動で開かない環境 (Google Colab・SSH 先など) では、表示された URL を手で開きます。
   - 受け取ったトークンは `.othello_token.json` に保存され、10 日間は承認なしで使えます。
3. プログラムが準備完了を送ります。ブラウザ側でも準備完了を押すと対局が始まり、あとは自動で打ちます。

```sh
python play.py --ai other_ai.py   # 別のファイルの AI で対戦
python play.py --logout           # 保存済みのトークンを消す
```

### 接続先を変える (開発用)

| 指定 | 環境変数 | 既定 |
|---|---|---|
| `--base-url` | `OTHELLO_BASE_URL` | `https://tdu-othello.com` |
| `--site-url` (承認ページのサイト) | `OTHELLO_SITE_URL` | `--base-url` と同じ |

ローカルの backend (`docker compose up`) に繋ぐ例:

```sh
python play.py --base-url http://127.0.0.1:8080 --site-url http://localhost:5173
```
