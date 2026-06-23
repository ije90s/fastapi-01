# FastAPI 핵심 개념 정리

## 1. async/await — 언제 쓰는가

FastAPI 공식 문서 기준:

| 상황 | 방식 |
|------|------|
| I/O 바운드 + async 라이브러리 | `async def` + `await` |
| I/O 바운드 + 동기 라이브러리 | `def` (FastAPI가 스레드풀에서 자동 실행) |
| CPU 바운드 | 멀티프로세스 (Gunicorn workers) |

- **I/O 바운드**: DB 쿼리, 외부 API 호출, 파일 읽기 등 — 대기 시간 동안 이벤트 루프가 다른 요청 처리 가능
- **CPU 바운드**: 이미지 처리, ML 추론, 암호화 등 — Python GIL 때문에 스레드로는 병렬 불가, 멀티프로세스 필요
- 웹/앱 서버는 대부분 I/O 바운드 → `async def`가 기본값

### 멀티스레드를 쓰는 경우

- async를 지원하지 않는 레거시 라이브러리 사용 시
- 동기 코드를 async로 못 바꿀 때
- `def` 엔드포인트 → FastAPI가 자동으로 `ThreadPoolExecutor`에서 실행

---

## 2. 공식 문서 필수 개념

### Path & Query Parameters

```python
@app.get("/items/{item_id}")
def read_item(item_id: str, skip: int = 0, limit: int = 10):
    ...
```

타입 힌트만으로 자동 파싱 + 검증.

### Request Body (Pydantic)

```python
class ItemBase(BaseModel):
    name: str = Field(description="상품명")
    color: Optional[ItemColor] = Field(default=None)
```

- `BaseModel`로 요청/응답 스키마 정의
- 자동 JSON 직렬화/역직렬화 + 문서 생성

### Dependencies (`Depends`)

공통 로직을 엔드포인트에 주입하는 핵심 패턴.

```python
@app.get("/items/{item_id}")
def read_item(item: Item = Depends(item_or_404)):
    return item
```

### HTTP Exception & Status Code

```python
raise HTTPException(status_code=404, detail="아이템이 없어요")

@app.post("/items", status_code=201)
```

### Response Model

```python
@app.get("/items", response_model=list[Item])
```

응답 데이터 필터링 + Swagger 문서 자동 생성.

### Lifespan (startup/shutdown)

async 클라이언트처럼 앱 시작 시 초기화가 필요한 리소스 관리.

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    global supabase
    supabase = await acreate_client(...)
    yield  # 여기서 앱 실행
    # yield 이후는 shutdown 시 실행

app = FastAPI(lifespan=lifespan)
```

### Middleware

모든 요청에 전역으로 적용.

```python
@app.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    print(f"{request.method} {request.url}")
    return response
```

---

## 3. Depends vs Middleware

비슷해 보이지만 역할이 다름.

| | Depends | Middleware |
|---|---|---|
| 적용 범위 | 특정 엔드포인트 | 앱 전체 (모든 요청) |
| 반환값 주입 | O | X |
| 선택적 적용 | O | X |
| 주요 용도 | 인증된 유저 객체, DB 세션 | 로깅, CORS, 응답 헤더 추가 |

- "이 엔드포인트에서 **현재 유저**가 누군지 알아야 해" → `Depends`
- "**모든 요청**에 처리 시간을 로그로 남겨야 해" → Middleware

---

## 4. NestJS 개념과 대응

| NestJS | FastAPI | 설명 |
|--------|---------|------|
| Guard | `Depends` | 인증/권한 체크 후 값 주입 |
| Pipe | Pydantic + `Field` | 요청 데이터 변환/검증 (타입 힌트로 자동 처리) |
| Interceptor | Middleware | 요청/응답 전후 처리 |
| Exception Filter | `HTTPException` + `exception_handler` | 전역 예외 처리 |

NestJS가 명시적으로 분리한 개념들을 FastAPI는 타입 힌트 + Pydantic으로 흡수.
