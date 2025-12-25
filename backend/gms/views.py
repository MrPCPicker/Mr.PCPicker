import json
import re
import hashlib
import random
from urllib.parse import quote_plus, urlparse
import os
import urllib.request
import urllib.error
import traceback
import requests
from bs4 import BeautifulSoup
import time

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

# ✅ 가격 파싱 우선 도메인 (요청: 다나와/네이버쇼핑)
PRICE_PARSE_PRIORITY_DOMAINS = [
    "danawa.com",
    "shopping.naver.com",
]

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MrPCPicker/1.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.6,en;q=0.5",
    "Connection": "close",
}

# ------------------------------------
# (유지) 쇼핑 URL 추출 함수 (SerpApi 기반)
# ------------------------------------
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


# ------------------------------------
# (유지) 기존 유틸들
# ------------------------------------
def _bing_search_first_url(query: str):
    api_key = (os.getenv("BING_SEARCH_API_KEY") or "").strip()
    if not api_key:
        return None
    endpoint = (os.getenv("BING_SEARCH_ENDPOINT") or "https://api.bing.microsoft.com/v7.0/search").strip()
    url = endpoint + "?q=" + quote_plus(query) + "&mkt=ko-KR&count=1&responseFilter=Webpages"
    req = urllib.request.Request(
        url,
        headers={"Ocp-Apim-Subscription-Key": api_key, "User-Agent": "MrPCPicker/1.0"},
        method="GET"
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            values = data.get("webPages", {}).get("value", [])
            return values[0].get("url") if values else None
    except Exception:
        return None


def _serpapi_google_shopping_first_url(query: str):
    api_key = (os.getenv("SERPAPI_API_KEY") or "").strip()
    if not api_key:
        return None
    url = f"https://serpapi.com/search.json?engine=google_shopping&hl=ko&gl=kr&num=1&q={quote_plus(query)}&api_key={quote_plus(api_key)}"
    try:
        response = requests.get(url, timeout=8)
        data = response.json()
        results = data.get("shopping_results") or []
        if not results:
            return None
        first = results[0] or {}
        return first.get("link") or first.get("product_link")
    except Exception:
        return None


@api_view(["GET"])
@permission_classes([AllowAny])
def gms_test(request):
    text = call_gms_openai("컴퓨터를 추천해줘")
    return Response({"result": text})


def _normalize_lines(items):
    normalized = []

    # ✅ string이면 줄바꿈으로 list화
    if isinstance(items, str):
        items = re.split(r"[\r\n]+", items)

    if not items or not isinstance(items, list):
        return []

    for s in items:
        if not isinstance(s, str):
            continue
        s = s.strip()
        if not s:
            continue
        if s[0] in "-•*":
            s = s[1:].lstrip()
        if s:
            normalized.append(s)

    return normalized


def _key_for_dedupe(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^0-9a-zA-Z가-힣 ]+", "", s)
    return s


def _dedupe_lines(items, existing_keys=None, max_items=3, min_items=0):
    existing_keys = set(existing_keys or [])
    out = []
    for s in items or []:
        if not isinstance(s, str):
            continue
        k = _key_for_dedupe(s)
        if not k or k in existing_keys:
            continue
        too_similar = False
        for ek in existing_keys:
            if not ek:
                continue
            if k in ek or ek in k:
                too_similar = True
                break
        if too_similar:
            continue
        out.append(s)
        existing_keys.add(k)
        if len(out) >= max_items:
            break

    # Ensure minimum items requirement
    if min_items > 0 and len(out) < min_items:
        for s in items or []:
            if not isinstance(s, str):
                continue
            if s not in out:
                out.append(s)
                if len(out) >= min_items:
                    break

    return out, existing_keys


# ------------------------------------
# ✅ 공통 helpers
# ------------------------------------
def _host(url: str) -> str:
    try:
        return (urlparse(url).netloc or "").lower()
    except Exception:
        return ""

def _is_domain(url: str, domain: str) -> bool:
    h = _host(url)
    return h == domain or h.endswith("." + domain)

def _coerce_price_value(price_text):
    if not isinstance(price_text, str):
        return None
    m = re.sub(r"[^0-9]", "", price_text)
    if not m:
        return None
    try:
        return int(m)
    except Exception:
        return None

def _fmt_krw(price_value: int) -> str:
    try:
        return f"{int(price_value):,}원"
    except Exception:
        return None


# ------------------------------------
# ✅ 썸네일 fallback: og:image
# ------------------------------------
def _extract_og_image(url: str, timeout=4) -> str:
    if not url or not isinstance(url, str):
        return None

    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout, allow_redirects=True)
        if resp.status_code != 200 or not resp.text:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        og = soup.find("meta", attrs={"property": "og:image"}) or soup.find("meta", attrs={"name": "og:image"})
        if og and og.get("content"):
            return og.get("content").strip()

        tw = soup.find("meta", attrs={"name": "twitter:image"}) or soup.find("meta", attrs={"property": "twitter:image"})
        if tw and tw.get("content"):
            return tw.get("content").strip()

        return None
    except Exception:
        return None


