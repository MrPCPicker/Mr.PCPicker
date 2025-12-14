# from django.shortcuts import render

# Create your views here.
import json
import re
import requests
from pprint import pprint

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .models import Product

API_ID = '693e6c6d8ea1b71b83af04d7'
API_KEY = '3a2991e9-9672-420a-b065-a35f6865fd95'

# =========================
# ✅ 네 코드 그대로 (함수 유지)
# =========================
def get_product_search():
    """
    API : GET / Product Search
    DOC : https://techspecs.readme.io/reference/search-products
    URL : https://api.techspecs.io/v5/products/search?query=&category=Desktops&brand=&keepCasing=True&machineId=&page=0&size=10
    """
    url = "https://api.techspecs.io/v5/products/search"

    params = {
        "query": "",
        "category": "Desktops",
        "brand": "",
        "keepCasing": True,
        "machineId": "",
        "page": 0,
        "size": 10
    }

    headers = {
        "accept": "application/json",
        "x-api-id": API_ID,
        "x-api-key": API_KEY,
    }

    response = requests.get(url, params=params, headers=headers)
    print(response.url)
    pprint(response.json())
    print("---------------------------------------------------")
    return response.json()


def get_product_detail(product_id):
    """
    API : GET / Product Detail
    DOC : https://techspecs.readme.io/reference/product-detail
    URL : https://api.techspecs.io/v5/products/{product_id}?lang=en&keepCasing=True
    """
    url = f"https://api.techspecs.io/v5/products/{product_id}"

    params = {
        "lang": "en",
        "keepCasing": True
    }

    headers = {
        "accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "x-api-id": API_ID,
        "x-api-key": API_KEY,
    }

    response = requests.get(url, params=params, headers=headers)
    print(response.url)
    pprint(response.json())
    print("---------------------------------------------------")
    return response.json()


# =========================
# 파싱 유틸 (DB 넣기 편하게)
# =========================
def deep_get(dct, *keys, default=None):
    cur = dct
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur


def parse_int(value):
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        m = re.search(r"-?\d+", value)
        return int(m.group()) if m else None
    return None


