from django import db
from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager
import os
# Create your models here.

class User(AbstractUser):
    username = None
    mobile = models.CharField(max_length=14)
    email = models.EmailField(unique=True)
    birthdate = models.DateField(null=True,blank=True)
    gender = models.CharField(max_length=50,null=True,blank=True)
    address = models.CharField(max_length = 80,null=True,blank=True)
    is_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100,null=True,blank=True)
    ssc_result = models.FileField(upload_to='Student_Documents/',blank=True ,null=True)
    hsc_result = models.FileField(upload_to='Student_Documents/',blank=True ,null=True)
    document_3 = models.FileField(upload_to='Student_Documents/',blank=True ,null=True)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] 
    class Meta:
        db_table = 'user'


class UserLevel(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    level = models.CharField(max_length=10)
    class Meta:
        db_table = 'userlevel'
        
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
    university = models.CharField(max_length=20,null=True,blank=True)
    name = models.CharField(max_length=50)
    created_by = models.CharField(max_length=100,null=True,blank=True)
    modified_by = models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        db_table = 'course'

class Stream(models.Model):
    name = models.CharField(max_length=50)
    sem = models.CharField(max_length=3,null=True,blank=True)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    created_by = models.CharField(max_length=100,null=True,blank=True)
    modified_by = models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        db_table = 'stream'
        
class StreamFees(models.Model):
    course = models.CharField(max_length=10)
    stream = models.CharField(max_length=10)
    sem1 = models.CharField(max_length=10,null=True,blank=True)
    sem2 = models.CharField(max_length=10,null=True,blank=True)
    sem3 = models.CharField(max_length=10,null=True,blank=True)
    sem4 = models.CharField(max_length=10,null=True,blank=True)
    sem5 = models.CharField(max_length=10,null=True,blank=True)
    sem6 = models.CharField(max_length=10,null=True,blank=True)
    sem7 = models.CharField(max_length=10,null=True,blank=True)
    sem8 = models.CharField(max_length=10,null=True,blank=True)
    sem9 = models.CharField(max_length=10,null=True,blank=True)
    sem10 = models.CharField(max_length=10,null=True,blank=True)
    class Meta:
        db_table = 'streamfees'
        

class FeesDetails(models.Model):
    streamfees = models.CharField(max_length=50)
    basefees = models.CharField(max_length=50,null=True,blank=True,default="0")
    tutionfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    bookfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    specialallowance = models.CharField(max_length=50,null=True,blank=True,default="0")
    universityfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    hostelfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    entrancefees = models.CharField(max_length=50,null=True,blank=True,default="0")
    extrafees = models.CharField(max_length=50,null=True,blank=True,default="0")
    discount = models.CharField(max_length=50,null=True,blank=True,default="0")
    totalfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    sem = models.CharField(max_length=10)
    class Meta:
        db_table = 'feesdetails'


class SemesterFees(models.Model):
    stream = models.CharField(max_length=50)
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
    class Meta:
        db_table = 'semesterfees'

class YearFees(models.Model):
    stream = models.CharField(max_length=50)
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
    alternateemail = models.EmailField(max_length=100,unique=True,null=True,blank=True)
    gender = models.CharField(max_length=15,null=True,blank=True)
    category = models.CharField(max_length=50,null=True,blank=True)
    address = models.CharField(max_length = 500,null=True,blank=True)
    alternateaddress = models.CharField(max_length = 500,null=True,blank=True)
    nationality = models.CharField(max_length=20,null=True,blank=True)
    country = models.CharField(max_length=20,null=True,blank=True)
    state = models.CharField(max_length=50,null=True,blank=True)
    city = models.CharField(max_length=20,null=True,blank=True)
    pincode = models.CharField(max_length=10,null=True,blank=True)
    registration_id = models.CharField(max_length=20,unique=True)
    old_university_enrollment_id = models.CharField(max_length=50,default=None,null=True,blank=True)
    new_university_enrollment_id = models.CharField(max_length=50,default=None,null=True,blank=True)
    enrollment_id = models.CharField(max_length=20,unique=True)
    enrollment_date = models.DateField(auto_now = True)
    university = models.CharField(max_length=100,null=True,blank=True)
    image = models.FileField(upload_to='student_image/',blank=True ,null=True)
    verified = models.BooleanField(default=False)
    user = models.CharField(max_length=20, null=True,blank=True)
    enrolled = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    created_by = models.CharField(max_length=100,null=True,blank=True)
    modified_by = models.CharField(max_length=100,null=True,blank=True)
    student_remarks = models.CharField(max_length=500,default="")
    class Meta:
        db_table = 'students'











class StudentArchive(Student):
    pass

class StudentDocuments(models.Model):
    document = models.CharField(max_length=50)
    document_name = models.CharField(max_length=50,null=True,blank=True)
    document_ID_no = models.CharField(max_length=50,null=True,blank=True)
    document_image_front = models.FileField(upload_to='student_documents/',blank=True ,null=True)
    document_image_back = models.FileField(upload_to='student_documents/',blank=True ,null=True)
    student = models.CharField(max_length=10)
    class Meta:
        db_table = 'studentdocuments'

class PersonalDocuments(models.Model):
    document = models.CharField(max_length=50)
    document_name = models.CharField(max_length=50,null=True,blank=True)
    document_ID_no = models.CharField(max_length=50,null=True,blank=True)
    student = models.CharField(max_length=10)
    class Meta:
        db_table = 'personaldocuments'

class PersonalDocumentsImages(models.Model):
    document = models.ForeignKey(PersonalDocuments,on_delete=models.CASCADE)
    document_image = models.FileField(upload_to='student_personal_documents/')
    class Meta:
        db_table = 'personaldocumentsimages'
        
        
class Enrolled(models.Model):
    student = models.CharField(max_length=20)
    course = models.CharField(max_length=20)
    stream = models.CharField(max_length=20)
    course_pattern = models.CharField(max_length=20)
    session = models.CharField(max_length=100,null=True,blank=True)
    entry_mode = models.CharField(max_length=100,null=True,blank=True)
    total_semyear = models.CharField(max_length=3,null=True,blank=True)
    current_semyear = models.CharField(max_length=3) 
    class Meta:
        db_table = 'enrolled'
    

class StudentFees(models.Model):
    student = models.CharField(max_length=10)
    studypattern = models.CharField(max_length = 20)
    stream = models.CharField(max_length=50)
    tutionfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    examinationfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    bookfees     = models.CharField(max_length=50,null=True,blank=True,default="0")
    resittingfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    entrancefees = models.CharField(max_length=50,null=True,blank=True,default="0")
    extrafees = models.CharField(max_length=50,null=True,blank=True,default="0")
    discount = models.CharField(max_length=50,null=True,blank=True,default="0")
    totalfees = models.CharField(max_length=50,null=True,blank=True,default="0")
    sem = models.CharField(max_length=10)
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
    student = models.CharField(max_length=10)
    class Meta:
        db_table = 'qualification'
        
class AdditionalEnrollmentDetails(models.Model):
    counselor_name = models.CharField(max_length=100,null=True,blank=True)
    reference_name = models.CharField(max_length=100,null=True,blank=True)
    session = models.CharField(max_length=100,null=True,blank=True)
    entry_mode = models.CharField(max_length=100,null=True,blank=True)
    old_university_enrollment_id = models.CharField(max_length=30,null=True,blank=True)
    university_enrollment_id = models.CharField(max_length=30,null=True,blank=True)
    student = models.CharField(max_length=10,null=True,blank=True)
    class Meta:
        db_table = "additionalenrollmentdetails"

class UniversityEnrollment(models.Model):
    student = models.CharField(max_length=20)
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
    student = models.CharField(max_length=10,null=True,blank=True)
    class Meta:
        db_table = 'courier'        


class EmailSentHistory(models.Model):
    student = models.CharField(max_length=20)
    type = models.CharField(max_length=20)
    amount = models.CharField(max_length=20,null=True,blank=True)
    email = models.CharField(max_length=100)
    subject = models.CharField(max_length=100,null=True,blank=True)
    body = models.CharField(max_length=5000,null=True,blank=True)
    payment_categories = models.CharField(max_length=100,null=True,blank=True)
    payment_type = models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        db_table = 'emailsenthistory'

        
class Fees(models.Model):
    student = models.CharField(max_length=10)
    streamfees = models.CharField(max_length=10)
    semyear = models.CharField(max_length=10)
    totalfees = models.CharField(max_length=10)
    discount = models.CharField(max_length=10,null=True,blank=True)
    specialallowance = models.CharField(max_length=10,null=True,blank=True)
    class Meta:
        db_table = 'fees'
    
   
    class Meta:
        db_table = 'fees'

class FeesPaid(models.Model):
    student = models.CharField(max_length=10)
    transactiontime = models.DateTimeField(auto_now=True)
    transactionID = models.CharField(max_length=50)
    amount = models.CharField(max_length=10)
    semesteryear = models.CharField(max_length=10,null=True,blank=True)
    paymentmode = models.CharField(max_length=10,default="Online")
    class Meta:
        db_table = 'feespaid'
        
class TestDB(models.Model):
    name = models.CharField(max_length = 10)
        

class PaymentReciept(models.Model):
    student = models.CharField(max_length=10)
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
        
class SaveStudentTransaction(models.Model):
    student_identifier = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    txnid = models.CharField(max_length=100)
    productinfo = models.CharField(max_length=100)
    amount = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    surl = models.CharField(max_length=100)
    furl = models.CharField(max_length=100)
    hash = models.CharField(max_length=500)
    student = models.CharField(max_length=100)
    status = models.CharField(max_length=30)
    used = models.CharField(max_length=20,default="no",null=True,blank=True)
    archived = models.CharField(max_length=20,default="no",null=True,blank=True)
    class Meta:
        db_table = 'savestudenttransaction'
    
class PaymentReciept1(models.Model):
    student = models.CharField(max_length=10)
    fee_reciept_type = models.CharField(max_length=30,null=True,blank=True)
    transaction_date = models.CharField(max_length=20)
    cheque_no = models.CharField(max_length=50,null=True,blank=True)
    bank_name = models.CharField(max_length=50,null=True,blank=True)
    paidamount = models.CharField(max_length=10)
    pendingamount = models.CharField(max_length=10,null=True,blank=True)
    transactiontime = models.DateTimeField(auto_now=True)
    transactionID = models.CharField(max_length=50)
    paymentmode = models.CharField(max_length=10,default="Online")
    remarks = models.CharField(max_length=500,null=True,blank=True)
    session = models.CharField(max_length=100,null=True,blank=True)
    semyear = models.CharField(max_length=10,null=True,blank=True) 

    class Meta:
        db_table = 'paymentreciept1'

class UniversityExamination(models.Model):
    student = models.CharField(max_length=10)
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
    student = models.CharField(max_length=10)
    class Meta:
        db_table = 'temptransaction'    

class ResultUploaded(models.Model):
    student = models.CharField(max_length=10)
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
    course = models.CharField(max_length=10)
    stream = models.CharField(max_length=10)
    semester = models.CharField(max_length=10)
    pdf = models.FileField(upload_to='syllabus/',blank=True ,null=True)
    class Meta:
        db_table = 'syllabus'    

class StudentSyllabus(models.Model):
    student = models.CharField(max_length=10)
    semester = models.CharField(max_length=10)
    pdf = models.FileField(upload_to='studentsyllabus/',blank=True ,null=True)
    class Meta:
        db_table = 'studentsyllabus'





class ImportCsvData(models.Model):
    import_csv_data = models.FileField(upload_to='Csv_Import/',blank=True ,null=True)
    class Meta:
        db_table = 'importcsv'

class StudentExaminationTime(models.Model):
    student = models.CharField(max_length=100)
    exam = models.CharField(max_length=100)
    time_in_minutes = models.CharField(max_length=100)
    class Meta:
        db_table = 'studentexaminationtime'
    

class Examination(models.Model):
    university = models.CharField(max_length=10,null=True,blank=True)
    course = models.CharField(max_length=10)
    stream = models.CharField(max_length=10)
    examname = models.CharField(max_length=100)
    examdate = models.CharField(max_length=20)
    examtime = models.TimeField(auto_now=False, auto_now_add=False,null=True, blank=True)
    totalquestions = models.CharField(max_length=10,null=True,blank=True)
    totalmarks = models.CharField(max_length=10)
    active = models.BooleanField(default=True)
    archive = models.BooleanField(default=False)
    created_by = models.CharField(max_length=100,null=True,blank=True)
    modified_by = models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        db_table = 'examination'


class Questions(models.Model):
    exam = models.CharField(max_length=10)
    question = models.CharField(max_length=500)
    image = models.CharField(max_length=100,null=True,blank=True)
    type = models.CharField(max_length=100,null=True,blank=True)
    marks = models.CharField(max_length=100,null=True,blank=True)
    option1 = models.CharField(max_length=100,null=True,blank=True)
    option2 = models.CharField(max_length=100,null=True,blank=True)
    option3 = models.CharField(max_length=100,null=True,blank=True)
    option4 = models.CharField(max_length=100,null=True,blank=True)
    option5 = models.CharField(max_length=100,null=True,blank=True)
    option6 = models.CharField(max_length=100,null=True,blank=True)
    shortanswer = models.CharField(max_length=999,null=True,blank=True)
    answer = models.CharField(max_length=99)
    class Meta:
        db_table = 'questions'

class Descriptive_Answer(models.Model):
    student = models.CharField(max_length=10,null=True,blank=True)
    exam = models.CharField(max_length=10)
    question = models.CharField(max_length=500)
    upload = models.FileField(upload_to='examination_uploads/',blank=True ,null=True)
    class Meta:
        db_table = "descriptive_answer"

    
class SubmittedExamination(models.Model):
    student = models.CharField(max_length=10,null=True,blank=True)
    exam = models.CharField(max_length=10)
    question = models.CharField(max_length=500)
    type = models.CharField(max_length=100,null=True,blank=True)
    marks = models.CharField(max_length=100,null=True,blank=True)
    marks_obtained = models.CharField(max_length=100,null=True,blank=True)
    submitted_answer = models.CharField(max_length=999,null=True,blank=True)
    answer = models.CharField(max_length=999,null=True,blank=True)
    result = models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        db_table = "submitted_answer"

class Result(models.Model):
    student = models.CharField(max_length=10)
    exam = models.CharField(max_length=10)
    total_question = models.CharField(max_length=10)
    attempted = models.CharField(max_length=10)
    total_marks = models.CharField(max_length=100,null=True,blank=True)
    score = models.CharField(max_length=10)
    result = models.CharField(max_length=10)
    created_by = models.CharField(max_length=100,null=True,blank=True)
    modified_by = models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        db_table = 'result'



class StudentAppearingExam(models.Model):
    exam = models.CharField(max_length=100)
    student = models.CharField(max_length=100)
    class Meta:
        db_table = 'studentappearingexam'

    
class Status(models.Model):
    user = models.CharField(max_length=10)
    status = models.CharField(max_length=10,default="Offline")
    last_login = models.CharField(max_length=50,null=True,blank=True)
    last_logout = models.CharField(max_length=50,null=True,blank=True)
    class Meta:
        db_table = 'status'
        
        
        
        
class TestPaymentGateway(models.Model):
    transactionID = models.CharField(max_length=50)
    student = models.CharField(max_length=10)
    class Meta:
        db_table = "testpaymentgateway"
        
        
        
        
class Countries(models.Model):
    shortname = models.CharField(max_length=5)
    name = models.CharField(max_length=150)
    phonecode = models.IntegerField(max_length=11)
    class Meta:
        db_table = "countries"

class States(models.Model):
    name = models.CharField(max_length=150)
    country_id = models.IntegerField(max_length=11,default='1')
    class Meta:
        db_table = "states"

class Cities(models.Model):
    name = models.CharField(max_length=150)
    state_id = models.IntegerField(max_length=11)
    class Meta:
        db_table = "cities"


        
class TempFiles(models.Model):
    tempfile = models.FileField(upload_to='temporary_uploads/',blank=True ,null=True)
    temptime = models.DateTimeField(auto_now=True)
    tempuser = models.CharField(max_length=100)
    temptype = models.CharField(max_length=100,null=True,blank=True)
    class Meta:
        db_table = "tempfiles"
    

        
        