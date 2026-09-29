# 게시·전달

## 결정
- 웹: 정적 HTML(`site/YYYY-MM-DD.html`, `index.html`, `feed.xml`)을 GitHub Pages로 게시.
- 메일: 발송 전용 Gmail SMTP, 구독자 BCC, 목록은 Secret `SUBSCRIBERS`.
- 푸시: 운영자 전용 ntfy(헤드라인+링크, 실패 알림).

## 배경·이유
- 프레임워크 없는 정적 HTML: 배포를 단순하게 하고 무료 Pages로 충분.
- 같은 날짜 재실행은 해당 날짜 페이지만 덮어씀: backfill이 다른 날짜에 영향을 주지 않게.
- BCC: 구독자끼리 주소가 노출되지 않게. 목록을 저장소가 아닌 Secret에 두는 것은 "구독자 주소를 코드·로그·`site/`에 두지 않는다"는 규칙 때문.
- Pages는 공개 사이트이므로 회사 내부 정보·구독자 정보는 넣지 않는다.
- RSS를 함께 제공하는 이유: 회사 메일로 외부 발송이 막힐 경우의 대안 ([미정 사항](../06-decisions/milestones-and-open-questions.md)).

## 변경 이력
- SPEC v2(PR #6): 초기 정의.

관련: [브리핑 생성](../03-pipeline/briefing.md), [운영·보안](../05-operations/operations-and-security.md)
