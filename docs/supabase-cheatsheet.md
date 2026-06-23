# Supabase Python 클라이언트 기본 문법

## SELECT

```python
# 전체 조회
res = supabase.table("items").select("*").execute()

# 특정 컬럼만
res = supabase.table("items").select("id, name").execute()

# 조건 (eq, neq, gt, lt, gte, lte)
res = supabase.table("items").select("*").eq("color", "red").execute()

# 단건 조회 (없으면 None)
res = supabase.table("items").select("*").eq("id", item_id).maybe_single().execute()

# 단건 조회 (없으면 예외)
res = supabase.table("items").select("*").eq("id", item_id).single().execute()

res.data  # 결과 데이터 (list 또는 dict)
```

## INSERT

```python
# 단건
res = supabase.table("items").insert({"name": "아이템1", "color": "red"}).execute()

# 다건
res = supabase.table("items").insert([
    {"name": "아이템1", "color": "red"},
    {"name": "아이템2", "color": "blue"},
]).execute()

res.data  # 삽입된 행 반환
```

## UPDATE

```python
# 조건에 맞는 행 수정 (.eq() 없으면 전체 업데이트되므로 주의)
res = supabase.table("items").update({"color": "blue"}).eq("id", item_id).execute()

res.data  # 수정된 행 반환
```

## DELETE

```python
# 조건에 맞는 행 삭제 (.eq() 없으면 전체 삭제되므로 주의)
res = supabase.table("items").delete().eq("id", item_id).execute()

res.data  # 삭제된 행 반환
```

## 공통 패턴

```python
# 체이닝 순서
supabase.table("테이블명")
    .select / insert / update / delete
    .eq / neq / gt / lt / like / in_  # 필터 (복수 체이닝 가능)
    .order("created_at", desc=True)   # 정렬
    .limit(10)                         # 개수 제한
    .execute()                         # 실행 (반드시 마지막)
```

> `execute()`를 호출해야 실제 쿼리가 날아가고, 결과는 항상 `res.data`로 접근합니다.
