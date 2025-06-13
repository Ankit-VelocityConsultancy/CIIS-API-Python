from super_admin.api_serializers import *


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions', 'created_at', 'updated_at', 'is_active']