"""외부 HTTP 호출 인터페이스와 구현 (실제 호출 / 녹화 / fixture 재생)."""

import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Protocol

import httpx

USER_AGENT = "ai-news-bot/0.1 (+https://github.com/degru82/ai-news-bot)"
Params = Mapping[str, str | int]


class HttpClient(Protocol):
    def get(self, url: str, params: Params | None = None) -> str: ...


class HttpxClient:
    """타임아웃 30초·재시도 2회·호출 간격을 지키는 실제 클라이언트."""

    def __init__(
        self,
        *,
        timeout: float = 30.0,
        retries: int = 2,
        min_interval: float = 1.0,
        transport: httpx.BaseTransport | None = None,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._client = httpx.Client(
            timeout=timeout,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
            transport=transport,
        )
        self._retries = retries
        self._min_interval = min_interval
        self._sleep = sleep
        self._clock = clock
        self._last_request: float | None = None

    def get(self, url: str, params: Params | None = None) -> str:
        for attempt in range(self._retries + 1):
            self._respect_interval()
            try:
                response = self._client.get(url, params=params)
                response.raise_for_status()
                return response.text
            except httpx.HTTPError as exc:
                if attempt == self._retries or not _retryable(exc):
                    raise
                self._sleep(2**attempt)
        raise AssertionError("unreachable")

    def _respect_interval(self) -> None:
        if self._last_request is not None:
            wait = self._min_interval - (self._clock() - self._last_request)
            if wait > 0:
                self._sleep(wait)
        self._last_request = self._clock()


def _retryable(exc: httpx.HTTPError) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return status == 429 or status >= 500
    return True


def fixture_path(directory: str | Path, name: str, ext: str, index: int = 0) -> Path:
    suffix = "" if index == 0 else f"-{index + 1}"
    return Path(directory) / f"{name}{suffix}{ext}"


class RecordingClient:
    """실제 응답을 그대로 fixture 파일로 저장하며 전달한다."""

    def __init__(self, inner: HttpClient, directory: str | Path, name: str, ext: str) -> None:
        self._inner = inner
        self._directory = directory
        self._name = name
        self._ext = ext
        self._count = 0

    def get(self, url: str, params: Params | None = None) -> str:
        text = self._inner.get(url, params)
        path = fixture_path(self._directory, self._name, self._ext, self._count)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        self._count += 1
        return text


class FixtureClient:
    """저장된 fixture를 호출 순서대로 돌려준다. 네트워크를 쓰지 않는다."""

    def __init__(self, directory: str | Path, name: str, ext: str) -> None:
        self._directory = directory
        self._name = name
        self._ext = ext
        self._count = 0

    def get(self, url: str, params: Params | None = None) -> str:
        path = fixture_path(self._directory, self._name, self._ext, self._count)
        self._count += 1
        return path.read_text(encoding="utf-8")
