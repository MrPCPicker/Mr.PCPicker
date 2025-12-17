

# Register your models here.

from django.contrib import admin
from .models import Laptop

@admin.register(Laptop)
class LaptopAdmin(admin.ModelAdmin):
    # 관리자 페이지 목록에서 보여줄 필드들
    list_display = ('model', 'price', 'ram', 'ssd', 'os')
    # 검색 기능 추가
    search_fields = ('model', 'graphics')