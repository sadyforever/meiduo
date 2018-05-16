# 每次登录成功返回的内容,token就像cookie标识用户身份
import re

from django.contrib.auth.backends import ModelBackend

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }
# 需要注册 在dev中 JWT的认证





# 用户输入的用户名或手机号,都支持登录
def get_user_by_account(account):
    """
    根据帐号获取user对象
    :param account: 账号，可以是用户名，也可以是手机号
    :return: User对象 或者 None
    """
    try:
        if re.match('^1[345789]\d{9}$', account):
            # 帐号为手机号
            user = User.objects.get(mobile=account)
        else:
            # 帐号为用户名
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


# authenticate是django内置的认证系统,JWT也使用,在认证的时候先判断是手机号还是用户名,查找到用户然后核对密码
# 通过重新authenticate方法来提供支持
class UsernameMobileAuthBackend(ModelBackend):
    """
    自定义用户名或手机号认证
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)    # 传入的内容,查询用户
        if user is not None and user.check_password(password):
            return user

# 需要注册,让django使用自定义的认证