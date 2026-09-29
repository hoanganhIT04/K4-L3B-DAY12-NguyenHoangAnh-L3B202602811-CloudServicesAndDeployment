"""CP4 — Stateless: state sống ngoài process.

Nếu lịch sử hội thoại nằm trong một dict trong RAM, thì khi scale lên 3
instance, user hỏi câu 1 vào instance A và câu 2 vào instance B sẽ thấy agent
"mất trí nhớ". Vì vậy state phải nằm ở Redis.
"""

from __future__ import annotations

import json

import redis

from .config import get_settings

HISTORY_MAX_MESSAGES = 20
HISTORY_TTL_SECONDS = 7 * 24 * 3600


def get_redis_client(url: str | None = None):
    """Tạo client Redis từ URL."""

    url = url or get_settings().redis_url

    if url.startswith("fake://"):
        import fakeredis

        return fakeredis.FakeRedis(decode_responses=True)

    return redis.from_url(url, decode_responses=True)


class ConversationStore:
    """Lưu lịch sử hội thoại của từng user trong Redis List."""

    def __init__(self, client) -> None:
        self.client = client

    @staticmethod
    def _key(user_id: str) -> str:
        return f"history:{user_id}"

    def ping(self) -> bool:
        """Redis có trả lời không? Dùng cho endpoint /ready."""

        try:
            self.client.ping()
            return True
        except Exception:
            return False

    def append(self, user_id: str, role: str, content: str) -> None:
        """Ghi thêm một lượt vào lịch sử."""

        key = self._key(user_id)

        message = {
            "role": role,
            "content": content,
        }

        self.client.rpush(
            key,
            json.dumps(message, ensure_ascii=False),
        )

        # Chỉ giữ 20 message gần nhất
        self.client.ltrim(
            key,
            -HISTORY_MAX_MESSAGES,
            -1,
        )

        # Tự động hết hạn sau 7 ngày
        self.client.expire(
            key,
            HISTORY_TTL_SECONDS,
        )

    def get_history(self, user_id: str) -> list[dict]:
        """Đọc lịch sử hội thoại, cũ nhất trước."""

        key = self._key(user_id)

        messages = self.client.lrange(key, 0, -1)

        return [json.loads(message) for message in messages]

    def clear(self, user_id: str) -> None:
        """Xóa lịch sử của một user."""

        self.client.delete(self._key(user_id))