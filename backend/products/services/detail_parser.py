# products/services/detail_parser.py

import re


def _get(d, path, default=None):
    """Safely get nested dictionary value using dot notation"""
    if not d or not path:
        return default

    cur = d
    for key in path.split("."):
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return default
    return cur


def get_first(d, paths, default=None):
    """여러 경로를 순서대로 조회해서 첫 유효값 반환"""
    for p in paths:
        v = _get(d, p)
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        return v
    return default


def parse_int(text):
    """Extract first integer from text"""
    if text is None:
        return None
    m = re.search(r"(\d+)", str(text))
    return int(m.group(1)) if m else None


def parse_float(text):
    """Extract first float from text"""
    if text is None:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)", str(text))
    return float(m.group(1)) if m else None


def normalize_gpu(gpu_raw):
    """
    GPU 값이 dict/list/str 등 어떤 형태로 와도
    ProductDetailSpec.gpu(CharField)에 저장 가능한 단일 문자열로 정규화
    예) "NVIDIA RTX 4060 (8 GB)"
    """
    if gpu_raw is None:
        return ""

    # 이미 문자열이면 그대로
    if isinstance(gpu_raw, str):
        return gpu_raw.strip()

    # list면 첫 번째를 대표로 사용
    if isinstance(gpu_raw, list):
        return normalize_gpu(gpu_raw[0]) if gpu_raw else ""

    # dict면 대표 키 조합
    if isinstance(gpu_raw, dict):
        brand = gpu_raw.get("Brand") or gpu_raw.get("brand") or ""
        model = gpu_raw.get("Model") or gpu_raw.get("model") or gpu_raw.get("Name") or gpu_raw.get("name") or ""
        vram = (
            gpu_raw.get("VRAM")
            or gpu_raw.get("vram")
            or gpu_raw.get("Memory")
            or gpu_raw.get("memory")
            or gpu_raw.get("Video Memory")
            or ""
        )

        parts = []
        if brand:
            parts.append(str(brand).strip())
        if model:
            parts.append(str(model).strip())

        name = " ".join(parts).strip()

        # brand/model이 둘 다 없으면 dict를 문자열화(최후 fallback)
        if not name:
            name = str(gpu_raw).strip()

        if vram:
            name = f"{name} ({str(vram).strip()})"

        return name.strip()

    # 그 외 타입
    return str(gpu_raw).strip()


def parse_weight_kg(raw_weight, unit_hint=None):
    """
    weight가 다양한 형태로 들어오는 케이스를 kg로 통일:
    - "1200 g", 1200
    - "1.2 kg"
    - lb / oz
    - 단위 없이 숫자만 (대체로 g일 확률이 큼)
    """
    if raw_weight is None:
        return None

    # unit_hint가 있으면 우선 사용
    if unit_hint:
        num = parse_float(raw_weight)
        if num is None:
            return None
        hint = str(unit_hint).lower()
        if hint in ["kg", "kilogram", "kilograms"]:
            return float(num)
        if hint in ["g", "gram", "grams"]:
            return float(num) / 1000.0
        if hint in ["lb", "lbs", "pound", "pounds"]:
            return float(num) * 0.45359237
        if hint in ["oz", "ounce", "ounces"]:
            return float(num) * 0.028349523125

    s = str(raw_weight).lower().strip()
    num = parse_float(s)
    if num is None:
        return None

    # 문자열에 단위가 포함된 경우
    if "kg" in s:
        return float(num)
    if " g" in s or s.endswith("g"):
        return float(num) / 1000.0
    if "lb" in s:
        return float(num) * 0.45359237
    if "oz" in s:
        return float(num) * 0.028349523125

    # 단위가 없으면:
    # TechSpecs에서 Weight_g처럼 숫자만 오는 경우가 있어, 50 이상이면 g로 간주
    if num >= 50:
        return float(num) / 1000.0

    # 50 미만이면 kg일 수도 있어서 그대로 kg로 둠(제품 무게 1.3 같은 케이스)
    return float(num)


