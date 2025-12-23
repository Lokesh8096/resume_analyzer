import re
import requests
from io import BytesIO

FILE_ID_PATTERNS = [
    r"/d/([a-zA-Z0-9_-]+)",          # /d/<id>/...
    r"id=([a-zA-Z0-9_-]+)",          # ?id=<id>
    r"uc\?id=([a-zA-Z0-9_-]+)",      # uc?id=<id>
]


def _extract_file_id(link: str) -> str:
    for pattern in FILE_ID_PATTERNS:
        match = re.search(pattern, link)
        if match:
            return match.group(1)
    raise ValueError("Could not extract Google Drive file ID from link")


def download_drive_file(link: str) -> BytesIO:
    file_id = _extract_file_id(link)
    url = f"https://drive.google.com/uc?id={file_id}"
    response = requests.get(url, timeout=20)
    if response.status_code != 200:
        raise ValueError(f"Failed to download file (status {response.status_code})")
    return BytesIO(response.content)
