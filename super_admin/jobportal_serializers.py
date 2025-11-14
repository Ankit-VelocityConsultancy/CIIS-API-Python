from super_admin.api_serializers import *
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from .utils import safe_value
from .utils import safe_value_serializer
from .models import *
from .models import (
    User,
    JobSeekerProfile,
    JobSeekerEducation,
    JobSeekerEmploymentDetails,
    JobSeekerWorkPreferences
)
import logging
logger = logging.getLogger(__name__)
logger = logging.getLogger('student_registration')
handler = logging.FileHandler('student_registration.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger = logging.getLogger('student_registration')


# class JobSeekerProfileSerializer(serializers.ModelSerializer):
#     first_name = serializers.CharField(source='user.first_name')
#     last_name = serializers.CharField(source='user.last_name')
#     email = serializers.EmailField(source='user.email')
#     mobile = serializers.CharField(source='user.mobile')

#     class Meta:
#         model = JobSeekerProfile
#         fields = [
#             'id', 
#             'first_name', 
#             'last_name', 
#             'email', 
#             'mobile', 
#             'resume', 
#             'work_status', 
#             'created_at',
#             'updated_at'
#         ]
#         read_only_fields = ['id', 'created_at','updated_at']

class JobSeekerProfileSerializer(serializers.ModelSerializer):
    # dynamic instead of source='user.first_name'
    first_name = serializers.SerializerMethodField()
    last_name  = serializers.CharField(source='user.last_name', read_only=True)
    email      = serializers.EmailField(source='user.email',    read_only=True)
    mobile     = serializers.CharField(source='user.mobile',    read_only=True)
    resume_url = serializers.SerializerMethodField()

    class Meta:
        model = JobSeekerProfile
        fields = [
            'id',
            'first_name', 'last_name', 'email', 'mobile',
            'resume',
            'resume_url',
            'work_status',
            'city',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'first_name', 'last_name', 'email', 'mobile', 'resume_url'
        ]

    def get_first_name(self, obj):
        """
        If the user is a student, return Student.name.
        We avoid hard-imports by using the reverse relation: user.student_set.
        This works regardless of the concrete student model class name.
        """
        user = obj.user
        try:
            if getattr(user, "is_student", False):
                # reverse FK: Student.user -> user.student_set
                student_qs = getattr(user, "student_set", None)
                if student_qs:
                    student = student_qs.first()
                    if student and getattr(student, "name", None):
                        return student.name
        except Exception as e:
            logger.warning(f"get_first_name student lookup failed for user_id={user.id}: {e}")

        # Non-student fallback chain
        if getattr(user, "first_name", None):
            return user.first_name
        # try full name, else a friendly default based on email
        full = getattr(user, "get_full_name", lambda: "")()
        if full:
            return full.split(" ")[0]
        email = getattr(user, "email", "") or ""
        return email.split("@")[0] if "@" in email else (email or "User")

    def get_resume_url(self, obj):
        try:
            if not obj.resume:
                return None
            request = self.context.get('request')
            return request.build_absolute_uri(obj.resume.url) if request else obj.resume.url
        except Exception as e:
            logger.warning(f"resume_url build failed for user={obj.user_id}: {e}")
            return None
class JobSeekerRegistrationSerializer(serializers.ModelSerializer):
    work_status = serializers.CharField(write_only=True, required=False)
    resume = serializers.FileField(write_only=True, required=False)
    city = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'password',
            'mobile',
            'work_status',
            'resume',
            'city'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered")
        return value

    def validate_mobile(self, value):
        if User.objects.filter(mobile=value).exists():
            raise serializers.ValidationError("This mobile number is already registered")
        return value

    def create(self, validated_data):
        work_status = validated_data.pop('work_status', None)
        resume = validated_data.pop('resume', None)
        city = validated_data.pop('city', None)

        # Create User
        validated_data['password'] = make_password(validated_data['password'])
        validated_data['is_jobseeker'] = True
        user = User.objects.create(**validated_data)

        # Create JobSeekerProfile
        JobSeekerProfile.objects.create(
            user=user,
            work_status=work_status,
            resume=resume,
            city=city
        )

        return user

class JobSeekerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

# class JobSeekerEducationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = JobSeekerEducation
#         fields = [
#             'id',
#             'education_details',
#             'key_skills',
#             'created_at',
#             'updated_at'
#         ]
#         read_only_fields = ['id', 'created_at', 'updated_at']

#     def validate_education_details(self, value):
#         if not isinstance(value, list):
#             raise serializers.ValidationError("education_details must be a list.")
#         return value

class JobSeekerEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSeekerEducation
        fields = ['id', 'education_details', 'key_skills', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_education_details(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("education_details must be a list.")
        return value

    def validate_key_skills(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("key_skills must be a list.")
        # optional: enforce list[str]
        if not all(isinstance(x, str) for x in value):
            raise serializers.ValidationError("key_skills must be a list of strings.")
        return value


# class JobSeekerWorkPreferencesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = JobSeekerWorkPreferences
#         fields = [
#             'id',
#             'preferred_locations',
#             'preferred_salary',
#             'gender',
#             'created_at',
#             'updated_at'
#         ]
#         read_only_fields = ['id', 'created_at', 'updated_at']

class JobSeekerWorkPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSeekerWorkPreferences
        fields = ['id', 'preferred_locations', 'preferred_salary', 'gender', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_preferred_locations(self, value):
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("preferred_locations must be a list.")
        return value

    def validate_preferred_salary(self, value):
        if value is None:
            return value
        try:
            # works for DecimalField/FloatField/numeric-like strings
            if float(value) < 0:
                raise serializers.ValidationError("preferred_salary cannot be negative.")
        except (TypeError, ValueError):
            raise serializers.ValidationError("preferred_salary must be numeric.")
        return value


# class JobSeekerEmploymentDetailsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = JobSeekerEmploymentDetails
#         fields = [
#             'id',
#             'is_currently_employed',
#             'total_work_exp_years',
#             'total_work_exp_months',
#             'company_name',
#             'current_job_title',
#             'current_city',
#             'start_date',
#             'end_date',
#             'is_current_job',
#             'annual_salary',
#             'notice_period',
#             'created_at',
#             'updated_at'
#         ]
#         read_only_fields = ['id', 'created_at', 'updated_at']

class JobSeekerEmploymentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSeekerEmploymentDetails
        fields = [
            'id',
            'is_currently_employed',
            'total_work_exp_years',
            'total_work_exp_months',
            'company_name',
            'current_job_title',
            'current_city',
            'start_date',
            'end_date',
            'is_current_job',
            'annual_salary',
            'notice_period',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        start = attrs.get('start_date') or getattr(self.instance, 'start_date', None)
        end   = attrs.get('end_date')   or getattr(self.instance, 'end_date', None)
        if start and end and end < start:
            raise serializers.ValidationError({"end_date": "end_date cannot be earlier than start_date."})

        years  = attrs.get('total_work_exp_years')  or getattr(self.instance, 'total_work_exp_years', 0)
        months = attrs.get('total_work_exp_months') or getattr(self.instance, 'total_work_exp_months', 0)
        if years < 0 or months < 0 or months > 11:
            raise serializers.ValidationError({"total_work_exp_months": "Use 0–11 for months; years/months cannot be negative."})
        return attrs


        
class JobApplicationSerializer(serializers.ModelSerializer):
    job_post = serializers.PrimaryKeyRelatedField(queryset=JobPost.objects.all())
    
    class Meta:
        model = JobSeekerApplication
        fields = ['id', 'user', 'job_post', 'resume', 'status', 'application_date']
        read_only_fields = ['id', 'user', 'status', 'application_date']
        extra_kwargs = {
            'resume': {'required': False, 'allow_null': True}
        }

    def validate(self, data):
        request = self.context.get('request')
        job_post = data.get('job_post')
        user = request.user

        # Check if already applied (redundant with view check, but good for API safety)
        if JobSeekerApplication.objects.filter(user=user, job_post=job_post).exists():
            raise serializers.ValidationError("You have already applied for this job")

        return data

    def create(self, validated_data):
        # Get the user from the request context
        validated_data['user'] = self.context['request'].user
        
        # Ensure resume is handled properly (might be None)
        if 'resume' not in validated_data or validated_data['resume'] is None:
            validated_data['resume'] = None
            
        try:
            return super().create(validated_data)
        except Exception as e:
            logger.error(f"Error in serializer create: {str(e)}")
            raise
        

class JobApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSeekerApplication  # Updated model name
        fields = ['status']

class JobApplicationDetailSerializer(serializers.ModelSerializer):
    job_post_title = serializers.CharField(source='job_post.job_title', read_only=True)
    company_name = serializers.CharField(source='job_post.company_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = JobSeekerApplication  # Updated model name
        fields = [
            'id', 'job_post', 'job_post_title', 'company_name',
            'status', 'status_display', 'application_date',
            'last_status_change', 'application_viewed',
            'resume_viewed', 'resume'
        ]
        read_only_fields = [
            'id', 'job_post_title', 'company_name', 'status_display',
            'application_date', 'last_status_change', 'application_viewed',
            'resume_viewed'
        ]

class JobApplicationHRSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_mobile = serializers.CharField(source='user.mobile', read_only=True)
    job_post_title = serializers.CharField(source='job_post.job_title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = JobSeekerApplication  # Updated model name
        fields = [
            'id', 'user', 'user_name', 'user_email',
            'user_mobile', 'job_post', 'job_post_title', 'status',
            'status_display', 'application_date', 'last_status_change',
            'application_viewed', 'application_viewed_at', 'resume_viewed',
            'resume_viewed_at', 'resume', 'notes'
        ]
    
    def get_user_name(self, obj):
        return obj.user.get_full_name()  # Using get_full_name() from User model
      


class jobportAdditionalBenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job_Portal_AdditionalBenefit
        fields = ['id', 'name','is_active']

class jobportRequiredSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job_Portal_RequiredSkill
        fields = ['id', 'name','is_active']


class jobportLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job_Portal_Language
        fields = ['id', 'name','is_active']


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['id', 'name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class JobPostSerializer(serializers.ModelSerializer):
    # Write-only ID inputs
    industries = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        default=list
    )
    industry_details = serializers.SerializerMethodField(read_only=True)

    qualifications = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, 
        required=False, 
        default=list
    )
    additional_benefits = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, 
        required=False, 
        default=list
    )
    department = serializers.IntegerField(
        write_only=True, 
        required=False, 
        allow_null=True
    )
    required_skills = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, 
        required=False, 
        default=list
    )
    languages_known = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, 
        required=False, 
        default=list
    )

    # Text-based list fields
    responsibilities = serializers.ListField(
        child=serializers.CharField(allow_blank=True, trim_whitespace=True),
        required=False,
        default=list
    )
    requirements = serializers.ListField(
        child=serializers.CharField(allow_blank=True, trim_whitespace=True),
        required=False,
        default=list
    )
    screening_questions = serializers.ListField(
        child=serializers.CharField(allow_blank=True, trim_whitespace=True),
        required=False,
        default=list
    )

    # Read-only detail fields
    qualifications_detail = serializers.SerializerMethodField(read_only=True)
    additional_benefits_detail = serializers.SerializerMethodField(read_only=True)
    department_detail = serializers.SerializerMethodField(read_only=True)
    required_skills_detail = serializers.SerializerMethodField(read_only=True)
    languages_known_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = JobPost
        fields = [
            'id', 'company_name', 'posted_by', 'job_title', 'job_location',
            'min_experience', 'max_experience', 'salary_min', 'salary_max',
            'qualifications', 'additional_benefits', 'department',
            'industries','industry_details',
            'required_skills', 'languages_known',
            'qualifications_detail', 'additional_benefits_detail', 'department_detail',
            'required_skills_detail', 'languages_known_detail',
            'responsibilities', 'requirements',
            'gender_preference', 'screening_questions', 'job_description',
            'allow_direct_calls', 'expire_date', 'is_active', 'posted_date', 'created_at'
        ]
        read_only_fields = [
            'id', 'posted_by', 'posted_date', 'created_at',
            'qualifications_detail', 'additional_benefits_detail', 'department_detail',
            'required_skills_detail', 'languages_known_detail', 'industry_details'
        ]

    # ---- Detail getters ----
    def get_industry_details(self, obj):
        return self._get_related_objects(obj.industry_ids, Industry)

    def get_qualifications_detail(self, obj):
        return self._get_related_objects(obj.qualification_ids, Job_Portal_Qualification)

    def get_additional_benefits_detail(self, obj):
        return self._get_related_objects(obj.additional_benefit_ids, Job_Portal_AdditionalBenefit)

    def get_department_detail(self, obj):
        if obj.department_id:
            try:
                dept = Job_Portal_Department.objects.get(id=obj.department_id)
                return {'id': dept.id, 'name': dept.name}
            except Job_Portal_Department.DoesNotExist:
                return None
        return None

    def get_required_skills_detail(self, obj):
        return self._get_related_objects(obj.required_skill_ids, Job_Portal_RequiredSkill)

    def get_languages_known_detail(self, obj):
        return self._get_related_objects(obj.language_ids, Job_Portal_Language)

    def _get_related_objects(self, ids, model_class):
        if not ids:
            return []
        
        # Check if the model has is_active field
        if hasattr(model_class, 'is_active'):
            objects = model_class.objects.filter(id__in=ids, is_active=True)
        else:
            objects = model_class.objects.filter(id__in=ids)
    
        return [{'id': o.id, 'name': o.name} for o in objects]

    # ---- Validation ----
    def validate(self, data):
        # Industry validation
        if 'industries' in data and data['industries']:
            incoming_industries = data['industries']
            existing_industry_ids = set(Industry.objects.filter(
                id__in=incoming_industries, 
                is_active=True
            ).values_list('id', flat=True))
            
            if len(existing_industry_ids) != len(incoming_industries):
                missing_ids = list(set(incoming_industries) - existing_industry_ids)
                raise serializers.ValidationError({
                    "industries": f"These industry IDs don't exist or are inactive: {missing_ids}"
                })

        # Department validation
        if 'department' in data and data['department']:
            if not Job_Portal_Department.objects.filter(id=data['department']).exists():
                raise serializers.ValidationError({"department": "Department does not exist"})

        # Validate all ID-based relationships
        for field, model in [
            ('qualifications', Job_Portal_Qualification),
            ('additional_benefits', Job_Portal_AdditionalBenefit),
            ('required_skills', Job_Portal_RequiredSkill),
            ('languages_known', Job_Portal_Language),
        ]:
            if field in data and data[field]:
                incoming = data[field]
                existing_ids = set(model.objects.filter(id__in=incoming).values_list('id', flat=True))
                if len(existing_ids) != len(incoming):
                    missing_ids = list(set(incoming) - existing_ids)
                    raise serializers.ValidationError({field: f"These IDs don't exist: {missing_ids}"})

        # Handle comma-separated strings from frontend
        for field in ['responsibilities', 'requirements', 'screening_questions']:
            if field in data:
                if isinstance(data[field], str):
                    if data[field].strip() == '':
                        data[field] = []
                    else:
                        data[field] = [item.strip() for item in data[field].split(',') if item.strip()]
                elif isinstance(data[field], list):
                    # Clean list items
                    data[field] = [item.strip() for item in data[field] if item.strip()]

        # Validate list fields
        for field in ['responsibilities', 'requirements', 'screening_questions']:
            if field in data and len(data[field]) > 50:
                raise serializers.ValidationError({field: "Cannot have more than 50 items"})
            if field in data and any(len(item) > 200 for item in data[field]):
                raise serializers.ValidationError({field: "Each item must be less than 200 characters"})

        return data

    # ---- Create/Update mapping ----
    def create(self, validated_data):
        validated_data['industry_ids'] = validated_data.pop('industries', [])
        validated_data['qualification_ids'] = validated_data.pop('qualifications', [])
        validated_data['additional_benefit_ids'] = validated_data.pop('additional_benefits', [])
        validated_data['department_id'] = validated_data.pop('department', None)
        validated_data['required_skill_ids'] = validated_data.pop('required_skills', [])
        validated_data['language_ids'] = validated_data.pop('languages_known', [])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'industries' in validated_data:
            instance.industry_ids = validated_data.pop('industries')
        if 'qualifications' in validated_data:
            instance.qualification_ids = validated_data.pop('qualifications')
        if 'additional_benefits' in validated_data:
            instance.additional_benefit_ids = validated_data.pop('additional_benefits')
        if 'department' in validated_data:
            instance.department_id = validated_data.pop('department')
        if 'required_skills' in validated_data:
            instance.required_skill_ids = validated_data.pop('required_skills')
        if 'languages_known' in validated_data:
            instance.language_ids = validated_data.pop('languages_known')
        return super().update(instance, validated_data)

class jobportQualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job_Portal_Qualification
        fields = '__all__'

class jobportDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job_Portal_Department
        fields = '__all__'
        
# serializers.py
from django.conf import settings
from rest_framework import serializers

class WhatsAppSendSerializer(serializers.Serializer):
    phone = serializers.CharField()

    # NEW: which campaign to use (defaults to NEW_CAMPAIGN)
    campaign_key = serializers.ChoiceField(
        choices=list(settings.AISENSY_CAMPAIGNS.keys()),
        required=False,
        default="NEW_CAMPAIGN",
    )

    # Option A: direct params
    template_params = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )

    # Option B: let backend build params
    name = serializers.CharField(required=False, allow_blank=True)  # used by both campaigns

    # EXAM_DETAILS fields (only needed if you don't pass template_params)
    subject_name = serializers.CharField(required=False, allow_blank=True)
    studypattern = serializers.CharField(required=False, allow_blank=True)
    semyear = serializers.CharField(required=False, allow_blank=True)
    portal_url = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    mobile = serializers.CharField(required=False, allow_blank=True)
    start_date = serializers.CharField(required=False, allow_blank=True)
    end_date = serializers.CharField(required=False, allow_blank=True)
    start_time = serializers.CharField(required=False, allow_blank=True)
    end_time = serializers.CharField(required=False, allow_blank=True)

    source = serializers.CharField(required=False, allow_blank=True)
    media_url = serializers.URLField(required=False)
    media_filename = serializers.CharField(required=False)

    def validate(self, data):
        # media must be both or neither
        if ("media_url" in data) ^ ("media_filename" in data):
            raise serializers.ValidationError("Provide both media_url and media_filename or neither.")

        # If no template_params, ensure required inputs exist for EXAM_DETAILS so we can build them
        if not data.get("template_params") and data.get("campaign_key") == "EXAM_DETAILS":
            required = ["subject_name","studypattern","semyear","email","start_date","end_date","start_time","end_time"]
            missing = [f for f in required if not data.get(f)]
            if missing:
                raise serializers.ValidationError({"detail": f"Missing fields for EXAM_DETAILS: {', '.join(missing)}"})
        return data
