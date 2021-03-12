
"""datest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path,include,re_path
from django.views.static import serve
from . import settings
from rest_framework import routers
from apitest import views
from django.views import static

router = routers.DefaultRouter()
router.register(r'postdata',views.PostdataViewset)
router.register(r'testcase',views.TestcaseViewset)
router.register(r'debugtalk',views.DebugTalkViewset)

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    re_path(r"data/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', static.serve,{'document_root': settings.STATIC_ROOT}, name='static'),
]