# ------------------------------------
# ✅ JSON-LD 기반 가격 파싱(공통)
# ------------------------------------
def _extract_price_from_jsonld(soup: BeautifulSoup):
    """
    다양한 사이트에서 공통적으로 박히는 ld+json(offers.price) 파싱
    """
    try:
        scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
        for sc in scripts:
            raw = (sc.string or sc.text or "").strip()
            if not raw:
                continue

            # jsonld가 배열/복합일 수 있음
            try:
                data = json.loads(raw)
            except Exception:
                # 가끔 여러 json이 섞인 문자열이 있을 수 있어, 간단 보정
                raw2 = raw.strip()
                if raw2.startswith("{") and raw2.endswith("}"):
                    try:
                        data = json.loads(raw2)
                    except Exception:
                        continue
                else:
                    continue

            candidates = data if isinstance(data, list) else [data]
            for item in candidates:
                if not isinstance(item, dict):
                    continue

                offers = item.get("offers")
                if isinstance(offers, list) and offers:
                    offers = offers[0]
                if isinstance(offers, dict):
                    price = offers.get("price") or offers.get("lowPrice") or offers.get("highPrice")
                    if price is not None:
                        try:
                            pv = int(float(str(price).replace(",", "").strip()))
                            return pv
                        except Exception:
                            pass

                # item 자체에 price가 박히는 케이스
                price = item.get("price")
                if price is not None:
                    try:
                        pv = int(float(str(price).replace(",", "").strip()))
                        return pv
                    except Exception:
                        pass
    except Exception:
        return None

    return None


# ------------------------------------
# ✅ 네이버쇼핑 가격 파싱
# ------------------------------------
def _parse_price_naver_shopping(html: str):
    """
    네이버쇼핑은 next-data/ld+json 등 여러 형태로 가격이 나옴.
    가능한 범위에서 최대한 잡는다.
    """
    soup = BeautifulSoup(html, "html.parser")

    # 1) JSON-LD
    pv = _extract_price_from_jsonld(soup)
    if pv:
        return pv

    # 2) meta (가끔 박힘)
    meta_amt = soup.find("meta", attrs={"property": "product:price:amount"}) or soup.find("meta", attrs={"name": "product:price:amount"})
    if meta_amt and meta_amt.get("content"):
        try:
            pv = int(float(meta_amt["content"].replace(",", "").strip()))
            return pv
        except Exception:
            pass

    # 3) __NEXT_DATA__ (네이버가 자주 씀)
    next_data = soup.find("script", id="__NEXT_DATA__")
    if next_data:
        raw = (next_data.string or next_data.text or "").strip()
        if raw:
            try:
                data = json.loads(raw)
                blob = json.dumps(data, ensure_ascii=False)
                # price: 숫자 우선
                m = re.search(r'"price"\s*:\s*([0-9]{2,})', blob)
                if m:
                    return int(m.group(1))
                m2 = re.search(r'"discountPrice"\s*:\s*([0-9]{2,})', blob)
                if m2:
                    return int(m2.group(1))
                m3 = re.search(r'"lowestPrice"\s*:\s*([0-9]{2,})', blob)
                if m3:
                    return int(m3.group(1))
            except Exception:
                pass

    # 4) HTML 텍스트에서 “원” 패턴
    text = soup.get_text(" ", strip=True)
    m = re.search(r"([0-9][0-9,]{3,})\s*원", text)
    if m:
        try:
            return int(m.group(1).replace(",", ""))
        except Exception:
            pass

    return None


