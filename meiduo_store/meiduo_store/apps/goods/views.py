from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView

from rest_framework_extensions.cache.mixins import ListCacheResponseMixin



from goods.models import SKU
from goods.serializers import SKUSerializer, SKUIndexSerializer


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





# GET /categories/(?P<category_id>\d+)/skus?page=xxx&page_size=xxx&ordering=xxx
# 商品list页数据
from rest_framework.filters import OrderingFilter

class SKUListView(ListAPIView):
    """
    sku列表数据
    """
    # 使用之前的序列化器字段可以满足,跟热销和浏览记录是同一个,看页面需要的内容
    serializer_class = SKUSerializer
    # 有序的过滤器,DRF中的
    filter_backends = (OrderingFilter,)
    # 过滤依据的字段
    ordering_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True)

# 搜索的视图,使用haystack的视图集
from drf_haystack.viewsets import HaystackViewSet

class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]

    serializer_class = SKUIndexSerializer

