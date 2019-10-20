from __future__ import absolute_import, unicode_literals
import xadmin

from django.utils.html import format_html
from django_celery_beat.models import IntervalSchedule, CrontabSchedule, ClockedSchedule, SolarSchedule, PeriodicTask
from django_celery_results.models import TaskResult
from import_export import resources
from xadmin import views
from xadmin.layout import Main, Fieldset, Side

from django.apps import apps
from xadmin.plugins.actions import BaseActionView
from xadmin.plugins.batch import BatchChangeAction

from interface.models import InterfaceInfo, ProductInfo, CaseGroupInfo, ModuleInfo


# Register your models here.


class ProductInfoResource(resources.ModelResource):
    # 导入按钮优化

    def __init__(self):
        super(ProductInfoResource, self).__init__()
        field_list = apps.get_model(
            'interface', 'ProductInfo')._meta.fields
        # 应用名与模型名
        self.verbose_name_dict = {}
        # 获取所有字段的verbose_name并存放在verbose_name_dict字典里
        for i in field_list:
            self.verbose_name_dict[i.name] = i.verbose_name

    def get_export_fields(self):
        fields = self.get_fields()
        # 默认导入导出field的column_name为字段的名称
        # 这里修改为字段的verbose_name
        for field in fields:
            field_name = self.get_field_name(field)
            if field_name in self.verbose_name_dict.keys():
                field.column_name = self.verbose_name_dict[field_name]
                # 如果设置过verbose_name，则将column_name替换为verbose_name
                # 否则维持原有的字段名
        return fields

    class Meta:
        model = ProductInfo

        skip_unchanged = True
        # 导入数据时，如果该条数据未修改过，则会忽略
        report_skipped = True
        # 在导入预览页面中显示跳过的记录

        import_id_fields = ('id',)
        # 对象标识的默认字段是id，可以选择在导入时设置哪些字段用作id

        fields = (
            'id',
            'product_name',
            'product_describe',
            'product_manager',
            'developer',
            'tester',
        )
        # 白名单

        exclude = (
            'create_time',
            'update_time',
        )
        # 黑名单


class CopyAction(BaseActionView):
    # 添加复制动作

    action_name = "copy_data"
    description = "复制所选的 %(verbose_name_plural)s"
    model_perm = 'change'
    icon = 'fa fa-facebook'

    def do_action(self, queryset):
        for qs in queryset:
            qs.id = None
            # 先让这条数据的id为空
            qs.save()
        return None


class ModuleInfoAdmin(object):
    model = ModuleInfo
    extra = 1
    # 提供1个足够的选项行，也可以提供N个
    style = "accordion"

    # 折叠

    def update_button(self, obj):
        # 修改按钮
        button_html = '<a class="icon fa fa-edit" style="color: green" href="/admin/interface/moduleinfo/%s/update/">修改</a>' % obj.id
        return format_html(button_html)

    update_button.short_description = '<span style="color: green">修改</span>'
    update_button.allow_tags = True

    def delete_button(self, obj):
        # 删除按钮
        button_html = '<a class="icon fa fa-times" style="color: blue" href="/admin/interface/moduleinfo/%s/delete/">删除</a>' % obj.id
        return format_html(button_html)

    delete_button.short_description = '<span style="color: blue">删除</span>'
    delete_button.allow_tags = True

    form_layout = (
        Main(
            Fieldset('模块信息部分',
                     'module_group', 'module_name', 'module_describe'),
        ),
        # Side(
        #     Fieldset('时间部分',
        #              'create_time', 'update_time'),
        # )
    )
    # 详情页面字段分区，请注意不是fieldsets

    list_display = [
        'id',
        'module_group',
        'module_name',
        'module_describe',
        'create_time',
        'update_time',
        'update_button',
        'delete_button',
    ]

    ordering = ("id",)
    search_fields = ("module_name",)
    list_filter = ["create_time"]
    list_display_links = ('id', 'module_group', 'module_name')
    show_detail_fields = ['module_name']
    list_editable = ['module_name']
    raw_id_fields = ('module_group',)
    list_per_page = 10

    batch_fields = (
        'module_name',
        'module_describe'
    )
    # 可批量修改的字段
    actions = [CopyAction, BatchChangeAction]
    # 列表页面，添加复制动作与批量修改动作


