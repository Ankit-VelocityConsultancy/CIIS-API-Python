"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from super_admin import api_views
from rest_framework_simplejwt.views import  TokenObtainPairView,TokenRefreshView

urlpatterns = [
  path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
  path('login/',api_views.login_view,name="login" ),
  path('universities/', api_views.add_university, name='university_list'),  # For GET and POST
  path('universities/<int:university_id>/',api_views.university_detail,name='university_detail'),# For GET,PUT DELETE
  path('create-user/',api_views.create_user,name="create_user" ),
  
  path('create-semester-fees/',api_views.create_semester_fees,name="create_semester_fees" ),
  path('create-year-fees/', api_views.create_year_fees, name='create_year_fees'),
  path('get-year-fees/', api_views.get_year_fees, name='get_year_fees'),

  path('payment-modes/',api_views.payment_modes,name="payment_modes" ),
  path('payment-modes/<int:id>/', api_views.payment_mode_detail, name='payment_mode_detail'),
  path('fee-receipt-options/', api_views.fee_receipt_options, name='fee_receipt_options'),
  path('fee-receipt-options/<int:id>/', api_views.fee_receipt_option_detail, name='fee_receipt_option_detail'),
  path('bank-names/', api_views.bank_names, name='bank_names'),
  path('bank-names/<int:id>/', api_views.bank_name_detail, name='bank_name_detail'),
  path('session-names/', api_views.session_names, name='session_names'),
  path('session-names/<int:id>/', api_views.session_name_detail, name='session_name_detail'),
  path('change-password/', api_views.change_password, name='change_password'),
  path('courses/', api_views.get_courses_by_university, name='get_courses_by_university'),
  path('streams/', api_views.get_stream_by_course_one, name='get_streams_by_course'),
  path('substreams/', api_views.get_substreams_by_university_course_stream, name='get_substreams_by_university_course_stream'),
  path('student-registration/', api_views.student_registration, name='student_registration'),  
  path('search-by-enrollment-id/', api_views.search_by_enrollment_id, name='search_by_enrollment_id'),
  path('search-by-student-name/', api_views.search_by_student_name, name='search_by_student_name'),
  path('create-courses/', api_views.create_course, name='create_course'),
  path('create-stream/', api_views.create_stream, name='create_stream'),
  path('create-substream/', api_views.create_sub_stream, name='create_sub_stream'),
  path('create-subject/', api_views.create_subject, name='create_subject'),

  path('get-student-course-details/<int:student_id>/',api_views.get_student_course_details,name='get_student_course_details'),
  path('update-student-course-details/<int:student_id>/',api_views.update_student_course_details, name='update_student_course_details'),
  # get all courses with there respective university
  path('universities-courses/', api_views.universities_with_courses, name='universities_with_courses'),
  path('update-course/<int:course_id>/',api_views.update_course, name='update_course'),
  path('streams/<int:course_id>/', api_views.get_stream_by_course_two, name='get-stream-by-course'),
  path('update-streams/<int:course_id>/', api_views.update_streams_by_course, name='update-streams-by-course'),  
  path('update-substreams/<int:stream_id>/', api_views.update_substreams_by_stream, name='update-substreams-by-stream'),
  
  path('quick-registration/', api_views.quick_registration, name='quick_registration'),
  path('get_sem_year_by_stream/', api_views.get_sem_year_by_stream, name='get_sem_year_by_stream'),
  
  path('get_sem_year_by_stream_byname/', api_views.get_sem_year_by_stream_byname, name='get_sem_year_by_stream_byname'),

  path('fee-receipt-options/', api_views.get_fee_recipt_option, name='get_fee_receipt_options'),
  path('bank_names/', api_views.bank_names_list_create, name='bank_names_list_create'),
  path('payment_modes/', api_views.payment_modes_list_create, name='payment_modes_list_create'),
  path('quick-registered-students/', api_views.view_quick_registered_students, name='quick_registered_students'),

  path('registered-students-list/', api_views.get_student_registration_list, name='get_student_registration_list'),
  
  path('delete-student/<int:student_id>/', api_views.delete_student, name='delete_student'),
  path('get-sem-fees/', api_views.get_sem_fees, name='get_sem_fees'),
  
  #created by ankit to get id of all 
  path('courses-with-id/', api_views.get_courses_by_university_with_id, name='get_courses_by_university_with_id'),
  path('streams-with-id/', api_views.get_stream_by_course_with_id, name='get_stream_by_course_with_id'),
  path('substreams-with-id/', api_views.get_substreams_by_university_course_stream_with_id, name='get_substreams_by_university_course_stream_with_id'),

    path('countries/', api_views.get_country, name='get_country'),
    path('states/', api_views.get_states, name='get_states'),
    path('cities/', api_views.get_cities, name='get_cities'),

    path('get-student/<int:enrollment_id>', api_views.get_student_details, name='get_student_details'),
    path('update-student/<int:enrollment_id>', api_views.update_student_details, name='update_student_details'),
    # path('upload-student-documents/', api_views.upload_student_documents, name='upload_student_documents'),
  # path('update-quick-student/<int:enrollment_id>', api_views.update_quick_student_details, name='update_quick_student_details'),
  
  path('bulk-student-upload/', api_views.bulk_student_upload, name='bulk_student_upload'),
  path('fetch-subject/',api_views.fetch_subject,name='fetch_subject'),
  path('exams-bulk-upload/', api_views.bulk_exam_upload, name='bulk_exam_upload'),
  # path('upload_bulk_exam_data/', api_views.upload_bulk_exam_data, name='upload_bulk_exam_data'),

  path('filter-questions/', api_views.filter_questions, name='filter_questions'),
  path('fetch_exam/', api_views.fetch_exam, name='fetch_exam'),
  path('view-assigned-students/', api_views.view_assigned_students, name='view_assigned_students'),
  path('save_exam_details/', api_views.save_exam_details, name='save_exam_details'),
  
  path('view_set_examination/', api_views.view_set_examination, name='view_set_examination'),

  path('set_exam_for_subject/', api_views.set_exam_for_subject, name='set_exam_for_subject'),
  path('delete_exam_for_student/', api_views.delete_exam_for_student, name='delete_exam_for_student'),

  path('reassign_student/', api_views.reassign_student, name='reassign_student'),
  path('get_course_duration/', api_views.get_course_duration, name='get_course_duration'),
  path('get_all_subjects/', api_views.get_all_subjects, name='get_all_subjects'),

  path('student_login/', api_views.student_login, name='student_login'),
  path('download-excel-for-subject/', api_views.download_excel_for_set_exam_for_subject, name='download_excel_for_set_exam_for_subject'),
  path('all-questions/', api_views.fetch_questions_based_on_exam_id, name='fetch_questions_based_on_exam_id'),
  path('resend-email/', api_views.resend_exam_email, name='resend_exam_email'),
  path('examinations/', api_views.get_result_to_show_based_on_subject, name='get_result_based_on_subject'),
  path('save-submitted-answers/', api_views.save_all_questions_answers, name='save_all_questions_answers'),
  path('export_to_excel/', api_views.export_to_excel, name='export_to_excel'),
  path('generate-result/', api_views.generate_result, name='generate_result'),
  path('show-result/', api_views.show_result, name='show_result'),

# delete stream substream course and university
  path('delete_university/<int:university_id>/', api_views.delete_university, name='delete_university'),
  path('delete_course/<int:course_id>/', api_views.delete_course, name='delete_course'),
  path('delete_stream/<int:stream_id>/', api_views.delete_stream, name='delete_stream'),
  path('delete_substream/<int:substream_id>/', api_views.delete_substream, name='delete_substream'),
  path('delete_subject/<int:subject_id>/', api_views.delete_subject, name='delete_subject'),  
  
  path('substreams-withid/', api_views.get_substreams_with_id_by_university_course_stream, name='get_substreams_with_id_by_university_course_stream'),
#---------------------------------------------------------------------------------------------
  path('list_of_all_registered_student/', api_views.list_of_all_registered_student, name='list_of_all_registered_student'), 
  
  path('list_of_all_cancelled_student/', api_views.list_of_all_cancelled_student, name='list_of_all_cancelled_student'),
   
  path('get_student_enroll_to_next_year/<int:id>/', api_views.get_student_enroll_to_next_year, name='get_student_enroll_to_next_year'),

  path('get_subjects_by_stream/<int:stream_id>/', api_views.get_subjects_by_stream, name='get_subjects_by_stream'),



  path('update-multiple-subjects/', api_views.update_multiple_subjects, name='update_multiple_subjects'),
  path('student-cancel/<int:id>/', api_views.register_cancel_student, name='register_cancel_student'),
  
  path("register-enrollment-new/", api_views.registered_new_university_enrollment_number, name="register_enrollment_new"),
  path("register-enrollment-old/", api_views.registered_old_university_enrollment_number, name="register_enrollment_old"),
  path("courier/", api_views.courier_api, name="courier_api"), 
  
  path('get_additional_fees/',api_views.get_additional_fees,name="get_additional_fees"),
  path('create_additional_fees/', api_views.create_additional_fees, name='create_additional_fees'),
  path('update_additional_fees/', api_views.update_additional_fees, name='update_additional_fees'),
  path('result_uploaded_view/', api_views.result_uploaded_view, name='result_uploaded_view'),
  path('update_result_uploaded/<int:result_id>/', api_views.update_result_uploaded, name='update_result_uploaded'),
  path('create_university_exam/', api_views.create_university_examination, name='create_university_exam'),
  
  path('create_university_reregistration/', api_views.create_university_reregistration, name='create_university_reregistration'),
  path('get_university_reregistration/', api_views.get_university_reregistration, name='get_university_reregistration'),
  path('get_paid_fees/', api_views.get_paid_fees, name='get_paid_fees'),

  path('save_single_answers/', api_views.save_single_question_answer, name='save_single_answers'),

  path('document-management/<int:enrollment_id>/',api_views.document_management, name='document_management'),

  path('save_exam_timer/', api_views.save_exam_timer),
  path('get_exam_timer/', api_views.get_exam_timer),
  
  path('save_result_after_exam/', api_views.save_result_after_exam),
  path('check_exam_result/', api_views.check_exam_result),
  
  path('check_exam_availability/', api_views.check_exam_availability),

#-----Leads module--------------------------------------
  path('categories-create/', api_views.create_category, name='create_category'),
  path('categories-update/<int:pk>/', api_views.update_category, name='update_category'),
  path('categories/', api_views.list_categories, name='list_categories'),
  
  path('sources-create/', api_views.create_source, name='create_source'),
  path('sources-update/<int:pk>/', api_views.update_source, name='update_source'),
  path('sources/', api_views.list_sources, name='list_sources'),
  
  path('dispositions/', api_views.list_dispositions, name='list_dispositions'),
  path('dispositions-create/', api_views.create_disposition, name='create_disposition'),
  path('dispositions-update/<int:pk>/', api_views.update_disposition, name='update_disposition'),
  
  
]
  

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)