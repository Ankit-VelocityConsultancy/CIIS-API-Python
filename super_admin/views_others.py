from itertools import chain
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
from django.contrib.auth.hashers import make_password
@login_required(login_url='/login/')
def addothersstudent(request):
   
    params = {
        'university': OtherUniversity.objects.all(),
        'course': OtherCourse.objects.all(),
        'stream': OtherStream.objects.all(),
        'substream': OtherSubStream.objects.all(),
        "countries":Countries.objects.all(),
        "paymentmodes":PaymentModes.objects.filter(status=True), 
        "feereceiptoptions":FeeReceiptOptions.objects.filter(status=True),
        "banknames":BankNames.objects.filter(status=True),
        "sessionnames":SessionNames.objects.filter(status=True),
    }
    return render(request, 'unplannedregistrations/addstudent.html', params)

def saveothersstudent(request):
    if request.method == "POST":
        print("inside saveothersstudent")
        univid = request.POST.get('university')
        print("univid: ", univid)
        if univid == 'Others':
            university = request.POST.get('otheruniversity')
            print("checking if univ is already present")
            univid = OtherUniversity.objects.filter(university_name=university).values_list('id', flat=True).first()
            print("univid is", univid)
            if univid == None:
                print("trying to add new univ")
                newuniv = OtherUniversity(
                    university_name= university,
                )
                newuniv.save()
                univid = OtherUniversity.objects.filter(university_name=university).values_list('id', flat=True).first()
                print(univid)
        
        student_image = request.FILES.get('student_image')
        name = request.POST.get('firstname')
        dob = request.POST.get('dob')
        fathername = request.POST.get('fathername')
        mothername = request.POST.get('mothername')
        email = request.POST.get('email')
        alternateemail = request.POST.get('alt_email')
        mobile = request.POST.get('mobile')
        alternatemobile = request.POST.get('alternatemobile1')
        gender = request.POST.get('gender')
        category = request.POST.get('category')
        address = request.POST.get('address')
        alternateaddress = request.POST.get('alternate_address')
        nationality = request.POST.get('nationality')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        counselor_name = request.POST.get('counselor_name')
        reference_name = request.POST.get('reference_name')
        university_enrollment_number = request.POST.get('university_enroll_number')
        student_remarks = request.POST.get('student_remarks')
        

        courseid = request.POST.get('course')
        if courseid == 'Others':
            course = request.POST.get('othercourse')
            courseid = OtherCourse.objects.filter(name=course).values_list('id', flat=True).first()
            if courseid == None:
                newcourse = OtherCourse(
                    name= course,
                )
                newcourse.save()
                courseid = OtherCourse.objects.filter(name=course).values_list('id', flat=True).first()
        print("course id is ", courseid)

        streamid = request.POST.get('Stream')
        if streamid == 'Others':
            stream = request.POST.get('otherstream')
            streamid = OtherStream.objects.filter(name=stream).values_list('id', flat=True).first()
            if streamid == None:
                newstream = OtherStream(
                    name= stream,
                )
                newstream.save()
                streamid = OtherStream.objects.filter(name=stream).values_list('id', flat=True).first()
        print("stream id is ", streamid)
        substreamid = request.POST.get('Substream')
        if substreamid == 'Others':
            print("in others")
            substream = request.POST.get('othersubstream')
            print("substream is ", substream)
            substreamid = OtherSubStream.objects.filter(name=substream).values_list('id', flat=True).first()
            if substreamid == None:
                print("no substream found")
                newsubstream = OtherSubStream(
                    name= substream,
                )
                newsubstream.save()
                substreamid = OtherSubStream.objects.filter(name=substream).values_list('id', flat=True).first()
        studypattern = request.POST.get('studypattern')
        semyear = request.POST.get('semyear')
        session = request.POST.get('session')
        entry_mode = request.POST.get('entry_mode')
        course_duration = request.POST.get('course_duration')
        remark = request.POST.get('courseremark')
        # # discount = request.POST.get('discount')
        
        # # Documents
        totaldocuments = request.POST.get('no_of_documents')
        print("totaldocuments :",totaldocuments)
        # # Qualifications
        secondary_year = request.POST.get('secondary_year')
        secondary_board = request.POST.get('secondary_board')
        secondary_percentage = request.POST.get('secondary_percentage')
        secondary_document = request.FILES.get('secondary_document')
        
        sr_year = request.POST.get('sr_year')
        sr_board = request.POST.get('sr_board')
        sr_percentage = request.POST.get('sr_percentage')
        sr_document = request.FILES.get('sr_document')
        
        under_year = request.POST.get('under_year')
        under_board = request.POST.get('under_board')
        under_percentage = request.POST.get('under_percentage')
        under_document = request.FILES.get('under_document')
        
        post_year = request.POST.get('post_year')
        post_board = request.POST.get('post_board')
        post_percentage = request.POST.get('post_percentage')
        post_document = request.FILES.get('post_document')
        
        mphil_year = request.POST.get('mphil_year')
        mphil_board = request.POST.get('mphil_board')
        mphil_percentage = request.POST.get('mphil_percentage')
        mphil_document = request.FILES.get('mphil_document')
        
        
        print(request.POST.get('qual_other_counter'), "cooooo")
        others_counter = request.POST.get('qual_other_counter')
        
        files_data = []
        for i in range(1,int(others_counter)+1):
            doctype = request.POST.get(f'other_{i}')
            year = request.POST.get(f'other_year_{i}')
            board = request.POST.get(f'other_board_{i}')
            docfile= request.FILES.get(f'other_document_{i}')
            file_data = {
                'doctype': doctype,
                'year': year,
                'board': board,
                'file_path': None
            }

            if docfile:
                # Save the file and get its path
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'University_Documents')
                file_path = os.path.join(upload_dir, docfile.name)
                save_path = f'University_Documents/{docfile.name}'
                with open(file_path, 'wb+') as destination:
                    for chunk in docfile.chunks():
                        destination.write(chunk)
                file_data['file_path'] = save_path

            files_data.append(file_data)
            #files_data[f'other_{i}'] = file_data
            print("files_data", files_data)

            
            

        fee_reciept_type = request.POST.get('fees_reciept')
        total_fees = request.POST.get('total_fees')
        fees = request.POST.get('fees')
        transaction_date = request.POST.get('date_of_transaction')
        payment_mode = request.POST.get('payment_mode')
        cheque_no = request.POST.get('cheque_no')
        bank_name = request.POST.get('bank_name')
        other_bank = request.POST.get('other_bank')
        remarks = request.POST.get('remarks')
        
        print("the remarks for the banks", remarks)
        
        # commented
        print("reached till here")

        try:
            print("getting latest id")
            random = OtherStudent.objects.latest('id')
            enroll = int(random.enrollment_id)+ 1
            print("enroll", enroll)
            
        except OtherStudent.DoesNotExist:
            print('no enrollment id found')
            enroll = 25000
          
        
        
        create_student = OtherStudent(
            name=name,
            father_name=fathername,
            mother_name=mothername,
            dateofbirth=dob,
            mobile=mobile,
            alternate_mobile1=alternatemobile,
            email=email,
            alternateemail=alternateemail,
            gender=gender,
            category=category,
            address=address,
            alternateaddress=alternateaddress,
            nationality=nationality,
            country=Countries.objects.get(id=country),
            state=States.objects.get(id=state),
            city=Cities.objects.get(id=city),
            pincode=pincode,
            enrollment_id=enroll,
            registration_id = enroll,
            image=student_image,
            created_by=request.user.id,
            student_remarks=student_remarks,
            user_id= request.user.id, ## added by Avani for showing who enrolled the student
            counselor_name=counselor_name,
            reference_name=reference_name,
            new_university_enrollment_id=university_enrollment_number,
            is_enrolled = True,
            )
        create_student.save()
        print("tried to add student")
        student = OtherStudent.objects.get(enrollment_id = enroll)
        
        create_user = User(
                        email = student.email,
                        is_student = True,
                        password = make_password(student.email)
                    )
        create_user.save()
        print("student saved successfully :",create_user.id)
        student.user = User.objects.get(id=create_user.id)
        student.save()

       
        totalsem = ""
        if studypattern == "Semester":
                totalsem = course_duration * 2
        elif studypattern == "Annual":
                totalsem = course_duration
        try:      
            print("courseid", courseid)
            print('streamid', streamid)
            print('univid', univid)
            if univid == '':
                university = None
            else:
                university = OtherUniversity.objects.get(id=univid)
            if courseid == '':
                course = None
            else:
                course = OtherCourse.objects.get(id=courseid)
            if streamid == '':
                stream = None
            else:
                stream = OtherStream.objects.get(id=streamid)   
            if substreamid == '':
                substream = None
            else:
                substream = OtherSubStream.objects.get(id=substreamid)  
            print("current sem", semyear)
            
            add_enrollmentdetails = OtherEnrolled(
                student=student,
                university = university,
                course=course,
                stream=stream,
                substream = substream,
                course_pattern=studypattern,
                session=session,
                entry_mode=entry_mode,
                total_semyear=totalsem,
                current_semyear=semyear,
                remarks = remark,
                )

            add_enrollmentdetails.save()   
        except OtherEnrolled.DoesNotExist:
            print("no entryy") 
        print("enrolled student")
        print(bank_name , other_bank)
        
            
        for i in range(1,int(totaldocuments)+1):
            
            document = request.POST.get(f'document{i}')
            DocumentName = request.POST.get(f'DocumentName{i}')
            ## added by Avani - if Document type is Other, store the name from the field other{i}
            if document == 'Other':
                document = request.POST.get(f'other{i}')
            DocumentID = request.POST.get(f'DocumentID{i}')
            DocumentFront = request.FILES.get(f'DocumentFront{i}', False)
            DocumentBack = request.FILES.get(f'DocumentBack{i}', False)
            # print(document,DocumentName,DocumentID,DocumentFront,DocumentBack)
            add_student_document = OtherStudentDocuments(document=document,document_name=DocumentName,document_ID_no=DocumentID,document_image_front= DocumentFront,document_image_back = DocumentBack,student=student)
            add_student_document.save()

        if secondary_year or secondary_board or secondary_percentage or secondary_document or sr_year or sr_board or sr_percentage or sr_document or under_year or under_board or under_percentage or under_document or post_year or post_board or post_percentage or post_document or mphil_year or mphil_board or mphil_percentage or mphil_document or files_data:
            setqualification = OtherQualification(
                others=files_data,
                student=student,
                secondary_year = secondary_year,
                sr_year = sr_year,
                under_year=under_year,
                post_year=post_year,
                mphil_year=mphil_year,
                secondary_board=secondary_board,
                sr_board=sr_board,
                under_board=under_board,
                post_board=post_board,
                mphil_board=mphil_board,
                secondary_percentage=secondary_percentage,
                sr_percentage=sr_percentage,
                under_percentage=under_percentage,
                post_percentage=post_percentage,
                mphil_percentage=mphil_percentage,
                secondary_document=secondary_document,
                sr_document=sr_document,
                under_document=under_document,
                post_document=post_document,
                mphil_document=mphil_document,
                )
            setqualification.save()
            print("qualification saved")
        

        try:
            getlatestreciept = OtherPaymentReciept.objects.latest('id')
            tid = getlatestreciept.transactionID
            tranx = tid.replace("OTH00AA",'')
            transactionID =  str("OTH00AA") + str(int(tranx) + 1)
        except OtherPaymentReciept.DoesNotExist:
            transactionID = "OTH00AA001"
        if payment_mode == "Cheque":
            payment_status = "Not Realised"
        else:
            payment_status = "Realised"
            
       
          
        reciept_type = fee_reciept_type
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
      
        if payment_mode == "Cheque":
            paidamount = 0
            uncleared_amount = fees
        else:
            paidamount = fees
            uncleared_amount = 0

        add_payment_reciept = OtherPaymentReciept(
                            student = student,
                            payment_for="Course Fees",
                            payment_categories = "New",
                            payment_type=paymenttype,
                            fee_reciept_type=reciept_type,
                            transaction_date= transaction_date,
                            cheque_no=cheque_no,
                            bank_name=bank_name,
                            semyearfees=total_fees,
                            paidamount=paidamount,
                            pendingamount=pending_amount,
                            advanceamount = advance_amount,
                            transactionID = transactionID,
                            paymentmode=payment_mode,
                            remarks=remarks,
                            session=session,
                            semyear=semyear,
                            uncleared_amount=uncleared_amount,
                            status=payment_status)
        add_payment_reciept.save()

            
        # commented



        # print(total_fees,fees , fee_reciept_type  , transaction_date , payment_mode , cheque_no , bank_name ,other_bank, remarks)
    ## modified by Avani on 23/07 - redirect to registerd students page. Client does not want pending verification.
    #return redirect('pending_verification')
    # return redirect('viewregister')
    return render(request, 'unplannedregistrations/addstudent.html')

