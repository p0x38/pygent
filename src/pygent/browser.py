from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import httpx


@dataclass(frozen=True, slots=True)
class BrowserPage:
    """A fetched web page with its final URL and response metadata."""

    url: str
    content: str
    status_code: int
    content_type: str | None = None


class Browser:
    """Minimal async HTTP browser for fetching public web pages."""

    def __init__(self, *, timeout: float = 15.0, max_bytes: int = 2_000_000) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be greater than 0")
        if max_bytes < 1:
            raise ValueError("max_bytes must be at least 1")
        self.timeout = timeout
        self.max_bytes = max_bytes

    async def fetch(self, url: str) -> BrowserPage:
        """Fetch an HTTP(S) URL with a bounded response size."""
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("url must be an absolute HTTP(S) URL")

        async with (
            httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            ) as client,
            client.stream(
                "GET",
                url,
                headers={"User-Agent": "pygent/0.2"},
            ) as response,
        ):
            response.raise_for_status()
            chunks: list[bytes] = []
            size = 0
            async for chunk in response.aiter_bytes():
                size += len(chunk)
                if size > self.max_bytes:
                    raise ValueError("response exceeds browser max_bytes limit")
                chunks.append(chunk)

            content = b"".join(chunks).decode(
                response.encoding or "utf-8", errors="replace"
            )
            return BrowserPage(
                url=str(response.url),
                content=content,
                status_code=response.status_code,
                content_type=response.headers.get("content-type"),
            )