# ------------------------------------
# ✅ 다나와 가격 파싱
# ------------------------------------
def _parse_price_danawa(html: str):
    """
    다나와는 페이지 타입이 여러 개.
    JSON-LD / meta / 스크립트 / 텍스트 기반으로 최대한 잡는다.
    """
    soup = BeautifulSoup(html, "html.parser")

    # 1) JSON-LD
    pv = _extract_price_from_jsonld(soup)
    if pv:
        return pv

    # 2) meta itemprop=price
    meta_price = soup.find("meta", attrs={"itemprop": "price"})
    if meta_price and meta_price.get("content"):
        try:
            return int(float(meta_price["content"].replace(",", "").strip()))
        except Exception:
            pass

    # 3) 흔한 영역/클래스 기반 (구조 바뀔 수 있음)
    # 예: .prc_c / .price_sect / .lowest_price 등에서 숫자
    possible = soup.select_one(".prc_c") or soup.select_one(".price_sect") or soup.select_one(".lowest_price")
    if possible:
        txt = possible.get_text(" ", strip=True)
        m = re.search(r"([0-9][0-9,]{3,})", txt)
        if m:
            try:
                return int(m.group(1).replace(",", ""))
            except Exception:
                pass

    # 4) 스크립트에서 price 숫자 찾기 (가끔 초기값이 박힘)
    scripts = soup.find_all("script")
    for sc in scripts[:40]:
        raw = (sc.string or sc.text or "")
        if not raw:
            continue
        # 너무 광범위하면 오탐 가능성↑이라, 키워드 있는 스크립트만 약하게 탐색
        if "price" not in raw and "lowest" not in raw and "prodPrice" not in raw:
            continue
        m = re.search(r'"(lowPrice|lowestPrice|price|finalPrice|prodPrice)"\s*:\s*([0-9]{3,})', raw)
        if m:
            try:
                return int(m.group(2))
            except Exception:
                pass

    # 5) 텍스트에서 원 패턴
    text = soup.get_text(" ", strip=True)
    m = re.search(r"([0-9][0-9,]{3,})\s*원", text)
    if m:
        try:
            return int(m.group(1).replace(",", ""))
        except Exception:
            pass

    return None


def _fetch_html(url: str, timeout=6):
    """
    사이트에 따라 요청 차단이 있을 수 있으니 headers/redirect 포함
    """
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout, allow_redirects=True)
    if resp.status_code != 200:
        return None
    # 일부는 인코딩 깨질 수 있으니 BeautifulSoup가 알아서 처리하게 text 사용
    return resp.text


# ------------------------------------
# ✅ 특정 사이트 가격 파싱(라우팅)
# ------------------------------------
def _parse_price_by_site(url: str):
    if not url:
        return None

    try:
        html = _fetch_html(url, timeout=6)
        if not html:
            return None

        if _is_domain(url, "shopping.naver.com"):
            return _parse_price_naver_shopping(html)

        if _is_domain(url, "danawa.com"):
            return _parse_price_danawa(html)

        # 다른 사이트들도 공통 JSON-LD만이라도 시도 (가능한 경우)
        soup = BeautifulSoup(html, "html.parser")
        pv = _extract_price_from_jsonld(soup)
        if pv:
            return pv

        # 마지막: 텍스트에서 원 패턴
        text = soup.get_text(" ", strip=True)
        m = re.search(r"([0-9][0-9,]{3,})\s*원", text)
        if m:
            return int(m.group(1).replace(",", ""))

        return None
    except Exception:
        return None


