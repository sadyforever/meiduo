thing = '新内容说明'

'''
1.短信验证码
前后端都没有问题,后端print了验证码,前段并没有倒计时
前后端分离开发,前端和后端的服务器地址是不同的,前端声明了返回json格式,后端给出的是post,有csrf验证,报错跨域问题
'''

'''
2.倒计时卡顿
视图阻塞了,使用celery异步框架工具,多线程或协程的方式,把发短信的事件委托出去
真正执行任务的是celery中的worker,worker不断出任务队列中拿出委托的任务
celery需要启动,main文件启动,config配置,执行的任务交给sms文件的tasks
'''