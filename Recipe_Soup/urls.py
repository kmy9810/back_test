from django.contrib import admin
from django.urls import path, include
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('recipe.urls')),
    path('payments/', include('pay.urls')),
    # path('users/', include('dj_rest_auth.urls')),
    path('users/', include('allauth.urls')),
    path('users/', include('users.urls')),
]
