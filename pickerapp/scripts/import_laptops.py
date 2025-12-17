import pandas as pd
import re
from pickerapp.models import Laptop

EXCHANGE_RATE = 16.5  # INR → KRW

def clean_text(value):
    """모든 입력을 문자열로 바꾸고 특수 공백 및 양끝 공백 제거"""
    if pd.isna(value):
        return ""
    # 엑셀의 특수 공백(Thin Space 등)을 일반 공백으로 치환
    return str(value).replace("\u2009", " ").strip()

def run():
    # 1. 엑셀 로드 및 결측치 기본 처리
    df = pd.read_excel("pickerapp/data/laptop.xlsx")
    df = df.fillna("") # NaN을 빈 문자열로 일괄 변환 (AttributeError 방지)

    laptops = []

    for _, row in df.iterrows():
        try:
            # --- [1] 기본 정보 및 가격 ---
            model_name = clean_text(row.get("Model", "Unknown"))
            
            price_str = clean_text(row.get("Price", "0"))
            price_rupee = int(re.sub(r"[^\d]", "", price_str)) if price_str else 0
            price_krw = int(price_rupee * EXCHANGE_RATE)

            # --- [2] 성능 (RAM, SSD) ---
            ram_raw = clean_text(row.get("Ram", "0"))
            ram_match = re.search(r"(\d+)", ram_raw)
            ram = int(ram_match.group(1)) if ram_match else 0

            ssd_raw = clean_text(row.get("SSD", "0")).upper()
            ssd_match = re.search(r"(\d+)", ssd_raw)
            if ssd_match:
                val = int(ssd_match.group(1))
                ssd = val * 1024 if "TB" in ssd_raw else val
            else:
                ssd = 0

            # --- [3] 디스플레이 (size, x, y) ---
            display_raw = clean_text(row.get("Display", "")).lower()
            # 정규식: (숫자.숫자)인치 ... (숫자)x(숫자) 추출
            display_match = re.search(r"([\d.]+)\s*inches.*?(\d+)\s*x\s*(\d+)", display_raw)
            
            if display_match:
                display_size = float(display_match.group(1))
                res_x = int(display_match.group(2))
                res_y = int(display_match.group(3))
            else:
                display_size, res_x, res_y = 0.0, 0, 0

            # --- [4] 기타 사양 ---
            rating_val = row.get("Rating")
            rating = float(rating_val) if rating_val != "" else None

            # Laptop 객체 생성
            laptop = Laptop(
                model=model_name,
                price=price_krw,
                rating=rating,
                generation=clean_text(row.get("Generation", "")),
                core=clean_text(row.get("Core", "")),
                ram=ram,
                ssd=ssd,
                display_size=display_size,
                resolution_x=res_x,
                resolution_y=res_y,
                graphics=clean_text(row.get("Graphics", "")),
                os=clean_text(row.get("OS", "")).replace(" OS", ""),
                warranty=clean_text(row.get("Warranty", ""))
            )
            laptops.append(laptop)

        except Exception as e:
            print(f"❌ 데이터 파싱 에러 (모델: {row.get('Model')}): {e}")
            continue

    # 2. DB 저장
    if laptops:
        Laptop.objects.bulk_create(laptops)
        print(f"✅ {len(laptops)}개의 노트북 데이터를 성공적으로 저장했습니다!")