from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Kind = Literal["paper", "news", "community", "linkedin"]
SignalValue = int | float | str


class Item(BaseModel):
    """모든 소스가 반환하는 공통 스키마 (SPEC 4장)."""

    source: str
    kind: Kind
    title: str
    url: str
    canonical_id: str
    published_at: datetime | None = None
    snippet: str = ""
    signals: dict[str, SignalValue] = Field(default_factory=dict)


class FetchResult(BaseModel):
    """소스 하나의 수집 결과. 실패해도 예외 대신 error에 기록한다."""

    source: str
    items: list[Item] = Field(default_factory=list)
    error: str | None = None
    skipped: bool = False

    @property
    def ok(self) -> bool:
        return self.error is None
