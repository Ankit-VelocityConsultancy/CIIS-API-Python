from django import db
from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from .manager import UserManager
import os
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your models here.
#8000


class CustomUserManager(BaseUserManager):
  def create_user(self, email, password=None, **extra_fields):
    if not email:
        raise ValueError("The Email field must be set")
    email = self.normalize_email(email)
    user = self.model(email=email, **extra_fields)
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_superuser(self, email, password=None, **extra_fields):
    """
    Create and return a superuser with the given email and password.
    """
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)

    # Automatically set the role to Super Admin (ID=1)
    role = Role.objects.get(id=1)  # Assuming Super Admin role has ID=1
    extra_fields['role'] = role

    # Step 1: Create the user (first save to get an ID)
    user = self.create_user(email, password, **extra_fields)

    # Step 2: Assign 'assigned_by' to the same user ID (self-assigned)
    user.assigned_by = user  # This should be the user instance, not a string 
    user.save(update_fields=["assigned_by"])

    return user

default_permissions = {
    # New permissions for different sections
    "student_management": "no",
    "view_student": "no",
    "other_student": "no",
    "miscellaneous": "no",
    "add_course_subject":"no",
    "fees": "no",
    "examination": "no",
    "exam_master_data": "no",
    "roles": "no",
    "users": "no",
    "lead_master_data": "no",
    "hr_module":"no",
    "leads_menu": "no",
    "studentregistration":{"add": 0, "view": 0, "edit": 0, "delete": 0},
    "setexam":{"add": 0, "view": 0, "edit": 0, "delete": 0},
    "assignexam":{"add": 0, "view": 0, "edit": 0, "delete": 0},
    "subjectwiseanalysis":{"add": 0, "view": 0, "edit": 0, "delete": 0},
    "university": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "course": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "stream": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "substream": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "subject": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "student_registration": {"add": 0, "view": 0, "edit": 0, "delete": 0},    
    "dashboard": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "user": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "report": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "department": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "categories": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "subcategories": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "paymentmodes": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "sources": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "statuses": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "tags": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "colors": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "countries": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "states": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "templates": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "leads": {"add": 0, "view": 0, "edit": 0, "delete": 0},
    "settings": {"add": 0, "view": 0, "edit": 0, "delete": 0},
}

# Permissions for super admins (set to 1 for full access)
super_admin_permissions = {
    "student_management": "yes",
    "view_student": "yes",
    "other_student": "yes",
    "miscellaneous": "yes",
    "add_course_subject":"no",
    "fees": "yes",
    "examination": "yes",
    "exam_master_data": "yes",
    "roles": "yes",
    "users": "yes",
    "lead_master_data": "yes",
    "hr_module":"no",
    "leads_menu": "yes",
    "studentregistration":{"add": 1, "view": 1, "edit": 1, "delete": 1},
    "setexam":{"add": 1, "view": 1, "edit": 1, "delete": 1},
    "assignexam":{"add": 1, "view": 1, "edit": 1, "delete": 1},
    "subjectwiseanalysis":{"add": 1, "view": 1, "edit": 1, "delete": 1},
    "university": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "course": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "stream": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "substream": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "subject": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "student_registration": {"add": 1, "view": 1, "edit": 1, "delete": 1},  
    "dashboard": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "user": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "report": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "department": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "categories": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "subcategories": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "paymentmodes": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "sources": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "statuses": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "tags": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "colors": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "countries": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "states": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "templates": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "leads": {"add": 1, "view": 1, "edit": 1, "delete": 1},
    "settings": {"add": 1, "view": 1, "edit": 1, "delete": 1},
}


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    permissions = models.JSONField(default=dict)  # Default to an empty dict for permissions
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'role'

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, max_length=191)
    mobile = models.CharField(max_length=14)
    birthdate = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=80, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_data_entry = models.BooleanField(default=False)
    is_fee_clerk = models.BooleanField(default=False)
    is_jobseeker = models.BooleanField(default=False, null=True, blank=True)  # New flag for job seekers
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()  # Your custom manager

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'user'



class Countries(models.Model):
    shortname = models.CharField(max_length=5)
    name = models.CharField(max_length=150)
    class Meta:
        db_table = "countries"

class States(models.Model):
    name = models.CharField(max_length=150)
    country= models.ForeignKey(Countries,on_delete=models.CASCADE)
    class Meta:
        db_table = "states"

class Cities(models.Model):
    name = models.CharField(max_length=150)
    state= models.ForeignKey(States,on_delete=models.CASCADE)
    class Meta:
        db_table = "cities"


class University(models.Model):
    university_name = models.CharField(max_length=100)
    university_address = models.CharField(max_length=100,null=True,blank=True)
    university_city = models.CharField(max_length=100,null=True,blank=True)
    university_state = models.CharField(max_length=100,null=True,blank=True)
    university_pincode = models.CharField(max_length=100,null=True,blank=True)
    university_logo = models.FileField(upload_to='University_Logo/',blank=True ,null=True)
    registrationID = models.CharField(max_length=100)
    class Meta:
        db_table = 'university'

class Course(models.Model):
    university = models.ForeignKey(University,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    year = models.IntegerField(null=True,blank=True)
    created_by = models.CharField(max_length=100,null=True,blank=True)
    modified_by = models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        db_table = 'course'

class Stream(models.Model):
    name = models.CharField(max_length=50)
    sem = models.CharField(max_length=3,null=True,blank=True)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    year = models.IntegerField(null=True,blank=True)
    created_by = models.CharField(max_length=100,null=True,blank=True)
    modified_by = models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        db_table = 'stream'

class SubStream(models.Model):
    name = models.CharField(max_length=50)
    stream = models.ForeignKey(Stream,on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'substream'
        

class SemesterFees(models.Model):
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)
    tutionfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    examinationfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    bookfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    resittingfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    entrancefees = models.CharField(max_length=50,null=True,blank=True,default="0")
    extrafees = models.CharField(max_length=50,null=True,blank=True,default="0")
    discount = models.CharField(max_length=50,null=True,blank=True,default="0")
    totalfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    sem = models.CharField(max_length=10)
    created_by = models.CharField(max_length=100,null=True,blank=True)
    modified_by = models.CharField(max_length=100,null=True,blank=True)
    substream = models.ForeignKey(SubStream,on_delete=models.CASCADE,null=True,blank=True) ## added by Avani 14/08
    class Meta:
        db_table = 'semesterfees'

class YearFees(models.Model):
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)
    tutionfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    examinationfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    bookfees     = models.CharField(max_length=50,null=True,blank=True,default="0")
    resittingfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    entrancefees = models.CharField(max_length=50,null=True,blank=True,default="0")
    extrafees = models.CharField(max_length=50,null=True,blank=True,default="0")
    discount = models.CharField(max_length=50,null=True,blank=True,default="0")
    totalfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    year = models.CharField(max_length=10)
    created_by = models.CharField(max_length=100,null=True,blank=True)
    modified_by = models.CharField(max_length=100,null=True,blank=True)
    substream = models.ForeignKey(SubStream,on_delete=models.CASCADE,null=True,blank=True) ## added by Avani 14/08
    class Meta:
        db_table = 'yearfees'


