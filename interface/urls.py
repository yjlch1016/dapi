from django.conf.urls import url

from interface import pyecharts

urlpatterns = [
    url('^bar/$', pyecharts.ChartView.as_view(), name='pyecharts'),
    url('^index/$', pyecharts.IndexView.as_view(), name='pyecharts'),
]
