import pickle
import base64
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response , user):
    """
    合并请求用户的购物车数据，将未登录保存在cookie里的保存到redis中
    :param request: 用户的请求对象
    :param user: 当前登录的用户
    :param response: 响应对象，用于清楚购物车cookie
    :return:
    """
    cookie_cart = request.COOKIES.get('cart')
    if cookie_cart is not None:
        cookie_cart = pickle.loads(base64.b64decode(cookie_cart.encode()))
        redis_conn = get_redis_connection('cart')
        redis_cart = redis_conn.hgetall('cart_%s' % user.id)
        redis_cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)
        cart = {}
        for sku_id, count in redis_cart.items():
            cart[int(sku_id)] = int(count)

        for sku_id, count_selected_dict in cookie_cart.items():
            # cookie中的商品 如果和redis中的重复那就把redis中的顶掉了,不重复就都添加进redis中
            cart[sku_id] = count_selected_dict['count']
            if count_selected_dict['selected']:
                redis_cart_selected.add(sku_id)

        if cart:
            pl = redis_conn.pipeline()
            pl.hmset('cart_%s' % user.id, cart)
            pl.sadd('cart_selected_%s' % user.id, *redis_cart_selected)
            pl.execute()
        # 别忘了删除cookie中的
        response.delete_cookie('cart')
        print('redis和cookie合并成功')
    return response



# import base64
# import pickle
#
# from django_redis import get_redis_connection
#
#
# def merge_cart_cookie_to_redis(request, response, user):
#     """
#     合并购物车，cookie保存到redis中
#     :return:
#     """
#     # 从cookie中取出购物车数据
#     cart_str = request.COOKIES.get('cart')
#
#     if not cart_str:
#         print('没有在cookie中拿到cart')   # 登录页面没有把cookie带上来 withCredentials:true   QQ登录需要在回调地址的页面js中也添加
#         return response
#
#     cookie_cart = pickle.loads(base64.b64decode(cart_str.encode()))
#
#     # {
#     #     sku_id: {
#     #                 "count": xxx, // 数量
#     #             "selected": True // 是否勾选
#         # },
#         # sku_id: {
#         #     "count": xxx,
#         #     "selected": False
#         # },
#         # ...
#     # }
#
#     # 从redis中取出购物车数据
#     redis_conn = get_redis_connection('cart')
#     cart_redis = redis_conn.hgetall('cart_%s' % user.id)
#     # 把redis取出的字典的键值对数据类型 转换为int
#
#     cart = {}
#     for sku_id, count in cart_redis.items():
#         cart[int(sku_id)] = int(count)
#
#     # {
#     #     sku_id: count,
#     #     sku_id: count
#     # }
#
#     selected_sku_id_list = []
#     for sku_id, selected_count_dict in cookie_cart.items():
#         # 如果redis购物车中原有商品数据，数量覆盖，如果没有，新添记录
#         cart[sku_id] = selected_count_dict['count']
#
#         # 处理勾选状态，
#         if selected_count_dict['selected']:
#             selected_sku_id_list.append(sku_id)
#
#     # 将cookie的购物车合并到redis中
#     pl = redis_conn.pipeline()
#     pl.hmset('cart_%s' % user.id, cart)
#
#     #     selected_sku_id_list = [1,2,3,4,]
#     # pl.sadd('cart_selected_%s' % user.id, 1, 2, 3, 4)
#     pl.sadd('cart_selected_%s' % user.id, *selected_sku_id_list)
#
#     pl.execute()
#
#     # 清除cookie中的购物车数据
#     response.delete_cookie('cart')
#
#     return response
