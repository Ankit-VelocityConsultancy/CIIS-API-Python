from django.http.response import HttpResponse,JsonResponse
from django.shortcuts import render,HttpResponse,redirect   ,HttpResponseRedirect
from django.contrib.auth import authenticate,get_user_model,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q , F
from .models import *
from rest_framework.response import Response
from django.core.mail import send_mail as sm,EmailMessage
from csv import reader
from csv import DictReader
from .serializers import *
import json
from datetime import date,datetime,timedelta
from hashlib import sha512
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paywix.payu import Payu
from django.core.mail import EmailMessage
import hashlib
# import pandas as pd 
import math
# from pandas import ExcelWriter
# from pandas import ExcelFile 
import csv
import os
#pdf import
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
# from xhtml2pdf import pisa
# import xlwt
import logging,traceback
logger = logging.getLogger('django')
from .functions import *


@login_required(login_url='/login/')
def RegisteredStudent(request):
    
    params = {

    }
    return render(request,"super_admin/registered_students.html",params)

def RegisteredStudentApi(request):
    #allstudent = Student.objects.filter(Q(verified = True) & Q(archive = False)).order_by('-id')
    allstudent = Student.objects.filter( Q(archive = False)).order_by('-id') ## modified by Avani 18/07 - all students entered in system will be verified
    studentlist = []
    for i in allstudent:
        student_id = i.id
        print(student_id, 'student')
               ## added try and except so that if no record the code will not break ... Added by Avani 08/08
        try:
            enrolled = Enrolled.objects.get(student = student_id)
            print(enrolled)
            course = Course.objects.get(id = enrolled.course.id)
            stream = Stream.objects.get(id = enrolled.stream.id)
            university = University.objects.get(id = i.university.id)
        except Enrolled.DoesNotExist:
            enrolled = ''
            course = ''
            stream=''

       ## added try and except so that if no record the code will not break ... Added by Avani 18/07
        try:
            additionaldetails = AdditionalEnrollmentDetails.objects.get(student = student_id)
        except AdditionalEnrollmentDetails.DoesNotExist:
            additionaldetails = ''
        
        if additionaldetails == '':
            counselor_name = ''
            university_enrollment_id = ''
        else:
            counselor_name = additionaldetails.counselor_name
            university_enrollment_id = additionaldetails.university_enrollment_id
        ## end of add
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
        if i.is_quick_register == False: ## added by Avani 18/07 change request to add Source
            is_quick_register ='SR'
        else:
            is_quick_register = 'QR'
        ## added by Avani, handling of empty data 08/08
        if course != '':
            course_name = course.name
        else:
            course_name = ''
        if stream != '':
            stream_name = stream.name
        else:
            stream_name = ''  
        if enrolled != '':
            entry_mode = enrolled.entry_mode
            course_pattern = enrolled.course_pattern
            current_sem = enrolled.current_semyear
            session = enrolled.session 
        else:
            entry_mode = ''
            current_sem = ''
            session = ''
            course_pattern = ''
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
            "counselor_name":counselor_name,## modified by Avani 18/07
            "university_enrollment_id":university_enrollment_id, ## modified by Avani 18/07
            "gender":i.gender,
            "category":i.category,
            "enrollment_id":i.enrollment_id,
            "enrollment_date":datetime.strptime(str(i.enrollment_date), '%Y-%m-%d').strftime('%d-%m-%Y'),
            #"registration_id":i.registration_id,
            "course_name":course_name, ## modified by Avani, handling of empty data
            "stream_name":stream_name,## modified by Avani, handling of empty data
            "course_pattern":course_pattern,## modified by Avani, handling of empty data
            "current_semester":current_sem,## modified by Avani, handling of empty data
            "session":session,## modified by Avani, handling of empty data
            'entry_mode':entry_mode,## modified by Avani, handling of empty data
            'university':university.university_name,
            "is_quick_register":is_quick_register
        }
        studentlist.append(obj)
    
    return JsonResponse({'data':studentlist})

def registered_get_fees(request):
    if request.method == 'POST':
        get_fees = request.POST.get('get_fees')
        if get_fees:
            getstudent = Student.objects.get(enrollment_id = get_fees)
            getfeespaid = PaymentReciept.objects.filter(Q(student = getstudent.id) & (Q(payment_for="Course Fees") | Q(payment_for="Tution Fees") | Q(payment_for="Re-Registration Fees") | Q(payment_for="Examination Fees")))
            feeserializer = PaymentRecieptSerializer(getfeespaid,many=True)
            return JsonResponse({'fees':feeserializer.data,'student_id':getstudent.id})
            

