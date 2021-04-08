"""
@project: PyCharm
@author: MZM
@file: urls.py
@ide: PyCharm
@time: 2021/3/18 17:19
@desc： 
"""
from django.conf.urls import url,include
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from datest import settings

def get_media_root():
    return settings.MEDIA_ROOT

router = DefaultRouter()
router.APIRootView = views.RootView
router.register(r'testcase',views.TestcaseViewset)
router.register(r'testsuite',views.TestsuiteViewset)
router.register(r'testbatch',views.TestbatchViewset)
router.register(r'debugtalk',views.DebugTalkViewset)
router.register(r'debugtalk',views.TESTREPORTViewset)
router.register(r'api',views.ApiViewset)

urlpatterns = [
    url(r'^',include(router.urls)),
    # path(r'runsuite/<int:id>/',views.runsuite),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]