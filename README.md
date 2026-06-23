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
- [uv](https://docs.astral.sh/uv/)
- [Ruff](https://docs.astral.sh/ruff/)
