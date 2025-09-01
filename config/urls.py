from django.contrib import admin
from django.urls import path, include
from core.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
    path('', index, name='home'),
    
    # django-allauth API endpoints (para password reset y email verification)
    path('api/accounts/', include('allauth.account.urls')),
]
