from django.contrib import admin
from django.urls import path, include
from core.views import index_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', index_view, name='home'),
    path('', include('core.urls')),
    
    # django-allauth API endpoints (para password reset y email verification)
    path('api/accounts/', include('allauth.account.urls')),
]
