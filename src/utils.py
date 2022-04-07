# 共通のメソッドをまとめます
# 詳しくは https://qiita.com/msi/items/d91ea3900373ff8b09d7

import os
from datetime import datetime, date, time, timedelta
import sys

import pytz
import requests
from slack_sdk import WebClient
from tqdm import tqdm

from src.config import *

__all__ = [
    "get_channel_list",
    "get_channel_id",
    "get_history",
    "get_file_url",
    "get_threads_all",
    "file_download",
    "run",
]


def get_channel_list():
    """ チャンネルリストを取得 """

    channel_list = {}  # 辞書(key=チャンネル名, value=チャンネルID)
    try:
        conversations_list = client.conversations_list()
        channels_info = conversations_list["channels"]
        for channel in channels_info:
            channel_id = channel["id"]
            channel_name = channel["name"]
            channel_list[channel_name] = channel_id
    except Exception as e:
        print(e)

    return channel_list  # 出力例
    # { "all_share" : "C01RV07PV88",
    #   "group_時系列" : "C01UL0U5J69" }


def get_channel_id(channel_list, channel_name="all_share"):
    """ 指定したチャンネルのIDをリスト参照して返す """

    if channel_name not in channel_list.keys():
        # もしチャンネル名が登録されてなかったらdefaultとしてall_shareのIDを返す
        channel_id = DEFAULT_CHANNEL_ID
    else:
        channel_id = channel_list[channel_name]

    return channel_id


def get_history(since=None, until=None, channel_id=DEFAULT_CHANNEL_ID):
    """ all_shareのメッセージを取得 """

    # init timerange if not specified
    if since is None:
        since = datetime.fromisoformat(DEFAULT_SINCE)
    if until is None:
        until = datetime.datetime.now()

    oldest = format_to_timestamp(since)
    latest = format_to_timestamp(until)

    try:
        response = client.conversations_history(channel=channel_id, latest=latest, oldest=oldest)
    except Exception as e:
        print(e)

    return response["messages"]


def get_file_url(thread_messages, url=None):
    """ スレッド内メッセージのファイル名，ファイルURLを取得 """

    files = []
    for messages in thread_messages:
        for msg in messages:
            if "files" in msg.keys():
                for file in msg["files"]:
                    file_name = file["name"]
                    url = file["url_private_download"]
                    files.append((file_name, url))

    return files


def get_threads_all(messages, channel_id=DEFAULT_CHANNEL_ID):
    """ 取得したメッセージの中で，スレッド内の全てのメッセージをリストで取得 """

    thread_messages = []
    for message in messages:
        # text = message['text']
        # if keyword in text:
        thread_id = message["ts"]
        try:
            response = client.conversations_replies(channel=channel_id, ts=thread_id)
        except Exception as e:
            print(e)
        thread_messages.append(response["messages"])

    return thread_messages


def file_download(files, root_path="."):
    """ ファイルURLからダウンロード """

    headers = {"Authorization": "Bearer " + SLACK_TOKEN}

    pbar_total = tqdm(  # 全ファイルのプログレスバー (ファイル毎更新)
        total=len(files), desc="Download", unit="files", ncols=0, dynamic_ncols=True,
    )

    os.makedirs(root_path, exist_ok=True)

    for name, url in files:
        filename = os.path.join(root_path, name)

        if not os.path.exists(filename):  # 同じファイル名が既に存在する場合保存しない
            response = requests.get(url, headers=headers, stream=True)

            total_size = int(response.headers.get("content-length", 0))
            chunk_size = 1024
            pbar_each = tqdm(  # 各ファイルのプログレスバー (1kB毎更新)
                total=total_size, desc=name, unit="B", unit_scale=True, dynamic_ncols=True,
            )

            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size):
                    f.write(chunk)
                    pbar_each.update(chunk_size)

            pbar_each.close()

        pbar_total.update(1)

    pbar_total.close()


def format_to_timestamp(attr):
    if type(attr) is str:
        try:
            dt = datetime.strptime(attr, "%Y%m%d")
        except ValueError:
            print(f"[Error] 指定した日付({attr})の書式が不適切です. (正例: 20210401)")
            sys.exit(-1)
    elif type(attr) is not datetime:
        if type(attr) is int:
            tm = int_to_date(attr)
        else:
            tm = attr
        dt = datetime.combine(tm, time())
    else:
        dt = attr

    # timezone指定
    dt_tokyo = pytz.timezone("Asia/Tokyo").localize(dt)

    # datetime to timestamp
    ts = dt_tokyo.timestamp()
    return ts


def int_to_date(int_date):
    year = int(int_date / 10000)
    month = int((int_date % 10000) / 100)
    day = int_date % 100
    return date(year, month, day)


def run(since=None, until=None, root_path=".", channel_name="all_share"):
    """ ダウンロードまでの流れをまとめた """

    channel_list = get_channel_list()
    channel_id = get_channel_id(channel_list, channel_name)

    messages = get_history(since=since, until=until, channel_id=channel_id)

    thread_messages = get_threads_all(messages=messages, channel_id=channel_id)

    files = get_file_url(thread_messages=thread_messages)

    return files
