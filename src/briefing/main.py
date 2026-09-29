"""수집 실행 진입점 (M1: 수집·정규화·fixture 저장까지)."""

import argparse
from datetime import UTC, date, datetime, time
from types import ModuleType

from briefing.config import load_config
from briefing.http import FixtureClient, HttpClient, HttpxClient, RecordingClient
from briefing.sources import collect_all


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="briefing")
    parser.add_argument("--date", type=date.fromisoformat, help="기준 날짜(UTC), 기본은 현재")
    parser.add_argument("--config", default="sources.yaml")
    parser.add_argument("--dry-run", action="store_true", help="게시·전송 없이 수집 결과만 출력")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--fixtures", help="네트워크 대신 이 디렉터리의 fixture를 읽는다")
    source.add_argument("--save-fixtures", help="실제 응답을 이 디렉터리에 저장한다")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    # 날짜를 지정하면 그날 UTC 끝 시각을 기준으로 삼아 조회 구간이 그날을 덮게 한다.
    now = (
        datetime.combine(args.date, time(23, 59, 59), tzinfo=UTC)
        if args.date
        else datetime.now(UTC)
    )

    def client_for(module: ModuleType) -> HttpClient:
        if args.fixtures:
            return FixtureClient(args.fixtures, module.NAME, module.EXT)
        client = HttpxClient()
        if args.save_fixtures:
            return RecordingClient(client, args.save_fixtures, module.NAME, module.EXT)
        return client

    results = collect_all(load_config(args.config), client_for, now)
    for result in results:
        if result.ok:
            print(f"{result.source}: {len(result.items)}건")
            for item in result.items:
                print(f"  - [{item.kind}] {item.title} ({item.canonical_id})")
        else:
            print(f"{result.source}: 수집 실패 - {result.error}")
    return 1 if all(not r.ok for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
