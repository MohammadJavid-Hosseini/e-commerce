from rest_framework import serializers


class RepresentAsStringMixin():
    def field_to_string(self, fields=None, field_name=None, many=False):
        request = self.context.get('request')
        if request.method == 'GET':
            fields[field_name] = serializers.StringRelatedField(many=many)
        return fields


# class IDForWriteMixin():
#     def two_fields(self, field_name, many=False):
#         field_name = serializers.StringRelatedField(many=many, read_only=True)
#         f"{field_name}_id" = serializers.PrimaryKeyRelatedField(
#             queryset = 
#         )
