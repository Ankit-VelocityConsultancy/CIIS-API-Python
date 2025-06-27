from super_admin.api_serializers import *


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions', 'created_at', 'updated_at', 'is_active']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['id', 'name', 'status', 'created_at', 'updated_at']
        
class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ['id', 'name', 'status', 'created_at', 'updated_at']
        
class RoleStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleStatus
        fields = ['id', 'name', 'status', 'created_at', 'updated_at']
      
class CommonLeadLabelTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Common_Lead_Label_Tags
        fields = ['id', 'name', 'status', 'created_at', 'updated_at']

class CountriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Countries
        fields = ['id', 'shortname', 'name']


class StatesSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    country = serializers.PrimaryKeyRelatedField(queryset=Countries.objects.all())

    class Meta:
        model = States
        fields = ['id', 'name', 'country', 'country_name']
        

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'color', 'created_at', 'updated_at']
        
        
class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'
        
class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'
        

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'
        

class CommonLeadLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Common_Lead_Label_Tags
        fields = '__all__'

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'color']