class ProductInfoAdmin(object):
    inlines = [ModuleInfoAdmin]

    # 使用内联显示

    def update_button(self, obj):
        # 修改按钮
        button_html = '<a class="icon fa fa-edit" style="color: green" href="/admin/interface/productinfo/%s/update/">修改</a>' % obj.id
        return format_html(button_html)

    update_button.short_description = '<span style="color: green">修改</span>'
    update_button.allow_tags = True

    def delete_button(self, obj):
        # 删除按钮
        button_html = '<a class="icon fa fa-times" style="color: blue" href="/admin/interface/productinfo/%s/delete/">删除</a>' % obj.id
        return format_html(button_html)

    delete_button.short_description = '<span style="color: blue">删除</span>'
    delete_button.allow_tags = True

    form_layout = (
        Main(
            Fieldset('产品信息部分',
                     'product_name', 'product_describe'),
            Fieldset('人员部分',
                     'product_manager', 'developer',
                     'tester'),
        ),
        # Side(
        #     Fieldset('时间部分',
        #              'create_time', 'update_time'),
        # )
    )
    # 详情页面字段分区

    list_display = [
        'id',
        'product_name',
        'product_describe',
        'product_manager',
        'developer',
        'tester',
        'module_sum',
        'create_time',
        'update_time',
        'update_button',
        'delete_button',
    ]

    ordering = ("id",)
    search_fields = ("product_name",)
    list_filter = ["product_manager", "create_time"]
    list_display_links = ('id', 'product_name')
    show_detail_fields = ['product_name']
    list_editable = ['product_name']
    list_per_page = 10

    import_export_args = {
        'import_resource_class': ProductInfoResource,
        # 'export_resource_class': ProductInfoResource,
    }
    # 列表页面，添加导入按钮
    list_export_fields = (
        'id',
        'product_name',
        'product_describe',
        'product_manager',
        'developer',
        'tester',
        'create_time'
    )
    # 列表页面，导出的字段

    batch_fields = (
        'product_name',
        'product_describe',
        'product_manager',
        'developer',
        'tester'
    )
    # 可批量修改的字段
    actions = [CopyAction, BatchChangeAction]
    # 列表页面，添加复制动作与批量修改动作

    list_bookmarks = [{
        "title": "产品书签",
        # 书签的名称
        "query": {"name": ""},
        # 过滤参数
        "order": ("-id",),
        # 排序
        "cols": (
            "product_name", "product_describe"),
        # 显示的列
        "search": "产品"
        # 搜索参数
    }]
    # 自定义书签


class InterfaceInfoAdmin(object):
    model = InterfaceInfo
    extra = 1
    # 提供1个足够的选项行，也可以提供N个
    style = "accordion"

    # 折叠

    def update_button(self, obj):
        # 修改按钮
        button_html = '<a class="icon fa fa-edit" style="color: green" href="/admin/interface/interfaceinfo/%s/update/">修改</a>' % obj.id
        return format_html(button_html)

    update_button.short_description = '<span style="color: green">修改</span>'
    update_button.allow_tags = True

    def delete_button(self, obj):
        # 删除按钮
        button_html = '<a class="icon fa fa-times" style="color: blue" href="/admin/interface/interfaceinfo/%s/delete/">删除</a>' % obj.id
        return format_html(button_html)

    delete_button.short_description = '<span style="color: blue">删除</span>'
    delete_button.allow_tags = True

    form_layout = (
        Main(
            Fieldset('用例信息部分',
                     'case_group', 'case_name'),
            Fieldset('接口信息部分',
                     'interface_url', 'request_mode',
                     'request_parameter', 'request_head', 'body_type',
                     'request_body', 'expected_result', 'response_assert',
                     'wait_time'),
            Fieldset('正则表达式提取器',
                     'regular_expression', 'regular_variable', 'regular_template'),
        ),
        Side(
            # Fieldset('响应信息部分',
            #          'response_code', 'actual_result', 'pass_status'),
            # Fieldset('时间部分',
            #          'create_time', 'update_time'),
        )
    )
    # 详情页面字段分区，请注意不是fieldsets

    list_display = [
        'id',
        'case_group',
        'case_name',
        'interface_url',
        'request_mode',
        'request_parameter',
        'request_head',
        'body_type',
        'request_body',
        'expected_result',
        'response_assert',
        'wait_time',
        'regular_expression',
        'regular_variable',
        'regular_template',
        'response_code',
        'actual_result',
        'pass_status',
        'create_time',
        'update_time',
        'update_button',
        'delete_button',
    ]

    ordering = ("id",)
    search_fields = ("case_name",)
    list_filter = ["pass_status", "create_time"]
    list_display_links = ('id', 'case_group', 'case_name')
    show_detail_fields = ['case_name']
    list_editable = ['case_name']
    readonly_fields = ['response_code', 'actual_result', 'pass_status']
    raw_id_fields = ('case_group',)
    list_per_page = 10

    batch_fields = (
        'case_name',
        'interface_url',
        'request_mode',
        'request_parameter',
        'request_head',
        'body_type',
        'request_body',
        'expected_result',
        'response_assert',
        'wait_time',
        'regular_expression',
        'regular_variable',
        'regular_template',
    )
    # 可批量修改的字段
    actions = [CopyAction, BatchChangeAction]
    # 列表页面，添加复制动作与批量修改动作


