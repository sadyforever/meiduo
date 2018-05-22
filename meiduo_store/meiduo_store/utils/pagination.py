# 全局的分页工具

from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    # 如果传入page_size就用传入的没有就用默认的 2
    max_page_size = 20

# 需要在settings中配置 REST framework
 # 分页
 #    'DEFAULT_PAGINATION_CLASS': 'meiduo_mall.utils.pagination.StandardResultsSetPagination',