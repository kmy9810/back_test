from django.urls import path
from . import views

urlpatterns = [
  path('success', views.success),
  # path('success', views.success),
  path('fail', views.fail),
]