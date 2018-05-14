import random

from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection
from django.http.response import HttpResponse

# 这个就报错,第二个没事,右键设置文件夹为源 as source
# from meiduo_store.meiduo_store.libs.captcha.captcha import captcha
from meiduo_store.libs.captcha.captcha import captcha
from verifications import serializers

from . import constants
# Create your views here.


class ImageCodeView(APIView):
    """
    图片验证码
    """
    def get(self, request, image_code_id):

        # 生成验证码图片
        text, image = captcha.generate_captcha()

        # 获取redis的连接对象
        redis_conn = get_redis_connection("verify_codes")
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return HttpResponse(image, content_type="images/jpg")




class SMSCodeView(GenericAPIView):   # 需要用到get_serializer方法
    serializer_class = serializers.CheckImageCodeSerialzier

    # GET /sms_codes/{mobile}/?image_code_id=xxx&text=xxx
    def get(self, request, mobile):
        # 校验图片验证码和发送短信的频次
        # mobile是被放到了类视图对象属性kwargs中
        # mobile在url的正则中验证
        # 所以反序列化的data中只传查询参数 query_params
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 校验通过
        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)

        # 保存验证码及发送记录
        redis_conn = get_redis_connection('verify_codes')
        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # 使用redis的pipeline管道一次执行多个命令
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 60S来控制已经发送短信
        # 让管道执行命令
        pl.execute()

        # 发送短信
        ccp = CCP()
        time = str(constants.SMS_CODE_REDIS_EXPIRES / 60)
        ccp.send_template_sms(mobile, [sms_code, time], constants.SMS_CODE_TEMP_ID)
        # 使用celery发布异步任务
        # send_sms_code.delay(mobile, sms_code)
        # print(sms_code)
        # 返回
        return Response({'message': 'OK'})