class CaseGroupInfoAdmin(object):
    inlines = [InterfaceInfoAdmin]

    # 使用内嵌显示

    def update_button(self, obj):
        # 修改按钮
        button_html = '<a class="icon fa fa-edit" style="color: green" href="/admin/interface/casegroupinfo/%s/update/">修改</a>' % obj.id
        return format_html(button_html)

    update_button.short_description = '<span style="color: green">修改</span>'
    update_button.allow_tags = True

    def delete_button(self, obj):
        # 删除按钮
        button_html = '<a class="icon fa fa-times" style="color: blue" href="/admin/interface/casegroupinfo/%s/delete/">删除</a>' % obj.id
        return format_html(button_html)

    delete_button.short_description = '<span style="color: blue">删除</span>'
    delete_button.allow_tags = True

    form_layout = (
        Main(
            Fieldset('用例组信息部分',
                     'case_group_name', 'case_group_describe'),
        ),
        # Side(
        #     Fieldset('时间部分',
        #              'create_time', 'update_time'),
        # )
    )

    list_display = [
        'id',
        'case_group_name',
        'case_group_describe',
        'case_sum',
        'create_time',
        'update_time',
        'update_button',
        'delete_button',
    ]
    ordering = ("id",)
    search_fields = ("case_group_name",)
    list_filter = ["case_group_name", "create_time"]
    show_detail_fields = ['case_group_name']
    list_display_links = ('id', 'case_group_name')
    list_editable = ['case_group_name']
    list_per_page = 10

    batch_fields = (
        'case_group_name',
        'case_group_describe',
    )
    # 可批量修改的字段
    actions = [CopyAction, BatchChangeAction]
    # 列表页面，添加复制动作与批量修改动作


class IntervalScheduleAdmin(object):
    list_display = [
        'id', 'every', 'period',
    ]
    ordering = ['id']
    search_fields = ['every']
    list_per_page = 10


class CrontabScheduleAdmin(object):
    list_display = [
        'id', 'minute', 'hour',
        'day_of_week', 'day_of_month', 'month_of_year', 'timezone'
    ]
    ordering = ['id']
    search_fields = ['minute']
    list_per_page = 10


class SolarScheduleAdmin(object):
    list_display = [
        'id', 'event', 'latitude', 'longitude'
    ]
    ordering = ['id']
    search_fields = ['event']
    list_per_page = 10


class ClockedScheduleAdmin(object):
    list_display = [
        'id', 'clocked_time', 'enabled'
    ]
    ordering = ['id']
    search_fields = ['clocked_time']
    list_per_page = 10


class PeriodicTaskAdmin(object):
    list_display = [
        'id', 'name', 'task',
        'interval', 'crontab', 'solar', 'clocked',
        'args', 'kwargs',
        'queue', 'exchange', 'routing_key', 'headers',
        'priority', 'expires', 'one_off', 'start_time', 'enabled', 'description',
        'last_run_at', 'total_run_count', 'date_changed'
    ]
    ordering = ['id']
    search_fields = ['name']
    list_per_page = 10


