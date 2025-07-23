from django.contrib import admin
from django.urls import path
from core.views import index_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_view, name='home'),
]
