from rest_framework.decorators import api_view 
from rest_framework_simplejwt.tokens import RefreshToken
from .api_serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes,parser_classes
from rest_framework.permissions import IsAuthenticated
from .models import *
import logging
from django.db import transaction
from django.db.models.query import QuerySet
import traceback
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import json
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from django.db.models import Q
import pandas as pd
from django.conf import settings
import openpyxl
from openpyxl.styles import Font
from super_admin.role_serializers import *
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
import logging
from django.contrib.auth.models import AnonymousUser
from decimal import Decimal, InvalidOperation
from .services.aisensy import send_aisensy_message, build_exam_details_params, AiSensyError, build_exam_reassign_params
from .utils import *
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

logger = logging.getLogger(__name__)
logger = logging.getLogger('student_registration')
handler = logging.FileHandler('student_registration.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
        }
    
def get_tokens_for_job_seeker(job_seeker):
    # Create a minimal user-like object for JWT
    user = AnonymousUser()
    user.id = job_seeker.id
    user.email = job_seeker.email
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# commented by ankit on 01-09-25 for jobseeker condition
# @api_view(['POST'])
# def login_view(request):
#     serializer = UserLoginSerializer(data=request.data)
    
#     if serializer.is_valid():
#         email = serializer.validated_data.get("email")
#         password = serializer.validated_data.get("password")
#         user = authenticate(email=email, password=password)
#         permissions = user.role.permissions if hasattr(user, 'role') and user.role else []
#         if user is not None:
#             token = get_tokens_for_user(user)
#             is_jobseeker = user.is_jobseeker

#             if user.is_student:
#                 print('inside is_student',user.is_jobseeker)
#                 try:
#                     student = Student.objects.get(email=email)
#                     exams = StudentAppearingExam.objects.filter(
#                         student_id__contains=[student.id]
#                     ).select_related(
#                         'exam__course__university', 
#                         'exam__stream', 
#                         'exam__subject', 
#                         'exam__substream'
#                     )
#                 except Student.DoesNotExist:
#                     return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

#                 if not exams.exists():
#                     print('inside not exams.exists',user.is_jobseeker)
#                     return Response({
#                         "message": "Login Successful",
#                         "token": token,
#                         "is_student": True,
#                         "email": user.email,
#                         "is_active": user.is_active,
#                         "is_jobseeker": is_jobseeker,
#                         "permissions": user.role.permissions if user.role else {},
#                         "is_superadmin": user.is_superuser
                        
#                     }, status=status.HTTP_200_OK)

#                 exam_details = []
#                 examination_data = []
#                 university = None
#                 exam_progress = []

#                 for exam in exams:
#                     try:
#                         examination = exam.exam
#                         university_obj = examination.course.university if examination.course and examination.course.university else None

#                         if university_obj:
#                             university = {
#                                 "id": university_obj.id,
#                                 "name": university_obj.university_name,
#                                 "city": university_obj.university_city,
#                                 "state": university_obj.university_state,
#                                 "pincode": university_obj.university_pincode,
#                                 "logo": request.build_absolute_uri(university_obj.university_logo.url) if university_obj.university_logo else None
#                             }

#                         exam_details.append({
#                             "id": exam.id,
#                             "exam_id": examination.id,
#                             "examstartdate": exam.examstartdate,
#                             "examenddate": exam.examenddate,
#                             "examstarttime": exam.examstarttime,
#                             "examendtime": exam.examendtime
#                         })

#                         examination_data.append({
#                             "id": examination.id,
#                             "course_id": examination.course.id,
#                             "stream_id": examination.stream.id,
#                             "subject_id": examination.subject.id,
#                             "studypattern": examination.studypattern,
#                             "semyear": examination.semyear,
#                             "substream_id": examination.substream.id if examination.substream else None,
#                             "course_name": examination.course.name,
#                             "stream_name": examination.stream.name,
#                             "subject_name": examination.subject.name,
#                             "substream_name": examination.substream.name if examination.substream else None
#                         })

#                         # ExamSession time left
#                         exam_session = ExamSession.objects.filter(student=student, exam=examination).first()
#                         time_left_ms = exam_session.time_left_ms if exam_session else None

#                         # Submitted answers
#                         answered_questions_qs = SubmittedExamination.objects.filter(student=student, exam=examination)
#                         answered_questions = list(answered_questions_qs.values_list('question', flat=True))

#                         # Last answered question id
#                         last_answered_question_id = None
#                         if answered_questions:
#                             try:
#                                 last_answered_question_id = max(int(q) for q in answered_questions if q.isdigit())
#                             except Exception:
#                                 last_answered_question_id = None

#                         exam_progress.append({
#                             "exam_id": examination.id,
#                             "time_left_ms": time_left_ms,
#                             "answered_questions": answered_questions,
#                             "last_answered_question_id": last_answered_question_id,
#                         })

#                     except Examination.DoesNotExist:
#                         logger.error(f"Examination for exam_id {exam.id} does not exist. Skipping.")
#                         continue

#                 # Fetch all Result records for this student filtered by student
#                 result_qs = Result.objects.filter(student=student)

#                 result_data = []
#                 for res in result_qs:
#                     result_data.append({
#                         "id": res.id,
#                         "student_id": res.student.id,  # Added student_id here
#                         "exam_id": res.exam.id if res.exam else None,
#                         "total_question": res.total_question,
#                         "attempted": res.attempted,
#                         "total_marks": res.total_marks,
#                         "score": res.score,
#                         "result": res.result,
#                         "percentage": res.percentage,
#                         "examdetails_id": res.examdetails.id if res.examdetails else None,
#                     })

#                 return Response({
#                     "message": "Login Successful",
#                     "is_student": True,
#                     "token": token,
#                     "student_id": student.id,
#                     "student_name": student.name,
#                     "university_logo": university["logo"] if university else None,
#                     "exam_details": exam_details,
#                     "examination_data": examination_data,
#                     "university": university,
#                     "exam_progress": exam_progress,
#                     "result_data": result_data, 
#                     "is_jobseeker": is_jobseeker,
#                     "permissions": user.role.permissions if user.role else {},
#                     "is_superadmin": user.is_superuser
#                 }, status=status.HTTP_200_OK)



#             else:
#                 print('User is job seeker or not ', user.is_jobseeker)
#                 print('inside else',user.is_jobseeker)
#                 return Response({
#                     "message": "Login Successful",
#                     "token": token,
#                     "is_student": False,
#                     "email": user.email,
#                     "is_active": user.is_active,
#                     "user_id": user.id,
#                     "is_jobseeker": user.is_jobseeker,
#                     "permissions": user.role.permissions if user.role else {},
#                     "is_superadmin": user.is_superuser
#                 }, status=status.HTTP_200_OK)

#         else:
#             return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# updated by ankit on 01-09-25 for jobseeker condition
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
def _safe_permissions(user):
    try:
        return user.role.permissions if getattr(user, "role", None) else {}
    except Exception:
        return {}

def _base_payload(user, token):
    """Common fields that should ALWAYS be present on successful login."""
    return {
        "message": "Login Successful",
        "token": token,
        "user_id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "is_student": bool(getattr(user, "is_student", False)),
        "is_jobseeker": bool(getattr(user, "is_jobseeker", False)),
        "permissions": _safe_permissions(user),
        "is_superadmin": bool(getattr(user, "is_superuser", False)),
    }

@api_view(['POST'])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data.get("email")
    password = serializer.validated_data.get("password")
    user = authenticate(email=email, password=password)

    if user is None:
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)

    token = get_tokens_for_user(user)
    is_student = bool(getattr(user, "is_student", False))
    is_jobseeker = bool(getattr(user, "is_jobseeker", False))

    # ------ STUDENT BRANCH ------
    if is_student:
        try:
            student = Student.objects.get(email=email)
        except Student.DoesNotExist:
            # Still return a consistent payload, just without student-specific add-ons
            payload = _base_payload(user, token)
            payload.update({
                "student_error": "Student not found",
            })
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

        exams = StudentAppearingExam.objects.filter(
            student_id__contains=[student.id]
        ).select_related(
            'exam__course__university',
            'exam__stream',
            'exam__subject',
            'exam__substream'
        )

        if not exams.exists():
            # Return base payload only (consistent keys)
            payload = _base_payload(user, token)
            payload.update({
                "student_id": student.id,
                "student_name": getattr(student, "name", None),
                "exam_details": [],
                "examination_data": [],
                "university": None,
                "university_logo": None,
                "exam_progress": [],
                "result_data": [],
            })
            return Response(payload, status=status.HTTP_200_OK)

        # Build student-specific info
        exam_details = []
        examination_data = []
        university = None
        exam_progress = []

        for exam in exams:
            try:
                examination = exam.exam
                university_obj = examination.course.university if examination.course and examination.course.university else None

                if university_obj:
                    university = {
                        "id": university_obj.id,
                        "name": university_obj.university_name,
                        "city": university_obj.university_city,
                        "state": university_obj.university_state,
                        "pincode": university_obj.university_pincode,
                        "logo": request.build_absolute_uri(university_obj.university_logo.url) if university_obj.university_logo else None
                    }

                exam_details.append({
                    "id": exam.id,
                    "exam_id": examination.id,
                    "examstartdate": exam.examstartdate,
                    "examenddate": exam.examenddate,
                    "examstarttime": exam.examstarttime,
                    "examendtime": exam.examendtime
                })

                examination_data.append({
                    "id": examination.id,
                    "course_id": examination.course.id,
                    "stream_id": examination.stream.id,
                    "subject_id": examination.subject.id,
                    "studypattern": examination.studypattern,
                    "semyear": examination.semyear,
                    "substream_id": examination.substream.id if examination.substream else None,
                    "course_name": examination.course.name,
                    "stream_name": examination.stream.name,
                    "subject_name": examination.subject.name,
                    "substream_name": examination.substream.name if examination.substream else None
                })

                exam_session = ExamSession.objects.filter(student=student, exam=examination).first()
                time_left_ms = exam_session.time_left_ms if exam_session else None

                answered_questions_qs = SubmittedExamination.objects.filter(student=student, exam=examination)
                answered_questions = list(answered_questions_qs.values_list('question', flat=True))

                last_answered_question_id = None
                if answered_questions:
                    try:
                        last_answered_question_id = max(int(q) for q in answered_questions if str(q).isdigit())
                    except Exception:
                        last_answered_question_id = None

                exam_progress.append({
                    "exam_id": examination.id,
                    "time_left_ms": time_left_ms,
                    "answered_questions": answered_questions,
                    "last_answered_question_id": last_answered_question_id,
                })

            except Examination.DoesNotExist:
                # Skip if any bad record
                continue

        # Results
        result_qs = Result.objects.filter(student=student)
        result_data = [{
            "id": res.id,
            "student_id": res.student.id,
            "exam_id": res.exam.id if res.exam else None,
            "total_question": res.total_question,
            "attempted": res.attempted,
            "total_marks": res.total_marks,
            "score": res.score,
            "result": res.result,
            "percentage": res.percentage,
            "examdetails_id": res.examdetails.id if res.examdetails else None,
        } for res in result_qs]

        payload = _base_payload(user, token)
        payload.update({
            "student_id": student.id,
            "student_name": getattr(student, "name", None),
            "university_logo": university["logo"] if university else None,
            "exam_details": exam_details,
            "examination_data": examination_data,
            "university": university,
            "exam_progress": exam_progress,
            "result_data": result_data,
        })
        return Response(payload, status=status.HTTP_200_OK)

    # ------ JOBSEEKER (NOT STUDENT) BRANCH ------
    if is_jobseeker and not is_student:
        # Provide lightweight JobSeekerProfile info so the frontend can immediately know
        # whether a resume exists, etc. (and still have user_id every time)
        profile, _created = JobSeekerProfile.objects.get_or_create(user=user)
        # If you want to include a serializer response instead, use your serializer:
        # js_data = JobSeekerProfileSerializer(profile, context={"request": request}).data

        resume_url = request.build_absolute_uri(profile.resume.url) if profile.resume else None

        payload = _base_payload(user, token)
        payload.update({
            "jobseeker_profile": {
                "id": profile.id,
                "work_status": profile.work_status,
                "city": profile.city,
                "resume_url": resume_url,
            }
            # Or: "jobseeker_profile": js_data
        })
        return Response(payload, status=status.HTTP_200_OK)

    # ------ NEITHER STUDENT NOR JOBSEEKER ------
    payload = _base_payload(user, token)
    return Response(payload, status=status.HTTP_200_OK)



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def add_university(request):
    user = request.user

    if request.method == 'GET':
        universities = University.objects.all()
        serializer = UniversitySerializer(universities, many=True)
        # logger.info(f"[{user.email}] fetched universities list.")
        return Response(serializer.data, status=status.HTTP_200_OK)

    # if not (user.is_superuser or getattr(user, 'is_data_entry', False)):
    #     logger.warning(f"[{user.email}] Unauthorized university creation attempt.")
    #     return Response({"message": "You do not have permission to add a university."}, status=status.HTTP_403_FORBIDDEN)

    university_name = request.data.get("university_name", "").strip()
    university_address = request.data.get("university_address", "").strip()

    if not university_name or not university_address:
        logger.warning(f"[{user.email}] Missing university fields.")
        return Response({"message": "University name and address are required."}, status=status.HTTP_400_BAD_REQUEST)

    if University.objects.filter(university_name__iexact=university_name).exists():
        logger.warning(f"[{user.email}] Tried adding duplicate university: {university_name}")
        return Response({"message": "University name already exists."}, status=status.HTTP_406_NOT_ACCEPTABLE)

    lowercase = university_name.lower().replace(' ', '')
    today = str(date.today()).replace('-', '')
    registration_id = f"{lowercase}{today}UNI"

    data = {
        'university_name': university_name,
        'university_address': university_address,
        'university_city': request.data.get('university_city', ''),
        'university_state': request.data.get('university_state', ''),
        'university_pincode': request.data.get('university_pincode', ''),
        'registrationID': registration_id,
        'university_logo': request.FILES.get('university_logo', None)
    }

    serializer = UniversitySerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        #logger.info(f"[{user.email}] Successfully added university: {university_name}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    logger.error(f"[{user.email}] Error validating university data: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def university_detail(request, university_id):
    user = request.user
    try:
        university = University.objects.get(pk=university_id)
    except University.DoesNotExist:
        logger.warning(f"[{user.email}] Tried accessing nonexistent university ID: {university_id}")
        return Response({"message": "University not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UniversitySerializer(university)
        #logger.info(f"[{user.email}] viewed university ID: {university_id}")
        return Response(serializer.data)

    if request.method == 'PUT':
        if not (user.is_superuser or getattr(user, 'is_data_entry', False)):
            logger.warning(f"[{user.email}] Unauthorized university update attempt.")
            return Response({"message": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UniversitySerializer(university, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            #logger.info(f"[{user.email}] updated university ID: {university_id}")
            return Response(serializer.data)
        logger.error(f"[{user.email}] error updating university ID: {university_id} | {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if not user.is_superuser:
            logger.warning(f"[{user.email}] Unauthorized university deletion attempt.")
            return Response({"message": "Only superusers can delete universities."}, status=status.HTTP_403_FORBIDDEN)
        university.delete()
        #logger.info(f"[{user.email}] deleted university ID: {university_id}")
        return Response({"message": "University deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
  
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def create_user(request):
    user = request.user

    # Handle GET request
    if request.method == "GET":
        if user.is_superuser:
            # Filter users by specific roles (e.g., Fee Clerk, Data Entry)
            roles_filter = request.query_params.get('role', None)
            if roles_filter:
                # Filter users by the role passed in query parameters
                users = User.objects.filter(role__name=roles_filter)
            else:
                # Default filter if no role is provided
                users = User.objects.filter(role__name__in=['Fee_clerk', 'Data_entry'])
            
            # Serialize the users
            serializer = UserSerializers(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Return forbidden if the user is not a superuser
        return Response({"message": "You do not have permission to view users."}, status=status.HTTP_403_FORBIDDEN)

    # Handle POST request to create new users
    if request.method == "POST":
        if user.is_superuser:
            # Ensure that the incoming data contains role information
            role_name = request.data.get('role', None)
            if role_name:
                try:
                    role = Role.objects.get(name=role_name)
                except Role.DoesNotExist:
                    return Response({"error": "Role does not exist."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Role is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Initialize serializer
            serializer = UserSerializers(data=request.data)

            if serializer.is_valid():
                # Assign role and default permissions based on role
                new_user = serializer.save(role=role)

                # Assign default permissions based on user role or super admin status
                if new_user.is_superuser:
                    new_user.permissions = super_admin_permissions
                elif new_user.role:
                    new_user.permissions = new_user.role.permissions
                else:
                    new_user.permissions = default_permissions

                new_user.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Return forbidden if the user is not a superuser
        return Response({"message": "You do not have permission to create users."}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_semester_fees(request):
    """
    Creates semester fees. substream_id is optional.
    - If substream_id is provided: create for that substream.
    - If substream_id is omitted/empty: create a 'generic' fee (substream=NULL) for the stream.
    Uniqueness: (stream, substream(or NULL), sem) must be unique.
    """
    try:
        payload = request.data if isinstance(request.data, list) else [request.data]
        responses = []

        with transaction.atomic():
            for entry in payload:
                try:
                    # required now excludes substream_id
                    required_fields = ['university_id', 'course_id', 'stream_id', 'sem']
                    missing = [f for f in required_fields if not entry.get(f)]
                    if missing:
                        responses.append({"error": f"Missing required fields: {', '.join(missing)}"})
                        continue

                    # Resolve FK chain
                    university = University.objects.filter(id=entry['university_id']).first()
                    if not university:
                        responses.append({"error": "Invalid university_id."})
                        continue

                    course = Course.objects.filter(id=entry['course_id'], university=university).first()
                    if not course:
                        responses.append({"error": "Invalid course_id for given university."})
                        continue

                    stream = Stream.objects.filter(id=entry['stream_id'], course=course).first()
                    if not stream:
                        responses.append({"error": "Invalid stream_id for given course."})
                        continue

                    # substream is optional
                    substream_id = entry.get('substream_id')
                    substream = None
                    if substream_id:
                        substream = SubStream.objects.filter(id=substream_id, stream=stream).first()
                        if not substream:
                            responses.append({"error": "Invalid substream_id for given stream."})
                            continue

                    # Sem validation
                    sem = int(entry['sem'])
                    if sem < 1 or sem > 8:
                        responses.append({"error": f"Semester '{sem}' must be between 1 and 8."})
                        continue

                    # Uniqueness check: stream + substream(NULL or specific) + sem
                    exists_qs = SemesterFees.objects.filter(stream=stream, sem=sem)
                    if substream is None:
                        exists_qs = exists_qs.filter(substream__isnull=True)
                    else:
                        exists_qs = exists_qs.filter(substream=substream)

                    if exists_qs.exists():
                        responses.append({"error": f"Semester fee for sem {sem} already exists for this stream/substream."})
                        continue

                    # Parse amounts (default 0)
                    tutionfees       = float(entry.get('tutionfees', 0) or 0)
                    examinationfees  = float(entry.get('examinationfees', 0) or 0)
                    bookfees         = float(entry.get('bookfees', 0) or 0)
                    resittingfees    = float(entry.get('resittingfees', 0) or 0)
                    entrancefees     = float(entry.get('entrancefees', 0) or 0)
                    extrafees        = float(entry.get('extrafees', 0) or 0)
                    discount         = float(entry.get('discount', 0) or 0)

                    totalfees = (
                        tutionfees + examinationfees + bookfees +
                        resittingfees + entrancefees + extrafees - discount
                    )

                    fee = SemesterFees.objects.create(
                        stream=stream,
                        substream=substream,  # can be None
                        sem=sem,
                        tutionfees=tutionfees,
                        examinationfees=examinationfees,
                        bookfees=bookfees,
                        resittingfees=resittingfees,
                        entrancefees=entrancefees,
                        extrafees=extrafees,
                        discount=discount,
                        totalfees=totalfees,
                        created_by=request.user.id,
                        modified_by=request.user.id,
                    )

                    responses.append({
                        "message": f"Semester fee created for Semester {sem}",
                        "data": {
                            "stream": stream.id,
                            "substream": substream.id if substream else None,
                            "sem": fee.sem,
                            "tutionfees": fee.tutionfees,
                            "examinationfees": fee.examinationfees,
                            "bookfees": fee.bookfees,
                            "resittingfees": fee.resittingfees,
                            "entrancefees": fee.entrancefees,
                            "extrafees": fee.extrafees,
                            "discount": fee.discount,
                            "totalfees": fee.totalfees,
                        },
                    })
                except Exception as entry_err:
                    logger.exception("Entry error in create_semester_fees")
                    responses.append({"error": str(entry_err)})

        return Response(responses, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.exception("Internal server error in create_semester_fees")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_semester_fees(request):
    """
    UPSERT semester fees (no model changes).
    - substream_id optional (None => generic)
    - Key: (stream, substream, sem)
    - If exists: UPDATE; else: CREATE
    Accepts a single object or a list.
    """
    try:
        payload = request.data if isinstance(request.data, list) else [request.data]
        responses = []

        def to_float(v):
            try:
                return float(v or 0)
            except Exception:
                return 0.0

        with transaction.atomic():
            for entry in payload:
                try:
                    required_fields = ['university_id', 'course_id', 'stream_id', 'sem']
                    missing = [f for f in required_fields if not entry.get(f)]
                    if missing:
                        responses.append({"error": f"Missing required fields: {', '.join(missing)}"})
                        continue

                    # FK chain
                    university = University.objects.filter(id=entry['university_id']).first()
                    if not university:
                        responses.append({"error": "Invalid university_id."})
                        continue

                    course = Course.objects.filter(id=entry['course_id'], university=university).first()
                    if not course:
                        responses.append({"error": "Invalid course_id for given university."})
                        continue

                    stream = Stream.objects.filter(id=entry['stream_id'], course=course).first()
                    if not stream:
                        responses.append({"error": "Invalid stream_id for given course."})
                        continue

                    # optional substream
                    substream = None
                    substream_id = entry.get('substream_id')
                    if substream_id:
                        substream = SubStream.objects.filter(id=substream_id, stream=stream).first()
                        if not substream:
                            responses.append({"error": "Invalid substream_id for given stream."})
                            continue

                    # sem as int but stored as str in model
                    try:
                        sem_int = int(entry['sem'])
                    except (ValueError, TypeError):
                        responses.append({"error": "sem must be an integer."})
                        continue
                    if sem_int < 1 or sem_int > 8:
                        responses.append({"error": f"Semester '{sem_int}' must be between 1 and 8."})
                        continue

                    # amounts
                    tutionfees      = to_float(entry.get('tutionfees'))
                    examinationfees = to_float(entry.get('examinationfees'))
                    bookfees        = to_float(entry.get('bookfees'))
                    resittingfees   = to_float(entry.get('resittingfees'))
                    entrancefees    = to_float(entry.get('entrancefees'))
                    extrafees       = to_float(entry.get('extrafees'))
                    discount        = to_float(entry.get('discount'))

                    totalfees = (
                        tutionfees + examinationfees + bookfees +
                        resittingfees + entrancefees + extrafees - discount
                    )

                    # UPSERT on (stream, substream, sem)
                    lookup = {
                        "stream": stream,
                        "substream": substream,         # can be None
                        "sem": str(sem_int),            # your model stores CharField
                    }
                    defaults = {
                        "tutionfees": str(tutionfees),
                        "examinationfees": str(examinationfees),
                        "bookfees": str(bookfees),
                        "resittingfees": str(resittingfees),
                        "entrancefees": str(entrancefees),
                        "extrafees": str(extrafees),
                        "discount": str(discount),
                        "totalfees": str(totalfees),
                        "modified_by": str(request.user.id),
                    }

                    obj, created = SemesterFees.objects.update_or_create(**lookup, defaults=defaults)
                    if created:
                        obj.created_by = str(request.user.id)
                        obj.save(update_fields=["created_by"])

                    responses.append({
                        "message": f"Semester {sem_int} {'created' if created else 'updated'}",
                        "action": "created" if created else "updated",
                        "data": {
                            "stream": obj.stream_id,
                            "substream": obj.substream_id,
                            "sem": obj.sem,
                            "tutionfees": obj.tutionfees,
                            "examinationfees": obj.examinationfees,
                            "bookfees": obj.bookfees,
                            "resittingfees": obj.resittingfees,
                            "entrancefees": obj.entrancefees,
                            "extrafees": obj.extrafees,
                            "discount": obj.discount,
                            "totalfees": obj.totalfees,
                        },
                    })
                except Exception as entry_err:
                    logger.exception("Entry error in create_semester_fees")
                    responses.append({"error": str(entry_err)})

        # Always 200 so frontend can inspect per-row results
        return Response(responses, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception("Internal server error in create_semester_fees")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_year_fees(request):
#     """
#     Creates year fees. substream_id is optional.
#     Uniqueness: (stream, substream(or NULL), year) must be unique.
#     """
#     try:
#         payload = request.data if isinstance(request.data, list) else [request.data]
#         responses = []

#         with transaction.atomic():
#             for entry in payload:
#                 try:
#                     # required now excludes substream_id
#                     required_fields = ['university_id', 'course_id', 'stream_id', 'year']
#                     missing = [f for f in required_fields if not entry.get(f)]
#                     if missing:
#                         responses.append({"error": f"Missing required fields: {', '.join(missing)}"})
#                         continue

#                     university = University.objects.filter(id=entry['university_id']).first()
#                     if not university:
#                         responses.append({"error": "Invalid university_id."})
#                         continue

#                     course = Course.objects.filter(id=entry['course_id'], university=university).first()
#                     if not course:
#                         responses.append({"error": "Invalid course_id for given university."})
#                         continue

#                     stream = Stream.objects.filter(id=entry['stream_id'], course=course).first()
#                     if not stream:
#                         responses.append({"error": "Invalid stream_id for given course."})
#                         continue

#                     # substream optional
#                     substream_id = entry.get('substream_id')
#                     substream = None
#                     if substream_id:
#                         substream = SubStream.objects.filter(id=substream_id, stream=stream).first()
#                         if not substream:
#                             responses.append({"error": "Invalid substream_id for given stream."})
#                             continue

#                     year = int(entry['year'])
#                     if year < 1 or year > 4:
#                         responses.append({"error": f"Year '{year}' must be between 1 and 4."})
#                         continue

#                     # Uniqueness check: stream + substream(NULL or specific) + year
#                     exists_qs = YearFees.objects.filter(stream=stream, year=year)
#                     if substream is None:
#                         exists_qs = exists_qs.filter(substream__isnull=True)
#                     else:
#                         exists_qs = exists_qs.filter(substream=substream)

#                     if exists_qs.exists():
#                         responses.append({"error": f"Year fee for year {year} already exists for this stream/substream."})
#                         continue

#                     # Parse amounts
#                     tutionfees       = float(entry.get('tutionfees', 0) or 0)
#                     examinationfees  = float(entry.get('examinationfees', 0) or 0)
#                     bookfees         = float(entry.get('bookfees', 0) or 0)
#                     resittingfees    = float(entry.get('resittingfees', 0) or 0)
#                     entrancefees     = float(entry.get('entrancefees', 0) or 0)
#                     extrafees        = float(entry.get('extrafees', 0) or 0)
#                     discount         = float(entry.get('discount', 0) or 0)

#                     totalfees = (
#                         tutionfees + examinationfees + bookfees +
#                         resittingfees + entrancefees + extrafees - discount
#                     )

#                     fee = YearFees.objects.create(
#                         stream=stream,
#                         substream=substream,  # can be None
#                         year=year,
#                         tutionfees=tutionfees,
#                         examinationfees=examinationfees,
#                         bookfees=bookfees,
#                         resittingfees=resittingfees,
#                         entrancefees=entrancefees,
#                         extrafees=extrafees,
#                         discount=discount,
#                         totalfees=totalfees,
#                         created_by=request.user.id,
#                         modified_by=request.user.id,
#                     )

#                     responses.append({
#                         "message": f"Year fee created for Year {year}",
#                         "data": {
#                             "stream": stream.id,
#                             "substream": substream.id if substream else None,
#                             "year": fee.year,
#                             "tutionfees": fee.tutionfees,
#                             "examinationfees": fee.examinationfees,
#                             "bookfees": fee.bookfees,
#                             "resittingfees": fee.resittingfees,
#                             "entrancefees": fee.entrancefees,
#                             "extrafees": fee.extrafees,
#                             "discount": fee.discount,
#                             "totalfees": fee.totalfees,
#                         },
#                     })
#                 except Exception as entry_err:
#                     logger.exception("Entry error in create_year_fees")
#                     responses.append({"error": str(entry_err)})

#         return Response(responses, status=status.HTTP_201_CREATED)

#     except Exception as e:
#         logger.exception("Internal server error in create_year_fees")
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_year_fees(request):
    """
    Upsert (create or update) Year Fees.
    substream_id is optional.
    Uniqueness key: (stream, substream (NULL or value), year)
    """
    try:
        payload = request.data if isinstance(request.data, list) else [request.data]
        responses = []

        with transaction.atomic():
            for entry in payload:
                try:
                    # required (substream optional)
                    required_fields = ['university_id', 'course_id', 'stream_id', 'year']
                    missing = [f for f in required_fields if not entry.get(f)]
                    if missing:
                        responses.append({"error": f"Missing required fields: {', '.join(missing)}"})
                        continue

                    # Resolve FK chain
                    university = University.objects.filter(id=entry['university_id']).first()
                    if not university:
                        responses.append({"error": "Invalid university_id."})
                        continue

                    course = Course.objects.filter(id=entry['course_id'], university=university).first()
                    if not course:
                        responses.append({"error": "Invalid course_id for given university."})
                        continue

                    stream = Stream.objects.filter(id=entry['stream_id'], course=course).first()
                    if not stream:
                        responses.append({"error": "Invalid stream_id for given course."})
                        continue

                    # substream optional
                    substream = None
                    substream_id = entry.get('substream_id')
                    if substream_id:
                        substream = SubStream.objects.filter(id=substream_id, stream=stream).first()
                        if not substream:
                            responses.append({"error": "Invalid substream_id for given stream."})
                            continue

                    # year (model uses CharField)
                    try:
                        year_int = int(entry['year'])
                    except (TypeError, ValueError):
                        responses.append({"error": "year must be an integer."})
                        continue
                    if year_int < 1 or year_int > 4:
                        responses.append({"error": f"Year '{year_int}' must be between 1 and 4."})
                        continue
                    year_str = str(year_int)

                    # amounts (same style as semester: float(... or 0))
                    tutionfees       = float(entry.get('tutionfees', 0) or 0)
                    examinationfees  = float(entry.get('examinationfees', 0) or 0)
                    bookfees         = float(entry.get('bookfees', 0) or 0)
                    resittingfees    = float(entry.get('resittingfees', 0) or 0)
                    entrancefees     = float(entry.get('entrancefees', 0) or 0)
                    extrafees        = float(entry.get('extrafees', 0) or 0)
                    discount         = float(entry.get('discount', 0) or 0)

                    totalfees = (
                        tutionfees + examinationfees + bookfees +
                        resittingfees + entrancefees + extrafees - discount
                    )

                    # UPSERT — match on (stream, substream, year), update fields in defaults
                    obj, created = YearFees.objects.update_or_create(
                        stream=stream,
                        substream=substream,          # None matches NULL
                        year=year_str,                # model is CharField
                        defaults={
                            "tutionfees":      str(tutionfees),
                            "examinationfees": str(examinationfees),
                            "bookfees":        str(bookfees),
                            "resittingfees":   str(resittingfees),
                            "entrancefees":    str(entrancefees),
                            "extrafees":       str(extrafees),
                            "discount":        str(discount),
                            "totalfees":       str(totalfees),
                            "modified_by":     str(request.user.id),
                        }
                    )

                    # set created_by only first time
                    if created:
                        obj.created_by = str(request.user.id)
                        obj.save(update_fields=["created_by"])

                    responses.append({
                        "action": "created" if created else "updated",
                        "message": f"Year fee {'created' if created else 'updated'} for Year {year_str}",
                        "data": {
                            "stream": stream.id,
                            "substream": substream.id if substream else None,
                            "year": obj.year,
                            "tutionfees": obj.tutionfees,
                            "examinationfees": obj.examinationfees,
                            "bookfees": obj.bookfees,
                            "resittingfees": obj.resittingfees,
                            "entrancefees": obj.entrancefees,
                            "extrafees": obj.extrafees,
                            "discount": obj.discount,
                            "totalfees": obj.totalfees,
                        },
                    })

                except Exception as entry_err:
                    logger.exception("Entry error in create_year_fees")
                    responses.append({"error": str(entry_err)})

        # 200 because it can be mixed created/updated
        return Response(responses, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception("Internal server error in create_year_fees")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def payment_modes(request):
    # if not request.user.is_superuser:
    #     logger.warning(f"[{request.user.email}] Unauthorized access to payment_modes.")
    #     return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        modes = PaymentModes.objects.all()
        serializer = PaymentModesSerializer(modes, many=True)
        #logger.info("Payment modes list fetched.")
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = PaymentModesSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            if PaymentModes.objects.filter(name__iexact=name).exists():
                logger.warning(f"Duplicate payment mode attempted: {name}")
                return Response({"error": "Mode already exists"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            #logger.info(f"Payment mode created: {name}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Payment mode creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def payment_mode_detail(request, id):
    try:
        mode = PaymentModes.objects.get(id=id)
    except PaymentModes.DoesNotExist:
        logger.warning(f"Payment mode with ID {id} not found.")
        return Response({"error": "PaymentMode not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PaymentModesSerializer(mode)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = PaymentModesSerializer(mode, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            #logger.info(f"Updated payment mode ID {id}.")
            return Response(serializer.data)
        logger.error(f"Failed to update payment mode ID {id}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        mode.delete()
        #logger.info(f"Deleted payment mode ID {id}.")
        return Response({"message": "Payment mode deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def fee_receipt_options(request):
    # if not request.user.is_superuser:
    #     logger.warning(f"[{request.user.email}] Unauthorized access to fee_receipt_options.")
    #     return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        options = FeeReceiptOptions.objects.all()
        serializer = FeeReceiptOptionsSerializer(options, many=True)
        #logger.info("Fetched all fee receipt options.")
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = FeeReceiptOptionsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            #logger.info("Created new fee receipt option.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Failed to create fee receipt option: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def fee_receipt_option_detail(request, id):
    # if not request.user.is_superuser:
    #     logger.warning(f"[{request.user.email}] Unauthorized access to fee_receipt_option_detail.")
    #     return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    try:
        option = FeeReceiptOptions.objects.get(id=id)
    except FeeReceiptOptions.DoesNotExist:
        return Response({"error": "FeeReceiptOption not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = FeeReceiptOptionsSerializer(option)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = FeeReceiptOptionsSerializer(option, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            #logger.info(f"Updated fee receipt option ID {id}.")
            return Response(serializer.data)
        logger.error(f"Failed to update fee receipt option ID {id}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        option.delete()
        #logger.info(f"Deleted fee receipt option ID {id}.")
        return Response({"message": "Fee receipt option deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def bank_names(request):
    # if not request.user.is_superuser:
    #     logger.warning(f"[{request.user.email}] Unauthorized access to bank_names.")
    #     return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        banks = BankNames.objects.all()
        serializer = BankNamesSerializer(banks, many=True)
        #logger.info("Fetched all bank names.")
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = BankNamesSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            if BankNames.objects.filter(name__iexact=name).exists():
                logger.warning(f"Attempted to create duplicate bank name: {name}")
                return Response({"error": "Bank name already exists"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            #logger.info(f"Created new bank name: {name}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Failed to create bank name: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def bank_name_detail(request, id):
    try:
        bank = BankNames.objects.get(id=id)
    except BankNames.DoesNotExist:
        logger.warning(f"Bank name with ID {id} not found.")
        return Response({"error": "BankName not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BankNamesSerializer(bank)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = BankNamesSerializer(bank, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            #logger.info(f"Updated bank name ID {id}.")
            return Response(serializer.data)
        logger.error(f"Failed to update bank name ID {id}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        bank.delete()
        #logger.info(f"Deleted bank name ID {id}.")
        return Response({"message": "Bank name deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def session_names(request):
    """
    Handles GET and POST for SessionNames.
    Only superusers can perform these operations.
    """
    # if not request.user.is_superuser:
    #     logger.warning(f"[{request.user.email}] Unauthorized access to session_names.")
    #     return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        sessions = SessionNames.objects.all()
        serializer = SessionNamesSerializer(sessions, many=True)
        #logger.info("Fetched all session names.")
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        serializer = SessionNamesSerializer(data=request.data)
        if serializer.is_valid():
            if SessionNames.objects.filter(name__iexact=serializer.validated_data['name']).exists():
                logger.warning("Attempt to create duplicate session name.")
                return Response({"error": "Session name already exists"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            #logger.info(f"Session name created: {serializer.validated_data['name']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Failed to create session name: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def session_name_detail(request, id):
    """
    Handles GET, PUT, and DELETE for a specific SessionName by ID.
    Only superusers can perform these operations.
    """
    # if not request.user.is_superuser:
    #     logger.warning(f"[{request.user.email}] Unauthorized access to session_name_detail.")
    #     return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    try:
        session = SessionNames.objects.get(id=id)
    except SessionNames.DoesNotExist:
        logger.warning(f"Session name ID {id} not found.")
        return Response({"error": "Session name not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SessionNamesSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        serializer = SessionNamesSerializer(session, data=request.data, partial=True)
        if serializer.is_valid():
            if 'name' in serializer.validated_data and SessionNames.objects.filter(
                name__iexact=serializer.validated_data['name']
            ).exclude(id=session.id).exists():
                logger.warning(f"Duplicate session name attempted in update: {serializer.validated_data['name']}")
                return Response({"error": "Session name already exists"}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            #logger.info(f"Updated session name ID {id}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(f"Failed to update session name ID {id}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        session.delete()
        #logger.info(f"Deleted session name ID {id}")
        return Response({"message": "Session name deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Handle password change. It takes two password fields: password and confirm_password.
    """
    user = request.user  # Get the authenticated user

    # Check if the user is authenticated
    if not user.is_authenticated:
        logger.warning("Unauthorized password change attempt.")
        return Response(
            {"error": "Authentication required. User not found or anonymous."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Initialize the serializer with the request data
    serializer = ChangePasswordSerializer(data=request.data)

    # Validate the serializer
    if serializer.is_valid():
        # Set the new password for the user
        user.set_password(serializer.validated_data['password'])
        user.save()  # Save the new password to the database

        # Return a success response
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

    # If validation fails, return errors
    logger.error(f"[{user.email}] failed password change: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_courses_by_university(request):
    university_name = request.query_params.get('university')

    if not university_name:
        logger.warning("Missing university parameter in get_courses_by_university.")
        return Response({"error": "University name is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        university = University.objects.get(university_name=university_name)
    except University.DoesNotExist:
        logger.warning(f"University not found: {university_name}")
        return Response({"error": "University not found."}, status=status.HTTP_404_NOT_FOUND)

    courses = university.course_set.all()
    course_names = [course.name for course in courses]

    #logger.info(f"Courses fetched for university: {university_name}")
    return Response({
        "university": university_name,
        "courses": course_names
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stream_by_course_one(request):
    course_name = request.query_params.get('course')
    university_name = request.query_params.get('university')

    if not course_name or not university_name:
        logger.warning("Missing course or university in request.")
        return Response({"error": "Both 'course_name' and 'university_name' are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        university = University.objects.get(university_name=university_name)
    except University.DoesNotExist:
        logger.error("University not found: '%s'", university_name)
        return Response({"error": f"University '{university_name}' not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        course = Course.objects.get(name=course_name, university=university)
    except Course.DoesNotExist:
        logger.error("Course '%s' not found for university '%s'", course_name, university_name)
        return Response({"error": f"Course '{course_name}' not found for university '{university_name}'."}, status=status.HTTP_404_NOT_FOUND)

    try:
        streams = Stream.objects.filter(course=course)
        stream_list = [
            {
                "stream_id": stream.id,
                "stream_name": stream.name,
                "semester": stream.sem,
                "year": stream.year
            }
            for stream in streams
        ]

        #logger.info("Streams fetched for course '%s' at university '%s'", course.name, university.university_name)

        return Response({
            "university_name": university.university_name,
            "course_name": course.name,
            "course_id": course.id,
            "streams": stream_list
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error("Exception occurred while fetching streams: %s", str(e))
        return Response({"error": "Unable to fetch streams."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
  
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_substreams_by_university_course_stream(request):
    university_name = request.query_params.get('university')
    course_name = request.query_params.get('course')
    stream_name = request.query_params.get('stream')

    if not university_name or not course_name or not stream_name:
        logger.warning("Missing one or more required parameters: university, course, stream.")
        return Response({"error": "University name, course name, and stream name are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        university = University.objects.get(university_name=university_name)
    except University.DoesNotExist:
        logger.error("University not found: '%s'", university_name)
        return Response({"error": "University not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        course = Course.objects.get(university=university, name=course_name)
    except Course.DoesNotExist:
        logger.error("Course not found: '%s' under university '%s'", course_name, university_name)
        return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        stream = Stream.objects.get(course=course, name=stream_name)
    except Stream.DoesNotExist:
        logger.error("Stream not found: '%s' in course '%s'", stream_name, course_name)
        return Response({"error": "Stream not found."}, status=status.HTTP_404_NOT_FOUND)

    substreams = SubStream.objects.filter(stream=stream)
    substream_names = [substream.name for substream in substreams]

    #logger.info("Fetched %d substreams for stream '%s'", len(substream_names), stream.name)
    return Response(substream_names, status=status.HTTP_200_OK)
        
from django.contrib.auth.hashers import make_password

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_by_enrollment_id(request):
    enrollment_id = request.query_params.get('enrollment_id')

    if not enrollment_id:
        logger.warning("Enrollment ID not provided in query parameters.")
        return Response({"error": "Enrollment ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        student = Student.objects.get(enrollment_id=enrollment_id)
        serializer = StudentSearchSerializer(student)
        #logger.info(f"Student found with enrollment_id: {enrollment_id}")
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        logger.warning(f"No student found for enrollment_id: {enrollment_id}")
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_by_student_name(request):
    """
    Search for students by their name using a case-insensitive substring match.
    """
    name_query = request.query_params.get('name', '').strip()

    if not name_query:
        logger.warning("No name provided in student name search.")
        return Response({"error": "Name query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

    students = Student.objects.filter(name__icontains=name_query)

    if students.exists():
        serializer = StudentSearchSerializer(students, many=True)
        #logger.info(f"Found {students.count()} student(s) matching: '{name_query}'")
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        #logger.info(f"No students found for name search: '{name_query}'")
        return Response({"message": "No students found."}, status=status.HTTP_404_NOT_FOUND)
  


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def create_course(request):
    """
    POST: Create a new course for a given university.
    GET: Retrieve all courses or filter by university name.
    """
    university_name = (
        request.data.get('university_name') if request.method == 'POST'
        else request.query_params.get('university_name')
    )

    if request.method == 'POST':
        course_name = request.data.get('name')

        if not university_name or not course_name:
            return Response(
                {'error': 'Both university_name and name are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            university = University.objects.get(university_name=university_name)
        except University.DoesNotExist:
            return Response({'error': 'University not found.'}, status=status.HTTP_404_NOT_FOUND)

        if Course.objects.filter(university=university, name=course_name).exists():
            return Response(
                {'error': 'Course with this name already exists for the specified university.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CourseSerializerTwo(data=request.data)
        if serializer.is_valid():
            serializer.save(university=university, created_by=request.user, modified_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # GET Request
    if university_name:
        try:
            university = University.objects.get(university_name=university_name)
            courses = Course.objects.filter(university=university)
        except University.DoesNotExist:
            return Response({'error': 'University not found.'}, status=status.HTTP_404_NOT_FOUND)
    else:
        courses = Course.objects.all()

    serializer = CourseSerializerTwo(courses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
  
  
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_stream(request):
    """
    Create a new stream for a given course and university.
    """
    university_name = request.data.get('university_name')
    course_name = request.data.get('course_name')
    stream_name = request.data.get('stream_name')
    year = request.data.get('year') or datetime.now().year
    sem = request.data.get('sem')

    # Validate required fields
    if not university_name or not course_name or not stream_name:
        return Response(
            {'error': 'university_name, course_name, and stream_name are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not sem:
        return Response({'error': 'Semester is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate University
    try:
        university = University.objects.get(university_name=university_name)
    except University.DoesNotExist:
        return Response({'error': 'University not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Validate Course
    try:
        course = Course.objects.get(name=course_name, university=university)
    except Course.DoesNotExist:
        return Response(
            {'error': 'Course not found for the specified university.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check for existing Stream
    if Stream.objects.filter(course=course, name=stream_name).exists():
        return Response(
            {'error': 'Stream with this name already exists for the specified course.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Prepare data for serializer
    data = request.data.copy()
    data['name'] = stream_name
    data['year'] = year

    serializer = StreamSerializer(data=data)
    if serializer.is_valid():
        serializer.save(course=course, created_by=request.user, modified_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
  
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_sub_stream(request):
    """
    Create a new substream for a specific stream, course, and university.
    """
    university_name = request.data.get('university_name')
    course_name = request.data.get('course_name')
    stream_name = request.data.get('stream_name')
    substream_name = request.data.get('substream_name')

    # Validate required fields
    missing_fields = []
    if not university_name: missing_fields.append('university_name')
    if not course_name: missing_fields.append('course_name')
    if not stream_name: missing_fields.append('stream_name')
    if not substream_name: missing_fields.append('substream_name')

    if missing_fields:
        return Response(
            {'error': f"The following fields are required: {', '.join(missing_fields)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        university = University.objects.get(university_name=university_name)
    except University.DoesNotExist:
        return Response({'error': 'University not found.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        course = Course.objects.get(name=course_name, university=university)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found for the specified university.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        stream = Stream.objects.get(name=stream_name, course=course)
    except Stream.DoesNotExist:
        return Response({'error': 'Stream not found for the specified course.'}, status=status.HTTP_404_NOT_FOUND)

    if SubStream.objects.filter(stream=stream, name=substream_name).exists():
        return Response(
            {'error': 'SubStream with this name already exists for the specified stream.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    data = request.data.copy()
    data['name'] = substream_name

    serializer = SubStreamSerializer(data=data)
    if serializer.is_valid():
        serializer.save(stream=stream)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_course_details(request, student_id):
    """
    Retrieve a student's course details including university, course, stream, substream, and enrollment details.
    """
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        logger.error(f"Student with ID {student_id} not found.")
        return Response({"error": f"Student with ID {student_id} not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        enrollment = Enrolled.objects.get(student=student)
    except Enrolled.DoesNotExist:
        logger.error(f"Enrollment not found for student ID {student_id}.")
        return Response({"error": "Enrollment details not found for the specified student."}, status=status.HTTP_404_NOT_FOUND)

    try:
        data = {
            "university_name": enrollment.course.university.university_name if enrollment.course and enrollment.course.university else None,
            "course_name": enrollment.course.name if enrollment.course else None,
            "stream_name": enrollment.stream.name if enrollment.stream else None,
            "substream_name": enrollment.substream.name if enrollment.substream else None,
            "study_pattern": enrollment.course_pattern or "",
            "session": enrollment.session or "",
            "semester": enrollment.current_semyear or "",
            "course_duration": enrollment.stream.sem if enrollment.stream else "",
        }

        return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Unexpected error while processing student ID {student_id}: {str(e)}")
        return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_student_course_details(request, student_id):
    """
    Update all fields for a student's course details.
    Requires all fields in the request data.
    """
    #logger.info("Update Student Course Details API called for student ID: %s with data: %s", student_id, request.data)

    # Validate if the student has an enrollment
    try:
        enrollment = Enrolled.objects.select_related(
            'course__university', 'stream', 'substream'
        ).get(student_id=student_id)
    except Enrolled.DoesNotExist:
        logger.error("Enrollment details not found for student ID: %s", student_id)
        return Response({"error": "Enrollment details not found for the specified student."}, status=status.HTTP_404_NOT_FOUND)

    # Extract and validate the input data
    required_fields = [
        "university_name", "course_name", "stream_name", "substream_name", 
        "study_pattern", "session", "semister", "course_duration"
    ]
    missing_fields = [field for field in required_fields if field not in request.data]
    
    if missing_fields:
        logger.error("Missing required fields: %s", missing_fields)
        return Response({"error": f"Missing required fields: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)

    data = request.data

    # Validate university
    try:
        university = University.objects.get(university_name=data["university_name"])
    except University.DoesNotExist:
        logger.error("University '%s' not found.", data["university_name"])
        return Response({"error": "University not found."}, status=status.HTTP_404_NOT_FOUND)

    # Validate course
    try:
        course = Course.objects.get(name=data["course_name"], university=university)
    except Course.DoesNotExist:
        logger.error("Course '%s' not found for university '%s'.", data["course_name"], data["university_name"])
        return Response({"error": "Course not found for the specified university."}, status=status.HTTP_404_NOT_FOUND)

    # Validate stream
    try:
        stream = Stream.objects.get(name=data["stream_name"], course=course)
    except Stream.DoesNotExist:
        logger.error("Stream '%s' not found for course '%s'.", data["stream_name"], data["course_name"])
        return Response({"error": "Stream not found for the specified course."}, status=status.HTTP_404_NOT_FOUND)

    # Validate substream (mandatory)
    if not data["substream_name"]:
        logger.error("Substream name is required.")
        return Response({"error": "Substream name is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        substream = SubStream.objects.get(name=data["substream_name"], stream=stream)
    except SubStream.DoesNotExist:
        logger.error("Substream '%s' not found for stream '%s'.", data["substream_name"], data["stream_name"])
        return Response({"error": "Substream not found for the specified stream."}, status=status.HTTP_404_NOT_FOUND)

    # Update enrollment details
    enrollment.course = course
    enrollment.stream = stream
    enrollment.substream = substream
    enrollment.course_pattern = data["study_pattern"]
    enrollment.session = data["session"]
    enrollment.current_semyear = data["semister"]
    enrollment.stream.sem = data["course_duration"]  # Assuming this updates `course_duration` dynamically

    enrollment.save()

    #logger.info("Enrollment updated successfully for student ID: %s", student_id)

    # Prepare response data
    response_data = {
        "university_name": university.university_name,
        "course_name": course.name,
        "stream_name": stream.name,
        "substream_name": substream.name if substream else None,
        "study_pattern": enrollment.course_pattern,
        "session": enrollment.session,
        "semister": enrollment.current_semyear,
        "course_duration": enrollment.stream.sem,
    }

    return Response(response_data, status=status.HTTP_200_OK)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def universities_with_courses(request):
#     try:
#         # Fetch all universities
#         universities = University.objects.all()

#         # Manually match courses based on university_id
#         result = {}
#         for university in universities:
#             # Fetch courses with id, name, and year for the current university
#             courses = Course.objects.filter(university_id=university.id).values('id', 'name', 'year')

#             # Format the course data as a list of dictionaries
#             formatted_courses = []
#             for course in courses:
#                 formatted_courses.append({
#                     "id": course['id'],
#                     "name":course['name'],
#                     "year": course['year']
#                 })
            
#             # Add to the result dictionary
#             result[university.university_name] = formatted_courses

#         #logger.info("Fetched universities and their courses successfully. Total universities: %d", len(universities))
#         return Response(result, status=status.HTTP_200_OK)
    
#     except Exception as e:
#         logger.error("Error fetching universities and courses. Exception: %s", str(e))
#         return Response({"message": "An error occurred while fetching data."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_course(request, course_id):
    try:
        # Fetch the course to update
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            logger.error("Update failed: Course with ID %d not found.", course_id)
            return Response({"message": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get data from the request
        data = request.data
        course_name = data.get('name', None)
        course_year = data.get('year', None)

        # Validate input
        if not course_name or not course_year:
            logger.warning("Invalid input for updating course ID %d. Data received: %s", course_id, data)
            return Response(
                {"message": "Both 'name' and 'year' fields are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update fields
        course.name = course_name
        course.year = course_year
        course.save()

        #logger.info("Course updated successfully. ID: %d, Name: %s, Year: %s", course_id, course_name, course_year)
        return Response(
            {
                "message": "Course updated successfully.",
                "course": {
                    "id": course.id,
                    "name": course.name,
                    "year": course.year
                }
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        logger.error("Error updating course ID %d. Exception: %s", course_id, str(e))
        return Response({"message": "An error occurred while updating the course."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stream_by_course_two(request, course_id):
    #logger.info("Request to fetch streams for course ID %d received.", course_id)
    
    try:
        # Fetch the course object
        course = Course.objects.get(id=course_id)
        
        # Fetch streams related to this course
        streams = Stream.objects.filter(course=course)
        
        # Prepare the response data
        stream_list = []
        for stream in streams:
            stream_data = {
                "stream_name": stream.name,
                "semester": stream.sem,
                "year": stream.year
            }
            stream_list.append(stream_data)

        #logger.info("Successfully fetched %d streams for course '%s' (ID: %d).", len(stream_list), course.name, course_id)
        
        return Response({"course_name": course.name, "streams": stream_list}, status=status.HTTP_200_OK)

    except Course.DoesNotExist:
        logger.error("Stream fetch failed: Course with ID %d not found.", course_id)
        return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error("Error fetching streams for course ID %d. Exception: %s", course_id, str(e))
        return Response({"error": "Unable to fetch streams."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_streams_by_course(request, course_id):
    #logger.info("Request to update streams for course ID %d received.", course_id)
    
    try:
        # Validate if course exists
        course = Course.objects.get(id=course_id)
        data = request.data

        if not isinstance(data, list):
            logger.warning("Invalid request format for updating streams. Expected a list, got: %s", type(data))
            return Response({"error": "Request data must be a list of streams."}, status=status.HTTP_400_BAD_REQUEST)

        updated_streams = []
        for stream_data in data:
            stream_id = stream_data.get('id')
            stream_name = stream_data.get('name')
            year = stream_data.get('year')

            if not stream_id:
                logger.error("Stream ID is missing in the update request for course ID %d.", course_id)
                return Response({"error": "Stream ID is required for updates."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Fetch the stream
                stream = Stream.objects.get(id=stream_id, course=course)

                # Update the fields
                if stream_name is not None:
                    stream.name = stream_name
                if year is not None:
                    stream.year = year
        
                stream.save()
                #logger.info("Stream updated: ID %d, Name '%s'", stream.id, stream.name)
                
                updated_streams.append({
                    "id": stream.id,
                    "name": stream.name,
                    "sem": stream.sem,
                    "year": stream.year,
                })

            except Stream.DoesNotExist:
                logger.error("Stream update failed: Stream ID %d not found for course '%s' (ID: %d).", stream_id, course.name, course_id)
                return Response({"error": f"Stream with ID {stream_id} not found for course {course.name}."}, status=status.HTTP_404_NOT_FOUND)

        #logger.info("Successfully updated %d streams for course '%s' (ID: %d).", len(updated_streams), course.name, course_id)
        return Response({
            "message": "Streams updated successfully.",
            "course_name": course.name,
            "updated_streams": updated_streams
        }, status=status.HTTP_200_OK)

    except Course.DoesNotExist:
        logger.error("Stream update failed: Course ID %d not found.", course_id)
        return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error("Error updating streams for course ID %d. Exception: %s", course_id, str(e))
        return Response({"error": "Unable to update streams."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_substreams_by_stream(request, stream_id):
    """
    Update single or multiple substreams associated with a specific stream.
    """
    #logger.info("Request to update substreams for stream ID %d received.", stream_id)
    
    try:
        # Validate if the stream exists
        stream = Stream.objects.get(id=stream_id)
        data = request.data

        if not isinstance(data, list):
            logger.warning("Invalid request format for updating substreams. Expected a list, got: %s", type(data))
            return Response({"error": "Request data must be a list of substreams."}, status=status.HTTP_400_BAD_REQUEST)

        updated_substreams = []
        for substream_data in data:
            substream_id = substream_data.get('id')
            substream_name = substream_data.get('name')

            if not substream_id:
                logger.error("Substream ID is missing in the update request for stream ID %d.", stream_id)
                return Response({"error": "Substream ID is required for updates."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Fetch the substream
                substream = SubStream.objects.get(id=substream_id, stream=stream)

                # Update the name
                if substream_name:
                    substream.name = substream_name
                    substream.save()

                #logger.info("Substream updated: ID %d, Name '%s'", substream.id, substream.name)
                updated_substreams.append({
                    "id": substream.id,
                    "name": substream.name,
                    "stream_id": substream.stream.id,
                })

            except SubStream.DoesNotExist:
                logger.error(
                    "Substream update failed: Substream ID %d not found for stream '%s' (ID: %d).",
                    substream_id,
                    stream.name,
                    stream_id
                )
                return Response(
                    {"error": f"SubStream with ID {substream_id} not found for stream {stream.name}."},
                    status=status.HTTP_404_NOT_FOUND
                )

        #logger.info("Successfully updated %d substreams for stream '%s' (ID: %d).",len(updated_substreams),stream.name,stream_id)
        return Response({
            "message": "Substreams updated successfully.",
            "stream_name": stream.name,
            "updated_substreams": updated_substreams
        }, status=status.HTTP_200_OK)

    except Stream.DoesNotExist:
        logger.error("Substream update failed: Stream ID %d not found.", stream_id)
        return Response({"error": "Stream not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error("Error updating substreams for stream ID %d. Exception: %s", stream_id, str(e))
        return Response({"error": "Unable to update substreams."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    
@api_view(['GET'])  # Specify that this view only accepts GET requests
@permission_classes([IsAuthenticated])
def get_sem_year_by_stream(request):
    course_id = request.GET.get('course')  # Use request.GET for query parameters
    university_id= request.GET.get('university')
    stream_id = request.GET.get('stream')

    try:
        university = University.objects.get(id=university_id)
        course = Course.objects.get(id=course_id, university=university)
        streams = Stream.objects.filter(id=stream_id, course=course)

        # Prepare the response data
        response_data = []
        for stream in streams:
            response_data.append({
                'year': stream.year,
                'stream_name': stream.name,
                'sem': stream.sem
            })

        # Return the response with the desired structure
        return Response({
            'university_name': university.university_name,
            'course_name': course.name,
            'streams': response_data
        }, status=200)

    except University.DoesNotExist:
        logger.error(f"University '{university_id}' not found.")
        return Response({'error': 'University not found'}, status=404)
    except Course.DoesNotExist:
        logger.error(f"Course '{course_id}' not found for university '{university_id}'.")
        return Response({'error': 'Course not found'}, status=404)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return Response({'error': 'An error occurred'}, status=500)

    except University.DoesNotExist:
        logger.error(f"University '{university_id}' not found.")
        return Response({'error': 'University not found'}, status=404)
    except Course.DoesNotExist:
        logger.error(f"Course '{course_id}' not found for university '{university_id}'.")
        return Response({'error': 'Course not found'}, status=404)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return Response({'error': 'An error occurred'}, status=500)
      
@api_view(['GET'])  # Specify that this view only accepts GET requests
@permission_classes([IsAuthenticated])
def get_sem_year_by_stream_byname(request):
    course_name = request.GET.get('course')  # Use request.GET for query parameters
    university_name = request.GET.get('university')
    stream_name = request.GET.get('stream')

    try:
        # Fetch the university by name
        university = University.objects.get(university_name=university_name)
        
        # Fetch the course by name and its associated university
        course = Course.objects.get(name=course_name, university=university)
        
        # Fetch the streams related to the course and with the given stream name
        streams = Stream.objects.filter(name=stream_name, course=course)

        # Prepare the response data
        response_data = []
        for stream in streams:
            response_data.append({
                'year': stream.year,
                'stream_name': stream.name,
                'sem': stream.sem
            })

        # Return the response with the desired structure
        return Response({
            'university_name': university.university_name,
            'course_name': course.name,
            'streams': response_data
        }, status=200)

    except University.DoesNotExist:
        logger.error(f"University '{university_name}' not found.")
        return Response({'error': 'University not found'}, status=404)
    except Course.DoesNotExist:
        logger.error(f"Course '{course_name}' not found for university '{university_name}'.")
        return Response({'error': 'Course not found'}, status=404)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return Response({'error': 'An error occurred'}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_fee_recipt_option(request):
    try:
        data = FeeReceiptOptions.objects.filter(status=True)
        serializer = FeeReceiptOptionsSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
              status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def bank_names_list_create(request):
    if request.method == 'GET':
        bank_names = BankNames.objects.filter(status=True)
        serializer = BankNamesSerializer(bank_names, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = BankNamesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def payment_modes_list_create(request):
    if request.method == 'GET':
        payment_modes = PaymentModes.objects.filter(status=True)
        serializer = PaymentModesSerializer(payment_modes, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PaymentModesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_quick_registered_students(request):
    # Fetch all students who are quick registered
    students = Student.objects.filter(is_quick_register=True, is_cancelled=False,is_approve=False,is_pending=False).order_by('-id')
    serializer = Student_Quick_RegisteredSerializer(students, many=True)
    return Response(serializer.data)  
  
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_pending_verification_students(request):
    # Fetch all students who are quick registered
    students = Student.objects.filter(is_quick_register=True, is_cancelled=False,is_pending=True).order_by('-id')
    serializer = Student_Quick_RegisteredSerializer(students, many=True)
    return Response(serializer.data)  

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_student(request, student_id):
    try:
        # Fetch the student by ID
        student = Student.objects.get(id=student_id)
        
        # Delete the student
        student.delete()
        
        return Response({"message": "Student deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Student.DoesNotExist:
        # If the student doesn't exist, return an error
        return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

#added by ankit on 18-08-2025 for jobapplication profile
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def student_registration(request):
    # if not request.user.is_superuser:
    #     return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    try:
        with transaction.atomic():  # <<< ADDED
            # Extract fields
            name = data.get('name')
            email = data.get('email')
            mobile = data.get('mobile_number')
            alternate_mobile = data.get('alternate_number')
            alternate_email = data.get('alternate_email')
            father_name = data.get('father_name')
            mother_name = data.get('mother_name')
            dob = data.get('dob')
            gender = data.get('gender')
            category = data.get('category')
            address = data.get('address')
            alternateaddress = data.get('alternateaddress')
            nationality = data.get('nationality')
            pincode = data.get('pincode')
            registration_number = data.get('registration_number')
            student_image = request.FILES.get('image')

            university_id = data.get('university')
            course_id = data.get('course')
            stream_id = data.get('stream')
            substream_id = data.get('substream')
            studypattern = data.get('studypattern', '').capitalize()
            semyear = data.get('semyear')
            session_val = data.get('session')  # renamed to avoid shadowing later
            entry_mode = data.get('entry_mode')

            country_id = data.get('country')
            state_id = data.get('state')
            city_id = data.get('city')

            # Validate uniqueness (Student)
            if Student.objects.filter(mobile=mobile).exists():
                return Response({"error": "Mobile number already registered."}, status=status.HTTP_400_BAD_REQUEST)
            if Student.objects.filter(email=email).exists():
                return Response({"error": "Email already registered."}, status=status.HTTP_400_BAD_REQUEST)

            # Foreign key validation
            try:
                university = University.objects.get(id=university_id)
                course = Course.objects.get(id=course_id, university=university)
                stream = Stream.objects.get(id=stream_id, course=course)
                print('substream_idsubstream_id11',substream_id)

                substream = SubStream.objects.get(id=substream_id, stream=stream) if substream_id else None
                print('substream_idsubstream_id',substream_id)

                country = Countries.objects.get(id=country_id)
                state = States.objects.get(id=state_id, country_id=country_id)
                city = Cities.objects.get(id=city_id, state_id=state_id)
            except (University.DoesNotExist, Course.DoesNotExist, Stream.DoesNotExist,
                    SubStream.DoesNotExist, Countries.DoesNotExist,
                    States.DoesNotExist, Cities.DoesNotExist) as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # Generate enrollment/registration IDs
            latest = Student.objects.order_by("-id").first()
            enrollment_id = int(latest.enrollment_id) + 1 if latest else 50000
            registration_id = int(latest.registration_id) + 1 if latest else 250000

            # <<< ADDED: Create or update the User (student + jobseeker)
            user, created_user = User.objects.get_or_create(
                email=str(email).strip().lower(),
                defaults={
                    "mobile": mobile,
                    "is_student": True,
                    "is_jobseeker": True,  # requires this field on User model
                    "password": make_password(mobile or "changeme"),
                },
            )
            if not created_user:
                updates = []
                if not getattr(user, "is_student", False):
                    user.is_student = True
                    updates.append("is_student")
                if not getattr(user, "is_jobseeker", False):
                    user.is_jobseeker = True
                    updates.append("is_jobseeker")
                if not user.mobile and mobile:
                    user.mobile = mobile
                    updates.append("mobile")
                if updates:
                    user.save(update_fields=updates)

            # Save Student (via serializer, same payload as before)
            student_data = {
                "name": name, "email": email, "mobile": mobile, "father_name": father_name,
                "mother_name": mother_name, "alternate_mobile1": alternate_mobile,
                "alternateemail": alternate_email, "enrollment_id": enrollment_id,
                "registration_id": registration_id, "dateofbirth": dob, "gender": gender,
                "category": category, "address": address, "alternateaddress": alternateaddress,
                "nationality": nationality, "pincode": pincode, "image": student_image,
                "university": university.id, "country": country.id, "state": state.id,
                "city": city.id, "verified": True, "is_enrolled": True,
                "created_by": request.user.id,
                "is_quick_register":False
            }
            student_serializer = StudentSerializer(data=student_data)
            if not student_serializer.is_valid():
                return Response({"error": "Validation failed", "details": student_serializer.errors}, status=400)
            student = student_serializer.save()

            # <<< ADDED: if Student has a user FK, link it
            if hasattr(student, "user_id") and not student.user_id:
                student.user = user
                student.save(update_fields=["user"])

            # Save Enrollment
            total_semyear = int(stream.sem) * (2 if studypattern == "Semester" else 1)
            enrolled_data = {
                "student": student.id, "course": course.id, "stream": stream.id,
                "substream": substream.id if substream else None,
                "course_pattern": studypattern, "session": session_val,
                "entry_mode": entry_mode, "total_semyear": total_semyear,
                "current_semyear": semyear
            }
            enrolled_serializer = EnrolledSerializer(data=enrolled_data)
            if not enrolled_serializer.is_valid():
                return Response({"error": "Enrollment failed", "details": enrolled_serializer.errors}, status=400)
            enrolled_serializer.save()

            # Save Additional Enrollment Info
            additional_data = {
                "student": student.id,
                "counselor_name": data.get("counselor_name"),
                "university_enrollment_id": data.get("university_enrollment_number"),
                "reference_name": data.get("reference_name")
            }
            add_serializer = AdditionalEnrollmentDetailsSerializer(data=additional_data)
            if not add_serializer.is_valid():
                return Response({"error": "Additional Enrollment Failed", "details": add_serializer.errors}, status=400)
            add_serializer.save()

            # Qualifications (unchanged)
            others = []
            for key in data.keys():
                if key.startswith("qualifications[others]") and key.endswith("[year]"):
                    try:
                        idx = key.split("[")[2].split("]")[0]
                        file_key = f"qualifications[others][{idx}][file]"
                        file_path = default_storage.save(
                            f"University_Documents/{request.FILES[file_key].name}",
                            request.FILES[file_key]
                        ) if file_key in request.FILES else None
                        others.append({
                            "year": data.get(f"qualifications[others][{idx}][year]"),
                            "board": data.get(f"qualifications[others][{idx}][board]"),
                            "doctype": data.get(f"qualifications[others][{idx}][doctype]"),
                            "file_path": file_path
                        })
                    except Exception as ex:
                        logger.error("Error in other qualifications: %s", ex)

            qualification_data = {
                "student": student.id,
                "secondary_year": data.get("qualifications[secondary_year]"),
                "secondary_board": data.get("qualifications[secondary_board]"),
                "secondary_percentage": data.get("qualifications[secondary_percentage]"),
                "sr_year": data.get("qualifications[sr_year]"),
                "sr_board": data.get("qualifications[sr_board]"),
                "sr_percentage": data.get("qualifications[sr_percentage]"),
                "under_year": data.get("qualifications[under_year]"),
                "under_board": data.get("qualifications[under_board]"),
                "under_percentage": data.get("qualifications[under_percentage]"),
                "post_year": data.get("qualifications[post_year]"),
                "post_board": data.get("qualifications[post_board]"),
                "post_percentage": data.get("qualifications[post_percentage]"),
                "mphil_year": data.get("qualifications[mphil_year]"),
                "mphil_board": data.get("qualifications[mphil_board]"),
                "mphil_percentage": data.get("qualifications[mphil_percentage]"),
                "secondary_document": request.FILES.get("qualifications[secondary_document]"),
                "sr_document": request.FILES.get("qualifications[sr_document]"),
                "under_document": request.FILES.get("qualifications[under_document]"),
                "post_document": request.FILES.get("qualifications[post_document]"),
                "mphil_document": request.FILES.get("qualifications[mphil_document]"),
                "others": others
            }
            qualification_serializer = QualificationSerializer(data=qualification_data)
            if not qualification_serializer.is_valid():
                return Response({"error": "Qualification failed", "details": qualification_serializer.errors}, status=400)
            qualification_serializer.save()

            # Personal Documents (unchanged)
            index = 0
            documents = []
            while f'documents[{index}][document]' in data:
                doc_data = {
                    "document": data.get(f'documents[{index}][document]'),
                    "document_name": data.get(f'documents[{index}][document_name]'),
                    "document_ID_no": data.get(f'documents[{index}][document_ID_no]'),
                    "document_image_front": request.FILES.get(f'documents[{index}][document_image_front]'),
                    "document_image_back": request.FILES.get(f'documents[{index}][document_image_back]')
                }
                doc_serializer = StudentDocumentsSerializer(data=doc_data)
                if doc_serializer.is_valid():
                    validated = {**doc_serializer.validated_data, "student": student}
                    documents.append(StudentDocuments(**validated))
                else:
                    return Response({"error": "Invalid Document", "details": doc_serializer.errors}, status=400)
                index += 1

            if documents:
                StudentDocuments.objects.bulk_create(documents)

            # Assign Fees (unchanged)
            fees_model = SemesterFees if studypattern == "Semester" else YearFees
            fees = fees_model.objects.filter(stream=stream, substream=substream)
            for fee in fees:
                StudentFees.objects.create(
                    student=student, stream=stream, substream=substream,
                    studypattern=studypattern,
                    tutionfees=fee.tutionfees, examinationfees=fee.examinationfees,
                    totalfees=fee.totalfees, sem=fee.sem if studypattern == "Semester" else fee.year
                )

            # Save Payment (unchanged except using session_val)
            try:
                latest_receipt = PaymentReciept.objects.latest("id")
                last_id = int(latest_receipt.transactionID.replace("TXT445FE", "")) if latest_receipt else 100
            except PaymentReciept.DoesNotExist:
                last_id = 100

            transaction_id = f"TXT445FE{last_id + 1}"
            payment_mode = data.get("payment_mode")
            fee_type = data.get("fee_reciept_type")
            other_type = data.get("other_data")
            receipt_type = other_type if fee_type == "Others" else fee_type
            total_fees = data.get('totalFees')
            paid = float(data.get("paidamount") or 0) 
            cheque_no = data.get("cheque_no")
            bank_name = data.get("bank_name")
            other_bank = data.get("other_bank")
            remarks = data.get("remarks")
            transaction_date = data.get("transaction_date")

            pending = float(total_fees) - paid
            advance = abs(pending) if pending < 0 else 0
            pending = pending if pending > 0 else 0
            payment_type = "Full Payment" if pending == 0 else "Part Payment"
            bank_used = other_bank if bank_name == "Others" else bank_name
            payment_status = "Not Realised" if payment_mode == "Cheque" else "Realised"
            semyear_value = "1" if studypattern == "Full Course" else semyear
            uncleared_amount = paid if payment_mode == "Cheque" else None

            PaymentReciept.objects.create(
                student=student, payment_for="Course Fees",
                payment_categories="New", payment_type=payment_type,
                fee_reciept_type=receipt_type, transaction_date=transaction_date,
                cheque_no=cheque_no, bank_name=bank_used, semyearfees=total_fees,
                paidamount=paid,  # Save the paid amount
                pendingamount=pending, advanceamount=advance,
                transactionID=transaction_id, paymentmode=payment_mode,
                remarks=remarks, session=session_val, semyear=semyear_value,
                uncleared_amount=uncleared_amount, status=payment_status
            )

            # <<< ADDED: Create JobSeekerProfile (work_status=student, city name or "")
            profile_defaults = {
                "work_status": "student",
                "city": (city.name if getattr(city, "name", None) else ""),
                "resume": None,
            }
            JobSeekerProfile.objects.get_or_create(user=user, defaults=profile_defaults)

            return Response({"message": "Student registered successfully."}, status=201)

    except Exception:
        logger.error("Unexpected error: %s", traceback.format_exc())
        return Response({"error": "An unexpected error occurred."}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sem_fees(request):
    try:
        stream_id = request.query_params.get('stream_id')
        substream_id = request.query_params.get('substream_id')

        if not stream_id:
            return Response({"error": "Stream ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        stream = get_object_or_404(Stream, id=stream_id)

        # Build queryset based on whether substream is specified
        if substream_id:
            substream = get_object_or_404(SubStream, id=substream_id, stream=stream)
            fees_qs = SemesterFees.objects.filter(stream=stream, substream=substream)
        else:
            # generic (no-substream) records
            fees_qs = SemesterFees.objects.filter(stream=stream, substream__isnull=True)

        semester_fees = fees_qs.values(
            'sem', 'tutionfees', 'examinationfees', 'bookfees',
            'resittingfees', 'entrancefees', 'extrafees', 'discount', 'totalfees'
        ).order_by('sem')  # neat ordering

        response_data = [
            {
                "sem": fee["sem"],
                "fees_details": {
                    "tutionfees": fee["tutionfees"],
                    "examinationfees": fee["examinationfees"],
                    "bookfees": fee["bookfees"],
                    "resittingfees": fee["resittingfees"],
                    "entrancefees": fee["entrancefees"],
                    "extrafees": fee["extrafees"],
                    "discount": fee["discount"],
                    "totalfees": fee["totalfees"],
                },
            }
            for fee in semester_fees
        ]

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception("Internal server error in get_sem_fees")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_year_fees(request):
    try:
        stream_id = request.query_params.get('stream_id')
        substream_id = request.query_params.get('substream_id')

        if not stream_id:
            return Response({"error": "Stream ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        stream = get_object_or_404(Stream, id=stream_id)

        substream = None
        if substream_id:
            substream = get_object_or_404(SubStream, id=substream_id, stream=stream)

        year_fees = YearFees.objects.filter(
            stream=stream, substream=substream
        ).values('year', 'tutionfees', 'examinationfees', 'bookfees', 
                 'resittingfees', 'entrancefees', 'extrafees', 'discount', 'totalfees')

        response_data = [
            {
                "year": fee["year"],
                "fees_details": {
                    "tutionfees": fee["tutionfees"],
                    "examinationfees": fee["examinationfees"],
                    "bookfees": fee["bookfees"],
                    "resittingfees": fee["resittingfees"],
                    "entrancefees": fee["entrancefees"],
                    "extrafees": fee["extrafees"],
                    "discount": fee["discount"],
                    "totalfees": fee["totalfees"]
                }
            }
            for fee in year_fees
        ]

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_courses_by_university_with_id(request):
    """
    GET /api/courses-with-id/?university_id=<id>

    Returns:
    {
      "university_id": 1,
      "university_name": "Global Tech University",
      "courses": [
        {"course_id": 10, "name": "Mechanical Engg"},
        ...
      ]
    }
    """
    university_id = request.query_params.get('university_id')
    user_email = getattr(request.user, "email", None)

    if not university_id:
        logger.warning("courses-with-id | missing university_id | user=%s", user_email)
        return Response({"error": "Parameter 'university_id' is required."},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        university = University.objects.get(id=university_id)
    except University.DoesNotExist:
        # logger.info("courses-with-id | university not found | id=%s | user=%s", university_id, user_email)
        return Response({"error": f"University with id '{university_id}' not found."},
                        status=status.HTTP_404_NOT_FOUND)

    courses = Course.objects.filter(university=university).only("id", "name").order_by("name")
    payload = {
        "university_id": university.id,
        "university_name": university.university_name,
        "courses": [{"course_id": c.id, "name": c.name} for c in courses]
    }

    logger.info("courses-with-id | ok | university_id=%s | count=%s | user=%s",
                university_id, len(payload["courses"]), user_email)
    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stream_by_course_with_id(request):
    """
    GET /api/streams-with-id/?course_id=<id>

    Returns:
    {
      "course_id": 1,
      "course_name": "Mechanical Engg",
      "streams": [
        {"stream_id": 1, "stream_name": "Machine", "semester": "2", "year": 2025},
        ...
      ]
    }
    """
    course_id = request.query_params.get('course_id')
    user_email = getattr(request.user, "email", None)

    if not course_id:
        logger.warning("streams-with-id | missing course_id | user=%s", user_email)
        return Response({"error": "Parameter 'course_id' is required."},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        # include university via select_related only if you want to return it as well
        course = Course.objects.select_related("university").get(id=course_id)
    except Course.DoesNotExist:
        # logger.info("streams-with-id | course not found | id=%s | user=%s", course_id, user_email)
        return Response({"error": f"Course with id '{course_id}' not found."},
                        status=status.HTTP_404_NOT_FOUND)

    streams = Stream.objects.filter(course=course).only("id", "name", "sem", "year").order_by("name")
    payload = {
        "course_id": course.id,
        "course_name": course.name,
        # If you also want to include university details, uncomment:
        # "university_id": course.university_id,
        # "university_name": course.university.university_name if course.university_id else "",
        "streams": [
            {
                "stream_id": s.id,
                "stream_name": s.name,
                "semester": s.sem,
                "year": s.year,
            }
            for s in streams
        ]
    }

    # logger.info("streams-with-id | ok | course_id=%s | count=%s | user=%s",
    #             course_id, len(payload["streams"]), user_email)
    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_substreams_by_stream_with_id(request):
    """
    GET /api/substreams-with-id/?stream_id=<id>

    Returns:
    {
      "stream_id": 7,
      "stream_name": "Machine",
      "substreams": [
        {"substream_id": 11, "substream_name": "Thermo"},
        ...
      ]
    }
    """
    stream_id = request.query_params.get('stream_id')
    user_email = getattr(request.user, "email", None)

    if not stream_id:
        logger.warning("substreams-with-id | missing stream_id | user=%s", user_email)
        return Response({"error": "Parameter 'stream_id' is required."},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        stream = Stream.objects.select_related("course", "course__university").get(id=stream_id)
    except Stream.DoesNotExist:
        # logger.info("substreams-with-id | stream not found | id=%s | user=%s", stream_id, user_email)
        return Response({"error": f"Stream with id '{stream_id}' not found."},
                        status=status.HTTP_404_NOT_FOUND)

    substreams = SubStream.objects.filter(stream=stream).only("id", "name").order_by("name")
    payload = {
        "stream_id": stream.id,
        "stream_name": stream.name,
        # Optional context (frontend can ignore these):
        # "course_id": stream.course_id,
        # "course_name": stream.course.name if stream.course_id else "",
        # "university_id": stream.course.university_id if stream.course_id else None,
        # "university_name": stream.course.university.university_name if stream.course_id else "",
        "substreams": [
            {"substream_id": ss.id, "substream_name": ss.name}
            for ss in substreams
        ]
    }

    # logger.info("substreams-with-id | ok | stream_id=%s | count=%s | user=%s",
    #             stream_id, len(payload["substreams"]), user_email)
    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_country(request):
    try:
        from .models import Countries  # ✅ Make sure this matches your actual model
        data = Countries.objects.all()
        serializer = CountrySerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in get_country: {str(e)}")
        return Response(
            {"error": "An internal server error occurred."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_states(request):
    try:
        country_input = request.query_params.get('country_id')

        if not country_input:
            return Response(
                {"error": "country_id is required as a query parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        from .models import Countries  

        if country_input.isdigit():
            data = States.objects.filter(country_id=int(country_input))
        else:
            country = Countries.objects.filter(name__iexact=country_input.strip()).first()
            if not country:
                return Response({"error": f"No country found with name '{country_input}'"}, status=404)
            data = States.objects.filter(country_id=country.id)

        serializer = StateSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in get_states: {str(e)}")
        return Response({"error": "An internal server error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cities(request):
    try:
        state_input = request.query_params.get('state_id')

        if not state_input:
            return Response(
                {"error": "state_id is required as a query parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        from .models import States  # Ensure States model is imported

        if state_input.isdigit():
            data = Cities.objects.filter(state_id=int(state_input))
        else:
            state = States.objects.filter(name__iexact=state_input.strip()).first()
            if not state:
                return Response({"error": f"No state found with name '{state_input}'"}, status=404)
            data = Cities.objects.filter(state_id=state.id)

        serializer = CitySerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in get_cities: {str(e)}")
        return Response({"error": "An internal server error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_student_details(request, enrollment_id):
#     if not enrollment_id:
#         logger.error("Missing required parameter: enrollment_id in request URL")
#         return Response(
#             {"error": "Missing required parameter: enrollment_id"},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     try:
#         student = Student.objects.get(enrollment_id=enrollment_id)

#         # === STUDENT DATA ===
#         student_data = {
#             "id": student.id,
#             "name": student.name,
#             "father_name": student.father_name,
#             "mother_name": student.mother_name,
#             "dateofbirth": student.dateofbirth,
#             "country": student.country.name if student.country else None,
#             "state": student.state.name if student.state else None,
#             "city": student.city.name if student.city else None,
#             "country_id": student.country.id if student.country else None,
#             "state_id": student.state.id if student.state else None,
#             "city_id": student.city.id if student.city else None,
#             "image": student.image.url if student.image else None,
#             "mobile": student.mobile,
#             "nationality": student.nationality,
#             "pincode": student.pincode,
#             "alternate_mobile1": student.alternate_mobile1,
#             "email": student.email,
#             "alternateemail": student.alternateemail,
#             "gender": student.gender,
#             "category": student.category,
#             "address": student.address,
#             "alternateaddress": student.alternateaddress,
#             "student_remarks": student.student_remarks,
#             "registration_id": student.registration_id,
#             "enrollment_id": student.enrollment_id,
#             "university": student.university.university_name if student.university else None,
#             "university_id": student.university.id if student.university else None,
#         }

#         # === ENROLLMENT DATA ===
#         enrollment = Enrolled.objects.filter(student=student).first()
#         enrollment_data = {
#             "course": enrollment.course.name if enrollment and enrollment.course else None,
#             "stream": enrollment.stream.name if enrollment and enrollment.stream else None,
#             "substream": enrollment.substream.name if enrollment and enrollment.substream else None,
#             "course_id": enrollment.course.id if enrollment and enrollment.course else None,
#             "stream_id": enrollment.stream.id if enrollment and enrollment.stream else None,
#             "substream_id": enrollment.substream.id if enrollment and enrollment.substream else None,
#             "studypattern": enrollment.course_pattern if enrollment else None,
#             "session": enrollment.session if enrollment else None,
#             "entry_mode": enrollment.entry_mode if enrollment else None,
#             "total_semyear": enrollment.total_semyear if enrollment else None,
#             "semyear": enrollment.current_semyear if enrollment else None,
#         } if enrollment else {}

#         # === ADDITIONAL ENROLLMENT DETAILS ===
#         additional_details = AdditionalEnrollmentDetails.objects.filter(student=student).first()
#         additional_details_data = {
#             "enrolled_by":additional_details.enrolled_by if additional_details else None,
#             "counselor_name": additional_details.counselor_name if additional_details else None,
#             "reference_name": additional_details.reference_name if additional_details else None,
#             "university_enroll_number": additional_details.university_enrollment_id if additional_details else None,
#         }

#         # === DOCUMENTS ===
#         student_documents = StudentDocuments.objects.filter(student=student)
#         student_documents_data = StudentDocumentsSerializerGET(student_documents, many=True).data

#         # === QUALIFICATION ===
#         qualifications = Qualification.objects.filter(student=student).first()
#         qualification_data = QualificationSerializer(qualifications).data if qualifications else None

#         # === PAYMENT RECEIPT ===
#         latest_payment = PaymentReciept.objects.filter(student=student).last()
#         due_amount = None
#         payment_data = {}

#         if latest_payment:
#             try:
#                 semyearfees = float(latest_payment.semyearfees) if latest_payment.semyearfees else 0.0
#                 paidamount = float(latest_payment.paidamount) if latest_payment.paidamount else 0.0
#                 due_amount = semyearfees - paidamount

#                 payment_data = {
#                     "Exam_Fee": latest_payment.payment_for,
#                     "transaction_date": latest_payment.transaction_date,
#                     "total_fees": latest_payment.semyearfees,
#                     "Due": due_amount,
#                     "cheque_no": latest_payment.cheque_no,
#                     "bank_name": latest_payment.bank_name,
#                     "paymentmode": latest_payment.paymentmode,
#                     "remarks": latest_payment.remarks,
#                     "paidamount": latest_payment.paidamount,
#                     "fee_recipt_type": latest_payment.fee_reciept_type,
#                     "payment_transaction_id":latest_payment.payment_transactionID
#                 }

#             except Exception as pe:
#                 logger.warning(f"Could not calculate payment due for enrollment_id {enrollment_id}: {pe}")
#                 payment_data = {}

#         # === FINAL RESPONSE ===
#         response_data = {
#             **student_data,
#             **enrollment_data,
#             **additional_details_data,
#             "documents": student_documents_data,
#             "qualifications": qualification_data,
#             "payment_details": payment_data,
#         }

#         return Response(response_data, status=status.HTTP_200_OK)

#     except Student.DoesNotExist:
#         logger.error(f"Student with enrollment_id {enrollment_id} not found.")
#         return Response(
#             {"error": "Student not found."},
#             status=status.HTTP_404_NOT_FOUND
#         )

#     except Exception as e:
#         logger.error(f"Unexpected error while retrieving student details for enrollment_id {enrollment_id}: {str(e)}")
#         return Response(
#             {"error": "An unexpected error occurred while retrieving student details."},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_details(request, enrollment_id):
    if not enrollment_id:
        logger.error("Missing required parameter: enrollment_id in request URL")
        return Response(
            {"error": "Missing required parameter: enrollment_id"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        student = Student.objects.get(enrollment_id=enrollment_id)
        print("is_approve",student.is_approve)
        # === STUDENT DATA ===
        student_data = {
            "id": student.id,
            "name": student.name,
            "father_name": student.father_name,
            "mother_name": student.mother_name,
            "dateofbirth": student.dateofbirth,
            "country": student.country.name if student.country else None,
            "state": student.state.name if student.state else None,
            "city": student.city.name if student.city else None,
            "country_id": student.country.id if student.country else None,
            "state_id": student.state.id if student.state else None,
            "city_id": student.city.id if student.city else None,
            "image": student.image.url if student.image else None,
            "mobile": student.mobile,
            "nationality": student.nationality,
            "pincode": student.pincode,
            "alternate_mobile1": student.alternate_mobile1,
            "email": student.email,
            "alternateemail": student.alternateemail,
            "gender": student.gender,
            "category": student.category,
            "address": student.address,
            "alternateaddress": student.alternateaddress,
            "student_remarks": student.student_remarks,
            "registration_id": student.registration_id,
            "enrollment_id": student.enrollment_id,
            "university": student.university.university_name if student.university else None,
            "university_id": student.university.id if student.university else None,
            "is_pending":student.is_pending,
            "is_approve":student.is_approve
      
        }

        # === ENROLLMENT DATA ===
        enrollment = Enrolled.objects.filter(student=student).first()
        enrollment_data = {
            "course": enrollment.course.name if enrollment and enrollment.course else None,
            "stream": enrollment.stream.name if enrollment and enrollment.stream else None,
            "substream": enrollment.substream.name if enrollment and enrollment.substream else None,
            "course_id": enrollment.course.id if enrollment and enrollment.course else None,
            "stream_id": enrollment.stream.id if enrollment and enrollment.stream else None,
            "substream_id": enrollment.substream.id if enrollment and enrollment.substream else None,
            "studypattern": enrollment.course_pattern if enrollment else None,
            "session": enrollment.session if enrollment else None,
            "entry_mode": enrollment.entry_mode if enrollment else None,
            "total_semyear": enrollment.total_semyear if enrollment else None,
            "semyear": enrollment.current_semyear if enrollment else None,
        } if enrollment else {}

        # === ADDITIONAL ENROLLMENT DETAILS ===
        additional_details = AdditionalEnrollmentDetails.objects.filter(student=student).first()
        additional_details_data = {
            "enrolled_by":additional_details.enrolled_by if additional_details else None,
            "counselor_name": additional_details.counselor_name if additional_details else None,
            "reference_name": additional_details.reference_name if additional_details else None,
            "university_enroll_number": additional_details.university_enrollment_id if additional_details else None,
        }

        # === DOCUMENTS ===
        student_documents = StudentDocuments.objects.filter(student=student)
        student_documents_data = StudentDocumentsSerializerGET(student_documents, many=True).data

        # === QUALIFICATION ===
        qualifications = Qualification.objects.filter(student=student).first()
        qualification_data = QualificationSerializer(qualifications).data if qualifications else None

        # === ALL PAYMENT RECEIPTS FOR CURRENT SEMYEAR ===
        current_semyear = enrollment.current_semyear if enrollment else None
        payment_reciepts = PaymentReciept.objects.filter(student=student, semyear=current_semyear).order_by('transaction_date')
        payment_data = []
        
        total_fees = 0.0
        cumulative_paid = 0.0
        
        for payment in payment_reciepts:
            try:
                semyearfees = float(payment.semyearfees) if payment.semyearfees else 0.0
                paidamount = float(payment.paidamount) if payment.paidamount else 0.0
                
                # Set total fees from first receipt (should be same for all)
                if total_fees == 0:
                    total_fees = semyearfees
                
                # Calculate cumulative paid amount up to this transaction
                cumulative_paid += paidamount
                
                # Calculate due amount after this transaction
                due_after_this_transaction = total_fees - cumulative_paid
                
                payment_data.append({
                    "Exam_Fee": payment.payment_for,
                    "transaction_date": payment.transaction_date,
                    "total_fees": payment.semyearfees,
                    "paidamount": payment.paidamount,
                    "Due": due_after_this_transaction,  # Due amount after this specific transaction
                    "cheque_no": payment.cheque_no,
                    "bank_name": payment.bank_name,
                    "paymentmode": payment.paymentmode,
                    "remarks": payment.remarks,
                    "fee_recipt_type": payment.fee_reciept_type,
                    "payment_transaction_id": payment.payment_transactionID,
                    "cumulative_paid_until_now": cumulative_paid  # Total paid including this transaction
                })

            except Exception as pe:
                logger.warning(f"Could not calculate payment due for payment ID {payment.id}: {pe}")
                continue

        # === FINAL RESPONSE ===
        response_data = {
            **student_data,
            **enrollment_data,
            **additional_details_data,
            "documents": student_documents_data,
            "qualifications": qualification_data,
            "payment_details": payment_data,
            "payment_summary": {
                "total_fees": total_fees,
                "total_paid_amount": cumulative_paid,
                "current_due_amount": total_fees - cumulative_paid
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Student.DoesNotExist:
        logger.error(f"Student with enrollment_id {enrollment_id} not found.")
        return Response(
            {"error": "Student not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    except Exception as e:
        logger.error(f"Unexpected error while retrieving student details for enrollment_id {enrollment_id}: {str(e)}")
        return Response(
            {"error": "An unexpected error occurred while retrieving student details."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


#29-10-2025
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_details(request, enrollment_id):
    if not enrollment_id:
        logger.error("Missing required parameter: enrollment_id in request URL")
        return Response(
            {"error": "Missing required parameter: enrollment_id"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        student = Student.objects.get(enrollment_id=enrollment_id)

        # === STUDENT DATA ===
        student_data = {
            "id": student.id,
            "name": student.name,
            "father_name": student.father_name,
            "mother_name": student.mother_name,
            "dateofbirth": student.dateofbirth,
            "country": student.country.name if student.country else None,
            "state": student.state.name if student.state else None,
            "city": student.city.name if student.city else None,
            "country_id": student.country.id if student.country else None,
            "state_id": student.state.id if student.state else None,
            "city_id": student.city.id if student.city else None,
            "image": student.image.url if student.image else None,
            "mobile": student.mobile,
            "nationality": student.nationality,
            "pincode": student.pincode,
            "alternate_mobile1": student.alternate_mobile1,
            "email": student.email,
            "alternateemail": student.alternateemail,
            "gender": student.gender,
            "category": student.category,
            "address": student.address,
            "alternateaddress": student.alternateaddress,
            "student_remarks": student.student_remarks,
            "registration_id": student.registration_id,
            "enrollment_id": student.enrollment_id,
            "university": student.university.university_name if student.university else None,
            "university_id": student.university.id if student.university else None,
            "is_pending": student.is_pending,
            "is_approve": student.is_approve,
        }

        # === PENDING VERIFICATION DATA ===
        pending_verification = PendingVerification.objects.filter(student=student).first()
        pending_verification_data = {
            "student_university_enrollment": getattr(pending_verification, "student_university_enrollment", None) if pending_verification else None,
            "student_university_user_id": getattr(pending_verification, "student_university_user_id", None) if pending_verification else None,
            "student_university_password": getattr(pending_verification, "student_university_password", None) if pending_verification else None,
        }

        # === ENROLLMENT DATA ===
        enrollment = Enrolled.objects.filter(student=student).first()
        enrollment_data = {}
        if enrollment:
            enrollment_data = {
                "course": enrollment.course.name if enrollment.course else None,
                "stream": enrollment.stream.name if enrollment.stream else None,
                "substream": enrollment.substream.name if enrollment.substream else None,
                "course_id": enrollment.course.id if enrollment.course else None,
                "stream_id": enrollment.stream.id if enrollment.stream else None,
                "substream_id": enrollment.substream.id if enrollment.substream else None,
                "studypattern": enrollment.course_pattern,
                "session": enrollment.session,
                "entry_mode": enrollment.entry_mode,
                "total_semyear": enrollment.total_semyear,
                "semyear": enrollment.current_semyear,
            }

        # === ADDITIONAL ENROLLMENT DETAILS ===
        additional_details = AdditionalEnrollmentDetails.objects.filter(student=student).first()
        additional_details_data = {
            "enrolled_by": getattr(additional_details, "enrolled_by", None) if additional_details else None,
            "counselor_name": getattr(additional_details, "counselor_name", None) if additional_details else None,
            "reference_name": getattr(additional_details, "reference_name", None) if additional_details else None,
            "university_enroll_number": getattr(additional_details, "university_enrollment_id", None) if additional_details else None,
        }

        # === DOCUMENTS ===
        student_documents = StudentDocuments.objects.filter(student=student).order_by("id")
        student_documents_data = StudentDocumentsSerializerGET(student_documents, many=True).data

        # === QUALIFICATION ===
        qualifications = Qualification.objects.filter(student=student).first()
        qualification_data = QualificationSerializer(qualifications).data if qualifications else None

        # === PAYMENT RECEIPTS (current semyear if available) ===
        current_semyear = getattr(enrollment, "current_semyear", None) if enrollment else None

        receipts_qs = PaymentReciept.objects.filter(student=student)
        if current_semyear not in (None, "", "null"):
            receipts_qs = receipts_qs.filter(semyear=str(current_semyear))

        # Order by id ASC to ensure chronological calculation (transaction_date is a CharField)
        receipts_qs = receipts_qs.order_by("id")

        # Serialize base rows (includes id & normalized keys)
        serialized_rows = PaymentReceiptSerializer(receipts_qs, many=True).data

        # Compute running values
        total_fees = 0.0
        cumulative_paid = 0.0
        enriched_rows = []

        for sr, pr in zip(serialized_rows, receipts_qs):
            try:
                # Numeric conversions
                row_total_fees = float(sr["total_fees"] or 0)
                row_paid = float(sr["paid_amount"] or 0)

                # Determine the total fees to use (first non-zero wins)
                if total_fees == 0.0 and row_total_fees > 0:
                    total_fees = row_total_fees

                cumulative_paid += row_paid
                due_after_this = total_fees - cumulative_paid

                # Match your UI keys (and keep normalized keys)
                enriched_rows.append({
                    **sr,
                    "id": pr.id,  # Ensure ID is included
                    "Exam_Fee": pr.payment_for,  # you were showing "Course Fees" / label
                    "cumulative_paid_until_now": cumulative_paid,
                    "Due": due_after_this,
                    "total_fees": row_total_fees,  # Ensure this is included
                    "paid_amount": row_paid,  # Ensure this is included
                    "fee_receipt_type": pr.fee_reciept_type or "",  # Add this field
                })
            except Exception as pe:
                logger.warning(f"Could not calculate payment due for payment ID {pr.id}: {pe}")
                # still push the raw row to avoid dropping it
                enriched_rows.append({**sr, "id": pr.id})

        payment_details = enriched_rows

        payment_summary = {
            "total_fees": total_fees,
            "total_paid_amount": cumulative_paid,
            "current_due_amount": total_fees - cumulative_paid,
        }

        # === FINAL RESPONSE ===
        response_data = {
            **student_data,
            **enrollment_data,
            **additional_details_data,
            "documents": student_documents_data,
            "qualifications": qualification_data,
            "payment_details": payment_details,  # includes id
            "payment_summary": payment_summary,
            "pending_verification": pending_verification_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Student.DoesNotExist:
        logger.error(f"Student with enrollment_id {enrollment_id} not found.")
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Unexpected error while retrieving student details for enrollment_id {enrollment_id}: {str(e)}")
        return Response({"error": "An unexpected error occurred while retrieving student details."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_student_details(request, enrollment_id):
    print('inside update student')
    """
    Update an enrolled student's complete profile by enrollment_id.
    """
    t0 = time.monotonic()
    user_email = getattr(request.user, "email", str(request.user))
    logger.info("[update_student] START user=%s enrollment_id=%s", user_email, enrollment_id)

    data = request.data
    print("Received data:", data)
    try:
        print('inside Try student')
        with transaction.atomic():
            # --- Load Student (FOR UPDATE to avoid races) ---
            try:
                student = Student.objects.select_for_update().get(enrollment_id=str(enrollment_id))
            except Student.DoesNotExist:
                logger.warning("[update_student] NOT_FOUND enrollment_id=%s", enrollment_id)
                return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

            # --- Map & update Student scalar fields ---
            student_field_map = {
                "name": "name",
                "father_name": "father_name",
                "mother_name": "mother_name",
                "dob": "dateofbirth",
                "mobile_number": "mobile",
                "alternate_number": "alternate_mobile1",
                "alternate_email": "alternateemail",
                "email": "email",
                "gender": "gender",
                "category": "category",
                "address": "address",
                "alternateaddress": "alternateaddress",
                "nationality": "nationality",
                "pincode": "pincode",
                "registration_number": "registration_number",
                "student_remarks": "student_remarks",
            }
            for in_key, model_field in student_field_map.items():
                if in_key in data and data.get(in_key) not in (None, ""):
                    setattr(student, model_field, data.get(in_key))

            # Country/State/City (optional)
            if "country" in data and data.get("country"):
                try:
                    student.country = Countries.objects.get(id=data.get("country"))
                except Countries.DoesNotExist:
                    return Response({"error": f"Country with id {data.get('country')} does not exist."}, status=400)
            if "state" in data and data.get("state"):
                try:
                    student.state = States.objects.get(id=data.get("state"))
                except States.DoesNotExist:
                    return Response({"error": f"State with id {data.get('state')} does not exist."}, status=400)
            if "city" in data and data.get("city"):
                try:
                    student.city = Cities.objects.get(id=data.get("city"))
                except Cities.DoesNotExist:
                    return Response({"error": f"City with id {data.get('city')} does not exist."}, status=400)

            # University (optional)
            if "university" in data and data.get("university"):
                try:
                    student.university = University.objects.get(id=data.get("university"))
                except University.DoesNotExist:
                    return Response({"error": f"University with id {data.get('university')} does not exist."}, status=400)

            # Image/file (optional)
            img_file = request.FILES.get("image") or data.get("image")
            if img_file:
                student.image = img_file

            student.save()
            
            # --- Pending Verification ---
            pending_verification, created = PendingVerification.objects.get_or_create(student=student)

            # Update fields if provided, otherwise set to empty/null
            if "student_university_enrollment" in data:
                enrollment_val = data.get("student_university_enrollment")
                pending_verification.student_university_enrollment = enrollment_val if enrollment_val not in (None, "") else None

            if "student_university_user_id" in data:
                user_id_val = data.get("student_university_user_id")
                pending_verification.student_university_user_id = user_id_val if user_id_val not in (None, "") else None

            if "student_university_password" in data:
                password_val = data.get("student_university_password")
                pending_verification.student_university_password = password_val if password_val not in (None, "") else None

            pending_verification.save()

            logger.info(f"[update_student] Updated pending verification for student {student.id}")

            # --- Enrollment: update or create one record ---
            enrollment = Enrolled.objects.filter(student=student).first()
            if not enrollment:
                enrollment = Enrolled(student=student)

            # Resolve related course/stream/substream when provided
            course_obj = None
            stream_obj = None
            substream_obj = None

            if data.get("course"):
                try:
                    course_obj = Course.objects.get(id=data.get("course"), university=student.university)
                except Course.DoesNotExist:
                    return Response({"error": "Course not found for the student's university."}, status=400)
                enrollment.course = course_obj

            if data.get("stream"):
                if not course_obj:
                    course_obj = enrollment.course
                if not course_obj:
                    return Response({"error": "Set course before stream."}, status=400)
                try:
                    stream_obj = Stream.objects.get(id=data.get("stream"), course=course_obj)
                except Stream.DoesNotExist:
                    return Response({"error": "Stream not found for the selected course."}, status=400)
                enrollment.stream = stream_obj

            # Substream can be null/empty => clear it
            if "substream" in data:
                sub_id = data.get("substream")
                if sub_id in (None, "", "null"):
                    enrollment.substream = None
                    substream_obj = None
                else:
                    if not stream_obj:
                        stream_obj = enrollment.stream
                    if not stream_obj:
                        return Response({"error": "Set stream before substream."}, status=400)
                    try:
                        substream_obj = SubStream.objects.get(id=sub_id, stream=stream_obj)
                    except SubStream.DoesNotExist:
                        return Response({"error": "SubStream not found for the selected stream."}, status=400)
                    enrollment.substream = substream_obj

            # Simple fields
            if "studypattern" in data and data.get("studypattern"):
                enrollment.course_pattern = str(data.get("studypattern")).capitalize()
            if "session" in data and data.get("session"):
                enrollment.session = data.get("session")
            if "entry_mode" in data and data.get("entry_mode"):
                enrollment.entry_mode = data.get("entry_mode")
            if "semyear" in data and data.get("semyear"):
                enrollment.current_semyear = data.get("semyear")

            # Compute total_semyear if we have a stream and pattern
            pattern = enrollment.course_pattern or ""
            stream_for_calc = enrollment.stream
            if stream_for_calc and pattern:
                try:
                    total = int(getattr(stream_for_calc, "sem"))
                    if pattern == "Semester":
                        total = total * 2
                    enrollment.total_semyear = str(total)
                except Exception:
                    pass

            enrollment.save()

            # --- Additional Enrollment Details ---
            add_details, _ = AdditionalEnrollmentDetails.objects.get_or_create(student=student)
            if "enrolledBy" in data:
              add_details.enrolled_by = data.get("enrolled_by") or ""
            if "counselor_name" in data:
                add_details.counselor_name = data.get("counselor_name") or ""
            if "reference_name" in data:
                add_details.reference_name = data.get("reference_name") or ""
            if "university_enroll_number" in data:
                add_details.university_enrollment_id = data.get("university_enroll_number") or ""
            if "university_enrollment_number" in data:
                add_details.university_enrollment_id = data.get("university_enrollment_number") or add_details.university_enrollment_id
            
            add_details.save()

            # --- Qualifications ---
            qual, _ = Qualification.objects.get_or_create(student=student)

            # Support nested dict (JSON) and/or FormData-style flat keys
            q = data.get("qualifications") if isinstance(data.get("qualifications"), dict) else {}

            # Scalar fields (years/boards/percentages)
            qual_fields = [
                "secondary_year", "sr_year", "under_year", "post_year", "mphil_year",
                "secondary_board", "sr_board", "under_board", "post_board", "mphil_board",
                "secondary_percentage", "sr_percentage", "under_percentage", "post_percentage", "mphil_percentage",
            ]
            for f in qual_fields:
                if f in q and q.get(f) not in (None, ""):
                    setattr(qual, f, q.get(f))
                else:
                    flat_val = data.get(f"qualifications[{f}]")
                    if flat_val not in (None, ""):
                        setattr(qual, f, flat_val)

            # File fields (accept both nested and flat)
            file_map = {
                "secondary_document": ["qualifications[secondary_document]"],
                "sr_document": ["qualifications[sr_document]"],
                "under_document": ["qualifications[under_document]"],
                "post_document": ["qualifications[post_document]"],
                "mphil_document": ["qualifications[mphil_document]"],
            }
            for model_field, flat_keys in file_map.items():
                file_obj = None
                if model_field in q and q.get(model_field):
                    file_obj = q.get(model_field)
                if not file_obj:
                    for k in flat_keys:
                        if k in request.FILES:
                            file_obj = request.FILES[k]
                            break
                if file_obj:
                    setattr(qual, model_field, file_obj)

            # "others" (list of dicts with optional file)
            others_payload = []
            if isinstance(q.get("others"), list):
                for item in q["others"]:
                    if not isinstance(item, dict):
                        continue
                    file_obj = item.get("file")
                    file_path = None
                    if file_obj:
                        file_path = default_storage.save(f"University_Documents/{getattr(file_obj, 'name', 'other')}", file_obj)
                    others_payload.append({
                        "year": item.get("year"),
                        "board": item.get("board"),
                        "doctype": item.get("doctype"),
                        "file_path": file_path
                    })
            else:
                indices = set()
                for k in data.keys():
                    if k.startswith("qualifications[others]") and "][" in k:
                        try:
                            idx = k.split("[")[2].split("]")[0]
                            if str(idx).isdigit():
                                indices.add(int(idx))
                        except Exception:
                            pass
                for idx in sorted(list(indices)):
                    file_key = f"qualifications[others][{idx}][file]"
                    file_obj = request.FILES.get(file_key)
                    file_path = None
                    if file_obj:
                        file_path = default_storage.save(f"University_Documents/{file_obj.name}", file_obj)
                    others_payload.append({
                        "year": data.get(f"qualifications[others][{idx}][year]"),
                        "board": data.get(f"qualifications[others][{idx}][board]"),
                        "doctype": data.get(f"qualifications[others][{idx}][doctype]"),
                        "file_path": file_path
                    })

            if others_payload:
                qual.others = others_payload
            elif "others" in q and not q.get("others"):
                qual.others = []

            qual.save()

            # --- Documents (JSON or FormData indexed) ---
            docs_json = data.get("documents")
            if isinstance(docs_json, list):
                for d in docs_json:
                    if not isinstance(d, dict):
                        continue
                    doc_id = d.get("id")
                    if doc_id:
                        try:
                            doc_obj = StudentDocuments.objects.get(id=doc_id, student=student)
                        except StudentDocuments.DoesNotExist:
                            return Response({"error": f"Document with id {doc_id} not found for this student."}, status=400)
                    else:
                        doc_obj = StudentDocuments(student=student)

                    for f in ["document", "document_name", "document_ID_no"]:
                        if f in d and d.get(f) not in (None, ""):
                            setattr(doc_obj, f, d.get(f))

                    f_front = d.get("document_image_front")
                    f_back = d.get("document_image_back")
                    if f_front:
                        doc_obj.document_image_front = f_front
                    if f_back:
                        doc_obj.document_image_back = f_back

                    doc_obj.save()
            else:
                idx = 0
                while True:
                    key_base = f"documents[{idx}]"
                    if f"{key_base}[document]" not in data:
                        break
                    doc_id_val = data.get(f"{key_base}[id]")
                    if doc_id_val:
                        try:
                            doc_obj = StudentDocuments.objects.get(id=doc_id_val, student=student)
                        except StudentDocuments.DoesNotExist:
                            return Response({"error": f"Document with id {doc_id_val} not found for this student."}, status=400)
                    else:
                        doc_obj = StudentDocuments.objects.filter(
                            student=student,
                            document=data.get(f"{key_base}[document]"),
                            document_name=data.get(f"{key_base}[document_name]"),
                            document_ID_no=data.get(f"{key_base}[document_ID_no]"),
                        ).first() or StudentDocuments(student=student)

                    doc_obj.document = data.get(f"{key_base}[document]") or doc_obj.document
                    doc_obj.document_name = data.get(f"{key_base}[document_name]") or doc_obj.document_name
                    doc_obj.document_ID_no = data.get(f"{key_base}[document_ID_no]") or doc_obj.document_ID_no

                    f_front = request.FILES.get(f"{key_base}[document_image_front]")
                    f_back = request.FILES.get(f"{key_base}[document_image_back]")
                    if f_front:
                        doc_obj.document_image_front = f_front
                    if f_back:
                        doc_obj.document_image_back = f_back

                    doc_obj.save()
                    idx += 1

            # --- StudentFees: UPSERT (no delete) ---
            if any(k in data for k in ("studypattern", "stream", "substream")):
                effective_pattern = (enrollment.course_pattern or "").strip()
                base_stream = enrollment.stream
                base_substream = enrollment.substream

                if effective_pattern and base_stream:
                    fees_model = SemesterFees if effective_pattern == "Semester" else YearFees
                    master_fees = fees_model.objects.filter(stream=base_stream, substream=base_substream)

                    existing = {sf.sem: sf for sf in StudentFees.objects.filter(student=student)}

                    to_create = []
                    to_update = []

                    for fee in master_fees:
                        key_sem = fee.sem if effective_pattern == "Semester" else fee.year
                        sf = existing.get(key_sem)
                        if sf:
                            changed = False
                            if sf.stream_id != base_stream.id:
                                sf.stream = base_stream
                                changed = True
                            if (sf.substream_id or None) != (base_substream.id if base_substream else None):
                                sf.substream = base_substream
                                changed = True
                            if sf.studypattern != effective_pattern:
                                sf.studypattern = effective_pattern
                                changed = True
                            if str(sf.tutionfees) != str(fee.tutionfees):
                                sf.tutionfees = fee.tutionfees
                                changed = True
                            if str(sf.examinationfees) != str(fee.examinationfees):
                                sf.examinationfees = fee.examinationfees
                                changed = True
                            if str(sf.totalfees) != str(fee.totalfees):
                                sf.totalfees = fee.totalfees
                                changed = True
                            if changed:
                                to_update.append(sf)
                        else:
                            to_create.append(
                                StudentFees(
                                    student=student,
                                    stream=base_stream,
                                    substream=base_substream,
                                    studypattern=effective_pattern,
                                    tutionfees=fee.tutionfees,
                                    examinationfees=fee.examinationfees,
                                    totalfees=fee.totalfees,
                                    sem=(fee.sem if effective_pattern == "Semester" else fee.year),
                                )
                            )

                    if to_create:
                        StudentFees.objects.bulk_create(to_create)
                    if to_update:
                        StudentFees.objects.bulk_update(
                            to_update,
                            ["stream", "substream", "studypattern", "tutionfees", "examinationfees", "totalfees"]
                        )

            # --- PaymentReciept: Handle cumulative payment calculations ---
            payment_sections = []
            
            # Check for multiple payment sections in FormData
            idx = 0
            while True:
                fee_receipt_key = f"paymentSections[{idx}][feeReceipt]"
                if fee_receipt_key not in data:
                    break
                
                # Check if this section has any payment data
                has_payment_data = (
                    data.get(fee_receipt_key) not in (None, "") or
                    data.get(f"paymentSections[{idx}][amount]") not in (None, "", "0") or
                    data.get(f"paymentSections[{idx}][totalFees]") not in (None, "", "0")
                )
                
                if has_payment_data:
                    # Get the payment ID - this is crucial for updates
                    payment_id = data.get(f"paymentSections[{idx}][id]")
                    is_existing = data.get(f"paymentSections[{idx}][isExisting]", "false").lower() == "true"
                    
                    payment_sections.append({
                        "index": idx,
                        "id": payment_id,
                        "fee_receipt": data.get(fee_receipt_key),
                        "total_fees": float(data.get(f"paymentSections[{idx}][totalFees]") or 0),
                        "amount": float(data.get(f"paymentSections[{idx}][amount]") or 0),
                        "transaction_date": data.get(f"paymentSections[{idx}][transactionDate]"),
                        "payment_mode": data.get(f"paymentSections[{idx}][paymentMode]"),
                        "cheque_no": data.get(f"paymentSections[{idx}][chequeNo]"),
                        "bank_name": data.get(f"paymentSections[{idx}][selectedBank]"),
                        "payment_transaction_id": data.get(f"paymentSections[{idx}][paymentTransactionId]"),
                        "remarks": data.get(f"paymentSections[{idx}][remarks]"),
                        "is_existing": is_existing,
                    })
                idx += 1

            # If no indexed sections found, check for single payment data (legacy support)
            if not payment_sections:
                single_payment_fields = (
                    "paidamount", "fee_reciept_type", "payment_mode", "remarks",
                    "transaction_date", "cheque_no", "bank_name", "totalFees", "payment_transactionID"
                )
                if any(data.get(k) not in (None, "") for k in single_payment_fields):
                    has_single_payment = (
                        data.get("paidamount") not in (None, "", "0") or
                        data.get("totalFees") not in (None, "", "0")
                    )
                    if has_single_payment:
                        payment_sections.append({
                            "index": 0,
                            "id": None,
                            "fee_receipt": data.get("fee_reciept_type"),
                            "total_fees": float(data.get("totalFees") or 0),
                            "amount": float(data.get("paidamount") or 0),
                            "transaction_date": data.get("transaction_date"),
                            "payment_mode": data.get("payment_mode"),
                            "cheque_no": data.get("cheque_no"),
                            "bank_name": data.get("bank_name"),
                            "payment_transaction_id": data.get("payment_transactionID"),
                            "remarks": data.get("remarks"),
                            "is_existing": False,
                        })

            # Get all existing payment receipts for this student in chronological order
            all_existing_receipts = list(PaymentReciept.objects.filter(student=student).order_by('id'))
            existing_receipts_map = {receipt.id: receipt for receipt in all_existing_receipts}

            # Track modified receipts
            modified_receipt_ids = set()
            updated_receipts = []

            # Process ALL payment sections - including new ones
            for payment_data in payment_sections:
                try:
                    payment_id = payment_data.get("id")
                    amount = payment_data["amount"]
                    
                    # Skip if no amount
                    if amount <= 0:
                        continue
                        
                    fee_type = payment_data.get("fee_receipt")
                    other_type = data.get("other_data")
                    receipt_type = (other_type if fee_type == "Others" else fee_type) or ""
                    
                    bank_name_in = payment_data.get("bank_name")
                    other_bank = data.get("other_bank")
                    bank_used = other_bank if bank_name_in == "Others" else bank_name_in
                    payment_mode = payment_data.get("payment_mode")
                    payment_status = "Not Realised" if payment_mode == "Cheque" else "Realised"
                    semyear_value = (
                        "1" if (enrollment.course_pattern == "Full Course")
                        else (data.get("semyear") or enrollment.current_semyear)
                    )
                    uncleared_amount = str(amount) if payment_mode == "Cheque" else None

                    pr = None
                    
                    # CASE 1: Existing payment with ID - UPDATE
                    if payment_id and payment_id not in (None, "", "null"):
                        try:
                            pr = PaymentReciept.objects.get(id=payment_id, student=student)
                            logger.info(f"[update_student] Found existing receipt by ID: {pr.id}")
                            modified_receipt_ids.add(payment_id)

                            # UPDATE existing record
                            pr.payment_for = "Course Fees"
                            pr.payment_categories = "Update"
                            pr.fee_reciept_type = receipt_type
                            pr.transaction_date = payment_data.get("transaction_date")
                            pr.cheque_no = payment_data.get("cheque_no")
                            pr.bank_name = bank_used
                            pr.paidamount = str(amount)
                            pr.paymentmode = payment_mode or "Online"
                            pr.remarks = payment_data.get("remarks")
                            pr.session = enrollment.session
                            pr.semyear = str(semyear_value) if semyear_value is not None else ""
                            pr.uncleared_amount = str(uncleared_amount) if uncleared_amount is not None else None
                            pr.status = payment_status
                            pr.payment_transactionID = payment_data.get("payment_transaction_id") or None
                            
                            pr.save()
                            updated_receipts.append(pr)
                            
                            logger.info(f"[update_student] Updated payment receipt ID {pr.id}")
                            
                        except PaymentReciept.DoesNotExist:
                            logger.warning(f"[update_student] Payment receipt with ID {payment_id} not found, will create new one")
                            # Fall through to create new record
                            payment_id = None
                    
                    # CASE 2: New payment (no ID) OR existing payment not found - CREATE
                    if not pr:
                        # Check if we should create a new record
                        should_create_new = (
                            not payment_data.get("is_existing") or  # Not marked as existing
                            payment_id is None  # No ID provided
                        )
                        
                        if should_create_new and amount > 0:  # Only create if there's an amount
                            try:
                                latest_receipt = PaymentReciept.objects.latest("id")
                                last_id = int(str(latest_receipt.transactionID).replace("TXT445FE", "")) if latest_receipt else 100
                            except PaymentReciept.DoesNotExist:
                                last_id = 100
                            transaction_id = f"TXT445FE{last_id + 1}"

                            pr = PaymentReciept.objects.create(
                                student=student,
                                payment_for="Course Fees",
                                payment_categories="New Payment",
                                fee_reciept_type=receipt_type,
                                transaction_date=payment_data.get("transaction_date"),
                                cheque_no=payment_data.get("cheque_no"),
                                bank_name=bank_used,
                                paidamount=str(amount),
                                transactionID=transaction_id,
                                paymentmode=payment_mode or "Online",
                                remarks=payment_data.get("remarks"),
                                session=enrollment.session,
                                semyear=str(semyear_value) if semyear_value is not None else "",
                                uncleared_amount=str(uncleared_amount) if uncleared_amount is not None else None,
                                status=payment_status,
                                created_by=str(request.user.id),
                                payment_transactionID=payment_data.get("payment_transaction_id") or None,
                            )
                            updated_receipts.append(pr)
                            logger.info(f"[update_student] Created new payment receipt: {pr.transactionID}")
                        else:
                            logger.warning(f"[update_student] Skipping payment section - marked as existing but no valid ID: {payment_data}")
                            
                except Exception as ex:
                    logger.exception("[update_student] payment_receipt_process_failed student_id=%s section_index=%s err=%s", 
                                    student.id, payment_data.get("index"), str(ex))

            # Second pass: Recalculate ALL payment amounts in chronological order
            all_receipts_final = list(PaymentReciept.objects.filter(student=student).order_by('id'))
            
            if all_receipts_final:
                # Get total fees from the first payment section or existing receipts
                total_fees_val = payment_sections[0]['total_fees'] if payment_sections else 0
                if total_fees_val == 0 and all_receipts_final:
                    total_fees_val = float(all_receipts_final[0].semyearfees or 0)
                
                cumulative_paid = 0.0
                
                # Process all receipts in chronological order
                for receipt in all_receipts_final:
                    try:
                        current_paid = float(receipt.paidamount or 0)
                        cumulative_paid += current_paid
                        
                        # Calculate pending and advance amounts
                        pending = max(0.0, total_fees_val - cumulative_paid)
                        advance = max(0.0, cumulative_paid - total_fees_val)
                        
                        # Determine payment type
                        payment_type = "Full Payment" if pending == 0 else "Part Payment"
                        if advance > 0:
                            payment_type = "Advance Payment"
                        
                        # Update the receipt with calculated amounts
                        receipt.pendingamount = str(pending)
                        receipt.advanceamount = str(advance)
                        receipt.payment_type = payment_type
                        receipt.semyearfees = str(total_fees_val)
                        
                        receipt.save()
                        
                        logger.info(f"[update_student] Final calculation for receipt {receipt.id}: "
                                   f"Paid={current_paid}, Cumulative={cumulative_paid}, "
                                   f"Pending={pending}, Advance={advance}, Type={payment_type}")
                               
                    except Exception as ex:
                        logger.exception("[update_student] Error in final calculation for receipt %s: %s", receipt.id, str(ex))

            # --- Build response payload ---
            student_ser = StudentSerializer(student)
            enrollment_data = {
                "course": enrollment.course.name if getattr(enrollment, "course", None) else None,
                "stream": enrollment.stream.name if getattr(enrollment, "stream", None) else None,
                "substream": enrollment.substream.name if getattr(enrollment, "substream", None) else None,
                "studypattern": enrollment.course_pattern,
                "session": enrollment.session,
                "entry_mode": enrollment.entry_mode,
                "total_semyear": enrollment.total_semyear,
                "semyear": enrollment.current_semyear,
            }
            additional_details_data = {
                "counselor_name": add_details.counselor_name or None,
                "reference_name": add_details.reference_name or None,
                "university_enroll_number": add_details.university_enrollment_id or None,
                "enrolled_by": add_details.enrolled_by or None,
            }
            docs_qs = StudentDocuments.objects.filter(student=student).order_by("id")
            docs_data = StudentDocumentsSerializerGET(docs_qs, many=True).data
            qual_data = QualificationSerializer(qual).data if qual else None
            
            # Get all payment receipts for response
            payment_receipts = PaymentReciept.objects.filter(student=student).order_by("-id")
            payment_data = []
            for receipt in payment_receipts:
                payment_data.append({
                    "id": receipt.id,  # Include ID in response
                    "fee_receipt_type": receipt.fee_reciept_type,
                    "total_fees": receipt.semyearfees,
                    "paid_amount": receipt.paidamount,
                    "transaction_date": receipt.transaction_date,
                    "payment_mode": receipt.paymentmode,
                    "cheque_no": receipt.cheque_no,
                    "bank_name": receipt.bank_name,
                    "payment_transaction_id": receipt.transactionID,
                    "remarks": receipt.remarks,
                    "pending_amount": receipt.pendingamount,
                    "advance_amount": receipt.advanceamount,
                    "payment_transactionID": receipt.payment_transactionID,
                })

            dt = (time.monotonic() - t0) * 1000.0
            logger.info("[update_student] OK user=%s enrollment_id=%s ms=%.1f", user_email, enrollment_id, dt)

            return Response({
                "message": "Student details updated successfully.",
                "student": student_ser.data,
                "enrollment": enrollment_data,
                "additional_details": additional_details_data,
                "documents": docs_data,
                "qualifications": qual_data,
                "payment_details": payment_data
            }, status=status.HTTP_200_OK)

    except Course.DoesNotExist:
        return Response({"error": "Course not found."}, status=status.HTTP_400_BAD_REQUEST)
    except Stream.DoesNotExist:
        return Response({"error": "Stream not found."}, status=status.HTTP_400_BAD_REQUEST)
    except SubStream.DoesNotExist:
        return Response({"error": "SubStream not found."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        dt = (time.monotonic() - t0) * 1000.0
        logger.exception("[update_student] FAIL user=%s enrollment_id=%s ms=%.1f err=%s", user_email, enrollment_id, dt, str(e))
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def update_student_details(request, enrollment_id):

#     try:
#         student = Student.objects.get(enrollment_id=enrollment_id)
#         for field in ['name', 'father_name', 'dateofbirth', 'mobile', 'email', 'gender', 'category', 'address']:
#             if field in request.data:
#                 setattr(student, field, request.data[field])
        
#         if 'country' in request.data:
#             try:
#                 student.country = Countries.objects.get(id=request.data['country'])
#             except Countries.DoesNotExist:
#                 return Response({"error": f"Country with id {request.data['country']} does not exist."}, status=400)

#         if 'state' in request.data:
#             try:
#                 student.state = States.objects.get(id=request.data['state'])
#             except States.DoesNotExist:
#                 return Response({"error": f"State with id {request.data['state']} does not exist."}, status=400)  
#         if 'city' in request.data:
#             try:
#                 student.city = Cities.objects.get(id=request.data['city'])
#             except Cities.DoesNotExist:
#                 return Response({"error": f"City with id {request.data['city']} does not exist."}, status=400)
        
#         if 'image' in request.data:
#             student.image = request.data['image']
#         student.save()

#         # Update enrollment details
#         enrollment = Enrolled.objects.filter(student=student).first()
#         if enrollment:
#             for field, data_field in [
#                 ('course', 'course'),
#                 ('stream', 'stream'),
#                 ('substream', 'substream'),
#                 ('course_pattern', 'studypattern'),
#                 ('session', 'session'),
#                 ('entry_mode', 'entry_mode'),
#                 ('total_semyear', 'total_semyear'),
#                 ('current_semyear', 'semyear')
#             ]:
#                 if data_field in request.data:
#                     if data_field == 'course':
#                         enrollment.course = Course.objects.get(id=request.data[data_field])
#                     elif data_field == 'stream':
#                         enrollment.stream = Stream.objects.get(id=request.data[data_field])
#                     elif data_field == 'substream':
#                       substream_id = request.data[data_field]
#                       if substream_id and str(substream_id).isdigit():
#                           enrollment.substream = SubStream.objects.get(id=substream_id)
#                       else:
#                           enrollment.substream = None
#                     else:
#                         setattr(enrollment, field, request.data[data_field])
#             enrollment.save()
#         # Update or create payment receipt
#         payment_data = request.data.get('payment_details', {})
#         print(payment_data,'payment_data')
#         if payment_data:
#             latest_payment = PaymentReciept.objects.filter(student=student).last()
#             if latest_payment:
#                 for field in ['remarks', 'transaction_date', 'bank_name', 'cheque_no', 'paymentmode']:
#                     if field in payment_data:
#                         setattr(latest_payment, field, payment_data[field])
#                 latest_payment.save()
#             else:
#                 PaymentReciept.objects.create(
#                     student=student,
#                     remarks=payment_data.get('remarks'),
#                     transaction_date=payment_data.get('transaction_date'),
#                     bank_name=payment_data.get('bank_name'),
#                     cheque_no=payment_data.get('cheque_no'),
#                     paymentmode=payment_data.get('paymentmode'),
#                     transactionID=payment_data.get('transaction_id')
#                 )

#         # Update additional enrollment details
#         additional_details, created = AdditionalEnrollmentDetails.objects.get_or_create(student=student)
#         for field, data_field in [
#             ('counselor_name', 'counselor_name'),
#             ('reference_name', 'reference_name'),
#             ('university_enrollment_id', 'university_enroll_number')
#         ]:
#             if data_field in request.data:
#                 setattr(additional_details, field, request.data[data_field])
#         additional_details.save()

#         # Update or add new documents
#         documents_data = request.data.get('documents', [])
#         for document_data in documents_data:
#             document_id = document_data.get('id')
#             if document_id:
#                 try:
#                     # Update existing document using its ID
#                     document = StudentDocuments.objects.get(id=document_id, student=student)
#                     for field in ['document', 'document_name', 'document_ID_no', 'document_image_front', 'document_image_back']:
#                         if field in document_data:
#                             setattr(document, field, document_data[field])
#                     document.save()
#                 except StudentDocuments.DoesNotExist:
#                     return Response(
#                         {"error": f"Document with id {document_id} not found for this student."},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )
#             else:
#                 # Check if a document with the same attributes already exists for the student
#                 existing_document = StudentDocuments.objects.filter(
#                     student=student,
#                     document=document_data.get('document'),
#                     document_name=document_data.get('document_name'),
#                     document_ID_no=document_data.get('document_ID_no')
#                 ).first()

#                 if existing_document:
#                     # Update existing document
#                     for field in ['document_image_front', 'document_image_back']:
#                         if field in document_data:
#                             setattr(existing_document, field, document_data[field])
#                     existing_document.save()
#                 else:
#                     # Create a new document if no match is found
#                     StudentDocuments.objects.create(
#                         student=student,
#                         document=document_data.get('document'),
#                         document_name=document_data.get('document_name'),
#                         document_ID_no=document_data.get('document_ID_no'),
#                         document_image_front=document_data.get('document_image_front'),
#                         document_image_back=document_data.get('document_image_back'),
#                     )

#         # Update qualifications
#         qualifications_data = request.data.get('qualifications', {})
#         qualifications, created = Qualification.objects.get_or_create(student=student)

#         for field in [
#             'secondary_year', 'sr_year', 'under_year', 'post_year', 'mphil_year', 
#             'secondary_board', 'sr_board', 'under_board', 'post_board', 'mphil_board',
#             'secondary_percentage', 'sr_percentage', 'under_percentage', 'post_percentage', 'mphil_percentage',
#             'secondary_document', 'sr_document', 'under_document', 'post_document', 'mphil_document'
#         ]:
#             if field in qualifications_data:
#                 setattr(qualifications, field, qualifications_data[field])

#         others = qualifications_data.get('others', [])
#         qualifications.others = others if others is not None else []
#         qualifications.save()

#         # Get updated student details after the update
#         student_serializer = StudentSerializer(student)

#         # Fetch enrollment details
#         enrollment_data = {
#             "course": enrollment.course.name if enrollment.course else None,
#             "stream": enrollment.stream.name if enrollment.stream else None,
#             "substream": enrollment.substream.name if enrollment.substream else None,
#             "studypattern": enrollment.course_pattern,
#             "session": enrollment.session,
#             "entry_mode": enrollment.entry_mode,
#             "total_semyear": enrollment.total_semyear,
#             "semyear": enrollment.current_semyear,
#         }

#         # Fetch additional enrollment details
#         additional_details_data = {
#             "counselor_name": additional_details.counselor_name if additional_details else None,
#             "reference_name": additional_details.reference_name if additional_details else None,
#             "university_enroll_number": additional_details.university_enrollment_id if additional_details else None,
#         }

#         # Fetch student documents
#         student_documents = StudentDocuments.objects.filter(student=student)
#         student_documents_data = StudentDocumentsSerializerGET(student_documents, many=True).data

#         # Fetch qualifications
#         qualification_data = QualificationSerializer(qualifications).data if qualifications else None

#         # Fetch latest payment details
#         latest_payment = PaymentReciept.objects.filter(student=student).last()
#         print(latest_payment,'latest_payment')
#         payment_data = {
#             "transaction_date": latest_payment.transaction_date if latest_payment else None,
#             "cheque_no": latest_payment.cheque_no if latest_payment else None,
#             "bank_name": latest_payment.bank_name if latest_payment else None,
#             "paymentmode": latest_payment.paymentmode if latest_payment else None,
#             "remarks": latest_payment.remarks if latest_payment else None,
#         }  

#         # Prepare response data
#         response_data = {
#             'message': 'Student details updated successfully.',
#             'student': student_serializer.data,
#             'enrollment': enrollment_data,
#             'additional_details': additional_details_data,
#             'documents': student_documents_data,
#             'qualifications': qualification_data,
#             'payment_details': payment_data
#         }

#         return Response(response_data, status=status.HTTP_200_OK)

#     except Student.DoesNotExist:
#         return Response(
#             {"error": "Student not found."},
#             status=status.HTTP_404_NOT_FOUND
#         )
#     except Course.DoesNotExist:
#         return Response(
#             {"error": "Course not found."},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#     except Stream.DoesNotExist:
#         return Response(
#             {"error": "Stream not found."},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#     except SubStream.DoesNotExist:
#         return Response(
#             {"error": "SubStream not found."},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#     except Exception as e:
#         return Response(
#             {"error": str(e)},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )

# import time 
# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def update_student_details(request, enrollment_id):
#     """
#     Update an enrolled student's complete profile by enrollment_id.
#     - Student core fields (incl. image)
#     - Enrollment (course/stream/substream/pattern/session/entry_mode/semyear)
#     - Additional enrollment details
#     - Qualifications (incl. file fields) + others[]
#     - Documents (create/update; supports JSON list or FormData-style indexed keys)
#     - Rebuild StudentFees if pattern/stream/substream changed
#     - Create PaymentReciept if payment fields provided
#     """
#     t0 = time.monotonic()
#     user_email = getattr(request.user, "email", str(request.user))
#     logger.info("[update_student] START user=%s enrollment_id=%s", user_email, enrollment_id)

#     data = request.data
#     try:
#         with transaction.atomic():
#             # --- Load Student (FOR UPDATE to avoid races) ---
#             try:
#                 student = Student.objects.select_for_update().get(enrollment_id=str(enrollment_id))
#             except Student.DoesNotExist:
#                 logger.warning("[update_student] NOT_FOUND enrollment_id=%s", enrollment_id)
#                 return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

#             # --- Map & update Student scalar fields ---
#             # Accept both your old/new keys (e.g., dob -> dateofbirth, mobile_number -> mobile)
#             student_field_map = {
#                 "name": "name",
#                 "father_name": "father_name",
#                 "mother_name": "mother_name",
#                 "dob": "dateofbirth",
#                 "mobile_number": "mobile",
#                 "alternate_number": "alternate_mobile1",
#                 "alternate_email": "alternateemail",
#                 "email": "email",
#                 "gender": "gender",
#                 "category": "category",
#                 "address": "address",
#                 "alternateaddress": "alternateaddress",
#                 "nationality": "nationality",
#                 "pincode": "pincode",
#                 "registration_number": "registration_number",
#                 "student_remarks": "student_remarks",
#             }
#             for in_key, model_field in student_field_map.items():
#                 if in_key in data and data.get(in_key) not in (None, ""):
#                     setattr(student, model_field, data.get(in_key))

#             # Country/State/City (optional)
#             if "country" in data and data.get("country"):
#                 try:
#                     student.country = Countries.objects.get(id=data.get("country"))
#                 except Countries.DoesNotExist:
#                     return Response({"error": f"Country with id {data.get('country')} does not exist."}, status=400)
#             if "state" in data and data.get("state"):
#                 try:
#                     student.state = States.objects.get(id=data.get("state"))
#                 except States.DoesNotExist:
#                     return Response({"error": f"State with id {data.get('state')} does not exist."}, status=400)
#             if "city" in data and data.get("city"):
#                 try:
#                     student.city = Cities.objects.get(id=data.get("city"))
#                 except Cities.DoesNotExist:
#                     return Response({"error": f"City with id {data.get('city')} does not exist."}, status=400)

#             # University (optional)
#             if "university" in data and data.get("university"):
#                 try:
#                     student.university = University.objects.get(id=data.get("university"))
#                 except University.DoesNotExist:
#                     return Response({"error": f"University with id {data.get('university')} does not exist."}, status=400)

#             # Image/file (optional)
#             img_file = request.FILES.get("image") or data.get("image")
#             if img_file:
#                 student.image = img_file  # FileField will store the path

#             student.save()

#             # --- Enrollment: update or create one record ---
#             enrollment = Enrolled.objects.filter(student=student).first()
#             if not enrollment:
#                 enrollment = Enrolled(student=student)

#             # Resolve related course/stream/substream when provided
#             # Note: We validate course → stream → substream coherence if IDs are sent.
#             course_obj = None
#             stream_obj = None
#             substream_obj = None

#             if data.get("course"):
#                 try:
#                     course_obj = Course.objects.get(id=data.get("course"),
#                                                     university=student.university)
#                 except Course.DoesNotExist:
#                     return Response({"error": "Course not found for the student's university."}, status=400)
#                 enrollment.course = course_obj

#             if data.get("stream"):
#                 # Need course if not already resolved (either sent now or existing on enrollment)
#                 if not course_obj:
#                     course_obj = enrollment.course
#                 if not course_obj:
#                     return Response({"error": "Set course before stream."}, status=400)
#                 try:
#                     stream_obj = Stream.objects.get(id=data.get("stream"), course=course_obj)
#                 except Stream.DoesNotExist:
#                     return Response({"error": "Stream not found for the selected course."}, status=400)
#                 enrollment.stream = stream_obj

#             # Substream can be null/empty => clear it
#             if "substream" in data:
#                 sub_id = data.get("substream")
#                 if sub_id in (None, "", "null"):
#                     enrollment.substream = None
#                     substream_obj = None
#                 else:
#                     # Need stream if not already resolved
#                     if not stream_obj:
#                         stream_obj = enrollment.stream
#                     if not stream_obj:
#                         return Response({"error": "Set stream before substream."}, status=400)
#                     try:
#                         substream_obj = SubStream.objects.get(id=sub_id, stream=stream_obj)
#                     except SubStream.DoesNotExist:
#                         return Response({"error": "SubStream not found for the selected stream."}, status=400)
#                     enrollment.substream = substream_obj

#             # Simple fields
#             if "studypattern" in data and data.get("studypattern"):
#                 enrollment.course_pattern = str(data.get("studypattern")).capitalize()
#             if "session" in data and data.get("session"):
#                 enrollment.session = data.get("session")
#             if "entry_mode" in data and data.get("entry_mode"):
#                 enrollment.entry_mode = data.get("entry_mode")
#             if "semyear" in data and data.get("semyear"):
#                 enrollment.current_semyear = data.get("semyear")

#             # Compute total_semyear if we have a stream and pattern
#             pattern = enrollment.course_pattern or ""
#             stream_for_calc = enrollment.stream
#             if stream_for_calc and pattern:
#                 try:
#                     total = int(getattr(stream_for_calc, "sem"))
#                     if pattern == "Semester":
#                         total = total * 2
#                     enrollment.total_semyear = str(total)
#                 except Exception:
#                     # leave existing if cannot compute
#                     pass

#             # Preserve earlier values if nothing sent
#             enrollment.save()

#             # --- Additional Enrollment Details ---
#             add_details, _ = AdditionalEnrollmentDetails.objects.get_or_create(student=student)
#             if "counselor_name" in data:
#                 add_details.counselor_name = data.get("counselor_name") or ""
#             if "reference_name" in data:
#                 add_details.reference_name = data.get("reference_name") or ""
#             # You used 'university_enrollment_number' at create-time; accept both keys on update
#             if "university_enroll_number" in data:
#                 add_details.university_enrollment_id = data.get("university_enroll_number") or ""
#             if "university_enrollment_number" in data:
#                 add_details.university_enrollment_id = data.get("university_enrollment_number") or add_details.university_enrollment_id
#             add_details.save()

#             # --- Qualifications ---
#             qual, _ = Qualification.objects.get_or_create(student=student)

#             # Support nested dict (JSON) and/or FormData-style flat keys
#             q = data.get("qualifications") if isinstance(data.get("qualifications"), dict) else {}

#             # Scalar fields (years/boards/percentages)
#             qual_fields = [
#                 "secondary_year", "sr_year", "under_year", "post_year", "mphil_year",
#                 "secondary_board", "sr_board", "under_board", "post_board", "mphil_board",
#                 "secondary_percentage", "sr_percentage", "under_percentage", "post_percentage", "mphil_percentage",
#             ]
#             for f in qual_fields:
#                 # Prefer nested dict → fallback to top-level like qualifications[secondary_year]
#                 if f in q and q.get(f) not in (None, ""):
#                     setattr(qual, f, q.get(f))
#                 else:
#                     flat_val = data.get(f"qualifications[{f}]")
#                     if flat_val not in (None, ""):
#                         setattr(qual, f, flat_val)

#             # File fields (accept both nested and flat)
#             file_map = {
#                 "secondary_document": ["qualifications[secondary_document]"],
#                 "sr_document": ["qualifications[sr_document]"],
#                 "under_document": ["qualifications[under_document]"],
#                 "post_document": ["qualifications[post_document]"],
#                 "mphil_document": ["qualifications[mphil_document]"],
#             }
#             for model_field, flat_keys in file_map.items():
#                 file_obj = None
#                 # Nested file: qualifications: { secondary_document: <file> }
#                 if model_field in q and q.get(model_field):
#                     file_obj = q.get(model_field)
#                 # FormData-style keys
#                 if not file_obj:
#                     for k in flat_keys:
#                         if k in request.FILES:
#                             file_obj = request.FILES[k]
#                             break
#                 if file_obj:
#                     setattr(qual, model_field, file_obj)

#             # "others" (list of dicts with optional file)
#             others_payload = []
#             # Case A: nested JSON list
#             if isinstance(q.get("others"), list):
#                 for item in q["others"]:
#                     if not isinstance(item, dict):
#                         continue
#                     file_obj = item.get("file")
#                     if not file_obj:
#                         # also check request.FILES if a unique key was sent; if not, we just keep meta without file
#                         pass
#                     file_path = None
#                     if file_obj:
#                         file_path = default_storage.save(f"University_Documents/{getattr(file_obj, 'name', 'other')}", file_obj)
#                     others_payload.append({
#                         "year": item.get("year"),
#                         "board": item.get("board"),
#                         "doctype": item.get("doctype"),
#                         "file_path": file_path
#                     })
#             else:
#                 # Case B: FormData-style: qualifications[others][{i}]...
#                 # detect indices by scanning keys like qualifications[others][0][year]
#                 indices = set()
#                 for k in data.keys():
#                     if k.startswith("qualifications[others]") and "][" in k:
#                         try:
#                             idx = k.split("[")[2].split("]")[0]
#                             if str(idx).isdigit():
#                                 indices.add(int(idx))
#                         except Exception:
#                             pass
#                 for idx in sorted(list(indices)):
#                     file_key = f"qualifications[others][{idx}][file]"
#                     file_obj = request.FILES.get(file_key)
#                     file_path = None
#                     if file_obj:
#                         file_path = default_storage.save(f"University_Documents/{file_obj.name}", file_obj)
#                     others_payload.append({
#                         "year": data.get(f"qualifications[others][{idx}][year]"),
#                         "board": data.get(f"qualifications[others][{idx}][board]"),
#                         "doctype": data.get(f"qualifications[others][{idx}][doctype]"),
#                         "file_path": file_path
#                     })

#             if others_payload:
#                 qual.others = others_payload
#             elif "others" in q and not q.get("others"):
#                 # If client explicitly sends empty list, clear it
#                 qual.others = []

#             qual.save()

#             # --- Documents ---
#             # Supports:
#             #   1) JSON: documents: [{id?, document, document_name, document_ID_no, document_image_front?, document_image_back?}]
#             #   2) FormData indexed: documents[0][document], documents[0][document_image_front] (files in request.FILES)
#             # JSON list path
#             docs_json = data.get("documents")
#             if isinstance(docs_json, list):
#                 for d in docs_json:
#                     if not isinstance(d, dict):
#                         continue
#                     doc_id = d.get("id")
#                     if doc_id:
#                         try:
#                             doc_obj = StudentDocuments.objects.get(id=doc_id, student=student)
#                         except StudentDocuments.DoesNotExist:
#                             return Response({"error": f"Document with id {doc_id} not found for this student."}, status=400)
#                     else:
#                         doc_obj = StudentDocuments(student=student)

#                     # scalar fields
#                     for f in ["document", "document_name", "document_ID_no"]:
#                         if f in d and d.get(f) not in (None, ""):
#                             setattr(doc_obj, f, d.get(f))

#                     # files
#                     f_front = d.get("document_image_front")
#                     f_back = d.get("document_image_back")
#                     if f_front:
#                         doc_obj.document_image_front = f_front
#                     if f_back:
#                         doc_obj.document_image_back = f_back

#                     doc_obj.save()
#             else:
#                 # FormData indexed path
#                 idx = 0
#                 while True:
#                     key_base = f"documents[{idx}]"
#                     if f"{key_base}[document]" not in data:
#                         break
#                     doc_id_val = data.get(f"{key_base}[id]")
#                     if doc_id_val:
#                         try:
#                             doc_obj = StudentDocuments.objects.get(id=doc_id_val, student=student)
#                         except StudentDocuments.DoesNotExist:
#                             return Response({"error": f"Document with id {doc_id_val} not found for this student."}, status=400)
#                     else:
#                         # Try to upsert on (document, name, id_no), else create new
#                         doc_obj = StudentDocuments.objects.filter(
#                             student=student,
#                             document=data.get(f"{key_base}[document]"),
#                             document_name=data.get(f"{key_base}[document_name]"),
#                             document_ID_no=data.get(f"{key_base}[document_ID_no]"),
#                         ).first() or StudentDocuments(student=student)

#                     doc_obj.document = data.get(f"{key_base}[document]") or doc_obj.document
#                     doc_obj.document_name = data.get(f"{key_base}[document_name]") or doc_obj.document_name
#                     doc_obj.document_ID_no = data.get(f"{key_base}[document_ID_no]") or doc_obj.document_ID_no

#                     f_front = request.FILES.get(f"{key_base}[document_image_front]")
#                     f_back = request.FILES.get(f"{key_base}[document_image_back]")
#                     if f_front:
#                         doc_obj.document_image_front = f_front
#                     if f_back:
#                         doc_obj.document_image_back = f_back

#                     doc_obj.save()
#                     idx += 1

#             # --- StudentFees (re)build if pattern/stream/substream changed ---
#             # Detect change vs DB snapshot: easiest is to rebuild when any of these were provided in request.
#             if any(k in data for k in ("studypattern", "stream", "substream")):
#                 try:
#                     # Clean old
#                     StudentFees.objects.filter(student=student).delete()
#                     # Build new from master tables
#                     effective_pattern = (enrollment.course_pattern or "").strip()
#                     base_stream = enrollment.stream
#                     base_substream = enrollment.substream

#                     if effective_pattern and base_stream:
#                         fees_model = SemesterFees if effective_pattern == "Semester" else YearFees
#                         fees_qs = fees_model.objects.filter(stream=base_stream, substream=base_substream)
#                         create_buf = []
#                         for fee in fees_qs:
#                             create_buf.append(
#                                 StudentFees(
#                                     student=student,
#                                     stream=base_stream,
#                                     substream=base_substream,
#                                     studypattern=effective_pattern,
#                                     tutionfees=fee.tutionfees,
#                                     examinationfees=fee.examinationfees,
#                                     totalfees=fee.totalfees,
#                                     sem=(fee.sem if effective_pattern == "Semester" else fee.year),
#                                 )
#                             )
#                         if create_buf:
#                             StudentFees.objects.bulk_create(create_buf)
#                 except Exception as ex:
#                     logger.exception("[update_student] fees_rebuild_failed student_id=%s err=%s", student.id, str(ex))
#                     return Response({"error": "Failed to rebuild student fees."}, status=500)

#             # --- PaymentReciept: create a new receipt if payment fields provided ---
#             payment_fields = (
#                 "paidamount", "fee_reciept_type", "payment_mode", "remarks",
#                 "transaction_date", "cheque_no", "bank_name", "totalFees"
#             )
#             if any(data.get(k) not in (None, "") for k in payment_fields):
#                 try:
#                     try:
#                         latest_receipt = PaymentReciept.objects.latest("id")
#                         last_id = int(str(latest_receipt.transactionID).replace("TXT445FE", "")) if latest_receipt else 100
#                     except PaymentReciept.DoesNotExist:
#                         last_id = 100
#                     transaction_id = f"TXT445FE{last_id + 1}"

#                     fee_type = data.get("fee_reciept_type")
#                     other_type = data.get("other_data")
#                     receipt_type = (other_type if fee_type == "Others" else fee_type) or ""

#                     total_fees_val = float(data.get("totalFees") or 0)
#                     paid_val = float(data.get("paidamount") or 0)
#                     pending = total_fees_val - paid_val
#                     advance = abs(pending) if pending < 0 else 0
#                     pending = pending if pending > 0 else 0
#                     payment_type = "Full Payment" if pending == 0 else "Part Payment"
#                     bank_name = data.get("bank_name")
#                     other_bank = data.get("other_bank")
#                     bank_used = other_bank if bank_name == "Others" else bank_name
#                     payment_mode = data.get("payment_mode")
#                     payment_status = "Not Realised" if payment_mode == "Cheque" else "Realised"
#                     semyear_value = "1" if (enrollment.course_pattern == "Full Course") else (data.get("semyear") or enrollment.current_semyear)
#                     uncleared_amount = str(paid_val) if payment_mode == "Cheque" else None

#                     PaymentReciept.objects.create(
#                         student=student,
#                         payment_for=data.get("fee_recipt"),
#                         payment_categories="Update",
#                         payment_type=payment_type,
#                         fee_reciept_type=receipt_type,
#                         transaction_date=data.get("transaction_date"),
#                         cheque_no=data.get("cheque_no"),
#                         bank_name=bank_used,
#                         semyearfees=str(total_fees_val),
#                         paidamount=str(paid_val),
#                         pendingamount=str(pending),
#                         advanceamount=str(advance),
#                         transactionID=transaction_id,
#                         paymentmode=payment_mode or "Online",
#                         remarks=data.get("remarks"),
#                         session=enrollment.session,
#                         semyear=str(semyear_value) if semyear_value is not None else "",
#                         uncleared_amount=str(uncleared_amount) if uncleared_amount is not None else None,
#                         status=payment_status,
#                         created_by=str(request.user.id),
#                     )
#                 except Exception as ex:
#                     logger.exception("[update_student] payment_receipt_failed student_id=%s err=%s", student.id, str(ex))
#                     return Response({"error": "Failed to create payment receipt."}, status=500)

#             # --- Build response payload ---
#             student_ser = StudentSerializer(student)
#             enrollment_data = {
#                 "course": enrollment.course.name if getattr(enrollment, "course", None) else None,
#                 "stream": enrollment.stream.name if getattr(enrollment, "stream", None) else None,
#                 "substream": enrollment.substream.name if getattr(enrollment, "substream", None) else None,
#                 "studypattern": enrollment.course_pattern,
#                 "session": enrollment.session,
#                 "entry_mode": enrollment.entry_mode,
#                 "total_semyear": enrollment.total_semyear,
#                 "semyear": enrollment.current_semyear,
#             }
#             additional_details_data = {
#                 "counselor_name": add_details.counselor_name or None,
#                 "reference_name": add_details.reference_name or None,
#                 "university_enroll_number": add_details.university_enrollment_id or None,
#             }
#             docs_qs = StudentDocuments.objects.filter(student=student).order_by("id")
#             docs_data = StudentDocumentsSerializerGET(docs_qs, many=True).data
#             qual_data = QualificationSerializer(qual).data if qual else None
#             latest_payment = PaymentReciept.objects.filter(student=student).order_by("-id").first()
#             payment_data = {
#                 "transaction_date": getattr(latest_payment, "transaction_date", None),
#                 "cheque_no": getattr(latest_payment, "cheque_no", None),
#                 "bank_name": getattr(latest_payment, "bank_name", None),
#                 "paymentmode": getattr(latest_payment, "paymentmode", None),
#                 "remarks": getattr(latest_payment, "remarks", None),
#             }

#             dt = (time.monotonic() - t0) * 1000.0
#             logger.info("[update_student] OK user=%s enrollment_id=%s ms=%.1f", user_email, enrollment_id, dt)

#             return Response({
#                 "message": "Student details updated successfully.",
#                 "student": student_ser.data,
#                 "enrollment": enrollment_data,
#                 "additional_details": additional_details_data,
#                 "documents": docs_data,
#                 "qualifications": qual_data,
#                 "payment_details": payment_data
#             }, status=status.HTTP_200_OK)

#     except Course.DoesNotExist:
#         return Response({"error": "Course not found."}, status=status.HTTP_400_BAD_REQUEST)
#     except Stream.DoesNotExist:
#         return Response({"error": "Stream not found."}, status=status.HTTP_400_BAD_REQUEST)
#     except SubStream.DoesNotExist:
#         return Response({"error": "SubStream not found."}, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         dt = (time.monotonic() - t0) * 1000.0
#         logger.exception("[update_student] FAIL user=%s enrollment_id=%s ms=%.1f err=%s", user_email, enrollment_id, dt, str(e))
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


import time
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.core.files.storage import default_storage
import logging


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_student_details(request, enrollment_id):
    print('inside update student')
    """
    Update an enrolled student's complete profile by enrollment_id.
    - Student core fields (incl. image)
    - Enrollment (course/stream/substream/pattern/session/entry_mode/semyear)
    - Additional enrollment details
    - Qualifications (incl. file fields) + others[]
    - Documents (create/update; supports JSON list or FormData-style indexed keys)
    - StudentFees: UPSERT (no delete)
    - PaymentReciept: Handle multiple payment sections - only save non-empty ones
    """
    t0 = time.monotonic()
    user_email = getattr(request.user, "email", str(request.user))
    logger.info("[update_student] START user=%s enrollment_id=%s", user_email, enrollment_id)

    data = request.data
    print("Received data:", data)
    try:
        print('inside Try student')
        with transaction.atomic():
            # --- Load Student (FOR UPDATE to avoid races) ---
            try:
                student = Student.objects.select_for_update().get(enrollment_id=str(enrollment_id))
            except Student.DoesNotExist:
                logger.warning("[update_student] NOT_FOUND enrollment_id=%s", enrollment_id)
                return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

            # --- Map & update Student scalar fields ---
            student_field_map = {
                "name": "name",
                "father_name": "father_name",
                "mother_name": "mother_name",
                "dob": "dateofbirth",
                "mobile_number": "mobile",
                "alternate_number": "alternate_mobile1",
                "alternate_email": "alternateemail",
                "email": "email",
                "gender": "gender",
                "category": "category",
                "address": "address",
                "alternateaddress": "alternateaddress",
                "nationality": "nationality",
                "pincode": "pincode",
                "registration_number": "registration_number",
                "student_remarks": "student_remarks",
            }
            for in_key, model_field in student_field_map.items():
                if in_key in data and data.get(in_key) not in (None, ""):
                    setattr(student, model_field, data.get(in_key))

            # Country/State/City (optional)
            if "country" in data and data.get("country"):
                try:
                    student.country = Countries.objects.get(id=data.get("country"))
                except Countries.DoesNotExist:
                    return Response({"error": f"Country with id {data.get('country')} does not exist."}, status=400)
            if "state" in data and data.get("state"):
                try:
                    student.state = States.objects.get(id=data.get("state"))
                except States.DoesNotExist:
                    return Response({"error": f"State with id {data.get('state')} does not exist."}, status=400)
            if "city" in data and data.get("city"):
                try:
                    student.city = Cities.objects.get(id=data.get("city"))
                except Cities.DoesNotExist:
                    return Response({"error": f"City with id {data.get('city')} does not exist."}, status=400)

            # University (optional)
            if "university" in data and data.get("university"):
                try:
                    student.university = University.objects.get(id=data.get("university"))
                except University.DoesNotExist:
                    return Response({"error": f"University with id {data.get('university')} does not exist."}, status=400)

            # Image/file (optional)
            img_file = request.FILES.get("image") or data.get("image")
            if img_file:
                student.image = img_file

            student.save()

            # --- Enrollment: update or create one record ---
            enrollment = Enrolled.objects.filter(student=student).first()
            if not enrollment:
                enrollment = Enrolled(student=student)

            # Resolve related course/stream/substream when provided
            course_obj = None
            stream_obj = None
            substream_obj = None

            if data.get("course"):
                try:
                    course_obj = Course.objects.get(id=data.get("course"), university=student.university)
                except Course.DoesNotExist:
                    return Response({"error": "Course not found for the student's university."}, status=400)
                enrollment.course = course_obj

            if data.get("stream"):
                if not course_obj:
                    course_obj = enrollment.course
                if not course_obj:
                    return Response({"error": "Set course before stream."}, status=400)
                try:
                    stream_obj = Stream.objects.get(id=data.get("stream"), course=course_obj)
                except Stream.DoesNotExist:
                    return Response({"error": "Stream not found for the selected course."}, status=400)
                enrollment.stream = stream_obj

            # Substream can be null/empty => clear it
            if "substream" in data:
                sub_id = data.get("substream")
                if sub_id in (None, "", "null"):
                    enrollment.substream = None
                    substream_obj = None
                else:
                    if not stream_obj:
                        stream_obj = enrollment.stream
                    if not stream_obj:
                        return Response({"error": "Set stream before substream."}, status=400)
                    try:
                        substream_obj = SubStream.objects.get(id=sub_id, stream=stream_obj)
                    except SubStream.DoesNotExist:
                        return Response({"error": "SubStream not found for the selected stream."}, status=400)
                    enrollment.substream = substream_obj

            # Simple fields
            if "studypattern" in data and data.get("studypattern"):
                enrollment.course_pattern = str(data.get("studypattern")).capitalize()
            if "session" in data and data.get("session"):
                enrollment.session = data.get("session")
            if "entry_mode" in data and data.get("entry_mode"):
                enrollment.entry_mode = data.get("entry_mode")
            if "semyear" in data and data.get("semyear"):
                enrollment.current_semyear = data.get("semyear")

            # Compute total_semyear if we have a stream and pattern
            pattern = enrollment.course_pattern or ""
            stream_for_calc = enrollment.stream
            if stream_for_calc and pattern:
                try:
                    total = int(getattr(stream_for_calc, "sem"))
                    if pattern == "Semester":
                        total = total * 2
                    enrollment.total_semyear = str(total)
                except Exception:
                    pass

            enrollment.save()

            # --- Additional Enrollment Details ---
            add_details, _ = AdditionalEnrollmentDetails.objects.get_or_create(student=student)
            if "enrolledBy" in data:
              add_details.enrolled_by = data.get("enrolledBy") or ""
            if "counselor_name" in data:
                add_details.counselor_name = data.get("counselor_name") or ""
            if "reference_name" in data:
                add_details.reference_name = data.get("reference_name") or ""
            if "university_enroll_number" in data:
                add_details.university_enrollment_id = data.get("university_enroll_number") or ""
            if "university_enrollment_number" in data:
                add_details.university_enrollment_id = data.get("university_enrollment_number") or add_details.university_enrollment_id
            
            add_details.save()

            # --- Qualifications ---
            qual, _ = Qualification.objects.get_or_create(student=student)

            # Support nested dict (JSON) and/or FormData-style flat keys
            q = data.get("qualifications") if isinstance(data.get("qualifications"), dict) else {}

            # Scalar fields (years/boards/percentages)
            qual_fields = [
                "secondary_year", "sr_year", "under_year", "post_year", "mphil_year",
                "secondary_board", "sr_board", "under_board", "post_board", "mphil_board",
                "secondary_percentage", "sr_percentage", "under_percentage", "post_percentage", "mphil_percentage",
            ]
            for f in qual_fields:
                if f in q and q.get(f) not in (None, ""):
                    setattr(qual, f, q.get(f))
                else:
                    flat_val = data.get(f"qualifications[{f}]")
                    if flat_val not in (None, ""):
                        setattr(qual, f, flat_val)

            # File fields (accept both nested and flat)
            file_map = {
                "secondary_document": ["qualifications[secondary_document]"],
                "sr_document": ["qualifications[sr_document]"],
                "under_document": ["qualifications[under_document]"],
                "post_document": ["qualifications[post_document]"],
                "mphil_document": ["qualifications[mphil_document]"],
            }
            for model_field, flat_keys in file_map.items():
                file_obj = None
                if model_field in q and q.get(model_field):
                    file_obj = q.get(model_field)
                if not file_obj:
                    for k in flat_keys:
                        if k in request.FILES:
                            file_obj = request.FILES[k]
                            break
                if file_obj:
                    setattr(qual, model_field, file_obj)

            # "others" (list of dicts with optional file)
            others_payload = []
            if isinstance(q.get("others"), list):
                for item in q["others"]:
                    if not isinstance(item, dict):
                        continue
                    file_obj = item.get("file")
                    file_path = None
                    if file_obj:
                        file_path = default_storage.save(f"University_Documents/{getattr(file_obj, 'name', 'other')}", file_obj)
                    others_payload.append({
                        "year": item.get("year"),
                        "board": item.get("board"),
                        "doctype": item.get("doctype"),
                        "file_path": file_path
                    })
            else:
                indices = set()
                for k in data.keys():
                    if k.startswith("qualifications[others]") and "][" in k:
                        try:
                            idx = k.split("[")[2].split("]")[0]
                            if str(idx).isdigit():
                                indices.add(int(idx))
                        except Exception:
                            pass
                for idx in sorted(list(indices)):
                    file_key = f"qualifications[others][{idx}][file]"
                    file_obj = request.FILES.get(file_key)
                    file_path = None
                    if file_obj:
                        file_path = default_storage.save(f"University_Documents/{file_obj.name}", file_obj)
                    others_payload.append({
                        "year": data.get(f"qualifications[others][{idx}][year]"),
                        "board": data.get(f"qualifications[others][{idx}][board]"),
                        "doctype": data.get(f"qualifications[others][{idx}][doctype]"),
                        "file_path": file_path
                    })

            if others_payload:
                qual.others = others_payload
            elif "others" in q and not q.get("others"):
                qual.others = []

            qual.save()

            # --- Documents (JSON or FormData indexed) ---
            docs_json = data.get("documents")
            if isinstance(docs_json, list):
                for d in docs_json:
                    if not isinstance(d, dict):
                        continue
                    doc_id = d.get("id")
                    if doc_id:
                        try:
                            doc_obj = StudentDocuments.objects.get(id=doc_id, student=student)
                        except StudentDocuments.DoesNotExist:
                            return Response({"error": f"Document with id {doc_id} not found for this student."}, status=400)
                    else:
                        doc_obj = StudentDocuments(student=student)

                    for f in ["document", "document_name", "document_ID_no"]:
                        if f in d and d.get(f) not in (None, ""):
                            setattr(doc_obj, f, d.get(f))

                    f_front = d.get("document_image_front")
                    f_back = d.get("document_image_back")
                    if f_front:
                        doc_obj.document_image_front = f_front
                    if f_back:
                        doc_obj.document_image_back = f_back

                    doc_obj.save()
            else:
                idx = 0
                while True:
                    key_base = f"documents[{idx}]"
                    if f"{key_base}[document]" not in data:
                        break
                    doc_id_val = data.get(f"{key_base}[id]")
                    if doc_id_val:
                        try:
                            doc_obj = StudentDocuments.objects.get(id=doc_id_val, student=student)
                        except StudentDocuments.DoesNotExist:
                            return Response({"error": f"Document with id {doc_id_val} not found for this student."}, status=400)
                    else:
                        doc_obj = StudentDocuments.objects.filter(
                            student=student,
                            document=data.get(f"{key_base}[document]"),
                            document_name=data.get(f"{key_base}[document_name]"),
                            document_ID_no=data.get(f"{key_base}[document_ID_no]"),
                        ).first() or StudentDocuments(student=student)

                    doc_obj.document = data.get(f"{key_base}[document]") or doc_obj.document
                    doc_obj.document_name = data.get(f"{key_base}[document_name]") or doc_obj.document_name
                    doc_obj.document_ID_no = data.get(f"{key_base}[document_ID_no]") or doc_obj.document_ID_no

                    f_front = request.FILES.get(f"{key_base}[document_image_front]")
                    f_back = request.FILES.get(f"{key_base}[document_image_back]")
                    if f_front:
                        doc_obj.document_image_front = f_front
                    if f_back:
                        doc_obj.document_image_back = f_back

                    doc_obj.save()
                    idx += 1

            # --- StudentFees: UPSERT (no delete) ---
            if any(k in data for k in ("studypattern", "stream", "substream")):
                effective_pattern = (enrollment.course_pattern or "").strip()
                base_stream = enrollment.stream
                base_substream = enrollment.substream

                if effective_pattern and base_stream:
                    fees_model = SemesterFees if effective_pattern == "Semester" else YearFees
                    master_fees = fees_model.objects.filter(stream=base_stream, substream=base_substream)

                    existing = {sf.sem: sf for sf in StudentFees.objects.filter(student=student)}

                    to_create = []
                    to_update = []

                    for fee in master_fees:
                        key_sem = fee.sem if effective_pattern == "Semester" else fee.year
                        sf = existing.get(key_sem)
                        if sf:
                            changed = False
                            if sf.stream_id != base_stream.id:
                                sf.stream = base_stream
                                changed = True
                            if (sf.substream_id or None) != (base_substream.id if base_substream else None):
                                sf.substream = base_substream
                                changed = True
                            if sf.studypattern != effective_pattern:
                                sf.studypattern = effective_pattern
                                changed = True
                            if str(sf.tutionfees) != str(fee.tutionfees):
                                sf.tutionfees = fee.tutionfees
                                changed = True
                            if str(sf.examinationfees) != str(fee.examinationfees):
                                sf.examinationfees = fee.examinationfees
                                changed = True
                            if str(sf.totalfees) != str(fee.totalfees):
                                sf.totalfees = fee.totalfees
                                changed = True
                            if changed:
                                to_update.append(sf)
                        else:
                            to_create.append(
                                StudentFees(
                                    student=student,
                                    stream=base_stream,
                                    substream=base_substream,
                                    studypattern=effective_pattern,
                                    tutionfees=fee.tutionfees,
                                    examinationfees=fee.examinationfees,
                                    totalfees=fee.totalfees,
                                    sem=(fee.sem if effective_pattern == "Semester" else fee.year),
                                )
                            )

                    if to_create:
                        StudentFees.objects.bulk_create(to_create)
                    if to_update:
                        StudentFees.objects.bulk_update(
                            to_update,
                            ["stream", "substream", "studypattern", "tutionfees", "examinationfees", "totalfees"]
                        )

            # --- PaymentReciept: Handle multiple payment sections using ID-based updates ---
            payment_sections = []
            
            # Check for multiple payment sections in FormData (NEW FORMAT)
            idx = 0
            while True:
                fee_receipt_key = f"paymentSections[{idx}][feeReceipt]"
                if fee_receipt_key not in data:
                    break
                
                # Check if this payment section has meaningful data
                has_payment_data = (
                    data.get(fee_receipt_key) not in (None, "") or
                    data.get(f"paymentSections[{idx}][amount]") not in (None, "", "0") or
                    data.get(f"paymentSections[{idx}][totalFees]") not in (None, "", "0")
                )
                
                if has_payment_data:
                    payment_sections.append({
                        "index": idx,
                        "id": data.get(f"paymentSections[{idx}][id]"),  # Get the payment receipt ID
                        "fee_receipt": data.get(fee_receipt_key),
                        "total_fees": data.get(f"paymentSections[{idx}][totalFees]"),
                        "amount": data.get(f"paymentSections[{idx}][amount]"),
                        "transaction_date": data.get(f"paymentSections[{idx}][transactionDate]"),
                        "payment_mode": data.get(f"paymentSections[{idx}][paymentMode]"),
                        "cheque_no": data.get(f"paymentSections[{idx}][chequeNo]"),
                        "bank_name": data.get(f"paymentSections[{idx}][selectedBank]"),
                        "payment_transaction_id": data.get(f"paymentSections[{idx}][paymentTransactionId]"),
                        "remarks": data.get(f"paymentSections[{idx}][remarks]"),
                        "is_existing": data.get(f"paymentSections[{idx}][isExisting]", "false").lower() == "true",
                    })
                idx += 1

            # If no indexed sections found, check for single payment data (OLD FORMAT - backward compatibility)
            if not payment_sections:
                single_payment_fields = (
                    "paidamount", "fee_reciept_type", "payment_mode", "remarks",
                    "transaction_date", "cheque_no", "bank_name", "totalFees", "payment_transactionID"
                )
                if any(data.get(k) not in (None, "") for k in single_payment_fields):
                    has_single_payment = (
                        data.get("paidamount") not in (None, "", "0") or
                        data.get("totalFees") not in (None, "", "0")
                    )
                    if has_single_payment:
                        payment_sections.append({
                            "index": 0,
                            "id": None,  # No ID for old format
                            "fee_receipt": data.get("fee_reciept_type"),
                            "total_fees": data.get("totalFees"),
                            "amount": data.get("paidamount"),
                            "transaction_date": data.get("transaction_date"),
                            "payment_mode": data.get("payment_mode"),
                            "cheque_no": data.get("cheque_no"),
                            "bank_name": data.get("bank_name"),
                            "payment_transaction_id": data.get("payment_transactionID"),
                            "remarks": data.get("remarks"),
                            "is_existing": False,
                        })

            # Process each valid payment section using ID-based updates
            for payment_idx, payment_data in enumerate(payment_sections):
                try:
                    # Skip if essential data is missing
                    if not payment_data.get("amount") or payment_data.get("amount") in ("", "0"):
                        continue
                        
                    fee_type = payment_data.get("fee_receipt")
                    other_type = data.get("other_data")
                    receipt_type = (other_type if fee_type == "Others" else fee_type) or ""

                    total_fees_val = float(payment_data.get("total_fees") or 0)
                    paid_val = float(payment_data.get("amount") or 0)
                    
                    # Skip if no actual payment
                    if paid_val <= 0:
                        continue
                        
                    pending = total_fees_val - paid_val
                    advance = abs(pending) if pending < 0 else 0
                    pending = pending if pending > 0 else 0
                    payment_type = "Full Payment" if pending == 0 else "Part Payment"
                    bank_name_in = payment_data.get("bank_name")
                    other_bank = data.get("other_bank")
                    bank_used = other_bank if bank_name_in == "Others" else bank_name_in
                    payment_mode = payment_data.get("payment_mode")
                    payment_status = "Not Realised" if payment_mode == "Cheque" else "Realised"
                    semyear_value = (
                        "1" if (enrollment.course_pattern == "Full Course")
                        else (data.get("semyear") or enrollment.current_semyear)
                    )
                    uncleared_amount = str(paid_val) if payment_mode == "Cheque" else None

                    # ID-BASED UPDATE: Use the payment receipt ID to find the exact record
                    pr = None
                    
                    # Method 1: Use payment receipt ID (most reliable)
                    payment_id = payment_data.get("id")
                    if payment_id:
                        try:
                            pr = PaymentReciept.objects.get(id=payment_id, student=student)
                            logger.info(f"[update_student] Found existing receipt by ID: {pr.id} - {pr.transactionID}")
                        except PaymentReciept.DoesNotExist:
                            logger.warning(f"[update_student] Payment receipt with ID {payment_id} not found for student {student.id}")
                    
                    # Method 2: Fallback to transaction ID if no payment ID
                    if not pr and payment_data.get("payment_transaction_id"):
                        pr = PaymentReciept.objects.filter(
                            transactionID=payment_data.get("payment_transaction_id"),
                            student=student
                        ).first()
                        if pr:
                            logger.info(f"[update_student] Found existing receipt by transaction ID: {pr.transactionID}")
                    
                    # Method 3: Fallback for existing records without ID (should not happen with proper frontend)
                    if not pr and payment_data.get("is_existing"):
                        # This is a fallback - try to find by combination
                        matching_receipts = PaymentReciept.objects.filter(
                            student=student,
                            semyear=str(semyear_value) if semyear_value is not None else "",
                            fee_reciept_type=receipt_type
                        ).order_by("id")
                        
                        if matching_receipts.exists():
                            # Use the first matching receipt that hasn't been updated
                            for receipt in matching_receipts:
                                if receipt not in [p.get('updated_receipt') for p in payment_sections if 'updated_receipt' in p]:
                                    pr = receipt
                                    logger.info(f"[update_student] Found existing receipt by combination: {pr.transactionID}")
                                    break

                    if pr:
                        # UPDATE existing record
                        pr.payment_for = "Course Fees"
                        pr.payment_categories = "Update"
                        pr.payment_type = payment_type
                        pr.fee_reciept_type = receipt_type
                        pr.transaction_date = payment_data.get("transaction_date")
                        pr.cheque_no = payment_data.get("cheque_no")
                        pr.bank_name = bank_used
                        pr.semyearfees = str(total_fees_val)
                        pr.paidamount = str(paid_val)
                        pr.pendingamount = str(pending)
                        pr.advanceamount = str(advance)
                        pr.paymentmode = payment_mode or "Online"
                        pr.remarks = payment_data.get("remarks")
                        pr.session = enrollment.session
                        pr.semyear = str(semyear_value) if semyear_value is not None else ""
                        pr.uncleared_amount = str(uncleared_amount) if uncleared_amount is not None else None
                        pr.status = payment_status
                        pr.created_by = str(request.user.id)
                        pr.payment_transactionID = payment_data.get("payment_transaction_id") or None
                        pr.save()
                        
                        # Mark this receipt as updated
                        payment_data['updated_receipt'] = pr
                        
                        logger.info(f"[update_student] Updated payment receipt ID {pr.id}: {pr.transactionID} (Section {payment_idx})")
                    else:
                        # CREATE new receipt
                        try:
                            latest_receipt = PaymentReciept.objects.latest("id")
                            last_id = int(str(latest_receipt.transactionID).replace("TXT445FE", "")) if latest_receipt else 100
                        except PaymentReciept.DoesNotExist:
                            last_id = 100
                        transaction_id = f"TXT445FE{last_id + 1}"

                        pr = PaymentReciept.objects.create(
                            student=student,
                            payment_for="Course Fees",
                            payment_categories="New Payment",
                            payment_type=payment_type,
                            fee_reciept_type=receipt_type,
                            transaction_date=payment_data.get("transaction_date"),
                            cheque_no=payment_data.get("cheque_no"),
                            bank_name=bank_used,
                            semyearfees=str(total_fees_val),
                            paidamount=str(paid_val),
                            pendingamount=str(pending),
                            advanceamount=str(advance),
                            transactionID=transaction_id,
                            paymentmode=payment_mode or "Online",
                            remarks=payment_data.get("remarks"),
                            session=enrollment.session,
                            semyear=str(semyear_value) if semyear_value is not None else "",
                            uncleared_amount=str(uncleared_amount) if uncleared_amount is not None else None,
                            status=payment_status,
                            created_by=str(request.user.id),
                            
                        )
                        logger.info(f"[update_student] Created new payment receipt: {pr.transactionID} (Section {payment_idx})")
                        
                except Exception as ex:
                    logger.exception("[update_student] payment_receipt_process_failed student_id=%s section_index=%s err=%s", 
                                    student.id, payment_idx, str(ex))
                    # Continue with other payment sections even if one fails

            # --- Build response payload ---
            student_ser = StudentSerializer(student)
            enrollment_data = {
                "course": enrollment.course.name if getattr(enrollment, "course", None) else None,
                "stream": enrollment.stream.name if getattr(enrollment, "stream", None) else None,
                "substream": enrollment.substream.name if getattr(enrollment, "substream", None) else None,
                "studypattern": enrollment.course_pattern,
                "session": enrollment.session,
                "entry_mode": enrollment.entry_mode,
                "total_semyear": enrollment.total_semyear,
                "semyear": enrollment.current_semyear,
            }
            additional_details_data = {
                "counselor_name": add_details.counselor_name or None,
                "reference_name": add_details.reference_name or None,
                "university_enroll_number": add_details.university_enrollment_id or None,
                "enrolled_by": add_details.enrolled_by or None,
            }
            docs_qs = StudentDocuments.objects.filter(student=student).order_by("id")
            docs_data = StudentDocumentsSerializerGET(docs_qs, many=True).data
            qual_data = QualificationSerializer(qual).data if qual else None
            
            # Get all payment receipts for response
            payment_receipts = PaymentReciept.objects.filter(student=student).order_by("-id")
            payment_data = []
            for receipt in payment_receipts:
                payment_data.append({
                    "id": receipt.id,  # Include ID in response
                    "fee_receipt_type": receipt.fee_reciept_type,
                    "total_fees": receipt.semyearfees,
                    "paid_amount": receipt.paidamount,
                    "transaction_date": receipt.transaction_date,
                    "payment_mode": receipt.paymentmode,
                    "cheque_no": receipt.cheque_no,
                    "bank_name": receipt.bank_name,
                    "payment_transaction_id": receipt.transactionID,
                    "remarks": receipt.remarks,
                    "pending_amount": receipt.pendingamount,
                    "advance_amount": receipt.advanceamount,
                })

            dt = (time.monotonic() - t0) * 1000.0
            logger.info("[update_student] OK user=%s enrollment_id=%s ms=%.1f", user_email, enrollment_id, dt)

            return Response({
                "message": "Student details updated successfully.",
                "student": student_ser.data,
                "enrollment": enrollment_data,
                "additional_details": additional_details_data,
                "documents": docs_data,
                "qualifications": qual_data,
                "payment_details": payment_data
            }, status=status.HTTP_200_OK)

    except Course.DoesNotExist:
        return Response({"error": "Course not found."}, status=status.HTTP_400_BAD_REQUEST)
    except Stream.DoesNotExist:
        return Response({"error": "Stream not found."}, status=status.HTTP_400_BAD_REQUEST)
    except SubStream.DoesNotExist:
        return Response({"error": "SubStream not found."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        dt = (time.monotonic() - t0) * 1000.0
        logger.exception("[update_student] FAIL user=%s enrollment_id=%s ms=%.1f err=%s", user_email, enrollment_id, dt, str(e))
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#28-07-2025
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_student_details(request, enrollment_id):
    print('inside update student')
    """
    Update an enrolled student's complete profile by enrollment_id.
    - Student core fields (incl. image)
    - Enrollment (course/stream/substream/pattern/session/entry_mode/semyear)
    - Additional enrollment details
    - Qualifications (incl. file fields) + others[]
    - Documents (create/update; supports JSON list or FormData-style indexed keys)
    - StudentFees: UPSERT (no delete)
    - PaymentReciept: Handle multiple payment sections - only save non-empty ones
    """
    t0 = time.monotonic()
    user_email = getattr(request.user, "email", str(request.user))
    logger.info("[update_student] START user=%s enrollment_id=%s", user_email, enrollment_id)

    data = request.data
    print("Received data:", data)
    try:
        print('inside Try student')
        with transaction.atomic():
            # --- Load Student (FOR UPDATE to avoid races) ---
            try:
                student = Student.objects.select_for_update().get(enrollment_id=str(enrollment_id))
            except Student.DoesNotExist:
                logger.warning("[update_student] NOT_FOUND enrollment_id=%s", enrollment_id)
                return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

            # --- Map & update Student scalar fields ---
            student_field_map = {
                "name": "name",
                "father_name": "father_name",
                "mother_name": "mother_name",
                "dob": "dateofbirth",
                "mobile_number": "mobile",
                "alternate_number": "alternate_mobile1",
                "alternate_email": "alternateemail",
                "email": "email",
                "gender": "gender",
                "category": "category",
                "address": "address",
                "alternateaddress": "alternateaddress",
                "nationality": "nationality",
                "pincode": "pincode",
                "registration_number": "registration_number",
                "student_remarks": "student_remarks",
            }
            for in_key, model_field in student_field_map.items():
                if in_key in data and data.get(in_key) not in (None, ""):
                    setattr(student, model_field, data.get(in_key))

            # Country/State/City (optional)
            if "country" in data and data.get("country"):
                try:
                    student.country = Countries.objects.get(id=data.get("country"))
                except Countries.DoesNotExist:
                    return Response({"error": f"Country with id {data.get('country')} does not exist."}, status=400)
            if "state" in data and data.get("state"):
                try:
                    student.state = States.objects.get(id=data.get("state"))
                except States.DoesNotExist:
                    return Response({"error": f"State with id {data.get('state')} does not exist."}, status=400)
            if "city" in data and data.get("city"):
                try:
                    student.city = Cities.objects.get(id=data.get("city"))
                except Cities.DoesNotExist:
                    return Response({"error": f"City with id {data.get('city')} does not exist."}, status=400)

            # University (optional)
            if "university" in data and data.get("university"):
                try:
                    student.university = University.objects.get(id=data.get("university"))
                except University.DoesNotExist:
                    return Response({"error": f"University with id {data.get('university')} does not exist."}, status=400)

            # Image/file (optional)
            img_file = request.FILES.get("image") or data.get("image")
            if img_file:
                student.image = img_file

            student.save()
            
            pending_verification, created = PendingVerification.objects.get_or_create(student=student)

            # Update fields if provided, otherwise set to empty/null
            if "student_university_enrollment" in data:
                enrollment_val = data.get("student_university_enrollment")
                pending_verification.student_university_enrollment = enrollment_val if enrollment_val not in (None, "") else None

            if "student_university_user_id" in data:
                user_id_val = data.get("student_university_user_id")
                pending_verification.student_university_user_id = user_id_val if user_id_val not in (None, "") else None

            if "student_university_password" in data:
                password_val = data.get("student_university_password")
                pending_verification.student_university_password = password_val if password_val not in (None, "") else None

            pending_verification.save()

            logger.info(f"[update_student] Updated pending verification for student {student.id}")

            # --- Enrollment: update or create one record ---
            enrollment = Enrolled.objects.filter(student=student).first()
            if not enrollment:
                enrollment = Enrolled(student=student)

            # Resolve related course/stream/substream when provided
            course_obj = None
            stream_obj = None
            substream_obj = None

            if data.get("course"):
                try:
                    course_obj = Course.objects.get(id=data.get("course"), university=student.university)
                except Course.DoesNotExist:
                    return Response({"error": "Course not found for the student's university."}, status=400)
                enrollment.course = course_obj

            if data.get("stream"):
                if not course_obj:
                    course_obj = enrollment.course
                if not course_obj:
                    return Response({"error": "Set course before stream."}, status=400)
                try:
                    stream_obj = Stream.objects.get(id=data.get("stream"), course=course_obj)
                except Stream.DoesNotExist:
                    return Response({"error": "Stream not found for the selected course."}, status=400)
                enrollment.stream = stream_obj

            # Substream can be null/empty => clear it
            if "substream" in data:
                sub_id = data.get("substream")
                if sub_id in (None, "", "null"):
                    enrollment.substream = None
                    substream_obj = None
                else:
                    if not stream_obj:
                        stream_obj = enrollment.stream
                    if not stream_obj:
                        return Response({"error": "Set stream before substream."}, status=400)
                    try:
                        substream_obj = SubStream.objects.get(id=sub_id, stream=stream_obj)
                    except SubStream.DoesNotExist:
                        return Response({"error": "SubStream not found for the selected stream."}, status=400)
                    enrollment.substream = substream_obj

            # Simple fields
            if "studypattern" in data and data.get("studypattern"):
                enrollment.course_pattern = str(data.get("studypattern")).capitalize()
            if "session" in data and data.get("session"):
                enrollment.session = data.get("session")
            if "entry_mode" in data and data.get("entry_mode"):
                enrollment.entry_mode = data.get("entry_mode")
            if "semyear" in data and data.get("semyear"):
                enrollment.current_semyear = data.get("semyear")

            # Compute total_semyear if we have a stream and pattern
            pattern = enrollment.course_pattern or ""
            stream_for_calc = enrollment.stream
            if stream_for_calc and pattern:
                try:
                    total = int(getattr(stream_for_calc, "sem"))
                    if pattern == "Semester":
                        total = total * 2
                    enrollment.total_semyear = str(total)
                except Exception:
                    pass

            enrollment.save()

            # --- Additional Enrollment Details ---
            add_details, _ = AdditionalEnrollmentDetails.objects.get_or_create(student=student)
            if "enrolledBy" in data:
              add_details.enrolled_by = data.get("enrolledBy") or ""
            if "counselor_name" in data:
                add_details.counselor_name = data.get("counselor_name") or ""
            if "reference_name" in data:
                add_details.reference_name = data.get("reference_name") or ""
            if "university_enroll_number" in data:
                add_details.university_enrollment_id = data.get("university_enroll_number") or ""
            if "university_enrollment_number" in data:
                add_details.university_enrollment_id = data.get("university_enrollment_number") or add_details.university_enrollment_id
            
            add_details.save()

            # --- Qualifications ---
            qual, _ = Qualification.objects.get_or_create(student=student)

            # Support nested dict (JSON) and/or FormData-style flat keys
            q = data.get("qualifications") if isinstance(data.get("qualifications"), dict) else {}

            # Scalar fields (years/boards/percentages)
            qual_fields = [
                "secondary_year", "sr_year", "under_year", "post_year", "mphil_year",
                "secondary_board", "sr_board", "under_board", "post_board", "mphil_board",
                "secondary_percentage", "sr_percentage", "under_percentage", "post_percentage", "mphil_percentage",
            ]
            for f in qual_fields:
                if f in q and q.get(f) not in (None, ""):
                    setattr(qual, f, q.get(f))
                else:
                    flat_val = data.get(f"qualifications[{f}]")
                    if flat_val not in (None, ""):
                        setattr(qual, f, flat_val)

            # File fields (accept both nested and flat)
            file_map = {
                "secondary_document": ["qualifications[secondary_document]"],
                "sr_document": ["qualifications[sr_document]"],
                "under_document": ["qualifications[under_document]"],
                "post_document": ["qualifications[post_document]"],
                "mphil_document": ["qualifications[mphil_document]"],
            }
            for model_field, flat_keys in file_map.items():
                file_obj = None
                if model_field in q and q.get(model_field):
                    file_obj = q.get(model_field)
                if not file_obj:
                    for k in flat_keys:
                        if k in request.FILES:
                            file_obj = request.FILES[k]
                            break
                if file_obj:
                    setattr(qual, model_field, file_obj)

            # "others" (list of dicts with optional file)
            others_payload = []
            if isinstance(q.get("others"), list):
                for item in q["others"]:
                    if not isinstance(item, dict):
                        continue
                    file_obj = item.get("file")
                    file_path = None
                    if file_obj:
                        file_path = default_storage.save(f"University_Documents/{getattr(file_obj, 'name', 'other')}", file_obj)
                    others_payload.append({
                        "year": item.get("year"),
                        "board": item.get("board"),
                        "doctype": item.get("doctype"),
                        "file_path": file_path
                    })
            else:
                indices = set()
                for k in data.keys():
                    if k.startswith("qualifications[others]") and "][" in k:
                        try:
                            idx = k.split("[")[2].split("]")[0]
                            if str(idx).isdigit():
                                indices.add(int(idx))
                        except Exception:
                            pass
                for idx in sorted(list(indices)):
                    file_key = f"qualifications[others][{idx}][file]"
                    file_obj = request.FILES.get(file_key)
                    file_path = None
                    if file_obj:
                        file_path = default_storage.save(f"University_Documents/{file_obj.name}", file_obj)
                    others_payload.append({
                        "year": data.get(f"qualifications[others][{idx}][year]"),
                        "board": data.get(f"qualifications[others][{idx}][board]"),
                        "doctype": data.get(f"qualifications[others][{idx}][doctype]"),
                        "file_path": file_path
                    })

            if others_payload:
                qual.others = others_payload
            elif "others" in q and not q.get("others"):
                qual.others = []

            qual.save()

            # --- Documents (JSON or FormData indexed) ---
            docs_json = data.get("documents")
            if isinstance(docs_json, list):
                for d in docs_json:
                    if not isinstance(d, dict):
                        continue
                    doc_id = d.get("id")
                    if doc_id:
                        try:
                            doc_obj = StudentDocuments.objects.get(id=doc_id, student=student)
                        except StudentDocuments.DoesNotExist:
                            return Response({"error": f"Document with id {doc_id} not found for this student."}, status=400)
                    else:
                        doc_obj = StudentDocuments(student=student)

                    for f in ["document", "document_name", "document_ID_no"]:
                        if f in d and d.get(f) not in (None, ""):
                            setattr(doc_obj, f, d.get(f))

                    f_front = d.get("document_image_front")
                    f_back = d.get("document_image_back")
                    if f_front:
                        doc_obj.document_image_front = f_front
                    if f_back:
                        doc_obj.document_image_back = f_back

                    doc_obj.save()
            else:
                idx = 0
                while True:
                    key_base = f"documents[{idx}]"
                    if f"{key_base}[document]" not in data:
                        break
                    doc_id_val = data.get(f"{key_base}[id]")
                    if doc_id_val:
                        try:
                            doc_obj = StudentDocuments.objects.get(id=doc_id_val, student=student)
                        except StudentDocuments.DoesNotExist:
                            return Response({"error": f"Document with id {doc_id_val} not found for this student."}, status=400)
                    else:
                        doc_obj = StudentDocuments.objects.filter(
                            student=student,
                            document=data.get(f"{key_base}[document]"),
                            document_name=data.get(f"{key_base}[document_name]"),
                            document_ID_no=data.get(f"{key_base}[document_ID_no]"),
                        ).first() or StudentDocuments(student=student)

                    doc_obj.document = data.get(f"{key_base}[document]") or doc_obj.document
                    doc_obj.document_name = data.get(f"{key_base}[document_name]") or doc_obj.document_name
                    doc_obj.document_ID_no = data.get(f"{key_base}[document_ID_no]") or doc_obj.document_ID_no

                    f_front = request.FILES.get(f"{key_base}[document_image_front]")
                    f_back = request.FILES.get(f"{key_base}[document_image_back]")
                    if f_front:
                        doc_obj.document_image_front = f_front
                    if f_back:
                        doc_obj.document_image_back = f_back

                    doc_obj.save()
                    idx += 1

            # --- StudentFees: UPSERT (no delete) ---
            if any(k in data for k in ("studypattern", "stream", "substream")):
                effective_pattern = (enrollment.course_pattern or "").strip()
                base_stream = enrollment.stream
                base_substream = enrollment.substream

                if effective_pattern and base_stream:
                    fees_model = SemesterFees if effective_pattern == "Semester" else YearFees
                    master_fees = fees_model.objects.filter(stream=base_stream, substream=base_substream)

                    existing = {sf.sem: sf for sf in StudentFees.objects.filter(student=student)}

                    to_create = []
                    to_update = []

                    for fee in master_fees:
                        key_sem = fee.sem if effective_pattern == "Semester" else fee.year
                        sf = existing.get(key_sem)
                        if sf:
                            changed = False
                            if sf.stream_id != base_stream.id:
                                sf.stream = base_stream
                                changed = True
                            if (sf.substream_id or None) != (base_substream.id if base_substream else None):
                                sf.substream = base_substream
                                changed = True
                            if sf.studypattern != effective_pattern:
                                sf.studypattern = effective_pattern
                                changed = True
                            if str(sf.tutionfees) != str(fee.tutionfees):
                                sf.tutionfees = fee.tutionfees
                                changed = True
                            if str(sf.examinationfees) != str(fee.examinationfees):
                                sf.examinationfees = fee.examinationfees
                                changed = True
                            if str(sf.totalfees) != str(fee.totalfees):
                                sf.totalfees = fee.totalfees
                                changed = True
                            if changed:
                                to_update.append(sf)
                        else:
                            to_create.append(
                                StudentFees(
                                    student=student,
                                    stream=base_stream,
                                    substream=base_substream,
                                    studypattern=effective_pattern,
                                    tutionfees=fee.tutionfees,
                                    examinationfees=fee.examinationfees,
                                    totalfees=fee.totalfees,
                                    sem=(fee.sem if effective_pattern == "Semester" else fee.year),
                                )
                            )

                    if to_create:
                        StudentFees.objects.bulk_create(to_create)
                    if to_update:
                        StudentFees.objects.bulk_update(
                            to_update,
                            ["stream", "substream", "studypattern", "tutionfees", "examinationfees", "totalfees"]
                        )

            # --- PaymentReciept: Handle cumulative payment calculations ---
            payment_sections = []
            
            # Check for multiple payment sections in FormData
            idx = 0
            while True:
                fee_receipt_key = f"paymentSections[{idx}][feeReceipt]"
                if fee_receipt_key not in data:
                    break
                
                has_payment_data = (
                    data.get(fee_receipt_key) not in (None, "") or
                    data.get(f"paymentSections[{idx}][amount]") not in (None, "", "0") or
                    data.get(f"paymentSections[{idx}][totalFees]") not in (None, "", "0")
                )
                
                if has_payment_data:
                    payment_sections.append({
                        "index": idx,
                        "id": data.get(f"paymentSections[{idx}][id]"),
                        "fee_receipt": data.get(fee_receipt_key),
                        "total_fees": float(data.get(f"paymentSections[{idx}][totalFees]") or 0),
                        "amount": float(data.get(f"paymentSections[{idx}][amount]") or 0),
                        "transaction_date": data.get(f"paymentSections[{idx}][transactionDate]"),
                        "payment_mode": data.get(f"paymentSections[{idx}][paymentMode]"),
                        "cheque_no": data.get(f"paymentSections[{idx}][chequeNo]"),
                        "bank_name": data.get(f"paymentSections[{idx}][selectedBank]"),
                        "payment_transaction_id": data.get(f"paymentSections[{idx}][paymentTransactionId]"),
                        "remarks": data.get(f"paymentSections[{idx}][remarks]"),
                        "is_existing": data.get(f"paymentSections[{idx}][isExisting]", "false").lower() == "true",
                    })
                idx += 1

            # If no indexed sections found, check for single payment data
            if not payment_sections:
                single_payment_fields = (
                    "paidamount", "fee_reciept_type", "payment_mode", "remarks",
                    "transaction_date", "cheque_no", "bank_name", "totalFees", "payment_transactionID"
                )
                if any(data.get(k) not in (None, "") for k in single_payment_fields):
                    has_single_payment = (
                        data.get("paidamount") not in (None, "", "0") or
                        data.get("totalFees") not in (None, "", "0")
                    )
                    if has_single_payment:
                        payment_sections.append({
                            "index": 0,
                            "id": None,
                            "fee_receipt": data.get("fee_reciept_type"),
                            "total_fees": float(data.get("totalFees") or 0),
                            "amount": float(data.get("paidamount") or 0),
                            "transaction_date": data.get("transaction_date"),
                            "payment_mode": data.get("payment_mode"),
                            "cheque_no": data.get("cheque_no"),
                            "bank_name": data.get("bank_name"),
                            "payment_transaction_id": data.get("payment_transactionID"),
                            "remarks": data.get("remarks"),
                            "is_existing": False,
                        })

            # Get all existing payment receipts for this student in chronological order
            all_existing_receipts = list(PaymentReciept.objects.filter(student=student).order_by('id'))
            existing_receipts_map = {receipt.id: receipt for receipt in all_existing_receipts}

            # Track modified receipts
            modified_receipt_ids = set()
            updated_receipts = []

            # First pass: Process payment sections - only create new ones if they don't have IDs
            for payment_data in payment_sections:
                try:
                    payment_id = payment_data.get("id")
                    amount = payment_data["amount"]
                    
                    # Skip if no amount
                    if amount <= 0:
                        continue
                        
                    fee_type = payment_data.get("fee_receipt")
                    other_type = data.get("other_data")
                    receipt_type = (other_type if fee_type == "Others" else fee_type) or ""
                    
                    bank_name_in = payment_data.get("bank_name")
                    other_bank = data.get("other_bank")
                    bank_used = other_bank if bank_name_in == "Others" else bank_name_in
                    payment_mode = payment_data.get("payment_mode")
                    payment_status = "Not Realised" if payment_mode == "Cheque" else "Realised"
                    semyear_value = (
                        "1" if (enrollment.course_pattern == "Full Course")
                        else (data.get("semyear") or enrollment.current_semyear)
                    )
                    uncleared_amount = str(amount) if payment_mode == "Cheque" else None

                    # Find existing receipt or create new ONLY if no ID provided
                    pr = None
                    if payment_id and payment_id in existing_receipts_map:
                        # UPDATE existing record
                        pr = existing_receipts_map[payment_id]
                        logger.info(f"[update_student] Found existing receipt by ID: {pr.id}")
                        modified_receipt_ids.add(payment_id)

                        pr.payment_for = "Course Fees"
                        pr.payment_categories = "Update"
                        pr.fee_reciept_type = receipt_type
                        pr.transaction_date = payment_data.get("transaction_date")
                        pr.cheque_no = payment_data.get("cheque_no")
                        pr.bank_name = bank_used
                        pr.paidamount = str(amount)
                        pr.paymentmode = payment_mode or "Online"
                        pr.remarks = payment_data.get("remarks")
                        pr.session = enrollment.session
                        pr.semyear = str(semyear_value) if semyear_value is not None else ""
                        pr.uncleared_amount = str(uncleared_amount) if uncleared_amount is not None else None
                        pr.status = payment_status
                        pr.payment_transactionID = payment_data.get("payment_transaction_id") or None
                        
                        pr.save()
                        updated_receipts.append(pr)
                        
                        logger.info(f"[update_student] Updated payment receipt ID {pr.id}")
                        
                    elif not payment_id and not payment_data.get("is_existing"):
                        # CREATE new receipt ONLY if no ID and not marked as existing
                        try:
                            latest_receipt = PaymentReciept.objects.latest("id")
                            last_id = int(str(latest_receipt.transactionID).replace("TXT445FE", "")) if latest_receipt else 100
                        except PaymentReciept.DoesNotExist:
                            last_id = 100
                        transaction_id = f"TXT445FE{last_id + 1}"

                        pr = PaymentReciept.objects.create(
                            student=student,
                            payment_for="Course Fees",
                            payment_categories="New Payment",
                            fee_reciept_type=receipt_type,
                            transaction_date=payment_data.get("transaction_date"),
                            cheque_no=payment_data.get("cheque_no"),
                            bank_name=bank_used,
                            paidamount=str(amount),
                            transactionID=transaction_id,
                            paymentmode=payment_mode or "Online",
                            remarks=payment_data.get("remarks"),
                            session=enrollment.session,
                            semyear=str(semyear_value) if semyear_value is not None else "",
                            uncleared_amount=str(uncleared_amount) if uncleared_amount is not None else None,
                            status=payment_status,
                            created_by=str(request.user.id),
                            payment_transactionID=payment_data.get("payment_transaction_id") or None,
                        )
                        updated_receipts.append(pr)
                        logger.info(f"[update_student] Created new payment receipt: {pr.transactionID}")
                    else:
                        # Skip if payment has ID but not found in database, or marked as existing but no ID
                        logger.warning(f"[update_student] Skipping payment section - ID not found or invalid: {payment_id}")
                        
                except Exception as ex:
                    logger.exception("[update_student] payment_receipt_process_failed student_id=%s section_index=%s err=%s", 
                                    student.id, payment_data.get("index"), str(ex))

            # Second pass: Recalculate ALL payment amounts in chronological order
            all_receipts_final = list(PaymentReciept.objects.filter(student=student).order_by('id'))
            
            if all_receipts_final:
                # Get total fees from the first payment section or existing receipts
                total_fees_val = payment_sections[0]['total_fees'] if payment_sections else 0
                if total_fees_val == 0 and all_receipts_final:
                    total_fees_val = float(all_receipts_final[0].semyearfees or 0)
                
                cumulative_paid = 0.0
                
                # Process all receipts in chronological order
                for receipt in all_receipts_final:
                    try:
                        current_paid = float(receipt.paidamount or 0)
                        cumulative_paid += current_paid
                        
                        # Calculate pending and advance amounts
                        pending = max(0.0, total_fees_val - cumulative_paid)
                        advance = max(0.0, cumulative_paid - total_fees_val)
                        
                        # Determine payment type
                        payment_type = "Full Payment" if pending == 0 else "Part Payment"
                        if advance > 0:
                            payment_type = "Advance Payment"
                        
                        # Update the receipt with calculated amounts
                        receipt.pendingamount = str(pending)
                        receipt.advanceamount = str(advance)
                        receipt.payment_type = payment_type
                        receipt.semyearfees = str(total_fees_val)
                        
                        receipt.save()
                        
                        logger.info(f"[update_student] Final calculation for receipt {receipt.id}: "
                                   f"Paid={current_paid}, Cumulative={cumulative_paid}, "
                                   f"Pending={pending}, Advance={advance}, Type={payment_type}")
                               
                    except Exception as ex:
                        logger.exception("[update_student] Error in final calculation for receipt %s: %s", receipt.id, str(ex))

            # --- Build response payload ---
            student_ser = StudentSerializer(student)
            enrollment_data = {
                "course": enrollment.course.name if getattr(enrollment, "course", None) else None,
                "stream": enrollment.stream.name if getattr(enrollment, "stream", None) else None,
                "substream": enrollment.substream.name if getattr(enrollment, "substream", None) else None,
                "studypattern": enrollment.course_pattern,
                "session": enrollment.session,
                "entry_mode": enrollment.entry_mode,
                "total_semyear": enrollment.total_semyear,
                "semyear": enrollment.current_semyear,
            }
            additional_details_data = {
                "counselor_name": add_details.counselor_name or None,
                "reference_name": add_details.reference_name or None,
                "university_enroll_number": add_details.university_enrollment_id or None,
                "enrolled_by": add_details.enrolled_by or None,
            }
            docs_qs = StudentDocuments.objects.filter(student=student).order_by("id")
            docs_data = StudentDocumentsSerializerGET(docs_qs, many=True).data
            qual_data = QualificationSerializer(qual).data if qual else None
            
            # Get all payment receipts for response
            payment_receipts = PaymentReciept.objects.filter(student=student).order_by("-id")
            payment_data = []
            for receipt in payment_receipts:
                payment_data.append({
                    "id": receipt.id,
                    "fee_receipt_type": receipt.fee_reciept_type,
                    "total_fees": receipt.semyearfees,
                    "paid_amount": receipt.paidamount,
                    "transaction_date": receipt.transaction_date,
                    "payment_mode": receipt.paymentmode,
                    "cheque_no": receipt.cheque_no,
                    "bank_name": receipt.bank_name,
                    "payment_transaction_id": receipt.transactionID,
                    "remarks": receipt.remarks,
                    "pending_amount": receipt.pendingamount,
                    "advance_amount": receipt.advanceamount,
                    "payment_transactionID": receipt.payment_transactionID,
                })

            dt = (time.monotonic() - t0) * 1000.0
            logger.info("[update_student] OK user=%s enrollment_id=%s ms=%.1f", user_email, enrollment_id, dt)

            return Response({
                "message": "Student details updated successfully.",
                "student": student_ser.data,
                "enrollment": enrollment_data,
                "additional_details": additional_details_data,
                "documents": docs_data,
                "qualifications": qual_data,
                "payment_details": payment_data
            }, status=status.HTTP_200_OK)

    except Course.DoesNotExist:
        return Response({"error": "Course not found."}, status=status.HTTP_400_BAD_REQUEST)
    except Stream.DoesNotExist:
        return Response({"error": "Stream not found."}, status=status.HTTP_400_BAD_REQUEST)
    except SubStream.DoesNotExist:
        return Response({"error": "SubStream not found."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        dt = (time.monotonic() - t0) * 1000.0
        logger.exception("[update_student] FAIL user=%s enrollment_id=%s ms=%.1f err=%s", user_email, enrollment_id, dt, str(e))
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#29-07-2025
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_student_details(request, enrollment_id):
    print('inside update student')
    """
    Update an enrolled student's complete profile by enrollment_id.
    - Student core fields (incl. image)
    - Enrollment (course/stream/substream/pattern/session/entry_mode/semyear)
    - Additional enrollment details
    - Qualifications (incl. file fields) + others[]
    - Documents (create/update; supports JSON list or FormData-style indexed keys)
    - StudentFees: UPSERT (no delete)
    - PaymentReciept: Handle multiple payment sections - only save non-empty ones
    """
    t0 = time.monotonic()
    user_email = getattr(request.user, "email", str(request.user))
    logger.info("[update_student] START user=%s enrollment_id=%s", user_email, enrollment_id)

    data = request.data
    print("Received data:", data)
    try:
        print('inside Try student')
        with transaction.atomic():
            # --- Load Student (FOR UPDATE to avoid races) ---
            try:
                student = Student.objects.select_for_update().get(enrollment_id=str(enrollment_id))
            except Student.DoesNotExist:
                logger.warning("[update_student] NOT_FOUND enrollment_id=%s", enrollment_id)
                return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

            # --- Map & update Student scalar fields ---
            student_field_map = {
                "name": "name",
                "father_name": "father_name",
                "mother_name": "mother_name",
                "dob": "dateofbirth",
                "mobile_number": "mobile",
                "alternate_number": "alternate_mobile1",
                "alternate_email": "alternateemail",
                "email": "email",
                "gender": "gender",
                "category": "category",
                "address": "address",
                "alternateaddress": "alternateaddress",
                "nationality": "nationality",
                "pincode": "pincode",
                "registration_number": "registration_number",
                "student_remarks": "student_remarks",
            }
            for in_key, model_field in student_field_map.items():
                if in_key in data and data.get(in_key) not in (None, ""):
                    setattr(student, model_field, data.get(in_key))

            # Country/State/City (optional)
            if "country" in data and data.get("country"):
                try:
                    student.country = Countries.objects.get(id=data.get("country"))
                except Countries.DoesNotExist:
                    return Response({"error": f"Country with id {data.get('country')} does not exist."}, status=400)
            if "state" in data and data.get("state"):
                try:
                    student.state = States.objects.get(id=data.get("state"))
                except States.DoesNotExist:
                    return Response({"error": f"State with id {data.get('state')} does not exist."}, status=400)
            if "city" in data and data.get("city"):
                try:
                    student.city = Cities.objects.get(id=data.get("city"))
                except Cities.DoesNotExist:
                    return Response({"error": f"City with id {data.get('city')} does not exist."}, status=400)

            # University (optional)
            if "university" in data and data.get("university"):
                try:
                    student.university = University.objects.get(id=data.get("university"))
                except University.DoesNotExist:
                    return Response({"error": f"University with id {data.get('university')} does not exist."}, status=400)

            # Image/file (optional)
            img_file = request.FILES.get("image") or data.get("image")
            if img_file:
                student.image = img_file

            student.save()
            
            # --- Pending Verification ---
            pending_verification, created = PendingVerification.objects.get_or_create(student=student)

            # Update fields if provided, otherwise set to empty/null
            if "student_university_enrollment" in data:
                enrollment_val = data.get("student_university_enrollment")
                pending_verification.student_university_enrollment = enrollment_val if enrollment_val not in (None, "") else None

            if "student_university_user_id" in data:
                user_id_val = data.get("student_university_user_id")
                pending_verification.student_university_user_id = user_id_val if user_id_val not in (None, "") else None

            if "student_university_password" in data:
                password_val = data.get("student_university_password")
                pending_verification.student_university_password = password_val if password_val not in (None, "") else None

            pending_verification.save()

            logger.info(f"[update_student] Updated pending verification for student {student.id}")

            # --- Enrollment: update or create one record ---
            enrollment = Enrolled.objects.filter(student=student).first()
            if not enrollment:
                enrollment = Enrolled(student=student)

            # Resolve related course/stream/substream when provided
            course_obj = None
            stream_obj = None
            substream_obj = None

            if data.get("course"):
                try:
                    course_obj = Course.objects.get(id=data.get("course"), university=student.university)
                except Course.DoesNotExist:
                    return Response({"error": "Course not found for the student's university."}, status=400)
                enrollment.course = course_obj

            if data.get("stream"):
                if not course_obj:
                    course_obj = enrollment.course
                if not course_obj:
                    return Response({"error": "Set course before stream."}, status=400)
                try:
                    stream_obj = Stream.objects.get(id=data.get("stream"), course=course_obj)
                except Stream.DoesNotExist:
                    return Response({"error": "Stream not found for the selected course."}, status=400)
                enrollment.stream = stream_obj

            # Substream can be null/empty => clear it
            if "substream" in data:
                sub_id = data.get("substream")
                if sub_id in (None, "", "null"):
                    enrollment.substream = None
                    substream_obj = None
                else:
                    if not stream_obj:
                        stream_obj = enrollment.stream
                    if not stream_obj:
                        return Response({"error": "Set stream before substream."}, status=400)
                    try:
                        substream_obj = SubStream.objects.get(id=sub_id, stream=stream_obj)
                    except SubStream.DoesNotExist:
                        return Response({"error": "SubStream not found for the selected stream."}, status=400)
                    enrollment.substream = substream_obj

            # Simple fields
            if "studypattern" in data and data.get("studypattern"):
                enrollment.course_pattern = str(data.get("studypattern")).capitalize()
            if "session" in data and data.get("session"):
                enrollment.session = data.get("session")
            if "entry_mode" in data and data.get("entry_mode"):
                enrollment.entry_mode = data.get("entry_mode")
            if "semyear" in data and data.get("semyear"):
                enrollment.current_semyear = data.get("semyear")

            # Compute total_semyear if we have a stream and pattern
            pattern = enrollment.course_pattern or ""
            stream_for_calc = enrollment.stream
            if stream_for_calc and pattern:
                try:
                    total = int(getattr(stream_for_calc, "sem"))
                    if pattern == "Semester":
                        total = total * 2
                    enrollment.total_semyear = str(total)
                except Exception:
                    pass

            enrollment.save()

            # --- Additional Enrollment Details ---
            add_details, _ = AdditionalEnrollmentDetails.objects.get_or_create(student=student)
            enrolled_by_value = (data.get("enrolled_by") or "")
            if enrolled_by_value:
              add_details.enrolled_by = enrolled_by_value
            if "counselor_name" in data:
                add_details.counselor_name = data.get("counselor_name") or ""
            if "reference_name" in data:
                add_details.reference_name = data.get("reference_name") or ""
            if "university_enroll_number" in data:
                add_details.university_enrollment_id = data.get("university_enroll_number") or ""
            if "university_enrollment_number" in data:
                add_details.university_enrollment_id = data.get("university_enrollment_number") or add_details.university_enrollment_id
            
            add_details.save()

            # --- Qualifications ---
            qual, _ = Qualification.objects.get_or_create(student=student)

            # Support nested dict (JSON) and/or FormData-style flat keys
            q = data.get("qualifications") if isinstance(data.get("qualifications"), dict) else {}

            # Scalar fields (years/boards/percentages)
            qual_fields = [
                "secondary_year", "sr_year", "under_year", "post_year", "mphil_year",
                "secondary_board", "sr_board", "under_board", "post_board", "mphil_board",
                "secondary_percentage", "sr_percentage", "under_percentage", "post_percentage", "mphil_percentage",
            ]
            for f in qual_fields:
                if f in q and q.get(f) not in (None, ""):
                    setattr(qual, f, q.get(f))
                else:
                    flat_val = data.get(f"qualifications[{f}]")
                    if flat_val not in (None, ""):
                        setattr(qual, f, flat_val)

            # File fields (accept both nested and flat)
            file_map = {
                "secondary_document": ["qualifications[secondary_document]"],
                "sr_document": ["qualifications[sr_document]"],
                "under_document": ["qualifications[under_document]"],
                "post_document": ["qualifications[post_document]"],
                "mphil_document": ["qualifications[mphil_document]"],
            }
            for model_field, flat_keys in file_map.items():
                file_obj = None
                if model_field in q and q.get(model_field):
                    file_obj = q.get(model_field)
                if not file_obj:
                    for k in flat_keys:
                        if k in request.FILES:
                            file_obj = request.FILES[k]
                            break
                if file_obj:
                    setattr(qual, model_field, file_obj)

            # "others" (list of dicts with optional file)
            others_payload = []
            if isinstance(q.get("others"), list):
                for item in q["others"]:
                    if not isinstance(item, dict):
                        continue
                    file_obj = item.get("file")
                    file_path = None
                    if file_obj:
                        file_path = default_storage.save(f"University_Documents/{getattr(file_obj, 'name', 'other')}", file_obj)
                    others_payload.append({
                        "year": item.get("year"),
                        "board": item.get("board"),
                        "doctype": item.get("doctype"),
                        "file_path": file_path
                    })
            else:
                indices = set()
                for k in data.keys():
                    if k.startswith("qualifications[others]") and "][" in k:
                        try:
                            idx = k.split("[")[2].split("]")[0]
                            if str(idx).isdigit():
                                indices.add(int(idx))
                        except Exception:
                            pass
                for idx in sorted(list(indices)):
                    file_key = f"qualifications[others][{idx}][file]"
                    file_obj = request.FILES.get(file_key)
                    file_path = None
                    if file_obj:
                        file_path = default_storage.save(f"University_Documents/{file_obj.name}", file_obj)
                    others_payload.append({
                        "year": data.get(f"qualifications[others][{idx}][year]"),
                        "board": data.get(f"qualifications[others][{idx}][board]"),
                        "doctype": data.get(f"qualifications[others][{idx}][doctype]"),
                        "file_path": file_path
                    })

            if others_payload:
                qual.others = others_payload
            elif "others" in q and not q.get("others"):
                qual.others = []

            qual.save()

            # --- Documents (JSON or FormData indexed) ---
            docs_json = data.get("documents")
            if isinstance(docs_json, list):
                for d in docs_json:
                    if not isinstance(d, dict):
                        continue
                    doc_id = d.get("id")
                    if doc_id:
                        try:
                            doc_obj = StudentDocuments.objects.get(id=doc_id, student=student)
                        except StudentDocuments.DoesNotExist:
                            return Response({"error": f"Document with id {doc_id} not found for this student."}, status=400)
                    else:
                        doc_obj = StudentDocuments(student=student)

                    for f in ["document", "document_name", "document_ID_no"]:
                        if f in d and d.get(f) not in (None, ""):
                            setattr(doc_obj, f, d.get(f))

                    f_front = d.get("document_image_front")
                    f_back = d.get("document_image_back")
                    if f_front:
                        doc_obj.document_image_front = f_front
                    if f_back:
                        doc_obj.document_image_back = f_back

                    doc_obj.save()
            else:
                idx = 0
                while True:
                    key_base = f"documents[{idx}]"
                    if f"{key_base}[document]" not in data:
                        break
                    doc_id_val = data.get(f"{key_base}[id]")
                    if doc_id_val:
                        try:
                            doc_obj = StudentDocuments.objects.get(id=doc_id_val, student=student)
                        except StudentDocuments.DoesNotExist:
                            return Response({"error": f"Document with id {doc_id_val} not found for this student."}, status=400)
                    else:
                        doc_obj = StudentDocuments.objects.filter(
                            student=student,
                            document=data.get(f"{key_base}[document]"),
                            document_name=data.get(f"{key_base}[document_name]"),
                            document_ID_no=data.get(f"{key_base}[document_ID_no]"),
                        ).first() or StudentDocuments(student=student)

                    doc_obj.document = data.get(f"{key_base}[document]") or doc_obj.document
                    doc_obj.document_name = data.get(f"{key_base}[document_name]") or doc_obj.document_name
                    doc_obj.document_ID_no = data.get(f"{key_base}[document_ID_no]") or doc_obj.document_ID_no

                    f_front = request.FILES.get(f"{key_base}[document_image_front]")
                    f_back = request.FILES.get(f"{key_base}[document_image_back]")
                    if f_front:
                        doc_obj.document_image_front = f_front
                    if f_back:
                        doc_obj.document_image_back = f_back

                    doc_obj.save()
                    idx += 1

            # --- StudentFees: UPSERT (no delete) ---
            if any(k in data for k in ("studypattern", "stream", "substream")):
                effective_pattern = (enrollment.course_pattern or "").strip()
                base_stream = enrollment.stream
                base_substream = enrollment.substream

                if effective_pattern and base_stream:
                    fees_model = SemesterFees if effective_pattern == "Semester" else YearFees
                    master_fees = fees_model.objects.filter(stream=base_stream, substream=base_substream)

                    existing = {sf.sem: sf for sf in StudentFees.objects.filter(student=student)}

                    to_create = []
                    to_update = []

                    for fee in master_fees:
                        key_sem = fee.sem if effective_pattern == "Semester" else fee.year
                        sf = existing.get(key_sem)
                        if sf:
                            changed = False
                            if sf.stream_id != base_stream.id:
                                sf.stream = base_stream
                                changed = True
                            if (sf.substream_id or None) != (base_substream.id if base_substream else None):
                                sf.substream = base_substream
                                changed = True
                            if sf.studypattern != effective_pattern:
                                sf.studypattern = effective_pattern
                                changed = True
                            if str(sf.tutionfees) != str(fee.tutionfees):
                                sf.tutionfees = fee.tutionfees
                                changed = True
                            if str(sf.examinationfees) != str(fee.examinationfees):
                                sf.examinationfees = fee.examinationfees
                                changed = True
                            if str(sf.totalfees) != str(fee.totalfees):
                                sf.totalfees = fee.totalfees
                                changed = True
                            if changed:
                                to_update.append(sf)
                        else:
                            to_create.append(
                                StudentFees(
                                    student=student,
                                    stream=base_stream,
                                    substream=base_substream,
                                    studypattern=effective_pattern,
                                    tutionfees=fee.tutionfees,
                                    examinationfees=fee.examinationfees,
                                    totalfees=fee.totalfees,
                                    sem=(fee.sem if effective_pattern == "Semester" else fee.year),
                                )
                            )

                    if to_create:
                        StudentFees.objects.bulk_create(to_create)
                    if to_update:
                        StudentFees.objects.bulk_update(
                            to_update,
                            ["stream", "substream", "studypattern", "tutionfees", "examinationfees", "totalfees"]
                        )

            # --- PaymentReciept: Handle cumulative payment calculations ---
            payment_sections = []
            
            # Check for multiple payment sections in FormData
            idx = 0
            while True:
                fee_receipt_key = f"paymentSections[{idx}][feeReceipt]"
                if fee_receipt_key not in data:
                    break
                
                has_payment_data = (
                    data.get(fee_receipt_key) not in (None, "") or
                    data.get(f"paymentSections[{idx}][amount]") not in (None, "", "0") or
                    data.get(f"paymentSections[{idx}][totalFees]") not in (None, "", "0")
                )
                
                if has_payment_data:
                    # Get the payment ID - this is crucial for updates
                    payment_id = data.get(f"paymentSections[{idx}][id]")
                    
                    payment_sections.append({
                        "index": idx,
                        "id": payment_id,
                        "fee_receipt": data.get(fee_receipt_key),
                        "total_fees": float(data.get(f"paymentSections[{idx}][totalFees]") or 0),
                        "amount": float(data.get(f"paymentSections[{idx}][amount]") or 0),
                        "transaction_date": data.get(f"paymentSections[{idx}][transactionDate]"),
                        "payment_mode": data.get(f"paymentSections[{idx}][paymentMode]"),
                        "cheque_no": data.get(f"paymentSections[{idx}][chequeNo]"),
                        "bank_name": data.get(f"paymentSections[{idx}][selectedBank]"),
                        "payment_transaction_id": data.get(f"paymentSections[{idx}][paymentTransactionId]"),
                        "remarks": data.get(f"paymentSections[{idx}][remarks]"),
                        "is_existing": data.get(f"paymentSections[{idx}][isExisting]", "false").lower() == "true",
                    })
                idx += 1

            # If no indexed sections found, check for single payment data
            if not payment_sections:
                single_payment_fields = (
                    "paidamount", "fee_reciept_type", "payment_mode", "remarks",
                    "transaction_date", "cheque_no", "bank_name", "totalFees", "payment_transactionID"
                )
                if any(data.get(k) not in (None, "") for k in single_payment_fields):
                    has_single_payment = (
                        data.get("paidamount") not in (None, "", "0") or
                        data.get("totalFees") not in (None, "", "0")
                    )
                    if has_single_payment:
                        payment_sections.append({
                            "index": 0,
                            "id": None,
                            "fee_receipt": data.get("fee_reciept_type"),
                            "total_fees": float(data.get("totalFees") or 0),
                            "amount": float(data.get("paidamount") or 0),
                            "transaction_date": data.get("transaction_date"),
                            "payment_mode": data.get("payment_mode"),
                            "cheque_no": data.get("cheque_no"),
                            "bank_name": data.get("bank_name"),
                            "payment_transaction_id": data.get("payment_transactionID"),
                            "remarks": data.get("remarks"),
                            "is_existing": False,
                        })

            # Get all existing payment receipts for this student in chronological order
            all_existing_receipts = list(PaymentReciept.objects.filter(student=student).order_by('id'))
            existing_receipts_map = {receipt.id: receipt for receipt in all_existing_receipts}

            # Track modified receipts
            modified_receipt_ids = set()
            updated_receipts = []

            # First pass: Process payment sections - only create new ones if they don't have IDs
            for payment_data in payment_sections:
                try:
                    payment_id = payment_data.get("id")
                    amount = payment_data["amount"]
                    
                    # Skip if no amount
                    if amount <= 0:
                        continue
                        
                    fee_type = payment_data.get("fee_receipt")
                    other_type = data.get("other_data")
                    receipt_type = (other_type if fee_type == "Others" else fee_type) or ""
                    
                    bank_name_in = payment_data.get("bank_name")
                    other_bank = data.get("other_bank")
                    bank_used = other_bank if bank_name_in == "Others" else bank_name_in
                    payment_mode = payment_data.get("payment_mode")
                    payment_status = "Not Realised" if payment_mode == "Cheque" else "Realised"
                    semyear_value = (
                        "1" if (enrollment.course_pattern == "Full Course")
                        else (data.get("semyear") or enrollment.current_semyear)
                    )
                    uncleared_amount = str(amount) if payment_mode == "Cheque" else None

                    # Find existing receipt or create new ONLY if no ID provided
                    pr = None
                    if payment_id:
                        try:
                            # Try to find the payment record by ID for this student
                            pr = PaymentReciept.objects.get(id=payment_id, student=student)
                            logger.info(f"[update_student] Found existing receipt by ID: {pr.id}")
                            modified_receipt_ids.add(payment_id)

                            # UPDATE existing record
                            pr.payment_for = "Course Fees"
                            pr.payment_categories = "Update"
                            pr.fee_reciept_type = receipt_type
                            pr.transaction_date = payment_data.get("transaction_date")
                            pr.cheque_no = payment_data.get("cheque_no")
                            pr.bank_name = bank_used
                            pr.paidamount = str(amount)
                            pr.paymentmode = payment_mode or "Online"
                            pr.remarks = payment_data.get("remarks")
                            pr.session = enrollment.session
                            pr.semyear = str(semyear_value) if semyear_value is not None else ""
                            pr.uncleared_amount = str(uncleared_amount) if uncleared_amount is not None else None
                            pr.status = payment_status
                            pr.payment_transactionID = payment_data.get("payment_transaction_id") or None
                            
                            pr.save()
                            updated_receipts.append(pr)
                            
                            logger.info(f"[update_student] Updated payment receipt ID {pr.id}")
                            
                        except PaymentReciept.DoesNotExist:
                            logger.warning(f"[update_student] Payment receipt with ID {payment_id} not found, creating new one")
                            # Fall through to create new record
                            payment_id = None
                    
                    if not payment_id and not payment_data.get("is_existing"):
                        # CREATE new receipt ONLY if no ID and not marked as existing
                        try:
                            latest_receipt = PaymentReciept.objects.latest("id")
                            last_id = int(str(latest_receipt.transactionID).replace("TXT445FE", "")) if latest_receipt else 100
                        except PaymentReciept.DoesNotExist:
                            last_id = 100
                        transaction_id = f"TXT445FE{last_id + 1}"

                        pr = PaymentReciept.objects.create(
                            student=student,
                            payment_for="Course Fees",
                            payment_categories="New Payment",
                            fee_reciept_type=receipt_type,
                            transaction_date=payment_data.get("transaction_date"),
                            cheque_no=payment_data.get("cheque_no"),
                            bank_name=bank_used,
                            paidamount=str(amount),
                            transactionID=transaction_id,
                            paymentmode=payment_mode or "Online",
                            remarks=payment_data.get("remarks"),
                            session=enrollment.session,
                            semyear=str(semyear_value) if semyear_value is not None else "",
                            uncleared_amount=str(uncleared_amount) if uncleared_amount is not None else None,
                            status=payment_status,
                            created_by=str(request.user.id),
                            payment_transactionID=payment_data.get("payment_transaction_id") or None,
                        )
                        updated_receipts.append(pr)
                        logger.info(f"[update_student] Created new payment receipt: {pr.transactionID}")
                    else:
                        # Skip if payment has ID but not found in database, or marked as existing but no ID
                        logger.warning(f"[update_student] Skipping payment section - ID not found or invalid: {payment_id}")
                        
                except Exception as ex:
                    logger.exception("[update_student] payment_receipt_process_failed student_id=%s section_index=%s err=%s", 
                                    student.id, payment_data.get("index"), str(ex))

            # Second pass: Recalculate ALL payment amounts in chronological order
            all_receipts_final = list(PaymentReciept.objects.filter(student=student).order_by('id'))
            
            if all_receipts_final:
                # Get total fees from the first payment section or existing receipts
                total_fees_val = payment_sections[0]['total_fees'] if payment_sections else 0
                if total_fees_val == 0 and all_receipts_final:
                    total_fees_val = float(all_receipts_final[0].semyearfees or 0)
                
                cumulative_paid = 0.0
                
                # Process all receipts in chronological order
                for receipt in all_receipts_final:
                    try:
                        current_paid = float(receipt.paidamount or 0)
                        cumulative_paid += current_paid
                        
                        # Calculate pending and advance amounts
                        pending = max(0.0, total_fees_val - cumulative_paid)
                        advance = max(0.0, cumulative_paid - total_fees_val)
                        
                        # Determine payment type
                        payment_type = "Full Payment" if pending == 0 else "Part Payment"
                        if advance > 0:
                            payment_type = "Advance Payment"
                        
                        # Update the receipt with calculated amounts
                        receipt.pendingamount = str(pending)
                        receipt.advanceamount = str(advance)
                        receipt.payment_type = payment_type
                        receipt.semyearfees = str(total_fees_val)
                        
                        receipt.save()
                        
                        logger.info(f"[update_student] Final calculation for receipt {receipt.id}: "
                                   f"Paid={current_paid}, Cumulative={cumulative_paid}, "
                                   f"Pending={pending}, Advance={advance}, Type={payment_type}")
                               
                    except Exception as ex:
                        logger.exception("[update_student] Error in final calculation for receipt %s: %s", receipt.id, str(ex))

            # --- Build response payload ---
            student_ser = StudentSerializer(student)
            enrollment_data = {
                "course": enrollment.course.name if getattr(enrollment, "course", None) else None,
                "stream": enrollment.stream.name if getattr(enrollment, "stream", None) else None,
                "substream": enrollment.substream.name if getattr(enrollment, "substream", None) else None,
                "studypattern": enrollment.course_pattern,
                "session": enrollment.session,
                "entry_mode": enrollment.entry_mode,
                "total_semyear": enrollment.total_semyear,
                "semyear": enrollment.current_semyear,
            }
            additional_details_data = {
                "counselor_name": add_details.counselor_name or None,
                "reference_name": add_details.reference_name or None,
                "university_enroll_number": add_details.university_enrollment_id or None,
                "enrolled_by": add_details.enrolled_by or None,
            }
            docs_qs = StudentDocuments.objects.filter(student=student).order_by("id")
            docs_data = StudentDocumentsSerializerGET(docs_qs, many=True).data
            qual_data = QualificationSerializer(qual).data if qual else None
            
            # Get all payment receipts for response
            payment_receipts = PaymentReciept.objects.filter(student=student).order_by("-id")
            payment_data = []
            for receipt in payment_receipts:
                payment_data.append({
                    "id": receipt.id,  # Include ID in response
                    "fee_receipt_type": receipt.fee_reciept_type,
                    "total_fees": receipt.semyearfees,
                    "paid_amount": receipt.paidamount,
                    "transaction_date": receipt.transaction_date,
                    "payment_mode": receipt.paymentmode,
                    "cheque_no": receipt.cheque_no,
                    "bank_name": receipt.bank_name,
                    "payment_transaction_id": receipt.transactionID,
                    "remarks": receipt.remarks,
                    "pending_amount": receipt.pendingamount,
                    "advance_amount": receipt.advanceamount,
                    "payment_transactionID": receipt.payment_transactionID,
                })

            dt = (time.monotonic() - t0) * 1000.0
            logger.info("[update_student] OK user=%s enrollment_id=%s ms=%.1f", user_email, enrollment_id, dt)

            return Response({
                "message": "Student details updated successfully.",
                "student": student_ser.data,
                "enrollment": enrollment_data,
                "additional_details": additional_details_data,
                "documents": docs_data,
                "qualifications": qual_data,
                "payment_details": payment_data
            }, status=status.HTTP_200_OK)

    except Course.DoesNotExist:
        return Response({"error": "Course not found."}, status=status.HTTP_400_BAD_REQUEST)
    except Stream.DoesNotExist:
        return Response({"error": "Stream not found."}, status=status.HTTP_400_BAD_REQUEST)
    except SubStream.DoesNotExist:
        return Response({"error": "SubStream not found."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        dt = (time.monotonic() - t0) * 1000.0
        logger.exception("[update_student] FAIL user=%s enrollment_id=%s ms=%.1f err=%s", user_email, enrollment_id, dt, str(e))
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_registration_list(request):
  students = Student.objects.filter(archive=False,is_quick_register=False, is_cancelled=False,is_pending=False,is_approve=False).order_by('-id')
  serializer = Student_Quick_RegisteredSerializer(students, many=True)
  return Response(serializer.data)  

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def quick_registration(request):
    """
    Create a student via quick registration flow.

    Notes:
    - `enrollment_id` and `registration_id` are auto-generated here.
    - `registration_number` is OPTIONAL free-text from client.
    - Expects Bearer auth; only superusers are allowed.
    """
    if not request.user.is_superuser:
        return Response({"error": "You are not authorized to perform this action."}, status=403)

    data = request.data
    image = request.FILES.get("image")

    # ------------- read required basics
    name          = (data.get("name") or "").strip()
    email         = (data.get("email") or "").strip().lower()
    mobile        = (data.get("mobile_number") or data.get("mobile") or "").strip()
    university_id = data.get("university")
    
    course_id     = data.get("course")
    enrolled_by   = data.get('enrolledBy')
    stream_id     = data.get("stream")
    substream_id  = data.get("substream")  # optional

    studypattern  = (data.get("studypattern") or "").strip().capitalize()  # "Semester" | "Annual" | "Full course"
    semyear       = (data.get("semyear") or "").strip()                     # "1", "2", ...
    session       = (data.get("session") or "").strip()
    entry_mode    = (data.get("entry_mode") or "").strip()

    # ------------- extra student fields (optional)
    father_name         = (data.get("father_name") or "").strip()
    mother_name         = (data.get("mother_name") or "").strip()
    # ✅ FIX: Handle empty date string properly
    dateofbirth_str     = (data.get("dateofbirth") or "").strip()
    dateofbirth = None
    if dateofbirth_str:
        try:
            dateofbirth = datetime.strptime(dateofbirth_str, '%Y-%m-%d').date()
            # Optional: Validate that date is not in future
            today = timezone.now().date()
            if dateofbirth >= today:
                return Response({"error": "Date of Birth cannot be today or in the future."}, status=400)
        except ValueError:
            return Response({"error": "Invalid date format for Date of Birth. Use YYYY-MM-DD."}, status=400)
    
    gender              = (data.get("gender") or "").strip()
    category            = (data.get("category") or "").strip()
    address             = (data.get("address") or "").strip()
    alternateaddress    = (data.get("alternate_address") or data.get("alternateaddress") or "").strip()
    nationality         = (data.get("nationality") or "").strip()
    pincode             = (data.get("pincode") or "").strip()

    # OPTIONAL free-text registration number from UI
    registration_number = (data.get("registration_number") or data.get("registration_id") or "").strip()

    # FK IDs (can be blank)
    country_id          = data.get("country")
    state_id            = data.get("state")
    city_id             = data.get("city")

    # optional alternates
    alternate_mobile1   = (data.get("alt_mobile_number") or data.get("alternate_mobile1") or "").strip()
    alternateemail      = (data.get("alt_email") or data.get("alternateemail") or "").strip()

    # remarks
    student_remarks     = (data.get("studentRemarks") or data.get("student_remarks") or data.get("remarks") or "").strip()

    # additional enrollment details (optional)
    counselor_name      = (data.get("counselor_name") or "").strip()
    
    uni_enroll_no       = (data.get("university_enrollment_number") or "").strip()
    reference_name      = (data.get("reference_name") or "").strip()

    # ------------- minimal validation
    required_missing = []
    for label, value in [
        ("name", name), ("email", email), ("mobile_number", mobile),
        ("university", university_id), ("course", course_id), ("stream", stream_id),
        ("studypattern", studypattern), ("semyear", semyear), ("session", session), ("entry_mode", entry_mode),("counselor_name", counselor_name)
    ]:
        if not value:
            required_missing.append(label)
    if required_missing:
        return Response({"error": f"Missing required fields: {', '.join(required_missing)}"}, status=400)

    if studypattern not in {"Semester", "Annual", "Full course"}:
        return Response({"error": "Invalid studypattern. Use 'Semester', 'Annual' or 'Full course'."}, status=400)

    try:
        int(semyear)
    except ValueError:
        return Response({"error": "Invalid semyear. Provide an integer value as a string (e.g. '1')."}, status=400)

    # ------------- duplicates
    if Student.objects.filter(mobile=mobile).exists():
        return Response({"error": "Mobile number already registered."}, status=400)
    if Student.objects.filter(email=email).exists():
        return Response({"error": "Email already registered."}, status=400)

    # ------------- FK lookups
    try:
        university = University.objects.get(id=university_id)
        course     = Course.objects.get(id=course_id, university=university)
        stream     = Stream.objects.get(id=stream_id, course=course)
        substream  = SubStream.objects.get(id=substream_id, stream=stream) if substream_id else None
    except Exception as e:
        return Response({"error": f"Invalid foreign key: {e}"}, status=400)

    # ------------- auto IDs
    latest = Student.objects.order_by("-id").first()
    enrollment_id   = int(latest.enrollment_id) + 1 if latest and latest.enrollment_id else 50000
    registration_id = int(latest.registration_id) + 1 if latest and latest.registration_id else 250000

    # ------------- totals / money inputs
    # from UI: totalFees (string/number), amount (paid)
    def _to_float(x, default=0.0):
        try:
            return float(x or 0)
        except Exception:
            return default

    total_fees_num = _to_float(data.get("totalFees"), 0.0)
    paid_num       = _to_float(data.get("amount"), 0.0)
    pending_num    = total_fees_num - paid_num
    advance_num    = abs(pending_num) if pending_num < 0 else 0.0
    pending_num    = pending_num if pending_num > 0 else 0.0

    # cast to strings for CharFields
    semyearfees_str = str(total_fees_num)
    paid_str        = str(paid_num)
    pending_str     = str(pending_num)
    advance_str     = str(advance_num)
    uncleared_str   = str(paid_num) if (data.get("payment_mode") == "Cheque") else None

    # ------------- begin atomic block
    try:
        with transaction.atomic():
            # --- create Student
            student_payload = {
                "name": name,
                "father_name": father_name,
                "mother_name":mother_name,
                "dateofbirth": dateofbirth,
                "mobile": mobile,
                "alternate_mobile1": alternate_mobile1,
                "email": email,
                "alternateemail": alternateemail,
                "gender": gender,
                "category": category,
                "address": address,
                "alternateaddress": alternateaddress,
                "nationality": nationality,
                "country": country_id,
                "state": state_id,
                "city": city_id,
                "pincode": pincode,
                "enrollment_id": enrollment_id,      # auto-generated
                "registration_id": registration_id,  # auto-generated
                "university": university.id,
                "is_quick_register": True,
                "student_remarks": student_remarks,
                "enrolled_by":enrolled_by,
            }
            # OPTIONAL: include registration_number only if present
            if registration_number:
                student_payload["registration_number"] = registration_number

            # OPTIONAL: image
            if image:
                student_payload["image"] = image

            student_serializer = StudentSerializer(data=student_payload)
            student_serializer.is_valid(raise_exception=True)
            student = student_serializer.save()
            logger.info("Student created | id=%s enrollment_id=%s", student.id, student.enrollment_id)

            # --- ensure a linked User
            user, created_user = User.objects.get_or_create(
                email=email,
                defaults={
                    "mobile": mobile,
                    "is_student": True,
                    "is_jobseeker": True,
                    "password": make_password(mobile or "changeme"),
                },
            )
            if not created_user:
                updates = []
                if not getattr(user, "is_student", False):
                    user.is_student = True; updates.append("is_student")
                if not getattr(user, "is_jobseeker", False):
                    user.is_jobseeker = True; updates.append("is_jobseeker")
                if not user.mobile and mobile:
                    user.mobile = mobile; updates.append("mobile")
                if updates:
                    user.save(update_fields=updates)

            if getattr(student, "user_id", None) is None:
                student.user = user
                student.save(update_fields=["user"])

            # --- Enrolled
            # derive total sem/year available for the course:
            if studypattern in {"Semester", "Annual"}:
                # if your Stream has `sem` = number of years, for Semester total slots are years*2
                total_semyear = int(stream.sem) * (2 if studypattern == "Semester" else 1)
            else:
                # Full course behaves like 1 big slot
                total_semyear = 1

            enrolled_data = {
                "student": student.id,
                "course": course.id,
                "stream": stream.id,
                "substream": substream.id if substream else None,
                "course_pattern": studypattern,
                "session": session,
                "entry_mode": entry_mode,
                "total_semyear": total_semyear,
                "current_semyear": semyear if studypattern != "Full course" else "1",
                # you can save counselor/reference/enrollment numbers in related model if needed
            }
            enrolled_serializer = EnrolledSerializer(data=enrolled_data)
            enrolled_serializer.is_valid(raise_exception=True)
            enrolled_serializer.save()
            logger.info("Enrolled saved | student_id=%s stream_id=%s pattern=%s", student.id, stream.id, studypattern)
            
            AdditionalEnrollmentDetails.objects.create(
                student=student,
                counselor_name=counselor_name,
                enrolled_by=(enrolled_by or None),
                reference_name=(reference_name or None),
                session=session,
                entry_mode=entry_mode,
                university_enrollment_id=(uni_enroll_no or None),
                old_university_enrollment_id=None
            )

            # --- StudentFees rows (copy fee tables into per-student rows)
            if studypattern in {"Semester", "Annual"}:
                fees_model = SemesterFees if studypattern == "Semester" else YearFees
                fees_qs = fees_model.objects.filter(stream=stream, substream=substream)
                for fee in fees_qs:
                    StudentFees.objects.create(
                        student=student, stream=stream, substream=substream,
                        studypattern=studypattern,
                        tutionfees=str(getattr(fee, "tutionfees", "0")),
                        examinationfees=str(getattr(fee, "examinationfees", "0")),
                        bookfees=str(getattr(fee, "bookfees", "0")) if hasattr(fee, "bookfees") else "0",
                        resittingfees=str(getattr(fee, "resittingfees", "0")),
                        entrancefees=str(getattr(fee, "entrancefees", "0")) if hasattr(fee, "entrancefees") else "0",
                        extrafees=str(getattr(fee, "extrafees", "0")) if hasattr(fee, "extrafees") else "0",
                        discount=str(getattr(fee, "discount", "0")) if hasattr(fee, "discount") else "0",
                        totalfees=str(getattr(fee, "totalfees", "0")),
                        sem=str(getattr(fee, "sem", getattr(fee, "year", ""))),
                    )
                logger.info("StudentFees created | count=%s | student_id=%s", fees_qs.count(), student.id)

            # --- PaymentReciept
            # transactionID generator
            try:
                latest_receipt = PaymentReciept.objects.latest("id")
                last_id = int(str(latest_receipt.transactionID).replace("TXT445FE", "") or "100")
                transactionID = f"TXT445FE{last_id + 1}"
            except PaymentReciept.DoesNotExist:
                transactionID = "TXT445FE101"

            receipt = PaymentReciept.objects.create(
                student=student,
                payment_for="Course Fees",
                payment_categories="New",
                payment_type=("Full Payment" if pending_num == 0 else "Part Payment"),
                fee_reciept_type=(data.get("other_data") if data.get("fee_reciept_type") == "Others" else data.get("fee_reciept_type")),
                transaction_date=data.get("transaction_date"),
                cheque_no=data.get("cheque_no"),
                bank_name=(data.get("other_bank") if data.get("bank_name") == "Others" else data.get("bank_name")),
                semyearfees=semyearfees_str,
                payment_transactionID=data.get("payment_transaction_id"),
                paidamount=paid_str,
                pendingamount=pending_str,
                advanceamount=advance_str,
                transactionID=transactionID,
                paymentmode=data.get("payment_mode"),
                remarks=(data.get("remarks") or "").strip(),
                session=session,
                semyear=("1" if studypattern == "Full course" else semyear),
                uncleared_amount=uncleared_str,
                status=("Not Realised" if data.get("payment_mode") == "Cheque" else "Realised"),
            )
            from super_admin.services.receipts import generate_receipt_pdf, email_payment_receipt
            try:
                pdf_bytes = generate_receipt_pdf(student, receipt)
                email_payment_receipt(student, receipt, pdf_bytes)
                emailed = True
            except Exception as mail_err:
                logger.exception("Failed to email receipt PDF: %s", mail_err)
                emailed = False

            logger.info(
                "PaymentReciept created | student_id=%s txn=%s total=%s paid=%s pending=%s",
                student.id, transactionID, semyearfees_str, paid_str, pending_str
            )

        # ------------- success
        return Response(
            {
                "message": "Student registered successfully.",
                "student_id": student.id,
                "enrollment_id": student.enrollment_id,
                "registration_id": student.registration_id,
            },
            status=201,
        )

    except Exception as e:
        logger.exception("Unexpected error during quick registration.")
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_subject(request):
    #logger.info("Received request to create subject.")
    
    # Extract input data from the request
    subject_data = {
        'name': request.data.get('name'),
        'code': request.data.get('code'),
        'stream_id': request.data.get('stream_id'),
        'substream_id': request.data.get('substream_id'),
        'studypattern': request.data.get('studypattern'),
        'semyear': request.data.get('semyear'),
    }
    logger.debug(f"Extracted subject data: {subject_data}")

    # Validate required fields
    if not subject_data['name'] or not subject_data['code']:
        logger.warning("Subject name and code are required but missing.")
        return Response({'error': 'Subject name and code are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Get the stream object
    try:
        stream = Stream.objects.get(id=subject_data['stream_id'])
        #logger.info(f"Stream with id {subject_data['stream_id']} found.")
    except Stream.DoesNotExist:
        logger.error(f"Stream with id {subject_data['stream_id']} not found.")
        return Response({'error': 'Stream not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Get the substream object (optional)
    substream = None
    if subject_data['substream_id']:
        try:
            substream = SubStream.objects.get(id=subject_data['substream_id'], stream=stream)
            #logger.info(f"Substream with id {subject_data['substream_id']} found for the stream.")
        except SubStream.DoesNotExist:
            logger.error(f"Substream with id {subject_data['substream_id']} not found for stream with id {subject_data['stream_id']}.")
            return Response({'error': 'SubStream not found for the specified stream.'}, status=status.HTTP_404_NOT_FOUND)
    else:
        pass
        #logger.info("No substream ID provided, substream will be set to null.")

    # ✅ Improved duplicate check logic
    duplicate_subject = Subject.objects.filter(
        name__iexact=subject_data['name'],
        code__iexact=subject_data['code'],
        stream=stream,
        substream=substream,
        studypattern__iexact=subject_data['studypattern'],
        semyear__iexact=subject_data['semyear']
    ).first()

    if duplicate_subject:
        logger.warning(f"Subject already exists: {subject_data['name']} ({subject_data['code']})")
        return Response({'msg': 'Subject already exists'}, status=status.HTTP_200_OK)

    # Prepare data for serializer
    subject_data['stream'] = subject_data['stream_id']
    subject_data['substream'] = subject_data['substream_id']

    serializer = SubjectSerializer(data=subject_data)
    if serializer.is_valid():
        serializer.save()
        #logger.info(f"Subject '{subject_data['name']}' with code '{subject_data['code']}' successfully created.")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    logger.error(f"Validation failed: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.http import HttpResponse,FileResponse
from io import BytesIO

def validate_row(row):
    errors = []
    if not row['University']:
        errors.append("University not found")
    if not row['Course']:
        errors.append("Course not found")
    if not row['Stream']:
        errors.append("Stream not found")
    if row['email'] and Student.objects.filter(email=row['email']).exists():
        errors.append("Email already exists")
    if row['mobile'] and Student.objects.filter(mobile=row['mobile']).exists():
        errors.append("Mobile number already exists")
    return errors

from openpyxl import load_workbook
from datetime import datetime
# working code without jobseekerapplication added 
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def bulk_student_upload(request):
#     if 'upload_file' not in request.FILES:
#         return Response({"errors": ["No file uploaded."]}, status=400)

#     file = request.FILES['upload_file']
#     try:
#         workbook = load_workbook(file)
#         sheet = workbook.active
#     except Exception as e:
#         logger.error(f"Invalid Excel file: {str(e)}")
#         return Response({"errors": [f"Invalid Excel file: {str(e)}"]}, status=400)

#     errors = []
#     successes = []
#     row_number = 1

#     for row in sheet.iter_rows(min_row=2, values_only=True):
#         row_number += 1
#         if all(value is None for value in row):
#             continue

#         try:
#             (
#                 name, date_of_birth, mobile_number, email, university_name, course_name, stream_name,
#                 substream_name, current_semyear, admission_type, session, course_pattern,
#                 total_semyear, country_name, state_name, city_name
#             ) = row

#             if isinstance(date_of_birth, datetime):
#                 date_of_birth = date_of_birth.date()
#             else:
#                 date_of_birth = datetime.strptime(date_of_birth, "%d-%m-%Y").date()

#             #logger.info(f"Processing Row {row_number}: {row}")

#             required_fields = [name, date_of_birth, mobile_number, email, university_name, course_name, stream_name]
#             if not all(required_fields):
#                 missing = [field_name for field_name, value in zip(
#                     ["Name", "Date of Birth", "Mobile Number", "Email", "University Name", "Course Name", "Stream Name"],
#                     required_fields
#                 ) if not value]
#                 error_msg = f"Row {row_number}: Missing required fields: {', '.join(missing)}."
#                 logger.warning(error_msg)
#                 errors.append(error_msg)
#                 continue

#             mobile_number_str = str(mobile_number).strip()
#             email = str(email).strip().lower()

#             # Check if user with same email already exists
#             if User.objects.filter(email=email).exists():
#                 msg = f"Row {row_number}: Email '{email}' already exists. Skipping entry."
#                 logger.warning(msg)
#                 errors.append(msg)
#                 continue

#             # Check if student already exists (based on mobile or email)
#             if Student.objects.filter(email=email).exists():
#                 msg = f"Row {row_number}: Student with email '{email}' already exists. Skipping entry."
#                 logger.warning(msg)
#                 errors.append(msg)
#                 continue

#             if Student.objects.filter(mobile=mobile_number_str).exists():
#                 msg = f"Row {row_number}: Student with mobile '{mobile_number_str}' already exists. Skipping entry."
#                 logger.warning(msg)
#                 errors.append(msg)
#                 continue

#             university = University.objects.filter(university_name=university_name).first()
#             course = Course.objects.filter(name=course_name, university=university).first()
#             stream = Stream.objects.filter(name=stream_name, course=course).first()
#             substream = SubStream.objects.filter(name=substream_name, stream=stream).first() if substream_name else None
#             country = Countries.objects.filter(name=country_name).first()
#             state = States.objects.filter(name=state_name).first()
#             city = Cities.objects.filter(name=city_name).first()

#             missing_refs = []
#             if not university: missing_refs.append("University")
#             if not course: missing_refs.append("Course")
#             if not stream: missing_refs.append("Stream")
#             if not country: missing_refs.append("Country")
#             if not state: missing_refs.append("State")
#             if not city: missing_refs.append("City")

#             if missing_refs:
#                 msg = f"Row {row_number}: Invalid references for fields: {', '.join(missing_refs)}."
#                 logger.warning(msg)
#                 errors.append(msg)
#                 continue

#             try:
#                 last_student = Student.objects.latest('id')
#                 enrollment_id = int(last_student.enrollment_id) + 1
#                 registration_id = int(last_student.registration_id) + 1
#             except Student.DoesNotExist:
#                 enrollment_id = 50000
#                 registration_id = 250000

#             # Create User
#             user = User.objects.create(
#                 email=email,
#                 mobile=mobile_number_str,
#                 is_student=True,
#                 password=make_password(mobile_number_str)
#             )

#             # Create Student
#             student = Student.objects.create(
#                 name=name,
#                 dateofbirth=date_of_birth,
#                 mobile=mobile_number_str,
#                 email=email,
#                 university=university,
#                 enrollment_id=enrollment_id,
#                 registration_id=registration_id,
#                 country=country,
#                 state=state,
#                 city=city,
#                 student_remarks="Bulk Data Upload",
#                 verified=True,
#                 is_enrolled=True,
#                 user=user
#             )

#             # Enroll student
#             Enrolled.objects.create(
#                 student=student,
#                 course=course,
#                 stream=stream,
#                 substream=substream,
#                 current_semyear=current_semyear,
#                 total_semyear=total_semyear,
#                 course_pattern=(course_pattern or "").capitalize(),
#                 session=session,
#                 entry_mode=admission_type,
#             )

#             msg = f"Row {row_number}: Student '{name}' added successfully."
#             #logger.info(msg)
#             successes.append(msg)

#         except Exception as e:
#             error_msg = f"Row {row_number}: Unexpected error: {str(e)}"
#             logger.error(error_msg, exc_info=True)
#             errors.append(error_msg)

#     return Response({
#         "success": successes,
#         "errors": errors
#     }, status=200)


#added by ankit 18-08-2025 for student jobseeker added for bulk upload student
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def bulk_student_upload(request):
#     if 'upload_file' not in request.FILES:
#         return Response({"errors": ["No file uploaded."]}, status=400)

#     file = request.FILES['upload_file']
#     try:
#         workbook = load_workbook(file)
#         sheet = workbook.active
#     except Exception as e:
#         logger.error(f"Invalid Excel file: {str(e)}")
#         return Response({"errors": [f"Invalid Excel file: {str(e)}"]}, status=400)

#     errors = []
#     successes = []
#     row_number = 1

#     for row in sheet.iter_rows(min_row=2, values_only=True):
#         row_number += 1
#         if all(value is None for value in row):
#             continue

#         # Make each row atomic so a failure doesn't affect other rows
#         with transaction.atomic():
#             try:
#                 (
#                     name, date_of_birth, mobile_number, email, university_name, course_name, stream_name,
#                     substream_name, current_semyear, admission_type, session, course_pattern,
#                     total_semyear, country_name, state_name, city_name
#                 ) = row

#                 # Parse DOB
#                 if isinstance(date_of_birth, datetime):
#                     date_of_birth = date_of_birth.date()
#                 else:
#                     date_of_birth = datetime.strptime(str(date_of_birth), "%d-%m-%Y").date()

#                 required_fields = [name, date_of_birth, mobile_number, email, university_name, course_name, stream_name]
#                 if not all(required_fields):
#                     missing = [field_name for field_name, value in zip(
#                         ["Name", "Date of Birth", "Mobile Number", "Email", "University Name", "Course Name", "Stream Name"],
#                         required_fields
#                     ) if not value]
#                     error_msg = f"Row {row_number}: Missing required fields: {', '.join(missing)}."
#                     logger.warning(error_msg)
#                     errors.append(error_msg)
#                     continue

#                 mobile_number_str = str(mobile_number).strip()
#                 email = str(email).strip().lower()

#                 # Dedup checks
#                 if User.objects.filter(email=email).exists():
#                     msg = f"Row {row_number}: Email '{email}' already exists. Skipping entry."
#                     logger.warning(msg)
#                     errors.append(msg)
#                     continue

#                 if Student.objects.filter(email=email).exists():
#                     msg = f"Row {row_number}: Student with email '{email}' already exists. Skipping entry."
#                     logger.warning(msg)
#                     errors.append(msg)
#                     continue

#                 if Student.objects.filter(mobile=mobile_number_str).exists():
#                     msg = f"Row {row_number}: Student with mobile '{mobile_number_str}' already exists. Skipping entry."
#                     logger.warning(msg)
#                     errors.append(msg)
#                     continue

#                 # Resolve references
#                 university = University.objects.filter(university_name=university_name).first()
#                 course = Course.objects.filter(name=course_name, university=university).first()
#                 stream = Stream.objects.filter(name=stream_name, course=course).first()
#                 substream = SubStream.objects.filter(name=substream_name, stream=stream).first() if substream_name else None
#                 country = Countries.objects.filter(name=country_name).first()
#                 state = States.objects.filter(name=state_name).first()
#                 city = Cities.objects.filter(name=city_name).first()

#                 missing_refs = []
#                 if not university: missing_refs.append("University")
#                 if not course: missing_refs.append("Course")
#                 if not stream: missing_refs.append("Stream")
#                 if not country: missing_refs.append("Country")
#                 if not state: missing_refs.append("State")
#                 if not city: missing_refs.append("City")

#                 if missing_refs:
#                     msg = f"Row {row_number}: Invalid references for fields: {', '.join(missing_refs)}."
#                     logger.warning(msg)
#                     errors.append(msg)
#                     continue

#                 # Enrollment & Registration IDs
#                 try:
#                     last_student = Student.objects.latest('id')
#                     enrollment_id = int(last_student.enrollment_id) + 1
#                     registration_id = int(last_student.registration_id) + 1
#                 except Student.DoesNotExist:
#                     enrollment_id = 50000
#                     registration_id = 250000

#                 # Create User
#                 user = User.objects.create(
#                     email=email,
#                     mobile=mobile_number_str,
#                     is_student=True,
#                     password=make_password(mobile_number_str)
#                 )

#                 # <<< ADDED: mark as jobseeker and save
#                 user.is_jobseeker = True
#                 user.save(update_fields=["is_jobseeker"])

#                 # Create Student
#                 student = Student.objects.create(
#                     name=name,
#                     dateofbirth=date_of_birth,
#                     mobile=mobile_number_str,
#                     email=email,
#                     university=university,
#                     enrollment_id=enrollment_id,
#                     registration_id=registration_id,
#                     country=country,
#                     state=state,
#                     city=city,
#                     student_remarks="Bulk Data Upload",
#                     verified=True,
#                     is_enrolled=True,
#                     user=user,
#                     is_quick_register=True
#                 )

#                 # Enroll student
#                 Enrolled.objects.create(
#                     student=student,
#                     course=course,
#                     stream=stream,
#                     substream=substream,
#                     current_semyear=current_semyear,
#                     total_semyear=total_semyear,
#                     course_pattern=(course_pattern or "").capitalize(),
#                     session=session,
#                     entry_mode=admission_type,
#                 )

#                 # <<< ADDED: create JobSeekerProfile
#                 JobSeekerProfile.objects.create(
#                     user=user,
#                     resume=None,                                # explicitly null
#                     work_status="student",                       # as requested
#                     city=(str(city_name).strip() if city_name else "")  # use provided name, else blank
#                 )

#                 msg = f"Row {row_number}: Student '{name}' added successfully."
#                 successes.append(msg)

#             except Exception as e:
#                 error_msg = f"Row {row_number}: Unexpected error: {str(e)}"
#                 logger.error(error_msg, exc_info=True)
#                 errors.append(error_msg)

#     return Response({
#         "success": successes,
#         "errors": errors
#     }, status=200)


# added by ankit 06-10-25 for download excel

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_student_upload(request):
    if 'upload_file' not in request.FILES:
        logger.warning("bulk_student_upload: no file uploaded")
        return Response({"errors": ["No file uploaded."]}, status=400)

    up_file = request.FILES['upload_file']

    # 1) Reject if the same file name already exists (your requirement)
    from .models import StudentFileUpload
    if StudentFileUpload.objects.filter(file_name=up_file.name).exists():
        logger.warning(f"bulk_student_upload: file_name already exists: {up_file.name}")
        return Response(
            {"errors": [f'File "{up_file.name}" already exists. Please rename or upload a different file.']},
            status=400
        )

    # Optional extra safety: compute hash now (can help guard against exact duplicates)
    raw_bytes = up_file.read()
    up_file.seek(0)
    file_size = len(raw_bytes)
    file_hash = hashlib.sha256(raw_bytes).hexdigest()

    # If you also want to reject same hash, uncomment:
    # if StudentFileUpload.objects.filter(file_hash=file_hash).exists():
    #     logger.info(f"bulk_student_upload: duplicate file hash for {up_file.name}")
    #     return Response({"errors": ["This exact file has already been uploaded."]}, status=400)

    # 2) Try to open the workbook
    try:
        workbook = load_workbook(BytesIO(raw_bytes), data_only=True)
        sheet = workbook.active
    except Exception as e:
        logger.error(f"bulk_student_upload: invalid Excel: {str(e)}")
        return Response({"errors": [f"Invalid Excel file: {str(e)}"]}, status=400)

    # 3) Create the upload record now (so we can attach its id to each new student)
    uploaded_by = getattr(request.user, 'email', str(request.user))
    upload_rec = StudentFileUpload.objects.create(
        file_name=up_file.name,
        file_size=file_size,
        file_hash=file_hash,
        uploaded_by=uploaded_by,
        total_rows=0, success_rows=0, error_rows=0
    )

    # 4) Process rows (your existing logic)
    errors = []
    successes = []
    row_number = 1
    total_rows = 0
    success_rows = 0
    error_rows = 0

    # imports your models
    from super_admin.models import (
        User, Student, University, Course, Stream, SubStream,
        Countries, States, Cities, Enrolled, JobSeekerProfile
    )
    from django.contrib.auth.hashers import make_password

    for row in sheet.iter_rows(min_row=2, values_only=True):
        row_number += 1
        if all(value is None for value in row):
            continue

        total_rows += 1

        with transaction.atomic():
            try:
                (
                    name, date_of_birth, mobile_number, email, university_name, course_name, stream_name,
                    substream_name, current_semyear, admission_type, session, course_pattern,
                    total_semyear, country_name, state_name, city_name
                ) = row

                # Parse DOB
                if isinstance(date_of_birth, datetime):
                    date_of_birth = date_of_birth.date()
                else:
                    date_of_birth = datetime.strptime(str(date_of_birth), "%d-%m-%Y").date()

                required_fields = [name, date_of_birth, mobile_number, email, university_name, course_name, stream_name]
                if not all(required_fields):
                    missing = [field_name for field_name, value in zip(
                        ["Name", "Date of Birth", "Mobile Number", "Email", "University Name", "Course Name", "Stream Name"],
                        required_fields
                    ) if not value]
                    msg = f"Row {row_number}: Missing required fields: {', '.join(missing)}."
                    logger.warning(msg)
                    errors.append(msg)
                    error_rows += 1
                    continue

                mobile_number_str = str(mobile_number).strip()
                email_norm = str(email).strip().lower()

                # Dedup checks (email / mobile) - keep as in your code
                if User.objects.filter(email=email_norm).exists():
                    msg = f"Row {row_number}: Email '{email_norm}' already exists. Skipping entry."
                    logger.warning(msg)
                    errors.append(msg)
                    error_rows += 1
                    continue

                if Student.objects.filter(email=email_norm).exists():
                    msg = f"Row {row_number}: Student with email '{email_norm}' already exists. Skipping entry."
                    logger.warning(msg)
                    errors.append(msg)
                    error_rows += 1
                    continue

                if Student.objects.filter(mobile=mobile_number_str).exists():
                    msg = f"Row {row_number}: Student with mobile '{mobile_number_str}' already exists. Skipping entry."
                    logger.warning(msg)
                    errors.append(msg)
                    error_rows += 1
                    continue

                # Resolve references
                university = University.objects.filter(university_name=university_name).first()
                course = Course.objects.filter(name=course_name, university=university).first() if university else None
                stream = Stream.objects.filter(name=stream_name, course=course).first() if course else None
                substream = SubStream.objects.filter(name=substream_name, stream=stream).first() if substream_name and stream else None
                country = Countries.objects.filter(name=country_name).first() if country_name else None
                state = States.objects.filter(name=state_name).first() if state_name else None
                city = Cities.objects.filter(name=city_name).first() if city_name else None

                missing_refs = []
                if not university: missing_refs.append("University")
                if not course: missing_refs.append("Course")
                if not stream: missing_refs.append("Stream")
                if country_name and not country: missing_refs.append("Country")
                if state_name and not state: missing_refs.append("State")
                if city_name and not city: missing_refs.append("City")

                if missing_refs:
                    msg = f"Row {row_number}: Invalid references for fields: {', '.join(missing_refs)}."
                    logger.warning(msg)
                    errors.append(msg)
                    error_rows += 1
                    continue

                # Enrollment & Registration IDs
                try:
                    last_student = Student.objects.latest('id')
                    enrollment_id = int(last_student.enrollment_id) + 1
                    registration_id = int(last_student.registration_id) + 1
                except Student.DoesNotExist:
                    enrollment_id = 50000
                    registration_id = 250000

                # Create User
                user = User.objects.create(
                    email=email_norm,
                    mobile=mobile_number_str,
                    is_student=True,
                    password=make_password(mobile_number_str)
                )
                user.is_jobseeker = True
                user.save(update_fields=["is_jobseeker"])

                # Create Student (ATTACH upload id)
                student = Student.objects.create(
                    name=name,
                    dateofbirth=date_of_birth,
                    mobile=mobile_number_str,
                    email=email_norm,
                    university=university,
                    enrollment_id=enrollment_id,
                    registration_id=registration_id,
                    country=country,
                    state=state,
                    city=city,
                    student_remarks="Bulk Data Upload",
                    verified=True,
                    is_enrolled=True,
                    user=user,
                    is_quick_register=True,
                    student_upload=upload_rec,   # <<==== SAVE the StudentFileUpload id
                )

                # Enroll student
                Enrolled.objects.create(
                    student=student,
                    course=course,
                    stream=stream,
                    substream=substream,
                    current_semyear=current_semyear,
                    total_semyear=total_semyear,
                    course_pattern=(course_pattern or "").capitalize(),
                    session=session,
                    entry_mode=admission_type,
                )

                # JobSeekerProfile
                JobSeekerProfile.objects.create(
                    user=user,
                    resume=None,
                    work_status="student",
                    city=(str(city_name).strip() if city_name else "")
                )

                msg = f"Row {row_number}: Student '{name}' added successfully."
                logger.info(msg)
                successes.append(msg)
                success_rows += 1

            except Exception as e:
                msg = f"Row {row_number}: Unexpected error: {str(e)}"
                logger.error(msg, exc_info=True)
                errors.append(msg)
                error_rows += 1

    # 5) Save stats
    upload_rec.total_rows = total_rows
    upload_rec.success_rows = success_rows
    upload_rec.error_rows = error_rows
    upload_rec.save(update_fields=['total_rows', 'success_rows', 'error_rows'])

    return Response({
        "status": "success",
        "message": f"Processed {total_rows} rows. Success: {success_rows}, Errors: {error_rows}.",
        "file_id": upload_rec.id,
        "file_name": upload_rec.file_name,
        "success": successes,
        "errors": errors
    }, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_student_data_excel(request):
    """
    Rebuild the ORIGINAL bulk upload (entire file) from DB.
    Accept exactly one of:
      - file_name=<original file name>
      - file_id=<StudentFileUpload.id>
    We export all Students where student_upload=<that upload>.
    """
    try:
        file_name = request.GET.get('file_name')
        file_id = request.GET.get('file_id')

        from .models import StudentFileUpload
        from super_admin.models import Student, Enrolled

        # Resolve upload by file_id or file_name
        if file_id:
            upload = StudentFileUpload.objects.filter(id=file_id).first()
        elif file_name:
            upload = StudentFileUpload.objects.filter(file_name=file_name).order_by('-uploaded_at').first()
        else:
            return Response({"error": "Provide file_id or file_name"}, status=400)

        if not upload:
            return Response({"error": "Upload not found"}, status=404)

        qs = (Student.objects
              .filter(student_upload=upload)
              .select_related('university', 'country', 'state', 'city')
              .order_by('id'))

        if not qs.exists():
            return Response({"error": "No students found for this upload"}, status=404)

        # EXACT columns used during upload
        headers = [
            "name", "date_of_birth", "mobile_number", "email",
            "university_name", "course_name", "stream_name", "substream_name",
            "current_semyear", "admission_type", "session", "course_pattern",
            "total_semyear", "country_name", "state_name", "city_name",
        ]

        # Helper to fetch enrolment
        def get_enr(stu):
            return (Enrolled.objects
                    .filter(student=stu)
                    .select_related('course', 'stream', 'substream')
                    .order_by('-id')
                    .first())

        # Build workbook
        out = BytesIO()
        wb = Workbook()
        ws = wb.active
        ws.title = "Student Data"
        ws.append(headers)

        for stu in qs:
            enr = get_enr(stu)
            ws.append([
                stu.name or "",
                (stu.dateofbirth.strftime("%d-%m-%Y") if stu.dateofbirth else ""),
                stu.mobile or "",
                stu.email or "",
                (stu.university.university_name if stu.university else ""),
                (enr.course.name if enr and enr.course else ""),
                (enr.stream.name if enr and enr.stream else ""),
                (enr.substream.name if enr and enr.substream else ""),
                (enr.current_semyear if enr else ""),
                (enr.entry_mode if enr else ""),
                (enr.session if enr else ""),
                (enr.course_pattern if enr else ""),
                (enr.total_semyear if enr else ""),
                (stu.country.name if stu.country else ""),
                (stu.state.name if stu.state else ""),
                (stu.city.name if stu.city else ""),
            ])

        # Autosize
        for col in ws.columns:
            ml = max(len(str(c.value)) if c.value else 0 for c in col)
            ws.column_dimensions[col[0].column_letter].width = min(max(10, ml + 2), 60)

        wb.save(out)
        out.seek(0)

        base = upload.file_name.rsplit('.', 1)[0]
        filename = f"reconstructed_{base}.xlsx"

        resp = HttpResponse(
            out.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        logger.info(f"download_student_data_excel: exported {qs.count()} rows for '{upload.file_name}'")
        return resp

    except Exception as e:
        logger.error(f"download_student_data_excel: error: {str(e)}", exc_info=True)
        return Response({"error": "Internal server error"}, status=500)


#-----------------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_subject(request):
    try:
        stream_id = request.query_params.get('stream')
        substream_id = request.query_params.get('substream')  # Optional
        study_pattern = request.query_params.get('study_pattern')
        semyear = request.query_params.get('semyear')
        
        # Initialize the queryset for subjects
        subject_query = Subject.objects.filter(
            stream_id=stream_id,  # Filtering by stream
            studypattern=study_pattern,  # Filtering by study pattern
            semyear=semyear  # Filtering by semester/year
        )

        # If substream is provided, filter by substream
        if substream_id:
            subject_query = subject_query.filter(substream_id=substream_id)
        else:
            # If substream is not provided, include subjects that don't have a substream
            subject_query = subject_query.filter(substream_id__isnull=True)

        # Check if subjects exist for the given parameters
        if not subject_query.exists():
            logger.warning("No subjects found for the given parameters.")
            return Response({"message": "No subjects found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the subject data
        subject_data = SubjectSerializer(subject_query, many=True)

        # Return the subjects data
        return Response({"data": subject_data.data}, status=status.HTTP_200_OK)

    except Exception as e:
        # Log the error if an exception occurs
        logger.error("An error occurred while fetching subjects: %s", str(e), exc_info=True)
        return Response({"message": "An error occurred while processing your request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
def validate_excel_file(file_path):
    required_columns = [
        "COURSE", "STREAM", "SUBSTREAM", "SESSION", "MODE", "YEAR/SEMESTER",
        "SUBJECT NAME", "TYPE OF EXAM", "QUESTION TYPE", "DIFFICULTY LEVEL",
        "QUESTION", "OPTION 1", "OPTION 2", "OPTION 3", "OPTION 4",
        "ANSWER", "MARKS", "EXAM DURATION", "PASSING MARKS"
    ]
    try:
        data = pd.read_excel(file_path)
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            error_message = f"Missing columns in Excel file: {', '.join(missing_columns)}"
            logger.error(error_message)
            return None, error_message
        return data, None
    except Exception as e:
        logger.error(f"Error reading Excel file: {str(e)}", exc_info=True)
        return None, "Invalid Excel file"

@api_view(['GET'])
def filter_questions(request):
    try:
        exam_id = request.query_params.get('exam_id')

        if not exam_id:
            return Response({"error": "Missing exam_id in request"}, status=status.HTTP_400_BAD_REQUEST)

        questions_queryset = Questions.objects.filter(exam__id=exam_id).distinct()
        serializer = QuestionsSerializer(questions_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error occurred while filtering questions: {str(e)}")
        return Response({"error": "Something went wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def fetch_exam(request):
    try:
        university = request.data.get("university")
        course = request.data.get("course")
        stream = request.data.get("stream") or request.data.get("Stream")
        session = request.data.get("session")
        studypattern = request.data.get("studypattern")
        semyear = request.data.get("semyear")
        substream = request.data.get("substream")

        # Treat blank/invalid substream as no filter
        apply_substream_filter = False
        if substream and str(substream).strip().isdigit():
            apply_substream_filter = True

        # === BASE EXAM FILTERS ===
        exam_filters = Q(university_id=university) & Q(course_id=course) & Q(stream_id=stream) & Q(active=True)

        if session:
            exam_filters &= Q(session=session)
        if studypattern:
            exam_filters &= Q(studypattern=studypattern)
        if semyear:
            exam_filters &= Q(semyear=semyear)
        if apply_substream_filter:
            exam_filters &= Q(substream_id=substream)

        examinations = Examination.objects.filter(exam_filters).select_related("subject")

        if not examinations.exists():
            return Response({"message": "No examinations found matching the criteria."}, status=404)

        # === STUDENT FILTERS ===
        student_filters = Q(course_id=course) & Q(stream_id=stream)

        if session:
            student_filters &= Q(session=session)
        if studypattern:
            student_filters &= Q(course_pattern=studypattern)
        if semyear:
            student_filters &= Q(current_semyear=semyear)
        if apply_substream_filter:
            student_filters &= Q(substream_id=substream)

        enrolled_students = Enrolled.objects.filter(student_filters).select_related('student')
        students_list = [e.student for e in enrolled_students if e.student]

        student_serializer = StudentSerializer(students_list, many=True)
        exam_serializer = ExaminationSubjectSerializer(examinations, many=True)

        return Response({
            "studentdata": student_serializer.data,
            "exams": exam_serializer.data
        }, status=200)

    except Exception as e:
        logger.error(f"Error in fetch_exam API: {str(e)}", exc_info=True)
        return Response({"error": "An error occurred while processing the request."}, status=500)


      
@api_view(['POST'])
def view_assigned_students(request):
    try:
        # Extract parameters
        params = {
            "university": request.data.get("university"),
            "course": request.data.get("course"),
            "stream": request.data.get("stream"),
            "session": request.data.get("session"),
            "studypattern": request.data.get("studypattern"),
            "semyear": request.data.get("semyear"),
            "subject": request.data.get("subject"),
        }

        # Handle substream separately
        substream = request.data.get("substream")
        if substream not in [None, "", "0", 0]:
            try:
                params["substream"] = int(substream)  # Safely cast to int
            except (ValueError, TypeError):
                logger.error(f"Invalid substream value: {substream}")
                return Response({'message': 'Invalid substream value provided.'}, status=400)

        # Remove None, empty or invalid entries
        filters = {key: value for key, value in params.items() if value not in [None, '', '0']}

        exams = Examination.objects.filter(**filters)

        if not exams.exists():
            return Response({'message': 'No results found', 'students': []}, status=404)

        formatted_data = []
        for exam in exams:
            student_data = StudentAppearingExam.objects.filter(exam=exam.id)
            if not student_data.exists():
                continue

            serializer = StudentAppearingExamSerializer(student_data, many=True)
            for record in serializer.data:
                for student_id in record['student_id']:
                    has_appeared = ExamSession.objects.filter(student_id=student_id, exam=exam.id).exists()
                    submitted_exam = Result.objects.filter(student_id=student_id, exam=exam).exists()

                    if has_appeared and submitted_exam:
                        status = "Appeared"
                    elif has_appeared:
                        status = "Ongoing Exam"
                    else:
                        status = "Not Appeared"

                    student = Student.objects.filter(id=student_id).first()
                    if student:
                        formatted_data.append({
                            'student_id': student_id,
                            'student_name': student.name,
                            'student_email': student.email,
                            'student_mobile': student.mobile,
                            'exam_id': record['exam'],
                            'examstarttime': record['examstarttime'],
                            'examendtime': record['examendtime'],
                            'examstartdate': record['examstartdate'],
                            'examenddate': record['examenddate'],
                            'id': record['id'],
                            'status': status,
                        })

        if not formatted_data:
            return Response({'message': 'No students assigned', 'students': []}, status=404)

        return Response({'message': 'Students fetched successfully', 'students': formatted_data}, status=200)

    except Exception as e:
        logger.error(f"Error fetching assigned students: {e}", exc_info=True)
        return Response({'message': 'An error occurred while fetching assigned students'}, status=500)

from django.core.mail import send_mail, EmailMessage
from threading import Thread

def send_exam_email(subject, message, recipient_list):
    """
    Sends an email asynchronously.
    """
    try:
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
        )
        email.send(fail_silently=False)
        #logger.info(f"Email sent successfully to {recipient_list}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}. Error: {e}")

@api_view(['POST'])
def resend_exam_email(request):
    data = request.data
    student_id = data.get("studentid")
    exam_id = data.get("examid")
    exam_start_date = data.get("examstartdate")
    exam_end_date = data.get("examenddate")
    exam_start_time = data.get("examstarttime")
    exam_end_time = data.get("examendtime")

    if not all([student_id, exam_id, exam_start_date, exam_end_date, exam_start_time, exam_end_time]):
        logger.error("Required fields are missing in the request.")
        return Response(
            {"error": "Student ID, Exam ID, Exam Start/End Dates, and Start/End Times are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        student = Student.objects.get(id=int(student_id))
        exam = Examination.objects.get(id=int(exam_id))
        subject = Subject.objects.get(id=exam.subject_id)

        university_name = student.university.university_name if student.university else "Your University"

        email_subject = f"{university_name} Examination - Exam Details"
        login_url = f"{settings.DOMAIN_NAME}"
        email_message = f"""Dear {student.name},

Your examination details are as follows:

Subject: {subject.name}
Exam Start Date: {exam_start_date}
Exam End Date: {exam_end_date}
Exam Start Time: {exam_start_time}
Exam End Time: {exam_end_time}

Please log in using the credentials below:
Email: {student.email}
Password: {student.mobile}

Click here to log in:
{login_url}

Best regards,
{university_name} Examination Team
"""

        Thread(target=send_exam_email, args=(email_subject, email_message, [student.email])).start()

        return Response({"message": "Email resent successfully."}, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        logger.error(f"Student with ID {student_id} does not exist.")
        return Response({"error": "Invalid student ID."}, status=status.HTTP_400_BAD_REQUEST)
    except Examination.DoesNotExist:
        logger.error(f"Examination with ID {exam_id} does not exist.")
        return Response({"error": "Invalid exam ID."}, status=status.HTTP_400_BAD_REQUEST)
    except Subject.DoesNotExist:
        logger.error(f"Subject for exam ID {exam_id} does not exist.")
        return Response({"error": "Invalid subject for the given exam."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception(f"Error occurred while resending email: {e}")
        return Response({"error": "An error occurred while resending the email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# comment by ankit on 17-09 new function created
# @api_view(['POST'])
# def save_exam_details(request):
#     try:
#         examdata = request.data.get("examsdata")
#         studentdata = request.data.get("studentdata")

#         if not examdata:
#             return Response({'message': 'Exam data is required'}, status=400)
#         if not studentdata:
#             return Response({'message': 'Student data is required'}, status=400)

#         messages = []
#         errors = []

#         for exam in examdata:
#             exam_id = exam.get("examination_id")
#             start_date = exam.get("start_date")
#             end_date = exam.get("end_date")
#             start_time = exam.get("start_time")
#             end_time = exam.get("end_time")

#             if not all([exam_id, start_date, end_date, start_time, end_time]):
#                 errors.append("Incomplete exam details provided.")
#                 continue

#             try:
#                 exam_instance = Examination.objects.get(id=exam_id)

#                 existing_exam, created = StudentAppearingExam.objects.get_or_create(
#                     exam=exam_instance,
#                     examstartdate=start_date,
#                     examenddate=end_date,
#                     examstarttime=start_time,
#                     examendtime=end_time,
#                     defaults={"student_id": []},
#                 )

#                 current_students = existing_exam.student_id or []
#                 new_student_ids = [student['id'] for student in studentdata if student['id'] not in current_students]

#                 if new_student_ids:
#                     current_students.extend(new_student_ids)
#                     existing_exam.student_id = current_students
#                     existing_exam.save()

#                     for student_id in new_student_ids:
#                         try:
#                             student_instance = Student.objects.get(id=student_id)
#                             messages.append(f"Exam details saved successfully for {student_instance.name}")

#                             email_subject = "Examination Details"
#                             login_url = f"{settings.DOMAIN_NAME}"
#                             email_message = f"""
#                             Dear {student_instance.name},

#                             You are invited to take the {exam_instance.subject.name} {exam_instance.studypattern} {exam_instance.semyear} Test.
#                             Exam Link: {login_url}
#                             User ID: {student_instance.email}
#                             Password: {student_instance.mobile}

#                             The exam is available from {start_date} to {end_date} between {start_time} and {end_time}.
#                             """

#                             Thread(
#                                 target=send_exam_email,
#                                 args=(email_subject, email_message, [student_instance.email])
#                             ).start()
#                             print(f'email send sucessfully {student_instance.email}')

#                         except Student.DoesNotExist:
#                             errors.append(f"Student with ID {student_id} not found.")
#                         except Exception as email_error:
#                             errors.append(f"Failed to send email to student ID {student_id}: {str(email_error)}")

#             except Examination.DoesNotExist:
#                 errors.append(f"Invalid exam ID: {exam_id}")
#             except Exception as e:
#                 errors.append(f"Failed to save exam details for exam ID {exam_id}: {str(e)}")

#         return Response({'messages': messages, 'errors': errors}, status=200)

#     except Exception as e:
#         return Response({'message': 'An unexpected error occurred.', 'error': str(e)}, status=500)

      
      
@api_view(['GET'])
def view_set_examination(request):
    try:
        # Extract query parameters
        query_params = {
            'university': request.query_params.get('university'),
            'course': request.query_params.get('course'),
            'stream': request.query_params.get('stream'),
            'substream': request.query_params.get('substream'),
            'session': request.query_params.get('session'),
            'studypattern': request.query_params.get('studypattern'),
            'semyear': request.query_params.get('semyear')
        }

        # Initialize the examinations queryset
        examinations = Examination.objects.all()

        # Check for empty or invalid parameters before filtering
        for param, value in query_params.items():
            if value is not None and value != '':  # Only filter if the parameter is provided and non-empty
                # Dynamically filter the queryset based on the query parameters
                # Ensure the value is a number for parameters like course, stream, university
                if param in ['university', 'course', 'stream', 'substream'] and value.isdigit():
                    examinations = examinations.filter(**{param: value})
                else:
                    # Handle case where value is invalid (non-numeric when a number is expected)
                    if param in ['university', 'course', 'stream', 'substream']:
                        logger.error(f"Invalid {param}: {value}")
                        return Response({"error": f"Invalid {param} parameter value."}, status=status.HTTP_400_BAD_REQUEST)

        # If `substream` is passed, apply that filter too
        if query_params['substream'] is not None and query_params['substream'] != '':
            examinations = examinations.filter(substream=query_params['substream'])

        # If no substream is provided, show examinations for the same course, stream, and university, but no substream
        if query_params['substream'] is None or query_params['substream'] == '':
            examinations = examinations.filter(substream__isnull=True)

        # Serialize the filtered examination data
        serializer = ExaminationSerializer(examinations, many=True)


        # Return the serialized data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        # Log the error if an exception occurs
        logger.error(f"Error occurred while fetching examinations: {str(e)}")
        
        # Return a structured error response
        return Response(
            {"error": "An error occurred while processing your request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_exam_for_student(request):
    try:
        if not (request.user.is_superuser or getattr(request.user, 'is_data_entry', False)):
            logger.warning(f"User {request.user} attempted unauthorized access to recall_exam_for_student.")
            return Response({"error": "You do not have permission to perform this action."}, status=403)
        
        student_id = request.data.get("studentid")
        exam_id = request.data.get("examid")
        
        if not student_id or not exam_id:
            logger.error("Missing required fields: studentid or examid.")
            return Response({"error": "Both studentid and examid are required."}, status=400)
        
        get_exam_data = StudentAppearingExam.objects.filter(id=exam_id).first()
        student = Student.objects.filter(id=student_id).first()
        
        if not get_exam_data:
            logger.error(f"Exam record with id {exam_id} not found.")
            return Response({"error": "Exam record not found."}, status=404)
        
        if not student:
            logger.error(f"Student record with id {student_id} not found.")
            return Response({"error": "Student record not found."}, status=404)
        
        list_of_students = get_exam_data.student_id
        
        if isinstance(list_of_students, list) and int(student_id) in list_of_students:
            university_name = student.university.university_name if student.university else "Your University"
            
            if len(list_of_students) > 1:
                list_of_students.remove(int(student_id))
                get_exam_data.student_id = list_of_students
                get_exam_data.save()
                
                email_subject = f"{university_name} Examination - Recall of Exam"
                email_message = f"An exam incorrectly assigned to you has been recalled by {university_name}."
                Thread(target=send_exam_email, args=(email_subject, email_message, [student.email])).start()
                
                return Response({"message": "Exam recalled for the student."}, status=200)
            else:
                get_exam_data.delete()
                
                email_subject = f"{university_name} Examination - Recall of Exam"
                email_message = f"An exam incorrectly assigned to you has been recalled by {university_name}."
                Thread(target=send_exam_email, args=(email_subject, email_message, [student.email])).start()
                
                return Response({"message": "Exam recalled and record deleted as only one student was present."}, status=200)
        else:
            logger.warning(f"Student ID {student_id} not found in the student list for exam {exam_id}.")
            return Response({"error": "Student ID not found in the list."}, status=404)
    except Exception as e:
        logger.error(f"Unexpected error in recall_exam_for_student: {str(e)}")
        return Response({"error": "An unexpected error occurred."}, status=500)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def reassign_student(request):
#     data = request.data
#     student_id = data.get("studentid")
#     exam_id = data.get("examid")
#     exam_start_time = data.get("examstarttime")
#     exam_end_time = data.get("examendtime")
#     exam_start_date = data.get("examstartdate")
#     exam_end_date = data.get("examenddate")

#     try:
#         exam = Examination.objects.get(id=int(exam_id))
#         subject = Subject.objects.get(id=exam.subject_id)
#     except Examination.DoesNotExist:
#         logger.error(f"Examination with ID {exam_id} does not exist.")
#         return Response({"message": "Invalid exam ID."}, status=status.HTTP_400_BAD_REQUEST)
#     except Subject.DoesNotExist:
#         logger.error(f"Subject for exam ID {exam_id} does not exist.")
#         return Response({"message": "Invalid subject for the given exam."}, status=status.HTTP_400_BAD_REQUEST)
#     except ValueError as e:
#         logger.error(f"Invalid exam ID: {exam_id}. Error: {e}")
#         return Response({"message": "Exam ID must be a valid integer."}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         new_exam = StudentAppearingExam(
#             exam=exam,
#             examstartdate=exam_start_date,
#             examenddate=exam_end_date,
#             examstarttime=exam_start_time,
#             examendtime=exam_end_time,
#             student_id=[int(student_id)]
#         )
#         new_exam.save()

#         student = Student.objects.get(id=student_id)
#         university_name = student.university.university_name if student.university else "Your University"

#         email_subject = f"{university_name} Examination - Reassign of Exam"
#         login_url = f"{settings.DOMAIN_NAME}"
#         email_message = f"""Dear {student.name},

# Your exam for {subject.name} has been reassigned by {university_name}. Please find the new details:

# Exam Start Date: {exam_start_date}
# Exam End Date: {exam_end_date}
# Exam Start Time: {exam_start_time}
# Exam End Time: {exam_end_time}

# Enter Email ID & Password in the link below:

# Email: {student.email}
# Password: {student.mobile}

# Click on the link to Login:
# {login_url}
# """
#         Thread(target=send_exam_email, args=(email_subject, email_message, [student.email])).start()

#         return Response({"message": "Exam reassigned successfully."}, status=status.HTTP_200_OK)
#     except Student.DoesNotExist:
#         logger.error(f"Student with ID {student_id} does not exist.")
#         return Response({"message": "Invalid student ID."}, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         logger.exception(f"Error occurred while reassigning exam: {e}")
#         return Response({"message": "An error occurred while reassigning the exam."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reassign_student(request):
    data = request.data
    student_id = data.get("studentid")
    exam_id = data.get("examid")
    exam_start_time = data.get("examstarttime")
    exam_end_time = data.get("examendtime")
    exam_start_date = data.get("examstartdate")
    exam_end_date = data.get("examenddate")

    logger.info("Reassign requested | student_id=%s exam_id=%s start=%s %s end=%s %s",
                student_id, exam_id, exam_start_date, exam_start_time, exam_end_date, exam_end_time)

    # 1) Load exam + subject
    try:
        exam = Examination.objects.get(id=int(exam_id))
        subject = Subject.objects.get(id=exam.subject_id)
    except Examination.DoesNotExist:
        logger.error("Invalid exam ID: %s (not found)", exam_id)
        return Response({"message": "Invalid exam ID."}, status=status.HTTP_400_BAD_REQUEST)
    except Subject.DoesNotExist:
        logger.error("Subject not found for exam ID: %s", exam_id)
        return Response({"message": "Invalid subject for the given exam."}, status=status.HTTP_400_BAD_REQUEST)
    except (TypeError, ValueError) as e:
        logger.error("Invalid exam ID (type/format): %s | %s", exam_id, e)
        return Response({"message": "Exam ID must be a valid integer."}, status=status.HTTP_400_BAD_REQUEST)

    # 2) Create new StudentAppearingExam
    try:
        new_exam = StudentAppearingExam(
            exam=exam,
            examstartdate=exam_start_date,
            examenddate=exam_end_date,
            examstarttime=exam_start_time,
            examendtime=exam_end_time,
            student_id=[int(student_id)],
        )
        new_exam.save()
        logger.info("StudentAppearingExam created | id=%s student_id=%s exam_id=%s",
                    getattr(new_exam, "id", None), student_id, exam_id)
    except Exception as e:
        logger.exception("Failed to create StudentAppearingExam | %s", e)
        return Response({"message": "An error occurred while reassigning the exam."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 3) Load student
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        logger.error("Invalid student ID: %s", student_id)
        return Response({"message": "Invalid student ID."}, status=status.HTTP_400_BAD_REQUEST)

    university_name = student.university.university_name if getattr(student, "university", None) else "Your University"
    login_url = f"{settings.DOMAIN_NAME}"

    # 4) Send Email (threaded same as you had)
    email_subject = f"{university_name} Examination - Reassign of Exam"
    email_message = f"""Dear {student.name},

Your exam for {subject.name} has been reassigned by {university_name}. Please find the new details:

Exam Start Date: {exam_start_date}
Exam End Date: {exam_end_date}
Exam Start Time: {exam_start_time}
Exam End Time: {exam_end_time}

Enter Email ID & Password in the link below:

Email: {student.email}
Password: {student.mobile}

Click on the link to Login:
{login_url}
"""
    try:
        Thread(target=send_exam_email, args=(email_subject, email_message, [student.email])).start()
        logger.info("Reassign email queued | to=%s", student.email)
    except Exception as e:
        logger.exception("Failed to queue email | to=%s | %s", student.email, e)

    # 5) Send WhatsApp via AiSensy
    #    Your template: Hello {{1}}, Your {{2}} test has been reassigned. Portal: {{3}} Credentials: {{4}} New schedule: {{5}}
    try:
        params = build_exam_reassign_params(
            student_name=student.name or "Student",
            subject_name=subject.name,
            studypattern=getattr(exam, "studypattern", "") or getattr(student, "studypattern", "") or "",
            semyear=getattr(exam, "semyear", "") or getattr(student, "semyear", "") or "",
            portal_url=login_url,
            email=student.email or "",
            mobile=student.mobile or "",
            start_date=exam_start_date,
            end_date=exam_end_date,
            start_time=exam_start_time,
            end_time=exam_end_time,
        )

        result = send_aisensy_message(
            phone=student.mobile,
            template_params=params,
            campaign_key="EXAM_REASSIGN",
            source="api.reassign_student",
        )

        logger.info("WhatsApp sent | student_id=%s dest=%s campaign=%s provider_id=%s",
                    student_id,
                    result.get("_normalized_destination"),
                    result.get("_campaign_name"),
                    result.get("data", {}).get("messageId") or result.get("messageId"),
        )
    except AiSensyError as e:
        logger.error("WhatsApp send failed (AiSensyError) | student_id=%s | %s", student_id, e)
        # Do not fail the whole API because WA failed—email + DB already done
    except Exception as e:
        logger.exception("WhatsApp send failed (Unexpected) | student_id=%s | %s", student_id, e)

    return Response({"message": "Exam reassigned successfully."}, status=status.HTTP_200_OK)

#added by ankit on 23-09-2025 for send whatsapp message also testing is pending

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def reassign_student(request):
#     """
#     Reassign a single student to a specific exam window (start/end date & time).
#     - No get_or_create: we first try to find the exact window, then update or create.
#     - Mirrors save_exam_details response shape: {'messages': [...], 'errors': [...]}
#     - Sends Email + WhatsApp notifications using your existing helpers.
#     """
#     data = request.data or {}

#     messages, errors = [], []

#     # ---- Required fields
#     student_id       = data.get("studentid")
#     exam_id          = data.get("examid")
#     exam_start_date  = data.get("examstartdate")
#     exam_end_date    = data.get("examenddate")
#     exam_start_time  = data.get("examstarttime")
#     exam_end_time    = data.get("examendtime")

#     # Validate presence
#     required = {
#         "studentid": student_id,
#         "examid": exam_id,
#         "examstartdate": exam_start_date,
#         "examenddate": exam_end_date,
#         "examstarttime": exam_start_time,
#         "examendtime": exam_end_time,
#     }
#     missing = [k for k, v in required.items() if not v]
#     if missing:
#         return Response(
#             {"messages": [], "errors": [f"Missing fields: {', '.join(missing)}"]},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     # Type cast IDs
#     try:
#         student_id = int(student_id)
#         exam_id = int(exam_id)
#     except (TypeError, ValueError):
#         return Response(
#             {"messages": [], "errors": ["studentid and examid must be valid integers."]},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     # ---- Fetch core objects
#     try:
#         exam = Examination.objects.get(id=exam_id)
#     except Examination.DoesNotExist:
#         errors.append(f"Invalid exam ID: {exam_id}")
#         return Response({"messages": messages, "errors": errors}, status=200)

#     try:
#         subject = Subject.objects.get(id=exam.subject_id)
#     except Subject.DoesNotExist:
#         errors.append(f"Invalid subject for the given exam ID: {exam_id}")
#         return Response({"messages": messages, "errors": errors}, status=200)

#     try:
#         student = Student.objects.get(id=student_id)
#     except Student.DoesNotExist:
#         errors.append(f"Student with ID {student_id} not found.")
#         return Response({"messages": messages, "errors": errors}, status=200)

#     # ---- Main logic (NO get_or_create)
#     try:
#         with transaction.atomic():
#             # Try to find existing window for this exam + exact schedule
#             existing_exam = StudentAppearingExam.objects.filter(
#                 exam=exam,
#                 examstartdate=exam_start_date,
#                 examenddate=exam_end_date,
#                 examstarttime=exam_start_time,
#                 examendtime=exam_end_time,
#             ).first()

#             if existing_exam:
#                 # Update student list if needed
#                 current_students = existing_exam.student_id or []
#                 if student_id not in current_students:
#                     current_students.append(student_id)
#                     existing_exam.student_id = current_students
#                     existing_exam.save(update_fields=["student_id"])
#                     messages.append(f"Exam details saved successfully for {student.name}")
#                 else:
#                     messages.append(f"Student {student.name} is already assigned to this exam window.")
#             else:
#                 # Create a fresh row for this window
#                 new_exam = StudentAppearingExam(
#                     exam=exam,
#                     examstartdate=exam_start_date,
#                     examenddate=exam_end_date,
#                     examstarttime=exam_start_time,
#                     examendtime=exam_end_time,
#                     student_id=[student_id],
#                 )
#                 new_exam.save()
#                 messages.append(f"Exam details saved successfully for {student.name}")

#             # ---- Notifications (same pattern as save_exam_details)
#             try:
#                 university_name = student.university.university_name if getattr(student, "university", None) else "Your University"
#                 email_subject = f"{university_name} Examination - Reassign of Exam"
#                 login_url = f"{settings.DOMAIN_NAME}"
#                 email_message = f"""Dear {student.name},

# Your exam for {subject.name} has been reassigned by {university_name}. Please find the new details:

# Exam Start Date: {exam_start_date}
# Exam End Date: {exam_end_date}
# Exam Start Time: {exam_start_time}
# Exam End Time: {exam_end_time}

# Enter Email ID & Password in the link below:

# Email: {student.email}
# Password: {student.mobile}

# Click on the link to Login:
# {login_url}
# """
#                 # Email async
#                 Thread(target=send_exam_email, args=(email_subject, email_message, [student.email])).start()

#                 # WhatsApp via your AiSensy helper
#                 try:
#                     values = build_exam_details_values(
#                         student=student,
#                         exam=exam,
#                         login_url=login_url,
#                         start_date=exam_start_date,
#                         end_date=exam_end_date,
#                         start_time=exam_start_time,
#                         end_time=exam_end_time,
#                     )
#                     send_whatsapp_using_template(
#                         template_key="exam_details",
#                         phone=student.mobile,
#                         name=student.name,
#                         values=values,
#                     )
#                 except AiSensyError as werr:
#                     errors.append(f"Failed to send WhatsApp to student ID {student_id}: {str(werr)}")

#             except Exception as notif_err:
#                 # Don't rollback the assignment if notifications fail
#                 errors.append(f"Notification error for {student.name}: {str(notif_err)}")

#     except Exception as e:
#         logger.exception(f"Error occurred while reassigning exam: {e}")
#         errors.append("An error occurred while reassigning the exam.")

#     return Response({"messages": messages, "errors": errors}, status=200)


@api_view(['GET'])
def get_course_duration(request):
    try:
        # Extract query parameters
        university_id = request.query_params.get('university')
        course_id = request.query_params.get('course')
        stream_id = request.query_params.get('stream')

        # Validate and fetch University
        university = University.objects.filter(id=university_id).first()
        if not university:
            logger.error(f"Invalid university ID: {university_id}")
            return Response({"error": "Invalid university ID."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and fetch Course
        course = Course.objects.filter(id=course_id, university=university).first()
        if not course:
            logger.error(f"Invalid course ID: {course_id} for university ID: {university_id}")
            return Response({"error": "Invalid course for the given university."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and fetch Stream
        stream = Stream.objects.filter(id=stream_id, course=course).first()
        if not stream:
            logger.error(f"Invalid stream ID: {stream_id} for course ID: {course_id}")
            return Response({"error": "Invalid stream for the given course."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch semester information from the Stream model
        sem = stream.sem
        #logger.info(f"Semester retrieved for stream ID {stream_id}: {sem}")

        # Return semester in the response
        return Response({"stream": stream.name, "sem": sem}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception("An unexpected error occurred in get_course_duration.")
        return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
@api_view(['POST'])
def student_login(request):
    try:
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            logger.error("Email or password not provided")
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(email=email)
        except Student.DoesNotExist:
            logger.error(f"Student with email {email} not found")
            return Response({"error": "Invalid email or password."}, status=status.HTTP_404_NOT_FOUND)

        # Authenticate student (assuming password is stored as mobile number)
        if password != student.mobile:
            logger.error(f"Invalid password attempt for student {email}")
            return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT Token
        try:
            token = get_tokens_for_user(student)  # Ensure this function is working
        except Exception as e:
            logger.error(f"Error generating token for student {email}: {str(e)}")
            return Response({"error": "An error occurred while generating the token."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Fetch student exams by checking if student.id is in the student_id JSON list
        try:
            exams = StudentAppearingExam.objects.filter(student_id__contains=[student.id])
        except Exception as e:
            logger.error(f"Error fetching exams for student {email}: {str(e)}")
            return Response({"error": "An error occurred while fetching exams."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not exams.exists():
            return Response({
                "message": "No exams found for this student.",
                "token": token
            }, status=status.HTTP_200_OK)

        # Prepare exam-related data
        exam_details = []
        examination_data = []

        for exam in exams:
            try:
                exam_details.append({
                    "exam_id": exam.exam.id,
                    "examstartdate": exam.examstartdate,
                    "examenddate": exam.examenddate,
                    "examstarttime": exam.examstarttime,
                    "examendtime": exam.examendtime
                })
            except Exception as e:
                logger.error(f"Error fetching exam details for exam {exam.id}: {str(e)}")
                continue  # Skip this exam if it's missing details

            try:
                examination = exam.exam
                examination_data.append({
                    "id": examination.id,
                    "course_id": examination.course.id,
                    "stream_id": examination.stream.id,
                    "subject_id": examination.subject.id,
                    "studypattern": examination.studypattern,
                    "semyear": examination.semyear,
                    "substream_id": examination.substream.id if examination.substream else None,
                    "course_name": examination.course.name,
                    "stream_name": examination.stream.name,
                    "subject_name": examination.subject.name,
                    "substream_name": examination.substream.name if examination.substream else None
                })
            except Exception as e:
                logger.error(f"Error fetching examination data for exam {exam.id}: {str(e)}")
                continue  # Skip this examination if it's missing related data

        return Response({
            "message": "Login Successful",
            "token": token,
            "student_id": student.id,
            "exam_details": exam_details,
            "examination_data": examination_data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"An error occurred while processing the student login: {str(e)}")
        return Response({"error": f"An internal server error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_excel_for_set_exam_for_subject(request):
    try:
        # Define the path to the predefined Excel file
        file_name = "SubjectWiseQuestionTemplate.xlsx"
        file_path = os.path.join('media', 'Download_Excel_Format', file_name)

        # Check if the file exists
        if not os.path.exists(file_path):
            logger.error("File not found: %s", file_path)
            return Response(
                {"error": "The requested Excel file does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serve the file as a response
        response = FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=file_name,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        return response

    except Exception as e:
        # Log any unexpected errors
        logger.error("Error while serving Excel file: %s", str(e))
        return Response(
            {"error": "An error occurred while processing the request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_subjects(request):
    try:
        stream = request.query_params.get('stream')
        substream = request.query_params.get('substream')  # Can be "", None, or valid ID
        semyear = request.query_params.get('semyear')

        if not stream:
            return Response({'error': "Stream parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not semyear:
            return Response({'error': "Semester/Year parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Base filters
        filters = {'stream__id': stream, 'semyear': semyear}

        # Filter by substream only if passed and valid
        if substream not in [None, '', 'null']:
            filters['substream__id'] = substream
        # else: no substream filter applied to include all with/without substream

        subjects = Subject.objects.filter(**filters).values(
            'id', 'name', 'code', 'stream', 'substream', 'studypattern', 'semyear'
        )

        if not subjects.exists():
            return Response({'message': "No subjects found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({'subjects': list(subjects)}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Error in get_all_subjects: {str(e)}")
        return Response({'error': "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def fetch_questions_based_on_exam_id(request):
    """
    Fetch questions for a given exam ID.
    """
    exam_id = request.query_params.get('exam_id')
    if not exam_id:
        logger.error("Exam ID is missing in the request.")
        return Response({"error": "Exam ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        questions = Questions.objects.filter(exam_id=exam_id)
        if not questions.exists():
            #logger.info(f"No questions found for Exam ID: {exam_id}")
            return Response({"message": "No questions found for the given Exam ID."}, status=status.HTTP_404_NOT_FOUND)
        
        # Prepare response data
        data = []
        for question in questions:
            data.append({
                "id": question.id,
                "exam_id": question.exam_id,
                "question": question.question,
                "image": question.image,
                "type": question.type,
                "marks": question.marks,
                "options": [
                    question.option1, question.option2, question.option3,
                    question.option4
                ],
                "short_answer": question.shortanswer,
                "answer": question.answer,
                "difficulty_level": question.difficultylevel
            })
        
        #logger.info(f"Successfully fetched {len(data)} questions for Exam ID: {exam_id}")
        return Response({"questions": data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching questions for Exam ID {exam_id}: {str(e)}")
        return Response({"error": "An error occurred while fetching questions."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

   
@api_view(['POST'])
def save_all_questions_answers(request):
    try:
        data = request.data
        student_id = data.get("student_id")
        exam_id = data.get("exam_id")
        questions = data.get("questions")

        #logger.info(f"Received submission for student_id={student_id}, exam_id={exam_id}")

        # Validate presence of required fields
        if not student_id or not exam_id or not questions:
            logger.error("Missing required fields: student_id, exam_id, or questions.")
            return Response({
                "error": "Missing required fields: student_id, exam_id, or questions."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch related instances
        try:
            student_instance = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            logger.error(f"Student with id {student_id} not found.")
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            exam_instance = Examination.objects.get(id=exam_id)
        except Examination.DoesNotExist:
            logger.error(f"Examination with id {exam_id} not found.")
            return Response({"error": "Examination not found."}, status=status.HTTP_404_NOT_FOUND)

        saved_answers = []

        for question in questions:
            question_id = question.get("id")
            submitted_answer = question.get("submitted_answer")
            
            print('submitted_answer',submitted_answer)

            if not question_id or submitted_answer is None:
                logger.warning(f"Skipping question with incomplete data: {question}")
                continue

            try:
                question_instance = Questions.objects.get(id=question_id)
            except Questions.DoesNotExist:
                logger.warning(f"Question with ID {question_id} does not exist. Skipping.")
                continue

            # Get correct answer and marks
            correct_answer = question_instance.answer.lower().strip() if question_instance.answer else ""
            
            print('submitted_answer correct_answer ',correct_answer,submitted_answer)
            
            submitted_value = submitted_answer.lower().strip()
            marks = question_instance.marks or "0"

            # Evaluate
            if correct_answer == submitted_value:
                result = "Right"
                marks_obtained = marks
            else:
                result = "Wrong"
                marks_obtained = "0"

            # Save submission
            SubmittedExamination.objects.create(
                student=student_instance,
                exam=exam_instance,
                question=str(question_id),  # Question ID stored as CharField
                type=question_instance.type,
                marks=marks,
                marks_obtained=marks_obtained,
                submitted_answer=submitted_answer,
                answer=correct_answer,
                result=result,
            )

            #logger.info(f"Saved answer for question_id={question_id}: {result}, Marks={marks_obtained}")

            saved_answers.append({
                "question_id": question_id,
                "result": result,
                "marks_obtained": marks_obtained,
            })

        #logger.info(f"Successfully saved {len(saved_answers)} answers for student {student_id}.")

        return Response({
            "message": "Submitted answers saved successfully.",
            "saved_answers": saved_answers
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.exception(f"Unexpected error while saving answers: {str(e)}")
        return Response({
            "error": "An internal server error occurred."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_result_to_show_based_on_subject(request):
    try:
        # Extract query parameters
        query_params = {
            'university': request.query_params.get('university'),
            'course': request.query_params.get('course'),
            'stream': request.query_params.get('stream'),
            'substream': request.query_params.get('substream'),
            'session': request.query_params.get('session'),
            'studypattern': request.query_params.get('studypattern'),
            'semyear': request.query_params.get('semyear')
        }

        # Filter examinations based on the provided query parameters
        examinations = Examination.objects.all()
        for param, value in query_params.items():
            if value:
                examinations = examinations.filter(**{param: value})

        # Construct response data
        response_data = []
        for exam in examinations:
            # Fetch all student-exam records related to this exam
            student_exam_entries = StudentAppearingExam.objects.filter(exam=exam)

            # Extract student IDs from all records
            student_ids = []
            for entry in student_exam_entries:
                if entry.student_id:  # Ensure it's not empty
                    student_ids.extend(entry.student_id)

            # Remove duplicates if necessary
            student_ids = list(set(student_ids))

            # Use the first StudentAppearingExam entry to get exam timing details
            student_exam_details = student_exam_entries.first()

            response_data.append({
                "id": exam.id,
                "subject": exam.subject.id if exam.subject else None,
                "subject_name": exam.subject.name if exam.subject else None,
                "exam_start_date": student_exam_details.examstartdate if student_exam_details else None,
                "exam_end_date": student_exam_details.examenddate if student_exam_details else None,
                "exam_start_time": student_exam_details.examstarttime if student_exam_details else None,
                "exam_end_time": student_exam_details.examendtime if student_exam_details else None,
                "total_questions": exam.totalquestions,
                "total_marks": exam.totalmarks,
                "student_ids": student_ids  # Include student IDs in the response
            })

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error occurred while fetching examinations: {str(e)}")
        return Response(
            {"error": "An error occurred while processing your request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


from openpyxl import Workbook
from openpyxl.styles import Font

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_to_excel(request):
    """
    Export data to Excel based on filters provided in the request.
    """
    try:
        # Extract filters from POST data
        university = request.data.get("university")
        course = request.data.get("course")
        stream = request.data.get("stream")
        session = request.data.get("session")
        studypattern = request.data.get("studypattern")
        semyear = request.data.get("semyear")
        substream = request.data.get("substream")

        #logger.info(f"Received export request with filters: {request.data}")

        # Validate required filters
        if not university or not course or not stream:
            return Response({'message': 'Missing required fields: university, course, stream'}, status=400)

        # Build query filters dynamically
        filters = Q(university=university) & Q(course=course) & Q(stream=stream)
        if session:
            filters &= Q(session=session)
        if studypattern:
            filters &= Q(studypattern=studypattern)
        if semyear:
            filters &= Q(semyear=semyear)
        if substream:
            filters &= Q(substream=substream)

        # Fetch relevant data
        fetch_exams = Examination.objects.filter(filters)
        if not fetch_exams.exists():
            logger.warning("No exams found for the given filters.")
            return Response({'message': 'No results found'}, status=404)

        formatted_data = []
        for exam in fetch_exams:
            subject = Subject.objects.filter(id=exam.subject_id).first()
            student_data = StudentAppearingExam.objects.filter(exam=exam.id)

            for student_record in student_data:
                for student_id in student_record.student_id:
                    student = Student.objects.filter(id=student_id).first()
                    status = "Not Appeared"
                    result_data = Result.objects.filter(student_id=student_id, exam=exam.id).first()

                    if result_data:
                        status = "Appeared"
                        marks_obtained = result_data.score
                        result = result_data.result
                    else:
                        marks_obtained = ''
                        result = ''

                    formatted_data.append({
                        'University': university,
                        'Course': course,
                        'Stream': stream,
                        'Substream': substream if substream else '',
                        'Session': session,
                        'Study Pattern': studypattern,
                        'Semester/Year': semyear,
                        'Subject Name': subject.name if subject else '',
                        'Student Name': student.name if student else '',
                        'Marks Obtained': marks_obtained,
                        'Result': result,
                        'Status': status
                    })

        if not formatted_data:
            logger.warning("No student data found to export.")
            return Response({'message': 'No data available for export'}, status=400)

        # Generate Excel file
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Exported Data"

        # Write headers
        headers = list(formatted_data[0].keys())
        for col_num, header in enumerate(headers, 1):
            cell = sheet.cell(row=1, column=col_num)
            cell.value = header
            cell.font = Font(bold=True)

        # Write data rows
        for row_num, row_data in enumerate(formatted_data, start=2):
            for col_num, header in enumerate(headers, start=1):
                sheet.cell(row=row_num, column=col_num).value = row_data[header]

        # Create response with HttpResponse
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = 'attachment; filename="exported_data.xlsx"'
        workbook.save(response)

        #logger.info("Excel file generated and sent successfully.")
        return response

    except Exception as e:
        logger.exception(f"Error occurred while exporting data: {str(e)}")
        return Response({'message': 'An internal server error occurred.'}, status=500)

from django.db.models import Sum, Count
@api_view(['POST'])
def generate_result(request):
    try:
        # Extract student_id and exam_id from the request
        student_id = request.data.get('student_id')
        exam_id = request.data.get('exam_id')

        # Validate input
        if not student_id or not exam_id:
            logger.error("Student ID or Exam ID is missing.")
            return Response({"error": "Student ID and Exam ID are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch submitted examinations for the student and exam
        submitted_exams = SubmittedExamination.objects.filter(student_id=student_id, exam_id=exam_id)
        if not submitted_exams.exists():
            logger.error(f"No submitted examinations found for student {student_id} and exam {exam_id}.")
            return Response({"error": "No submitted examinations found."}, status=status.HTTP_404_NOT_FOUND)

        # Calculate total marks obtained and attempted questions
        total_marks_obtained = submitted_exams.aggregate(total_marks=Sum('marks_obtained'))['total_marks'] or 0
        attempted_questions = submitted_exams.exclude(submitted_answer__isnull=True).exclude(submitted_answer="").count()

        # Get the total questions count
        total_questions = submitted_exams.count()

        # Fetch examination details
        exam = Examination.objects.get(id=exam_id)
        total_marks = int(exam.totalmarks)
        passing_marks = int(exam.passingmarks) if exam.passingmarks else 0

        # Calculate percentage
        percentage = (int(total_marks_obtained) / total_marks) * 100 if total_marks > 0 else 0

        # Determine result
        result_status = "Pass" if total_marks_obtained >= passing_marks else "Fail"

        # Create or update the Result entry
        result, created = Result.objects.update_or_create(
            student_id=student_id,
            exam_id=exam_id,
            defaults={
                "total_question": total_questions,
                "attempted": attempted_questions,
                "total_marks": total_marks,
                "score": int(total_marks_obtained),
                "percentage": round(percentage, 2),
                "result": result_status,
                "created_by": request.user.username if request.user else None,
                "modified_by": request.user.username if request.user else None,
            },
        )

        #logger.info(f"Result {'created' if created else 'updated'} successfully for student {student_id} and exam {exam_id}.")
        return Response({
            "message": "Result generated successfully.",
            "result_id": result.id,
            "percentage": round(percentage, 2),
            "result_status": result_status
        }, status=status.HTTP_200_OK)

    except Examination.DoesNotExist:
        logger.error(f"Examination with ID {exam_id} does not exist.")
        return Response({"error": "Examination not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.exception("An error occurred while generating the result.")
        return Response({"error": "An unexpected error occurred.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def show_result(request):
    try:
        # Get query parameters
        student_id = request.query_params.get('student_id')
        exam_id = request.query_params.get('exam_id')

        # Validate query parameters
        if not student_id or not exam_id:
            logger.error("Student ID or Exam ID is missing.")
            return Response({"error": "Student ID and Exam ID are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the result based on student_id and exam_id
        result = Result.objects.filter(student_id=student_id, exam_id=exam_id).select_related('student', 'exam').first()
        if not result:
            logger.error(f"No result found for student ID {student_id} and exam ID {exam_id}.")
            return Response({"error": "No result found."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch student details
        student = result.student
        response_data = {
            "student_name": student.name,
            "email": student.email,
            "enrollment_id": student.enrollment_id,
            "exam_id": result.exam.id,
            "total_questions": result.total_question,
            "total_marks": result.total_marks,
            "score": result.score,
            "percentage": result.percentage,
            "result_status": result.result,
        }

        #logger.info(f"Result fetched successfully for student {student_id} and exam {exam_id}.")
        return Response({"message": "Result fetched successfully.", "data": response_data}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception("An error occurred while fetching the result.")
        return Response({"error": "An unexpected error occurred.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_university(request, university_id):
    try:
        university = University.objects.get(id=university_id)
        if Course.objects.filter(university=university).exists():
            return Response({"message": "Cannot delete university as it has associated courses."}, status=status.HTTP_400_BAD_REQUEST)
        university_name = university.university_name
        university.delete()
        #logger.info(f"University '{university_name}' with ID {university_id} deleted successfully.")
        return Response({"message": f"University '{university_name}' deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except University.DoesNotExist:
        logger.warning(f"Attempt to delete non-existent university with ID {university_id}.")
        return Response({"message": "University not found."}, status=status.HTTP_404_NOT_FOUND)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_course(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        if Stream.objects.filter(course=course).exists():
            return Response({"message": "Cannot delete course as it has associated streams."}, status=status.HTTP_400_BAD_REQUEST)
        course_name = course.name
        course.delete()
        #logger.info(f"Course '{course_name}' with ID {course_id} deleted successfully.")
        return Response({"message": f"Course '{course_name}' deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Course.DoesNotExist:
        logger.warning(f"Attempt to delete non-existent course with ID {course_id}.")
        return Response({"message": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_stream(request, stream_id):
    try:
        stream = Stream.objects.get(id=stream_id)
        if SubStream.objects.filter(stream=stream).exists() or Subject.objects.filter(stream=stream).exists():
            return Response({"message": "Cannot delete stream as it has associated substreams or subjects."}, status=status.HTTP_400_BAD_REQUEST)
        stream_name = stream.name
        stream.delete()
        #logger.info(f"Stream '{stream_name}' with ID {stream_id} deleted successfully.")
        return Response({"message": f"Stream '{stream_name}' deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Stream.DoesNotExist:
        logger.warning(f"Attempt to delete non-existent stream with ID {stream_id}.")
        return Response({"message": "Stream not found."}, status=status.HTTP_404_NOT_FOUND)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_substream(request, substream_id):
    try:
        substream = SubStream.objects.get(id=substream_id)
        if Subject.objects.filter(substream=substream).exists():
            return Response({"message": "Cannot delete substream as it has associated subjects."}, status=status.HTTP_400_BAD_REQUEST)
        substream_name = substream.name
        substream.delete()
        #logger.info(f"SubStream '{substream_name}' with ID {substream_id} deleted successfully.")
        return Response({"message": f"SubStream '{substream_name}' deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except SubStream.DoesNotExist:
        logger.warning(f"Attempt to delete non-existent substream with ID {substream_id}.")
        return Response({"message": "SubStream not found."}, status=status.HTTP_404_NOT_FOUND)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_subject(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
        subject_name = subject.name
        subject.delete()
        #logger.info(f"Subject '{subject_name}' with ID {subject_id} deleted successfully.")
        return Response({"message": f"Subject '{subject_name}' deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Subject.DoesNotExist:
        logger.warning(f"Attempt to delete non-existent subject with ID {subject_id}.")
        return Response({"message": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_substreams_with_id_by_university_course_stream(request):
    university_name = request.query_params.get('university')
    course_name = request.query_params.get('course')
    stream_name = request.query_params.get('stream')
    if not university_name or not course_name or not stream_name:
        return Response({"error": "University name, course name, and stream name are required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        university = University.objects.get(university_name=university_name)
    except University.DoesNotExist:
        return Response({"error": "University not found."}, status=status.HTTP_404_NOT_FOUND)
    try:
        course = Course.objects.get(university=university, name=course_name)
    except Course.DoesNotExist:
        return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
    try:
        stream = Stream.objects.get(course=course, name=stream_name)
    except Stream.DoesNotExist:
        return Response({"error": "Stream not found."}, status=status.HTTP_404_NOT_FOUND)
    substreams = SubStream.objects.filter(stream=stream)
    substream_list = [{"id": substream.id, "name": substream.name} for substream in substreams]
    return Response(substream_list, status=status.HTTP_200_OK)
  
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subjects_by_stream(request, stream_id):
    try:
        subjects = Subject.objects.filter(stream_id=stream_id)
        if not subjects.exists():
            return Response({"status": "error", "message": "No subjects found for the given stream."}, status=status.HTTP_404_NOT_FOUND)
        subject_data = [
            {   "id":subject.id,
                "studypattern": subject.studypattern,
                "semyear": subject.semyear,
                "name": subject.name,
                "code": subject.code
            }
            for subject in subjects
        ]
        return Response({"status": "success", "data": subject_data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching subjects for stream_id {stream_id}: {str(e)}")
        return Response({"status": "error", "message": "Something went wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
from django.db.models import OuterRef, Subquery

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_of_all_registered_student(request):
    try:
        # Subquery to grab the most recent Enrolled row per student
        latest_enrolled = Enrolled.objects.filter(student_id=OuterRef('pk')).order_by('-id')

        # Annotate students with fields from their latest enrolled row
        students = (
            Student.objects
            .filter(archive=False,is_approve=True)
            .select_related('university','user')
            .annotate(
                ann_current_semyear = Subquery(latest_enrolled.values('current_semyear')[:1]),
                ann_total_semyear   = Subquery(latest_enrolled.values('total_semyear')[:1]),
                ann_entry_mode      = Subquery(latest_enrolled.values('entry_mode')[:1]),
                ann_course_pattern  = Subquery(latest_enrolled.values('course_pattern')[:1]),
            )
            .order_by('-id')
        )

        data = []
        for s in students:
            # Determine Source (is_quick_register condition)
            source = 'SR' if not getattr(s, 'is_quick_register', False) else 'QR'
            user_id = s.user.id if s.user else None
            data.append({
                "id": s.id,
                "user_id": user_id,  # Added user_id here
                "current_semyear": s.ann_current_semyear or "",
                "totalsemyear": s.ann_total_semyear or "",          # <-- added
                "enrollment_id": s.enrollment_id,
                "student_name": s.name,
                "student_email":s.email,
                "university_name": getattr(s.university, 'university_name', "") if s.university else "",
                "source": source,
                "study_pattern_mode": s.ann_course_pattern or "",
                "entry_mode": s.ann_entry_mode or "",
                "enrollment_date": s.enrollment_date.strftime('%Y-%m-%d') if s.enrollment_date else ""
            })

        return Response({"status": "success", "data": data}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error fetching students: {str(e)}")
        return Response({"status": "error", "message": "Something went wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# def get_student_enroll_to_next_year(request, id):
#     try:
#         student = Student.objects.get(id=id)
#         enrolled = Enrolled.objects.filter(student=student).first()

#         if not enrolled:
#             return Response({"status": "error", "message": "Student enrollment not found!"}, status=status.HTTP_404_NOT_FOUND)

#         if request.method == "GET":
#             if int(enrolled.current_semyear) == int(enrolled.total_semyear):
#                 return Response({"status": "error", "message": "Student is in Final Semester / Year!"}, status=status.HTTP_400_BAD_REQUEST)
#             elif int(enrolled.current_semyear) < int(enrolled.total_semyear):
#                 student_data = {
#                     "id": student.id,
#                     "total_semyear": enrolled.total_semyear,
#                     "course": enrolled.course.name if enrolled.course else "",  # Course Name
#                     "stream": enrolled.stream.name if enrolled.stream else "",  # Stream Name
#                     "current_semyear": enrolled.current_semyear,
#                     "next_semyear": int(enrolled.current_semyear) + 1,
#                 }
#                 #logger.info(f"GET Request - Student ID: {id}, Response: {student_data}")
#                 return Response({"status": "success", "data": student_data}, status=status.HTTP_200_OK)

#         if request.method == "POST":
#             if int(enrolled.current_semyear) == int(enrolled.total_semyear):
#                 return Response({"status": "error", "message": "Student is already in Final Semester / Year!"}, status=status.HTTP_400_BAD_REQUEST)

#             new_semyear = int(enrolled.current_semyear) + 1
#             enrolled.current_semyear = str(new_semyear)
#             enrolled.save()

#             response_data = {
#                 "id": student.id,
#                 "message": f"Student has been enrolled to Semester/Year {new_semyear}",
#                 "updated_current_semyear": new_semyear,
#                 "total_semyear": enrolled.total_semyear,
#                 "course": enrolled.course.name if enrolled.course else "",  # Course Name
#                 "stream": enrolled.stream.name if enrolled.stream else "",  # Stream Name
#             }

#             #logger.info(f"POST Request - Student ID: {id}, New Semester/Year: {new_semyear}, Response: {response_data}")
#             return Response({"status": "success", "data": response_data}, status=status.HTTP_200_OK)

#     except Student.DoesNotExist:
#         logger.error(f"Student with ID {id} not found!")
#         return Response({"status": "error", "message": "Student not Found!"}, status=status.HTTP_404_NOT_FOUND)

#     except Exception as e:
#         logger.error(f"Error processing request for student {id}: {str(e)}")
#         return Response({"status": "error", "message": "Something went wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# commit on 05-11-2025
# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# def get_student_enroll_to_next_year(request, id):
#     try:
#         student = Student.objects.get(id=id)
#         enrolled = Enrolled.objects.filter(student=student).first()

#         if not enrolled:
#             logger.error(f"Student enrollment not found for student ID: {id}")
#             return Response({"status": "error", "message": "Student enrollment not found!"}, status=status.HTTP_404_NOT_FOUND)

#         # Check if user is superadmin
#         is_superadmin = request.user.is_superuser
        
#         if request.method == "GET":
#             if int(enrolled.current_semyear) == int(enrolled.total_semyear):
#                 logger.warning(f"Student {id} is in final semester/year: {enrolled.current_semyear}")
#                 return Response({"status": "error", "message": "Student is in Final Semester / Year!"}, status=status.HTTP_400_BAD_REQUEST)
#             elif int(enrolled.current_semyear) < int(enrolled.total_semyear):
                
#                 # Check payment status for non-superadmin users
#                 payment_validation = validate_payment_status(student, enrolled.current_semyear, is_superadmin)
#                 if not payment_validation["is_eligible"] and not is_superadmin:
#                     return Response({
#                         "status": "error", 
#                         "message": payment_validation["message"],
#                         "validation_details": payment_validation
#                     }, status=status.HTTP_400_BAD_REQUEST)

#                 student_data = {
#                     "id": student.id,
#                     "total_semyear": enrolled.total_semyear,
#                     "course": enrolled.course.name if enrolled.course else "",
#                     "stream": enrolled.stream.name if enrolled.stream else "",
#                     "current_semyear": enrolled.current_semyear,
#                     "next_semyear": int(enrolled.current_semyear) + 1,
#                     "payment_validation": payment_validation,
#                     "is_superadmin": is_superadmin
#                 }
                
#                 logger.info(f"GET Request - Student ID: {id}, Current Semester: {enrolled.current_semyear}, Payment Status: {payment_validation['status']}")
#                 return Response({"status": "success", "data": student_data}, status=status.HTTP_200_OK)

#         if request.method == "POST":
#             if int(enrolled.current_semyear) == int(enrolled.total_semyear):
#                 logger.warning(f"POST - Student {id} is already in final semester/year: {enrolled.current_semyear}")
#                 return Response({"status": "error", "message": "Student is already in Final Semester / Year!"}, status=status.HTTP_400_BAD_REQUEST)

#             # Validate payment status for non-superadmin users
#             payment_validation = validate_payment_status(student, enrolled.current_semyear, is_superadmin)
#             if not payment_validation["is_eligible"] and not is_superadmin:
#                 logger.warning(f"POST - Payment validation failed for student {id}: {payment_validation['message']}")
#                 return Response({
#                     "status": "error", 
#                     "message": payment_validation["message"],
#                     "validation_details": payment_validation
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             # Proceed with enrollment
#             new_semyear = int(enrolled.current_semyear) + 1
#             enrolled.current_semyear = str(new_semyear)
#             enrolled.save()

#             response_data = {
#                 "id": student.id,
#                 "message": f"Student has been enrolled to Semester/Year {new_semyear}",
#                 "updated_current_semyear": new_semyear,
#                 "total_semyear": enrolled.total_semyear,
#                 "course": enrolled.course.name if enrolled.course else "",
#                 "stream": enrolled.stream.name if enrolled.stream else "",
#                 "payment_validation": payment_validation,
#                 "enrolled_by_superadmin": not payment_validation["is_eligible"] and is_superadmin
#             }

#             if not payment_validation["is_eligible"] and is_superadmin:
#                 logger.info(f"POST - Superadmin override: Student {id} enrolled to semester {new_semyear} despite payment issues")
#                 response_data["warning"] = "Enrollment completed with superadmin override due to payment issues"
#             else:
#                 logger.info(f"POST - Student {id} successfully enrolled to semester {new_semyear}")

#             return Response({"status": "success", "data": response_data}, status=status.HTTP_200_OK)

#     except Student.DoesNotExist:
#         logger.error(f"Student with ID {id} not found!")
#         return Response({"status": "error", "message": "Student not Found!"}, status=status.HTTP_404_NOT_FOUND)

#     except Exception as e:
#         logger.error(f"Error processing request for student {id}: {str(e)}")
#         return Response({"status": "error", "message": "Something went wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def validate_payment_status(student, current_semyear, is_superadmin=False):
#     """
#     Validate payment status for student enrollment
#     Returns: dict with validation results
#     """
#     validation_result = {
#         "is_eligible": True,
#         "status": "eligible",
#         "message": "Payment validation successful",
#         "details": {}
#     }
    
#     try:
#         # 1. Check PaymentReceipt for current semester pending amount
#         current_sem_payments = PaymentReciept.objects.filter(
#             student=student,
#             semyear=current_semyear
#         ).order_by('-id')
        
#         if current_sem_payments.exists():
#             latest_payment = current_sem_payments.first()
#             pending_amount = float(latest_payment.pendingamount or 0)
            
#             validation_result["details"]["payment_receipt"] = {
#                 "has_records": True,
#                 "latest_pending_amount": pending_amount,
#                 "latest_transaction_id": latest_payment.transactionID,
#                 "latest_transaction_date": latest_payment.transaction_date
#             }
            
#             if pending_amount > 0:
#                 validation_result["is_eligible"] = False
#                 validation_result["status"] = "pending_payment"
#                 validation_result["message"] = f"Pending amount of ₹{pending_amount} exists for current semester {current_semyear}"
#                 return validation_result
#         else:
#             validation_result["details"]["payment_receipt"] = {
#                 "has_records": False,
#                 "message": "No payment records found for current semester"
#             }
#             # If no payment records exist, consider as pending payment
#             validation_result["is_eligible"] = False
#             validation_result["status"] = "no_payment_records"
#             validation_result["message"] = f"No payment records found for semester {current_semyear}"
#             return validation_result

#         # 2. Check University Exam Fees
#         university_exam_fees = UniversityReregistrtationFee.objects.filter(
#             student=student,
#             payment_type="University Exam Fees",
#             semester_year=current_semyear
#         ).exists()
        
#         validation_result["details"]["university_exam_fees"] = {
#             "required": True,
#             "paid": university_exam_fees,
#             "message": "University Exam Fees paid" if university_exam_fees else "University Exam Fees not paid"
#         }
        
#         if not university_exam_fees:
#             validation_result["is_eligible"] = False
#             validation_result["status"] = "university_exam_fees_pending"
#             validation_result["message"] = "University Exam Fees not paid for current semester"
#             return validation_result

#         # 3. Check University Re-Registration Fees
#         university_rereg_fees = UniversityReregistrtationFee.objects.filter(
#             student=student,
#             payment_type="University Re-Registration Fees",
#             semester_year=current_semyear
#         ).exists()
        
#         validation_result["details"]["university_reregistration_fees"] = {
#             "required": True,
#             "paid": university_rereg_fees,
#             "message": "University Re-Registration Fees paid" if university_rereg_fees else "University Re-Registration Fees not paid"
#         }
        
#         if not university_rereg_fees:
#             validation_result["is_eligible"] = False
#             validation_result["status"] = "university_rereg_fees_pending"
#             validation_result["message"] = "University Re-Registration Fees not paid for current semester"
#             return validation_result

#         # If all checks pass
#         validation_result["message"] = "All payment validations passed successfully"
#         logger.info(f"Payment validation successful for student {student.id}, semester {current_semyear}")

#     except Exception as e:
#         logger.error(f"Error in payment validation for student {student.id}: {str(e)}")
#         validation_result["is_eligible"] = False
#         validation_result["status"] = "validation_error"
#         validation_result["message"] = "Error occurred during payment validation"
#         validation_result["error"] = str(e)

#     return validation_result

# commit on 06-11-2025
# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# def get_student_enroll_to_next_year(request, id):
#     try:
#         student = Student.objects.get(id=id)
#         enrolled = Enrolled.objects.filter(student=student).first()

#         if not enrolled:
#             logger.error(f"Student enrollment not found for student ID: {id}")
#             return Response({"status": "error", "message": "Student enrollment not found!"}, status=status.HTTP_404_NOT_FOUND)

#         # Check if user is superadmin
#         is_superadmin = request.user.is_superuser
        
#         if request.method == "GET":
#             if int(enrolled.current_semyear) == int(enrolled.total_semyear):
#                 logger.warning(f"Student {id} is in final semester/year: {enrolled.current_semyear}")
#                 return Response({"status": "error", "message": "Student is in Final Semester / Year!"}, status=status.HTTP_400_BAD_REQUEST)
#             elif int(enrolled.current_semyear) < int(enrolled.total_semyear):
                
#                 # Check payment status for non-superadmin users
#                 payment_validation = validate_payment_status(student, enrolled.current_semyear, is_superadmin)
#                 if not payment_validation["is_eligible"] and not is_superadmin:
#                     return Response({
#                         "status": "error", 
#                         "message": payment_validation["message"],
#                         "validation_details": payment_validation
#                     }, status=status.HTTP_400_BAD_REQUEST)

#                 student_data = {
#                     "id": student.id,
#                     "total_semyear": enrolled.total_semyear,
#                     "course": enrolled.course.name if enrolled.course else "",
#                     "stream": enrolled.stream.name if enrolled.stream else "",
#                     "current_semyear": enrolled.current_semyear,
#                     "next_semyear": int(enrolled.current_semyear) + 1,
#                     "payment_validation": payment_validation,
#                     "is_superadmin": is_superadmin
#                 }
                
#                 logger.info(f"GET Request - Student ID: {id}, Current Semester: {enrolled.current_semyear}, Payment Status: {payment_validation['status']}")
#                 return Response({"status": "success", "data": student_data}, status=status.HTTP_200_OK)

#         if request.method == "POST":
#             if int(enrolled.current_semyear) == int(enrolled.total_semyear):
#                 logger.warning(f"POST - Student {id} is already in final semester/year: {enrolled.current_semyear}")
#                 return Response({"status": "error", "message": "Student is already in Final Semester / Year!"}, status=status.HTTP_400_BAD_REQUEST)

#             # Validate payment status for non-superadmin users
#             payment_validation = validate_payment_status(student, enrolled.current_semyear, is_superadmin)
            
#             if not payment_validation["is_eligible"] and not is_superadmin:
#                 logger.warning(f"POST - Payment validation failed for student {id}: {payment_validation['message']}")
#                 return Response({
#                     "status": "error", 
#                     "message": payment_validation["message"],
#                     "validation_details": payment_validation
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             # Get current semester advance amount before updating enrollment
#             current_sem_advance = get_current_semester_advance_amount(student, enrolled.current_semyear)
            
#             # Proceed with enrollment
#             new_semyear = int(enrolled.current_semyear) + 1
#             enrolled.current_semyear = str(new_semyear)
#             enrolled.save()

#             # Create payment receipt for next semester ONLY if there's positive advance amount from previous semester
#             payment_receipt_created = False
            
#             if current_sem_advance > 0:
#                 try:
#                     receipt_details = create_next_semester_payment_receipt(student, new_semyear, current_sem_advance, request.user.id)
#                     if receipt_details:
#                         payment_receipt_created = True
#                         logger.info(f"Created payment receipt for student {id} for semester {new_semyear} with advance amount: {current_sem_advance}")
#                 except Exception as e:
#                     logger.error(f"Failed to create payment receipt for student {id}: {str(e)}")
#                     # Continue with enrollment even if receipt creation fails
#             else:
#                 logger.info(f"No advance amount found for student {id}. Skipping payment receipt creation.")

#             response_data = {
#                 "id": student.id,
#                 "message": f"Student has been enrolled to Semester/Year {new_semyear}",
#                 "updated_current_semyear": new_semyear,
#                 "total_semyear": enrolled.total_semyear,
#                 "course": enrolled.course.name if enrolled.course else "",
#                 "stream": enrolled.stream.name if enrolled.stream else "",
#                 "payment_validation": payment_validation,
#                 "enrolled_by_superadmin": not payment_validation["is_eligible"] and is_superadmin,
#                 "advance_amount_carried_forward": current_sem_advance,
#                 "payment_receipt_created": payment_receipt_created,
#             }

#             if not payment_validation["is_eligible"] and is_superadmin:
#                 logger.info(f"POST - Superadmin override: Student {id} enrolled to semester {new_semyear} despite payment issues")
#                 response_data["warning"] = "Enrollment completed with superadmin override due to payment issues"
#             else:
#                 logger.info(f"POST - Student {id} successfully enrolled to semester {new_semyear}")

#             return Response({"status": "success", "data": response_data}, status=status.HTTP_200_OK)

#     except Student.DoesNotExist:
#         logger.error(f"Student with ID {id} not found!")
#         return Response({"status": "error", "message": "Student not Found!"}, status=status.HTTP_404_NOT_FOUND)

#     except Exception as e:
#         logger.error(f"Error processing request for student {id}: {str(e)}")
#         return Response({"status": "error", "message": "Something went wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def validate_payment_status(student, current_semyear, is_superadmin=False):
#     """
#     Validate payment status for student enrollment
#     Returns: dict with validation results
#     """
#     validation_result = {
#         "is_eligible": True,
#         "status": "eligible",
#         "message": "Payment validation successful",
#         "details": {}
#     }
    
#     try:
#         # 1. Check PaymentReceipt for current semester pending amount
#         current_sem_payments = PaymentReciept.objects.filter(
#             student=student,
#             semyear=current_semyear
#         ).order_by('-id')
        
#         if current_sem_payments.exists():
#             latest_payment = current_sem_payments.first()
#             pending_amount = float(latest_payment.pendingamount or 0)
            
#             validation_result["details"]["payment_receipt"] = {
#                 "has_records": True,
#                 "latest_pending_amount": pending_amount,
#                 "latest_transaction_id": latest_payment.transactionID,
#                 "latest_transaction_date": latest_payment.transaction_date,
#                 "latest_advance_amount": latest_payment.advanceamount
#             }
            
#             if pending_amount > 0:
#                 validation_result["is_eligible"] = False
#                 validation_result["status"] = "pending_payment"
#                 validation_result["message"] = f"Pending amount of ₹{pending_amount} exists for current semester {current_semyear}"
#                 return validation_result
#         else:
#             validation_result["details"]["payment_receipt"] = {
#                 "has_records": False,
#                 "message": "No payment records found for current semester"
#             }
#             # If no payment records exist, consider as pending payment
#             validation_result["is_eligible"] = False
#             validation_result["status"] = "no_payment_records"
#             validation_result["message"] = f"No payment records found for semester {current_semyear}"
#             return validation_result

#         # 2. Check University Exam Fees
#         university_exam_fees = UniversityReregistrtationFee.objects.filter(
#             student=student,
#             payment_type="University Exam Fees",
#             semester_year=current_semyear
#         ).exists()
        
#         validation_result["details"]["university_exam_fees"] = {
#             "required": True,
#             "paid": university_exam_fees,
#             "message": "University Exam Fees paid" if university_exam_fees else "University Exam Fees not paid"
#         }
        
#         if not university_exam_fees:
#             validation_result["is_eligible"] = False
#             validation_result["status"] = "university_exam_fees_pending"
#             validation_result["message"] = "University Exam Fees not paid for current semester"
#             return validation_result

#         # 3. Check University Re-Registration Fees
#         university_rereg_fees = UniversityReregistrtationFee.objects.filter(
#             student=student,
#             payment_type="University Re-Registration Fees",
#             semester_year=current_semyear
#         ).exists()
        
#         validation_result["details"]["university_reregistration_fees"] = {
#             "required": True,
#             "paid": university_rereg_fees,
#             "message": "University Re-Registration Fees paid" if university_rereg_fees else "University Re-Registration Fees not paid"
#         }
        
#         if not university_rereg_fees:
#             validation_result["is_eligible"] = False
#             validation_result["status"] = "university_rereg_fees_pending"
#             validation_result["message"] = "University Re-Registration Fees not paid for current semester"
#             return validation_result

#         # If all checks pass
#         validation_result["message"] = "All payment validations passed successfully"
#         logger.info(f"Payment validation successful for student {student.id}, semester {current_semyear}")

#     except Exception as e:
#         logger.error(f"Error in payment validation for student {student.id}: {str(e)}")
#         validation_result["is_eligible"] = False
#         validation_result["status"] = "validation_error"
#         validation_result["message"] = "Error occurred during payment validation"
#         validation_result["error"] = str(e)

#     return validation_result


# def get_current_semester_advance_amount(student, current_semyear):
#     """
#     Get the advance amount from the current semester's payment receipts
#     Returns 0.0 if no advance amount exists
#     """
#     try:
#         # Get the latest payment receipt for current semester
#         latest_receipt = PaymentReciept.objects.filter(
#             student=student,
#             semyear=current_semyear
#         ).order_by('-id').first()
        
#         if latest_receipt and latest_receipt.advanceamount:
#             try:
#                 advance_amount = float(latest_receipt.advanceamount)
#                 # Only return positive advance amounts
#                 return advance_amount if advance_amount > 0 else 0.0
#             except (ValueError, TypeError):
#                 return 0.0
#         return 0.0
#     except Exception as e:
#         logger.error(f"Error getting advance amount for student {student.id}: {str(e)}")
#         return 0.0


# def create_next_semester_payment_receipt(student, next_semyear, advance_amount, user_id):
#     """
#     Create a payment receipt for the next semester with advance amount from previous semester
#     Only called when advance_amount > 0
#     """
#     try:
#         # Get total fees for next semester from StudentFees
#         next_sem_fees = StudentFees.objects.filter(
#             student=student,
#             sem=str(next_semyear)
#         ).first()
        
#         if not next_sem_fees:
#             logger.warning(f"No StudentFees found for student {student.id} for semester {next_semyear}")
#             return None

#         # Calculate total fees
#         total_fees = 0.0
#         try:
#             total_fees = float(next_sem_fees.totalfees) if next_sem_fees.totalfees else 0.0
#         except (ValueError, TypeError):
#             # If totalfees is not available, calculate from individual fees
#             fee_fields = ['tutionfees', 'examinationfees', 'bookfees', 'resittingfees', 'entrancefees', 'extrafees']
#             for field in fee_fields:
#                 fee_value = getattr(next_sem_fees, field, "0")
#                 try:
#                     total_fees += float(fee_value) if fee_value else 0.0
#                 except (ValueError, TypeError):
#                     continue

#         # Calculate pending amount
#         pending_amount = max(0.0, total_fees - advance_amount)
        
#         # Generate transaction ID
#         try:
#             latest_receipt = PaymentReciept.objects.latest("id")
#             last_id = int(str(latest_receipt.transactionID).replace("TXT445FE", "")) if latest_receipt else 100
#         except PaymentReciept.DoesNotExist:
#             last_id = 100
#         except Exception as e:
#             return None
        
#         transaction_id = f"TXT445FE{last_id + 1}"

#         # Get current session from enrollment
#         enrolled = Enrolled.objects.filter(student=student).first()
#         session = enrolled.session if enrolled else ""

#         # Create payment receipt
#         payment_receipt = PaymentReciept.objects.create(
#             student=student,
#             payment_for="Course Fees",
#             payment_categories="Update",
#             payment_type="Advance Carry Forward",
#             fee_reciept_type="Regular",
#             transaction_date=timezone.now().date().isoformat(),
#             cheque_no="",
#             bank_name="",
#             semyearfees=str(total_fees),
#             paidamount=str(advance_amount),
#             pendingamount=str(pending_amount),
#             advanceamount="0",
#             transactionID=transaction_id,
#             paymentmode="Carry Forward",
#             remarks=f"Advance amount {advance_amount} carried forward from previous semester",
#             session=session,
#             semyear=str(next_semyear),
#             uncleared_amount=None,
#             status="Realised",
#             created_by=str(user_id),
#             payment_transactionID=None,
#         )

#         logger.info(f"Created payment receipt {transaction_id} for student {student.id} for semester {next_semyear}")
#         return payment_receipt

#     except Exception as e:
#         logger.error(f"Error creating payment receipt for student {student.id}: {str(e)}")
#         raise e

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def get_student_enroll_to_next_year(request, id):
    try:
        student = Student.objects.get(id=id)
        enrolled = Enrolled.objects.filter(student=student).first()

        if not enrolled:
            logger.error(f"Student enrollment not found for student ID: {id}")
            return Response({"status": "error", "message": "Student enrollment not found!"}, status=status.HTTP_404_NOT_FOUND)

        # Check if user is superadmin
        is_superadmin = request.user.is_superuser
        
        if request.method == "GET":
            if int(enrolled.current_semyear) == int(enrolled.total_semyear):
                logger.warning(f"Student {id} is in final semester/year: {enrolled.current_semyear}")
                return Response({"status": "error", "message": "Student is in Final Semester / Year!"}, status=status.HTTP_400_BAD_REQUEST)
            elif int(enrolled.current_semyear) < int(enrolled.total_semyear):
                
                # Check payment status for non-superadmin users
                payment_validation = validate_payment_status(student, enrolled.current_semyear, is_superadmin)
                
                # Check exam results validation
                exam_results_validation = validate_exam_results(student, enrolled.current_semyear, is_superadmin)
                
                # Combine validations
                overall_validation = {
                    "is_eligible": payment_validation["is_eligible"] and exam_results_validation["is_eligible"],
                    "payment_validation": payment_validation,
                    "exam_results_validation": exam_results_validation,
                    "status": "eligible" if (payment_validation["is_eligible"] and exam_results_validation["is_eligible"]) else "not_eligible",
                    "message": "All validations passed" if (payment_validation["is_eligible"] and exam_results_validation["is_eligible"]) else "Validation failed"
                }
                
                if not overall_validation["is_eligible"] and not is_superadmin:
                    error_message = ""
                    if not payment_validation["is_eligible"]:
                        error_message = payment_validation["message"]
                    elif not exam_results_validation["is_eligible"]:
                        error_message = exam_results_validation["message"]
                    
                    return Response({
                        "status": "error", 
                        "message": error_message,
                        "validation_details": overall_validation
                    }, status=status.HTTP_400_BAD_REQUEST)

                student_data = {
                    "id": student.id,
                    "total_semyear": enrolled.total_semyear,
                    "course": enrolled.course.name if enrolled.course else "",
                    "stream": enrolled.stream.name if enrolled.stream else "",
                    "current_semyear": enrolled.current_semyear,
                    "next_semyear": int(enrolled.current_semyear) + 1,
                    "validation_details": overall_validation,
                    "is_superadmin": is_superadmin
                }
                
                logger.info(f"GET Request - Student ID: {id}, Current Semester: {enrolled.current_semyear}, Payment Status: {payment_validation['status']}, Exam Results Status: {exam_results_validation['status']}")
                return Response({"status": "success", "data": student_data}, status=status.HTTP_200_OK)

        if request.method == "POST":
            if int(enrolled.current_semyear) == int(enrolled.total_semyear):
                logger.warning(f"POST - Student {id} is already in final semester/year: {enrolled.current_semyear}")
                return Response({"status": "error", "message": "Student is already in Final Semester / Year!"}, status=status.HTTP_400_BAD_REQUEST)

            # Validate payment status for non-superadmin users
            payment_validation = validate_payment_status(student, enrolled.current_semyear, is_superadmin)
            
            # Validate exam results
            exam_results_validation = validate_exam_results(student, enrolled.current_semyear, is_superadmin)
            
            # Combine validations
            overall_validation = {
                "is_eligible": payment_validation["is_eligible"] and exam_results_validation["is_eligible"],
                "payment_validation": payment_validation,
                "exam_results_validation": exam_results_validation,
                "status": "eligible" if (payment_validation["is_eligible"] and exam_results_validation["is_eligible"]) else "not_eligible"
            }
            
            if not overall_validation["is_eligible"] and not is_superadmin:
                error_message = ""
                if not payment_validation["is_eligible"]:
                    error_message = payment_validation["message"]
                elif not exam_results_validation["is_eligible"]:
                    error_message = exam_results_validation["message"]
                
                logger.warning(f"POST - Validation failed for student {id}: {error_message}")
                return Response({
                    "status": "error", 
                    "message": error_message,
                    "validation_details": overall_validation
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get current semester advance amount before updating enrollment
            current_sem_advance = get_current_semester_advance_amount(student, enrolled.current_semyear)
            
            # Proceed with enrollment
            new_semyear = int(enrolled.current_semyear) + 1
            enrolled.current_semyear = str(new_semyear)
            enrolled.save()

            # Create payment receipt for next semester ONLY if there's positive advance amount from previous semester
            payment_receipt_created = False
            
            if current_sem_advance > 0:
                try:
                    receipt_details = create_next_semester_payment_receipt(student, new_semyear, current_sem_advance, request.user.id)
                    if receipt_details:
                        payment_receipt_created = True
                        logger.info(f"Created payment receipt for student {id} for semester {new_semyear} with advance amount: {current_sem_advance}")
                except Exception as e:
                    logger.error(f"Failed to create payment receipt for student {id}: {str(e)}")
                    # Continue with enrollment even if receipt creation fails
            else:
                logger.info(f"No advance amount found for student {id}. Skipping payment receipt creation.")

            response_data = {
                "id": student.id,
                "message": f"Student has been enrolled to Semester/Year {new_semyear}",
                "updated_current_semyear": new_semyear,
                "total_semyear": enrolled.total_semyear,
                "course": enrolled.course.name if enrolled.course else "",
                "stream": enrolled.stream.name if enrolled.stream else "",
                "validation_details": overall_validation,
                "enrolled_by_superadmin": not overall_validation["is_eligible"] and is_superadmin,
                "advance_amount_carried_forward": current_sem_advance,
                "payment_receipt_created": payment_receipt_created,
            }

            if not overall_validation["is_eligible"] and is_superadmin:
                logger.info(f"POST - Superadmin override: Student {id} enrolled to semester {new_semyear} despite validation issues")
                response_data["warning"] = "Enrollment completed with superadmin override due to validation issues"
            else:
                logger.info(f"POST - Student {id} successfully enrolled to semester {new_semyear}")

            return Response({"status": "success", "data": response_data}, status=status.HTTP_200_OK)

    except Student.DoesNotExist:
        logger.error(f"Student with ID {id} not found!")
        return Response({"status": "error", "message": "Student not Found!"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Error processing request for student {id}: {str(e)}")
        return Response({"status": "error", "message": "Something went wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def validate_exam_results(student, current_semyear, is_superadmin=False):
    """
    Validate if student has any assigned exams without results
    Returns: dict with validation results
    """
    validation_result = {
        "is_eligible": True,
        "status": "eligible",
        "message": "All assigned exams have results",
        "details": {}
    }
    
    try:
        # Get all exams assigned to this student in StudentAppearingExam
        assigned_exams = StudentAppearingExam.objects.filter(
            student_id__contains=[student.id]
        )
        
        if not assigned_exams.exists():
            validation_result["details"]["assigned_exams"] = {
                "has_assigned_exams": False,
                "message": "No exams assigned to student"
            }
            return validation_result
        
        validation_result["details"]["assigned_exams"] = {
            "has_assigned_exams": True,
            "total_assigned_exams": assigned_exams.count(),
            "exams_without_results": []
        }
        
        # Check for each assigned exam if result exists
        exams_without_results = []
        for assigned_exam in assigned_exams:
            # Check if result exists for this student and exam
            result_exists = Result.objects.filter(
                student=student,
                exam=assigned_exam.exam,
                examdetails=assigned_exam
            ).exists()
            
            if not result_exists:
                exams_without_results.append({
                    "exam_id": assigned_exam.exam.id,
                    "exam_name": assigned_exam.exam.name if hasattr(assigned_exam.exam, 'name') else str(assigned_exam.exam),
                    "student_appearing_exam_id": assigned_exam.id,
                    "exam_start_date": assigned_exam.examstartdate,
                    "exam_end_date": assigned_exam.examenddate
                })
        
        validation_result["details"]["assigned_exams"]["exams_without_results"] = exams_without_results
        validation_result["details"]["assigned_exams"]["exams_without_results_count"] = len(exams_without_results)
        
        if exams_without_results:
            validation_result["is_eligible"] = False
            validation_result["status"] = "pending_exam_results"
            validation_result["message"] = f"Student has {len(exams_without_results)} assigned exam(s) without results"
        
        logger.info(f"Exam results validation for student {student.id}: {len(exams_without_results)} exams without results out of {assigned_exams.count()} assigned exams")
        
    except Exception as e:
        logger.error(f"Error in exam results validation for student {student.id}: {str(e)}")
        validation_result["is_eligible"] = False
        validation_result["status"] = "validation_error"
        validation_result["message"] = "Error occurred during exam results validation"
        validation_result["error"] = str(e)
    
    return validation_result


def validate_payment_status(student, current_semyear, is_superadmin=False):
    """
    Validate payment status for student enrollment
    Returns: dict with validation results
    """
    validation_result = {
        "is_eligible": True,
        "status": "eligible",
        "message": "Payment validation successful",
        "details": {}
    }
    
    try:
        # 1. Check PaymentReceipt for current semester pending amount
        current_sem_payments = PaymentReciept.objects.filter(
            student=student,
            semyear=current_semyear
        ).order_by('-id')
        
        if current_sem_payments.exists():
            latest_payment = current_sem_payments.first()
            pending_amount = float(latest_payment.pendingamount or 0)
            
            validation_result["details"]["payment_receipt"] = {
                "has_records": True,
                "latest_pending_amount": pending_amount,
                "latest_transaction_id": latest_payment.transactionID,
                "latest_transaction_date": latest_payment.transaction_date,
                "latest_advance_amount": latest_payment.advanceamount
            }
            
            if pending_amount > 0:
                validation_result["is_eligible"] = False
                validation_result["status"] = "pending_payment"
                validation_result["message"] = f"Pending amount of ₹{pending_amount} exists for current semester {current_semyear}"
                return validation_result
        else:
            validation_result["details"]["payment_receipt"] = {
                "has_records": False,
                "message": "No payment records found for current semester"
            }
            # If no payment records exist, consider as pending payment
            validation_result["is_eligible"] = False
            validation_result["status"] = "no_payment_records"
            validation_result["message"] = f"No payment records found for semester {current_semyear}"
            return validation_result

        # 2. Check University Exam Fees
        university_exam_fees = UniversityReregistrtationFee.objects.filter(
            student=student,
            payment_type="University Exam Fees",
            semester_year=current_semyear
        ).exists()
        
        validation_result["details"]["university_exam_fees"] = {
            "required": True,
            "paid": university_exam_fees,
            "message": "University Exam Fees paid" if university_exam_fees else "University Exam Fees not paid"
        }
        
        if not university_exam_fees:
            validation_result["is_eligible"] = False
            validation_result["status"] = "university_exam_fees_pending"
            validation_result["message"] = "University Exam Fees not paid for current semester"
            return validation_result

        # 3. Check University Re-Registration Fees
        university_rereg_fees = UniversityReregistrtationFee.objects.filter(
            student=student,
            payment_type="University Re-Registration Fees",
            semester_year=current_semyear
        ).exists()
        
        validation_result["details"]["university_reregistration_fees"] = {
            "required": True,
            "paid": university_rereg_fees,
            "message": "University Re-Registration Fees paid" if university_rereg_fees else "University Re-Registration Fees not paid"
        }
        
        if not university_rereg_fees:
            validation_result["is_eligible"] = False
            validation_result["status"] = "university_rereg_fees_pending"
            validation_result["message"] = "University Re-Registration Fees not paid for current semester"
            return validation_result

        # If all checks pass
        validation_result["message"] = "All payment validations passed successfully"
        logger.info(f"Payment validation successful for student {student.id}, semester {current_semyear}")

    except Exception as e:
        logger.error(f"Error in payment validation for student {student.id}: {str(e)}")
        validation_result["is_eligible"] = False
        validation_result["status"] = "validation_error"
        validation_result["message"] = "Error occurred during payment validation"
        validation_result["error"] = str(e)

    return validation_result


def get_current_semester_advance_amount(student, current_semyear):
    """
    Get the advance amount from the current semester's payment receipts
    Returns 0.0 if no advance amount exists
    """
    try:
        # Get the latest payment receipt for current semester
        latest_receipt = PaymentReciept.objects.filter(
            student=student,
            semyear=current_semyear
        ).order_by('-id').first()
        
        if latest_receipt and latest_receipt.advanceamount:
            try:
                advance_amount = float(latest_receipt.advanceamount)
                # Only return positive advance amounts
                return advance_amount if advance_amount > 0 else 0.0
            except (ValueError, TypeError):
                return 0.0
        return 0.0
    except Exception as e:
        logger.error(f"Error getting advance amount for student {student.id}: {str(e)}")
        return 0.0


def create_next_semester_payment_receipt(student, next_semyear, advance_amount, user_id):
    """
    Create a payment receipt for the next semester with advance amount from previous semester
    Only called when advance_amount > 0
    """
    try:
        # Get total fees for next semester from StudentFees
        next_sem_fees = StudentFees.objects.filter(
            student=student,
            sem=str(next_semyear)
        ).first()
        
        if not next_sem_fees:
            logger.warning(f"No StudentFees found for student {student.id} for semester {next_semyear}")
            return None

        # Calculate total fees
        total_fees = 0.0
        try:
            total_fees = float(next_sem_fees.totalfees) if next_sem_fees.totalfees else 0.0
        except (ValueError, TypeError):
            # If totalfees is not available, calculate from individual fees
            fee_fields = ['tutionfees', 'examinationfees', 'bookfees', 'resittingfees', 'entrancefees', 'extrafees']
            for field in fee_fields:
                fee_value = getattr(next_sem_fees, field, "0")
                try:
                    total_fees += float(fee_value) if fee_value else 0.0
                except (ValueError, TypeError):
                    continue

        # Calculate pending amount
        pending_amount = max(0.0, total_fees - advance_amount)
        
        # Generate transaction ID
        try:
            latest_receipt = PaymentReciept.objects.latest("id")
            last_id = int(str(latest_receipt.transactionID).replace("TXT445FE", "")) if latest_receipt else 100
        except PaymentReciept.DoesNotExist:
            last_id = 100
        except Exception as e:
            return None
        
        transaction_id = f"TXT445FE{last_id + 1}"

        # Get current session from enrollment
        enrolled = Enrolled.objects.filter(student=student).first()
        session = enrolled.session if enrolled else ""

        # Create payment receipt
        payment_receipt = PaymentReciept.objects.create(
            student=student,
            payment_for="Course Fees",
            payment_categories="Update",
            payment_type="Advance Carry Forward",
            fee_reciept_type="Regular",
            transaction_date=timezone.now().date().isoformat(),
            cheque_no="",
            bank_name="",
            semyearfees=str(total_fees),
            paidamount=str(advance_amount),
            pendingamount=str(pending_amount),
            advanceamount="0",
            transactionID=transaction_id,
            paymentmode="Carry Forward",
            remarks=f"Advance amount {advance_amount} carried forward from previous semester",
            session=session,
            semyear=str(next_semyear),
            uncleared_amount=None,
            status="Realised",
            created_by=str(user_id),
            payment_transactionID=None,
        )

        logger.info(f"Created payment receipt {transaction_id} for student {student.id} for semester {next_semyear}")
        return payment_receipt

    except Exception as e:
        logger.error(f"Error creating payment receipt for student {student.id}: {str(e)}")
        raise e


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_multiple_subjects(request):
    try:
        subjects_data = request.data.get("subjects", [])

        if not subjects_data:
            logger.error("No subjects data provided for update.")
            return Response({"status": "error", "message": "No subjects data provided."}, status=status.HTTP_400_BAD_REQUEST)

        updated_subjects = []
        errors = []

        for subject_data in subjects_data:
            subject_id = subject_data.get("id")
            if not subject_id:
                errors.append({"id": None, "message": "Subject ID is required."})
                continue

            subject = Subject.objects.filter(id=subject_id).first()
            if not subject:
                errors.append({"id": subject_id, "message": "Subject not found."})
                continue

            fields_updated = []

            if 'studypattern' in subject_data:
                subject.studypattern = subject_data['studypattern']
                fields_updated.append("Study Pattern")

            if 'semyear' in subject_data:
                subject.semyear = subject_data['semyear']
                fields_updated.append("Semester/Year")

            if 'name' in subject_data:
                subject.name = subject_data['name']
                fields_updated.append("Subject Name")

            if 'code' in subject_data:
                subject.code = subject_data['code']
                fields_updated.append("Subject Code")

            if not fields_updated:
                errors.append({"id": subject_id, "message": "No valid fields provided for update."})
                continue

            subject.save()
            updated_subjects.append({"id": subject.id, "updated_fields": fields_updated})
            #logger.info(f"Updated Subject ID {subject.id}. Fields updated: {', '.join(fields_updated)}")

        response_data = {"status": "success", "updated_subjects": updated_subjects}
        if errors:
            response_data["errors"] = errors

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error updating subjects: {str(e)}")
        return Response({"status": "error", "message": "Something went wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def register_cancel_student(request, id):
    try:
        student = Student.objects.get(id=id)
    except Student.DoesNotExist:
        logger.error(f"Student with ID {id} not found.")
        return Response({"status": "error", "message": "Student not found!"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == "GET":
        student_data = {
            'id': student.id,
            'name': student.name,
            'mobile': student.mobile,
            'email': student.email,
            'enrolled': student.is_enrolled,
            'active': student.is_enrolled,
        }
        return Response({"status": "success", "data": student_data}, status=status.HTTP_200_OK)
    
    if request.method == "POST":
        cancel_status = request.data.get('cancel_status')
        if cancel_status == "in-active":
            student.archive = True
            student.is_enrolled = False
            student.is_cancelled = True
            student.save()
            #logger.info(f"Student with ID {id} has been cancelled.")
            return Response({"status": "success", "message": "Student registration cancelled successfully."}, status=status.HTTP_200_OK)
        else:
            logger.error(f"Invalid cancel_status received: {cancel_status}")
            return Response({"status": "error", "message": "Invalid cancel_status value."}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({"status": "error", "message": "Invalid request method."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


from django.db import transaction, IntegrityError

@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
def registered_new_university_enrollment_number(request):
    if request.method == "POST":
        data = request.data
        student_id = data.get("student_id")
        course_id_in = data.get("course_id")           # CharField in model
        enrollment_id = data.get("enrollment_id")
        course_name_in = data.get("course_name", "")   # optional

        # Only check: enrollment_id uniqueness
        if not enrollment_id:
            return Response(
                {"status": "error", "message": "enrollment_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if UniversityEnrollment.objects.filter(enrollment_id=enrollment_id).exists():
            return Response(
                {"status": "error", "message": "Enrollment ID already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Best-effort auto-fill of course_name using Course.id
        course_name_value = (course_name_in or "").strip()
        if not course_name_value and course_id_in:
            try:
                course_name_value = Course.objects.only("name").get(id=int(course_id_in)).name
            except Exception:
                course_name_value = ""  # keep minimal validation contract

        try:
            with transaction.atomic():
                enrollment = UniversityEnrollment.objects.create(
                    student_id=student_id,                         # pass FK id directly
                    type="new",
                    course_id=str(course_id_in) if course_id_in else "",
                    course_name=course_name_value,                 # auto-filled if possible
                    enrollment_id=enrollment_id,
                )
        except IntegrityError:
            logger.exception("DB constraint error while creating NEW enrollment")
            return Response(
                {"status": "error", "message": "Could not create enrollment (invalid data/constraints)"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            logger.exception("Unexpected error while creating NEW enrollment")
            return Response({"status": "error", "message": "Internal Server Error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {
                "status": "success",
                "message": "Enrollment registered successfully",
                "data": {
                    "id": enrollment.id,
                    "student_id": student_id,
                    "type": "new",
                    "course_id": enrollment.course_id,
                    "course_name": enrollment.course_name,
                    "enrollment_id": enrollment.enrollment_id,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    # -------- GET (all "new" for a student) --------
    student_id = request.query_params.get("student_id")
    if not student_id:
        return Response({"status": "error", "message": "student_id is required"},
                        status=status.HTTP_400_BAD_REQUEST)

    if not Student.objects.filter(id=student_id).exists():
        return Response({"status": "error", "message": "Invalid student ID"},
                        status=status.HTTP_400_BAD_REQUEST)

    enrollments = UniversityEnrollment.objects.filter(student_id=student_id, type="new").order_by("-id")
    if not enrollments.exists():
        return Response({"status": "error", "message": "No new enrollment records found"},
                        status=status.HTTP_404_NOT_FOUND)

    data_out = [
        {
            "id": e.id,
            "student_id": e.student_id,
            "type": e.type,
            "course_id": e.course_id,
            "course_name": e.course_name,
            "enrollment_id": e.enrollment_id,
        }
        for e in enrollments
    ]
    return Response({"status": "success", "message": "New enrollment records fetched successfully", "data": data_out},
                    status=status.HTTP_200_OK)


@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
def registered_old_university_enrollment_number(request):
    if request.method == "POST":
        data = request.data
        student_id = data.get("student_id")
        course_id_in = data.get("course_id")           # CharField in model
        enrollment_id = data.get("enrollment_id")
        course_name_in = data.get("course_name", "")   # optional

        # Only check: enrollment_id uniqueness
        if not enrollment_id:
            return Response(
                {"status": "error", "message": "enrollment_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if UniversityEnrollment.objects.filter(enrollment_id=enrollment_id).exists():
            return Response(
                {"status": "error", "message": "Enrollment ID already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Best-effort auto-fill of course_name using Course.id
        course_name_value = (course_name_in or "").strip()
        if not course_name_value and course_id_in:
            try:
                course_name_value = Course.objects.only("name").get(id=int(course_id_in)).name
            except Exception:
                course_name_value = ""  # keep minimal validation contract

        try:
            with transaction.atomic():
                enrollment = UniversityEnrollment.objects.create(
                    student_id=student_id,                         # pass FK id directly
                    type="old",
                    course_id=str(course_id_in) if course_id_in else "",
                    course_name=course_name_value,                 # auto-filled if possible
                    enrollment_id=enrollment_id,
                )
        except IntegrityError:
            logger.exception("DB constraint error while creating OLD enrollment")
            return Response(
                {"status": "error", "message": "Could not create enrollment (invalid data/constraints)"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            logger.exception("Unexpected error while creating OLD enrollment")
            return Response({"status": "error", "message": "Internal Server Error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {
                "status": "success",
                "message": "Enrollment registered successfully",
                "data": {
                    "id": enrollment.id,
                    "student_id": student_id,
                    "type": "old",
                    "course_id": enrollment.course_id,
                    "course_name": enrollment.course_name,
                    "enrollment_id": enrollment.enrollment_id,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    # -------- GET (all "old" for a student) --------
    student_id = request.query_params.get("student_id")
    if not student_id:
        return Response({"status": "error", "message": "student_id is required"},
                        status=status.HTTP_400_BAD_REQUEST)

    if not Student.objects.filter(id=student_id).exists():
        return Response({"status": "error", "message": "Invalid student ID"},
                        status=status.HTTP_400_BAD_REQUEST)

    enrollments = UniversityEnrollment.objects.filter(student_id=student_id, type="old").order_by("-id")
    if not enrollments.exists():
        return Response({"status": "error", "message": "No old enrollment records found"},
                        status=status.HTTP_404_NOT_FOUND)

    data_out = [
        {
            "id": e.id,
            "student_id": e.student_id,
            "type": e.type,
            "course_id": e.course_id,
            "course_name": e.course_name,
            "enrollment_id": e.enrollment_id,
        }
        for e in enrollments
    ]
    return Response({"status": "success", "message": "Old enrollment records fetched successfully", "data": data_out},
                    status=status.HTTP_200_OK)

@api_view(["GET", "POST"])
def courier_api(request):
    if request.method == "GET":
        student_id = request.query_params.get("student_id")
        if not student_id:
            return Response(
                {"status": "error", "message": "student_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            student = get_object_or_404(Student, id=student_id)  # Cleaner lookup
            couriers = Courier.objects.filter(student=student).values(
                "id", "article_name", "courier_from", "courier_to", "booking_date", 
                "courier_company", "tracking_id", "remarks"
            )

            return Response({
                "status": "success",
                "message": "Courier records retrieved successfully",
                "data": list(couriers)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response(
                {"status": "error", "message": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    elif request.method == "POST":
        try:
            data = request.data
            student_id = data.get("student_id")
            article_name = data.get("article_name")
            courier_from = data.get("courier_from")
            courier_to = data.get("courier_to")
            booking_date = data.get("booking_date")
            courier_company = data.get("courier_company")
            tracking_id = data.get("tracking_id")
            remarks = data.get("remarks")

            # Validate student_id
            if not student_id:
                return Response(
                    {"status": "error", "message": "student_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            student = get_object_or_404(Student, id=student_id)  # Cleaner lookup

            # Create the courier record
            courier = Courier.objects.create(
                student=student,
                article_name=article_name,
                courier_from=courier_from,
                courier_to=courier_to,
                booking_date=booking_date,
                courier_company=courier_company,
                tracking_id=tracking_id,
                remarks=remarks
            )

            return Response({
                "status": "success",
                "message": "Courier record created successfully",
                "data": {
                    "id": courier.id,
                    "student_id": student_id,
                    "article_name": article_name,
                    "courier_from": courier_from,
                    "courier_to": courier_to,
                    "booking_date": booking_date,
                    "courier_company": courier_company,
                    "tracking_id": tracking_id,
                    "remarks": remarks
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response(
                {"status": "error", "message": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# @api_view(['GET'])
# def get_additional_fees(request):
#     student_id = request.query_params.get("student_id")
#     if not student_id:
#         logger.error("Student ID is required.")
#         return Response({"error": "Student ID is required."}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         student = Student.objects.get(id=student_id)
#         fees = PaymentReciept.objects.filter(student=student)
        
#         response_data = []
#         for fee in fees:
#             response_data.append({
#                 "student_id": student.id,
#                 "fees_id":fee.id,
#                 "semyear": fee.semyear,
#                 "payment_for": fee.payment_for,
#                 "payment_type": fee.payment_type,
#                 "session": fee.session,
#                 "transaction_date": fee.transaction_date,
#                 "paymentmode": fee.paymentmode,
#                 "cheque_no": fee.cheque_no,
#                 "paidamount": fee.paidamount,
#                 "pendingamount": fee.pendingamount,
#             })
        
#         return Response(response_data, status=status.HTTP_200_OK)
#     except Student.DoesNotExist:
#         logger.error(f"Student with ID {student_id} does not exist.")
#         return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         logger.error(f"Unexpected error: {str(e)}")
#         return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['POST'])
# def create_additional_fees(request):
#     student_id = request.data.get('student_id')
#     if not student_id:
#         logger.error("Student ID is required.")
#         return Response({"error": "Student ID is required."}, status=status.HTTP_400_BAD_REQUEST)
#     try:
#         student = Student.objects.get(id=student_id)
#     except Student.DoesNotExist:
#         logger.error(f"Student with ID {student_id} does not exist.")
#         return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
    
#     extrafees_feesfor = request.data.get('extrafees_feesfor')
#     extrafees_amount = request.data.get('extrafees_amount')
#     extrafees_feestype = request.data.get('extrafees_feestype')
#     extrafees_semyear = request.data.get('extrafees_semyear')
#     extrafees_transactiondate = request.data.get('extrafees_transactiondate')
#     extrafees_paymentmode = request.data.get('extrafees_paymentmode')
#     extrafees_chequeno = request.data.get('extrafees_chequeno')
#     extrafees_bankname = request.data.get('extrafees_bankname')
#     extrafees_remarks = request.data.get('extrafees_remarks')
    
#     if not all([extrafees_feesfor, extrafees_amount, extrafees_feestype, extrafees_semyear]):
#         logger.error("Missing required fee details.")
#         return Response({"error": "Missing required fee details."}, status=status.HTTP_400_BAD_REQUEST)
    
#     try:
#         getlatestreciept = PaymentReciept.objects.latest('id')
#         tid = getlatestreciept.transactionID.replace("TXT445FE", '')
#         transactionID = f"TXT445FE{int(tid) + 1}"
#     except PaymentReciept.DoesNotExist:
#         transactionID = "TXT445FE101"
    
#     try:
#         add_payment_reciept = PaymentReciept(
#             student=student,
#             payment_for=extrafees_feesfor,
#             payment_type=extrafees_feestype,
#             fee_reciept_type="",
#             transaction_date=extrafees_transactiondate,
#             cheque_no=extrafees_chequeno,
#             bank_name=extrafees_bankname,
#             paidamount=extrafees_amount,
#             pendingamount="0",
#             transactionID=transactionID,
#             paymentmode=extrafees_paymentmode,
#             remarks=extrafees_remarks,
#             session="",
#             semyear=extrafees_semyear
#         )
#         add_payment_reciept.save()
        
#         response_data = {
#             "student_id": student.id,
#             "semyear": add_payment_reciept.semyear,
#             "payment_for": add_payment_reciept.payment_for,
#             "payment_type": add_payment_reciept.payment_type,
#             "transaction_date": add_payment_reciept.transaction_date,
#             "paymentmode": add_payment_reciept.paymentmode,
#             "cheque_no": add_payment_reciept.cheque_no,
#             "paidamount": add_payment_reciept.paidamount,
#             "pendingamount": add_payment_reciept.pendingamount,
#             "transactionID": add_payment_reciept.transactionID,
#         }
        
#         return Response(response_data, status=status.HTTP_201_CREATED)
#     except Exception as e:
#         logger.error(f"Error saving payment receipt: {str(e)}")
#         return Response({"error": "An error occurred while saving the payment receipt."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['POST'])
# def create_additional_fees(request):
#     student_id = request.data.get('student_id')
#     if not student_id:
#         logger.error("Student ID is required.")
#         return Response({"error": "Student ID is required."}, status=status.HTTP_400_BAD_REQUEST)

#     # Validate student
#     try:
#         student = Student.objects.get(id=student_id)
#     except Student.DoesNotExist:
#         logger.error(f"Student with ID {student_id} does not exist.")
#         return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

#     # Inputs
#     extrafees_feesfor         = request.data.get('extrafees_feesfor')
#     extrafees_amount_raw      = request.data.get('extrafees_amount')
#     extrafees_feestype        = request.data.get('extrafees_feestype')
#     extrafees_semyear         = request.data.get('extrafees_semyear')
#     extrafees_transactiondate = request.data.get('extrafees_transactiondate')
#     extrafees_paymentmode     = request.data.get('extrafees_paymentmode')
#     extrafees_chequeno        = request.data.get('extrafees_chequeno')
#     extrafees_bankname        = request.data.get('extrafees_bankname')
#     extrafees_remarks         = request.data.get('extrafees_remarks')
#     session_name              = request.data.get('session')

#     if not all([extrafees_feesfor, extrafees_amount_raw, extrafees_feestype, extrafees_semyear]):
#         logger.error("Missing required fee details.")
#         return Response({"error": "Missing required fee details."}, status=status.HTTP_400_BAD_REQUEST)

#     # Convert amount to int
#     try:
#         extrafees_amount = int(float(extrafees_amount_raw))  # handles "100", "100.0" etc.
#         if extrafees_amount < 0:
#             return Response({"error": "Amount cannot be negative."}, status=status.HTTP_400_BAD_REQUEST)
#     except (ValueError, TypeError):
#         return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

#     # Get total fees
#     fees_qs = StudentFees.objects.filter(student_id=student_id, sem=extrafees_semyear)
#     if not fees_qs.exists():
#         logger.error(f"No fee structure found for student {student_id} and sem/year '{extrafees_semyear}'.")
#         return Response({"error": "Fee structure for the given sem/year not found."},
#                         status=status.HTTP_400_BAD_REQUEST)

#     totalfees_raw = fees_qs.aggregate(total=Sum('totalfees'))['total']
#     try:
#         totalfees = int(totalfees_raw) if totalfees_raw else 0
#     except (ValueError, TypeError):
#         totalfees = 0

#     # Pending = total - paid now
#     pendingamount = totalfees - extrafees_amount
#     if pendingamount < 0:
#         pendingamount = 0

#     # Transaction ID
#     PREFIX = "TXT445FE"
#     try:
#         with transaction.atomic():
#             last = PaymentReciept.objects.select_for_update(skip_locked=True).order_by('-id').first()
#             if last and last.transactionID and last.transactionID.startswith(PREFIX):
#                 try:
#                     numeric_part = int(last.transactionID.replace(PREFIX, '') or "100")
#                 except ValueError:
#                     numeric_part = 100
#                 transactionID = f"{PREFIX}{numeric_part + 1}"
#             else:
#                 transactionID = f"{PREFIX}101"
#     except Exception as e:
#         logger.warning(f"Could not lock last receipt for transactionID; falling back. Error: {e}")
#         transactionID = f"{PREFIX}101"

#     # Save receipt
#     try:
#         add_payment_reciept = PaymentReciept(
#             student=student,
#             payment_for="Course Fees",
#             payment_type=extrafees_feestype,
#             fee_reciept_type="",
#             transaction_date=extrafees_transactiondate,
#             cheque_no=extrafees_chequeno,
#             bank_name=extrafees_bankname,
#             paidamount=extrafees_amount,
#             pendingamount=pendingamount,
#             transactionID=transactionID,
#             paymentmode=extrafees_paymentmode,
#             remarks=extrafees_remarks,
#             session=session_name or None,
#             semyear=extrafees_semyear
#         )
#         add_payment_reciept.save()

#         return Response({
#             "student_id": student.id,
#             "semyear": add_payment_reciept.semyear,
#             "session": add_payment_reciept.session,
#             "payment_for": add_payment_reciept.payment_for,
#             "payment_type": add_payment_reciept.payment_type,
#             "transaction_date": str(add_payment_reciept.transaction_date),
#             "paymentmode": add_payment_reciept.paymentmode,
#             "cheque_no": add_payment_reciept.cheque_no,
#             "bank_name": add_payment_reciept.bank_name,
#             "paidamount": add_payment_reciept.paidamount,
#             "pendingamount": add_payment_reciept.pendingamount,
#             "transactionID": add_payment_reciept.transactionID,
#             "remarks": add_payment_reciept.remarks,
#             "totalfees": totalfees,
#         }, status=status.HTTP_201_CREATED)

#     except Exception as e:
#         logger.error(f"Error saving payment receipt: {str(e)}")
#         return Response({"error": "An error occurred while saving the payment receipt."},
#                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['PUT'])
# def update_additional_fees(request):
#     fees_id = request.data.get('fees_id')
#     student_id = request.data.get('student_id')
    
#     if not fees_id or not student_id:
#         logger.error("Fees ID and Student ID are required.")
#         return Response({"error": "Fees ID and Student ID are required."}, status=status.HTTP_400_BAD_REQUEST)
    
#     try:
#         payment_receipt = PaymentReciept.objects.get(id=fees_id, student_id=student_id)
#     except PaymentReciept.DoesNotExist:
#         logger.error("No payment receipt found for the given Fees ID and Student ID.")
#         return Response({"error": "No payment receipt found."}, status=status.HTTP_404_NOT_FOUND)
    
#     # Update fields if provided in request
#     for field in ['payment_for', 'payment_type', 'transaction_date', 'cheque_no', 'bank_name', 
#                   'paidamount', 'pendingamount', 'paymentmode', 'remarks', 'semyear', 'status']:
#         if request.data.get(field) is not None:
#             setattr(payment_receipt, field, request.data[field])
    
#     payment_receipt.save()
    
#     response_data = {
#         "fees_id": payment_receipt.id,
#         "student_id": payment_receipt.student.id,
#         "semyear": payment_receipt.semyear,
#         "payment_for": payment_receipt.payment_for,
#         "payment_type": payment_receipt.payment_type,
#         "transaction_date": payment_receipt.transaction_date,
#         "paymentmode": payment_receipt.paymentmode,
#         "cheque_no": payment_receipt.cheque_no,
#         "paidamount": payment_receipt.paidamount,
#         "pendingamount": payment_receipt.pendingamount,
#         "transactionID": payment_receipt.transactionID,
#         "status": payment_receipt.status,
#     }
    
#     return Response(response_data, status=status.HTTP_200_OK)
  
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def result_uploaded_view(request):
    if request.method == 'POST':
        student_id = request.data.get('student_id')
        date = request.data.get('date')
        examination = request.data.get('examination')
        semyear = request.data.get('semyear')
        uploaded = request.data.get('uploaded')
        remarks = request.data.get('remarks')

        if not student_id:
            logger.error("Student ID is required.")
            return Response({"error": "Student ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not semyear:
            logger.error("Semester/Year is required.")
            return Response({"error": "Semester/Year is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            logger.error(f"Student with ID {student_id} not found.")
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if record already exists for this student and semyear
        existing_record = ResultUploaded.objects.filter(
            student__id=student_id, 
            semyear=semyear
        ).first()
        
        if existing_record:
            logger.error(f"Result record already exists for student {student_id} and semyear {semyear}")
            return Response({
                "error": f"Result record already exists for semester/year {semyear}. Please use update instead.",
                "existing_id": existing_record.id
            }, status=status.HTTP_409_CONFLICT)

        # Create a mutable copy of request.data
        data = request.data.copy()
        data['student'] = student.id
        
        # Remove student_id from data as it's not a model field
        if 'student_id' in data:
            del data['student_id']

        serializer = ResultUploadedSerializer(data=data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(ResultUploadedSerializer(instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # GET method remains the same
    student_id = request.GET.get('student_id')
    semyear = request.GET.get('semyear')
    if not student_id:
        return Response({"error": "Student ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    qs = ResultUploaded.objects.filter(student__id=student_id)
    if semyear:
        qs = qs.filter(semyear=semyear)

    serializer = ResultUploadedSerializer(qs.order_by('-id'), many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_result_uploaded_by_student_sem(request):
    student_id = request.data.get('student_id')
    semyear = request.data.get('semyear')

    if not student_id or not semyear:
        return Response({"error": "student_id and semyear are required."},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        instance = ResultUploaded.objects.get(student__id=student_id, semyear=semyear)
    except ResultUploaded.DoesNotExist:
        return Response({"error": "Result not found for this student and semyear."},
                        status=status.HTTP_404_NOT_FOUND)

    partial = (request.method == 'PATCH')
    
    # Create a mutable copy of request.data
    data = request.data.copy()
    data['student'] = student_id
    
    # Remove student_id from data as it's not a model field
    if 'student_id' in data:
        del data['student_id']

    serializer = ResultUploadedSerializer(instance, data=data, partial=partial)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_university_examination(request):
    student_id = request.data.get('student_id')
    exam_type = request.data.get('type')
    amount = request.data.get('amount')
    date = request.data.get('date')
    examination = request.data.get('examination')
    semyear = request.data.get('semyear')
    paymentmode = request.data.get('paymentmode')
    remarks = request.data.get('remarks')
    
    if not student_id:
        logger.error("Student ID is required.")
        return Response({"error": "Student ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        logger.error(f"Student with ID {student_id} not found.")
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
    
    university_exam = UniversityExamination(
        student=student,
        type=exam_type,
        amount=amount,
        date=date,
        examination=examination,
        semyear=semyear,
        paymentmode=paymentmode,
        remarks=remarks
    )
    university_exam.save()
    
    response_data = {
        "id": university_exam.id,
        "student_id": university_exam.student.id,
        "type": university_exam.type,
        "amount": university_exam.amount,
        "date": university_exam.date,
        "examination": university_exam.examination,
        "semyear": university_exam.semyear,
        "paymentmode": university_exam.paymentmode,
        "remarks": university_exam.remarks
    }
    
    return Response(response_data, status=status.HTTP_201_CREATED)
  
@api_view(['POST'])
def create_university_reregistration(request):
    student_id = request.data.get('student_id')
    type = request.data.get('type')
    amount = request.data.get('amount')
    date = request.data.get('date')
    examination = request.data.get('examination')
    semyear = request.data.get('semyear')
    paymentmode = request.data.get('paymentmode')
    remarks = request.data.get('remarks')
    
    if not student_id:
        logger.error("Student ID is required.")
        return Response({"error": "Student ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        logger.error(f"Student with ID {student_id} not found.")
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
    
    university_exam = UniversityExamination(
        student=student,
        type=type,
        amount=amount,
        date=date,
        examination=examination,
        semyear=semyear,
        paymentmode=paymentmode,
        remarks=remarks
    )
    university_exam.save()
    
    response_data = {
        "id": university_exam.id,
        "student_id": university_exam.student.id,
        "type": university_exam.type,
        "amount": university_exam.amount,
        "date": university_exam.date,
        "examination": university_exam.examination,
        "semyear": university_exam.semyear,
        "paymentmode": university_exam.paymentmode,
        "remarks": university_exam.remarks
    }
    
    return Response(response_data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_university_reregistration(request):
    student_id = request.query_params.get("student_id")
    
    if not student_id:
        logger.error("Student ID is required.")
        return Response({"error": "Student ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        student = Student.objects.get(id=student_id)
        exams = UniversityExamination.objects.filter(student=student)
        
        response_data = [
            {
                "id": exam.id,
                "student_id": exam.student.id,
                "type": exam.type,
                "amount": exam.amount,
                "date": exam.date,
                "examination": exam.examination,
                "semyear": exam.semyear,
                "paymentmode": exam.paymentmode,
                "remarks": exam.remarks
            } for exam in exams
        ]
        
        return Response(response_data, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        logger.error(f"Student with ID {student_id} not found.")
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
@api_view(['GET'])
def get_paid_fees(request):
    student_id = request.query_params.get("student_id")

    if not student_id:
        logger.error("Student ID is required.")
        return Response({"error": "Student ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        getstudent = Student.objects.get(id=student_id)
        university = getstudent.university  # Fetch the related university

        response_data = {
            "name": getstudent.name,
            "dateofbirth": getstudent.dateofbirth,
            "email": getstudent.email,
            "mobile": getstudent.mobile,
            "address": getstudent.address,
            "city": getstudent.city.name if getstudent.city else None,
            "state": getstudent.state.name if getstudent.state else None,
            "pincode": getstudent.pincode,
            "country": getstudent.country.name if getstudent.country else None,
            "enrollment_id": getstudent.enrollment_id,
            "university_name": university.university_name,
            "university_address": university.university_address,
            "university_city": university.university_city,
            "university_state": university.university_state,
            "university_pincode": university.university_pincode,
            "university_logo": str(university.university_logo.url) if university.university_logo else None,
            "registrationID": university.registrationID
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Student.DoesNotExist:
        logger.error(f"Student with ID {student_id} not found.")
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def save_single_question_answer(request):
    try:
        data = request.data

        # Convert student_id and exam_id to int for filtering
        try:
            student_id = int(data.get("student_id"))
            exam_id = int(data.get("exam_id"))
        except (TypeError, ValueError):
            return Response({"error": "Invalid student_id or exam_id. Must be integer."}, status=status.HTTP_400_BAD_REQUEST)

        question_id = data.get("question_id")
        submitted_answer = data.get("submitted_answer")
        exam_details_id = data.get("exam_details_id")  # NEW: get exam_details_id from request

        if not student_id or not exam_id or not question_id or submitted_answer is None:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate question exists
        try:
            question_instance = Questions.objects.get(id=question_id)
        except Questions.DoesNotExist:
            return Response({"error": f"Question ID {question_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Validate exam_details_id
        try:
            exam_details_instance = StudentAppearingExam.objects.get(id=int(exam_details_id))
        except (StudentAppearingExam.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Invalid or missing exam_details_id"}, status=status.HTTP_400_BAD_REQUEST)

        correct_answer = question_instance.answer.lower()
        marks = question_instance.marks

        if submitted_answer.lower() == correct_answer:
            result = "Right"
            marks_obtained = marks
        else:
            result = "Wrong"
            marks_obtained = "0"

        submission, created = SubmittedExamination.objects.update_or_create(
            student_id=student_id,
            exam_id=exam_id,
            question=str(question_id),
            examdetails=exam_details_instance,  # use passed exam_details_id here
            defaults={
                "type": question_instance.type,
                "marks": marks,
                "marks_obtained": marks_obtained,
                "submitted_answer": submitted_answer,
                "answer": correct_answer,
                "result": result,
            }
        )

        return Response({
            "message": "Answer updated successfully." if not created else "Answer submitted successfully.",
            "question_id": question_id,
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"An error occurred while saving answer: {str(e)}")
        return Response({"error": "An internal server error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_of_all_cancelled_student(request):
    try:
        students = Student.objects.filter(is_cancelled=True).order_by('-id')

        student_data = []
        for student in students:
            enrolled = Enrolled.objects.filter(student=student).first()

            student_data.append({
                "id": student.id,
                "mobile": student.mobile,
                "name": student.name,
                "registration_id": student.registration_id,
                "email": student.email,
                "current_semyear": enrolled.current_semyear if enrolled else "",
                "enrollment_id": student.enrollment_id,
                "student_name": student.name,
                "university_name": student.university.university_name if student.university else "",
                "source": 'QR' if student.is_quick_register else 'SR',
                "study_pattern_mode": enrolled.course_pattern if enrolled and enrolled.course_pattern else "",
                "entry_mode": enrolled.entry_mode if enrolled and enrolled.entry_mode else "",
                "enrollment_date": student.enrollment_date.strftime('%Y-%m-%d') if student.enrollment_date else ""
            })

        return Response({"status": "success", "data": student_data}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error fetching cancelled students: {str(e)}")
        return Response({"status": "error", "message": "Something went wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def document_management(request, enrollment_id):
    if not enrollment_id:
        logger.error("Missing required parameter: enrollment_id in request URL")
        return Response(
            {"error": "Missing required parameter: enrollment_id"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Fetch the student by enrollment_id
        student = Student.objects.get(enrollment_id=enrollment_id)
        #logger.info(f"Fetching documents for student: {student.name} (Enrollment ID: {student.enrollment_id})")

        # Fetch student documents
        student_documents = StudentDocuments.objects.filter(student=student)
        student_documents_data = StudentDocumentsSerializerGET(student_documents, many=True).data

        # Fetch student qualifications
        qualifications = Qualification.objects.filter(student=student).first()
        qualification_data = QualificationSerializer(qualifications).data if qualifications else None

        # Prepare response data
        response_data = {
            "image": student.image.url if student.image else None,
            "documents": student_documents_data,
            "qualifications": qualification_data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Student.DoesNotExist:
        logger.error(f"Student with enrollment_id {enrollment_id} not found.")
        return Response(
            {"error": "Student not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    except Exception as e:
        logger.error(f"Unexpected error while retrieving documents for student {enrollment_id}: {str(e)}")
        return Response(
            {"error": "An unexpected error occurred while retrieving student documents."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        


@api_view(["POST"])
def save_exam_timer(request):
    student_id = request.data.get("student_id")
    exam_id = request.data.get("exam_id")
    time_left_ms_raw = request.data.get("time_left_ms")
    exam_details_id = request.data.get("exam_details_id")

    if not all([student_id, exam_id, time_left_ms_raw, exam_details_id]):
        return Response({"error": "Missing data"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        time_left_ms = int(time_left_ms_raw)
    except (TypeError, ValueError):
        return Response({"error": "Invalid time_left_ms, must be integer"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        examdetails_instance = StudentAppearingExam.objects.get(id=int(exam_details_id))
    except (StudentAppearingExam.DoesNotExist, ValueError):
        return Response({"error": "Invalid exam_details_id"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        student_obj = Student.objects.get(id=student_id)
        exam_obj = Examination.objects.get(id=exam_id)
    except (Student.DoesNotExist, Examination.DoesNotExist):
        return Response({"error": "Student or Exam not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        session = ExamSession.objects.get(
            student=student_obj,
            exam=exam_obj,
            examdetails=examdetails_instance
        )
        session.time_left_ms = time_left_ms
        session.save()
        created = False
    except ExamSession.DoesNotExist:
        duration_minutes = getattr(exam_obj, "examduration", None)
        if duration_minutes is not None:
            init_time_left_ms = int(duration_minutes) * 60 * 1000
        else:
            init_time_left_ms = time_left_ms

        session = ExamSession.objects.create(
            student=student_obj,
            exam=exam_obj,
            examdetails=examdetails_instance,
            time_left_ms=init_time_left_ms
        )
        created = True

    return Response({"status": "saved", "created": created, "time_left_ms": session.time_left_ms}, status=status.HTTP_200_OK)



@api_view(["GET"])
def get_exam_timer(request):
    student_id = request.query_params.get("student_id")
    exam_id = request.query_params.get("exam_id")
    exam_details_id = request.query_params.get("exam_details_id")

    if not all([student_id, exam_id, exam_details_id]):
        return Response({"error": "Missing data"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        session = ExamSession.objects.get(
            student_id=student_id,
            exam_id=exam_id,
            examdetails_id=exam_details_id
        )
        return Response({"time_left_ms": session.time_left_ms})
    except ExamSession.DoesNotExist:
        return Response({"time_left_ms": None})


# @api_view(['POST'])
# def save_result_after_exam(request):
#     """
#     Save the result after an exam is finished.
#     Use provided exam_details_id instead of latest.
#     """
#     try:
#         data = request.data
#         student_id = data.get("student_id")
#         exam_id = data.get("exam_id")
#         exam_details_id = data.get("exam_details_id")  # <-- new param
#         created_by = data.get("created_by", None)
#         modified_by = data.get("modified_by", None)

#         if not student_id or not exam_id:
#             return Response({"error": "Missing required fields: student_id or exam_id"}, 
#                             status=status.HTTP_400_BAD_REQUEST)

#         try:
#             student_id_int = int(student_id)
#             exam_id_int = int(exam_id)
#         except (TypeError, ValueError):
#             return Response({"error": "Invalid student_id or exam_id"}, status=status.HTTP_400_BAD_REQUEST)

#         examdetails_instance = None
#         if exam_details_id:
#             try:
#                 exam_details_id_int = int(exam_details_id)
#                 examdetails_instance = StudentAppearingExam.objects.get(id=exam_details_id_int)
#             except (ValueError, StudentAppearingExam.DoesNotExist):
#                 return Response({"error": "Invalid exam_details_id"}, status=status.HTTP_400_BAD_REQUEST)

#         if not examdetails_instance:
#             # fallback: get latest
#             examdetails_instance = StudentAppearingExam.objects.filter(
#                 student_id__contains=[student_id_int],
#                 exam_id=exam_id_int
#             ).order_by('-id').first()

#         if not examdetails_instance:
#             return Response({"error": "No StudentAppearingExam record found for given student and exam."},
#                             status=status.HTTP_404_NOT_FOUND)


#         questions = Questions.objects.filter(exam_id=exam_id_int)

#         for question in questions:
#             submitted_answer = SubmittedExamination.objects.filter(
#                 student_id=student_id_int,
#                 exam_id=exam_id_int,
#                 question=str(question.id),
#                 examdetails=examdetails_instance
#             ).order_by('-id').first()

#             if not submitted_answer:
#                 SubmittedExamination.objects.create(
#                     student_id=student_id_int,
#                     exam_id=exam_id_int,
#                     question=str(question.id),
#                     type=question.type,
#                     marks=question.marks,
#                     marks_obtained="0",
#                     submitted_answer="NA",
#                     answer=question.answer,
#                     result="Wrong",
#                     examdetails=examdetails_instance
#                 )

#         total_questions = questions.count()
#         attempted = SubmittedExamination.objects.filter(
#             student_id=student_id_int, 
#             exam_id=exam_id_int,
#             examdetails=examdetails_instance
#         ).filter(
#                 ~Q(submitted_answer="NA"),
#                 ~Q(submitted_answer="")
#             ).count()
#         score = SubmittedExamination.objects.filter(
#             student_id=student_id_int, 
#             exam_id=exam_id_int, 
#             result="Right",
#             examdetails=examdetails_instance
#         ).count()
#         total_marks = questions.aggregate(Sum('marks'))['marks__sum'] or 0

#         exam = Examination.objects.get(id=exam_id_int)
#         passing_marks = int(exam.passingmarks or 50)
#         percentage = (score / total_questions) * 100 if total_questions > 0 else 0
#         result_status = "Passed" if percentage >= passing_marks else "Failed"

#         result_obj, created = Result.objects.update_or_create(
#             student_id=student_id_int,
#             exam_id=exam_id_int,
#             examdetails=examdetails_instance,
#             defaults={
#                 'total_question': str(total_questions),
#                 'attempted': str(attempted),
#                 'total_marks': str(total_marks),
#                 'score': str(score),
#                 'result': result_status,
#                 'percentage': percentage,
#                 'created_by': created_by,
#                 'modified_by': modified_by,
#             }
#         )

#         return Response({
#             "message": "Exam results saved successfully",
#             "result_id": result_obj.id
#         }, status=status.HTTP_200_OK)

#     except Exception as e:
#         logger.exception(f"Error saving exam result: {str(e)}")
#         return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# modify by ankit 29-09-25 for add more response
from django.db.models.functions import Cast
from django.db.models import Q, Sum, IntegerField

# @api_view(['POST'])
# def save_result_after_exam(request):
#     """
#     Save the result after an exam is finished.
#     Uses provided exam_details_id when given; otherwise falls back to latest.
#     Also returns stats and time taken.

#     Response includes:
#       - total_questions
#       - total_marks
#       - attempted_answers
#       - unanswered
#       - right_answers
#       - wrong_answers
#       - score
#       - percentage
#       - result ("Passed"/"Failed")
#       - time_taken_ms (if computable)
#       - time_left_ms (latest saved)
#     """
#     try:
#         data = request.data
#         student_id = data.get("student_id")
#         exam_id = data.get("exam_id")
#         exam_details_id = data.get("exam_details_id")  # optional
#         created_by = data.get("created_by", None)
#         modified_by = data.get("modified_by", None)

#         if not student_id or not exam_id:
#             return Response(
#                 {"error": "Missing required fields: student_id or exam_id"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             student_id_int = int(student_id)
#             exam_id_int = int(exam_id)
#         except (TypeError, ValueError):
#             return Response({"error": "Invalid student_id or exam_id"},
#                             status=status.HTTP_400_BAD_REQUEST)

#         # --- locate StudentAppearingExam (either explicit id or latest for student+exam)
#         examdetails_instance = None
#         if exam_details_id:
#             try:
#                 exam_details_id_int = int(exam_details_id)
#                 examdetails_instance = StudentAppearingExam.objects.get(id=exam_details_id_int)
#             except (ValueError, StudentAppearingExam.DoesNotExist):
#                 return Response({"error": "Invalid exam_details_id"},
#                                 status=status.HTTP_400_BAD_REQUEST)

#         if not examdetails_instance:
#             examdetails_instance = (
#                 StudentAppearingExam.objects
#                 .filter(student_id__contains=[student_id_int], exam_id=exam_id_int)
#                 .order_by('-id')
#                 .first()
#             )

#         if not examdetails_instance:
#             return Response(
#                 {"error": "No StudentAppearingExam record found for given student and exam."},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         # --- ensure every question has a SubmittedExamination row (create NA for missing)
#         questions = Questions.objects.filter(exam_id=exam_id_int)

#         for question in questions:
#             submitted_answer = SubmittedExamination.objects.filter(
#                 student_id=student_id_int,
#                 exam_id=exam_id_int,
#                 question=str(question.id),
#                 examdetails=examdetails_instance
#             ).order_by('-id').first()

#             if not submitted_answer:
#                 SubmittedExamination.objects.create(
#                     student_id=student_id_int,
#                     exam_id=exam_id_int,
#                     question=str(question.id),
#                     type=question.type,
#                     marks=question.marks,
#                     marks_obtained="0",
#                     submitted_answer="NA",
#                     answer=question.answer,
#                     result="Wrong",
#                     examdetails=examdetails_instance
#                 )

#         # --- stats
#         total_questions = questions.count()

#         # Sum total marks (marks is CharField, so cast to int)
#         total_marks = (
#             questions.annotate(m_int=Cast('marks', IntegerField()))
#                      .aggregate(total=Sum('m_int'))['total'] or 0
#         )

#         # Case-insensitive "NA"/"na" or empty => unanswered
#         unanswered_qs = SubmittedExamination.objects.filter(
#             student_id=student_id_int,
#             exam_id=exam_id_int,
#             examdetails=examdetails_instance
#         ).filter(
#             Q(submitted_answer__iexact="na") | Q(submitted_answer="") | Q(submitted_answer__isnull=True)
#         ).count()

#         attempted_answers = total_questions - unanswered_qs

#         right_answers = SubmittedExamination.objects.filter(
#             student_id=student_id_int,
#             exam_id=exam_id_int,
#             result="Right",
#             examdetails=examdetails_instance
#         ).count()

#         wrong_answers = SubmittedExamination.objects.filter(
#             student_id=student_id_int,
#             exam_id=exam_id_int,
#             result="Wrong",
#             examdetails=examdetails_instance
#         ).count()

#         # Score: count of right answers (you were already using this)
#         score = right_answers

#         # --- exam & pass/fail
#         exam = Examination.objects.get(id=exam_id_int)

#         # If passingmarks is a percentage threshold (as your code implied):
#         try:
#             passing_marks = int(exam.passingmarks or 50)
#         except (TypeError, ValueError):
#             passing_marks = 50

#         percentage = (score / total_questions) * 100 if total_questions > 0 else 0.0
#         result_status = "Passed" if percentage >= passing_marks else "Failed"

#         # --- derive time taken (ms) from ExamSession(time_left_ms) and exam.examduration (minutes)
#         duration_minutes = getattr(exam, "examduration", None)
#         time_left_ms_latest = None
#         time_taken_ms = None

#         try:
#             session = ExamSession.objects.get(
#                 student_id=student_id_int,
#                 exam_id=exam_id_int,
#                 examdetails=examdetails_instance
#             )
#             time_left_ms_latest = int(session.time_left_ms)
#         except ExamSession.DoesNotExist:
#             session = None

#         # If examduration is set, compute time taken as duration - time_left
#         if duration_minutes is not None:
#             try:
#                 duration_ms = int(duration_minutes) * 60 * 1000
#                 if time_left_ms_latest is not None:
#                     time_taken_ms = max(0, duration_ms - time_left_ms_latest)
#             except (TypeError, ValueError):
#                 pass

#         # --- upsert Result
#         result_obj, created = Result.objects.update_or_create(
#             student_id=student_id_int,
#             exam_id=exam_id_int,
#             examdetails=examdetails_instance,
#             defaults={
#                 'total_question': str(total_questions),
#                 'attempted': str(attempted_answers),
#                 'total_marks': str(total_marks),
#                 'score': str(score),
#                 'result': result_status,
#                 'percentage': percentage,
#                 'created_by': created_by,
#                 'modified_by': modified_by,
#             }
#         )

#         return Response({
#             "message": "Exam results saved successfully",
#             "result_id": result_obj.id,
#             # --- extra stats you asked for
#             "total_questions": total_questions,
#             "total_marks": total_marks,
#             "attempted_answers": attempted_answers,
#             "unanswered": unanswered_qs,
#             # "right_answers": right_answers,
#             # "wrong_answers": wrong_answers,
#             # "score": score,
#             # "percentage": percentage,
#             # "result": result_status,
#             # time info
#             "time_left_ms": time_left_ms_latest,
#             "time_taken_ms": time_taken_ms,
#         }, status=status.HTTP_200_OK)

#     except Exception as e:
#         logger.exception(f"Error saving exam result: {str(e)}")
#         return Response({"error": "Internal server error"},
#                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.db import transaction
from django.db.models import Sum, Count, Q, IntegerField, FloatField
from django.db.models.functions import Cast
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
@api_view(['POST'])
@transaction.atomic
def save_result_after_exam(request):
    try:
        data = request.data
        student_id = data.get("student_id")
        exam_id = data.get("exam_id")
        exam_details_id = data.get("exam_details_id")  # optional
        created_by = data.get("created_by")
        modified_by = data.get("modified_by")

        if not student_id or not exam_id:
            return Response({"error": "Missing required fields: student_id or exam_id"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            student_id = int(student_id)
            exam_id = int(exam_id)
        except (TypeError, ValueError):
            return Response({"error": "Invalid student_id or exam_id"}, status=400)

        # --- locate StudentAppearingExam (explicit or latest exact match)
        examdetails_instance = None
        if exam_details_id:
            try:
                examdetails_instance = StudentAppearingExam.objects.get(id=int(exam_details_id))
            except (ValueError, StudentAppearingExam.DoesNotExist):
                return Response({"error": "Invalid exam_details_id"}, status=400)

        if not examdetails_instance:
            examdetails_instance = (
                StudentAppearingExam.objects
                .filter(student_id=student_id, exam_id=exam_id)   # FIX: exact match, not contains
                .order_by('-id')
                .first()
            )
        if not examdetails_instance:
            return Response({"error": "No StudentAppearingExam found."}, status=404)

        # --- ensure each question has a submitted record (create NA without labeling as Wrong)
        questions = Questions.objects.filter(exam_id=exam_id)
        existing_q_ids = set(
            SubmittedExamination.objects.filter(
                student_id=student_id, exam_id=exam_id, examdetails=examdetails_instance
            ).values_list('question', flat=True)
        )
        bulk_create = []
        for q in questions:
            if str(q.id) not in existing_q_ids:
                bulk_create.append(SubmittedExamination(
                    student_id=student_id,
                    exam_id=exam_id,
                    question=str(q.id),
                    type=q.type,
                    marks=q.marks,
                    marks_obtained="0",
                    submitted_answer="NA",
                    answer=q.answer,
                    result=None,                      # FIX: leave None for NA, don’t mark Wrong
                    examdetails=examdetails_instance
                ))
        if bulk_create:
            SubmittedExamination.objects.bulk_create(bulk_create, ignore_conflicts=True)

        total_questions = questions.count()

        # If your exam total marks are stored on Examination, use that;
        # otherwise, sum question.marks (they're CharFields, so cast)
        exam = Examination.objects.get(id=exam_id)
        try:
            total_marks = int(exam.totalmarks)
        except (TypeError, ValueError):
            total_marks = (
                questions.annotate(m_int=Cast('marks', IntegerField()))
                         .aggregate(total=Sum('m_int'))['total'] or 0
            )

        # --- aggregate from SubmittedExamination in ONE query
        sub_qs = SubmittedExamination.objects.filter(
            student_id=student_id,
            exam_id=exam_id,
            examdetails=examdetails_instance
        ).annotate(
            mo=Cast('marks_obtained', FloatField())
        )

        agg = sub_qs.aggregate(
            unanswered=Count('id', filter=Q(submitted_answer__iexact='na') | Q(submitted_answer__isnull=True) | Q(submitted_answer="")),
            right_answers=Count('id', filter=Q(result__iexact='Right')),
            wrong_answers=Count('id', filter=Q(result__iexact='Wrong')),
            sum_marks=Sum('mo'),
        )

        unanswered = agg['unanswered'] or 0
        right_answers = agg['right_answers'] or 0
        wrong_answers = agg['wrong_answers'] or 0
        sum_marks = float(agg['sum_marks'] or 0.0)

        attempted_answers = total_questions - unanswered

        # --- choose the definition of score:
        # FIX: score should be SUM of marks_obtained (not count of rights)
        score = sum_marks

        # pass/fail: compare percentage of marks, not question count
        try:
            passing_threshold_pct = float(exam.passingmarks or 50)
        except (TypeError, ValueError):
            passing_threshold_pct = 50.0

        percentage = (score / total_marks * 100) if total_marks > 0 else 0.0
        result_status = "Passed" if percentage >= passing_threshold_pct else "Failed"

        # --- time metrics (same as your logic)
        time_left_ms_latest = None
        time_taken_ms = None
        try:
            session = ExamSession.objects.get(
                student_id=student_id, exam_id=exam_id, examdetails=examdetails_instance
            )
            time_left_ms_latest = int(session.time_left_ms)
        except ExamSession.DoesNotExist:
            session = None

        try:
            duration_ms = int(exam.examduration) * 60 * 1000
            if time_left_ms_latest is not None:
                time_taken_ms = max(0, duration_ms - time_left_ms_latest)
        except (TypeError, ValueError):
            pass

        # --- upsert Result (score as marks-sum, stored as string due to CharField)
        result_obj, created = Result.objects.update_or_create(
            student_id=student_id,
            exam_id=exam_id,
            examdetails=examdetails_instance,
            defaults={
                'total_question': str(total_questions),
                'attempted': str(attempted_answers),
                'total_marks': str(total_marks),
                'score': str(score),             # FIX: save marks sum
                'result': result_status,
                'percentage': percentage,
                'created_by': created_by,
                'modified_by': modified_by,
            }
        )

        return Response({
            "message": "Exam results saved successfully",
            "result_id": result_obj.id,
            "total_questions": total_questions,
            "total_marks": total_marks,
            "attempted_answers": attempted_answers,
            "unanswered": unanswered,
            "right_answers": right_answers,
            "wrong_answers": wrong_answers,
            "score": score,
            "percentage": percentage,
            "result": result_status,
            "time_left_ms": time_left_ms_latest,
            "time_taken_ms": time_taken_ms,
        }, status=200)

    except Exception as e:
        import logging
        logging.exception("save_result_after_exam failed: %s", e)
        return Response({"error": "Internal server error"}, status=500)

@api_view(['GET'])
def check_exam_result(request):
    """
    Check if a result has been created for a student and exam.
    """
    try:
        student_id = request.query_params.get("student_id")
        exam_id = request.query_params.get("exam_id")
        
        print(student_id," --->student_id",exam_id,'" --->exam_id"')

        if not student_id or not exam_id:
            return Response({"error": "Missing required fields: student_id or exam_id"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the result exists
        result = Result.objects.filter(student_id=student_id, exam_id=exam_id).exists()

        return Response({
            "has_result": result
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"An error occurred while checking exam result: {str(e)}")
        return Response({"error": "An internal server error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
@api_view(['GET'])
def check_exam_result(request):
    """
    Check if a result has been created for a student, exam, and specific examdetails (StudentAppearingExam).
    """
    try:
        student_id = request.query_params.get("student_id")
        exam_id = request.query_params.get("exam_id")
        examdetails_id = request.query_params.get("examdetails_id")

        # Validate presence
        if not student_id or not exam_id or not examdetails_id:
            return Response({"error": "Missing required fields: student_id, exam_id or examdetails_id"}, status=status.HTTP_400_BAD_REQUEST)

        # Convert to integers safely
        try:
            student_id_int = int(student_id)
            exam_id_int = int(exam_id)
            examdetails_id_int = int(examdetails_id)
        except ValueError:
            return Response({"error": "student_id, exam_id and examdetails_id must be integers"}, status=status.HTTP_400_BAD_REQUEST)

        # Filter with typed parameters
        result_exists = Result.objects.filter(
            student_id=student_id_int,
            exam_id=exam_id_int,
            examdetails_id=examdetails_id_int
        ).exists()

        return Response({"has_result": result_exists}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Error checking exam result: {str(e)}")
        return Response({"error": "An internal server error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  


@api_view(['GET'])
def check_exam_availability(request):
    """
    Check if the current time is between exam start and end time, and if the exam date is valid for the student.
    """
    try:
        student_id = request.query_params.get("student_id")
        exam_id = request.query_params.get("exam_id")

        if not student_id or not exam_id:
            return Response({"error": "Missing student_id or exam_id."}, status=400)

        # Get the exam and student appearing data
        student_exam = StudentAppearingExam.objects.filter(exam_id=exam_id, student_id__contains=[student_id]).first()

        if not student_exam:
            return Response({"error": "Student is not enrolled for this exam."}, status=404)

        # Get exam start/end date and time
        exam = Examination.objects.get(id=exam_id)
        print('examexam',exam)
        print('examstartdate',student_exam.examstartdate)
        print('examenddate',student_exam.examenddate)
        print('examstarttime',student_exam.examstarttime)
        print('examendtime',student_exam.examendtime)

        start_datetime = datetime.combine(student_exam.examstartdate, student_exam.examstarttime)
        end_datetime = datetime.combine(student_exam.examenddate, student_exam.examendtime)

        now = datetime.now()

        # Check if the current date and time are within the exam window
        is_within_exam_window = now >= start_datetime and now <= end_datetime

        if is_within_exam_window:
            return Response({"can_start": True, "message": "You can start the exam."})
        else:
            return Response({"can_start": False, "message": "The exam is not available at this time."})

    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=500)
      

@api_view(['POST'])
def create_category(request):
    serializer = CategoriesSerializer(data=request.data)
    if serializer.is_valid():
        try:
            serializer.save()
            #logger.info(f"Category created successfully: {serializer.data}")
            return Response({
                'message': 'Category created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error saving category: {str(e)}", exc_info=True)
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        logger.warning(f"Category creation failed due to validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
def update_category(request, pk):
    try:
        category = Categories.objects.get(pk=pk)
    except Categories.DoesNotExist:
        logger.warning(f"Category update failed: Category with ID {pk} not found")
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CategoriesSerializer(category, data=request.data, partial=(request.method == 'PATCH'))
    if serializer.is_valid():
        try:
            serializer.save()
            #logger.info(f"Category updated successfully (ID: {pk}): {serializer.data}")
            return Response({
                'message': 'Category updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error updating category ID {pk}: {str(e)}", exc_info=True)
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        logger.warning(f"Category update failed for ID {pk} due to validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
@api_view(['GET'])
def list_categories(request):
    try:
        categories = Categories.objects.all()
        serializer = CategoriesSerializer(categories, many=True)
        #logger.info(f"{len(categories)} categories fetched successfully.")
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}", exc_info=True)
        return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
      
@api_view(['POST'])
def create_source(request):
    serializer = SourceSerializer(data=request.data)
    if serializer.is_valid():
        try:
            serializer.save()
            #logger.info(f"Source created: {serializer.data}")
            return Response({'message': 'Source created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error saving source: {str(e)}", exc_info=True)
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        logger.warning(f"Validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
def update_source(request, pk):
    try:
        source = Source.objects.get(pk=pk)
    except Source.DoesNotExist:
        logger.warning(f"Source with ID {pk} not found")
        return Response({'error': 'Source not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SourceSerializer(source, data=request.data, partial=(request.method == 'PATCH'))
    if serializer.is_valid():
        try:
            serializer.save()
            #logger.info(f"Source updated (ID {pk}): {serializer.data}")
            return Response({'message': 'Source updated successfully', 'data': serializer.data})
        except Exception as e:
            logger.error(f"Error updating source (ID {pk}): {str(e)}", exc_info=True)
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        logger.warning(f"Validation failed during update for ID {pk}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_sources(request):
    try:
        sources = Source.objects.all()
        serializer = SourceSerializer(sources, many=True)
        #logger.info(f"{len(sources)} sources fetched.")
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching sources: {str(e)}", exc_info=True)
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
@api_view(['GET'])
def list_statuses(request):
    try:
        statuses = Status.objects.all().order_by('-id')
        serializer = StatusSerializer(statuses, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error listing statuses: {e}")
        return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_status(request):
    serializer = StatusSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Status created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    logger.warning(f"Create status validation error: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
def update_status(request, pk):
    try:
        status_instance = Status.objects.get(pk=pk)
    except Status.DoesNotExist:
        logger.warning(f"Status not found with id: {pk}")
        return Response({'error': 'Status not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = StatusSerializer(status_instance, data=request.data, partial=(request.method == 'PATCH'))
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Status updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
    logger.warning(f"Update status validation error: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_common_lead_labels(request):
    try:
        labels = Common_Lead_Label_Tags.objects.all().order_by('-id')
        serializer = CommonLeadLabelSerializer(labels, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error listing common lead labels: {e}")
        return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_common_lead_label(request):
    serializer = CommonLeadLabelSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Common Lead Label created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    logger.warning(f"Validation error while creating label: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
def update_common_lead_label(request, pk):
    try:
        label = Common_Lead_Label_Tags.objects.get(pk=pk)
    except Common_Lead_Label_Tags.DoesNotExist:
        logger.warning(f"Label not found with id: {pk}")
        return Response({'error': 'Common Lead Label not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CommonLeadLabelSerializer(label, data=request.data, partial=(request.method == 'PATCH'))
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Common Lead Label updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
    logger.warning(f"Validation error while updating label: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def sync_answers(request):
    student_id = request.query_params.get("student_id")
    exam_id = request.query_params.get("exam_id")
    exam_details_id = request.query_params.get("exam_details_id")  # new param

    if not student_id or not exam_id or not exam_details_id:
        return Response({"error": "Missing student_id, exam_id, or exam_details_id"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        student_obj = Student.objects.get(id=student_id)
        exam_obj = Examination.objects.get(id=exam_id)
        exam_details_obj = StudentAppearingExam.objects.get(id=exam_details_id)
    except (Student.DoesNotExist, Examination.DoesNotExist, StudentAppearingExam.DoesNotExist):
        return Response({"error": "Student, Exam, or Exam Details not found"}, status=status.HTTP_404_NOT_FOUND)

    submitted_answers = SubmittedExamination.objects.filter(
        student=student_obj,
        exam=exam_obj,
        examdetails=exam_details_obj
    )

    answer_dict = {}
    for ans in submitted_answers:
        try:
            question_id_int = int(ans.question)
            answer_dict[question_id_int] = ans.submitted_answer
        except (ValueError, TypeError):
            continue

    return Response({"answers": answer_dict}, status=status.HTTP_200_OK)


@api_view(['POST'])
def registered_save_enrollment_to_next_semyear(request):
    student_id = request.data.get('student_id')
    current_semyear = request.data.get('current_semyear')
    total_semyear = request.data.get('total_semyear')
    next_semyear = request.data.get('next_semyear')

    if not all([student_id, current_semyear, total_semyear, next_semyear]):
        logger.warning("Missing required fields")
        return Response({"status": "error", "message": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        current = int(current_semyear)
        total = int(total_semyear)
        next_s = int(next_semyear)
    except ValueError:
        logger.error("Invalid data types for semester fields")
        return Response({"status": "error", "message": "Invalid semester values"}, status=status.HTTP_400_BAD_REQUEST)

    if total <= current:
        logger.warning(f"Next semester not allowed. Current: {current}, Total: {total}")
        return Response({"status": "error", "message": "Cannot enroll beyond total sem/year"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        enrolled = Enrolled.objects.get(student=student_id)
        enrolled.current_semyear = next_s
        enrolled.save()
        #logger.info(f"Student {student_id} promoted to sem/year {next_s}")
        return Response({"status": "success", "message": "Student enrolled to next semester/year"}, status=status.HTTP_200_OK)
    except Enrolled.DoesNotExist:
        logger.error(f"No enrollment found for student ID {student_id}")
        return Response({"status": "error", "message": "Enrollment not found"}, status=status.HTTP_404_NOT_FOUND)
      
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_exam_data_to_excel(request):
    user = request.user
    #logger.info(f"[EXPORT] Request received by user: {user.username} (ID: {user.id})")

    if not (user.is_superuser or getattr(user, 'is_data_entry', False)):
        logger.warning(f"[EXPORT] Unauthorized access attempt by user: {user.username}")
        return Response({"message": "Unauthorized access"}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    university = data.get("university")
    course = data.get("course")
    stream = data.get('stream')
    session = data.get('session')
    studypattern = data.get('studypattern')
    semyear = data.get('semyear')
    substream = data.get('substream')

    logger.debug(f"[EXPORT] Filters received: university={university}, course={course}, stream={stream}, session={session}, studypattern={studypattern}, semyear={semyear}, substream={substream}")

    try:
        filters = Q(university=university, course=course, stream=stream)
        if session not in ['0', '', None]:
            filters &= Q(session=session)
        if studypattern not in ['0', '', None]:
            filters &= Q(studypattern=studypattern)
        if semyear not in ['0', '', None]:
            filters &= Q(semyear=semyear)
        if substream not in ['0', '', None]:
            filters &= Q(substream=substream)

        exams = Examination.objects.filter(filters)
        if not exams.exists():
            #logger.info("[EXPORT] No matching exams found for the given filters.")
            return Response({"message": "No results found"}, status=status.HTTP_400_BAD_REQUEST)

        formatted_data = []
        for exam in exams:
            logger.debug(f"[EXPORT] Processing exam: ID={exam.id}, subject={exam.subject_id}")
            subject = Subject.objects.filter(id=exam.subject_id).first()
            student_exam_qs = StudentAppearingExam.objects.filter(exam=exam.id)

            if student_exam_qs.exists():
                serializer = StudentAppearingExamSerializer(student_exam_qs, many=True)
                for record in serializer.data:
                    for student_id in record['student_id']:
                        logger.debug(f"[EXPORT] Processing student ID={student_id} for exam ID={exam.id}")
                        has_appeared = ExamSession.objects.filter(
                            student_id=student_id,
                            exam=exam.id,
                            examdetails_id=record['id']
                        )
                        submitted_exam = Result.objects.filter(
                            student_id=student_id,
                            exam=exam,
                            examdetails_id=record['id']
                        )

                        status_str = "Not Appeared"
                        if has_appeared.exists() and submitted_exam.exists():
                            status_str = "Appeared"
                        elif has_appeared.exists():
                            status_str = "Ongoing Exam"

                        student = Student.objects.filter(id=student_id).first()
                        university_obj = University.objects.filter(id=university).first()
                        course_obj = Course.objects.filter(id=course).first()
                        stream_obj = Stream.objects.filter(id=stream).first()
                        substream_obj = SubStream.objects.filter(id=substream).first() if substream else None
                        enrolled = Enrolled.objects.filter(student_id=student_id).first()

                        if not enrolled:
                            logger.warning(f"[EXPORT] No enrollment found for student ID={student_id}. Skipping.")
                            continue

                        course_duration = int(enrolled.total_semyear) if enrolled.course_pattern == 'Annual' else int(enrolled.total_semyear) / 2

                        marks_obtained = ''
                        attempted_questions = ''
                        result_status = ''
                        if status_str == "Appeared":
                            sub_exam = submitted_exam.first()
                            if sub_exam:
                                marks_obtained = sub_exam.score
                                attempted_questions = sub_exam.attempted
                                result_status = sub_exam.result

                        formatted_data.append({
                            'University': university_obj.university_name if university_obj else '',
                            'Course': course_obj.name if course_obj else '',
                            'Stream': stream_obj.name if stream_obj else '',
                            'Substream': substream_obj.name if substream_obj else '',
                            'Session': session,
                            'Study Pattern': studypattern,
                            'Semester/Year': semyear,
                            'Course Duration': course_duration,
                            'Subject Name': subject.name if subject else '',
                            'Student Name': student.name if student else '',
                            'Student Email ID': student.email if student else '',
                            'Student Mobile Number': student.mobile if student else '',
                            'Enrollment ID': student.enrollment_id if student else '',
                            'Exam Start Time': record['examstarttime'],
                            'Exam End Time': record['examendtime'],
                            'Exam Start Date': record['examstartdate'],
                            'Exam End Date': record['examenddate'],
                            'Status': status_str,
                            'Total Marks': exam.totalmarks,
                            'Passing Marks': exam.passingmarks,
                            'Marks Obtained': marks_obtained,
                            'Questions Attempted': attempted_questions,
                            'Result': result_status,
                        })

        if not formatted_data:
            #logger.info("[EXPORT] No student data available to export.")
            return Response({"message": "No students assigned"}, status=status.HTTP_400_BAD_REQUEST)

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Exam Data"

        headers = list(formatted_data[0].keys())
        for col_num, header in enumerate(headers, 1):
            cell = sheet.cell(row=1, column=col_num)
            cell.value = header.upper()
            cell.font = Font(bold=True)

        for row_num, row_data in enumerate(formatted_data, 2):
            for col_num, header in enumerate(headers, 1):
                value = row_data[header]
                sheet.cell(row=row_num, column=col_num).value = value.upper() if isinstance(value, str) else value

        #logger.info(f"[EXPORT] Excel file prepared with {len(formatted_data)} records.")

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response['Content-Disposition'] = 'attachment; filename="exam_data_export.xlsx"'
        workbook.save(response)

        #logger.info("[EXPORT] Excel file successfully sent as response.")
        return response

    except Exception as e:
        logger.exception(f"[EXPORT] An unexpected error occurred: {str(e)}")
        return Response({"message": "An error occurred during export."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

import zipfile
import io

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def view_all_assigned_students_api(request):
    print('inside view_all_assigned_students_api')
    user = request.user
    logger.info(f"[VIEW-STUDENTS] API accessed by user: {user.username} (ID: {user.id})")

    if not (user.is_superuser or getattr(user, 'is_data_entry', False)):
        logger.warning(f"[VIEW-STUDENTS] Unauthorized access attempt by {user.username}")
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    try:
        data = request.data
        university_id = int(data.get("university"))
        course_id = int(data.get("course"))
        stream_id = int(data.get("stream") or data.get("Stream"))
        session = data.get("session", "").strip()
        studypattern = data.get("studypattern", "").upper().strip()
        semyear = data.get("semyear", "").strip()
        substream_id = data.get("substream")

        # ✅ Ensure semyear is mandatory
        if not semyear:
            logger.warning("[VIEW-STUDENTS] Missing semyear in request.")
            return Response({'error': 'Semester/Year (semyear) is required.'}, status=400)

        # Prepare filter for matching results via exams
        exam_filter = {
            'course_id': course_id,
            'stream_id': stream_id,
            'semyear__iexact': semyear
        }

        if substream_id and str(substream_id).lower() != 'null':
            try:
                exam_filter['substream_id'] = int(substream_id)
            except ValueError:
                logger.error("[VIEW-STUDENTS] Invalid substream_id format.")
                return Response({'error': 'Invalid substream_id'}, status=400)

        if session:
            exam_filter['session__iexact'] = session

        if studypattern:
            exam_filter['studypattern__iexact'] = studypattern

        logger.debug(f"[VIEW-STUDENTS] Exam filter: {exam_filter}")

        # Get results that match the exam filters
        matched_results = Result.objects.filter(
            exam__in=Examination.objects.filter(**exam_filter),
            student__university_id=university_id
        ).select_related('student', 'exam')

        # Build unique student response from results
        student_data = []
        seen_ids = set()

        for r in matched_results:
            if r.student and r.student.id not in seen_ids:
                student = r.student
                seen_ids.add(student.id)
                student_data.append({
                    "student_id": student.id,
                    "name": student.name,
                    "email": student.email,
                    "mobile": student.mobile,
                    "enrollment_id": student.enrollment_id,
                    "current_semyear": "",  # optional: could be pulled from Enrolled
                    "session": r.exam.session,
                    "entry_mode": "",       # optional: could be pulled from Enrolled
                    "course_pattern": r.exam.studypattern,
                })

        #logger.info(f"[VIEW-STUDENTS] Found {len(student_data)} students with result records")
        return Response({'message': 'Students fetched successfully', 'students': student_data}, status=200)

    except Exception as e:
        logger.exception(f"[VIEW-STUDENTS] Unexpected error: {str(e)}")
        return Response({'error': 'Internal server error'}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def fetch_complete_student_data_api(request):
    user = request.user
    #logger.info(f"[EXPORT-ZIP] Started by {user.username} (ID={user.id})")

    if not (user.is_superuser or getattr(user, 'is_data_entry', False)):
        logger.warning(f"[EXPORT-ZIP] Unauthorized access attempt by {user.username}")
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    try:
        data = request.data

        # FIX: ensure student_ids is parsed correctly
        raw_ids = data.get('student_ids', [])
        if isinstance(raw_ids, str):
            try:
                student_ids = json.loads(raw_ids)
            except json.JSONDecodeError:
                return Response({'error': 'Invalid student_ids format'}, status=400)
        else:
            student_ids = raw_ids

        course_id = data.get("course")
        stream_id = data.get("stream")
        substream_id = data.get("substream")
        session = data.get("session")
        semyear = data.get("semyear")
        studypattern = data.get("studypattern")

        course = Course.objects.get(id=course_id)
        stream = Stream.objects.get(id=stream_id)
        substream = SubStream.objects.get(id=substream_id) if substream_id else None

        results = Result.objects.filter(
            student_id__in=student_ids,
            exam__semyear=str(semyear)  # cast to string to match field type
        ).select_related('exam__subject', 'student').order_by('student_id', 'exam_id')


        student_subject_map = {}
        student_name_map = {}
        all_exam_ids, all_examdetail_ids, all_student_ids = set(), set(), set()

        for r in results:
            sid = str(r.student_id)
            subject_name = r.exam.subject.name.strip() if r.exam and r.exam.subject else f"Exam_{r.exam_id}"
            student_name = r.student.name.strip() if r.student else f"Student_{sid}"
            student_subject_map.setdefault(sid, {}).setdefault(subject_name, []).append(r)
            student_name_map[sid] = student_name
            all_exam_ids.add(r.exam_id)
            all_examdetail_ids.add(r.examdetails_id)
            all_student_ids.add(r.student_id)

        students_without_data = []
        for sid in student_ids:
            if int(sid) not in all_student_ids:
                try:
                    student = Student.objects.get(id=sid)
                    students_without_data.append(student.name.strip())
                except Student.DoesNotExist:
                    students_without_data.append(f"Student_{sid}")

        questions = Questions.objects.filter(exam_id__in=all_exam_ids)
        questions_map = {}
        for q in questions:
            questions_map.setdefault(q.exam_id, []).append(q)

        exam_sessions = ExamSession.objects.filter(
            examdetails__in=all_examdetail_ids,
            student__in=all_student_ids
        )
        exam_time_map = {
            (es.examdetails_id, es.student_id): f"{int(es.time_left_ms / 60000)} mins"  # Convert ms to minutes
            for es in exam_sessions
        }

        submitted_answers = SubmittedExamination.objects.filter(
            student_id__in=all_student_ids,
            examdetails_id__in=all_examdetail_ids
        )

        submitted_answer_map = {
            (int(sa.question), sa.student_id, sa.examdetails_id): sa
            for sa in submitted_answers if sa.question.isdigit()
        }

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for sid, subjects in student_subject_map.items():
                student_name = student_name_map.get(sid, f"Student_{sid}")
                safe_name = student_name.replace(" ", "_").replace("/", "_")
                excel_buffer = io.BytesIO()

                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    for subject_name, result_list in subjects.items():
                        any_result = result_list[0]

                        exam_month = (
                            any_result.examdetails.examstartdate.strftime("%B %Y")
                            if any_result.examdetails and any_result.examdetails.examstartdate
                            else ""
                        )
                        time_key = (any_result.examdetails_id, any_result.student_id)
                        time_appeared = f"{exam_time_map[time_key]} mins" if time_key in exam_time_map else "Not Recorded"
                        duration = f"{any_result.exam.examduration} mins" if any_result.exam else ""

                        metadata = [
                            ['Student Name', student_name],
                            ['Course', course.name],
                            ['Stream', stream.name],
                        ]
                        if substream:
                            metadata.append(['Substream', substream.name])
                        metadata += [
                            ['Session', session],
                            ['Study Pattern', studypattern],
                            ['Semester/Year', any_result.exam.semyear or semyear],
                            ['Subject Name', subject_name],
                            ['Exam Month', exam_month],
                            ['Time Appeared', time_appeared],
                            ['Duration', duration]
                        ]
                        meta_df = pd.DataFrame(metadata, columns=["", ""])

                        exam_questions = questions_map.get(any_result.exam_id, [])
                        question_rows = []
                        for idx, q in enumerate(exam_questions, start=1):
                            key = (q.id, any_result.student_id, any_result.examdetails_id)
                            sa = submitted_answer_map.get(key)
                            question_rows.append({
                                "SR. NO.": idx,
                                "QUESTION": q.question,
                                "OPTION 1": q.option1,
                                "OPTION 2": q.option2,
                                "OPTION 3": q.option3,
                                "OPTION 4": q.option4,
                                "MARKED ANSWER": sa.submitted_answer if sa else "",
                                "CORRECT ANSWER": sa.answer if sa else "",
                                "OBTAINED MARKS": sa.marks_obtained if sa else "",
                                "MAX MARKS": sa.marks if sa else ""
                            })

                        data_df = pd.DataFrame(question_rows)
                        sheet_name = subject_name[:31]
                        meta_df.to_excel(writer, sheet_name=sheet_name, startrow=0, header=False, index=False)
                        data_df.to_excel(writer, sheet_name=sheet_name, startrow=len(metadata) + 2, index=False)

                        worksheet = writer.sheets[sheet_name]
                        workbook = writer.book
                        bold_border = workbook.add_format({'bold': True, 'border': 1})
                        border_only = workbook.add_format({'border': 1})
                        header_format = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1})
                        right_align_bold_border = workbook.add_format({'bold': True, 'border': 1, 'align': 'right'})
                        left_align_border = workbook.add_format({'border': 1, 'align': 'left'})

                        for i in range(len(metadata)):
                            worksheet.write(i, 0, metadata[i][0], bold_border)
                            worksheet.write(i, 1, metadata[i][1], border_only)

                        for col_num, value in enumerate(data_df.columns.values):
                            worksheet.write(len(metadata) + 2, col_num, value, header_format)

                        worksheet.set_column('A:A', 25)
                        worksheet.set_column('B:B', 80)
                        worksheet.set_column('C:G', 25)
                        worksheet.set_column('H:J', 18)

                        total_obtained = sum(
                            float(sa.marks_obtained)
                            for sa in submitted_answer_map.values()
                            if sa.student_id == any_result.student_id and
                               sa.examdetails_id == any_result.examdetails_id and
                               sa.question.isdigit() and
                               int(sa.question) in [q.id for q in exam_questions] and
                               sa.marks_obtained
                        )

                        total_max = sum(
                            float(sa.marks)
                            for sa in submitted_answer_map.values()
                            if sa.student_id == any_result.student_id and
                               sa.examdetails_id == any_result.examdetails_id and
                               sa.question.isdigit() and
                               int(sa.question) in [q.id for q in exam_questions] and
                               sa.marks
                        )

                        summary_row = len(metadata) + 2 + len(data_df) + 2
                        
                        try:
                            worksheet.merge_range(summary_row, 0, summary_row, 7, "MARKS OBTAINED", right_align_bold_border)
                        except Exception as merge_err:
                            logger.warning(f"Skipping merge range due to overlap: {merge_err}")
                            worksheet.write(summary_row, 7, "MARKS OBTAINED", right_align_bold_border)

                        worksheet.write(summary_row, 8, total_obtained, left_align_border)
                        worksheet.write(summary_row, 9, total_max, left_align_border)

                        
                        
                zip_file.writestr(f"{safe_name}.xlsx", excel_buffer.getvalue())

        if not student_subject_map:
            logger.warning("[EXPORT-ZIP] No data found for selected students.")
            return Response({'error': 'No data found for selected students'}, status=404)

        zip_buffer.seek(0)
        filename_parts = [course.name.replace(" ", "_"), stream.name.replace(" ", "_")]
        if substream:
            filename_parts.append(substream.name.replace(" ", "_"))
        filename = "_".join(filename_parts).lower() + ".zip"

        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        if students_without_data:
            response['X-Missing-Students'] = ', '.join(students_without_data[:10])
            response['X-Missing-Count'] = str(len(students_without_data))

        #logger.info(f"[EXPORT-ZIP] Successfully generated ZIP for {len(student_subject_map)} students")
        return response

    except Exception as e:
        logger.exception(f"[EXPORT-ZIP] Internal error: {str(e)}")
        return Response({'error': 'Internal Server Error'}, status=500)
      

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_team_info(request):
    """
    Direct reports = users whose `assigned_by` points to the logged-in user.
    We exclude self defensively (in case of bad data).
    Returns:
      { "has_subordinates": bool, "count": int }
    """
    qs = User.objects.filter(assigned_by=request.user).exclude(id=request.user.id)
    has_subordinates = qs.exists()
    print()
    return Response({
        "has_subordinates": has_subordinates,
        "count": qs.count(),
    })
    
#--- code added by ankit from 16-09-2025 ---

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def filter_students_all_register(request):
    try:
        qp = request.query_params
        university_id = qp.get("university")     or qp.get("university_id")
        course_id     = qp.get("course")         or qp.get("course_id")
        stream_id     = qp.get("stream")         or qp.get("Stream") or qp.get("stream_id")
        substream     = qp.get("substream")      or qp.get("substream_id")
        session_name  = qp.get("session")
        studypattern  = qp.get("studypattern")   or qp.get("study_pattern") or qp.get("course_pattern")
        semyear       = qp.get("sem_year")        or qp.get("current_semyear")

        # Apply substream only if it's a valid integer-like value
        apply_substream_filter = bool(substream and str(substream).strip().isdigit())


        # -------- Base queryset (Student) --------git 
        qs = (
            Student.objects
            .filter(archive=False,is_cancelled=False,is_pending=False,is_approve=True)
            .select_related("university", "user")
            .order_by("-id")
        )

        if university_id:
            qs = qs.filter(university_id=university_id)

        # -------- Reverse relation filters on Enrolled --------
        enrolled_filters = Q()
        if course_id:
            enrolled_filters &= Q(enrolled__course_id=course_id)
        if stream_id:
            enrolled_filters &= Q(enrolled__stream_id=stream_id)
        if session_name:
            enrolled_filters &= Q(enrolled__session=session_name)
        if studypattern:
            enrolled_filters &= Q(enrolled__course_pattern=studypattern)
        if semyear:
            enrolled_filters &= Q(enrolled__current_semyear=semyear)
        if apply_substream_filter:
            enrolled_filters &= Q(enrolled__substream_id=substream)

        if enrolled_filters:
            qs = qs.filter(enrolled_filters).distinct()

        # -------- Latest Enrolled per student (highest id) --------
        student_ids = list(qs.values_list("id", flat=True))

        enrolled_map = {}
        for e in (
            Enrolled.objects
            .filter(student_id__in=student_ids)
            .select_related("course", "stream", "substream")
            .order_by("student_id", "-id")
        ):
            if e.student_id not in enrolled_map:  # first seen due to ordering => latest
                enrolled_map[e.student_id] = e

        # -------- Build response payload (same fields) --------
        results = []
        for student in qs:
            enrolled = enrolled_map.get(student.id)

            if enrolled:
                current_semyear = enrolled.current_semyear
                entry_mode = enrolled.entry_mode or ""
                study_pattern_mode = enrolled.course_pattern or ""
                course_name = enrolled.course.name if enrolled.course else ""
                stream_name = enrolled.stream.name if enrolled.stream else ""
                substream_name = enrolled.substream.name if enrolled.substream else ""
                session_value = enrolled.session or ""
            else:
                current_semyear = ""
                entry_mode = ""
                study_pattern_mode = ""
                course_name = ""
                stream_name = ""
                substream_name = ""
                session_value = ""

            is_quick_register = "SR" if not student.is_quick_register else "QR"

            results.append({
                "id": student.id,
                "current_semyear": current_semyear,
                "enrollment_id": student.enrollment_id,
                "student_name": student.name,
                "university_name": student.university.university_name if student.university else "",
                "source": is_quick_register,
                "study_pattern_mode": study_pattern_mode,
                "entry_mode": entry_mode,
                "enrollment_date": student.enrollment_date.strftime("%Y-%m-%d") if student.enrollment_date else "",
                # extras
                "course": course_name,
                "stream": stream_name,
                "substream": substream_name,
                "session": session_value,
            })

        return Response(
            {"status": "success", "count": len(results), "data": results},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        logger.exception("Error in filter_students (GET): %s", str(e))
        return Response(
            {"status": "error", "message": "Something went wrong!"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def filter_students_quick_register(request):
    try:
        qp = request.query_params
        university_id = qp.get("university")     or qp.get("university_id")
        course_id     = qp.get("course")         or qp.get("course_id")
        stream_id     = qp.get("stream")         or qp.get("Stream") or qp.get("stream_id")
        substream     = qp.get("substream")      or qp.get("substream_id")
        session_name  = qp.get("session")
        studypattern  = qp.get("studypattern")   or qp.get("study_pattern") or qp.get("course_pattern")
        semyear       = qp.get("sem_year")        or qp.get("current_semyear")

        # Apply substream only if it's a valid integer-like value
        apply_substream_filter = bool(substream and str(substream).strip().isdigit())


        # -------- Base queryset (Student) --------git 
        qs = (
            Student.objects
            .filter(archive=False,is_cancelled=False,is_pending=False,is_approve=False,is_quick_register=True)
            .select_related("university", "user")
            .order_by("-id")
        )

        if university_id:
            qs = qs.filter(university_id=university_id)

        # -------- Reverse relation filters on Enrolled --------
        enrolled_filters = Q()
        if course_id:
            enrolled_filters &= Q(enrolled__course_id=course_id)
        if stream_id:
            enrolled_filters &= Q(enrolled__stream_id=stream_id)
        if session_name:
            enrolled_filters &= Q(enrolled__session=session_name)
        if studypattern:
            enrolled_filters &= Q(enrolled__course_pattern=studypattern)
        if semyear:
            enrolled_filters &= Q(enrolled__current_semyear=semyear)
        if apply_substream_filter:
            enrolled_filters &= Q(enrolled__substream_id=substream)

        if enrolled_filters:
            qs = qs.filter(enrolled_filters).distinct()

        # -------- Latest Enrolled per student (highest id) --------
        student_ids = list(qs.values_list("id", flat=True))

        enrolled_map = {}
        for e in (
            Enrolled.objects
            .filter(student_id__in=student_ids)
            .select_related("course", "stream", "substream")
            .order_by("student_id", "-id")
        ):
            if e.student_id not in enrolled_map:  # first seen due to ordering => latest
                enrolled_map[e.student_id] = e

        # -------- Build response payload (same fields) --------
        results = []
        for student in qs:
            enrolled = enrolled_map.get(student.id)

            if enrolled:
                current_semyear = enrolled.current_semyear
                entry_mode = enrolled.entry_mode or ""
                study_pattern_mode = enrolled.course_pattern or ""
                course_name = enrolled.course.name if enrolled.course else ""
                stream_name = enrolled.stream.name if enrolled.stream else ""
                substream_name = enrolled.substream.name if enrolled.substream else ""
                session_value = enrolled.session or ""
            else:
                current_semyear = ""
                entry_mode = ""
                study_pattern_mode = ""
                course_name = ""
                stream_name = ""
                substream_name = ""
                session_value = ""

            is_quick_register = "SR" if not student.is_quick_register else "QR"

            results.append({
                "id": student.id,
                "current_semyear": current_semyear,
                "enrollment_id": student.enrollment_id,
                "student_name": student.name,
                "university_name": student.university.university_name if student.university else "",
                "source": is_quick_register,
                "study_pattern_mode": study_pattern_mode,
                "entry_mode": entry_mode,
                "enrollment_date": student.enrollment_date.strftime("%Y-%m-%d") if student.enrollment_date else "",
                # extras
                "course": course_name,
                "stream": stream_name,
                "substream": substream_name,
                "session": session_value,
            })

        return Response(
            {"status": "success", "count": len(results), "data": results},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        logger.exception("Error in filter_students (GET): %s", str(e))
        return Response(
            {"status": "error", "message": "Something went wrong!"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def filter_students_register_student(request):
    try:
        qp = request.query_params
        university_id = qp.get("university")     or qp.get("university_id")
        course_id     = qp.get("course")         or qp.get("course_id")
        stream_id     = qp.get("stream")         or qp.get("Stream") or qp.get("stream_id")
        substream     = qp.get("substream")      or qp.get("substream_id")
        session_name  = qp.get("session")
        studypattern  = qp.get("studypattern")   or qp.get("study_pattern") or qp.get("course_pattern")
        semyear       = qp.get("sem_year")        or qp.get("current_semyear")

        # Apply substream only if it's a valid integer-like value
        apply_substream_filter = bool(substream and str(substream).strip().isdigit())


        # -------- Base queryset (Student) --------git 
        qs = (
            Student.objects
            .filter(archive=False,is_quick_register=False, is_cancelled=False,is_pending=False,is_approve=False)
            .select_related("university", "user")
            .order_by("-id")
        )

        if university_id:
            qs = qs.filter(university_id=university_id)

        # -------- Reverse relation filters on Enrolled --------
        enrolled_filters = Q()
        if course_id:
            enrolled_filters &= Q(enrolled__course_id=course_id)
        if stream_id:
            enrolled_filters &= Q(enrolled__stream_id=stream_id)
        if session_name:
            enrolled_filters &= Q(enrolled__session=session_name)
        if studypattern:
            enrolled_filters &= Q(enrolled__course_pattern=studypattern)
        if semyear:
            enrolled_filters &= Q(enrolled__current_semyear=semyear)
        if apply_substream_filter:
            enrolled_filters &= Q(enrolled__substream_id=substream)

        if enrolled_filters:
            qs = qs.filter(enrolled_filters).distinct()

        # -------- Latest Enrolled per student (highest id) --------
        student_ids = list(qs.values_list("id", flat=True))

        enrolled_map = {}
        for e in (
            Enrolled.objects
            .filter(student_id__in=student_ids)
            .select_related("course", "stream", "substream")
            .order_by("student_id", "-id")
        ):
            if e.student_id not in enrolled_map:  # first seen due to ordering => latest
                enrolled_map[e.student_id] = e

        # -------- Build response payload (same fields) --------
        results = []
        for student in qs:
            enrolled = enrolled_map.get(student.id)

            if enrolled:
                current_semyear = enrolled.current_semyear
                entry_mode = enrolled.entry_mode or ""
                study_pattern_mode = enrolled.course_pattern or ""
                course_name = enrolled.course.name if enrolled.course else ""
                stream_name = enrolled.stream.name if enrolled.stream else ""
                substream_name = enrolled.substream.name if enrolled.substream else ""
                session_value = enrolled.session or ""
            else:
                current_semyear = ""
                entry_mode = ""
                study_pattern_mode = ""
                course_name = ""
                stream_name = ""
                substream_name = ""
                session_value = ""

            is_quick_register = "SR" if not student.is_quick_register else "QR"

            results.append({
                "id": student.id,
                "current_semyear": current_semyear,
                "enrollment_id": student.enrollment_id,
                "student_name": student.name,
                "university_name": student.university.university_name if student.university else "",
                "source": is_quick_register,
                "study_pattern_mode": study_pattern_mode,
                "entry_mode": entry_mode,
                "enrollment_date": student.enrollment_date.strftime("%Y-%m-%d") if student.enrollment_date else "",
                # extras
                "course": course_name,
                "stream": stream_name,
                "substream": substream_name,
                "session": session_value,
            })

        return Response(
            {"status": "success", "count": len(results), "data": results},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        logger.exception("Error in filter_students (GET): %s", str(e))
        return Response(
            {"status": "error", "message": "Something went wrong!"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


############### Added By Avanti to fetch data for Student Form ###################

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_form(request, student_id):
    try:
        logger.info(
            "student_form requested",
            extra={"student_id": student_id, "user_id": getattr(request.user, "id", None)}
        )

        student = get_object_or_404(Student, id=student_id, archive=False)

        # Related objects
        enrolled = Enrolled.objects.filter(student=student).first()
        additional_details = AdditionalEnrollmentDetails.objects.filter(student=student).first()
        qualification = Qualification.objects.filter(student=student).first()

        # ---- Build the document name -> ID number map ----
        # Key: StudentDocuments.document
        # Value: StudentDocuments.document_ID_no
        # - Skips entries with missing document name or ID number
        # - If duplicate document names appear, value becomes a list of ID numbers
        docs_qs = StudentDocuments.objects.filter(student_id=student_id)

        document_id_map = {}
        duplicate_counts = 0

        for d in docs_qs:
            key = (d.document or "").strip()
            val = (d.document_ID_no or "").strip()

            if not key or not val:
                # skip incomplete rows but note it for observability
                logger.warning(
                    "Skipping incomplete StudentDocuments row",
                    extra={
                        "student_id": student_id,
                        "document": d.document,
                        "document_ID_no": d.document_ID_no,
                        "doc_pk": getattr(d, "pk", None),
                    },
                )
                continue

            if key in document_id_map:
                # turn into list on first duplicate
                if not isinstance(document_id_map[key], list):
                    document_id_map[key] = [document_id_map[key]]
                document_id_map[key].append(val)
                duplicate_counts += 1
            else:
                document_id_map[key] = val

        # ---- Main response payload ----
        data = {
            # ---- Student Personal Info ----
            "name_of_candidate": student.name,
            "father_name": student.father_name,
            "mother_name": student.mother_name,
            "date_of_birth": student.dateofbirth,
            "gender": student.gender,
            "category": student.category,
            "nationality": student.nationality,
            "contact_number": student.mobile,
            "email": student.email,
            "candidate_address": student.address,
            "district": student.city.name if student.city else "",
            "pincode": student.pincode,
            "state": student.state.name if student.state else "",
            "country": student.country.name if student.country else "",
            "university_name": student.university.university_name if student.university else "",

            # ---- Enrollment Info ----
            "admission_type": enrolled.entry_mode if enrolled else "",
            "year_semester": enrolled.current_semyear if enrolled else "",
            "session": enrolled.session if enrolled else "",
            "course": enrolled.course.name if enrolled and enrolled.course else "",
            "stream": enrolled.stream.name if enrolled and enrolled.stream else "",

            # ---- Counselor Info ----
            "counselor_name": additional_details.counselor_name if additional_details else "",

            # ---- Qualification Info ----
            "qualificationdetails": {
                "secondary_year": qualification.secondary_year if qualification else "",
                "sr_year": qualification.sr_year if qualification else "",
                "under_year": qualification.under_year if qualification else "",
                "post_year": qualification.post_year if qualification else "",
                "mphil_year": qualification.mphil_year if qualification else "",
                "secondary_board": qualification.secondary_board if qualification else "",
                "sr_board": qualification.sr_board if qualification else "",
                "under_board": qualification.under_board if qualification else "",
                "post_board": qualification.post_board if qualification else "",
                "mphil_board": qualification.mphil_board if qualification else "",
                "secondary_percentage": qualification.secondary_percentage if qualification else "",
                "sr_percentage": qualification.sr_percentage if qualification else "",
                "under_percentage": qualification.under_percentage if qualification else "",
                "post_percentage": qualification.post_percentage if qualification else "",
                "mphil_percentage": qualification.mphil_percentage if qualification else "",
            },

            # ---- Your requested map: document name -> document_ID_no ----
            # Example: { "Aadhaar": "XXXX-XXXX-XXXX", "PAN": "ABCDE1234F" }
            # If duplicates exist: { "Aadhaar": ["ID1", "ID2"] }
            "personal_document_ids": document_id_map,
        }

        logger.info(
            "student_form response ready",
            extra={
                "student_id": student_id,
                "documents_unique": len([k for k in document_id_map.keys()]),
                "duplicate_keys": duplicate_counts,
            },
        )

        return Response({"status": "success", "data": data}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(
            "student_form failed",
            exc_info=True,
            extra={"student_id": student_id}
        )
        return Response({"status": "error", "message": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.http import Http404
def _abs_url_or_none(request, file_field):
    """Return absolute URL if the FileField/ImageField has a file, else None."""
    try:
        if file_field and getattr(file_field, "url", None):
            return request.build_absolute_uri(file_field.url)
    except ValueError:
        # e.g. file has no name
        return None
    return None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_documents(request, student_id):
    logger.info(
        "Student documents requested",
        extra={"student_id": student_id, "user_id": getattr(request.user, "id", None)}
    )

    try:
        # 1) Fetch student (404 if not found or archived)
        student = get_object_or_404(Student, id=student_id, archive=False)

        # 2) Fetch first qualification (if any)
        qualification = Qualification.objects.filter(student=student).first()

        # 3) Build qualification documents (name + url)
        qualification_documents = []
        if qualification:
            q_fields = [
                ("Secondary", "secondary_document"),
                ("Sr. Secondary", "sr_document"),
                ("Undergraduate", "under_document"),
                ("Postgraduate", "post_document"),
                ("M.Phil", "mphil_document"),
                ("Others", "others_document"),
            ]
            for label, attr in q_fields:
                file_obj = getattr(qualification, attr, None)
                url = _abs_url_or_none(request, file_obj)
                if url:
                    qualification_documents.append(
                        {"name": label, "field": attr, "url": url}
                    )

        # 4) Personal documents (name + id_number + front/back urls)
        personal_qs = StudentDocuments.objects.filter(student_id=student_id)

        personal_documents = []
        for doc in personal_qs:
            front_url = _abs_url_or_none(request, getattr(doc, "document_image_front", None))
            back_url  = _abs_url_or_none(request, getattr(doc, "document_image_back", None))

            personal_documents.append(
                {
                    "name": doc.document,  # internal/type name (e.g., "aadhaar")
                    "display_name": doc.document_name,  # optional label shown to user
                    "id_number": doc.document_ID_no,
                    "front_url": front_url,
                    "back_url": back_url,
                }
            )

        payload = {
            "status": "success",
            "student_id": student_id,
            "documents": {
                "qualification_documents": qualification_documents,
                "personal_documents": personal_documents,
            },
        }

        return Response(payload, status=status.HTTP_200_OK)

    except Http404:
        logger.warning("Student not found or archived", extra={"student_id": student_id})
        return Response(
            {"status": "error", "message": "Student not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        logger.error(
            "Failed to fetch student documents",
            exc_info=True,
            extra={"student_id": student_id},
        )
        return Response(
            {"status": "error", "message": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['POST'])
def save_exam_details(request):
    """
    Body:
    {
      "examsdata": [
        {
          "examination_id": 1,
          "start_date": "2025-09-28",
          "end_date": "2025-09-29",
          "start_time": "10:00",
          "end_time": "13:00"
        }
      ],
      "studentdata": [
        {"id": 5}, {"id": 19}, {"id": 20}
      ]
    }
    """
    try:
        examdata = request.data.get("examsdata")
        studentdata = request.data.get("studentdata")

        if not examdata:
            return Response({'message': 'Exam data is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not studentdata:
            return Response({'message': 'Student data is required'}, status=status.HTTP_400_BAD_REQUEST)

        results = {"success": [], "failed": []}
        messages, errors = [], []

        for exam in examdata:
            exam_id    = exam.get("examination_id")
            start_date = exam.get("start_date")
            end_date   = exam.get("end_date")
            start_time = exam.get("start_time")
            end_time   = exam.get("end_time")

            if not all([exam_id, start_date, end_date, start_time, end_time]):
                msg = "Incomplete exam details provided."
                logger.warning(msg)
                errors.append(msg)
                continue

            # 1) Fetch Examination
            try:
                exam_instance = Examination.objects.get(id=exam_id)
            except Examination.DoesNotExist:
                msg = f"Invalid exam ID: {exam_id}"
                logger.error(msg)
                errors.append(msg)
                continue
            except Exception as e:
                msg = f"Failed to read exam ID {exam_id}: {str(e)}"
                logger.exception(msg)
                errors.append(msg)
                continue

            # 2) Upsert StudentAppearingExam for these timings
            try:
                existing_exam, _created = StudentAppearingExam.objects.get_or_create(
                    exam=exam_instance,
                    examstartdate=start_date,
                    examenddate=end_date,
                    examstarttime=start_time,
                    examendtime=end_time,
                    defaults={"student_id": []},
                )
            except Exception as e:
                msg = f"Failed to create/fetch exam schedule for exam {exam_id}: {str(e)}"
                logger.exception(msg)
                errors.append(msg)
                continue

            # 3) Merge new students into StudentAppearingExam.student_id
            try:
                current_students = list(existing_exam.student_id or [])
                requested_ids = [s.get('id') for s in studentdata if 'id' in s]
                new_student_ids = [sid for sid in requested_ids if sid not in current_students]

                if new_student_ids:
                    current_students.extend(new_student_ids)
                    # keep unique while preserving order
                    seen = set()
                    current_students = [x for x in current_students if not (x in seen or seen.add(x))]
                    existing_exam.student_id = current_students
                    existing_exam.save()
                else:
                    logger.info("No new students to add for exam %s", exam_id)
            except Exception as e:
                msg = f"Failed to update student list for exam {exam_id}: {str(e)}"
                logger.exception(msg)
                errors.append(msg)
                continue

            # 4) Notify each newly-added student
            for student_id in new_student_ids:
                try:
                    student_instance = Student.objects.get(id=student_id)
                except Student.DoesNotExist:
                    msg = f"Student with ID {student_id} not found."
                    logger.error(msg)
                    errors.append(msg)
                    continue
                except Exception as e:
                    msg = f"Error fetching student {student_id}: {str(e)}"
                    logger.exception(msg)
                    errors.append(msg)
                    continue

                login_url = f"{settings.DOMAIN_NAME}"

                # --- Email (async) ---
                try:
                    subject = "Examination Details"
                    email_message = (
                        f"Dear {student_instance.name},\n\n"
                        f"You are invited to take the {getattr(exam_instance.subject, 'name', '')} "
                        f"{getattr(exam_instance, 'studypattern', '')} {getattr(exam_instance, 'semyear', '')} Test.\n"
                        f"Exam Link: {login_url}\n"
                        f"User ID: {student_instance.email}\n"
                        f"Password: {student_instance.mobile}\n\n"
                        f"The exam is available from {start_date} to {end_date} between "
                        f"{start_time} and {end_time}.\n"
                    )
                    Thread(
                        target=send_exam_email,
                        args=(subject, email_message, [student_instance.email])
                    ).start()
                except Exception as e:
                    logger.exception("Email error for student %s", student_id)
                    errors.append(f"Email error for student {student_id}: {str(e)}")

                # --- WhatsApp via AiSensy (“Exam Details” needs 5 params) ---
                try:
                    params = build_exam_details_params(
                        student_name=student_instance.name,
                        subject_name=getattr(exam_instance.subject, "name", ""),
                        studypattern=getattr(exam_instance, "studypattern", ""),
                        semyear=getattr(exam_instance, "semyear", ""),
                        portal_url=login_url,
                        email=student_instance.email,
                        mobile=student_instance.mobile,
                        start_date=start_date,
                        end_date=end_date,
                        start_time=start_time,
                        end_time=end_time,
                    )

                    ai_resp = send_aisensy_message(
                        phone=student_instance.mobile,
                        template_params=params,
                        campaign_key="EXAM_DETAILS",
                        source="save_exam_details",
                    )

                    # Pull typical id/status; also send the entire provider response back
                    st = ai_resp.get("_extracted_status") or ai_resp.get("status")
                    mid = ai_resp.get("_extracted_messageId")
                    dest = ai_resp.get("_normalized_destination")

                    logger.info("[AiSensy OK] dest=%s status=%s id=%s", dest, st, mid)
                    print(f"[AiSensy OK] dest={dest} status={st} id={mid} resp={ai_resp}")  # console fallback

                    messages.append(
                        f"Exam details sent to {student_instance.name} ({student_instance.id}). "
                        f"dest={dest} status={st or 'n/a'} id={mid or 'n/a'}"
                    )
                    results["success"].append({
                        "student_id": student_instance.id,
                        "name": student_instance.name,
                        "destination": dest,
                        "status": st,
                        "message_id": mid,
                        "campaign": ai_resp.get("_campaign_name"),
                        "provider_response": ai_resp,  # full raw response for debugging
                    })

                except AiSensyError as e:
                    logger.error("[AiSensy FAIL] student=%s error=%s", student_instance.id, e)
                    print(f"[AiSensy FAIL] student={student_instance.id} error={e}")  # console fallback
                    errors.append(f"AiSensy failed for student {student_instance.id}: {str(e)}")
                    results["failed"].append({
                        "student_id": student_instance.id,
                        "name": student_instance.name,
                        "error": str(e),
                    })
                except Exception as e:
                    logger.exception("[AiSensy EXCEPTION] student=%s", student_instance.id)
                    print(f"[AiSensy EXCEPTION] student={student_instance.id} error={e}")  # console fallback
                    errors.append(f"WhatsApp send error for student {student_instance.id}: {str(e)}")
                    results["failed"].append({
                        "student_id": student_instance.id,
                        "name": student_instance.name,
                        "error": str(e),
                    })

        return Response({
            "status": "ok",
            "results": results,
            "messages": messages,
            "errors": errors,
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception("save_exam_details fatal error")
        print(f"[save_exam_details FATAL] {e}")  # console fallback
        return Response(
            {"status": "error", "message": "Unexpected error.", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_student_by_name_email_mob_enroll_id(request):
    """
    Search students by single query param ?q= matching:
      - name (icontains)
      - enrollment_id (iexact)
      - email (iexact)
      - mobile (iexact)

    Response fields per student:
      name, email, mobile, enrollment_id,
      course_pattern, total_semyear, current_semyear,
      course, stream, substream  (from latest Enrolled)
    """
    q = (request.query_params.get("q") or "").strip()

    if not q:
        return Response(
            {"detail": "Please provide query parameter ?q=<name/email/mobile/enrollment_id>."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        filters = (
            Q(name__icontains=q) |
            Q(enrollment_id__iexact=q) |
            Q(email__iexact=q) |
            Q(mobile__iexact=q)
        )

        # No select_related to 'academic'—it doesn't exist.
        students = Student.objects.filter(
            filters, archive=False, is_cancelled=False
        )

        results = []
        for s in students:
            # Grab the most recent enrollment for this student
            enr = (
                Enrolled.objects
                .filter(student=s)
                .select_related("course", "stream", "substream")
                .order_by("-id")
                .first()
            )

            course_pattern  = getattr(enr, "course_pattern", "") or ""
            total_semyear   = getattr(enr, "total_semyear", "") or ""
            current_semyear = getattr(enr, "current_semyear", "") or ""
            course_name     = getattr(getattr(enr, "course", None), "name", "") or ""
            stream_name     = getattr(getattr(enr, "stream", None), "name", "") or ""
            substream_name  = getattr(getattr(enr, "substream", None), "name", "") or ""

            results.append({
                "id"  :            s.id or "",
                "name":            s.name or "",
                "email":           s.email or "",
                "mobile":          s.mobile or "",
                "enrollment_id":   s.enrollment_id or "",
                "course_pattern":  course_pattern,
                "total_semyear":   str(total_semyear) if total_semyear != "" else "",
                "current_semyear": str(current_semyear) if current_semyear != "" else "",
                "course":          course_name,
                "stream":          stream_name,
                "substream":       substream_name,
            })

        payload = {"results": results, "count": len(results)}
        return Response(payload, status=status.HTTP_200_OK)

    except Exception:
        logger.exception("Unhandled error during student search. q=%r", q)
        return Response({"error": "An unexpected error occurred."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(["GET"])
@permission_classes([IsAuthenticated])  # remove this line if public API
def list_courses(request):
    """
    GET /api/courses/?university_id=<ID>
    Returns courses for a given university_id.
    """
    university_id = request.query_params.get("university_id", "").strip()


    if not university_id.isdigit():
        return Response(
            {"detail": "Please provide a valid ?university_id=<integer>."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    qs = (
        Course.objects
        .filter(university_id=int(university_id))
        .select_related("university")
        .order_by("name")
    )

    data = [
        {
            "id": c.id,
            "name": c.name,
            "year": c.year,
            "university_id": c.university_id,
            "university_name": getattr(c.university, "university_name", ""),
        }
        for c in qs
    ]

    resp = {"results": data, "count": len(data)}
    logger.info("Courses response for university_id=%s: count=%d", university_id, len(data))
    return Response(resp, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])  # remove this line if public API
def list_streams_by_course(request):
    """
    GET /api/streams/?course_id=<ID>
    Returns streams for a given course_id.
    """
    course_id = request.query_params.get("course_id", "").strip()

    if not course_id.isdigit():
        return Response(
            {"detail": "Please provide a valid ?course_id=<integer>."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    qs = (
        Stream.objects
        .filter(course_id=int(course_id))
        .select_related("course")
        .order_by("name")
    )

    data = [
        {
            "id": s.id,
            "name": s.name,
            "sem": s.sem,
            "year": s.year,
            "course_id": s.course_id,
            "course_name": getattr(s.course, "name", ""),
        }
        for s in qs
    ]

    resp = {"results": data, "count": len(data)}
    return Response(resp, status=status.HTTP_200_OK)
  
@api_view(["GET"])
@permission_classes([IsAuthenticated])  # remove if public
def students_by_course_stream(request):
    """
    GET /api/students/by-course-stream/?course=<course_id>&stream=<stream_id>

    Returns students enrolled in the given course + stream.
    For each student, uses the LATEST Enrolled row (by id DESC) to produce:
      {
        "id": <student_id>,
        "name": "...",
        "email": "...",
        "mobile": "...",
        "enrollment_id": "...",
        "course_pattern": "...",
        "total_semyear": "...",
        "current_semyear": "...",
        "course": "...",
        "stream": "...",
        "substream": "..."
      }
    """
    params = dict(request.query_params)

    course_id = (request.query_params.get("course") or "").strip()
    stream_id = (request.query_params.get("stream") or "").strip()

    # Basic validation
    if not course_id or not stream_id:
        return Response(
            {"detail": "Please provide both ?course=<id> and ?stream=<id>."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not course_id.isdigit() or not stream_id.isdigit():
        return Response(
            {"detail": "Parameters ?course and ?stream must be integers."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Pull all enrollments for this course+stream, newest first
        enrollments = (
            Enrolled.objects
            .filter(
                course_id=int(course_id),
                stream_id=int(stream_id),
                student__archive=False,
                student__is_cancelled=False,
            )
            .select_related("student", "course", "stream", "substream")
            .order_by("-id")
        )

        # Keep the latest enrollment per student
        seen_student_ids = set()
        results = []
        for enr in enrollments:
            sid = enr.student_id
            if sid in seen_student_ids:
                continue
            seen_student_ids.add(sid)

            s = enr.student  # the Student row

            results.append({
                "id":              s.id or "",
                "name":            s.name or "",
                "email":           s.email or "",
                "mobile":          s.mobile or "",
                "enrollment_id":   s.enrollment_id or "",
                "course_pattern":  enr.course_pattern or "",
                "total_semyear":   str(enr.total_semyear) if enr.total_semyear else "",
                "current_semyear": str(enr.current_semyear) if enr.current_semyear else "",
                "course":          getattr(enr.course, "name", "") or "",
                "stream":          getattr(enr.stream, "name", "") or "",
                "substream":       getattr(getattr(enr, "substream", None), "name", "") or "",
            })

        payload = {"results": results, "count": len(results)}
        return Response(payload, status=status.HTTP_200_OK)

    except Exception:
        logger.exception(
            "Unhandled error in students_by_course_stream. course=%r stream=%r",
            course_id, stream_id
        )
        return Response({"error": "An unexpected error occurred."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["GET"])
def get_student_fees(request, student_id):
    """
    Return all PaymentReciept records for the given student (by Student.pk).
    """
    try:
        receipts = (
            PaymentReciept.objects
            .filter(student_id=student_id)
            .order_by("id")
        )

        if not receipts.exists():
            # logger.warning(f"No receipts found for student_id={student_id}")
            return Response(
                {"error": "No fees/receipts found for this student"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PaymentRecieptSerializer(receipts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Error fetching receipts for student_id={student_id}: {e}")
        return Response(
            {"error": "Something went wrong while fetching receipts"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
#11-11-2025 commented by ankit
# @api_view(["PUT", "PATCH"])
# def update_student_fees_by_sem(request, student_id: int):
#     data = request.data

#     txid = data.get("transactionID")
#     if not txid:
#         return Response(
#             {"error": "transactionID is required to update a payment receipt."},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     # find the receipt for this student
#     receipt = PaymentReciept.objects.filter(student_id=student_id, transactionID=txid).first()
#     if not receipt:
#         return Response(
#             {"error": f"No PaymentReciept found for student_id={student_id} and transactionID={txid}"},
#             status=status.HTTP_404_NOT_FOUND,
#         )

#     try:
#         with transaction.atomic():
#             # Optional: map client alias -> model field
#             if "payment_method" in data and "paymentmode" not in data:
#                 data = dict(data)  # make a shallow copy so we can mutate safely
#                 data["paymentmode"] = data.pop("payment_method")

#             # Make sure we don't accidentally change protected fields even if they were sent
#             for blocked in ("transactionID", "id", "student", "student_id", "transactiontime"):
#                 if blocked in data:
#                     data = dict(data)
#                     data.pop(blocked, None)

#             # Get the paid amount from request data for recalculation
#             new_paid_amount = data.get("paidamount")
#             if new_paid_amount:
#                 try:
#                     new_paid_amount = float(new_paid_amount)
#                 except (ValueError, TypeError):
#                     return Response(
#                         {"error": "Invalid paidamount format."},
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#             # Update the specific receipt first
#             serializer = PaymentRecieptSerializersave(receipt, data=data, partial=True)
#             if not serializer.is_valid():
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#             updated_receipt = serializer.save()

#             # Get total fees for this semester (use the updated receipt's semyearfees or get from first receipt)
#             total_fees_val = 0.0
#             if updated_receipt.semyearfees:
#                 try:
#                     total_fees_val = float(updated_receipt.semyearfees)
#                 except (ValueError, TypeError):
#                     pass

#             # If no total fees in updated receipt, get from first receipt for this student and semester
#             if total_fees_val == 0:
#                 first_receipt = PaymentReciept.objects.filter(
#                     student_id=student_id, 
#                     semyear=updated_receipt.semyear
#                 ).order_by('id').first()
#                 if first_receipt and first_receipt.semyearfees:
#                     try:
#                         total_fees_val = float(first_receipt.semyearfees)
#                     except (ValueError, TypeError):
#                         pass

#             # ---- Check for advance amount from previous semesters ----
#             previous_advance_amount = 0.0
#             previous_semesters_receipts = PaymentReciept.objects.filter(
#                 student_id=student_id
#             ).exclude(semyear=updated_receipt.semyear).order_by('semyear', 'id')
            
#             # Find advance amount from all previous semesters
#             for prev_receipt in previous_semesters_receipts:
#                 try:
#                     advance_amt = float(prev_receipt.advanceamount or 0)
#                     if advance_amt > 0:
#                         previous_advance_amount += advance_amt
#                 except (ValueError, TypeError):
#                     continue

#             # Get ALL payment receipts for this student in the same semester, ordered chronologically
#             all_receipts = list(PaymentReciept.objects.filter(
#                 student_id=student_id, 
#                 semyear=updated_receipt.semyear
#             ).order_by('id'))

#             # Recalculate cumulative amounts for ALL receipts in chronological order
#             cumulative_paid = 0.0
            
#             for receipt_item in all_receipts:
#                 try:
#                     current_paid = float(receipt_item.paidamount or 0)
#                     cumulative_paid += current_paid
                    
#                     # Calculate effective total payment (current semester cumulative + previous advance)
#                     effective_total_payment = cumulative_paid + previous_advance_amount
                    
#                     # Calculate pending and advance amounts CORRECTLY
#                     pending = max(0.0, total_fees_val - effective_total_payment)
#                     advance = max(0.0, effective_total_payment - total_fees_val)
                    
#                     # Determine payment type
#                     if pending == 0 and advance == 0:
#                         payment_type = "Full Payment"
#                     elif advance > 0:
#                         payment_type = "Advance Payment"
#                     else:
#                         payment_type = "Part Payment"
                    
#                     # Update the receipt with calculated amounts
#                     receipt_item.pendingamount = str(pending)
#                     receipt_item.advanceamount = str(advance)
#                     receipt_item.payment_type = payment_type
                    
#                     # Only update semyearfees if it's empty or zero
#                     if not receipt_item.semyearfees or float(receipt_item.semyearfees or 0) == 0:
#                         receipt_item.semyearfees = str(total_fees_val)
                    
#                     # Update remarks to include previous advance info if not already present
#                     current_remarks = receipt_item.remarks or ""
#                     if previous_advance_amount > 0 and "previous advance" not in current_remarks.lower():
#                         receipt_item.remarks = f"{current_remarks} | Previous advance applied: {previous_advance_amount}".strip()
                    
#                     receipt_item.save()
                            
#                 except Exception as ex:
#                     # Log error but continue with other receipts
#                     print(f"Error calculating amounts for receipt {receipt_item.id}: {str(ex)}")
#                     continue

#             # Return the updated receipt along with success message
#             response_data = PaymentRecieptSerializersave(updated_receipt).data
#             response_data["previous_advance_applied"] = previous_advance_amount
#             response_data["calculation_note"] = f"Total Fees: {total_fees_val}, Cumulative Paid: {cumulative_paid}, Previous Advance: {previous_advance_amount}, Effective Payment: {cumulative_paid + previous_advance_amount}, Pending: {pending}, Advance: {advance}"

#             return Response({
#                 "message": f"Payment receipt updated successfully. Previous advance of {previous_advance_amount} considered in calculation.",
#                 "receipt": response_data
#             }, status=status.HTTP_200_OK)

#     except Exception as e:
#         return Response(
#             {"error": f"An error occurred during update: {str(e)}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )

from collections import OrderedDict
@api_view(["PUT", "PATCH"])
def update_student_fees_by_sem(request, student_id: int):
    data = request.data

    txid = data.get("transactionID")
    if not txid:
        return Response(
            {"error": "transactionID is required to update a payment receipt."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # find the receipt for this student
    receipt = PaymentReciept.objects.filter(
        student_id=student_id,
        transactionID=txid
    ).first()

    if not receipt:
        return Response(
            {
                "error": (
                    f"No PaymentReciept found for "
                    f"student_id={student_id} and transactionID={txid}"
                )
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        with transaction.atomic():

            # Optional: map client alias -> model field
            if "payment_method" in data and "paymentmode" not in data:
                data = dict(data)  # make a shallow copy so we can mutate safely
                data["paymentmode"] = data.pop("payment_method")

            # Make sure we don't accidentally change protected fields even if they were sent
            for blocked in ("transactionID", "id", "student", "student_id", "transactiontime"):
                if blocked in data:
                    data = dict(data)
                    data.pop(blocked, None)

            # Update ONLY this receipt first
            serializer = PaymentRecieptSerializersave(receipt, data=data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            updated_receipt = serializer.save()

            # ----------------------------------------------------------------------------------
            # 1) GET ALL RECEIPTS OF THIS STUDENT (ALL SEMESTERS)
            # ----------------------------------------------------------------------------------
            all_receipts = list(
                PaymentReciept.objects.filter(student_id=student_id)
                .order_by("semyear", "id")  # adjust ordering if needed
            )

            if not all_receipts:
                return Response(
                    {"error": "No receipts found for this student after update."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # ----------------------------------------------------------------------------------
            # 2) GROUP BY SEMYEAR
            # ----------------------------------------------------------------------------------
            sem_groups = OrderedDict()
            for r in all_receipts:
                sem_key = r.semyear or ""  # handle NULL semyear
                sem_groups.setdefault(sem_key, []).append(r)

            # ----------------------------------------------------------------------------------
            # 3) DETERMINE TOTAL FEES PER SEM
            #    (take first non-zero semyearfees we find for that sem)
            # ----------------------------------------------------------------------------------
            def safe_float(val, default=0.0):
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return default

            sem_totals = {}
            for sem_key, recs in sem_groups.items():
                total_for_sem = 0.0
                for r in recs:
                    fees = safe_float(r.semyearfees, 0.0)
                    if fees > 0:
                        total_for_sem = fees
                        break
                sem_totals[sem_key] = total_for_sem

            # ----------------------------------------------------------------------------------
            # 4) RECALCULATE ALL RECEIPTS IN ORDER, CARRYING ADVANCE TO NEXT SEM
            # ----------------------------------------------------------------------------------
            carry_forward_advance = 0.0  # advance that moves from sem N to sem N+1
            sem_previous_advance_map = {}  # to report for specific sem if needed

            for sem_key, recs in sem_groups.items():
                total_fees_val = sem_totals.get(sem_key, 0.0)
                sem_previous_advance = carry_forward_advance
                sem_previous_advance_map[sem_key] = sem_previous_advance

                sem_cumulative_paid = 0.0

                for r in recs:
                    paid = safe_float(r.paidamount, 0.0)
                    sem_cumulative_paid += paid

                    # Effective payment includes previous advance + paid of this sem so far
                    effective_total_payment = sem_previous_advance + sem_cumulative_paid

                    pending = max(0.0, total_fees_val - effective_total_payment)
                    advance = max(0.0, effective_total_payment - total_fees_val)

                    # Decide payment_type
                    if total_fees_val == 0 and effective_total_payment == 0:
                        payment_type = "No Payment"
                    elif pending == 0 and advance == 0:
                        payment_type = "Full Payment"
                    elif advance > 0:
                        payment_type = "Advance Payment"
                    else:
                        payment_type = "Part Payment"

                    # Set calculated fields
                    r.pendingamount = str(pending)
                    r.advanceamount = str(advance)
                    r.payment_type = payment_type

                    # Ensure semyearfees is filled if empty/zero
                    if total_fees_val > 0:
                        if not r.semyearfees or safe_float(r.semyearfees) == 0.0:
                            r.semyearfees = str(total_fees_val)

                    # Add remark about previous advance (only once per sem per receipt)
                    current_remarks = (r.remarks or "").strip()
                    if sem_previous_advance > 0 and "previous advance applied" not in current_remarks.lower():
                        extra = f"Previous advance applied: {sem_previous_advance}"
                        r.remarks = f"{current_remarks} | {extra}".strip(" |")
                    r.save()

                # After finishing one sem, whatever advance remains on the LAST receipt
                # is the carry_forward_advance for the next sem.
                carry_forward_advance = advance  # from last receipt in this sem

            # ----------------------------------------------------------------------------------
            # 5) PREPARE RESPONSE (UPDATED RECEIPT AFTER RECALC)
            # ----------------------------------------------------------------------------------
            final_updated_receipt = PaymentReciept.objects.get(pk=updated_receipt.pk)
            sem_key_of_updated = final_updated_receipt.semyear or ""
            previous_advance_applied = sem_previous_advance_map.get(sem_key_of_updated, 0.0)

            response_data = PaymentRecieptSerializersave(final_updated_receipt).data

            # Some debug / info fields (optional)
            response_data["previous_advance_applied"] = previous_advance_applied
            response_data["carry_forward_after_all_semesters"] = carry_forward_advance

            return Response(
                {
                    "message": (
                        "Payment receipt updated successfully and all receipts for "
                        "this student have been recalculated across semesters."
                    ),
                    "receipt": response_data,
                },
                status=status.HTTP_200_OK,
            )

    except Exception as e:
        return Response(
            {"error": f"An error occurred during update: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

from collections import defaultdict
@api_view(["GET"])
def payment_receipt(request, student_id):
    """
    GET /api/get-payment-receipt/<student_id>/?semyear=1

    Response:
    {
      "status": true,
      "student": { student_name, email, mobile, course_name },
      "semesters": {
        "semester 1": {
          "fees": { ...all StudentFees fields... },
          "payments": [ { ...PaymentReciept fields... }, ... ]
        },
        ...
      }
    }

    - Only semesters that have at least one PaymentReciept are included.
    - If ?semyear=<n> is provided, only that semester is included.
    """
    try:
        # ---- student
        student = get_object_or_404(Student, id=student_id)

        # ---- course_name (try from Enrolled, else from StudentFees.stream)
        course_name = None
        enr = Enrolled.objects.select_related("stream").filter(student=student).order_by("-id").first()
        if enr and enr.stream:
            course_name = enr.stream.name
        if not course_name:
            fee_any = StudentFees.objects.select_related("stream").filter(student=student).first()
            if fee_any and getattr(fee_any, "stream", None):
                course_name = fee_any.stream.name

        # ---- optional filter by semyear
        semyear_param = (request.query_params.get("semyear") or "").strip()
        payments_qs = PaymentReciept.objects.filter(student=student).order_by("-transactiontime")
        if semyear_param:
            payments_qs = payments_qs.filter(
                Q(semyear=str(semyear_param)) | Q(semyearfees=str(semyear_param))
            )

        # ---- group payments by semyear
        semesters = {}
        payments_by_sem = defaultdict(list)
        for p in payments_qs:
            sem_key_raw = (p.semyear or p.semyearfees or "").strip()
            if not sem_key_raw:
                continue
            payments_by_sem[sem_key_raw].append(p)

        for sem_num, plist in payments_by_sem.items():
            # get StudentFees for this semester
            fee = StudentFees.objects.filter(student=student, sem=str(sem_num)).order_by("-id").first()
            fee_breakup = {}
            if fee:
                fee_breakup = {
                    "studypattern": fee.studypattern,
                    "tutionfees": fee.tutionfees,
                    "examinationfees": fee.examinationfees,
                    "bookfees": fee.bookfees,
                    "resittingfees": fee.resittingfees,
                    "entrancefees": fee.entrancefees,
                    "extrafees": fee.extrafees,
                    "discount": fee.discount,
                    "totalfees": fee.totalfees,
                    "sem": fee.sem,
                    "stream": fee.stream.name if fee.stream else None,
                    "substream": fee.substream.name if fee.substream else None,
                }

            semesters[f"semester {sem_num}"] = {
                "fees": fee_breakup,
                "payments": [
                    {
                        "payment_method": p.paymentmode,
                        "session": p.session,
                        "transactionID": p.transactionID,
                        "transactiontime": p.transactiontime.isoformat() if p.transactiontime else None,
                        "status": p.status,
                        "paidamount": p.paidamount,
                        "pendingamount": p.pendingamount,
                        "advanceamount": p.advanceamount,
                        "payment_for": p.payment_for,
                        "payment_categories": p.payment_categories,
                        "payment_type": p.payment_type,
                        "fee_reciept_type": p.fee_reciept_type,
                        "transaction_date": p.transaction_date,
                        "cheque_no": p.cheque_no,
                        "bank_name": p.bank_name,
                        "semyear": p.semyear,
                        "semyearfees": p.semyearfees,
                        "remarks": p.remarks,
                        "uncleared_amount": p.uncleared_amount,
                        "created_by": p.created_by,
                        "modified_by": p.modified_by,
                    }
                    for p in plist
                ],
            }

        return Response({
            "status": True,
            "student": {
                "student_name": student.name,
                "email": student.email,
                "mobile": student.mobile,
                "course_name": course_name,
            },
            "semesters": semesters
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"status": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_payment_receipt(request):
    """
    Create PaymentReciept.
    Mandatory: student_id, semyear
    Auto-generate transactionID with prefix 'TXT445FE' + sequence.
    """
    ser = PaymentReceiptCreateSerializer(data=request.data)
    try:
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        # ---- Validate Student ----
        try:
            student = Student.objects.get(pk=data["student_id"])
        except Student.DoesNotExist:
            logger.error("Student not found | student_id=%s | user=%s",
                         data["student_id"], getattr(request.user, "email", str(request.user)))
            return Response({"errors": {"student_id": ["Invalid student id."]}},
                            status=status.HTTP_400_BAD_REQUEST)

        # ---- Generate transactionID ----
        prefix = "TXT445FE"
        latest_receipt = PaymentReciept.objects.order_by("-id").first()
        last_id = int(latest_receipt.transactionID.replace(prefix, "")) if (latest_receipt and latest_receipt.transactionID.startswith(prefix)) else 100
        transaction_id = f"{prefix}{last_id + 1}"

        # ---- Get semyear from request data ----
        semyear = data.get("semyear", "")
        if not semyear:
            return Response({"errors": {"semyear": ["Semester year is required."]}},
                            status=status.HTTP_400_BAD_REQUEST)

        # ---- Get total fees for the semester ----
        total_fees_val = 0.0
        semyearfees_from_request = data.get("semyearfees", "")
        
        if semyearfees_from_request:
            try:
                total_fees_val = float(semyearfees_from_request)
            except (ValueError, TypeError):
                # If provided semyearfees is invalid, try to get from existing receipts
                pass
        
        # If no valid total fees from request, check existing receipts for this student and semester
        if total_fees_val == 0:
            existing_receipt = PaymentReciept.objects.filter(
                student_id=data["student_id"], 
                semyear=semyear
            ).order_by('id').first()
            if existing_receipt and existing_receipt.semyearfees:
                try:
                    total_fees_val = float(existing_receipt.semyearfees)
                except (ValueError, TypeError):
                    pass

        # If still no total fees, use the one from request (even if 0)
        if total_fees_val == 0 and semyearfees_from_request:
            try:
                total_fees_val = float(semyearfees_from_request)
            except (ValueError, TypeError):
                total_fees_val = 0.0

        # ---- Check for advance amount from previous semesters ----
        previous_advance_amount = 0.0
        previous_semesters_receipts = PaymentReciept.objects.filter(
            student_id=data["student_id"]
        ).exclude(semyear=semyear).order_by('semyear', 'id')
        
        # Find advance amount from all previous semesters
        for receipt in previous_semesters_receipts:
            try:
                advance_amt = float(receipt.advanceamount or 0)
                if advance_amt > 0:
                    previous_advance_amount += advance_amt
            except (ValueError, TypeError):
                continue

        # ---- Calculate cumulative amounts for ALL receipts in the current semester ----
        all_receipts = list(PaymentReciept.objects.filter(
            student_id=data["student_id"], 
            semyear=semyear
        ).order_by('id'))

        # Calculate current cumulative paid amount (before adding new receipt)
        cumulative_paid_before = 0.0
        for receipt in all_receipts:
            try:
                cumulative_paid_before += float(receipt.paidamount or 0)
            except (ValueError, TypeError):
                continue

        # Get new paid amount from request
        new_paid_amount = data.get("paidamount", 0)
        try:
            new_paid_amount_float = float(new_paid_amount or 0)
        except (ValueError, TypeError):
            new_paid_amount_float = 0.0

        # Calculate new cumulative paid amount (after adding new receipt)
        cumulative_paid_after = cumulative_paid_before + new_paid_amount_float

        # Calculate effective total payment (current semester cumulative + previous advance)
        effective_total_payment = cumulative_paid_after + previous_advance_amount

        # Calculate pending and advance amounts CORRECTLY
        # Pending amount should be based on total fees minus effective payment
        pending = max(0.0, total_fees_val - effective_total_payment)
        
        # Advance amount should be the EXTRA amount paid beyond total fees
        # This is the amount that exceeds total fees after considering previous advance
        advance = max(0.0, effective_total_payment - total_fees_val)
        
        # Determine payment type for the NEW receipt
        if pending == 0 and advance == 0:
            payment_type = "Full Payment"
        elif advance > 0:
            payment_type = "Advance Payment"
        else:
            payment_type = "Part Payment"

        # ---- Create Receipt ----
        obj = PaymentReciept.objects.create(
            student=student,
            payment_for=data.get("payment_for", "Course Fees"),
            payment_categories="New",
            payment_type=payment_type,
            fee_reciept_type=data.get("fee_reciept_type", ""),
            transaction_date=data.get("transaction_date", ""),
            cheque_no=data.get("cheque_no", ""),
            bank_name=data.get("bank_name", ""),
            semyearfees=str(total_fees_val),
            paidamount=data.get("paidamount", ""),
            pendingamount=str(pending),  # Calculated pending amount considering previous advance
            advanceamount=str(advance),  # Properly calculated advance amount
            transactionID=transaction_id,
            paymentmode=data.get("paymentmode", "Online") or "Online",
            remarks=f"{data.get('remarks', '')} | Previous advance applied: {previous_advance_amount}".strip(),
            session=data.get("session", ""),
            semyear=semyear,
            uncleared_amount=data.get("uncleared_amount", ""),
            status=data.get("status", "Realised"),
            created_by=getattr(request.user, "email", str(request.user)),
            modified_by=getattr(request.user, "email", str(request.user)),
        )

        # ---- Recalculate ALL receipts in the current semester to update their amounts ----
        try:
            with transaction.atomic():
                # Get ALL payment receipts for this student in the same semester (including the new one)
                all_receipts_updated = list(PaymentReciept.objects.filter(
                    student_id=data["student_id"], 
                    semyear=semyear
                ).order_by('id'))

                cumulative_paid = 0.0
                
                for receipt_item in all_receipts_updated:
                    try:
                        current_paid = float(receipt_item.paidamount or 0)
                        cumulative_paid += current_paid
                        
                        # Calculate effective total payment for recalculation
                        effective_total_recalc = cumulative_paid + previous_advance_amount
                        
                        # Calculate pending and advance amounts correctly
                        pending_recalc = max(0.0, total_fees_val - effective_total_recalc)
                        advance_recalc = max(0.0, effective_total_recalc - total_fees_val)
                        
                        # Determine payment type for each receipt
                        if pending_recalc == 0 and advance_recalc == 0:
                            payment_type_recalc = "Full Payment"
                        elif advance_recalc > 0:
                            payment_type_recalc = "Advance Payment"
                        else:
                            payment_type_recalc = "Part Payment"
                        
                        # Update the receipt with calculated amounts
                        receipt_item.pendingamount = str(pending_recalc)
                        receipt_item.advanceamount = str(advance_recalc)
                        receipt_item.payment_type = payment_type_recalc
                        
                        # Only update semyearfees if it's empty or zero
                        if not receipt_item.semyearfees or float(receipt_item.semyearfees or 0) == 0:
                            receipt_item.semyearfees = str(total_fees_val)
                        
                        receipt_item.save()
                                
                    except Exception as ex:
                        # Log error but continue with other receipts
                        logger.error(f"Error calculating amounts for receipt {receipt_item.id}: {str(ex)}")
                        continue

        except Exception as recalc_error:
            # Log recalculation error but don't fail the creation
            logger.error("Error recalculating amounts for all receipts: %s", str(recalc_error))

        logger.info("Payment receipt created | transactionID=%s | student_id=%s | user=%s | previous_advance_applied=%s | new_advance=%s",
                    obj.transactionID, obj.student_id, getattr(request.user, "email", str(request.user)), previous_advance_amount, advance)

        resp = {
            "id": obj.id,
            "student_id": obj.student_id,
            "transactionID": obj.transactionID,
            "semyear": obj.semyear,
            "paymentmode": obj.paymentmode,
            "paidamount": obj.paidamount,
            "pendingamount": obj.pendingamount,
            "advanceamount": obj.advanceamount,
            "semyearfees": obj.semyearfees,
            "payment_type": obj.payment_type,
            "status": obj.status,
            "payment_categories": obj.payment_categories,
            "previous_advance_applied": previous_advance_amount,
            "calculation_note": f"Total Fees: {total_fees_val}, Current Payment: {new_paid_amount_float}, Previous Advance: {previous_advance_amount}, Effective Payment: {effective_total_payment}, Pending: {pending}, Advance: {advance}"
        }

        return Response({
            "message": f"Payment receipt created successfully. Previous advance of {previous_advance_amount} applied.",
            "data": resp
        }, status=status.HTTP_201_CREATED)

    except Exception as exc:
        if hasattr(exc, "detail"):
            logger.error("Validation error creating payment receipt: %s | payload=%s | user=%s",
                         exc.detail, request.data, getattr(request.user, "email", str(request.user)))
            return Response({"errors": exc.detail}, status=status.HTTP_400_BAD_REQUEST)

        logger.error("Unexpected error creating payment receipt: %s | payload=%s | user=%s",
                     str(exc), request.data, getattr(request.user, "email", str(request.user)))
        return Response({"message": "Something went wrong while creating the payment receipt."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from django.db.models import Prefetch
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def universities_with_courses(request):
    # Lean course queryset using only existing fields on your model
    course_qs = (
        Course.objects
        .only("id", "name", "year", "university_id")
        .order_by("name")
    )

    universities = (
        University.objects
        .only("id", "university_name")
        .prefetch_related(Prefetch("course_set", queryset=course_qs))
        .order_by("university_name")
    )

    data = [
        {
            "id": u.id,
            "university_name": u.university_name,
            "courses": [
                {
                    "id": c.id,
                    "name": c.name,
                    "year": c.year,
                }
                for c in u.course_set.all()
            ],
        }
        for u in universities
    ]

    return Response({"universities": data}, status=status.HTTP_200_OK)
  

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_uploaded_files(request):
#     """Get list of uploaded files for a university (metadata only; no media saved)."""
#     university_id = request.GET.get('university')
#     upload_type = request.GET.get('upload_type')  # 'bulk_exam' or 'single_subject'

#     if not university_id:
#         return Response({"error": "University ID is required"}, status=400)

#     try:
#         filters = {'university_id': university_id}
#         if upload_type:
#             filters['upload_type'] = upload_type

#         uploaded_files = ExamFileUpload.objects.filter(**filters).order_by('-uploaded_at')

#         files_list = [{
#             'id': uf.id,
#             'file_name': uf.file_name,
#             'file_size': uf.file_size,
#             'upload_type': uf.upload_type,
#             'upload_type_display': uf.get_upload_type_display(),
#             'uploaded_at': uf.uploaded_at.strftime('%Y-%m-%d %H:%M'),
#             'uploaded_by': uf.uploaded_by,
#         } for uf in uploaded_files]

#         return Response({
#             "uploaded_files": files_list,
#             "total_count": len(files_list)
#         })
#     except Exception as e:
#         logger.error(f"Error fetching uploaded files: {str(e)}", exc_info=True)
#         return Response({"error": "Internal server error"}, status=500)

from django.urls import reverse, NoReverseMatch
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_uploaded_files(request):
    """List uploads for a university (metadata only; no media saved)."""
    university_id = request.GET.get('university')
    upload_type = request.GET.get('upload_type')  # optional

    if not university_id:
        return Response({"error": "University ID is required"}, status=400)

    try:
        filters = {'university_id': university_id}
        if upload_type:
            filters['upload_type'] = upload_type

        uploaded_files = ExamFileUpload.objects.filter(**filters).order_by('-uploaded_at')

        files_list = []
        for uf in uploaded_files:
            files_list.append({
                'id': uf.id,
                'file_name': uf.file_name,
                'file_size': uf.file_size,
                'upload_type': uf.upload_type,
                'upload_type_display': uf.get_upload_type_display(),
                'uploaded_at': uf.uploaded_at.strftime('%Y-%m-%d %H:%M'),
                'uploaded_by': uf.uploaded_by,
                # Reconstructed download with same columns for that upload type:
                'reconstructed_download_url': request.build_absolute_uri(
                    reverse('download_exam_data_excel') + f"?university={university_id}&file_id={uf.id}"
                ),
            })

        return Response({"uploaded_files": files_list, "total_count": len(files_list)})
    except Exception as e:
        logger.error(f"Error fetching uploaded files: {str(e)}", exc_info=True)
        return Response({"error": "Internal server error"}, status=500)


# ---------- B) DOWNLOAD reconstructed Excel from DB (works for both types)
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def download_exam_data_excel(request):
#     """
#     Reconstruct exam data to an .xlsx directly from database.
#     Optional query params:
#     - university=<id> (required)
#     - file_id=<ExamFileUpload.id> (optional; only used to switch headers by upload_type)
#     """
#     university_id = request.GET.get('university')
#     file_id = request.GET.get('file_id')

#     if not university_id:
#         return Response({"error": "University ID is required"}, status=400)

#     try:
#         uploaded_file = None
#         if file_id:
#             uploaded_file = ExamFileUpload.objects.filter(id=file_id, university_id=university_id).first()

#         exams = Examination.objects.filter(university_id=university_id).select_related(
#             'course', 'stream', 'substream', 'subject'
#         )
#         if not exams.exists():
#             return Response({"error": "No exam data found for this university"}, status=404)

#         output = BytesIO()
#         wb = Workbook()
#         ws = wb.active
#         ws.title = "Exam Data"

#         # Headers
#         if uploaded_file and uploaded_file.upload_type == 'bulk_exam':
#             headers = [
#                 'COURSE', 'STREAM', 'SUBSTREAM', 'SUBJECT NAME', 'YEAR/SEMESTER',
#                 'TYPE OF EXAM', 'SESSION', 'MODE', 'QUESTION', 'QUESTION TYPE',
#                 'MARKS', 'OPTION 1', 'OPTION 2', 'OPTION 3', 'OPTION 4',
#                 'ANSWER', 'DIFFICULTY LEVEL'
#             ]
#         else:
#             headers = [
#                 'Subject', 'Exam Type', 'Session', 'Study Pattern', 'Semester/Year',
#                 'Total Marks', 'Passing Marks', 'Exam Duration', 'Question',
#                 'Question Type', 'Marks', 'Option 1', 'Option 2', 'Option 3',
#                 'Option 4', 'Answer', 'Difficulty Level'
#             ]
#         ws.append(headers)

#         # Rows
#         for exam in exams:
#             qs = Questions.objects.filter(exam=exam)
#             for q in qs:
#                 if uploaded_file and uploaded_file.upload_type == 'bulk_exam':
#                     row = [
#                         getattr(exam.course, 'name', ''),
#                         getattr(exam.stream, 'name', ''),
#                         getattr(exam.substream, 'name', '') if exam.substream_id else '',
#                         getattr(exam.subject, 'name', ''),
#                         exam.semyear or '',
#                         exam.examtype or '',
#                         exam.session or '',
#                         exam.studypattern or '',
#                         q.question or '',
#                         q.type or '',
#                         q.marks or '',
#                         q.option1 or '',
#                         q.option2 or '',
#                         q.option3 or '',
#                         q.option4 or '',
#                         (q.answer or '').lower(),
#                         q.difficultylevel or '',
#                     ]
#                 else:
#                     row = [
#                         getattr(exam.subject, 'name', ''),
#                         exam.examtype or '',
#                         exam.session or '',
#                         exam.studypattern or '',
#                         exam.semyear or '',
#                         exam.totalmarks or '',
#                         exam.passingmarks or '',
#                         exam.examduration or '',
#                         q.question or '',
#                         q.type or '',
#                         q.marks or '',
#                         q.option1 or '',
#                         q.option2 or '',
#                         q.option3 or '',
#                         q.option4 or '',
#                         (q.answer or '').lower(),
#                         q.difficultylevel or '',
#                     ]
#                 ws.append(row)

#         wb.save(output)
#         output.seek(0)

#         filename = f"exam_data_{university_id}.xlsx"
#         if uploaded_file:
#             # keep a friendly name hinting reconstruction
#             base = os.path.splitext(uploaded_file.file_name)[0]
#             filename = f"reconstructed_{base}.xlsx"

#         resp = HttpResponse(
#             output.getvalue(),
#             content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#         )
#         resp['Content-Disposition'] = f'attachment; filename="{filename}"'
#         return resp

#     except Exception as e:
#         logger.error(f"Error generating Excel file: {str(e)}", exc_info=True)
#         return Response({"error": "Internal server error"}, status=500)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def download_exam_data_excel(request):
#     """
#     Reconstruct exam data to .xlsx from DB.
#     Query:
#       - university (required)
#       - file_id (optional): if provided, only include questions linked to that upload,
#                             and use headers matching that upload_type.
#     """
#     university_id = request.GET.get('university')
#     file_id = request.GET.get('file_id')

#     if not university_id:
#         return Response({"error": "University ID is required"}, status=400)

#     try:
#         uploaded_file = None
#         if file_id:
#             uploaded_file = ExamFileUpload.objects.filter(id=file_id, university_id=university_id).first()
#             if not uploaded_file:
#                 return Response({"error": "Upload file not found for this university"}, status=404)

#         output = BytesIO()
#         wb = Workbook()
#         ws = wb.active
#         ws.title = "Exam Data"

#         # Headers by upload_type when file_id present; otherwise single-subject style by default
#         if uploaded_file and uploaded_file.upload_type == 'bulk_exam':
#             headers = [
#                 'COURSE', 'STREAM', 'SUBSTREAM', 'SUBJECT NAME', 'YEAR/SEMESTER',
#                 'TYPE OF EXAM', 'SESSION', 'MODE', 'QUESTION', 'QUESTION TYPE',
#                 'MARKS', 'OPTION 1', 'OPTION 2', 'OPTION 3', 'OPTION 4',
#                 'ANSWER', 'DIFFICULTY LEVEL'
#             ]
#         else:
#             headers = [
#                 'Subject', 'Exam Type', 'Session', 'Study Pattern', 'Semester/Year',
#                 'Total Marks', 'Passing Marks', 'Exam Duration', 'Question',
#                 'Question Type', 'Marks', 'Option 1', 'Option 2', 'Option 3',
#                 'Option 4', 'Answer', 'Difficulty Level'
#             ]
#         ws.append(headers)

#         if uploaded_file:
#             # Only questions inserted by that upload; preserves row order by PK
#             qs = (Questions.objects
#                   .filter(excel_upload=uploaded_file, exam__university_id=university_id)
#                   .select_related('exam__course', 'exam__stream', 'exam__substream', 'exam__subject')
#                   .order_by('id'))
#             if not qs.exists():
#                 return Response({"error": "No questions found for this uploaded file"}, status=404)

#             for q in qs:
#                 exam = q.exam
#                 if uploaded_file.upload_type == 'bulk_exam':
#                     row = [
#                         getattr(exam.course, 'name', ''),
#                         getattr(exam.stream, 'name', ''),
#                         getattr(exam.substream, 'name', '') if exam.substream_id else '',
#                         getattr(exam.subject, 'name', ''),
#                         exam.semyear or '',
#                         exam.examtype or '',
#                         exam.session or '',
#                         exam.studypattern or '',
#                         q.question or '',
#                         q.type or '',
#                         q.marks or '',
#                         q.option1 or '',
#                         q.option2 or '',
#                         q.option3 or '',
#                         q.option4 or '',
#                         (q.answer or '').lower(),
#                         q.difficultylevel or '',
#                     ]
#                 else:
#                     row = [
#                         getattr(exam.subject, 'name', ''),
#                         exam.examtype or '',
#                         exam.session or '',
#                         exam.studypattern or '',
#                         exam.semyear or '',
#                         exam.totalmarks or '',
#                         exam.passingmarks or '',
#                         exam.examduration or '',
#                         q.question or '',
#                         q.type or '',
#                         q.marks or '',
#                         q.option1 or '',
#                         q.option2 or '',
#                         q.option3 or '',
#                         q.option4 or '',
#                         (q.answer or '').lower(),
#                         q.difficultylevel or '',
#                     ]
#                 ws.append(row)
#         else:
#             # Legacy: everything for the university
#             exams = Examination.objects.filter(university_id=university_id).select_related(
#                 'course', 'stream', 'substream', 'subject'
#             )
#             if not exams.exists():
#                 return Response({"error": "No exam data found for this university"}, status=404)

#             for exam in exams:
#                 for q in Questions.objects.filter(exam=exam).order_by('id'):
#                     row = [
#                         getattr(exam.subject, 'name', ''),
#                         exam.examtype or '',
#                         exam.session or '',
#                         exam.studypattern or '',
#                         exam.semyear or '',
#                         exam.totalmarks or '',
#                         exam.passingmarks or '',
#                         exam.examduration or '',
#                         q.question or '',
#                         q.type or '',
#                         q.marks or '',
#                         q.option1 or '',
#                         q.option2 or '',
#                         q.option3 or '',
#                         q.option4 or '',
#                         (q.answer or '').lower(),
#                         q.difficultylevel or '',
#                     ]
#                     ws.append(row)

#         wb.save(output)
#         output.seek(0)

#         filename = f"exam_data_{university_id}.xlsx"
#         if uploaded_file:
#             base = os.path.splitext(uploaded_file.file_name)[0]
#             filename = f"reconstructed_{base}.xlsx"

#         resp = HttpResponse(
#             output.getvalue(),
#             content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#         )
#         resp['Content-Disposition'] = f'attachment; filename="{filename}"'
#         return resp

#     except Exception as e:
#         logger.error(f"Error generating Excel file: {str(e)}", exc_info=True)
#         return Response({"error": "Internal server error"}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_exam_data_excel(request):
    """
    Reconstruct an Excel with EXACT fixed columns for the upload type.
    Query:
      - university (required)
      - file_id (preferred): use the uploaded file's type and only its questions
      - OR upload_type in {'bulk_exam','single_subject'} to export all rows in that format
    """
    university_id = request.GET.get('university')
    file_id = request.GET.get('file_id')
    upload_type_param = request.GET.get('upload_type')

    if not university_id:
        return Response({"error": "University ID is required"}, status=400)

    try:
        if file_id:
            upload = ExamFileUpload.objects.filter(id=file_id, university_id=university_id).first()
            if not upload:
                return Response({"error": "Upload file not found for this university"}, status=404)
            fmt = upload.upload_type
        else:
            if upload_type_param not in ('bulk_exam', 'single_subject'):
                return Response({"error": "Provide either file_id or upload_type={'bulk_exam','single_subject'}"}, status=400)
            fmt = upload_type_param
            upload = None

        headers = BULK_HEADERS if fmt == 'bulk_exam' else SINGLE_HEADERS

        output = BytesIO()
        wb = Workbook()
        ws = wb.active
        ws.title = "Exam Data"
        ws.append(headers)

        if upload:
            qs = (Questions.objects
                  .filter(excel_upload=upload, exam__university_id=university_id)
                  .select_related('exam__course', 'exam__stream', 'exam__substream', 'exam__subject')
                  .order_by('id'))
            if not qs.exists():
                return Response({"error": "No questions found for this uploaded file"}, status=404)

            for q in qs:
                exam = q.exam
                ws.append(build_bulk_row(exam, q) if fmt == 'bulk_exam' else build_single_row(exam, q))
        else:
            exams = (Examination.objects
                     .filter(university_id=university_id)
                     .select_related('course', 'stream', 'substream', 'subject'))
            if not exams.exists():
                return Response({"error": "No exam data found for this university"}, status=404)

            for exam in exams:
                for q in Questions.objects.filter(exam=exam).order_by('id'):
                    ws.append(build_bulk_row(exam, q) if fmt == 'bulk_exam' else build_single_row(exam, q))

        wb.save(output)
        output.seek(0)

        if upload:
            base = os.path.splitext(upload.file_name)[0]
            filename = f"reconstructed_{base}.xlsx"
        else:
            filename = f"exam_data_{university_id}_{fmt}.xlsx"

        resp = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp

    except Exception as e:
        logger.error(f"Error generating Excel file: {str(e)}", exc_info=True)
        return Response({"error": "Internal server error"}, status=500)

# ---------- C) DELETE upload metadata record (no media to remove)
# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def delete_uploaded_file(request, file_id):
#     """Delete uploaded file metadata; no physical file stored."""
#     try:
#         uploaded_file = ExamFileUpload.objects.get(id=file_id)
#         uploaded_file.delete()
#         return Response({"status": "success", "message": "File metadata deleted successfully"})
#     except ExamFileUpload.DoesNotExist:
#         return Response({"error": "File record not found"}, status=404)
#     except Exception as e:
#         logger.error(f"Error deleting file: {str(e)}", exc_info=True)
#         return Response({"error": "Internal server error"}, status=500)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_uploaded_file(request, file_id):
    try:
        uploaded_file = ExamFileUpload.objects.get(id=file_id)
        uploaded_file.delete()
        return Response({"status": "success", "message": "File metadata deleted successfully"})
    except ExamFileUpload.DoesNotExist:
        return Response({"error": "File record not found"}, status=404)
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}", exc_info=True)
        return Response({"error": "Internal server error"}, status=500)




@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def bulk_exam_upload(request):
    try:
        if 'file' not in request.FILES:
            return Response({"status": "error", "message": "No file uploaded"}, status=400)

        file = request.FILES['file']
        university_id = request.data.get("university")
        if not university_id:
            return Response({"status": "error", "message": "University is required"}, status=400)

        file_hash = calculate_file_hash(file)
        if check_file_exists(university_id, file_hash, 'bulk_exam'):
            existing = ExamFileUpload.objects.filter(
                university_id=university_id, file_hash=file_hash, upload_type='bulk_exam'
            ).first()
            when = existing.uploaded_at.strftime('%Y-%m-%d %H:%M') if existing else 'earlier'
            return Response({
                "status": "error",
                "message": f"File '{file.name}' already uploaded for this university on {when}"
            }, status=400)

        # Validate bulk format (19 fixed columns)
        df, error = validate_excel_file(file)
        if error:
            return Response({"status": "error", "message": error}, status=400)

        # Create metadata first so we can link Examination & Questions
        uploaded_by = request.user.username if request.user.is_authenticated else "Bulk Upload"
        upload_meta = save_file_metadata(university_id, file, file_hash, 'bulk_exam', uploaded_by)

        errors, success_rows = [], []
        total_saved = 0

        with transaction.atomic():
            for idx, row in df.iterrows():
                try:
                    course_name   = str(row["COURSE"]).strip()
                    stream_name   = str(row["STREAM"]).strip()
                    subject_name  = str(row["SUBJECT NAME"]).strip()
                    substream_val = str(row["SUBSTREAM"]).strip() if pd.notna(row["SUBSTREAM"]) else None
                    exam_semyear  = str(row["YEAR/SEMESTER"]).strip()
                    session_val   = str(row["SESSION"]).strip()
                    mode_val      = str(row["MODE"]).strip()
                    exam_type     = str(row["TYPE OF EXAM"]).strip()
                    exam_duration = str(row.get("EXAM DURATION", "") or "").strip()
                    passing_marks = str(row.get("PASSING MARKS", "") or "").strip()
                    qtype         = str(row["QUESTION TYPE"]).strip()
                    qdiff         = str(row.get("DIFFICULTY LEVEL", "") or "").strip()
                    qtext         = str(row["QUESTION"]).strip()
                    marks_val     = int(row["MARKS"])

                    course = Course.objects.get(name=course_name, university_id=university_id)
                    stream = Stream.objects.get(name=stream_name, course=course)

                    substream = None
                    if substream_val and substream_val.lower() != 'nan':
                        substream = SubStream.objects.get(name=substream_val, stream=stream)

                    subject = Subject.objects.filter(
                        name=subject_name, stream=stream, substream=substream, semyear=exam_semyear
                    ).first()
                    if not subject:
                        raise Subject.DoesNotExist(
                            f"Subject '{subject_name}' with sem/year '{exam_semyear}' not found"
                        )

                    # Find or create the exam
                    exam = Examination.objects.filter(
                        university_id=university_id,
                        course=course,
                        stream=stream,
                        substream=substream,
                        subject=subject,
                        examtype=exam_type,
                        session=session_val,
                        studypattern=mode_val,
                        semyear=exam_semyear,
                    ).first()

                    if exam:
                        # set excel_upload only if not already set
                        if not exam.excel_upload_id:
                            exam.excel_upload = upload_meta
                        # increment totals
                        exam.totalquestions = str((int(exam.totalquestions) if exam.totalquestions else 0) + 1)
                        exam.totalmarks = str((int(exam.totalmarks) if exam.totalmarks else 0) + marks_val)
                        # fill duration/passing if empty
                        if not exam.examduration and exam_duration:
                            exam.examduration = exam_duration
                        if not exam.passingmarks and passing_marks:
                            exam.passingmarks = passing_marks
                        exam.save()
                    else:
                        exam = Examination.objects.create(
                            university_id=university_id,
                            course=course,
                            stream=stream,
                            substream=substream,
                            subject=subject,
                            examtype=exam_type,
                            examduration=exam_duration,
                            studypattern=mode_val,
                            semyear=exam_semyear,
                            session=session_val,
                            totalquestions="1",
                            totalmarks=str(marks_val),
                            passingmarks=passing_marks,
                            created_by="Bulk File Uploaded",
                            active=True,
                            archive=False,
                            excel_upload=upload_meta,  # NEW: link upload to exam
                        )

                    # Create question (link this upload too)
                    Questions.objects.create(
                        exam=exam,
                        excel_upload=upload_meta,   # NEW
                        question=qtext,
                        type=qtype,
                        marks=str(marks_val),
                        option1=str(row.get("OPTION 1", "") or "").strip(),
                        option2=str(row.get("OPTION 2", "") or "").strip(),
                        option3=str(row.get("OPTION 3", "") or "").strip(),
                        option4=str(row.get("OPTION 4", "") or "").strip(),
                        answer=str(row["ANSWER"]).strip().lower(),
                        difficultylevel=qdiff,
                    )

                    success_rows.append(f"Row {idx + 2}: Question added successfully.")
                    total_saved += 1

                except (Course.DoesNotExist, Stream.DoesNotExist, SubStream.DoesNotExist, Subject.DoesNotExist) as e:
                    errors.append(f"Row {idx + 2}: {e}")
                except Exception as e:
                    logger.error("Bulk row error", exc_info=True)
                    errors.append(f"Row {idx + 2}: Unexpected error: {str(e)}")

            if total_saved == 0:
                upload_meta.delete()

        return Response({
            "status": "success",
            "message": "Data processed",
            "success_logs": success_rows,
            "error_logs": errors,
            "file_id": upload_meta.id if upload_meta.pk else None
        }, status=200)

    except Exception as e:
        logger.error(f"bulk_exam_upload error: {e}", exc_info=True)
        return Response({"status": "error", "message": "Internal server error"}, status=500)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def set_exam_for_subject(request):
    try:
        data = request.data
        university_id = data.get('university')
        course_id = data.get('course')
        stream_id = data.get('stream')
        substream_id = data.get('substream')
        subject_id = data.get('subject')
        examtype = data.get('examtype')
        examduration = data.get('examduration')
        session = data.get('session')
        studypattern = data.get('studypattern')
        semyear = data.get('semyear')
        totalmarks = data.get('totalmarks')
        passingmarks = data.get('passingmarks')
        created_by = data.get('created_by')

        university = University.objects.filter(id=university_id).first()
        if not university:
            return Response({"error": "Invalid university ID."}, status=400)
        course = Course.objects.filter(id=course_id, university=university).first()
        if not course:
            return Response({"error": "Invalid course for the given university."}, status=400)
        stream = Stream.objects.filter(id=stream_id, course=course).first()
        if not stream:
            return Response({"error": "Invalid stream for the given course."}, status=400)
        substream = None
        if substream_id:
            substream = SubStream.objects.filter(id=substream_id, stream=stream).first()
            if not substream:
                return Response({"error": "Invalid substream for the given stream."}, status=400)
        subject = Subject.objects.filter(id=subject_id, stream=stream, substream=substream).first()
        if not subject:
            return Response({"error": "Invalid subject for the given stream and substream."}, status=400)

        excel_file = request.FILES.get('file')
        if not excel_file:
            return Response({"error": "Questions Excel file is required."}, status=400)

        # dedupe for single_subject
        file_hash = calculate_file_hash(excel_file)
        if check_file_exists(university_id, file_hash, 'single_subject'):
            existing = ExamFileUpload.objects.filter(
                university_id=university_id, file_hash=file_hash, upload_type='single_subject'
            ).first()
            when = existing.uploaded_at.strftime('%Y-%m-%d %H:%M') if existing else 'earlier'
            return Response({"error": f"File '{excel_file.name}' already uploaded on {when}"}, status=400)

        # read + validate (single)
        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            logger.error(f"Error reading Excel file: {str(e)}", exc_info=True)
            return Response({"error": "Invalid Excel file."}, status=400)

        missing = [c for c in REQUIRED_SINGLE_COLUMNS if c not in df.columns]
        if missing:
            return Response({"error": f"Missing columns in Excel: {', '.join(missing)}"}, status=400)

        # metadata first to attach to Exam and Questions
        uploaded_by = request.user.username if request.user.is_authenticated else (created_by or "Single Upload")
        upload_meta = save_file_metadata(university_id, excel_file, file_hash, 'single_subject', uploaded_by)

        # create exam (link the upload here)
        exam = Examination.objects.create(
            university=university,
            course=course,
            stream=stream,
            substream=substream,
            subject=subject,
            examtype=examtype,
            examduration=examduration,
            studypattern=studypattern,
            semyear=semyear,
            session=session,
            totalmarks=str(totalmarks or ""),
            passingmarks=str(passingmarks or ""),
            created_by=created_by,
            excel_upload=upload_meta,  # NEW: link upload to exam
        )

        total_questions, error_count = 0, 0
        error_messages = []

        for i, row in df.iterrows():
            try:
                # Mandatory fields check
                if any(pd.isna(row.get(col)) for col in REQUIRED_SINGLE_COLUMNS):
                    error_messages.append(f"Row {i + 2}: Missing mandatory fields.")
                    error_count += 1
                    continue

                Questions.objects.create(
                    exam=exam,
                    excel_upload=upload_meta,  # NEW
                    question=str(row['Question']),
                    type=str(row['Question Type']),
                    marks=str(int(row['Marks'])),
                    option1=str(row['Option 1']),
                    option2=str(row['Option 2']),
                    option3=str(row['Option 3']),
                    option4=str(row['Option 4']),
                    answer=str(row['Answer']).lower(),
                    difficultylevel=str(row['Difficulty Level'])
                )
                total_questions += 1
            except Exception as e:
                logger.error(f"Row {i + 2} error: {e}", exc_info=True)
                error_messages.append(f"Row {i + 2}: {e}")
                error_count += 1

        exam.totalquestions = str(total_questions)
        exam.save()

        if total_questions == 0:
            upload_meta.delete()
            exam.delete()

        return Response({
            "status": "success",
            "message": "Data processed successfully.",
            "total_success": total_questions,
            "total_errors": error_count,
            "errors": error_messages,
            "file_id": upload_meta.id if upload_meta.pk else None
        }, status=201)

    except Exception as e:
        logger.error(f"set_exam_for_subject error: {e}", exc_info=True)
        return Response({"error": "An unexpected error occurred."}, status=500)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_and_student(request, user_id: int):
    """
    DELETE /users/<user_id>/delete/

    Manually deletes ALL related rows for the single student linked to user_id:
      - Enrolled (0..n)
      - StudentDocuments (0..n)
      - StudentFees (0..n)
      - PersonalDocuments (0..n)
      - Qualification (0..n)  # modeled as FK, so we handle n just in case
      - AdditionalEnrollmentDetails (0..n)
    Then deletes the Student (0..1) and the User (1).
    """
    user = get_object_or_404(User, pk=user_id)

    # If a user might have 0 or 1 student, this picks that one; if your data guarantees 1:1, this is fine.
    student = Student.objects.filter(user_id=user_id).first()

    counts = {
        "Enrolled": 0,
        "StudentDocuments": 0,
        "StudentFees": 0,
        "PersonalDocuments": 0,
        "Qualification": 0,
        "AdditionalEnrollmentDetails": 0,
        "Student": 0,
        "User": 0,
    }

    with transaction.atomic():
        if student:
            sid = student.id
            counts["Enrolled"], _ = Enrolled.objects.filter(student_id=sid).delete()
            counts["StudentDocuments"], _ = StudentDocuments.objects.filter(student_id=sid).delete()
            counts["StudentFees"], _ = StudentFees.objects.filter(student_id=sid).delete()
            counts["PersonalDocuments"], _ = PersonalDocuments.objects.filter(student_id=sid).delete()
            counts["Qualification"], _ = Qualification.objects.filter(student_id=sid).delete()
            counts["AdditionalEnrollmentDetails"], _ = AdditionalEnrollmentDetails.objects.filter(student_id=sid).delete()
            counts["Student"], _ = student.delete()

        counts["User"], _ = user.delete()

    return Response(
        {
            "message": "User and all related student data deleted successfully.",
            "user_id": user_id,
            "deleted_counts": counts,
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_examination(request, exam_id):
    """
    Delete examination only if:
    1. No data exists in submitted_answer table for this exam_id
    2. No data exists in result table for this exam_id
    """
    try:
        # Get the examination object
        examination = Examination.objects.get(id=exam_id)
        
        # Check condition 1: No data in submitted_answer table for this exam_id
        submitted_exams_count = SubmittedExamination.objects.filter(exam=examination).count()
        if submitted_exams_count > 0:
            return Response({
                "status": "error",
                "message": f"Cannot delete examination. There are {submitted_exams_count} submitted answers associated with this exam."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check condition 2: No data in result table for this exam_id
        results_count = Result.objects.filter(exam=examination).count()
        if results_count > 0:
            return Response({
                "status": "error",
                "message": f"Cannot delete examination. There are {results_count} results associated with this exam."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # If both conditions are satisfied, delete the examination
        with transaction.atomic():
            # First delete related questions
            questions_count = Questions.objects.filter(exam=examination).count()
            Questions.objects.filter(exam=examination).delete()
            
            # Store exam details before deletion for response
            exam_details = {
                'id': examination.id,
                'exam_type': examination.examtype,
                'subject': examination.subject.name if examination.subject else 'N/A'
            }
            
            # Then delete the examination (THIS DELETES FROM EXAMINATION TABLE)
            examination.delete()
            
            # Debug: Verify deletion
            exam_exists = Examination.objects.filter(id=exam_id).exists()
            print(f"Exam {exam_id} still exists after deletion: {exam_exists}")  # Should be False
        
        return Response({
            "status": "success",
            "message": f"Examination '{exam_details['exam_type']} - {exam_details['subject']}' deleted successfully.",
            "deleted_items": {
                "examination": 1,
                "questions": questions_count
            }
        }, status=status.HTTP_200_OK)
        
    except Examination.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Examination not found."
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"An error occurred while deleting examination: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_exam_file_upload(request, file_upload_id):
    """
    Delete ExamFileUpload with detailed validation
    """
    try:
        exam_file_upload = ExamFileUpload.objects.get(id=file_upload_id)
        
        # Get all linked examinations
        linked_examinations = Examination.objects.filter(excel_upload=exam_file_upload)
        linked_exam_ids = list(linked_examinations.values_list('id', flat=True))
        
        # Check conditions with detailed counts
        validation_errors = []
        
        # Check submitted answers for all linked exams
        submitted_exams_count = SubmittedExamination.objects.filter(
            exam_id__in=linked_exam_ids
        ).count()
        if submitted_exams_count > 0:
            validation_errors.append(f"{submitted_exams_count} submitted answers")
        
        # Check results for all linked exams
        results_count = Result.objects.filter(
            exam_id__in=linked_exam_ids
        ).count()
        if results_count > 0:
            validation_errors.append(f"{results_count} results")
        
        if validation_errors:
            error_message = "Cannot delete file upload. There are " + " and ".join(validation_errors) + " associated with exams from this file upload."
            return Response({
                "status": "error",
                "message": error_message,
                "details": {
                    "file_upload_id": file_upload_id,
                    "file_name": exam_file_upload.file_name,
                    "linked_examinations_count": len(linked_exam_ids),
                    "submitted_answers_count": submitted_exams_count,
                    "results_count": results_count
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Perform deletion
        with transaction.atomic():
            # Count questions to be deleted
            questions_from_exams = Questions.objects.filter(exam__in=linked_examinations)
            questions_from_file = Questions.objects.filter(excel_upload=exam_file_upload)
            all_questions = questions_from_exams | questions_from_file
            questions_count = all_questions.count()
            
            # Delete in order: Questions -> Examinations -> File Upload
            all_questions.delete()
            examinations_count = linked_examinations.count()
            linked_examinations.delete()
            
            file_name = exam_file_upload.file_name
            exam_file_upload.delete()
        
        return Response({
            "status": "success",
            "message": f"File upload '{file_name}' deleted successfully.",
            "deleted_items": {
                "file_upload": 1,
                "examinations": examinations_count,
                "questions": questions_count
            },
            "file_details": {
                "id": file_upload_id,
                "file_name": file_name,
                "upload_type": exam_file_upload.upload_type,
                "university": exam_file_upload.university.university_name
            }
        }, status=status.HTTP_200_OK)
        
    except ExamFileUpload.DoesNotExist:
        return Response({
            "status": "error",
            "message": f"Exam file upload with ID {file_upload_id} not found."
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({
            "status": "error",
            "message": "An error occurred while deleting file upload.",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# views.py - Updated backend APIs

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_uploaded_student_files(request):
    """
    Get list of ALL uploaded student files (no university filter)
    """
    try:
        # Get all student file uploads ordered by most recent first
        student_uploads = StudentFileUpload.objects.all().order_by('-uploaded_at')
        
        uploaded_files = []
        for upload in student_uploads:
            uploaded_files.append({
                'id': upload.id,
                'file_name': upload.file_name,
                'file_size': upload.file_size,
                'uploaded_at': upload.uploaded_at,
                'uploaded_by': upload.uploaded_by,
                'total_rows': upload.total_rows,
                'success_rows': upload.success_rows,
                'error_rows': upload.error_rows,
            })

        return Response({
            'uploaded_files': uploaded_files
        })

    except Exception as e:
        logger.error(f"get_uploaded_student_files error: {str(e)}", exc_info=True)
        return Response({"error": "Internal server error"}, status=500)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_student_file_upload(request, file_id):
    """
    Delete student file upload and all associated students
    """
    try:
        from .models import StudentFileUpload
        from super_admin.models import Student, Enrolled

        upload = get_object_or_404(StudentFileUpload, id=file_id)
        
        # Get counts before deletion for response
        student_count = Student.objects.filter(student_upload=upload).count()
        
        # Delete all students associated with this upload (this will cascade to Enrolled records)
        deleted_students, _ = Student.objects.filter(student_upload=upload).delete()
        
        # Delete the file upload record
        upload_name = upload.file_name
        upload.delete()
        
        return Response({
            'status': 'success',
            'message': f'Successfully deleted student file "{upload_name}" and all associated student records',
            'deleted_items': {
                'file_upload': 1,
                'students': student_count,
            }
        })

    except Exception as e:
        logger.error(f"delete_student_file_upload error: {str(e)}", exc_info=True)
        return Response({"error": "Internal server error"}, status=500)
      

from decimal import Decimal, InvalidOperation
from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce, Cast
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Student, Enrolled, StudentFees, PaymentReciept

def _dec(x) -> Decimal:
    if x in (None, "", "None"):
        return Decimal("0")
    try:
        return Decimal(str(x))
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _total_fees_for_sem(student, sem_str: str) -> Decimal:
    """
    StudentFees me se given sem ka total nikalo.
    Agar totalfees > 0 hai to wahi, warna components sum - discount.
    Agar row hi na mile to 0.
    """
    fees = StudentFees.objects.filter(student=student, sem=str(sem_str)).order_by("-id").first()
    if not fees:
        return Decimal("0")
    total = _dec(fees.totalfees)
    if total > 0:
        return total
    total = (
        _dec(fees.tutionfees) + _dec(fees.examinationfees) + _dec(fees.bookfees)
        + _dec(fees.resittingfees) + _dec(fees.entrancefees) + _dec(fees.extrafees)
        - _dec(fees.discount)
    )
    return total if total > 0 else Decimal("0")


# ---------- API ----------
#11-11-2025 
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def payment_receipt_details(request):
#     student_id = request.GET.get("student_id")
#     if not student_id:
#         return Response({"error": "student_id is required"}, status=status.HTTP_400_BAD_REQUEST)

#     # Student
#     student = Student.objects.filter(id=student_id).first()
#     if not student:
#         return Response({"error": "Invalid student_id"}, status=status.HTTP_404_NOT_FOUND)

#     # Enrollment (latest)
#     enrolled = Enrolled.objects.filter(student=student).order_by("-id").first()
#     if not enrolled:
#         return Response({"error": "Enrollment not found for this student"}, status=status.HTTP_404_NOT_FOUND)

#     current_sem = str(enrolled.current_semyear).strip()
#     cur_total_fees = _total_fees_for_sem(student, current_sem)

#     # ---- Current sem realised receipts ----
#     cur_qs = PaymentReciept.objects.filter(
#         student=student,
#         semyear=current_sem,
#         status__iexact="Realised"
#     )

#     if cur_qs.exists():
#         # Case A: current sem has receipts -> aggregate paid with proper casting
#         DEC = DecimalField(max_digits=18, decimal_places=2)
#         agg = cur_qs.aggregate(
#             total_paid=Coalesce(
#                 Sum(Cast("paidamount", DEC)),
#                 Value(0, output_field=DEC),
#                 output_field=DEC
#             )
#         )
#         total_paid = _dec(agg["total_paid"])

#         diff = cur_total_fees - total_paid
#         if diff > 0:
#             paymentpending = "yes"
#             pendingamount = diff
#             advance_amount = Decimal("0")
#         else:
#             paymentpending = "no"
#             pendingamount = Decimal("0")
#             advance_amount = -diff  # positive

#         return Response({
#             "student_id": student.id,
#             "current_semyear": current_sem,
#             "paymentpending": paymentpending,
#             "total_fees": str(cur_total_fees),
#             "total_paid": str(total_paid),
#             "pendingamount": str(pendingamount),
#             "advance_amount": str(advance_amount),
#             "source": "current_semyear"
#         }, status=status.HTTP_200_OK)

#     # ---- Case B: no current sem receipts -> use latest previous sem's advance to reduce pending ----
#     prev_qs = PaymentReciept.objects.filter(
#         student=student,
#         status__iexact="Realised"
#     ).exclude(semyear__isnull=True)

#     # numeric compare if possible; else lexical
#     try:
#         cur_sem_int = int(current_sem)
#         prev_qs = prev_qs.extra(where=["CAST(semyear AS SIGNED) < %s"], params=[cur_sem_int])
#     except ValueError:
#         prev_qs = prev_qs.filter(semyear__lt=current_sem)

#     latest_prev = prev_qs.order_by("-transaction_date", "-id").first()
#     prev_advance = _dec(latest_prev.advanceamount) if latest_prev else Decimal("0")

#     # ✅ APPLY previous-sem advance to current sem pending
#     net_pending = cur_total_fees - prev_advance
#     if net_pending > 0:
#         paymentpending = "yes"
#         pendingamount = net_pending
#     else:
#         paymentpending = "no"
#         pendingamount = Decimal("0")
#         # You may also expose carry-forward advance if desired:
#         # advance_carry_forward = -net_pending

#     return Response({
#         "student_id": student.id,
#         "current_semyear": current_sem,
#         "paymentpending": paymentpending,
#         "total_fees": str(cur_total_fees),        # current sem total
#         "total_paid": "0",                         # no current sem receipts yet
#         "pendingamount": str(pendingamount),       # reduced by previous advance
#         "advance_amount": str(prev_advance),       # previous sem latest advance (as-is)
#         "source": "previous_semyear_latest_receipt"
#         # Optional:
#         # "advance_carry_forward": str(max(prev_advance - cur_total_fees, Decimal("0")))
#     }, status=status.HTTP_200_OK)
    
from collections import OrderedDict
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


def safe_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


@api_view(["GET"])
def payment_receipt_details(request):
    student_id = request.query_params.get("student_id")
    if not student_id:
        return Response(
            {"error": "student_id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    receipts_qs = PaymentReciept.objects.filter(student_id=student_id).order_by("semyear", "id")
    if not receipts_qs.exists():
        return Response(
            {"error": "No payment receipts found for this student."},
            status=status.HTTP_404_NOT_FOUND,
        )

    receipts = list(receipts_qs)

    # ----------------------------------------------------------------------
    # 1) GROUP BY SEMYEAR
    # ----------------------------------------------------------------------
    sem_groups = OrderedDict()
    for r in receipts:
        sem_key = r.semyear or ""  # handle NULL/empty
        sem_groups.setdefault(sem_key, []).append(r)

    # ----------------------------------------------------------------------
    # 2) FIND TOTAL FEES PER SEM (first non-zero semyearfees)
    # ----------------------------------------------------------------------
    sem_totals = {}
    for sem_key, recs in sem_groups.items():
        total_for_sem = 0.0
        for r in recs:
            fees = safe_float(r.semyearfees, 0.0)
            if fees > 0:
                total_for_sem = fees
                break
        sem_totals[sem_key] = total_for_sem

    # ----------------------------------------------------------------------
    # 3) RECALCULATE PER-SEM WITH CARRY-FORWARD ADVANCE
    #    (we DON'T save here, just calculate for summary)
    # ----------------------------------------------------------------------
    carry_forward_advance = 0.0
    sem_summaries = OrderedDict()

    for sem_key, recs in sem_groups.items():
        total_fees_val = sem_totals.get(sem_key, 0.0)
        sem_previous_advance = carry_forward_advance

        sem_cumulative_paid = 0.0
        pending = 0.0
        advance = sem_previous_advance  # default if no receipts

        for r in recs:
            paid = safe_float(r.paidamount, 0.0)
            sem_cumulative_paid += paid

            effective_total_payment = sem_previous_advance + sem_cumulative_paid

            pending = max(0.0, total_fees_val - effective_total_payment)
            advance = max(0.0, effective_total_payment - total_fees_val)

        # After last receipt of this sem:
        carry_forward_advance = advance

        # Effective amount actually used to pay THIS sem's fees:
        # = total_fees_val - pending
        effective_paid_for_sem = total_fees_val - pending

        sem_summaries[sem_key] = {
            "total_fees": total_fees_val,
            "sem_cumulative_paid": sem_cumulative_paid,
            "previous_advance_applied": sem_previous_advance,
            "pending": pending,
            "advance": advance,
            "effective_paid_for_sem": effective_paid_for_sem,
        }

    # ----------------------------------------------------------------------
    # 4) PICK CURRENT / LATEST SEM
    # ----------------------------------------------------------------------
    # Try numeric sort (1,2,3...), fallback to string
    def sem_sort_key(k):
        try:
            return int(k)
        except (ValueError, TypeError):
            return k or ""

    all_sem_keys = list(sem_summaries.keys())
    all_sem_keys.sort(key=sem_sort_key)
    current_semyear = all_sem_keys[-1]  # last = latest
    summary = sem_summaries[current_semyear]

    # Decide paymentpending flag
    payment_pending = "yes" if summary["pending"] > 0 else "no"

    response_data = {
        "student_id": int(student_id),
        "current_semyear": str(current_semyear),
        "paymentpending": payment_pending,
        "total_fees": f"{summary['total_fees']:.2f}",
        # show how much of the sem's fee is covered:
        "total_paid": f"{summary['effective_paid_for_sem']:.2f}",
        "pendingamount": f"{summary['pending']:.2f}",
        # remaining advance to carry to next sem
        "advance_amount": f"{summary['advance']:.2f}",
        "source": "current_semyear",
    }

    return Response(response_data, status=status.HTTP_200_OK)


# API 1: name OR mobile OR enrollment_id  -> LIST
# --------------------------
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def search_students_by_any(request):
#     """
#     GET /api/students/search-any/?q=<text>&limit=50&offset=0
#     Single input `q` matched against:
#       - name (icontains)
#       - mobile (icontains)
#       - enrollment_id (icontains)
#     Returns: LIST of {id, name, mobile, email, enrollment_id, registration_id, is_enrolled}
#     """
#     q = (request.GET.get("q") or "").strip()
#     if not q:
#         return Response({"error": "Provide q"}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         limit = int(request.GET.get("limit", 50))
#     except ValueError:
#         limit = 50
#     try:
#         offset = int(request.GET.get("offset", 0))
#     except ValueError:
#         offset = 0

#     filters = (
#         Q(name__icontains=q) |
#         Q(mobile__icontains=q) |
#         Q(enrollment_id__icontains=q)
#     )

#     qs = (
#         Student.objects
#         .filter(filters)
#         .order_by("name", "enrollment_id")
#         .values("id", "name", "mobile", "email", "enrollment_id", "registration_id", "is_enrolled")
#     )

#     data = list(qs[offset:offset + limit])
#     return Response(data, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_students_by_any(request):
    """
    GET /api/students/search-any/?q=<text>&limit=50&offset=0
    Matches input `q` against:
      - name
      - mobile
      - enrollment_id

    Returns the SAME structure as the table:
      [
        {
          "id": <int>,
          "user_id": <int|null>,
          "current_semyear": "<str>",
          "total_semyear": "<str>",
          "enrollment_id": "<str>",
          "student_name": "<str>",
          "university_name": "<str>",
          "source": "SR|QR",
          "study_pattern_mode": "<str>",
          "entry_mode": "<str>",
          "enrollment_date": "YYYY-MM-DD"
        }, ...
      ]
    """
    q = (request.GET.get("q") or "").strip()
    if not q:
        return Response({"error": "Provide q"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        limit = int(request.GET.get("limit", 50))
    except ValueError:
        limit = 50
    try:
        offset = int(request.GET.get("offset", 0))
    except ValueError:
        offset = 0

    # build filter for search term
    filters = (
        Q(name__icontains=q) |
        Q(mobile__icontains=q) |
        Q(enrollment_id__icontains=q)
    )

    # subquery to get latest enrolled info
    latest_enrolled = Enrolled.objects.filter(student_id=OuterRef('pk')).order_by('-id')

    # main queryset
    students = (
        Student.objects
        .filter(filters, archive=False)
        .select_related('university', 'user')
        .annotate(
            ann_current_semyear=Subquery(latest_enrolled.values('current_semyear')[:1]),
            ann_total_semyear=Subquery(latest_enrolled.values('total_semyear')[:1]),
            ann_entry_mode=Subquery(latest_enrolled.values('entry_mode')[:1]),
            ann_course_pattern=Subquery(latest_enrolled.values('course_pattern')[:1]),
        )
        .order_by('name', 'enrollment_id')
    )

    # prepare data for frontend table
    data = []
    for s in students[offset:offset + limit]:
        source = "QR" if getattr(s, "is_quick_register", False) else "SR"
        data.append({
            "id": s.id,
            "user_id": s.user.id if s.user else None,
            "current_semyear": s.ann_current_semyear or "",
            "total_semyear": s.ann_total_semyear or "",
            "enrollment_id": s.enrollment_id or "",
            "student_name": s.name or "",
            "university_name": getattr(s.university, "university_name", "") if s.university else "",
            "source": source,
            "study_pattern_mode": s.ann_course_pattern or "",
            "entry_mode": s.ann_entry_mode or "",
            "enrollment_date": s.enrollment_date.strftime("%Y-%m-%d") if s.enrollment_date else "",
            "mobile": s.mobile or "",
            "email": s.email or "",
            "registration_id": s.registration_id or "",
        })

    return Response(data, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_students_by_any_quick(request):
    """
    GET /api/students/search-any/?q=<text>&limit=50&offset=0
    Matches input `q` against:
      - name
      - mobile
      - enrollment_id

    Returns the SAME structure as the table:
      [
        {
          "id": <int>,
          "user_id": <int|null>,
          "current_semyear": "<str>",
          "total_semyear": "<str>",
          "enrollment_id": "<str>",
          "student_name": "<str>",
          "university_name": "<str>",
          "source": "SR|QR",
          "study_pattern_mode": "<str>",
          "entry_mode": "<str>",
          "enrollment_date": "YYYY-MM-DD"
        }, ...
      ]
    """
    q = (request.GET.get("q") or "").strip()
    if not q:
        return Response({"error": "Provide q"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        limit = int(request.GET.get("limit", 50))
    except ValueError:
        limit = 50
    try:
        offset = int(request.GET.get("offset", 0))
    except ValueError:
        offset = 0

    # build filter for search term
    filters = (
        Q(name__icontains=q) |
        Q(mobile__icontains=q) |
        Q(enrollment_id__icontains=q)
    )

    # subquery to get latest enrolled info
    latest_enrolled = Enrolled.objects.filter(student_id=OuterRef('pk')).order_by('-id')

    # main queryset
    students = (
        Student.objects
        .filter(filters, archive=False,is_quick_register=True, is_cancelled=False)
        .select_related('university', 'user')
        .annotate(
            ann_current_semyear=Subquery(latest_enrolled.values('current_semyear')[:1]),
            ann_total_semyear=Subquery(latest_enrolled.values('total_semyear')[:1]),
            ann_entry_mode=Subquery(latest_enrolled.values('entry_mode')[:1]),
            ann_course_pattern=Subquery(latest_enrolled.values('course_pattern')[:1]),
        )
        .order_by('name', 'enrollment_id')
    )

    # prepare data for frontend table
    data = []
    for s in students[offset:offset + limit]:
        source = "QR" if getattr(s, "is_quick_register", False) else "SR"
        data.append({
            "id": s.id,
            "user_id": s.user.id if s.user else None,
            "current_semyear": s.ann_current_semyear or "",
            "total_semyear": s.ann_total_semyear or "",
            "enrollment_id": s.enrollment_id or "",
            "student_name": s.name or "",
            "university_name": getattr(s.university, "university_name", "") if s.university else "",
            "source": source,
            "study_pattern_mode": s.ann_course_pattern or "",
            "entry_mode": s.ann_entry_mode or "",
            "enrollment_date": s.enrollment_date.strftime("%Y-%m-%d") if s.enrollment_date else "",
            "mobile": s.mobile or "",
            "email": s.email or "",
            "registration_id": s.registration_id or "",
        })

    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_students_by_any_register(request):
    """
    GET /api/students/search-any/?q=<text>&limit=50&offset=0
    Matches input `q` against:
      - name
      - mobile
      - enrollment_id

    Returns the SAME structure as the table:
      [
        {
          "id": <int>,
          "user_id": <int|null>,
          "current_semyear": "<str>",
          "total_semyear": "<str>",
          "enrollment_id": "<str>",
          "student_name": "<str>",
          "university_name": "<str>",
          "source": "SR|QR",
          "study_pattern_mode": "<str>",
          "entry_mode": "<str>",
          "enrollment_date": "YYYY-MM-DD"
        }, ...
      ]
    """
    q = (request.GET.get("q") or "").strip()
    if not q:
        return Response({"error": "Provide q"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        limit = int(request.GET.get("limit", 50))
    except ValueError:
        limit = 50
    try:
        offset = int(request.GET.get("offset", 0))
    except ValueError:
        offset = 0

    # build filter for search term
    filters = (
        Q(name__icontains=q) |
        Q(mobile__icontains=q) |
        Q(enrollment_id__icontains=q)
    )

    # subquery to get latest enrolled info
    latest_enrolled = Enrolled.objects.filter(student_id=OuterRef('pk')).order_by('-id')

    # main queryset
    students = (
        Student.objects
        .filter(filters, archive=False,is_quick_register=False, is_cancelled=False)
        .select_related('university', 'user')
        .annotate(
            ann_current_semyear=Subquery(latest_enrolled.values('current_semyear')[:1]),
            ann_total_semyear=Subquery(latest_enrolled.values('total_semyear')[:1]),
            ann_entry_mode=Subquery(latest_enrolled.values('entry_mode')[:1]),
            ann_course_pattern=Subquery(latest_enrolled.values('course_pattern')[:1]),
        )
        .order_by('name', 'enrollment_id')
    )

    # prepare data for frontend table
    data = []
    for s in students[offset:offset + limit]:
        source = "QR" if getattr(s, "is_quick_register", False) else "SR"
        data.append({
            "id": s.id,
            "user_id": s.user.id if s.user else None,
            "current_semyear": s.ann_current_semyear or "",
            "total_semyear": s.ann_total_semyear or "",
            "enrollment_id": s.enrollment_id or "",
            "student_name": s.name or "",
            "university_name": getattr(s.university, "university_name", "") if s.university else "",
            "source": source,
            "study_pattern_mode": s.ann_course_pattern or "",
            "entry_mode": s.ann_entry_mode or "",
            "enrollment_date": s.enrollment_date.strftime("%Y-%m-%d") if s.enrollment_date else "",
            "mobile": s.mobile or "",
            "email": s.email or "",
            "registration_id": s.registration_id or "",
        })

    return Response(data, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def lookup_student_by_q_with_university(request):
    """
    GET /api/students/search-any/?q=<text>&limit=50&offset=0
    Matches input `q` against:
      - name
      - mobile
      - enrollment_id

    Returns the SAME structure as the table:
      [
        {
          "id": <int>,
          "user_id": <int|null>,
          "current_semyear": "<str>",
          "total_semyear": "<str>",
          "enrollment_id": "<str>",
          "student_name": "<str>",
          "university_name": "<str>",
          "source": "SR|QR",
          "study_pattern_mode": "<str>",
          "entry_mode": "<str>",
          "enrollment_date": "YYYY-MM-DD"
        }, ...
      ]
    """
    q = (request.GET.get("q") or "").strip()
    if not q:
        return Response({"error": "Provide q"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        limit = int(request.GET.get("limit", 50))
    except ValueError:
        limit = 50
    try:
        offset = int(request.GET.get("offset", 0))
    except ValueError:
        offset = 0
        
    uni_filter = Q(university__university_name__icontains=q)
    # build filter for search term
    filters = (
        Q(name__icontains=q) |
        Q(enrollment_id__icontains=q)|
        uni_filter
    )

    # subquery to get latest enrolled info
    latest_enrolled = Enrolled.objects.filter(student_id=OuterRef('pk')).order_by('-id')

    # main queryset
    students = (
        Student.objects
        .filter(filters, archive=False)
        .select_related('university', 'user')
        .annotate(
            ann_current_semyear=Subquery(latest_enrolled.values('current_semyear')[:1]),
            ann_total_semyear=Subquery(latest_enrolled.values('total_semyear')[:1]),
            ann_entry_mode=Subquery(latest_enrolled.values('entry_mode')[:1]),
            ann_course_pattern=Subquery(latest_enrolled.values('course_pattern')[:1]),
        )
        .order_by('name', 'enrollment_id')
    )

    # prepare data for frontend table
    data = []
    for s in students[offset:offset + limit]:
        source = "QR" if getattr(s, "is_quick_register", False) else "SR"
        data.append({
            "id": s.id,
            "user_id": s.user.id if s.user else None,
            "current_semyear": s.ann_current_semyear or "",
            "total_semyear": s.ann_total_semyear or "",
            "enrollment_id": s.enrollment_id or "",
            "student_name": s.name or "",
            "university_name": getattr(s.university, "university_name", "") if s.university else "",
            "source": source,
            "study_pattern_mode": s.ann_course_pattern or "",
            "entry_mode": s.ann_entry_mode or "",
            "enrollment_date": s.enrollment_date.strftime("%Y-%m-%d") if s.enrollment_date else "",
            "mobile": s.mobile or "",
            "email": s.email or "",
            "registration_id": s.registration_id or "",
        })

    return Response(data, status=status.HTTP_200_OK)




@api_view(["GET"])
@permission_classes([IsAuthenticated])
def result_report_grouped(request):
    """
    GET /api/exams/result-report-grouped
    Required query params:
      - university (id)
      - course (id)
      - stream (id)
      - studypattern (string, e.g., 'Semester' or 'Yearly')
      - semyear (string, e.g., '1', '2', '2024-25', etc.)
    Optional:
      - substream (id)

    Returns grouped student results with:
      - stream_name
      - substream_name
      - university_name
      - course_name
      - father_or_husband_name
    """
    qp = request.query_params
    university_id = qp.get("university")
    course_id = qp.get("course")
    stream_id = qp.get("stream")
    substream_id = qp.get("substream")  # optional
    studypattern = qp.get("studypattern")
    semyear = qp.get("semyear")

    missing = [k for k, v in {
        "university": university_id,
        "course": course_id,
        "stream": stream_id,
        "studypattern": studypattern,
        "semyear": semyear,
    }.items() if not v]
    if missing:
        return Response(
            {"detail": f"Missing required query params: {', '.join(missing)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    filters = {
        "exam__university_id": university_id,
        "exam__course_id": course_id,
        "exam__stream_id": stream_id,
        "exam__studypattern": studypattern,
        "exam__semyear": semyear,
        "exam__active": True,
        "exam__archive": False,
    }
    if substream_id:
        filters["exam__substream_id"] = substream_id

    # Include stream/substream names
    qs = (
        Result.objects
        .select_related(
            "student",
            "exam",
            "exam__subject",
            "exam__course",
            "exam__university",
            "exam__stream",
            "exam__substream",
        )
        .filter(**filters)
        .values(
            "student_id",
            "student__name",
            "student__father_name",
            "student__enrollment_id",
            "exam__semyear",
            "exam__subject__name",
            "exam__subject__code",
            "exam__totalmarks",
            "exam__totalquestions",
            "exam__university__university_name",
            "exam__course__name",
            "exam__stream__name",
            "exam__substream__name",
            "score",
        )
        .order_by("student__name", "exam__subject__name")
    )

    grouped = {}

    def to_float(v, default=0.0):
        try:
            return float(v) if v not in (None, "") else default
        except (ValueError, TypeError):
            return default

    def to_int(v, default=None):
        try:
            return int(v) if v not in (None, "") else default
        except (ValueError, TypeError):
            return default

    for row in qs:
        sid = row["student_id"]
        if sid not in grouped:
            grouped[sid] = {
                "student_name": row["student__name"],
                "father_or_husband_name": row.get("student__father_name"),
                "stream_name": row.get("exam__stream__name") or "",
                "substream_name": row.get("exam__substream__name") or "",
                "enrollment_no": row["student__enrollment_id"],
                "semyear": row["exam__semyear"],
                "university_name": row.get("exam__university__university_name"),
                "course_name": row.get("exam__course__name"),
                "subjects": [],
                "total_obtained": 0.0,
                "total_max": 0.0,
            }

        max_marks = to_float(row["exam__totalmarks"])
        total_questions = to_int(row["exam__totalquestions"])
        marks_obtained = to_float(row["score"])

        grouped[sid]["subjects"].append({
            "subject_name": row["exam__subject__name"],
            "subject_code": row.get("exam__subject__code") or "",
            "max_marks": max_marks,
            "total_questions": total_questions,
            "marks_obtained": marks_obtained,
        })
        grouped[sid]["total_obtained"] += marks_obtained
        grouped[sid]["total_max"] += max_marks

    data = list(grouped.values())
    return Response({"count": len(data), "results": data}, status=status.HTTP_200_OK)


from super_admin.services.receipts import generate_receipt_pdf, email_payment_receipt

def _sanitize_receipt_id(raw):
    """Return int id if valid; otherwise None for None / '' / 'null' / 'None' / bad values."""
    if raw is None:
        return None
    if isinstance(raw, str):
        s = raw.strip().lower()
        if s in ("", "null", "none"):
            return None
        try:
            return int(s)
        except ValueError:
            return None
    try:
        return int(raw)
    except Exception:
        return None

@api_view(["POST"])
def create_payment_receipt_edit(request):
    start_ts = timezone.now()
    body = request.data

    # ----- Required fields
    student_id = body.get("student_id")
    semyear = body.get("semyear")
    paidamount_in = body.get("paidamount", 0)
    receipt_id = body.get("id")  # Get the receipt ID from request

    print(f"DEBUG: Received receipt_id: {receipt_id}, type: {type(receipt_id)}")
    print(f"DEBUG: student_id: {student_id}, semyear: {semyear}, paidamount: {paidamount_in}")

    if not student_id:
        return Response({"error": "student_id is required."}, status=400)
    if not semyear:
        return Response({"error": "semyear is required."}, status=400)
    if paidamount_in is None:
        return Response({"error": "paidamount is required."}, status=400)

    try:
        # ----- Load student
        student = Student.objects.get(id=int(student_id))
        print(f"DEBUG: Found student: {student.name}")
    except (Student.DoesNotExist, ValueError):
        return Response({"error": "Student not found."}, status=404)

    try:
        # ----- Check if payment receipt already exists by ID
        existing_receipt = None
        
        # ✅ PROPERLY CHECK IF RECEIPT ID EXISTS AND IS VALID
        # Check if receipt_id is provided and is a valid integer (not null, "null", empty, etc.)
        if receipt_id is not None and receipt_id != "null" and receipt_id != "":
            try:
                # Convert to integer and try to find the receipt
                receipt_id_int = int(receipt_id)
                existing_receipt = PaymentReciept.objects.get(id=receipt_id_int)
                print(f"DEBUG: Found existing receipt ID: {existing_receipt.id}")
                logger.info(
                    "[payment.send_existing] Found existing receipt ID=%s student_id=%s semyear=%s txid=%s",
                    existing_receipt.id, student.id, semyear, existing_receipt.transactionID
                )
            except (PaymentReciept.DoesNotExist, ValueError, TypeError):
                existing_receipt = None
                print(f"DEBUG: No existing receipt found with ID={receipt_id}, will create new one")
                logger.info(
                    "[payment.create_new] No existing receipt found with ID=%s, creating new one",
                    receipt_id
                )
        else:
            print(f"DEBUG: receipt_id is null/empty, will create new receipt")

        if existing_receipt:
            # ----- CASE 1: Receipt already exists, just send the email
            print("DEBUG: Processing existing receipt - sending email only")
            try:
                # Generate PDF for existing receipt
                pdf_bytes = generate_receipt_pdf(student, existing_receipt)
                # Send email with the receipt attached
                email_payment_receipt(student, existing_receipt, pdf_bytes)
                emailed = True
                logger.info(f"Existing payment receipt sent to {student.email}")
            except Exception as mail_err:
                logger.exception(f"Failed to email existing receipt PDF: {mail_err}")
                emailed = False

            # ----- Response for existing receipt
            resp = {
                "id": existing_receipt.id,
                "student": existing_receipt.student_id,
                "transactionID": existing_receipt.transactionID,
                "fee_reciept_type": existing_receipt.fee_reciept_type,
                "transaction_date": existing_receipt.transaction_date,
                "payment_mode": existing_receipt.paymentmode,
                "cheque_no": existing_receipt.cheque_no,
                "bank_name": existing_receipt.bank_name,
                "payment_transaction_id": existing_receipt.payment_transactionID,
                "remarks": existing_receipt.remarks,
                "session": existing_receipt.session,
                "semyear": existing_receipt.semyear,
                "status": existing_receipt.status,
                "semyearfees": existing_receipt.semyearfees,
                "paidamount": existing_receipt.paidamount,
                "pendingamount": existing_receipt.pendingamount,
                "advanceamount": existing_receipt.advanceamount,
                "uncleared_amount": existing_receipt.uncleared_amount,
                "action": "email_sent",  # Indicate that only email was sent
                "message": "Existing receipt found, email sent successfully"
            }

            return Response(resp, status=status.HTTP_200_OK)

        else:
            # ----- CASE 2: Create new payment receipt (ID is null or invalid)
            print("DEBUG: Creating new payment receipt")
            
            # ----- Fetch total fees from StudentFees for the student and corresponding semyear
            student_fees = StudentFees.objects.filter(student=student, sem=semyear).first()
            if not student_fees:
                print(f"DEBUG: No fees record found for student {student_id} and semyear {semyear}")
                return Response({"error": "Fees record not found for this student and semyear."}, status=404)

            # Get the total fees
            total_fees = Decimal(student_fees.totalfees)
            print(f"DEBUG: Total fees: {total_fees}")
            
            if total_fees <= 0:
                return Response({"error": "Total fees must be greater than 0."}, status=400)

            # ----- Convert paidamount from request to Decimal
            paidamount = Decimal(paidamount_in)

            if paidamount < 0:
                return Response({"error": "Paid amount must be >= 0."}, status=400)

            # ----- Generate the next transaction ID
            latest = PaymentReciept.objects.order_by("-id").first()
            prefix, start_from = "TXT445FE", 100
            if latest and isinstance(latest.transactionID, str) and latest.transactionID.startswith(prefix):
                try:
                    last_num = int(latest.transactionID.replace(prefix, ""))
                except ValueError:
                    last_num = start_from
            else:
                last_num = start_from
            transaction_id = f"{prefix}{last_num + 1}"

            # ----- Sum all previous payments for this student and semyear to calculate pending and advance
            past_qs = PaymentReciept.objects.filter(student=student, semyear=semyear)
            past_sum = Decimal("0")
            for p in past_qs:
                past_sum += Decimal(p.paidamount)

            cumulative_paid = past_sum + paidamount

            # ✅ FIXED: Calculate pending amount - NEVER GO BELOW 0
            # If pending amount is negative (overpayment), set it to 0
            pending_amount = max(total_fees - cumulative_paid, Decimal("0"))
            
            # ✅ FIXED: Calculate advance amount - ONLY POSITIVE VALUES
            # If cumulative paid exceeds total fees, that's the advance amount
            advance_amount = max(cumulative_paid - total_fees, Decimal("0"))
            
            payment_type = "Full Payment" if pending_amount == 0 else "Part Payment"
            if advance_amount > 0:
              payment_type = "Advance Payment"
            

            # ----- Set status (if not provided, deduced from pending/advance)
            status_in = body.get("status", "").strip()
            if status_in:
                status_val = status_in
            else:
                if pending_amount == 0 and advance_amount == 0:
                    status_val = "Paid"
                elif pending_amount > 0:
                    status_val = "Partial"
                else:
                    status_val = "Advance"

            # ----- Create the PaymentReciept entry
            receipt_data = {
                "student": student,
                "fee_reciept_type": body.get("fee_recipt_type", ""),
                "payment_for":"Course Fees",
                "payment_categories": "New",
                "payment_type": payment_type,
                "transaction_date": body.get("transaction_date", ""),
                "cheque_no": body.get("cheque_no", ""),
                "bank_name": body.get("bank_name", ""),
                "semyearfees": str(total_fees),
                "paidamount": str(paidamount),
                "pendingamount": str(pending_amount),  # ✅ This will never be negative
                "advanceamount": str(advance_amount),  # ✅ This will never be negative
                "transactionID": transaction_id,
                "payment_transactionID": body.get("payment_transaction_id", ""),
                "paymentmode": body.get("payment_mode", "Online"),
                "remarks": body.get("remarks", ""),
                "session": body.get("session", ""),
                "semyear": semyear,
                "status": "Realised",
                "uncleared_amount": body.get("uncleared_amount", ""),
                "created_by": request.user.email if request.user else "system",
                "modified_by": request.user.email if request.user else "system",
            }
            
            
            receipt = PaymentReciept.objects.create(**receipt_data)

            # ----- Generate PDF for receipt and send email
            try:
                pdf_bytes = generate_receipt_pdf(student, receipt)
                email_payment_receipt(student, receipt, pdf_bytes)
                emailed = True
                logger.info(f"New payment receipt created and sent to {student.email}")
            except Exception as mail_err:
                logger.exception(f"Failed to email new receipt PDF: {mail_err}")
                emailed = False

            # ----- Response for new receipt
            resp = {
                "id": receipt.id,
                "student": receipt.student_id,
                "transactionID": receipt.transactionID,
                "fee_reciept_type": receipt.fee_reciept_type,
                "transaction_date": receipt.transaction_date,
                "payment_mode": receipt.paymentmode,
                "cheque_no": receipt.cheque_no,
                "bank_name": receipt.bank_name,
                "payment_transaction_id": receipt.payment_transactionID,
                "remarks": receipt.remarks,
                "session": receipt.session,
                "semyear": receipt.semyear,
                "status": receipt.status,
                "semyearfees": receipt.semyearfees,
                "paidamount": receipt.paidamount,
                "pendingamount": receipt.pendingamount,
                "advanceamount": receipt.advanceamount,
                "uncleared_amount": receipt.uncleared_amount,
                "cumulative_paid": str(cumulative_paid),
                "action": "created_and_emailed",  # Indicate that new receipt was created and emailed
                "message": "New receipt created and email sent successfully"
            }

            # ----- Log the successful transaction creation
            logger.info(
                "[payment.create] OK student_id=%s semyear=%s txid=%s paid=%s total=%s pending=%s advance=%s",
                student.id, receipt.semyear, receipt.transactionID,
                receipt.paidamount, receipt.semyearfees, receipt.pendingamount, receipt.advanceamount
            )

            return Response(resp, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.exception(
            "[payment.create] ERROR student_id=%s semyear=%s",
            student_id, semyear
        )
        return Response({"error": "Failed to create payment receipt.", "detail": str(e)}, status=500)
      
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_student_pending(request, student_id: int):
    """
    POST /api/students/<student_id>/mark-pending-fbv/

    Logic:
      - Find student's current semyear (latest Enrolled.current_semyear)
      - Get StudentFees.totalfees for that semyear
      - Sum PaymentReciept.paidamount for (student, semyear)
      - If sum >= totalfees, set Student.is_pending = True
    """
    request_id = request.headers.get("X-Request-ID")

    # 1) Student
    student = get_object_or_404(Student, pk=student_id)

    # 2) Current semyear
    enrolled = Enrolled.objects.filter(student=student).order_by("-id").first()
    if not enrolled:
        logger.info(
            "mark_student_pending_denied",
            extra={"custom": {
                "event": "mark_student_pending_fbv",
                "reason": "no_enrollment",
                "student_id": student.id,
                "request_id": request_id,
            }}
        )
        return Response(
            {"success": False, "message": "No enrollment record found.", "data": {"student_id": student.id}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    current_sem = (enrolled.current_semyear or "").strip()
    if not current_sem:
        logger.info(
            "mark_student_pending_denied",
            extra={"custom": {
                "event": "mark_student_pending_fbv",
                "reason": "empty_current_semyear",
                "student_id": student.id,
                "request_id": request_id,
            }}
        )
        return Response(
            {"success": False, "message": "Current semyear is not set for the student.", "data": {"student_id": student.id}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 3) Fee schedule (StudentFees.totalfees is CharField)
    fee = StudentFees.objects.filter(student=student, sem=current_sem).order_by("-id").first()
    if not fee or not (fee.totalfees or "").strip():
        logger.info(
            "mark_student_pending_denied",
            extra={"custom": {
                "event": "mark_student_pending_fbv",
                "reason": "no_fee_schedule",
                "student_id": student.id,
                "current_sem": current_sem,
                "request_id": request_id,
            }}
        )
        return Response(
            {"success": False, "message": "No fee schedule (totalfees) for current semyear.", "data": {"student_id": student.id, "current_semyear": current_sem}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        required_total = Decimal(fee.totalfees.strip())
    except (InvalidOperation, AttributeError):
        logger.info(
            "mark_student_pending_denied",
            extra={"custom": {
                "event": "mark_student_pending_fbv",
                "reason": "invalid_totalfees",
                "student_id": student.id,
                "current_sem": current_sem,
                "totalfees": fee.totalfees,
                "request_id": request_id,
            }}
        )
        return Response(
            {"success": False, "message": "Invalid totalfees in StudentFees.", "data": {"student_id": student.id, "current_semyear": current_sem, "totalfees": fee.totalfees}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 4) Sum PaymentReciept.paidamount for same (student, semyear)
    total_paid = Decimal("0")
    for r in PaymentReciept.objects.filter(student=student, semyear=current_sem):
        try:
            total_paid += Decimal((r.paidamount or "0").strip())
        except (InvalidOperation, AttributeError):
            # treat bad values as 0; alternatively, you could reject here
            continue

    # 5) Compare and update
    if required_total > 0 and total_paid >= required_total:
        with transaction.atomic():
            student.is_pending = True
            student.save(update_fields=["is_pending"])

        logger.info(
            "mark_student_pending_success",
            extra={"custom": {
                "event": "mark_student_pending_fbv",
                "student_id": student.id,
                "current_sem": current_sem,
                "required_total": str(required_total),
                "total_paid": str(total_paid),
                "new_is_pending": student.is_pending,
                "user_id": getattr(request.user, "id", None),
                "request_id": request_id,
            }}
        )
        return Response(
            {
                "success": True,
                "message": "Student marked as pending successfully.",
                "data": {
                    "student_id": student.id,
                    "name": student.name,
                    "enrollment_id": student.enrollment_id,
                    "current_semyear": current_sem,
                    "required_total": str(required_total),
                    "total_paid": str(total_paid),
                    "is_pending": True,
                },
            },
            status=status.HTTP_200_OK,
        )

    # Not fully paid
    logger.info(
        "mark_student_pending_denied",
        extra={"custom": {
            "event": "mark_student_pending_fbv",
            "reason": "outstanding_dues",
            "student_id": student.id,
            "current_sem": current_sem,
            "required_total": str(required_total),
            "total_paid": str(total_paid),
            "user_id": getattr(request.user, "id", None),
            "request_id": request_id,
        }}
    )
    return Response(
        {
            "success": False,
            "message": "Outstanding dues for current semyear.",
            "data": {
                "student_id": student.id,
                "current_semyear": current_sem,
                "required_total": str(required_total),
                "total_paid": str(total_paid),
            },
        },
        status=status.HTTP_400_BAD_REQUEST,
    ) 


#29-10-2025

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_student_pending(request, student_id: int):
    """
    POST /api/students/<student_id>/mark-pending-fbv/

    Logic:
      - Super Admin: Can directly mark as pending without checks
      - Other Users: Check fee payment status before allowing
    """
    request_id = request.headers.get("X-Request-ID")
    is_super_admin = request.user.is_superuser

    # 1) Student
    student = get_object_or_404(Student, pk=student_id)

    # Super Admin bypasses all checks
    if is_super_admin:
        with transaction.atomic():
            student.is_pending = True
            student.save(update_fields=["is_pending"])

        logger.info(
            "mark_student_pending_success",
            extra={"custom": {
                "event": "mark_student_pending_fbv",
                "student_id": student.id,
                "user_id": request.user.id,
                "user_type": "super_admin",
                "new_is_pending": student.is_pending,
                "request_id": request_id,
            }}
        )
        return Response(
            {
                "success": True,
                "message": "Student marked as pending successfully (Super Admin override).",
                "data": {
                    "student_id": student.id,
                    "name": student.name,
                    "enrollment_id": student.enrollment_id,
                    "is_pending": True,
                    "bypass_reason": "super_admin_override",
                },
            },
            status=status.HTTP_200_OK,
        )

    # For regular users - perform fee validation checks
    # 2) Current semyear
    enrolled = Enrolled.objects.filter(student=student).order_by("-id").first()
    if not enrolled:
        logger.info(
            "mark_student_pending_denied",
            extra={"custom": {
                "event": "mark_student_pending_fbv",
                "reason": "no_enrollment",
                "student_id": student.id,
                "user_id": request.user.id,
                "user_type": "regular_user",
                "request_id": request_id,
            }}
        )
        return Response(
            {"success": False, "message": "No enrollment record found.", "data": {"student_id": student.id}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    current_sem = (enrolled.current_semyear or "").strip()
    if not current_sem:
        logger.info(
            "mark_student_pending_denied",
            extra={"custom": {
                "event": "mark_student_pending_fbv",
                "reason": "empty_current_semyear",
                "student_id": student.id,
                "user_id": request.user.id,
                "user_type": "regular_user",
                "request_id": request_id,
            }}
        )
        return Response(
            {"success": False, "message": "Current semyear is not set for the student.", "data": {"student_id": student.id}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 3) Fee schedule (StudentFees.totalfees is CharField)
    fee = StudentFees.objects.filter(student=student, sem=current_sem).order_by("-id").first()
    if not fee or not (fee.totalfees or "").strip():
        logger.info(
            "mark_student_pending_denied",
            extra={"custom": {
                "event": "mark_student_pending_fbv",
                "reason": "no_fee_schedule",
                "student_id": student.id,
                "current_sem": current_sem,
                "user_id": request.user.id,
                "user_type": "regular_user",
                "request_id": request_id,
            }}
        )
        return Response(
            {"success": False, "message": "No fee schedule (totalfees) for current semyear.", "data": {"student_id": student.id, "current_semyear": current_sem}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        required_total = Decimal(fee.totalfees.strip())
    except (InvalidOperation, AttributeError):
        logger.info(
            "mark_student_pending_denied",
            extra={"custom": {
                "event": "mark_student_pending_fbv",
                "reason": "invalid_totalfees",
                "student_id": student.id,
                "current_sem": current_sem,
                "totalfees": fee.totalfees,
                "user_id": request.user.id,
                "user_type": "regular_user",
                "request_id": request_id,
            }}
        )
        return Response(
            {"success": False, "message": "Invalid totalfees in StudentFees.", "data": {"student_id": student.id, "current_semyear": current_sem, "totalfees": fee.totalfees}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 4) Sum PaymentReciept.paidamount for same (student, semyear)
    total_paid = Decimal("0")
    for r in PaymentReciept.objects.filter(student=student, semyear=current_sem):
        try:
            total_paid += Decimal((r.paidamount or "0").strip())
        except (InvalidOperation, AttributeError):
            continue

    # 5) Compare and update (only if fees are fully paid for regular users)
    if required_total > 0 and total_paid >= required_total:
        with transaction.atomic():
            student.is_pending = True
            student.save(update_fields=["is_pending"])

        logger.info(
            "mark_student_pending_success",
            extra={"custom": {
                "event": "mark_student_pending_fbv",
                "student_id": student.id,
                "current_sem": current_sem,
                "required_total": str(required_total),
                "total_paid": str(total_paid),
                "new_is_pending": student.is_pending,
                "user_id": request.user.id,
                "user_type": "regular_user",
                "request_id": request_id,
            }}
        )
        return Response(
            {
                "success": True,
                "message": "Student marked as pending successfully.",
                "data": {
                    "student_id": student.id,
                    "name": student.name,
                    "enrollment_id": student.enrollment_id,
                    "current_semyear": current_sem,
                    "required_total": str(required_total),
                    "total_paid": str(total_paid),
                    "is_pending": True,
                },
            },
            status=status.HTTP_200_OK,
        )

    # Not fully paid - regular user cannot mark as pending
    logger.info(
        "mark_student_pending_denied",
        extra={"custom": {
            "event": "mark_student_pending_fbv",
            "reason": "outstanding_dues",
            "student_id": student.id,
            "current_sem": current_sem,
            "required_total": str(required_total),
            "total_paid": str(total_paid),
            "user_id": request.user.id,
            "user_type": "regular_user",
            "request_id": request_id,
        }}
    )
    return Response(
        {
            "success": False,
            "message": "Outstanding dues for current semyear. Cannot mark as pending.",
            "data": {
                "student_id": student.id,
                "current_semyear": current_sem,
                "required_total": str(required_total),
                "total_paid": str(total_paid),
                "outstanding_amount": str(required_total - total_paid),
            },
        },
        status=status.HTTP_400_BAD_REQUEST,
    )

@api_view(['GET'])
def pending_verification_student(request):
    students = Student.objects.filter(is_quick_register=True, is_pending=True)
    serializer = StudentSerializer(students, many=True)
    return Response(serializer.data)
  
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_student(request, student_id):
    """
    API endpoint to approve a student (superadmin only)
    Sets is_approve=True and is_pending=False
    """
    try:
        # Check if user is superadmin
        if not request.user.is_superuser:
            return Response({
                'success': False,
                'error': 'PERMISSION_DENIED',
                'message': 'Only superadmin users can approve students.'
            }, status=status.HTTP_403_FORBIDDEN)

        # Get student object
        student = Student.objects.get(id=student_id)
        
        # Check if student is already approved
        if student.is_approve:
            return Response({
                'success': False,
                'error': 'ALREADY_APPROVED',
                'message': 'Student is already approved.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if student is pending
        if not student.is_pending:
            return Response({
                'success': False,
                'error': 'NOT_PENDING',
                'message': 'Student is not in pending status.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update approval status
        student.is_approve = True
        student.is_pending = False
        student.modified_by = request.user.username
        student.save()
        
        return Response({
            'success': True,
            'message': f'Student {student.name} has been approved successfully.',
            'student': {
                'id': student.id,
                'name': student.name,
                'enrollment_id': student.enrollment_id,
                'email': student.email,
                'is_approve': student.is_approve,
                'is_pending': student.is_pending,
                'approved_by': request.user.username,
                'approved_at': student.updated_at.isoformat() if hasattr(student, 'updated_at') else None
            }
        }, status=status.HTTP_200_OK)
        
    except Student.DoesNotExist:
        return Response({
            'success': False,
            'error': 'STUDENT_NOT_FOUND',
            'message': 'Student not found with the provided ID.'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': 'SERVER_ERROR',
            'message': f'An error occurred while approving the student: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_username_or_email(user):
    """Return username or fallback to email."""
    return user.username if getattr(user, "username", None) else getattr(user, "email", "Unknown")
        
import re
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])   # <-- important for file uploads
def create_additional_receipt(request):
    # DO NOT copy request.data (it can contain UploadedFile / BufferedRandom)
    user_identifier = get_username_or_email(request.user)

    # generate next transactionID safely
    PREFIX = "ADD-TXT445FE"
    base_num = 100
    try:
        latest_receipt = Additional_PaymentReciept.objects.latest("id")
        m = re.search(r'(\d+)$', (latest_receipt.transactionID or ""))
        last_num = int(m.group(1)) if m else base_num
    except Additional_PaymentReciept.DoesNotExist:
        last_num = base_num

    transaction_id = f"{PREFIX}{last_num + 1}"

    # Initialize serializer directly with request.data (let DRF bind request.FILES automatically)
    serializer = AdditionalPaymentReceiptSerializer(data=request.data)

    if serializer.is_valid():
        with transaction.atomic():
            instance = serializer.save(
                # server-side fields
                transactionID=transaction_id,
                created_by=user_identifier,
                modified_by=user_identifier,
                # if you want to force-save the uploaded file with a specific key name:
                # uploaded_file=request.FILES.get('uploaded_file'),       # for generic files
                # receipt_image=request.FILES.get('receipt_image'),       # if you also added an ImageField
            )
        return Response(
            {"message": "Receipt created successfully",
             "data": AdditionalPaymentReceiptSerializer(instance).data},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ VIEW all or filter by student ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_additional_receipts(request):
    student_id = request.GET.get('student_id')
    if student_id:
        receipts = Additional_PaymentReciept.objects.filter(student_id=student_id).order_by('id')
    else:
        receipts = Additional_PaymentReciept.objects.all().order_by('-transactiontime')

    serializer = AdditionalPaymentReceiptSerializer(receipts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_additional_receipt(request, pk):
    try:
        receipt = Additional_PaymentReciept.objects.get(pk=pk)
    except Additional_PaymentReciept.DoesNotExist:
        return Response({"error": "Receipt not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = AdditionalPaymentReceiptSerializer(receipt)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_additional_receipt(request, pk):
    try:
        receipt = Additional_PaymentReciept.objects.get(pk=pk)
    except Additional_PaymentReciept.DoesNotExist:
        return Response({"error": "Receipt not found"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    user_identifier = get_username_or_email(request.user)
    data['modified_by'] = user_identifier  # ✅ auto-track editor

    partial = True if request.method == 'PATCH' else False
    serializer = AdditionalPaymentReceiptSerializer(receipt, data=data, partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Receipt updated successfully", "data": serializer.data},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_additional_receipt(request, pk):
    try:
        receipt = Additional_PaymentReciept.objects.get(pk=pk)
    except Additional_PaymentReciept.DoesNotExist:
        return Response(
            {"error": "Receipt not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Optional: restrict deletion to superadmins only
    if not request.user.is_superuser:
        return Response(
            {"error": "You do not have permission to delete receipts."},
            status=status.HTTP_403_FORBIDDEN
        )

    receipt.delete()
    return Response(
        {"message": "Additional receipt deleted successfully."},
        status=status.HTTP_204_NO_CONTENT
    )

from super_admin.services.receipts import generate_additional_receipt_pdf,email_additional_payment_receipt

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_additional_receipt(request):
    body = request.data
    receipt_id = body.get("id")
    student_id = body.get("student_id")

    if not receipt_id:
        return Response({"error": "id is required."}, status=400)
    if not student_id:
        return Response({"error": "student_id is required."}, status=400)

    # load student
    try:
        student = Student.objects.get(id=int(student_id))
    except (Student.DoesNotExist, ValueError):
        return Response({"error": "Student not found."}, status=404)

    # load additional receipt
    try:
        receipt = Additional_PaymentReciept.objects.get(id=int(receipt_id))
    except (Additional_PaymentReciept.DoesNotExist, ValueError):
        return Response({"error": "Additional receipt not found."}, status=404)

    # generate + email
    try:
        pdf_bytes = generate_additional_receipt_pdf(student, receipt)
        email_additional_payment_receipt(student, receipt, pdf_bytes)
        action = "email_sent"
        msg = "Additional payment receipt emailed successfully."
    except Exception as mail_err:
        return Response({"error": f"Failed to send email: {mail_err}"}, status=500)

    # response payload (handy for frontend toast/log)
    resp = {
        "id": receipt.id,
        "student": receipt.student_id,
        "transactionID": receipt.transactionID,
        "transaction_date": receipt.transaction_date,
        "payment_mode": receipt.paymentmode,
        "cheque_no": receipt.cheque_no,
        "bank_name": receipt.bank_name,
        "payment_transaction_id": receipt.payment_transactionID,
        "remarks": receipt.remarks,
        "session": receipt.session,
        "semyear": receipt.semyear,
        "status": receipt.status,
        "paidamount": receipt.paidamount,
        "pendingamount": receipt.pendingamount,
        "advanceamount": receipt.advanceamount,
        "action": action,
        "message": msg,
        "ts": timezone.now(),
    }
    return Response(resp, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_refund_receipt(request):
    user_identifier = get_username_or_email(request.user)

    # ---- Validate student
    student_id = request.data.get("student")
    if not student_id:
        return Response({"error": "student is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        student = Student.objects.get(pk=int(student_id))
    except (Student.DoesNotExist, ValueError):
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    # ---- Generate next transactionID (ADD-TXT445FE###)
    PREFIX = "ADD-TXT445FE"
    base_num = 100
    try:
        latest_receipt = Additional_PaymentReciept.objects.latest("id")
        m = re.search(r'(\d+)$', (latest_receipt.transactionID or ""))
        last_num = int(m.group(1)) if m else base_num
    except Additional_PaymentReciept.DoesNotExist:
        last_num = base_num
    transaction_id = f"{PREFIX}{last_num + 1}"

    # ---- Bind request (let DRF handle request.FILES)
    serializer = AdditionalPaymentReceiptRefundSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ---- Save receipt + mark student cancelled in a transaction
    with transaction.atomic():
        # Force "Refund" and server-only fields; everything else comes from request
        instance = serializer.save(
            student=student,
            payment_for="Refund",
            transactionID=transaction_id,
            created_by=user_identifier,
            modified_by=user_identifier,
        )

        # Mark student cancelled
        student.is_cancelled = True
        student.archive = True
        # Optionally track who did it if you store that:
        if hasattr(student, "modified_by"):
            student.modified_by = user_identifier
        student.save(update_fields=["is_cancelled", "modified_by","archive"] if hasattr(student, "modified_by") else ["is_cancelled"])

    return Response(
        {
            "message": "Refund receipt created successfully.",
            "data": AdditionalPaymentReceiptRefundSerializer(instance).data,
        },
        status=status.HTTP_201_CREATED,
    )
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_university_reregistration_fees(request):
    """
    GET /api/university-reregistration-fees/list/?student_id=<id>
    Return all fee records for the given student having payment_type = "University Exam Fees".
    """
    student_id = request.query_params.get('student_id')
    if not student_id:
        return Response(
            {'error': 'student_id query param is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    qs = UniversityReregistrtationFee.objects.filter(
        student_id=student_id,
        payment_type="University Exam Fees"
    ).order_by('-date', '-created_at')

    serializer = UniversityReregistrtationFeeSerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])  # supports file upload
def create_university_reregistration_Examfee(request):
    """
    POST /api/university-reregistration-fees/
    Forces payment_type = "University Exam Fees" (ignores any incoming payment_type).
    Accepts multipart/form-data or JSON.
    """
    data = request.data.copy()         # QueryDict -> mutable
    data['payment_type'] = "University Exam Fees"

    serializer = UniversityReregistrtationFeeSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_university_reregistration_fee(request, pk: int):
    """
    PUT/PATCH /api/university-reregistration-fees/<pk>/
    Protects payment_type from being changed.
    """
    instance = get_object_or_404(UniversityReregistrtationFee, pk=pk)
    data = request.data.copy()

    # Prevent changes to payment_type; keep existing value
    if 'payment_type' in data:
        data['payment_type'] = instance.payment_type or "University Exam Fees"

    partial = (request.method == 'PATCH')
    serializer = UniversityReregistrtationFeeSerializer(instance, data=data, partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_university_reregistration_fee(request, pk: int):
    obj = get_object_or_404(UniversityReregistrtationFee, pk=pk)
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])  # supports file upload
def create_university_re_registration_fee(request):
    """
    POST /api/university-re-registration-fees/
    Forces payment_type = "University Re-Registration Fees" (ignores incoming payment_type).
    Accepts multipart/form-data or JSON.
    """
    data = request.data.copy()
    data['payment_type'] = "University Re-Registration Fees"

    serializer = UniversityReregistrtationFeeSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------- LIST (by student, filtered by payment_type) ----------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_university_re_registration_fees(request):
    """
    GET /api/university-re-registration-fees/list/?student_id=<id>
    Returns all fee records for the given student where payment_type = "University Re-Registration Fees".
    """
    student_id = request.query_params.get('student_id')
    if not student_id:
        return Response({'error': 'student_id query param is required.'},
                        status=status.HTTP_400_BAD_REQUEST)

    qs = UniversityReregistrtationFee.objects.filter(
        student_id=student_id,
        payment_type="University Re-Registration Fees"
    ).order_by('-date', '-created_at')

    return Response(UniversityReregistrtationFeeSerializer(qs, many=True).data, status=status.HTTP_200_OK)


# ---------- UPDATE (protect payment_type) ----------
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_university_re_registration_fee(request, pk: int):
    """
    PUT/PATCH /api/university-re-registration-fees/<pk>/
    Protects payment_type from being changed (keeps existing or enforces the fixed value).
    """
    instance = get_object_or_404(UniversityReregistrtationFee, pk=pk)

    data = request.data.copy()
    # Never let client change payment_type; enforce the fixed label
    data['payment_type'] = instance.payment_type or "University Re-Registration Fees"

    # If somehow existing is different, normalize to the correct label
    if data['payment_type'] != "University Re-Registration Fees":
        data['payment_type'] = "University Re-Registration Fees"

    partial = (request.method == 'PATCH')
    serializer = UniversityReregistrtationFeeSerializer(instance, data=data, partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_student_document(request):
    serializer = StudentDocumentsSerializerCreate(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_student_documents(request):
    """
    GET /api/student-documents/list/?student_id=<id>
    """
    student_id = request.query_params.get('student_id')
    if not student_id:
        return Response({'error': 'student_id query param is required.'}, status=status.HTTP_400_BAD_REQUEST)
    qs = StudentDocuments.objects.filter(student_id=student_id).order_by('-id')
    return Response(StudentDocumentsSerializerCreate(qs, many=True).data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])  # added for file upload
def create_personal_document(request):
    """
    POST /api/personal-documents/
    Body: document, document_name, document_ID_no, student, document_file(optional)
    """
    serializer = PersonalDocumentsSerializerCreate(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------- LIST Personal Documents by student ----------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_personal_documents(request):
    """
    GET /api/personal-documents/list/?student_id=<id>
    """
    student_id = request.query_params.get('student_id')
    if not student_id:
        return Response({'error': 'student_id query param is required.'}, status=status.HTTP_400_BAD_REQUEST)

    qs = PersonalDocuments.objects.filter(student_id=student_id).order_by('-id')
    serializer = PersonalDocumentsSerializerCreate(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])  # to allow file upload for multiple fields
def create_qualification(request):
    """
    POST /api/qualifications/
    Creates a qualification record for a student.
    Accepts multipart/form-data (for files) or JSON.
    """
    serializer = QualificationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------- LIST (by student) ----------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_qualifications(request):
    """
    GET /api/qualifications/list/?student_id=<id>
    List all qualification records for the given student.
    """
    student_id = request.query_params.get('student_id')
    if not student_id:
        return Response({'error': 'student_id query param is required.'}, status=status.HTTP_400_BAD_REQUEST)

    qs = Qualification.objects.filter(student_id=student_id).order_by('-id')
    data = QualificationSerializer(qs, many=True).data
    return Response(data, status=status.HTTP_200_OK)


# ---------- UPDATE (PUT/PATCH by id) ----------
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_qualification(request, pk: int):
    """
    PUT/PATCH /api/qualifications/<pk>/
    Updates a qualification record by id.
    PUT = full update, PATCH = partial update.
    """
    instance = get_object_or_404(Qualification, pk=pk)
    partial = (request.method == 'PATCH')
    serializer = QualificationSerializer(instance, data=request.data, partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_qualification(request, pk: int):
    """
    DELETE /api/qualifications/<pk>/delete/
    Deletes a qualification record by id.
    """
    instance = get_object_or_404(Qualification, pk=pk)
    instance.delete()
    return Response({'message': 'Qualification deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_additional_payment_exclude_refund(request):
    student_id = request.query_params.get('student_id')
    
    if not student_id:
        logger.error("get_additional_payment_exclude_refund: student_id parameter is missing from request")
        return Response({'error': 'student_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        logger.info(f"get_additional_payment_exclude_refund: Fetching payments for student_id: {student_id}")
        
        # Filter by student and exclude refund payments
        data = Additional_PaymentReciept.objects.filter(student=student_id)
        data = data.exclude(payment_for="Refund")
        
        # Log the query count for monitoring
        logger.debug(f"get_additional_payment_exclude_refund: Found {data.count()} payments for student {student_id} (excluding refunds)")
        
        # Serialize the data using your existing serializer
        serializer = AdditionalPaymentReceiptRefundSerializer(data, many=True)
        
        logger.info(f"get_additional_payment_exclude_refund: Successfully retrieved {len(serializer.data)} payments for student {student_id}")
        
        return Response({
            'success': True,
            'count': len(serializer.data),
            'payments': serializer.data
        })
        
    except Additional_PaymentReciept.DoesNotExist:
        logger.warning(f"get_additional_payment_exclude_refund: No payments found for student_id: {student_id}")
        return Response({
            'success': False,
            'error': 'No payments found for this student'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"get_additional_payment_exclude_refund: Error retrieving payments for student {student_id}. Error: {str(e)}", 
                    exc_info=True,
                    extra={'student_id': student_id, 'endpoint': 'get_additional_payment_exclude_refund'})
        
        return Response({
            'success': False,
            'error': f'An error occurred while retrieving payments'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def update_payment_status(request, payment_id):
    try:
        logger.info(f"update_payment_status: Updating payment status for payment_id: {payment_id}")
        
        # Get the payment record
        payment = Additional_PaymentReciept.objects.get(id=payment_id)
        
        # Get the new status from request data
        new_status = request.data.get('status')
        
        if not new_status:
            logger.error("update_payment_status: status parameter is required")
            return Response({'error': 'status parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate status value
        if new_status not in ['Realised', 'Not Realised']:
            logger.error(f"update_payment_status: Invalid status value: {new_status}")
            return Response({'error': 'Status must be either "Realised" or "Not Realised"'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the status
        payment.status = new_status
        payment.save()
        
        logger.info(f"update_payment_status: Successfully updated payment {payment_id} status to {new_status}")
        
        # Serialize and return updated data
        serializer = AdditionalPaymentReceiptRefundSerializer(payment)
        
        return Response({
            'success': True,
            'message': 'Payment status updated successfully',
            'payment': serializer.data
        })
        
    except Additional_PaymentReciept.DoesNotExist:
        logger.error(f"update_payment_status: Payment not found with id: {payment_id}")
        return Response({
            'success': False,
            'error': 'Payment not found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"update_payment_status: Error updating payment {payment_id}. Error: {str(e)}", 
                    exc_info=True,
                    extra={'payment_id': payment_id, 'endpoint': 'update_payment_status'})
        
        return Response({
            'success': False,
            'error': f'An error occurred while updating payment status'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['GET'])
def get_student_profile_image(request, student_id):
    try:
        logger.info(f"get_student_profile_image: Fetching profile image for student_id: {student_id}")
        
        # Get the student object
        student = Student.objects.get(id=student_id)
        
        # Check if image exists
        if not student.image:
            logger.warning(f"get_student_profile_image: No profile image found for student_id: {student_id}")
            return Response({
                'success': False,
                'error': 'No profile image found for this student'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Return image URL and student details
        image_url = request.build_absolute_uri(student.image.url) if student.image else None
        
        logger.info(f"get_student_profile_image: Successfully retrieved profile image for student_id: {student_id}")
        
        return Response({
            'success': True,
            'student_id': student.id,
            'student_name': student.name,
            'enrollment_id': student.enrollment_id,
            'profile_image_url': image_url,
            'has_image': bool(student.image)
        })
        
    except Student.DoesNotExist:
        logger.error(f"get_student_profile_image: Student not found with id: {student_id}")
        return Response({
            'success': False,
            'error': 'Student not found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"get_student_profile_image: Error retrieving profile image for student {student_id}. Error: {str(e)}", 
                    exc_info=True,
                    extra={'student_id': student_id, 'endpoint': 'get_student_profile_image'})
        
        return Response({
            'success': False,
            'error': f'An error occurred while retrieving profile image'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def update_student_profile_image(request, student_id):
    try:
        logger.info(f"update_student_profile_image: Updating profile image for student_id: {student_id}")
        
        # Get the student object
        student = Student.objects.get(id=student_id)
        
        # Check if image file is provided in the request
        if 'image' not in request.FILES:
            logger.error("update_student_profile_image: No image file provided in request")
            return Response({
                'success': False,
                'error': 'Image file is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['image']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if image_file.content_type not in allowed_types:
            logger.error(f"update_student_profile_image: Invalid file type: {image_file.content_type}")
            return Response({
                'success': False,
                'error': 'Invalid file type. Only JPEG, JPG, PNG, and GIF images are allowed.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        if image_file.size > max_size:
            logger.error(f"update_student_profile_image: File size too large: {image_file.size} bytes")
            return Response({
                'success': False,
                'error': 'File size too large. Maximum allowed size is 5MB.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete old image if exists
        if student.image:
            try:
                if os.path.isfile(student.image.path):
                    os.remove(student.image.path)
                    logger.info(f"update_student_profile_image: Deleted old image for student_id: {student_id}")
            except Exception as e:
                logger.warning(f"update_student_profile_image: Could not delete old image for student {student_id}: {str(e)}")
        
        # Update the student image
        student.image = image_file
        student.save()
        
        # Get the updated image URL
        image_url = request.build_absolute_uri(student.image.url) if student.image else None
        
        logger.info(f"update_student_profile_image: Successfully updated profile image for student_id: {student_id}")
        
        return Response({
            'success': True,
            'message': 'Profile image updated successfully',
            'student_id': student.id,
            'student_name': student.name,
            'enrollment_id': student.enrollment_id,
            'profile_image_url': image_url,
            'has_image': bool(student.image)
        })
        
    except Student.DoesNotExist:
        logger.error(f"update_student_profile_image: Student not found with id: {student_id}")
        return Response({
            'success': False,
            'error': 'Student not found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"update_student_profile_image: Error updating profile image for student {student_id}. Error: {str(e)}", 
                    exc_info=True,
                    extra={'student_id': student_id, 'endpoint': 'update_student_profile_image'})
        
        return Response({
            'success': False,
            'error': f'An error occurred while updating profile image'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_fees_request_email(request):
    try:
        data = request.data
        
        # Required fields
        student_id = data.get('student_id')
        email = data.get('email')
        amount = data.get('amount')
        payment_categories = data.get('payment_categories')
        payment_type = data.get('payment_type')
        subject = data.get('subject')
        message = data.get('message')
        
        if not all([student_id, email, amount, payment_categories, payment_type, subject, message]):
            return Response({
                'success': False,
                'error': 'All fields are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get student and university name
        try:
            student = Student.objects.get(id=student_id)
            university_name = student.university.university_name if student.university else "University"
        except Student.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Student not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Email content
        email_subject = f"Fees Request: {subject}"
        
        email_body = f"""
Dear Student,

Pending Amount: Rs. {amount}/-

Payment Category: {payment_categories}
Payment Type: {payment_type}

{message}

NOTE: Dear Student, (Please ignore if already paid.)

We wish to thank you for your continued support throughout the Academic Year.

Best regards,
{university_name}
"""
        
        # Send email
        send_mail(
            subject=email_subject,
            message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        return Response({
            'success': True,
            'message': 'Fees request email sent successfully!'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Failed to send email: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_reminder_email(request):
  try:
      data = request.data
      student_id = data.get('student_id')
      email = data.get('email')
      message = data.get('message')
      subject = data.get('subject', 'Reminder Message')
      
      if not all([student_id, email, message]):
          return Response({
              'success': False,
              'error': 'Student ID, email and message are required'
          }, status=status.HTTP_400_BAD_REQUEST)
      
      # Get student and university name
      try:
          student = Student.objects.get(id=student_id)
          university_name = student.university.university_name if student.university else "University"
      except Student.DoesNotExist:
          return Response({
              'success': False,
              'error': 'Student not found'
          }, status=status.HTTP_404_NOT_FOUND)
      
      # Email content
      email_subject = subject
      
      email_body = f"""
Dear Student,

{message}

Best regards,
{university_name}
"""
      
      # Send email
      send_mail(
          subject=email_subject,
          message=email_body,
          from_email=settings.DEFAULT_FROM_EMAIL,
          recipient_list=[email],
          fail_silently=False,
      )
      
      return Response({
          'success': True,
          'message': 'Reminder email sent successfully!'
      }, status=status.HTTP_200_OK)
      
  except Exception as e:
      return Response({
          'success': False,
          'error': f'Failed to send reminder email: {str(e)}'
      }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      


@api_view(['POST'])
def create_student_form(request):
    """
    Create a new student form
    """
    if request.method == 'POST':
        try:
            # Get data from request
            student_id = request.data.get('student_id')
            sem_year = request.data.get('sem_year')
            form_type = request.data.get('form_type')
            
            # Check if form already exists for same student, sem_year and form_type
            existing_form = StudentForm.objects.filter(
                student_id=student_id,
                sem_year=sem_year,
                form_type=form_type
            ).first()
            
            if existing_form:
                return Response({
                    'error': f'Form of type {form_type} already exists for student {student_id} in semester/year {sem_year}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate form type
            valid_form_types = dict(StudentForm.FORM_TYPES).keys()
            if form_type not in valid_form_types:
                return Response({
                    'error': f'Invalid form type. Must be one of: {list(valid_form_types)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create serializer with request data
            serializer = StudentFormSerializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Student form created successfully',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': 'Validation failed',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': f'Server error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_all_forms(request):
    """
    Get all student forms with optional filtering
    """
    try:
        # Get query parameters for filtering
        student_id = request.GET.get('student_id')
        sem_year = request.GET.get('sem_year')
        form_type = request.GET.get('form_type')
        
        # Start with all forms
        forms = StudentForm.objects.all()
        
        # Apply filters if provided
        if student_id:
            forms = forms.filter(student_id=student_id)
        if sem_year:
            forms = forms.filter(sem_year=sem_year)
        if form_type:
            forms = forms.filter(form_type=form_type)
        
        # Serialize data
        serializer = StudentFormSerializer(forms, many=True)
        
        return Response({
            'count': forms.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_forms_by_type(request, form_type):
    """
    Get all forms by specific form type with optional student_id filter
    """
    try:
        # Validate form type
        valid_form_types = dict(StudentForm.FORM_TYPES).keys()
        if form_type not in valid_form_types:
            return Response({
                'error': f'Invalid form type. Must be one of: {list(valid_form_types)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get query parameters for filtering
        student_id = request.GET.get('student_id')
        
        # Get forms by type
        forms = StudentForm.objects.filter(form_type=form_type)
        
        # Apply student filter if provided
        if student_id:
            forms = forms.filter(student_id=student_id)
        
        serializer = StudentFormSerializer(forms, many=True)
        
        return Response({
            'form_type': form_type,
            'count': forms.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_student_forms(request, student_id):
    """
    Get all forms for a specific student
    """
    try:
        # Optional sem_year filter
        sem_year = request.GET.get('sem_year')
        
        forms = StudentForm.objects.filter(student_id=student_id)
        
        if sem_year:
            forms = forms.filter(sem_year=sem_year)
        
        serializer = StudentFormSerializer(forms, many=True)
        
        return Response({
            'student_id': student_id,
            'sem_year': sem_year,
            'count': forms.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_form_detail(request, form_id):
    """
    Get specific form details
    """
    try:
        form = get_object_or_404(StudentForm, id=form_id)
        serializer = StudentFormSerializer(form)
        
        return Response({
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except StudentForm.DoesNotExist:
        return Response({
            'error': 'Form not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def update_student_form(request, form_id):
    """
    Update existing student form
    """
    try:
        form = get_object_or_404(StudentForm, id=form_id)
        
        # Check if update would create duplicate
        student_id = request.data.get('student_id', form.student_id)
        sem_year = request.data.get('sem_year', form.sem_year)
        form_type = request.data.get('form_type', form.form_type)
        
        existing_form = StudentForm.objects.filter(
            student_id=student_id,
            sem_year=sem_year,
            form_type=form_type
        ).exclude(id=form_id).first()
        
        if existing_form:
            return Response({
                'error': f'Form of type {form_type} already exists for student {student_id} in semester/year {sem_year}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = StudentFormSerializer(form, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Form updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except StudentForm.DoesNotExist:
        return Response({
            'error': 'Form not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_student_form(request, form_id):
    """
    Delete student form
    """
    try:
        form = get_object_or_404(StudentForm, id=form_id)
        form.delete()
        
        return Response({
            'message': 'Form deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except StudentForm.DoesNotExist:
        return Response({
            'error': 'Form not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_form_types(request):
    """
    Get available form types
    """
    return Response({
        'form_types': dict(StudentForm.FORM_TYPES)
    }, status=status.HTTP_200_OK)
    
import logging
import threading
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CallRecording, DriveFolder, SyncLog, PlaybackLog
from .api_serializers import (
    CallRecordingSerializer, DriveFolderSerializer, SyncLogSerializer, PlaybackLogSerializer
)
from .services.google_drive_service import GoogleDriveService
from .services.sync_service import DriveSyncService

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_call_recordings(request):
    try:
        recordings = CallRecording.objects.all()

        phone_number = request.GET.get('phone_number')
        status_filter = request.GET.get('status')
        search = request.GET.get('search')

        if phone_number:
            recordings = recordings.filter(phone_number__icontains=phone_number)
        if status_filter:
            recordings = recordings.filter(status=status_filter)
        if search:
            recordings = recordings.filter(
                Q(phone_number__icontains=search) |
                Q(file_name__icontains=search) |
                Q(drive_file_name__icontains=search)
            )

        order_by = request.GET.get('order_by', '-created_at')
        if order_by.lstrip('-') in ['phone_number', 'file_name', 'recording_date', 'created_at']:
            recordings = recordings.order_by(order_by)

        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        total_count = recordings.count()
        recordings = recordings[start_index:end_index]

        # 🔴 IMPORTANT: pass request in context so audio_url becomes absolute
        serializer = CallRecordingSerializer(
            recordings,
            many=True,
            context={'request': request}
        )

        return Response({
            'success': True,
            'data': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        })
    except Exception as e:
        logger.exception("get_call_recordings failed")
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_drive_folder(request):
    try:
        serializer = DriveFolderSerializer(data=request.data)
        if serializer.is_valid():
            folder = serializer.save()
            return Response({
                'success': True,
                'message': f"Folder '{folder.name}' added successfully",
                'data': DriveFolderSerializer(folder).data
            })
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("add_drive_folder failed")
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_drive_folders(request):
    try:
        folders = DriveFolder.objects.all()
        serializer = DriveFolderSerializer(folders, many=True)
        return Response({'success': True, 'data': serializer.data})
    except Exception as e:
        logger.exception("get_drive_folders failed")
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sync_logs(request):
    try:
        logs = SyncLog.objects.all()

        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        total_count = logs.count()
        logs = logs[start_index:end_index]

        serializer = SyncLogSerializer(logs, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        })
    except Exception as e:
        logger.exception("get_sync_logs failed")
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sync_status(request):
    try:
        total_recordings = CallRecording.objects.count()
        total_folders = DriveFolder.objects.count()
        active_folders = DriveFolder.objects.filter(is_active=True).count()
        last_sync = SyncLog.objects.first()

        return Response({
            'success': True,
            'data': {
                'total_recordings': total_recordings,
                'total_folders': total_folders,
                'active_folders': active_folders,
                'last_sync': SyncLogSerializer(last_sync).data if last_sync else None
            }
        })
    except Exception as e:
        logger.exception("get_sync_status failed")
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_playback(request):
    try:
        recording_id = request.data.get('recording_id')
        if not recording_id:
            return Response({'success': False, 'error': 'recording_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        recording = CallRecording.objects.get(id=recording_id)
        recording.play_count += 1
        recording.last_played_at = timezone.now()
        recording.save(update_fields=["play_count", "last_played_at"])

        PlaybackLog.objects.create(
            recording=recording,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        return Response({'success': True, 'message': 'Playback logged successfully'})
    except CallRecording.DoesNotExist:
        return Response({'success': False, 'error': 'Recording not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception("log_playback failed")
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_playback_logs(request):
    try:
        logs = PlaybackLog.objects.all()

        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        total_count = logs.count()
        logs = logs[start_index:end_index]

        serializer = PlaybackLogSerializer(logs, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        })
    except Exception as e:
        logger.exception("get_playback_logs failed")
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')
