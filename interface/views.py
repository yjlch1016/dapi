import re
from time import sleep

import demjson
import requests
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.datetime_safe import datetime
from django.views import View
from django_celery_beat.models import IntervalSchedule, CrontabSchedule, PeriodicTask, PeriodicTasks
from django_celery_results.models import TaskResult
from rest_framework import viewsets

from interface.models import InterfaceInfo, ProductInfo, CaseGroupInfo, ModuleInfo
from interface.serializers import ProductInfoSerializer, ModuleInfoSerializer, CaseGroupInfoSerializer, \
    InterfaceInfoSerializer


# Create your views here.


class ProductInfoViewSet(viewsets.ModelViewSet):
    """产品线表"""
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer


class ModuleInfoViewSet(viewsets.ModelViewSet):
    """模块表"""
    queryset = ModuleInfo.objects.all()
    serializer_class = ModuleInfoSerializer


class CaseGroupInfoViewSet(viewsets.ModelViewSet):
    """用例组表"""
    queryset = CaseGroupInfo.objects.all()
    serializer_class = CaseGroupInfoSerializer


class InterfaceInfoViewSet(viewsets.ModelViewSet):
    """用例表"""
    queryset = InterfaceInfo.objects.all()
    serializer_class = InterfaceInfoSerializer


