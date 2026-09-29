"""소스 수집기 모음. 모듈마다 `NAME`, `EXT`, `collect(client, config, now) -> list[Item]`."""

from collections.abc import Callable
from datetime import datetime
from types import ModuleType

from briefing.config import Config
from briefing.http import HttpClient
from briefing.models import FetchResult
from briefing.sources import ainews, alerts, arxiv, hf, hn

SOURCES: tuple[ModuleType, ...] = (hf, arxiv, ainews, alerts, hn)
ClientFactory = Callable[[ModuleType], HttpClient]


def collect_all(config: Config, client_for: ClientFactory, now: datetime) -> list[FetchResult]:
    """모든 소스를 수집한다. 한 소스의 예외는 해당 결과의 error에만 기록한다."""
    results = []
    for module in SOURCES:
        try:
            items = module.collect(client_for(module), config, now)
            results.append(FetchResult(source=module.NAME, items=items))
        except Exception as exc:
            results.append(FetchResult(source=module.NAME, error=f"{type(exc).__name__}: {exc}"))
    return results
