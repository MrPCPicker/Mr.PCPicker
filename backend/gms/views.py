from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .services.gms_client import call_gms_openai
from products.models import Laptop

import json


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


@api_view(["POST"])
@permission_classes([AllowAny])
def recommend_laptops(request):
    """
    SearchBar 에서 입력한 니즈(query)를 받아서
    GMS 를 한 번만 호출해 추천 결과를 반환.
    """
    query = (request.data.get("query") or "").strip()
    if not query:
        return Response(
            {"detail": "query 필드는 필수입니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 1) 후보 노트북 (개수 줄여서 토큰/크레딧 절약)
    candidates = Laptop.objects.all()[:12]

    laptop_list = []
    for lap in candidates:
        name = getattr(lap, "name", None) or getattr(lap, "model_name", "")
        brand = getattr(lap, "brand", "")
        cpu = getattr(lap, "cpu", "")
        gpu = getattr(lap, "gpu", "")
        ram = getattr(lap, "ram", "")
        storage = getattr(lap, "storage", "")
        price = getattr(lap, "price", None)

        laptop_list.append({
            "id": lap.id,
            "name": name,
            "brand": brand,
            "cpu": cpu,
            "gpu": gpu,
            "ram": ram,
            "storage": storage,
            "price": int(price) if price is not None else None,
        })

    # 2) GMS 프롬프트 (짧게 다이어트)
    prompt = f"""
당신은 노트북 쇼핑 어시스턴트입니다.

1. 아래 [사용자 요구사항]과 [후보 노트북 JSON 목록]을 보고,
   사용자에게 가장 잘 맞는 노트북 3대를 선택하세요.
2. "needs"에는 사용자의 요구/상황을 개념적으로 개조식으로 정리합니다.
   예: "대학생, 문서 작업 위주", "AfterEffect 영상 편집", "휴대성 중요"
3. "recommends"에는 가능한 한 구체적인 사양 수치를 개조식으로 적습니다.
   예: "RTX 4060 이상", "16GB RAM 이상", "512GB SSD 이상"
4. "needs"와 "recommends" 항목의 문자열에는
   불릿 기호(-, •, 숫자 등)를 넣지 말고, 문장만 작성하세요.
   (프론트엔드에서 bullet 로 렌더링됩니다.)

[사용자 요구사항]
{query}

[후보 노트북 JSON 목록]
{json.dumps(laptop_list, ensure_ascii=False)}

아래 JSON 형식으로만, 다른 설명 없이 출력하세요:

{{
  "choice_ids": [1, 2, 3],
  "needs": ["...", "..."],
  "recommends": ["...", "..."],
  "summary": "전체 추천 내용을 2~3문장 한국어로 요약"
}}
"""

    # ✅ 한 번만 GMS 호출
    raw = call_gms_openai(prompt)

    try:
        gms_data = json.loads(raw)
    except Exception:
        return Response(
            {"detail": "GMS 응답 파싱 실패", "raw": raw},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    choice_ids = (gms_data.get("choice_ids") or [])[:3]

    # 개조식 문장만 남기기
    needs = _normalize_lines(gms_data.get("needs"))
    recommends = _normalize_lines(gms_data.get("recommends"))
    summary = gms_data.get("summary") or ""

    # 3) 선택된 id 기준으로 실제 Laptop 조회
    db_laptops = Laptop.objects.filter(id__in=choice_ids)
    by_id = {lap.id: lap for lap in db_laptops}

    results = []
    for lid in choice_ids:
        lap = by_id.get(lid)
        if not lap:
            continue

        name = getattr(lap, "name", None) or getattr(lap, "model_name", "")
        price = getattr(lap, "price", None)
        image_url = getattr(lap, "image_url", "") or getattr(lap, "thumbnail_url", "")
        cpu = getattr(lap, "cpu", "")
        gpu = getattr(lap, "gpu", "")
        ram = getattr(lap, "ram", "")
        storage = getattr(lap, "storage", "")

        specs = []
        if cpu:
            specs.append(f"CPU: {cpu}")
        if gpu:
            specs.append(f"GPU: {gpu}")
        if ram:
            specs.append(f"RAM: {ram}")
        if storage:
            specs.append(f"Storage: {storage}")

        results.append({
            "id": lid,
            "title": name,
            "price": int(price) if price is not None else None,
            "imageUrl": image_url,
            "specs": specs,
        })

    return Response({
        "results": results,
        "needs": needs,
        "summary": summary,
        "recommends": recommends,
    })
