from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.utils.datetime_safe import datetime
from django.views import View
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