def extract_spec(raw):
    """
    raw_json → ProductDetailSpec dict (meta + spec)
    - meta: product_id/product_type/brand/category/model/version/release_date
      (ProductSearch 값이 비었을 때 fallback으로 사용)
    - spec: os/cpu/gpu/ram_gb/storage_gb/weight_kg/display_inch/price_text/battery_wh/charging_power_w
      (제품마다 json 구조가 다를 수 있어 여러 경로를 매핑)
    """
    data = (raw or {}).get("data", {}) or {}
    product = data.get("Product", {}) or {}

    # ✅ meta candidates (fallback용)
    product_id = get_first(
        data,
        ["Product.Product_id", "Product.Product ID", "Product.ProductId", "Product.product_id"],
        default=None,
    )
    brand = get_first(product, ["Brand", "brand"], default="")
    category_raw = get_first(product, ["Category", "category"], default="")
    category_lower = (category_raw or "").lower()

    model = get_first(product, ["Model", "Model Name", "model", "model_name"], default="")
    version = get_first(product, ["Version", "version"], default="")
    release_date = get_first(product, ["ReleaseDate", "Release Date", "release_date"], default="")

    # ✅ product_type 판정 (models.py choices와 통일)
    product_type = "unknown"
    if "laptop" in category_lower:
        product_type = "laptop"
    elif "desktop" in category_lower:
        product_type = "desktop"
    elif "all-in-one" in category_lower or "allinone" in category_lower or "aio" in category_lower:
        product_type = "allinone"

    # ✅ OS
    os = get_first(
        data,
        [
            "Inside.Software.OS",
            "Key Aspects.OS",
            "Software.OS",
            "Inside.Operating System",
            "KeyAspects.OS",
        ],
        default="",
    )

    # ✅ CPU
    cpu = get_first(
        data,
        [
            "Inside.Processor.CPU",
            "Key Aspects.Processor",
            "Processor.CPU",
            "Inside.CPU",
            "KeyAspects.Processor",
        ],
        default="",
    )

    # ✅ GPU (dict/list/str 모두 정규화)
    gpu_raw = get_first(
        data,
        [
            "Inside.Processor.GPU",
            "Graphics.GPU",
            "Processor.GPU",
            "Inside.GPU",
        ],
        default=None,
    )
    gpu = normalize_gpu(gpu_raw)

    # ✅ RAM / Storage
    ram_raw = get_first(
        data,
        [
            "Inside.RAM.Capacity",
            "Key Aspects.RAM",
            "Memory.RAM",
            "Inside.Memory.RAM",
        ],
        default=None,
    )
    ram_gb = parse_int(ram_raw)

    storage_raw = get_first(
        data,
        [
            "Inside.Storage.Capacity",
            "Key Aspects.Storage",
            "Storage.Capacity",
            "Inside.Storage.Total",
        ],
        default=None,
    )
    storage_gb = parse_int(storage_raw)

    # ✅ Weight (g/kg/lb/oz 모두 커버)
    weight_g = get_first(data, ["Design.Body.Weight_g"], default=None)
    weight_kg_direct = get_first(data, ["Design.Body.Weight_kg"], default=None)
    weight_lb = get_first(data, ["Design.Body.Weight_lb"], default=None)
    weight_oz = get_first(data, ["Design.Body.Weight_oz"], default=None)

    if weight_kg_direct is not None:
        weight_kg = parse_weight_kg(weight_kg_direct, unit_hint="kg")
    elif weight_g is not None:
        weight_kg = parse_weight_kg(weight_g, unit_hint="g")
    elif weight_lb is not None:
        weight_kg = parse_weight_kg(weight_lb, unit_hint="lb")
    elif weight_oz is not None:
        weight_kg = parse_weight_kg(weight_oz, unit_hint="oz")
    else:
        weight_candidate = get_first(
            data,
            [
                "Design.Body.Weight",
                "Design.Weight",
                "Body.Weight",
            ],
            default=None,
        )
        weight_kg = parse_weight_kg(weight_candidate)

    # ✅ Display
    display_candidate = get_first(
        data,
        [
            "Display.Diagonal_in",
            "Display.Size_in",
            "Display.Diagonal",
        ],
        default=None,
    )
    display_inch = parse_float(display_candidate)

    # ✅ Price
    price_text = get_first(
        data,
        [
            "Price.MSRP",
            "Key Aspects.MSRP",
            "Price.Price",
            "Pricing.MSRP",
        ],
        default="",
    )

    # ✅ Battery / Power
    battery_wh = parse_float(
        get_first(
            data,
            [
                "Inside.Battery.Energy_W",
                "Inside.Battery.Energy_Wh",
                "Battery.Energy_Wh",
                "Battery.Capacity_Wh",
            ],
            default=None,
        )
    )

    charging_power_w = parse_int(
        get_first(
            data,
            [
                "Inside.Battery.ChargingPower_W",
                "Power.ChargingPower_W",
                "Battery.ChargingPower_W",
                "Power.Adapter_W",
            ],
            default=None,
        )
    )

    return {
        # ✅ meta fallback
        "product_id": product_id,
        "product_type": product_type,
        "brand": brand,
        "category": category_raw,
        "model": model or "Unknown",
        "version": version,
        "release_date": release_date,
        # ✅ spec
        "os": os or "",
        "cpu": cpu or "",
        "gpu": gpu or "",
        "ram_gb": ram_gb,
        "storage_gb": storage_gb,
        "weight_kg": weight_kg,
        "display_inch": display_inch,
        "price_text": price_text or "",
        "battery_wh": battery_wh,
        "charging_power_w": charging_power_w,
    }
