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


'''
3.JWT: json web token   判断用户登录,类cookie
session需要储存在服务器上,基于cookie来使用,同源不能跨域,比较局限

token机制,使用JWT,跨域
由三部分组成: header存放加密算法
            playload一些信息
            signature 结合只有后端有的secret_key,结合加密算法,处理playload的信息然后放在这
            secret_key只有后端有,所以请求中带上去,后端通过secret_key来解密第三部分,和第二部分是否
            一致,来判断是否被篡改,来判断用户,不需要再服务器存储了
其实是因为静态服务器是一个域名,而html文件中请求的地址又是另一个域名,当是post请求的时候,
需要csrf验证,并且必须是同源,不满足需求,所以出现JWT这种token机制,跨域就涉及到安全问题,
设置白名单CORS验证

'''


'''
4.CORS验证  类csrf验证
针对跨域请求出现的设置白名单,配置见讲义
就算设置了跨域白名单,cookie也不可能支持跨域,只是允许把cookie带上去
'''


'''
5.FastDFS分布式文件储存
就是分布式存储文件和图片的工具
由Traker集群(追踪变化) 和 Storage集群组成(存储)      
由client操作
'''


'''
6.docker:虚拟化
一个容器,就是个虚拟机,可以安装镜像,但是性能各方面更强大, 一些命令行看讲义
始终用终端来操作,没有可视化窗口
'''


'''
7.QQ登录
核心: (1) 用户在QQ登录页登录,QQ给用户标识身份的 code, 然后执行回调callback,把code发给我们
     (2) 我们用code访问QQ的服务器, QQ服务器给我们一个access_token
     (3) 用access_token向QQ服务器要一个 open_id 用户的公开信息
     
     (4) 接下来跟QQ服务器就没关系了 , 如果我们有用户信息 就和QQ信息绑定, 没有就创建信息并绑定
     
urllib模块
    urllib.parse.urlencode(query) 将query字典转换为url路径中的查询字符串
    
    urllib.parse.parse_qs(qs)  将qs查询字符串格式数据转换为python的字典
    
    urllib.request.urlopen(url, data=None)
    发送http请求，如果data为None，发送GET请求，如果data不为None，发送POST请求
    返回response响应对象，可以通过read()读取响应体数据，需要注意读取出的响应体数据为bytes类型 
'''


'''
8.CKEditor富文本编辑器
9.页面静态化
10.定时任务和手动执行脚本
11.搜索引擎elasticsearch
    使用haystack用接口的方式操作
12.接口的幂等性
    购物车:只关注用户最后传的数量,修改数据库, 无论发多少次请求,返回的结果都相同就是幂等
    非幂等
    购物车:如果每次用户+1或-1都发送请求,那每次返回的购物车数量结果都不同,这就是非幂等
13.操作cookie的模块
    pickle模块:(和json模块相似,但效率更快)
        pickle.dumps()   python数据类型 转换成  bytes类型
        pickle.loads()    bytes类型  转化成  python类型   
    base64模块:加密btyes类型的模块
        base64.b64encode  加密
        base64.b64decode  解码
14.数据库同时操作:
事务问题:(一个函数中操作多个数据库表)
并发问题:(多个用户同时访问,库存不足)

    

'''