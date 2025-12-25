# products/management/commands/import_laptops.py  (또는 네가 쓰는 위치에 그대로)
import json
import re
from typing import Any, Dict, Optional, Tuple, List

from django.utils import timezone
from django.db import transaction

from products.models import ProductDetailRaw, ProductDetailSpec


# ---------------------------
# 공통 유틸
# ---------------------------

def clean_text(v: Any) -> str:
    if v is None:
        return ""
    s = str(v)
    # 특수 공백/얇은 공백 제거
    s = s.replace("\u2009", " ").replace("\xa0", " ").strip()
    # "None" 문자열 방지
    if s.lower() in ("none", "null", "nan"):
        return ""
    return s


def deep_get(obj: Any, path: str) -> Any:
    """
    path 예: "data.Product.Brand" / "Product.Brand" / "Inside.CPU.Model"
    dict만 대상으로 '.' 기준 탐색. 없으면 None.
    """
    if obj is None:
        return None
    cur = obj
    for key in path.split("."):
        if not isinstance(cur, dict):
            return None
        if key not in cur:
            return None
        cur = cur[key]
    return cur


def first_non_empty(*vals: Any) -> Optional[str]:
    for v in vals:
        s = clean_text(v)
        if s != "":
            return s
    return None


def parse_number(s: Any) -> Optional[float]:
    """
    '15.6 inch', '2.28 kg', '230 W', '58 Wh', '1920 x 1080' 등에서 숫자 하나만 뽑기
    """
    s = clean_text(s)
    if not s:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)", s)
    return float(m.group(1)) if m else None


def parse_weight_kg(s: Any) -> Optional[float]:
    """
    '2.28 kg' / '2280 g' 등 처리
    """
    s = clean_text(s)
    if not s:
        return None

    # g 단위
    if re.search(r"\bg\b", s.lower()) and not re.search(r"\bkg\b", s.lower()):
        n = parse_number(s)
        return round(n / 1000.0, 3) if n is not None else None

    # kg 단위
    n = parse_number(s)
    return float(n) if n is not None else None


def parse_storage_gb(s: Any) -> Optional[int]:
    """
    '512 GB', '1 TB', '1024GB' 등 → GB int
    """
    s = clean_text(s).upper().replace(",", "")
    if not s:
        return None

    # 예: "1 TB", "1TB"
    tb = re.search(r"(\d+(?:\.\d+)?)\s*TB", s)
    if tb:
        return int(float(tb.group(1)) * 1024)

    gb = re.search(r"(\d+(?:\.\d+)?)\s*GB", s)
    if gb:
        return int(float(gb.group(1)))

    # 숫자만 있고 단위가 없을 때(애매하지만 마지막 fallback)
    only = re.fullmatch(r"\d+(?:\.\d+)?", s)
    if only:
        return int(float(s))

    return None


def parse_ram_gb(s: Any) -> Optional[int]:
    """
    '16 GB', '32GB' → GB int
    """
    return parse_storage_gb(s)


def parse_power_w(s: Any) -> Optional[int]:
    """
    '230 W' → 230
    """
    n = parse_number(s)
    return int(n) if n is not None else None


def parse_battery_wh(s: Any) -> Optional[float]:
    """
    '58 Wh', '99 Wh' → 58.0, 99.0
    """
    n = parse_number(s)
    return float(n) if n is not None else None


def normalize_gpu_text(dedicated_brand: str, dedicated_model: str, integrated: str, vram: str) -> str:
    parts = []
    if dedicated_brand or dedicated_model:
        s = " ".join([p for p in [dedicated_brand, dedicated_model] if p]).strip()
        if vram:
            s = f"{s} ({vram})".strip()
        parts.append(s)
    if integrated:
        parts.append(integrated)
    # 중복 제거
    uniq = []
    for p in parts:
        if p and p not in uniq:
            uniq.append(p)
    return " / ".join(uniq).strip()


def extract_candidates(payload: Dict[str, Any], paths: List[str]) -> Any:
    """
    후보 경로 리스트를 순서대로 시도해서, 가장 먼저 non-empty인 값을 반환
    """
    for p in paths:
        v = deep_get(payload, p)
        if isinstance(v, dict):
            # dict는 바로 쓰기 애매 → 일단 패스 (필요하면 호출부에서 dict 경로로 더 깊게)
            continue
        if clean_text(v) != "":
            return v
    return None


# ---------------------------
# raw_json -> spec 추출 로직
# ---------------------------