def getcourse(request):
    university_id = request.GET.get('university_id')
    try:
        print("getting coursehghghh", university_id)
        getcourse = OtherCourse.objects.all()
        print("coursess", getcourse)
        courseserializer = CourseSerializer(getcourse,many=True)
        return JsonResponse({'course':courseserializer.data,})
    except Course.DoesNotExist:
        pass

@login_required(login_url='/login/')
def viewregisterother (request):
    params= {
                "students":OtherStudent.objects.filter(~Q(is_cancelled = True) ).order_by('-id'),
                "title" : 'List of Students'
                
            }
    return render(request,"unplannedregistrations/viewstudents.html", params)

@login_required(login_url='/login/')
def EditOtherStudent(request,enroll_id):

    found_student = ""
    student = []
    personaldoccounter = ''
    
    if request.user.is_superuser or request.user.is_data_entry:
        try:
            getstudent = OtherStudent.objects.get(enrollment_id = enroll_id)
            print("student found", getstudent.id)
            found_student = "yes"
            try:
                getenroll = OtherEnrolled.objects.get(student=getstudent.id)
                print(getenroll)
                if getenroll.course != None:
                    course = OtherCourse.objects.get(id = getenroll.course.id)
                else:
                    course = ''
                if getenroll.stream != None:
                    stream = OtherStream.objects.get(id = getenroll.stream.id)
                else:
                    stream = ''
                if getenroll.substream != None:
                    substream = OtherSubStream.objects.get(id = getenroll.substream.id)
                else:
                    substream = ''
                if getenroll.university != None:
                    university = OtherUniversity.objects.get(id = getenroll.university.id)
                else:
                    university = ''

                getdocuments = OtherStudentDocuments.objects.filter(student=getstudent.id)
                # print(getdocuments)
                try:
                    getqualification = OtherQualification.objects.get(student=getstudent.id)
                    # print(getqualification)
                except OtherQualification.DoesNotExist:
                    getqualification = "none"
                # try:
                #     getuniversity = OtherUniversity.objects.get(id=getstudent.university.id)
                #     # print(getuniversity)
                # except OtherUniversity.DoesNotExist:
                #     getuniversity = "none"

                
                ## Fetch payment details to show in fronten added by Avani 15/07
                try:
                    paymentdetails = OtherPaymentReciept.objects.filter(student=getstudent.id).first()
                except OtherPaymentReciept.DoesNotExist:
                    paymentdetails = "none"
                try:
                    personaldocuments = OtherStudentDocuments.objects.filter(student_id=getstudent.id)
                    print("personaldoc", personaldocuments)
                except OtherStudentDocuments.DoesNotExist:
                    personaldocuments = 'none'
                personaldoccounter = personaldocuments.count()
                print('personaldoccounter', personaldoccounter)
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
                    "qualification":getqualification,
                    'counselor_name':getstudent.counselor_name,
                    'university_enrollment_id':getstudent.new_university_enrollment_id,
                    'reference_name':getstudent.reference_name,
                    'registration_number':getstudent.registration_number,
                    "course":course,
                    "stream":stream,
                    "substream":substream,
                    "university":university,
                    # "substream":substream,##added by Avani 14/08
                    "course_pattern":getenroll.course_pattern,
                    "session":getenroll.session,
                    "entry_mode":getenroll.entry_mode,
                    "current_semyear":getenroll.current_semyear,
                    "remarks":getenroll.remarks,
                    # "university":getuniversity,
                    "student_remarks":getstudent.student_remarks,
                    "documents":getdocuments, # show docoument related details in frontend added by Avani 15/07
                    "personaldocs":personaldocuments,
                    
                    
                }
                student.append(obj)
            except OtherEnrolled.DoesNotExist:
                print("dfdfdfd")
                getenroll = "none"

        except OtherStudent.DoesNotExist:
            # print("student not found")
            found_student = "no"
     

    params = {
            "course":OtherCourse.objects.all(),
            "stream":OtherStream.objects.all(),
            "university":OtherUniversity.objects.all(),
            "substream":OtherSubStream.objects.all(),
            "found_student":found_student,
            "student":student,
            "country":Countries.objects.all(),
            'personaldoccounter':personaldoccounter,
            "mobile":getstudent.mobile,
            "alternate_mobile1":getstudent.alternate_mobile1,
            "email":getstudent.email,
            "alternateemail":getstudent.alternateemail,
            "paymentmodes":PaymentModes.objects.filter(status=True), ## added by Avani on 09/08 -pick data from mastertables
            "feereceiptoptions":FeeReceiptOptions.objects.filter(status=True),## added by Avani on 09/08 -pick data from mastertables
            "banknames":BankNames.objects.filter(status=True),## added by Avani on 09/08 -pick data from mastertables
            "session":SessionNames.objects.filter(status=True),## added by Avani on 12/08 -pick data from mastertables
            "paymentdetails":paymentdetails,

    }
    return render(request,"unplannedregistrations/editstudent.html",params)

