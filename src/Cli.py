from datetime import datetime, timedelta

from src.utils import *
from src.config import *


def main(since=None, until=None, root_path=".", channel_name="all_share", weeks: int = None):

    # 検索する日時範囲の初期化
    if until is None:
        until = datetime.now()
    if weeks is not None:
        weeks_num = int(weeks) if (type(weeks) is str) else weeks
        td = timedelta(weeks=weeks_num)
        since = until - td
    if since is None:
        since = datetime.fromisoformat(DEFAULT_SINCE)

    files = run(since, until, root_path, channel_name)

    file_download(files, root_path)


def print_list(line=False):
    r"""チャンネル一覧をターミナルに出力

	Args:
		line (bool, optional): チャンネル名を改行('\n')区切りで出力. デフォルト: 空白('  ')区切り.
	"""
    sep = "\n" if line else "  "

    channel_list = get_channel_list()
    for channel_name in channel_list.keys():
        print(channel_name, end=sep)


def latest():
    """ all_shareから直近の日付の輪講資料をダウンロードするメソッド """
    since = until = datetime.now()
    td = timedelta(weeks=1)
    thread_msgs = []

    # 1週間毎に遡って「資料置き場」を検索する (最大12週間前迄)
    for _ in range(MAX_WEEKS):
        until = since
        since = until - td

        messages = get_history(since=since, until=until)

        if messages != []:
            for msg in messages:
                if KEYWORD in msg["text"]:
                    thread_msgs = get_threads_all(messages=[msg])
                    break
            if thread_msgs != []:
                break
    files = get_file_url(thread_messages=thread_msgs)

    file_download(files)

