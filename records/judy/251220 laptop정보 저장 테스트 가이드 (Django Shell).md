# 🧪 DB 저장 테스트 가이드 (Django Shell)

엑셀 데이터를 Django DB에 정상적으로 저장하는지 확인하기 위한 테스트 절차입니다.
Django REST framework나 Vue 연결 없이 백엔드 단독으로 검증합니다.

---

## 1️⃣ Django shell 실행

```bash
python manage.py shell
```

---

## 2️⃣ 데이터 적재 함수 import

```python
from products.scripts.import_laptops import run
```

---

## 3️⃣ 엑셀 → DB 저장 실행 (핵심)

```python
run()
```

성공 시 예시 출력:

```text
✅ 1234개의 노트북 데이터를 성공적으로 저장했습니다!
```

---

## 4️⃣ DB 저장 여부 확인

```python
from products.models import Laptop
Laptop.objects.count()
```

- 결과가 `0`이 아니면 DB 저장 성공

---

## 🔍 추가 확인 (선택)

### 일부 데이터 조회
```python
Laptop.objects.all()[:5]
```

### 조건 필터링 확인
```python
Laptop.objects.filter(ram=16)
```

### 특정 필드 확인
```python
Laptop.objects.values('model', 'ram', 'ssd')[:5]
```

---


# 📄 Laptop DB → JSON export 스크립트 실행 가이드

Django DB에 저장된 Laptop 데이터를 **스크립트 파일로 JSON으로 저장**하는 방법입니다.  
Django shell에서 스크립트를 실행하는 방식까지만 다룹니다.

---

## 1️⃣ JSON export 스크립트 생성

아래 파일을 생성합니다.

```text
products/scripts/export_laptops_json.py
```

```python
import json
import os
from django.conf import settings
from products.models import Laptop

def run():
    file_path = os.path.join(
        settings.BASE_DIR,
        "products",
        "data",
        "laptops.json"
    )

    data = list(Laptop.objects.values())

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(data)}개의 노트북 데이터를 JSON으로 저장했습니다.")
    print(f"📁 저장 위치: {file_path}")
```

---

## 2️⃣ Django shell 실행

```bash
python manage.py shell
```

---

## 3️⃣ 스크립트 실행

```python
from products.scripts.export_laptops_json import run
run()
```

---

## 4️⃣ 결과

- `products/data/laptops.json` 파일 생성
- DB에 저장된 Laptop 데이터가 JSON 형식으로 저장됨

---

## ✅ 정리

- 스크립트 방식은 **재사용 및 자동화에 적합**
- Django shell에서 `run()` 호출만으로 실행 가능