@login_required(login_url='/login/')
def saveEditOtherStudent(request):
    print("inside this function other editstudent")
    if request.user.is_superuser or request.user.is_data_entry:
        
        if request.method == "POST":
            print("in here")
            university = request.POST.get('university')
            enroll_id = request.POST.get('student_enrollment_id')
            print("enroll_id: ", enroll_id)
            student_image = request.FILES.get('student_image')
            print("student_image:",student_image)
            name = request.POST.get('name')
            dob = request.POST.get('dateofbirth')
            print("dateofbirth", dob)
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
            if country:
                change_country = Countries.objects.get(id=country)
            else:
                change_country = Countries.objects.get(id=101)
            if state:
                change_state = States.objects.get(id=state)
            else:
                change_state = States.objects.get(id=22)
            if city:
                change_city = Cities.objects.get(id=city)
            else:
                change_city = Cities.objects.get(id=2707)
            try:
                getstudent = OtherStudent.objects.get(enrollment_id = enroll_id)
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
                getstudent.country = change_country
                getstudent.state = change_state
                getstudent.city = change_city
                getstudent.pincode = pincode
                getstudent.counselor_name=counselor_name
                getstudent.reference_name=reference_name
                getstudent.university_enrollment_id=university_enrollment_number
                if student_image != None:
                    print("inside if student image")
                    getstudent.image = student_image
                
                getstudent.student_remarks = student_remarks
                getstudent.save()
                    
            except OtherStudent.DoesNotExist:
                print("No student found")

            #Enrollment details
            studypattern = request.POST.get('studypattern')
            semyear = request.POST.get('semyear')
            session = request.POST.get('session')
            entry_mode = request.POST.get('entry_mode')
            course_duration = request.POST.get('course_duration')
            courseremarks = request.POST.get('courseremarks')
            univid = request.POST.get('university')
            if univid == 'Others':
                university = request.POST.get('otheruniversity')
                univid = addOtherUniversity(university)
              
            print(univid)
            courseid = request.POST.get('course')
            if courseid == 'Others':
                othercourse = request.POST.get('othercourse')
                courseid = addOtherCourse(othercourse)
              
            print(courseid)
            streamid = request.POST.get('stream')
            if streamid == 'Others':
                otherstream = request.POST.get('otherstream')
                streamid = addOtherStream(otherstream)
              
            print(streamid)
            substreamid = request.POST.get('substream')
            if substreamid == 'Others':
                print("got others")
                othersubstream = request.POST.get('othersubstream')
                substreamid = addOtherSubStream(othersubstream)
            print(course_duration, 'course duration')
            totalsem = ''
            if studypattern == "Semester":
                if course_duration != None:
                    totalsem = course_duration * 2
            elif studypattern == "Annual":
                totalsem = course_duration
                  
            print("courseid", courseid)
            print('streamid', streamid)
            print('univid', univid)
            if univid == '':
                    university = None
            else:
                    university = OtherUniversity.objects.get(id=univid)
            if courseid == '':
                    course = None
            else:
                    course = OtherCourse.objects.get(id=courseid)
            if streamid == '':
                    stream = None
            else:
                    stream = OtherStream.objects.get(id=streamid) 
            if substreamid == '':
                    substream = None
            else:
                    substream = OtherSubStream.objects.get(id=substreamid)  
            try:
                edit_enrollmentdetails = OtherEnrolled.objects.get(student = getstudent.id) 
                print(edit_enrollmentdetails)
                edit_enrollmentdetails.university = university
                edit_enrollmentdetails.course = course
                edit_enrollmentdetails.stream = stream
                edit_enrollmentdetails.substream = substream 
                if studypattern != '':
                    edit_enrollmentdetails.course_pattern = studypattern
                if session != '':
                    edit_enrollmentdetails.session = session
                if entry_mode != '':
                    edit_enrollmentdetails.entry_mode = entry_mode
                if totalsem != '':
                    edit_enrollmentdetails.total_semyear = totalsem
                if semyear != '':
                    edit_enrollmentdetails.current_semyear = semyear
                if courseremarks != '':
                    edit_enrollmentdetails.remarks = courseremarks
                edit_enrollmentdetails.save()   
            except OtherEnrolled.DoesNotExist:
                print("no entryy") 
        
            #Personal Documents
            getstudent = OtherStudent.objects.get(enrollment_id = enroll_id)
            id = getstudent.id
            no_of_docs = request.POST.get('personaldocs_counter')
            print("no of docus" , no_of_docs)
            for i in range(1,int(no_of_docs)+1):
                docid= request.POST.get(f'docid{i}')
                print("docid" , docid)
                document = request.POST.get(f'document{i}')
                DocumentName = request.POST.get(f'DocumentName{i}')
                ## added by Avani - if Document type is Other, store the name from the field other{i}
                if document == 'Other':
                    document = request.POST.get(f'other{i}')
                DocumentID = request.POST.get(f'DocumentID{i}')
                DocumentFront = request.FILES.get(f'DocumentFront{i}')
                DocumentBack = request.FILES.get(f'DocumentBack{i}')
                print("DocumentFront",  request.FILES.get(f'DocumentFront{i}'))
                # print(document,DocumentName,DocumentID,DocumentFront,DocumentBack)
                if docid != None:
                    getrecord = OtherStudentDocuments.objects.get(id = docid)
                    getrecord.document = document
                    getrecord.document_name = DocumentName
                    getrecord.document_ID_no = DocumentID
                    if DocumentFront != None:
                            getrecord.document_image_front = DocumentFront
                    if DocumentBack != None:
                            getrecord.document_image_back = DocumentBack
                    getrecord.save()
                else:
                    add_student_document = OtherStudentDocuments(document=document,document_name=DocumentName,document_ID_no=DocumentID,document_image_front= DocumentFront,document_image_back = DocumentBack,student_id=id)
                    add_student_document.save()

           

            # Qualifications
            secondary_year = request.POST.get('secondary_year')
            secondary_board = request.POST.get('secondary_board')
            secondary_percentage = request.POST.get('secondary_percentage')
            secondary_document = request.FILES.get('secondary_document')## modified by Avani, removed the False part 15/07
            
            sr_year = request.POST.get('sr_year')
            sr_board = request.POST.get('sr_board')
            sr_percentage = request.POST.get('sr_percentage')
            sr_document = request.FILES.get('sr_document')## modified by Avani, removed the False part 15/07
            
            under_year = request.POST.get('under_year')
            under_board = request.POST.get('under_board')
            under_percentage = request.POST.get('under_percentage')
            under_document = request.FILES.get('under_document') ## modified by Avani, removed the False part 15/07
            
            post_year = request.POST.get('post_year')
            post_board = request.POST.get('post_board')
            post_percentage = request.POST.get('post_percentage')
            post_document = request.FILES.get('post_document')## modified by Avani, removed the False part 15/07
            
            mphil_year = request.POST.get('mphil_year')
            print("mphil_year", mphil_year)
            mphil_board = request.POST.get('mphil_board')
            mphil_percentage = request.POST.get('mphil_percentage')
            mphil_document = request.FILES.get('mphil_document')## modified by Avani, removed the False part 15/07
            
            others_counter = request.POST.get('qual_other_counter')
            print(others_counter, "others_counter")
            files_data = []
            for i in range(1,int(others_counter)+1):
                print("inside for")
                doctype = request.POST.get(f'other_{i}')
                print("doctype", doctype)
                year = request.POST.get(f'other_year_{i}')
                board = request.POST.get(f'other_board_{i}')
                percentage = request.POST.get(f'other_percentage_{i}')
                docfile= request.FILES.get(f'other_document-{i}')
                uploadeddoc_other = request.POST.get(f'olddoc_{i}')
               
                print("uploaded-doc-other_", uploadeddoc_other)
                print("docfile", docfile)

                
                if docfile:
                    # Save the file and get its path
                    upload_dir = os.path.join(settings.MEDIA_ROOT, 'University_Documents')
                    file_path = os.path.join(upload_dir, docfile.name)
                    save_path = f'University_Documents/{docfile.name}'
                    with open(file_path, 'wb+') as destination:
                        for chunk in docfile.chunks():
                            destination.write(chunk)
                        docfile = save_path
                else:
                    docfile = uploadeddoc_other
                file_data = {
                    'doctype': doctype,
                    'year': year,
                    'board': board,
                    'percentage': percentage,
                    'file_path': docfile
                }
                files_data.append(file_data)
                #files_data[f'other_{i}'] = file_data
                print("files_data", files_data)

            if secondary_year or secondary_board or secondary_percentage or secondary_document or sr_year or sr_board or sr_percentage or sr_document or under_year or under_board or under_percentage or under_document or post_year or post_board or post_percentage or post_document or mphil_year or mphil_board or mphil_percentage or mphil_document or files_data:
                try:

                    getqualification = OtherQualification.objects.get(student = getstudent.id)
                    print("sr_document", sr_document)
                    getqualification.secondary_year = secondary_year
                    getqualification.sr_year = sr_year
                    getqualification.under_year = under_year
                    getqualification.post_year = post_year
                    getqualification.mphil_year = mphil_year
                        
                    getqualification.secondary_board = secondary_board
                    getqualification.sr_board = sr_board
                    getqualification.under_board = under_board
                    getqualification.post_board = post_board
                    getqualification.mphil_board = mphil_board
                        
                    getqualification.secondary_percentage = secondary_percentage
                    getqualification.sr_percentage = sr_percentage
                    getqualification.under_percentage = under_percentage
                    getqualification.post_percentage = post_percentage
                    getqualification.mphil_percentage = mphil_percentage
                        
                    if secondary_document != None:
                            getqualification.secondary_document = secondary_document
                    if sr_document != None:
                            getqualification.sr_document = sr_document
                    if under_document != None:
                            getqualification.under_document = under_document
                    if post_document != None:
                            getqualification.post_document = post_document
                    if mphil_document != None:
                            getqualification.mphil_document = mphil_document
                   
                    getqualification.others = files_data
                    getqualification.save()

                except OtherQualification.DoesNotExist:
                    print("no record for qualification" , sr_document)
                    create_student_qualification = OtherQualification(
                            student_id = getstudent.id,
                            secondary_year = secondary_year,
                            sr_year = sr_year,
                            under_year = under_year,
                            post_year = post_year,
                            mphil_year = mphil_year,
                          
                        
                            secondary_board = secondary_board,
                            sr_board = sr_board,
                            under_board = under_board,
                            post_board = post_board,
                            mphil_board = mphil_board,
                            
                            
                            secondary_percentage = secondary_percentage,
                            sr_percentage = sr_percentage,
                            under_percentage = under_percentage,
                            post_percentage = post_percentage,
                            mphil_percentage = mphil_percentage,
                            
                            
                            secondary_document = secondary_document,
                            sr_document = sr_document,
                            under_document = under_document,
                            post_document = post_document,
                            mphil_document = mphil_document,
                            
                        )
                    create_student_qualification.save()
              
                ##save any changes made  to Payment details (added by Avani on 15/7)
                try:
                    getPaymentDetails = OtherPaymentReciept.objects.filter(student = getstudent.id).first()
                    print("Payment details object", getPaymentDetails, request.POST.get('payment_mode'))
                    getPaymentDetails.fee_reciept_type =  request.POST.get('fees_reciept')
                    getPaymentDetails.transaction_date =  request.POST.get('date_of_transaction')
                    getPaymentDetails.cheque_no =  request.POST.get('cheque_no')
                    getPaymentDetails.bank_name =  request.POST.get('bank_name')
                    getPaymentDetails.paymentmode =  request.POST.get('payment_mode')
                    getPaymentDetails.remarks =  request.POST.get('remarks')
                    getPaymentDetails.semyearfees =  request.POST.get('total_fees')
                    getPaymentDetails.paidamount =  request.POST.get('fees')
                    getPaymentDetails.pendingamount =  request.POST.get('dues')
                    getPaymentDetails.save()
                except OtherPaymentReciept.DoesNotExist:
                    print("OOOOOOPPPPPS")
                    pass
          
   
   
    params= {
                "students":OtherStudent.objects.filter(~Q(is_cancelled = True) ).order_by('-id'),
                "title" : 'List of Students',
                "msg": 'Student details updated successfully'
    }
    
            
    return render(request,"unplannedregistrations/viewstudents.html", params)

