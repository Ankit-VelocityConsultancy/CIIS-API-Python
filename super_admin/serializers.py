from rest_framework import serializers
from .models import  States,Cities, University,Course,Stream,Student,Enrolled,Qualification,PaymentReciept,Syllabus,StudentSyllabus,Courier,SemesterFees,YearFees,StudentDocuments,StudentFees,PersonalDocuments,PersonalDocumentsImages,UniversityExamination,ResultUploaded,UniversityEnrollment,EmailSentHistory,Questions,Examination,SubmittedExamination,SubStream


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class StreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = '__all__'
        
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        
class EnrolledSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrolled
        fields = '__all__'
        
class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = '__all__'

class CourseYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['year']









class PaymentRecieptSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentReciept
        fields = '__all__'


class SyllabusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Syllabus
        fields = '__all__'



class CourierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = '__all__'


class SemesterFeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SemesterFees
        fields = '__all__'

class YearFeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = YearFees
        fields = '__all__'

class StudentDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDocuments
        fields = '__all__'
        
        
class StudentSyllabusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSyllabus
        fields = '__all__'    
        
class StudentFeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFees
        fields = '__all__'   


        


        
class PersonalDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalDocuments
        fields = '__all__' 

class PersonalDocumentsImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalDocumentsImages
        fields = '__all__'        

class UniversityExaminationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityExamination
        fields = '__all__'     

class ResultUploadedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultUploaded
        fields = '__all__'  

class UniversityEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityEnrollment
        fields = '__all__'  

class EmailSentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSentHistory
        fields = '__all__'  

class StatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = States
        fields = '__all__'  

class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cities
        fields = '__all__'  

class QuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = '__all__'  

class ExaminationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Examination
        fields = '__all__'  

class SubmittedExaminationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmittedExamination
        fields = '__all__'  

##added by Avani 14/08
class SubStreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubStream
        fields = '__all__'  
