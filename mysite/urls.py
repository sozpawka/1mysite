from django.contrib import admin
from django.urls import path, include

# подключаем статические медиа-файлы в режиме DEBUG
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('polls.urls')),     # корень сайта — список опросов
    path('accounts/', include('accounts.urls')),  # регистрация / профиль
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
