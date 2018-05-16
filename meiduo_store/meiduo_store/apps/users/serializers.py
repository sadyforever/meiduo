import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from users.models import User


class CreateUserSerializer(serializers.ModelSerializer):# 继承模型类省略已有字段
    """
    创建用户序列化器,如果验证通过就是创建用户
    """
    # 模型类没有的字段需要定义
    password2 = serializers.CharField(label='确认密码', required=True, allow_null=False, allow_blank=False, write_only=True)
    sms_code = serializers.CharField(label='短信验证码', required=True, allow_null=False, allow_blank=False, write_only=True)
    allow = serializers.CharField(label='同意协议', required=True, allow_null=False, allow_blank=False, write_only=True)

    token = serializers.CharField(label='登录状态token', read_only=True)  # 增加token字段

    # 验证单一字段,虽然前端限制了,但是后端需要更严谨
    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[345789]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value
    # 验证同意协议是否勾选
    def validate_allow(self, value):
        """检验用户是否同意协议"""
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value
    # 验证多个字段    第二个参数上下一致就可以,不用必须是attrs
    def validate(self, data):
        # 判断两次密码
        if data['password'] != data['password2']:
            raise serializers.ValidationError('两次密码不一致')

        # 判断短信验证码
        redis_conn = get_redis_connection('verify_codes')
        mobile = data['mobile']

        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if data['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')

        return data


        # 以上提供反序列化的验证
        # 以下提供反序列化的保存


    def create(self, validated_data):
        """
        创建用户
        """
        # 移除数据库模型类中不存在的属性字段
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        # views直接继承于CreateAPIView,为了使用create方法
        user = super().create(validated_data)

        # 调用django的认证系统加密密码,set_password是django中auth认证提供的方法
        user.set_password(validated_data['password'])
        user.save() # 相当于对密码重新加密赋值

        # 手动为用户生成JWT token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        # 将token保存到user对象中，随着返回值返回给前端
        user.token = token



        return user





    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow','token')
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }