from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('recipe.urls')),
    path('payments/', include('pay.urls')),
    path('users/', include('dj_rest_auth.urls')),
    path('users/', include('allauth.urls')),
    path('users/', include('users.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
