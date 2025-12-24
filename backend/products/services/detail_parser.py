# 2️⃣ 파서 코드 (raw → spec 변환)
# products/services/detail_parser.py
import re

def _get(d, path):
    cur = d
    for p in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return cur


def parse_int(text):
    if not text:
        return None
    m = re.search(r"(\d+)", str(text))
    return int(m.group(1)) if m else None


def parse_float(text):
    if not text:
        return None
    m = re.search(r"(\d+(\.\d+)?)", str(text))
    return float(m.group(1)) if m else None


def extract_spec(raw):
    """
    raw_json → ProductDetailSpec dict
    """
    data = raw.get("data", {})

    # Product
    product = data.get("Product", {})
    brand = product.get("Brand", "")
    model = product.get("Model", "")
    category = product.get("Category", "").lower()

    product_type = "unknown"
    if "laptop" in category:
        product_type = "laptop"
    elif "desktop" in category:
        product_type = "desktop"
    elif "all-in-one" in category:
        product_type = "aio"

    # OS
    os = _get(data, "Inside.Software.OS") or _get(data, "Key Aspects.OS")

    # CPU / GPU
    cpu = _get(data, "Inside.Processor.CPU") or _get(data, "Key Aspects.Processor")
    gpu = _get(data, "Inside.Processor.GPU")

    # RAM / Storage
    ram = _get(data, "Inside.RAM.Capacity") or _get(data, "Key Aspects.RAM")
    ram_gb = parse_int(ram)

    storage = _get(data, "Inside.Storage.Capacity") or _get(data, "Key Aspects.Storage")
    storage_gb = parse_int(storage)

    # Weight / Display
    weight_kg = None
    w_g = _get(data, "Design.Body.Weight_g")
    if w_g:
        weight_kg = float(w_g) / 1000

    display = _get(data, "Display.Diagonal_in")
    display_inch = float(display) if display else None

    # Price
    price_text = _get(data, "Price.MSRP") or _get(data, "Key Aspects.MSRP") or ""

    # Battery / Power
    battery_wh = _get(data, "Inside.Battery.Energy_W")
    charging_w = _get(data, "Inside.Battery.ChargingPower_W")

    return {
        "product_type": product_type,
        "brand": brand,
        "model": model,
        "os": os or "",
        "cpu": cpu or "",
        "gpu": gpu or "",
        "ram_gb": ram_gb,
        "storage_gb": storage_gb,
        "weight_kg": weight_kg,
        "display_inch": display_inch,
        "price_text": price_text,
        "battery_wh": battery_wh,
        "charging_power_w": charging_w,
    }
