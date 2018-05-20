from django.shortcuts import render

# Create your views here.


from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Area
from .serializers import AreaSerializer, SubAreaSerializer
from rest_framework_extensions.cache.mixins import CacheResponseMixin

# Create your views here.



# 访问地址 GET /areas/
#        GET /areas/210000/
class AreasViewSet(CacheResponseMixin,ReadOnlyModelViewSet):
    """
    行政区划信息
    """
    pagination_class = None  # 区划信息不分页

    def get_queryset(self):
        """
        提供数据集
        """
        # 看一下action部分,声明视图行为
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
        # GET /areas/210000/  就不是list行为
            return Area.objects.all()

    def get_serializer_class(self):
        """
        提供序列化器
        """
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubAreaSerializer