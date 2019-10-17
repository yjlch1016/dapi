# Create your tasks here
from __future__ import absolute_import, unicode_literals

from dapi.celery import app


@app.task
def debug_1():
    print("调试_1已运行！")


@app.task
def debug_2():
    print("调试_2已运行！")
