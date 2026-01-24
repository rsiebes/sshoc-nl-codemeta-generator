"""Generic API rate limiter for respecting rate limits across different APIs."""

import time
from typing import Dict, Optional, Tuple
from collections import deque

from .logger import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Generic rate limiter that works with any API."""

    # Common API rate limit configurations
    API_CONFIGS = {
        "github": {
            "requests_per_hour": 60,  # Unauthenticated
            "description": "GitHub API (unauthenticated)",
        },
        "pypi": {
            "requests_per_second": 1,
            "description": "PyPI API",
        },
        "npm": {
            "requests_per_second": 10,
            "description": "npm Registry API",
        },
        "maven": {
            "requests_per_second": 5,
            "description": "Maven Central Repository API",
        },
    }

    def __init__(
        self,
        api_name: str = "generic",
        wait_on_limit: bool = True,
        initial_delay: float = 1.0,
        delay_increment: float = 1.0,
        max_delay: float = 30.0,
    ):
        """
        Initialize the rate limiter.

        Args:
            api_name: Name of the API (used for configuration lookup)
            wait_on_limit: If True, wait when rate limit is hit; if False, raise error
            initial_delay: Initial delay in seconds for linear backoff
            delay_increment: Increment per retry in seconds
            max_delay: Maximum delay cap in seconds
        """
        self.api_name = api_name
        self.wait_on_limit = wait_on_limit
        self.initial_delay = initial_delay
        self.delay_increment = delay_increment
        self.max_delay = max_delay

        # Request tracking (memory-only)
        self.request_times: Dict[str, deque] = {}
        self.rate_limit_info: Dict[str, Dict] = {}
        self.retry_count: Dict[str, int] = {}

        logger.debug(
            f"RateLimiter initialized for {api_name}: "
            f"wait_on_limit={wait_on_limit}, "
            f"backoff={initial_delay}s initial, +{delay_increment}s per retry, max {max_delay}s"
        )

    def wait_if_needed(self, endpoint: str = "default") -> None:
        """
        Wait if necessary to respect rate limits.

        Args:
            endpoint: API endpoint identifier (for tracking separate limits)

        Raises:
            RuntimeError: If rate limit exceeded and wait_on_limit is False
        """
        if endpoint not in self.request_times:
            self.request_times[endpoint] = deque()
            self.retry_count[endpoint] = 0

        # Check if rate limit is exceeded
        if self._is_rate_limited(endpoint):
            retry_count = self.retry_count[endpoint]
            delay = min(
                self.initial_delay + (retry_count * self.delay_increment),
                self.max_delay,
            )

            if not self.wait_on_limit:
                raise RuntimeError(
                    f"Rate limit exceeded for {self.api_name}/{endpoint}. "
                    f"Would need to wait {delay}s. Use --wait-on-rate-limit to wait automatically."
                )

            logger.warning(
                f"Rate limit hit for {self.api_name}/{endpoint}. "
                f"Waiting {delay}s (retry #{retry_count + 1})"
            )
            time.sleep(delay)
            self.retry_count[endpoint] += 1

        # Record this request
        self.request_times[endpoint].append(time.time())

    def record_request(self, endpoint: str = "default", response_headers: Optional[Dict] = None) -> None:
        """
        Record a request and extract rate limit info from response headers.

        Args:
            endpoint: API endpoint identifier
            response_headers: HTTP response headers (may contain rate limit info)
        """
        if endpoint not in self.request_times:
            self.request_times[endpoint] = deque()

        # Extract rate limit info from common header patterns
        if response_headers:
            self._extract_rate_limit_info(endpoint, response_headers)

    def _extract_rate_limit_info(self, endpoint: str, headers: Dict) -> None:
        """
        Extract rate limit information from response headers.

        Args:
            endpoint: API endpoint identifier
            headers: HTTP response headers
        """
        # GitHub API headers
        if "X-RateLimit-Limit" in headers:
            self.rate_limit_info[endpoint] = {
                "limit": int(headers.get("X-RateLimit-Limit", 0)),
                "remaining": int(headers.get("X-RateLimit-Remaining", 0)),
                "reset": int(headers.get("X-RateLimit-Reset", 0)),
                "source": "github",
            }
            logger.debug(
                f"GitHub rate limit for {endpoint}: "
                f"{self.rate_limit_info[endpoint]['remaining']}/{self.rate_limit_info[endpoint]['limit']}"
            )

        # Generic rate limit headers
        elif "RateLimit-Limit" in headers:
            self.rate_limit_info[endpoint] = {
                "limit": int(headers.get("RateLimit-Limit", 0)),
                "remaining": int(headers.get("RateLimit-Remaining", 0)),
                "reset": int(headers.get("RateLimit-Reset", 0)),
                "source": "generic",
            }

    def _is_rate_limited(self, endpoint: str) -> bool:
        """
        Check if rate limit is exceeded based on tracked requests.

        Args:
            endpoint: API endpoint identifier

        Returns:
            True if rate limited, False otherwise
        """
        # Get rate limit config for this API
        config = self.API_CONFIGS.get(self.api_name, {})

        # If no config, allow requests (auto-detect mode)
        if not config:
            return False

        # Check requests per second limit
        if "requests_per_second" in config:
            limit = config["requests_per_second"]
            window = 1.0  # 1 second window
            cutoff_time = time.time() - window

            # Remove old requests outside the window
            while self.request_times[endpoint] and self.request_times[endpoint][0] < cutoff_time:
                self.request_times[endpoint].popleft()

            if len(self.request_times[endpoint]) >= limit:
                return True

        # Check requests per hour limit
        if "requests_per_hour" in config:
            limit = config["requests_per_hour"]
            window = 3600.0  # 1 hour window
            cutoff_time = time.time() - window

            # Remove old requests outside the window
            while self.request_times[endpoint] and self.request_times[endpoint][0] < cutoff_time:
                self.request_times[endpoint].popleft()

            if len(self.request_times[endpoint]) >= limit:
                return True

        return False

    def get_status(self, endpoint: str = "default") -> Dict:
        """
        Get current rate limit status.

        Args:
            endpoint: API endpoint identifier

        Returns:
            Dictionary with rate limit status
        """
        status = {
            "api": self.api_name,
            "endpoint": endpoint,
            "requests_tracked": len(self.request_times.get(endpoint, [])),
            "retry_count": self.retry_count.get(endpoint, 0),
            "wait_on_limit": self.wait_on_limit,
        }

        if endpoint in self.rate_limit_info:
            status["rate_limit_info"] = self.rate_limit_info[endpoint]

        return status

    def reset(self, endpoint: Optional[str] = None) -> None:
        """
        Reset rate limiter state.

        Args:
            endpoint: Specific endpoint to reset, or None to reset all
        """
        if endpoint:
            if endpoint in self.request_times:
                self.request_times[endpoint].clear()
            if endpoint in self.retry_count:
                self.retry_count[endpoint] = 0
            logger.debug(f"Reset rate limiter for {self.api_name}/{endpoint}")
        else:
            self.request_times.clear()
            self.retry_count.clear()
            logger.debug(f"Reset all rate limiters for {self.api_name}")
