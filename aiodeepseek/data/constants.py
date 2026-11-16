from __future__ import annotations

from typing import Dict

BASE_URL: str = "https://chat.deepseek.com"
COMPLETION_PATH: str = "/api/v0/chat/completion"
UPLOAD_PATH: str = "/api/v0/file/upload_file"

HEADERS: Dict[str, str] = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "DeepSeek/2 CFNetwork/3826.400.12 Darwin/24.3.0",
    "x-client-platform": "ios",
    "x-client-version": "2.8.0",
    "x-client-bundle-id": "com.deepseek.chat",
    "x-client-locale": "en_US",
    "x-client-timezone-offset": "0",
    "Origin": "https://chat.deepseek.com",
    "Priority": "u=0",
    "Referer": "https://chat.deepseek.com/",
}
