from importlib.util import find_spec

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('account/', include('accounts.urls', namespace='accounts')),
    path('account/', include('django.contrib.auth.urls')),
]

if find_spec('cookie_consent') is not None:
    urlpatterns.append(path('cookie_consent/', include('cookie_consent.urls')))

if find_spec('django_ckeditor_5') is not None:
    urlpatterns.append(path('ckeditor5/', include('django_ckeditor_5.urls')))

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)