def addOtherUniversity(name):
    print("checking if univ is already present")
    univid = OtherUniversity.objects.filter(university_name=name).values_list('id', flat=True).first()
    print("univid is", univid)
    if univid == None:
        print("trying to add new univ")
        newuniv = OtherUniversity(
        university_name= name,
    )
    newuniv.save()
    univid = OtherUniversity.objects.filter(university_name=name).values_list('id', flat=True).first()
    
    return univid

def addOtherCourse(name):
    print("checking if course is already present")
    courseid = OtherCourse.objects.filter(name=name).values_list('id', flat=True).first()
    print("course is", courseid)
    if courseid == None:
        print("trying to add new course")
        newcourse = OtherCourse(
        name= name,
        )
        newcourse.save()
        courseid = OtherCourse.objects.filter(name=name).values_list('id', flat=True).first()
    
    return courseid

def addOtherStream(name):
    print("checking if stream is already present", name)
    streamid = OtherStream.objects.filter(name=name).values_list('id', flat=True).first()
    print("stream is", streamid)
    if streamid == None:
        print("trying to add new stream")
        newstream = OtherStream(
        name= name,
        )
        newstream.save()
        streamid = OtherStream.objects.filter(name=name).values_list('id', flat=True).first()
    
    return streamid

def addOtherSubStream(name):
    print("checking if substream is already present", name)
    substreamid = OtherSubStream.objects.filter(name=name).values_list('id', flat=True).first()
    print("substream is", substreamid)
    if substreamid == None:
        print("trying to add new substream")
        newsubstream = OtherSubStream(
        name= name,
        )
        newsubstream.save()
        substreamid = OtherSubStream.objects.filter(name=name).values_list('id', flat=True).first()
    
    return substreamid

