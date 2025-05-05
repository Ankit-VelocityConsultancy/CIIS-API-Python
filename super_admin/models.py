from django import db
from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager
import os
# Create your models here.
#8000
class User(AbstractUser):
    username = None
    mobile = models.CharField(max_length=14)
    email = models.EmailField(unique=True)
    birthdate = models.DateField(null=True,blank=True)
    gender = models.CharField(max_length=50,null=True,blank=True)
    address = models.CharField(max_length = 80,null=True,blank=True)
    is_verified = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_data_entry = models.BooleanField(default=False)
    is_fee_clerk = models.BooleanField(default=False)
    
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] 
    class Meta:
        db_table = 'user'

class Countries(models.Model):
    shortname = models.CharField(max_length=5)
    name = models.CharField(max_length=150)
    phonecode = models.IntegerField(max_length=11)
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
        
class Subject(models.Model):
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=50)
    stream = models.ForeignKey(Stream,on_delete=models.CASCADE)
    substream = models.ForeignKey(SubStream,on_delete=models.CASCADE,null=True,blank=True) 
    studypattern = models.CharField(max_length = 20, null=True, blank=True)
    semyear = models.CharField(max_length=20, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'subject'

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

class Student(models.Model):
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
    registration_number = models.CharField(max_length=100, default="")
    is_quick_register = models.BooleanField(default=False)
    class Meta:
        db_table = 'students'

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
    date = models.CharField(max_length=50)
    examination = models.CharField(max_length=50)
    semyear = models.CharField(max_length=20)
    uploaded = models.CharField(max_length=10)
    remarks = models.CharField(max_length=1000)
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


class StudentExaminationTime(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    exam = models.CharField(max_length=100)
    time_in_minutes = models.CharField(max_length=100)
    class Meta:
        db_table = 'studentexaminationtime'
    



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


class Examination(models.Model):
    university = models.ForeignKey(University,on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    stream = models.ForeignKey(Stream,on_delete=models.CASCADE)
    substream = models.ForeignKey(SubStream,on_delete=models.CASCADE,null=True,blank=True) ## added by Avani 6/11
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE, default=None)
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
    exam = models.ForeignKey(Examination,on_delete=models.CASCADE)
    question = models.CharField(max_length=500)
    image = models.CharField(max_length=100,null=True,blank=True)
    type = models.CharField(max_length=100,null=True,blank=True)
    marks = models.CharField(max_length=100,null=True,blank=True)
    option1 = models.CharField(max_length=500,null=True,blank=True)
    option2 = models.CharField(max_length=500,null=True,blank=True)
    option3 = models.CharField(max_length=500,null=True,blank=True)
    option4 = models.CharField(max_length=500,null=True,blank=True)
    option5 = models.CharField(max_length=500,null=True,blank=True)
    option6 = models.CharField(max_length=500,null=True,blank=True)
    shortanswer = models.CharField(max_length=999,null=True,blank=True)
    answer = models.CharField(max_length=99,null=True,blank=True)
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


class SubmittedExamination(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    exam = models.ForeignKey(Examination,on_delete=models.CASCADE)
    # question = models.ForeignKey(Questions,on_delete=models.CASCADE,default=" ") #modify by ankit on 22-01-2025
    question = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100,null=True,blank=True)
    marks = models.CharField(max_length=100,null=True,blank=True)
    marks_obtained = models.CharField(max_length=100,null=True,blank=True)
    submitted_answer = models.CharField(max_length=999,null=True,blank=True)
    answer = models.CharField(max_length=999,null=True,blank=True)
    result = models.CharField(max_length=100,null=True,blank=True)
    # attempt=models.IntegerField(null=True,blank=True)

    class Meta:
        db_table = "submitted_answer"

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
    class Meta:
        db_table = 'result'

class StudentAppearingExam(models.Model):
    exam = models.ForeignKey(Examination,on_delete=models.CASCADE)
    student_id = models.JSONField(default=list, blank=True ,null=True)
    examstarttime = models.TimeField(auto_now=False, auto_now_add=False,null=True, blank=True)
    examendtime = models.TimeField(auto_now=False, auto_now_add=False,null=True, blank=True)
    examstartdate = models.DateField(auto_now=False, auto_now_add=False,null=True, blank=True)
    examenddate = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    # attempt=models.IntegerField(null=True,blank=True)
    class Meta:
        db_table = 'studentappearingexam'

class ExamSession(models.Model):
  student = models.ForeignKey('Student', on_delete=models.CASCADE)
  exam = models.ForeignKey('Examination', on_delete=models.CASCADE)
  time_left_ms = models.BigIntegerField(default=0)
  updated_at = models.DateTimeField(auto_now=True)
  class Meta:
      unique_together = ('student', 'exam')
      
      
class Categories(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
  