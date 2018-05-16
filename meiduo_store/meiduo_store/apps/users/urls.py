from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from . import views

urlpatterns = [
    url(r'^users/$', views.UserView.as_view()),
    url(r'usernames/(?P<username>\w{5,20})/count/', views.UsernameCountView.as_view()),
    url(r'mobiles/(?P<mobile>1[345789]\d{9})/count/', views.MobileCountView.as_view()),
    # 现在是使用JWT,获取token,不是基于cookie来获取,是基于json,jwt提供了原生视图来帮助获取缓存中的token
    url(r'authorizations/', obtain_jwt_token, name='authorizations'),
]