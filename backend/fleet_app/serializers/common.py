"""统一序列化器基类：Django snake_case <-> 前端 camelCase。"""
from rest_framework import serializers


def snake_to_camel(name: str) -> str:
    parts = name.split('_')
    return parts[0] + ''.join(p.title() for p in parts[1:])


def camel_to_snake(name: str) -> str:
    return ''.join('_' + ch.lower() if ch.isupper() else ch for ch in name).lstrip('_')


class CamelModelSerializer(serializers.ModelSerializer):
    """输出 camelCase，输入同时接受 camelCase 与 snake_case。"""

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {snake_to_camel(key): value for key, value in data.items()}

    def to_internal_value(self, data):
        # serializer 字段名是 snake_case，接受 camelCase 输入：
        #   plateNo -> plate_no；vehicleId -> vehicle（外键主键字段）
        normalized = {}
        for key, value in data.items():
            normalized[self._resolve_input_key(key)] = value
        return super().to_internal_value(normalized)

    def _resolve_input_key(self, key):
        if key in self.fields:
            return key
        snake_key = camel_to_snake(key)
        if snake_key in self.fields:
            return snake_key
        # vehicleId -> vehicle_id -> vehicle
        if snake_key.endswith('_id'):
            fk_field = snake_key[:-3]
            if fk_field in self.fields:
                return fk_field
        # 按字段 source 兜底
        for name, field in self.fields.items():
            source = field.source if field.source and field.source != '*' else name
            if source == snake_key:
                return name
        return snake_key
