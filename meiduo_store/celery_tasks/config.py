# celery的配置信息
broker_url = "redis://127.0.0.1/14" # 任务队列地址
result_backend = "redis://127.0.0.1/15" # 结果
# 看来是结合redis缓存来的