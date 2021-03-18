"""
@project: PyCharm
@author: MZM
@file: urls.py
@ide: PyCharm
@time: 2021/3/18 17:19
@desc： 
"""
from django.conf.urls import url,include
from rest_framework.routers import DefaultRouter
from . import views
from datest import settings

def get_media_root():
    return settings.MEDIA_ROOT

router = DefaultRouter()
router.APIRootView = views.RootView
router.register(r'postdata',views.PostdataViewset)
router.register(r'testcase',views.TestcaseViewset)
router.register(r'debugtalk',views.DebugTalkViewset)

urlpatterns = [
    url(r'^',include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]