import json
import re
import random
import traceback
import os
import requests

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .services.gms_client import call_gms_openai
from products.models import ProductDetailSpec


# ==================================================
# 공통 유틸
# ==================================================
def _normalize_lines(items):
    if isinstance(items, str):
        items = re.split(r"[\r\n]+", items)
    if not isinstance(items, list):
        return []
    return [s.strip("-•* ").strip() for s in items if isinstance(s, str) and s.strip()]


def _dedupe(items, max_items=6, min_items=3):
    seen = set()
    out = []
    for s in items:
        k = re.sub(r"[^0-9a-zA-Z가-힣]", "", s.lower())
        if k in seen:
            continue
        seen.add(k)
        out.append(s)
        if len(out) >= max_items:
            break
    while len(out) < min_items and items:
        for s in items:
            if s not in out:
                out.append(s)
            if len(out) >= min_items:
                break
    return out


# ==================================================
# SerpApi (절대 안 터지는 안정화 버전)
# ==================================================
def _serpapi_shopping_one(brand, model):
    """
    - 최대 3초만 대기
    - 실패하면 {} 반환 (절대 raise 안 함)
    - API 전체 실패로 이어지지 않음
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return {}

    params = {
        "engine": "google_shopping",
        "q": f"{brand} {model}",
        "hl": "ko",
        "gl": "kr",
        "num": 1,
        "api_key": api_key,
    }

    try:
        resp = requests.get(
            "https://serpapi.com/search.json",
            params=params,
            timeout=3,  # 🔥 핵심
        )

        if resp.status_code != 200:
            return {}

        data = resp.json()
        results = data.get("shopping_results") or []
        if not results:
            return {}

        r = results[0]
        return {
            "url": r.get("link") or r.get("product_link"),
            "image": r.get("thumbnail"),
            "price_text": r.get("price"),
            "price_value": r.get("extracted_price"),
            "source": r.get("source"),
        }

    except Exception:
        return {}


# ==================================================
# 추천 이유 요약 생성
# ==================================================
def _build_recommend_summary(filters, products):
    reasons = []

    if filters.get("preferred_types"):
        reasons.append("요청한 사용 목적에 맞는 기기 유형을 우선 고려")

    if filters.get("min_ram_gb"):
        reasons.append(f"RAM {filters['min_ram_gb']}GB 이상으로 개발·학습에 적합")

    if filters.get("min_storage_gb"):
        reasons.append(f"저장공간 {filters['min_storage_gb']}GB 이상 제품 위주로 선별")

    if products:
        brands = {p.brand for p in products if p.brand}
        if len(brands) >= 2:
            reasons.append("여러 브랜드 중 성능 대비 평가가 좋은 모델 중심")

    if not reasons:
        reasons.append("전반적인 성능과 가격 균형을 고려한 추천")

    return reasons[:3]


# ==================================================
# GMS 테스트 API
# ==================================================
@api_view(["GET"])
@permission_classes([AllowAny])
def gms_test(request):
    data = call_gms_openai("사무용 노트북 추천")
    return Response(data)


# ==================================================
# 메인 추천 API
# ==================================================
@api_view(["POST"])
@permission_classes([AllowAny])
def recommend_computers(request):
    try:
        query = (request.data.get("query") or "").strip()
        if not query:
            return Response({"detail": "query 필드는 필수입니다."}, status=400)

        # 1️⃣ GMS 호출
        gms_data = call_gms_openai(query)

        needs = _dedupe(_normalize_lines(gms_data.get("needs", [])))
        filters = gms_data.get("filters") or {}

        # 2️⃣ DB 필터
        qs = ProductDetailSpec.objects.all()

        if filters.get("preferred_types"):
            qs = qs.filter(product_type__in=filters["preferred_types"])
        if filters.get("min_ram_gb"):
            qs = qs.filter(ram_gb__gte=filters["min_ram_gb"])
        if filters.get("min_storage_gb"):
            qs = qs.filter(storage_gb__gte=filters["min_storage_gb"])

        pool = list(qs[:60])
        random.shuffle(pool)

        # 3️⃣ 추천 결과 생성 (쇼핑 링크 있는 제품만)
        results = []
        final_products = []

        for p in pool[:10]:
            if len(results) >= 3:
                break

            shop = _serpapi_shopping_one(p.brand, p.model)

            # 🔥 쇼핑 링크 없으면 제외
            if not shop.get("url"):
                continue

            results.append({
                "id": p.id,
                "title": f"{p.brand} {p.model}",
                "shoppingUrl": shop.get("url"),
                "imageUrl": shop.get("image"),
                "price": shop.get("price_text") or p.price_text,
                "priceValue": shop.get("price_value"),
                "shoppingSource": shop.get("source"),
                "specs": [
                    f"CPU: {p.cpu}",
                    f"GPU: {p.gpu}",
                    f"RAM: {p.ram_gb}GB",
                    f"Storage: {p.storage_gb}GB",
                ],
            })

            final_products.append(p)

        # 4️⃣ 추천 이유 요약
        recommends = _build_recommend_summary(filters, final_products)

        return Response({
            "results": results,
            "needs": needs,
            "recommends": recommends,
        })

    except Exception as e:
        traceback.print_exc()
        return Response(
            {"detail": "서버 내부 오류", "error": str(e)},
            status=500,
        )
