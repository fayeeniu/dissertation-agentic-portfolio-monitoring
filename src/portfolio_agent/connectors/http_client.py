from __future__ import annotations

import threading
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from urllib.parse import urlsplit

import httpx

from portfolio_agent.enums import CollectionStatus


@dataclass(frozen=True, slots=True)
class HttpPolicy:
    allowed_origins: tuple[str, ...]
    allowed_content_types: tuple[str, ...] = ("application/json",)
    timeout_seconds: float = 10.0
    max_response_bytes: int = 5 * 1024 * 1024
    max_attempts: int = 3
    minimum_interval_seconds: float = 0.0
    maximum_retry_after_seconds: float = 5.0

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("HTTP timeout must be positive.")
        if self.max_response_bytes <= 0 or self.max_attempts <= 0:
            raise ValueError("HTTP size and attempt bounds must be positive.")


@dataclass(frozen=True, slots=True)
class HttpFetchResult:
    status: CollectionStatus
    url: str
    attempts: int
    http_status: int | None = None
    media_type: str | None = None
    content: bytes | None = None
    error_code: str | None = None
    error_message: str | None = None


class BoundedHttpClient:
    """Read-only HTTP with an origin allowlist and explicit resource bounds."""

    def __init__(
        self,
        policy: HttpPolicy,
        *,
        transport: httpx.BaseTransport | None = None,
        sleeper: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._policy = policy
        self._client = httpx.Client(
            transport=transport,
            timeout=httpx.Timeout(policy.timeout_seconds),
            follow_redirects=False,
        )
        self._sleeper = sleeper
        self._clock = clock
        self._last_request_at: dict[str, float] = {}
        self._lock = threading.Lock()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> BoundedHttpClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def get(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> HttpFetchResult:
        origin = self._validate_url(url)
        last_error: tuple[str, str] | None = None
        for attempt in range(1, self._policy.max_attempts + 1):
            self._respect_rate_limit(origin)
            try:
                request = self._client.build_request("GET", url, headers=headers)
                response = self._client.send(request, stream=True)
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_error = ("timeout_or_transport", type(exc).__name__)
                if attempt < self._policy.max_attempts:
                    self._sleeper(self._retry_delay(attempt, None))
                    continue
                return HttpFetchResult(
                    status=CollectionStatus.SOURCE_UNAVAILABLE,
                    url=url,
                    attempts=attempt,
                    error_code=last_error[0],
                    error_message=last_error[1],
                )

            try:
                result, retry_delay = self._consume_response(response, url=url, attempt=attempt)
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_error = ("timeout_or_transport", type(exc).__name__)
                if attempt < self._policy.max_attempts:
                    self._sleeper(self._retry_delay(attempt, None))
                    continue
                return HttpFetchResult(
                    status=CollectionStatus.SOURCE_UNAVAILABLE,
                    url=url,
                    attempts=attempt,
                    error_code=last_error[0],
                    error_message=last_error[1],
                )
            if result is not None:
                return result
            assert retry_delay is not None
            last_error = ("retryable_http_status", str(response.status_code))
            self._sleeper(retry_delay)

        assert last_error is not None
        raise AssertionError("Bounded retry loop ended without a result.")

    def _validate_url(self, url: str) -> str:
        parts = urlsplit(url)
        if parts.scheme not in {"https", "http"} or not parts.netloc:
            raise ValueError("HTTP collection requires an absolute HTTP(S) URL.")
        origin = f"{parts.scheme}://{parts.netloc}".lower()
        if origin not in {item.rstrip("/").lower() for item in self._policy.allowed_origins}:
            raise ValueError("HTTP origin is outside the source allowlist.")
        return origin

    def _consume_response(
        self,
        response: httpx.Response,
        *,
        url: str,
        attempt: int,
    ) -> tuple[HttpFetchResult | None, float | None]:
        try:
            status_code = response.status_code
            if status_code == 404:
                return (
                    HttpFetchResult(
                        status=CollectionStatus.NO_RECORD,
                        url=url,
                        attempts=attempt,
                        http_status=status_code,
                    ),
                    None,
                )
            if status_code == 429 or 500 <= status_code <= 599:
                if attempt < self._policy.max_attempts:
                    return (
                        None,
                        self._retry_delay(attempt, response.headers.get("retry-after")),
                    )
                return (
                    HttpFetchResult(
                        status=CollectionStatus.SOURCE_UNAVAILABLE,
                        url=url,
                        attempts=attempt,
                        http_status=status_code,
                        error_code="retryable_http_status",
                        error_message=str(status_code),
                    ),
                    None,
                )
            if not 200 <= status_code <= 299:
                return (
                    HttpFetchResult(
                        status=CollectionStatus.FAILED,
                        url=url,
                        attempts=attempt,
                        http_status=status_code,
                        error_code="non_retryable_http_status",
                        error_message=str(status_code),
                    ),
                    None,
                )

            media_type = response.headers.get("content-type", "").split(";", 1)[0].lower()
            if media_type not in self._policy.allowed_content_types:
                return (
                    HttpFetchResult(
                        status=CollectionStatus.FAILED,
                        url=url,
                        attempts=attempt,
                        http_status=status_code,
                        media_type=media_type or None,
                        error_code="unexpected_content_type",
                        error_message=media_type or "missing content type",
                    ),
                    None,
                )
            declared_length = response.headers.get("content-length")
            if declared_length and int(declared_length) > self._policy.max_response_bytes:
                return (
                    HttpFetchResult(
                        status=CollectionStatus.FAILED,
                        url=url,
                        attempts=attempt,
                        http_status=status_code,
                        media_type=media_type,
                        error_code="response_too_large",
                        error_message="Declared response size exceeds the configured limit.",
                    ),
                    None,
                )
            chunks: list[bytes] = []
            total = 0
            for chunk in response.iter_bytes():
                total += len(chunk)
                if total > self._policy.max_response_bytes:
                    return (
                        HttpFetchResult(
                            status=CollectionStatus.FAILED,
                            url=url,
                            attempts=attempt,
                            http_status=status_code,
                            media_type=media_type,
                            error_code="response_too_large",
                            error_message="Streamed response exceeds the configured limit.",
                        ),
                        None,
                    )
                chunks.append(chunk)
            return (
                HttpFetchResult(
                    status=CollectionStatus.SUCCEEDED,
                    url=url,
                    attempts=attempt,
                    http_status=status_code,
                    media_type=media_type,
                    content=b"".join(chunks),
                ),
                None,
            )
        finally:
            response.close()

    def _respect_rate_limit(self, origin: str) -> None:
        with self._lock:
            now = self._clock()
            previous = self._last_request_at.get(origin)
            if previous is not None:
                remaining = self._policy.minimum_interval_seconds - (now - previous)
                if remaining > 0:
                    self._sleeper(remaining)
                    now = self._clock()
            self._last_request_at[origin] = now

    def _retry_delay(self, attempt: int, retry_after: str | None) -> float:
        if retry_after is not None:
            try:
                return min(
                    max(float(retry_after), 0.0),
                    self._policy.maximum_retry_after_seconds,
                )
            except ValueError:
                pass
        return min(
            0.25 * (2.0 ** (attempt - 1)),
            self._policy.maximum_retry_after_seconds,
        )