# ------------------------------------
# ✅ SerpApi 후보 20개에서 “가격/도메인 우선”으로 best 선택
# ------------------------------------
def _pick_best_shopping_result(results: list):
    """
    ✅ 우선순위:
    1) 다나와/네이버쇼핑 도메인 + price 있음
    2) price 있음
    3) 다나와/네이버쇼핑 도메인
    4) 기타
    """
    if not results:
        return None

    best = None
    best_score = -10**9

    for idx, r in enumerate(results):
        if not isinstance(r, dict):
            continue

        url = r.get("link") or r.get("product_link") or ""
        if not url:
            continue

        price_text = r.get("price")
        extracted = r.get("extracted_price")
        if extracted is None:
            extracted = _coerce_price_value(price_text)

        thumb = r.get("thumbnail") or r.get("thumbnail_url")
        host = _host(url)
        is_priority = any(host == d or host.endswith("." + d) for d in PRICE_PARSE_PRIORITY_DOMAINS)

        has_price_value = extracted is not None
        has_price_text = bool(price_text)

        score = 0

        # ✅ 도메인 우선점
        if is_priority:
            score += 2000

        # ✅ 가격이 최우선
        if has_price_value:
            score += 10000
        elif has_price_text:
            score += 7000

        # 썸네일은 보조
        if thumb:
            score += 30

        # 앞쪽 결과 약간 선호
        score += max(0, 25 - idx)

        if score > best_score:
            best_score = score
            best = r

    return best or (results[0] if results else None)


def _find_price_candidate(results: list):
    if not results:
        return None

    best = None
    best_score = -1

    for idx, r in enumerate(results):
        if not isinstance(r, dict):
            continue

        url = r.get("link") or r.get("product_link")
        if not url:
            continue

        price_text = r.get("price")
        price_value = r.get("extracted_price")
        if price_value is None:
            price_value = _coerce_price_value(price_text)

        if not price_text and price_value is None:
            continue

        score = 0
        if price_value is not None:
            score += 100
        if price_text:
            score += 40
        score += max(0, 25 - idx)

        if score > best_score:
            best_score = score
            best = {
                "price_text": price_text,
                "price_value": price_value,
                "url": url,
                "source": r.get("source"),
            }

    return best


def _serpapi_shopping_top_result(brand: str, model: str):
    """
    ✅ 변경점:
    - num=20
    - best 선택: 가격 + 다나와/네이버쇼핑 우선
    - best에 price 없으면: 후보에서 price만 합치기(기존 유지)
    - 최종적으로 candidates도 같이 반환 (사이트 파싱용 순회)
    """
    api_key = (os.getenv("SERPAPI_API_KEY") or "").strip()
    if not api_key:
        return None

    q = f"{brand} {model}".strip()
    params = {
        "engine": "google_shopping",
        "q": q,
        "hl": "ko",
        "gl": "kr",
        "num": 20,  # ✅ 핵심
        "api_key": api_key,
    }

    def _do_request():
        return requests.get("https://serpapi.com/search.json", params=params, timeout=8)

    try:
        resp = _do_request()

        if resp.status_code == 429:
            time.sleep(0.6)
            resp = _do_request()

        if resp.status_code != 200:
            return None

        data = resp.json() or {}
        results = data.get("shopping_results") or []
        if not results:
            return None

        best = _pick_best_shopping_result(results) or (results[0] if results else None)
        if not best or not isinstance(best, dict):
            return None

        url = best.get("link") or best.get("product_link")
        thumb = best.get("thumbnail") or best.get("thumbnail_url")
        price_text = best.get("price")
        price_value = best.get("extracted_price")
        source = best.get("source")

        if price_value is None:
            price_value = _coerce_price_value(price_text)

        # ✅ best 결과에 price 없으면 다른 후보에서 price만 가져오기
        if (not price_text) and (price_value is None):
            cand = _find_price_candidate(results)
            if cand:
                price_text = cand.get("price_text")
                price_value = cand.get("price_value")
                # url은 best 그대로 유지 (가격만 보충)
                # 단, best url이 없으면 cand url 사용
                if not url:
                    url = cand.get("url")
                if not source:
                    source = cand.get("source")

        # ✅ candidates 정리 (사이트 파싱에서 순회하기 위함)
        candidates = []
        for r in results:
            if not isinstance(r, dict):
                continue
            u = r.get("link") or r.get("product_link")
            if not u:
                continue
            candidates.append({
                "url": u,
                "host": _host(u),
                "price_text": r.get("price"),
                "price_value": r.get("extracted_price") or _coerce_price_value(r.get("price")),
                "thumbnail": r.get("thumbnail") or r.get("thumbnail_url"),
                "source": r.get("source"),
            })

        return {
            "url": url,
            "thumbnail": thumb,
            "price_text": price_text,
            "price_value": price_value,
            "source": source,
            "query": q,
            "candidates": candidates,
        }

    except Exception:
        return None


