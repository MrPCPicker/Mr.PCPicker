import json
import re
import hashlib
import random
from urllib.parse import quote_plus
import os
import urllib.request
import urllib.error
import traceback
import requests

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .services.gms_client import call_gms_openai
from products.models import ProductDetailSpec

# 브랜드별 공식 도메인 정의
OFFICIAL_DOMAINS_BY_BRAND = {
    "apple": ["apple.com"],
    "asus": ["asus.com"],
    "lenovo": ["lenovo.com"],
    "hp": ["hp.com"],
    "dell": ["dell.com"],
    "msi": ["msi.com"],
    "samsung": ["samsung.com"],
    "lg": ["lg.com"],
    "acer": ["acer.com"],
    "microsoft": ["microsoft.com"],
}

# 우선순위 쇼핑몰 도메인 리스트
SHOPPING_DOMAINS = [
    "danawa.com", "coupang.com", "shopping.naver.com", "gmarket.co.kr", 
    "auction.co.kr", "11st.co.kr", "ssg.com"
]

# --- 쇼핑 URL 추출 함수 (SerpApi 기반) ---
def _resolve_shopping_url(brand: str, model: str):
    query = f"{brand} {model}".strip()
    fallback_url = "https://www.google.com/search?q=" + quote_plus(query)
    
    api_key = (os.getenv("SERPAPI_API_KEY") or "").strip()
    if not api_key:
        return fallback_url

    params = {
        "engine": "google",
        "q": query,
        "hl": "ko",
        "gl": "kr",
        "api_key": api_key
    }

    try:
        response = requests.get("https://serpapi.com/search.json", params=params, timeout=5)
        if response.status_code != 200:
            return fallback_url
            
        data = response.json()
        organic_results = data.get("organic_results", [])
        if not organic_results:
            return fallback_url

        links = [res.get("link") for res in organic_results if res.get("link")]
        
        brand_lower = (brand or "").lower()
        official_domains = OFFICIAL_DOMAINS_BY_BRAND.get(brand_lower, [])
        for link in links:
            if any(domain in link.lower() for domain in official_domains):
                return link
        
        for link in links:
            if any(shop in link.lower() for shop in SHOPPING_DOMAINS):
                return link
                
        return links[0]
    except Exception:
        return fallback_url

# --- 기존에 유지해야 할 모든 유틸리티 함수들 ---

def _bing_search_first_url(query: str):
    api_key = (os.getenv("BING_SEARCH_API_KEY") or "").strip()
    if not api_key: return None
    endpoint = (os.getenv("BING_SEARCH_ENDPOINT") or "https://api.bing.microsoft.com/v7.0/search").strip()
    url = endpoint + "?q=" + quote_plus(query) + "&mkt=ko-KR&count=1&responseFilter=Webpages"
    req = urllib.request.Request(url, headers={"Ocp-Apim-Subscription-Key": api_key, "User-Agent": "MrPCPicker/1.0"}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            values = data.get("webPages", {}).get("value", [])
            return values[0].get("url") if values else None
    except Exception: return None

def _serpapi_google_shopping_first_url(query: str):
    api_key = (os.getenv("SERPAPI_API_KEY") or "").strip()
    if not api_key: return None
    url = f"https://serpapi.com/search.json?engine=google_shopping&hl=ko&gl=kr&num=1&q={quote_plus(query)}&api_key={quote_plus(api_key)}"
    try:
        response = requests.get(url, timeout=8)
        data = response.json()
        results = data.get("shopping_results") or []
        if not results: return None
        first = results[0] or {}
        return first.get("link") or first.get("product_link")
    except Exception: return None

@api_view(["GET"])
@permission_classes([AllowAny])
def gms_test(request):
    text = call_gms_openai("컴퓨터를 추천해줘")
    return Response({"result": text})

def _normalize_lines(items):
    normalized = []
    if not items or not isinstance(items, list): return []
    for s in items:
        if not isinstance(s, str): continue
        s = s.strip()
        if not s: continue
        if s[0] in "-•*": s = s[1:].lstrip()
        if s: normalized.append(s)
    return normalized

def _key_for_dedupe(s: str) -> str:
    if not isinstance(s, str): return ""
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^0-9a-zA-Z가-힣 ]+", "", s)
    return s

