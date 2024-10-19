from datetime import datetime

def convert_timestamp_to_iso(airing_at: int):
    return datetime.fromtimestamp(airing_at).strftime("%Y-%m-%dT%H:%M:%S")
