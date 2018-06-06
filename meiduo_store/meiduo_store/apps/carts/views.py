import base64
import pickle

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.serializer import CartSerializer, CartSKUSerializer, CartDeleteSerializer
from goods.models import SKU


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

    def get(self, request):
        """
        获取购物车
        """
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            # 用户已登录，从redis中读取
            redis_conn = get_redis_connection('cart')
            redis_cart = redis_conn.hgetall('cart_%s' % user.id)
            redis_cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)
            cart = {}
            for key, val in redis_cart.items():
                cart[int(key)] = {
                    'count': int(val),
                    'selected': key in redis_cart_selected
                }
        else:
            # 用户未登录，从cookie中读取
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}

        # 遍历处理购物车数据
        # 如果用户未登录并且购物车有数据
        # cart.keys 是拿出 sku_id 的列表  看一下cookie中保存的格式
        # 从sku的表中去查详细信息,得到sku商品列表
        # 但是数量和勾选状态并不是sku原表中的
        # 重新赋值 数量是购物车中的数量
        # 然后传给序列化器检验,因为用了模型类的序列化器
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']

        serializer = CartSKUSerializer(skus, many=True)
        return Response(serializer.data)

    def put(self, request):
        """
        修改购物车数据
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
            pl.hset('cart_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            else:
                pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(serializer.data)
        else:
            # 用户未登录，在cookie中保存
            # 使用pickle序列化购物车数据，pickle操作的是bytes类型
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}

            cart[sku_id] = {
                'count': count,
                'selected': selected
            }
            response = Response(serializer.data)
            response.set_cookie('cart', base64.b64encode(pickle.dumps(cart)).decode())
            return response

    def delete(self, request):
        """
        删除购物车数据
        """
        serializer = CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.data['sku_id']

        try:
            user = request.user
        except Exception:
            # 验证失败，用户未登录
            user = None

        if user is not None and user.is_authenticated:
            # 用户已登录，在redis中保存
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            pl.hdel('cart_%s' % user.id, sku_id)
            pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # 用户未登录，在cookie中保存
            response = Response(status=status.HTTP_204_NO_CONTENT)

            # 使用pickle序列化购物车数据，pickle操作的是bytes类型
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
                if sku_id in cart:
                    del cart[sku_id]
                    response.set_cookie('cart', base64.b64encode(pickle.dumps(cart)).decode())
            return response