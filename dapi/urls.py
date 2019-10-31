"""dapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import xadmin
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from django.urls import path, include
from rest_framework import routers

from interface import views
from interface.views import ModuleListView, AddModuleView, UpdateModuleView, DeleteModuleView, CaseGroupListView, \
    InterfaceListView, AddCaseGroupView, DeleteCaseGroupView, UpdateCaseGroupView, ProductListView, AddProductView, \
    UpdateProductView, DeleteProductView, AddInterfaceView, DeleteInterfaceView, UpdateInterfaceView, \
    DebugInterfaceView, DebugCaseGroupView, IntervalScheduleListView, AddIntervalScheduleView, \
    UpdateIntervalScheduleView, DeleteIntervalScheduleView, CrontabScheduleListView, AddCrontabScheduleView, \
    UpdateCrontabScheduleView, DeleteCrontabScheduleView, PeriodicTaskListView, TaskResultListView, AddPeriodicTaskView, \
    DeletePeriodicTaskView, UpdatePeriodicTaskView, DeleteTaskResultView, PerformanceListView, AddPerformanceView, \
    UpdatePerformanceView, DeletePerformanceView, DebugPerformanceView, PerformanceResultListView, \
    DeletePerformanceResultView

router = routers.DefaultRouter()
router.register('product_info', views.ProductInfoViewSet)
router.register('module_info', views.ModuleInfoViewSet)
router.register('case_group_info', views.CaseGroupInfoViewSet)
router.register('interface_info', views.InterfaceInfoViewSet)

urlpatterns = [
    path('admin/', xadmin.site.urls),
    # 后台路由

    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # API路由

    path('login/', views.login),
    path('', views.login),
    path('home/', views.home),
    path('logout/', views.logout),
    # 登录、首页、退出路由

    path('product/', ProductListView.as_view(), name='product'),
    path('product_add/', AddProductView.as_view(), name='product_add'),
    path('product_update/', UpdateProductView.as_view(), name='product_update'),
    path('product_delete/', DeleteProductView.as_view(), name='product_delete'),
    # 产品线路由

    path('module/', ModuleListView.as_view(), name='module'),
    path('module_add/', AddModuleView.as_view(), name='module_add'),
    path('module_update/', UpdateModuleView.as_view(), name='module_update'),
    path('module_delete/', DeleteModuleView.as_view(), name='module_delete'),
    # 模块路由

    path('case_group/', CaseGroupListView.as_view(), name='case_group'),
    path('case_group_add/', AddCaseGroupView.as_view(), name='case_group_add'),
    path('case_group_update/', UpdateCaseGroupView.as_view(), name='case_group_update'),
    path('case_group_delete/', DeleteCaseGroupView.as_view(), name='case_group_delete'),
    path('case_group_debug/', DebugCaseGroupView.as_view(), name='case_group_debug'),
    path('get_case_ajax/', views.get_case_ajax),
    # 用例组路由

    path('interface/', InterfaceListView.as_view(), name='interface'),
    path('interface_add/', AddInterfaceView.as_view(), name='interface_add'),
    path('interface_update/', UpdateInterfaceView.as_view(), name='interface_update'),
    path('interface_delete/', DeleteInterfaceView.as_view(), name='interface_delete'),
    path('interface_debug/', DebugInterfaceView.as_view(), name='interface_debug'),
    # 用例路由

    path('performance/', PerformanceListView.as_view(),
         name='performance'),
    path('performance_add/', AddPerformanceView.as_view(),
         name='performance_add'),
    path('performance_update/', UpdatePerformanceView.as_view(),
         name='performance_update'),
    path('performance_delete/', DeletePerformanceView.as_view(),
         name='performance_delete'),
    path('performance_debug/', DebugPerformanceView.as_view(),
         name='performance_debug'),
    # 压测脚本路由

    path('performance_result/', PerformanceResultListView.as_view(),
         name='performance_result'),
    path('performance_result_delete/', DeletePerformanceResultView.as_view(),
         name='performance_result_delete'),
    # 压测结果路由

    path('interval_schedule/', IntervalScheduleListView.as_view(),
         name='interval_schedule'),
    path('interval_add/', AddIntervalScheduleView.as_view(),
         name='interval_add'),
    path('interval_update/', UpdateIntervalScheduleView.as_view(),
         name='interval_update'),
    path('interval_delete/', DeleteIntervalScheduleView.as_view(),
         name='interval_delete'),
    # 间隔时间路由

    path('crontab_schedule/', CrontabScheduleListView.as_view(),
         name='crontab_schedule'),
    path('crontab_add/', AddCrontabScheduleView.as_view(),
         name='crontab_add'),
    path('crontab_update/', UpdateCrontabScheduleView.as_view(),
         name='crontab_update'),
    path('crontab_delete/', DeleteCrontabScheduleView.as_view(),
         name='crontab_delete'),
    # 定时时间路由

    path('periodic_task/', PeriodicTaskListView.as_view(),
         name='periodic_task'),
    path('periodic_add/', AddPeriodicTaskView.as_view(),
         name='periodic_add'),
    path('periodic_update/', UpdatePeriodicTaskView.as_view(),
         name='periodic_update'),
    path('periodic_delete/', DeletePeriodicTaskView.as_view(),
         name='periodic_delete'),
    # 任务设置路由

    path('task_result/', TaskResultListView.as_view(),
         name='task_result'),
    path('result_delete/', DeleteTaskResultView.as_view(),
         name='result_delete'),
    # 任务结果路由

    url('^pyecharts/', include('interface.urls')),
    # pyecharts路由
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# 配置文件url转发