def registered_view_fees(request):
    if request.method == "POST":
        getpayment_reciept = request.POST.get('getpayment_reciept')
        if getpayment_reciept:
            # print(getpayment_reciept)
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

def registered_show_common_fees(request):
    if request.method == "POST":
        show_common_fees = request.POST.get('show_common_fees')
        if show_common_fees:
            getstudent = Student.objects.get(id = show_common_fees)
            getfeespaid = PaymentReciept.objects.filter(Q(student = getstudent.id) & (Q(payment_for="Course Fees") | Q(payment_for="Tution Fees") | Q(payment_for="Re-Registration Fees") | Q(payment_for="Examination Fees")))
            feeserializer = PaymentRecieptSerializer(getfeespaid,many=True)
            return JsonResponse({'fees':feeserializer.data,'student_id':getstudent.id})
            

def registered_show_additional_fees(request):
    if request.method == "POST":
        show_additional_fees = request.POST.get('show_additional_fees')
        if show_additional_fees:
            getstudent = Student.objects.get(id = show_additional_fees)
            getfeespaid = PaymentReciept.objects.filter(Q(student = getstudent.id) & ~(Q(payment_for="Course Fees") | Q(payment_for="Tution Fees") | Q(payment_for="Re-Registration Fees") | Q(payment_for="Examination Fees")))
            feeserializer = PaymentRecieptSerializer(getfeespaid,many=True)
            return JsonResponse({'fees':feeserializer.data,'student_id':getstudent.id})


def registered_edit_payment_reciept(request):
    if request.method == "POST":
        editpayment_reciept = request.POST.get('editpayment_reciept')
        if editpayment_reciept:
            try:
                getreciept = PaymentReciept.objects.get(id = editpayment_reciept)
                paymentrecieptserializer = PaymentRecieptSerializer(getreciept,many=False)
                
                return JsonResponse({'edit':'yes','data':paymentrecieptserializer.data})
            except PaymentReciept.DoesNotExist:
                return JsonResponse({'edit':'no'})

def register_edit_payment_reciept_save(request):
    if request.method == "POST":
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



def registered_get_common_fees_details(request):
    if request.method == "POST":
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



def registered_save_common_fees_details(request):
    if request.method == 'POST':
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
                                student = getstudent,
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
                                    student = getstudent,
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
                                    student = getstudent,
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
                                    student = getstudent,
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
                                    student = getstudent,
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
                        
                        add_payment_reciept = PaymentReciept(student = getstudent,payment_for="Course Fees",payment_categories = commonfees_feesfor,payment_type=commonfees_feestype,fee_reciept_type="",transaction_date= commonfees_transactiondate,cheque_no=commonfees_chequeno,bank_name=commonfees_bankname,paidamount=commonfees_amount,pendingamount="0",transactionID = transactionID,paymentmode=commonfees_paymentmode,remarks=commonfees_remarks,session="",semyear=commonfees_semyear,status=payment_status)
                        # add_payment_reciept.save()
                        getfeespaid = PaymentReciept.objects.filter(student = getstudent.id)
                        
                        feeserializer = PaymentRecieptSerializer(getfeespaid,many=True)
                        return JsonResponse({'success':'yes','fees':feeserializer.data,'student_id':getstudent.id})
                        
                    
                    except Student.DoesNotExist:
                        print("no student found")


def registered_save_extra_fees(request):
    if request.method == 'POST':
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
            print("Extra Fees",extrafees_student_id,extrafees_feesfor,extrafees_amount,extrafees_feestype,extrafees_semyear,extrafees_transactiondate,extrafees_paymentmode,extrafees_chequeno,extrafees_bankname,extrafees_remarks)
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
                
                add_payment_reciept = PaymentReciept(student = getstudent,payment_for=extrafees_feesfor,payment_type=extrafees_feestype,fee_reciept_type="",transaction_date= extrafees_transactiondate,cheque_no=extrafees_chequeno,bank_name=extrafees_bankname,paidamount=extrafees_amount,pendingamount="0",transactionID = transactionID,paymentmode=extrafees_paymentmode,remarks=extrafees_remarks,session="",semyear=extrafees_semyear)
                add_payment_reciept.save()

                getfeespaid = PaymentReciept.objects.filter(student = getstudent)
                
                feeserializer = PaymentRecieptSerializer(getfeespaid,many=True)
                return JsonResponse({'success':'yes','fees':feeserializer.data,'student_id':getstudent.id})
                
                
            except Student.DoesNotExist:
                print("no student found")


