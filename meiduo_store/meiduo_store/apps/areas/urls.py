from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from areas import views

router = DefaultRouter()
# 路由必须写areas,因为三次访问的都是用一个路由,因为省市区都是在一个表中
router.register(r'areas', views.AreasViewSet, base_name='areas')

urlpatterns = [
    # url(r'^areas/$',views.AreasViewSet.as_view()),
]

urlpatterns += router.urls