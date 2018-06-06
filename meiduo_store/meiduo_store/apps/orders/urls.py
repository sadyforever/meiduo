from . import views
from django.conf.urls import url

urlpatterns = [
    url(r'orders/settlement/',views.OrderSettlementView.as_view()),
    url(r'orders/$', views.SaveOrderView.as_view()),

]