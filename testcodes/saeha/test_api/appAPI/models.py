from django.db import models


class ProductSearchItem(models.Model):
    """
    TechSpecs product search의 data[] 한 항목을 저장.
    (status, total_results 등은 저장 안 함)
    """
    techspecs_id = models.CharField(max_length=64, unique=True, db_index=True)  # Product.id
    brand = models.CharField(max_length=128, blank=True, db_index=True)
    category = models.CharField(max_length=128, blank=True, db_index=True)
    model_name = models.CharField(max_length=256, blank=True, db_index=True)   # Product.Model
    version = models.CharField(max_length=128, blank=True, db_index=True)      # Product.Version
    thumbnail_url = models.URLField(blank=True)                                # Product.Thumbnail
    release_date = models.CharField(max_length=64, blank=True)                 # "Release Date" (문자 그대로 보관)
    image_note = models.CharField(max_length=256, blank=True)                  # "Image" 필드가 메시지일 수도 있어서

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"[{self.brand}] {self.model_name} ({self.version})"


class ProductDetail(models.Model):
    """
    TechSpecs product detail의 data{}를 저장.
    - 핵심 컬럼(추천/필터/정렬용)
    - 나머지는 raw_json에 통째로 저장
    """
    # search item과 1:1로 연결(없을 수도 있으니 null 허용)
    search_item = models.OneToOneField(
        ProductSearchItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="detail",
    )

    techspecs_id = models.CharField(max_length=64, unique=True, db_index=True)  # detail의 _id(or english_id)
    brand = models.CharField(max_length=128, blank=True, db_index=True)
    category = models.CharField(max_length=128, blank=True, db_index=True)
    model_name = models.CharField(max_length=256, blank=True, db_index=True)
    version = models.CharField(max_length=128, blank=True, db_index=True)

    # 추천에 자주 쓰는 핵심들(예시)
    os = models.CharField(max_length=128, blank=True, db_index=True)            # Inside.Software.OS
    os_version = models.CharField(max_length=128, blank=True)
    cpu = models.CharField(max_length=256, blank=True, db_index=True)           # Inside.Processor.CPU
    gpu = models.CharField(max_length=256, blank=True, db_index=True)           # Inside.Processor.GPU
    ram_gb = models.FloatField(null=True, blank=True, db_index=True)            # "6 GB" -> 6
    storage_gb_min = models.IntegerField(null=True, blank=True, db_index=True)  # "128 GB, 256 GB..." -> 128
    weight_g = models.IntegerField(null=True, blank=True, db_index=True)        # Design.Body.Weight_g

    display_size_in = models.FloatField(null=True, blank=True, db_index=True)   # Display.Diagonal_in
    refresh_rate_hz = models.IntegerField(null=True, blank=True, db_index=True) # Display.Refresh Rate

    msrp_text = models.CharField(max_length=256, blank=True)                    # Price.MSRP (문자 그대로)

    # 방대한 전체 원본 저장(JSONField 가능하면 JSONField 권장)
    # SQLite에서도 Django JSONField는 가능하지만, 환경 따라 TextField가 더 안정적일 수 있어 TextField로 둠.
    raw_json = models.TextField()

    added_on = models.DateTimeField(null=True, blank=True)  # detail.added_on 파싱 가능하면 저장

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Detail: [{self.brand}] {self.model_name} ({self.version})"
