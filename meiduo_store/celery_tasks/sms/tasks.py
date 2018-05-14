# 发送短信的异步任务

import logging

from celery_tasks.main import app
from .yuntongxun.sms import CCP



# 验证码短信模板
SMS_CODE_TEMP_ID = 1
SMS_CODE_REDIS_EXPIRES = 300


@app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """
    发送短信任务
    :param mobile: 手机号
    :param sms_code: 验证码
    :return: None
    """
    # 发送短信
    ccp = CCP()
    time = str(SMS_CODE_REDIS_EXPIRES / 60)
    ccp.send_template_sms(mobile, [sms_code, time], SMS_CODE_TEMP_ID)