class TaskResultAdmin(object):
    list_display = [
        'id', 'task_id', 'task_name',
        'task_args', 'task_kwargs',
        'status', 'content_type', 'content_encoding', 'traceback',
        'result', 'date_done', 'hidden', 'meta',
    ]
    ordering = ['id']
    search_fields = ['task_id']
    list_per_page = 10


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True
    # 开启主题自由切换


class GlobalSetting(object):
    global_search_models = [
        ProductInfo,
        ModuleInfo,
        CaseGroupInfo,
        InterfaceInfo
    ]
    # 配置全局搜索选项
    # 默认搜索组、用户、日志记录

    site_title = "测试平台"
    # 标题
    site_footer = "测试部门"
    # 页脚

    menu_style = "accordion"
    # 左侧菜单收缩功能
    apps_icons = {
        "interface": "fa fa-github-square",
    }
    # 配置应用图标，即一级菜单图标
    global_models_icon = {
        ProductInfo: "fa fa-apple",
        ModuleInfo: "fa fa-android",
        CaseGroupInfo: "fa fa-linux",
        InterfaceInfo: "fa fa-windows"
    }

    # 配置模型图标，即二级菜单图标

    def get_site_menu(self):
        return (
            {
                'title': '产品管理',
                'icon': 'fa fa-github-square',
                'perm': self.get_model_perm(ProductInfo, 'change'),
                # 权限
                'menus': (
                    {
                        'title': '产品线列表',
                        'icon': 'fa fa-apple',
                        'url': self.get_model_url(ProductInfo, 'changelist')
                    },
                    {
                        'title': '模块列表',
                        'icon': 'fa fa-android',
                        'url': self.get_model_url(ModuleInfo, 'changelist')
                    },
                )
            },
            {
                'title': '用例管理',
                'icon': 'fa fa-github',
                'perm': self.get_model_perm(CaseGroupInfo, 'change'),
                'menus': (
                    {
                        'title': '用例组列表',
                        'icon': 'fa fa-linux',
                        'url': self.get_model_url(CaseGroupInfo, 'changelist')
                    },
                    {
                        'title': '用例列表',
                        'icon': 'fa fa-windows',
                        'url': self.get_model_url(InterfaceInfo, 'changelist')
                    },
                )
            },
            {
                'title': '任务管理',
                'icon': 'fa fa-github-alt',
                'perm': self.get_model_perm(PeriodicTask, 'change'),
                'menus': (
                    {
                        'title': '间隔时间列表',
                        'icon': 'fa fa-backward',
                        'url': self.get_model_url(IntervalSchedule, 'changelist')
                    },
                    {
                        'title': '定时时间列表',
                        'icon': 'fa fa-forward',
                        'url': self.get_model_url(CrontabSchedule, 'changelist')
                    },
                    {
                        'title': '太阳时间列表（无用）',
                        'icon': 'fa fa-fast-backward',
                        'url': self.get_model_url(SolarSchedule, 'changelist')
                    },
                    {
                        'title': '计时时间列表（无用）',
                        'icon': 'fa fa-fast-forward',
                        'url': self.get_model_url(ClockedSchedule, 'changelist')
                    },
                    {
                        'title': '任务设置列表',
                        'icon': 'fa fa-play-circle',
                        'url': self.get_model_url(PeriodicTask, 'changelist')
                    },
                    {
                        'title': '任务结果列表',
                        'icon': 'fa fa-arrows-alt',
                        'url': self.get_model_url(TaskResult, 'changelist')
                    },
                )
            },
        )
    # 自定义应用的顺序


xadmin.site.register(ProductInfo, ProductInfoAdmin)
xadmin.site.register(ModuleInfo, ModuleInfoAdmin)
xadmin.site.register(CaseGroupInfo, CaseGroupInfoAdmin)
xadmin.site.register(InterfaceInfo, InterfaceInfoAdmin)

xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSetting)

xadmin.site.register(IntervalSchedule, IntervalScheduleAdmin)
# 间隔时间表
xadmin.site.register(CrontabSchedule, CrontabScheduleAdmin)
# 定时时间表
xadmin.site.register(SolarSchedule, SolarScheduleAdmin)
# 太阳时间表
xadmin.site.register(ClockedSchedule, ClockedScheduleAdmin)
# 计时时间表
xadmin.site.register(PeriodicTask, PeriodicTaskAdmin)
# 配置任务

xadmin.site.register(TaskResult, TaskResultAdmin)
# 任务结果
