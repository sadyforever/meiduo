import random
import re

from django.shortcuts import render

# Create your views here.

# 判断用户名或手机是否存在
from django_redis import get_redis_connection
from rest_framework import status, mixins
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users import serializers
from users.models import User

# 判断用户名是否存在
from users.utils import get_user_by_account
from verifications.serializers import CheckImageCodeSerialzier
# from users.serializers import CheckSMSCodeSerializer

class UsernameCountView(APIView):
    """
    用户名数量
    """
    # GET usernames/(?P<username>\w{5,20})/count/
    def get(self, request, username):
        """
        获取指定用户名数量
        """
        count = User.objects.filter(username=username).count()
        # 并没有序列化
        data = {
            'username': username,
            'count': count
        }

        return Response(data)
# 判断手机号是否存在
class MobileCountView(APIView):
    """
    手机号数量
    """
    def get(self, request, mobile):
        """
        获取指定手机号数量
        """
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)


# 注册创建用户
class UserView(CreateAPIView):
    """
    用户注册
    """
    serializer_class = serializers.CreateUserSerializer


# 登录
# 居然不需要写视图


# 忘记密码第一步
class SMSCodeTokenView(GenericAPIView):
    """
    根据账号和图片验证码，获取发送短信的token
    """
    # GET accounts/(?P<account>\w{5,20})/sms/token/?image_code_id=xxx&text=xxx

    serializer_class = CheckImageCodeSerialzier

    def get(self, request, account):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = get_user_by_account(account)
        if user is None:
            return Response({'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 生成发送短信的access_token
        access_token = user.generate_send_sms_token()

        # 处理手机号
        mobile = re.sub(r'(\d{3})\d{4}(\d{3})', r'\1****\2', user.mobile)
        return Response({'mobile': mobile, 'access_token': access_token})




# 忘记密码第二步
# GET /sms_codes/?access_token=xxx
class SMSCodeByTokenView(APIView):
    """
    短信验证码
    """
    def get(self, request):
        """
        凭借token发送短信验证码
        """
        # 验证access_token
        access_token = request.query_params.get('access_token')
        if not access_token:
            return Response({'message': '缺少access token'}, status=status.HTTP_400_BAD_REQUEST)
        mobile = User.check_send_sms_code_token(access_token)
        # 使用的itsdangerouse模块
        # 使用一个序列化器
        # 通过手机号生成一个access_token,然后通过反序列化来验证这个token是刚才那个手机的吗
        # 如果前端乱传token也找不到手机
        if not mobile:
            return Response({'message': 'access token无效'}, status=status.HTTP_400_BAD_REQUEST)

        # 判断是否在60s内
        redis_conn = get_redis_connection('verify_codes')
        send_flag = redis_conn.get("send_flag_%s" % mobile)
        if send_flag:
            return Response({"message": "请求次数过于频繁"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # 生成短信验证码
        sms_code = "%06d" % random.randint(0, 999999)

        # 保存短信验证码与发送记录
        pl = redis_conn.pipeline()
        pl.setex("sms_%s" % mobile, 300, sms_code)
        pl.setex("send_flag_%s" % mobile, 60, 1)
        pl.execute()

        # 发送短信验证码
        # send_sms_code.delay(mobile, sms_code)
        print(sms_code)
        return Response({"message": "OK"}, status.HTTP_200_OK)




# 忘记密码第三步
# GET accounts/(?P<account>\w{5,20})/password/token/?sms_code=xxx
class PasswordTokenView(GenericAPIView):
    """
    用户帐号设置密码的token
    """
    serializer_class = serializers.CheckSMSCodeSerializer

    def get(self, request, account):
        """
        根据用户帐号获取修改密码的token
        """
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        # 生成修改用户密码的access token
        access_token = user.generate_set_password_token()

        return Response({'user_id': user.id, 'access_token': access_token})




# 忘记密码第四步
# GET users/(?P<pk>\d+)/password/?access_token=xxx
class PasswordView(mixins.UpdateModelMixin, GenericAPIView):
    """
    用户密码
    """
    queryset = User.objects.all()
    serializer_class = serializers.ResetPasswordSerializer

    def post(self, request, pk):
        return self.update(request, pk)

