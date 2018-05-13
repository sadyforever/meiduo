# from django.conf.urls import url
#
# from verifications import views
#
# urlpatterns = [
#     url(r'image_codes/(?P<code_id>.+)/$',views.ImageCodeView.as_view())
# ]

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'image_codes/(?P<code_id>.+)/$', views.ImageCodeView.as_view()),
]