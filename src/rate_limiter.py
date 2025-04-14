import time
from threading import Lock

class RateLimiter:
    def __init__(self, max_requests: int, refill_interval: float = 1.0):
        """
        :param max_requests: Number of tokens (requests) allowed per interval.
        :param refill_interval: Time in seconds after which tokens are refilled.
        """
        self.max_tokens = max_requests
        self.tokens = max_requests
        self.refill_interval = refill_interval
        self.last_refill = time.time()
        self.lock = Lock()

    def acquire(self):
        """Blocks until a token is available, then consumes one."""
        while True:
            with self.lock:
                now = time.time()
                elapsed = now - self.last_refill

                # Refill logic
                if elapsed >= self.refill_interval:
                    refill_count = int(elapsed / self.refill_interval)
                    self.tokens = min(self.max_tokens, self.tokens + refill_count)
                    self.last_refill = now

                if self.tokens > 0:
                    self.tokens -= 1
                    return  # Token acquired

            # Wait briefly before retrying
            time.sleep(0.1)