class StudentFileUpload(models.Model):
    """
    Metadata for a bulk student upload. We do NOT store the file itself.
    """
    file_name   = models.CharField(max_length=255)              # reject duplicate names in view
    file_size   = models.BigIntegerField()
    file_hash   = models.CharField(max_length=64, unique=True)  # SHA-256 of file bytes
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.CharField(max_length=100, null=True, blank=True)

    # Optional stats
    total_rows   = models.IntegerField(default=0)
    success_rows = models.IntegerField(default=0)
    error_rows   = models.IntegerField(default=0)

    class Meta:
        db_table = 'student_file_uploads'
        indexes = [models.Index(fields=['file_name'])]

    def __str__(self):
        return f"{self.file_name} ({self.uploaded_at:%Y-%m-%d %H:%M})"

class Student(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    student_upload = models.ForeignKey(
    StudentFileUpload,
    on_delete=models.SET_NULL,
    null=True, blank=True,
    related_name='students'
)
    father_name = models.CharField(max_length=100,null=True,blank=True)
    mother_name = models.CharField(max_length=100,null=True,blank=True)
    dateofbirth = models.DateField(null=True,blank=True)
    mobile = models.CharField(max_length=14,unique=True)
    alternate_mobile1 = models.CharField(max_length=14,null=True,blank=True)
    email = models.EmailField(max_length=100,unique=True)
    alternateemail = models.EmailField(max_length=100,null=True,blank=True)
    gender = models.CharField(max_length=15,null=True,blank=True)
    category = models.CharField(max_length=50,null=True,blank=True)
    address = models.CharField(max_length = 500,null=True,blank=True)
    alternateaddress = models.CharField(max_length = 500,null=True, blank=True)
    nationality = models.CharField(max_length=20,null=True,blank=True)
    country = models.ForeignKey(Countries,on_delete=models.DO_NOTHING,null=True,blank=True)
    state = models.ForeignKey(States,on_delete=models.DO_NOTHING,null=True,blank=True)
    city = models.ForeignKey(Cities,on_delete=models.DO_NOTHING,null=True,blank=True)
    pincode = models.CharField(max_length=10,null=True,blank=True)
    registration_id = models.CharField(max_length=20,unique=True)
    old_university_enrollment_id = models.CharField(max_length=50,default=None,null=True,blank=True)
    new_university_enrollment_id = models.CharField(max_length=50,default=None,null=True,blank=True)
    enrollment_id = models.CharField(max_length=20,unique=True)
    enrollment_date = models.DateField(auto_now = True)
    university = models.ForeignKey(University,on_delete=models.CASCADE)
    image = models.FileField(upload_to='student_image/',blank=True ,null=True)
    verified = models.BooleanField(default=False)
    user = models.ForeignKey(User, null=True, blank=True,on_delete=models.DO_NOTHING)
    is_enrolled = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    created_by = models.CharField(max_length=100,null=True,blank=True)
    modified_by = models.CharField(max_length=100,null=True,blank=True)
    student_remarks = models.CharField(max_length=500,default="")
    registration_number = models.CharField(max_length=100, default="",blank=True,null=True)
    is_quick_register = models.BooleanField(default=False)
    is_pending= models.BooleanField(default=False,null=True,blank=True)
    is_approve= models.BooleanField(default=False,null=True,blank=True)

    class Meta:
        db_table = 'students'
        

class PendingVerification(models.Model):
  student_university_enrollment = models.CharField(max_length=20, blank=True, null=True)
  student_university_user_id = models.CharField(max_length=20, blank=True, null=True)
  student_university_password = models.CharField(max_length=100, blank=True, null=True)
  student = models.ForeignKey('super_admin.Student', on_delete=models.CASCADE)
  
  class Meta:
      db_table = 'pending_verification'


class Enrolled(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    stream = models.ForeignKey(Stream,on_delete=models.CASCADE)
    course_pattern = models.CharField(max_length=20)
    session = models.CharField(max_length=100,null=True,blank=True)
    entry_mode = models.CharField(max_length=100,null=True,blank=True)
    total_semyear = models.CharField(max_length=3,null=True,blank=True)
    current_semyear = models.CharField(max_length=3) 
    substream = models.ForeignKey(SubStream,on_delete=models.CASCADE,null=True,blank=True) ## added by Avani 14/08
    class Meta:
        db_table = 'enrolled'

# added by ankit 12-12-24
class StudyPattern(models.Model):
  name=models.CharField(max_length=100,null=True,blank=True)
  student = models.ForeignKey(Student,on_delete=models.CASCADE)
  class Meta:
        db_table = 'studypattern'

class AddmissionType(models.Model):
  name=models.CharField(max_length=100,null=True,blank=True)
  student = models.ForeignKey(Student,on_delete=models.CASCADE)
  class Meta:
        db_table = 'addmissiontype'


class StudentDocuments(models.Model):
    document = models.CharField(max_length=50)
    document_name = models.CharField(max_length=50,null=True,blank=True)
    document_ID_no = models.CharField(max_length=50,null=True,blank=True)
    document_image_front = models.FileField(upload_to='student_documents/',blank=True ,null=True)
    document_image_back = models.FileField(upload_to='student_documents/',blank=True ,null=True)
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    class Meta:
        db_table = 'studentdocuments'

class PersonalDocuments(models.Model):
    document = models.CharField(max_length=50)
    document_name = models.CharField(max_length=50,null=True,blank=True)
    document_ID_no = models.CharField(max_length=50,null=True,blank=True)
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    document_file = models.FileField(upload_to='personal_documents/', null=True, blank=True)

    class Meta:
        db_table = 'personaldocuments'

class PersonalDocumentsImages(models.Model):
    document = models.ForeignKey(PersonalDocuments,on_delete=models.CASCADE)
    document_image = models.FileField(upload_to='student_personal_documents/')
    class Meta:
        db_table = 'personaldocumentsimages'

class StudentFees(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    studypattern = models.CharField(max_length = 20)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)
    tutionfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    examinationfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    bookfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    resittingfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    entrancefees = models.CharField(max_length=50,null=True,blank=True,default="0")
    extrafees = models.CharField(max_length=50,null=True,blank=True,default="0")
    discount = models.CharField(max_length=50,null=True,blank=True,default="0")
    totalfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    sem = models.CharField(max_length=10)
    substream = models.ForeignKey(SubStream,on_delete=models.CASCADE,null=True,blank=True) ## added by Avani 14/08
    class Meta:
        db_table = 'studentfees'



class Qualification(models.Model):
    secondary_year = models.CharField(max_length=10,null=True,blank=True)
    sr_year = models.CharField(max_length=10,null=True,blank=True)
    under_year = models.CharField(max_length=10,null=True,blank=True)
    post_year = models.CharField(max_length=10,null=True,blank=True)
    mphil_year = models.CharField(max_length=10,null=True,blank=True)
    others_year = models.CharField(max_length=10,null=True,blank=True)
    
    secondary_board = models.CharField(max_length=50,null=True,blank=True)
    sr_board = models.CharField(max_length=50,null=True,blank=True)
    under_board = models.CharField(max_length=50,null=True,blank=True)
    post_board = models.CharField(max_length=50,null=True,blank=True)
    mphil_board = models.CharField(max_length=50,null=True,blank=True)
    others_board = models.CharField(max_length=50,null=True,blank=True)
    
    secondary_percentage = models.CharField(max_length=10,null=True,blank=True)
    sr_percentage = models.CharField(max_length=10,null=True,blank=True)
    under_percentage = models.CharField(max_length=10,null=True,blank=True)
    post_percentage = models.CharField(max_length=10,null=True,blank=True)
    mphil_percentage = models.CharField(max_length=10,null=True,blank=True)
    others_percentage = models.CharField(max_length=10,null=True,blank=True)
    
    secondary_document = models.FileField(upload_to='University_Documents/',blank=True ,null=True)
    sr_document = models.FileField(upload_to='University_Documents/',blank=True ,null=True)
    under_document = models.FileField(upload_to='University_Documents/',blank=True ,null=True)
    post_document = models.FileField(upload_to='University_Documents/',blank=True ,null=True)
    mphil_document = models.FileField(upload_to='University_Documents/',blank=True ,null=True)
    others_document = models.FileField(upload_to='University_Documents/',blank=True ,null=True)
    
    others = models.JSONField(default=list, blank=True ,null=True)
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    class Meta:
        db_table = 'qualification'

class AdditionalEnrollmentDetails(models.Model):
    counselor_name = models.CharField(max_length=100,null=True,blank=True)
    enrolled_by=models.CharField(max_length=100,null=True,blank=True)
    reference_name = models.CharField(max_length=100,null=True,blank=True)
    session = models.CharField(max_length=100,null=True,blank=True)
    entry_mode = models.CharField(max_length=100,null=True,blank=True)
    old_university_enrollment_id = models.CharField(max_length=30,null=True,blank=True)
    university_enrollment_id = models.CharField(max_length=30,null=True,blank=True)
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    class Meta:
        db_table = "additionalenrollmentdetails"

class UniversityEnrollment(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    type = models.CharField(max_length=10)
    course_id = models.CharField(max_length=20,null=True,blank=True)
    course_name = models.CharField(max_length=50,null=True,blank=True)
    enrollment_id = models.CharField(max_length=20)
    class Meta:
        db_table = "universityenrollment"


class Courier(models.Model):
    article_name = models.CharField(max_length=100,null=True,blank=True)
    courier_from = models.CharField(max_length=100,null=True,blank=True)
    courier_to = models.CharField(max_length=100,null=True,blank=True)
    booking_date = models.CharField(max_length=100,null=True,blank=True)
    courier_company = models.CharField(max_length=100,null=True,blank=True)
    tracking_id = models.CharField(max_length=100,null=True,blank=True)
    remarks = models.CharField(max_length=100,null=True,blank=True)
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    class Meta:
        db_table = 'courier'   

class EmailSentHistory(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    type = models.CharField(max_length=20)
    amount = models.CharField(max_length=20,null=True,blank=True)
    email = models.CharField(max_length=100)
    subject = models.CharField(max_length=100,null=True,blank=True)
    body = models.CharField(max_length=5000,null=True,blank=True)
    payment_categories = models.CharField(max_length=100,null=True,blank=True)
    payment_type = models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        db_table = 'emailsenthistory'


class TestDB(models.Model):
    name = models.CharField(max_length = 10)

class PaymentReciept(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    payment_for = models.CharField(max_length=50,null=True,blank=True)
    payment_categories = models.CharField(max_length=50,null=True,blank=True)
    payment_type = models.CharField(max_length=30,null=True,blank=True)
    fee_reciept_type = models.CharField(max_length=30,null=True,blank=True)
    transaction_date = models.CharField(max_length=20,null=True,blank=True)
    cheque_no = models.CharField(max_length=50,null=True,blank=True)
    bank_name = models.CharField(max_length=50,null=True,blank=True)
    semyearfees = models.CharField(max_length=10,null=True,blank=True)
    paidamount = models.CharField(max_length=10,null=True,blank=True)
    pendingamount = models.CharField(max_length=10,null=True,blank=True)
    advanceamount = models.CharField(max_length=10,null=True,blank=True)
    transactiontime = models.DateTimeField(auto_now=True)
    transactionID = models.CharField(max_length=50)
    payment_transactionID=models.CharField(max_length=50,null=True,blank=True)
    paymentmode = models.CharField(max_length=20,default="Online")
    remarks = models.CharField(max_length=500,null=True,blank=True)
    session = models.CharField(max_length=100,null=True,blank=True)
    semyear = models.CharField(max_length=10,null=True,blank=True)
    uncleared_amount = models.CharField(max_length=10,null=True,blank=True)
    status = models.CharField(max_length=100,null=True,blank=True)
    created_by = models.CharField(max_length=100,null=True,blank=True)
    modified_by = models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        db_table = 'paymentreciept'

class Additional_PaymentReciept(models.Model):
  student = models.ForeignKey(Student,on_delete=models.CASCADE)
  payment_for = models.CharField(max_length=50,null=True,blank=True)
  payment_categories = models.CharField(max_length=50,null=True,blank=True)
  payment_type = models.CharField(max_length=30,null=True,blank=True)
  fee_reciept_type = models.CharField(max_length=30,null=True,blank=True)
  transaction_date = models.CharField(max_length=20,null=True,blank=True)
  cheque_no = models.CharField(max_length=50,null=True,blank=True)
  bank_name = models.CharField(max_length=50,null=True,blank=True)
  semyearfees = models.CharField(max_length=10,null=True,blank=True)
  paidamount = models.CharField(max_length=10,null=True,blank=True)
  pendingamount = models.CharField(max_length=10,null=True,blank=True)
  advanceamount = models.CharField(max_length=10,null=True,blank=True)
  transactiontime = models.DateTimeField(auto_now=True)
  transactionID = models.CharField(max_length=50)
  payment_transactionID=models.CharField(max_length=50,null=True,blank=True)
  paymentmode = models.CharField(max_length=20,default="Online")
  remarks = models.CharField(max_length=500,null=True,blank=True)
  session = models.CharField(max_length=100,null=True,blank=True)
  semyear = models.CharField(max_length=10,null=True,blank=True)
  uncleared_amount = models.CharField(max_length=10,null=True,blank=True)
  status = models.CharField(max_length=100,null=True,blank=True)
  
  uploaded_file = models.FileField(upload_to="additional_receipts/",null=True,blank=True)
  
  created_by = models.CharField(max_length=100,null=True,blank=True)
  modified_by = models.CharField(max_length=100,null=True,blank=True)
  class Meta:
      db_table = 'additional_paymentreciept'


class UniversityExamination(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    amount = models.CharField(max_length=15)
    date = models.CharField(max_length=50)
    examination = models.CharField(max_length=50)
    semyear = models.CharField(max_length=20)
    paymentmode = models.CharField(max_length=50)
    remarks = models.CharField(max_length=1000)
    class Meta:
        db_table = "universityexamination"

class TempTransaction(models.Model):
    transactionID = models.CharField(max_length=100)
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    class Meta:
        db_table = 'temptransaction' 

class ResultUploaded(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    date = models.CharField(max_length=50,null=True,blank=True)
    examination = models.CharField(max_length=50,null=True,blank=True)
    semyear = models.CharField(max_length=20,null=True,blank=True)
    uploaded = models.CharField(max_length=10,null=True,blank=True)
    remarks = models.CharField(max_length=1000,null=True,blank=True)
    uploaded_file = models.FileField(upload_to="university_result/",null=True,blank=True)
    class Meta:
        db_table = 'resultuploaded'


class TransactionDetails(models.Model):
    transactionID = models.CharField(max_length=50)
    mihpayid = models.CharField(max_length=50,null=True,blank=True)
    mode = models.CharField(max_length=50,null=True,blank=True)
    status = models.CharField(max_length=50,null=True,blank=True)
    unmappedstatus = models.CharField(max_length=50,null=True,blank=True)
    key = models.CharField(max_length=50,null=True,blank=True)
    txnid = models.CharField(max_length=50,null=True,blank=True)
    amount = models.CharField(max_length=50,null=True,blank=True)
    cardCategory = models.CharField(max_length=50,null=True,blank=True)
    net_amount_debit = models.CharField(max_length=50,null=True,blank=True)
    addedon = models.CharField(max_length=50,null=True,blank=True)
    productinfo = models.CharField(max_length=50,null=True,blank=True)
    firstname =  models.CharField(max_length=50,null=True,blank=True)
    lastname = models.CharField(max_length=50,null=True,blank=True)
    email = models.CharField(max_length=50,null=True,blank=True)
    phone = models.CharField(max_length=50,null=True,blank=True)
    payment_source = models.CharField(max_length=50,null=True,blank=True)
    PG_TYPE = models.CharField(max_length=50,null=True,blank=True)
    bank_ref_num = models.CharField(max_length=50,null=True,blank=True)
    bankcode = models.CharField(max_length=50,null=True,blank=True)
    name_on_card = models.CharField(max_length=50,null=True,blank=True)
    cardnum = models.CharField(max_length=50,null=True,blank=True)
    class Meta:
        db_table = 'transactiondetails'

class Syllabus(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    stream = models.ForeignKey(Stream,on_delete=models.CASCADE)
    semester = models.CharField(max_length=10)
    pdf = models.FileField(upload_to='syllabus/',blank=True ,null=True)
    class Meta:
        db_table = 'syllabus'    

class StudentSyllabus(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    semester = models.CharField(max_length=10)
    pdf = models.FileField(upload_to='studentsyllabus/',blank=True ,null=True)
    class Meta:
        db_table = 'studentsyllabus'

class ImportCsvData(models.Model):
    import_csv_data = models.FileField(upload_to='Csv_Import/',blank=True ,null=True)
    class Meta:
        db_table = 'importcsv'



    



class Status(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    status = models.CharField(max_length=10,default="Offline")
    last_login = models.CharField(max_length=50,null=True,blank=True)
    last_logout = models.CharField(max_length=50,null=True,blank=True)
    class Meta:
        db_table = 'status'

class TestPaymentGateway(models.Model):
    transactionID = models.CharField(max_length=50)
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    class Meta:
        db_table = "testpaymentgateway"

class PaymentModes(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "payment_modes"

class FeeReceiptOptions(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "feereceipt_options"

class BankNames(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "bank_names"

class SessionNames(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "session_names"


class OtherUniversity(models.Model):
    university_name = models.CharField(max_length=100)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'other_university'

class OtherCourse(models.Model):
    name = models.CharField(max_length=100)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'other_course'

class OtherStream(models.Model):
    name = models.CharField(max_length=100)
    stream_id = models.CharField(max_length=50)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'other_stream'

class OtherSubStream(models.Model):
    name = models.CharField(max_length=100)
    substream_id = models.CharField(max_length=50)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'other_substream'


class OtherStudent(models.Model):
    class Meta:
        abstract=True
    name = models.CharField(max_length=100,null=True,blank=True)
    father_name = models.CharField(max_length=100,null=True,blank=True)
    mother_name = models.CharField(max_length=100,null=True,blank=True)
    dateofbirth = models.DateField(null=True,blank=True)
    mobile = models.CharField(max_length=14,unique=True)
    alternate_mobile1 = models.CharField(max_length=14,null=True,blank=True)
    email = models.EmailField(max_length=100,unique=True)
    alternateemail = models.EmailField(max_length=100,null=True,blank=True)
    gender = models.CharField(max_length=15,null=True,blank=True)
    category = models.CharField(max_length=50,null=True,blank=True)
    address = models.CharField(max_length = 500,null=True,blank=True)
    alternateaddress = models.CharField(max_length = 500,null=True,blank=True)
    nationality = models.CharField(max_length=20,null=True,blank=True)
    country = models.ForeignKey(Countries,on_delete=models.DO_NOTHING,null=True,blank=True)
    state = models.ForeignKey(States,on_delete=models.DO_NOTHING,null=True,blank=True)
    city = models.ForeignKey(Cities,on_delete=models.DO_NOTHING,null=True,blank=True)
    pincode = models.CharField(max_length=10,null=True,blank=True)
    registration_id = models.CharField(max_length=20,unique=True)
    old_university_enrollment_id = models.CharField(max_length=50,default=None,null=True,blank=True)
    new_university_enrollment_id = models.CharField(max_length=50,default=None,null=True,blank=True)
    enrollment_id = models.CharField(max_length=20,unique=True)
    enrollment_date = models.DateField(auto_now = True)
    image = models.FileField(upload_to='student_image_others/',blank=True ,null=True)
    verified = models.BooleanField(default=False)
    user = models.ForeignKey(User, null=True, blank=True,on_delete=models.DO_NOTHING)
    is_enrolled = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    created_by = models.CharField(max_length=100,null=True,blank=True)
    modified_by = models.CharField(max_length=100,null=True,blank=True)
    student_remarks = models.CharField(max_length=500,default="")
    registration_number = models.CharField(max_length=100, default="")
    is_quick_register = models.BooleanField(default=False)
    counselor_name = models.CharField(max_length=100,null=True,blank=True)
    reference_name = models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        db_table = 'other_students'

class OtherEnrolled(models.Model):
    student = models.ForeignKey(OtherStudent,on_delete=models.CASCADE)
    university = models.ForeignKey(OtherCourse,on_delete=models.CASCADE, null=True,blank=True)
    streamsity = models.ForeignKey(OtherUniversity,on_delete=models.CASCADE, null=True,blank=True)
    course = models.ForeignKey(OtherStream,on_delete=models.CASCADE, null=True,blank=True)
    substream = models.ForeignKey(OtherSubStream,on_delete=models.CASCADE, null=True,blank=True)
    course_pattern = models.CharField(max_length=20, null=True,blank=True)
    session = models.CharField(max_length=100,null=True,blank=True)
    entry_mode = models.CharField(max_length=100,null=True,blank=True)
    total_semyear = models.CharField(max_length=3,null=True,blank=True)
    current_semyear = models.CharField(max_length=3, null=True,blank=True) 
    remarks = models.CharField(max_length=500,default="")
    class Meta:
        db_table = 'other_enrolled'

class OtherQualification(models.Model):
    secondary_year = models.CharField(max_length=10,null=True,blank=True)
    sr_year = models.CharField(max_length=10,null=True,blank=True)
    under_year = models.CharField(max_length=10,null=True,blank=True)
    post_year = models.CharField(max_length=10,null=True,blank=True)
    mphil_year = models.CharField(max_length=10,null=True,blank=True)
    
    secondary_board = models.CharField(max_length=50,null=True,blank=True)
    sr_board = models.CharField(max_length=50,null=True,blank=True)
    under_board = models.CharField(max_length=50,null=True,blank=True)
    post_board = models.CharField(max_length=50,null=True,blank=True)
    mphil_board = models.CharField(max_length=50,null=True,blank=True)
    
    secondary_percentage = models.CharField(max_length=10,null=True,blank=True)
    sr_percentage = models.CharField(max_length=10,null=True,blank=True)
    under_percentage = models.CharField(max_length=10,null=True,blank=True)
    post_percentage = models.CharField(max_length=10,null=True,blank=True)
    mphil_percentage = models.CharField(max_length=10,null=True,blank=True)
    
    secondary_document = models.FileField(upload_to='University_Documents_Others/',blank=True ,null=True)
    sr_document = models.FileField(upload_to='University_Documents_Others/',blank=True ,null=True)
    under_document = models.FileField(upload_to='University_Documents_Others/',blank=True ,null=True)
    post_document = models.FileField(upload_to='University_Documents_Others/',blank=True ,null=True)
    mphil_document = models.FileField(upload_to='University_Documents_Others/',blank=True ,null=True)
    others = models.JSONField(default=list, blank=True ,null=True)
    student = models.ForeignKey(OtherStudent,on_delete=models.CASCADE)
    class Meta:
        db_table = 'other_qualification'

class OtherStudentDocuments(models.Model):
    document = models.CharField(max_length=50)
    document_name = models.CharField(max_length=50,null=True,blank=True)
    document_ID_no = models.CharField(max_length=50,null=True,blank=True)
    document_image_front = models.FileField(upload_to='student_documents/',blank=True ,null=True)
    document_image_back = models.FileField(upload_to='student_documents/',blank=True ,null=True)
    student = models.ForeignKey(OtherStudent,on_delete=models.CASCADE)
    class Meta:
        db_table = 'other_studentdocuments'

class OtherPaymentReciept(models.Model):
    student = models.ForeignKey(OtherStudent,on_delete=models.CASCADE)
    payment_for = models.CharField(max_length=50,null=True,blank=True)
    payment_categories = models.CharField(max_length=50,null=True,blank=True)
    payment_type = models.CharField(max_length=30,null=True,blank=True)
    fee_reciept_type = models.CharField(max_length=30,null=True,blank=True)
    transaction_date = models.CharField(max_length=20,null=True,blank=True)
    cheque_no = models.CharField(max_length=50,null=True,blank=True)
    bank_name = models.CharField(max_length=50,null=True,blank=True)
    semyearfees = models.CharField(max_length=10,null=True,blank=True)
    paidamount = models.CharField(max_length=10,null=True,blank=True)
    pendingamount = models.CharField(max_length=10,null=True,blank=True)
    advanceamount = models.CharField(max_length=10,null=True,blank=True)
    transactiontime = models.DateTimeField(auto_now=True)
    transactionID = models.CharField(max_length=50)
    paymentmode = models.CharField(max_length=20,default="Online")
    remarks = models.CharField(max_length=500,null=True,blank=True)
    session = models.CharField(max_length=100,null=True,blank=True)
    semyear = models.CharField(max_length=10,null=True,blank=True)
    uncleared_amount = models.CharField(max_length=10,null=True,blank=True)
    status = models.CharField(max_length=100,null=True,blank=True)
    created_by = models.CharField(max_length=100,null=True,blank=True)
    modified_by = models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        db_table = 'other_paymentreciept'
        
class Subject(models.Model):
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=50)
    stream = models.ForeignKey(Stream,on_delete=models.CASCADE)
    substream = models.ForeignKey(SubStream,on_delete=models.CASCADE,null=True,blank=True) ## added by Avani 12/11
    studypattern = models.CharField(max_length = 20, null=True, blank=True)
    semyear = models.CharField(max_length=20, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'subject'


class ExamFileUpload(models.Model):
    UPLOAD_TYPE_CHOICES = [
        ('bulk_exam', 'Bulk Exam Upload'),
        ('single_subject', 'Single Subject Exam Upload'),
    ]

    # ✅ FK to University (ensure the University table exists BEFORE this migration)
    university = models.ForeignKey(University,
        on_delete=models.CASCADE,
        related_name='exam_file_uploads',
        db_index=True,
    )

    file_name   = models.CharField(max_length=255)
    file_size   = models.BigIntegerField()
    file_hash   = models.CharField(max_length=64)  # SHA-256
    upload_type = models.CharField(max_length=20, choices=UPLOAD_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'exam_file_uploads'
        unique_together = [('university', 'file_hash', 'upload_type')]

    def __str__(self):
        return f"{self.file_name} - {self.university}"        
        
        

class Examination(models.Model):
    university = models.ForeignKey(University,on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    stream = models.ForeignKey(Stream,on_delete=models.CASCADE)
    substream = models.ForeignKey(SubStream,on_delete=models.CASCADE,null=True,blank=True) ## added by Avani 6/11
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE, default=None)
    excel_upload = models.ForeignKey(
        ExamFileUpload,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='examination'
    )
    examtype = models.CharField(max_length=100, null=True, blank=True)
    examduration = models.CharField(max_length=10, null=True, blank=True)
    studypattern = models.CharField(max_length = 20, null=True, blank=True)
    semyear = models.CharField(max_length=20, null=True, blank=True)
    session = models.CharField(max_length = 20, null=True, blank=True)
    totalquestions = models.CharField(max_length=10,null=True,blank=True)
    totalmarks = models.CharField(max_length=10)
    passingmarks = models.CharField(max_length=10, null=True, blank=True)
    active = models.BooleanField(default=True)
    archive = models.BooleanField(default=False)
    created_by = models.CharField(max_length=100,null=True,blank=True)
    modified_by = models.CharField(max_length=100,null=True,blank=True)
    class Meta:
      db_table = 'examination'
        
        

class Questions(models.Model):
    exam = models.ForeignKey(Examination, on_delete=models.CASCADE)
    # NEW: link back to the upload this question came from
    excel_upload = models.ForeignKey(
        ExamFileUpload,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='questions'
    )
    question = models.CharField(max_length=500)
    image = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    marks = models.CharField(max_length=100, null=True, blank=True)
    option1 = models.CharField(max_length=500, null=True, blank=True)
    option2 = models.CharField(max_length=500, null=True, blank=True)
    option3 = models.CharField(max_length=500, null=True, blank=True)
    option4 = models.CharField(max_length=500, null=True, blank=True)
    option5 = models.CharField(max_length=500, null=True, blank=True)
    option6 = models.CharField(max_length=500, null=True, blank=True)
    shortanswer = models.CharField(max_length=999, null=True, blank=True)
    answer = models.CharField(max_length=99, null=True, blank=True)
    difficultylevel = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'questions'

class Descriptive_Answer(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    exam = models.ForeignKey(Examination,on_delete=models.CASCADE)
    question = models.CharField(max_length=500)
    upload = models.FileField(upload_to='examination_uploads/',blank=True ,null=True)
    class Meta:
        db_table = "descriptive_answer"



class StudentAppearingExam(models.Model):
    exam = models.ForeignKey(Examination,on_delete=models.CASCADE)
    student_id = models.JSONField(default=list, blank=True ,null=True)
    examstarttime = models.TimeField(auto_now=False, auto_now_add=False,null=True, blank=True)
    examendtime = models.TimeField(auto_now=False, auto_now_add=False,null=True, blank=True)
    examstartdate = models.DateField(auto_now=False, auto_now_add=False,null=True, blank=True)
    examenddate = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    class Meta:
        db_table = 'studentappearingexam'
        
# Not use added by ankit 06-05-2025
class StudentExaminationTime(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    exam = models.CharField(max_length=100)
    time_in_minutes = models.CharField(max_length=100)
    # examdetails = models.ForeignKey(StudentAppearingExam, on_delete=models.CASCADE, null=True, blank=True) 
    class Meta:
        db_table = 'studentexaminationtime'
        
class Result(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    exam = models.ForeignKey(Examination,on_delete=models.CASCADE)
    total_question = models.CharField(max_length=10)
    attempted = models.CharField(max_length=10)
    total_marks = models.CharField(max_length=100,null=True,blank=True)
    score = models.CharField(max_length=10)
    result = models.CharField(max_length=10)
    created_by = models.CharField(max_length=100,null=True,blank=True)
    modified_by = models.CharField(max_length=100,null=True,blank=True)
    percentage=models.FloatField(default=100)
    examdetails = models.ForeignKey(StudentAppearingExam, on_delete=models.CASCADE, null=True, blank=True)  ## added by Ankit for multiple results on reassign change
    class Meta:
        db_table = 'result'
        
class SubmittedExamination(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    exam = models.ForeignKey(Examination,on_delete=models.CASCADE)
    question = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100,null=True,blank=True)
    marks = models.CharField(max_length=100,null=True,blank=True)
    marks_obtained = models.CharField(max_length=100,null=True,blank=True)
    submitted_answer = models.CharField(max_length=999,null=True,blank=True)
    answer = models.CharField(max_length=999,null=True,blank=True)
    result = models.CharField(max_length=100,null=True,blank=True)
    examdetails = models.ForeignKey(StudentAppearingExam, on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        db_table = "submitted_answer"

class ExamSession(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    exam = models.ForeignKey('Examination', on_delete=models.CASCADE)
    examdetails = models.ForeignKey(StudentAppearingExam, on_delete=models.CASCADE, null=True, blank=True)
    time_left_ms = models.BigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'exam', 'examdetails')
      
      
class Categories(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        

class Source(models.Model):
  name = models.CharField(max_length=255)
  status = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
      db_table = 'source'
      ordering = ['-created_at']

  def __str__(self):
      return self.name


class RoleStatus(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'role_status'

    def __str__(self):
        return self.name
      


class Common_Lead_Label_Tags(models.Model):
    id = models.BigAutoField(primary_key=True)   # explicit
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'common_lead_labels_tags'

    def __str__(self):
        return self.name

      
class Color(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=50)  # This field stores color values (e.g., HEX or name)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'colors'

    def __str__(self):
        return f"{self.name} ({self.color})"
      
class Leads(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    landline = models.CharField(max_length=100, null=True, blank=True)
    state=models.ForeignKey(States,on_delete=models.SET_NULL,null=True,blank=True)
    mobile = models.CharField(max_length=100, null=True, blank=True)
    mobile_one = models.CharField(max_length=100, null=True, blank=True)
    mobile_two = models.CharField(max_length=100, null=True, blank=True)
    mobile_three = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    email_one = models.CharField(max_length=100, null=True, blank=True)
    email_two = models.CharField(max_length=100, null=True, blank=True)
    email_three = models.CharField(max_length=100, null=True, blank=True)
    followup_date = models.DateField(null=True, blank=True)
    mobile_numbers = models.JSONField(default=dict, blank=True, null=True)
    email_addresses = models.JSONField(default=dict, blank=True, null=True)
    
    # Foreign Keys with db_index=True
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leads_as_owner", null=True, blank=True, db_index=True)
    co_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leads_as_co_owner", null=True, blank=True, db_index=True)
    lead_status = models.ForeignKey(RoleStatus, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    lead_source = models.ForeignKey(Source, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    lead_categories = models.ForeignKey(Categories, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    lead_color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    common_lead_label_tags = models.JSONField(default=list, blank=True, null=True)
    
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)


    lead_comments = models.JSONField(default=list, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    activity_log = models.JSONField(default=list, blank=True, null=True)  # <— add this

    class Meta:
        db_table = "leads"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.mobile_one})"

class Leads_Addditional_Details(models.Model):
    company_name = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField()
    branch_area = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    
    # Foreign Keys with null=True, blank=True to allow NULL values
    state = models.ForeignKey(States, on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey(Countries, on_delete=models.CASCADE, null=True, blank=True)
    lead = models.ForeignKey(Leads, on_delete=models.CASCADE, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "leads_additional_details"

    def __str__(self):
        return f"{self.company_name} ({self.city})"

#---------------job portal--------------------------------------

class JobSeekerProfile(models.Model):
    WORK_STATUS_CHOICES = [
        ("experienced", "I'm experienced"),
        ("fresher", "I'm a fresher"),
        ("student", "I'm a student"),

    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='jobseeker_profile')
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    work_status = models.CharField(max_length=20, choices=WORK_STATUS_CHOICES, blank=True, null=True)
    city=models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"

    class Meta:
        db_table = 'jobseeker_profile'

class JobSeekerEducation(models.Model):
    COURSE_TYPE_CHOICES = [
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='educations')
    education_details = models.JSONField(default=list)
    key_skills = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)  # Only this
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} Education"

    class Meta:
        db_table = 'jobseeker_education'

class JobSeekerEmploymentDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employment_history')
    is_currently_employed = models.BooleanField(default=False)
    total_work_exp_years = models.IntegerField(default=0)
    total_work_exp_months = models.IntegerField(default=0)
    company_name = models.CharField(max_length=200, default="")
    current_job_title = models.CharField(max_length=100, default="")
    current_city = models.CharField(max_length=100, default="")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current_job = models.BooleanField(default=False)
    annual_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notice_period = models.CharField(max_length=50, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company_name}"

    class Meta:
        db_table = 'jobseeker_employmentdetails'

class JobSeekerWorkPreferences(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_preferences')
    preferred_locations = models.JSONField(default=list, help_text="List of up to 10 preferred locations")
    preferred_salary = models.DecimalField(max_digits=10, decimal_places=2)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} Preferences"

    class Meta:
        db_table = 'jobseeker_workpreferences'

class JobSeekerApplication(models.Model):
    STATUS_CHOICES = [
        ("applied", "Applied"),
        ("viewed", "Viewed"),
        ("shortlisted", "Shortlisted"),
        ("interviewing", "Interviewing"),
        ("rejected", "Rejected"),
        ("hired", "Hired"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    job_post = models.ForeignKey('JobPost', on_delete=models.CASCADE)
    resume = models.FileField(upload_to='job_applications/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="applied")
    application_date = models.DateTimeField(auto_now_add=True)
    last_status_change = models.DateTimeField(auto_now=True)
    resume_viewed = models.BooleanField(default=False)
    resume_viewed_at = models.DateTimeField(null=True, blank=True)
    application_viewed = models.BooleanField(default=False)
    application_viewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'job_post')
        db_table = 'jobseeker_application'

    def __str__(self):
        return f"{self.user.get_full_name()} applied for {self.job_post.job_title}"

    def clean(self):
        pass

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def mark_resume_viewed(self):
        if not self.resume_viewed:
            self.resume_viewed = True
            self.resume_viewed_at = timezone.now()
            self.save()

    def update_status(self, new_status):
        if new_status not in dict(self.STATUS_CHOICES).keys():
            raise ValueError("Invalid status provided")
        self.status = new_status
        self.last_status_change = timezone.now()
        self.save()


class Job_Portal_AdditionalBenefit(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True,null=True,blank=True)

    def __str__(self):
        return self.name


class Job_Portal_Qualification(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True,null=True,blank=True)

    def __str__(self):
        return self.name


class Job_Portal_Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True,null=True,blank=True)

    def __str__(self):
        return self.name


class Job_Portal_RequiredSkill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True,null=True,blank=True)

    def __str__(self):
        return self.name


class Job_Portal_Language(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True,null=True,blank=True)

    def __str__(self):
        return self.name

class Industry(models.Model):
    name = models.CharField(max_length=120, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "industry"
        ordering = ["name"]

    def __str__(self):
        return self.name

class JobPost(models.Model):
    company_name = models.CharField(max_length=250)
    posted_by = models.ForeignKey("User", on_delete=models.CASCADE)
    job_title = models.CharField(max_length=255)
    job_location = models.CharField(max_length=255)
    min_experience = models.IntegerField(null=True, blank=True)
    max_experience = models.IntegerField(null=True, blank=True)
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    industry_ids = models.JSONField(default=list)  
    qualification_ids = models.JSONField(default=list)
    additional_benefit_ids = models.JSONField(default=list)
    department_id = models.IntegerField(null=True, blank=True)
    required_skill_ids = models.JSONField(default=list)
    language_ids = models.JSONField(default=list)

    # NEW FIELDS
    responsibilities = models.JSONField(default=list, blank=True)  # list[str]
    requirements = models.JSONField(default=list, blank=True)      # list[str]

    gender_preference = models.CharField(
        max_length=20,
        choices=[("Any", "Any"), ("Male", "Male"), ("Female", "Female")],
        default="Any"
    )
    screening_questions = models.JSONField(default=list, blank=True)
    job_description = models.TextField()
    allow_direct_calls = models.BooleanField(default=False)
    posted_date = models.DateTimeField(auto_now_add=True)
    expire_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

    class Meta:
        db_table = 'jobpost'
        

class UniversityReregistrtationFee(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='university_reregistration_fees', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_type= models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    examination = models.CharField(max_length=100, null=True, blank=True)
    semester_year = models.CharField(max_length=100, null=True, blank=True)
    payment_mode = models.CharField(max_length=100, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    attachment = models.FileField(upload_to='university_fees/', null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'UniversityReregistrtationFee'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"Fee Record {self.id}"

class StudentForm(models.Model):
    FORM_TYPES = [
        ('self_assessment', 'Self Assessment Form'),
        ('teacher_assessment', 'Teacher Assessment Form'),
        ('assignment_assessment', 'Assignment Assessment Form'),
        ('industrial_assessment', 'Industrial Assessment Form'),
        ('guardian_assessment', 'Guardian Assessment Form'),
    ]
    
    student_id = models.CharField(max_length=50)
    form_name = models.CharField(max_length=100)
    sem_year = models.CharField(max_length=20)
    remarks = models.TextField(blank=True, null=True)
    file_field = models.FileField(upload_to='student_forms/')
    form_type = models.CharField(max_length=100, choices=FORM_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_assessment_form'  
        unique_together = ['student_id', 'sem_year', 'form_type']
    
    def __str__(self):
        return f"{self.student_id} - {self.form_type} - {self.sem_year}"




# models.py
import os
from django.db import models
from django.conf import settings
from django.utils import timezone


class CallRecording(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Upload'),
        ('uploaded', 'Uploaded to Drive'),
        ('failed', 'Upload Failed'),
        ('synced', 'Synced from Drive'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True, default="")
    local_file_path = models.CharField(max_length=500, blank=True, null=True)
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField(help_text="File size in bytes", null=True, blank=True)

    # Google Drive fields
    google_drive_file_id = models.CharField(max_length=255, blank=True, null=True)
    google_drive_link = models.URLField(blank=True, null=True)
    drive_file_name = models.CharField(max_length=255, blank=True, null=True)

    # Playback fields
    audio_url = models.URLField(blank=True, null=True, help_text="Direct audio playback URL")
    duration = models.IntegerField(default=0, help_text="Duration in seconds")
    play_count = models.IntegerField(default=0, help_text="Number of times played")
    last_played_at = models.DateTimeField(blank=True, null=True)

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    upload_attempts = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)        # <-- NEW, used in update_fields
    recording_date = models.DateTimeField(default=timezone.now)
    uploaded_at = models.DateTimeField(null=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'call_recording'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['status']),
            models.Index(fields=['recording_date']),
        ]

    def __str__(self):
        return f"{self.phone_number} - {self.file_name}"

    def get_file_extension(self):
        return os.path.splitext(self.file_name)[1].lower()

    def get_file_size_display(self):
        if not self.file_size:
            return "0 B"
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} GB"

    def get_duration_display(self):
        if not self.duration:
            return "00:00"
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes:02d}:{seconds:02d}"


class DriveFolder(models.Model):
    name = models.CharField(max_length=255)
    folder_id = models.CharField(max_length=128, unique=True)  # Google Drive folder ID
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "drive_folder"

    def __str__(self):
        return f"{self.name} ({self.folder_id})"


class SyncLog(models.Model):
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    folder = models.ForeignKey(DriveFolder, on_delete=models.CASCADE)
    sync_started_at = models.DateTimeField(auto_now_add=True)
    sync_completed_at = models.DateTimeField(null=True, blank=True)
    total_files_found = models.IntegerField(default=0)
    new_files_added = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'sync_log'
        ordering = ['-sync_started_at']


class PlaybackLog(models.Model):
    recording = models.ForeignKey(CallRecording, on_delete=models.CASCADE)
    played_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'playback_log'
        ordering = ['-played_at']
