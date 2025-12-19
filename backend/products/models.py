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

