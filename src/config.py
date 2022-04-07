from slack_sdk import WebClient

SLACK_TOKEN = "" # Slakcワークスペースの認証トークン
DEFAULT_CHANNEL_ID = ""  # デフォルト対象のチャンネルID
KEYWORD = "資料置き場"
MAX_WEEKS = 12  # `slackcat dl`で遡るする週の上限
DEFAULT_SINCE = "2021-04-01"  # sinceが指定されていない時のデフォルト値 (ISO 8601形式)

client = WebClient(SLACK_TOKEN)
