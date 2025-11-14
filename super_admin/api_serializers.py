from rest_framework import serializers
from super_admin.models import *
from django.contrib.auth import authenticate


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'is_verified', 'is_student', 'is_data_entry', 'is_fee_clerk', 'is_superuser']

    def validate(self, data):
        required_fields = ['email', 'password', 'is_verified', 'is_student', 'is_data_entry', 'is_fee_clerk']
        
        for field in required_fields:
            if field not in data or data[field] is None:
                raise serializers.ValidationError({field: f"{field} is required."})

        # is_superuser should not be required unless it's for a superuser
        # In the POST request for user creation, let's set `is_superuser` conditionally
        return data
    
    def create(self, validated_data):
      user = User.objects.create(
          email=validated_data['email'],
          is_verified=validated_data['is_verified'],
          is_student=validated_data['is_student'],
          is_data_entry=validated_data['is_data_entry'],
          is_fee_clerk=validated_data['is_fee_clerk']
      )
      user.set_password(validated_data['password'])
      user.save()
      return user


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=["email","password"]
        extra_kwargs={
        'email': {'validators': []},  # Disable the default unique validator for email and allow duplicate email
        }
    def validate(self, attrs):
        email=attrs.get("email")
        errors={}
        try:
            user=User.objects.get(email=email)
            print(user,user.is_active)
            if not user.is_active:
                errors['email']="This account is inactive please contact administrator"
                raise serializers.ValidationError(errors)
        except User.DoesNotExist:
            errors["email"]="User not found please signup first"
            raise serializers.ValidationError(errors)
        return attrs
    

class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['id', 'university_name', 'university_address', 'university_city', 'university_state', 'university_pincode', 'university_logo', 'registrationID']

class PaymentModesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentModes
        fields = ['id', 'name', 'status', 'created_time', 'modified_time']

class FeeReceiptOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeReceiptOptions
        fields = ['id', 'name', 'status', 'created_time', 'modified_time']
        read_only_fields = ['id', 'created_time', 'modified_time']

    def validate_name(self, value):
        """
        Ensure the name is not empty and does not already exist in a case-insensitive manner.
        """
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty or just whitespace.")

        # Check for uniqueness during both creation and update
        if FeeReceiptOptions.objects.filter(name__iexact=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("A FeeReceiptOption with this name already exists.")
        return value
    
class BankNamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankNames
        fields = ['id', 'name', 'status', 'created_time', 'modified_time']


class SessionNamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionNames
        fields = ['id', 'name', 'status', 'created_time', 'modified_time']

class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True, min_length=8)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs
    
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['name']

class StreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = ['name']

class SubStreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubStream
        fields = ['name']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        
        
class EnrolledSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrolled
        fields = '__all__'  # or specify the fields you want to include
        
class StudentDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDocuments
        exclude = ('student',)
  
class QualificationSerializer(serializers.ModelSerializer):
    others = serializers.JSONField(required=False)

    class Meta:
        model = Qualification
        fields = '__all__'
        
class AdditionalEnrollmentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalEnrollmentDetails
        fields = ['counselor_name','reference_name','university_enrollment_id','student']
        
        
class StudentSearchSerializer(serializers.ModelSerializer):
  class Meta:
    model=Student
    fields=["id",'enrollment_id','name']
    

