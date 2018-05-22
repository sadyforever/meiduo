from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from . import views

urlpatterns = [
    url(r'^users/$', views.UserView.as_view()),
    url(r'usernames/(?P<username>\w{5,20})/count/', views.UsernameCountView.as_view()),
    url(r'mobiles/(?P<mobile>1[345789]\d{9})/count/', views.MobileCountView.as_view()),
    # 现在是使用JWT,获取token,不是基于cookie来获取,是基于json,jwt提供了原生视图来帮助获取缓存中的token
    # 而且居然不用写视图,使用jwt默认提供的,更改其中的方法,并注册使用
    url(r'authorizations/', obtain_jwt_token, name='authorizations'),
    url(r'^accounts/(?P<account>\w{4,20})/sms/token/$', views.SMSCodeTokenView.as_view()),  # 获取发送短信验证码的token
    # GET /sms_codes/?access_token=xxx
    url(r'sms_codes/$',views.SMSCodeByTokenView.as_view()),
    url(r'^accounts/(?P<account>\w{4,20})/password/token/$', views.PasswordTokenView.as_view()),  # 获取修改密码的token
    url(r'users/(?P<pk>\d+)/password/$',views.PasswordView.as_view()),
    url(r'^user/$',views.UserDetailView.as_view()),

    url(r'^emails/$', views.EmailView.as_view()),
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),  # 用户个人中心数据

]