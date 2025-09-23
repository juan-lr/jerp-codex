"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static

from django.conf import settings


if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls
    admin.site.site_url = "http://127.0.0.1:8000/admin"
else:
    admin.site.site_url = 'u forgot to set me'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('accounts/', include('allauth.urls')),

    path('', include('pages.urls')),
    path('farmplanning/', include('farmplanning.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        *debug_toolbar_urls(),
        *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    ]