class CourseSerializerTwo(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['name', 'year', 'created_by', 'modified_by']
        read_only_fields = ['created_by', 'modified_by']

    def create(self, validated_data):
        # The university is now passed directly from the view
        return Course.objects.create(**validated_data)
      
class StreamSerializer(serializers.ModelSerializer):
    stream_name = serializers.CharField(source='name')  # Map `stream_name` to `name`

    class Meta:
        model = Stream
        fields = ['stream_name', 'sem', 'year', 'created_by', 'modified_by']
        
class SubStreamSerializer(serializers.ModelSerializer):
    substream_name = serializers.CharField(source='name')  # Map `substream_name` to `name`

    class Meta:
        model = SubStream
        fields = ['substream_name', 'created_time', 'modified_time']
        
        
class StudentSerializerWithDocumet(serializers.ModelSerializer):
  class Meta:
    model = Student
    fields=['name','father_name','mother_name','dateofbirth','mobile','email','gender','category','address','image','alternateaddress','alternate_mobile1','university']
    
    
    
class FeeReceiptOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeReceiptOptions
        fields = '__all__'  # You can specify fields like ['id', 'option_name', 'option_value']
        
class BankNamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankNames
        fields = '__all__'  # You can specify fields explicitly if needed

class PaymentModesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentModes
        fields = '__all__'  # You can specify fields explicitly if needed
        
        
class PaymentReceiptSerializer(serializers.ModelSerializer):
    fee_receipt_type = serializers.CharField(source="fee_reciept_type", allow_null=True)
    total_fees = serializers.CharField(source="semyearfees", allow_null=True)
    paid_amount = serializers.CharField(source="paidamount", allow_null=True)
    transaction_date = serializers.CharField(allow_null=True)
    payment_mode = serializers.CharField(source="paymentmode", allow_null=True)
    cheque_no = serializers.CharField(allow_null=True)
    bank_name = serializers.CharField(allow_null=True)
    remarks = serializers.CharField(allow_null=True)
    pending_amount = serializers.CharField(source="pendingamount", allow_null=True)
    advance_amount = serializers.CharField(source="advanceamount", allow_null=True)
    # Internal “receipt code” and external UTR/UPI:
    receipt_code = serializers.CharField(source="transactionID", allow_null=True)
    payment_transaction_id = serializers.CharField(source="payment_transactionID", allow_null=True)

    class Meta:
        model = PaymentReciept
        fields = [
            "id",
            "fee_receipt_type",
            "total_fees",
            "paid_amount",
            "transaction_date",
            "payment_mode",
            "cheque_no",
            "bank_name",
            "remarks",
            "pending_amount",
            "advance_amount",
            "receipt_code",
            "payment_transaction_id",
        ]
        


class Student_Quick_RegisteredSerializer(serializers.ModelSerializer):
  class Meta:
    model=Student
    fields=['id','name','mobile','email','enrollment_id','registration_id','is_enrolled']
    
    
class CountrySerializer(serializers.ModelSerializer):
  class Meta:
    model=Countries
    fields="__all__"
    
class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = States
        fields = "__all__"

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Cities
        fields = "__all__"
        
        
class AdditionalEnrollmentDetailsSerializerGET(serializers.ModelSerializer):
    class Meta:
        model = AdditionalEnrollmentDetails
        fields = ['university_enrollment_id', 'counselor_name', 'reference_name']

class StudentDocumentsSerializerGET(serializers.ModelSerializer):
    class Meta:
        model = StudentDocuments
        fields = ['id','document', 'document_name', 'document_ID_no', 'document_image_front', 'document_image_back']
        
class QualificationSerializerGET(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = [
            "secondary_year", "sr_year", "under_year", "post_year", "mphil_year",
            "secondary_board", "sr_board", "under_board", "post_board", "mphil_board",
            "secondary_percentage", "sr_percentage", "under_percentage", "post_percentage", "mphil_percentage",
            "secondary_document", "sr_document", "under_document", "post_document", "mphil_document",
            "others"
        ]

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'
        extra_kwargs = {
            'stream': {'required': False},
            'substream': {'required': False},
        }

    def create(self, validated_data):
        # `stream` and `substream` are provided via context, not the input data
        stream = self.context.get('stream')
        substream = self.context.get('substream', None)

        # Assign `stream` and `substream` to validated data
        validated_data['stream'] = stream
        validated_data['substream'] = substream

        # Create the subject instance
        return Subject.objects.create(**validated_data)
      
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'  


class StudentAppearingExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAppearingExam
        fields = [
            'exam',
            'student_id',
            'examstarttime',
            'examendtime',
            'examstartdate',
            'examenddate',
            'id'
        ]

class ExaminationSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True) 

    class Meta:
        model = Examination
        fields = [
            'id',
            'session',
            'studypattern',
            'semyear',
            'subject',
            'subject_name',
            'examtype',
            'totalmarks',
            'passingmarks',
            'totalquestions',
            'examduration',
        ]
        
class QuestionsSerializer(serializers.ModelSerializer):
    exam = serializers.PrimaryKeyRelatedField(queryset=Examination.objects.all())
    examduration = serializers.CharField(source='exam.examduration', read_only=True)

    class Meta:
        model = Questions
        fields = ['id','exam','question','image','type','marks','option1','option2','option3','option4','option5','option6','shortanswer','difficultylevel','examduration'
        ]
        
        
class ResultUploadedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultUploaded
        fields = '__all__'
        extra_kwargs = {
            'uploaded_file': {'required': False, 'allow_null': True}
        }

class ExaminationSubjectSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = Examination
        fields = '__all__'
        
class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Password must be at least 8 characters long."
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirm password must match the password."
    )

    def validate(self, data):
        """
        Check if the password and confirm_password match.
        """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("The passwords do not match.")
        return data
    
class StudentFeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFees
        fields = "__all__"
        

# app/serializers.py
from rest_framework import serializers

class PaymentReceiptCreateSerializer(serializers.Serializer):
    # Mandatory
    student_id = serializers.IntegerField()
    semyear = serializers.CharField(max_length=10)

    # Optional
    payment_for = serializers.CharField(max_length=50, required=False, allow_blank=True)
    payment_categories = serializers.CharField(max_length=50, required=False, allow_blank=True)
    payment_type = serializers.CharField(max_length=30, required=False, allow_blank=True)
    fee_reciept_type = serializers.CharField(max_length=30, required=False, allow_blank=True)
    transaction_date = serializers.CharField(max_length=20, required=False, allow_blank=True)
    cheque_no = serializers.CharField(max_length=50, required=False, allow_blank=True)
    bank_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    semyearfees = serializers.CharField(max_length=10, required=False, allow_blank=True)
    paidamount = serializers.CharField(max_length=10, required=False, allow_blank=True)
    pendingamount = serializers.CharField(max_length=10, required=False, allow_blank=True)
    advanceamount = serializers.CharField(max_length=10, required=False, allow_blank=True)
    paymentmode = serializers.CharField(max_length=20, required=False, allow_blank=True)
    remarks = serializers.CharField(max_length=500, required=False, allow_blank=True)
    session = serializers.CharField(max_length=100, required=False, allow_blank=True)
    uncleared_amount = serializers.CharField(max_length=10, required=False, allow_blank=True)
    status = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_semyear(self, value):
        if not str(value).strip():
            raise serializers.ValidationError("This field is required.")
        return value


class PaymentRecieptSerializer(serializers.ModelSerializer):
    total_fees_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentReciept
        fields = "__all__"
    
    def get_total_fees_display(self, obj):
        """Return pendingamount as total_fees_display"""
        return obj.pendingamount
        
class PaymentRecieptSerializersave(serializers.ModelSerializer):
    class Meta:
        model = PaymentReciept
        fields = "__all__"
        read_only_fields = ("id", "transactiontime", "transactionID", "student")

class SubjectResultItemSerializer(serializers.Serializer):
    subject_name = serializers.CharField()
    subject_code = serializers.CharField(allow_blank=True, required=False)
    max_marks = serializers.FloatField()
    total_questions = serializers.IntegerField(allow_null=True)
    marks_obtained = serializers.FloatField()

class StudentResultAggregateSerializer(serializers.Serializer):
    student_name = serializers.CharField()
    father_name = serializers.CharField(allow_null=True, required=False)
    enrollment_no = serializers.CharField()
    semyear = serializers.CharField()
    subjects = SubjectResultItemSerializer(many=True)
    total_obtained = serializers.FloatField()
    total_max = serializers.FloatField()
    
class AdditionalPaymentReceiptSerializer(serializers.ModelSerializer):
    # If you added these fields on the model, keep them optional:
    uploaded_file = serializers.FileField(required=False, allow_null=True)
    # If you also use an ImageField:
    # receipt_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Additional_PaymentReciept
        fields = "__all__"  # keep everything, but make some read-only
        read_only_fields = [
            "transactionID",     # generated in view
            "created_by",        # set in view
            "modified_by",       # set in view
            "transactiontime",   # auto_now
        ]
        # If you prefer __all__, ensure these aren't required by validation:
        extra_kwargs = {
            "uploaded_file": {"required": False, "allow_null": True},
            # "receipt_image": {"required": False, "allow_null": True},  # if used
        }

