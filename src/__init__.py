import fire

import src.Cli as cui
import src.Application as gui


def run():
    # help表示の設定
    fire.core.Display = lambda lines, out: print(*lines, file=out)

    # サブコマンドの設定
    fire.Fire(
        {"list": cui.print_list, "all": cui.main, "dl": cui.latest, "gui": gui.main,}
    )


if __name__ == "__main__":
    run()
