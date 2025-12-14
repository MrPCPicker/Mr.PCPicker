from django.db import models

# Create your models here.
class Product(models.Model):
    # --- identifiers / basic ---
    techspecs_id = models.CharField(max_length=64, unique=True)  # data._id or search.Product.id
    english_id = models.CharField(max_length=64, blank=True, null=True)

    brand = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    model_name = models.CharField(max_length=255, blank=True, null=True)
    version = models.CharField(max_length=255, blank=True, null=True)
    product_type = models.CharField(max_length=255, blank=True, null=True)  # e.g., All-in-One PC

    thumbnail_1 = models.URLField(blank=True, null=True)
    thumbnail_2 = models.URLField(blank=True, null=True)

    # --- price ---
    msrp = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # --- CPU ---
    cpu_brand = models.CharField(max_length=100, blank=True, null=True)
    cpu_family = models.CharField(max_length=100, blank=True, null=True)
    cpu_model = models.CharField(max_length=100, blank=True, null=True)
    cpu_cores = models.IntegerField(blank=True, null=True)
    cpu_base_freq = models.CharField(max_length=50, blank=True, null=True)   # "1 GHz"
    cpu_boost_freq = models.CharField(max_length=50, blank=True, null=True)  # "3.6 GHz"

    # --- GPU ---
    igpu = models.CharField(max_length=255, blank=True, null=True)
    dgpu = models.CharField(max_length=255, blank=True, null=True)  # 없으면 None

    # --- RAM ---
    ram_size = models.CharField(max_length=50, blank=True, null=True)         # "8 GB"
    ram_type = models.CharField(max_length=50, blank=True, null=True)         # "DDR4-SDRAM"
    ram_clock = models.CharField(max_length=50, blank=True, null=True)        # "3200 MHz"
    ram_max = models.CharField(max_length=50, blank=True, null=True)          # "64 GB"
    ram_slots = models.IntegerField(blank=True, null=True)

    # --- Storage ---
    storage_type = models.CharField(max_length=50, blank=True, null=True)     # "SSD"/"HDD"
    ssd_capacity = models.CharField(max_length=50, blank=True, null=True)     # "512 GB"
    hdd_capacity = models.CharField(max_length=50, blank=True, null=True)     # "1 TB"

    # --- Display (AIO일 때 핵심) ---
    display_diagonal = models.CharField(max_length=50, blank=True, null=True)     # '23.8"'
    display_resolution = models.CharField(max_length=50, blank=True, null=True)   # "1920 x 1080 pixels"
    display_panel = models.CharField(max_length=50, blank=True, null=True)        # "IPS"

    # --- Wireless / OS ---
    wifi_standard = models.CharField(max_length=100, blank=True, null=True)       # "Wi-Fi 6 (802.11ax)"
    bluetooth_version = models.CharField(max_length=50, blank=True, null=True)
    os_version = models.CharField(max_length=100, blank=True, null=True)

    # --- Ports (요약) ---
    usb_c = models.IntegerField(blank=True, null=True)
    usb_a_gen2 = models.IntegerField(blank=True, null=True)
    usb_a_gen1 = models.IntegerField(blank=True, null=True)
    hdmi_ports = models.IntegerField(blank=True, null=True)
    dp_ports = models.IntegerField(blank=True, null=True)
    ethernet_ports = models.IntegerField(blank=True, null=True)

    # --- keep the rest for later ---
    raw_search = models.JSONField(blank=True, null=True)   # product search 원본(선택)
    raw_detail = models.JSONField(blank=True, null=True)   # product detail 원본(보류용)

    fetched_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand} {self.model_name} ({self.version})"
