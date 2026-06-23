import random
from celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def notify_item_created(self, item_id: str, name: str):
    if random.random() < 0.2:  # 20% 확률로 실패
        exc = Exception("푸시 전송 실패")
        if self.request.retries >= self.max_retries:
            print(f"[DLQ] item_id={item_id} name={name} retries={self.request.retries}")
            return {"status": "failed", "item_id": item_id}
        raise self.retry(exc=exc, countdown=5)

    print(f"[알림] 등록 완료: {name} ({item_id})")
    return {"status": "success", "item_id": item_id}
