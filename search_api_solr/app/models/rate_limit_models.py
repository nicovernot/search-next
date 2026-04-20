"""
Rate limiting data models and configuration structures.
"""
import json
from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


@dataclass
class RateLimit:
    """Rate limit configuration for a specific endpoint or client type."""
    requests: int  # Maximum requests allowed
    window_seconds: int  # Time window in seconds
    burst_multiplier: float = 1.0  # Allow burst up to this multiplier

    def __post_init__(self):
        """Validate rate limit configuration."""
        if self.requests <= 0:
            raise ValueError("requests must be positive")
        if self.window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        if self.burst_multiplier < 1.0:
            raise ValueError("burst_multiplier must be >= 1.0")


@dataclass
class RateLimitResult:
    """Result of rate limit check operation."""
    allowed: bool  # Whether request is allowed
    current_count: int  # Current request count
    limit: int  # Maximum allowed requests
    remaining: int  # Remaining requests in window
    reset_at: datetime  # When the window resets
    retry_after: int | None = None  # Seconds to wait if blocked

    def __post_init__(self):
        """Validate rate limit result."""
        if self.current_count < 0:
            raise ValueError("current_count cannot be negative")
        if self.limit <= 0:
            raise ValueError("limit must be positive")
        if self.remaining < 0:
            self.remaining = 0


class RateLimitConfig(BaseModel):
    """Pydantic model for rate limit configuration validation."""
    enabled: bool = Field(default=True, description="Enable rate limiting")
    default_requests: int = Field(default=100, description="Default requests per window")
    default_window: int = Field(default=60, description="Default window in seconds")
    burst_multiplier: float = Field(default=1.0, description="Burst multiplier")

    # Endpoint-specific limits (JSON string that gets parsed)
    endpoints: dict[str, RateLimit] = Field(default_factory=dict, description="Endpoint-specific limits")

    # Client type configuration
    authenticated_multiplier: float = Field(default=2.0, description="Multiplier for authenticated clients")
    ip_whitelist: list[str] = Field(default_factory=list, description="IP addresses to whitelist")

    # Backend configuration
    backend: str = Field(default="redis", description="Backend type (redis or memory)")
    redis_key_prefix: str = Field(default="rate_limit:", description="Redis key prefix")

    # Monitoring configuration
    log_violations: bool = Field(default=True, description="Log rate limit violations")
    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")

    @field_validator('default_requests', 'default_window')
    @classmethod
    def validate_positive(cls, v: int) -> int:
        """Validate that numeric values are positive."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v

    @field_validator('burst_multiplier', 'authenticated_multiplier')
    @classmethod
    def validate_multiplier(cls, v: float) -> float:
        """Validate that multipliers are >= 1.0."""
        if v < 1.0:
            raise ValueError("Multiplier must be >= 1.0")
        return v

    @field_validator('backend')
    @classmethod
    def validate_backend(cls, v: str) -> str:
        """Validate backend type."""
        if v not in ['redis', 'memory']:
            raise ValueError("Backend must be 'redis' or 'memory'")
        return v

    @classmethod
    def parse_endpoints_from_json(cls, endpoints_json: str) -> dict[str, RateLimit]:
        """Parse endpoint configuration from JSON string."""
        if not endpoints_json.strip():
            return {}

        try:
            data = json.loads(endpoints_json)
            endpoints = {}

            for endpoint, config in data.items():
                if not isinstance(config, dict):
                    raise ValueError(f"Invalid config for endpoint {endpoint}")

                requests = config.get('requests')
                window = config.get('window')
                burst_multiplier = config.get('burst_multiplier', 1.0)

                if requests is None or window is None:
                    raise ValueError(f"Missing requests or window for endpoint {endpoint}")

                endpoints[endpoint] = RateLimit(
                    requests=int(requests),
                    window_seconds=int(window),
                    burst_multiplier=float(burst_multiplier)
                )

            return endpoints

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in endpoints configuration: {e}") from e
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid endpoint configuration: {e}") from e

    def get_rate_limit_for_endpoint(self, endpoint: str) -> RateLimit:
        """Get rate limit configuration for a specific endpoint."""
        if endpoint in self.endpoints:
            return self.endpoints[endpoint]

        # Return default configuration
        return RateLimit(
            requests=self.default_requests,
            window_seconds=self.default_window,
            burst_multiplier=self.burst_multiplier
        )

    def get_rate_limit_for_client(self, endpoint: str, is_authenticated: bool = False) -> RateLimit:
        """Get rate limit configuration for a client type."""
        base_limit = self.get_rate_limit_for_endpoint(endpoint)

        if is_authenticated:
            # Apply authenticated multiplier
            return RateLimit(
                requests=int(base_limit.requests * self.authenticated_multiplier),
                window_seconds=base_limit.window_seconds,
                burst_multiplier=base_limit.burst_multiplier
            )

        return base_limit

    def is_ip_whitelisted(self, ip: str) -> bool:
        """Check if an IP address is whitelisted."""
        return ip in self.ip_whitelist
