from django.contrib import admin
from django.urls import path, re_path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path("api/(?P<version>(v1|v2))/", include("analyzer.urls")),
]

urlpatterns += staticfiles_urlpatterns()
