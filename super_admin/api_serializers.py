from rest_framework import serializers
from super_admin.models import *
from django.contrib.auth import authenticate


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'is_verified', 'is_student', 'is_data_entry', 'is_fee_clerk']

    def validate(self, data):
        required_fields = ['email', 'password', 'is_verified', 'is_student', 'is_data_entry', 'is_fee_clerk']
        for field in required_fields:
            if field not in data or data[field] is None:
                raise serializers.ValidationError({field: f"{field} is required."})
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
    class Meta:
        model = PaymentReciept
        fields = '__all__'  # You can specify fields explicitly if needed

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
    class Meta:
        model = Examination
        fields = [
            'session',
            'studypattern',
            'semyear',
            'subject',
            'examtype',
            'totalmarks',
            'passingmarks',
            'totalquestions',
            'examduration',
        ]
        
class QuestionsSerializer(serializers.ModelSerializer):
    # Include any nested relations you need
    exam = serializers.PrimaryKeyRelatedField(queryset=Examination.objects.all())  # You can customize this if needed

    class Meta:
        model = Questions
        fields = '__all__'  # Alternatively, you can specify the fields explicitly like: ['id', 'question', 'marks', etc.]
        
class ResultUploadedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultUploaded
        fields = '__all__'