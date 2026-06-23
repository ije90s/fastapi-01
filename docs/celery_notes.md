# Celery 핵심 개념 정리

## 개요

Python 백그라운드 작업 큐. 시간이 오래 걸리거나 즉시 응답이 필요 없는 작업을 **별도 워커 프로세스**에서 처리.

```
FastAPI → 브로커(Redis) → Celery Worker → 결과
```

---

## 1. 브로커 vs 백엔드

| | 역할 | 주로 쓰는 것 |
|---|---|---|
| **브로커** | 작업 메시지 전달 (큐) | Redis, RabbitMQ |
| **백엔드** | 작업 결과 저장 | Redis, DB |

```python
app = Celery(
    "worker",
    broker="redis://localhost:6379/0",   # 작업 전달
    backend="redis://localhost:6379/1",  # 결과 저장
)
```

---

## 2. Task 정의

```python
@app.task(bind=True, max_retries=3)
def send_push(self, user_id: str, title: str):
    try:
        result = push_client.send(user_id, title)
        if not result.ok:
            raise Exception("전송 실패")
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)  # 5초 후 재시도
```

- `bind=True` → `self`로 태스크 인스턴스 접근 (retry에 필요)
- `max_retries=3` → 최대 3회 재시도
- `countdown=5` → N초 후 재시도

---

## 3. 큐에 넣기

```python
# 즉시 실행 요청
send_push.delay(user_id="abc", title="알림")

# 옵션 지정
send_push.apply_async(
    args=["abc", "알림"],
    countdown=10,       # 10초 후 실행
    expires=3600,       # 1시간 후 만료
)
```

---

## 4. 중요 설정

```python
app.conf.update(
    task_acks_late=True,           # 처리 완료 후 ACK → 크래시 시 재처리 보장
    worker_prefetch_multiplier=1,  # 워커당 1개만 가져옴 → 중복 최소화
    task_serializer="json",
    result_expires=3600,
)
```

### task_acks_late 동작 차이

```
# False (기본) — 위험
워커가 메시지 수신 즉시 ACK → 처리 중 크래시 → 메시지 유실

# True — 안전
처리 완료 후 ACK → 크래시 시 브로커에 메시지 남아 → 재처리
```

---

## 5. 워커 실행

```bash
# 기본
celery -A worker worker

# 동시성 지정 (프로세스 수)
celery -A worker worker --concurrency=4

# 로그 레벨
celery -A worker worker --loglevel=info
```

---

## 6. Celery Beat — 스케줄 실행

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    "매일-새벽-2시-일괄-발송": {
        "task": "worker.send_daily_push",
        "schedule": crontab(hour=2, minute=0),
    },
}
```

```bash
# Beat는 별도 프로세스로 실행
celery -A worker beat
celery -A worker worker  # 워커도 따로
```

---

## 7. 작업 상태 조회

```python
# 큐에 넣을 때 task_id 받기
task = send_push.delay(user_id="abc", title="알림")
task_id = task.id

# 상태 조회
result = AsyncResult(task_id)
print(result.state)   # PENDING / STARTED / SUCCESS / FAILURE / RETRY
print(result.result)  # 반환값 or 예외
```

---

## 8. 시그널 — 성공/실패 훅

```python
from celery.signals import task_failure, task_success

@task_failure.connect
def on_failure(sender, task_id, exception, **kwargs):
    # 슬랙 알람, DLQ 저장 등
    save_to_dlq(task_id, str(exception))
```

---

## 전체 흐름 요약

```
POST /push
  ↓
send_push.delay()        # 브로커(Redis)에 메시지 PUT
  ↓
Celery Worker            # 메시지 꺼내서 실행
  ├─ 성공 → ACK, 결과 백엔드 저장
  └─ 실패 → retry (최대 3회)
              └─ 초과 → DLQ 저장 (커스텀 로직)
```

---

## 모니터링 — Flower

```bash
pip install flower
celery -A worker flower --port=5555
# http://localhost:5555 — 태스크 현황, 워커 상태 실시간 확인
```

---

## ARQ와 비교

| | Celery | ARQ |
|---|---|---|
| 기반 | sync (gevent/eventlet로 async 흉내) | asyncio 네이티브 |
| 브로커 | Redis, RabbitMQ 등 다양 | Redis 전용 |
| 설정 복잡도 | 높음 (celeryconfig, beat 별도) | 낮음 (WorkerSettings 하나) |
| 태스크 정의 | `@celery.task` 데코레이터 | 일반 `async def` |
| 스케줄 | Celery Beat (별도 프로세스) | `cron_jobs` (워커에 내장) |
| 모니터링 | Flower | 별도 없음 (직접 구현) |
| 성숙도 | 높음 | 낮음 (문서 빈약) |
