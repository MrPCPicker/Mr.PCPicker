import json
import re
from datetime import datetime
from typing import Any, Dict, Optional, Tuple


def _get(d: Dict[str, Any], path: str, default=None):
    """
    path 예: "Inside.Processor.CPU"
    """
    cur: Any = d
    for key in path.split("."):
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


def _parse_gb(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    # "6 GB" / "16GB" / "6 GB, 8 GB" 등에서 첫 값만
    m = re.search(r"(\d+(?:\.\d+)?)\s*GB", text.replace(",", ""))
    if m:
        return float(m.group(1))
    return None


def _parse_storage_min_gb(text: Optional[str]) -> Optional[int]:
    if not text:
        return None
    # "128 GB, 256 GB, 512 GB" -> 128
    nums = [int(x) for x in re.findall(r"(\d+)\s*GB", text.replace(",", ""))]
    return min(nums) if nums else None


def _parse_int(value) -> Optional[int]:
    try:
        if value is None:
            return None
        return int(float(value))
    except Exception:
        return None


def _parse_float(value) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def parse_search_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    product search의 data[] 한 항목 -> ProductSearchItem에 저장할 dict
    """
    product = item.get("Product", {}) or {}
    return {
        "techspecs_id": str(product.get("id", "")),
        "brand": product.get("Brand", "") or "",
        "category": product.get("Category", "") or "",
        "model_name": product.get("Model", "") or "",
        "version": product.get("Version", "") or "",
        "thumbnail_url": (product.get("Thumbnail") or "").strip(),
        "release_date": item.get("Release Date", "") or "",
        "image_note": item.get("Image", "") or "",
    }


def parse_detail_payload(payload: Dict[str, Any]) -> Tuple[str, Dict[str, Any], str]:
    """
    product detail 응답 전체(payload)에서
    - techspecs_id
    - ProductDetail에 저장할 핵심 필드 dict
    - raw_json(text)
    """
    data = payload.get("data", {}) or {}

    # id 결정: _id 우선, 없으면 english_id
    techspecs_id = str(data.get("_id") or data.get("english_id") or "").strip()

    # 핵심 필드 추출
    brand = _get(data, "Product.Brand", "") or ""
    category = _get(data, "Product.Category", "") or ""
    model_name = _get(data, "Product.Model", "") or ""
    version = _get(data, "Product.Version", "") or ""

    os_name = _get(data, "Inside.Software.OS", "") or ""
    os_version = _get(data, "Inside.Software.OS Version", "") or ""
    cpu = _get(data, "Inside.Processor.CPU", "") or ""
    gpu = _get(data, "Inside.Processor.GPU", "") or ""

    ram_text = _get(data, "Inside.RAM.Capacity", "") or ""
    storage_text = _get(data, "Inside.Storage.Capacity", "") or ""

    weight_g = _get(data, "Design.Body.Weight_g", None)
    display_size_in = _get(data, "Display.Diagonal_in", None)

    refresh_rate_text = _get(data, "Display.Refresh Rate", None)  # "60 Hz"
    refresh_rate_hz = None
    if isinstance(refresh_rate_text, str):
        m = re.search(r"(\d+)", refresh_rate_text)
        refresh_rate_hz = int(m.group(1)) if m else None
    else:
        refresh_rate_hz = _parse_int(refresh_rate_text)

    msrp_text = _get(data, "Price.MSRP", "") or ""

    added_on_str = data.get("added_on")
    added_on = None
    if isinstance(added_on_str, str):
        # 예: "2023-02-12T22:04:16.000Z"
        try:
            added_on = datetime.fromisoformat(added_on_str.replace("Z", "+00:00"))
        except Exception:
            added_on = None

    detail_fields = {
        "techspecs_id": techspecs_id,
        "brand": brand,
        "category": category,
        "model_name": model_name,
        "version": version,
        "os": os_name,
        "os_version": os_version,
        "cpu": cpu,
        "gpu": gpu,
        "ram_gb": _parse_gb(ram_text),
        "storage_gb_min": _parse_storage_min_gb(storage_text),
        "weight_g": _parse_int(weight_g),
        "display_size_in": _parse_float(display_size_in),
        "refresh_rate_hz": refresh_rate_hz,
        "msrp_text": msrp_text,
        "added_on": added_on,
    }

    raw_json = json.dumps(data, ensure_ascii=False)
    return techspecs_id, detail_fields, raw_json
