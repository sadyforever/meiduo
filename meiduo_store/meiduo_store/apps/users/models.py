from django.conf import settings
from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
# django提供了验证权限模型类,自带一些常用字段

from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData

# 发送短信token的有效期
from meiduo_store.utils.models import BaseModel

SEND_SMS_CODE_TOKEN_EXIPIRES = 300

# 修改密码token的有效期
SET_PASSWORD_TOKEN_EXPIRES = 300

        # django内置的auth用户权限验证的类
class User(AbstractUser):
    """
    用户信息
    """
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name='默认地址')

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


    # 生成验证邮箱的链接
    def generate_verify_email_url(self):
        """
        生成验证邮箱的url
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=300)
        data = {'user_id': self.id, 'email': self.email}
        token = serializer.dumps(data).decode()
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token
        return verify_url

    @staticmethod
    def check_verify_email_token(token):
        """
        检查验证邮件的token
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=300)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            email = data.get('email')
            user_id = data.get('user_id')
            try:
                user = User.objects.get(id=user_id, email=email)
            except User.DoesNotExist:
                return None
            else:
                return user





class Address(BaseModel):
    """
    用户地址
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']