class AdditionalPaymentReceiptRefundSerializer(serializers.ModelSerializer):
    uploaded_file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Additional_PaymentReciept
        fields = "__all__"
        read_only_fields = [
            "transactionID",
            "created_by",
            "modified_by",
            "transactiontime",
            "student",          # we pass the actual Student instance in save()
            "payment_for",      # we force this to "Refund"
        ]
        extra_kwargs = {
            "uploaded_file": {"required": False, "allow_null": True},
        }
class UniversityReregistrtationFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityReregistrtationFee
        fields = '__all__'
        

class StudentDocumentsSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = StudentDocuments
        fields = '__all__'

class PersonalDocumentsSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = PersonalDocuments
        fields = '__all__'

class StudentFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentForm
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


from django.conf import settings
from rest_framework import serializers

from .models import CallRecording, DriveFolder, SyncLog, PlaybackLog


class CallRecordingSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    file_size_display = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()
    formatted_date = serializers.SerializerMethodField()
    audio_url = serializers.SerializerMethodField()  # <-- changed to computed URL

    class Meta:
        model = CallRecording
        fields = [
            'id', 'user', 'user_email', 'phone_number', 'local_file_path',
            'file_name', 'file_size', 'file_size_display', 'google_drive_file_id',
            'google_drive_link', 'drive_file_name', 'audio_url', 'duration',
            'duration_display', 'play_count', 'last_played_at', 'status',
            'upload_attempts', 'error_message', 'created_at', 'recording_date',
            'formatted_date', 'uploaded_at', 'last_synced_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_synced_at']

    def get_file_size_display(self, obj):
        return obj.get_file_size_display()

    def get_duration_display(self, obj):
        return obj.get_duration_display()

    def get_formatted_date(self, obj):
        return obj.recording_date.strftime('%b %d, %Y %I:%M %p') if obj.recording_date else None

    def get_audio_url(self, obj):
        """
        Prefer stored obj.audio_url, else build from local_file_path.
        Returns an absolute URL if request is in context.
        """
        request = self.context.get('request')

        # 1) If audio_url is already set
        if obj.audio_url:
            # If stored as relative path (/media/...), make it absolute
            if request and obj.audio_url.startswith('/'):
                return request.build_absolute_uri(obj.audio_url)
            return obj.audio_url

        # 2) Build from local_file_path if available
        if obj.local_file_path:
            rel_url = settings.MEDIA_URL + obj.local_file_path
            if request:
                return request.build_absolute_uri(rel_url)
            return rel_url

        # 3) Nothing available
        return None


class DriveFolderSerializer(serializers.ModelSerializer):
    recording_count = serializers.SerializerMethodField()

    class Meta:
        model = DriveFolder
        fields = ['id', 'name', 'folder_id', 'user', 'is_active', 'recording_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_recording_count(self, obj):
        # You can adjust this logic later if needed
        return CallRecording.objects.filter(drive_file_name__icontains=obj.name).count()


class SyncLogSerializer(serializers.ModelSerializer):
    folder_name = serializers.CharField(source='folder.name', read_only=True)

    class Meta:
        model = SyncLog
        fields = [
            'id', 'folder', 'folder_name', 'sync_started_at', 'sync_completed_at',
            'total_files_found', 'new_files_added', 'status', 'error_message'
        ]
        read_only_fields = ['id', 'sync_started_at']


class PlaybackLogSerializer(serializers.ModelSerializer):
    recording_name = serializers.CharField(source='recording.file_name', read_only=True)
    phone_number = serializers.CharField(source='recording.phone_number', read_only=True)

    class Meta:
        model = PlaybackLog
        fields = ['id', 'recording', 'recording_name', 'phone_number', 'played_at', 'ip_address', 'user_agent']
        read_only_fields = ['id', 'played_at']
