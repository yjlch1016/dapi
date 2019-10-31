from django.conf.urls import url

from interface import pyecharts

urlpatterns = [
    url('^bar/$', pyecharts.BarChartView.as_view(), name='pyecharts'),
    url('^pie/$', pyecharts.PieBarChartView.as_view(), name='pyecharts'),
    url('^index/$', pyecharts.IndexView.as_view(), name='pyecharts'),
]
