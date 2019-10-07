from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, platforms
from django.utils.datetime_safe import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dapi.settings')
# 设置默认celery命令行的环境变量

app = Celery('dapi')
# 实例化celery

app.now = datetime.now
# 解决时区问题

app.config_from_object('django.conf:settings', namespace='CELERY')
# 直接从Django设置中配置Celery

app.autodiscover_tasks()
# 从所有应用中加载任务模块tasks.py

platforms.C_FORCE_ROOT = True
# 解决celery不能root用户启动的问题
