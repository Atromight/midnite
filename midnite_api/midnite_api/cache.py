from threading import Lock
from typing import Optional


class Cache:
    def __init__(self):
        self._lock = Lock()
        self._latest_t = None  # latest `t` seen

    def initialize(self, t: int):
        with self._lock:
            self._latest_t = t

    def get_latest_t(self) -> Optional[int]:
        with self._lock:
            return self._latest_t

    def update_latest_t(self, t: int):
        with self._lock:
            if self._latest_t is None or t > self._latest_t:
                self._latest_t = t

    def clear(self):
        with self._lock:
            self._latest_t = None


# Create a global cache instance to be used across your app
cache = Cache()