def login(request):
    if request.method == "POST":
        user_name = request.POST.get('form_user_name', '')
        # 对应前端的<input name="form_user_name">
        password = request.POST.get('form_password', '')
        # 对应前端的<input name="form_password">
        user = auth.authenticate(username=user_name, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            request.session['user'] = user_name
            return redirect('/home/')
        else:
            return render(request, 'login.html', {'error': '用户名或密码错误！'})
    return render(request, 'login.html')


@login_required
# 要求用户登录
def home(request):
    return render(request, "home.html")


@login_required
def logout(request):
    auth.logout(request)
    return render(request, 'login.html')


class ProductListView(LoginRequiredMixin, View):
    """产品线列表"""

    def get(self, request):
        user_name = request.session.get('user', '')
        # 读取浏览器session
        product_list = ProductInfo.objects.all().order_by("id")
        product_count = ProductInfo.objects.all().count()

        search_product = request.GET.get("form_product_name_s", "")
        # 搜索产品线
        if search_product:
            product_list = product_list.filter(product_name__icontains=search_product)
            product_count = product_list.count()

        paginator = Paginator(product_list, 10)
        # 生成paginator对象,设置每页显示10条记录
        page = request.GET.get('page', 1)
        # 获取当前的页码数，默认为第1页
        try:
            p_list = paginator.page(page)
            # 获取当前页数的记录列表
        except PageNotAnInteger:
            p_list = paginator.page(1)
            # 如果请求的页数不是整数，返回第一页
        except EmptyPage:
            p_list = paginator.page(paginator.num_pages)
            # 如果请求的页数不在合法的页数范围内，返回结果的最后一页

        return render(
            request,
            "product.html",
            {
                "user": user_name,
                "p_list": p_list,
                "p_count": product_count,
            }
        )


class AddProductView(LoginRequiredMixin, View):
    """增加产品线"""

    def post(self, request):
        p_name = request.POST.get('form_product_name_a', '')
        p_describe = request.POST.get('form_product_describe_a', '')
        p_manager = request.POST.get('form_product_manager_a', '')
        developer = request.POST.get('form_developer_a', '')
        tester = request.POST.get('form_tester_a', '')
        ProductInfo.objects.create(
            product_name=p_name,
            product_describe=p_describe,
            product_manager=p_manager,
            developer=developer,
            tester=tester,
        )

        return redirect('/product/')


class UpdateProductView(LoginRequiredMixin, View):
    """修改产品线"""

    def post(self, request):
        p_id = request.POST.get('form_product_id_u', '')
        p_name = request.POST.get('form_product_name_u', '')
        p_describe = request.POST.get('form_product_describe_u', '')
        p_manager = request.POST.get('form_product_manager_u', '')
        developer = request.POST.get('form_developer_u', '')
        tester = request.POST.get('form_tester_u', '')
        ProductInfo.objects.filter(id=p_id).update(
            product_name=p_name,
            product_describe=p_describe,
            product_manager=p_manager,
            developer=developer,
            tester=tester,
            update_time=datetime.now(),
        )

        return redirect('/product/')


class DeleteProductView(LoginRequiredMixin, View):
    """删除产品线"""

    def post(self, request):
        product_id = request.POST.get('form_product_id_d', '')
        ProductInfo.objects.filter(id=product_id).delete()

        return redirect('/product/')


class ModuleListView(LoginRequiredMixin, View):
    """模块列表"""

    def get(self, request):
        user_name = request.session.get('user', '')
        product_list = ProductInfo.objects.all().order_by("id")
        module_list = ModuleInfo.objects.all().order_by("id")
        module_count = ModuleInfo.objects.all().count()

        search_module = request.GET.get("form_module_name_s", "")
        # 搜索模块
        if search_module:
            module_list = module_list.filter(module_name__icontains=search_module)
            module_count = module_list.count()

        paginator = Paginator(module_list, 10)
        page = request.GET.get('page', 1)
        try:
            m_list = paginator.page(page)
        except PageNotAnInteger:
            m_list = paginator.page(1)
        except EmptyPage:
            m_list = paginator.page(paginator.num_pages)

        return render(
            request,
            "module.html",
            {
                "user": user_name,
                "p_list": product_list,
                "m_list": m_list,
                "m_count": module_count,
            }
        )


class AddModuleView(LoginRequiredMixin, View):
    """增加模块"""

    def post(self, request):
        m_group = request.POST.get('form_module_group_a', '')
        m_name = request.POST.get('form_module_name_a', '')
        m_describe = request.POST.get('form_module_describe_a', '')
        ModuleInfo.objects.create(
            module_group_id=m_group,
            module_name=m_name,
            module_describe=m_describe,
        )

        return redirect('/module/')


class UpdateModuleView(LoginRequiredMixin, View):
    """修改模块"""

    def post(self, request):
        m_id = request.POST.get('form_module_id_u', '')
        m_group = request.POST.get('form_module_group_u', '')
        m_name = request.POST.get('form_module_name_u', '')
        m_describe = request.POST.get('form_module_describe_u', '')
        ModuleInfo.objects.filter(id=m_id).update(
            module_group_id=m_group,
            module_name=m_name,
            module_describe=m_describe,
            update_time=datetime.now(),
        )

        return redirect('/module/')


class DeleteModuleView(LoginRequiredMixin, View):
    """删除模块"""

    def post(self, request):
        module_id = request.POST.get('form_module_id_d', '')
        ModuleInfo.objects.filter(id=module_id).delete()

        return redirect('/module/')


class CaseGroupListView(LoginRequiredMixin, View):
    """用例组列表"""

    def get(self, request):
        user_name = request.session.get('user', '')
        case_group_list = CaseGroupInfo.objects.all().order_by("id")
        case_group_count = CaseGroupInfo.objects.all().count()

        search_case_group = request.GET.get("form_case_group_name_s", "")
        # 搜索用例组
        if search_case_group:
            case_group_list = case_group_list.filter(
                case_group_name__icontains=search_case_group)
            case_group_count = case_group_list.count()

        paginator = Paginator(case_group_list, 10)
        page = request.GET.get('page', 1)
        try:
            c_list = paginator.page(page)
        except PageNotAnInteger:
            c_list = paginator.page(1)
        except EmptyPage:
            c_list = paginator.page(paginator.num_pages)

        return render(
            request,
            "case_group.html",
            {
                "user": user_name,
                "c_list": c_list,
                "c_count": case_group_count,
            }
        )


class AddCaseGroupView(LoginRequiredMixin, View):
    """增加用例组"""

    def post(self, request):
        c_name = request.POST.get('form_case_group_name_a', '')
        c_describe = request.POST.get('form_case_group_describe_a', '')
        CaseGroupInfo.objects.create(
            case_group_name=c_name,
            case_group_describe=c_describe,
        )

        return redirect('/case_group/')


class UpdateCaseGroupView(LoginRequiredMixin, View):
    """修改用例组"""

    def post(self, request):
        c_id = request.POST.get('form_case_group_id_u', '')
        c_name = request.POST.get('form_case_group_name_u', '')
        c_describe = request.POST.get('form_case_group_describe_u', '')
        CaseGroupInfo.objects.filter(id=c_id).update(
            case_group_name=c_name,
            case_group_describe=c_describe,
            update_time=datetime.now(),
        )

        return redirect('/case_group/')


class DeleteCaseGroupView(LoginRequiredMixin, View):
    """删除用例组"""

    def post(self, request):
        case_group_id = request.POST.get('form_case_group_id_d', '')
        CaseGroupInfo.objects.filter(id=case_group_id).delete()

        return redirect('/case_group/')


class DebugCaseGroupView(LoginRequiredMixin, View):
    """运行用例组"""

    def update_interface_info(self, case_id, field, value):
        # 等价于UPDATE interface_info SET field=value WHERE id=case_id;
        field_value = {field: value}
        InterfaceInfo.objects.filter(id=case_id).update(**field_value)

    def post(self, request):

        global regular_result
        # 声明一个全局变量regular_result（正则表达式提取的结果）
        # 用于传参

        case_group_id = request.POST.get('form_case_group_id_b', '')
        data_object = CaseGroupInfo.objects.get(
            id=case_group_id).groups.values().order_by("id")
        # 反向查询用例组包含的用例信息

        data_list = list(data_object)
        # 把QuerySet对象转换成列表
        for item in data_list:
            case_id = item["id"]
            request_mode = item["request_mode"]
            interface_url = item["interface_url"]
            body_type = item["body_type"]
            request_body = item["request_body"]
            request_head = item["request_head"]
            request_parameter = item["request_parameter"]
            expected_result = item["expected_result"]
            response_assert = item["response_assert"]
            regular_expression = item["regular_expression"]
            regular_variable = item["regular_variable"]
            regular_template = item["regular_template"]
            actual_result = item["actual_result"]
            wait_time = item["wait_time"]
            # 获取列表里面的字典的值

            if regular_expression == "开启" and regular_variable is not None:
                # 如果正则表达式开启，并且变量名不为空
                regular_result = re.findall(regular_template, actual_result)[0]
                # re.findall(正则表达式模板, 某个接口的实际结果)
                # 返回一个符合规则的list，取第1个
                # 即为正则表达式提取的结果

            if regular_expression == "不开启" and regular_variable == "":
                # 如果正则表达式不开启，并且变量名为空
                data_object = CaseGroupInfo.objects.get(
                    id=case_group_id).groups.values("regular_variable").filter(
                    regular_expression="开启").order_by("id")
                # 取出过滤条件为"正则表达式开启"的那条用例的变量名
                data_list = list(data_object)
                for item in data_list:
                    regular_variable = item["regular_variable"]

            old = "${" + regular_variable + "}"
            # ${变量名} = ${ + 变量名 + }
            if "$" in interface_url:
                interface_url = interface_url.replace(old, regular_result)
                # replace(old, new)把字符串中的旧字符串替换成新字符串
                # 即把正则表达式提取的值替换进去
            elif "$" in request_parameter:
                request_parameter = request_parameter.replace(old, regular_result)
            elif "$" in request_head:
                request_head = request_head.replace(old, regular_result)
            elif "$" in request_body:
                request_body = request_body.replace(old, regular_result)
            elif "$" in expected_result:
                expected_result = expected_result.replace(old, regular_result)

            if body_type == "x-www-form-urlencoded":
                pass
                # 请求体类型默认使用浏览器原生表单
                # 如果是这种格式，不作任何处理
            elif body_type == "json":
                request_body = demjson.decode(request_body)
                # 等价于json.loads()反序列化

            response = requests.request(
                request_mode,
                interface_url,
                data=request_body,
                headers=demjson.decode(request_head),
                params=demjson.decode(request_parameter)
            )

            result_code = response.status_code
            # 实际的响应代码
            result_text = response.text
            # 实际的响应文本
            expect_error = "接口请求失败，请检查拼写是否正确！"

            if result_code == 200:
                if response_assert == "包含":
                    self.update_interface_info(case_id, "response_code", result_code)
                    # 插入响应代码
                    self.update_interface_info(case_id, "actual_result", result_text)
                    # 插入实际结果
                    if expected_result in result_text:
                        self.update_interface_info(case_id, "pass_status", 1)
                        # 插入通过状态
                    else:
                        self.update_interface_info(case_id, "pass_status", 0)
                        # 插入不通过状态
                elif response_assert == "相等":
                    self.update_interface_info(case_id, "response_code", result_code)
                    self.update_interface_info(case_id, "actual_result", result_text)
                    if expected_result == result_text:
                        self.update_interface_info(case_id, "pass_status", 1)
                    else:
                        self.update_interface_info(case_id, "pass_status", 0)
            else:
                self.update_interface_info(case_id, "response_code", result_code)
                self.update_interface_info(case_id, "actual_result", expect_error)
                self.update_interface_info(case_id, "pass_status", 0)

            sleep(wait_time)
            # 等待时间

        return redirect('/case_group/')


def get_case_ajax(request):
    """用例组ajax获取用例信息"""

    if request.method == 'POST':
        i = request.POST.get('i')
        data_object = CaseGroupInfo.objects.get(id=i).groups.values(
            "id", "case_name", "pass_status").order_by("id")
        # 反向查询用例组包含的用例
        data_list = list(data_object)
        # 把QuerySet对象转换成列表

        return JsonResponse(data_list, safe=False)
        # JsonResponse在抛出列表的时候需要将safe设置为False


class InterfaceListView(LoginRequiredMixin, View):
    """用例列表"""

    def get(self, request):
        user_name = request.session.get('user', '')
        case_group_list = CaseGroupInfo.objects.all().order_by("id")
        interface_list = InterfaceInfo.objects.all().order_by("id")
        interface_count = InterfaceInfo.objects.all().count()

        search_interface = request.GET.get("form_case_name_s", "")
        # 搜索用例
        if search_interface:
            interface_list = interface_list.filter(
                case_name__icontains=search_interface)
            interface_count = interface_list.count()

        paginator = Paginator(interface_list, 10)
        page = request.GET.get('page', 1)
        try:
            i_list = paginator.page(page)
        except PageNotAnInteger:
            i_list = paginator.page(1)
        except EmptyPage:
            i_list = paginator.page(paginator.num_pages)

        return render(
            request,
            "interface.html",
            {
                "user": user_name,
                "c_list": case_group_list,
                "i_list": i_list,
                "i_count": interface_count,
            }
        )


class AddInterfaceView(LoginRequiredMixin, View):
    """增加用例"""

    def post(self, request):
        case_group = request.POST.get('form_case_group_a', '')
        case_name = request.POST.get('form_case_name_a', '')
        interface_url = request.POST.get('form_interface_url_a', '')
        request_mode = request.POST.get('form_request_mode_a', '')
        request_parameter = request.POST.get('form_request_parameter_a', '')
        request_head = request.POST.get('form_request_head_a', '')
        body_type = request.POST.get('form_body_type_a', '')
        request_body = request.POST.get('form_request_body_a', '')
        expected_result = request.POST.get('form_expected_result_a', '')
        response_assert = request.POST.get('form_response_assert_a', '')
        wait_time = request.POST.get('form_wait_time_a', '')
        regular_expression = request.POST.get('form_regular_expression_a', '')
        regular_variable = request.POST.get('form_regular_variable_a', '')
        regular_template = request.POST.get('form_regular_template_a', '')
        InterfaceInfo.objects.create(
            case_group_id=case_group,
            case_name=case_name,
            interface_url=interface_url,
            request_mode=request_mode,
            request_parameter=request_parameter,
            request_head=request_head,
            body_type=body_type,
            request_body=request_body,
            expected_result=expected_result,
            response_assert=response_assert,
            wait_time=wait_time,
            regular_expression=regular_expression,
            regular_variable=regular_variable,
            regular_template=regular_template,
        )

        return redirect('/interface/')


class UpdateInterfaceView(LoginRequiredMixin, View):
    """修改用例"""

    def post(self, request):
        case_id = request.POST.get('form_case_id_u', '')
        case_group = request.POST.get('form_case_group_u', '')
        case_name = request.POST.get('form_case_name_u', '')
        interface_url = request.POST.get('form_interface_url_u', '')
        request_mode = request.POST.get('form_request_mode_u', '')
        request_parameter = request.POST.get('form_request_parameter_u', '')
        request_head = request.POST.get('form_request_head_u', '')
        body_type = request.POST.get('form_body_type_u', '')
        request_body = request.POST.get('form_request_body_u', '')
        expected_result = request.POST.get('form_expected_result_u', '')
        response_assert = request.POST.get('form_response_assert_u', '')
        wait_time = request.POST.get('form_wait_time_u', '')
        regular_expression = request.POST.get('form_regular_expression_u', '')
        regular_variable = request.POST.get('form_regular_variable_u', '')
        regular_template = request.POST.get('form_regular_template_u', '')
        InterfaceInfo.objects.filter(id=case_id).update(
            case_group_id=case_group,
            case_name=case_name,
            interface_url=interface_url,
            request_mode=request_mode,
            request_parameter=request_parameter,
            request_head=request_head,
            body_type=body_type,
            request_body=request_body,
            expected_result=expected_result,
            response_assert=response_assert,
            wait_time=wait_time,
            regular_expression=regular_expression,
            regular_variable=regular_variable,
            regular_template=regular_template,
            update_time=datetime.now(),
        )

        return redirect('/interface/')


class DeleteInterfaceView(LoginRequiredMixin, View):
    """删除用例"""

    def post(self, request):
        case_id = request.POST.get('form_case_id_d', '')
        InterfaceInfo.objects.filter(id=case_id).delete()

        return redirect('/interface/')


class DebugInterfaceView(LoginRequiredMixin, View):
    """运行用例"""

    def update_interface_info(self, case_id, field, value):
        # 等价于UPDATE interface_info SET field=value WHERE id=case_id;
        field_value = {field: value}
        InterfaceInfo.objects.filter(id=case_id).update(**field_value)

    def post(self, request):
        case_id = request.POST.get('form_case_id_b', '')
        data_object = InterfaceInfo.objects.get(id=case_id)
        data_dict = model_to_dict(data_object)
        # 把QuerySet对象转换成字典

        if data_dict["body_type"] == "x-www-form-urlencoded":
            pass
            # 请求体类型默认使用浏览器原生表单
            # 如果是这种格式，不作任何处理
        elif data_dict["body_type"] == "json":
            data_dict["request_body"] = demjson.decode(data_dict["request_body"])
            # 等价于json.loads()反序列化

        response = requests.request(
            data_dict["request_mode"],
            data_dict["interface_url"],
            data=data_dict["request_body"],
            headers=demjson.decode(data_dict["request_head"]),
            params=demjson.decode(data_dict["request_parameter"])
        )

        result_code = response.status_code
        # 实际的响应代码
        result_text = response.text
        # 实际的响应文本
        expect_error = "接口请求失败，请检查拼写是否正确！"

        if result_code == 200:
            if data_dict["response_assert"] == "包含":
                self.update_interface_info(case_id, "response_code", result_code)
                # 插入响应代码
                self.update_interface_info(case_id, "actual_result", result_text)
                # 插入实际结果
                if data_dict["expected_result"] in result_text:
                    self.update_interface_info(case_id, "pass_status", 1)
                    # 插入通过状态
                else:
                    self.update_interface_info(case_id, "pass_status", 0)
                    # 插入不通过状态
            elif data_dict["response_assert"] == "相等":
                self.update_interface_info(case_id, "response_code", result_code)
                self.update_interface_info(case_id, "actual_result", result_text)
                if data_dict["expected_result"] == result_text:
                    self.update_interface_info(case_id, "pass_status", 1)
                else:
                    self.update_interface_info(case_id, "pass_status", 0)
        else:
            self.update_interface_info(case_id, "response_code", result_code)
            self.update_interface_info(case_id, "actual_result", expect_error)
            self.update_interface_info(case_id, "pass_status", 0)

        sleep(data_dict["wait_time"])
        # 等待时间

        return redirect('/interface/')


class IntervalScheduleListView(LoginRequiredMixin, View):
    """间隔时间列表"""

    def get(self, request):
        user_name = request.session.get('user', '')
        interval_schedule_list = IntervalSchedule.objects.all().order_by("id")
        interval_schedule_count = IntervalSchedule.objects.all().count()

        search_interval_schedule = request.GET.get("form_every_s", "")
        # 搜索周期数
        if search_interval_schedule:
            interval_schedule_list = interval_schedule_list.filter(
                every__icontains=search_interval_schedule)
            interval_schedule_count = interval_schedule_list.count()

        paginator = Paginator(interval_schedule_list, 10)
        page = request.GET.get('page', 1)
        try:
            is_list = paginator.page(page)
        except PageNotAnInteger:
            is_list = paginator.page(1)
        except EmptyPage:
            is_list = paginator.page(paginator.num_pages)

        return render(
            request,
            "interval_schedule.html",
            {
                "user": user_name,
                "is_list": is_list,
                "is_count": interval_schedule_count,
            }
        )


class AddIntervalScheduleView(LoginRequiredMixin, View):
    """增加间隔时间"""

    def post(self, request):
        every = request.POST.get('form_every_a', '')
        period = request.POST.get('form_period_a', '')
        IntervalSchedule.objects.create(
            every=every,
            period=period,
        )

        return redirect('/interval_schedule/')


class UpdateIntervalScheduleView(LoginRequiredMixin, View):
    """修改间隔时间"""

    def post(self, request):
        interval_id = request.POST.get('form_interval_id_u', '')
        every = request.POST.get('form_every_u', '')
        period = request.POST.get('form_period_u', '')
        IntervalSchedule.objects.filter(id=interval_id).update(
            every=every,
            period=period,
        )

        return redirect('/interval_schedule/')


class DeleteIntervalScheduleView(LoginRequiredMixin, View):
    """删除间隔时间"""

    def post(self, request):
        interval_id = request.POST.get('form_interval_id_d', '')
        IntervalSchedule.objects.filter(id=interval_id).delete()

        return redirect('/interval_schedule/')


class CrontabScheduleListView(LoginRequiredMixin, View):
    """定时时间列表"""

    def get(self, request):
        user_name = request.session.get('user', '')
        crontab_schedule_list = CrontabSchedule.objects.all().order_by("id")
        crontab_schedule_count = CrontabSchedule.objects.all().count()

        search_crontab_schedule = request.GET.get("form_minute_s", "")
        # 搜索分钟
        if search_crontab_schedule:
            crontab_schedule_list = crontab_schedule_list.filter(
                minute__icontains=search_crontab_schedule)
            crontab_schedule_count = crontab_schedule_list.count()

        paginator = Paginator(crontab_schedule_list, 10)
        page = request.GET.get('page', 1)
        try:
            cs_list = paginator.page(page)
        except PageNotAnInteger:
            cs_list = paginator.page(1)
        except EmptyPage:
            cs_list = paginator.page(paginator.num_pages)

        return render(
            request,
            "crontab_schedule.html",
            {
                "user": user_name,
                "cs_list": cs_list,
                "cs_count": crontab_schedule_count,
            }
        )


class AddCrontabScheduleView(LoginRequiredMixin, View):
    """增加定时时间"""

    def post(self, request):
        minute = request.POST.get('form_minute_a', '')
        hour = request.POST.get('form_hour_a', '')
        day_of_week = request.POST.get('form_week_a', '')
        day_of_month = request.POST.get('form_day_a', '')
        month_of_year = request.POST.get('form_month_a', '')
        timezone = request.POST.get('form_timezone_a', '')
        CrontabSchedule.objects.create(
            minute=minute,
            hour=hour,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
            timezone=timezone,
        )

        return redirect('/crontab_schedule/')


class UpdateCrontabScheduleView(LoginRequiredMixin, View):
    """修改定时时间"""

    def post(self, request):
        crontab_id = request.POST.get('form_crontab_id_u', '')
        minute = request.POST.get('form_minute_u', '')
        hour = request.POST.get('form_hour_u', '')
        day_of_week = request.POST.get('form_week_u', '')
        day_of_month = request.POST.get('form_day_u', '')
        month_of_year = request.POST.get('form_month_u', '')
        timezone = request.POST.get('form_timezone_u', '')
        CrontabSchedule.objects.filter(id=crontab_id).update(
            minute=minute,
            hour=hour,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
            timezone=timezone,
        )

        return redirect('/crontab_schedule/')


class DeleteCrontabScheduleView(LoginRequiredMixin, View):
    """删除定时时间"""

    def post(self, request):
        crontab_id = request.POST.get('form_crontab_id_d', '')
        CrontabSchedule.objects.filter(id=crontab_id).delete()

        return redirect('/crontab_schedule/')


class PeriodicTaskListView(LoginRequiredMixin, View):
    """任务设置列表"""

    def get(self, request):
        user_name = request.session.get('user', '')
        interval_schedule_list = IntervalSchedule.objects.all().order_by("id")
        crontab_schedule_list = CrontabSchedule.objects.all().order_by("id")
        periodic_task_list = PeriodicTask.objects.all().order_by("id")
        periodic_task_count = PeriodicTask.objects.all().count()

        search_periodic_task = request.GET.get("form_name_s", "")
        # 搜索任务说明
        if search_periodic_task:
            periodic_task_list = periodic_task_list.filter(
                name__icontains=search_periodic_task)
            periodic_task_count = periodic_task_list.count()

        paginator = Paginator(periodic_task_list, 10)
        page = request.GET.get('page', 1)
        try:
            pt_list = paginator.page(page)
        except PageNotAnInteger:
            pt_list = paginator.page(1)
        except EmptyPage:
            pt_list = paginator.page(paginator.num_pages)

        return render(
            request,
            "periodic_task.html",
            {
                "user": user_name,
                "is_list": interval_schedule_list,
                "cs_list": crontab_schedule_list,
                "pt_list": pt_list,
                "pt_count": periodic_task_count,
            }
        )


class AddPeriodicTaskView(LoginRequiredMixin, View):
    """增加任务设置"""

    def post(self, request):
        name = request.POST.get('form_name_a', '')
        task = request.POST.get('form_task_a', '')
        interval_id = request.POST.get('form_interval_id_a', '')
        if interval_id == "":
            interval_id = None
        crontab_id = request.POST.get('form_crontab_id_a', '')
        if crontab_id == "":
            crontab_id = None
        args = request.POST.get('form_args_a', '')
        if args == "":
            args = "[]"
        kwargs = request.POST.get('form_kwargs_a', '')
        if kwargs == "":
            kwargs = "{}"
        queue = request.POST.get('form_queue_a', '')
        if queue == "":
            queue = None
        exchange = request.POST.get('form_exchange_a', '')
        if exchange == "":
            exchange = None
        routing_key = request.POST.get('form_routing_key_a', '')
        if routing_key == "":
            routing_key = None
        headers = request.POST.get('form_headers_a', '')
        if headers == "":
            headers = "{}"
        priority = request.POST.get('form_priority_a', '')
        if priority == "":
            priority = None
        expires = request.POST.get('form_expires_a', '')
        if expires == "":
            expires = None
        one_off = request.POST.get('form_one_off_a', '')
        if one_off == "":
            one_off = 0
        elif one_off == "on":
            one_off = 1
        start_time = request.POST.get('form_start_time_a', '')
        if start_time == "":
            start_time = None
        enabled = request.POST.get('form_enabled_a', '')
        if enabled == "on":
            enabled = 1
        elif enabled == "":
            enabled = 0
        description = request.POST.get('form_description_a', '')
        if description == "":
            description = "空"
        PeriodicTask.objects.create(
            name=name,
            task=task,
            interval_id=interval_id,
            crontab_id=crontab_id,
            args=args,
            kwargs=kwargs,
            queue=queue,
            exchange=exchange,
            routing_key=routing_key,
            headers=headers,
            priority=priority,
            expires=expires,
            one_off=one_off,
            start_time=start_time,
            enabled=enabled,
            description=description,
        )

        return redirect('/periodic_task/')


class UpdatePeriodicTaskView(LoginRequiredMixin, View):
    """修改任务设置"""

    def post(self, request):
        periodic_id = request.POST.get('form_periodic_id_u', '')
        name = request.POST.get('form_name_u', '')
        task = request.POST.get('form_task_u', '')
        interval_id = request.POST.get('form_interval_u', '')
        if interval_id == "":
            interval_id = None
        crontab_id = request.POST.get('form_crontab_u', '')
        if crontab_id == "":
            crontab_id = None
        args = request.POST.get('form_args_u', '')
        if args == "":
            args = "[]"
        kwargs = request.POST.get('form_kwargs_u', '')
        if kwargs == "":
            kwargs = "{}"
        queue = request.POST.get('form_queue_u', '')
        if queue == "None":
            queue = None
        exchange = request.POST.get('form_exchange_u', '')
        if exchange == "None":
            exchange = None
        routing_key = request.POST.get('form_routing_key_u', '')
        if routing_key == "None":
            routing_key = None
        headers = request.POST.get('form_headers_u', '')
        if headers == "":
            headers = "{}"
        priority = request.POST.get('form_priority_u', '')
        if priority == "None":
            priority = None
        expires = request.POST.get('form_expires_u', '')
        if expires == "None":
            expires = None
        one_off = request.POST.get('form_one_off_u', '')
        if one_off == "":
            one_off = 0
        elif one_off == "on":
            one_off = 1
        start_time = request.POST.get('form_start_time_u', '')
        if start_time == "None":
            start_time = None
        enabled = request.POST.get('form_enabled_u', '')
        if enabled == "on":
            enabled = 1
        elif enabled == "":
            enabled = 0
        description = request.POST.get('form_description_u', '')
        if description == "":
            description = "空"
        PeriodicTask.objects.filter(id=periodic_id).update(
            name=name,
            task=task,
            interval_id=interval_id,
            crontab_id=crontab_id,
            args=args,
            kwargs=kwargs,
            queue=queue,
            exchange=exchange,
            routing_key=routing_key,
            headers=headers,
            priority=priority,
            expires=expires,
            one_off=one_off,
            start_time=start_time,
            enabled=enabled,
            description=description,
            date_changed=datetime.now(),
        )

        PeriodicTask.objects.all().update(last_run_at=None)
        for task in PeriodicTask.objects.all():
            PeriodicTasks.changed(task)

        return redirect('/periodic_task/')


class DeletePeriodicTaskView(LoginRequiredMixin, View):
    """删除任务设置"""

    def post(self, request):
        periodic_id = request.POST.get('form_periodic_id_d', '')
        PeriodicTask.objects.filter(id=periodic_id).delete()

        return redirect('/periodic_task/')


class TaskResultListView(LoginRequiredMixin, View):
    """任务结果列表"""

    def get(self, request):
        user_name = request.session.get('user', '')
        task_result_list = TaskResult.objects.all().order_by("id")
        task_result_count = TaskResult.objects.all().count()

        search_task_result = request.GET.get("form_name_s", "")
        # 搜索任务名称
        if search_task_result:
            task_result_list = task_result_list.filter(
                task_name__icontains=search_task_result)
            task_result_count = task_result_list.count()

        paginator = Paginator(task_result_list, 10)
        page = request.GET.get('page', 1)
        try:
            tr_list = paginator.page(page)
        except PageNotAnInteger:
            tr_list = paginator.page(1)
        except EmptyPage:
            tr_list = paginator.page(paginator.num_pages)

        return render(
            request,
            "task_result.html",
            {
                "user": user_name,
                "tr_list": tr_list,
                "tr_count": task_result_count,
            }
        )
