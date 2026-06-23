# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 환경 변수

`.env.example`을 복사해 `.env`를 만들고 Supabase 프로젝트의 값을 채워야 서버가 기동됨.

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key
```

## 명령어

```bash
# 의존성 설치
uv sync

# 개발 서버 실행 (자동 재시작)
uv run fastapi dev main.py

# 린트
uv run ruff check .

# 포맷
uv run ruff format .
```

## 아키텍처

단일 파일 FastAPI 앱(`main.py`) — Supabase `items` 테이블을 백엔드로 사용.

**Supabase 테이블 스키마 (`items`):**
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | uuid | PK, 자동 생성 |
| name | varchar | not null |
| color | varchar | nullable |

**데이터 모델:**
- `ItemBase` — 요청 바디 스키마 (name, 선택적 color 열거형)
- `Item(ItemBase)` — `id: str` (UUID)를 추가한 전체 모델
- `ItemId = str` — 전체 코드에서 사용하는 타입 별칭

**패턴:** `item_or_404(item_id)`는 Supabase에서 `.maybe_single()`로 조회 후 없으면 `HTTPException(404)`를 발생시키는 공통 헬퍼.

**엔드포인트:** `/items`에 대한 표준 CRUD — GET `/items/{id}`, POST `/items` (201), PUT `/items/{id}` (202), DELETE `/items/{id}` (204).

서버 실행 중 `/docs`에서 인터랙티브 API 문서를 확인할 수 있음.
