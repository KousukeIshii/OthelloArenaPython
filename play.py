"""OthelloArena でオンライン対戦する。

    python play.py                    # my_ai.py の get_action で対戦
    python play.py --ai other_ai.py   # 別のファイルの AI で対戦

先にブラウザでルームを作成するか、ルームに入っておいてください。
初回はブラウザでのサインインの承認を求められます。
"""

from __future__ import annotations

import argparse
import sys

from arena import auth
from arena.ai import InvalidAction, load_ai
from arena.config import load_config
from arena.net import ApiError, NetworkError
from arena.runner import GameAborted, run


def main() -> int:
    parser = argparse.ArgumentParser(description="OthelloArena でオンライン対戦する")
    parser.add_argument("--ai", default="my_ai.py", help="get_action を書いた .py ファイル (既定: my_ai.py)")
    parser.add_argument("--base-url", help="接続先のサーバー (既定: https://tdu-othello.com。環境変数 OTHELLO_BASE_URL でも指定可)")
    parser.add_argument("--site-url", help="サインインの承認ページのサイト (既定: --base-url と同じ。環境変数 OTHELLO_SITE_URL)")
    parser.add_argument("--interval", type=float, default=1.0, help="盤面を問い合わせる間隔 (秒、既定 1.0)")
    parser.add_argument("--logout", action="store_true", help="保存済みのトークンを消して終了する")
    args = parser.parse_args()

    config = load_config(args.base_url, args.site_url)
    if args.logout:
        auth.forget_token(config)
        print("保存済みのトークンを消しました。")
        return 0

    get_action = load_ai(args.ai)
    try:
        run(config, get_action, max(0.5, args.interval))
    except KeyboardInterrupt:
        print("\n中断しました。")
        return 130
    except InvalidAction as e:
        print(f"\nAI のエラー: {e}\nサーバーには送らずに停止しました。")
        return 1
    except (GameAborted, auth.AuthError, NetworkError) as e:
        print(f"\n{e}")
        return 1
    except ApiError as e:
        print(f"\nサーバーがエラーを返しました (HTTP {e.status}): {e.message}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
