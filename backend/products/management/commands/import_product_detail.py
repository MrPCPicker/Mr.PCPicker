from django.core.management.base import BaseCommand
from products.models import ProductSearch, ProductDetailRaw, ProductDetailSpec
from products.services.detail_parser import extract_spec


def is_blank(v):
    """값이 비어있는지 확인 (None, 빈 문자열 등)"""
    if v is None:
        return True
    if isinstance(v, str) and v.strip() == "":
        return True
    return False


def pick_meta(ps, spec_data: dict, key: str):
    """
    메타 필드 우선순위 선택:
    1. ProductSearch 값 (우선)
    2. spec_data(Raw에서 추출한 값) (fallback)

    대상 필드: product_id, product_type, brand, category, model, version, release_date
    """
    # ProductSearch에서 먼저 확인
    if ps is not None and hasattr(ps, key):
        v = getattr(ps, key)
        if not is_blank(v):
            return v

    # spec_data에서 fallback
    v2 = (spec_data or {}).get(key)
    if not is_blank(v2):
        return v2

    return None


class Command(BaseCommand):
    help = "Parse ProductDetailRaw into ProductDetailSpec (merge ProductSearch meta + Raw spec)"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=0, help="처리할 제품 수 제한")
        parser.add_argument("--only-missing", action="store_true", help="아직 처리되지 않은 제품만")
        parser.add_argument("--product-id", type=str, default="", help="특정 제품 ID만 처리")

    def handle(self, *args, **kwargs):
        limit = int(kwargs.get("limit") or 0)
        only_missing = bool(kwargs.get("only_missing"))
        only_pid = (kwargs.get("product_id") or "").strip()

        raws = ProductDetailRaw.objects.all().order_by("-fetched_at")

        if only_pid:
            raws = raws.filter(product_id=only_pid)

        if only_missing:
            raws = raws.exclude(
                product_id__in=ProductDetailSpec.objects.values_list("product_id", flat=True)
            )

        if limit > 0:
            raws = raws[:limit]

        self.stdout.write(f"Processing {raws.count()} raw products")

        created = 0
        updated = 0
        skipped = 0

        for raw in raws:
            # 1) Raw JSON → (meta fallback + spec) 추출
            spec_data = extract_spec(raw.raw_json) or {}

            # 2) ProductSearch 메타 로드
            ps = ProductSearch.objects.filter(product_id=raw.product_id).first()

            # 3) 최종 product_id 결정 (기본 raw.product_id)
            final_product_id = pick_meta(ps, spec_data, "product_id") or raw.product_id
            if is_blank(final_product_id):
                self.stdout.write(f"Skipping raw id={raw.id} because product_id is blank")
                skipped += 1
                continue

            # 4) model은 ProductSearch 우선, 없으면 Raw fallback
            final_model = pick_meta(ps, spec_data, "model")

            # ✅ 둘 다 비었으면 skip (기존: Unknown이면 무조건 skip → 완화)
            if is_blank(final_model) or final_model == "Unknown":
                ps_model = getattr(ps, "model", None) if ps else None
                if is_blank(ps_model):
                    self.stdout.write(f"Skipping product {final_product_id} due to missing model")
                    skipped += 1
                    continue
                final_model = ps_model  # ProductSearch에 있으면 그걸 사용

            # 5) 메타 필드: ProductSearch 우선, 없으면 Raw fallback
            final_product_type = pick_meta(ps, spec_data, "product_type") or "unknown"
            if final_product_type == "aio":  # 혹시 남아있을 레거시 보정
                final_product_type = "allinone"

            final_brand = pick_meta(ps, spec_data, "brand")
            final_category = pick_meta(ps, spec_data, "category")
            final_version = pick_meta(ps, spec_data, "version") or ""
            final_release_date = pick_meta(ps, spec_data, "release_date") or ""

            # 6) 최종 데이터 구성
            merged_defaults = {
                # 메타 필드
                "product_type": final_product_type,
                "brand": final_brand,
                "category": final_category,
                "model": final_model,
                "version": final_version,
                "release_date": final_release_date,

                # 스펙 필드: ProductDetailRaw에서 여러 경로로 추출한 결과 사용
                "os": spec_data.get("os", ""),
                "cpu": spec_data.get("cpu", ""),
                "gpu": spec_data.get("gpu", ""),
                "ram_gb": spec_data.get("ram_gb"),
                "storage_gb": spec_data.get("storage_gb"),
                "weight_kg": spec_data.get("weight_kg"),
                "display_inch": spec_data.get("display_inch"),
                "price_text": spec_data.get("price_text", ""),
                "battery_wh": spec_data.get("battery_wh"),
                "charging_power_w": spec_data.get("charging_power_w"),
            }

            # 7) ProductDetailSpec 생성 또는 업데이트
            obj, is_created = ProductDetailSpec.objects.update_or_create(
                product_id=final_product_id,
                defaults=merged_defaults,
            )

            if is_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"ProductDetailSpec updated. created={created}, updated={updated}, skipped={skipped}"
            )
        )
