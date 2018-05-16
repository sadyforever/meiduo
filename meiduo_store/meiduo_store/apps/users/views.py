from django.shortcuts import render

# Create your views here.

# 判断用户名或手机是否存在
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users import serializers
from users.models import User

# 判断用户名是否存在
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