def registered_get_idcard(request):
    if request.method == 'POST':
        idcard = request.POST.get('idcard')
        if idcard:
            getstudent = Student.objects.get(enrollment_id = idcard)
            university = University.objects.get(id = getstudent.university.id)
            obj = {
                "name":getstudent.name,
                "dateofbirth":getstudent.dateofbirth,
                "email":getstudent.email,
                "mobile":getstudent.mobile,
                "address":getstudent.address,
                "city":getstudent.city.name,
                "state":getstudent.state.name,
                "pincode":getstudent.pincode,
                "country":getstudent.country.name,
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


def registered_request_fees(request):
    if request.method == "POST":
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

def registered_fetch_message_request_fees(request):
    if request.method == "POST":
        amount = request.POST.get('request_amount')
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
       

def registered_enroll_to_next_semyear(request):
    if request.method == 'POST':
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
                
                course = Course.objects.get(id = enroll.course.id)
                stream = Stream.objects.get(id = enroll.stream.id)
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

        return JsonResponse({'data':'data'})

def registered_save_enrollment_to_next_semyear(request):
    if request.method == 'POST':
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
        return JsonResponse({'data':'data'})

def registered_show_profile_pic(request):
    if request.method == "POST":
        show_profile_pic = request.POST.get('show_profile_pic')
        if show_profile_pic:
            getstudent = Student.objects.get(enrollment_id = show_profile_pic)
            
            if getstudent.image == "False":
                return JsonResponse({'image':'no'})
            else:
                student_serializer = StudentSerializer(getstudent,many=False)
                return JsonResponse({'image':student_serializer.data})


def registered_result_uploaded(request):
    if request.method == 'POST':
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
            addresultuploaded = ResultUploaded(student = Student.objects.get(id=addresultuploaded_studentid),
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


def registered_university_exam_fee(request):
    if request.method == 'POST':
        universityExamFees = request.POST.get('universityExamFees')
        if universityExamFees:
            try:
                getstudent = Student.objects.get(enrollment_id = universityExamFees)
                getuniversity_examination = UniversityExamination.objects.filter(Q(student = getstudent.id) & Q(type = "University_Exam"))
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
            addnew_universityexamination = UniversityExamination(student = Student.objects.get(id=adduniversity_studentid),
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

def registered_university_re_registration(request):
    if request.method == 'POST':
        universityReRegistration = request.POST.get('universityReRegistration')
        if universityReRegistration:
            try:
                getstudent = Student.objects.get(enrollment_id = universityReRegistration)
                getuniversity_examination = UniversityExamination.objects.filter(Q(student = getstudent.id) & Q(type = "University_Re_Registration"))
                university_examination_serializer = UniversityExaminationSerializer(getuniversity_examination,many=True)
                
                return JsonResponse({'student_id':getstudent.id,'data':university_examination_serializer.data})
            except Student.DoesNotExist:
                pass
        adduniversity_re_registration_studentid = request.POST.get('adduniversity_re_registration_studentid')
        adduniversity_re_registration_amount = request.POST.get('adduniversity_re_registration_amount')
        adduniversity_re_registration_date = request.POST.get('adduniversity_re_registration_date')
        adduniversity_re_registration_examination = request.POST.get('adduniversity_re_registration_examination')
        adduniversity_re_registration_semyear = request.POST.get('adduniversity_re_registration_semyear')
        adduniversity_re_registration_paymentmode = request.POST.get('adduniversity_re_registration_paymentmode')
        adduniversity_re_registration_remarks = request.POST.get('adduniversity_re_registration_remarks')
        adduniversity_re_registration_type = request.POST.get('adduniversity_re_registration_type')
        if adduniversity_re_registration_studentid and adduniversity_re_registration_amount and adduniversity_re_registration_date and adduniversity_re_registration_examination and adduniversity_re_registration_semyear and adduniversity_re_registration_paymentmode and adduniversity_re_registration_remarks and adduniversity_re_registration_type:
            addnew_universityexamination = UniversityExamination(student = Student.objects.get(id=adduniversity_re_registration_studentid),
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

def registered_show_personal_documents(request):
    if request.method == 'POST':
        show_personal_documents = request.POST.get('show_personal_documents')
        if show_personal_documents:
            # print(show_personal_documents)
            data = []
            show_personal_documents_files = PersonalDocuments.objects.filter(student__enrollment_id=show_personal_documents)
            for i in show_personal_documents_files:
                personal_document_image_files = PersonalDocumentsImages.objects.filter(document=i)
                personal_document_image_files_serializer = PersonalDocumentsImagesSerializer(personal_document_image_files,many=True)
                obj = {
                    "id":i.id,
                    "document":i.document,
                    "document_name":i.document_name,
                    "document_ID_no":i.document_ID_no,
                    "student":i.student.id,
                    "images":personal_document_image_files_serializer.data
                    
                }
                data.append(obj)
            print(data)
            # # print(show_personal_documents_files)
            # getresultserializer = PersonalDocumentsSerializer(show_personal_documents_files,many=True)
            return JsonResponse({'result':data})
        
        personal_student_enrollment_id = request.POST.get('personal_student_enrollment_id')
        if personal_student_enrollment_id:
            # print(request.POST)
            # print(request.FILES)
            personal_update_document = request.POST.get('personal_update_document')
            personal_update_DocumentName = request.POST.get('personal_update_DocumentName')
            personal_upload_DocumentID = request.POST.get('personal_upload_DocumentID')
            personal_upload_Documents = request.FILES.getlist('personal_uploaded_file')
            create_new_document = PersonalDocuments(
                document = personal_update_document,
                document_name = personal_update_DocumentName,
                document_ID_no = personal_upload_DocumentID,
                student = Student.objects.get(enrollment_id = personal_student_enrollment_id)
            )
            create_new_document.save()
            for i in personal_upload_Documents:
                create_personal_document_files = PersonalDocumentsImages(
                    document = create_new_document,
                    document_image = i
                )
                create_personal_document_files.save()
            # print(create_new_document)
            return JsonResponse({'status':'stis'})
            
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
                getdocument = StudentDocuments.objects.get(Q(student = Student.objects.get(id=upload_student_id)) & Q(document=upload_document))
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
                adddocument = StudentDocuments(student=Student.objects.get(id=upload_student_id),document=upload_document,document_name=upload_document_name,document_ID_no=upload_document_id,document_image_front=document_file_front,document_image_back=document_file_back)
                adddocument.save()
                getalldocuments = StudentDocuments.objects.filter(student=upload_student_id)
                studentdocumentserializer = StudentDocumentsSerializer(getalldocuments,many=True)
                return JsonResponse({'added':'yes','documents':studentdocumentserializer.data})
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

def registered_get_qualification_documents(request):
    if request.method == "POST":
        documents = request.POST.get('documents')
        if documents:
            print("got documents")
            try:       
                getstudent = Student.objects.get(enrollment_id = documents)
                try:
                    getqualification = Qualification.objects.get(student= getstudent)
                    getqualificationserializer = QualificationSerializer(getqualification,many=False)
                    return JsonResponse({'qualification':getqualificationserializer.data})
                except Qualification.DoesNotExist:
                    setqualification = Qualification(student=getstudent,secondary_year = '',sr_year = '',under_year='',post_year='',mphil_year='',others_year = '',secondary_board='',sr_board='',under_board='',post_board='',mphil_board='',others_board='',secondary_percentage='',sr_percentage='',under_percentage='',post_percentage='',mphil_percentage='',others_percentage='',secondary_document='',sr_document='',under_document='',post_document='',mphil_document='',others_document='')
                    setqualification.save()
                    getqualification = Qualification.objects.get(student= getstudent)
                    getqualificationserializer = QualificationSerializer(getqualification,many=False)
                    return JsonResponse({'qualification':getqualificationserializer.data})
                    
            except Student.DoesNotExist:
                pass
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
        else:
            return JsonResponse({'qualification':'none'})

def registered_get_remarks(request):
    if request.method == 'POST':
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


def registered_new_university_enrollment_number(request):
    if request.method == 'POST':
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
        new_university_enrollment_student_id = request.POST.get('new_university_enrollment_student_id')
        new_university_enrollment_course = request.POST.get('new_university_enrollment_course')
        new_university_enrollment_id = request.POST.get('new_university_enrollment_id')
        new_university_enrollment_type = request.POST.get('new_university_enrollment_type')
        if new_university_enrollment_student_id and new_university_enrollment_course and new_university_enrollment_id and new_university_enrollment_type:
            print(new_university_enrollment_student_id , new_university_enrollment_course , new_university_enrollment_id , new_university_enrollment_type)
            getcourse = Course.objects.get(id = new_university_enrollment_course)
            print(getcourse.name)
            add_new_university_enrollment_id = UniversityEnrollment(student = Student.objects.get(id=new_university_enrollment_student_id),
                type = new_university_enrollment_type,
                course_id = new_university_enrollment_course,
                course_name = getcourse.name,
                enrollment_id = new_university_enrollment_id)
            add_new_university_enrollment_id.save()
            get_new_university_enrollment_id = UniversityEnrollment.objects.filter(Q(student = new_university_enrollment_student_id) & Q(type=new_university_enrollment_type))
            get_new_university_enrollment_id_serializer = UniversityEnrollmentSerializer(get_new_university_enrollment_id,many=True)
            return JsonResponse({'data':get_new_university_enrollment_id_serializer.data})


def registered_old_university_enrollment_number(request):
    if request.method == 'POST':
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
            
        old_university_enrollment_student_id = request.POST.get('old_university_enrollment_student_id')
        old_university_enrollment_course = request.POST.get('old_university_enrollment_course')
        old_university_enrollment_id = request.POST.get('old_university_enrollment_id')
        old_university_enrollment_type = request.POST.get('old_university_enrollment_type')
        if old_university_enrollment_student_id and old_university_enrollment_course and old_university_enrollment_id and old_university_enrollment_type:
            # print(old_university_enrollment_student_id , old_university_enrollment_course , old_university_enrollment_id , old_university_enrollment_type)
            getcourse = Course.objects.get(id = old_university_enrollment_course)
            # print(getcourse.name)
            add_old_university_enrollment_id = UniversityEnrollment(student = Student.objects.get(id=old_university_enrollment_student_id),
                type = old_university_enrollment_type,
                course_id = old_university_enrollment_course,
                course_name = getcourse.name,
                enrollment_id = old_university_enrollment_id)
            add_old_university_enrollment_id.save()
            get_old_university_enrollment_id = UniversityEnrollment.objects.filter(Q(student = old_university_enrollment_student_id) & Q(type=old_university_enrollment_type))
            get_old_university_enrollment_id_serializer = UniversityEnrollmentSerializer(get_old_university_enrollment_id,many=True)
            return JsonResponse({'data':get_old_university_enrollment_id_serializer.data})

def registered_courier_details(request):
    if request.method == 'POST':
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
            addcourier = Courier(student=Student.objects.get(id=courier_student_id), 
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

def registered_update_payment_status(request):
    if request.method == 'POST':
        update_payment = request.POST.get('update_payment')
        if update_payment:
            getstudent = Student.objects.get(enrollment_id = update_payment)
            getpaymentreciepts = PaymentReciept.objects.filter(Q(student = getstudent.id) & Q(paymentmode = "Cheque"))
            paymentSerializer = PaymentRecieptSerializer(getpaymentreciepts,many=True)
            return JsonResponse({'data':paymentSerializer.data})
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


def registered_cancel_student(request):
    if request.method == 'POST':
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


def registered_payment_gateway(request):
    if request.method == 'POST':
        payment_gateway = request.POST.get('payment_gateway')
        if payment_gateway:
            try:
                getstudent = Student.objects.get(enrollment_id = payment_gateway)
                studentserializer = StudentSerializer(getstudent,many=False)
                try:
                    paymentgatewaylatest = TestPaymentGateway.objects.latest('id')
                    trans_id = int(paymentgatewaylatest.transactionID) + 85245
                    addnewpaymentgatewaylatest = TestPaymentGateway(student = getstudent , transactionID = trans_id)
                    addnewpaymentgatewaylatest.save()
                except TestPaymentGateway.DoesNotExist:
                    paymentgatewaylatest = TestPaymentGateway(student = getstudent, transactionID="44343521")
                    paymentgatewaylatest.save()
                getenroll = Enrolled.objects.get(student = getstudent)

                try:
                    getpaymentreciept = PaymentReciept.objects.filter(Q(student = getstudent) & Q(payment_for = "Course Fees") & Q(semyear = getenroll.current_semyear))
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
                                'address2': 'test', 'city': getstudent.city.name,  'state': getstudent.state.name, 'country': getstudent.country.name,
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























































































































































































































































































































