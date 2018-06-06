import base64
import pickle

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.serializer import CartSerializer


class CartView(APIView):
    """
    购物车
    """
    def perform_authentication(self, request):
        """
        重写父类的用户验证方法，不在进入视图前就检查JWT
        无论用户是否登录都可以向购物车保存内容，判断用户是否登录，前端会把Authorazition：’’JWT’ 的请求头带上来，
        然后后端判断，但是如果没登录那内置的验证就会报错，所以重新系统内置的验证 pass
        """
        pass

    def post(self, request):
        """
        添加购物车
        """
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.data.get('sku_id')
        count = serializer.data.get('count')
        selected = serializer.data.get('selected')

        # 尝试对请求的用户进行验证
        try:
            user = request.user
        except Exception:
            # 验证失败，用户未登录
            user = None

        if user is not None and user.is_authenticated:
            # 用户已登录，在redis中保存
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            # 记录购物车商品数量
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            # 记录购物车的勾选项
            pl.sadd('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(serializer.data)
        else:
            # 用户未登录，在cookie中保存
            # {
            #     1001: { "count": 10, "selected": true},
            #     ...
            # }
            # 使用pickle序列化购物车数据，pickle操作的是bytes类型
            # 从cookie中拿出购物车如果已经存在那继续添加,如果不存在创建新的
            cart = request.COOKIES.get('cart')
            if cart is not None:
                # 获取cart键对应的值,然后编码成bytes类型,才能使用base64模块,解密成明文,然后pickle模块把bytes类型转换成python数据类型
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}
            # 因为cookie中的购物车格式是我们给到用户的所以怎么拿出来当然知道了
            # 对已经存在的商品数量增加
            sku = cart.get(sku_id)
            if sku:
                count += int(sku.get('count'))
            # 不存在的商品添加键值对
            cart[sku_id] = {
                'count': count,
                'selected': True
            }

            response = Response(serializer.data)
            # 
            response.set_cookie('cart', base64.b64encode(pickle.dumps(cart)).decode())
            return response