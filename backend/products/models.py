from django.db import models

# Create your models here.
class Laptop(models.Model):
    model = models.CharField(max_length=255)
    price = models.IntegerField()  # 원 단위
    rating = models.FloatField(null=True, blank=True)

    generation = models.CharField(max_length=100)
    core = models.CharField(max_length=100)

    ram = models.IntegerField()      # GB
    ssd = models.IntegerField()      # GB

    display_size = models.FloatField(default=0.0)
    resolution_x = models.IntegerField(default=0)
    resolution_y = models.IntegerField(default=0)

    graphics = models.CharField(max_length=100)
    os = models.CharField(max_length=50)
    warranty = models.CharField(max_length=50)

# 1️⃣ models.py (3개 모델 전체)

class ProductSearch(models.Model):
    """
    TechSpecs Product Search API (고정 필드)
    """
    product_id = models.CharField(max_length=64, unique=True)
    brand = models.CharField(max_length=128)
    category = models.CharField(max_length=128)
    model = models.CharField(max_length=256)
    version = models.CharField(max_length=128, blank=True)
    thumbnail = models.URLField(blank=True)
    release_date = models.CharField(max_length=32, blank=True)
    image = models.CharField(max_length=256, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.brand}] {self.model}"

class ProductDetailRaw(models.Model):
    """
    TechSpecs Product Detail API 원본 저장
    """
    product_id = models.CharField(max_length=64, unique=True)
    raw_json = models.JSONField()

    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RAW {self.product_id}"

class ProductDetailSpec(models.Model):
    """
    추천/검색/GMS용 정규화 스펙
    """
    PRODUCT_TYPE_CHOICES = [
        ("laptop", "Laptop"),
        ("desktop", "Desktop"),
        ("aio", "All-in-One"),
        ("unknown", "Unknown"),
    ]

    product_id = models.CharField(max_length=64, unique=True)
    product_type = models.CharField(max_length=16, choices=PRODUCT_TYPE_CHOICES, default="unknown")

    brand = models.CharField(max_length=128)
    model = models.CharField(max_length=256)

    # 핵심 사양
    os = models.CharField(max_length=128, blank=True)
    cpu = models.CharField(max_length=256, blank=True)
    gpu = models.CharField(max_length=256, blank=True)
    ram_gb = models.IntegerField(null=True, blank=True)
    storage_gb = models.IntegerField(null=True, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)
    display_inch = models.FloatField(null=True, blank=True)

    # 가격 / 전원
    price_text = models.CharField(max_length=256, blank=True)
    battery_wh = models.FloatField(null=True, blank=True)
    charging_power_w = models.IntegerField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SPEC {self.product_id}"

