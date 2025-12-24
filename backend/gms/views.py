# backend/gms/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .services.gms_client import call_gms_openai
from products.models import ProductDetailSpec

import json
import re
import hashlib
import random


@api_view(["GET"])
@permission_classes([AllowAny])
def gms_test(request):
    text = call_gms_openai("컴퓨터를 추천해줘")
    return Response({"result": text})


def _normalize_lines(items):
    """
    제거되는 요소:
    - 앞의 '-', '•', '*'
    - 양쪽 공백
    => 개조식 문장만 남김
    """
    normalized = []
    for s in items or []:
        if not isinstance(s, str):
            continue
        s = s.strip()
        if not s:
            continue

        if s and s[0] in "-•*":
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


def _dedupe_lines(items, existing_keys=None, max_items=3):
    existing_keys = set(existing_keys or [])
    out = []
    for s in items or []:
        if not isinstance(s, str):
            continue
        s = s.strip()
        if not s:
            continue

        k = _key_for_dedupe(s)
        if not k:
            continue
        if k in existing_keys:
            continue

        # very simple near-duplicate guard: if one key contains the other, treat as duplicate
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
    return out, existing_keys


@api_view(["POST"])
@permission_classes([AllowAny])
def recommend_computers(request):
    """
    SearchBar 에서 입력한 니즈(query)를 받아서
    GMS 를 한 번만 호출해 추천 결과를 반환.
    """
    query = (request.data.get("query") or "").strip()
    print(f"[VIEW] recommend_computers called, query='{query}'")

    if not query:
        return Response(
            {"detail": "query 필드는 필수입니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    prompt = f"""
    당신은 컴퓨터 추천 어시스턴트입니다.

    [요구사항]을 보고, 사용자의 니즈와 권장 사양을 정리한 뒤,
    데이터베이스에서 후보를 검색할 수 있도록 조건을 구조화하세요.

    - "needs": 사용자의 상황/용도/제약을 개조식 한국어 문장으로 정리 (최대 3개)
    - "recommends": 하드웨어/성능/수치 중심 권장 사양을 개조식 한국어 문장으로 정리 (최대 3개)
    - needs / recommends 문자열에는 불릿 기호(-, •, 숫자.)를 넣지 말고 문장만 적으세요.
    - needs 항목끼리 중복 금지, recommends 항목끼리 중복 금지, needs 와 recommends 간에도 의미가 겹치지 않게 작성하세요.

    - "filters"는 아래 규칙을 따르세요.
      - min_ram_gb: 정수 또는 null
      - min_storage_gb: 정수 또는 null
      - require_gpu: true/false/null
      - cpu_keywords: 문자열 배열 (없으면 빈 배열)
      - gpu_keywords: 문자열 배열 (없으면 빈 배열)
      - preferred_types: ["laptop","desktop","aio"] 중 일부 (없으면 빈 배열)

    [요구사항]
    {query}

    아래 JSON 형식만, 추가 설명 없이 출력하세요:

    {{
      "needs": ["..."],
      "recommends": ["..."],
      "filters": {{
        "min_ram_gb": 16,
        "min_storage_gb": 512,
        "require_gpu": true,
        "cpu_keywords": ["i7", "ryzen"],
        "gpu_keywords": ["rtx"],
        "preferred_types": ["laptop"]
      }}
    }}
    """

    # 2) GMS 호출
    try:
        raw = call_gms_openai(prompt)
    except Exception as e:
        print("[ERROR] GMS 호출 실패:", repr(e))
        return Response(
            {"detail": "GMS 호출 실패", "error": str(e)},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    # 3) GMS 응답 JSON 파싱
    try:
        gms_data = json.loads(raw)
    except Exception:
        print("[ERROR] GMS 응답 JSON 파싱 실패. raw:", raw)
        return Response(
            {"detail": "GMS 응답 파싱 실패", "raw": raw},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    # 개조식 문장만 남기기
    needs = _normalize_lines(gms_data.get("needs"))
    recommends = _normalize_lines(gms_data.get("recommends"))

    needs, seen = _dedupe_lines(needs, existing_keys=None, max_items=3)
    recommends, _ = _dedupe_lines(recommends, existing_keys=seen, max_items=3)

    filters = gms_data.get("filters") or {}
    try:
        min_ram_gb = filters.get("min_ram_gb")
        min_ram_gb = int(min_ram_gb) if min_ram_gb is not None else None
    except Exception:
        min_ram_gb = None

    try:
        min_storage_gb = filters.get("min_storage_gb")
        min_storage_gb = int(min_storage_gb) if min_storage_gb is not None else None
    except Exception:
        min_storage_gb = None

    require_gpu = filters.get("require_gpu")
    if require_gpu not in (True, False, None):
        require_gpu = None

    cpu_keywords = filters.get("cpu_keywords") or []
    if not isinstance(cpu_keywords, list):
        cpu_keywords = []
    cpu_keywords = [str(x).strip() for x in cpu_keywords if str(x).strip()]

    gpu_keywords = filters.get("gpu_keywords") or []
    if not isinstance(gpu_keywords, list):
        gpu_keywords = []
    gpu_keywords = [str(x).strip() for x in gpu_keywords if str(x).strip()]

    preferred_types = filters.get("preferred_types") or []
    if not isinstance(preferred_types, list):
        preferred_types = []
    preferred_types = [t for t in preferred_types if t in ("laptop", "desktop", "aio")]

    base_qs = ProductDetailSpec.objects.filter(product_type__in=["laptop", "desktop", "aio"])

    # --- fallback: if hard filters make the pool empty/small, relax step by step ---
    qs = base_qs
    applied = {
        "preferred_types": bool(preferred_types),
        "min_ram_gb": min_ram_gb,
        "min_storage_gb": min_storage_gb,
        "require_gpu": require_gpu,
        "cpu_keywords": cpu_keywords,
        "gpu_keywords": gpu_keywords,
    }
    print(f"[RECOMMEND] parsed_filters={applied}")

    if preferred_types:
        qs_pref = qs.filter(product_type__in=preferred_types)
        if qs_pref.exists():
            qs = qs_pref
        else:
            print("[RECOMMEND] relax preferred_types (no matches)")

    if min_ram_gb is not None:
        qs_ram = qs.filter(ram_gb__gte=min_ram_gb)
        if qs_ram.count() >= 3:
            qs = qs_ram
        else:
            print("[RECOMMEND] relax min_ram_gb (matches < 3)")
            min_ram_gb = None

    if min_storage_gb is not None:
        qs_storage = qs.filter(storage_gb__gte=min_storage_gb)
        if qs_storage.count() >= 3:
            qs = qs_storage
        else:
            print("[RECOMMEND] relax min_storage_gb (matches < 3)")
            min_storage_gb = None

    if require_gpu is True:
        qs_gpu = qs.exclude(gpu__isnull=True).exclude(gpu__exact="")
        if qs_gpu.count() >= 3:
            qs = qs_gpu
        else:
            print("[RECOMMEND] relax require_gpu (matches < 3)")
            require_gpu = None

    pool = list(qs.only(
        "id",
        "product_type",
        "brand",
        "model",
        "cpu",
        "gpu",
        "ram_gb",
        "storage_gb",
        "os",
        "price_text",
    ))

    if not pool:
        # last resort: score across all products (still limited by product_type)
        print("[RECOMMEND] pool empty after relax; using base_qs")
        pool = list(base_qs.only(
            "id",
            "product_type",
            "brand",
            "model",
            "cpu",
            "gpu",
            "ram_gb",
            "storage_gb",
            "os",
            "price_text",
        ))

    def _text(s):
        return (s or "").lower()

    seed_src = json.dumps({"q": query, "filters": filters}, ensure_ascii=False, sort_keys=True)
    seed = int(hashlib.sha256(seed_src.encode("utf-8")).hexdigest()[:8], 16)
    rng = random.Random(seed)

    scored = []
    for p in pool:
        score = 0
        if preferred_types and p.product_type in preferred_types:
            score += 10
        if min_ram_gb is not None:
            if p.ram_gb is not None and p.ram_gb >= min_ram_gb:
                score += 8
                score += min(p.ram_gb - min_ram_gb, 32)
            else:
                score -= 4

        if min_storage_gb is not None:
            if p.storage_gb is not None and p.storage_gb >= min_storage_gb:
                score += 6
                score += min(p.storage_gb - min_storage_gb, 1024) // 256
            else:
                score -= 3

        cpu_text = _text(p.cpu)
        gpu_text = _text(p.gpu)
        for kw in cpu_keywords:
            if kw.lower() and kw.lower() in cpu_text:
                score += 4
        for kw in gpu_keywords:
            if kw.lower() and kw.lower() in gpu_text:
                score += 5
        if require_gpu is True:
            score += 3 if gpu_text else 0

        ram_val = p.ram_gb if p.ram_gb is not None else -1
        storage_val = p.storage_gb if p.storage_gb is not None else -1
        has_gpu = 1 if _text(p.gpu) else 0
        tie = rng.random()
        scored.append((score, ram_val, storage_val, has_gpu, tie, p.id))

    # Sort by: score desc, ram desc, storage desc, has_gpu desc, random tie-break
    scored.sort(key=lambda x: (x[0], x[1], x[2], x[3], x[4]), reverse=True)
    top_k = 50
    top_candidates = scored[:top_k] if len(scored) > top_k else scored

    # Diversity selection: sample 3 from top-K with deterministic RNG, avoiding duplicate brand+model
    id_to_prod = {p.id: p for p in pool}
    selected = []
    used_keys = set()

    def _pick_one(cands):
        if not cands:
            return None
        # weight by (score+offset) to prefer higher-scored items but still allow variety
        weights = []
        for s, r, st, hg, tie, pid in cands:
            w = max(1.0, float(s) + 10.0)
            weights.append(w)
        total = sum(weights)
        if total <= 0:
            return cands[0]
        x = rng.random() * total
        acc = 0.0
        for item, w in zip(cands, weights):
            acc += w
            if acc >= x:
                return item
        return cands[-1]

    remaining = list(top_candidates)
    for _ in range(3):
        pick = _pick_one(remaining)
        if not pick:
            break
        s, r, st, hg, tie, pid = pick
        prod = id_to_prod.get(pid)
        dedupe_key = None
        if prod is not None:
            dedupe_key = f"{(prod.brand or '').strip().lower()}|{(prod.model or '').strip().lower()}"
        if dedupe_key and dedupe_key in used_keys:
            # remove and retry next loop
            remaining = [it for it in remaining if it[5] != pid]
            continue
        selected.append(pick)
        if dedupe_key:
            used_keys.add(dedupe_key)
        remaining = [it for it in remaining if it[5] != pid]

    if len(selected) < 3:
        # fill deterministically from the top of remaining
        for item in remaining:
            if len(selected) >= 3:
                break
            s, r, st, hg, tie, pid = item
            prod = id_to_prod.get(pid)
            dedupe_key = None
            if prod is not None:
                dedupe_key = f"{(prod.brand or '').strip().lower()}|{(prod.model or '').strip().lower()}"
            if dedupe_key and dedupe_key in used_keys:
                continue
            selected.append(item)
            if dedupe_key:
                used_keys.add(dedupe_key)

    top_ids = [pid for _, _, _, _, _, pid in selected[:3]]
    top_debug = [
        {"id": pid, "score": s, "ram": r, "storage": st, "has_gpu": hg}
        for (s, r, st, hg, _, pid) in selected[:3]
    ]
    print(f"[RECOMMEND] scored_pool_size={len(pool)}, top={top_debug}")

    if not top_ids:
        return Response(
            {"detail": "조건에 맞는 추천 결과가 없습니다."},
            status=status.HTTP_404_NOT_FOUND,
        )

    db_products = ProductDetailSpec.objects.filter(id__in=top_ids)
    by_id = {p.id: p for p in db_products}

    results = []
    for pid in top_ids:
        prod = by_id.get(pid)
        if not prod:
            continue

        name = f"{prod.brand} {prod.model}".strip()
        price = prod.price_text
        image_url = ""
        cpu = prod.cpu
        gpu = prod.gpu
        ram = prod.ram_gb
        storage = prod.storage_gb

        specs = []
        if cpu:
            specs.append(f"CPU: {cpu}")
        if gpu:
            specs.append(f"GPU: {gpu}")
        if ram:
            specs.append(f"RAM: {ram}GB")
        if storage:
            specs.append(f"Storage: {storage}GB")

        results.append({
            "id": prod.id,
            "title": name,
            "price": price,
            "imageUrl": image_url,
            "specs": specs,
        })

    return Response({
        "results": results,
        "needs": needs,
        "recommends": recommends,
    })