def showallstudents(request):
    allstudent = OtherStudent.objects.filter( Q(archive = False)).order_by('-id') ## modified by Avani 18/07 - all students entered in system will be verified
    studentlist = []
    for i in allstudent:
        student_id = i.id
        print(student_id, 'student')
               ## added try and except so that if no record the code will not break ... Added by Avani 08/08
        try:
            enrolled = OtherEnrolled.objects.get(student = student_id)
            print(enrolled)
            if enrolled.course != None:
                course = OtherCourse.objects.get(id = enrolled.course.id)
                coursename = course.name
            else:
                coursename = ''
            if enrolled.stream != None:
                stream = OtherStream.objects.get(id = enrolled.stream.id)
                streamname =stream.name
            else:
                streamname = ''
            if enrolled.university != None:
                university = OtherUniversity.objects.get(id = enrolled.university.id)
                universityname = university.university_name
            else:
                universityname = ''
            if enrolled.substream != None:
                substream = OtherSubStream.objects.get(id = enrolled.substream.id)
                substreamname =substream.name
            else:
                substreamname = ''
        except OtherEnrolled.DoesNotExist:
            enrolled = ''
            coursename = ''
            streamname=''
            substreamname = ''

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
         
        if enrolled != '':
            entry_mode = enrolled.entry_mode
            course_pattern = enrolled.course_pattern
            current_sem = enrolled.current_semyear
            session = enrolled.session 
            remarks = enrolled.remarks
        else:
            entry_mode = ''
            current_sem = ''
            session = ''
            course_pattern = ''
            remarks = ''
        if i.counselor_name == '':
            counselor_name = ''
        else:
            counselor_name = i.counselor_name
        if i.new_university_enrollment_id == '':
            university_enrollment_id = ''
        else:
            university_enrollment_id = i.new_university_enrollment_id
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
            "course_name":coursename, ## modified by Avani, handling of empty data
            "stream_name":streamname,## modified by Avani, handling of empty data
            "substream_name":substreamname,
            "course_pattern":course_pattern,## modified by Avani, handling of empty data
            "current_semester":current_sem,## modified by Avani, handling of empty data
            "session":session,## modified by Avani, handling of empty data
            'entry_mode':entry_mode,## modified by Avani, handling of empty data
            'remarks':remarks,
            'university':universityname,
            "is_quick_register":is_quick_register
        }
        studentlist.append(obj)
    
    return JsonResponse({'data':studentlist})

