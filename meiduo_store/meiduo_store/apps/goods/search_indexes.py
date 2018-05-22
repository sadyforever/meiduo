from haystack import indexes

from .models import SKU

                # 必须继承于这两个类
class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """
    SKU索引数据模型类
    """
    # text模糊字段,可以通过自定义来生成,识别指明的字段    前端通过传入text参数来按照字段大范围搜索
    # 需要在模板文件夹中指明text识别的字段
    text = indexes.CharField(document=True, use_template=True)
    id = indexes.IntegerField(model_attr='id')      # 映射是通过model_attr来指明的
    name = indexes.CharField(model_attr='name')
    price = indexes.CharField(model_attr='price')
    default_image_url = indexes.CharField(model_attr='default_image_url')
    comments = indexes.IntegerField(model_attr='comments')

    def get_model(self):
        """返回建立索引的模型类"""
        return SKU

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        return self.get_model().objects.filter(is_launched=True)