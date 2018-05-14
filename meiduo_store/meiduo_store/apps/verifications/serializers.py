from django_redis import get_redis_connection
from redis import RedisError
from rest_framework import serializers

import logging
# 初始化logger对象,配置过,在dev模块
logger = logging.getLogger('django')

class CheckImageCodeSerialzier(serializers.Serializer):
    """
    图片验证码校验序列化器
    GenericAPIView  ->  get_seriliazer()  context

    """
    # 自定义两个字段 图片编码是UUID  text是字符串 只需要校验这两个字段 还有一个mobile字段在路由中由正则来校验
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(min_length=4, max_length=4)

    # 多个字段的is_valid验证
    def validate(self, attrs):
        """校验图片验证码是否正确"""
        image_code_id = attrs['image_code_id']
        text = attrs['text']

        # 查询redis数据库，获取真实的验证码
        redis_conn = get_redis_connection('verify_codes') # 连接名字为verify_codes,redis数据库
        real_text = redis_conn.get('img_%s' % image_code_id)  # 获取验证码的内容

        if real_text is None:
            # 过期或者不存在
            raise serializers.ValidationError('无效的图片验证码')

        # 删除redis中的图片验证码，防止用户对同一个进行多次请求验证
        # 造成用户输入错误一次,就需要获取新的,不能再次输入
        # 而且是调用视图类的时候才发生验证
        try:
            redis_conn.delete('img_%s' % image_code_id)
        except RedisError as e:
            logger.error(e) # 并不需要报给前端

        # 对比
        real_image_code = real_text.decode()  # redis中拿出的是bytes类型
        if real_image_code.lower() != text.lower():
            raise serializers.ValidationError('图片验证码错误')

        # redis中发送过短信验证码的标志 send_flag_<mobile> : 1, 由redis维护60s的有效期,有值说明刚发送过
        # mobile是在路由地址中传过来的,路由地址是视图函数中request参数后边的参数
        # 有1个context参数包含request,formet,view
        # 因为mobile是在路由中,拿出来通过context的view,在视图中拿出来
        # request后边的参数是通过kwargs拿出来
        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            raise serializers.ValidationError('发送短信次数过于频繁')
            # 如果redis中有电话号了,说明之前发过短信了
        return attrs
        # 验证通过返回attrs