def parse_raw_to_spec_fields(raw_json: str) -> Dict[str, Any]:
    """
    다양한 소스(raw_json 스키마가 제각각)를 최대한 커버해서 Spec 필드를 생성
    """
    try:
        payload = json.loads(raw_json)
    except Exception:
        return {}

    # 어떤 raw는 {"status":"success","data":{...}} 형태
    data = payload.get("data") if isinstance(payload, dict) else None
    if isinstance(data, dict):
        root = data
    else:
        root = payload if isinstance(payload, dict) else {}

    # ---- product_type ----
    product_type = first_non_empty(
        extract_candidates(root, [
            "Product.Category",
            "Product.category",
            "Category",
            "Design.Body.Type",
            "Design.Type",
        ]),
        "laptop",
    )

    # ---- brand / model ----
    brand = first_non_empty(
        extract_candidates(root, [
            "Product.Brand",
            "Product.brand",
            "brand",
            "Brand",
        ]),
        ""
    )

    # model: Model Name/Model/Part Number/Family 등 다양
    model = first_non_empty(
        extract_candidates(root, [
            "Product.Model Name",
            "Product.ModelName",
            "Product.Model",
            "Product.model",
            "Product.Part Number",
            "Product.PartNumber",
            "Product.Family",
            "Product.english_id",
        ]),
        ""
    )

    # ---- os ----
    os_text = first_non_empty(
        extract_candidates(root, [
            "Inside.Software.Operating System Version",
            "Inside.Software.OS",
            "Software.Operating System Version",
            "Software.OS",
            "Inside.OS",
            "OS",
        ]),
        ""
    )

    # ---- cpu ----
    cpu_text = first_non_empty(
        extract_candidates(root, [
            "Inside.CPU.Model",
            "Inside.CPU.Processor",
            "Inside.Processor.Model",
            "Inside.Processor",
            "Processor.Model",
            "Processor",
            "Key Aspects.Processor",
            "Key Aspects.CPU",
        ]),
        ""
    )

    # ---- ram_gb ----
    # RAM 용량이 "RAM" dict 안에 없고, Key Aspects 혹은 다른 텍스트에 박혀있는 경우가 많아서 후보를 넓게 잡음
    ram_str = first_non_empty(
        extract_candidates(root, [
            "Inside.RAM.Capacity",
            "Inside.RAM.Size",
            "Inside.RAM.Total Capacity",
            "Inside.Memory.Total Capacity",
            "Inside.Memory.Capacity",
            "Key Aspects.RAM",
            "Key Aspects.Memory",
        ]),
        ""
    )
    ram_gb = parse_ram_gb(ram_str) if ram_str else None

    # ---- storage_gb ----
    storage_str = first_non_empty(
        extract_candidates(root, [
            "Inside.Storage.Total Capacity",
            "Inside.Storage.Capacity",
            "Inside.SSD.Total Capacity",
            "Inside.SSD.Capacity",
            "Inside.SSD.Size",
            "Inside.SSD",
            "Inside.HDD.Total Capacity",
            "Key Aspects.Storage",
            "Key Aspects.SSD",
        ]),
        ""
    )
    storage_gb = parse_storage_gb(storage_str) if storage_str else None

    # ---- gpu ----
    # dedicated + integrated 조합 시도
    dedicated_brand = clean_text(extract_candidates(root, [
        "Inside.GPU.Dedicated Card Brand",
        "Inside.Graphics.Dedicated Card Brand",
        "Graphics.Dedicated Card Brand",
        "GPU.Dedicated Card Brand",
    ]) or "")

    dedicated_model = clean_text(extract_candidates(root, [
        "Inside.GPU.Dedicated Card Model",
        "Inside.GPU.Model",
        "Inside.Graphics.Dedicated Card Model",
        "Key Aspects.Dedicated Graphics Card",
    ]) or "")

    integrated = clean_text(extract_candidates(root, [
        "Inside.GPU.Integrated Card Model",
        "Inside.GPU.Integrated Card Family",
        "Inside.Graphics.Integrated Card Model",
        "Key Aspects.Integrated Graphics Card",
    ]) or "")

    vram = clean_text(extract_candidates(root, [
        "Inside.GPU.Dedicated Card Memory",
        "Inside.Graphics.Dedicated Card Memory",
    ]) or "")

    gpu_text = normalize_gpu_text(dedicated_brand, dedicated_model, integrated, vram)

    # ---- weight_kg ----
    weight_raw = first_non_empty(
        extract_candidates(root, [
            "Design.Body.Weight",
            "Design.Weight",
            "Design.Body.Weight_kg",   # 이미 숫자면 parse_number로도 잡힘
            "Key Aspects.Weight",
        ]),
        ""
    )
    weight_kg = parse_weight_kg(weight_raw) if weight_raw else None
    # 혹시 숫자로 직접 들어온 경우
    if weight_kg is None:
        wnum = deep_get(root, "Design.Body.Weight_kg")
        if isinstance(wnum, (int, float)):
            weight_kg = float(wnum)

    # ---- display_inch ----
    display_diag = first_non_empty(
        extract_candidates(root, [
            "Display.Diagonal",
            "Display.Size",
            "Display.Diagonal Size",
            "Key Aspects.Display",
        ]),
        ""
    )
    display_inch = parse_number(display_diag) if display_diag else None

    # ---- battery_wh ----
    battery_raw = first_non_empty(
        extract_candidates(root, [
            "Inside.Battery.Capacity (Watt-hours)",
            "Inside.Battery.Capacity (mAh)",   # 어떤 소스는 여기에도 '99 Wh'가 들어옴
            "Inside.Battery.Capacity",
            "Battery.Capacity (Watt-hours)",
            "Battery.Capacity",
            "Key Aspects.Battery",
        ]),
        ""
    )
    battery_wh = parse_battery_wh(battery_raw) if battery_raw else None

    # ---- charging_power_w ----
    power_raw = first_non_empty(
        extract_candidates(root, [
            "Inside.Power.Power",
            "Inside.Power",
            "Power.Power",
            "Power",
        ]),
        ""
    )
    charging_power_w = parse_power_w(power_raw) if power_raw else None

    # ---- price_text ----
    # raw_json에 가격이 없는 케이스가 많음 → 그래도 빈 문자열 대신 "Unknown"으로 최소 채움(원하면 여기만 다시 비우게 바꿔도 됨)
    price_text = first_non_empty(
        extract_candidates(root, [
            "Price",
            "Pricing.Price",
            "Offers.Price",
            "Key Aspects.Price",
        ]),
        "Unknown"
    )

    return {
        "product_type": (product_type or "laptop").lower()[:16],
        "brand": (brand or "Unknown")[:128],
        "model": (model or "Unknown")[:256],
        "os": (os_text or "Unknown")[:128],
        "cpu": (cpu_text or "Unknown")[:256],
        "gpu": (gpu_text or "Unknown")[:256],
        "ram_gb": ram_gb,
        "storage_gb": storage_gb,
        "weight_kg": weight_kg,
        "display_inch": display_inch,
        "price_text": (price_text or "Unknown")[:256],
        "battery_wh": battery_wh,
        "charging_power_w": charging_power_w,
    }


