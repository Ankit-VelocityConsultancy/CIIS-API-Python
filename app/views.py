from django.http.response import HttpResponse,JsonResponse
from django.shortcuts import render,HttpResponse,redirect   ,HttpResponseRedirect
from django.contrib.auth import authenticate,get_user_model,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q , F
from .models import Countries,States,Cities,StudentArchive,Course,Student,Fees,ImportCsvData,UserLevel,User,Stream,Qualification,Enrolled,University,StreamFees,FeesPaid,Status,PaymentReciept ,Examination , Questions,Result ,AdditionalEnrollmentDetails,FeesDetails,Syllabus,StudentSyllabus,Courier,TestPaymentGateway,SemesterFees,YearFees,StudentDocuments,StudentFees,TransactionDetails,SaveStudentTransaction,PersonalDocuments,PersonalDocumentsImages,UniversityExamination,ResultUploaded,UniversityEnrollment,EmailSentHistory,SubmittedExamination,StudentExaminationTime,StudentAppearingExam,Descriptive_Answer
from rest_framework.response import Response
from django.core.mail import send_mail as sm,EmailMessage
from csv import reader
from csv import DictReader
from .serializers import StatesSerializer,CitiesSerializer,UniversitySerializer, CourseSerializer,StreamSerializer,StudentSerializer,EnrolledSerializer,QualificationSerializer,FeesSerializer,StreamFeesSerializer,FeesPaidSerializer,FeesDetailsSerializer,PaymentRecieptSerializer,SyllabusSerializer,StudentSyllabusSerializer,CourierSerializer,SemesterFeesSerializer,YearFeesSerializer,StudentDocumentsSerializer,StudentFeesSerializer,SaveStudentTransactionSerializer,PersonalDocumentsSerializer,PersonalDocumentsImagesSerializer,UniversityExaminationSerializer,ResultUploadedSerializer,UniversityEnrollmentSerializer,EmailSentHistorySerializer,QuestionsSerializer,ExaminationSerializer,SubmittedExaminationSerializer
import json
from datetime import date,datetime,timedelta
from hashlib import sha512
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paywix.payu import Payu
from django.core.mail import EmailMessage
import hashlib
import pandas as pd 
import math
# from pandas import ExcelWriter
# from pandas import ExcelFile 
import csv
import os
#pdf import
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import xlwt
import logging,traceback
logger = logging.getLogger('django')

def test(request):
    # stud = Student.objects.get(enrollment_id =   50001  )
    # print(stud)
    # list_of_files = os.listdir('media/student_documents')
    # length_of_files = len(list_of_files)
    # # walk_of_files = os.walk('media/student_documents')
    # # print(walk_of_files)
    # scan = os.scandir('media/student_documents')
    # # print(scan)
    # x = os.path
    # ROOT_DIR = os.path.abspath(os.curdir)
    # print(ROOT_DIR)

    # directory = stud.name
    # parent_dict = "media/"
    # path = os.path.join(parent_dict, directory)
    # # os.mkdir(path)
    # print("Directory '% s' created" % directory)

    #_____________________________________________________________________________________________
    # size = os.path.getsize('media/University_Logo/')
    # print("size :",size)
    # size = 0
    # path = "media/University_Logo/"
    # for path, dirs, files in os.walk(path):
    #     for f in files:
    #         fp = os.path.join(path, f)
    #         size += os.path.getsize(fp)
 
    # # display size
    # print("Folder size: " + str(size))
    # x = size * 0.000001
    # print(round(x,2))

    #_____________________________________________________________________________________________

    # startdate = "2022-07-05"
    # enddate = "2022-08-10"

    # students = Student.objects.filter(enrollment_date__range=[startdate, enddate])
    # for i in students:
    #     print(i.name , i.email, i.enrollment_date)

    

    return render(request,"test.html")
    # response = HttpResponse(content_type = 'text/csv')
    # writer = csv.writer(response)
    # writer.writerow(['student','course','stream','course pattern','session','entry mode','total semyear','current semyear'])
    # for enroll in Enrolled.objects.all().values_list('student','course','stream','course_pattern','session','entry_mode','total_semyear','current_semyear'):
    #     writer.writerow(enroll)
    # response['Content-Disposition'] = 'atachment; filename="enrolled.csv"'
    # print(response)
    # return response

def index(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4" or level.level == "2":
            return redirect('overview')
        elif level.level == "1":
            return redirect('profile')
    else:
        return redirect('login')

def home(request):
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4" or level.level == "2":
            display = "yes"
    params = {
        "display": display,
        "total_student":Student.objects.filter(Q(archive=False) & Q(is_cancelled=False)).count(),
        "pending_student":Student.objects.filter(Q(archive=False) & Q(is_cancelled=False) & Q(enrolled=False)).count(),
        "registered_student":Student.objects.filter(Q(archive=False) & Q(is_cancelled=False) & Q(enrolled=True)).count(),
        "courses":Course.objects.all()[:15]
    }
    return render(request,"homepage.html",params)

def PrintAddress(request):
    display = ""
    level_of_user = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            level_of_user = level.level
            display = "yes"
            if request.method == "POST":
                student_id = request.POST.get('student_id')
                if student_id:
                    try:
                        getstudent = Student.objects.get(id = student_id)
                        obj = {
                            "address":getstudent.address,
                            "country":getstudent.country,
                            "state":getstudent.state,
                            "city":getstudent.city,
                            "pincode":getstudent.pincode
                            
                        }
                        return JsonResponse({'address':'yes','data':obj})
                    except Student.DoesNotExist:
                        print("student not avaliable")
    params = {
        "display":display,
        "students":Student.objects.all(),
        "level_of_user":level_of_user
    }
    return render(request,"print_address.html",params)
# # Create your views here.
@login_required(login_url='/login/')
def StudentProfile(request):
    user_id = ''
    display = ""
    obj = {}
    getstudent = ''
    if request.user.is_authenticated:
        user_id = request.user.id
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            return redirect('overview')
        if level.level == "1":
            display = "yes"
            getuser = User.objects.get(id = user_id)
            print(getuser)
            
            try:
                getstudent = Student.objects.get(email=getuser.email)
                if not getstudent.user:
                    getstudent.user = getuser.id
                    getstudent.save()
                else:
                    print("linked")
            except Student.DoesNotExist:
                getstudent = "none"
                print("student doesnot exiist")
            if getstudent != "none":

                try:
                    getfees = Fees.objects.get(student = getstudent)
                except Fees.DoesNotExist:
                    createfees = Fees(student = getstudent)
                    createfees.save()
            
           
            if getstudent != "none":
                getenroll = Enrolled.objects.get(student=getstudent.id)
                getcourse = Course.objects.get(id = getenroll.course)
                getstream = Stream.objects.get(id = getenroll.stream)
                obj = {
                    "name" : getstudent.name.capitalize(),
                    'father_name'  :getstudent.father_name.capitalize(),
                    'mother_name'  :getstudent.mother_name.capitalize(),
                    'dateofbirth'  :getstudent.dateofbirth,
                    'mobile'  :getstudent.mobile,
                    'email'  :getstudent.email,
                    'gender'  :getstudent.gender,
                    'category'  :getstudent.category,
                    'address'   :getstudent.address,
                    'ID_type'  :getstudent.ID_type,
                    'ID_number'  :getstudent.ID_number,
                    'nationality'  :getstudent.nationality,
                    'country'  :getstudent.country,
                    'state'  :getstudent.state,
                    'city'  :getstudent.city,
                    'pincode'  :getstudent.pincode,
                    'registration_id' :getstudent.registration_id,
                    'enrollment_id'  :getstudent.enrollment_id,
                    'enrollment_date'  :getstudent.enrollment_date,
                    'university'  :getstudent.university,
                    'course_name':getcourse.name,
                    'stream_name':getstream.name,
                    'course_pattern':getenroll.course_pattern,
                    'current_semester':getenroll.current_semester
                }
        else:
            print("no")
    print(getstudent)
    params = {
        "display":display,
        'student':obj,
        'getstudent':getstudent
        
    }
    return render(request,"profile.html",params)
# 3672 3555 3548 10775     3672+   4550
@login_required(login_url='/login/') 
def StudentDashboard(request):
    if request.user.is_authenticated:
        print(request.user)
    display = ""
    getfeespaid = ''
    feesobject = {}
    if request.user.is_authenticated:
        user_id = request.user.id
        level = UserLevel.objects.get(user = user_id)
        if level.level == "1":
            display = "yes"
            if request.method == "POST":
                checksem = request.POST.get('checksem')
                print("checksem :",checksem)
                semester = request.POST.get('semester')
                print("semester",semester)
                if semester:
                    return JsonResponse({'redirect':'yes'})
                if checksem:
                    request.session['feespaid'] = checksem
                    return JsonResponse({'invoiceredirect':'yes'})
            getuser = User.objects.get(id = user_id)
            
            print(getuser)
            try:
                getstudent = Student.objects.get(email=getuser.email)
                if not getstudent.user:
                    getstudent.user = getuser.id
                    getstudent.save()
                else:
                    print("linked")

            except Student.DoesNotExist:
                getstudent = "none"
                print("student doesnot exiist")
            if getstudent != "none":

                getfeespaid = FeesPaid.objects.filter(student=getstudent.id)
                getenroll = Enrolled.objects.get(student=getstudent.id)
                getcourse = Course.objects.get(id = getenroll.course)
                getstream = Stream.objects.get(id = getenroll.stream)
                getstreamfees = StreamFees.objects.get(Q(course=getenroll.course) and Q(stream=getenroll.stream))
                try:
                    getstudentfees = Fees.objects.get(student=getstudent)
                except Fees.DoesNotExist:
                    getstudentfees = "none"
                if getenroll.current_semester == "1":
                    if getstudentfees.paidsem1:
                        sem1 = getstudentfees.paidsem1
                    else:
                        sem1 = "0"
                    print(sem1)
                    feesobject = {
                        "semester":"1",
                        "sem1":getstreamfees.sem1,
                        "sem1paid":sem1,
                        "pendingsem1":int(getstreamfees.sem1) - int(sem1)
                    }
                elif getenroll.current_semester == "2":
                    if getstudentfees.paidsem1:
                        sem1 = getstudentfees.paidsem1                      
                    else:
                        sem1 = "0"
                    if getstudentfees.paidsem2:
                        sem2 = getstudentfees.paidsem2                      
                    else:
                        sem2 = "0"
                    
                    feesobject = {
                        "semester":"2",
                        "sem1":getstreamfees.sem1,
                        "sem2":getstreamfees.sem2,
                        "sem1paid":sem1,
                        "sem2paid":sem2,
                        "pendingsem1":int(getstreamfees.sem1) - int(sem1),
                        "pendingsem2":int(getstreamfees.sem2) - int(sem2)                     
                    }
                elif getenroll.current_semester == "3":
                    if getstudentfees.paidsem1:
                        sem1 = getstudentfees.paidsem1                      
                    else:
                        sem1 = "0"
                    if getstudentfees.paidsem2:
                        sem2 = getstudentfees.paidsem2                      
                    else:
                        sem2 = "0"
                    if getstudentfees.paidsem3:
                        sem3 = getstudentfees.paidsem3                      
                    else:
                        sem3 = "0"
                    
                    feesobject = {
                        "semester":"3",
                        "sem1":getstreamfees.sem1,
                        "sem2":getstreamfees.sem2,
                        "sem3":getstreamfees.sem3,
                        "sem1paid":sem1,
                        "sem2paid":sem2,
                        "sem3paid":sem3,
                        "pendingsem1":int(getstreamfees.sem1) - int(sem1),
                        "pendingsem2":int(getstreamfees.sem2) - int(sem2),
                        "pendingsem3":int(getstreamfees.sem3) - int(sem3),
                                              
                    }
                elif getenroll.current_semester == "4":
                    if getstudentfees.paidsem1:
                        sem1 = getstudentfees.paidsem1                      
                    else:
                        sem1 = "0"
                    if getstudentfees.paidsem2:
                        sem2 = getstudentfees.paidsem2                      
                    else:
                        sem2 = "0"
                    if getstudentfees.paidsem3:
                        sem3 = getstudentfees.paidsem3                      
                    else:
                        sem3 = "0"
                    if getstudentfees.paidsem4:
                        sem4 = getstudentfees.paidsem4                      
                    else:
                        sem4 = "0"
                    
                    feesobject = {
                        "semester":"4",
                        "sem1":getstreamfees.sem1,
                        "sem2":getstreamfees.sem2,
                        "sem3":getstreamfees.sem3,
                        "sem4":getstreamfees.sem4,                       
                        "sem1paid":sem1,
                        "sem2paid":sem2,
                        "sem3paid":sem3,
                        "sem4paid":sem4,
                        "pendingsem1":int(getstreamfees.sem1) - int(sem1),
                        "pendingsem2":int(getstreamfees.sem2) - int(sem2),
                        "pendingsem3":int(getstreamfees.sem3) - int(sem3),
                        "pendingsem4":int(getstreamfees.sem4) - int(sem4),
                                         
                    }
                elif getenroll.current_semester == "5":
                    if getstudentfees.paidsem1:
                        sem1 = getstudentfees.paidsem1                      
                    else:
                        sem1 = "0"
                    if getstudentfees.paidsem2:
                        sem2 = getstudentfees.paidsem2                      
                    else:
                        sem2 = "0"
                    if getstudentfees.paidsem3:
                        sem3 = getstudentfees.paidsem3                      
                    else:
                        sem3 = "0"
                    if getstudentfees.paidsem4:
                        sem4 = getstudentfees.paidsem4                      
                    else:
                        sem4 = "0"
                    if getstudentfees.paidsem5:
                        sem5 = getstudentfees.paidsem5                      
                    else:
                        sem5 = "0"
                                         
                    feesobject = {
                        "semester":"5",
                        "sem1":getstreamfees.sem1,
                        "sem2":getstreamfees.sem2,
                        "sem3":getstreamfees.sem3,
                        "sem4":getstreamfees.sem4,
                        "sem5":getstreamfees.sem5,                      
                        "sem1paid":sem1,
                        "sem2paid":sem2,
                        "sem3paid":sem3,
                        "sem4paid":sem4,
                        "sem5paid":sem5,
                        "pendingsem1":int(getstreamfees.sem1) - int(sem1),
                        "pendingsem2":int(getstreamfees.sem2) - int(sem2),
                        "pendingsem3":int(getstreamfees.sem3) - int(sem3),
                        "pendingsem4":int(getstreamfees.sem4) - int(sem4),
                        "pendingsem5":int(getstreamfees.sem5) - int(sem5),
                                           
                    }
                elif getenroll.current_semester == "6":
                    if getstudentfees.paidsem1:
                        sem1 = getstudentfees.paidsem1                      
                    else:
                        sem1 = "0"
                    if getstudentfees.paidsem2:
                        sem2 = getstudentfees.paidsem2                      
                    else:
                        sem2 = "0"
                    if getstudentfees.paidsem3:
                        sem3 = getstudentfees.paidsem3                      
                    else:
                        sem3 = "0"
                    if getstudentfees.paidsem4:
                        sem4 = getstudentfees.paidsem4                      
                    else:
                        sem4 = "0"
                    if getstudentfees.paidsem5:
                        sem5 = getstudentfees.paidsem5                      
                    else:
                        sem5 = "0"
                    if getstudentfees.paidsem6:
                        sem6 = getstudentfees.paidsem6                      
                    else:
                        sem6 = "0"
                    
                    feesobject = {
                        "semester":"6",
                        "sem1":getstreamfees.sem1,
                        "sem2":getstreamfees.sem2,
                        "sem3":getstreamfees.sem3,
                        "sem4":getstreamfees.sem4,
                        "sem5":getstreamfees.sem5,
                        "sem6":getstreamfees.sem6,                     
                        "sem1paid":sem1,
                        "sem2paid":sem2,
                        "sem3paid":sem3,
                        "sem4paid":sem4,
                        "sem5paid":sem5,
                        "sem6paid":sem6,
                        "pendingsem1":int(getstreamfees.sem1) - int(sem1),
                        "pendingsem2":int(getstreamfees.sem2) - int(sem2),
                        "pendingsem3":int(getstreamfees.sem3) - int(sem3),
                        "pendingsem4":int(getstreamfees.sem4) - int(sem4),
                        "pendingsem5":int(getstreamfees.sem5) - int(sem5),
                        "pendingsem6":int(getstreamfees.sem6) - int(sem6),
                                           
                    }
                elif getenroll.current_semester == "7":
                    if getstudentfees.paidsem1:
                        sem1 = getstudentfees.paidsem1                      
                    else:
                        sem1 = "0"
                    if getstudentfees.paidsem2:
                        sem2 = getstudentfees.paidsem2                      
                    else:
                        sem2 = "0"
                    if getstudentfees.paidsem3:
                        sem3 = getstudentfees.paidsem3                      
                    else:
                        sem3 = "0"
                    if getstudentfees.paidsem4:
                        sem4 = getstudentfees.paidsem4                      
                    else:
                        sem4 = "0"
                    if getstudentfees.paidsem5:
                        sem5 = getstudentfees.paidsem5                      
                    else:
                        sem5 = "0"
                    if getstudentfees.paidsem6:
                        sem6 = getstudentfees.paidsem6                      
                    else:
                        sem6 = "0"
                    if getstudentfees.paidsem7:
                        sem7 = getstudentfees.paidsem7                      
                    else:
                        sem7 = "0"
                    
                    feesobject = {
                        "semester":"7",
                        "sem1":getstreamfees.sem1,
                        "sem2":getstreamfees.sem2,
                        "sem3":getstreamfees.sem3,
                        "sem4":getstreamfees.sem4,
                        "sem5":getstreamfees.sem5,
                        "sem6":getstreamfees.sem6,
                        "sem7":getstreamfees.sem7,                                            
                        "sem1paid":sem1,
                        "sem2paid":sem2,
                        "sem3paid":sem3,
                        "sem4paid":sem4,
                        "sem5paid":sem5,
                        "sem6paid":sem6,
                        "sem7paid":sem7,
                        "pendingsem1":int(getstreamfees.sem1) - int(sem1),
                        "pendingsem2":int(getstreamfees.sem2) - int(sem2),
                        "pendingsem3":int(getstreamfees.sem3) - int(sem3),
                        "pendingsem4":int(getstreamfees.sem4) - int(sem4),
                        "pendingsem5":int(getstreamfees.sem5) - int(sem5),
                        "pendingsem6":int(getstreamfees.sem6) - int(sem6),
                        "pendingsem7":int(getstreamfees.sem7) - int(sem7),
                                                                    
                    }
                elif getenroll.current_semester == "8":
                    if getstudentfees.paidsem1:
                        sem1 = getstudentfees.paidsem1                      
                    else:
                        sem1 = "0"
                    if getstudentfees.paidsem2:
                        sem2 = getstudentfees.paidsem2                      
                    else:
                        sem2 = "0"
                    if getstudentfees.paidsem3:
                        sem3 = getstudentfees.paidsem3                      
                    else:
                        sem3 = "0"
                    if getstudentfees.paidsem4:
                        sem4 = getstudentfees.paidsem4                      
                    else:
                        sem4 = "0"
                    if getstudentfees.paidsem5:
                        sem5 = getstudentfees.paidsem5                      
                    else:
                        sem5 = "0"
                    if getstudentfees.paidsem6:
                        sem6 = getstudentfees.paidsem6                      
                    else:
                        sem6 = "0"
                    if getstudentfees.paidsem7:
                        sem7 = getstudentfees.paidsem7                      
                    else:
                        sem7 = "0"
                    if getstudentfees.paidsem8:
                        sem8 = getstudentfees.paidsem8                      
                    else:
                        sem8 = "0"
                                         
                    feesobject = {
                        "semester":"8",
                        "sem1":getstreamfees.sem1,
                        "sem2":getstreamfees.sem2,
                        "sem3":getstreamfees.sem3,
                        "sem4":getstreamfees.sem4,
                        "sem5":getstreamfees.sem5,
                        "sem6":getstreamfees.sem6,
                        "sem7":getstreamfees.sem7,
                        "sem8":getstreamfees.sem8,                                             
                        "sem1paid":sem1,
                        "sem2paid":sem2,
                        "sem3paid":sem3,
                        "sem4paid":sem4,
                        "sem5paid":sem5,
                        "sem6paid":sem6,
                        "sem7paid":sem7,
                        "sem8paid":sem8, 
                        "pendingsem1":int(getstreamfees.sem1) - int(sem1),
                        "pendingsem2":int(getstreamfees.sem2) - int(sem2),
                        "pendingsem3":int(getstreamfees.sem3) - int(sem3),
                        "pendingsem4":int(getstreamfees.sem4) - int(sem4),
                        "pendingsem5":int(getstreamfees.sem5) - int(sem5),
                        "pendingsem6":int(getstreamfees.sem6) - int(sem6),
                        "pendingsem7":int(getstreamfees.sem7) - int(sem7),
                        "pendingsem8":int(getstreamfees.sem8) - int(sem8),
                                                                     
                    }
                
                obj = {
                    "name" : getstudent.name.capitalize(),
                    'father_name'  :getstudent.father_name.capitalize(),
                    'mother_name'  :getstudent.mother_name.capitalize(),
                    'dateofbirth'  :getstudent.dateofbirth,
                    'mobile'  :getstudent.mobile,
                    'email'  :getstudent.email,
                    'gender'  :getstudent.gender,
                    'category'  :getstudent.category,
                    'address'   :getstudent.address,
                    'ID_type'  :getstudent.ID_type,
                    'ID_number'  :getstudent.ID_number,
                    'nationality'  :getstudent.nationality,
                    'country'  :getstudent.country,
                    'state'  :getstudent.state,
                    'city'  :getstudent.city,
                    'pincode'  :getstudent.pincode,
                    'registration_id' :getstudent.registration_id,
                    'enrollment_id'  :getstudent.enrollment_id,
                    'enrollment_date'  :getstudent.enrollment_date,
                    'university'  :getstudent.university,
                    'course_name':getcourse.name,
                    'stream_name':getstream.name,
                    'course_pattern':getenroll.course_pattern,
                    'current_semester':getenroll.current_semester
                    
                } 
        else:
            print("no")
    params = {
        "display":display,
        "student":obj,
        "fees":feesobject,
        "paidfees":getfeespaid
    }
    return render(request,"studentdashboard.html",params)

@login_required(login_url='/login/')
def PayFees(request):
    if request.user.is_authenticated:
        print(request.user)
    display = ""
    feesobject = {}
    if request.user.is_authenticated:
        user_id = request.user.id
        level = UserLevel.objects.get(user = user_id)
        if level.level == "1":
            display = "yes"
            try:
                getstudent = Student.objects.get(user = user_id)
            except Student.DoesNotExist:
                getstudent = "no"
            getenroll = Enrolled.objects.get(student=getstudent.id)
            if request.method == "POST":
                
                sem = request.POST.get('sem')
                pay_amount = request.POST.get('pay_amount')
                print("semester :",sem," ammount :",pay_amount)
                if pay_amount:
                    try:
                        getfee = Fees.objects.get(student = getstudent)
                    except Fees.DoesNotExist:
                        getfee = "no"
                    if getfee != "no":
                        if sem == "1":
                            getfee.paidsem1 = pay_amount
                            getfee.save()
                        if sem == "2":
                            getfee.paidsem2 = pay_amount
                            getfee.save()
                        if sem == "3":
                            getfee.paidsem3 = pay_amount
                            getfee.save()
                        if sem == "4":
                            getfee.paidsem4 = pay_amount
                            getfee.save()
                        if sem == "5":
                            getfee.paidsem5 = pay_amount
                            getfee.save()
                        if sem == "6":
                            getfee.paidsem6 = pay_amount
                            getfee.save()
                        if sem == "7":
                            getfee.paidsem7 = pay_amount
                            getfee.save()
                        if sem == "8":
                            getfee.paidsem8 = pay_amount
                            getfee.save()
                        
                        
                        
                        try:
                            getfeepaid = FeesPaid.objects.latest('id')
                        except FeesPaid.DoesNotExist:
                            getfeepaid = "none"
                        if getenroll.course_pattern == "Semester":
                            current_sem = getenroll.current_semester
                        elif getenroll.course_pattern == "Annual":
                            if getenroll.current_semester == "1":
                                current_sem = "1"
                            elif getenroll.current_semester == "2":
                                current_sem = "1"
                            elif getenroll.current_semester == "3":
                                current_sem = "2"
                            elif getenroll.current_semester == "4":
                                current_sem = "2"
                            elif getenroll.current_semester == "5":
                                current_sem = "3"
                            elif getenroll.current_semester == "6":
                                current_sem = "3"
                            elif getenroll.current_semester == "7":
                                current_sem = "4"
                            elif getenroll.current_semester == "8":
                                current_sem = "4"
                        print(current_sem)
                        if getfeepaid == "none":
                            setfeepaid = FeesPaid(student=getstudent.id,transactionID="TXT445FE101",amount=pay_amount,semesteryear=current_sem)
                            setfeepaid.save()
                            return redirect('studentdashboard')
                        else:
                            print("reached here")
                            tid = getfeepaid.transactionID
                            tranx = tid.replace("TXT445FE",'')
                            transactionID =  str("TXT445FE") + str(int(tranx) + 1)
                            setfeepaid = FeesPaid(student=getstudent.id,transactionID=transactionID,amount=pay_amount,semesteryear=current_sem)
                            setfeepaid.save()
                            return redirect('studentdashboard')
            
            if getstudent != "no":
                getenroll = Enrolled.objects.get(student = getstudent.id)
                print(getenroll)
                try:
                    getstreamfees = StreamFees.objects.get(Q(course=getenroll.course) and Q(stream = getenroll.stream))
                except StreamFees.DoesNotExist:
                    getstreamfees = "no"
                    
                getfees = Fees.objects.get(student = getstudent)
                if getenroll.total_semester == "4":
                    if getfees.paidsem1:
                        sem1paid = getfees.paidsem1
                    else:
                        sem1paid = 0
                    
                    if getfees.paidsem2:
                        sem2paid = getfees.paidsem2
                    else:
                        sem2paid = 0
                    
                    if getfees.paidsem3:
                        sem3paid = getfees.paidsem3
                    else:
                        sem3paid = 0
                    
                    if getfees.paidsem4:
                        sem4paid = getfees.paidsem4
                    else:
                        sem4paid = 0
                    obj = {
                    "semester":getenroll.current_semester,
                    "sem1":getstreamfees.sem1,
                    "sem2":getstreamfees.sem2,
                    "sem3":getstreamfees.sem3,
                    "sem4":getstreamfees.sem4,
                    
                    "sem1paid":sem1paid,
                    "sem2paid":sem2paid,
                    "sem3paid":sem3paid,
                    "sem4paid":sem4paid,
                    
                    "pendingsem1":int(getstreamfees.sem1) - int(sem1paid),
                    "pendingsem2":int(getstreamfees.sem2) - int(sem2paid),
                    "pendingsem3":int(getstreamfees.sem3) - int(sem3paid),
                    "pendingsem4":int(getstreamfees.sem4) - int(sem4paid)     
                    }
                elif getenroll.total_semester == "6":
                    if getfees.paidsem1:
                        sem1paid = getfees.paidsem1
                    else:
                        sem1paid = 0
                    
                    if getfees.paidsem2:
                        sem2paid = getfees.paidsem2
                    else:
                        sem2paid = 0
                    
                    if getfees.paidsem3:
                        sem3paid = getfees.paidsem3
                    else:
                        sem3paid = 0
                    
                    if getfees.paidsem4:
                        sem4paid = getfees.paidsem4
                    else:
                        sem4paid = 0
                    if getfees.paidsem5:
                        sem5paid = getfees.paidsem5
                    else:
                        sem5paid = 0
                    if getfees.paidsem6:
                        sem6paid = getfees.paidsem6
                    else:
                        sem6paid = 0
                    
                    obj = {
                    "semester":getenroll.current_semester,
                    "sem1":getstreamfees.sem1,
                    "sem2":getstreamfees.sem2,
                    "sem3":getstreamfees.sem3,
                    "sem4":getstreamfees.sem4,
                    "sem5":getstreamfees.sem5,
                    "sem6":getstreamfees.sem6,
                    
                    
                    "sem1paid":sem1paid,
                    "sem2paid":sem2paid,
                    "sem3paid":sem3paid,
                    "sem4paid":sem4paid,
                    "sem5paid":sem5paid,
                    "sem6paid":sem6paid,
                    
                    
                    "pendingsem1":int(getstreamfees.sem1) - int(sem1paid),
                    "pendingsem2":int(getstreamfees.sem2) - int(sem2paid),
                    "pendingsem3":int(getstreamfees.sem3) - int(sem3paid),
                    "pendingsem4":int(getstreamfees.sem4) - int(sem4paid),
                    "pendingsem5":int(getstreamfees.sem5) - int(sem5paid),
                    "pendingsem6":int(getstreamfees.sem6) - int(sem6paid),
                         
                    }  
                elif getenroll.total_semester == "8":
                    if getfees.paidsem1:
                        sem1paid = getfees.paidsem1
                    else:
                        sem1paid = 0
                    
                    if getfees.paidsem2:
                        sem2paid = getfees.paidsem2
                    else:
                        sem2paid = 0
                    
                    if getfees.paidsem3:
                        sem3paid = getfees.paidsem3
                    else:
                        sem3paid = 0
                    
                    if getfees.paidsem4:
                        sem4paid = getfees.paidsem4
                    else:
                        sem4paid = 0
                    if getfees.paidsem5:
                        sem5paid = getfees.paidsem5
                    else:
                        sem5paid = 0
                    if getfees.paidsem6:
                        sem6paid = getfees.paidsem6
                    else:
                        sem6paid = 0
                    if getfees.paidsem7:
                        sem7paid = getfees.paidsem7
                    else:
                        sem7paid = 0
                    if getfees.paidsem8:
                        sem8paid = getfees.paidsem8
                    else:
                        sem8paid = 0
                    
                    
                    obj = {
                    "semester":getenroll.current_semester,
                    "sem1":getstreamfees.sem1,
                    "sem2":getstreamfees.sem2,
                    "sem3":getstreamfees.sem3,
                    "sem4":getstreamfees.sem4,
                    "sem5":getstreamfees.sem5,
                    "sem6":getstreamfees.sem6,
                    "sem7":getstreamfees.sem7,
                    "sem8":getstreamfees.sem8,
                    
                    
                    
                    "sem1paid":sem1paid,
                    "sem2paid":sem2paid,
                    "sem3paid":sem3paid,
                    "sem4paid":sem4paid,
                    "sem5paid":sem5paid,
                    "sem6paid":sem6paid,
                    "sem7paid":sem7paid,
                    "sem8paid":sem8paid,
                    
                    
                    "pendingsem1":int(getstreamfees.sem1) - int(sem1paid),
                    "pendingsem2":int(getstreamfees.sem2) - int(sem2paid),
                    "pendingsem3":int(getstreamfees.sem3) - int(sem3paid),
                    "pendingsem4":int(getstreamfees.sem4) - int(sem4paid),
                    "pendingsem5":int(getstreamfees.sem5) - int(sem5paid),
                    "pendingsem6":int(getstreamfees.sem6) - int(sem6paid),
                    "pendingsem7":int(getstreamfees.sem7) - int(sem7paid),
                    "pendingsem8":int(getstreamfees.sem8) - int(sem8paid),
                         
                    }  
                

    params = {
        "display":display,
        'fees':obj
        
        
        
    }
    return render(request,"payfees.html",params)

@login_required(login_url='/login/')
def Invoice(request):
    if request.user.is_authenticated:
        print(request.user)
    display = ""
    sessiondata = ''
    obj = {}
    if request.user.is_authenticated:
        user_id = request.user.id
        level = UserLevel.objects.get(user = user_id)
        if level.level == "1":
            display = "yes"
            if 'feespaid' in request.session:
                sessiondata = request.session['feespaid']
                print(sessiondata)
            if sessiondata:
                try:
                    getstudent = Student.objects.get(user = user_id)
                except Student.DoesNotExist:
                    getstudent = "none"
                if getstudent != "none":
                    try:
                        getfeespaid = FeesPaid.objects.get((Q(student=getstudent.id)) & (Q(semesteryear = sessiondata)))
                    except Fees.DoesNotExist:
                        getfeespaid = "none"
                    if getfeespaid != "none":
                        getenroll = Enrolled.objects.get(student = getstudent.id)
                        
                        try:
                            getstreamfees = StreamFees.objects.get(Q(course =getenroll.course) & Q(stream = getenroll.stream) )
                        except StreamFees.DoesNotExist:
                            getstreamfees = "none"
                        if getstreamfees != "none":
                            print(getstreamfees)
                            if sessiondata == "1":
                                fees = getstreamfees.sem1
                            elif sessiondata == "2":
                                fees = getstreamfees.sem2
                            elif sessiondata == "3":
                                fees = getstreamfees.sem3
                            elif sessiondata == "4":
                                fees = getstreamfees.sem4
                            elif sessiondata == "5":
                                fees = getstreamfees.sem5
                            elif sessiondata == "6":
                                fees = getstreamfees.sem6
                            elif sessiondata == "7":
                                fees = getstreamfees.sem7
                            elif sessiondata == "8":
                                fees = getstreamfees.sem8
                            
                            
                            obj = {
                                "name":getstudent.name.capitalize(),
                                "mobile":getstudent.mobile,
                                "email":getstudent.email,
                                "country":getstudent.country,
                                "state":getstudent.state,
                                "city":getstudent.city,
                                "pincode":getstudent.pincode,
                                "paid":getfeespaid.amount,
                                "transactiontime":getfeespaid.transactiontime,
                                "transactionID":getfeespaid.transactionID,
                                "semesteryear":getfeespaid.semesteryear,
                                "fees":fees
                            }
                            print(obj)
    params ={
        "display":display,
        "data":obj
    }
    return render(request,"invoice.html",params)

@login_required(login_url='/login/')
def CourseRegistration(request):
    if request.user.is_authenticated:
        print(request.user)
        user_id = request.user.id
    display = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "1":
            display = "yes"
            selected_course = request.GET.get('data')
            if selected_course:
                get_course_id = Course.objects.get(degree = selected_course)
                get_specialization = Stream.objects.filter(degree = get_course_id.id)
                serializer = SpecializationSerializer(get_specialization,many=True)
                return JsonResponse({'data':serializer.data})
            if request.method == "POST":
                name = request.POST.get('name')
                print("got data from ajax is:",name)
                
                
                course=request.POST.get('course')
                specialization= request.POST.get('specialization')
                sem1 = request.POST.get('sem1')
                sem1paid= request.POST.get('sem1paid')
                ssc_result= request.FILES['doc1']
                hsc_result= request.FILES['doc2']
                document_3= request.FILES['doc3']
                
                print(course, specialization,sem1,sem1paid,ssc_result,hsc_result,document_3)
                try:
                    getstudent = Student.objects.get(user=user_id)
                except Student.DoesNotExist:
                    sem = 1
                if sem ==1:
                    current_semester = "1"
                else:
                    current_semester = int(getstudent.sem) + 1
                
                try:
                    random = Student.objects.latest('id')
                except Student.DoesNotExist:
                    random = 1
                if random==1:
                    roll = 5000
                else:
                    roll = int(random.enrollmentid)+ 1
                if course and specialization and roll and current_semester:
                    addstudent = Student(degree=course,field=specialization,enrollmentid=roll,sem=current_semester)
                    addstudent.save()
                    if sem1 or sem1paid:
                        get_student = Student.objects.latest('id')
                        save_fees = Fees(student=get_student,sem1=sem1,paidsem1=sem1paid)
                        save_fees.save()
                        return redirect('index')
        else:
            print("no")
    params = {
        "course":Course.objects.all(),
        "display":display
    }
    return render(request,"course_registration.html",params)

# ____________________________________________________________
@login_required(login_url='/login/')
def Overview(request):
    # logger.info('>>>>>>>>>>>>>> Something Debug wrong!')
    # print("System 25")
    display = ""
    level_of_user = ""
    student_count= ''
    student_list = []
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4" or level.level =="2":
            if request.method == "POST":
                payment_reciept_id = request.POST.get('payment_reciept_id')
                payment_reciept_status = request.POST.get('payment_reciept_status')
                if payment_reciept_id and payment_reciept_status:
                    get_payment_reciept = PaymentReciept.objects.get(id = payment_reciept_id)
                    get_payment_reciept.status = payment_reciept_status
                    total_fees = get_payment_reciept.semyearfees
                    paid_fees = get_payment_reciept.uncleared_amount
                    print(total_fees , paid_fees)
                    if int(paid_fees) > int(total_fees):
                        get_payment_reciept.advanceamount = int(paid_fees) - int(total_fees)
                        get_payment_reciept.paidamount = int(paid_fees)
                        get_payment_reciept.pendingamount = 0
                        get_payment_reciept.uncleared_amount = 0
                    elif int(paid_fees) < int(total_fees):
                        get_payment_reciept.advanceamount = 0
                        get_payment_reciept.paidamount = int(paid_fees)
                        get_payment_reciept.pendingamount = int(total_fees) - int(paid_fees)
                        get_payment_reciept.uncleared_amount = 0
                    elif int(paid_fees) == int(total_fees):
                        get_payment_reciept.advanceamount = 0
                        get_payment_reciept.paidamount = int(paid_fees)
                        get_payment_reciept.pendingamount = int(total_fees) - int(paid_fees)
                        get_payment_reciept.uncleared_amount = 0
                    # print("total fees :",get_payment_reciept.semyearfees)
                    # print("paid fees :",get_payment_reciept.paidamount)
                    # print("pending fees :",get_payment_reciept.pendingamount)
                    # print("uncleared amount :",get_payment_reciept.uncleared_amount)
                    get_payment_reciept.save()
                    updated_payment_data = []
                    all_pending_realisation = PaymentReciept.objects.filter(status = "Not Realised")
                    for i in all_pending_realisation:
                        try:
                            getstudent = Student.objects.get(id = i.student)
                            enrolled = Enrolled.objects.get(student = i.student)
                            course_name = Course.objects.get(id = enrolled.course)
                            stream_name = Stream.objects.get(id = enrolled.stream)
                            obj = {
                                "student_id":getstudent.id,
                                "name":getstudent.name,
                                "email":getstudent.email,
                                "mobile":getstudent.mobile,
                                "course":course_name.name,
                                "stream":stream_name.name,
                                "current_semester":enrolled.current_semyear,
                                "payment_reciept_id":i.id,                        
                                "payment_status":i.status,
                                "transactionID":i.transactionID,
                                "uncleared_amount":i.uncleared_amount
                            }
                            updated_payment_data.append(obj)
                        except Student.DoesNotExist:
                            pass
                    return JsonResponse({'data': updated_payment_data})

            all_pending_realisation = PaymentReciept.objects.filter(status = "Not Realised")
            for i in all_pending_realisation:
                try:
                    getstudent = Student.objects.get(id = i.student)
                    enrolled = Enrolled.objects.get(student = i.student)
                    course_name = Course.objects.get(id = enrolled.course)
                    stream_name = Stream.objects.get(id = enrolled.stream)
                    obj = {
                        "student_id":getstudent.id,
                        "name":getstudent.name,
                        "email":getstudent.email,
                        "mobile":getstudent.mobile,
                        "course":course_name.name,
                        "stream":stream_name.name,
                        "current_semester":enrolled.current_semyear,
                        "payment_reciept_id":i.id,                        
                        "payment_status":i.status,
                        "transactionID":i.transactionID,
                        "uncleared_amount":i.uncleared_amount
                    }
                    student_list.append(obj)
                except Student.DoesNotExist:
                    pass
            display = "yes"
            level_of_user = level.level
            student_count = Student.objects.all().count()
        else:
            print("no")
    
    params= {
        "allstudents":student_count,
        "display":display,
        "level_of_user":level_of_user,
        "students":Student.objects.filter(~Q(is_cancelled = True)).order_by('-id'),
        "payment_student":student_list
    }
    return render(request,"overview.html",params)

@login_required(login_url='/login/') 
def EditFees(request):
    display = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            display = "yes"
        else:
            print("no")
    params = {
        "display":display
    }
    return render(request,"editStudentFees.html",params)

@login_required(login_url='/login/')
def EditOldStudentFees(request):
    display = ""
    level_of_user = ""
    temp = []
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4" or level.level =="2":
            display = "yes"
            level_of_user = level.level
            if request.method == "POST":

                tution1 = request.POST.get('tution1')
                exam1 = request.POST.get('exam1')
                book1 = request.POST.get('book1')
                resitting1 = request.POST.get('resitting1')
                entrance1 = request.POST.get('entrance1')
                extra1 = request.POST.get('extra1')
                discount1 = request.POST.get('discount1')
                total1 = request.POST.get('total1')

                tution2 = request.POST.get('tution2')
                exam2 = request.POST.get('exam2')
                book2 = request.POST.get('book2')
                resitting2 = request.POST.get('resitting2')
                entrance2 = request.POST.get('entrance2')
                extra2 = request.POST.get('extra2')
                discount2 = request.POST.get('discount2')
                total2 = request.POST.get('total2')

                tution3 = request.POST.get('tution3')
                exam3 = request.POST.get('exam3')
                book3 = request.POST.get('book3')
                resitting3 = request.POST.get('resitting3')
                entrance3 = request.POST.get('entrance3')
                extra3 = request.POST.get('extra3')
                discount3 = request.POST.get('discount3')
                total3 = request.POST.get('total3')

                tution4 = request.POST.get('tution4')
                exam4 = request.POST.get('exam4')
                book4 = request.POST.get('book4')
                resitting4 = request.POST.get('resitting4')
                entrance4 = request.POST.get('entrance4')
                extra4 = request.POST.get('extra4')
                discount4 = request.POST.get('discount4')
                total4 = request.POST.get('total4')

                tution5 = request.POST.get('tution5')
                exam5 = request.POST.get('exam5')
                book5 = request.POST.get('book5')
                resitting5 = request.POST.get('resitting5')
                entrance5 = request.POST.get('entrance5')
                extra5 = request.POST.get('extra5')
                discount5 = request.POST.get('discount5')
                total5 = request.POST.get('total5')

                tution6 = request.POST.get('tution6')
                exam6 = request.POST.get('exam6')
                book6 = request.POST.get('book6')
                resitting6 = request.POST.get('resitting6')
                entrance6 = request.POST.get('entrance6')
                extra6 = request.POST.get('extra6')
                discount6 = request.POST.get('discount6')
                total6 = request.POST.get('total6')

                tution7 = request.POST.get('tution7')
                exam7 = request.POST.get('exam7')
                book7 = request.POST.get('book7')
                resitting7 = request.POST.get('resitting7')
                entrance7 = request.POST.get('entrance7')
                extra7 = request.POST.get('extra7')
                discount7 = request.POST.get('discount7')
                total7 = request.POST.get('total7')

                tution8 = request.POST.get('tution8')
                exam8 = request.POST.get('exam8')
                book8 = request.POST.get('book8')
                resitting8 = request.POST.get('resitting8')
                entrance8 = request.POST.get('entrance8')
                extra8 = request.POST.get('extra8')
                discount8 = request.POST.get('discount8')
                total8 = request.POST.get('total8')
                print("data :",tution1,exam1,book1, resitting1, entrance1, extra1,discount1, total1)
                print("data :",tution2,exam2,book2, resitting2, entrance2, extra2,discount2, total2)
                print("data :",tution3,exam3,book3, resitting3, entrance3, extra3,discount3, total3)
                print("data :",tution4,exam4,book4, resitting4, entrance4, extra4,discount4, total4)
                print("data :",tution5,exam5,book5, resitting5, entrance5, extra5,discount5, total5)
                print("data :",tution6,exam6,book6, resitting6, entrance6, extra6,discount6, total6)
                print("data :",tution7,exam7,book7, resitting7, entrance7, extra7,discount7, total7)
                print("data :",tution8,exam8,book8, resitting8, entrance8, extra8,discount8, total8)
                
                
                



                student_id = request.POST.get('student')
                no_of_semester = request.POST.get('no_of_semester')
                stream_semester = request.POST.get('stream_semester')
                
                
                if student_id and no_of_semester:
                    enrolled = Enrolled.objects.get(student = student_id)
                    print(enrolled)
                    if no_of_semester == '4':
                        
                        try:
                            semesterfees1 = StudentFees.objects.get(Q(student = student_id) & Q(sem="1"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "1")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "1")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data :",tution1,exam1,book1, resitting1, entrance1, extra1,discount1, total1)
                            if semesterfees1.tutionfees == tution1:
                                pass
                            else:
                                semesterfees1.tutionfees = tution1
                            if semesterfees1.examinationfees == exam1:
                                pass
                            else:
                                semesterfees1.examinationfees = exam1
                            if semesterfees1.bookfees == book1:
                                pass
                            else:
                                semesterfees1.bookfees = book1
                            if semesterfees1.resittingfees == resitting1:
                                pass
                            else:
                                semesterfees1.resittingfees = resitting1
                            if semesterfees1.entrancefees == entrance1:
                                pass
                            else:
                                semesterfees1.entrancefees = entrance1
                            if semesterfees1.extrafees == extra1:
                                pass
                            else:
                                semesterfees1.extrafees = extra1
                            if semesterfees1.discount == discount1:
                                pass
                            else:
                                semesterfees1.discount = discount1
                            if semesterfees1.totalfees == total1:
                                pass
                            else:
                                tempfees = semesterfees1.totalfees
                                semesterfees1.totalfees = total1
                                if mainreciept:
                                    mainreciept.pendingamount = int(total1) - int(mainreciept.paidamount)
                                    diff = int(total1) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")                                                      
                            semesterfees1.save()
                            
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Semester",stream=stream_semester, tutionfees=tution1,examinationfees=exam1,bookfees=book1,resittingfees=resitting1,entrancefees=entrance1,extrafees=extra1,discount=discount1,totalfees=total1,sem="1")
                            addsemesterfees.save()
                        try:
                            semesterfees2 = StudentFees.objects.get(Q(student = student_id) & Q(sem="2"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "2")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "2")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data :",tution2,exam2,book2, resitting2, entrance2, extra2,discount2, total2)
                            if semesterfees2.tutionfees == tution2:
                                pass
                            else:
                                semesterfees2.tutionfees = tution2
                            if semesterfees2.examinationfees == exam2:
                                pass
                            else:
                                semesterfees2.examinationfees = exam2
                            if semesterfees2.bookfees == book2:
                                pass
                            else:
                                semesterfees2.bookfees = book2
                            if semesterfees2.resittingfees == resitting2:
                                pass
                            else:
                                semesterfees2.resittingfees = resitting2
                            if semesterfees2.entrancefees == entrance2:
                                pass
                            else:
                                semesterfees2.entrancefees = entrance2
                            if semesterfees2.extrafees == extra2:
                                pass
                            else:
                                semesterfees2.extrafees = extra2
                            if semesterfees2.discount == discount2:
                                pass
                            else:
                                semesterfees2.discount = discount2
                            if semesterfees2.totalfees == total2:
                                pass
                            else:
                                tempfees = semesterfees2.totalfees
                                semesterfees2.totalfees = total2
                                if mainreciept:
                                    mainreciept.pendingamount = int(total2) - int(mainreciept.paidamount)
                                    diff = int(total2) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")
                                
                            semesterfees2.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Semester",stream=stream_semester, tutionfees=tution2,examinationfees=exam2,bookfees=book2,resittingfees=resitting2,entrancefees=entrance2,extrafees=extra2,discount=discount2,totalfees=total2,sem="2")
                            addsemesterfees.save()
                        try:
                            semesterfees3 = StudentFees.objects.get(Q(student = student_id) & Q(sem="3"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "3")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "3")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data :",tution3,exam3,book3, resitting3, entrance3, extra3,discount3, total3)
                            if semesterfees3.tutionfees == tution3:
                                pass
                            else:
                                semesterfees3.tutionfees = tution3
                            if semesterfees3.examinationfees == exam3:
                                pass
                            else:
                                semesterfees3.examinationfees = exam3
                            if semesterfees3.bookfees == book3:
                                pass
                            else:
                                semesterfees3.bookfees = book3
                            if semesterfees3.resittingfees == resitting3:
                                pass
                            else:
                                semesterfees3.resittingfees = resitting3
                            if semesterfees3.entrancefees == entrance3:
                                pass
                            else:
                                semesterfees3.entrancefees = entrance3
                            if semesterfees3.extrafees == extra3:
                                pass
                            else:
                                semesterfees3.extrafees = extra3
                            if semesterfees3.discount == discount3:
                                pass
                            else:
                                semesterfees3.discount = discount3
                            if semesterfees3.totalfees == total3:
                                pass
                            else:
                                tempfees = semesterfees3.totalfees
                                semesterfees3.totalfees = total3
                                if mainreciept:
                                    mainreciept.pendingamount = int(total3) - int(mainreciept.paidamount)
                                    diff = int(total3) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")
                               
                            semesterfees3.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Semester",stream=stream_semester, tutionfees=tution3,examinationfees=exam3,bookfees=book3,resittingfees=resitting3,entrancefees=entrance3,extrafees=extra3,discount=discount3,totalfees=total3,sem="3")
                            addsemesterfees.save()
                        try:
                            semesterfees4 = StudentFees.objects.get(Q(student = student_id) & Q(sem="4"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "4")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "4")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data :",tution4,exam4,book4, resitting4, entrance4, extra4,discount4, total4)
                            if semesterfees4.tutionfees == tution4:
                                pass
                            else:
                                semesterfees4.tutionfees = tution4
                            if semesterfees4.examinationfees == exam4:
                                pass
                            else:
                                semesterfees4.examinationfees = exam4
                            if semesterfees4.bookfees == book4:
                                pass
                            else:
                                semesterfees4.bookfees = book4
                            if semesterfees4.resittingfees == resitting4:
                                pass
                            else:
                                semesterfees4.resittingfees = resitting4
                            if semesterfees4.entrancefees == entrance4:
                                pass
                            else:
                                semesterfees4.entrancefees = entrance4
                            if semesterfees4.extrafees == extra4:
                                pass
                            else:
                                semesterfees4.extrafees = extra4
                            if semesterfees4.discount == discount4:
                                pass
                            else:
                                semesterfees4.discount = discount4
                            if semesterfees4.totalfees == total4:
                                pass
                            else:
                                tempfees = semesterfees4.totalfees
                                semesterfees4.totalfees = total4
                                if mainreciept:
                                    mainreciept.pendingamount = int(total4) - int(mainreciept.paidamount)
                                    diff = int(total4) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")
                                
                            semesterfees4.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Semester",stream=stream_semester, tutionfees=tution4,examinationfees=exam4,bookfees=book4,resittingfees=resitting4,entrancefees=entrance4,extrafees=extra4,discount=discount4,totalfees=total4,sem="4")
                            addsemesterfees.save()
                        return JsonResponse({'added':'yes'})

                    elif no_of_semester == '6':
                        try:
                            semesterfees1 = StudentFees.objects.get(Q(student = student_id)  & Q(sem="1"))
                            
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "1")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "1")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                                print("data :",tution1,exam1,book1, resitting1, entrance1, extra1,discount1, total1)
                            if semesterfees1.tutionfees == tution1:
                                pass
                            else:
                                semesterfees1.tutionfees = tution1
                            if semesterfees1.examinationfees == exam1:
                                pass
                            else:
                                semesterfees1.examinationfees = exam1
                            if semesterfees1.bookfees == book1:
                                pass
                            else:
                                semesterfees1.bookfees = book1
                            if semesterfees1.resittingfees == resitting1:
                                pass
                            else:
                                semesterfees1.resittingfees = resitting1
                            if semesterfees1.entrancefees == entrance1:
                                pass
                            else:
                                semesterfees1.entrancefees = entrance1
                            if semesterfees1.extrafees == extra1:
                                pass
                            else:
                                semesterfees1.extrafees = extra1
                            if semesterfees1.discount == discount1:
                                pass
                            else:
                                semesterfees1.discount = discount1
                            if semesterfees1.totalfees == total1:
                                pass
                            else:
                                tempfees = semesterfees1.totalfees
                                semesterfees1.totalfees = total1
                                if mainreciept:
                                    mainreciept.pendingamount = int(total1) - int(mainreciept.paidamount)
                                    diff = int(total1) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")
                                
                                

                               
                            
                            semesterfees1.save()
                            
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Semester",stream=stream_semester, tutionfees=tution1,examinationfees=exam1,bookfees=book1,resittingfees=resitting1,entrancefees=entrance1,extrafees=extra1,discount=discount1,totalfees=total1,sem="1")
                            addsemesterfees.save()
                        try:
                            semesterfees2 = StudentFees.objects.get(Q(student = student_id) & Q(sem="2"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "2")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "2")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data :",tution2,exam2,book2, resitting2, entrance2, extra2,discount2, total2)
                            if semesterfees2.tutionfees == tution2:
                                pass
                            else:
                                semesterfees2.tutionfees = tution2
                            if semesterfees2.examinationfees == exam2:
                                pass
                            else:
                                semesterfees2.examinationfees = exam2
                            if semesterfees2.bookfees == book2:
                                pass
                            else:
                                semesterfees2.bookfees = book2
                            if semesterfees2.resittingfees == resitting2:
                                pass
                            else:
                                semesterfees2.resittingfees = resitting2
                            if semesterfees2.entrancefees == entrance2:
                                pass
                            else:
                                semesterfees2.entrancefees = entrance2
                            if semesterfees2.extrafees == extra2:
                                pass
                            else:
                                semesterfees2.extrafees = extra2
                            if semesterfees2.discount == discount2:
                                pass
                            else:
                                semesterfees2.discount = discount2
                            if semesterfees2.totalfees == total2:
                                pass
                            else:
                                
                                tempfees = semesterfees2.totalfees
                                semesterfees2.totalfees = total2
                                if mainreciept:
                                    mainreciept.pendingamount = int(total2) - int(mainreciept.paidamount)
                                    diff = int(total2) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")
                                
                            semesterfees2.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Semester",stream=stream_semester, tutionfees=tution2,examinationfees=exam2,bookfees=book2,resittingfees=resitting2,entrancefees=entrance2,extrafees=extra2,discount=discount2,totalfees=total2,sem="2")
                            addsemesterfees.save()
                        try:
                            semesterfees3 = StudentFees.objects.get(Q(student = student_id) & Q(sem="3"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "3")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "3")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data :",tution3,exam3,book3, resitting3, entrance3, extra3,discount3, total3)
                            if semesterfees3.tutionfees == tution3:
                                pass
                            else:
                                semesterfees3.tutionfees = tution3
                            if semesterfees3.examinationfees == exam3:
                                pass
                            else:
                                semesterfees3.examinationfees = exam3
                            if semesterfees3.bookfees == book3:
                                pass
                            else:
                                semesterfees3.bookfees = book3
                            if semesterfees3.resittingfees == resitting3:
                                pass
                            else:
                                semesterfees3.resittingfees = resitting3
                            if semesterfees3.entrancefees == entrance3:
                                pass
                            else:
                                semesterfees3.entrancefees = entrance3
                            if semesterfees3.extrafees == extra3:
                                pass
                            else:
                                semesterfees3.extrafees = extra3
                            if semesterfees3.discount == discount3:
                                pass
                            else:
                                semesterfees3.discount = discount3
                            if semesterfees3.totalfees == total3:
                                pass
                            else:
                                tempfees = semesterfees3.totalfees
                                semesterfees3.totalfees = total3
                                if mainreciept:
                                    mainreciept.pendingamount = int(total3) - int(mainreciept.paidamount)
                                    diff = int(total3) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")
                               
                            semesterfees3.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Semester",stream=stream_semester, tutionfees=tution3,examinationfees=exam3,bookfees=book3,resittingfees=resitting3,entrancefees=entrance3,extrafees=extra3,discount=discount3,totalfees=total3,sem="3")
                            addsemesterfees.save()
                        try:
                            semesterfees4 = StudentFees.objects.get(Q(student = student_id) & Q(sem="4"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "4")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "4")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data :",tution4,exam4,book4, resitting4, entrance4, extra4,discount4, total4)
                            if semesterfees4.tutionfees == tution4:
                                pass
                            else:
                                semesterfees4.tutionfees = tution4
                            if semesterfees4.examinationfees == exam4:
                                pass
                            else:
                                semesterfees4.examinationfees = exam4
                            if semesterfees4.bookfees == book4:
                                pass
                            else:
                                semesterfees4.bookfees = book4
                            if semesterfees4.resittingfees == resitting4:
                                pass
                            else:
                                semesterfees4.resittingfees = resitting4
                            if semesterfees4.entrancefees == entrance4:
                                pass
                            else:
                                semesterfees4.entrancefees = entrance4
                            if semesterfees4.extrafees == extra4:
                                pass
                            else:
                                semesterfees4.extrafees = extra4
                            if semesterfees4.discount == discount4:
                                pass
                            else:
                                semesterfees4.discount = discount4
                            if semesterfees4.totalfees == total4:
                                pass
                            else:
                                tempfees = semesterfees4.totalfees
                                semesterfees4.totalfees = total4
                                if mainreciept:
                                    mainreciept.pendingamount = int(total4) - int(mainreciept.paidamount)
                                    diff = int(total4) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")
                                
                            semesterfees4.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Semester",stream=stream_semester, tutionfees=tution4,examinationfees=exam4,bookfees=book4,resittingfees=resitting4,entrancefees=entrance4,extrafees=extra4,discount=discount4,totalfees=total4,sem="4")
                            addsemesterfees.save()
                        try:
                            semesterfees5 = StudentFees.objects.get(Q(student = student_id) & Q(sem="5"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "5")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "5")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data :",tution5,exam5,book5, resitting5, entrance5, extra5,discount5, total5)
                            if semesterfees5.tutionfees == tution5:
                                pass
                            else:
                                semesterfees5.tutionfees = tution5
                            if semesterfees5.examinationfees == exam5:
                                pass
                            else:
                                semesterfees5.examinationfees = exam5
                            if semesterfees5.bookfees == book5:
                                pass
                            else:
                                semesterfees5.bookfees = book5
                            if semesterfees5.resittingfees == resitting5:
                                pass
                            else:
                                semesterfees5.resittingfees = resitting5
                            if semesterfees5.entrancefees == entrance5:
                                pass
                            else:
                                semesterfees5.entrancefees = entrance5
                            if semesterfees5.extrafees == extra5:
                                pass
                            else:
                                semesterfees5.extrafees = extra5
                            if semesterfees5.discount == discount5:
                                pass
                            else:
                                semesterfees5.discount = discount5
                            if semesterfees5.totalfees == total5:
                                pass
                            else:
                                tempfees = semesterfees5.totalfees
                                semesterfees5.totalfees = total5
                                if mainreciept:
                                    mainreciept.pendingamount = int(total5) - int(mainreciept.paidamount)
                                    diff = int(total5) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")
                                
                            semesterfees5.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Semester",stream=stream_semester, tutionfees=tution5,examinationfees=exam5,bookfees=book5,resittingfees=resitting5,entrancefees=entrance5,extrafees=extra5,discount=discount5,totalfees=total5,sem="5")
                            addsemesterfees.save()
                        try:
                            semesterfees6 = StudentFees.objects.get(Q(student = student_id) & Q(sem="6"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "6")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "6")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data :",tution6,exam6,book6, resitting6, entrance6, extra6,discount6, total6)
                            if semesterfees6.tutionfees == tution6:
                                pass
                            else:
                                semesterfees6.tutionfees = tution6
                            if semesterfees6.examinationfees == exam6:
                                pass
                            else:
                                semesterfees6.examinationfees = exam6
                            if semesterfees6.bookfees == book6:
                                pass
                            else:
                                semesterfees6.bookfees = book6
                            if semesterfees6.resittingfees == resitting6:
                                pass
                            else:
                                semesterfees6.resittingfees = resitting6
                            if semesterfees6.entrancefees == entrance6:
                                pass
                            else:
                                semesterfees6.entrancefees = entrance6
                            if semesterfees6.extrafees == extra6:
                                pass
                            else:
                                semesterfees6.extrafees = extra6
                            if semesterfees6.discount == discount6:
                                pass
                            else:
                                semesterfees6.discount = discount6
                            if semesterfees6.totalfees == total6:
                                pass
                            else:
                                tempfees = semesterfees6.totalfees
                                semesterfees6.totalfees = total6
                                if mainreciept:
                                    mainreciept.pendingamount = int(total6) - int(mainreciept.paidamount)
                                    diff = int(total6) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")
                                
                            semesterfees6.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Semester",stream=stream_semester, tutionfees=tution6,examinationfees=exam6,bookfees=book6,resittingfees=resitting6,entrancefees=entrance6,extrafees=extra6,discount=discount6,totalfees=total6,sem="6")
                            addsemesterfees.save()
                        return JsonResponse({'added':'yes'})
                        
                    elif no_of_semester == '8':
                        try:
                            semesterfees1 = StudentFees.objects.get(Q(student = student_id) & Q(sem="1"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "1")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "1")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data :",tution1,exam1,book1, resitting1, entrance1, extra1,discount1, total1)
                            if semesterfees1.tutionfees == tution1:
                                pass
                            else:
                                semesterfees1.tutionfees = tution1
                            if semesterfees1.examinationfees == exam1:
                                pass
                            else:
                                semesterfees1.examinationfees = exam1
                            if semesterfees1.bookfees == book1:
                                pass
                            else:
                                semesterfees1.bookfees = book1
                            if semesterfees1.resittingfees == resitting1:
                                pass
                            else:
                                semesterfees1.resittingfees = resitting1
                            if semesterfees1.entrancefees == entrance1:
                                pass
                            else:
                                semesterfees1.entrancefees = entrance1
                            if semesterfees1.extrafees == extra1:
                                pass
                            else:
                                semesterfees1.extrafees = extra1
                            if semesterfees1.discount == discount1:
                                pass
                            else:
                                semesterfees1.discount = discount1
                            if semesterfees1.totalfees == total1:
                                pass
                            else:
                                tempfees = semesterfees1.totalfees
                                semesterfees1.totalfees = total1
                                if mainreciept:
                                    mainreciept.pendingamount = int(total1) - int(mainreciept.paidamount)
                                    diff = int(total1) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")
                               
                            
                            semesterfees1.save()
                            
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Semester",stream=stream_semester, tutionfees=tution1,examinationfees=exam1,bookfees=book1,resittingfees=resitting1,entrancefees=entrance1,extrafees=extra1,discount=discount1,totalfees=total1,sem="1")
                            addsemesterfees.save()
                        try:
                            semesterfees2 = StudentFees.objects.get(Q(student = student_id) & Q(sem="2"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "2")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "2")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data :",tution2,exam2,book2, resitting2, entrance2, extra2,discount2, total2)
                            if semesterfees2.tutionfees == tution2:
                                pass
                            else:
                                semesterfees2.tutionfees = tution2
                            if semesterfees2.examinationfees == exam2:
                                pass
                            else:
                                semesterfees2.examinationfees = exam2
                            if semesterfees2.bookfees == book2:
                                pass
                            else:
                                semesterfees2.bookfees = book2
                            if semesterfees2.resittingfees == resitting2:
                                pass
                            else:
                                semesterfees2.resittingfees = resitting2
                            if semesterfees2.entrancefees == entrance2:
                                pass
                            else:
                                semesterfees2.entrancefees = entrance2
                            if semesterfees2.extrafees == extra2:
                                pass
                            else:
                                semesterfees2.extrafees = extra2
                            if semesterfees2.discount == discount2:
                                pass
                            else:
                                semesterfees2.discount = discount2
                            if semesterfees2.totalfees == total2:
                                pass
                            else:
                                tempfees = semesterfees2.totalfees
                                semesterfees2.totalfees = total2
                                if mainreciept:
                                    mainreciept.pendingamount = int(total2) - int(mainreciept.paidamount)
                                    diff = int(total2) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")
                                
                            semesterfees2.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Semester",stream=stream_semester, tutionfees=tution2,examinationfees=exam2,bookfees=book2,resittingfees=resitting2,entrancefees=entrance2,extrafees=extra2,discount=discount2,totalfees=total2,sem="2")
                            addsemesterfees.save()
                        try:
                            semesterfees3 = StudentFees.objects.get(Q(student = student_id) & Q(sem="3"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "3")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "3")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data :",tution3,exam3,book3, resitting3, entrance3, extra3,discount3, total3)
                            if semesterfees3.tutionfees == tution3:
                                pass
                            else:
                                semesterfees3.tutionfees = tution3
                            if semesterfees3.examinationfees == exam3:
                                pass
                            else:
                                semesterfees3.examinationfees = exam3
                            if semesterfees3.bookfees == book3:
                                pass
                            else:
                                semesterfees3.bookfees = book3
                            if semesterfees3.resittingfees == resitting3:
                                pass
                            else:
                                semesterfees3.resittingfees = resitting3
                            if semesterfees3.entrancefees == entrance3:
                                pass
                            else:
                                semesterfees3.entrancefees = entrance3
                            if semesterfees3.extrafees == extra3:
                                pass
                            else:
                                semesterfees3.extrafees = extra3
                            if semesterfees3.discount == discount3:
                                pass
                            else:
                                semesterfees3.discount = discount3
                            if semesterfees3.totalfees == total3:
                                pass
                            else:
                                tempfees = semesterfees3.totalfees
                                semesterfees3.totalfees = total3
                                if mainreciept:
                                    mainreciept.pendingamount = int(total3) - int(mainreciept.paidamount)
                                    diff = int(total3) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")
                               
                            semesterfees3.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Semester",stream=stream_semester, tutionfees=tution3,examinationfees=exam3,bookfees=book3,resittingfees=resitting3,entrancefees=entrance3,extrafees=extra3,discount=discount3,totalfees=total3,sem="3")
                            addsemesterfees.save()
                        try:
                            semesterfees4 = StudentFees.objects.get(Q(student = student_id) & Q(sem="4"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "4")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "4")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data :",tution4,exam4,book4, resitting4, entrance4, extra4,discount4, total4)
                            if semesterfees4.tutionfees == tution4:
                                pass
                            else:
                                semesterfees4.tutionfees = tution4
                            if semesterfees4.examinationfees == exam4:
                                pass
                            else:
                                semesterfees4.examinationfees = exam4
                            if semesterfees4.bookfees == book4:
                                pass
                            else:
                                semesterfees4.bookfees = book4
                            if semesterfees4.resittingfees == resitting4:
                                pass
                            else:
                                semesterfees4.resittingfees = resitting4
                            if semesterfees4.entrancefees == entrance4:
                                pass
                            else:
                                semesterfees4.entrancefees = entrance4
                            if semesterfees4.extrafees == extra4:
                                pass
                            else:
                                semesterfees4.extrafees = extra4
                            if semesterfees4.discount == discount4:
                                pass
                            else:
                                semesterfees4.discount = discount4
                            if semesterfees4.totalfees == total4:
                                pass
                            else:
                                tempfees = semesterfees4.totalfees
                                semesterfees4.totalfees = total4
                                if mainreciept:
                                    mainreciept.pendingamount = int(total4) - int(mainreciept.paidamount)
                                    diff = int(total4) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")
                                
                            semesterfees4.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Semester",stream=stream_semester, tutionfees=tution4,examinationfees=exam4,bookfees=book4,resittingfees=resitting4,entrancefees=entrance4,extrafees=extra4,discount=discount4,totalfees=total4,sem="4")
                            addsemesterfees.save()
                        try:
                            semesterfees5 = StudentFees.objects.get(Q(student = student_id) & Q(sem="5"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "5")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "5")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data :",tution5,exam5,book5, resitting5, entrance5, extra5,discount5, total5)
                            if semesterfees5.tutionfees == tution5:
                                pass
                            else:
                                semesterfees5.tutionfees = tution5
                            if semesterfees5.examinationfees == exam5:
                                pass
                            else:
                                semesterfees5.examinationfees = exam5
                            if semesterfees5.bookfees == book5:
                                pass
                            else:
                                semesterfees5.bookfees = book5
                            if semesterfees5.resittingfees == resitting5:
                                pass
                            else:
                                semesterfees5.resittingfees = resitting5
                            if semesterfees5.entrancefees == entrance5:
                                pass
                            else:
                                semesterfees5.entrancefees = entrance5
                            if semesterfees5.extrafees == extra5:
                                pass
                            else:
                                semesterfees5.extrafees = extra5
                            if semesterfees5.discount == discount5:
                                pass
                            else:
                                semesterfees5.discount = discount5
                            if semesterfees5.totalfees == total5:
                                pass
                            else:
                                tempfees = semesterfees5.totalfees
                                semesterfees5.totalfees = total5
                                if mainreciept:
                                    mainreciept.pendingamount = int(total5) - int(mainreciept.paidamount)
                                    diff = int(total5) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")
                                
                            semesterfees5.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Semester",stream=stream_semester, tutionfees=tution5,examinationfees=exam5,bookfees=book5,resittingfees=resitting5,entrancefees=entrance5,extrafees=extra5,discount=discount5,totalfees=total5,sem="5")
                            addsemesterfees.save()
                        try:
                            semesterfees6 = StudentFees.objects.get(Q(student = student_id) & Q(sem="6"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "6")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "6")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data :",tution6,exam6,book6, resitting6, entrance6, extra6,discount6, total6)
                            if semesterfees6.tutionfees == tution6:
                                pass
                            else:
                                semesterfees6.tutionfees = tution6
                            if semesterfees6.examinationfees == exam6:
                                pass
                            else:
                                semesterfees6.examinationfees = exam6
                            if semesterfees6.bookfees == book6:
                                pass
                            else:
                                semesterfees6.bookfees = book6
                            if semesterfees6.resittingfees == resitting6:
                                pass
                            else:
                                semesterfees6.resittingfees = resitting6
                            if semesterfees6.entrancefees == entrance6:
                                pass
                            else:
                                semesterfees6.entrancefees = entrance6
                            if semesterfees6.extrafees == extra6:
                                pass
                            else:
                                semesterfees6.extrafees = extra6
                            if semesterfees6.discount == discount6:
                                pass
                            else:
                                semesterfees6.discount = discount6
                            if semesterfees6.totalfees == total6:
                                pass
                            else:
                                tempfees = semesterfees6.totalfees
                                semesterfees6.totalfees = total6
                                if mainreciept:
                                    mainreciept.pendingamount = int(total6) - int(mainreciept.paidamount)
                                    diff = int(total6) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")
                                
                            semesterfees6.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Semester",stream=stream_semester, tutionfees=tution6,examinationfees=exam6,bookfees=book6,resittingfees=resitting6,entrancefees=entrance6,extrafees=extra6,discount=discount6,totalfees=total6,sem="6")
                            addsemesterfees.save()
                        try:
                            semesterfees7 = StudentFees.objects.get(Q(student = student_id) & Q(sem="7"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "7")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "7")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data :",tution7,exam7,book7, resitting7, entrance7, extra7,discount7, total7)
                            if semesterfees7.tutionfees == tution7:
                                pass
                            else:
                                semesterfees7.tutionfees = tution7
                            if semesterfees7.examinationfees == exam7:
                                pass
                            else:
                                semesterfees7.examinationfees = exam7
                            if semesterfees7.bookfees == book7:
                                pass
                            else:
                                semesterfees7.bookfees = book7
                            if semesterfees7.resittingfees == resitting7:
                                pass
                            else:
                                semesterfees7.resittingfees = resitting7
                            if semesterfees7.entrancefees == entrance7:
                                pass
                            else:
                                semesterfees7.entrancefees = entrance7
                            if semesterfees7.extrafees == extra7:
                                pass
                            else:
                                semesterfees7.extrafees = extra7
                            if semesterfees7.discount == discount7:
                                pass
                            else:
                                semesterfees7.discount = discount7
                            if semesterfees7.totalfees == total7:
                                pass
                            else:
                                tempfees = semesterfees7.totalfees
                                semesterfees7.totalfees = total7
                                if mainreciept:
                                    mainreciept.pendingamount = int(total7) - int(mainreciept.paidamount)
                                    diff = int(total7) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")
                                
                            semesterfees7.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Semester",stream=stream_semester, tutionfees=tution7,examinationfees=exam7,bookfees=book7,resittingfees=resitting7,entrancefees=entrance7,extrafees=extra7,discount=discount7,totalfees=total7,sem="7")
                            addsemesterfees.save()
                        try:
                            semesterfees8 = StudentFees.objects.get(Q(student = student_id) & Q(sem="8"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "8")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "8")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data :",tution8,exam8,book8, resitting8, entrance8, extra8,discount8, total8)
                            if semesterfees8.tutionfees == tution8:
                                pass
                            else:
                                semesterfees8.tutionfees = tution8
                            if semesterfees8.examinationfees == exam8:
                                pass
                            else:
                                semesterfees8.examinationfees = exam8
                            if semesterfees8.bookfees == book8:
                                pass
                            else:
                                semesterfees8.bookfees = book8
                            if semesterfees8.resittingfees == resitting8:
                                pass
                            else:
                                semesterfees8.resittingfees = resitting8
                            if semesterfees8.entrancefees == entrance8:
                                pass
                            else:
                                semesterfees8.entrancefees = entrance8
                            if semesterfees8.extrafees == extra8:
                                pass
                            else:
                                semesterfees8.extrafees = extra8
                            if semesterfees8.discount == discount8:
                                pass
                            else:
                                semesterfees8.discount = discount8
                            if semesterfees8.totalfees == total8:
                                pass
                            else:
                                tempfees = semesterfees8.totalfees
                                semesterfees8.totalfees = total8
                                if mainreciept:
                                    mainreciept.pendingamount = int(total8) - int(mainreciept.paidamount)
                                    diff = int(total8) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")
                                
                            semesterfees8.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Semester",stream=stream_semester, tutionfees=tution8,examinationfees=exam8,bookfees=book8,resittingfees=resitting8,entrancefees=entrance8,extrafees=extra8,discount=discount8,totalfees=total8,sem="8")
                            addsemesterfees.save()
                        return JsonResponse({'added':'yes'})

                no_of_year = request.POST.get('no_of_year')
                stream_year = request.POST.get('stream_year')
                year_tution1 = request.POST.get('year_tution1')
                year_exam1 = request.POST.get('year_exam1')
                year_book1 = request.POST.get('year_book1')
                year_resitting1 = request.POST.get('year_resitting1')
                year_entrance1 = request.POST.get('year_entrance1')
                year_extra1 = request.POST.get('year_extra1')
                year_discount1 = request.POST.get('year_discount1')
                year_total1 = request.POST.get('year_total1')
                
                year_tution2 = request.POST.get('year_tution2')
                year_exam2 = request.POST.get('year_exam2')
                year_book2 = request.POST.get('year_book2')
                year_resitting2 = request.POST.get('year_resitting2')
                year_entrance2 = request.POST.get('year_entrance2')
                year_extra2 = request.POST.get('year_extra2')
                year_discount2 = request.POST.get('year_discount2')
                year_total2 = request.POST.get('year_total2')
                
                year_tution3 = request.POST.get('year_tution3')
                year_exam3 = request.POST.get('year_exam3')
                year_book3 = request.POST.get('year_book3')
                year_resitting3 = request.POST.get('year_resitting3')
                year_entrance3 = request.POST.get('year_entrance3')
                year_extra3 = request.POST.get('year_extra3')
                year_discount3 = request.POST.get('year_discount3')
                year_total3 = request.POST.get('year_total3')
                
                year_tution4 = request.POST.get('year_tution4')
                year_exam4 = request.POST.get('year_exam4')
                year_book4 = request.POST.get('year_book4')
                year_resitting4 = request.POST.get('year_resitting4')
                year_entrance4 = request.POST.get('year_entrance4')
                year_extra4 = request.POST.get('year_extra4')
                year_discount4 = request.POST.get('year_discount4')
                year_total4 = request.POST.get('year_total4')


                if student_id and no_of_year:
                    if no_of_year == '2':
                        
                        try:
                            semesterfees1 = StudentFees.objects.get(Q(student = student_id) & Q(sem="1"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "1")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                print("all payment reciept : ",allpaymentreciept)
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "1")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data year:", year_tution1, year_exam1, year_book1, year_resitting1, year_entrance1, year_extra1, year_discount1, year_total1)
                            if semesterfees1.tutionfees == year_tution1:
                                pass
                            else:
                                semesterfees1.tutionfees = year_tution1
                            if semesterfees1.examinationfees == year_exam1:
                                pass
                            else:
                                semesterfees1.examinationfees = year_exam1
                            if semesterfees1.bookfees == year_book1:
                                pass
                            else:
                                semesterfees1.bookfees = year_book1
                            if semesterfees1.resittingfees == year_resitting1:
                                pass
                            else:
                                semesterfees1.resittingfees = year_resitting1
                            if semesterfees1.entrancefees == year_entrance1:
                                pass
                            else:
                                semesterfees1.entrancefees = year_entrance1
                            if semesterfees1.extrafees == year_extra1:
                                pass
                            else:
                                semesterfees1.extrafees = year_extra1
                            if semesterfees1.discount == year_discount1:
                                pass
                            else:
                                semesterfees1.discount = year_discount1
                            if semesterfees1.totalfees == year_total1:
                                pass
                            else:
                                tempfees = semesterfees1.totalfees
                                semesterfees1.totalfees = year_total1
                                if mainreciept:
                                    mainreciept.pendingamount = int(year_total1) - int(mainreciept.paidamount)
                                    diff = int(year_total1) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")                          
                            semesterfees1.save()
                            
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Annual",stream=stream_year, tutionfees=year_tution1,examinationfees=year_exam1,bookfees=year_book1,resittingfees=year_resitting1,entrancefees=year_entrance1,extrafees=year_extra1,discount=year_discount1,totalfees=year_total1,sem="1")
                            addsemesterfees.save()
                            print("added year 2 year 1")
                        try:
                            semesterfees2 = StudentFees.objects.get(Q(student = student_id) & Q(sem="2"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "2")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "2")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data year:", year_tution2, year_exam2, year_book2, year_resitting2, year_entrance2, year_extra2, year_discount2, year_total2)
                            if semesterfees2.tutionfees == year_tution2:
                                pass
                            else:
                                semesterfees2.tutionfees = year_tution2
                            if semesterfees2.examinationfees == year_exam2:
                                pass
                            else:
                                semesterfees2.examinationfees = year_exam2
                            if semesterfees2.bookfees == year_book2:
                                pass
                            else:
                                semesterfees2.bookfees = year_book2
                            if semesterfees2.resittingfees == year_resitting2:
                                pass
                            else:
                                semesterfees2.resittingfees = year_resitting2
                            if semesterfees2.entrancefees == year_entrance2:
                                pass
                            else:
                                semesterfees2.entrancefees = year_entrance2
                            if semesterfees2.extrafees == year_extra2:
                                pass
                            else:
                                semesterfees2.extrafees = year_extra2
                            if semesterfees2.discount == year_discount2:
                                pass
                            else:
                                semesterfees2.discount = year_discount2
                            if semesterfees2.totalfees == year_total2:
                                pass
                            else:
                                tempfees = semesterfees2.totalfees
                                semesterfees2.totalfees = year_total2
                                if mainreciept:
                                    mainreciept.pendingamount = int(year_total2) - int(mainreciept.paidamount)
                                    diff = int(year_total2) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")  
                                
                            semesterfees2.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id, studypattern="Annual",stream=stream_year, tutionfees=year_tution2,examinationfees=year_exam2,bookfees=year_book2,resittingfees=year_resitting2,entrancefees=year_entrance2,extrafees=year_extra2,discount=year_discount2,totalfees=year_total2,sem="2")
                            addsemesterfees.save()
                            print("added year 2 year 2")
                        
                        return JsonResponse({'added':'yes'})

                    elif no_of_year == '3':
                        try:
                            semesterfees1 = StudentFees.objects.get(Q(student = student_id) & Q(sem="1"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "1")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "1")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data year:", year_tution1, year_exam1, year_book1, year_resitting1, year_entrance1, year_extra1, year_discount1, year_total1)
                            if semesterfees1.tutionfees == year_tution1:
                                pass
                            else:
                                semesterfees1.tutionfees = year_tution1
                            if semesterfees1.examinationfees == year_exam1:
                                pass
                            else:
                                semesterfees1.examinationfees = year_exam1
                            if semesterfees1.bookfees == year_book1:
                                pass
                            else:
                                semesterfees1.bookfees = year_book1
                            if semesterfees1.resittingfees == year_resitting1:
                                pass
                            else:
                                semesterfees1.resittingfees = year_resitting1
                            if semesterfees1.entrancefees == year_entrance1:
                                pass
                            else:
                                semesterfees1.entrancefees = year_entrance1
                            if semesterfees1.extrafees == year_extra1:
                                pass
                            else:
                                semesterfees1.extrafees = year_extra1
                            if semesterfees1.discount == year_discount1:
                                pass
                            else:
                                semesterfees1.discount = year_discount1
                            if semesterfees1.totalfees == year_total1:
                                pass
                            else:
                                tempfees = semesterfees1.totalfees
                                semesterfees1.totalfees = year_total1
                                if mainreciept:
                                    mainreciept.pendingamount = int(year_total1) - int(mainreciept.paidamount)
                                    diff = int(year_total1) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")  
                               
                            
                            semesterfees1.save()
                            
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Annual",stream=stream_year, tutionfees=year_tution1,examinationfees=year_exam1,bookfees=year_book1,resittingfees=year_resitting1,entrancefees=year_entrance1,extrafees=year_extra1,discount=year_discount1,totalfees=year_total1,sem="1")
                            addsemesterfees.save()
                            print("added year 3 year 1")
                        try:
                            semesterfees2 = StudentFees.objects.get(Q(student = student_id) & Q(sem="2"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "2")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "2")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data year:", year_tution2, year_exam2, year_book2, year_resitting2, year_entrance2, year_extra2, year_discount2, year_total2)
                            if semesterfees2.tutionfees == year_tution2:
                                pass
                            else:
                                semesterfees2.tutionfees = year_tution2
                            if semesterfees2.examinationfees == year_exam2:
                                pass
                            else:
                                semesterfees2.examinationfees = year_exam2
                            if semesterfees2.bookfees == year_book2:
                                pass
                            else:
                                semesterfees2.bookfees = year_book2
                            if semesterfees2.resittingfees == year_resitting2:
                                pass
                            else:
                                semesterfees2.resittingfees = year_resitting2
                            if semesterfees2.entrancefees == year_entrance2:
                                pass
                            else:
                                semesterfees2.entrancefees = year_entrance2
                            if semesterfees2.extrafees == year_extra2:
                                pass
                            else:
                                semesterfees2.extrafees = year_extra2
                            if semesterfees2.discount == year_discount2:
                                pass
                            else:
                                semesterfees2.discount = year_discount2
                            if semesterfees2.totalfees == year_total2:
                                pass
                            else:
                                tempfees = semesterfees2.totalfees
                                semesterfees2.totalfees = year_total2
                                if mainreciept:
                                    mainreciept.pendingamount = int(year_total2) - int(mainreciept.paidamount)
                                    diff = int(year_total2) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")  
                                
                            semesterfees2.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Annual",stream=stream_year, tutionfees=year_tution2,examinationfees=year_exam2,bookfees=year_book2,resittingfees=year_resitting2,entrancefees=year_entrance2,extrafees=year_extra2,discount=year_discount2,totalfees=year_total2,sem="2")
                            addsemesterfees.save()
                            print("added year 3 year 2")
                        try:
                            semesterfees3 = StudentFees.objects.get(Q(student = student_id) & Q(sem="3"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "3")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "3")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data year:", year_tution3, year_exam3, year_book3, year_resitting3, year_entrance3, year_extra3, year_discount3, year_total3)
                            if semesterfees3.tutionfees == year_tution3:
                                pass
                            else:
                                semesterfees3.tutionfees = year_tution3
                            if semesterfees3.examinationfees == year_exam3:
                                pass
                            else:
                                semesterfees3.examinationfees = year_exam3
                            if semesterfees3.bookfees == year_book3:
                                pass
                            else:
                                semesterfees3.bookfees = year_book3
                            if semesterfees3.resittingfees == year_resitting3:
                                pass
                            else:
                                semesterfees3.resittingfees = year_resitting3
                            if semesterfees3.entrancefees == year_entrance3:
                                pass
                            else:
                                semesterfees3.entrancefees = year_entrance3
                            if semesterfees3.extrafees == year_extra3:
                                pass
                            else:
                                semesterfees3.extrafees = year_extra3
                            if semesterfees3.discount == year_discount3:
                                pass
                            else:
                                semesterfees3.discount = year_discount3
                            if semesterfees3.totalfees == year_total3:
                                pass
                            else:
                                tempfees = semesterfees3.totalfees
                                semesterfees3.totalfees = year_total3
                                if mainreciept:
                                    mainreciept.pendingamount = int(year_total3) - int(mainreciept.paidamount)
                                    diff = int(year_total3) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")  
                               
                            semesterfees3.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Annual",stream=stream_year, tutionfees=year_tution3,examinationfees=year_exam3,bookfees=year_book3,resittingfees=year_resitting3,entrancefees=year_entrance3,extrafees=year_extra3,discount=year_discount3,totalfees=year_total3,sem="3")
                            addsemesterfees.save()
                            print("added year 3 year 3")
                        
                        return JsonResponse({'added':'yes'})
                        
                    elif no_of_year == '4':
                        try:
                            semesterfees1 = StudentFees.objects.get(Q(student = student_id) & Q(sem="1"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "1")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "1")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data year:", year_tution1, year_exam1, year_book1, year_resitting1, year_entrance1, year_extra1, year_discount1, year_total1)
                            if semesterfees1.tutionfees == year_tution1:
                                pass
                            else:
                                semesterfees1.tutionfees = year_tution1
                            if semesterfees1.examinationfees == year_exam1:
                                pass
                            else:
                                semesterfees1.examinationfees = year_exam1
                            if semesterfees1.bookfees == year_book1:
                                pass
                            else:
                                semesterfees1.bookfees = year_book1
                            if semesterfees1.resittingfees == year_resitting1:
                                pass
                            else:
                                semesterfees1.resittingfees = year_resitting1
                            if semesterfees1.entrancefees == year_entrance1:
                                pass
                            else:
                                semesterfees1.entrancefees = year_entrance1
                            if semesterfees1.extrafees == year_extra1:
                                pass
                            else:
                                semesterfees1.extrafees = year_extra1
                            if semesterfees1.discount == year_discount1:
                                pass
                            else:
                                semesterfees1.discount = year_discount1
                            if semesterfees1.totalfees == year_total1:
                                pass
                            else:
                                tempfees = semesterfees1.totalfees
                                semesterfees1.totalfees = year_total1
                                if mainreciept:
                                    mainreciept.pendingamount = int(year_total1) - int(mainreciept.paidamount)
                                    diff = int(year_total1) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")  
                               
                            
                            semesterfees1.save()
                            
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Annual",stream=stream_year, tutionfees=year_tution1,examinationfees=year_exam1,bookfees=year_book1,resittingfees=year_resitting1,entrancefees=year_entrance1,extrafees=year_extra1,discount=year_discount1,totalfees=year_total1,sem="1")
                            addsemesterfees.save()
                            print("added year 4 year 1")
                        try:
                            semesterfees2 = StudentFees.objects.get(Q(student = student_id) & Q(sem="2"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "2")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "2")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data year:", year_tution2, year_exam2, year_book2, year_resitting2, year_entrance2, year_extra2, year_discount2, year_total2)
                            if semesterfees2.tutionfees == year_tution2:
                                pass
                            else:
                                semesterfees2.tutionfees = year_tution2
                            if semesterfees2.examinationfees == year_exam2:
                                pass
                            else:
                                semesterfees2.examinationfees = year_exam2
                            if semesterfees2.bookfees == year_book2:
                                pass
                            else:
                                semesterfees2.bookfees = year_book2
                            if semesterfees2.resittingfees == year_resitting2:
                                pass
                            else:
                                semesterfees2.resittingfees = year_resitting2
                            if semesterfees2.entrancefees == year_entrance2:
                                pass
                            else:
                                semesterfees2.entrancefees = year_entrance2
                            if semesterfees2.extrafees == year_extra2:
                                pass
                            else:
                                semesterfees2.extrafees = year_extra2
                            if semesterfees2.discount == year_discount2:
                                pass
                            else:
                                semesterfees2.discount = year_discount2
                            if semesterfees2.totalfees == year_total2:
                                pass
                            else:
                                tempfees = semesterfees2.totalfees
                                semesterfees2.totalfees = year_total2
                                if mainreciept:
                                    mainreciept.pendingamount = int(year_total2) - int(mainreciept.paidamount)
                                    diff = int(year_total2) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")  
                                
                            semesterfees2.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Annual",stream=stream_year, tutionfees=year_tution2,examinationfees=year_exam2,bookfees=year_book2,resittingfees=year_resitting2,entrancefees=year_entrance2,extrafees=year_extra2,discount=year_discount2,totalfees=year_total2,sem="2")
                            addsemesterfees.save()
                            print("added year 4 year 2")
                        try:
                            semesterfees3 = StudentFees.objects.get(Q(student = student_id) & Q(sem="3"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "3")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "3")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data year:", year_tution3, year_exam3, year_book3, year_resitting3, year_entrance3, year_extra3, year_discount3, year_total3)
                            if semesterfees3.tutionfees == year_tution3:
                                pass
                            else:
                                semesterfees3.tutionfees = year_tution3
                            if semesterfees3.examinationfees == year_exam3:
                                pass
                            else:
                                semesterfees3.examinationfees = year_exam3
                            if semesterfees3.bookfees == year_book3:
                                pass
                            else:
                                semesterfees3.bookfees = year_book3
                            if semesterfees3.resittingfees == year_resitting3:
                                pass
                            else:
                                semesterfees3.resittingfees = year_resitting3
                            if semesterfees3.entrancefees == year_entrance3:
                                pass
                            else:
                                semesterfees3.entrancefees = year_entrance3
                            if semesterfees3.extrafees == year_extra3:
                                pass
                            else:
                                semesterfees3.extrafees = year_extra3
                            if semesterfees3.discount == year_discount3:
                                pass
                            else:
                                semesterfees3.discount = year_discount3
                            if semesterfees3.totalfees == year_total3:
                                pass
                            else:
                                tempfees = semesterfees3.totalfees
                                semesterfees3.totalfees = year_total3
                                if mainreciept:
                                    mainreciept.pendingamount = int(year_total3) - int(mainreciept.paidamount)
                                    diff = int(year_total3) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")  
                               
                            semesterfees3.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Annual",stream=stream_year, tutionfees=year_tution3,examinationfees=year_exam3,bookfees=year_book3,resittingfees=year_resitting3,entrancefees=year_entrance3,extrafees=year_extra3,discount=year_discount3,totalfees=year_total3,sem="3")
                            addsemesterfees.save()
                            print("added year 4 year 3")
                        try:
                            semesterfees4 = StudentFees.objects.get(Q(student = student_id) & Q(sem="4"))
                            allpaymentreciept = PaymentReciept.objects.filter(Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "4")).order_by('id')
                            mainreciept = ""
                            if allpaymentreciept:
                                mainreciept = allpaymentreciept[0]
                                print("First Main : ",mainreciept)
                                remainingpaymentreciept = PaymentReciept.objects.filter(~Q(id = mainreciept.id) & Q(student = student_id) & Q(payment_for = "Course Fees") & Q(semyear = "4")).order_by('id')
                                print("Remaining All : ",remainingpaymentreciept)
                            print("data year:", year_tution4, year_exam4, year_book4, year_resitting4, year_entrance4, year_extra4, year_discount4, year_total4)
                            if semesterfees4.tutionfees == year_tution4:
                                pass
                            else:
                                semesterfees4.tutionfees = year_tution4
                            if semesterfees4.examinationfees == year_exam4:
                                pass
                            else:
                                semesterfees4.examinationfees = year_exam4
                            if semesterfees4.bookfees == year_book4:
                                pass
                            else:
                                semesterfees4.bookfees = year_book4
                            if semesterfees4.resittingfees == year_resitting4:
                                pass
                            else:
                                semesterfees4.resittingfees = year_resitting4
                            if semesterfees4.entrancefees == year_entrance4:
                                pass
                            else:
                                semesterfees4.entrancefees = year_entrance4
                            if semesterfees4.extrafees == year_extra4:
                                pass
                            else:
                                semesterfees4.extrafees = year_extra4
                            if semesterfees4.discount == year_discount4:
                                pass
                            else:
                                semesterfees4.discount = year_discount4
                            if semesterfees4.totalfees == year_total4:
                                pass
                            else:
                                tempfees = semesterfees4.totalfees
                                semesterfees4.totalfees = year_total4
                                if mainreciept:
                                    mainreciept.pendingamount = int(year_total4) - int(mainreciept.paidamount)
                                    diff = int(year_total4) - int(tempfees)
                                    print(diff)
                                    print((int(mainreciept.paidamount) + int(mainreciept.pendingamount)) , int(mainreciept.paidamount) , int(mainreciept.pendingamount))
                                    mainreciept.save()
                                    for i in remainingpaymentreciept:
                                        i.pendingamount = int(i.pendingamount) + int(diff)
                                        i.save()
                                else:
                                    print("not working")  
                                
                            semesterfees4.save()
                        except StudentFees.DoesNotExist:
                            addsemesterfees = StudentFees(student=student_id,studypattern="Annual",stream=stream_year, tutionfees=year_tution4,examinationfees=year_exam4,bookfees=year_book4,resittingfees=year_resitting4,entrancefees=year_entrance4,extrafees=year_extra4,discount=year_discount4,totalfees=year_total4,sem="4")
                            addsemesterfees.save()
                            print("added year 4 year 4")
                        
                        return JsonResponse({'added':'yes'})




                getoldstudentfees_enroll_id = request.POST.get('getoldstudentfees_enroll_id')
                if getoldstudentfees_enroll_id:
                    try:
                        getstudent = Student.objects.get(enrollment_id = getoldstudentfees_enroll_id)
                        getenroll = Enrolled.objects.get(student=getstudent.id)
                        stream = Stream.objects.get(id=getenroll.stream)
                        if getstudent:
                            try:
                                getoldstudentfees = StudentFees.objects.filter(student=getstudent.id)
                                getoldstudentfeescount = StudentFees.objects.filter(student=getstudent.id).count() 
                                getstudentfeesserializer = StudentFeesSerializer(getoldstudentfees,many=True)
                                return JsonResponse({'data':getstudentfeesserializer.data,'count':getoldstudentfeescount,'studypattern':getenroll.course_pattern,'sem':stream.sem,'student':getstudent.id})
                            except StudentFees.DoesNotExist:
                                print("no student fees found")
                    except Student.DoesNotExist:
                        print("no student Found")
                name = request.POST.get('name')
                if name:
                    getstudent = Student.objects.filter(Q(name = name) | Q(name__icontains = name)  | Q(email__icontains = name))
                    for i in getstudent:
                        enrolled = Enrolled.objects.get(student= i.id)
                        course = Course.objects.get(id=enrolled.course)
                        stream = Stream.objects.get(id = enrolled.stream)
                        paymentreciept = PaymentReciept.objects.filter(student=i.id)
                        payment_reciept_serializer = PaymentRecieptSerializer(paymentreciept,many=True)
                        obj = {
                            "name":i.name,
                            "email":i.email,
                            "mobile":i.mobile,
                            "enrollment_id":i.enrollment_id,
                            "course_pattern":enrolled.course_pattern,
                            "total_semyear":enrolled.total_semyear,
                            "current_semyear":enrolled.current_semyear,
                            "course":course.name,
                            "stream":stream.name,
                            "paymentreciept":payment_reciept_serializer.data
                        }
                        temp.append(obj)
                    return JsonResponse({'student_data':temp})

                course_id = request.POST.get('course_id')
                stream_id = request.POST.get('stream_id')
                if course_id and stream_id:
                    enroll = Enrolled.objects.filter(Q(course = course_id) & Q(stream = stream_id))
                    for i in enroll:
                        student = Student.objects.get(id=i.student)
                        enrolled = Enrolled.objects.get(student=student.id)
                        course = Course.objects.get(id=enrolled.course)
                        stream = Stream.objects.get(id = enrolled.stream)
                        paymentreciept = PaymentReciept.objects.filter(student=student.id)
                        payment_reciept_serializer = PaymentRecieptSerializer(paymentreciept,many=True)
                        obj = {
                            "name":student.name,
                            "email":student.email,
                            "mobile":student.mobile,
                            "enrollment_id":student.enrollment_id,
                            "course_pattern":enrolled.course_pattern,
                            "total_semyear":enrolled.total_semyear,
                            "current_semyear":enrolled.current_semyear,
                            "course":course.name,
                            "stream":stream.name,
                            "paymentreciept":payment_reciept_serializer.data
                        }
                        temp.append(obj)
                    return JsonResponse({'student_data':temp})
                
                courseid = request.POST.get('courseid')
                if courseid:
                    getcourse = Course.objects.get(id=courseid)
                    getstream = Stream.objects.filter(course=getcourse)
                    streamserializer = StreamSerializer(getstream,many=True)
                    return JsonResponse({'stream':streamserializer.data})

                enroll_id = request.POST.get('enroll_id')
                if enroll_id:
                    try:
                        checkstudent = Student.objects.get(Q(enrollment_id=enroll_id) | Q(mobile=enroll_id) | Q(email=enroll_id))
                        enrolled = Enrolled.objects.get(student= checkstudent.id)
                        course = Course.objects.get(id=enrolled.course)
                        stream = Stream.objects.get(id = enrolled.stream)
                        paymentreciept = PaymentReciept.objects.filter(student=checkstudent.id)
                        payment_reciept_serializer = PaymentRecieptSerializer(paymentreciept,many=True)
                        obj = {
                            "name":checkstudent.name,
                            "email":checkstudent.email,
                            "mobile":checkstudent.mobile,
                            "enrollment_id":checkstudent.enrollment_id,
                            "course_pattern":enrolled.course_pattern,
                            "total_semyear":enrolled.total_semyear,
                            "current_semyear":enrolled.current_semyear,
                            "course":course.name,
                            "stream":stream.name,
                            "paymentreciept":payment_reciept_serializer.data
                        }
                        temp.append(obj)
                    except Student.DoesNotExist:
                        pass
                    return JsonResponse({'student_data':temp})

    params = {
        "display":display,
        "level_of_user":level_of_user,
        "course":Course.objects.all()
    }
    return render(request,"editoldstudentfees.html",params)

@login_required(login_url='/login/') 
def ImportCsv(request):
    display = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            display = "yes"
        else:
            print("no")
    count = 0
    if request.method == "POST":
        doc = request.FILES['doc1']
        if doc:
            saveimportedfile = ImportCsvData(import_csv_data=doc)
            if saveimportedfile:
                saveimportedfile.save()
                getcsv = ImportCsvData.objects.latest('id')
                pathdata =str("media/") + str(getcsv.import_csv_data)
                with open(pathdata, 'r' ) as read_obj:
                    csv_dict_reader = DictReader(read_obj)
                    for row in csv_dict_reader:
                        firstname=row['firstname']
                        lastname = row['lastname']
                        email = row['email']
                        mobile = row['mobile']
                        enrollmentdate= row['enrollmentdate']
                        enrollmentid= row['enrollmentid']
                        address= row['address']
                        username= row['username']
                        password= row['password']
                        saveuser = User.objects.create_user(username= username,email=email, first_name=firstname,last_name = lastname,password=password)
                        if saveuser:
                            saveuser.save()
                        # savestudent = Student(firstname=firstname,lastname=lastname,email=email,mobile=mobile,enrollmentid=enrollmentid,enrollmentdate=enrollmentdate,address=address)
        
        
        
    params = {
        "display":display
    }
    return render(request,"importfromcsv.html",params)

def ULogin(request):
    showsignup = ""
    usercreated = ""
    usernamepresent = ''
    checkuser = ''
    loggedinuser = ''
    if request.user.is_authenticated:
        user_id = request.user.id
        loggedinuser = "yes"
    if request.method == "POST":
        usignup = request.POST.get('signup')
        if usignup == "signup":
            showsignup = "yes"
        else:
            showsignup = "no"
            
        Remail = request.POST.get('Remail')
        Rpassword = request.POST.get('Rpassword')
        if  Remail  and Rpassword:
            try:
                checkuser = User.objects.get(email=Remail)
                print("checkuser :",checkuser)
            except User.DoesNotExist:
                createuser = User.objects.create_user(email=Remail,password=Rpassword)
                createuser.save()
                usercreated = "yes"
            if checkuser:
                usernamepresent = "yes"
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email,password)
        authen = authenticate(email = email,password = password)
        print(authen)
        if authen:
            try:
                level = UserLevel.objects.get(user = authen.id)
                print(level)
            except UserLevel.DoesNotExist:
                checksuperuser = authen.is_superuser
                print(checksuperuser)
                if checksuperuser == True:        
                    createlevel = UserLevel(level='4',user=authen)
                    createlevel.save()
                else:
                    createlevel = UserLevel(level='1',user=authen)
                    createlevel.save()
            level = UserLevel.objects.get(user = authen.id)
            if level.level == "1":
                login(request,authen)
                print("yes loggeed in user 1")
                return redirect('profile')
                
            elif level.level == "2":
                login(request,authen)
                print("yes loggeed in user 2")
                return redirect('overview')
            
            elif level.level == "3":
                login(request,authen)
                print("yes loggeed in user 3")
                return redirect('profile')
            
            elif level.level == "4":
                login(request,authen)
                print("yes loggeed in user 4")
                return redirect('overview')
    
    params = {
        "signup":showsignup,
        "usernamepresent":usernamepresent,
        "usercreated":usercreated,
        "loggedinuser":loggedinuser
    }
    return render(request,'login.html',params)

def logout_page(request):
    logout(request)
    # return HttpResponseRedirect('login') 
    return HttpResponseRedirect(request.GET.get('next', '/login')) 

@login_required(login_url='/login/')
def AddCourse(request):
    display = ""
    level_of_user = ""
    main = []
    university = University.objects.all()
    for i in university:
        courses = Course.objects.filter(university = i.id)
        obj = {
            "university_name":i.university_name,
            "course_name":courses
        }
        main.append(obj)
    print("main : ",main)

    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4" or level.level =="2":
            display = "yes"
            level_of_user = level.level
        else:
            print("no")
    
    if request.method == "POST":
        add_coursename = request.POST.get('add_coursename')
        add_university = request.POST.get('add_university')
        importdata = request.FILES.get('importdata')
        if importdata:
            df=pd.read_excel(importdata,sheet_name='Sheet1')
            for i in df.index:
                course_name = df['courseName'][i]
                stream_name = df['streamName'][i]
                stream_duration = df['streamDurationYear'][i]
                

                try:
                    getcourse = Course.objects.get(name = course_name)
                except Course.DoesNotExist:
                    getcourse = Course(name=course_name)
                    getcourse.save()
                getcourse = Course.objects.get(name = course_name)
                try:
                    getstream = Stream.objects.get(Q(name = stream_name) & Q(course = getcourse))
                except Stream.DoesNotExist:
                    getstream = Stream(name = stream_name,course=getcourse,sem=stream_duration)
                    getstream.save()
                

        university_name = request.POST.get('university_name')
        if university_name:
            try:
                getuniversity = University.objects.get(university_name = university_name)
                getcourse = Course.objects.filter(university = getuniversity.id)
                course_list = []
                for i in getcourse:
                    courseserializer = {
                        "id":i.id,
                        "name":i.name
                    }
                    course_list.append(courseserializer)
                return JsonResponse({'course':course_list})
            except University.DoesNotExist:
                print("University does not exist")        


        update_course_id = request.POST.get('update_course_id')
        update_course_name = request.POST.get('update_course_name')            
        if update_course_id and update_course_name:
            updatecourse = Course.objects.get(id=update_course_id)
            if updatecourse.name == update_course_name:
                pass
            else:
                updatecourse.name = update_course_name
                updatecourse.save()
                return JsonResponse({'updated':'yes'})

        delete_course_id = request.POST.get('delete_course_id')
        if delete_course_id:
            deletecourse = Course.objects.get(id=delete_course_id)
            deletecourse.delete()
            deletestream = Stream.objects.filter(course=delete_course_id)
            deletestream.delete()
            return JsonResponse({'deleted':'yes'})

        if add_coursename and add_university != "Select University":
            addcourse = Course(name = add_coursename,university = add_university)
            addcourse.save()
            getlatestcourse = Course.objects.latest('id')
            allcoursecount = Course.objects.all().count()
            obj = {
                "id":getlatestcourse.id,
                "name":getlatestcourse.name,
                "count":allcoursecount
            }
            return JsonResponse({'course':obj})
        else:
            return JsonResponse({'course':'no','redirect':'yes'})
        
    params = {
        "main":main,
        "courses":Course.objects.all(),
        "university":University.objects.all(),
        "display":display,
        "level_of_user":level_of_user
    }
    return render(request,"addcourse.html",params)

@login_required(login_url='/login/')
def AddStream(request):
    display = ""
    level_of_user = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4" or level.level =="2":
            display = "yes"
            level_of_user = level.level
        else:
            print("no")
    cdata = ''
    special = ''
    allcourse = Course.objects.all()
    mainlist = []

    

    for i in allcourse:
        id = i.id
        
        coursename = i.name
        
        allstream = Stream.objects.filter(course=id)
        specializationlist = []
        for j in allstream:
            obj = {
                "type":j.name,
                "duration":j.sem
            }
            specializationlist.append(obj)
        main = {
            "id":i.id,
            "coursename":coursename,
            "specialization":specializationlist
        }
        mainlist.append(main)
        

    main = []
    university = University.objects.all()
    for i in university:
        courses = Course.objects.filter(university = i.id)
        obj = {
            "university_name":i.university_name,
            "course_name":courses
        }
        main.append(obj)
    
    if request.method == "POST":
        get_course = request.POST.get('get_course')
        if get_course:
            try:
                getcourse = Course.objects.filter(university = get_course)
                courseserializer = CourseSerializer(getcourse,many=True)
                return JsonResponse({'course':courseserializer.data})
            except Course.DoesNotExist:
                pass
        
        
        stream_delete_id = request.POST.get('stream_delete_id')
        if stream_delete_id:
            try:
                getdeletestream = Stream.objects.get(id=stream_delete_id)
                getdeletestream.delete()
                return JsonResponse({'deleted':'yes'})
            except Stream.DoesNotExist:
                pass

        streamchange = request.POST.get('streamchange')
        if streamchange:
            jsondata = json.loads(streamchange)
            data = jsondata['data']
            for i in data:
                stream_id = i['stream_id']
                stream_name = i['stream_name']
                try:
                    updatestream = Stream.objects.get(id=stream_id)
                    if updatestream.name == stream_name:
                        pass
                    else:
                        updatestream.name = stream_name
                        updatestream.save()
                except Stream.DoesNotExist:
                    print("stream not available")
            return JsonResponse({'updated':'yes'})
        

        university_name = request.POST.get('university_name')
        if university_name:
            try:
                getuniversity = University.objects.get(university_name = university_name)
                getcourse = Course.objects.filter(university = getuniversity.id)
                course_list = []
                for i in getcourse:
                    courseserializer = {
                        "id":i.id,
                        "name":i.name
                    }
                    course_list.append(courseserializer)
                return JsonResponse({'course':course_list})
            except University.DoesNotExist:
                print("University does not exist") 

        course_id = request.POST.get('course_id')
        if course_id:
            print(course_id)
            try:
                getcourse = Course.objects.get(id = course_id)
                getstream = Stream.objects.filter(course = getcourse.id)
                streamserializer = StreamSerializer(getstream,many=True)
                if len(getstream) != 0:
                    streamcount = len(getstream)
                    return JsonResponse({'data':streamserializer.data,'stream':'yes','streamcount':streamcount})
                else:
                    return JsonResponse({'data':streamserializer.data,'stream':'no'})
            except Course.DoesNotExist:
                print("no course")
        
        coursename = request.POST.get('add_selectcourse')
        specialization = request.POST.get('add_specialization')
        duration = request.POST.get('add_duration')
        
        if coursename and specialization:
            print("gotcoursename and specialization")
            getcourseid = Course.objects.get(id = coursename)
            save_specialization = Stream(name=specialization,course=getcourseid,sem=duration)
            save_specialization.save()
            return JsonResponse({'added':'yes'})
   
    params = {
        "maindata":main,
        "courses":Course.objects.all(),
        "university":University.objects.all(),
        "main":mainlist,
        "display":display,
        "level_of_user":level_of_user
    }
    return render(request,"stream.html",params)

@login_required(login_url='/login/')    
def AddStudent(request): 
    display = ""
    level_of_user = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4" or level.level =="2":
            display = "yes"
            user_id = request.user.id
            level_of_user = level.level
        else:
            print("no")
    roll= ''
    mobile_unique = ''
    get_course = request.GET.get('get_course')
    if get_course:
        try:
            getuniversity = University.objects.get(registrationID = get_course )
            getcourse = Course.objects.filter(university = getuniversity.id)
            if getcourse:
                courseserializer = CourseSerializer(getcourse,many=True)
                return JsonResponse({'course':courseserializer.data})
        except University.DoesNotExist:
            print("no university found")
    get_country_id = request.GET.get('get_country_id')
    if get_country_id:
        states = States.objects.filter( country_id = get_country_id )
        states_serializer = StatesSerializer(states,many=True)
        return JsonResponse({'states':states_serializer.data})

    get_cities_id = request.GET.get('get_cities_id')
    if get_cities_id:
        states = Cities.objects.filter( state_id = get_cities_id )
        states_serializer = CitiesSerializer(states,many=True)
        return JsonResponse({'cities':states_serializer.data})
    selected_course = request.GET.get('selected_course')
    print(selected_course)
    if selected_course:
        get_course_id = Course.objects.get(id = selected_course)
        get_specialization = Stream.objects.filter(course = get_course_id.id)
        serializer = StreamSerializer(get_specialization,many=True)
        return JsonResponse({'data':serializer.data})
    if request.method == "POST":
        
        xuniversity = request.POST.get('xuniversity')
        if xuniversity:
            print("university :",xuniversity)


        course_name = request.POST.get('course_name')
        stream_name = request.POST.get('stream_name')
        study_pattern = request.POST.get('study_pattern')
        
        student_image = request.FILES.get('student_image', False)
        name = request.POST.get('name')
        dob = request.POST.get('dateofbirth')
        fathername = request.POST.get('fathers_name')
        mothername = request.POST.get('mothers_name')
        email = request.POST.get('email')
        alternateemail = request.POST.get('alternateemail')
        mobile = request.POST.get('mobile')
        alternatemobile1 = request.POST.get('alternatemobile1')
        gender = request.POST.get('gender')
        category = request.POST.get('category')
       
        address = request.POST.get('address')
        alternateaddress = request.POST.get('alternateaddress')
        nationality = request.POST.get('nationality')
        country = request.POST.get('countryId')
        state = request.POST.get('stateId')
        city = request.POST.get('cityId')
        pincode = request.POST.get('Pincode')

        counselor_name = request.POST.get('counselor_name')
        reference_name = request.POST.get('reference_name')
        university_enrollment_number = request.POST.get('university_enrollment_number')
        student_remarks = request.POST.get('student_remarks')
        


        fees = request.POST.get('fees')
        total_fees = request.POST.get('total_fees')
        course = request.POST.get('course')
        streamID = request.POST.get('Stream')
        studypattern = request.POST.get('studypattern')
        semyear = request.POST.get('semyear')
        university = request.POST.get('university')
        session = request.POST.get('session')
        entry_mode = request.POST.get('entry_mode')

        discount = request.POST.get('discount')
        # Documents
        
        totaldocuments = request.POST.get('totaldocuments')
        document1 = request.POST.get('document1')
        DocumentName1 = request.POST.get('DocumentName1')
        DocumentID1 = request.POST.get('DocumentID1')
        DocumentFront1 = request.FILES.get('DocumentFront1', False)
        DocumentBack1 = request.FILES.get('DocumentBack1', False)

        document2 = request.POST.get('document2')
        DocumentName2 = request.POST.get('DocumentName2')
        DocumentID2 = request.POST.get('DocumentID2')
        DocumentFront2 = request.FILES.get('DocumentFront2', False)
        DocumentBack2 = request.FILES.get('DocumentBack2', False)
        
        document3 = request.POST.get('document3')
        DocumentName3 = request.POST.get('DocumentName3')
        DocumentID3 = request.POST.get('DocumentID3')
        DocumentFront3 = request.FILES.get('DocumentFront3', False)
        DocumentBack3 = request.FILES.get('DocumentBack3', False)
        
        document4 = request.POST.get('document4')
        DocumentName4 = request.POST.get('DocumentName4')
        DocumentID4 = request.POST.get('DocumentID4')
        DocumentFront4 = request.FILES.get('DocumentFront4', False)
        DocumentBack4 = request.FILES.get('DocumentBack4', False)
        
        document5 = request.POST.get('document5')
        DocumentName5 = request.POST.get('DocumentName5')
        DocumentID5 = request.POST.get('DocumentID5')
        DocumentFront5 = request.FILES.get('DocumentFront5', False)
        DocumentBack5 = request.FILES.get('DocumentBack5', False)
        
        
        
        

        
        # Qualifications
        secondary_year = request.POST.get('secondary_year')
        secondary_board = request.POST.get('secondary_board')
        secondary_percentage = request.POST.get('secondary_percentage')
        secondary_document = request.FILES.get('secondary_document', False)
        
        sr_year = request.POST.get('sr_year')
        sr_board = request.POST.get('sr_board')
        sr_percentage = request.POST.get('sr_percentage')
        sr_document = request.FILES.get('sr_document', False)
        
        under_year = request.POST.get('under_year')
        under_board = request.POST.get('under_board')
        under_percentage = request.POST.get('under_percentage')
        under_document = request.FILES.get('under_document', False)
        
        post_year = request.POST.get('post_year')
        post_board = request.POST.get('post_board')
        post_percentage = request.POST.get('post_percentage')
        post_document = request.FILES.get('post_document', False)
        
        mphil_year = request.POST.get('mphil_year')
        mphil_board = request.POST.get('mphil_board')
        mphil_percentage = request.POST.get('mphil_percentage')
        mphil_document = request.FILES.get('mphil_document', False)
        
        others_year = request.POST.get('other_year')
        others_board = request.POST.get('other_board')
        others_percentage = request.POST.get('other_percentage')
        others_document = request.FILES.get('other_document', False)


        fee_reciept_type = request.POST.get('fee_reciept_type')
        other_data = request.POST.get('other_data')
        transaction_date = request.POST.get('transaction_date')
        payment_mode = request.POST.get('payment_mode')
        cheque_no = request.POST.get('cheque_no')
        bank_name = request.POST.get('bank_name')
        other_bank = request.POST.get('other_bank')
        remarks = request.POST.get('remarks')
        random_number = request.POST.get('random_number')
        print("random number :",random_number)
        print(name, dob , fathername , mothername , email , mobile , gender , category ,  address , nationality , country , state , city , pincode)
        print(secondary_year , secondary_board , secondary_percentage , secondary_document , sr_year , sr_board , sr_percentage , sr_document , under_year , under_board , under_percentage , under_document , post_year , post_board , post_percentage , post_document , mphil_year , mphil_board , mphil_percentage , mphil_document , others_year , others_board , others_percentage , others_document)
        print(course , streamID , studypattern , semyear , session , university)
        print(fees , fee_reciept_type , other_data , transaction_date , payment_mode , cheque_no , bank_name , remarks)

        if payment_mode == "Cheque":
            payment_status = "Not Realised"
        else:
            payment_status = "Realised"
            
        
        if course_name and stream_name and study_pattern:
            print(course_name, stream_name , study_pattern)
            if study_pattern == "Semester":
                try:
                    getstream = Stream.objects.get(id=stream_name)
                    obj = {
                        "semyear":int(getstream.sem) * 2,
                        "study_pattern":"Semester"
                    }
                    print(obj)
                    return JsonResponse({'obj':obj})
                except Stream.DoesNotExist:
                    pass
            elif study_pattern == "Annual":
                try:
                    getstream = Stream.objects.get(id=stream_name)
                    obj = {
                        "semyear":int(getstream.sem),
                        "study_pattern":"Annual"
                    }
                    print(obj)
                    return JsonResponse({'obj':obj})
                except Stream.DoesNotExist:
                    pass

        get_c_id = request.POST.get('c_id')
        get_s_id = request.POST.get('s_id')
        get_studypattern = request.POST.get('studypattern')
        get_semyear = request.POST.get('semyear')
        if get_c_id and get_s_id and get_studypattern and get_semyear:
            if get_studypattern == "Semester":
                try:
                    getsemesterfees = SemesterFees.objects.get(Q(stream=get_s_id) & Q(sem = get_semyear))
                    getsemesterfeesserializer = SemesterFeesSerializer(getsemesterfees,many=False)
                    return JsonResponse({'data':getsemesterfeesserializer.data})
                except SemesterFees.DoesNotExist:
                    pass
            elif get_studypattern == "Annual":
                try:
                    getyearfees = YearFees.objects.get(Q(stream=get_s_id) & Q(year = get_semyear))
                    getyearfeesserializer = YearFeesSerializer(getyearfees,many=False)
                    return JsonResponse({'data':getyearfeesserializer.data})
                except YearFees.DoesNotExist:
                    pass
           

        
        email_unique = ''
        try:
            random = Student.objects.latest('id')
        except Student.DoesNotExist:
            random = 1
        if random==1:
            enroll = 50000
            registration_id = 250000
        else:
            enroll = int(random.enrollment_id)+ 1
            registration_id = int(random.registration_id) +1
        
        if mobile:
            print("mobile : ",mobile)
            try:
                check_mobile = Student.objects.get(mobile = mobile)
                print("check_mobile ; ",check_mobile)
                mobile_unique = "no"
            except Student.DoesNotExist:
                mobile_unique = "yes"
            print("mobile_unique ; ",mobile_unique)
        if email:
            try:
                check_email = Student.objects.get(email = email)
                email_unique = "no"
            except Student.DoesNotExist:
                email_unique = "yes"
        if mobile_unique == "no" or email_unique == "no":
            obj = {
                'mobile_unique':mobile_unique,
                'email_unique':email_unique
            }
            print("data :",obj)
            return JsonResponse({'data':obj})
        

        if mobile_unique == "yes" and email_unique == "yes":       
            if name or dob or fathername or mothername or email or mobile or gender or category  or address or nationality or country or state or city or pincode or (course and streamID and studypattern and semyear and session and entry_mode):
                create_student = Student(name=name,father_name=fathername,mother_name=mothername,dateofbirth=dob,mobile=mobile,alternate_mobile1=alternatemobile1,email=email,alternateemail=alternateemail,gender=gender,category=category,address=address,alternateaddress=alternateaddress,nationality=nationality,country=country,state=state,city=city,pincode=pincode,registration_id=registration_id,enrollment_id=enroll,image=student_image,verified=False,university=university,created_by=user_id,modified_by=user_id,student_remarks=student_remarks)
                create_student.save()
                print("student saved")
                print(name , dob , fathername , mothername , email , mobile , gender , category ,  address , nationality , country , state , city , pincode)
                print(secondary_year , secondary_board , secondary_percentage , secondary_document , sr_year , sr_board , sr_percentage , sr_document , under_year , under_board , under_percentage , under_document , post_year , post_board , post_percentage , post_document , mphil_year , mphil_board , mphil_percentage , mphil_document , others_year , others_board , others_percentage , others_document)
                print(course , streamID , studypattern , semyear , session , university)
                print(total_fees,fees , fee_reciept_type , other_data , transaction_date , payment_mode , cheque_no , bank_name , remarks)
                 
                # return JsonResponse({'added':'yes'})
                
                # print("Total Fees : ",total_fees)
                # print("Paid Fees : ",fees)
                # pendingfees = abs(int(total_fees) - int(fees))
                # print("Pending Fees : ",pendingfees)

                    
                
                
                    
                    
        
                latest_student = Student.objects.latest('id')
                archive_post = StudentArchive()
                for field in latest_student._meta.fields:
                    setattr(archive_post, field.name, getattr(latest_student, field.name))
                archive_post.pk = None
                archive_post.save()
                if course and streamID and studypattern and semyear and session and entry_mode:
                    try:
                        stream = Stream.objects.get(id = streamID)
                    except Stream.DoesNotExist:
                        pass
                    totalsem = ""
                    if studypattern == "Semester":
                        totalsem = int(stream.sem) * 2
                        add_enrollmentdetails = Enrolled(student=latest_student.id,course=course,stream=streamID,course_pattern=studypattern,session=session,entry_mode=entry_mode,total_semyear=totalsem,current_semyear=semyear)
                        add_enrollmentdetails.save()
                    elif studypattern == "Annual":
                        totalsem = int(stream.sem)
                        add_enrollmentdetails = Enrolled(student=latest_student.id,course=course,stream=streamID,course_pattern=studypattern,session=session,entry_mode=entry_mode,total_semyear=totalsem,current_semyear=semyear)
                        add_enrollmentdetails.save()
                    elif studypattern == "Full Course":
                        totalsem = int(stream.sem)
                        add_enrollmentdetails = Enrolled(student=latest_student.id,course=course,stream=streamID,course_pattern=studypattern,session=session,entry_mode=entry_mode,total_semyear=totalsem,current_semyear="1")
                        add_enrollmentdetails.save()
                    print("enrolled student")

                print(bank_name , other_bank)
                if document1 == "Select":
                    print("document not selected")
                else:
                    print(document1,DocumentName1,DocumentID1,DocumentFront1,DocumentBack1)
                    add_student_document = StudentDocuments(document=document1,document_name=DocumentName1,document_ID_no=DocumentID1,document_image_front= DocumentFront1,document_image_back = DocumentBack1,student=latest_student.id)
                    add_student_document.save()
                
                if document2:
                    print(document2,DocumentName2,DocumentID2,DocumentFront2,DocumentBack2)
                    add_student_document = StudentDocuments(document=document2,document_name=DocumentName2,document_ID_no=DocumentID2,document_image_front= DocumentFront2,document_image_back = DocumentBack2,student=latest_student.id)
                    add_student_document.save()
                
                if document3:
                    print(document3,DocumentName3,DocumentID3,DocumentFront3,DocumentBack3)
                    add_student_document = StudentDocuments(document=document3,document_name=DocumentName3,document_ID_no=DocumentID3,document_image_front= DocumentFront3,document_image_back = DocumentBack3,student=latest_student.id)
                    add_student_document.save()
                
                if document4:
                    print(document4,DocumentName4,DocumentID4,DocumentFront4,DocumentBack4)
                    add_student_document = StudentDocuments(document=document4,document_name=DocumentName4,document_ID_no=DocumentID4,document_image_front= DocumentFront4,document_image_back = DocumentBack4,student=latest_student.id)
                    add_student_document.save()
                
                if document5:
                    print(document5,DocumentName5,DocumentID5,DocumentFront5,DocumentBack5)
                    add_student_document = StudentDocuments(document=document5,document_name=DocumentName5,document_ID_no=DocumentID5,document_image_front= DocumentFront5,document_image_back = DocumentBack5,student=latest_student.id)
                    add_student_document.save()
                    
                

            
                add_additional_details = AdditionalEnrollmentDetails(counselor_name=counselor_name,reference_name=reference_name,university_enrollment_id=university_enrollment_number,student=latest_student.id)
                add_additional_details.save()

                if studypattern == "Semester":
                    try:
                        getsemesterfees = SemesterFees.objects.filter(stream=streamID)
                        for i in getsemesterfees:
                            addstudentfees = StudentFees(student = latest_student.id,studypattern="Semester",stream=streamID,tutionfees=i.tutionfees,examinationfees=i.examinationfees,bookfees=i.bookfees,resittingfees=i.resittingfees,entrancefees=i.entrancefees,extrafees=i.extrafees,discount=i.discount,totalfees=i.totalfees,sem=i.sem)
                            addstudentfees.save()
                    except SemesterFees.DoesNotExist:
                        pass
                elif studypattern == "Annual":
                    try:
                        print("Annual try reached")
                        getyearfees = YearFees.objects.filter(stream=streamID)
                        for i in getyearfees:
                            addstudentfees = StudentFees(student = latest_student.id,studypattern="Annual",stream=streamID,tutionfees=i.tutionfees,examinationfees=i.examinationfees,bookfees=i.bookfees,resittingfees=i.resittingfees,entrancefees=i.entrancefees,extrafees=i.extrafees,discount=i.discount,totalfees=i.totalfees,sem=i.year)
                            addstudentfees.save()
                    except YearFees.DoesNotExist:
                        print("annual not reached")
                
                if secondary_year or secondary_board or secondary_percentage or secondary_document or sr_year or sr_board or sr_percentage or sr_document or under_year or under_board or under_percentage or under_document or post_year or post_board or post_percentage or post_document or mphil_year or mphil_board or mphil_percentage or mphil_document or others_year or others_board or others_percentage or others_document:
                    setqualification = Qualification(student=latest_student.id,secondary_year = secondary_year,sr_year = sr_year,under_year=under_year,post_year=post_year,mphil_year=mphil_year,others_year = others_year,secondary_board=secondary_board,sr_board=sr_board,under_board=under_board,post_board=post_board,mphil_board=mphil_board,others_board=others_board,secondary_percentage=secondary_percentage,sr_percentage=sr_percentage,under_percentage=under_percentage,post_percentage=post_percentage,mphil_percentage=mphil_percentage,others_percentage=others_percentage,secondary_document=secondary_document,sr_document=sr_document,under_document=under_document,post_document=post_document,mphil_document=mphil_document,others_document=others_document)
                    setqualification.save()
                    print("qualification saved")
                
                try:
                    getlatestreciept = PaymentReciept.objects.latest('id')
                except PaymentReciept.DoesNotExist:
                    getlatestreciept = "none"
                if getlatestreciept == "none":
                    transactionID = "TXT445FE101"
                else:
                    tid = getlatestreciept.transactionID
                    tranx = tid.replace("TXT445FE",'')
                    transactionID =  str("TXT445FE") + str(int(tranx) + 1)
                if fee_reciept_type == "Others":
                    reciept_type = other_data
                else:
                    reciept_type = fee_reciept_type
                if payment_mode == "Cheque":
                    if studypattern == "Full Course":
                        if fees and fee_reciept_type and transaction_date and payment_mode:
                            pending_fees = int(total_fees) - int(fees)
                            if pending_fees > 0:
                                print("positive")
                                pending_amount = pending_fees
                                advance_amount = 0
                            elif pending_fees == 0:
                                print("no pending semyear clear")
                                pending_amount = 0
                                advance_amount = 0
                            elif pending_fees < 0:
                                print("negative hence advance payment")
                                pending_amount = 0
                                advance_amount = abs(pending_fees)
                            if pending_fees == 0 | pending_fees < 0:
                                paymenttype = "Full Payment"
                            else:
                                paymenttype = "Part Payment"
                            if bank_name == "Others":
                                add_payment_reciept = PaymentReciept(
                                    student = latest_student.id,
                                    payment_for="Course Fees",
                                    payment_categories = "New",
                                    payment_type=paymenttype,
                                    fee_reciept_type=reciept_type,
                                    transaction_date= transaction_date,
                                    cheque_no=cheque_no,
                                    bank_name=other_bank,
                                    semyearfees=total_fees,
                                    paidamount=0,
                                    pendingamount=total_fees,
                                    advanceamount = advance_amount,
                                    transactionID = transactionID,
                                    paymentmode=payment_mode,
                                    remarks=remarks,
                                    session=session,
                                    semyear="1",
                                    uncleared_amount=fees,
                                    status=payment_status)
                            else:
                                add_payment_reciept = PaymentReciept(
                                    student = latest_student.id,
                                    payment_for="Course Fees",
                                    payment_categories = "New",
                                    payment_type=paymenttype,
                                    fee_reciept_type=reciept_type,
                                    transaction_date= transaction_date,
                                    cheque_no=cheque_no,
                                    bank_name=bank_name,
                                    semyearfees=total_fees,
                                    paidamount=0,
                                    pendingamount=total_fees,
                                    advanceamount = advance_amount,
                                    transactionID = transactionID,
                                    paymentmode=payment_mode,
                                    remarks=remarks,
                                    session=session,
                                    semyear="1",
                                    uncleared_amount=fees,
                                    status=payment_status)
                                add_payment_reciept.save()
                    else:
                        if fees and fee_reciept_type and transaction_date and payment_mode:
                            pending_fees = int(total_fees) - int(fees)
                            if pending_fees > 0:
                                print("positive")
                                pending_amount = pending_fees
                                advance_amount = 0
                            elif pending_fees == 0:
                                print("no pending semyear clear")
                                pending_amount = 0
                                advance_amount = 0
                            elif pending_fees < 0:
                                print("negative hence advance payment")
                                pending_amount = 0
                                advance_amount = abs(pending_fees)
                                
                            if pending_fees == 0:
                                paymenttype = "Full Payment"
                            else:
                                paymenttype = "Part Payment"
                            if bank_name == "Others":
                                add_payment_reciept = PaymentReciept(
                                    student = latest_student.id,
                                    payment_for="Course Fees",
                                    payment_categories = "New",
                                    payment_type=paymenttype,
                                    fee_reciept_type=reciept_type,
                                    transaction_date= transaction_date,
                                    cheque_no=cheque_no,
                                    bank_name=other_bank,
                                    semyearfees=total_fees,
                                    paidamount=0,
                                    pendingamount=total_fees,
                                    advanceamount = advance_amount,
                                    transactionID = transactionID,
                                    paymentmode=payment_mode,
                                    remarks=remarks,
                                    session=session,
                                    semyear=semyear,
                                    uncleared_amount=fees,
                                    status=payment_status)
                                add_payment_reciept.save()
                            else:
                                add_payment_reciept = PaymentReciept(
                                    student = latest_student.id,
                                    payment_for="Course Fees",
                                    payment_categories = "New",
                                    payment_type=paymenttype,
                                    fee_reciept_type=reciept_type,
                                    transaction_date= transaction_date,
                                    cheque_no=cheque_no,
                                    bank_name=bank_name,
                                    semyearfees=total_fees,
                                    paidamount=0,
                                    pendingamount=total_fees,
                                    advanceamount = advance_amount,
                                    transactionID = transactionID,
                                    paymentmode=payment_mode,
                                    remarks=remarks,
                                    session=session,
                                    semyear=semyear,
                                    uncleared_amount=fees,
                                    status=payment_status)
                                add_payment_reciept.save()
                else:
                    if studypattern == "Full Course":
                        if fees and fee_reciept_type and transaction_date and payment_mode:
                            pending_fees = int(total_fees) - int(fees)
                            if pending_fees > 0:
                                print("positive")
                                pending_amount = pending_fees
                                advance_amount = 0
                            elif pending_fees == 0:
                                print("no pending semyear clear")
                                pending_amount = 0
                                advance_amount = 0
                            elif pending_fees < 0:
                                print("negative hence advance payment")
                                pending_amount = 0
                                advance_amount = abs(pending_fees)
                            if pending_fees == 0 | pending_fees < 0:
                                paymenttype = "Full Payment"
                            else:
                                paymenttype = "Part Payment"
                            if bank_name == "Others":
                                add_payment_reciept = PaymentReciept(
                                    student = latest_student.id,
                                    payment_for="Course Fees",
                                    payment_categories = "New",
                                    payment_type=paymenttype,
                                    fee_reciept_type=reciept_type,
                                    transaction_date= transaction_date,
                                    cheque_no=cheque_no,
                                    bank_name=other_bank,
                                    semyearfees=total_fees,
                                    paidamount=fees,
                                    pendingamount=pending_amount,
                                    advanceamount = advance_amount,
                                    transactionID = transactionID,
                                    paymentmode=payment_mode,
                                    remarks=remarks,
                                    session=session,
                                    semyear="1",
                                    status=payment_status)
                            else:
                                add_payment_reciept = PaymentReciept(
                                    student = latest_student.id,
                                    payment_for="Course Fees",
                                    payment_categories = "New",
                                    payment_type=paymenttype,
                                    fee_reciept_type=reciept_type,
                                    transaction_date= transaction_date,
                                    cheque_no=cheque_no,
                                    bank_name=bank_name,
                                    semyearfees=total_fees,
                                    paidamount=fees,
                                    pendingamount=pending_amount,
                                    advanceamount = advance_amount,
                                    transactionID = transactionID,
                                    paymentmode=payment_mode,
                                    remarks=remarks,
                                    session=session,
                                    semyear="1",
                                    status=payment_status)
                                add_payment_reciept.save()
                    else:
                        if fees and fee_reciept_type and transaction_date and payment_mode:
                            pending_fees = int(total_fees) - int(fees)
                            if pending_fees > 0:
                                print("positive")
                                pending_amount = pending_fees
                                advance_amount = 0
                            elif pending_fees == 0:
                                print("no pending semyear clear")
                                pending_amount = 0
                                advance_amount = 0
                            elif pending_fees < 0:
                                print("negative hence advance payment")
                                pending_amount = 0
                                advance_amount = abs(pending_fees)
                                
                            if pending_fees == 0:
                                paymenttype = "Full Payment"
                            else:
                                paymenttype = "Part Payment"
                            if bank_name == "Others":
                                add_payment_reciept = PaymentReciept(
                                    student = latest_student.id,
                                    payment_for="Course Fees",
                                    payment_categories = "New",
                                    payment_type=paymenttype,
                                    fee_reciept_type=reciept_type,
                                    transaction_date= transaction_date,
                                    cheque_no=cheque_no,
                                    bank_name=other_bank,
                                    semyearfees=total_fees,
                                    paidamount=fees,
                                    pendingamount=pending_amount,
                                    advanceamount = advance_amount,
                                    transactionID = transactionID,
                                    paymentmode=payment_mode,
                                    remarks=remarks,
                                    session=session,
                                    semyear=semyear,
                                    status=payment_status)
                                add_payment_reciept.save()
                            else:
                                add_payment_reciept = PaymentReciept(
                                    student = latest_student.id,
                                    payment_for="Course Fees",
                                    payment_categories = "New",
                                    payment_type=paymenttype,
                                    fee_reciept_type=reciept_type,
                                    transaction_date= transaction_date,
                                    cheque_no=cheque_no,
                                    bank_name=bank_name,
                                    semyearfees=total_fees,
                                    paidamount=fees,
                                    pendingamount=pending_amount,
                                    advanceamount = advance_amount,
                                    transactionID = transactionID,
                                    paymentmode=payment_mode,
                                    remarks=remarks,
                                    session=session,
                                    semyear=semyear,
                                    status=payment_status)
                                add_payment_reciept.save()


            
                return JsonResponse({'added':'yes'})
        

        
 
    params = {
        "university":University.objects.all(),
        "display":display,
        "level_of_user":level_of_user,
        "mobile_unique":mobile_unique,
        "countries":Countries.objects.all()
    }
    return render(request,"addstudent.html",params)

@login_required(login_url='/login/')    
def AddStudentQuick(request):
    display = ""
    level_of_user=""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4" or level.level =="2":
            user_id = request.user.id
            display = "yes"
            level_of_user = level.level
    if request.method == "POST":
        xuniversity = request.POST.get('xuniversity')
        if xuniversity:
            print("university :",xuniversity)



        
        university = request.POST.get('university')
        student_image = request.FILES.get('student_image', False)
        name = request.POST.get('name')
        father_name = request.POST.get('father_name')
        dob = request.POST.get('dateofbirth')
        
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        counselor_name = request.POST.get('counselor_name')
        university_enrollment_number = request.POST.get('university_enrollment_number')
        student_remarks = request.POST.get('student_remarks')

        fees = request.POST.get('fees')
        total_fees = request.POST.get('total_fees')
        course = request.POST.get('course')
        streamID = request.POST.get('Stream')
        studypattern = request.POST.get('studypattern')
        semyear = request.POST.get('semyear')
        session = request.POST.get('session')
        entry_mode = request.POST.get('entry_mode')

        

        fee_reciept_type = request.POST.get('fee_reciept_type')
        other_data = request.POST.get('other_data')
        transaction_date = request.POST.get('transaction_date')
        payment_mode = request.POST.get('payment_mode')
        cheque_no = request.POST.get('cheque_no')
        bank_name = request.POST.get('bank_name')
        other_bank = request.POST.get('other_bank')
        remarks = request.POST.get('remarks')
        random_number = request.POST.get('random_number')
        print("random number :",random_number)
        print( university , student_image , name ,dob  , email , mobile ,university_enrollment_number , student_remarks )
        print(course , streamID , studypattern , semyear , session , entry_mode)
        print(fees , fee_reciept_type , other_data , transaction_date , payment_mode , cheque_no , bank_name , remarks)

        
        
        

        
           

        
        email_unique = ''
        try:
            random = Student.objects.latest('id')
        except Student.DoesNotExist:
            random = 1
        if random==1:
            enroll = 50000
            registration_id = 250000
        else:
            enroll = int(random.enrollment_id)+ 1
            registration_id = int(random.registration_id) +1
        
        if mobile:
            print("mobile : ",mobile)
            try:
                check_mobile = Student.objects.get(Q(mobile = mobile) | Q(alternate_mobile1 = mobile))
                print("check_mobile ; ",check_mobile)
                mobile_unique = "no"
            except Student.DoesNotExist:
                mobile_unique = "yes"
            print("mobile_unique ; ",mobile_unique)
        if email:
            try:
                check_email = Student.objects.get(email = email)
                email_unique = "no"
            except Student.DoesNotExist:
                email_unique = "yes"
        if mobile_unique == "no" or email_unique == "no":
            obj = {
                'mobile_unique':mobile_unique,
                'email_unique':email_unique
            }
            print("data :",obj)
            return JsonResponse({'data':obj})
        

        if mobile_unique == "yes" and email_unique == "yes":
            if name or dob  or email or mobile  or (course and streamID and studypattern and semyear and session and entry_mode):
                create_student = Student(name=name,father_name=father_name,dateofbirth=dob,mobile=mobile,email=email,registration_id=registration_id,enrollment_id=enroll,image=student_image,verified=False,university=university,created_by=user_id,modified_by=user_id,student_remarks=student_remarks)
                create_student.save()
                print("student saved")
                print(name ,father_name, dob , email , mobile )
                
                print(course , streamID , studypattern , semyear , session , university)
                print(fees , fee_reciept_type , other_data , transaction_date , payment_mode , cheque_no , bank_name , remarks)
                 
                if payment_mode == "Cheque":
                    payment_status = "Not Realised"
                    uncleared_amount = fees
                    paidfees = 0
                else:
                    payment_status = "Realised"
                    uncleared_amount = 0
                    paidfees = fees
                
                
                    
                    
                
                    
                    
        
                latest_student = Student.objects.latest('id')
                if course and streamID and studypattern and semyear and session and entry_mode:
                    try:
                        stream = Stream.objects.get(id = streamID)
                    except Stream.DoesNotExist:
                        pass
                    totalsem = ""
                    if studypattern == "Semester":
                        totalsem = int(stream.sem) * 2
                        add_enrollmentdetails = Enrolled(student=latest_student.id,course=course,stream=streamID,course_pattern=studypattern,session=session,entry_mode=entry_mode,total_semyear=totalsem,current_semyear=semyear)
                        add_enrollmentdetails.save()
                    elif studypattern == "Annual":
                        totalsem = int(stream.sem)
                        add_enrollmentdetails = Enrolled(student=latest_student.id,course=course,stream=streamID,course_pattern=studypattern,session=session,entry_mode=entry_mode,total_semyear=totalsem,current_semyear=semyear)
                        add_enrollmentdetails.save()
                    elif studypattern == "Full Course":
                        totalsem = int(stream.sem)
                        add_enrollmentdetails = Enrolled(student=latest_student.id,course=course,stream=streamID,course_pattern=studypattern,session=session,entry_mode=entry_mode,total_semyear=totalsem,current_semyear="1")
                        add_enrollmentdetails.save()
                    print("enrolled student")

                print(bank_name , other_bank)
                
                    
                

            
                add_additional_details = AdditionalEnrollmentDetails(student=latest_student.id,counselor_name=counselor_name,university_enrollment_id=university_enrollment_number)
                add_additional_details.save()

                if studypattern == "Semester":
                    try:
                        getsemesterfees = SemesterFees.objects.filter(stream=streamID)
                        for i in getsemesterfees:
                            addstudentfees = StudentFees(student = latest_student.id,studypattern="Semester",stream=streamID,tutionfees=i.tutionfees,examinationfees=i.examinationfees,bookfees=i.bookfees,resittingfees=i.resittingfees,entrancefees=i.entrancefees,extrafees=i.extrafees,discount=i.discount,totalfees=i.totalfees,sem=i.sem)
                            addstudentfees.save()
                    except SemesterFees.DoesNotExist:
                        pass
                elif studypattern == "Annual":
                    try:
                        print("Annual try reached")
                        getyearfees = YearFees.objects.filter(stream=streamID)
                        for i in getyearfees:
                            addstudentfees = StudentFees(student = latest_student.id,studypattern="Annual",stream=streamID,tutionfees=i.tutionfees,examinationfees=i.examinationfees,bookfees=i.bookfees,resittingfees=i.resittingfees,entrancefees=i.entrancefees,extrafees=i.extrafees,discount=i.discount,totalfees=i.totalfees,sem=i.year)
                            addstudentfees.save()
                    except YearFees.DoesNotExist:
                        print("annual not reached")

                
                
                
        
                
                try:
                    getlatestreciept = PaymentReciept.objects.latest('id')
                except PaymentReciept.DoesNotExist:
                    getlatestreciept = "none"
                if getlatestreciept == "none":
                    transactionID = "TXT445FE101"
                else:
                    tid = getlatestreciept.transactionID
                    tranx = tid.replace("TXT445FE",'')
                    transactionID =  str("TXT445FE") + str(int(tranx) + 1)
                if fee_reciept_type == "Others":
                    reciept_type = other_data
                else:
                    reciept_type = fee_reciept_type
                if payment_mode == "Cheque":
                    if studypattern == "Full Course":
                        if fees and fee_reciept_type and transaction_date and payment_mode:
                            pending_fees = int(total_fees) - int(fees)
                            if pending_fees > 0:
                                print("positive")
                                pending_amount = pending_fees
                                advance_amount = 0
                            elif pending_fees == 0:
                                print("no pending semyear clear")
                                pending_amount = 0
                                advance_amount = 0
                            elif pending_fees < 0:
                                print("negative hence advance payment")
                                pending_amount = 0
                                advance_amount = abs(pending_fees)
                            if pending_fees == 0 | pending_fees < 0:
                                paymenttype = "Full Payment"
                            else:
                                paymenttype = "Part Payment"
                            if bank_name == "Others":
                                add_payment_reciept = PaymentReciept(
                                    student = latest_student.id,
                                    payment_for="Course Fees",
                                    payment_categories = "New",
                                    payment_type=paymenttype,
                                    fee_reciept_type=reciept_type,
                                    transaction_date= transaction_date,
                                    cheque_no=cheque_no,
                                    bank_name=other_bank,
                                    semyearfees=total_fees,
                                    paidamount=0,
                                    pendingamount=total_fees,
                                    advanceamount = advance_amount,
                                    transactionID = transactionID,
                                    paymentmode=payment_mode,
                                    remarks=remarks,
                                    session=session,
                                    semyear="1",
                                    uncleared_amount=fees,
                                    status=payment_status)
                                add_payment_reciept.save()
                            else:
                                add_payment_reciept = PaymentReciept(
                                    student = latest_student.id,
                                    payment_for="Course Fees",
                                    payment_categories = "New",
                                    payment_type=paymenttype,
                                    fee_reciept_type=reciept_type,
                                    transaction_date= transaction_date,
                                    cheque_no=cheque_no,
                                    bank_name=bank_name,
                                    semyearfees=total_fees,
                                    paidamount=0,
                                    pendingamount=total_fees,
                                    advanceamount = advance_amount,
                                    transactionID = transactionID,
                                    paymentmode=payment_mode,
                                    remarks=remarks,
                                    session=session,
                                    semyear="1",
                                    uncleared_amount=fees,
                                    status=payment_status)
                                add_payment_reciept.save()
                    else:
                        if fees and fee_reciept_type and transaction_date and payment_mode:
                            pending_fees = int(total_fees) - int(fees)
                            if pending_fees > 0:
                                print("positive")
                                pending_amount = pending_fees
                                advance_amount = 0
                            elif pending_fees == 0:
                                print("no pending semyear clear")
                                pending_amount = 0
                                advance_amount = 0
                            elif pending_fees < 0:
                                print("negative hence advance payment")
                                pending_amount = 0
                                advance_amount = abs(pending_fees)
                                
                            if pending_fees == 0:
                                paymenttype = "Full Payment"
                            else:
                                paymenttype = "Part Payment"
                            if bank_name == "Others":
                                add_payment_reciept = PaymentReciept(
                                    student = latest_student.id,
                                    payment_for="Course Fees",
                                    payment_categories = "New",
                                    payment_type=paymenttype,
                                    fee_reciept_type=reciept_type,
                                    transaction_date= transaction_date,
                                    cheque_no=cheque_no,
                                    bank_name=other_bank,
                                    semyearfees=total_fees,
                                    paidamount=0,
                                    pendingamount=total_fees,
                                    advanceamount = advance_amount,
                                    transactionID = transactionID,
                                    paymentmode=payment_mode,
                                    remarks=remarks,
                                    session=session,
                                    semyear=semyear,
                                    uncleared_amount=fees,
                                    status=payment_status)
                                add_payment_reciept.save()
                            else:
                                add_payment_reciept = PaymentReciept(
                                    student = latest_student.id,
                                    payment_for="Course Fees",
                                    payment_categories = "New",
                                    payment_type=paymenttype,
                                    fee_reciept_type=reciept_type,
                                    transaction_date= transaction_date,
                                    cheque_no=cheque_no,
                                    bank_name=bank_name,
                                    semyearfees=total_fees,
                                    paidamount=0,
                                    pendingamount=total_fees,
                                    advanceamount = advance_amount,
                                    transactionID = transactionID,
                                    paymentmode=payment_mode,
                                    remarks=remarks,
                                    session=session,
                                    semyear=semyear,
                                    uncleared_amount=fees,
                                    status=payment_status)
                                add_payment_reciept.save()
                else:
                    if studypattern == "Full Course":
                        if fees and fee_reciept_type and transaction_date and payment_mode:
                            pending_fees = int(total_fees) - int(fees)
                            if pending_fees > 0:
                                print("positive")
                                pending_amount = pending_fees
                                advance_amount = 0
                            elif pending_fees == 0:
                                print("no pending semyear clear")
                                pending_amount = 0
                                advance_amount = 0
                            elif pending_fees < 0:
                                print("negative hence advance payment")
                                pending_amount = 0
                                advance_amount = abs(pending_fees)
                            if pending_fees == 0 | pending_fees < 0:
                                paymenttype = "Full Payment"
                            else:
                                paymenttype = "Part Payment"
                            if bank_name == "Others":
                                add_payment_reciept = PaymentReciept(
                                    student = latest_student.id,
                                    payment_for="Course Fees",
                                    payment_categories = "New",
                                    payment_type=paymenttype,
                                    fee_reciept_type=reciept_type,
                                    transaction_date= transaction_date,
                                    cheque_no=cheque_no,
                                    bank_name=other_bank,
                                    semyearfees=total_fees,
                                    paidamount=fees,
                                    pendingamount=pending_amount,
                                    advanceamount = advance_amount,
                                    transactionID = transactionID,
                                    paymentmode=payment_mode,
                                    remarks=remarks,
                                    session=session,
                                    semyear="1",
                                    status=payment_status)
                                add_payment_reciept.save()
                            else:
                                add_payment_reciept = PaymentReciept(
                                    student = latest_student.id,
                                    payment_for="Course Fees",
                                    payment_categories = "New",
                                    payment_type=paymenttype,
                                    fee_reciept_type=reciept_type,
                                    transaction_date= transaction_date,
                                    cheque_no=cheque_no,
                                    bank_name=bank_name,
                                    semyearfees=total_fees,
                                    paidamount=fees,
                                    pendingamount=pending_amount,
                                    advanceamount = advance_amount,
                                    transactionID = transactionID,
                                    paymentmode=payment_mode,
                                    remarks=remarks,
                                    session=session,
                                    semyear="1",
                                    status=payment_status)
                                add_payment_reciept.save()
                    else:
                        if fees and fee_reciept_type and transaction_date and payment_mode:
                            pending_fees = int(total_fees) - int(fees)
                            if pending_fees > 0:
                                print("positive")
                                pending_amount = pending_fees
                                advance_amount = 0
                            elif pending_fees == 0:
                                print("no pending semyear clear")
                                pending_amount = 0
                                advance_amount = 0
                            elif pending_fees < 0:
                                print("negative hence advance payment")
                                pending_amount = 0
                                advance_amount = abs(pending_fees)
                                
                            if pending_fees == 0:
                                paymenttype = "Full Payment"
                            else:
                                paymenttype = "Part Payment"
                            if bank_name == "Others":
                                add_payment_reciept = PaymentReciept(
                                    student = latest_student.id,
                                    payment_for="Course Fees",
                                    payment_categories = "New",
                                    payment_type=paymenttype,
                                    fee_reciept_type=reciept_type,
                                    transaction_date= transaction_date,
                                    cheque_no=cheque_no,
                                    bank_name=other_bank,
                                    semyearfees=total_fees,
                                    paidamount=fees,
                                    pendingamount=pending_amount,
                                    advanceamount = advance_amount,
                                    transactionID = transactionID,
                                    paymentmode=payment_mode,
                                    remarks=remarks,
                                    session=session,
                                    semyear=semyear,
                                    status=payment_status)
                                add_payment_reciept.save()
                            else:
                                add_payment_reciept = PaymentReciept(
                                    student = latest_student.id,
                                    payment_for="Course Fees",
                                    payment_categories = "New",
                                    payment_type=paymenttype,
                                    fee_reciept_type=reciept_type,
                                    transaction_date= transaction_date,
                                    cheque_no=cheque_no,
                                    bank_name=bank_name,
                                    semyearfees=total_fees,
                                    paidamount=fees,
                                    pendingamount=pending_amount,
                                    advanceamount = advance_amount,
                                    transactionID = transactionID,
                                    paymentmode=payment_mode,
                                    remarks=remarks,
                                    session=session,
                                    semyear=semyear,
                                    status=payment_status)
                                add_payment_reciept.save()
                            


            
                return JsonResponse({'added':'yes'})
    params = {
        "display":display,
        "level_of_user":level_of_user,
        "university":University.objects.all()
    }
    return render(request,"quick_addstudent.html",params)

@login_required(login_url='/login/')
def CancelledStudent(request):
    display = ""
    level_of_user=""
    students = []
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4" or level.level =="2":
            display = "yes"
            level_of_user = level.level
            if request.method == "POST":
                student_active_id = request.POST.get('student_id')
                if student_active_id:
                    print("Active student",student_active_id)
                    getstudent = Student.objects.get(id = student_active_id)
                    getstudent.is_cancelled = False
                    getstudent.archive = False
                    getstudent.enrolled = True
                    getstudent.save()
                    return JsonResponse({'success':'yes'})
            allstudents = Student.objects.filter(Q(is_cancelled = True))
            for i in allstudents:
                student_id = i.id
                enrolled = Enrolled.objects.get(student = student_id)
                course = Course.objects.get(id = enrolled.course)
                stream = Stream.objects.get(id = enrolled.stream)
                university = University.objects.get(registrationID = i.university)
                # datetimedata = datetime.strptime(str(i.enrollment_date), '%Y-%m-%d').strftime('%d-%m-%Y')
                # print(i.name,datetimedata)
                obj = {
                    "id":i.id,
                    "name":str(i.name),
                    "father_name":i.father_name,
                    "mother_name":i.mother_name,
                    "dateofbirth":datetime.strptime(str(i.dateofbirth), '%Y-%m-%d').strftime('%d-%m-%Y'),
                    "mobile":i.mobile,
                    "email":i.email,
                    "gender":i.gender,
                    "category":i.category,
                    "enrollment_id":i.enrollment_id,
                    "enrollment_date":datetime.strptime(str(i.enrollment_date), '%Y-%m-%d').strftime('%d-%m-%Y'),
                    "registration_id":i.registration_id,
                    "course_name":course.name,
                    "stream_name":stream.name,
                    "course_pattern":enrolled.course_pattern,
                    "current_semester":enrolled.current_semyear,
                    "session":enrolled.session,
                    'entry_mode':enrolled.entry_mode,
                    'university':university.university_name
                }
                students.append(obj)

            
    params = {
        "display":display,
        "level_of_user":level_of_user,
        "students":students
    }
    return render(request,"cancelled_students.html",params)


@login_required(login_url='/login/')
def EditStudent(request,enroll_id):
    display = ""
    level_of_user = ""
    found_student = ""
    student = []
    selected_course = request.GET.get('selected_course')
    
    print(selected_course)
    if selected_course:
        get_course_id = Course.objects.get(id = selected_course)
        get_specialization = Stream.objects.filter(course = get_course_id.id)
        serializer = StreamSerializer(get_specialization,many=True)
        return JsonResponse({'data':serializer.data})
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4" or level.level =="2":
            display = "yes"
            level_of_user = level.level
            if request.method == "POST":
                student_image = request.FILES.get('student_image', False)
                name = request.POST.get('name')
                dob = request.POST.get('dateofbirth')
                fathername = request.POST.get('fathers_name')
                mothername = request.POST.get('mothers_name')
                email = request.POST.get('email')
                alternateemail = request.POST.get('alternateemail')
                mobile = request.POST.get('mobile')
                alternatemobile1 = request.POST.get('alternatemobile1')
                gender = request.POST.get('gender')
                category = request.POST.get('category')
                address = request.POST.get('address')
                alternateaddress = request.POST.get('alternateaddress')
                nationality = request.POST.get('nationality')
                country = request.POST.get('country')
                state = request.POST.get('stateId')
                city = request.POST.get('cityId')
                pincode = request.POST.get('Pincode')
                student_remarks = request.POST.get('student_remarks')
                counselor_name = request.POST.get('counselor_name')
                reference_name = request.POST.get('reference_name')
                university_enrollment_number = request.POST.get('university_enrollment_number')
                
                course = request.POST.get('course')
                streamID = request.POST.get('Stream')
                studypattern = request.POST.get('studypattern')
                semyear = request.POST.get('semyear')
                university = request.POST.get('university')
                session = request.POST.get('session')
                entry_mode = request.POST.get('entry_mode')


                
                totaldocuments = request.POST.get('totaldocuments')
                document1 = request.POST.get('document1')
                DocumentName1 = request.POST.get('DocumentName1')
                DocumentID1 = request.POST.get('DocumentID1')
                DocumentUpload1 = request.FILES.getlist('DocumentUpload1')

                document2 = request.POST.get('document2')
                DocumentName2 = request.POST.get('DocumentName2')
                DocumentID2 = request.POST.get('DocumentID2')
                DocumentUpload2 = request.FILES.getlist('DocumentUpload2')

                document3 = request.POST.get('document3')
                DocumentName3 = request.POST.get('DocumentName3')
                DocumentID3 = request.POST.get('DocumentID3')
                DocumentUpload3 = request.FILES.getlist('DocumentUpload3')

                document4 = request.POST.get('document4')
                DocumentName4 = request.POST.get('DocumentName4')
                DocumentID4 = request.POST.get('DocumentID4')
                DocumentUpload4 = request.FILES.getlist('DocumentUpload4')
                
                # print("totaldocuments :",totaldocuments)
                # print("document1 :",document1)
                # print("DocumentName1 :",DocumentName1)
                # print("DocumentID1 :",DocumentID1)
                # print("___________________")
                # for i in DocumentUpload1:
                #     print(i)
                #     print(type(i))

                # print("document2 :",document2)
                # print("DocumentName2 :",DocumentName2)
                # print("DocumentID2 :",DocumentID2)
                # for i in DocumentUpload2:
                #     print(i)
                #     print(type(i))

                # print("document3 :",document3)
                # print("DocumentName3 :",DocumentName3)
                # print("DocumentID3 :",DocumentID3)
                # for i in DocumentUpload3:
                #     print(i)
                #     print(type(i))

                # print("document4 :",document4)
                # print("DocumentName4 :",DocumentName4)
                # print("DocumentID4 :",DocumentID4)
                # for i in DocumentUpload4:
                #     print(i)
                #     print(type(i))
                
                
                
                # Qualifications
                secondary_year = request.POST.get('secondary_year')
                secondary_board = request.POST.get('secondary_board')
                secondary_percentage = request.POST.get('secondary_percentage')
                secondary_document = request.FILES.get('secondary_document', False)
                
                sr_year = request.POST.get('sr_year')
                sr_board = request.POST.get('sr_board')
                sr_percentage = request.POST.get('sr_percentage')
                sr_document = request.FILES.get('sr_document', False)
                
                under_year = request.POST.get('under_year')
                under_board = request.POST.get('under_board')
                under_percentage = request.POST.get('under_percentage')
                under_document = request.FILES.get('under_document', False)
                
                post_year = request.POST.get('post_year')
                post_board = request.POST.get('post_board')
                post_percentage = request.POST.get('post_percentage')
                post_document = request.FILES.get('post_document', False)
                
                mphil_year = request.POST.get('mphil_year')
                mphil_board = request.POST.get('mphil_board')
                mphil_percentage = request.POST.get('mphil_percentage')
                mphil_document = request.FILES.get('mphil_document', False)
                
                others_year = request.POST.get('other_year')
                others_board = request.POST.get('other_board')
                others_percentage = request.POST.get('other_percentage')
                others_document = request.FILES.get('other_document', False)
                print(country , state , city , pincode)
                # print(firstname , middlename , lastname , dob , fathername , mothername , email , mobile , gender , category , idtype , idnumber , address , nationality , country , state , city , pincode)
                # print(secondary_year , secondary_board , secondary_percentage , secondary_document , sr_year , sr_board , sr_percentage , sr_document , under_year , under_board , under_percentage , under_document , post_year , post_board , post_percentage , post_document , mphil_year , mphil_board , mphil_percentage , mphil_document , others_year , others_board , others_percentage , others_document)
                # print(course , streamID , studypattern , semyear , session , entry_mode , university)
                # print(counselor_name , reference_name , university_enrollment_number)
                if name or dob or fathername or mothername or email or mobile or gender or category  or address or nationality or country or state or city or pincode:
                    try:
                        getstudent = Student.objects.get(enrollment_id = enroll_id)
                        
                        if getstudent.email == email  or email == "None":
                            print("same email")
                        else:
                            try:
                                match = Student.objects.get(Q(email = email) | Q(alternateemail = email))
                                return JsonResponse({'match':'email','enroll_id':enroll_id})
                            except Student.DoesNotExist:
                                pass
                        
                        if getstudent.alternateemail == alternateemail or alternateaddress == "None":
                            print("same alternateemail")
                        else:
                            try:
                                match = Student.objects.get(Q(email = alternateemail) | Q(alternateemail = alternateemail))
                                return JsonResponse({'match':'alternateemail','enroll_id':enroll_id})
                            except Student.DoesNotExist:
                                pass
                        
                        if getstudent.mobile == mobile or mobile == "None":
                            print("same mobile")
                        else:
                            try:
                                match = Student.objects.get(Q(mobile = mobile) | Q(alternate_mobile1 = mobile))
                                return JsonResponse({'match':'mobile','enroll_id':enroll_id})
                            except Student.DoesNotExist:
                                pass
                        
                        if getstudent.alternate_mobile1 == alternatemobile1 or alternatemobile1 == "None":
                            print("same alternatemobile")
                        else:
                            try:
                                match = Student.objects.get(Q(mobile = alternatemobile1) | Q(alternate_mobile1 = alternatemobile1))
                                return JsonResponse({'match':'alternatemobile','enroll_id':enroll_id})
                            except Student.DoesNotExist:
                                pass
                        
                        

                        print("student found")
                        getstudent.name = name
                        getstudent.dateofbirth = dob
                        getstudent.father_name = fathername
                        getstudent.mother_name = mothername
                        getstudent.gender = gender
                        getstudent.category = category

                        getstudent.email = email
                        getstudent.alternateemail = alternateemail
                        getstudent.mobile = mobile
                        getstudent.alternate_mobile1 = alternatemobile1
                        
                        getstudent.address = address
                        getstudent.alternateaddress = alternateaddress
                        getstudent.nationality = nationality
                        getstudent.country = country
                        getstudent.state = state
                        getstudent.city = city
                        getstudent.pincode = pincode
                        getstudent.image = student_image
                        getstudent.university = university
                        getstudent.student_remarks = student_remarks
                        getstudent.save()
                        
                        
                    except Student.DoesNotExist:
                        print("student not found ..!!")
                if secondary_year or secondary_board or secondary_percentage or secondary_document or sr_year or sr_board or sr_percentage or sr_document or under_year or under_board or under_percentage or under_document or post_year or post_board or post_percentage or post_document or mphil_year or mphil_board or mphil_percentage or mphil_document or others_year or others_board or others_percentage or others_document:
                    try:
                        getstudent = Student.objects.get(enrollment_id = enroll_id)
                        getqualification = Qualification.objects.get(student = getstudent.id)
                        getqualification.secondary_year = secondary_year
                        getqualification.sr_year = sr_year
                        getqualification.under_year = under_year
                        getqualification.post_year = post_year
                        getqualification.mphil_year = mphil_year
                        getqualification.others_year = others_year
                        
                        getqualification.secondary_board = secondary_board
                        getqualification.sr_board = sr_board
                        getqualification.under_board = under_board
                        getqualification.post_board = post_board
                        getqualification.mphil_board = mphil_board
                        getqualification.others_board = others_board
                        
                        getqualification.secondary_percentage = secondary_percentage
                        getqualification.sr_percentage = sr_percentage
                        getqualification.under_percentage = under_percentage
                        getqualification.post_percentage = post_percentage
                        getqualification.mphil_percentage = mphil_percentage
                        getqualification.others_percentage = others_percentage
                        
                        getqualification.secondary_document = secondary_document
                        getqualification.sr_document = sr_document
                        getqualification.under_document = under_document
                        getqualification.post_document = post_document
                        getqualification.mphil_document = mphil_document
                        getqualification.others_document = others_document
                        # getqualification.save()
                    except Student.DoesNotExist:
                        pass

                if counselor_name or reference_name or university_enrollment_number:
                    try:
                        getstudent = Student.objects.get(enrollment_id = enroll_id)
                        getadditionaldetails = AdditionalEnrollmentDetails.objects.get(student=getstudent.id)
                        getadditionaldetails.counselor_name=counselor_name
                        getadditionaldetails.reference_name=reference_name
                        getadditionaldetails.university_enrollment_id=university_enrollment_number
                        getadditionaldetails.save()
                        
                    except Student.DoesNotExist:
                        pass
                
                return JsonResponse({'saved':'yes','enroll_id':enroll_id})

            try:
                getstudent = Student.objects.get(enrollment_id = enroll_id)
                # print("student found")
                found_student = "yes"
                try:
                    getenroll = Enrolled.objects.get(student=getstudent.id)
                    # print(getenroll)
                    course = Course.objects.get(id = getenroll.course)
                    stream = Stream.objects.get(id = getenroll.stream)
                    # print(course)
                    # print(stream)
                    getdocuments = StudentDocuments.objects.filter(student=getstudent.id)
                    # print(getdocuments)
                    try:
                        getqualification = Qualification.objects.get(student=getstudent.id)
                        # print(getqualification)
                    except Qualification.DoesNotExist:
                        getqualification = "none"
                    try:
                        getuniversity = University.objects.get(registrationID=getstudent.university)
                        # print(getuniversity)
                    except University.DoesNotExist:
                        getuniversity = "none"

                    try:
                        getadditionalenrollmentdetails = AdditionalEnrollmentDetails.objects.get(student = getstudent.id)
                        # print(getadditionalenrollmentdetails)
                    except AdditionalEnrollmentDetails.DoesNotExist:
                        getadditionalenrollmentdetails = "none"
                    obj = {
                        "enrollment_id":getstudent.enrollment_id,
                        "image":getstudent.image,
                        "name":getstudent.name,
                        "father_name":getstudent.father_name,
                        "mother_name":getstudent.mother_name,
                        "dateofbirth":str(getstudent.dateofbirth),
                        "mobile":getstudent.mobile,
                        "alternate_mobile1":getstudent.alternate_mobile1,
                        "email":getstudent.email,
                        "alternateemail":getstudent.alternateemail,
                        "gender":getstudent.gender,
                        "category":getstudent.category,
                        "address":getstudent.address,
                        "alternateaddress":getstudent.alternateaddress,
                        "nationality":getstudent.nationality,
                        "country":getstudent.country,
                        "state":getstudent.state,
                        "city":getstudent.city,
                        "pincode":getstudent.pincode,
                        "university":getstudent.university,
                        "qualification":getqualification,
                        "course":course,
                        "stream":stream,
                        "course_pattern":getenroll.course_pattern,
                        "session":getenroll.session,
                        "entry_mode":getenroll.entry_mode,
                        "current_semyear":getenroll.current_semyear,
                        "university":getuniversity,
                        "student_remarks":getstudent.student_remarks,
                        "additionalenrollmentdetails":getadditionalenrollmentdetails
                        
                    }
                    student.append(obj)
                except Enrolled.DoesNotExist:
                    getenroll = "none"

            except Student.DoesNotExist:
                # print("student not found")
                found_student = "no"
        
            
            
            
            




    params = {
        "display":display,
        "level_of_user":level_of_user,
        "course":Course.objects.all(),
        "university":University.objects.all(),
        "found_student":found_student,
        "student":student,
        "country":Countries.objects.all()
    }
    return render(request,"editstudent.html",params)

@login_required(login_url='/login/')  
def DeleteArchive(request,enroll_id):
    display = ""
    found_student = ""
    student = []
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            display = "yes"
            if request.method == "POST":
                delete_student_id = request.POST.get('delete_student_id')
                delete = request.POST.get('delete')
                if delete_student_id:
                    print("student got")
                    try:
                        getstudent = Student.objects.get(id = delete_student_id)
                        print("Delete Student : ",getstudent)
                        getenroll = Enrolled.objects.filter(student = getstudent.id)
                        studentdocuments = StudentDocuments.objects.filter(student = getstudent.id)
                        studentfees = StudentFees.objects.filter(student = getstudent.id)
                        qualification = Qualification.objects.filter(student = getstudent.id)
                        additionalenrollmentdetails = AdditionalEnrollmentDetails.objects.filter(student = getstudent.id)
                        courier = Courier.objects.filter(student = getstudent.id)
                        paymentreciept = PaymentReciept.objects.filter(student = getstudent.id)
                        studentsyllabus = StudentSyllabus.objects.filter(student = getstudent.id)

                        getstudent.delete()
                        getenroll.delete()
                        studentdocuments.delete()
                        studentfees.delete()
                        qualification.delete()
                        additionalenrollmentdetails.delete()
                        courier.delete()
                        paymentreciept.delete()
                        studentsyllabus.delete()
                        

                        return JsonResponse({'deleted':'yes'})

                    except Student.DoesNotExist:
                        pass
                archive = request.POST.get('archive')
                student_id = request.POST.get('student_id')
                if student_id:
                    try:
                        getstudent = Student.objects.get(id = student_id)
                        enrolled = Enrolled.objects.get(student = student_id)
                        studentfees = StudentFees.objects.filter(student = student_id)
                        try:
                            qualification = Qualification.objects.get(student = student_id)
                            create_archive_qualification = Qualification(
                                id=qualification.id,
                                student= qualification.student,
                                secondary_year = qualification.secondary_year,
                                sr_year = qualification.sr_year,
                                under_year= qualification.under_year,
                                post_year= qualification.post_year,
                                mphil_year= qualification.mphil_year,
                                others_year = qualification.others_year,
                                secondary_board= qualification.secondary_board,
                                sr_board= qualification.sr_board,
                                under_board= qualification.under_board,
                                post_board= qualification.post_board,
                                mphil_board= qualification.mphil_board,
                                others_board= qualification.others_board,
                                secondary_percentage= qualification.secondary_percentage,
                                sr_percentage= qualification.sr_percentage,
                                under_percentage= qualification.under_percentage,
                                post_percentage= qualification.post_percentage,
                                mphil_percentage= qualification.mphil_percentage,
                                others_percentage= qualification.others_percentage,
                                secondary_document= qualification.secondary_document,
                                sr_document= qualification.sr_document,
                                under_document= qualification.under_document,
                                post_document= qualification.post_document,
                                mphil_document= qualification.mphil_document,
                                others_document= qualification.others_document
                                )
                            create_archive_qualification.save(using="archive")
                            qualification.delete()

                        except Qualification.DoesNotExist:
                            pass
                        additionalenrollmentdetails = AdditionalEnrollmentDetails.objects.get(student = student_id)
                        university_enrollment = UniversityEnrollment.objects.filter(student = student_id)
                        courier = Courier.objects.filter(student = student_id)
                        paymentreciept = PaymentReciept.objects.filter(student = student_id)
                        submitted_answer = SubmittedExamination.objects.filter(student = getstudent.user)
                        results = Result.objects.filter(student = student_id)
                        personal_documents = PersonalDocuments.objects.filter(student = student_id)
                        student_documents = StudentDocuments.objects.filter(student = student_id)
                        university_examination = UniversityExamination.objects.filter(student = student_id)
                        result_uploaded = ResultUploaded.objects.filter(student = student_id)
                        if archive == "yes":
                            # print("yes")
                            getstudent.archive = True
                            getstudent.save()
                            create_archive_student = Student(
                                id = getstudent.id,
                                name = getstudent.name, 
                                father_name = getstudent.father_name, 
                                mother_name = getstudent.mother_name, 
                                dateofbirth = getstudent.dateofbirth, 
                                mobile = getstudent.mobile, 
                                alternate_mobile1 = getstudent.alternate_mobile1, 
                                alternate_mobile2 = getstudent.alternate_mobile2, 
                                email = getstudent.email,
                                gender = getstudent.gender,
                                category = getstudent.category,
                                address = getstudent.address,
                                ID_type = getstudent.ID_type,
                                ID_number = getstudent.ID_number,
                                nationality = getstudent.nationality,
                                country = getstudent.country,
                                state = getstudent.state,
                                city = getstudent.city,
                                pincode = getstudent.pincode,
                                registration_id = getstudent.registration_id,
                                old_university_enrollment_id = getstudent.old_university_enrollment_id,
                                new_university_enrollment_id = getstudent.new_university_enrollment_id,
                                enrollment_id = getstudent.enrollment_id,
                                enrollment_date = getstudent.enrollment_date,
                                university = getstudent.university,
                                image = getstudent.image,
                                verified = getstudent.verified,
                                user = getstudent.user,
                                enrolled = getstudent.enrolled,
                                archive = getstudent.archive,
                                is_cancelled = getstudent.is_cancelled,
                                created_by = getstudent.created_by,
                                modified_by = getstudent.modified_by
                                )
                            create_archive_enrolled = Enrolled(
                                id=enrolled.id,
                                student=enrolled.student,
                                course=enrolled.course,
                                stream=enrolled.stream,
                                course_pattern=enrolled.course_pattern,
                                session=enrolled.session,
                                entry_mode=enrolled.entry_mode,
                                total_semyear=enrolled.total_semyear,
                                current_semyear=enrolled.current_semyear
                                )
                            create_archive_student.save(using="archive")
                            create_archive_enrolled.save(using="archive")
                            
                            
                            for i in studentfees:
                                create_archive_studntfees = StudentFees(
                                    id=i.id,
                                    student=i.student,
                                    studypattern=i.studypattern,
                                    stream=i.stream,
                                    tutionfees=i.tutionfees,
                                    examinationfees=i.examinationfees,
                                    bookfees=i.bookfees,
                                    resittingfees=i.resittingfees,
                                    entrancefees=i.entrancefees,
                                    extrafees=i.extrafees,
                                    discount=i.discount,
                                    totalfees=i.totalfees,
                                    sem=i.sem
                                    )
                                create_archive_studntfees.save(using="archive")
                                i.delete()

                            for i in university_enrollment:
                                create_archive_universityenrollment = UniversityEnrollment(
                                    id=i.id,
                                    student = i.student,
                                    type = i.type,
                                    course_id = i.course_id,
                                    course_name = i.course_name,
                                    enrollment_id = i.enrollment_id
                                    )
                                create_archive_universityenrollment.save(using="archive")
                                i.delete()
                            for i in courier:
                                create_archive_courier = Courier(
                                    id=i.id,
                                    student=i.student, 
                                    article_name = i.article_name , 
                                    courier_from = i.courier_from , 
                                    courier_to = i.courier_to, 
                                    booking_date = i.booking_date, 
                                    courier_company = i.courier_company , 
                                    tracking_id = i.tracking_id , 
                                    remarks = i.remarks 
                                    )
                                create_archive_courier.save(using="archive")
                                i.delete()
                            for i in paymentreciept:
                                create_archive_paymentreciept = PaymentReciept(
                                    id=i.id,
                                    student = i.student,
                                    payment_for= i.payment_for,
                                    payment_type= i.payment_type,
                                    fee_reciept_type= i.fee_reciept_type,
                                    transaction_date= i.transaction_date,
                                    cheque_no= i.cheque_no,
                                    bank_name= i.bank_name,
                                    paidamount= i.paidamount,
                                    pendingamount= i.pendingamount,
                                    transactionID = i.transactionID,
                                    paymentmode= i.paymentmode,
                                    remarks= i.remarks,
                                    session= i.session,
                                    semyear= i.semyear
                                    )
                                create_archive_paymentreciept.save(using="archive")
                                i.delete()
                            for i in submitted_answer:
                                create_archive_submitted_answer = SubmittedExamination(
                                    id=i.id,
                                    student=i.student,
                                    exam=i.exam,
                                    question=i.question,
                                    type=i.type,
                                    marks=i.marks,
                                    marks_obtained=i.marks_obtained,
                                    submitted_answer=i.submitted_answer,
                                    answer=i.answer,
                                    result=i.result
                                    )
                                create_archive_submitted_answer.save(using="archive")
                                i.delete()



                            for i in results:
                                create_archive_result = Result(
                                    id=i.id,
                                    student=i.student,
                                    exam=i.exam,
                                    total_question=i.total_question,
                                    attempted=i.attempted,
                                    total_marks=i.total_marks,
                                    score=i.score,
                                    result=i.result
                                    )
                                create_archive_result.save(using="archive")
                                i.delete()
                            for i in personal_documents:
                                create_archive_personal_documents = PersonalDocuments(
                                    id = i.id,
                                    document=i.document,
                                    document_name=i.document_name,
                                    document_ID_no=i.document_ID_no,
                                    student=i.student
                                    )
                                create_archive_personal_documents.save(using="archive")
                                personal_document_images = PersonalDocumentsImages.objects.filter(document = i)
                                for j in personal_document_images:
                                    create_archive_personal_documents_images = PersonalDocumentsImages(
                                        id=j.id,
                                        document = j.document,
                                        document_image=j.document_image
                                        )
                                    create_archive_personal_documents_images.save(using="archive")
                                    j.delete()
                                i.delete()
                            for i in student_documents:
                                create_archive_student_documents = StudentDocuments(
                                    id=i.id,
                                    student=i.student,
                                    document=i.document,
                                    document_name=i.document_name,
                                    document_ID_no=i.document_ID_no,
                                    document_image_front=i.document_image_front,
                                    document_image_back=i.document_image_back
                                    )
                                create_archive_student_documents.save(using="archive")
                                i.delete()

                            for i in university_examination:
                                create_archive_university_examination = UniversityExamination(
                                    id=i.id,
                                    student = i.student,
                                    type = i.type,
                                    amount = i.amount,
                                    date = i.date,
                                    examination = i.examination,
                                    semyear = i.semyear,
                                    paymentmode = i.paymentmode,
                                    remarks = i.remarks
                                    )
                                create_archive_university_examination.save(using="archive")
                                i.delete()

                            for i in result_uploaded:
                                create_archive_result_uploaded = ResultUploaded(
                                    id=i.id,
                                    student = i.student,
                                    date = i.date,
                                    examination = i.examination,
                                    semyear = i.semyear,
                                    uploaded = i.uploaded,
                                    remarks = i.remarks
                                    )
                                create_archive_result_uploaded.save(using="archive")
                                i.delete()
                            
                            getstudent.delete()
                            enrolled.delete()
                            return JsonResponse({'archived':'yes'})
                        else:
                            print("no")
                            getstudent.archive = False
                            getstudent.save()
                            
                            return JsonResponse({'archived':'yes'})
                    except Student.DoesNotExist:
                        pass
            try:
                getstudent = Student.objects.get(enrollment_id = enroll_id)
                enroll = Enrolled.objects.get(student = getstudent.id)
                course = Course.objects.get(id = enroll.course)
                stream = Stream.objects.get(id = enroll.stream)
                # print(getstudent , enroll , course , stream)
                commonfees = PaymentReciept.objects.filter(Q(student = getstudent.id) & (Q(payment_for="Course Fees") | Q(payment_for="Tution Fees") | Q(payment_for="Re-Registration Fees") | Q(payment_for="Examination Fees")))
                additionalfees = PaymentReciept.objects.filter(Q(student = getstudent.id) & ~(Q(payment_for="Course Fees") | Q(payment_for="Tution Fees") | Q(payment_for="Re-Registration Fees") | Q(payment_for="Examination Fees")))
                # print("Common Fees : ",commonfees)
                # print("Additional Fees : ",additionalfees)
                obj = {
                    "id":getstudent.id,
                    "enrollment_id":getstudent.enrollment_id,
                    "name":getstudent.name,
                    "dateofbirth":getstudent.dateofbirth,
                    "email":getstudent.email,
                    "mobile":getstudent.mobile,
                    "archive":getstudent.archive,
                    "course_pattern":enroll.course_pattern,
                    "session":enroll.session,
                    "entry_mode":enroll.entry_mode,
                    "total_semyear":enroll.total_semyear,
                    "current_semyear":enroll.current_semyear,
                    "course":course.name,
                    "stream":stream.name,
                    "commonfees":commonfees,
                    "additionalfees":additionalfees
                    
                    
                }
                student.append(obj)
                
                found_student = "yes"
            except Student.DoesNotExist:
                pass
    params = {
        "display":display,
        "found_student":found_student,
        "student":student
    }
    return render(request,"delete_archive.html",params)


@login_required(login_url='/login/')
def UnArchive(request):
    display = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            display = "yes"
            if request.method == "POST":
                unarchive_student_id = request.POST.get('unarchive_student_id')
                if unarchive_student_id:
                    print(unarchive_student_id)
                    try:
                        getstudent = Student.objects.using("archive").get(id = unarchive_student_id)
                        enrolled = Enrolled.objects.using("archive").get(student = unarchive_student_id)
                        studentfees = StudentFees.objects.using("archive").filter(student = unarchive_student_id)
                        print(getstudent , enrolled , studentfees)
                        try:
                            qualification = Qualification.objects.using("archive").get(student = unarchive_student_id)
                            create_archive_qualification = Qualification(
                                id=qualification.id,
                                student= qualification.student,
                                secondary_year = qualification.secondary_year,
                                sr_year = qualification.sr_year,
                                under_year= qualification.under_year,
                                post_year= qualification.post_year,
                                mphil_year= qualification.mphil_year,
                                others_year = qualification.others_year,
                                secondary_board= qualification.secondary_board,
                                sr_board= qualification.sr_board,
                                under_board= qualification.under_board,
                                post_board= qualification.post_board,
                                mphil_board= qualification.mphil_board,
                                others_board= qualification.others_board,
                                secondary_percentage= qualification.secondary_percentage,
                                sr_percentage= qualification.sr_percentage,
                                under_percentage= qualification.under_percentage,
                                post_percentage= qualification.post_percentage,
                                mphil_percentage= qualification.mphil_percentage,
                                others_percentage= qualification.others_percentage,
                                secondary_document= qualification.secondary_document,
                                sr_document= qualification.sr_document,
                                under_document= qualification.under_document,
                                post_document= qualification.post_document,
                                mphil_document= qualification.mphil_document,
                                others_document= qualification.others_document
                                )
                            # create_archive_qualification.save(using="archive")
                            # qualification.delete()

                        except Qualification.DoesNotExist:
                            pass
                        university_enrollment = UniversityEnrollment.objects.using("archive").filter(student = unarchive_student_id)
                        courier = Courier.objects.using("archive").filter(student = unarchive_student_id)
                        paymentreciept = PaymentReciept.objects.using("archive").filter(student = unarchive_student_id)
                        submitted_answer = SubmittedExamination.objects.using("archive").filter(student = getstudent.user)
                        results = Result.objects.using("archive").filter(student = unarchive_student_id)
                        personal_documents = PersonalDocuments.objects.using("archive").filter(student = unarchive_student_id)
                        student_documents = StudentDocuments.objects.using("archive").filter(student = unarchive_student_id)
                        university_examination = UniversityExamination.objects.using("archive").filter(student = unarchive_student_id)
                        result_uploaded = ResultUploaded.objects.using("archive").filter(student = unarchive_student_id)
                       
                        
                        getstudent.archive = False
                        getstudent.save()
                        create_archive_student = Student(
                            id = getstudent.id,
                            name = getstudent.name, 
                            father_name = getstudent.father_name, 
                            mother_name = getstudent.mother_name, 
                            dateofbirth = getstudent.dateofbirth, 
                            mobile = getstudent.mobile, 
                            alternate_mobile1 = getstudent.alternate_mobile1, 
                            alternate_mobile2 = getstudent.alternate_mobile2, 
                            email = getstudent.email,
                            gender = getstudent.gender,
                            category = getstudent.category,
                            address = getstudent.address,
                            ID_type = getstudent.ID_type,
                            ID_number = getstudent.ID_number,
                            nationality = getstudent.nationality,
                            country = getstudent.country,
                            state = getstudent.state,
                            city = getstudent.city,
                            pincode = getstudent.pincode,
                            registration_id = getstudent.registration_id,
                            old_university_enrollment_id = getstudent.old_university_enrollment_id,
                            new_university_enrollment_id = getstudent.new_university_enrollment_id,
                            enrollment_id = getstudent.enrollment_id,
                            enrollment_date = getstudent.enrollment_date,
                            university = getstudent.university,
                            image = getstudent.image,
                            verified = getstudent.verified,
                            user = getstudent.user,
                            enrolled = getstudent.enrolled,
                            archive = getstudent.archive,
                            is_cancelled = getstudent.is_cancelled,
                            created_by = getstudent.created_by,
                            modified_by = getstudent.modified_by
                            )
                        create_archive_enrolled = Enrolled(
                            id=enrolled.id,
                            student=enrolled.student,
                            course=enrolled.course,
                            stream=enrolled.stream,
                            course_pattern=enrolled.course_pattern,
                            session=enrolled.session,
                            entry_mode=enrolled.entry_mode,
                            total_semyear=enrolled.total_semyear,
                            current_semyear=enrolled.current_semyear
                            )
                        create_archive_student.save()
                        create_archive_enrolled.save()
                        
                        
                        for i in studentfees:
                            create_archive_studntfees = StudentFees(
                                id=i.id,
                                student=i.student,
                                studypattern=i.studypattern,
                                stream=i.stream,
                                tutionfees=i.tutionfees,
                                examinationfees=i.examinationfees,
                                bookfees=i.bookfees,
                                resittingfees=i.resittingfees,
                                entrancefees=i.entrancefees,
                                extrafees=i.extrafees,
                                discount=i.discount,
                                totalfees=i.totalfees,
                                sem=i.sem
                                )
                            create_archive_studntfees.save()
                            i.delete()

                        for i in university_enrollment:
                            create_archive_universityenrollment = UniversityEnrollment(
                                id=i.id,
                                student = i.student,
                                type = i.type,
                                course_id = i.course_id,
                                course_name = i.course_name,
                                enrollment_id = i.enrollment_id
                                )
                            create_archive_universityenrollment.save()
                            i.delete()
                            
                        for i in courier:
                            create_archive_courier = Courier(
                                id=i.id,
                                student=i.student, 
                                article_name = i.article_name , 
                                courier_from = i.courier_from , 
                                courier_to = i.courier_to, 
                                booking_date = i.booking_date, 
                                courier_company = i.courier_company , 
                                tracking_id = i.tracking_id , 
                                remarks = i.remarks 
                                )
                            create_archive_courier.save()
                            i.delete()
                            
                        for i in paymentreciept:
                            create_archive_paymentreciept = PaymentReciept(
                                id=i.id,
                                student = i.student,
                                payment_for= i.payment_for,
                                payment_type= i.payment_type,
                                fee_reciept_type= i.fee_reciept_type,
                                transaction_date= i.transaction_date,
                                cheque_no= i.cheque_no,
                                bank_name= i.bank_name,
                                paidamount= i.paidamount,
                                pendingamount= i.pendingamount,
                                transactionID = i.transactionID,
                                paymentmode= i.paymentmode,
                                remarks= i.remarks,
                                session= i.session,
                                semyear= i.semyear
                                )
                            create_archive_paymentreciept.save()
                            i.delete()
                            
                        for i in submitted_answer:
                            create_archive_submitted_answer = SubmittedExamination(
                                id=i.id,
                                student=i.student,
                                exam=i.exam,
                                question=i.question,
                                type=i.type,
                                marks=i.marks,
                                marks_obtained=i.marks_obtained,
                                submitted_answer=i.submitted_answer,
                                answer=i.answer,
                                result=i.result
                                )
                            create_archive_submitted_answer.save()
                            i.delete()



                        for i in results:
                            create_archive_result = Result(
                                id=i.id,
                                student=i.student,
                                exam=i.exam,
                                total_question=i.total_question,
                                attempted=i.attempted,
                                total_marks=i.total_marks,
                                score=i.score,
                                result=i.result
                                )
                            create_archive_result.save()
                            i.delete()
                            
                        for i in personal_documents:
                            create_archive_personal_documents = PersonalDocuments(
                                id = i.id,
                                document=i.document,
                                document_name=i.document_name,
                                document_ID_no=i.document_ID_no,
                                student=i.student
                                )
                            create_archive_personal_documents.save()
                            i.delete()

                            personal_document_images = PersonalDocumentsImages.objects.using("archive").filter(document = i)
                            for j in personal_document_images:
                                create_archive_personal_documents_images = PersonalDocumentsImages(
                                    id=j.id,
                                    document = j.document,
                                    document_image=j.document_image
                                    )
                                create_archive_personal_documents_images.save()
                                j.delete()
                            i.delete()   
                            
                        for i in student_documents:
                            create_archive_student_documents = StudentDocuments(
                                id=i.id,
                                student=i.student,
                                document=i.document,
                                document_name=i.document_name,
                                document_ID_no=i.document_ID_no,
                                document_image_front=i.document_image_front,
                                document_image_back=i.document_image_back
                                )
                            create_archive_student_documents.save()
                            i.delete()

                        for i in university_examination:
                            create_archive_university_examination = UniversityExamination(
                                id=i.id,
                                student = i.student,
                                type = i.type,
                                amount = i.amount,
                                date = i.date,
                                examination = i.examination,
                                semyear = i.semyear,
                                paymentmode = i.paymentmode,
                                remarks = i.remarks
                                )
                            create_archive_university_examination.save()
                            i.delete()

                        for i in result_uploaded:
                            create_archive_result_uploaded = ResultUploaded(
                                id=i.id,
                                student = i.student,
                                date = i.date,
                                examination = i.examination,
                                semyear = i.semyear,
                                uploaded = i.uploaded,
                                remarks = i.remarks
                                )
                            create_archive_result_uploaded.save()
                            i.delete()
                        
                        getstudent.delete()
                        enrolled.delete()


                    except Student.DoesNotExist:
                        pass      
    params = {
        "display": display,
        "students":Student.objects.all().using("archive")
    }
    return render(request,"un-archive.html",params)



@login_required(login_url='/login/')
def AddAdditionalDetails(request):
    display = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            display = "yes"
            if request.method == "POST":
                enroll_id = request.POST.get('enroll_id')
                data = request.POST.get('data')
                if data:
                    jsondata = json.loads(data)
                    print(jsondata)
                    print(jsondata['email'])
                    try:
                        get_student = Student.objects.get( Q(email = jsondata['email']) & Q(mobile = jsondata['mobile']) )
                        get_additional_details = AdditionalEnrollmentDetails.objects.get(student=get_student.id)
                        if get_additional_details.counselor_name == jsondata['counselor_name']:
                            pass
                        else:
                            get_additional_details.counselor_name = jsondata['counselor_name']
                            get_additional_details.save()


                        if get_additional_details.reference_name == jsondata['reference_name']:
                            pass
                        else:
                            get_additional_details.reference_name = jsondata['reference_name']
                            get_additional_details.save()

                        if get_additional_details.session == jsondata['session']:
                            pass
                        else:
                            get_additional_details.session = jsondata['session']
                            get_additional_details.save()

                        if get_additional_details.entry_mode == jsondata['entry_mode']:
                            pass
                        else:
                            get_additional_details.entry_mode = jsondata['entry_mode']
                            get_additional_details.save()

                        if get_additional_details.old_university_enrollment_id == jsondata['old_university_enrollment_id']:
                            pass
                        else:
                            get_additional_details.old_university_enrollment_id = jsondata['old_university_enrollment_id']
                            get_additional_details.save()

                        if get_additional_details.university_enrollment_id == jsondata['university_enrollment_id']:
                            pass
                        else:
                            get_additional_details.university_enrollment_id = jsondata['university_enrollment_id']
                            get_additional_details.save()

                        if get_additional_details.courier_company_name == jsondata['courier_company_name']:
                            pass
                        else:
                            get_additional_details.courier_company_name = jsondata['courier_company_name']
                            get_additional_details.save()

                        if get_additional_details.courier_tracking_id == jsondata['courier_tracking_id']:
                            pass
                        else:
                            get_additional_details.courier_tracking_id = jsondata['courier_tracking_id']
                            get_additional_details.save()

                        if get_additional_details.courier_date == jsondata['courier_date']:
                            pass
                        else:
                            get_additional_details.courier_date = jsondata['courier_date']
                            get_additional_details.save()

                        if get_additional_details.courier_return_date == jsondata['courier_return_date']:
                            pass
                        else:
                            get_additional_details.courier_return_date = jsondata['courier_return_date']
                            get_additional_details.save()

                        if get_additional_details.courier_return_reason == jsondata['courier_return_reason']:
                            pass
                        else:
                            get_additional_details.courier_return_reason = jsondata['courier_return_reason']
                            get_additional_details.save()

                        if get_additional_details.courier_goods_type == jsondata['courier_goods_type']:
                            pass
                        else:
                            get_additional_details.courier_goods_type = jsondata['courier_goods_type']
                            get_additional_details.save()

                        if get_additional_details.courier_remarks == jsondata['courier_remarks']:
                            pass
                        else:
                            get_additional_details.courier_remarks = jsondata['courier_remarks']
                            get_additional_details.save()

                        
                        
                        
                        
                    except Student.DoesNotExist:
                        print("student doesnt exist")
                if enroll_id:
                    try:
                        getstudent = Student.objects.get(enrollment_id = enroll_id)
                        getenroll = Enrolled.objects.get(student=getstudent.id)
                        try:
                            getadditionaldetails = AdditionalEnrollmentDetails.objects.get(student=getstudent.id)
                        except AdditionalEnrollmentDetails.DoesNotExist:
                            create_additional_details = AdditionalEnrollmentDetails(student = getstudent.id)
                            create_additional_details.save()
                        additionaldetails = AdditionalEnrollmentDetails.objects.get(student=getstudent.id)
                        course = Course.objects.get(id = getenroll.course)
                        stream = Stream.objects.get(id = getenroll.stream)
                        print(getstudent , getenroll , additionaldetails , course , stream)
                        obj = {
                            "name":getstudent.name,
                            "mobile":getstudent.mobile,
                            "email":getstudent.email,
                            "course":course.name,
                            "stream":stream.name,
                            "counselor_name":additionaldetails.counselor_name,
                            "reference_name":additionaldetails.reference_name,
                            "session":additionaldetails.session,
                            "entry_mode":additionaldetails.entry_mode,
                            "old_university_enrollment_id":additionaldetails.old_university_enrollment_id,
                            "university_enrollment_id":additionaldetails.university_enrollment_id,
                            "courier_company_name":additionaldetails.courier_company_name,
                            "courier_tracking_id":additionaldetails.courier_tracking_id,
                            "courier_date":additionaldetails.courier_date,
                            "courier_return_date":additionaldetails.courier_return_date,
                            "courier_return_reason":additionaldetails.courier_return_reason,
                            "courier_goods_type":additionaldetails.courier_goods_type,
                            "courier_remarks":additionaldetails.courier_remarks,

                        }
                        return JsonResponse({'student':'YES','data':obj})
                    except Student.DoesNotExist:
                        return JsonResponse({'student':'NA'})
    params = {
        "display":display
    }
    return render(request,"additionaldetails.html",params)

@login_required(login_url='/login/')
def AddSyllabus(request):
    print("yes")
    display = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            display = "yes"
            if request.method == "POST":
                course_id = request.POST.get('course_id')
                stream_id = request.POST.get('stream_id')
                semester = request.POST.get('semester')
                c_id = request.POST.get('c_id')
                s_id = request.POST.get('s_id')
                sem = request.POST.get('sem')
                pdf = request.FILES.get('pdf', False)
                uc_id = request.POST.get('uc_id')
                us_id = request.POST.get('us_id')
                usem = request.POST.get('usem')
                updf = request.FILES.get('updf', False)
                if uc_id and us_id and usem and updf:
                    try:
                        syllabus = Syllabus.objects.get(Q(course=uc_id) & Q(stream = us_id) & Q(semester = usem))
                        syllabus.pdf = updf
                        syllabus.save()
                    except Syllabus.DoesNotExist:
                        pass

                if c_id and s_id and sem and pdf:
                    addsyllabus = Syllabus(course = c_id , stream = s_id, semester = sem , pdf = pdf)
                    addsyllabus.save()

                if course_id and stream_id and semester:
                    try:
                        print("show",course_id , stream_id , semester)
                        syllabus = Syllabus.objects.get(Q(course=course_id) & Q(stream = stream_id) & Q(semester = semester))
                        syllabus_serializer = SyllabusSerializer(syllabus,many=False)
                        return JsonResponse({'syllabus':'yes','data':syllabus_serializer.data})
                    except Syllabus.DoesNotExist:
                        return JsonResponse({'syllabus':'na'})
                data = request.POST.get('data')
                if data:
                    try:
                        getstream = Stream.objects.filter(course=data)
                    except Stream.DoesNotExist:
                        getstream = "yes"
                    if getstream != "yes":
                        streamserializer = StreamSerializer(getstream,many=True)
                        return JsonResponse({'stream':streamserializer.data})
    params = {
        "display":display,
        "university":University.objects.all()
    }
    return render(request,"addsyllabus.html",params)

# student , enrolled , additionalenrollmentdetails , paymentreciept , qualification , studentdocuments, student fees
# pincode should be compulsory
# muttishwamichinnaswamivenugopaliyerchandrakantavishkunal@gmail.com
# MOON MANOJKUMAR BHASKAR
@login_required(login_url='/login/')
def PendingVerification(request):
    display = ""
    serializer = ''
    level_of_user = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4" or level.level =="2":
            display = "yes"
            level_of_user = level.level
            if request.method == "POST":
                delete_student = request.POST.get('delete_student')
                if delete_student:
                    # print("delete_student : ",delete_student)
                    getstudent = Student.objects.get(enrollment_id = delete_student)
                    # print("getstudent : ",getstudent)
                    # print("Delete Student : ",getstudent)
                    getenroll = Enrolled.objects.filter(student = getstudent.id)
                    studentdocuments = StudentDocuments.objects.filter(student = getstudent.id)
                    studentfees = StudentFees.objects.filter(student = getstudent.id)
                    qualification = Qualification.objects.filter(student = getstudent.id)
                    additionalenrollmentdetails = AdditionalEnrollmentDetails.objects.filter(student = getstudent.id)
                    courier = Courier.objects.filter(student = getstudent.id)
                    paymentreciept = PaymentReciept.objects.filter(student = getstudent.id)
                    studentsyllabus = StudentSyllabus.objects.filter(student = getstudent.id)

                    getstudent.delete()
                    getenroll.delete()
                    studentdocuments.delete()
                    studentfees.delete()
                    qualification.delete()
                    additionalenrollmentdetails.delete()
                    courier.delete()
                    paymentreciept.delete()
                    studentsyllabus.delete()
                    return JsonResponse({'deleted':'yes'})

                verified = request.POST.get('verified')
                if verified:
                    try:
                        getstudent = Student.objects.get(enrollment_id = verified)
                        getstudent.verified = True
                        getstudent.enrolled = True
                        getstudent.save()
                    except Student.DoesNotExist:
                        pass
                

                fees = request.POST.get('fees')
                if fees:
                    try:
                        getstudent = Student.objects.get(enrollment_id = fees)
                        try:
                            getfeespaid = PaymentReciept.objects.filter(student = getstudent.id)
                            feeserializer = PaymentRecieptSerializer(getfeespaid,many=True)
                            return JsonResponse({'fees':feeserializer.data})
                        except Fees.DoesNotExist:
                            getfeespaid = "none"
                    except Student.DoesNotExist:
                        pass
                getpayment_reciept = request.POST.get('getpayment_reciept')
                if getpayment_reciept:
                    # print(getpayment_reciept)
                    get_reciept = PaymentReciept.objects.get(id = getpayment_reciept)
                    paymentrecieptserializer = PaymentRecieptSerializer(get_reciept,many=False)
                    view_student = Student.objects.get(id=get_reciept.student)
                    view_enroll = Enrolled.objects.get(student=view_student.id)
                    view_course = Course.objects.get(id = view_enroll.course)
                    view_stream = Stream.objects.get(id = view_enroll.stream)
                    temp = {
                        "name":view_student.name,
                        "email":view_student.email,
                        "mobile":view_student.mobile,
                        "enrollment_id":view_student.enrollment_id,
                        "address":view_student.address,
                        "country":view_student.country,
                        "state":view_student.state,
                        "city":view_student.city,
                        "pincode":view_student.pincode,
                        "course":view_course.name,
                        "stream":view_stream.name
                    }
                    return JsonResponse({'view_reciept':paymentrecieptserializer.data,'personal':temp})
                
                enrollid = request.POST.get('enrollid')
                if enrollid:
                    try:
                        getstudent = Student.objects.get(enrollment_id = enrollid)
                        getqualification = Qualification.objects.get(student = getstudent.id)
                        qualificationserializer = QualificationSerializer(getqualification,many=False)
                        return JsonResponse({'student':'yes','qualification':qualificationserializer.data})
                    except Student.DoesNotExist:
                        return JsonResponse({'student':'no'})
            
            
            # pending = Student.objects.filter(verified=False)
            # serializer = StudentSerializer(pending,many=True)
            # postdata = serializer.data
            
            # od1 = json.dumps(postdata)
            # od2 = json.dumps(postdata,indent=4)
            # # print(od1)
            # file_object = open('static/dict/sample.txt', 'a')
            # file_object.truncate(0)
            # file_object.write('{"data": '+od2+'}')
            # file_object.close()
            allstudent = Student.objects.filter(verified = False).order_by('-id')
            # print(allstudent)
            # logger.info(allstudent)
            file_object = open('static/dict/sample.txt', 'a')
            file_object.truncate(0)
            file_object.close()
            studentlist = []
            enrolled = []
            for i in allstudent:
                
                student_id = i.id
                # print(student_id)
                university = University.objects.get(registrationID=i.university)
                try:
                    enrolled = Enrolled.objects.get(student = student_id)
                except Enrolled.DoesNotExist:
                    print("error beacuse of student id :",student_id)
                course = Course.objects.get(id = enrolled.course)
                stream = Stream.objects.get(id = enrolled.stream)
                # logger.info(enrolled)
                # print("print enrolled error:",enrolled)
                # print(enrolled.course_pattern)
                obj = {
                    "name":str(i.name),
                    "father_name":i.father_name,
                    "mother_name":i.mother_name,
                    "dateofbirth":datetime.strptime(str(i.dateofbirth), '%Y-%m-%d').strftime('%d/%m/%Y'),
                    "mobile":i.mobile,
                    "email":i.email,
                    "gender":i.gender,
                    "category":i.category,
                    "enrollment_id":i.enrollment_id,
                    "enrollment_date":str(i.enrollment_date),
                    "registration_id":i.registration_id,
                    "course":course.name,
                    "stream":stream.name,
                    "semyear":enrolled.current_semyear,
                    "course_pattern":enrolled.course_pattern,
                    "session":enrolled.session,
                    "entry_mode":enrolled.entry_mode,
                    "university":university.university_name
                }
                studentlist.append(obj)
                
            od2 = json.dumps(studentlist,indent=4)
            # print(od2)
            file_object = open('static/dict/sample.txt', 'a')
            file_object.write('{"data": '+od2+'}')
            file_object.close()
            
        else:
            print("no")
    params = {
        "display":display,
        "level_of_user":level_of_user,
        'allstudents' : Student.objects.filter(verified=False).order_by('-id'),
        'dataSet':od2
    }
    return render(request,"pendingverification.html",params)

@login_required(login_url='/login/')
def RegisteredStudent(request):
    display = ""
    level_of_user = ""
    od2 = []
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4" or level.level =="2":
            display = "yes"
            level_of_user = level.level
            if request.method == "POST":
                show_profile_pic = request.POST.get('show_profile_pic')
                if show_profile_pic:
                    getstudent = Student.objects.get(enrollment_id = show_profile_pic)
                    
                    if getstudent.image == "False":
                        return JsonResponse({'image':'no'})
                    else:
                        student_serializer = StudentSerializer(getstudent,many=False)
                        return JsonResponse({'image':student_serializer.data})
                attach = request.FILES.get("send_reciept_file")
                send_reciept_student_id = request.POST.get('send_reciept_student_id')
                send_reciept_paidamount = request.POST.get('send_reciept_paidamount')
                if send_reciept_student_id and attach and send_reciept_paidamount:
                    print(send_reciept_student_id,attach,send_reciept_paidamount)
                    getstudent = Student.objects.get(id = send_reciept_student_id)
                    subject = "CIIS Payment Reciept"
                    message = '''Thankyou For Making Payment of rs {} \n
    CIIS INDIA \n
    Payment Reciept is attached with this Email. \n
    '''.format(send_reciept_paidamount)
                    recipient_list = [getstudent.email]
                    # print(message)
                    
                    
                    mail = EmailMessage(
                        subject
                        , message
                        , settings.EMAIL_HOST_USER,
                        recipient_list)
                    mail.attach("invoice.pdf", attach.read(), attach.content_type)
                    mail.send()
                    return JsonResponse({'sent_mail':'yes'})
                else:
                    print("nope")
                send_reciept = request.POST.get('send_reciept')
                if send_reciept:
                    getstudent = Student.objects.get(enrollment_id = send_reciept)
                    getlatest_reciept = PaymentReciept.objects.filter(Q(student = getstudent.id) & Q(payment_for="Course Fees")).latest('id')
                    studentserializer = StudentSerializer(getstudent,many=False)
                    paymentserializer = PaymentRecieptSerializer(getlatest_reciept,many=False)
                    print(getlatest_reciept,getlatest_reciept.semyearfees,getlatest_reciept.paidamount,getlatest_reciept.advanceamount,getlatest_reciept.pendingamount)
                    return JsonResponse({'sent':'yes','student':studentserializer.data,'payment_reciept':paymentserializer.data})

                cancel_student_id = request.POST.get('cancel_student_id')
                cancel_student_status = request.POST.get('cancel_student_status')
                if cancel_student_id and cancel_student_status:
                    print("ID :",cancel_student_id," Status :",cancel_student_status)
                    getstudent = Student.objects.get(id = cancel_student_id)
                    
                    
                    if cancel_student_status == "In-Active":
                        print("inactive")
                        getstudent.is_cancelled = True
                        getstudent.archive = True
                        getstudent.enrolled = False
                        getstudent.save()
                        return JsonResponse({'success':'yes'})

                cancel_student = request.POST.get('cancel_student')
                if cancel_student:
                    getstudent = Student.objects.get(enrollment_id = cancel_student)
                    print("Get Student :",getstudent)
                    studentserializer = StudentSerializer(getstudent,many=False)
                    return JsonResponse({'data':studentserializer.data})
                refund_fees_student_id = request.POST.get('refund_fees_student_id')
                refund_fees_amount = request.POST.get('refund_fees_amount')
                refund_fees_feestype = request.POST.get('refund_fees_feestype')
                refund_fees_semyear = request.POST.get('refund_fees_semyear')
                refund_fees_transactiondate = request.POST.get('refund_fees_transactiondate')
                refund_fees_paymentmode = request.POST.get('refund_fees_paymentmode')
                refund_fees_chequeno = request.POST.get('refund_fees_chequeno')
                refund_fees_bankname = request.POST.get('refund_fees_student_id')
                refund_fees_remarks = request.POST.get('refund_fees_remarks')
                if refund_fees_student_id and refund_fees_amount and refund_fees_feestype and refund_fees_transactiondate and refund_fees_paymentmode and refund_fees_paymentmode and refund_fees_remarks:
                    try:
                        getstudent = Student.objects.get(enrollment_id = refund_fees_student_id)
                        try:
                            getlatestreciept = PaymentReciept.objects.latest('id')
                        except PaymentReciept.DoesNotExist:
                            getlatestreciept = "none"
                        if getlatestreciept == "none":
                            transactionID = "TXT445FE101"
                        else:
                            tid = getlatestreciept.transactionID
                            tranx = tid.replace("TXT445FE",'')
                            transactionID =  str("TXT445FE") + str(int(tranx) + 1)
                        print(transactionID)
                        
                        add_payment_reciept = PaymentReciept(
                            student = getstudent.id,
                            payment_for="Refund",
                            payment_type=refund_fees_feestype,
                            fee_reciept_type="",
                            transaction_date= refund_fees_transactiondate,
                            cheque_no=refund_fees_chequeno,
                            bank_name=refund_fees_bankname,
                            paidamount=refund_fees_amount,
                            pendingamount="0",
                            transactionID = transactionID,
                            paymentmode=refund_fees_paymentmode,
                            remarks=refund_fees_remarks,
                            session="",
                            semyear=refund_fees_semyear)
                        add_payment_reciept.save()

                        getfeespaid = PaymentReciept.objects.filter(student = getstudent.id)
                        
                        feeserializer = PaymentRecieptSerializer(getfeespaid,many=True)
                        return JsonResponse({'success':'yes','fees':feeserializer.data,'student_id':getstudent.id})
                    except Student.DoesNotExist:
                        pass
                update_reciept_id = request.POST.get('update_reciept_id')
                update_reciept_status = request.POST.get('update_reciept_status')
                if  update_reciept_id and update_reciept_status:
                    print("ID :",update_reciept_id, " Status :",update_reciept_status)
                    getreciept = PaymentReciept.objects.get(id = update_reciept_id)
                    if update_reciept_status == "Realised":

                        total_fees = getreciept.semyearfees
                        paid_fees = getreciept.uncleared_amount
                        print(total_fees , paid_fees)
                        if int(paid_fees) > int(total_fees):
                            getreciept.advanceamount = int(paid_fees) - int(total_fees)
                            getreciept.paidamount = int(paid_fees)
                            getreciept.pendingamount = 0
                            getreciept.uncleared_amount = 0
                        elif int(paid_fees) < int(total_fees):
                            getreciept.advanceamount = 0
                            getreciept.paidamount = int(paid_fees)
                            getreciept.pendingamount = int(total_fees) - int(paid_fees)
                            getreciept.uncleared_amount = 0
                        elif int(paid_fees) == int(total_fees):
                            getreciept.advanceamount = 0
                            getreciept.paidamount = int(paid_fees)
                            getreciept.pendingamount = int(total_fees) - int(paid_fees)
                            getreciept.uncleared_amount = 0
                    else:
                        total_fees = int(getreciept.semyearfees)
                        paid_fees = int(getreciept.paidamount)
                        advance_fees = int(getreciept.advanceamount)
                        pending_fees = int(getreciept.pendingamount)
                        uncleared_fees = int(getreciept.uncleared_amount)
                        print(total_fees , paid_fees , advance_fees , pending_fees , uncleared_fees)
                        if advance_fees > 0:
                            getreciept.uncleared_amount = paid_fees
                            getreciept.advanceamount = 0
                            getreciept.paidamount = 0
                            getreciept.pendingamount = total_fees
                        else:
                            getreciept.uncleared_amount = paid_fees
                            getreciept.advanceamount = 0
                            getreciept.paidamount = 0
                            getreciept.pendingamount = total_fees
                        # getreciept.uncleared_amount = getreciept.paidamount
                        # getreciept.pendingamount = int(getreciept.pendingamount) + int(getreciept.paidamount)
                        # getreciept.paidamount = 0
                    getreciept.status = update_reciept_status
                    getreciept.save()
                    getallreciept = PaymentReciept.objects.filter(Q(student = getreciept.student) & Q(paymentmode = "Cheque"))
                    paymentSerializer = PaymentRecieptSerializer(getallreciept,many=True)
                    return JsonResponse({'data':paymentSerializer.data})
                update_payment = request.POST.get('update_payment')
                if update_payment:
                    getstudent = Student.objects.get(enrollment_id = update_payment)
                    getpaymentreciepts = PaymentReciept.objects.filter(Q(student = getstudent.id) & Q(paymentmode = "Cheque"))
                    paymentSerializer = PaymentRecieptSerializer(getpaymentreciepts,many=True)
                    return JsonResponse({'data':paymentSerializer.data})
                personal_update_document = request.POST.get('personal_update_document')
                personal_update_DocumentName = request.POST.get('personal_update_DocumentName')
                personal_upload_DocumentID = request.POST.get('personal_upload_DocumentID')
                personal_upload_Documents = request.FILES.getlist('personal_uploaded_file')
                personal_student_enrollment_id = request.POST.get('personal_student_enrollment_id')
                if personal_student_enrollment_id or personal_update_document or personal_update_DocumentName or personal_upload_DocumentID or personal_upload_Documents:
                    try:
                        getstudent = Student.objects.get(enrollment_id = personal_student_enrollment_id)
                        print("getstudent : ",getstudent)
                        add_personal_document = PersonalDocuments(document=personal_update_document,document_name=personal_update_DocumentName,document_ID_no=personal_upload_DocumentID,student=getstudent.id)
                        add_personal_document.save()
                        getpersonaldocuments = PersonalDocuments.objects.latest('id')
                        for i in personal_upload_Documents:
                            add_personal_document_images = PersonalDocumentsImages(document = getpersonaldocuments,document_image=i)
                            add_personal_document_images.save()
                        return JsonResponse({'added':'yes'})
                    except Student.DoesNotExist:
                        pass
                
                show_personal_documents = request.POST.get('show_personal_documents')
                if show_personal_documents:
                    maindata = []
                    try:
                        getstudent = Student.objects.get(id = show_personal_documents)
                        get_personal_documents = PersonalDocuments.objects.filter(student = getstudent.id)
                        if get_personal_documents:
                            for i in get_personal_documents:
                                temp = []
                                getpersonaldocumentimages = PersonalDocumentsImages.objects.filter(document = i)
                                personaldocumentimagesserializer = PersonalDocumentsImagesSerializer(getpersonaldocumentimages,many=True)
                                
                                obj = {
                                    "id":i.id,
                                    "document":i.document,
                                    "document_name":i.document_name,
                                    "document_ID_no":i.document_ID_no,
                                    "document_Images":personaldocumentimagesserializer.data
                                }
                                print(obj)
                                maindata.append(obj)
                            return JsonResponse({'data':maindata})
                        else:
                            print("no data")
                    except Student.DoesNotExist:
                        pass
                get_personal_images = request.POST.get('get_personal_images')
                if get_personal_images:
                    print("get_personal_images : ",get_personal_images)
                    try:
                        get_personal_documents = PersonalDocuments.objects.get(id = get_personal_images)
                        getpersonaldocumentimages = PersonalDocumentsImages.objects.filter(document = get_personal_documents)
                        print("getpersonaldocumentimages : ",getpersonaldocumentimages)
                        personaldocumentimagesserializer = PersonalDocumentsImagesSerializer(getpersonaldocumentimages,many=True)
                        return JsonResponse({'data':personaldocumentimagesserializer.data})
                    except PersonalDocuments.DoesNotExist:
                        print("document not present")


                ens_student_id = request.POST.get('ens_student_id')
                ens_total_semyear = request.POST.get('ens_total_semyear')
                ens_current_semyear = request.POST.get('ens_current_semyear')
                ens_next_semyear = request.POST.get('ens_next_semyear')
                if ens_student_id and ens_total_semyear and ens_current_semyear and ens_next_semyear:
                    print(ens_student_id , ens_total_semyear ,ens_current_semyear , ens_next_semyear )
                    if ens_total_semyear > ens_current_semyear:
                        try:
                            getenroll = Enrolled.objects.get(student = ens_student_id)
                            getenroll.current_semyear = ens_next_semyear
                            getenroll.save()
                            print("enrolled")
                            return JsonResponse({'enrolled':'yes'})
                        except Enrolled.DoesNotExist:
                            pass

                enroll_to_next_semester = request.POST.get('enroll_to_next_semester')
                if enroll_to_next_semester:
                    try:
                        getstudent = Student.objects.get(enrollment_id = enroll_to_next_semester)
                        enroll = Enrolled.objects.get(student = getstudent.id)
                        paymentreciept = PaymentReciept.objects.filter(Q(student = getstudent.id) & Q(semyear = enroll.current_semyear))
                        pending_reciept_list = []
                        for i in paymentreciept:
                            pending_reciept_list.append(i.pendingamount)
                        print(pending_reciept_list)
                        checkpaid = ""
                        for i in pending_reciept_list:
                            if int(i) == 0 or int(i) < 0:
                                checkpaid = "yes"
                        
                        course = Course.objects.get(id = enroll.course)
                        stream = Stream.objects.get(id = enroll.stream)
                        can_enroll = ""
                        if enroll.course_pattern == "Semester":
                            if enroll.total_semyear != enroll.current_semyear:
                                can_enroll = int(enroll.current_semyear) + 1
                            else:
                                can_enroll = "no"
                        else:
                            print("Annual")
                            if enroll.total_semyear != enroll.current_semyear:
                                can_enroll = int(enroll.current_semyear) + 1
                            else:
                                can_enroll = "no"
                        obj = {
                            "course":course.name,
                            "stream":stream.name,
                            "total_semyear":enroll.total_semyear,
                            "current_semyear":enroll.current_semyear,
                            "can_enroll":can_enroll
                        }
                        if checkpaid == "yes":
                            return JsonResponse({'clear':'yes','student':getstudent.id,'enroll':obj})
                        else:
                            return JsonResponse({'clear':'no','student':getstudent.id})
                        # if '0' in pending_reciept_list:
                        #     return JsonResponse({'clear':'yes'})
                        # else:
                        #     return JsonResponse({'clear':'no'})
                    except Student.DoesNotExist:
                        print("student not available")
                sendremainder = request.POST.get('sendremainder')
                if sendremainder:
                    try:
                        getstudent = Student.objects.get(enrollment_id = sendremainder)
                        getenroll = Enrolled.objects.get(student = getstudent.id)
                        try:
                            getpaymentreciept = PaymentReciept.objects.filter(Q(student = getstudent.id) & Q(semyear = getenroll.current_semyear))
                            feespendinglist = []
                            # SaveStudentTransaction
                            for i in getpaymentreciept:
                                print(i.paidamount , i.pendingamount)
                                feespendinglist.append(i.pendingamount)
                            print("feespendinglist =",feespendinglist)
                            if '0' in feespendinglist:
                                return JsonResponse({'pending':'no'})
                            else:
                                getpendingreciept = PaymentReciept.objects.get(Q(student = getstudent.id) & Q(semyear = getenroll.current_semyear) & ~Q(pendingamount="0"))
                                getlatestreciept = PaymentReciept.objects.latest('id')
                                transactionid = getlatestreciept.transactionID
                                tranx = transactionid.replace("TXT445FE",'')
                                transactionID =  str("TXT445FE") + str(int(tranx) + 1)
                                payu_config = settings.PAYU_CONFIG
                                merchant_key = payu_config.get('merchant_key')
                                merchant_salt = payu_config.get('merchant_salt')
                                surl = payu_config.get('success_url')
                                furl = payu_config.get('failure_url')
                                mode = payu_config.get('mode')
                                payu = Payu(merchant_key, merchant_salt, surl, furl, mode)
                                
                                data = {
                                    'amount': i.pendingamount, 'firstname': getstudent.name,
                                    'email': getstudent.email,
                                    'phone': getstudent.mobile, 'productinfo': 'test',  'lastname': getstudent.name, 'address1': getstudent.address,
                                    'address2': 'test', 'city': getstudent.city,  'state': getstudent.state, 'country': getstudent.country,
                                    'zipcode': getstudent.pincode, 'udf1': '', 'udf2': '', 'udf3': '', 'udf4': '', 'udf5': '',
                                    'surl':surl,
                                    'furl':furl
                                }
                                # Make sure the transaction ID is unique
                                txnid = transactionID
                                data.update({"txnid": txnid})
                                payu_data = payu.transaction(**data)
                                print(payu_data)
                                create_hash = str(payu_data['firstname']) + str(payu_data['lastname']) + str(payu_data['email']) + str(payu_data['amount']) + str(txnid) + str(datetime.now())
                                hash_object = hashlib.md5(create_hash.encode())
                                random = hash_object.hexdigest()
                                print(random)
                                try:
                                    studenttransaction = SaveStudentTransaction.objects.get(student_identifier = random)
                                except SaveStudentTransaction.DoesNotExist:
                                    # pass
                                    studenttransactionfilter = SaveStudentTransaction.objects.filter(student = getstudent.id)
                                    studenttransactionfilter.delete()
                                    res = sm(
                                        subject = "CIIS Payment Link",
                                        message = '''Please Pay Your Outstanding Fees From The Link Given Below \n
                                        CIIS INDIA \n
                                        Click on the link below to Pay \n
                                        https://erp.ciisindia.in/payment/{}'''.format(random),
                                        from_email = 'testmail@erp.ciisindia.in',
                                        recipient_list = [payu_data['email']],
                                        fail_silently=False,
                                            )
                                    addstudenttransaction = SaveStudentTransaction(student_identifier= random,key=payu_data['key'],txnid=txnid,productinfo=payu_data['productinfo'],amount=payu_data['amount'],email=payu_data['email'],firstname=payu_data['firstname'],lastname=payu_data['lastname'],phone=payu_data['phone'],surl=payu_data['surl'],furl=payu_data['furl'],hash=payu_data['hashh'],student=getstudent.id,status="pending")
                                    addstudenttransaction.save()
                                return JsonResponse({'pending':'yes','data':payu_data})
                        except PaymentReciept.DoesNotExist:
                            pass
                    except Student.DoesNotExist:
                        pass
                remarks = request.POST.get('remarks')
                if remarks:
                    print("remarks :",remarks)
                    try:
                        getstudent = Student.objects.get(enrollment_id = remarks)
                        getreciept = PaymentReciept.objects.filter(student = getstudent.id)
                        paymentrecieptserializer = PaymentRecieptSerializer(getreciept,many=True)
                        return JsonResponse({'payment_reciept':paymentrecieptserializer.data})
                    except Student.DoesNotExist:
                        pass
                    
                getpayment_reciept = request.POST.get('getpayment_reciept')
                if getpayment_reciept:
                    print(getpayment_reciept)
                    get_reciept = PaymentReciept.objects.get(id = getpayment_reciept)
                    paymentrecieptserializer = PaymentRecieptSerializer(get_reciept,many=False)
                    view_student = Student.objects.get(id=get_reciept.student)
                    view_enroll = Enrolled.objects.get(student=view_student.id)
                    view_course = Course.objects.get(id = view_enroll.course)
                    view_stream = Stream.objects.get(id = view_enroll.stream)
                    temp = {
                        "name":view_student.name,
                        "email":view_student.email,
                        "mobile":view_student.mobile,
                        "enrollment_id":view_student.enrollment_id,
                        "address":view_student.address,
                        "country":view_student.country,
                        "state":view_student.state,
                        "city":view_student.city,
                        "pincode":view_student.pincode,
                        "course":view_course.name,
                        "stream":view_stream.name
                    }
                    return JsonResponse({'view_reciept':paymentrecieptserializer.data,'personal':temp})
                
                upload_document_student_id = request.POST.get('upload_document_student_id')
                upload_qualification_name = request.POST.get('upload_qualification_name')
                upload_qualification_year = request.POST.get('upload_qualification_year')
                upload_qualification_board = request.POST.get('upload_qualification_board')
                upload_qualification_percentage = request.POST.get('upload_qualification_percentage')
                upload_qualification_document = request.FILES.get('upload_qualification_document', False)
                
                if upload_document_student_id and upload_qualification_name and  upload_qualification_year and upload_qualification_board and upload_qualification_percentage and upload_qualification_document:
                    try:
                        getqualification = Qualification.objects.get(id = upload_document_student_id)
                        if upload_qualification_name == "Secondary/High School":
                            if upload_qualification_year:
                                getqualification.secondary_year = upload_qualification_year
                            if upload_qualification_board:
                                getqualification.secondary_board = upload_qualification_board
                            if upload_qualification_percentage:
                                getqualification.secondary_percentage = upload_qualification_percentage
                            if upload_qualification_document:
                                getqualification.secondary_document = upload_qualification_document
                            getqualification.save()

                        elif upload_qualification_name == "Sr. Secondary":
                            if upload_qualification_year:
                                getqualification.sr_year = upload_qualification_year
                            if upload_qualification_board:
                                getqualification.sr_board = upload_qualification_board
                            if upload_qualification_percentage:
                                getqualification.sr_percentage = upload_qualification_percentage
                            if upload_qualification_document:
                                getqualification.sr_document = upload_qualification_document
                            getqualification.save()

                        elif upload_qualification_name == "Under Graduation":
                            if upload_qualification_year:
                                getqualification.under_year = upload_qualification_year
                            if upload_qualification_board:
                                getqualification.under_board = upload_qualification_board
                            if upload_qualification_percentage:
                                getqualification.under_percentage = upload_qualification_percentage
                            if upload_qualification_document:
                                getqualification.under_document = upload_qualification_document
                            getqualification.save()

                        elif upload_qualification_name == "Post Graduation":
                            if upload_qualification_year:
                                getqualification.post_year = upload_qualification_year
                            if upload_qualification_board:
                                getqualification.post_board = upload_qualification_board
                            if upload_qualification_percentage:
                                getqualification.post_percentage = upload_qualification_percentage
                            if upload_qualification_document:
                                getqualification.post_document = upload_qualification_document
                            getqualification.save()

                        elif upload_qualification_name == "M.Phil":
                            if upload_qualification_year:
                                getqualification.mphil_year = upload_qualification_year
                            if upload_qualification_board:
                                getqualification.mphil_board = upload_qualification_board
                            if upload_qualification_percentage:
                                getqualification.mphil_percentage = upload_qualification_percentage
                            if upload_qualification_document:
                                getqualification.mphil_document = upload_qualification_document
                            getqualification.save()

                        elif upload_qualification_name == "Others":
                            if upload_qualification_year:
                                getqualification.others_year = upload_qualification_year
                            if upload_qualification_board:
                                getqualification.others_board = upload_qualification_board
                            if upload_qualification_percentage:
                                getqualification.others_percentage = upload_qualification_percentage
                            if upload_qualification_document:
                                getqualification.others_document = upload_qualification_document
                            getqualification.save()

                        getqualification = Qualification.objects.get(id = upload_document_student_id)
                        qualificationserializer = QualificationSerializer(getqualification,many=False)
                        return JsonResponse({'qualification':qualificationserializer.data})

                        
                        

                    except Qualification.DoesNotExist:
                        pass
                
                
                
                
                studentsyllabus_student_id = request.POST.get('studentsyllabus_student_id')
                studentsyllabus_semester = request.POST.get('studentsyllabus_semester')
                studentsyllabus_file = request.FILES.get('studentsyllabus_file', False)
                if studentsyllabus_student_id and studentsyllabus_semester and studentsyllabus_file:
                    try:
                        getstudentsyllabus = StudentSyllabus.objects.get(Q(student = studentsyllabus_student_id) & Q(semester = studentsyllabus_semester))
                        print("yes student syllabus")
                    except StudentSyllabus.DoesNotExist:
                        addstudentsyllabus = StudentSyllabus(student=studentsyllabus_student_id,semester=studentsyllabus_semester,pdf=studentsyllabus_file)
                        addstudentsyllabus.save()
                        getlateststudentsyllabus = StudentSyllabus.objects.get(Q(student=studentsyllabus_student_id) & Q(semester=studentsyllabus_semester))
                        lateststudentsyllabusserializer = StudentSyllabusSerializer(getlateststudentsyllabus,many=False)
                        return JsonResponse({'data':lateststudentsyllabusserializer.data})

                
                
                
                
                resultuploaded = request.POST.get('resultuploaded')
                if resultuploaded:
                    try:
                        getstudent = Student.objects.get(enrollment_id = resultuploaded)
                        getresult = StudentDocuments.objects.filter(student = getstudent.id)
                        getresultserializer = StudentDocumentsSerializer(getresult,many=True)
                        return JsonResponse({'result':getresultserializer.data,'student':getstudent.id})
                        
                    except Student.DoesNotExist:
                        pass
                
                upload_student_id = request.POST.get('upload_student_id')
                upload_document = request.POST.get('upload_document')
                upload_document_name = request.POST.get('upload_document_name')
                upload_document_id = request.POST.get('upload_document_id')
                document_file_front = request.FILES.get('document_file_front', False)
                document_file_back = request.FILES.get('document_file_back', False)
                
                if upload_student_id and upload_document or (upload_document_name or upload_document_id) or (document_file_front or document_file_back):
                    try:
                        getdocument = StudentDocuments.objects.get(Q(student = upload_student_id) & Q(document=upload_document))
                        print("Get Document : ", getdocument)
                        if upload_document_name:
                            getdocument.document_name = upload_document_name
                            getdocument.save()
                        if upload_document_id:
                            getdocument.document_ID_no = upload_document_id
                            getdocument.save()
                        if document_file_front:
                            getdocument.document_image_front = document_file_front
                            getdocument.save()
                        if document_file_back:
                            getdocument.document_image_back = document_file_back
                            getdocument.save()
                        getalldocuments = StudentDocuments.objects.filter(student=upload_student_id)
                        studentdocumentserializer = StudentDocumentsSerializer(getalldocuments,many=True)
                        return JsonResponse({'added':'yes','documents':studentdocumentserializer.data})
                    except StudentDocuments.DoesNotExist:
                        adddocument = StudentDocuments(student=upload_student_id,document=upload_document,document_name=upload_document_name,document_ID_no=upload_document_id,document_image_front=document_file_front,document_image_back=document_file_back)
                        adddocument.save()
                        getalldocuments = StudentDocuments.objects.filter(student=upload_student_id)
                        studentdocumentserializer = StudentDocumentsSerializer(getalldocuments,many=True)
                        return JsonResponse({'added':'yes','documents':studentdocumentserializer.data})



                 
                
                
                payment_gateway = request.POST.get('payment_gateway')
                if payment_gateway:
                    try:
                        getstudent = Student.objects.get(enrollment_id = payment_gateway)
                        studentserializer = StudentSerializer(getstudent,many=False)
                        try:
                            paymentgatewaylatest = TestPaymentGateway.objects.latest('id')
                            trans_id = int(paymentgatewaylatest.transactionID) + 8545
                            addnewpaymentgatewaylatest = TestPaymentGateway(student = getstudent.id , transactionID = trans_id)
                            addnewpaymentgatewaylatest.save()
                        except TestPaymentGateway.DoesNotExist:
                            paymentgatewaylatest = TestPaymentGateway(student = getstudent.id, transactionID="452200124521")
                            paymentgatewaylatest.save()
                        getenroll = Enrolled.objects.get(student = getstudent.id)
                        

                        try:
                            getpaymentreciept = PaymentReciept.objects.filter(Q(student = getstudent.id) & Q(payment_for = "Course Fees") & Q(semyear = getenroll.current_semyear))
                            print(getpaymentreciept)
                            if getpaymentreciept:
                                feespendinglist = []
                                for i in getpaymentreciept:
                                    print(i.paidamount , i.pendingamount)
                                    feespendinglist.append(int(i.pendingamount))
                                minimum_pending = min(feespendinglist)
                                print("minimum_pending : ",minimum_pending)
                                print("feespendinglist =",feespendinglist)
                                if 0 in feespendinglist or minimum_pending < 0:
                                    return JsonResponse({'pending':'no'})
                                else:
                                    print("no")
                                    getlatestpaymentgateway = TestPaymentGateway.objects.latest('id')
                                    transactionid = getlatestpaymentgateway.transactionID
                                    payu_config = settings.PAYU_CONFIG
                                    merchant_key = payu_config.get('merchant_key')
                                    merchant_salt = payu_config.get('merchant_salt')
                                    surl = payu_config.get('success_url')
                                    furl = payu_config.get('failure_url')
                                    mode = payu_config.get('mode')
                                    payu = Payu(merchant_key, merchant_salt, surl, furl, mode)
                                    
                                    data = {
                                        'amount': i.pendingamount, 'firstname': getstudent.name,
                                        'email': getstudent.email,
                                        'phone': getstudent.mobile, 'productinfo': 'test',  'lastname': getstudent.name, 'address1': getstudent.address,
                                        'address2': 'test', 'city': getstudent.city,  'state': getstudent.state, 'country': getstudent.country,
                                        'zipcode': getstudent.pincode, 'udf1': '', 'udf2': '', 'udf3': '', 'udf4': '', 'udf5': '',
                                        'surl':surl,
                                        'furl':furl
                                    }
                                    # Make sure the transaction ID is unique
                                    txnid = transactionid
                                    data.update({"txnid": txnid})
                                    payu_data = payu.transaction(**data)
                                    print("Payu Data : ",payu_data)
                                    return JsonResponse({'pending':'yes','amount':i.pendingamount,'transactionData':payu_data,'student_data':studentserializer.data})
                            else:
                                print("no fees paid for current semester")
                                try:
                                    getstudentfees = StudentFees.objects.get(Q(student = getstudent.id) & Q(sem = getenroll.current_semyear))
                                    getlatestpaymentgateway = TestPaymentGateway.objects.latest('id')
                                    transactionid = getlatestpaymentgateway.transactionID
                                    payu_config = settings.PAYU_CONFIG
                                    merchant_key = payu_config.get('merchant_key')
                                    merchant_salt = payu_config.get('merchant_salt')
                                    surl = payu_config.get('success_url')
                                    furl = payu_config.get('failure_url')
                                    mode = payu_config.get('mode')
                                    payu = Payu(merchant_key, merchant_salt, surl, furl, mode)
                                    
                                    data = {
                                        'amount': getstudentfees.totalfees, 'firstname': getstudent.name,
                                        'email': getstudent.email,
                                        'phone': getstudent.mobile, 'productinfo': 'test',  'lastname': getstudent.name, 'address1': getstudent.address,
                                        'address2': 'test', 'city': getstudent.city,  'state': getstudent.state, 'country': getstudent.country,
                                        'zipcode': getstudent.pincode, 'udf1': '', 'udf2': '', 'udf3': '', 'udf4': '', 'udf5': '',
                                        'surl':surl,
                                        'furl':furl
                                    }
                                    # Make sure the transaction ID is unique
                                    txnid = transactionid
                                    data.update({"txnid": txnid})
                                    payu_data = payu.transaction(**data)
                                    print("Payu Data : ",payu_data)
                                    return JsonResponse({'pending':'yes','amount':getstudentfees.totalfees,'transactionData':payu_data,'student_data':studentserializer.data})
                                except StudentFees.DoesNotExist:
                                    pass
                        except PaymentReciept.DoesNotExist:
                            print("payment reciept not found")
                    except Student.DoesNotExist:
                        pass

                email_ID = request.POST.get('email_ID')
                amount = request.POST.get('request_amount')
                request_payment_categories = request.POST.get('request_payment_categories')
                request_payment_type = request.POST.get('request_payment_type')
                email_subject = request.POST.get('subject')
                email_message = request.POST.get('email_message')
                fetch_message = request.POST.get('fetch_message')
                if fetch_message:
                    # print("amount : ",amount)
                    mail_body = f'''\n
Dear Students,\n
Pending Amount :- Rs.{amount}/-\n
Clear the outstanding dues for the Semester / Year on an urgent basis. The cooperation and understanding are desired for the smooth functioning of the Organisation. Kindly pay the entire pending fee to avoid inconvenience.\n


                    

                    

NOTE:  Dear Student: (Pl ignore if already Paid.)

we wish to thank you for your continued support throughout the Academic Year. 

C.I.I.S
                    '''
                    # print(mail_body)
                    return JsonResponse({'message':mail_body})
                if email_subject and email_ID and email_message:
                    # print(email_subject , email_ID , email_message)
                    print(amount,request_payment_categories,request_payment_type)
                    res = sm(
                    subject = email_subject,
                    message = email_message,
                    from_email = 'testmail@erp.ciisindia.in',
                    recipient_list = [email_ID],
                    fail_silently=False,
                        )
                    getstudent = Student.objects.get(email=email_ID)
                    add_new_email_sent_history = EmailSentHistory(student = getstudent.id,
                        amount = amount,
                        type="request_fees",
                        email = email_ID,
                        subject = email_subject,
                        body = email_message,
                        payment_categories = request_payment_categories,
                        payment_type = request_payment_type
                        
                        )
                    add_new_email_sent_history.save()
                    return JsonResponse({'sent':'yes'})
                requestFees = request.POST.get('requestFees')
                if requestFees:
                    print("yupp")
                    try:
                        getstudent = Student.objects.get(enrollment_id = requestFees)
                        getpaymentreciept = PaymentReciept.objects.filter(student = getstudent.id)
                        getlatest = getpaymentreciept.latest('id')
                        print(getlatest.paidamount, getlatest.pendingamount)
                        obj = {
                            "paidamount":getlatest.paidamount,
                            "pendingamount":getlatest.pendingamount,
                            "student_id":getstudent.id
                            
                        }
                        return JsonResponse({'email':getstudent.email,'data':obj})
                    except Student.DoesNotExist:
                        pass
                get_request_fees_history = request.POST.get('get_request_fees_history')
                if get_request_fees_history:
                    gethistory = EmailSentHistory.objects.filter(Q(student = get_request_fees_history ) & Q(type = "request_fees"))
                    gethistoryserializer = EmailSentHistorySerializer(gethistory,many=True)
                    return JsonResponse({'data':gethistoryserializer.data})
                    print(gethistory)
                
                

                newuniversityenrollment_id = request.POST.get('newuniversityenrollment_id')
                if newuniversityenrollment_id:
                    try:
                        getstudent = Student.objects.get(enrollment_id = newuniversityenrollment_id)
                        getnewuniversityenrollment = UniversityEnrollment.objects.filter(Q(student = getstudent.id) & Q(type="new"))
                        getnewuniversityenrollmentserializer = UniversityEnrollmentSerializer(getnewuniversityenrollment,many=True)
                        return JsonResponse({'student_id':getstudent.id,'data':getnewuniversityenrollmentserializer.data})
                    except Student.DoesNotExist:
                        return JsonResponse({'student':'no'})

                getnewuniversity_enrollment_details = request.POST.get('getnewuniversity_enrollment_details')
                if getnewuniversity_enrollment_details:
                    try:
                        getstudent = Student.objects.get(id = getnewuniversity_enrollment_details)
                        getuniversity = University.objects.all()
                        getuniversityserializer = UniversitySerializer(getuniversity,many=True)
                        return JsonResponse({'university':getuniversityserializer.data,'student_id':getstudent.id})
                    except Student.DoesNotExist:
                        return JsonResponse({'student':'no'})
                get_course = request.GET.get('get_course')
                if get_course:
                    try:
                        getcourse = Course.objects.filter(university = get_course)
                        if getcourse:
                            courseserializer = CourseSerializer(getcourse,many=True)
                            print(courseserializer)
                            return JsonResponse({'course':courseserializer.data})
                    except University.DoesNotExist:
                        print("no university found")

                new_university_enrollment_student_id = request.POST.get('new_university_enrollment_student_id')
                new_university_enrollment_course = request.POST.get('new_university_enrollment_course')
                new_university_enrollment_id = request.POST.get('new_university_enrollment_id')
                new_university_enrollment_type = request.POST.get('new_university_enrollment_type')
                if new_university_enrollment_student_id and new_university_enrollment_course and new_university_enrollment_id and new_university_enrollment_type:
                    print(new_university_enrollment_student_id , new_university_enrollment_course , new_university_enrollment_id , new_university_enrollment_type)
                    getcourse = Course.objects.get(id = new_university_enrollment_course)
                    print(getcourse.name)
                    add_new_university_enrollment_id = UniversityEnrollment(student = new_university_enrollment_student_id,
                        type = new_university_enrollment_type,
                        course_id = new_university_enrollment_course,
                        course_name = getcourse.name,
                        enrollment_id = new_university_enrollment_id)
                    add_new_university_enrollment_id.save()
                    get_new_university_enrollment_id = UniversityEnrollment.objects.filter(Q(student = new_university_enrollment_student_id) & Q(type=new_university_enrollment_type))
                    get_new_university_enrollment_id_serializer = UniversityEnrollmentSerializer(get_new_university_enrollment_id,many=True)
                    return JsonResponse({'data':get_new_university_enrollment_id_serializer.data})


                olduniversityenrollment_id = request.POST.get('olduniversityenrollment_id')
                if olduniversityenrollment_id:
                    try:
                        getstudent = Student.objects.get(enrollment_id = olduniversityenrollment_id)
                        getolduniversityenrollment = UniversityEnrollment.objects.filter(Q(student = getstudent.id) & Q(type="old"))
                        getolduniversityenrollmentserializer = UniversityEnrollmentSerializer(getolduniversityenrollment,many=True)
                        return JsonResponse({'student_id':getstudent.id,'data':getolduniversityenrollmentserializer.data})
                    except Student.DoesNotExist:
                        return JsonResponse({'student':'no'})

                getolduniversity_enrollment_details = request.POST.get('getolduniversity_enrollment_details')
                if getolduniversity_enrollment_details:
                    try:
                        getstudent = Student.objects.get(id = getolduniversity_enrollment_details)
                        getuniversity = University.objects.all()
                        getuniversityserializer = UniversitySerializer(getuniversity,many=True)
                        return JsonResponse({'university':getuniversityserializer.data,'student_id':getstudent.id})
                    except Student.DoesNotExist:
                        return JsonResponse({'student':'no'})
                get_course = request.GET.get('get_course')
                if get_course:
                    try:
                        getcourse = Course.objects.filter(university = get_course)
                        if getcourse:
                            courseserializer = CourseSerializer(getcourse,many=True)
                            print(courseserializer)
                            return JsonResponse({'course':courseserializer.data})
                    except University.DoesNotExist:
                        print("no university found")

                old_university_enrollment_student_id = request.POST.get('old_university_enrollment_student_id')
                old_university_enrollment_course = request.POST.get('old_university_enrollment_course')
                old_university_enrollment_id = request.POST.get('old_university_enrollment_id')
                old_university_enrollment_type = request.POST.get('old_university_enrollment_type')
                if old_university_enrollment_student_id and old_university_enrollment_course and old_university_enrollment_id and old_university_enrollment_type:
                    print(old_university_enrollment_student_id , old_university_enrollment_course , old_university_enrollment_id , old_university_enrollment_type)
                    getcourse = Course.objects.get(id = old_university_enrollment_course)
                    print(getcourse.name)
                    add_old_university_enrollment_id = UniversityEnrollment(student = old_university_enrollment_student_id,
                        type = old_university_enrollment_type,
                        course_id = old_university_enrollment_course,
                        course_name = getcourse.name,
                        enrollment_id = old_university_enrollment_id)
                    add_old_university_enrollment_id.save()
                    get_old_university_enrollment_id = UniversityEnrollment.objects.filter(Q(student = old_university_enrollment_student_id) & Q(type=old_university_enrollment_type))
                    get_old_university_enrollment_id_serializer = UniversityEnrollmentSerializer(get_old_university_enrollment_id,many=True)
                    return JsonResponse({'data':get_old_university_enrollment_id_serializer.data})


                
                courier_student_id = request.POST.get('courier_student_id')
                courier_article_name = request.POST.get('courier_article_name')
                courier_from = request.POST.get('courier_from')
                courier_to = request.POST.get('courier_to')
                courier_booking_date = request.POST.get('courier_booking_date')
                courier_company = request.POST.get('courier_company')
                courier_tracking_id = request.POST.get('courier_tracking_id')
                courier_remarks = request.POST.get('courier_remarks')
                # print(courier_company_name , courier_tracking_id , courier_date , courier_return_date , courier_return_reason , courier_goods_type , courier_remarks , courier_student_id)
                if courier_article_name or courier_from or courier_to or courier_booking_date or courier_company or courier_tracking_id or courier_remarks or courier_student_id:
                    print(courier_article_name , courier_from , courier_to , courier_booking_date , courier_company , courier_tracking_id , courier_remarks , courier_student_id)
                    addcourier = Courier(student=courier_student_id, 
                        article_name = courier_article_name , 
                        courier_from = courier_from , 
                        courier_to = courier_to, 
                        booking_date = courier_booking_date, 
                        courier_company = courier_company , 
                        tracking_id = courier_tracking_id , 
                        remarks = courier_remarks )
                    addcourier.save()
                    getcourier = Courier.objects.filter(student = courier_student_id)
                    courier_serializer = CourierSerializer(getcourier,many=True)
                    
                    return JsonResponse({'saved':'yes','data':courier_serializer.data})
                courier = request.POST.get('courier')
                if courier:
                    
                    try:
                        getstudent = Student.objects.get(enrollment_id = courier)
                        try:
                            getcourier = Courier.objects.filter(student = getstudent.id)
                            courier_serializer = CourierSerializer(getcourier,many=True)
                            if getcourier:
                                return JsonResponse({'courier':'yes','data':courier_serializer.data,'student':getstudent.id})
                            else:
                                return JsonResponse({'courier':'no','student':getstudent.id})
                        except Courier.DoesNotExist:
                            pass
                    except Student.DoesNotExist:
                        pass
                
                courier_id = request.POST.get('courier_id')
                if courier_id:
                    try:
                        getcourier = Courier.objects.get(id=courier_id)
                        courier_getstudent = Student.objects.get(id = getcourier.student)
                        obj = {
                            "name":courier_getstudent.name,
                            "mobile":courier_getstudent.mobile,
                            "email":courier_getstudent.email,
                            "address":courier_getstudent.address,
                            "country":courier_getstudent.country,
                            "state":courier_getstudent.first_name,
                            "city":courier_getstudent.city,
                            "pincode":courier_getstudent.pincode
                        } 
                        courierserializer = CourierSerializer(getcourier,many=False)
                        return JsonResponse({'courier':courierserializer.data,'student':obj})
                    except Courier.DoesNotExist:
                        print("Courier Not Present")
                
                
                syllabus = request.POST.get('syllabus')
                if syllabus:
                    try:
                        getstudent = Student.objects.get(enrollment_id = syllabus)
                        getenroll = Enrolled.objects.get(student=getstudent.id)
                        getstudentsyllabus = StudentSyllabus.objects.filter(student= getstudent.id)
                        getstudentsyllabusserializer = StudentSyllabusSerializer(getstudentsyllabus,many=True)
                        try:
                            getsyllabus = Syllabus.objects.get(Q(course=getenroll.course) & Q(stream = getenroll.stream) & Q(semester = getenroll.current_semyear))
                            syllabus_serializer = SyllabusSerializer(getsyllabus,many=False)
                            getcourse = Course.objects.get(id=getenroll.course)
                            getstream = Stream.objects.get(id = getenroll.stream)
                            study = {
                                "coursename":getcourse.name,
                                "streamname":getstream.name
                            }
                            
                            return JsonResponse({'syllabus':'yes','data':syllabus_serializer.data,'study':study,'student':getstudent.id,'studentsyllabus':getstudentsyllabusserializer.data})
                        except Syllabus.DoesNotExist:
                            return JsonResponse({'syllabus':'na','student':getstudent.id,'studentsyllabus':getstudentsyllabusserializer.data})
                    except Student.DoesNotExist:
                        pass

                documents = request.POST.get('documents')
                if documents:
                    print("got documents")
                    try:       
                        getstudent = Student.objects.get(enrollment_id = documents)
                        try:
                            getqualification = Qualification.objects.get(student= getstudent.id)
                            getqualificationserializer = QualificationSerializer(getqualification,many=False)
                            return JsonResponse({'qualification':getqualificationserializer.data})
                        except Qualification.DoesNotExist:
                            setqualification = Qualification(student=getstudent.id,secondary_year = '',sr_year = '',under_year='',post_year='',mphil_year='',others_year = '',secondary_board='',sr_board='',under_board='',post_board='',mphil_board='',others_board='',secondary_percentage='',sr_percentage='',under_percentage='',post_percentage='',mphil_percentage='',others_percentage='',secondary_document='',sr_document='',under_document='',post_document='',mphil_document='',others_document='')
                            setqualification.save()
                            getqualification = Qualification.objects.get(student= getstudent.id)
                            getqualificationserializer = QualificationSerializer(getqualification,many=False)
                            return JsonResponse({'qualification':getqualificationserializer.data})
                            
                    except Student.DoesNotExist:
                        pass
                universityExamFees = request.POST.get('universityExamFees')
                if universityExamFees:
                    try:
                        getstudent = Student.objects.get(enrollment_id = universityExamFees)
                        getuniversity_examination = UniversityExamination.objects.filter(Q(student = getstudent.id) & Q(type = "University_Exam"))
                        university_examination_serializer = UniversityExaminationSerializer(getuniversity_examination,many=True)
                        
                        return JsonResponse({'student_id':getstudent.id,'data':university_examination_serializer.data})
                    except Student.DoesNotExist:
                        pass
                universityReRegistration = request.POST.get('universityReRegistration')
                if universityReRegistration:
                    try:
                        getstudent = Student.objects.get(enrollment_id = universityReRegistration)
                        getuniversity_examination = UniversityExamination.objects.filter(Q(student = getstudent.id) & Q(type = "University_Re_Registration"))
                        university_examination_serializer = UniversityExaminationSerializer(getuniversity_examination,many=True)
                        
                        return JsonResponse({'student_id':getstudent.id,'data':university_examination_serializer.data})
                    except Student.DoesNotExist:
                        pass
                
                adduniversity_studentid = request.POST.get('adduniversity_studentid')
                adduniversity_amount = request.POST.get('adduniversity_amount')
                adduniversity_date = request.POST.get('adduniversity_date')
                adduniversity_examination = request.POST.get('adduniversity_examination')
                adduniversity_semyear = request.POST.get('adduniversity_semyear')
                adduniversity_paymentmode = request.POST.get('adduniversity_paymentmode')
                adduniversity_remarks = request.POST.get('adduniversity_remarks')
                adduniversity_type = request.POST.get('adduniversity_type')
                if adduniversity_studentid and adduniversity_amount and adduniversity_date and adduniversity_examination and adduniversity_semyear and adduniversity_paymentmode and adduniversity_remarks and adduniversity_type:
                    addnew_universityexamination = UniversityExamination(student = adduniversity_studentid,
                        type = adduniversity_type,
                        amount = adduniversity_amount,
                        date = adduniversity_date,
                        examination = adduniversity_examination,
                        semyear = adduniversity_semyear,
                        paymentmode = adduniversity_paymentmode,
                        remarks = adduniversity_remarks)
                    addnew_universityexamination.save()
                    getuniversity_examination = UniversityExamination.objects.filter(Q(student = adduniversity_studentid) & Q(type = adduniversity_type))
                    university_examination_serializer = UniversityExaminationSerializer(getuniversity_examination,many=True)
                    return JsonResponse({'data':university_examination_serializer.data})
                

                adduniversity_re_registration_studentid = request.POST.get('adduniversity_re_registration_studentid')
                adduniversity_re_registration_amount = request.POST.get('adduniversity_re_registration_amount')
                adduniversity_re_registration_date = request.POST.get('adduniversity_re_registration_date')
                adduniversity_re_registration_examination = request.POST.get('adduniversity_re_registration_examination')
                adduniversity_re_registration_semyear = request.POST.get('adduniversity_re_registration_semyear')
                adduniversity_re_registration_paymentmode = request.POST.get('adduniversity_re_registration_paymentmode')
                adduniversity_re_registration_remarks = request.POST.get('adduniversity_re_registration_remarks')
                adduniversity_re_registration_type = request.POST.get('adduniversity_re_registration_type')
                if adduniversity_re_registration_studentid and adduniversity_re_registration_amount and adduniversity_re_registration_date and adduniversity_re_registration_examination and adduniversity_re_registration_semyear and adduniversity_re_registration_paymentmode and adduniversity_re_registration_remarks and adduniversity_re_registration_type:
                    addnew_universityexamination = UniversityExamination(student = adduniversity_re_registration_studentid,
                        type = adduniversity_re_registration_type,
                        amount = adduniversity_re_registration_amount,
                        date = adduniversity_re_registration_date,
                        examination = adduniversity_re_registration_examination,
                        semyear = adduniversity_re_registration_semyear,
                        paymentmode = adduniversity_re_registration_paymentmode,
                        remarks = adduniversity_re_registration_remarks)
                    addnew_universityexamination.save()
                    getuniversity_examination = UniversityExamination.objects.filter(Q(student = adduniversity_re_registration_studentid) & Q(type = adduniversity_re_registration_type))
                    university_examination_serializer = UniversityExaminationSerializer(getuniversity_examination,many=True)
                    return JsonResponse({'data':university_examination_serializer.data})
                


                is_result_uploaded = request.POST.get('is_result_uploaded')
                if is_result_uploaded:
                    try:
                        getstudent = Student.objects.get(enrollment_id = is_result_uploaded)
                        getresultuploaded = ResultUploaded.objects.filter(student = getstudent.id)
                        getresultuploadedserializer = ResultUploadedSerializer(getresultuploaded,many=True)
                        return JsonResponse({'student_id':getstudent.id,'data':getresultuploadedserializer.data})
                        
                    except Student.DoesNotExist:
                        pass
                addresultuploaded_studentid = request.POST.get('addresultuploaded_studentid')
                addresultuploaded_date = request.POST.get('addresultuploaded_date')
                addresultuploaded_examination = request.POST.get('addresultuploaded_examination')
                addresultuploaded_semyear = request.POST.get('addresultuploaded_semyear')
                addresultuploaded_yn = request.POST.get('addresultuploaded_yn')
                addresultuploaded_remarks = request.POST.get('addresultuploaded_remarks')
                if addresultuploaded_studentid and addresultuploaded_date and addresultuploaded_examination and addresultuploaded_semyear and addresultuploaded_yn and addresultuploaded_remarks:
                    addresultuploaded = ResultUploaded(student = addresultuploaded_studentid,
                        date = addresultuploaded_date,
                        examination = addresultuploaded_examination,
                        semyear = addresultuploaded_semyear,
                        uploaded = addresultuploaded_yn,
                        remarks = addresultuploaded_remarks
                        )
                    addresultuploaded.save()
                    getresultuploaded = ResultUploaded.objects.filter(student = addresultuploaded_studentid)
                    getresultuploadedserializer = ResultUploadedSerializer(getresultuploaded,many=True)
                    return JsonResponse({'data':getresultuploadedserializer.data})

                

                edit_result_uploaded = request.POST.get('edit_result_uploaded')
                if edit_result_uploaded:
                    getresultuploaded = ResultUploaded.objects.get(id = edit_result_uploaded)
                    getresultuploadedserializer = ResultUploadedSerializer(getresultuploaded,many=False)
                    return JsonResponse({'data':getresultuploadedserializer.data})

                editresultuploaded_studentid = request.POST.get('editresultuploaded_studentid')
                editresultuploaded_date = request.POST.get('editresultuploaded_date')
                editresultuploaded_examination = request.POST.get('editresultuploaded_examination')
                editresultuploaded_semyear = request.POST.get('editresultuploaded_semyear')
                editresultuploaded_yn = request.POST.get('editresultuploaded_yn')
                editresultuploaded_remarks = request.POST.get('editresultuploaded_remarks')
                if editresultuploaded_studentid and editresultuploaded_date and editresultuploaded_examination and editresultuploaded_semyear and editresultuploaded_yn and editresultuploaded_remarks:
                    editresultuploaded = ResultUploaded.objects.get(id = editresultuploaded_studentid)
                    editresultuploaded.date = editresultuploaded_date
                    editresultuploaded.examination = editresultuploaded_examination
                    editresultuploaded.semyear = editresultuploaded_semyear
                    editresultuploaded.uploaded = editresultuploaded_yn
                    editresultuploaded.remarks = editresultuploaded_remarks
                    editresultuploaded.save()
                    getresultuploaded = ResultUploaded.objects.filter(student = editresultuploaded.student)
                    getresultuploadedserializer = ResultUploadedSerializer(getresultuploaded,many=True)
                    return JsonResponse({'data':getresultuploadedserializer.data})



                data = request.POST.get('data')
                idcard = request.POST.get('idcard')
                if idcard:
                    getstudent = Student.objects.get(enrollment_id = idcard)
                    university = University.objects.get(registrationID = getstudent.university)
                    obj = {
                        "name":getstudent.name,
                        "dateofbirth":getstudent.dateofbirth,
                        "email":getstudent.email,
                        "mobile":getstudent.mobile,
                        "address":getstudent.address,
                        "city":getstudent.city,
                        "state":getstudent.state,
                        "pincode":getstudent.pincode,
                        "country":getstudent.country,
                        "enrollment_id":getstudent.enrollment_id,
                        "university_name":university.university_name,
                        "university_address":university.university_address,
                        "university_city":university.university_city,
                        "university_state":university.university_state,
                        "university_pincode":university.university_pincode,
                        "university_logo":str(university.university_logo),
                        "registrationID":university.registrationID
                    }
                    return JsonResponse({'idcard':obj})
                
                editpayment_reciept = request.POST.get('editpayment_reciept')
                if editpayment_reciept:
                    try:
                        getreciept = PaymentReciept.objects.get(id = editpayment_reciept)
                        paymentrecieptserializer = PaymentRecieptSerializer(getreciept,many=False)
                        
                        return JsonResponse({'edit':'yes','data':paymentrecieptserializer.data})
                    except PaymentReciept.DoesNotExist:
                        return JsonResponse({'edit':'no'})
                editpayment_payment_reciept_id = request.POST.get('editpayment_payment_reciept_id')
                editpayment_semyear = request.POST.get('editpayment_semyear')
                editpayment_session = request.POST.get('editpayment_session')
                editpayment_fees_reciept_type = request.POST.get('editpayment_fees_reciept_type')
                editpayment_date_of_transaction = request.POST.get('editpayment_date_of_transaction')
                editpayment_payment_for = request.POST.get('editpayment_payment_for')
                editpayment_payment_type = request.POST.get('editpayment_payment_type')
                editpayment_total_fees = request.POST.get('editpayment_total_fees')
                editpayment_advance_fees = request.POST.get('editpayment_advance_fees')
                print(editpayment_advance_fees)
                editpayment_paid_fees = request.POST.get('editpayment_paid_fees')
                editpayment_pending_fees = request.POST.get('editpayment_pending_fees')
                editpayment_payment_mode = request.POST.get('editpayment_payment_mode')
                editpayment_cheque_no = request.POST.get('editpayment_cheque_no')
                editpayment_b_name = request.POST.get('editpayment_b_name')
                editpayment_remarks = request.POST.get('editpayment_remarks')
                if editpayment_payment_reciept_id:
                    try:
                        getpaymentreciept = PaymentReciept.objects.get(id = editpayment_payment_reciept_id)
                        if editpayment_semyear == getpaymentreciept.semyear:
                            pass
                        else:
                            getpaymentreciept.semyear = editpayment_semyear
                        # -----------------------------------------------------------!
                        if editpayment_session == getpaymentreciept.session:
                            pass
                        else:
                            getpaymentreciept.session = editpayment_session
                        # -----------------------------------------------------------!
                        if editpayment_fees_reciept_type == getpaymentreciept.fee_reciept_type:
                            pass
                        else:
                            getpaymentreciept.fee_reciept_type = editpayment_fees_reciept_type
                        # -----------------------------------------------------------!
                        if editpayment_date_of_transaction == getpaymentreciept.transaction_date:
                            pass
                        else:
                            getpaymentreciept.transaction_date = editpayment_date_of_transaction
                        # -----------------------------------------------------------!
                        if editpayment_payment_for == getpaymentreciept.payment_for:
                            pass
                        else:
                            getpaymentreciept.payment_for = editpayment_payment_for
                        # -----------------------------------------------------------!
                        if editpayment_payment_type == getpaymentreciept.payment_type:
                            pass
                        else:
                            getpaymentreciept.payment_type = editpayment_payment_type
                        # -----------------------------------------------------------!
                        if editpayment_paid_fees == getpaymentreciept.paidamount:
                            pass
                        else:
                            getpaymentreciept.paidamount = editpayment_paid_fees
                        # -----------------------------------------------------------!
                        if editpayment_advance_fees == getpaymentreciept.advanceamount:
                            pass
                        else:
                            getpaymentreciept.advanceamount = editpayment_advance_fees
                        # -----------------------------------------------------------!
                        if editpayment_pending_fees == getpaymentreciept.pendingamount:
                            pass
                        else:
                            getpaymentreciept.pendingamount = editpayment_pending_fees
                        # -----------------------------------------------------------!
                        if editpayment_payment_mode == getpaymentreciept.paymentmode:
                            pass
                        else:
                            getpaymentreciept.paymentmode = editpayment_payment_mode
                        # -----------------------------------------------------------!
                        if editpayment_cheque_no == getpaymentreciept.cheque_no:
                            pass
                        else:
                            getpaymentreciept.cheque_no = editpayment_cheque_no
                        # -----------------------------------------------------------!
                        if editpayment_b_name == getpaymentreciept.bank_name:
                            pass
                        else:
                            getpaymentreciept.bank_name = editpayment_b_name
                        # -----------------------------------------------------------!
                        if editpayment_remarks == getpaymentreciept.remarks:
                            pass
                        else:
                            getpaymentreciept.remarks = editpayment_remarks
                        getpaymentreciept.save()    
                        return JsonResponse({'saved':'yes'})
                        
                    except PaymentReciept.DoesNotExist:
                        print("no payment reciept")
                

                commonfees_pendingfees_studentid = request.POST.get('commonfees_pendingfees_studentid')
                if commonfees_pendingfees_studentid:
                    # print("clicked")
                    try:
                        getstudent = Student.objects.get(id = commonfees_pendingfees_studentid)
                        enrolled = Enrolled.objects.get(student = getstudent.id)
                        
                        if enrolled.course_pattern == "Full Course":
                            getprevioussemyearfees = PaymentReciept.objects.filter(Q(student = getstudent.id) & Q(payment_for = "Course Fees") & Q(semyear = int(enrolled.current_semyear) - 1))
                            previoussemyearfees = []
                            if getprevioussemyearfees:
                                print("getprevioussemyearfees :",getprevioussemyearfees)
                                try:
                                    getcurrentsemyearfees = PaymentReciept.objects.filter(Q(student = getstudent.id) & Q(payment_for = "Course Fees") & Q(semyear = enrolled.current_semyear)).latest('id')
                                    print("current semester fees present")
                                    if int(getcurrentsemyearfees.advanceamount) > 0:
                                        print("advance got 1")
                                    else:
                                        print("no advance 1")
                                        return JsonResponse({
                                            'pattern':'fullcourse',
                                            'paymentpending':'yes',
                                            'pendingamount':getcurrentsemyearfees.pendingamount,
                                            'total_fees':getcurrentsemyearfees.pendingamount,
                                            'previous_pending':0,
                                            'current_semyear':enrolled.current_semyear})
                                except PaymentReciept.DoesNotExist:
                                    getcurrentsemyearfees = PaymentReciept.objects.filter(Q(student = getstudent.id) & Q(payment_for = "Course Fees") & Q(semyear = int(enrolled.current_semyear) - 1)).latest('id')
                                    print("current semester fees not present")
                                    if int(getcurrentsemyearfees.advanceamount) > 0:
                                        return JsonResponse({
                                            'pattern':'fullcourse',
                                            'paymentpending':'yes',
                                            'pendingamount':0,
                                            'total_fees':0,
                                            'previous_pending':int(getcurrentsemyearfees.advanceamount),
                                            'current_semyear':enrolled.current_semyear})
                                    else:
                                        print("no advance 2")
                                        return JsonResponse({
                                            'pattern':'fullcourse',
                                            'paymentpending':'yes',
                                            'pendingamount':0,
                                            'total_fees':0,
                                            'previous_pending':0,
                                            'current_semyear':enrolled.current_semyear})
                            else:
                                getcurrentsemyearfees = PaymentReciept.objects.filter(Q(student = getstudent.id) & Q(payment_for = "Course Fees") & Q(semyear = enrolled.current_semyear)).latest('id')
                                if getcurrentsemyearfees.paymentmode == "Cheque":
                                    print("cheque it is")
                                    current_status = getcurrentsemyearfees.status
                                    if current_status == "Not Realised":
                                        print("Not Realised")
                                    else:
                                        print("realised")
                                        if int(getcurrentsemyearfees.pendingamount) == 0:
                                            print("semyear clear")
                                            return JsonResponse({'paymentpending':'no'})
                                        else:
                                            print("semyear not clear")

                                            return JsonResponse({
                                                'pattern':'fullcourse',
                                                'paymentpending':'yes',
                                                'pendingamount':getcurrentsemyearfees.pendingamount,
                                                'total_fees':getcurrentsemyearfees.pendingamount,
                                                'previous_pending':getcurrentsemyearfees.advanceamount,
                                                'current_semyear':enrolled.current_semyear})
                                else:
                                    if int(getcurrentsemyearfees.pendingamount) == 0:
                                        print("semyear clear")
                                        return JsonResponse({'paymentpending':'no'})
                                    else:
                                        print("semyear not clear")

                                        return JsonResponse({
                                            'pattern':'fullcourse',
                                            'paymentpending':'yes',
                                            'pendingamount':getcurrentsemyearfees.pendingamount,
                                            'total_fees':getcurrentsemyearfees.pendingamount,
                                            'previous_pending':getcurrentsemyearfees.advanceamount,
                                            'current_semyear':enrolled.current_semyear})
                            
                        else:
                            getstudentfees = StudentFees.objects.get(Q(student = getstudent.id) & Q(sem = enrolled.current_semyear))
                            print("nooo")
                            getprevioussemyearfees = PaymentReciept.objects.filter(Q(student = getstudent.id) & Q(payment_for = "Course Fees") & Q(semyear = int(enrolled.current_semyear) - 1))
                            
                            if getprevioussemyearfees:
                                getlatestsemyearfees = PaymentReciept.objects.filter(Q(student = getstudent.id) & Q(payment_for = "Course Fees") & Q(semyear = int(enrolled.current_semyear) - 1)).latest('id')
                                print("getlatestsemyearfees",getlatestsemyearfees)
                                if int(getlatestsemyearfees.advanceamount) > 0:
                                    print("1")
                                    try:
                                        current_semyear_reciept = PaymentReciept.objects.filter(Q(student = getstudent.id) & Q(payment_for = "Course Fees") & Q(semyear = enrolled.current_semyear)).latest('id')
                                        print("reciept found")
                                        if int(current_semyear_reciept.pendingamount) > 0:

                                            return JsonResponse({
                                                'paymentpending':'yes',
                                                'pendingamount':current_semyear_reciept.pendingamount,
                                                'total_fees':getstudentfees.totalfees,
                                                'previous_pending':0,
                                                'current_semyear':enrolled.current_semyear})
                                    except PaymentReciept.DoesNotExist:
                                        print("reciept not found")
                                        
                                        total_fees = int(getstudentfees.totalfees) - int(getlatestsemyearfees.advanceamount)
                                        if (int(getlatestsemyearfees.advanceamount) > 0):
                                            pendingamount = int(total_fees) - int(getlatestsemyearfees.advanceamount)
                                            total_fees = int(getstudentfees.totalfees)
                                            advance_fees = int(getlatestsemyearfees.advanceamount)
                                            print(total_fees , advance_fees)
                                            if (total_fees - advance_fees > 0):
                                                print("positive")
                                                pending_fees = total_fees - advance_fees
                                                return JsonResponse({
                                                    'pattern':'fullcourse',
                                                    'paymentpending':'yes',
                                                    'pendingamount':pending_fees,
                                                    'total_fees':getstudentfees.totalfees,
                                                    'previous_pending':int(getlatestsemyearfees.advanceamount),
                                                    'current_semyear':enrolled.current_semyear})
                                            else:
                                                print("negative")
                                                return JsonResponse({
                                                    'pattern':'fullcourse',
                                                    'paymentpending':'yes',
                                                    'pendingamount':0,
                                                    'total_fees':getstudentfees.totalfees,
                                                    'previous_pending':int(getlatestsemyearfees.advanceamount),
                                                    'current_semyear':enrolled.current_semyear})
                                        
                                else:
                                    print("2")
                                    try:
                                        current_semyear_reciept = PaymentReciept.objects.filter(Q(student = getstudent.id) & Q(payment_for = "Course Fees") & Q(semyear = enrolled.current_semyear)).latest('id')
                                        if int(current_semyear_reciept.pendingamount) == 0:
                                            return JsonResponse({
                                                'paymentpending':'no',
                                                'pendingamount':""})
                                        else:
                                            print("reciept found")
                                            if int(current_semyear_reciept.advanceamount) > 0:
                                                print("advance found")
                                            else:
                                                print("no advance")

                                                return JsonResponse({
                                                    'paymentpending':'yes',
                                                    'pendingamount':current_semyear_reciept.pendingamount,
                                                    'total_fees':getstudentfees.totalfees,
                                                    'previous_pending':0,
                                                    'current_semyear':enrolled.current_semyear})
                                        
                                    except PaymentReciept.DoesNotExist:
                                        print("reciept not found")
                                        
                                        # total_fees = int(getstudentfees.totalfees) - int(getlatestsemyearfees.advanceamount)
                                        # print(getstudentfees)
                                        return JsonResponse({
                                           'paymentpending':'yes',
                                            'pendingamount':getstudentfees.totalfees,
                                            'total_fees':getstudentfees.totalfees,
                                            'previous_pending':0,
                                            'current_semyear':enrolled.current_semyear})
                            else:
                                try:
                                    current_semyear_reciept = PaymentReciept.objects.filter(Q(student = getstudent.id) & Q(payment_for = "Course Fees") & Q(semyear = enrolled.current_semyear)).latest('id')
                                    if current_semyear_reciept.paymentmode == "Cheque":
                                        print("cheque it is")
                                        current_status = current_semyear_reciept.status
                                        if current_status == "Not Realised":
                                            print("Not Realised")
                                        else:
                                            print("realised")
                                            if int(current_semyear_reciept.pendingamount) == 0:
                                                return JsonResponse({
                                                    'paymentpending':'no',
                                                    'pendingamount':""})
                                            else:
                                                if int(current_semyear_reciept.advanceamount) > 0:
                                                    print("advance got")
                                                    total_fees = int(getstudentfees.totalfees) - int(current_semyear_reciept.advanceamount)
                                                    return JsonResponse({
                                                        'paymentpending':'yes',
                                                        'pendingamount':total_fees,
                                                        'total_fees':getstudentfees.totalfees,
                                                        'previous_pending':current_semyear_reciept.advanceamount,
                                                        'current_semyear':enrolled.current_semyear})
                                                else:
                                                    print("advance not got")
                                                    total_fees = int(current_semyear_reciept.pendingamount)
                                                    return JsonResponse({
                                                        'paymentpending':'yes',
                                                        'pendingamount':total_fees,
                                                        'total_fees':getstudentfees.totalfees,
                                                        'previous_pending':0,
                                                        'current_semyear':enrolled.current_semyear})


                                    else: 
                                        if int(current_semyear_reciept.pendingamount) == 0:
                                            return JsonResponse({
                                                'paymentpending':'no',
                                                'pendingamount':""})
                                        else:
                                            if int(current_semyear_reciept.advanceamount) > 0:
                                                print("advance got")
                                                total_fees = int(getstudentfees.totalfees) - int(current_semyear_reciept.advanceamount)
                                                return JsonResponse({
                                                    'paymentpending':'yes',
                                                    'pendingamount':total_fees,
                                                    'total_fees':getstudentfees.totalfees,
                                                    'previous_pending':current_semyear_reciept.advanceamount,
                                                    'current_semyear':enrolled.current_semyear})
                                            else:
                                                print("advance not got")
                                                total_fees = int(current_semyear_reciept.pendingamount)
                                                return JsonResponse({
                                                    'paymentpending':'yes',
                                                    'pendingamount':total_fees,
                                                    'total_fees':getstudentfees.totalfees,
                                                    'previous_pending':0,
                                                    'current_semyear':enrolled.current_semyear})
                                    
                                except PaymentReciept.DoesNotExist:
                                    previous_semyear_reciept = PaymentReciept.objects.filter(Q(student = getstudent.id) & Q(payment_for = "Course Fees") & Q(semyear = int(enrolled.current_semyear) - 1 )).latest('id')    
                                    print("get previous semyear : ",previous_semyear_reciept)
                            
                                    
                            
                    except Student.DoesNotExist:
                        print("no student")
                
                commonfees_student_id = request.POST.get('commonfees_student_id')
                commonfees_feesfor = request.POST.get('commonfees_feesfor')
                commonfees_totalfees = request.POST.get('commonfees_totalfees')
                commonfees_amount = request.POST.get('commonfees_amount')
                commonfees_feestype = request.POST.get('commonfees_feestype')
                commonfees_semyear = request.POST.get('commonfees_semyear')
                commonfees_transactiondate = request.POST.get('commonfees_transactiondate')
                commonfees_paymentmode = request.POST.get('commonfees_paymentmode')
                commonfees_chequeno = request.POST.get('commonfees_chequeno')
                commonfees_bankname = request.POST.get('commonfees_bankname')
                commonfees_remarks = request.POST.get('commonfees_remarks')
                commonfees_previous_pending_advance = request.POST.get('commonfees_previous_pending')
                commonfees_semyear_totalfees = request.POST.get('commonfees_semyear_totalfees')
                
                # print("Common Fees :",commonfees_student_id,commonfees_feesfor,commonfees_amount,commonfees_feestype,commonfees_semyear,commonfees_transactiondate,commonfees_paymentmode,commonfees_chequeno,commonfees_bankname,commonfees_remarks)
                if commonfees_student_id and commonfees_feesfor and commonfees_amount and commonfees_feestype and commonfees_semyear and commonfees_paymentmode and commonfees_remarks:
                    if commonfees_paymentmode == "Cheque":
                        print("yes cheque got ___________________")
                        if commonfees_feesfor:
                            print("commonfees_feesfor = ",commonfees_feesfor)
                            try:
                                getstudent = Student.objects.get(id = commonfees_student_id)
                                enrolled = Enrolled.objects.get(student = getstudent.id)
                                try:
                                    getlatestreciept = PaymentReciept.objects.latest('id')
                                except PaymentReciept.DoesNotExist:
                                    getlatestreciept = "none"
                                if getlatestreciept == "none":
                                    transactionID = "TXT445FE101"
                                else:
                                    tid = getlatestreciept.transactionID
                                    tranx = tid.replace("TXT445FE",'')
                                    transactionID =  str("TXT445FE") + str(int(tranx) + 1)
                                
                                
                                print("Total SemYear Fees : ",commonfees_semyear_totalfees)
                                print("Previous Pending Fees : ",commonfees_previous_pending_advance)
                                print("Current Total Pending : ",commonfees_totalfees)
                                print("Paid Fees : ",commonfees_amount)



                                if enrolled.course_pattern == "avc":
                                    pass
                                if commonfees_paymentmode == "Cheque":
                                    payment_status = "Not Realised"
                                else:
                                    payment_status = "Realised"
                                if int(commonfees_previous_pending_advance) == 0:    
                                    add_payment_reciept = PaymentReciept(
                                        student = getstudent.id,
                                        payment_for="Course Fees",
                                        payment_categories = commonfees_feesfor,
                                        payment_type=commonfees_feestype,
                                        fee_reciept_type="",
                                        transaction_date= commonfees_transactiondate,
                                        cheque_no=commonfees_chequeno,
                                        bank_name=commonfees_bankname,
                                        semyearfees=commonfees_totalfees,
                                        paidamount=0,
                                        advanceamount = 0,
                                        pendingamount=commonfees_totalfees,
                                        transactionID = transactionID,
                                        paymentmode=commonfees_paymentmode,
                                        remarks=commonfees_remarks,session="",
                                        semyear=commonfees_semyear,
                                        uncleared_amount=commonfees_amount,
                                        status = payment_status)
                                    
                                    add_payment_reciept.save()
                                elif int(commonfees_previous_pending_advance) > 0:
                                    add_payment_reciept = PaymentReciept(
                                            student = getstudent.id,
                                            payment_for="Course Fees",
                                            payment_categories = commonfees_feesfor,
                                            payment_type=commonfees_feestype,
                                            fee_reciept_type="",
                                            transaction_date= commonfees_transactiondate,
                                            cheque_no=commonfees_chequeno,
                                            bank_name=commonfees_bankname,
                                            semyearfees=commonfees_totalfees,
                                            paidamount=0,
                                            advanceamount = 0,
                                            pendingamount=commonfees_totalfees,
                                            transactionID = transactionID,
                                            paymentmode=commonfees_paymentmode,
                                            remarks=commonfees_remarks,session="",
                                            semyear=commonfees_semyear,
                                            uncleared_amount=int(commonfees_amount),
                                            status = payment_status)
                                    add_payment_reciept.save()
                                
                                getfeespaid = PaymentReciept.objects.filter(student = getstudent.id)
                                
                                feeserializer = PaymentRecieptSerializer(getfeespaid,many=True)
                                return JsonResponse({'success':'yes','fees':feeserializer.data,'student_id':getstudent.id})
                                
                            
                            except Student.DoesNotExist:
                                print("no student found")
                        
                   
                    else:
                        print("else payment mode ___________________")
                        if commonfees_feesfor:
                            print("commonfees_feesfor = ",commonfees_feesfor)
                            try:
                                getstudent = Student.objects.get(id = commonfees_student_id)
                                enrolled = Enrolled.objects.get(student = getstudent.id)
                                try:
                                    getlatestreciept = PaymentReciept.objects.latest('id')
                                except PaymentReciept.DoesNotExist:
                                    getlatestreciept = "none"
                                if getlatestreciept == "none":
                                    transactionID = "TXT445FE101"
                                else:
                                    tid = getlatestreciept.transactionID
                                    tranx = tid.replace("TXT445FE",'')
                                    transactionID =  str("TXT445FE") + str(int(tranx) + 1)
                                
                                
                                print("Total SemYear Fees : ",commonfees_semyear_totalfees)
                                print("Previous Pending Fees : ",commonfees_previous_pending_advance)
                                print("Current Total Pending : ",commonfees_totalfees)
                                print("Paid Fees : ",commonfees_amount)



                                if enrolled.course_pattern == "avc":
                                    pass
                                if commonfees_paymentmode == "Cheque":
                                    payment_status = "Not Realised"
                                else:
                                    payment_status = "Realised"
                                if int(commonfees_previous_pending_advance) == 0:
                                    print("condition1")
                                    semyear_fees = int(commonfees_totalfees) 
                                    paid_fees = int(commonfees_amount)
                                    pending_fees = semyear_fees - paid_fees
                                    print(semyear_fees , paid_fees , pending_fees)
                                    if (semyear_fees - paid_fees) < 0 :
                                        print("negative got hence advance amount :")
                                        print(abs(semyear_fees - paid_fees))
                                        add_payment_reciept = PaymentReciept(
                                            student = getstudent.id,
                                            payment_for="Course Fees",
                                            payment_categories = commonfees_feesfor,
                                            payment_type=commonfees_feestype,
                                            fee_reciept_type="",
                                            transaction_date= commonfees_transactiondate,
                                            cheque_no=commonfees_chequeno,
                                            bank_name=commonfees_bankname,
                                            semyearfees=semyear_fees,
                                            paidamount=paid_fees,
                                            advanceamount = abs(semyear_fees - paid_fees),
                                            pendingamount=0,
                                            transactionID = transactionID,
                                            paymentmode=commonfees_paymentmode,
                                            remarks=commonfees_remarks,session="",
                                            semyear=commonfees_semyear,
                                            status = payment_status)
                                    else:
                                        print("positive")
                                        add_payment_reciept = PaymentReciept(
                                            student = getstudent.id,
                                            payment_for="Course Fees",
                                            payment_categories = commonfees_feesfor,
                                            payment_type=commonfees_feestype,
                                            fee_reciept_type="",
                                            transaction_date= commonfees_transactiondate,
                                            cheque_no=commonfees_chequeno,
                                            bank_name=commonfees_bankname,
                                            semyearfees=semyear_fees,
                                            paidamount=paid_fees,
                                            advanceamount = 0,
                                            pendingamount=pending_fees,
                                            transactionID = transactionID,
                                            paymentmode=commonfees_paymentmode,
                                            remarks=commonfees_remarks,session="",
                                            semyear=commonfees_semyear,
                                            status = payment_status)
                                    add_payment_reciept.save()
                                elif int(commonfees_previous_pending_advance) > 0:
                                    print("condition2")
                                    pending_amount = int(commonfees_totalfees)
                                    semyear_fees = int(commonfees_semyear_totalfees) 
                                    paid_fees = int(commonfees_amount)
                                    advance_fees = int(commonfees_previous_pending_advance)
                                    pending_fees = pending_amount - paid_fees
                                    if pending_fees < 0:
                                        print("advance fees has to be updated")
                                        print(semyear_fees , paid_fees ,advance_fees, pending_fees)
                                        advanceamount = abs(pending_fees)
                                        print("advance fees : ",advanceamount)
                                        pending_fees = 0
                                    else:

                                        print(semyear_fees , paid_fees ,advance_fees, pending_fees)
                                        advanceamount = 0
                                        if int(semyear_fees - paid_fees) < 0:
                                            pending_fees = 0
                                            advanceamount = abs(semyear_fees - paid_fees)
                                        elif int(semyear_fees - advance_fees) < 0:
                                            advanceamount = abs(semyear_fees - advance_fees)
                                        else:
                                            advanceamount = 0
                                    add_payment_reciept = PaymentReciept(
                                            student = getstudent.id,
                                            payment_for="Course Fees",
                                            payment_categories = commonfees_feesfor,
                                            payment_type=commonfees_feestype,
                                            fee_reciept_type="",
                                            transaction_date= commonfees_transactiondate,
                                            cheque_no=commonfees_chequeno,
                                            bank_name=commonfees_bankname,
                                            semyearfees=semyear_fees,
                                            paidamount=paid_fees,
                                            advanceamount = advanceamount,
                                            pendingamount=pending_fees,
                                            transactionID = transactionID,
                                            paymentmode=commonfees_paymentmode,
                                            remarks=commonfees_remarks,session="",
                                            semyear=commonfees_semyear,
                                            status = payment_status)
                                    add_payment_reciept.save()
                                
                                getfeespaid = PaymentReciept.objects.filter(student = getstudent.id)
                                
                                feeserializer = PaymentRecieptSerializer(getfeespaid,many=True)
                                return JsonResponse({'success':'yes','fees':feeserializer.data,'student_id':getstudent.id})
                                
                            
                            except Student.DoesNotExist:
                                print("no student found")
                        else:
                            print("course fees not given")
                            try:
                                getstudent = Student.objects.get(id = commonfees_student_id)
                                try:
                                    getlatestreciept = PaymentReciept.objects.latest('id')
                                except PaymentReciept.DoesNotExist:
                                    getlatestreciept = "none"
                                if getlatestreciept == "none":
                                    transactionID = "TXT445FE101"
                                else:
                                    tid = getlatestreciept.transactionID
                                    tranx = tid.replace("TXT445FE",'')
                                    transactionID =  str("TXT445FE") + str(int(tranx) + 1)
                                print(transactionID)
                                
                                add_payment_reciept = PaymentReciept(student = getstudent.id,payment_for="Course Fees",payment_categories = commonfees_feesfor,payment_type=commonfees_feestype,fee_reciept_type="",transaction_date= commonfees_transactiondate,cheque_no=commonfees_chequeno,bank_name=commonfees_bankname,paidamount=commonfees_amount,pendingamount="0",transactionID = transactionID,paymentmode=commonfees_paymentmode,remarks=commonfees_remarks,session="",semyear=commonfees_semyear,status=payment_status)
                                # add_payment_reciept.save()
                                getfeespaid = PaymentReciept.objects.filter(student = getstudent.id)
                                
                                feeserializer = PaymentRecieptSerializer(getfeespaid,many=True)
                                return JsonResponse({'success':'yes','fees':feeserializer.data,'student_id':getstudent.id})
                                
                            
                            except Student.DoesNotExist:
                                print("no student found")
                    
                extrafees_student_id = request.POST.get('extrafees_student_id')
                extrafees_feesfor = request.POST.get('extrafees_feesfor')
                extrafees_amount = request.POST.get('extrafees_amount')
                extrafees_feestype = request.POST.get('extrafees_feestype')
                extrafees_semyear = request.POST.get('extrafees_semyear')
                extrafees_transactiondate = request.POST.get('extrafees_transactiondate')
                extrafees_paymentmode = request.POST.get('extrafees_paymentmode')
                extrafees_chequeno = request.POST.get('extrafees_chequeno')
                extrafees_bankname = request.POST.get('extrafees_bankname')
                extrafees_remarks = request.POST.get('extrafees_remarks')
                
                if extrafees_student_id and extrafees_feesfor and extrafees_amount and extrafees_feestype and extrafees_semyear:
                    print("Extra Feesa",extrafees_student_id,extrafees_feesfor,extrafees_amount,extrafees_feestype,extrafees_semyear,extrafees_transactiondate,extrafees_paymentmode,extrafees_chequeno,extrafees_bankname,extrafees_remarks)
                    try:
                        getstudent = Student.objects.get(enrollment_id = extrafees_student_id)
                        try:
                            getlatestreciept = PaymentReciept.objects.latest('id')
                        except PaymentReciept.DoesNotExist:
                            getlatestreciept = "none"
                        if getlatestreciept == "none":
                            transactionID = "TXT445FE101"
                        else:
                            tid = getlatestreciept.transactionID
                            tranx = tid.replace("TXT445FE",'')
                            transactionID =  str("TXT445FE") + str(int(tranx) + 1)
                        print(transactionID)
                        
                        add_payment_reciept = PaymentReciept(student = getstudent.id,payment_for=extrafees_feesfor,payment_type=extrafees_feestype,fee_reciept_type="",transaction_date= extrafees_transactiondate,cheque_no=extrafees_chequeno,bank_name=extrafees_bankname,paidamount=extrafees_amount,pendingamount="0",transactionID = transactionID,paymentmode=extrafees_paymentmode,remarks=extrafees_remarks,session="",semyear=extrafees_semyear)
                        add_payment_reciept.save()

                        getfeespaid = PaymentReciept.objects.filter(student = getstudent.id)
                        
                        feeserializer = PaymentRecieptSerializer(getfeespaid,many=True)
                        return JsonResponse({'success':'yes','fees':feeserializer.data,'student_id':getstudent.id})
                        
                       
                    except Student.DoesNotExist:
                        print("no student found")
                
                
                id = request.POST.get('id')
                if id:
                    getstudent = Student.objects.get(enrollment_id = id)
                    try:
                        getfeespaid = PaymentReciept.objects.filter(Q(student = getstudent.id) & (Q(payment_for="Course Fees") | Q(payment_for="Tution Fees") | Q(payment_for="Re-Registration Fees") | Q(payment_for="Examination Fees")))
                        feeserializer = PaymentRecieptSerializer(getfeespaid,many=True)
                        return JsonResponse({'fees':feeserializer.data,'student_id':getstudent.id})
                    except Fees.DoesNotExist:
                        getfeespaid = "none"
                    
                show_common_fees = request.POST.get('show_common_fees')
                if show_common_fees:
                    getstudent = Student.objects.get(id = show_common_fees)
                    try:
                        getfeespaid = PaymentReciept.objects.filter(Q(student = getstudent.id) & (Q(payment_for="Course Fees") | Q(payment_for="Tution Fees") | Q(payment_for="Re-Registration Fees") | Q(payment_for="Examination Fees")))
                        feeserializer = PaymentRecieptSerializer(getfeespaid,many=True)
                        return JsonResponse({'fees':feeserializer.data,'student_id':getstudent.id})
                    except Fees.DoesNotExist:
                        getfeespaid = "none"
                
                show_additional_fees = request.POST.get('show_additional_fees')
                if show_additional_fees:
                    getstudent = Student.objects.get(id = show_additional_fees)
                    try:
                        getfeespaid = PaymentReciept.objects.filter(Q(student = getstudent.id) & ~(Q(payment_for="Course Fees") | Q(payment_for="Tution Fees") | Q(payment_for="Re-Registration Fees") | Q(payment_for="Examination Fees")))
                        feeserializer = PaymentRecieptSerializer(getfeespaid,many=True)
                        return JsonResponse({'fees':feeserializer.data,'student_id':getstudent.id})
                    except Fees.DoesNotExist:
                        getfeespaid = "none"
                    
        
            allstudent = Student.objects.filter(Q(verified = True) & Q(archive = False)).order_by('-id')
            # print(allstudent)
            file_object = open('static/dict/registered_students.txt', 'a')
            file_object.truncate(0)
            file_object.close()
            studentlist = []
            for i in allstudent:
                student_id = i.id
                enrolled = Enrolled.objects.get(student = student_id)
                course = Course.objects.get(id = enrolled.course)
                stream = Stream.objects.get(id = enrolled.stream)
                university = University.objects.get(registrationID = i.university)
                additionaldetails = AdditionalEnrollmentDetails.objects.get(student = student_id)
                
                # datetimedata = datetime.strptime(str(i.enrollment_date), '%Y-%m-%d').strftime('%d-%m-%Y')
                # print(i.name,datetimedata)
                if i.father_name:
                    father_name = i.father_name
                else:
                    father_name = ""
                if i.alternate_mobile1:
                    alternate_mobile1 = i.alternate_mobile1
                else:
                    alternate_mobile1 = ""

                if i.alternate_mobile1:
                    alternate_mobile1 = i.alternate_mobile1
                else:
                    alternate_mobile1 = ""
                
                if i.alternateemail:
                    alternateemail = i.alternateemail
                else:
                    alternateemail = ""
                
                if i.student_remarks:
                    student_remarks = i.student_remarks
                else:
                    student_remarks = ""

                if i.address:
                    address = i.address
                else:
                    address = ""
                
                obj = {
                    "name":str(i.name),
                    "father_name":father_name,
                    "mother_name":i.mother_name,
                    "dateofbirth":datetime.strptime(str(i.dateofbirth), '%Y-%m-%d').strftime('%d-%m-%Y'),
                    "mobile":i.mobile,
                    "alternate_mobile1":alternate_mobile1,
                    "email":i.email,
                    "alternateemail":alternateemail,
                    "address":address,
                    "alternateaddress":i.alternateaddress,
                    "student_remarks":student_remarks,
                    "counselor_name":additionaldetails.counselor_name,
                    "university_enrollment_id":additionaldetails.university_enrollment_id,
                    "gender":i.gender,
                    "category":i.category,
                    "enrollment_id":i.enrollment_id,
                    "enrollment_date":datetime.strptime(str(i.enrollment_date), '%Y-%m-%d').strftime('%d-%m-%Y'),
                    "registration_id":i.registration_id,
                    "course_name":course.name,
                    "stream_name":stream.name,
                    "course_pattern":enrolled.course_pattern,
                    "current_semester":enrolled.current_semyear,
                    "session":enrolled.session,
                    'entry_mode':enrolled.entry_mode,
                    'university':university.university_name
                }
                studentlist.append(obj)
                
            od2 = json.dumps(studentlist,indent=4)
            
            file_object = open('static/dict/registered_students.txt', 'a')
            file_object.write('{"data": '+od2+'}')
            file_object.close()
            
        else:
            print("no")
    params = {
        "display":display,
        "level_of_user":level_of_user,
        "students":Student.objects.all()
    }
    return render(request,"registeredstudent.html",params)

def RedirectMail(request,pk):
    # print(request.FILES)

    if request.method == "POST":
        print(request.FILES.get("file"))
        subject = "CIIS TEST"
        message = '''Thankyou For Making Payment of rs  \n
        CIIS INDIA \n
        '''
        recipient_list = ["chandrakant.s.belell@gmail.com"]
        attach=request.FILES.get("file")
        mail = EmailMessage(
            subject
            , message
            , settings.EMAIL_HOST_USER,
             recipient_list)
        mail.attach("invoice.pdf", attach.read(), attach.content_type)
        # mail.send()

    else:
        print("suifiu")
    data = {}
    try:
        getlatestpaymentreciept = PaymentReciept.objects.get(id=pk)
        print("This is Redirect Mail Page..")
        # print("latest payment reciept :",getlatestpaymentreciept)
        view_student = Student.objects.get(id=getlatestpaymentreciept.student)
        view_enroll = Enrolled.objects.get(student=view_student.id)
        view_course = Course.objects.get(id = view_enroll.course)
        view_stream = Stream.objects.get(id = view_enroll.stream)
        
        data = {
            'get_reciept_id':getlatestpaymentreciept.id,
            "name":view_student.name,
            "email":view_student.email,
            "mobile":view_student.mobile,
            "enrollment_id":view_student.enrollment_id,
            "address":view_student.address,
            "country":view_student.country,
            "state":view_student.state,
            "city":view_student.city,
            "pincode":view_student.pincode,
            "course":view_course.name,
            "stream":view_stream.name,
            "transactionID":getlatestpaymentreciept.transactionID,
            "transaction_date":getlatestpaymentreciept.transaction_date,
            "semyear":getlatestpaymentreciept.semyear,
            "paidamount":getlatestpaymentreciept.paidamount,
            "pendingamount":getlatestpaymentreciept.pendingamount,
            "paymentmode":getlatestpaymentreciept.paymentmode,
            "url":pk
        }
        # print(data)
    except PaymentReciept.DoesNotExist:
        pass
    return render(request,"redirect_mail.html",data)

@login_required(login_url='/login/')
def AddFees(request):
    print("yes")
    display = ""
    getstream = ""
    level_of_user = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            level_of_user = level.level
            display = "yes"
            if request.method == "POST":
                get_course = request.POST.get('get_course')
                if get_course:
                    try:
                        getcourse = Course.objects.filter(university = get_course)
                        courseserializer = CourseSerializer(getcourse,many=True)
                        return JsonResponse({'course':courseserializer.data})
                    except Course.DoesNotExist:
                        pass
                tution1 = request.POST.get('tution1')
                exam1 = request.POST.get('exam1')
                book1 = request.POST.get('book1')
                resitting1 = request.POST.get('resitting1')
                entrance1 = request.POST.get('entrance1')
                extra1 = request.POST.get('extra1')
                discount1 = request.POST.get('discount1')
                total1 = request.POST.get('total1')

                

                tution2 = request.POST.get('tution2')
                exam2 = request.POST.get('exam2')
                book2 = request.POST.get('book2')
                resitting2 = request.POST.get('resitting2')
                entrance2 = request.POST.get('entrance2')
                extra2 = request.POST.get('extra2')
                discount2 = request.POST.get('discount2')
                total2 = request.POST.get('total2')

                tution3 = request.POST.get('tution3')
                exam3 = request.POST.get('exam3')
                book3 = request.POST.get('book3')
                resitting3 = request.POST.get('resitting3')
                entrance3 = request.POST.get('entrance3')
                extra3 = request.POST.get('extra3')
                discount3 = request.POST.get('discount3')
                total3 = request.POST.get('total3')

                tution4 = request.POST.get('tution4')
                exam4 = request.POST.get('exam4')
                book4 = request.POST.get('book4')
                resitting4 = request.POST.get('resitting4')
                entrance4 = request.POST.get('entrance4')
                extra4 = request.POST.get('extra4')
                discount4 = request.POST.get('discount4')
                total4 = request.POST.get('total4')

                tution5 = request.POST.get('tution5')
                exam5 = request.POST.get('exam5')
                book5 = request.POST.get('book5')
                resitting5 = request.POST.get('resitting5')
                entrance5 = request.POST.get('entrance5')
                extra5 = request.POST.get('extra5')
                discount5 = request.POST.get('discount5')
                total5 = request.POST.get('total5')

                tution6 = request.POST.get('tution6')
                exam6 = request.POST.get('exam6')
                book6 = request.POST.get('book6')
                resitting6 = request.POST.get('resitting6')
                entrance6 = request.POST.get('entrance6')
                extra6 = request.POST.get('extra6')
                discount6 = request.POST.get('discount6')
                total6 = request.POST.get('total6')

                tution7 = request.POST.get('tution7')
                exam7 = request.POST.get('exam7')
                book7 = request.POST.get('book7')
                resitting7 = request.POST.get('resitting7')
                entrance7 = request.POST.get('entrance7')
                extra7 = request.POST.get('extra7')
                discount7 = request.POST.get('discount7')
                total7 = request.POST.get('total7')

                tution8 = request.POST.get('tution8')
                exam8 = request.POST.get('exam8')
                book8 = request.POST.get('book8')
                resitting8 = request.POST.get('resitting8')
                entrance8 = request.POST.get('entrance8')
                extra8 = request.POST.get('extra8')
                discount8 = request.POST.get('discount8')
                total8 = request.POST.get('total8')

                tution1 = request.POST.get('tution1')
                exam1 = request.POST.get('exam1')
                book1 = request.POST.get('book1')
                resitting1 = request.POST.get('resitting1')
                entrance1 = request.POST.get('entrance1')
                extra1 = request.POST.get('extra1')
                discount1 = request.POST.get('discount1')
                total1 = request.POST.get('total1')
                
                
                

                courseid = request.POST.get('coursename')
                streamid = request.POST.get('streamname')
                semesters = request.POST.get('semesters')
                print("data",courseid , streamid , semesters)
                if courseid and streamid and semesters:
                    streamfees = Stream.objects.get(id = streamid)

                    if semesters == '4':
                        
                        try:
                            semesterfees1 = SemesterFees.objects.get(Q(stream = streamid) & Q(sem="1"))
                            print("data :",tution1,exam1,book1, resitting1, entrance1, extra1,discount1, total1)
                            if semesterfees1.tutionfees == tution1:
                                pass
                            else:
                                semesterfees1.tutionfees = tution1
                            if semesterfees1.examinationfees == exam1:
                                pass
                            else:
                                semesterfees1.examinationfees = exam1
                            if semesterfees1.bookfees == book1:
                                pass
                            else:
                                semesterfees1.bookfees = book1
                            if semesterfees1.resittingfees == resitting1:
                                pass
                            else:
                                semesterfees1.resittingfees = resitting1
                            if semesterfees1.entrancefees == entrance1:
                                pass
                            else:
                                semesterfees1.entrancefees = entrance1

                            if semesterfees1.extrafees == extra1:
                                pass
                            else:
                                semesterfees1.extrafees = extra1


                            if semesterfees1.discount == discount1:
                                pass
                            else:
                                semesterfees1.discount = discount1

                            if semesterfees1.totalfees == total1:
                                pass
                            else:
                                semesterfees1.totalfees = total1
                                streamfees.sem1 = total1
                                streamfees.save()
                            
                            semesterfees1.save()
                            
                        except SemesterFees.DoesNotExist:
                            addsemesterfees = SemesterFees(stream=streamid, tutionfees=tution1,examinationfees=exam1,bookfees=book1,resittingfees=resitting1,entrancefees=entrance1,extrafees=extra1,discount=discount1,totalfees=total1,sem="1")
                            addsemesterfees.save()
                        try:
                            semesterfees2 = SemesterFees.objects.get(Q(stream = streamid) & Q(sem="2"))
                            print("data :",tution2,exam2,book2, resitting2, entrance2, extra2,discount2, total2)
                            if semesterfees2.tutionfees == tution2:
                                pass
                            else:
                                semesterfees2.tutionfees = tution2
                            if semesterfees2.examinationfees == exam2:
                                pass
                            else:
                                semesterfees2.examinationfees = exam2
                            if semesterfees2.bookfees == book2:
                                pass
                            else:
                                semesterfees2.bookfees = book2
                            if semesterfees2.resittingfees == resitting2:
                                pass
                            else:
                                semesterfees2.resittingfees = resitting2
                            if semesterfees2.entrancefees == entrance2:
                                pass
                            else:
                                semesterfees2.entrancefees = entrance2

                            if semesterfees2.extrafees == extra2:
                                pass
                            else:
                                semesterfees2.extrafees = extra2


                            if semesterfees2.discount == discount2:
                                pass
                            else:
                                semesterfees2.discount = discount2

                            if semesterfees2.totalfees == total2:
                                pass
                            else:
                                semesterfees2.totalfees = total2
                                streamfees.sem2 = total2
                                streamfees.save()
                            semesterfees2.save()
                        except SemesterFees.DoesNotExist:
                            addsemesterfees = SemesterFees(stream=streamid, tutionfees=tution2,examinationfees=exam2,bookfees=book2,resittingfees=resitting2,entrancefees=entrance2,extrafees=extra2,discount=discount2,totalfees=total2,sem="2")
                            addsemesterfees.save()
                        try:
                            semesterfees3 = SemesterFees.objects.get(Q(stream = streamid) & Q(sem="3"))
                            print("data :",tution3,exam3,book3, resitting3, entrance3, extra3,discount3, total3)
                            if semesterfees3.tutionfees == tution3:
                                pass
                            else:
                                semesterfees3.tutionfees = tution3
                            if semesterfees3.examinationfees == exam3:
                                pass
                            else:
                                semesterfees3.examinationfees = exam3
                            if semesterfees3.bookfees == book3:
                                pass
                            else:
                                semesterfees3.bookfees = book3
                            if semesterfees3.resittingfees == resitting3:
                                pass
                            else:
                                semesterfees3.resittingfees = resitting3
                            if semesterfees3.entrancefees == entrance3:
                                pass
                            else:
                                semesterfees3.entrancefees = entrance3

                            if semesterfees3.extrafees == extra3:
                                pass
                            else:
                                semesterfees3.extrafees = extra3


                            if semesterfees3.discount == discount3:
                                pass
                            else:
                                semesterfees3.discount = discount3

                            if semesterfees3.totalfees == total3:
                                pass
                            else:
                                semesterfees3.totalfees = total3
                                streamfees.sem3 = total3
                                streamfees.save()
                            semesterfees3.save()
                        except SemesterFees.DoesNotExist:
                            addsemesterfees = SemesterFees(stream=streamid, tutionfees=tution3,examinationfees=exam3,bookfees=book3,resittingfees=resitting3,entrancefees=entrance3,extrafees=extra3,discount=discount3,totalfees=total3,sem="3")
                            addsemesterfees.save()
                        try:
                            semesterfees4 = SemesterFees.objects.get(Q(stream = streamid) & Q(sem="4"))
                            print("data :",tution4,exam4,book4, resitting4, entrance4, extra4,discount4, total4)
                            if semesterfees4.tutionfees == tution4:
                                pass
                            else:
                                semesterfees4.tutionfees = tution4
                            if semesterfees4.examinationfees == exam4:
                                pass
                            else:
                                semesterfees4.examinationfees = exam4
                            if semesterfees4.bookfees == book4:
                                pass
                            else:
                                semesterfees4.bookfees = book4
                            if semesterfees4.resittingfees == resitting4:
                                pass
                            else:
                                semesterfees4.resittingfees = resitting4
                            if semesterfees4.entrancefees == entrance4:
                                pass
                            else:
                                semesterfees4.entrancefees = entrance4

                            if semesterfees4.extrafees == extra4:
                                pass
                            else:
                                semesterfees4.extrafees = extra4


                            if semesterfees4.discount == discount4:
                                pass
                            else:
                                semesterfees4.discount = discount4

                            if semesterfees4.totalfees == total4:
                                pass
                            else:
                                semesterfees4.totalfees = total4
                                streamfees.sem4 = total4
                                streamfees.save()
                            semesterfees4.save()
                        except SemesterFees.DoesNotExist:
                            addsemesterfees = SemesterFees(stream=streamid, tutionfees=tution4,examinationfees=exam4,bookfees=book4,resittingfees=resitting4,entrancefees=entrance4,extrafees=extra4,discount=discount4,totalfees=total4,sem="4")
                            addsemesterfees.save()
                        return JsonResponse({'added':'yes'})

                    elif semesters == '6':
                        try:
                            semesterfees1 = SemesterFees.objects.get(Q(stream = streamid) & Q(sem="1"))
                            print("semester1",semesterfees1)
                            print("data :",tution1,exam1,book1, resitting1, entrance1, extra1,discount1, total1)
                            if semesterfees1.tutionfees == tution1:
                                pass
                            else:
                                semesterfees1.tutionfees = tution1
                            if semesterfees1.examinationfees == exam1:
                                pass
                            else:
                                semesterfees1.examinationfees = exam1
                            if semesterfees1.bookfees == book1:
                                pass
                            else:
                                semesterfees1.bookfees = book1
                            if semesterfees1.resittingfees == resitting1:
                                pass
                            else:
                                semesterfees1.resittingfees = resitting1
                            if semesterfees1.entrancefees == entrance1:
                                pass
                            else:
                                semesterfees1.entrancefees = entrance1

                            if semesterfees1.extrafees == extra1:
                                pass
                            else:
                                semesterfees1.extrafees = extra1


                            if semesterfees1.discount == discount1:
                                pass
                            else:
                                semesterfees1.discount = discount1

                            if semesterfees1.totalfees == total1:
                                pass
                            else:
                                semesterfees1.totalfees = total1
                                streamfees.sem1 = total1
                                streamfees.save()
                            
                            semesterfees1.save()
                            
                        except SemesterFees.DoesNotExist:
                            print("creating semester 1 of course 6")
                            addsemesterfees = SemesterFees(stream=streamid, tutionfees=tution1,examinationfees=exam1,bookfees=book1,resittingfees=resitting1,entrancefees=entrance1,extrafees=extra1,discount=discount1,totalfees=total1,sem="1")
                            addsemesterfees.save()

                        try:
                            semesterfees2 = SemesterFees.objects.get(Q(stream = streamid) & Q(sem="2"))
                            print("data :",tution2,exam2,book2, resitting2, entrance2, extra2,discount2, total2)
                            if semesterfees2.tutionfees == tution2:
                                pass
                            else:
                                semesterfees2.tutionfees = tution2
                            if semesterfees2.examinationfees == exam2:
                                pass
                            else:
                                semesterfees2.examinationfees = exam2
                            if semesterfees2.bookfees == book2:
                                pass
                            else:
                                semesterfees2.bookfees = book2
                            if semesterfees2.resittingfees == resitting2:
                                pass
                            else:
                                semesterfees2.resittingfees = resitting2
                            if semesterfees2.entrancefees == entrance2:
                                pass
                            else:
                                semesterfees2.entrancefees = entrance2

                            if semesterfees2.extrafees == extra2:
                                pass
                            else:
                                semesterfees2.extrafees = extra2


                            if semesterfees2.discount == discount2:
                                pass
                            else:
                                semesterfees2.discount = discount2

                            if semesterfees2.totalfees == total2:
                                pass
                            else:
                                semesterfees2.totalfees = total2
                                streamfees.sem2 = total2
                                streamfees.save()
                            semesterfees2.save()
                        except SemesterFees.DoesNotExist:
                            print("creating semester 2 of course 6")
                            addsemesterfees = SemesterFees(stream=streamid, tutionfees=tution2,examinationfees=exam2,bookfees=book2,resittingfees=resitting2,entrancefees=entrance2,extrafees=extra2,discount=discount2,totalfees=total2,sem="2")
                            addsemesterfees.save()
                        try:
                            semesterfees3 = SemesterFees.objects.get(Q(stream = streamid) & Q(sem="3"))
                            print("data :",tution3,exam3,book3, resitting3, entrance3, extra3,discount3, total3)
                            if semesterfees3.tutionfees == tution3:
                                pass
                            else:
                                semesterfees3.tutionfees = tution3
                            if semesterfees3.examinationfees == exam3:
                                pass
                            else:
                                semesterfees3.examinationfees = exam3
                            if semesterfees3.bookfees == book3:
                                pass
                            else:
                                semesterfees3.bookfees = book3
                            if semesterfees3.resittingfees == resitting3:
                                pass
                            else:
                                semesterfees3.resittingfees = resitting3
                            if semesterfees3.entrancefees == entrance3:
                                pass
                            else:
                                semesterfees3.entrancefees = entrance3

                            if semesterfees3.extrafees == extra3:
                                pass
                            else:
                                semesterfees3.extrafees = extra3


                            if semesterfees3.discount == discount3:
                                pass
                            else:
                                semesterfees3.discount = discount3

                            if semesterfees3.totalfees == total3:
                                pass
                            else:
                                semesterfees3.totalfees = total3
                                streamfees.sem3 = total3
                                streamfees.save()
                            semesterfees3.save()
                        except SemesterFees.DoesNotExist:
                            print("creating semester 3 of course 6")
                            addsemesterfees = SemesterFees(stream=streamid, tutionfees=tution3,examinationfees=exam3,bookfees=book3,resittingfees=resitting3,entrancefees=entrance3,extrafees=extra3,discount=discount3,totalfees=total3,sem="3")
                            addsemesterfees.save()
                        try:
                            semesterfees4 = SemesterFees.objects.get(Q(stream = streamid) & Q(sem="4"))
                            print("data :",tution4,exam4,book4, resitting4, entrance4, extra4,discount4, total4)
                            if semesterfees4.tutionfees == tution4:
                                pass
                            else:
                                semesterfees4.tutionfees = tution4
                            if semesterfees4.examinationfees == exam4:
                                pass
                            else:
                                semesterfees4.examinationfees = exam4
                            if semesterfees4.bookfees == book4:
                                pass
                            else:
                                semesterfees4.bookfees = book4
                            if semesterfees4.resittingfees == resitting4:
                                pass
                            else:
                                semesterfees4.resittingfees = resitting4
                            if semesterfees4.entrancefees == entrance4:
                                pass
                            else:
                                semesterfees4.entrancefees = entrance4

                            if semesterfees4.extrafees == extra4:
                                pass
                            else:
                                semesterfees4.extrafees = extra4


                            if semesterfees4.discount == discount4:
                                pass
                            else:
                                semesterfees4.discount = discount4

                            if semesterfees4.totalfees == total4:
                                pass
                            else:
                                semesterfees4.totalfees = total4
                                streamfees.sem4 = total4
                                streamfees.save()
                            semesterfees4.save()
                        except SemesterFees.DoesNotExist:
                            print("creating semester 4 of course 6")
                            addsemesterfees = SemesterFees(stream=streamid, tutionfees=tution4,examinationfees=exam4,bookfees=book4,resittingfees=resitting4,entrancefees=entrance4,extrafees=extra4,discount=discount4,totalfees=total4,sem="4")
                            addsemesterfees.save()

                        try:
                            semesterfees5 = SemesterFees.objects.get(Q(stream = streamid) & Q(sem="5"))
                            print("data :",tution5,exam5,book5, resitting5, entrance5, extra5,discount5, total5)
                            if semesterfees5.tutionfees == tution5:
                                pass
                            else:
                                semesterfees5.tutionfees = tution5
                            if semesterfees5.examinationfees == exam5:
                                pass
                            else:
                                semesterfees5.examinationfees = exam5
                            if semesterfees5.bookfees == book5:
                                pass
                            else:
                                semesterfees5.bookfees = book5
                            if semesterfees5.resittingfees == resitting5:
                                pass
                            else:
                                semesterfees5.resittingfees = resitting5
                            if semesterfees5.entrancefees == entrance5:
                                pass
                            else:
                                semesterfees5.entrancefees = entrance5

                            if semesterfees5.extrafees == extra5:
                                pass
                            else:
                                semesterfees5.extrafees = extra5


                            if semesterfees5.discount == discount5:
                                pass
                            else:
                                semesterfees5.discount = discount5

                            if semesterfees5.totalfees == total5:
                                pass
                            else:
                                semesterfees5.totalfees = total5
                                streamfees.sem5 = total5
                                streamfees.save()
                            semesterfees5.save()
                        except SemesterFees.DoesNotExist:
                            print("creating semester 5 of course 6")
                            addsemesterfees = SemesterFees(stream=streamid, tutionfees=tution5,examinationfees=exam5,bookfees=book5,resittingfees=resitting5,entrancefees=entrance5,extrafees=extra5,discount=discount5,totalfees=total5,sem="5")
                            addsemesterfees.save()

                        try:
                            semesterfees6 = SemesterFees.objects.get(Q(stream = streamid) & Q(sem="6"))
                            print("data :",tution6,exam6,book6, resitting6, entrance6, extra6,discount6, total6)
                            if semesterfees6.tutionfees == tution6:
                                pass
                            else:
                                semesterfees6.tutionfees = tution6
                            if semesterfees6.examinationfees == exam6:
                                pass
                            else:
                                semesterfees6.examinationfees = exam6
                            if semesterfees6.bookfees == book6:
                                pass
                            else:
                                semesterfees6.bookfees = book6
                            if semesterfees6.resittingfees == resitting6:
                                pass
                            else:
                                semesterfees6.resittingfees = resitting6
                            if semesterfees6.entrancefees == entrance6:
                                pass
                            else:
                                semesterfees6.entrancefees = entrance6

                            if semesterfees6.extrafees == extra6:
                                pass
                            else:
                                semesterfees6.extrafees = extra6


                            if semesterfees6.discount == discount6:
                                pass
                            else:
                                semesterfees6.discount = discount6

                            if semesterfees6.totalfees == total6:
                                pass
                            else:
                                semesterfees6.totalfees = total6
                                streamfees.sem6 = total6
                                streamfees.save()
                            semesterfees6.save()
                        except SemesterFees.DoesNotExist:
                            print("creating semester 6 of course 6")
                            addsemesterfees = SemesterFees(stream=streamid, tutionfees=tution6,examinationfees=exam6,bookfees=book6,resittingfees=resitting6,entrancefees=entrance6,extrafees=extra6,discount=discount6,totalfees=total6,sem="6")
                            addsemesterfees.save()
                        return JsonResponse({'added':'yes'})
                        
                    elif semesters == '8':
                        try:
                            semesterfees1 = SemesterFees.objects.get(Q(stream = streamid) & Q(sem="1"))
                            print("data :",tution1,exam1,book1, resitting1, entrance1, extra1,discount1, total1)
                            if semesterfees1.tutionfees == tution1:
                                pass
                            else:
                                semesterfees1.tutionfees = tution1
                            if semesterfees1.examinationfees == exam1:
                                pass
                            else:
                                semesterfees1.examinationfees = exam1
                            if semesterfees1.bookfees == book1:
                                pass
                            else:
                                semesterfees1.bookfees = book1
                            if semesterfees1.resittingfees == resitting1:
                                pass
                            else:
                                semesterfees1.resittingfees = resitting1
                            if semesterfees1.entrancefees == entrance1:
                                pass
                            else:
                                semesterfees1.entrancefees = entrance1

                            if semesterfees1.extrafees == extra1:
                                pass
                            else:
                                semesterfees1.extrafees = extra1


                            if semesterfees1.discount == discount1:
                                pass
                            else:
                                semesterfees1.discount = discount1

                            if semesterfees1.totalfees == total1:
                                pass
                            else:
                                semesterfees1.totalfees = total1
                                streamfees.sem1 = total1
                                streamfees.save()
                            
                            semesterfees1.save()
                            
                        except SemesterFees.DoesNotExist:
                            addsemesterfees = SemesterFees(stream=streamid, tutionfees=tution1,examinationfees=exam1,bookfees=book1,resittingfees=resitting1,entrancefees=entrance1,extrafees=extra1,discount=discount1,totalfees=total1,sem="1")
                            addsemesterfees.save()
                        try:
                            semesterfees2 = SemesterFees.objects.get(Q(stream = streamid) & Q(sem="2"))
                            print("data :",tution2,exam2,book2, resitting2, entrance2, extra2,discount2, total2)
                            if semesterfees2.tutionfees == tution2:
                                pass
                            else:
                                semesterfees2.tutionfees = tution2
                            if semesterfees2.examinationfees == exam2:
                                pass
                            else:
                                semesterfees2.examinationfees = exam2
                            if semesterfees2.bookfees == book2:
                                pass
                            else:
                                semesterfees2.bookfees = book2
                            if semesterfees2.resittingfees == resitting2:
                                pass
                            else:
                                semesterfees2.resittingfees = resitting2
                            if semesterfees2.entrancefees == entrance2:
                                pass
                            else:
                                semesterfees2.entrancefees = entrance2

                            if semesterfees2.extrafees == extra2:
                                pass
                            else:
                                semesterfees2.extrafees = extra2


                            if semesterfees2.discount == discount2:
                                pass
                            else:
                                semesterfees2.discount = discount2

                            if semesterfees2.totalfees == total2:
                                pass
                            else:
                                semesterfees2.totalfees = total2
                                streamfees.sem2 = total2
                                streamfees.save()
                            semesterfees2.save()
                        except SemesterFees.DoesNotExist:
                            addsemesterfees = SemesterFees(stream=streamid, tutionfees=tution2,examinationfees=exam2,bookfees=book2,resittingfees=resitting2,entrancefees=entrance2,extrafees=extra2,discount=discount2,totalfees=total2,sem="2")
                            addsemesterfees.save()
                        try:
                            semesterfees3 = SemesterFees.objects.get(Q(stream = streamid) & Q(sem="3"))
                            print("data :",tution3,exam3,book3, resitting3, entrance3, extra3,discount3, total3)
                            if semesterfees3.tutionfees == tution3:
                                pass
                            else:
                                semesterfees3.tutionfees = tution3
                            if semesterfees3.examinationfees == exam3:
                                pass
                            else:
                                semesterfees3.examinationfees = exam3
                            if semesterfees3.bookfees == book3:
                                pass
                            else:
                                semesterfees3.bookfees = book3
                            if semesterfees3.resittingfees == resitting3:
                                pass
                            else:
                                semesterfees3.resittingfees = resitting3
                            if semesterfees3.entrancefees == entrance3:
                                pass
                            else:
                                semesterfees3.entrancefees = entrance3

                            if semesterfees3.extrafees == extra3:
                                pass
                            else:
                                semesterfees3.extrafees = extra3


                            if semesterfees3.discount == discount3:
                                pass
                            else:
                                semesterfees3.discount = discount3

                            if semesterfees3.totalfees == total3:
                                pass
                            else:
                                semesterfees3.totalfees = total3
                                streamfees.sem3 = total3
                                streamfees.save()
                            semesterfees3.save()
                        except SemesterFees.DoesNotExist:
                            addsemesterfees = SemesterFees(stream=streamid, tutionfees=tution3,examinationfees=exam3,bookfees=book3,resittingfees=resitting3,entrancefees=entrance3,extrafees=extra3,discount=discount3,totalfees=total3,sem="3")
                            addsemesterfees.save()
                        try:
                            semesterfees4 = SemesterFees.objects.get(Q(stream = streamid) & Q(sem="4"))
                            print("data :",tution4,exam4,book4, resitting4, entrance4, extra4,discount4, total4)
                            if semesterfees4.tutionfees == tution4:
                                pass
                            else:
                                semesterfees4.tutionfees = tution4
                            if semesterfees4.examinationfees == exam4:
                                pass
                            else:
                                semesterfees4.examinationfees = exam4
                            if semesterfees4.bookfees == book4:
                                pass
                            else:
                                semesterfees4.bookfees = book4
                            if semesterfees4.resittingfees == resitting4:
                                pass
                            else:
                                semesterfees4.resittingfees = resitting4
                            if semesterfees4.entrancefees == entrance4:
                                pass
                            else:
                                semesterfees4.entrancefees = entrance4

                            if semesterfees4.extrafees == extra4:
                                pass
                            else:
                                semesterfees4.extrafees = extra4


                            if semesterfees4.discount == discount4:
                                pass
                            else:
                                semesterfees4.discount = discount4

                            if semesterfees4.totalfees == total4:
                                pass
                            else:
                                semesterfees4.totalfees = total4
                                streamfees.sem4 = total4
                                streamfees.save()
                            semesterfees4.save()
                        except SemesterFees.DoesNotExist:
                            addsemesterfees = SemesterFees(stream=streamid, tutionfees=tution4,examinationfees=exam4,bookfees=book4,resittingfees=resitting4,entrancefees=entrance4,extrafees=extra4,discount=discount4,totalfees=total4,sem="4")
                            addsemesterfees.save()

                        try:
                            semesterfees5 = SemesterFees.objects.get(Q(stream = streamid) & Q(sem="5"))
                            print("data :",tution5,exam5,book5, resitting5, entrance5, extra5,discount5, total5)
                            if semesterfees5.tutionfees == tution5:
                                pass
                            else:
                                semesterfees5.tutionfees = tution5
                            if semesterfees5.examinationfees == exam5:
                                pass
                            else:
                                semesterfees5.examinationfees = exam5
                            if semesterfees5.bookfees == book5:
                                pass
                            else:
                                semesterfees5.bookfees = book5
                            if semesterfees5.resittingfees == resitting5:
                                pass
                            else:
                                semesterfees5.resittingfees = resitting5
                            if semesterfees5.entrancefees == entrance5:
                                pass
                            else:
                                semesterfees5.entrancefees = entrance5

                            if semesterfees5.extrafees == extra5:
                                pass
                            else:
                                semesterfees5.extrafees = extra5


                            if semesterfees5.discount == discount5:
                                pass
                            else:
                                semesterfees5.discount = discount5

                            if semesterfees5.totalfees == total5:
                                pass
                            else:
                                semesterfees5.totalfees = total5
                                streamfees.sem5 = total5
                                streamfees.save()
                            semesterfees5.save()
                        except SemesterFees.DoesNotExist:
                            addsemesterfees = SemesterFees(stream=streamid, tutionfees=tution5,examinationfees=exam5,bookfees=book5,resittingfees=resitting5,entrancefees=entrance5,extrafees=extra5,discount=discount5,totalfees=total5,sem="5")
                            addsemesterfees.save()

                        try:
                            semesterfees6 = SemesterFees.objects.get(Q(stream = streamid) & Q(sem="6"))
                            print("data :",tution6,exam6,book6, resitting6, entrance6, extra6,discount6, total6)
                            if semesterfees6.tutionfees == tution6:
                                pass
                            else:
                                semesterfees6.tutionfees = tution6
                            if semesterfees6.examinationfees == exam6:
                                pass
                            else:
                                semesterfees6.examinationfees = exam6
                            if semesterfees6.bookfees == book6:
                                pass
                            else:
                                semesterfees6.bookfees = book6
                            if semesterfees6.resittingfees == resitting6:
                                pass
                            else:
                                semesterfees6.resittingfees = resitting6
                            if semesterfees6.entrancefees == entrance6:
                                pass
                            else:
                                semesterfees6.entrancefees = entrance6

                            if semesterfees6.extrafees == extra6:
                                pass
                            else:
                                semesterfees6.extrafees = extra6


                            if semesterfees6.discount == discount6:
                                pass
                            else:
                                semesterfees6.discount = discount6

                            if semesterfees6.totalfees == total6:
                                pass
                            else:
                                semesterfees6.totalfees = total6
                                streamfees.sem6 = total6
                                streamfees.save()
                            semesterfees6.save()
                        except SemesterFees.DoesNotExist:
                            addsemesterfees = SemesterFees(stream=streamid, tutionfees=tution6,examinationfees=exam6,bookfees=book6,resittingfees=resitting6,entrancefees=entrance6,extrafees=extra6,discount=discount6,totalfees=total6,sem="6")
                            addsemesterfees.save()
                        try:
                            semesterfees7 = SemesterFees.objects.get(Q(stream = streamid) & Q(sem="7"))
                            print("data :",tution7,exam7,book7, resitting7, entrance7, extra7,discount7, total7)
                            if semesterfees7.tutionfees == tution7:
                                pass
                            else:
                                semesterfees7.tutionfees = tution7
                            if semesterfees7.examinationfees == exam7:
                                pass
                            else:
                                semesterfees7.examinationfees = exam7
                            if semesterfees7.bookfees == book7:
                                pass
                            else:
                                semesterfees7.bookfees = book7
                            if semesterfees7.resittingfees == resitting7:
                                pass
                            else:
                                semesterfees7.resittingfees = resitting7
                            if semesterfees7.entrancefees == entrance7:
                                pass
                            else:
                                semesterfees7.entrancefees = entrance7

                            if semesterfees7.extrafees == extra7:
                                pass
                            else:
                                semesterfees7.extrafees = extra7


                            if semesterfees7.discount == discount7:
                                pass
                            else:
                                semesterfees7.discount = discount7

                            if semesterfees7.totalfees == total7:
                                pass
                            else:
                                semesterfees7.totalfees = total7
                                streamfees.sem7 = total7
                                streamfees.save()
                            semesterfees7.save()
                        except SemesterFees.DoesNotExist:
                            addsemesterfees = SemesterFees(stream=streamid, tutionfees=tution7,examinationfees=exam7,bookfees=book7,resittingfees=resitting7,entrancefees=entrance7,extrafees=extra7,discount=discount7,totalfees=total7,sem="7")
                            addsemesterfees.save()

                        try:
                            semesterfees8 = SemesterFees.objects.get(Q(stream = streamid) & Q(sem="8"))
                            print("data :",tution8,exam8,book8, resitting8, entrance8, extra8,discount8, total8)
                            if semesterfees8.tutionfees == tution8:
                                pass
                            else:
                                semesterfees8.tutionfees = tution8
                            if semesterfees8.examinationfees == exam8:
                                pass
                            else:
                                semesterfees8.examinationfees = exam8
                            if semesterfees8.bookfees == book8:
                                pass
                            else:
                                semesterfees8.bookfees = book8
                            if semesterfees8.resittingfees == resitting8:
                                pass
                            else:
                                semesterfees8.resittingfees = resitting8
                            if semesterfees8.entrancefees == entrance8:
                                pass
                            else:
                                semesterfees8.entrancefees = entrance8

                            if semesterfees8.extrafees == extra8:
                                pass
                            else:
                                semesterfees8.extrafees = extra8


                            if semesterfees8.discount == discount8:
                                pass
                            else:
                                semesterfees8.discount = discount8

                            if semesterfees8.totalfees == total8:
                                pass
                            else:
                                semesterfees8.totalfees = total8
                                streamfees.sem8 = total8
                                streamfees.save()
                            semesterfees8.save()
                        except SemesterFees.DoesNotExist:
                            addsemesterfees = SemesterFees(stream=streamid, tutionfees=tution8,examinationfees=exam8,bookfees=book8,resittingfees=resitting8,entrancefees=entrance8,extrafees=extra8,discount=discount8,totalfees=total8,sem="8")
                            addsemesterfees.save()
                        return JsonResponse({'added':'yes'})
                    
                # year data

                year_tution1 = request.POST.get('year_tution1')
                year_exam1 = request.POST.get('year_exam1')
                year_book1 = request.POST.get('year_book1')
                year_resitting1 = request.POST.get('year_resitting1')
                year_entrance1 = request.POST.get('year_entrance1')
                year_extra1 = request.POST.get('year_extra1')
                year_discount1 = request.POST.get('year_discount1')
                year_total1 = request.POST.get('year_total1')
                
                year_tution2 = request.POST.get('year_tution2')
                year_exam2 = request.POST.get('year_exam2')
                year_book2 = request.POST.get('year_book2')
                year_resitting2 = request.POST.get('year_resitting2')
                year_entrance2 = request.POST.get('year_entrance2')
                year_extra2 = request.POST.get('year_extra2')
                year_discount2 = request.POST.get('year_discount2')
                year_total2 = request.POST.get('year_total2')
                
                year_tution3 = request.POST.get('year_tution3')
                year_exam3 = request.POST.get('year_exam3')
                year_book3 = request.POST.get('year_book3')
                year_resitting3 = request.POST.get('year_resitting3')
                year_entrance3 = request.POST.get('year_entrance3')
                year_extra3 = request.POST.get('year_extra3')
                year_discount3 = request.POST.get('year_discount3')
                year_total3 = request.POST.get('year_total3')
                
                year_tution4 = request.POST.get('year_tution4')
                year_exam4 = request.POST.get('year_exam4')
                year_book4 = request.POST.get('year_book4')
                year_resitting4 = request.POST.get('year_resitting4')
                year_entrance4 = request.POST.get('year_entrance4')
                year_extra4 = request.POST.get('year_extra4')
                year_discount4 = request.POST.get('year_discount4')
                year_total4 = request.POST.get('year_total4')
                


                


                year_coursename = request.POST.get('year_coursename')
                year_streamname = request.POST.get('year_streamname')
                year_semesters = request.POST.get('year_semesters')

                if year_coursename and year_streamname and year_semesters:
                    print("yearly data received")
                    if year_semesters == '2':
                        
                        try:
                            yearfees1 = YearFees.objects.get(Q(stream = year_streamname) & Q(year="1"))
                            print("data year:", year_tution1, year_exam1, year_book1, year_resitting1, year_entrance1, year_extra1, year_discount1, year_total1)
                            if yearfees1.tutionfees == year_tution1:
                                pass
                            else:
                                yearfees1.tutionfees = year_tution1
                            if yearfees1.examinationfees == year_exam1:
                                pass
                            else:
                                yearfees1.examinationfees = year_exam1
                            if yearfees1.bookfees == year_book1:
                                pass
                            else:
                                yearfees1.bookfees = year_book1
                            if yearfees1.resittingfees == year_resitting1:
                                pass
                            else:
                                yearfees1.resittingfees = year_resitting1
                            if yearfees1.entrancefees == year_entrance1:
                                pass
                            else:
                                yearfees1.entrancefees = year_entrance1

                            if yearfees1.extrafees == year_extra1:
                                pass
                            else:
                                yearfees1.extrafees = year_extra1


                            if yearfees1.discount == year_discount1:
                                pass
                            else:
                                yearfees1.discount = year_discount1

                            if yearfees1.totalfees == year_total1:
                                pass
                            else:
                                yearfees1.totalfees = year_total1
                                
                            
                            yearfees1.save()
                            
                        except YearFees.DoesNotExist:
                            addyearfees = YearFees(stream=year_streamname,tutionfees=year_tution1,examinationfees=year_exam1,bookfees=year_book1,resittingfees=year_resitting1,entrancefees=year_entrance1,extrafees=year_extra1,discount=year_discount1,totalfees=year_total1,year="1")
                            addyearfees.save()

                        try:
                            yearfees2 = YearFees.objects.get(Q(stream = year_streamname) & Q(year="2"))
                            print("data year:", year_tution2, year_exam2, year_book2, year_resitting2, year_entrance2, year_extra2, year_discount2, year_total2)
                            if yearfees2.tutionfees == year_tution2:
                                pass
                            else:
                                yearfees2.tutionfees = year_tution2
                            if yearfees2.examinationfees == year_exam2:
                                pass
                            else:
                                yearfees2.examinationfees = year_exam2
                            if yearfees2.bookfees == year_book2:
                                pass
                            else:
                                yearfees2.bookfees = year_book2
                            if yearfees2.resittingfees == year_resitting2:
                                pass
                            else:
                                yearfees2.resittingfees = year_resitting2
                            if yearfees2.entrancefees == year_entrance2:
                                pass
                            else:
                                yearfees2.entrancefees = year_entrance2

                            if yearfees2.extrafees == year_extra2:
                                pass
                            else:
                                yearfees2.extrafees = year_extra2


                            if yearfees2.discount == year_discount2:
                                pass
                            else:
                                yearfees2.discount = year_discount2

                            if yearfees2.totalfees == year_total2:
                                pass
                            else:
                                yearfees2.totalfees = year_total2
                                
                            
                            yearfees2.save()
                            
                        except YearFees.DoesNotExist:
                            addyearfees = YearFees(stream=year_streamname,tutionfees=year_tution2,examinationfees=year_exam2,bookfees=year_book2,resittingfees=year_resitting2,entrancefees=year_entrance2,extrafees=year_extra2,discount=year_discount2,totalfees=year_total2,year="2")
                            addyearfees.save()
                        return JsonResponse({'added':'yes'})
                    if year_semesters == '3':
                        
                        try:
                            yearfees1 = YearFees.objects.get(Q(stream = year_streamname) & Q(year="1"))
                            print("data year:", year_tution1, year_exam1, year_book1, year_resitting1, year_entrance1, year_extra1, year_discount1, year_total1)
                            if yearfees1.tutionfees == year_tution1:
                                pass
                            else:
                                yearfees1.tutionfees = year_tution1
                            if yearfees1.examinationfees == year_exam1:
                                pass
                            else:
                                yearfees1.examinationfees = year_exam1
                            if yearfees1.bookfees == year_book1:
                                pass
                            else:
                                yearfees1.bookfees = year_book1
                            if yearfees1.resittingfees == year_resitting1:
                                pass
                            else:
                                yearfees1.resittingfees = year_resitting1
                            if yearfees1.entrancefees == year_entrance1:
                                pass
                            else:
                                yearfees1.entrancefees = year_entrance1

                            if yearfees1.extrafees == year_extra1:
                                pass
                            else:
                                yearfees1.extrafees = year_extra1


                            if yearfees1.discount == year_discount1:
                                pass
                            else:
                                yearfees1.discount = year_discount1

                            if yearfees1.totalfees == year_total1:
                                pass
                            else:
                                yearfees1.totalfees = year_total1
                                
                            
                            yearfees1.save()
                            
                        except YearFees.DoesNotExist:
                            addyearfees = YearFees(stream=year_streamname,tutionfees=year_tution1,examinationfees=year_exam1,bookfees=year_book1,resittingfees=year_resitting1,entrancefees=year_entrance1,extrafees=year_extra1,discount=year_discount1,totalfees=year_total1,year="1")
                            addyearfees.save()

                        try:
                            yearfees2 = YearFees.objects.get(Q(stream = year_streamname) & Q(year="2"))
                            print("data year:", year_tution2, year_exam2, year_book2, year_resitting2, year_entrance2, year_extra2, year_discount2, year_total2)
                            if yearfees2.tutionfees == year_tution2:
                                pass
                            else:
                                yearfees2.tutionfees = year_tution2
                            if yearfees2.examinationfees == year_exam2:
                                pass
                            else:
                                yearfees2.examinationfees = year_exam2
                            if yearfees2.bookfees == year_book2:
                                pass
                            else:
                                yearfees2.bookfees = year_book2
                            if yearfees2.resittingfees == year_resitting2:
                                pass
                            else:
                                yearfees2.resittingfees = year_resitting2
                            if yearfees2.entrancefees == year_entrance2:
                                pass
                            else:
                                yearfees2.entrancefees = year_entrance2

                            if yearfees2.extrafees == year_extra2:
                                pass
                            else:
                                yearfees2.extrafees = year_extra2


                            if yearfees2.discount == year_discount2:
                                pass
                            else:
                                yearfees2.discount = year_discount2

                            if yearfees2.totalfees == year_total2:
                                pass
                            else:
                                yearfees2.totalfees = year_total2
                                
                            
                            yearfees2.save()
                            
                        except YearFees.DoesNotExist:
                            addyearfees = YearFees(stream=year_streamname,tutionfees=year_tution2,examinationfees=year_exam2,bookfees=year_book2,resittingfees=year_resitting2,entrancefees=year_entrance2,extrafees=year_extra2,discount=year_discount2,totalfees=year_total2,year="2")
                            addyearfees.save()


                        try:
                            yearfees3 = YearFees.objects.get(Q(stream = year_streamname) & Q(year="3"))
                            print("data year:", year_tution3, year_exam3, year_book3, year_resitting3, year_entrance3, year_extra3, year_discount3, year_total3)
                            if yearfees3.tutionfees == year_tution3:
                                pass
                            else:
                                yearfees3.tutionfees = year_tution3
                            if yearfees3.examinationfees == year_exam3:
                                pass
                            else:
                                yearfees3.examinationfees = year_exam3
                            if yearfees3.bookfees == year_book3:
                                pass
                            else:
                                yearfees3.bookfees = year_book3
                            if yearfees3.resittingfees == year_resitting3:
                                pass
                            else:
                                yearfees3.resittingfees = year_resitting3
                            if yearfees3.entrancefees == year_entrance3:
                                pass
                            else:
                                yearfees3.entrancefees = year_entrance3

                            if yearfees3.extrafees == year_extra3:
                                pass
                            else:
                                yearfees3.extrafees = year_extra3


                            if yearfees3.discount == year_discount3:
                                pass
                            else:
                                yearfees3.discount = year_discount3

                            if yearfees3.totalfees == year_total3:
                                pass
                            else:
                                yearfees3.totalfees = year_total3
                                
                            
                            yearfees3.save()
                            
                        except YearFees.DoesNotExist:
                            addyearfees = YearFees(stream=year_streamname,tutionfees=year_tution3,examinationfees=year_exam3,bookfees=year_book3,resittingfees=year_resitting3,entrancefees=year_entrance3,extrafees=year_extra3,discount=year_discount3,totalfees=year_total3,year="3")
                            addyearfees.save() 
                        return JsonResponse({'added':'yes'})                  
                    if year_semesters == '4':
                        
                        try:
                            yearfees1 = YearFees.objects.get(Q(stream = year_streamname) & Q(year="1"))
                            print("data year:", year_tution1, year_exam1, year_book1, year_resitting1, year_entrance1, year_extra1, year_discount1, year_total1)
                            if yearfees1.tutionfees == year_tution1:
                                pass
                            else:
                                yearfees1.tutionfees = year_tution1
                            if yearfees1.examinationfees == year_exam1:
                                pass
                            else:
                                yearfees1.examinationfees = year_exam1
                            if yearfees1.bookfees == year_book1:
                                pass
                            else:
                                yearfees1.bookfees = year_book1
                            if yearfees1.resittingfees == year_resitting1:
                                pass
                            else:
                                yearfees1.resittingfees = year_resitting1
                            if yearfees1.entrancefees == year_entrance1:
                                pass
                            else:
                                yearfees1.entrancefees = year_entrance1

                            if yearfees1.extrafees == year_extra1:
                                pass
                            else:
                                yearfees1.extrafees = year_extra1


                            if yearfees1.discount == year_discount1:
                                pass
                            else:
                                yearfees1.discount = year_discount1

                            if yearfees1.totalfees == year_total1:
                                pass
                            else:
                                yearfees1.totalfees = year_total1
                                
                            
                            yearfees1.save()
                            
                        except YearFees.DoesNotExist:
                            addyearfees = YearFees(stream=year_streamname,tutionfees=year_tution1,examinationfees=year_exam1,bookfees=year_book1,resittingfees=year_resitting1,entrancefees=year_entrance1,extrafees=year_extra1,discount=year_discount1,totalfees=year_total1,year="1")
                            addyearfees.save()

                        try:
                            yearfees2 = YearFees.objects.get(Q(stream = year_streamname) & Q(year="2"))
                            print("data year:", year_tution2, year_exam2, year_book2, year_resitting2, year_entrance2, year_extra2, year_discount2, year_total2)
                            if yearfees2.tutionfees == year_tution2:
                                pass
                            else:
                                yearfees2.tutionfees = year_tution2
                            if yearfees2.examinationfees == year_exam2:
                                pass
                            else:
                                yearfees2.examinationfees = year_exam2
                            if yearfees2.bookfees == year_book2:
                                pass
                            else:
                                yearfees2.bookfees = year_book2
                            if yearfees2.resittingfees == year_resitting2:
                                pass
                            else:
                                yearfees2.resittingfees = year_resitting2
                            if yearfees2.entrancefees == year_entrance2:
                                pass
                            else:
                                yearfees2.entrancefees = year_entrance2

                            if yearfees2.extrafees == year_extra2:
                                pass
                            else:
                                yearfees2.extrafees = year_extra2


                            if yearfees2.discount == year_discount2:
                                pass
                            else:
                                yearfees2.discount = year_discount2

                            if yearfees2.totalfees == year_total2:
                                pass
                            else:
                                yearfees2.totalfees = year_total2
                                
                            
                            yearfees2.save()
                            
                        except YearFees.DoesNotExist:
                            addyearfees = YearFees(stream=year_streamname,tutionfees=year_tution2,examinationfees=year_exam2,bookfees=year_book2,resittingfees=year_resitting2,entrancefees=year_entrance2,extrafees=year_extra2,discount=year_discount2,totalfees=year_total2,year="2")
                            addyearfees.save()


                        try:
                            yearfees3 = YearFees.objects.get(Q(stream = year_streamname) & Q(year="3"))
                            print("data year:", year_tution3, year_exam3, year_book3, year_resitting3, year_entrance3, year_extra3, year_discount3, year_total3)
                            if yearfees3.tutionfees == year_tution3:
                                pass
                            else:
                                yearfees3.tutionfees = year_tution3
                            if yearfees3.examinationfees == year_exam3:
                                pass
                            else:
                                yearfees3.examinationfees = year_exam3
                            if yearfees3.bookfees == year_book3:
                                pass
                            else:
                                yearfees3.bookfees = year_book3
                            if yearfees3.resittingfees == year_resitting3:
                                pass
                            else:
                                yearfees3.resittingfees = year_resitting3
                            if yearfees3.entrancefees == year_entrance3:
                                pass
                            else:
                                yearfees3.entrancefees = year_entrance3

                            if yearfees3.extrafees == year_extra3:
                                pass
                            else:
                                yearfees3.extrafees = year_extra3


                            if yearfees3.discount == year_discount3:
                                pass
                            else:
                                yearfees3.discount = year_discount3

                            if yearfees3.totalfees == year_total3:
                                pass
                            else:
                                yearfees3.totalfees = year_total3
                                
                            
                            yearfees3.save()
                            
                        except YearFees.DoesNotExist:
                            addyearfees = YearFees(stream=year_streamname,tutionfees=year_tution3,examinationfees=year_exam3,bookfees=year_book3,resittingfees=year_resitting3,entrancefees=year_entrance3,extrafees=year_extra3,discount=year_discount3,totalfees=year_total3,year="3")
                            addyearfees.save()
                        
                        try:
                            yearfees4 = YearFees.objects.get(Q(stream = year_streamname) & Q(year="4"))
                            print("data year:", year_tution4, year_exam4, year_book4, year_resitting4, year_entrance4, year_extra4, year_discount4, year_total4)
                            if yearfees4.tutionfees == year_tution4:
                                pass
                            else:
                                yearfees4.tutionfees = year_tution4
                            if yearfees4.examinationfees == year_exam4:
                                pass
                            else:
                                yearfees4.examinationfees = year_exam4
                            if yearfees4.bookfees == year_book4:
                                pass
                            else:
                                yearfees4.bookfees = year_book4
                            if yearfees4.resittingfees == year_resitting4:
                                pass
                            else:
                                yearfees4.resittingfees = year_resitting4
                            if yearfees4.entrancefees == year_entrance4:
                                pass
                            else:
                                yearfees4.entrancefees = year_entrance4

                            if yearfees4.extrafees == year_extra4:
                                pass
                            else:
                                yearfees4.extrafees = year_extra4


                            if yearfees4.discount == year_discount4:
                                pass
                            else:
                                yearfees4.discount = year_discount4

                            if yearfees4.totalfees == year_total4:
                                pass
                            else:
                                yearfees4.totalfees = year_total4
                                
                            
                            yearfees4.save()
                            
                        except YearFees.DoesNotExist:
                            addyearfees = YearFees(stream=year_streamname,tutionfees=year_tution4,examinationfees=year_exam4,bookfees=year_book4,resittingfees=year_resitting4,entrancefees=year_entrance4,extrafees=year_extra4,discount=year_discount4,totalfees=year_total4,year="4")
                            addyearfees.save()
                        return JsonResponse({'added':'yes'})
                        


                year_c_name = request.POST.get('year_c_name')
                year_s_name = request.POST.get('year_s_name')
                if year_c_name and year_s_name:
                    stream = Stream.objects.get(id =year_s_name)
                    print(stream)
                    streamserializer = StreamSerializer(stream,many=False)
                    
                    streamfees= ''
                    
                    try:
                        getfeesdetails = YearFees.objects.filter(stream = year_s_name)
                        feesdetails = YearFeesSerializer(getfeesdetails,many=True)
                        streamfees = "yes"
                        
                    except StreamFees.DoesNotExist:
                       
                        print("didn't got streamfees creating one..")
                        # if course_id and stream_id and (sem1 or sem2 or sem3 or sem4 or sem5 or sem6 or sem7 or sem8):
                        #     addstreamfees = StreamFees(course=course_id,stream=stream_id,sem1= sem1,sem2=sem2,sem3=sem3,sem4=sem4,sem5=sem5,sem6=sem6,sem7=sem7,sem8=sem8)
                        #     addstreamfees.save()
                    
                    if streamfees == "yes":
                        
                        return JsonResponse({'stream':streamserializer.data,'feesdetails':feesdetails.data})
                    else:
                        return JsonResponse({'stream':streamserializer.data})
                    

                coursename = request.POST.get('c_name')
                streamname = request.POST.get('s_name')
                data = request.POST.get('data')
                

                print("course name :",coursename, "stream name :",streamname )
                print("data",data)
                if data:
                    try:
                        getstream = Stream.objects.filter(course=data)
                        print(getstream)
                    except Stream.DoesNotExist:
                        getstream = "yes"
                    if getstream != "yes":
                        streamserializer = StreamSerializer(getstream,many=True)
                        return JsonResponse({'stream':streamserializer.data})
                    
                    
                if coursename and streamname:
                    stream = Stream.objects.get(id =streamname)
                    print(stream)
                    streamserializer = StreamSerializer(stream,many=False)
                    
                    streamfees= ''
                    
                    try:
                        getfeesdetails = SemesterFees.objects.filter(stream = streamname)
                        feesdetails = SemesterFeesSerializer(getfeesdetails,many=True)
                        streamfees = "yes"
                        
                    except StreamFees.DoesNotExist:
                       
                        print("didn't got streamfees creating one..")
                        # if course_id and stream_id and (sem1 or sem2 or sem3 or sem4 or sem5 or sem6 or sem7 or sem8):
                        #     addstreamfees = StreamFees(course=course_id,stream=stream_id,sem1= sem1,sem2=sem2,sem3=sem3,sem4=sem4,sem5=sem5,sem6=sem6,sem7=sem7,sem8=sem8)
                        #     addstreamfees.save()
                    
                    if streamfees == "yes":
                        return JsonResponse({'stream':streamserializer.data,'feesdetails':feesdetails.data})
                    else:
                        return JsonResponse({'stream':streamserializer.data})
                    
                
    params = {
        "university":University.objects.all(),
        "display":display,
        "course":Course.objects.all(),
        "level_of_user":level_of_user
    }
    return render(request,"addfees.html",params)

@login_required(login_url='/login/') 
def StudentReAdmission(request):
    display = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            display = "yes"
        else:
            print("no")
    temp = []
    data =''
    if request.method == "POST":
        enum = request.POST.get('enum')
        if enum:
            request.session['enumber'] = enum
        if 'enumber' in request.session:
            sessdata = request.session['enumber']
        else:
            sessdata = "no"
        forsem = request.POST.get('forsem')
        forsempaid = request.POST.get('forsempaid')
        print(forsem , forsempaid,sessdata)
        if forsem and forsempaid and sessdata:
            getstudent = Student.objects.get(enrollmentid = sessdata)
            getfees = Fees.objects.get(student = getstudent.id)
            getsem = getstudent.sem
            if getsem == '1':
                print(forsem , forsempaid,sessdata)
                
                getfees.sem2 = forsem
                getfees.save()
                getfees.paidsem2 = forsempaid
                getfees.save()
                getstudent.sem = '2'
                getstudent.save()
            elif getsem == '2':
                getfees.sem3 = forsem
                getfees.save()
                getfees.paidsem3 = forsempaid
                getfees.save()
                getstudent.sem = '3'
                getstudent.save()
            elif getsem == '3':
                getfees.sem4 = forsem
                getfees.save()
                getfees.paidsem4 = forsempaid
                getfees.save()
                getstudent.sem = '4'
                getstudent.save()
            elif getsem == '4':
                getfees.sem5 = forsem
                getfees.save()
                getfees.paidsem5 = forsempaid
                getfees.save()
                getstudent.sem = '5'
                getstudent.save()
            elif getsem == '5':
                getfees.sem6 = forsem
                getfees.save()
                getfees.paidsem6 = forsempaid
                getfees.save()
                getstudent.sem = '6'
                getstudent.save()
            elif getsem == '6':
                getfees.sem7 = forsem
                getfees.save()
                getfees.paidsem7 = forsempaid
                getfees.save()
                getstudent.sem = '7'
                getstudent.save()
            elif getsem == '7':
                getfees.sem8 = forsem
                getfees.save()
                getfees.paidsem8 = forsempaid
                getfees.save()
                getstudent.sem = '8'
                getstudent.save()
            elif getsem == '8':
                pass
            print("saved")
            
                
        if enum:
            try:
                studentdata = Student.objects.get(enrollmentid=enum)
            except Student.DoesNotExist:
                studentdata = "Does Not Exist"
            if studentdata != "Does Not Exist":
                try:
                    field = Specialization.objects.get(id=studentdata.field)
                except Specialization.DoesNotExist:
                    field = "Not Present"
                try:
                    fees = Fees.objects.get(student=studentdata.id)
                except Fees.DoesNotExist:
                    fees = "Fees Details Not Provided"
                sem1fees = fees.sem1
                sem2fees = fees.sem2
                sem3fees = fees.sem3
                sem4fees = fees.sem4
                sem5fees = fees.sem5
                sem6fees = fees.sem6
                sem7fees = fees.sem7
                sem8fees = fees.sem8

                
                paidsem1 = fees.paidsem1
                paidsem2 = fees.paidsem2
                paidsem3 = fees.paidsem3
                paidsem4 = fees.paidsem4
                paidsem5 = fees.paidsem5
                paidsem6 = fees.paidsem6
                paidsem7 = fees.paidsem7
                paidsem8 = fees.paidsem8
                
                
                
                
                if sem1fees and paidsem1:
                    sem1balance = int(sem1fees) - int(paidsem1)
                else:
                    sem1balance = int(0)

                if sem2fees and paidsem2:
                    sem2balance = int(sem2fees) - int(paidsem2)
                else:
                    sem2balance = int(0)

                if sem3fees and paidsem3:
                    sem3balance = int(sem3fees) - int(paidsem3)
                else:
                    sem3balance = int(0)

                if sem4fees and paidsem4:
                    sem4balance = int(sem4fees) - int(paidsem4)
                else:
                    sem4balance = int(0)

                if sem5fees and paidsem5:
                    sem5balance = int(sem5fees) - int(paidsem5)
                else:
                    sem5balance = int(0)

                if sem6fees and paidsem6:
                    sem6balance = int(sem6fees) - int(paidsem6)
                else:
                    sem6balance = int(0)

                if sem7fees and paidsem7:
                    sem7balance = int(sem7fees) - int(paidsem7)
                else:
                    sem7balance = int(0)

                if sem8fees and paidsem8:
                    sem8balance = int(sem8fees) - int(paidsem8)
                else:
                    sem8balance = int(0)
                if field.duration != "Not Present":
                    durationofsem = int(field.duration) * 2
                    if durationofsem == 2:
                        total = sem1balance + sem2balance
                    elif durationofsem == 4:
                        total = sem1balance + sem2balance + sem3balance + sem4balance
                    elif durationofsem == 6:
                        total = sem1balance + sem2balance + sem3balance + sem4balance + sem5balance + sem6balance
                    elif durationofsem == 8:
                        total = sem1balance + sem2balance + sem3balance + sem4balance + sem5balance + sem6balance + sem7balance + sem8balance
                print("total:",total)
                obj = {
                    "firstname":studentdata.firstname,
                    "lastname":studentdata.lastname,
                    "email":studentdata.email,
                    "mobile":studentdata.mobile,
                    "degree":studentdata.degree,
                    "field":field.type,
                    "duration":field.duration,
                    "enrollmentdate":studentdata.enrollmentdate,
                    "enrollmentid":studentdata.enrollmentid,
                    "address":studentdata.address,
                    "dob":studentdata.dob,
                    "gender":studentdata.gender,
                    "sem":studentdata.sem,
                    "sem1fees":fees.sem1,
                    "sem1paid":fees.paidsem1,
                    "sem1balance":sem1balance,
                    
                    "sem2fees":fees.sem2,
                    "sem2paid":fees.paidsem2,
                    "sem2balance":sem2balance,
                    
                    "sem3fees":fees.sem3,
                    "sem3paid":fees.paidsem3,
                    "sem3balance":sem3balance,
                    

                    "sem4fees":fees.sem4,
                    "sem4paid":fees.paidsem4,
                    "sem4balance":sem4balance,
                    

                    "sem5fees":fees.sem5,
                    "sem5paid":fees.paidsem5,
                    "sem5balance":sem5balance,
                    

                    "sem6fees":fees.sem6,
                    "sem6paid":fees.paidsem6,
                    "sem6balance":sem6balance,
                    

                    "sem7fees":fees.sem7,
                    "sem7paid":fees.paidsem7,
                    "sem7balance":sem7balance,
                    

                    "sem8fees":fees.sem8,
                    "sem8paid":fees.paidsem8,
                    "sem8balance":sem8balance,  
                    "totalpayable":total 
                }
                return JsonResponse({'data':obj})
            else:
                return JsonResponse({'data':"Not Found"})
    params = {
        "display":display
    }
    return render(request,"studentreadmission.html",params)

@login_required(login_url='/login/')
def Registration_Cash(request):
    display = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            display = "yes"
            if request.method == "POST":
                enrollid = request.POST.get('enrollid')
                if enrollid:
                    try:
                        getstudent = Student.objects.get(enrollment_id = enrollid)
                        print(getstudent)
                    except Student.DoesNotExist:
                        getstudent = "none"
                    if getstudent != "none":
                        try:
                            getfees = Fees.objects.get(student = getstudent)
                        except Fees.DoesNotExist:
                            getfees = "none"
                        try:
                            getenrolled = Enrolled.objects.get(student=getstudent.id)
                        except Enrolled.DoesNotExist:
                            getenrolled = "none"
                        studentserializer = StudentSerializer(getstudent,many=False)
                        
                        if getfees != "none":
                            feeserializer = FeesSerializer(getfees,many=False)
                        else:
                            feeserializer = "none"
                        enrolledserializer = EnrolledSerializer(getenrolled,many=False)
                        print(studentserializer.data)
                        print(enrolledserializer.data)
                        # print(feeserializer.data)
                            
    params = {
        "display":display
    }
    return render(request,"registration_cash.html",params)

@login_required(login_url='/login/')
def PendingFees(request):
    display = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            display = "yes"
        else:
            print("no")
    allstudentdata = Student.objects.all()
    allstudents = []
    sem1 = ''
    sem2 = ''
    sem3 = ''
    sem4 = ''
    sem5 = ''
    sem6 = ''
    sem7 = ''
    sem8= ''
    total = ''
    for i in allstudentdata:
        temp = []
        specialization = Specialization.objects.get(id=i.field)
        try:
            feesdata = Fees.objects.get(student=i.id)
        except Fees.DoesNotExist:
            feesdata = "Data Not Present"
        if feesdata != "Data Not Present":
            sem1fees = feesdata.sem1
            sem2fees = feesdata.sem2
            sem3fees = feesdata.sem3
            sem4fees = feesdata.sem4
            sem5fees = feesdata.sem5
            sem6fees = feesdata.sem6
            sem7fees = feesdata.sem7
            sem8fees = feesdata.sem8

            
            paidsem1 = feesdata.paidsem1
            paidsem2 = feesdata.paidsem2
            paidsem3 = feesdata.paidsem3
            paidsem4 = feesdata.paidsem4
            paidsem5 = feesdata.paidsem5
            paidsem6 = feesdata.paidsem6
            paidsem7 = feesdata.paidsem7
            paidsem8 = feesdata.paidsem8
            
            
            
            
            if sem1fees and paidsem1:
                sem1balance = int(sem1fees) - int(paidsem1)
            else:
                sem1balance = int(0)

            if sem2fees and paidsem2:
                sem2balance = int(sem2fees) - int(paidsem2)
            else:
                sem2balance = int(0)

            if sem3fees and paidsem3:
                sem3balance = int(sem3fees) - int(paidsem3)
            else:
                sem3balance = int(0)

            if sem4fees and paidsem4:
                sem4balance = int(sem4fees) - int(paidsem4)
            else:
                sem4balance = int(0)

            if sem5fees and paidsem5:
                sem5balance = int(sem5fees) - int(paidsem5)
            else:
                sem5balance = int(0)

            if sem6fees and paidsem6:
                sem6balance = int(sem6fees) - int(paidsem6)
            else:
                sem6balance = int(0)

            if sem7fees and paidsem7:
                sem7balance = int(sem7fees) - int(paidsem7)
            else:
                sem7balance = int(0)

            if sem8fees and paidsem8:
                sem8balance = int(sem8fees) - int(paidsem8)
            else:
                sem8balance = int(0)
            if specialization.duration != "Not Present":
                durationofsem = int(specialization.duration) * 2
                if durationofsem == 2:
                    total = sem1balance + sem2balance
                elif durationofsem == 4:
                    total = sem1balance + sem2balance + sem3balance + sem4balance
                elif durationofsem == 6:
                    total = sem1balance + sem2balance + sem3balance + sem4balance + sem5balance + sem6balance
                elif durationofsem == 8:
                    total = sem1balance + sem2balance + sem3balance + sem4balance + sem5balance + sem6balance + sem7balance + sem8balance
           
            
            
        data = total
        if data != 0:
            obj = {
                "firstname":i.firstname,
                "lastname":i.lastname,
                "email":i.email,
                "mobile":i.mobile,
                "degree":i.degree,
                "field":specialization.type,
                "enrollmentid":i.enrollmentid,
                "enrollmentdate":i.enrollmentdate,
                "address":i.address,
                "dob":i.dob,
                "gender":i.gender,
                "totalsem1":feesdata.sem1,
                "totalsem2":feesdata.sem2,
                "totalsem3":feesdata.sem3,
                "totalsem4":feesdata.sem4,
                "totalsem5":feesdata.sem5,
                "totalsem6":feesdata.sem6,
                "totalsem7":feesdata.sem7,
                "totalsem8":feesdata.sem8,
                'totalpending':total
                
            }
            allstudents.append(obj)
    print(allstudents)
    params= {
        "studentdata":allstudents,
        "display":display
    }
        
    return render(request,"pendingfees.html",params)

@login_required(login_url='/login/')
def PaidFees(request):
    display = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            display = "yes"
        else:
            print("no")
    params = {
        "display":display
    }
    return render(request,"paidfees.html",params)

@login_required(login_url='/login/')
def StudentReport(request):
    display = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            display = "yes"
        else:
            print("no")
    params = {
        "display":display
    }
    return render(request,"studentreport.html",params)

@login_required(login_url='/login/')
def AddUniversity(request):
    display = ""
    level_of_user = ""
    universitysame = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4" or level.level =="2":
            display = "yes"
            level_of_user = level.level
            if request.method == "POST":
                edit_university_id = request.POST.get('edit_university_id')
                edit_university_name = request.POST.get('edit_university_name')
                edit_university_address = request.POST.get('edit_university_address')
                edit_university_state = request.POST.get('edit_university_state')
                edit_university_city = request.POST.get('edit_university_city')
                edit_university_pincode = request.POST.get('edit_university_pincode')
                edit_university_logo = request.FILES.get('edit_university_logo', False)
                if edit_university_id:
                    print(edit_university_id,edit_university_name,edit_university_address,edit_university_state,edit_university_city,edit_university_pincode,edit_university_logo)
                    try:
                        university = University.objects.get(id = edit_university_id)
                        university.university_name = edit_university_name
                        university.university_address = edit_university_address
                        university.university_state = edit_university_state
                        university.university_city = edit_university_city
                        university.university_pincode = edit_university_pincode
                        university.university_logo = edit_university_logo
                        university.save()
                        return JsonResponse({'updated':'yes'})
                    except University.DoesNotExist:
                        pass




                university_name = request.POST.get('university_name')
                university_address = request.POST.get('university_address')
                university_city = request.POST.get('university_city')
                university_state = request.POST.get('university_state')
                university_pincode = request.POST.get('university_pincode')
                try:
                    university_logo = request.FILES['university_logo']
                except KeyError:
                    university_logo = ''
                if university_name:
                    try:
                        checkuniversity = University.objects.get(university_name = university_name)
                        if checkuniversity:
                            universitysame = "yes"
                    except University.DoesNotExist:
                        removespaces = university_name.replace(' ','')
                        lowercase = removespaces.lower()
                        today = str(date.today())
                        today = today.replace('-','')
                        registrationID = str(lowercase) + str(today) + str('UNI')
                        adduniversity = University(university_name=university_name,university_address=university_address,university_city=university_city,university_state=university_state,university_pincode=university_pincode,university_logo=university_logo,registrationID=registrationID)
                        adduniversity.save()
                        return redirect('adduniversity')
                        # print(regstrationID)
                        # print(university_name)
                        # print(university_address)
                        # print(university_city)
                        # print(university_state)
                        # print(university_pincode)
                        # print(university_logo)
                    
                
    params = {
        "display":display,
        "level_of_user":level_of_user,
        "universitysame":universitysame,
        "universities":University.objects.all()
    }
    return render(request,'adduniversity.html',params)

@login_required(login_url='/login/')
def AddStreamFees(request):
    print("yes")
    display = ""
    getstream = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            display = "yes"
            if request.method == "POST":
                coursename = request.POST.get('c_name')
                streamname = request.POST.get('s_name')
                data = request.POST.get('data')
                sem1 = request.POST.get('sem1')
                sem2 = request.POST.get('sem2')
                sem3 = request.POST.get('sem3')
                sem4 = request.POST.get('sem4')
                sem5 = request.POST.get('sem5')
                sem6 = request.POST.get('sem6')
                sem7 = request.POST.get('sem7')
                sem8 = request.POST.get('sem8')
                course_id = request.POST.get('course_id')
                stream_id = request.POST.get('stream_id')
                print("course name :",coursename, "stream name :",streamname )
                print("data",data)
                if data:
                    try:
                        getstream = Stream.objects.filter(course=data)
                        print(getstream)
                    except Stream.DoesNotExist:
                        getstream = "yes"
                    if getstream != "yes":
                        streamserializer = StreamSerializer(getstream,many=True)
                        return JsonResponse({'stream':streamserializer.data})
                    
                    
                if coursename and streamname:
                    stream = Stream.objects.get(id =streamname)
                    print(stream)
                    streamserializer = StreamSerializer(stream,many=False)
                    
                    streamfees= ''
                    
                    try:
                        getstreamfees = StreamFees.objects.get(Q(course = coursename) and Q(stream = streamname))
                        print("yes fot streamfees :",getstreamfees)
                        streamfees = "yes"
                        
                    except StreamFees.DoesNotExist:
                       
                        print("didn't got streamfees creating one..")
                        # if course_id and stream_id and (sem1 or sem2 or sem3 or sem4 or sem5 or sem6 or sem7 or sem8):
                        #     addstreamfees = StreamFees(course=course_id,stream=stream_id,sem1= sem1,sem2=sem2,sem3=sem3,sem4=sem4,sem5=sem5,sem6=sem6,sem7=sem7,sem8=sem8)
                        #     addstreamfees.save()
                    
                    if streamfees == "yes":
                        streamfeesserializer = StreamFeesSerializer(getstreamfees,many=False)
                        return JsonResponse({'streamfees':streamfeesserializer.data,'stream':streamserializer.data})
                    else:
                        return JsonResponse({'stream':streamserializer.data})
                    
                if course_id and stream_id and (sem1 or sem2 or sem3 or sem4 or sem5 or sem6 or sem7 or sem8):
                    try:
                        getstreamfees = StreamFees.objects.get(Q(course = course_id) and Q(stream = stream_id))
                        print(course_id,stream_id)
                        print("present")
                        if sem1:
                            getstreamfees.sem1 = sem1
                            getstreamfees.save()
                        if sem2:
                            getstreamfees.sem2 = sem2
                            getstreamfees.save()
                        if sem3:
                            getstreamfees.sem3 = sem3
                            getstreamfees.save()
                        if sem4:
                            getstreamfees.sem4 = sem4
                            getstreamfees.save()
                        if sem5:
                            getstreamfees.sem5 = sem5
                            getstreamfees.save()
                        if sem6:
                            getstreamfees.sem6 = sem6
                            getstreamfees.save()
                        if sem7:
                            getstreamfees.sem7 = sem7
                            getstreamfees.save()
                        if sem8:
                            getstreamfees.sem8 = sem8
                            getstreamfees.save()
                        
                        
                    except StreamFees.DoesNotExist:
                        print("not present")
                        if course_id and stream_id and (sem1 or sem2 or sem3 or sem4 or sem5 or sem6 or sem7 or sem8):
                            addstreamfees = StreamFees(course=course_id,stream=stream_id,sem1= sem1,sem2=sem2,sem3=sem3,sem4=sem4,sem5=sem5,sem6=sem6,sem7=sem7,sem8=sem8)
                            addstreamfees.save()
                        
                        
                    
                # sem1 = request.POST.get('sem1')
                # sem2 = request.POST.get('sem2')
                # sem3 = request.POST.get('sem3')
                # sem4 = request.POST.get('sem4')
                # sem5 = request.POST.get('sem5')
                # sem6 = request.POST.get('sem6')
                # sem7 = request.POST.get('sem7')
                # sem8 = request.POST.get('sem8')
                # course_id = request.POST.get('course_id')
                # stream_id = request.POST.get('stream_id')
                # print(course_id,stream_id,sem1,sem2,sem3,sem4,sem5,sem6,sem7,sem8)
                # if coursename and streamname:
                #     stream = Stream.objects.get(id =streamname)
                #     print(stream)
                #     streamserializer = StreamSerializer(stream,many=False)
                    
                #     streamfees= ''
                #     try:
                #         getstreamfees = StreamFees.objects.get(Q(course = coursename) and Q(stream = streamname))
                #         streamfees = "yes"
                #     except StreamFees.DoesNotExist:
                #         addstreamfees = StreamFees(course=course_id,stream=stream_id,sem1= sem1,sem2=sem2,sem3=sem3,sem4=sem4,sem5=sem5,sem6=sem6,sem7=sem7,sem8=sem8)
                #         addstreamfees.save()
                #     if streamfees == "yes":
                #         streamfeesserializer = StreamFeesSerializer(getstreamfees,many=False)
                #         return JsonResponse({'streamfees':streamfeesserializer.data,'stream':streamserializer.data})
                #     else:
                #         print("no")
                
                    
                
                
                
                 
                # if data:
                #     try:
                #         getstream = Stream.objects.filter(course=data)
                #         print(getstream)
                #     except Stream.DoesNotExist:
                #         getstream = "yes"
                #     if getstream != "yes":
                #         streamserializer = StreamSerializer(getstream,many=True)
                #         return JsonResponse({'stream':streamserializer.data})
    params = {
        "display":display,
        "course":Course.objects.all()
    }
    
    return render(request,'addstreamfees.html',params)

@login_required(login_url='/login/')
def SetExam(request):
    get_course = request.GET.get('get_course')
    if get_course:
        print("University ID:",get_course)
        getcourse = Course.objects.filter(university = get_course)
        courseserializer = CourseSerializer(getcourse,many=True)
        return JsonResponse({'course':courseserializer.data})
    display = ""
    universitysame = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            display = "yes"
            if request.method == "POST":
                student_course_id = request.POST.get('student_course_id')
                student_stream_id = request.POST.get('student_stream_id')
                if student_course_id and student_stream_id:
                    getstream = Stream.objects.get(Q(id = student_stream_id) & Q(course = student_course_id))
                    return JsonResponse({'total_semester': getstream.sem})
                university = request.POST.get('university')
                course = request.POST.get('course')
                stream = request.POST.get('stream')
                exam_name = request.POST.get('exam_name')
                exam_date = request.POST.get('exam_date')
                total_marks = request.POST.get('total_marks')
                total_questions = request.POST.get('total_questions')
                # print(university,course,stream,exam_name,exam_date,total_marks,total_questions)
                data = request.POST
                # print(data)
                

                course_id = request.POST.get('course_id')
                # print(course_id)
                if course_id:
                    try:
                        getstream = Stream.objects.filter(course=course_id)
                        # print(getstream)
                    except Stream.DoesNotExist:
                        getstream = "yes"
                    if getstream != "yes":
                        streamserializer = StreamSerializer(getstream,many=True)
                        return JsonResponse({'stream':streamserializer.data})

                get_students_course_id = request.POST.get('get_students_course_id')
                get_students_stream_id = request.POST.get('get_students_stream_id')
                get_students_study_pattern = request.POST.get('get_students_study_pattern')
                get_students_semyear = request.POST.get('get_students_semyear')
                examination_all_student = []
                if get_students_course_id and get_students_stream_id and get_students_study_pattern and get_students_semyear:
                    print(get_students_course_id , get_students_stream_id , get_students_study_pattern , get_students_semyear)
                    get_total_enrolled = Enrolled.objects.filter(
                        course = get_students_course_id,
                        stream = get_students_stream_id,
                        course_pattern = get_students_study_pattern,
                        current_semyear = get_students_semyear
                    )
                    for i in get_total_enrolled:
                        try:
                            get_student = Student.objects.get(id = i.student)
                            examination_all_student.append(get_student)
                            
                        except Student.DoesNotExist:
                            pass
                    student_serializer = StudentSerializer(examination_all_student,many=True)
                    return JsonResponse({'data': student_serializer.data})
    params = {
        "display":display,
        "university":University.objects.all()
    }
    return render(request,"setexam.html",params)

@login_required
def SetExamination(request):
    display = ""
    level_of_user = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            level_of_user = level.level
            # all_questions = Questions.objects.all()
            # for i in all_questions:
            #     print(i.answer)
            display = "yes"
            if request.method == "POST":
                student_course_id = request.POST.get('student_course_id')
                student_stream_id = request.POST.get('student_stream_id')
                if student_course_id and student_stream_id:
                    print(student_course_id, student_stream_id)
                university = request.POST.get("university")
                course = request.POST.get("course")
                stream = request.POST.get('stream')
                exam_date = request.POST.get('exam_date')
                exam_time = request.POST.get('exam_time')
                exam_name = request.POST.get('exam_name')
                total_marks = request.POST.get('total_marks')
                array_data = request.POST.get('array_data')
                # if array_data:
                #     x = array_data.split(',')
                #     for i in x:
                #         try:
                #             getstudent = Student.objects.get(id = i)
                #             print("student :",getstudent)
                #         except Student.DoesNotExist:
                #             pass
                file =  request.FILES.get('upload_file')
                
                # if file:
                #     print("loop")
                #     df=pd.read_excel(file,sheet_name='Sheet1')
                #     for i in df.index:
                        # question = df['question'][i]
                        # image = df['image'][i]
                        # question_type = df['type'][i]
                        # marks = df['marks'][i]
                        # option1 = df['option1'][i]
                        # option2 = df['option2'][i]
                        # option3 = df['option3'][i]
                        # option4 = df['option4'][i]
                        # option5 = df['option5'][i]
                        # option6 =df['option6'][i]
                        # shortanswer = df['shortanswer'][i]
                        # answer =  df['answer'][i]
                        # print(answer , len(answer))
                        
                if university and file:
                    # print(university , file)
                    df=pd.read_excel(file,sheet_name='Sheet1')		
                   
                    #loop over the lines and save them in db. If error , store as string and then display
                    add_examination = Examination(university=university,course = course, stream = stream ,examname= exam_name,examdate=exam_date,examtime=exam_time,totalmarks=total_marks)
                    add_examination.save()
                    latest_examination = Examination.objects.latest('id')
                    count = 0
                    for i in df.index:
                        count = count + 1
                        question = df['question'][i]
                        image = df['image'][i]
                        question_type = df['type'][i]
                        marks = df['marks'][i]
                        option1 = df['option1'][i]
                        option2 = df['option2'][i]
                        option3 = df['option3'][i]
                        option4 = df['option4'][i]
                        option5 = df['option5'][i]
                        option6 =df['option6'][i]
                        shortanswer = df['shortanswer'][i]
                        answer =  df['answer'][i]
                        add_questions = Questions(
                            exam=latest_examination.id,
                            question=question,
                            image=image,
                            type=question_type,
                            marks=marks,
                            option1=option1,
                            option2=option2,
                            option3=option3,
                            option4=option4,
                            option5=option5,
                            option6=option6,
                            shortanswer=shortanswer,
                            answer=answer)
                        add_questions.save()
                    latest_examination.totalquestions = count
                    latest_examination.save()
                    # print("Count :",count)
                    # print("data len",len(data))
                    if array_data:
                        # print("exam time :",exam_time)
                        # d = datetime.strptime(exam_time, "%H:%M")
                        # now = datetime.now()
                        # current_time = now.strftime("%I:%M %p")
                        # print("Current Time =", current_time)
                        # if current_time > d.strftime("%I:%M %p"):
                        #     print("current time greater")
                        # else:
                        #     print("current time is less")
                        # print("Exam time is :",d.strftime("%I:%M %p"))


                        x = array_data.split(',')
                        for i in x:
                            print("added student :",i, " for exam :",latest_examination.id)
                            add_StudentAppearingExam = StudentAppearingExam(
                                exam = latest_examination.id,
                                student = i
                                )
                            add_StudentAppearingExam.save()
                    return JsonResponse({'saved':'yes'})    


                        
                        
    params = {
        "display":display,
        "university":University.objects.all(),
        "level_of_user":level_of_user
    }
    return render(request,"setexamination.html",params)

@login_required(login_url='/login/')
def GiveExamination(request):
    
    display = ""
    error = ""
    exams = []
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "1":
            display = "yes"
            user_id = request.user.id
            student = Student.objects.get(user=user_id)
            # print(student.id)
            today = date.today()
            now = datetime.now()
            current_time = now.strftime("%I:%M %p")
            # print("Current date:", today,"Current time :",current_time)
            
            can_give_exam = StudentAppearingExam.objects.filter(student = student.id)
            if can_give_exam:
                enrolled = Enrolled.objects.get(student = student.id)
                for i in can_give_exam:
                    exam = Examination.objects.filter(Q(stream = enrolled.stream) & Q(id = i.exam))
                    for j in exam:
                        if str(j.examdate) == str(today):
                            exams.append(j)
            else:
                print("cant give exam")
            
            # enrolled = Enrolled.objects.get(student = student.id)
            # exam = Examination.objects.filter(stream = enrolled.stream)
            # for i in exam:
                # h, m, s = str(i.examtime).split(':')
                # exam_time = datetime.strptime(str(h)+":"+str(m), "%H:%M").strftime("%I:%M %p")
                # print("exam time: ",exam_time)

                # now = datetime.now()
                # current_time = now.strftime("%I:%M %p")
                # print("current time :",current_time)
                # # print("Current Time =", current_time)
            #     if current_time >= exam_time:
            #         print("You can give exam")
            #     else:
            #         print("There is time to give exam")
                # print("Exam time is :",d.strftime("%I:%M %p"))
                # try:
                #     result = Result.objects.get(Q(exam = i.id) & Q(student = user_id))
                #     # print("Exam ID :",i.id,type(i.id) , "Result Exam :",result.exam)
                #     if int(i.id) == int(result.exam):
                #         print("found")
                #     else:
                #         tester = 0
                #         # print("not found")
                # except Result.DoesNotExist:
                #     # print("not found")
                #     exams.append(i)
            if request.method == "POST":
                check_timing = request.POST.get("check_timing")
                if check_timing:
                    print("check timing :",check_timing)
                    try:
                        exam = Examination.objects.get(id = check_timing)
                        h, m, s = str(exam.examtime).split(':')
                        exam_time = datetime.strptime(str(h)+":"+str(m), "%H:%M").strftime("%I:%M %p")
                        # print("exam time: ",exam_time)
                        # print("current time :",current_time , ">" , " exam time :", exam_time)
                        if current_time >= exam_time:
                            try:
                                result = Result.objects.get(Q(exam = exam.id) & Q(student=student.id))
                                return JsonResponse({'error':"Examination already Given. Please Wait Until Result is Announced"})
                            except Result.DoesNotExist:
                                print("yupp no result hence can give exam")
                                return JsonResponse({'exam_id':exam.id})
                        else:
                            print("cannot give exam")
                            error = "Please Wait Till EXAM TIME. Exam Starts At : {}".format(exam_time)
                            return JsonResponse({'error':error})





                    except Examination.DoesNotExist:
                        print("no examination found")
                save_question_no = request.POST.get('save_question_no')
                save_question_id = request.POST.get('save_question_id')
                save_question_type = request.POST.get('save_question_type')
                save_question = request.POST.get('save_question')
                save_value = request.POST.get('save_value')
                
                uploaded_files = request.FILES.getlist('uploaded_files')
                if uploaded_files:
                    # print("uploaded_files :",uploaded_files)
                    print(save_question,save_question_type,save_question_id,save_value)
                if save_question_no and save_question_id and save_question_type and save_question and save_value:
                    print("got everything")
                    try:
                        getsubmittedanswer = SubmittedExamination.objects.get(Q(student = user_id) & Q(question = save_question_id))
                        print(getsubmittedanswer)
                        print("try is used")
                        getquestion = Questions.objects.get(id = getsubmittedanswer.question)
                        print(len(getquestion.answer))
                        if save_question_type == "radio" or save_question_type == "mcq(single)":
                            # print("question answer :",getquestion.answer , len(getquestion.answer))
                            # print("submitted answer :",submitted_answer , len(submitted_answer))
                            if str(getquestion.answer) == str(save_value):
                                print("right answer")
                                print("getsubmittedanswer:",getsubmittedanswer)
                                getsubmittedanswer.marks_obtained=getquestion.marks
                                getsubmittedanswer.submitted_answer=save_value
                                getsubmittedanswer.result="right"
                                getsubmittedanswer.save()
                                print("data saved")
                                
                            else:
                                print("wrong answer")
                                getsubmittedanswer.marks_obtained=0
                                getsubmittedanswer.submitted_answer=save_value
                                getsubmittedanswer.result="wrong"
                                getsubmittedanswer.save()
                        elif save_question_type == "mcq(multiple)":
                            answer = getquestion.answer.split(",")
                            # print(len(answer),answer)
                            count = 0
                            save_values_list = save_value.split(",")
                            # print(len(save_values_list),save_values_list)
                            for j in answer:
                                for k in save_values_list:
                                    if k == j:
                                        count = count +1
                            length_of_answer = len(answer)
                            marks_per_answer = len(answer)/int(getquestion.marks)
                            # print("marks per answer:",math.trunc(marks_per_answer))
                            set_marks = int(count) * math.trunc(marks_per_answer)
                            # marks_obtained = marks_obtained + int(set_marks)
                            # print("set_marks:",set_marks)


                            getsubmittedanswer.marks_obtained=set_marks
                            getsubmittedanswer.submitted_answer=save_value
                            getsubmittedanswer.result="right"
                            getsubmittedanswer.save()
                            
                        elif save_question_type == "shortanswer":
                            
                            getsubmittedanswer.submitted_answer=save_value
                            getsubmittedanswer.save()
                        elif save_question_type == "long_desc":
                            print("try used and long desc") 
                            getsubmittedanswer.submitted_answer = save_value
                            getsubmittedanswer.save()
                            get_all_uploads = Descriptive_Answer.objects.filter(Q(student=user_id) & Q(exam = getquestion.exam) & Q(question = getquestion.id))
                            print("all uploads :",get_all_uploads)
                            if uploaded_files:
                                get_all_uploads.delete()
                                for i in uploaded_files:
                                    save_descriptive = Descriptive_Answer(
                                        student = user_id,
                                        exam = getquestion.exam,
                                        question = getquestion.id,
                                        upload = i
                                    )
                                    save_descriptive.save()

                    except SubmittedExamination.DoesNotExist:
                        print("except is used")
                        getquestion = Questions.objects.get(id = save_question_id)
                        if save_question_type == "radio" or save_question_type == "mcq(single)":
                            if getquestion.answer == save_value:
                                # print("right answer")
                                # marks_obtained = marks_obtained + int(getquestion.marks)
                                submitanswer = SubmittedExamination(
                                    student=user_id,
                                    exam=getquestion.exam,
                                    question=getquestion.id,
                                    type=getquestion.type,
                                    marks=getquestion.marks,
                                    marks_obtained=getquestion.marks,
                                    submitted_answer=save_value,
                                    answer=getquestion.answer,
                                    result="right"
                                    )
                                submitanswer.save()
                            else:
                                # print("wrong answer")
                                submitanswer = SubmittedExamination(
                                    student=user_id,
                                    exam=getquestion.exam,
                                    question=getquestion.id,
                                    type=getquestion.type,
                                    marks=getquestion.marks,
                                    marks_obtained=0,
                                    submitted_answer=save_value,
                                    answer=getquestion.answer,
                                    result="wrong"
                                    )
                                submitanswer.save()
                        elif save_question_type == "mcq(multiple)":
                            answer = getquestion.answer.split(",")
                            # print(len(answer),answer)
                            count = 0
                            save_values_list = save_value.split(",")
                            # print(len(save_values_list),save_values_list)
                            for j in answer:
                                for k in save_values_list:
                                    if k == j:
                                        count = count +1
                            length_of_answer = len(answer)
                            marks_per_answer = len(answer)/int(getquestion.marks)
                            # print("marks per answer:",math.trunc(marks_per_answer))
                            set_marks = int(count) * math.trunc(marks_per_answer)
                            # marks_obtained = marks_obtained + int(set_marks)
                            # print("set_marks:",set_marks)
                            submitanswer = SubmittedExamination(
                                student=user_id,
                                exam=getquestion.exam,
                                question=getquestion.id,
                                type=getquestion.type,
                                marks=getquestion.marks,
                                marks_obtained=set_marks,
                                submitted_answer=save_value,
                                answer=getquestion.answer,
                                result="right"
                                )
                            submitanswer.save()
                        elif save_question_type == "shortanswer":
                            
                            submitanswer = SubmittedExamination(
                                student=user_id,
                                exam=getquestion.exam,
                                question=getquestion.id,
                                type=getquestion.type,
                                marks=getquestion.marks,
                                marks_obtained=0,
                                submitted_answer=save_value,
                                answer=getquestion.answer,
                                result="pending"
                                )
                            submitanswer.save()
                        elif save_question_type == "long_desc":
                            print("saved question long description")
                            submitanswer = SubmittedExamination(
                                student=user_id,
                                exam=getquestion.exam,
                                question=getquestion.id,
                                type=getquestion.type,
                                marks=getquestion.marks,
                                marks_obtained=0,
                                submitted_answer=save_value,
                                answer=getquestion.answer,
                                result="pending"
                                )
                            submitanswer.save()
                            if uploaded_files:
                                for i in uploaded_files:
                                    print(i)
                                    save_descriptive = Descriptive_Answer(
                                        student = user_id,
                                        exam = getquestion.exam,
                                        question = getquestion.id,
                                        upload = i
                                    )
                                    save_descriptive.save()
                exam_id_timer = request.POST.get('exam_id_timer')
                exam_in_minutes = request.POST.get('exam_in_minutes')
                if exam_id_timer and exam_in_minutes:
                    # print("Time :", exam_in_minutes,exam_id_timer)
                    try:
                        getexaminationtime = StudentExaminationTime.objects.get(Q(student = student.id ) & Q(exam = exam_id_timer))
                        getexaminationtime.time_in_minutes = exam_in_minutes
                        getexaminationtime.save()
                        # print("examination time found",getexaminationtime,"time left:",exam_in_minutes)
                    except StudentExaminationTime.DoesNotExist:
                        # print("timer not found")
                        create_timer = StudentExaminationTime(
                            student = student.id,
                            exam = exam_id_timer,
                            time_in_minutes = 180
                        )
                        create_timer.save()
                # print(request.POST)
                # print("1 16 radio what is 10+10? option4")
                # print("2 17 radio what is a sun? option3")
                # print("3 18 mcq(single) what is a rose option1")
                # print("4 19 mcq(single) what is 1+1? option2")
                # print("5 20 mcq(multiple) select animal from following option1")
                # print("5 20 mcq(multiple) select animal from following option2")
                # print("6 21 shortanswer write in brief what is a star star")
                # print("_____________________________________________________________________________________________")
                result_exam_id = request.POST.get('result_exam_id')
                question_count = request.POST.get("count")
                if question_count and result_exam_id:
                    question_count = int(question_count)
                    marks_obtained = 0
                    print(result_exam_id)
                    getexamination = Examination.objects.get(id = result_exam_id)
                    get_submitted_questions = SubmittedExamination.objects.filter(Q(student = user_id) & Q(exam = result_exam_id))
                    for i in get_submitted_questions:
                        marks_obtained = int(i.marks_obtained) + marks_obtained
                    print("total_marks : ",getexamination.totalmarks , "Marks Obtained : ",marks_obtained)
                    total_marks_of_exam = getexamination.totalmarks
                    percentage_of_marks_obtained = (int(marks_obtained) / int(total_marks_of_exam) )* 100
                    print("total marks :",total_marks_of_exam , "marks obained :",marks_obtained)
                    print("percentage_of_marks_obtained :",percentage_of_marks_obtained)
                    if(percentage_of_marks_obtained >= 35):
                        result = "Pass"
                    else:
                        result = "Fail"
                    set_result = Result(
                        student=student.id,
                        exam=result_exam_id,
                        total_question=getexamination.totalquestions,
                        attempted=question_count,
                        total_marks=getexamination.totalmarks,
                        score=marks_obtained,
                        result=result
                        )
                    set_result.save()
                    return JsonResponse({'added':'yes'})
                        #sun is an astonomical object made up of hydrogen and helium which generates plasma and since it has huge mass it creates a huge gravity.
                exam_id = request.POST.get('exam_id')
                if exam_id:
                    hours = 0
                    minutes = 0
                    try:
                        getexaminationtime = StudentExaminationTime.objects.get(Q(student = student.id ) & Q(exam = exam_id))
                        # print("time data available",getexaminationtime)
                        get_time_in_minutes = int(getexaminationtime.time_in_minutes)
                        time_string = str(timedelta(minutes=get_time_in_minutes))[:-3]
                        data_list = time_string.split(":")
                        hours = data_list[0]
                        minutes = data_list[1]
                        print(hours , minutes)

                        # getexaminationtime.time_in_minutes = (int(hours) * 60 ) + int(minutes)
                        # getexaminationtime.save()
                        # print("examination time found",getexaminationtime,"time left:",(int(hours) * 60 ) + int(minutes))
                    except StudentExaminationTime.DoesNotExist:
                        print("time data not available")
                        # print("timer not found",(int(hours) * 60 ) + int(minutes))
                        # create_timer = StudentExaminationTime(
                        #     student = student.id,
                        #     exam = exam_id_timer,
                        #     time_in_minutes = (int(hours) * 60 ) + int(minutes)
                        # )
                        # create_timer.save()
                    getexamination = Examination.objects.get(id=exam_id)
                    getquestions = Questions.objects.filter(exam = getexamination.id)
                    questionsserializer = QuestionsSerializer(getquestions, many=True)
                    temp = []
                    for i in getquestions:
                        # print(i)
                        try:
                            get_submitted_questions = SubmittedExamination.objects.get(Q(student = user_id) & Q(exam = exam_id) & Q(question=i.id))
                            print("get submitted questions :",get_submitted_questions)
                            submitted_answer = get_submitted_questions.submitted_answer
                        except SubmittedExamination.DoesNotExist:
                            submitted_answer = ""
                        
                        obj = {
                            "id":i.id,
                            "exam":i.exam,
                            "question":i.question,
                            "image":i.image,
                            "type":i.type,
                            "marks":i.marks,
                            "option1":i.option1,
                            "option2":i.option2,
                            "option3":i.option3,
                            "option4":i.option4,
                            "option5":i.option5,
                            "option6":i.option6,
                            "shortanswer":i.shortanswer,
                            "answer":i.answer,
                            "submitted_answer":submitted_answer
                        }
                        temp.append(obj)
                    print(temp)
                    return JsonResponse({'data':temp,'exam_id':getexamination.id,'hours':hours,'minutes':minutes})
                # show = request.POST.get('show')
                # if show == "yes":
                #     getexamination = Examination.objects.latest('id')
                #     getquestions = Questions.objects.filter(exam = getexamination.id)
                #     questionsserializer = QuestionsSerializer(getquestions, many=True)
                #     return JsonResponse({'data':questionsserializer.data})
            # print(exams)
    params = {
        "display":display,
        "exams":exams,
        "error":error
    }
    return render(request,"give_examination.html",params)


def ExamSubmitted(request):
    return render(request,"exam_submitted.html")

def CheckResult(request):
    display = ""
    level_of_user = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            level_of_user = level.level
            display = "yes"
            if request.method == "POST":
                course_id = request.POST.get('course_id')
                stream_id = request.POST.get('stream_id')
                if course_id and stream_id:
                    getexamination = Examination.objects.filter(Q(course=course_id) & Q(stream=stream_id))
                    examinationserializer = ExaminationSerializer(getexamination,many=True)
                    return JsonResponse({'data':examinationserializer.data})

                exam_id = request.POST.get('exam_id')
                if exam_id:
                    all_data = []
                    get_all_results = Result.objects.filter(exam= exam_id)
                    for i in get_all_results:
                        getstudent = Student.objects.get(id = i.student)
                        percentage_of_marks_obtained = (int(i.score) / int(i.total_marks) )* 100
                        print("total marks :",i.total_marks , "marks obained :",i.score)
                        percentage_of_marks_obtained = round(percentage_of_marks_obtained,2)
                        print("percentage_of_marks_obtained :",percentage_of_marks_obtained)
                        obj = {
                            "exam_id":i.exam,
                            "name":getstudent.name,
                            "email":getstudent.email,
                            "enrollment_id":getstudent.enrollment_id,
                            "total_question":i.total_question,
                            "total_marks":i.total_marks,
                            "score":i.score,
                            "result":i.result,
                            "percentage":percentage_of_marks_obtained
                        }
                        all_data.append(obj)
                    return JsonResponse({'data':all_data})
                    
                student_id = request.POST.get('check_result_student_id')
                check_result_exam_id = request.POST.get('check_result_exam_id')
                
                if student_id and check_result_exam_id:
                    print("student id :",student_id , "exam id :",check_result_exam_id)
                    try:
                        all_questions_data = []
                        getstudent = Student.objects.get(enrollment_id = student_id)
                        get_submitted_questions = SubmittedExamination.objects.filter(Q(student=getstudent.user) & Q(exam = check_result_exam_id))
                        for i in get_submitted_questions:
                            getquestion = Questions.objects.get(id=i.question)
                            # print("selected answer : ",i.answer)
                            question_answer = ''
                            if i.type == "radio" or i.type == "mcq(single)":
                                # print("submitted_answer :",selected_ans)
                                if i.submitted_answer == "option1":
                                    selected_answer = getquestion.option1
                                elif i.submitted_answer == "option2":
                                    selected_answer = getquestion.option2
                                elif i.submitted_answer == "option3":
                                    selected_answer = getquestion.option3
                                elif i.submitted_answer == "option4":
                                    selected_answer = getquestion.option4
                                if i.answer == "option1":
                                    question_answer = getquestion.option1
                                elif i.answer == "option2":
                                    question_answer = getquestion.option2
                                elif i.answer == "option3":
                                    question_answer = getquestion.option3
                                elif i.answer == "option4":
                                    question_answer = getquestion.option4
                            elif i.type == "mcq(multiple)":
                                answers = i.submitted_answer.split(",")
                                question_answer_list = getquestion.answer.split(",")
                                answer_list = []
                                temp_question_answer_list = []
                                for j in answers:
                                    if j == "option1":
                                        answer_list.append(getquestion.option1)
                                    elif j == "option2":
                                        answer_list.append(getquestion.option2)
                                    elif j == "option3":
                                        answer_list.append(getquestion.option3)
                                    elif j == "option4":
                                        answer_list.append(getquestion.option4)
                                for j in question_answer_list:
                                    if j == "option1":
                                        temp_question_answer_list.append(getquestion.option1)
                                    elif j == "option2":
                                        temp_question_answer_list.append(getquestion.option2)
                                    elif j == "option3":
                                        temp_question_answer_list.append(getquestion.option3)
                                    elif j == "option4":
                                        temp_question_answer_list.append(getquestion.option4)
                                selected_answer = ",".join(answer_list)
                                question_answer = ",".join(temp_question_answer_list)
                            elif i.type == "shortanswer":
                                selected_answer = i.submitted_answer
                                question_answer = i.answer
                                
                            obj = {
                                "question":getquestion.question,
                                "answer":question_answer,
                                "submitted_answer":selected_answer,
                                "marks":i.marks,
                                "marks_obtained":i.marks_obtained,
                                "test":"test"
                            }
                            all_questions_data.append(obj)
                        
                        
                        return JsonResponse({'data':all_questions_data})
                    except Student.DoesNotExist:
                        print("no student with that enrollment")


    params = {
        "display":display,
        "university":University.objects.all(),
        "level_of_user":level_of_user
    }
    return render(request,"check_result.html",params)

@login_required(login_url='/login/')
def UserCreation(request):
    display = ""
    main = []
    level_of_user = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            level_of_user = level.level
            display = "yes"
            alluserlevel = UserLevel.objects.filter(~Q(level = '1') & ~Q(level='4'))
            
            for i in alluserlevel:
                try:
                    alluser = User.objects.get(id=i.user_id)
                    print(alluser)
                    obj = {
                        "email":alluser.email,
                        "level":i.level
                    }
                    main.append(obj)
                except User.DoesNotExist:
                    print("user doesnt exist")
            print(main)
            if request.method == "POST":
                useremail = request.POST.get('email')
                userpassword = request.POST.get('password')
                userlevel = request.POST.get('level')
                if useremail and userpassword and userlevel:
                    createuser = User.objects.create_user(email=useremail,password=userpassword)
                    createuser.save()
                    getlatestuser = User.objects.latest('id')
                    createuserlevel = UserLevel(user=getlatestuser,level=userlevel)
                    createuserlevel.save()
                    getlatest_level = UserLevel.objects.get(user=getlatestuser)
                    obj1 = {
                        "email":getlatestuser.email,
                        "level":getlatest_level.level
                    }
                    return JsonResponse({'created':'sucessfully','user':obj1})
    params = {
        "display":display,
        "main":main,
        "level_of_user":level_of_user
    }
    return render(request,"user_creation.html",params)


def export_users_xls(request,student_ids):
    students = student_ids.split(',')
    print("students :",students)
    temp = []
    for i in students:
        getstudent = Student.objects.get(id = i)
        enrolled = Enrolled.objects.get(student= getstudent.id)
        course = Course.objects.get(id=enrolled.course)
        stream = Stream.objects.get(id = enrolled.stream)
        test_tuple = (
            getstudent.name,
            getstudent.email,
            getstudent.mobile,
            getstudent.enrollment_id,
            enrolled.course_pattern,
            enrolled.total_semyear,
            enrolled.current_semyear,
            course.name,
            stream.name
        )
        temp.append(test_tuple)
    # print("test_tuple :",temp)
    # for i in temp:
    #     print(i.values)
    # print("Temp : ",temp)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="DataSet.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Data Export') # this will make a sheet named Users Data

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Name', 'Email Address', 'Mobile' , 'Enrollment ID','Course Pattern' , 'Total Semester', 'Current Semester' , 'Course Name', 'Stream Name']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style) # at 0 row 0 column 

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = Student.objects.all().values_list('name', 'email' , 'mobile' , 'enrollment_id','dateofbirth')
    # print("rows :",rows)

    for row in temp:
        # print("row : ",row)
        # print("_______________________________________________________________________________________________________")
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)

    return response

def export_pdf(request,student_ids):
    students = student_ids.split(',')
    print("students :",students)
    temp = []
    for i in students:
        getstudent = Student.objects.get(id = i)
        enrolled = Enrolled.objects.get(student= getstudent.id)
        course = Course.objects.get(id=enrolled.course)
        stream = Stream.objects.get(id = enrolled.stream)
        stream = Stream.objects.get(id = enrolled.stream)
        paymentreciept = PaymentReciept.objects.filter(student=getstudent.id)
        payment_reciept_serializer = PaymentRecieptSerializer(paymentreciept,many=True)
        obj = {
            "student_id":getstudent.id,
            "name":getstudent.name,
            "email":getstudent.email,
            "mobile":getstudent.mobile,
            "enrollment_id":getstudent.enrollment_id,
            "course_pattern":enrolled.course_pattern,
            "total_semyear":enrolled.total_semyear,
            "current_semyear":enrolled.current_semyear,
            "course":course.name,
            "stream":stream.name,
            "paymentreciept":payment_reciept_serializer.data
        }
        temp.append(obj)
    print("temp :",temp)
    params = {
        "data":temp
    }
    return render(request,"export_pdf.html",params)

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
@login_required(login_url='/login/')
def AdvanceSearch(request):
    display = ""
    temp = []
    level_of_user = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            level_of_user = level.level
            display = "yes"
            if 'term' in request.GET:
                q = request.GET.get('term', '')
                getstudents = Student.objects.filter(enrollment_date__icontains = q).order_by('-id')
                count = getstudents.count()
                print(count)
                studentserializer = StudentSerializer(getstudents,many=True)
                return JsonResponse({'student':studentserializer.data})
            if request.method == "POST":
                enroll_id = request.POST.get('search_enroll_id')
                university = request.POST.get('search_university')
                course = request.POST.get('search_course')
                stream = request.POST.get('search_stream')
                name = request.POST.get('search_name')
                registration_year = request.POST.get('search_registration_year')
                paid_fees_switch = request.POST.get('search_paid_fees_switch')
                pending_fees_switch = request.POST.get('search_pending_fees_switch')
                if enroll_id or university or course or stream or name or registration_year or paid_fees_switch=="true" or pending_fees_switch=="true":
                    print(enroll_id , university , course , stream , name , registration_year , paid_fees_switch , pending_fees_switch)
                    getstudents = []
                    if enroll_id:
                        getstudents = Student.objects.filter(
                            Q(enrollment_id__icontains = enroll_id) |
                            Q(email__icontains = enroll_id) |
                            Q(mobile__icontains = enroll_id)
                        )
                    elif name:
                        getstudents = Student.objects.filter(
                            Q(name__icontains = name) 
                        )
                    elif registration_year:
                        if getstudents:
                            getstudents = getstudents.filter(enrollment_date__icontains = registration_year)
                        else:
                            getstudents = Student.objects.filter(enrollment_date__icontains = registration_year)
                        print(getstudents)
                    
                    elif course and stream:
                        enrolled = Enrolled.objects.filter(Q(course = course) & Q(stream = stream))
                        for i in enrolled:
                            students = Student.objects.get(id = i.student)
                            getstudents.append(students)
                    elif paid_fees_switch == "true":
                        getallfees = PaymentReciept.objects.filter(pendingamount = 0)
                        for i in getallfees:
                            stud = Student.objects.get(id = i.student)
                            if stud in getstudents:
                                pass
                            else:
                                getstudents.append(stud)
                    elif pending_fees_switch == "true":
                        getallfees = PaymentReciept.objects.filter(~Q(pendingamount = 0))
                        print(getallfees)
                        for i in getallfees:
                            stud = Student.objects.get(id = i.student)
                            if stud in getstudents:
                                pass
                            else:
                                getstudents.append(stud)
                        print(getallfees)
                    # print("students :",getstudents)
                    for i in getstudents:
                        enrolled = Enrolled.objects.get(student= i.id)
                        course = Course.objects.get(id=enrolled.course)
                        stream = Stream.objects.get(id = enrolled.stream)
                        paymentreciept = PaymentReciept.objects.filter(student=i.id)
                        payment_reciept_serializer = PaymentRecieptSerializer(paymentreciept,many=True)
                        obj = {
                            "student_id":i.id,
                            "name":i.name,
                            "email":i.email,
                            "mobile":i.mobile,
                            "enrollment_id":i.enrollment_id,
                            "course_pattern":enrolled.course_pattern,
                            "total_semyear":enrolled.total_semyear,
                            "current_semyear":enrolled.current_semyear,
                            "course":course.name,
                            "stream":stream.name,
                            "paymentreciept":payment_reciept_serializer.data
                        }
                        temp.append(obj)
                
                    return JsonResponse({'student_data':temp})

                name = request.POST.get('name')
                if name:
                    getstudent = Student.objects.filter(Q(name = name) |  Q(name__icontains = name) |  Q(email__icontains = name))
                    for i in getstudent:
                        enrolled = Enrolled.objects.get(student= i.id)
                        course = Course.objects.get(id=enrolled.course)
                        stream = Stream.objects.get(id = enrolled.stream)
                        paymentreciept = PaymentReciept.objects.filter(student=i.id)
                        payment_reciept_serializer = PaymentRecieptSerializer(paymentreciept,many=True)
                        obj = {
                            "student_id":i.id,
                            "name":i.name,
                            "email":i.email,
                            "mobile":i.mobile,
                            "enrollment_id":i.enrollment_id,
                            "course_pattern":enrolled.course_pattern,
                            "total_semyear":enrolled.total_semyear,
                            "current_semyear":enrolled.current_semyear,
                            "course":course.name,
                            "stream":stream.name,
                            "paymentreciept":payment_reciept_serializer.data
                        }
                        temp.append(obj)
                    return JsonResponse({'student_data':temp})

                course_id = request.POST.get('course_id')
                stream_id = request.POST.get('stream_id')
                # if course_id and stream_id:
                #     enroll = Enrolled.objects.filter(Q(course = course_id) & Q(stream = stream_id))
                    # for i in enroll:
                    #     student = Student.objects.get(id=i.student)
                    #     enrolled = Enrolled.objects.get(student=student.id)
                    #     course = Course.objects.get(id=enrolled.course)
                    #     stream = Stream.objects.get(id = enrolled.stream)
                    #     paymentreciept = PaymentReciept.objects.filter(student=student.id)
                    #     payment_reciept_serializer = PaymentRecieptSerializer(paymentreciept,many=True)
                    #     obj = {
                    #         "name":student.name,
                    #         "email":student.email,
                    #         "mobile":student.mobile,
                    #         "enrollment_id":student.enrollment_id,
                    #         "course_pattern":enrolled.course_pattern,
                    #         "total_semyear":enrolled.total_semyear,
                    #         "current_semyear":enrolled.current_semyear,
                    #         "course":course.name,
                    #         "stream":stream.name,
                    #         "paymentreciept":payment_reciept_serializer.data
                    #     }
                    #     temp.append(obj)
                    # return JsonResponse({'student_data':temp})
                
                courseid = request.POST.get('courseid')
                if courseid:
                    getcourse = Course.objects.get(id=courseid)
                    getstream = Stream.objects.filter(course=getcourse)
                    streamserializer = StreamSerializer(getstream,many=True)
                    return JsonResponse({'stream':streamserializer.data})
                university_registration_id = request.POST.get('university_registration_id')
                if university_registration_id:
                    getuniversity = University.objects.get(registrationID = university_registration_id)
                    getcourse = Course.objects.filter(university = getuniversity.id)
                    courseserializer = CourseSerializer(getcourse,many=True)
                    return JsonResponse({'course':courseserializer.data})

                # enroll_id = request.POST.get('enroll_id')
                # if enroll_id:
                #     checkstudent = Student.objects.filter(Q(enrollment_id=enroll_id) | Q(mobile__icontains=enroll_id) | Q(email__icontains=enroll_id) | Q(name__icontains=enroll_id))
                    # for i in checkstudent:
                    #     enrolled = Enrolled.objects.get(student= i.id)
                    #     course = Course.objects.get(id=enrolled.course)
                    #     stream = Stream.objects.get(id = enrolled.stream)
                    #     paymentreciept = PaymentReciept.objects.filter(student=i.id)
                    #     payment_reciept_serializer = PaymentRecieptSerializer(paymentreciept,many=True)
                    #     obj = {
                    #         "name":i.name,
                    #         "email":i.email,
                    #         "mobile":i.mobile,
                    #         "enrollment_id":i.enrollment_id,
                    #         "course_pattern":enrolled.course_pattern,
                    #         "total_semyear":enrolled.total_semyear,
                    #         "current_semyear":enrolled.current_semyear,
                    #         "course":course.name,
                    #         "stream":stream.name,
                    #         "paymentreciept":payment_reciept_serializer.data
                    #     }
                    #     temp.append(obj)
                
                    # return JsonResponse({'student_data':temp})


                # search_enrollment_id = request.POST.get('search_enrollment_id')
                # if search_enrollment_id:
                #     getstudent = Student.objects.get(enrollment_id = search_enrollment_id)
                    


    params = {
        "display":display,
        "university":University.objects.all(),
        "level_of_user":level_of_user
    }
    return render(request,"advancesearch.html",params)

@login_required(login_url='/login/')
def SendEmail(request):
    display = ""
    if request.user.is_authenticated:
        level = UserLevel.objects.get(user = request.user.id)
        if level.level == "4":
            display = "yes"
            if request.method == "POST":
                subject = request.POST.get('subject')
                email = request.POST.get('email')
                message = request.POST.get('message')
                if subject and email and message:
                    logger.info(subject , email , message)
                    res = sm(
                    subject = subject,
                    message = message,
                    from_email = 'chandrakant.velocityconsultancy@gmail.com',
                    recipient_list = [email],
                    fail_silently=False,
                        )
                    return JsonResponse({'sent':'yes'})
                enroll_id = request.POST.get('enroll_id')
                if enroll_id:
                    try:
                        getstudent = Student.objects.get(Q(enrollment_id=enroll_id) | Q(mobile=enroll_id) | Q(email=enroll_id))
                        obj = {
                            "name":getstudent.name,
                            "email":getstudent.email
                        }
                        return JsonResponse({'student':'yes','details':obj})
                    except Student.DoesNotExist:
                        return JsonResponse({'student':'no'})
    params = {
        "display":display
    }
    return render(request,"sendemail.html",params)

@csrf_exempt
def PaymentSuccess(request):
    print("request")
    obj = {}
    if request.method == "POST":
        response = request.POST
        dumpdata = json.dumps(response)
        responsestring = json.loads(dumpdata)
        mihpayid = responsestring['mihpayid']
        mode = responsestring['mode']
        status = responsestring['status']
        unmappedstatus = responsestring['unmappedstatus']
        key = responsestring['key']
        txnid = responsestring['txnid']
        amount = responsestring['amount']
        cardCategory = responsestring['cardCategory']
        net_amount_debit = responsestring['net_amount_debit']
        addedon = responsestring['addedon']
        productinfo = responsestring['productinfo']
        firstname = responsestring['firstname']
        lastname = responsestring['lastname']

        email = responsestring['email']
        phone = responsestring['phone']
        payment_source = responsestring['payment_source']
        PG_TYPE = responsestring['PG_TYPE']
        bank_ref_num = responsestring['bank_ref_num']
        bankcode = responsestring['bankcode']
        cardnum = responsestring['cardnum']
        print(mihpayid)
        print(mode)
        print(status)
        print(unmappedstatus)
        print(key)
        print(txnid)
        print(amount)

        print(cardCategory)
        print(net_amount_debit)
        print(addedon)
        print(productinfo)
        print(firstname)
        print(lastname)

        print(email)
        print(phone)
        print(payment_source)
        print(PG_TYPE)
        print(bank_ref_num)
        print(bankcode)
        print(cardnum)
        try:
            getstudent = Student.objects.get(Q(email = email) & Q(mobile = phone))
            getenroll = Enrolled.objects.get(student = getstudent.id)
            getpaymentreciept = PaymentReciept.objects.filter(Q(student = getstudent.id) & Q(semyear = getenroll.current_semyear))
            print(getpaymentreciept)
            # add_payment_reciept = PaymentReciept(student = getstudent.id,fee_reciept_type="Course Fees",transaction_date= str(date.today()),cheque_no='',bank_name='',paidamount=net_amount_debit,pendingamount='0',transactionID = txnid,paymentmode='Online',remarks=status,session=getenroll.session,semyear=getenroll.current_semyear)
            add_payment_reciept = PaymentReciept(student = getstudent.id,payment_for="Course Fees",payment_type="Full Payment",fee_reciept_type="New",transaction_date= str(date.today()),cheque_no='',bank_name='',paidamount=net_amount_debit,pendingamount='0',transactionID = txnid,paymentmode='Online',remarks=status,session=getenroll.session,semyear=getenroll.current_semyear)
            add_payment_reciept.save()
    
            add_transactiondetails = TransactionDetails(transactionID=txnid,mihpayid=mihpayid,mode=mode,status=status,unmappedstatus=unmappedstatus,key=key,amount=amount,cardCategory=cardCategory,net_amount_debit=net_amount_debit,addedon=addedon,productinfo=productinfo,firstname=firstname,lastname=lastname,email=email,phone=phone,payment_source=payment_source,PG_TYPE=PG_TYPE,bank_ref_num=bank_ref_num,bankcode=bankcode,name_on_card='',cardnum=cardnum)
            add_transactiondetails.save()

            getlatestpaymentreciept = PaymentReciept.objects.latest('id')
            print("latest payment reciept :",getlatestpaymentreciept)
            paymentrecieptserializer = PaymentRecieptSerializer(getlatestpaymentreciept,many=False)
            view_student = Student.objects.get(id=getlatestpaymentreciept.student)
            view_enroll = Enrolled.objects.get(student=view_student.id)
            view_course = Course.objects.get(id = view_enroll.course)
            view_stream = Stream.objects.get(id = view_enroll.stream)
            temp = {
                "name":view_student.name,
                "email":view_student.email,
                "mobile":view_student.mobile,
                "enrollment_id":view_student.enrollment_id,
                "address":view_student.address,
                "country":view_student.country,
                "state":view_student.state,
                "city":view_student.city,
                "pincode":view_student.pincode,
                "course":view_course.name,
                "stream":view_stream.name
            }
            obj = {
                'view_reciept':paymentrecieptserializer.data,
                'personal':temp
                }
            
            
            
            
            
            res = sm(
                subject = "CIIS Payment Recieved",
                message = '''Thankyou For Making Payment of rs {} \n
                CIIS INDIA \n
                Click on the link below to download Invoice \n
                https://erp.ciisindia.in/getinvoice/{}'''.format(net_amount_debit,getlatestpaymentreciept.id),
                from_email = 'testmail@erp.ciisindia.in',
                recipient_list = [email],
                fail_silently=False,
                    )
            print(res)

        except Student.DoesNotExist:
            print("student Does not exist")
        try:
            getstudenttransaction = SaveStudentTransaction.objects.get(txnid = txnid)
            getstudenttransaction.status = "success"
            getstudenttransaction.used = "yes"
            getstudenttransaction.archived = "yes"
            getstudenttransaction.save()
        except SaveStudentTransaction.DoesNotExist:
            print("student transaction data not found")
        
    else:
        print("get")
    params = {
        "obj":obj
    }
    return render(request,"payment_success.html",params)

def GetInvoice(request,pk):
    # print(request.FILES)

    if request.method == "POST":
        print(request.FILES.get("file"))
        subject = "CIIS TEST"
        message = '''Thankyou For Making Payment of rs  \n
        CIIS INDIA \n
        '''
        from_email = 'testmail@erp.ciisindia.in'
        recipient_list = ["chandrakant.s.belell@gmail.com"]
        fail_silently=False,
        attach=request.FILES.get("file")
        # res = sm(
        #         subject = "CIIS TEST",
        #         message = '''Thankyou For Making Payment of rs  \n
        #         CIIS INDIA \n
        #         ''',
        #         from_email = 'testmail@erp.ciisindia.in',
        #         recipient_list = ["chandrakant.s.belell@gmail.com"],
        #         fail_silently=False,
        #         attach=request.FILES.get("file")
        #             )
        # mail = EmailMessage(
        #     subject
        #     , message
        #     , settings.EMAIL_HOST_USER,
        #      recipient_list)
        # mail.attach("invoice.pdf", attach.read(), attach.content_type)
        # mail.send()

    else:
        print("suifiu")
    data = {}
    try:
        getlatestpaymentreciept = PaymentReciept.objects.get(id=pk)
        print("latest payment reciept :",getlatestpaymentreciept)
        paymentrecieptserializer = PaymentRecieptSerializer(getlatestpaymentreciept,many=False)
        view_student = Student.objects.get(id=getlatestpaymentreciept.student)
        view_enroll = Enrolled.objects.get(student=view_student.id)
        view_course = Course.objects.get(id = view_enroll.course)
        view_stream = Stream.objects.get(id = view_enroll.stream)
        
        data = {
            'get_reciept_id':getlatestpaymentreciept.id,
            "name":view_student.name,
            "email":view_student.email,
            "mobile":view_student.mobile,
            "enrollment_id":view_student.enrollment_id,
            "address":view_student.address,
            "country":view_student.country,
            "state":view_student.state,
            "city":view_student.city,
            "pincode":view_student.pincode,
            "course":view_course.name,
            "stream":view_stream.name,
            "transactionID":getlatestpaymentreciept.transactionID,
            "transaction_date":getlatestpaymentreciept.transaction_date,
            "semyear":getlatestpaymentreciept.semyear,
            "paidamount":getlatestpaymentreciept.paidamount,
            "pendingamount":getlatestpaymentreciept.pendingamount,
            "paymentmode":getlatestpaymentreciept.paymentmode,
            "url":pk
        }
        print(data)
    except PaymentReciept.DoesNotExist:
        pass
    return render(request,"getinvoice.html",data)

@csrf_exempt
def PaymentFailure(request):
    responsestring = {'mihpayid': '403993715525829827', 'mode': 'CC', 'status': 'success', 'unmappedstatus': 'captured', 'key': '7rnFly', 'txnid': '34245223234332', 'amount': '10.00', 'cardCategory': 'domestic', 'discount': '0.00', 'net_amount_debit': '10', 'addedon': '2022-04-05 18:35:28', 'productinfo': 'test', 'firstname': 'chandrakant', 'lastname': 'belell', 'address1': '', 'address2': '', 'city': '', 'state': '', 'country': '', 'zipcode': '',\
         'email': 'chandrakant.s.belell@gmail.com', 'phone': '7021361784', 'udf1': '', 'udf2': '', 'udf3': '', 'udf4': '', 'udf5': '', 'udf6': '', 'udf7': '', 'udf8': '', 'udf9': '', 'udf10': '', 'hash': '024c02c2941c5bf0756125ac0d41476919f3c15644bd3bc47dacfc1830e027bdaab861af7d989a54f52b36916778c6b483c5facb75721df589105dc0cbd929cc', 'field1': '907030215644', 'field2': '723370', 'field3': '095876935603444', 'field4': 'cVcxczlPS1BNTmVUOHhBZzFBTTc=', 'field5': '02', 'field6': '', 'field7': 'AUTHPOSITIVE', 'field8': '', 'field9': '', 
         'payment_source': 'payu', 'PG_TYPE': 'HDFCPG', 'bank_ref_num': '095876935603444', 'bankcode': 'CC', 'error': 'E000', 'error_Message': 'No Error', 'name_on_card': 'uigig', 'cardnum': '512345XXXXXX2346', 'cardhash': 'This field is no longer supported in postback params.'}
    mihpayid = responsestring['mihpayid']
    mode = responsestring['mode']
    status = responsestring['status']
    unmappedstatus = responsestring['unmappedstatus']
    key = responsestring['key']
    txnid = responsestring['txnid']
    amount = responsestring['amount']
    cardCategory = responsestring['cardCategory']
    net_amount_debit = responsestring['net_amount_debit']
    addedon = responsestring['addedon']
    productinfo = responsestring['productinfo']
    firstname = responsestring['firstname']
    lastname = responsestring['lastname']

    email = responsestring['email']
    phone = responsestring['phone']
    payment_source = responsestring['payment_source']
    PG_TYPE = responsestring['PG_TYPE']
    bank_ref_num = responsestring['bank_ref_num']
    bankcode = responsestring['bankcode']
    name_on_card = responsestring['name_on_card']
    cardnum = responsestring['cardnum']

    
    
    return render(request,"payment_failure.html")

@csrf_exempt
def OnlinePayment(request,identifier):
    print(identifier)
    display = ""
    studentdata = {}
    try:
        getstudenttransaction = SaveStudentTransaction.objects.get(Q(student_identifier = identifier) & Q(used = "no") & Q(archived = "no"))
        studenttransactionserializer = SaveStudentTransactionSerializer(getstudenttransaction,many=False)
        studentdata = studenttransactionserializer.data
        display = "yes"
    except SaveStudentTransaction.DoesNotExist:
        print("not found")
        display = "no"
    params = {
        "display":display,
        "studentdata":studentdata
    }
    return render(request,"online_payment.html",params)
