from __future__ import absolute_import, unicode_literals
from dapi.celery import app as celery_app
import pymysql

__all__ = ('celery_app',)

pymysql.install_as_MySQLdb()
# PyMySQL初始化
