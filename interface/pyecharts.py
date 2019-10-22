import json

from django.http import HttpResponse
from rest_framework.views import APIView

from pyecharts.charts import Bar
from pyecharts import options as opts

from interface.models import ProductInfo, ModuleInfo, CaseGroupInfo, InterfaceInfo


def response_as_json(data):
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str,
        content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, code=200):
    data = {
        "code": code,
        "msg": "success",
        "data": data,
    }
    return response_as_json(data)


def json_error(error_string="error", code=500, **kwargs):
    data = {
        "code": code,
        "msg": error_string,
        "data": {}
    }
    data.update(kwargs)
    return response_as_json(data)


JsonResponse = json_response
JsonError = json_error


def bar_base() -> Bar:
    product_count = ProductInfo.objects.all().count()
    module_count = ModuleInfo.objects.all().count()
    case_group_count = CaseGroupInfo.objects.all().count()
    total = InterfaceInfo.objects.all().count()
    success = InterfaceInfo.objects.filter(pass_status=1).count()
    fail = InterfaceInfo.objects.filter(pass_status=0).count()
    not_run = InterfaceInfo.objects.filter(pass_status=None).count()

    c = (
        Bar()
        .add_xaxis(["产品线", "模块", "用例组", "用例"])
        .add_yaxis("总共", [product_count, module_count, case_group_count, total])
        .add_yaxis("通过", ["", "", "", success])
        .add_yaxis("不通过", ["", "", "", fail])
        .add_yaxis("未运行", ["", "", "", not_run])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="测试报告", subtitle="接口测试报告"))
        .dump_options_with_quotes()
    )
    return c


class ChartView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(bar_base()))


class IndexView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(
            content=open("interface/templates/index.html").read())
