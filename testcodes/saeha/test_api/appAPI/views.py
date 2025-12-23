from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.db import transaction

from .models import ProductSearchItem, ProductDetail
from .serializers import ProductSearchItemSerializer, ProductDetailSerializer
from .services.techspecs_parsers import parse_search_item, parse_detail_payload


class ImportProductSearchResponseAPIView(APIView):
    """
    TechSpecs product search '응답 그대로'를 POST로 받아서 data[]만 저장.
    body 예:
    {
      "status":"success",
      "data":[ ... ]
    }
    """
    @transaction.atomic
    def post(self, request):
        payload = request.data
        items = payload.get("data", [])
        if not isinstance(items, list):
            return Response({"detail": "data must be a list"}, status=status.HTTP_400_BAD_REQUEST)

        created, updated, skipped = 0, 0, 0

        for item in items:
            if not isinstance(item, dict):
                skipped += 1
                continue

            data = parse_search_item(item)
            techspecs_id = data.get("techspecs_id")
            if not techspecs_id:
                skipped += 1
                continue

            obj, is_created = ProductSearchItem.objects.update_or_create(
                techspecs_id=techspecs_id,
                defaults=data,
            )
            created += 1 if is_created else 0
            updated += 0 if is_created else 1

        return Response(
            {"created": created, "updated": updated, "skipped": skipped},
            status=status.HTTP_200_OK,
        )


class ImportProductDetailResponseAPIView(APIView):
    """
    TechSpecs product detail '응답 그대로'를 POST로 받아서 data{}를 저장.
    """
    @transaction.atomic
    def post(self, request):
        payload = request.data
        techspecs_id, fields, raw_json = parse_detail_payload(payload)

        if not techspecs_id:
            return Response({"detail": "missing data._id/english_id"}, status=status.HTTP_400_BAD_REQUEST)

        # SearchItem과 연결 시도:
        # - 일반적으로 search의 Product.id와 detail._id가 같다고 가정할 수 있으면 그대로 매칭
        # - 만약 다르면, version/model+brand로 매칭하거나, 별도의 매핑 테이블이 필요
        search_item = ProductSearchItem.objects.filter(techspecs_id=techspecs_id).first()

        obj, is_created = ProductDetail.objects.update_or_create(
            techspecs_id=techspecs_id,
            defaults={
                **fields,
                "raw_json": raw_json,
                "search_item": search_item,
            },
        )

        ser = ProductDetailSerializer(obj)
        return Response(
            {"created": is_created, "detail": ser.data},
            status=status.HTTP_200_OK,
        )


class ProductSearchItemListAPIView(ListAPIView):
    queryset = ProductSearchItem.objects.all().order_by("-updated_at")
    serializer_class = ProductSearchItemSerializer


class ProductDetailListAPIView(ListAPIView):
    queryset = ProductDetail.objects.select_related("search_item").all().order_by("-updated_at")
    serializer_class = ProductDetailSerializer


class ProductDetailRetrieveAPIView(RetrieveAPIView):
    lookup_field = "techspecs_id"
    queryset = ProductDetail.objects.select_related("search_item").all()
    serializer_class = ProductDetailSerializer