def showstudents(request):
    return render(request, 'unplannedregistrations/viewallstudents.html')

def others_registered_get_fees(request):
    if request.method == 'POST':
        get_fees = request.POST.get('get_fees')
        if get_fees:
            getstudent = OtherStudent.objects.get(enrollment_id = get_fees)
            getfeespaid = OtherPaymentReciept.objects.filter(Q(student = getstudent.id) & (Q(payment_for="Course Fees") | Q(payment_for="Tution Fees") | Q(payment_for="Re-Registration Fees") | Q(payment_for="Examination Fees")))
            feeserializer = PaymentRecieptSerializer(getfeespaid,many=True)
            return JsonResponse({'fees':feeserializer.data,'student_id':getstudent.id})

def others_registered_view_fees(request):
    if request.method == "POST":
        getpayment_reciept = request.POST.get('getpayment_reciept')
        if getpayment_reciept:
            # print(getpayment_reciept)
            get_reciept = OtherPaymentReciept.objects.get(id = getpayment_reciept)
            paymentrecieptserializer = PaymentRecieptSerializer(get_reciept,many=False)
            view_student = OtherStudent.objects.get(id=get_reciept.student.id)
            view_enroll = OtherEnrolled.objects.get(student=view_student.id)
            view_course = OtherCourse.objects.get(id = view_enroll.course.id)
            view_stream = OtherStream.objects.get(id = view_enroll.stream.id)
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
        
def others_registered_get_common_fees_details(request):
    if request.method == "POST":
        commonfees_pendingfees_studentid = request.POST.get('commonfees_pendingfees_studentid')
        if commonfees_pendingfees_studentid:
            # print("clicked")
            try:
                getstudent = OtherStudent.objects.get(id = commonfees_pendingfees_studentid)
                enrolled = OtherEnrolled.objects.get(student = getstudent.id)
                print(getstudent.id)
                try:
                    getfees = OtherPaymentReciept.objects.filter(Q(student = getstudent.id) & Q(payment_for = "Course Fees") )
                    print(getfees.count())
                    if getfees.exists():
                            # Assuming you're interested in the first matching record
                            fees_record = getfees.last()
                            
                            print(fees_record)
                            return JsonResponse({
                                'pendingamount': fees_record.pendingamount,
                                'total_fees': fees_record.semyearfees,
                                
                            })
                    else:
                            # Handle case when no matching records are found
                            return JsonResponse({
                                'pendingamount': None,
                                'total_fees': None,
                                'message': 'No matching record found'
                            })
                                                        
                except PaymentReciept.DoesNotExist:
                        print("reciept not found")
                                
                                # total_fees = int(getstudentfees.totalfees) - int(getlatestsemyearfees.advanceamount)
                                # print(getstudentfees)
                               
                    
                            
                    
            except Student.DoesNotExist:
                print("no student")


