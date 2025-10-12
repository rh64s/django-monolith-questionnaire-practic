from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.views.static import serve
from django.conf.urls.static import static

urlpatterns = [
    # path('polls/', include('polls.urls')),
    path('admin/', admin.site.urls),
    path('', include('polls.urls', namespace='')), #временное решение, чтобы не заполнять лишними запросами
]

# id in DEBUG mode server doesnt cache static urls
if settings.DEBUG:
    urlpatterns.append(path('static/<path:path>', never_cache(serve)))
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)