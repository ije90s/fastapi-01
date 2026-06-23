# fastapi-01

FastAPI + Supabase로 만든 간단한 Items CRUD API.

## 시작하기

### 1. 의존성 설치

```bash
uv sync
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 Supabase 프로젝트 정보를 입력합니다.

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key
```

### 3. Supabase 테이블 생성

Supabase 대시보드 SQL 에디터에서 아래 쿼리를 실행합니다.

```sql
create table items (
  id    uuid primary key default gen_random_uuid(),
  name  varchar not null,
  color varchar
);
```

### 4. 서버 실행

```bash
uv run fastapi dev main.py
```

서버가 뜨면 http://localhost:8000/docs 에서 인터랙티브 API 문서를 확인할 수 있습니다.

## API

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/items/{id}` | 아이템 단건 조회 |
| POST | `/items` | 아이템 등록 (201) |
| PUT | `/items/{id}` | 아이템 수정 (202) |
| DELETE | `/items/{id}` | 아이템 삭제 (204) |

### 요청/응답 예시

**POST /items**
```json
// Request
{ "name": "사과", "color": "red" }

// Response 201
{ "id": "uuid...", "name": "사과", "color": "red" }
```

`color`는 `red` / `green` / `blue` 중 하나 또는 생략 가능.

## Celery 백그라운드 워커

`POST /items`로 아이템 등록 시 Celery가 백그라운드에서 알림 태스크를 처리합니다.

### 흐름

```
POST /items
  → Supabase 저장 (즉시 201 응답)
  → notify_item_created.delay()  ← Redis 큐에 적재
       ↓
  Celery Worker
  → 80% 성공: [알림] 등록 완료: {name}
  → 20% 실패: retry (5초 간격, 최대 3회)
               └→ 초과 시 [DLQ] 실패 기록 출력
```

### 실행 순서

**1. Redis 실행**

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

**2. Celery 워커 실행**

```bash
uv run celery -A celery_app worker --loglevel=info
```

**3. Flower 모니터링 실행**

```bash
uv run celery -A celery_app flower --port=5555
```

`http://localhost:5555` 에서 태스크 현황을 실시간으로 확인할 수 있습니다.

### 주요 설정 (`celery_app.py`)

| 설정 | 값 | 설명 |
|------|----|------|
| `task_acks_late` | `True` | 처리 완료 후 ACK → 크래시 시 재처리 보장 |
| `worker_prefetch_multiplier` | `1` | 워커당 1개만 가져옴 → 중복 최소화 |
| `include` | `["tasks"]` | 워커 시작 시 tasks.py 자동 등록 |

## 개발

```bash
# 린트
uv run ruff check .

# 포맷
uv run ruff format .
```

## 기술 스택

- [FastAPI](https://fastapi.tiangolo.com/)
- [Supabase Python](https://supabase.com/docs/reference/python/introduction)
- [Celery](https://docs.celeryq.dev/)
- [Flower](https://flower.readthedocs.io/)
- [uv](https://docs.astral.sh/uv/)
- [Ruff](https://docs.astral.sh/ruff/)