def _dedupe_lines(items, existing_keys=None, max_items=3):
    existing_keys = set(existing_keys or [])
    out = []
    for s in items or []:
        if not isinstance(s, str): continue
        k = _key_for_dedupe(s)
        if not k or k in existing_keys: continue
        too_similar = False
        for ek in existing_keys:
            if not ek: continue
            if k in ek or ek in k:
                too_similar = True
                break
        if too_similar: continue
        out.append(s)
        existing_keys.add(k)
        if len(out) >= max_items: break
    return out, existing_keys

# --- 메인 추천 뷰 (로직 완전 복구) ---

@api_view(["POST"])
@permission_classes([AllowAny])
def recommend_computers(request):
    try:
        query = (request.data.get("query") or "").strip()
        if not query:
            return Response({"detail": "query 필드는 필수입니다."}, status=400)

        # 1. GMS 호출 및 파싱
        prompt = f"""당신은 컴퓨터 추천 어시스턴트입니다. 아래 요구사항을 보고 'needs', 'recommends', 'filters'를 포함한 JSON으로 응답하세요.\n[요구사항]\n{query}"""
        raw = call_gms_openai(prompt)
        gms_data = json.loads(raw)

        # 2. Needs / Recommends 파싱 및 중복제거 (데이터 누락 방지)
        raw_needs = gms_data.get("needs", [])
        raw_recommends = gms_data.get("recommends", [])
        
        norm_needs = _normalize_lines(raw_needs)
        norm_recommends = _normalize_lines(raw_recommends)
        
        needs, seen = _dedupe_lines(norm_needs, max_items=3)
        recommends, _ = _dedupe_lines(norm_recommends, existing_keys=seen, max_items=3)

        # 3. 필터 및 쿼리 로직
        filters = gms_data.get("filters") or {}
        min_ram = filters.get("min_ram_gb")
        min_storage = filters.get("min_storage_gb")
        preferred_types = [t for t in (filters.get("preferred_types") or []) if t in ("laptop", "desktop", "aio")]

        base_qs = ProductDetailSpec.objects.filter(product_type__in=["laptop", "desktop", "aio"])
        qs = base_qs

        # 필터 완화 로직 유지
        if preferred_types:
            qs_pref = qs.filter(product_type__in=preferred_types)
            if qs_pref.exists(): qs = qs_pref
        if min_ram:
            qs_ram = qs.filter(ram_gb__gte=int(min_ram))
            if qs_ram.count() >= 3: qs = qs_ram
        
        pool = list(qs.only("id", "brand", "model", "cpu", "gpu", "ram_gb", "storage_gb", "price_text", "product_type")[:100])
        if not pool: pool = list(base_qs[:50])

        # 4. 스코어링 및 다양성 선택
        seed_src = json.dumps({"q": query, "f": filters}, sort_keys=True)
        seed = int(hashlib.sha256(seed_src.encode()).hexdigest()[:8], 16)
        rng = random.Random(seed)

        scored = []
        for p in pool:
            score = 0
            if preferred_types and p.product_type in preferred_types: score += 10
            tie = rng.random()
            scored.append((score, p.ram_gb or 0, tie, p.id))
        
        scored.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
        
        # 다양성 선택
        id_to_prod = {p.id: p for p in pool}
        selected_ids = []
        used_brands = set()
        for item in scored:
            pid = item[3]
            p = id_to_prod.get(pid)
            if p.brand.lower() in used_brands: continue
            selected_ids.append(pid)
            used_brands.add(p.brand.lower())
            if len(selected_ids) >= 3: break
        
        if len(selected_ids) < 3: # 부족분 채우기
            for item in scored:
                if item[3] not in selected_ids:
                    selected_ids.append(item[3])
                if len(selected_ids) >= 3: break

        # 5. 최종 결과 생성
        results = []
        final_db_prods = ProductDetailSpec.objects.filter(id__in=selected_ids)
        by_id = {p.id: p for p in final_db_prods}

        for pid in selected_ids:
            p = by_id.get(pid)
            if not p: continue
            results.append({
                "id": p.id,
                "title": f"{p.brand} {p.model}",
                "shoppingUrl": _resolve_shopping_url(p.brand, p.model),
                "price": p.price_text,
                "specs": [f"CPU: {p.cpu}", f"GPU: {p.gpu}", f"RAM: {p.ram_gb}GB", f"Storage: {p.storage_gb}GB"]
            })

        return Response({
            "results": results, 
            "needs": needs, 
            "recommends": recommends
        })

    except Exception as e:
        traceback.print_exc()
        return Response({"detail": "서버 내부 오류", "error": str(e)}, status=500)