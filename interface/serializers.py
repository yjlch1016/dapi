from rest_framework import serializers

from interface.models import InterfaceInfo, ProductInfo, CaseGroupInfo, ModuleInfo


class ProductInfoSerializer(serializers.HyperlinkedModelSerializer):
    # 产品线序列化

    class Meta:
        model = ProductInfo
        fields = "__all__"


class ModuleInfoSerializer(serializers.HyperlinkedModelSerializer):
    # 模块序列化

    product_name = serializers.ReadOnlyField(source='module_group.product_name')

    # 外键序列化

    class Meta:
        model = ModuleInfo
        fields = (
            'id',
            'module_group',
            'product_name',
            'module_name',
            'module_describe',
            'create_time',
            'update_time',
        )


class CaseGroupInfoSerializer(serializers.HyperlinkedModelSerializer):
    # 用例组序列化

    class Meta:
        model = CaseGroupInfo
        fields = "__all__"


class InterfaceInfoSerializer(serializers.HyperlinkedModelSerializer):
    # 用例序列化

    case_group_name = serializers.ReadOnlyField(source='case_group.case_group_name')

    # 外键序列化

    class Meta:
        model = InterfaceInfo
        fields = (
            'id',
            'case_group',
            'case_group_name',
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
        )
