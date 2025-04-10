from django.http.response import HttpResponse,JsonResponse
from django.shortcuts import render,HttpResponse,redirect   ,HttpResponseRedirect
from django.contrib.auth import authenticate,get_user_model,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from super_admin.models import *
from rest_framework.response import Response
from django.core.mail import send_mail as sm
from csv import reader
from csv import DictReader
from super_admin.serializers import *
import json
from datetime import date
from hashlib import sha512
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paywix.payu import Payu

# import pandas as pd 



# Create your views here.
@login_required(login_url='/login/')
def StudentProfile(request):
    obj = {}
    getstudent = ''
    if request.user.is_student:

            
        try:
            getstudent = Student.objects.get(email=request.user.email)
        except Student.DoesNotExist:
            getstudent = "none"
        if getstudent != "none":
            getenroll = Enrolled.objects.get(student=getstudent.id)
            getcourse = Course.objects.get(id = getenroll.course.id)
            getstream = Stream.objects.get(id = getenroll.stream.id)
            obj = {

                "name":getstudent.name,
                'father_name'  :getstudent.father_name,
                'mother_name'  :getstudent.mother_name,
                "image":getstudent.image,
                'dateofbirth'  :getstudent.dateofbirth,
                'mobile'  :getstudent.mobile,
                'email'  :getstudent.email,
                'gender'  :getstudent.gender,
                'category'  :getstudent.category,
                'address'   :getstudent.address,
                'nationality'  :getstudent.nationality,
                'country'  :getstudent.country.name,
                'state'  :getstudent.state.name,
                'city'  :getstudent.city.name,
                'pincode'  :getstudent.pincode,
                'registration_id' :getstudent.registration_id,
                'enrollment_id'  :getstudent.enrollment_id,
                'enrollment_date'  :getstudent.enrollment_date,
                'university'  :getstudent.university,
                'course_name':getcourse.name,
                'stream_name':getstream.name,
                'course_pattern':getenroll.course_pattern,
                'current_semester':getenroll.current_semyear    
            }

        else:
            print("no")

    params = {
        'student':obj,
        'getstudent':getstudent
        
    }
    return render(request,"profile1.html",params)

@login_required(login_url='/login/')
def StudentStudyMaterial(request):

    if request.user.is_student:
        
        return render(request,"study_material1.html")

@login_required(login_url='/login/')
def StudentVideoMaterial(request):
    if request.user.is_student:
        return render(request,"study_video_material1.html")



@login_required(login_url='/login/') 
def StudentDashboard(request):
    registered_student = ""
    if request.user.is_student:

        try:
            student = Student.objects.get(user = request.user)
            registered_student = "yes"
        except Student.DoesNotExist:
            registered_student = "no"
        if request.method == "POST":
            

            getpayment_reciept = request.POST.get('getpayment_reciept')
            if getpayment_reciept:
                print(getpayment_reciept)
                get_reciept = PaymentReciept.objects.get(id = getpayment_reciept)
                paymentrecieptserializer = PaymentRecieptSerializer(get_reciept,many=False)
                view_student = Student.objects.get(id=get_reciept.student.id)
                view_enroll = Enrolled.objects.get(student=view_student.id)
                view_course = Course.objects.get(id = view_enroll.course.id)
                view_stream = Stream.objects.get(id = view_enroll.stream.id)
                temp = {
                    "name":view_student.name,
                    "email":view_student.email,
                    "mobile":view_student.mobile,
                    "enrollment_id":view_student.enrollment_id,
                    "address":view_student.address,
                    "country":view_student.country.name,
                    "state":view_student.state.name,
                    "city":view_student.city.name,
                    "pincode":view_student.pincode,
                    "course":view_course.name,
                    "stream":view_stream.name
                }
                return JsonResponse({'view_reciept':paymentrecieptserializer.data,'personal':temp})
            
            button = request.POST.get('button')
            if button == "getsyllabus":
                try:
                    enrolled = Enrolled.objects.get(student = student.id)
                    course = Course.objects.get(id = enrolled.course)
                    stream = Stream.objects.get(id = enrolled.stream)
                    print(course.name)
                    try:
                        syllabus = Syllabus.objects.get(Q(course=course.id) & Q(stream=stream.id) & Q(semester=enrolled.current_semyear))
                        syllabusserializer = SyllabusSerializer(syllabus,many=False)
                        return JsonResponse({'data':syllabusserializer.data,'openmodal':'yes'})
                    except Syllabus.DoesNotExist:
                        return JsonResponse({'openmodal':'no'})
                except Enrolled.DoesNotExist:
                    print("Enrolled not present")
            elif button == "getpaymentinvoice":
                student = Student.objects.get(user=request.user)
                try:
                    enrolled = Enrolled.objects.get(student = student)
                    try:
                        getfeespaid = PaymentReciept.objects.filter(student = student)
                        
                        feeserializer = PaymentRecieptSerializer(getfeespaid,many=True)
                        return JsonResponse({'fees':feeserializer.data,'data':'yes'})
                    except PaymentReciept.DoesNotExist:
                        return JsonResponse({'data':'no'})
                except Enrolled.DoesNotExist:
                    print("Enrolled not present")
            elif button == "payment_gateway":
                try:
                    getstudent = Student.objects.get(id = student.id)
                    studentserializer = StudentSerializer(getstudent,many=False)
                    try:
                        latestpaymenreciept = PaymentReciept.objects.latest('id')
                        latest_transactionID = latestpaymenreciept.transactionID
                        tranx = latest_transactionID.replace("TXT445FE",'')
                        transactionID =  str("TXT445FE") + str(int(tranx) + 131)
                        print(transactionID)
                        insert_transactionID = TempTransaction(transactionID=transactionID,student=student)
                        insert_transactionID.save()
                    except PaymentReciept.DoesNotExist:
                        print("payment reciept not present")
                    getenroll = Enrolled.objects.get(student = getstudent)
                    

                    try:
                        getpaymentreciept = PaymentReciept.objects.filter(Q(student = getstudent) & Q(semyear = getenroll.current_semyear))
                        feespendinglist = []
                        for i in getpaymentreciept:
                            print(i.paidamount , i.pendingamount)
                            feespendinglist.append(i.pendingamount)
                        print("feespendinglist =",feespendinglist)
                        if '0' in feespendinglist:
                            return JsonResponse({'pending':'no'})
                        else:
                            print("no")
                            getlatestpaymentgateway = TempTransaction.objects.latest('id')
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
                                'address2': 'test', 'city': getstudent.city.name,  'state': getstudent.state.name, 'country': getstudent.country.name,
                                'zipcode': getstudent.pincode, 'udf1': '', 'udf2': '', 'udf3': '', 'udf4': '', 'udf5': '',
                                'surl':surl,
                                'furl':furl
                            }
                            # Make sure the transaction ID is unique
                            txnid = transactionid
                            data.update({"txnid": txnid})
                            payu_data = payu.transaction(**data)
                            return JsonResponse({'pending':'yes','amount':i.pendingamount,'transactionData':payu_data,'student_data':studentserializer.data})
                        
                    except PaymentReciept.DoesNotExist:
                        print("payment reciept not found")




                    
                    
                    
                except Student.DoesNotExist:
                    pass
                
                
                
    else:
        print("no")
    params = {
        "student":registered_student
    }
    return render(request,"studentdashboard1.html",params)