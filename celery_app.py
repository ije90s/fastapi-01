from celery import Celery

celery_app = Celery(
    "fastapi-01",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    include=["tasks"],  # 워커 시작 시 tasks.py 자동 import
)

celery_app.conf.update(
    task_acks_late=True,           # 처리 완료 후 ACK → 크래시 시 재처리 보장
    worker_prefetch_multiplier=1,  # 워커당 1개만 가져옴 → 중복 최소화
    task_serializer="json",
    result_expires=3600,
)