def save_more_fees_others(request):
    if request.method == 'POST':
        commonfees_student_id = request.POST.get('commonfees_student_id')
        commonfees_feesfor = request.POST.get('commonfees_feesfor')
        commonfees_totalfees = request.POST.get('commonfees_totalfees')
        commonfees_amount = request.POST.get('commonfees_amount')
        commonfees_feestype = request.POST.get('commonfees_feestype')
        commonfees_transactiondate = request.POST.get('commonfees_transactiondate')
        commonfees_paymentmode = request.POST.get('commonfees_paymentmode')
        commonfees_chequeno = request.POST.get('commonfees_chequeno')
        commonfees_bankname = request.POST.get('commonfees_bankname')
        commonfees_remarks = request.POST.get('commonfees_remarks')
        commonfees_previous_pending_advance = request.POST.get('commonfees_previous_pending')
        commonfees_semyear_totalfees = request.POST.get('commonfees_semyear_totalfees')
        print("commonfees_feesfor", commonfees_feesfor)
        print("commonfees_totalfees", commonfees_totalfees) ##pending amount
        print("commonfees_amount", commonfees_amount) #fees paid 
        print("commonfees_transactiondate", commonfees_transactiondate)
        print("commonfees_paymentmode", commonfees_paymentmode)
        print("commonfees_previous_pending_advance", commonfees_previous_pending_advance) #advance if any
        print("commonfees_semyear_totalfees", commonfees_semyear_totalfees) #total fees
        pending_amount = int(commonfees_totalfees) - int(commonfees_amount)
        if pending_amount < 0:
            if commonfees_previous_pending_advance == '' or commonfees_previous_pending_advance == 0:
                advance_amount = abs(pending_amount)
            else:
                advance_amount = abs(pending_amount) + int(commonfees_previous_pending_advance)
            pending_amount = 0
        else:
            if commonfees_previous_pending_advance == '':
                advance_amount = 0
            else:
                advance_amount = int(commonfees_previous_pending_advance)
            
        if commonfees_paymentmode == "Cheque":
                payment_status = "Not Realised"
                uncleared_amount = commonfees_amount
                paid_amount = 0

        else:
                payment_status = "Realised"
                uncleared_amount = 0
                paid_amount = commonfees_amount
       
        if commonfees_chequeno != '':
            cheque_no = commonfees_chequeno
        else:
            cheque_no = ''
        if commonfees_bankname != '':
            bankname = commonfees_bankname
        else:
            bankname = ''
        # print("Common Fees :",commonfees_student_id,commonfees_feesfor,commonfees_amount,commonfees_feestype,commonfees_semyear,commonfees_transactiondate,commonfees_paymentmode,commonfees_chequeno,commonfees_bankname,commonfees_remarks)
        if commonfees_student_id and commonfees_feesfor and commonfees_amount and commonfees_feestype  and commonfees_paymentmode and commonfees_remarks:
          
            if commonfees_feesfor:
                    print("commonfees_feesfor = ",commonfees_feesfor)
                    try:
                        getstudent = OtherStudent.objects.get(id = commonfees_student_id)
                        
                        try:
                            getlatestreciept = OtherPaymentReciept.objects.latest('id')
                        except OtherPaymentReciept.DoesNotExist:
                            getlatestreciept = "none"
                        if getlatestreciept == "none":
                            transactionID = "OTH00AA01"
                        else:
                            tid = getlatestreciept.transactionID
                            tranx = tid.replace("OTH00AA",'')
                            transactionID =  str("OTH00AA") + str(int(tranx) + 1)
                           
                        
                        
                        print("Total SemYear Fees : ",commonfees_semyear_totalfees)
                        print("Previous Pending Fees : ",commonfees_previous_pending_advance)
                        print("Current Total Pending : ",commonfees_totalfees)
                        print("Paid Fees : ",commonfees_amount)
                        print((commonfees_previous_pending_advance))

                       
                       
                       
                        add_payment_reciept = OtherPaymentReciept(
                                student = getstudent,
                                payment_for="Course Fees",
                                payment_categories = commonfees_feesfor,
                                payment_type=commonfees_feestype,
                                fee_reciept_type="",
                                transaction_date= commonfees_transactiondate,
                                cheque_no=cheque_no,
                                bank_name=bankname,
                                semyearfees=commonfees_semyear_totalfees,
                                paidamount=paid_amount,
                                advanceamount = advance_amount,
                                pendingamount=pending_amount,
                                transactionID = transactionID,
                                paymentmode=commonfees_paymentmode,
                                remarks=commonfees_remarks,session="",
                                uncleared_amount=uncleared_amount,
                                status = payment_status)
                            
                        add_payment_reciept.save()
                        
                        getfeespaid = OtherPaymentReciept.objects.filter(student = getstudent.id)
                        
                        feeserializer = PaymentRecieptSerializer(getfeespaid,many=True)
                        return JsonResponse({'success':'yes','fees':feeserializer.data,'student_id':getstudent.id})
                        
                    
                    except OtherStudent.DoesNotExist:
                        print("no student found")
                
def other_edit_payment_reciept(request):
    if request.method == "POST":
        print("dfdfdfdfdfdfgfdgd")
        editpayment_reciept = request.POST.get('editpayment_reciept')
        if editpayment_reciept:
            try:
                getreciept = OtherPaymentReciept.objects.get(id = editpayment_reciept)
                paymentrecieptserializer = PaymentRecieptSerializer(getreciept,many=False)
                
                return JsonResponse({'edit':'yes','data':paymentrecieptserializer.data})
            except OtherPaymentReciept.DoesNotExist:
                return JsonResponse({'edit':'no'})
                        
def other_edit_payment_reciept_save(request):
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
        editpayment_status = request.POST.get('editpayment_status')
       

        if editpayment_payment_reciept_id:
            try:
                getpaymentreciept = OtherPaymentReciept.objects.get(id = editpayment_payment_reciept_id)

                if editpayment_status != getpaymentreciept.status:
                    getpaymentreciept.status = editpayment_status
                    if editpayment_status == 'Realised':
                        getpaymentreciept.paidamount = editpayment_paid_fees
                        getpaymentreciept.uncleared_amount = 0
                    if editpayment_status == 'Not Realised':
                        getpaymentreciept.uncleared_amount = editpayment_paid_fees
                        getpaymentreciept.paidamount = 0
                else:
                    if editpayment_paid_fees == getpaymentreciept.paidamount:
                        pass
                    else:
                        getpaymentreciept.paidamount = editpayment_paid_fees
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
                
            except OtherPaymentReciept.DoesNotExist:
                print("no payment reciept")