def is_blank_text(v: Any) -> bool:
    return clean_text(v) == ""


def is_blank_number(v: Any) -> bool:
    # None or 0 or NaN 취급
    if v is None:
        return True
    try:
        if isinstance(v, (int, float)) and v == 0:
            return True
    except Exception:
        pass
    return False


# ---------------------------
# 실행 진입점
# ---------------------------

@transaction.atomic
def run():
    raws = ProductDetailRaw.objects.all().only("product_id", "raw_json")
    if not raws.exists():
        print("⚠️ ProductDetailRaw 데이터가 없습니다.")
        return

    updated_specs = []
    created = 0
    updated = 0

    for r in raws.iterator(chunk_size=500):
        fields = parse_raw_to_spec_fields(r.raw_json)
        if not fields:
            continue

        spec, was_created = ProductDetailSpec.objects.get_or_create(
            product_id=r.product_id,
            defaults={
                **fields,
                "updated_at": timezone.now(),
            },
        )

        if was_created:
            created += 1
            continue

        changed = False

        # 텍스트 필드: 비어있을 때만 채움
        for k in ["product_type", "brand", "model", "os", "cpu", "gpu", "price_text"]:
            newv = fields.get(k)
            if is_blank_text(getattr(spec, k)) and not is_blank_text(newv):
                setattr(spec, k, newv)
                changed = True

        # 숫자 필드: None/0일 때만 채움
        for k in ["ram_gb", "storage_gb", "weight_kg", "display_inch", "battery_wh", "charging_power_w"]:
            newv = fields.get(k)
            if is_blank_number(getattr(spec, k)) and not is_blank_number(newv):
                setattr(spec, k, newv)
                changed = True

        if changed:
            spec.updated_at = timezone.now()
            updated_specs.append(spec)
            updated += 1

    if updated_specs:
        ProductDetailSpec.objects.bulk_update(
            updated_specs,
            fields=[
                "product_type", "brand", "model", "os", "cpu", "gpu",
                "ram_gb", "storage_gb", "weight_kg", "display_inch",
                "price_text", "battery_wh", "charging_power_w",
                "updated_at",
            ],
            batch_size=500
        )

    print(f"✅ 완료: created={created}, updated={updated}, total_raw={raws.count()}")
