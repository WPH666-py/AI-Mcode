from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.http import HttpResponse


def frontend_index(request):
    index_path = settings.FRONTEND_DIST / 'index.html'
    html = index_path.read_text(encoding='utf-8')
    inject = "<script>window.__AI_MCODE_API_BASE__='http://127.0.0.1:3032/api';window.__AI_MCODE_WS_HOST__='127.0.0.1:3031';</script>"
    html = html.replace('<head>', f'<head>{inject}', 1)
    return HttpResponse(html, content_type='text/html; charset=utf-8')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/projects/', include('apps.projects.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^assets/(?P<path>.*)$', serve, {'document_root': settings.FRONTEND_DIST / 'assets'}),
    re_path(r'^(?P<path>wechat-py-qr\.jpg\.jpg)$', serve, {'document_root': settings.FRONTEND_DIST}),
    re_path(r'^.*$', frontend_index),
]