def _try_site_price_from_candidates(primary_url: str, candidates: list):
    """
    ✅ 가격 파싱 fallback:
    1) primary_url 먼저 파싱
    2) candidates 중 다나와/네이버쇼핑 우선 순회하며 파싱
    """
    # 1) primary 먼저
    pv = _parse_price_by_site(primary_url)
    if pv:
        return pv

    if not candidates:
        return None

    # 2) 우선 도메인 후보 먼저
    prioritized = []
    others = []

    for c in candidates:
        u = (c or {}).get("url")
        if not u:
            continue
        host = (c or {}).get("host") or _host(u)
        if any(host == d or host.endswith("." + d) for d in PRICE_PARSE_PRIORITY_DOMAINS):
            prioritized.append(u)
        else:
            others.append(u)

    # 중복 제거하면서 순회
    seen = set()
    ordered = []
    for u in prioritized + others:
        if u in seen:
            continue
        seen.add(u)
        ordered.append(u)

    # 너무 많이 돌면 느려지니 상한
    ordered = ordered[:8]

    for u in ordered:
        pv = _parse_price_by_site(u)
        if pv:
            return pv

    return None


# ------------------------------------
# ✅ 메인 추천 뷰
# ------------------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def recommend_computers(request):
    try:
        query = (request.data.get("query") or "").strip()
        if not query:
            return Response({"detail": "query 필드는 필수입니다."}, status=400)

        # 1) GMS 호출 및 파싱
        prompt = f"""당신은 컴퓨터 추천 어시스턴트입니다. 아래 요구사항을 보고 'needs', 'recommends', 'filters'를 포함한 JSON으로 응답하세요.\n[요구사항]\n{query}"""
        raw = call_gms_openai(prompt)

        # ✅ GMS JSON 안전 파싱
        try:
            gms_data = json.loads(raw)
        except Exception:
            m = re.search(r"\{[\s\S]*\}", raw)
            if not m:
                return Response({"detail": "GMS 응답이 JSON이 아닙니다.", "raw": raw[:500]}, status=502)
            gms_data = json.loads(m.group(0))

        # 2) Needs / Recommends
        raw_needs = gms_data.get("needs", [])
        raw_recommends = gms_data.get("recommends", [])

        norm_needs = _normalize_lines(raw_needs)
        norm_recommends = _normalize_lines(raw_recommends)

        needs, seen = _dedupe_lines(norm_needs, max_items=6, min_items=3)
        recommends, _ = _dedupe_lines(norm_recommends, existing_keys=seen, max_items=6, min_items=3)

        # 3) 필터
        filters = gms_data.get("filters") or {}
        min_ram = filters.get("min_ram_gb")
        min_storage = filters.get("min_storage_gb")
        preferred_types = [t for t in (filters.get("preferred_types") or []) if t in ("laptop", "desktop", "aio")]

        base_qs = ProductDetailSpec.objects.filter(product_type__in=["laptop", "desktop", "aio"])
        qs = base_qs

        # 필터 완화 로직 유지
        if preferred_types:
            qs_pref = qs.filter(product_type__in=preferred_types)
            if qs_pref.exists():
                qs = qs_pref
        if min_ram:
            qs_ram = qs.filter(ram_gb__gte=int(min_ram))
            if qs_ram.count() >= 3:
                qs = qs_ram
        if min_storage:
            qs_storage = qs.filter(storage_gb__gte=int(min_storage))
            if qs_storage.count() >= 3:
                qs = qs_storage

        pool = list(qs.only(
            "id", "brand", "model", "cpu", "gpu", "ram_gb", "storage_gb", "price_text", "product_type"
        )[:100])
        if not pool:
            pool = list(base_qs[:50])

        # 4) 스코어링 및 다양성 선택
        seed_src = json.dumps({"q": query, "f": filters}, sort_keys=True, ensure_ascii=False)
        seed = int(hashlib.sha256(seed_src.encode()).hexdigest()[:8], 16)
        rng = random.Random(seed)

        scored = []
        for p in pool:
            score = 0
            if preferred_types and p.product_type in preferred_types:
                score += 10
            if min_ram and (p.ram_gb or 0) >= int(min_ram):
                score += 3
            if min_storage and (p.storage_gb or 0) >= int(min_storage):
                score += 2
            tie = rng.random()
            scored.append((score, p.ram_gb or 0, tie, p.id))

        scored.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)

        id_to_prod = {p.id: p for p in pool}
        selected_ids = []
        used_brands = set()
        for item in scored:
            pid = item[3]
            p = id_to_prod.get(pid)
            if not p:
                continue
            brand_key = (p.brand or "").lower().strip()
            if brand_key and brand_key in used_brands:
                continue
            selected_ids.append(pid)
            if brand_key:
                used_brands.add(brand_key)
            if len(selected_ids) >= 3:
                break

        if len(selected_ids) < 3:
            for item in scored:
                if item[3] not in selected_ids:
                    selected_ids.append(item[3])
                if len(selected_ids) >= 3:
                    break

        # 5) 최종 결과 생성 (SerpApi + 특정 사이트 가격 파싱)
        results = []
        final_db_prods = ProductDetailSpec.objects.filter(id__in=selected_ids)
        by_id = {p.id: p for p in final_db_prods}

        for pid in selected_ids:
            p = by_id.get(pid)
            if not p:
                continue

            shopping = _serpapi_shopping_top_result(p.brand, p.model)

            shopping_url = (shopping or {}).get("url") or _resolve_shopping_url(p.brand, p.model)
            image_url = (shopping or {}).get("thumbnail")
            price_text = (shopping or {}).get("price_text")
            price_value = (shopping or {}).get("price_value")
            source = (shopping or {}).get("source")
            candidates = (shopping or {}).get("candidates") or []

            # ✅ 썸네일 og:image fallback
            if not image_url and shopping_url:
                og_img = _extract_og_image(shopping_url, timeout=4)
                if og_img:
                    image_url = og_img

            # ✅ (핵심) 가격이 없으면: 특정 사이트 파싱으로 채우기
            if (not price_text) and (price_value is None):
                pv = _try_site_price_from_candidates(shopping_url, candidates)
                if pv:
                    price_value = pv
                    price_text = _fmt_krw(pv)

            # DB fallback
            db_price_text = p.price_text

            results.append({
                "id": p.id,
                "title": f"{p.brand} {p.model}",
                "shoppingUrl": shopping_url,
                "imageUrl": image_url,
                "price": price_text or db_price_text,
                "priceValue": price_value,
                "shoppingSource": source,
                "specs": [
                    f"CPU: {p.cpu}",
                    f"GPU: {p.gpu}",
                    f"RAM: {p.ram_gb}GB",
                    f"Storage: {p.storage_gb}GB"
                ]
            })

        return Response({
            "results": results,
            "needs": needs,
            "recommends": recommends
        })

    except Exception as e:
        traceback.print_exc()
        return Response({"detail": "서버 내부 오류", "error": str(e)}, status=500)
