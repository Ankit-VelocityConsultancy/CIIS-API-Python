from super_admin.api_serializers import *
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from .utils import safe_value
from .utils import safe_value_serializer

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
        
        

class CitiesSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source='state.name', read_only=True)  # Human-readable name
    state = serializers.PrimaryKeyRelatedField(queryset=States.objects.all())  # FK ID field

    class Meta:
        model = Cities
        fields = ['id', 'name', 'state', 'state_name']
        

        
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

class RoleStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleStatus
        fields = ['id', 'name', 'status', 'created_at', 'updated_at']
        
class LeadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leads
        fields = '__all__'
        

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "mobile", "role", "first_name", "last_name", "is_student","is_active"]

class LeadSerializer_two(serializers.ModelSerializer):
    class Meta:
        model = Leads
        fields = ['first_name', 'last_name', 'landline', 'mobile_one', 'mobile_two', 'mobile_three', 'email_one', 'email_two', 'email_three', 'followup_date', 'owner', 'lead_status', 'common_lead_label_tag', 'lead_source', 'lead_categories', 'lead_color']

    def validate(self, data):
        # Ensure owner and first_name are provided
        if not data.get('owner'):
            raise serializers.ValidationError("Owner is required")
        if not data.get('first_name'):
            raise serializers.ValidationError("First name is required")
        return data
      
      
from .middleware import actor_context  # <-- import from step 1
class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leads
        fields = "__all__"

    def create(self, validated_data):
        instance = Leads(**validated_data)
        request = self.context.get("request")
        if request is not None:
            with actor_context(request.user):
                instance.save()
        else:
            instance.save()
        return instance

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        request = self.context.get("request")
        if request is not None:
            with actor_context(request.user):
                instance.save()
        else:
            instance.save()
        return instance


class JobPostStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPost
        fields = ['is_active']
        








        
#added by ankit to export report based on filter 01-08-2025

class FullLeadExportSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    co_owner_name = serializers.SerializerMethodField()
    lead_status_name = serializers.SerializerMethodField()
    lead_source_name = serializers.SerializerMethodField()
    lead_categories_name = serializers.SerializerMethodField()
    lead_color_name = serializers.SerializerMethodField()
    additional_details = serializers.SerializerMethodField()
    tag_names = serializers.SerializerMethodField()
    university_name = serializers.SerializerMethodField()  # <-- Add this line


    class Meta:
        model = Leads
        fields = [
            "id", "first_name", "last_name", "mobile", "mobile_one", "mobile_two", "mobile_three",
            "email", "email_one", "email_two", "email_three", "landline",
            "owner_name", "co_owner_name", "lead_status_name", "lead_source_name",
            "lead_categories_name", "lead_color_name", "followup_date", "created_at", "updated_at",
            "tag_names", "additional_details",'university_name'
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Clean all simple fields (model fields + method fields)
        for key, val in rep.items():
            if isinstance(val, str) or val is None or isinstance(val, float):
                rep[key] = safe_value_serializer(val)

        return rep

    def get_owner_name(self, obj):
        return safe_value_serializer(getattr(obj.owner, "first_name", None))

    def get_co_owner_name(self, obj):
        return safe_value_serializer(getattr(obj.co_owner, "first_name", None))

    def get_lead_status_name(self, obj):
        return safe_value_serializer(getattr(obj.lead_status, "name", None))

    def get_lead_source_name(self, obj):
        return safe_value_serializer(getattr(obj.lead_source, "name", None))

    def get_lead_categories_name(self, obj):
        return safe_value_serializer(getattr(obj.lead_categories, "name", None))

    def get_lead_color_name(self, obj):
        return safe_value_serializer(getattr(obj.lead_color, "name", None))

    def get_tag_names(self, obj):
        if obj.common_lead_label_tags:
            tags = Common_Lead_Label_Tags.objects.filter(id__in=obj.common_lead_label_tags)
            return [safe_value_serializer(tag.name) for tag in tags]
        return []

    def get_university_name(self, obj):
        return safe_value_serializer(getattr(obj.university, "university_name", None))


    def get_additional_details(self, obj):
        try:
            add = Leads_Addditional_Details.objects.select_related('state', 'country').get(lead=obj)
            return {
                "company_name": safe_value_serializer(add.company_name),
                "address": safe_value_serializer(add.address),
                "branch_area": safe_value_serializer(add.branch_area),
                "city": safe_value_serializer(add.city),
                "state_name": safe_value_serializer(getattr(add.state, "name", None)),
                "country_name": safe_value_serializer(getattr(add.country, "name", None))
            }
        except Leads_Addditional_Details.DoesNotExist:
            return {
                "company_name": "",
                "address": "",
                "branch_area": "",
                "city": "",
                "state_name": "",
                "country_name": ""
            }