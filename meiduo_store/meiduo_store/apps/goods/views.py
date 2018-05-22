from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView

from rest_framework_extensions.cache.mixins import ListCacheResponseMixin



from goods.models import SKU
from goods.serializers import SKUSerializer

# GET /categories/(?P<category_id>\d+)/hotsk
class HotSKUListView(ListCacheResponseMixin, ListAPIView): # 热销商品经常展示,添加缓存,所谓热销就是sales字段
    """
    热销商品, 使用缓存扩展
    """
    serializer_class = SKUSerializer
    pagination_class = None

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2] # 只返回两个数据