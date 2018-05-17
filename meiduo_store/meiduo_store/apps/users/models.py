from django.conf import settings
from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
# django提供了验证权限模型类,自带一些常用字段

from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData

# 发送短信token的有效期
SEND_SMS_CODE_TOKEN_EXIPIRES = 300

# 修改密码token的有效期
SET_PASSWORD_TOKEN_EXPIRES = 300


class User(AbstractUser):
    """
    用户信息
    """
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')


    class Meta:
        db_table = "tb_users"
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name




    def generate_send_sms_token(self):
        """
        生成发送短信验证码的token
        """
        # 注意看导入的包,access_token是作为一种验证身份,使用itsdangerouse包
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=300)
        data = {'mobile': self.mobile}
        token = serializer.dumps(data)
        return token.decode()


    # 不需要用到用户对象,只是检验access_token,所以用静态方法
    @staticmethod
    def check_send_sms_code_token(token):
        """
        检验发送短信验证码的token
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=300)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            return data.get('mobile')







    def generate_set_password_token(self):
        """
        生成修改密码的token
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=300)
        data = {'user_id': self.id}
        token = serializer.dumps(data)
        return token.decode()




    @staticmethod
    def check_set_password_token(token, user_id):
        """
        检验设置密码的token
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=300)
        try:
            data = serializer.loads(token)
        except BadData:
            return False
        else:
            # user_id 是前端传进来的
            if user_id != str(data.get('user_id')):
                return False
            else:
                return True