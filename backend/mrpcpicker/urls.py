from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('articles/', include('articles.urls')),
    path('products/', include('products.urls')),
    path("gms/", include("gms.urls")),
    path('api/', include('products.urls')),  # 'products' 앱에 있는 urls.py를 포함
]

if settings.DEBUG:
    # 개발 환경에서 /media/ 요청을 MEDIA_ROOT(업로드 폴더)에서 찾아서 응답
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
