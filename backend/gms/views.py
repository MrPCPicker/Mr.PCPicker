# backend/gms/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .services.gms_client import call_gms_openai
from products.models import ProductDetailSpec

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

    # 0) 후보 컴퓨터 목록 구성 (노트북/데스크탑/AIO)
    candidates = ProductDetailSpec.objects.filter(
        product_type__in=["laptop", "desktop", "aio"]
    )[:12]

    computer_list = []
    for pc in candidates:
        computer_list.append({
            "id": pc.id,
            "product_type": pc.product_type,
            "brand": pc.brand,
            "model": pc.model,
            "cpu": pc.cpu,
            "gpu": pc.gpu,
            "ram_gb": pc.ram_gb,
            "storage_gb": pc.storage_gb,
            "os": pc.os,
            "price_text": pc.price_text,
        })

    # 1) GMS 프롬프트를 사용해 GMS 호출
    prompt = f"""
    당신은 컴퓨터 추천 어시스턴트입니다.

    [요구사항]과 [후보 컴퓨터 목록]을 보고,
    사용자의 요구에 가장 적합한 컴퓨터 3대를 선택하세요.

    - "needs": 사용자의 상황/용도를 개조식 한국어 문장으로 정리 (예: "대학생, 문서 작업 위주")
    - "recommends": 권장 사양을 수치 중심 개조식 한국어 문장으로 작성 (예: "16GB RAM 이상")
    - needs / recommends 문자열에는 불릿 기호(-, •, 숫자.)를 넣지 말고 문장만 적으세요.

    [요구사항]
    {query}

    [후보 컴퓨터 목록]
    {json.dumps(computer_list, ensure_ascii=False)}

    아래 JSON 형식만, 추가 설명 없이 출력하세요:

    {{
      "choice_ids": [1, 2, 3],
      "needs": ["...", "..."],
      "recommends": ["...", "..."]
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

    # 최대 3개까지 사용
    choice_ids = (gms_data.get("choice_ids") or [])[:3]

    # 개조식 문장만 남기기
    needs = _normalize_lines(gms_data.get("needs"))
    recommends = _normalize_lines(gms_data.get("recommends"))

    # 4) 선택된 id 기준으로 실제 ProductDetailSpec 조회
    db_products = ProductDetailSpec.objects.filter(id__in=choice_ids)
    by_id = {p.id: p for p in db_products}

    # 5) 검색된 3개의 적합한 제품을 반환 (GMS가 준 순서 유지)
    results = []
    for pid in choice_ids:
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
