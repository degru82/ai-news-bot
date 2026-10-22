from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class HfConfig(BaseModel):
    min_upvotes: int = 10


class ArxivConfig(BaseModel):
    categories: list[str]
    keywords: list[str] = Field(default_factory=list)


class AinewsConfig(BaseModel):
    feed: str


class AlertFeed(BaseModel):
    name: str
    feed: str


class HackerNewsConfig(BaseModel):
    min_points: int = 100
    keywords: list[str] = Field(default_factory=list)


class Limits(BaseModel):
    prefilter_max: int = 150
    papers: int = 5
    news: int = 5
    linkedin: int = 3


class Config(BaseModel):
    timezone: str = "Asia/Seoul"
    lookback_hours: int = 26
    hf_papers: HfConfig = Field(default_factory=HfConfig)
    arxiv: ArxivConfig
    ainews: AinewsConfig
    google_alerts: list[AlertFeed] = Field(default_factory=list)
    hackernews: HackerNewsConfig = Field(default_factory=HackerNewsConfig)
    limits: Limits = Field(default_factory=Limits)


def load_config(path: str | Path = "sources.yaml") -> Config:
    with open(path, encoding="utf-8") as f:
        return Config.model_validate(yaml.safe_load(f))
