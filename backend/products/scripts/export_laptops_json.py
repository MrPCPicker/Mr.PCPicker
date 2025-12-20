import json
from products.models import Laptop

def run():
    data = list(Laptop.objects.values())
    with open("laptops.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(data)}개의 노트북 데이터를 JSON으로 저장했습니다.")
