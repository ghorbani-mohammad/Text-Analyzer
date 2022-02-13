from django.contrib import admin
from django.urls import path, re_path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("secret-admin/", admin.site.urls),
    re_path("api/(?P<version>(v1|v2))/", include("analyzer.urls")),
]

urlpatterns += staticfiles_urlpatterns()

admin.site.site_header = "Analyzer Administration Panel"
admin.site.index_title = "Analyzer"
admin.site.site_title = "Analyzer Admin"