def parse_float(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.replace(",", "")
        m = re.search(r"-?\d+(\.\d+)?", s)
        return float(m.group()) if m else None
    return None


def map_detail_to_fields(detail_json):
    """
    detail 응답에서 "사양 비교 핵심 필드"만 꺼내서 Product 모델에 넣을 dict 생성
    """
    d = detail_json.get("data", {}) if isinstance(detail_json, dict) else {}

    product = d.get("Product", {}) or {}
    inside = d.get("Inside", {}) or {}
    cpu = inside.get("CPU", {}) or {}
    gpu = inside.get("GPU", {}) or {}
    ram = inside.get("RAM", {}) or {}
    storage = inside.get("Storage", {}) or {}
    display = d.get("Display", {}) or {}
    wireless = inside.get("Wireless", {}) or {}
    software = inside.get("Software", {}) or {}
    ports = inside.get("Ports", {}) or {}
    price = d.get("Price", {}) or {}
    thumb = d.get("Thumbnail", {}) or {}

    return {
        # IDs / basic
        "techspecs_id": d.get("_id") or product.get("english_id") or product.get("id"),
        "english_id": d.get("english_id") or product.get("english_id"),
        "brand": product.get("Brand"),
        "category": product.get("Category"),
        "model_name": product.get("Model"),
        "version": product.get("Version"),
        "product_type": product.get("Type"),

        "thumbnail_1": thumb.get("Image_1"),
        "thumbnail_2": thumb.get("Image_2"),

        # price
        "msrp": parse_float(price.get("MSRP")),

        # CPU
        "cpu_brand": cpu.get("Brand"),
        "cpu_family": cpu.get("Family"),
        "cpu_model": cpu.get("Model"),
        "cpu_cores": parse_int(cpu.get("Number of Cores")),
        "cpu_base_freq": cpu.get("Frequency"),
        "cpu_boost_freq": cpu.get("Boost Frequency"),

        # GPU
        "igpu": gpu.get("Integrated Graphics Card") or gpu.get("Integrated Card Family"),
        "dgpu": gpu.get("Dedicated Graphics Card") or gpu.get("Discrete Graphics Card"),

        # RAM
        "ram_size": ram.get("Size"),
        "ram_type": ram.get("Type"),
        "ram_clock": ram.get("Clock Speed"),
        "ram_max": ram.get("Maximum Capacity"),
        "ram_slots": parse_int(ram.get("Slots")),

        # Storage
        "storage_type": storage.get("Type"),
        "ssd_capacity": storage.get("SSD Capacity"),
        "hdd_capacity": storage.get("HDD Capacity"),

        # Display
        "display_diagonal": display.get("Diagonal"),
        "display_resolution": display.get("Resolution (H x W)"),
        "display_panel": display.get("Panel Type"),

        # Wireless / OS
        "wifi_standard": wireless.get("Top Wi-Fi Standard") or wireless.get("Wi-Fi Standard"),
        "bluetooth_version": wireless.get("Bluetooth Version"),
        "os_version": software.get("OS Version"),

        # Ports (비교에 자주 쓰는 것만)
        "usb_c": parse_int(ports.get("USB Type C 3,2 Gen 2 Ports")),
        "usb_a_gen2": parse_int(ports.get("USB Type A 3,2 Gen 2 Ports")),
        "usb_a_gen1": parse_int(ports.get("USB Type A 3,2 Gen 1 Ports")),
        "hdmi_ports": parse_int(ports.get("HDMI Ports")),
        "dp_ports": parse_int(ports.get("DisplayPorts")),
        "ethernet_ports": parse_int(ports.get("Ethernet RJ-45 Ports")),
    }


# =========================
# ✅ Views
# =========================
@csrf_exempt
@require_http_methods(["POST"])
def sync_products(request):
    """
    네 main 코드 흐름 그대로:
    - product_search 실행
    - 앞에서 N개 id 가져와서 product_detail 호출
    - DB 저장

    POST body 예:
    { "limit": 3 }  # 기본 3개
    """
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        body = {}

    limit = int(body.get("limit", 3))

    # 1) search
    response_product_search = get_product_search()

    if response_product_search.get("status") != "success":
        # 너가 겪었던 KeyError('data') 방지: 실패면 data가 없을 수 있음
        return JsonResponse(
            {"ok": False, "stage": "search", "response": response_product_search},
            status=400
        )

    data_list = response_product_search.get("data", []) or []
    data_list = data_list[:max(0, limit)]

    saved = 0
    failed = []

    # 2) detail + save
    for i in range(len(data_list)):
        product_model_id = deep_get(data_list[i], "Product", "id")
        if not product_model_id:
            failed.append({"index": i, "reason": "missing_Product.id"})
            continue

        response_product_detail = get_product_detail(product_model_id)

        if response_product_detail.get("status") != "success":
            failed.append({"index": i, "product_id": product_model_id, "reason": "detail_failed", "response": response_product_detail})
            continue

        fields = map_detail_to_fields(response_product_detail)
        techspecs_id = fields.get("techspecs_id")
        if not techspecs_id:
            failed.append({"index": i, "product_id": product_model_id, "reason": "missing_techspecs_id"})
            continue

        obj, _created = Product.objects.update_or_create(
            techspecs_id=techspecs_id,
            defaults={
                **fields,
                # ✅ 원본도 DB화(요청대로)
                "raw_search": data_list[i],
                "raw_detail": response_product_detail.get("data"),
            }
        )

        saved += 1

    return JsonResponse({"ok": True, "requested": len(data_list), "saved": saved, "failed": failed})


@require_http_methods(["GET"])
def product_list(request):
    """
    DB에 저장된 제품 목록 조회
    GET /api/products/?category=Desktops&brand=Lenovo&limit=50
    """
    qs = Product.objects.all().order_by("-fetched_at")

    category = request.GET.get("category")
    brand = request.GET.get("brand")
    limit = int(request.GET.get("limit", 50))

    if category:
        qs = qs.filter(category=category)
    if brand:
        qs = qs.filter(brand=brand)

    qs = qs[:max(1, min(limit, 200))]

    results = list(qs.values(
        "techspecs_id", "brand", "category", "model_name", "version", "product_type",
        "cpu_model", "cpu_cores", "ram_size", "storage_type", "ssd_capacity", "hdd_capacity",
        "igpu", "dgpu", "wifi_standard", "msrp", "thumbnail_1", "fetched_at"
    ))
    return JsonResponse({"ok": True, "count": len(results), "results": results})


@require_http_methods(["GET"])
def product_detail(request, techspecs_id):
    """
    DB에 저장된 특정 제품 1개 조회
    ?raw=1 -> raw_search/raw_detail 같이 내려줌
    """
    raw = request.GET.get("raw") == "1"

    try:
        p = Product.objects.get(techspecs_id=techspecs_id)
    except Product.DoesNotExist:
        return JsonResponse({"ok": False, "error": "not_found"}, status=404)

    payload = {
        "techspecs_id": p.techspecs_id,
        "english_id": p.english_id,
        "brand": p.brand,
        "category": p.category,
        "model_name": p.model_name,
        "version": p.version,
        "product_type": p.product_type,
        "thumbnail_1": p.thumbnail_1,
        "thumbnail_2": p.thumbnail_2,
        "msrp": float(p.msrp) if p.msrp is not None else None,
        "cpu_model": p.cpu_model,
        "cpu_cores": p.cpu_cores,
        "cpu_base_freq": p.cpu_base_freq,
        "cpu_boost_freq": p.cpu_boost_freq,
        "igpu": p.igpu,
        "dgpu": p.dgpu,
        "ram_size": p.ram_size,
        "ram_type": p.ram_type,
        "ram_clock": p.ram_clock,
        "ram_max": p.ram_max,
        "storage_type": p.storage_type,
        "ssd_capacity": p.ssd_capacity,
        "hdd_capacity": p.hdd_capacity,
        "display_diagonal": p.display_diagonal,
        "display_resolution": p.display_resolution,
        "display_panel": p.display_panel,
        "wifi_standard": p.wifi_standard,
        "bluetooth_version": p.bluetooth_version,
        "os_version": p.os_version,
        "ports": {
            "usb_c": p.usb_c,
            "usb_a_gen2": p.usb_a_gen2,
            "usb_a_gen1": p.usb_a_gen1,
            "hdmi_ports": p.hdmi_ports,
            "dp_ports": p.dp_ports,
            "ethernet_ports": p.ethernet_ports,
        },
        "fetched_at": p.fetched_at.isoformat() if p.fetched_at else None,
    }

    if raw:
        payload["raw_search"] = p.raw_search
        payload["raw_detail"] = p.raw_detail

    return JsonResponse({"ok": True, "product": payload})
