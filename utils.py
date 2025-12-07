from datetime import datetime

def str_to_datetime_standard(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

def datetime_to_ltt(dt: datetime) -> str:
    return dt.strftime("%a %b %d %H:%M:%S %Y")

def ltt_str_to_datetime(s: str) -> datetime:
    return datetime.strptime(s, "%a %b %d %H:%M:%S %Y")