@login_required(login_url='/login/')
def DeleteOtherStudent(request,enroll_id):
    display = ""
    found_student = ""
    student = []
    if request.user.is_superuser:

        if request.method == "POST":
            delete_student_id = request.POST.get('delete_student_id')
            delete = request.POST.get('delete')
            if delete_student_id:
                print("student got")
                try:
                    getstudent = OtherStudent.objects.get(id = delete_student_id)
                    print("Delete Student : ",getstudent)
                    getenroll = OtherEnrolled.objects.filter(student = getstudent.id)
                    studentdocuments = OtherStudentDocuments.objects.filter(student = getstudent.id)
                    qualification = OtherQualification.objects.filter(student = getstudent.id)
                    paymentreciept = OtherPaymentReciept.objects.filter(student = getstudent.id)
                    

                    getstudent.delete()
                    getenroll.delete()
                    studentdocuments.delete()
                    qualification.delete()
                    paymentreciept.delete()
                    return JsonResponse({'deleted':'yes'})

                except Student.DoesNotExist:
                    pass
            
        try:
            getstudent = OtherStudent.objects.get(enrollment_id = enroll_id)
            enroll = OtherEnrolled.objects.get(student = getstudent.id)
            if enroll.course != None:
                course = OtherCourse.objects.get(id = enroll.course.id)
                coursename = course.name
            else:
                coursename = ''
            if enroll.stream != None:
                stream = OtherStream.objects.get(id = enroll.stream.id)
                streamname = stream.name
            else:
                streamname = ''
            if enroll.substream != None:
                substream = OtherSubStream.objects.get(id = enroll.substream.id)
                substreamname = substream.name
            else:
                substreamname = ''
            # print(getstudent , enroll , course , stream)
            commonfees = OtherPaymentReciept.objects.filter(Q(student = getstudent.id) & (Q(payment_for="Course Fees") | Q(payment_for="Tution Fees") | Q(payment_for="Re-Registration Fees") | Q(payment_for="Examination Fees")))
           
            # print("Common Fees : ",commonfees)
            # print("Additional Fees : ",additionalfees)
            obj = {
                "id":getstudent.id,
                "enrollment_id":getstudent.enrollment_id,
                "name":getstudent.name,
                "dateofbirth":getstudent.dateofbirth,
                "email":getstudent.email,
                "mobile":getstudent.mobile,
                "course_pattern":enroll.course_pattern,
                "session":enroll.session,
                "entry_mode":enroll.entry_mode,
                "total_semyear":enroll.total_semyear,
                "current_semyear":enroll.current_semyear,
                "course":coursename,
                "stream":streamname,
                "substream":substreamname,
                "commonfees":commonfees,
               
                
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
    return render(request,"unplannedregistrations/deletestudent.html",params)
                
def showstudentformothers(request, enroll_id): 
    print("enroll_id: ", enroll_id)
    try:
        getstudent = OtherStudent.objects.get(enrollment_id = enroll_id)
        try:
            country = Countries.objects.get(id = getstudent.country_id)
            try:
                state = States.objects.get(id = getstudent.state_id)
                try:
                    district = Cities.objects.get(id = getstudent.city_id)
                except Cities.DoesNotExist:
                    district=''
                    print("No District found")
            except States.DoesNotExist:
                state =''
                print("No state found")
        except Countries.DoesNotExist: 
            country= ''
            print("No Country found")
        addressdetails = {}
        addressdetails['country'] = country.name
        addressdetails['state'] = state.name
        addressdetails['district'] = district.name
        
        counselor_name = getstudent.counselor_name
        university = ''
        streamname = ''
        coursename = ''
        try:
            passport = OtherStudentDocuments.objects.get(student_id = getstudent.id, document="Passport").document_ID_no
        except OtherStudentDocuments.DoesNotExist:
            passport = ''
        try:
            aadhar = OtherStudentDocuments.objects.get(student_id = getstudent.id, document="Aadhar Card").document_ID_no
        except OtherStudentDocuments.DoesNotExist:
            aadhar = ''
        try:
            enrolled = OtherEnrolled.objects.get(student_id = getstudent.id)
            if enrolled.university != None:
                try:
                    university = OtherUniversity.objects.get(id = enrolled.university.id).university_name
                except OtherUniversity.DoesNotExist:
                    university = ''
            if enrolled.course != None:
                try:
                    coursename = OtherCourse.objects.get(id = enrolled.course.id).name
                except OtherCourse.DoesNotExist:
                    coursename = ''
            if enrolled.stream != None:
                try:
                    streamname = OtherStream.objects.get(id = enrolled.stream.id).name
                except OtherStream.DoesNotExist:
                    streamname = ''    
            if enrolled.substream != None:
                try:
                    substreamname = OtherSubStream.objects.get(id = enrolled.substream.id).name
                except OtherSubStream.DoesNotExist:
                    substreamname = ''      
        except OtherEnrolled.DoesNotExist:
            enrolled = ''
            university = ''
            coursename = ''
            streamname = ''
            substreamname = ''
      
        otherdetails = {}
        otherdetails['aadhar'] = aadhar
        otherdetails['passport'] = passport
        otherdetails['counselor'] = counselor_name
        otherdetails['university'] =university
        otherdetails['coursename'] = coursename
        otherdetails['streamname'] = streamname
        otherdetails['substreamname'] = substreamname
        
        try:
            qualificationdetails = OtherQualification.objects.get(student_id = getstudent.id)
            print("qualificationdetails",qualificationdetails)
        except OtherQualification.DoesNotExist:
            qualificationdetails = ''
    except OtherStudent.DoesNotExist:
        getstudent= ''
        print("No student details found.")
   
   
    imagename = "/media/" + str(getstudent.image)
    print("imagename", imagename)
    params= {
        "student": getstudent,
        "addressdetails": addressdetails,
        "otherdetails": otherdetails,
        "coursedetails": enrolled,
        "qualificationdetails": qualificationdetails,
        "image": imagename

    }
    return render(request,"super_admin/studentform.html", params)

def documentmanagementothers(request, enroll_id):
    try:
        getstudent = OtherStudent.objects.get(enrollment_id = enroll_id)
        qualificationdocs = {}
        try:
            qualificationdetails = OtherQualification.objects.get(student_id = getstudent.id)
            print("qualificationdetails",qualificationdetails)
            
            if qualificationdetails.secondary_document != '':
                qualificationdocs["secondary"]= '/media/' + str(qualificationdetails.secondary_document)
            else:
                qualificationdocs["secondary"]= ''
            if qualificationdetails.sr_document != '':
                qualificationdocs["sr"]= '/media/' + str(qualificationdetails.sr_document)
            else:
                qualificationdocs["sr"]= ''
            if qualificationdetails.under_document != '':
                qualificationdocs["under"]= '/media/' + str(qualificationdetails.under_document)
            else:
                qualificationdocs["under"]= ''
            if qualificationdetails.post_document != '':
                qualificationdocs["post"]= '/media/' + str(qualificationdetails.post_document)
            else:
                qualificationdocs['post'] = ''
            if qualificationdetails.mphil_document != '':
                qualificationdocs["mphil"]= '/media/' + str(qualificationdetails.mphil_document)
            else:
                qualificationdocs['mphil'] =''
                qualificationdocs['others'] = qualificationdetails.others
            print(qualificationdetails.others)
        except OtherQualification.DoesNotExist:
            qualificationdetails = ''
        try:
            personaldocuments = OtherStudentDocuments.objects.filter(student_id = getstudent.id)
            print(personaldocuments)
        except OtherStudentDocuments.DoesNotExist:
            personaldocuments = ''

    except Student.DoesNotExist:
        print("No student found")
    params = {
        "qualificationdocs":qualificationdocs,
        "personaldocs":personaldocuments
    }

    return render(request, "super_admin/documentmanagement.html", params)
