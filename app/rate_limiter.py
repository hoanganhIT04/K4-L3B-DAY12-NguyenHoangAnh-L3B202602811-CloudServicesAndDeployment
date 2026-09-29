"""CP3 — Rate limiting bằng thuật toán sliding window.

Đếm số request trong 60 giây gần nhất (cửa sổ trượt).
"""

from __future__ import annotations

import time
import uuid

from fastapi import HTTPException, status

WINDOW_SECONDS = 60


class RateLimiter:
    def __init__(self, client, limit_per_minute: int) -> None:
        self.client = client
        self.limit = limit_per_minute

    @staticmethod
    def _key(user_id: str) -> str:
        """Mỗi user một key riêng."""
        return f"ratelimit:{user_id}"

    def hit_count(self, user_id: str, now: float | None = None) -> int:
        """Số request của user trong WINDOW_SECONDS giây gần nhất."""

        now = now if now is not None else time.time()

        key = self._key(user_id)

        # Xóa các request đã cũ hơn cửa sổ 60 giây
        self.client.zremrangebyscore(
            key,
            0,
            now - WINDOW_SECONDS,
        )

        # Đếm số request còn lại trong cửa sổ
        return self.client.zcard(key)

    def check(self, user_id: str, now: float | None = None) -> None:
        """Cho qua nếu còn quota, ngược lại raise 429."""

        now = now if now is not None else time.time()

        # Kiểm tra trước khi ghi nhận request
        count = self.hit_count(user_id, now)

        if count >= self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="rate limit exceeded",
                headers={
                    "Retry-After": str(WINDOW_SECONDS),
                },
            )

        # Member phải unique để các request cùng timestamp
        # không ghi đè lên nhau
        key = self._key(user_id)

        member = f"{now}:{uuid.uuid4().hex}"

        self.client.zadd(
            key,
            {member: now},
        )

        # Tự động dọn key sau 60 giây
        self.client.expire(
            key,
            WINDOW_SECONDS,
        )