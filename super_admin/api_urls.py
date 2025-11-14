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
from super_admin import api_views, views_bootstrap
from rest_framework_simplejwt.views import  TokenObtainPairView,TokenRefreshView
from super_admin import api_role
from super_admin import api_jobportal
from .api_jobportal import WhatsAppSendView
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
  path('view_pending_verification_students/', api_views.view_pending_verification_students, name='view_pending_verification_students'),

  path('registered-students-list/', api_views.get_student_registration_list, name='get_student_registration_list'),
  
  path('delete-student/<int:student_id>/', api_views.delete_student, name='delete_student'),
  path('get-sem-fees/', api_views.get_sem_fees, name='get_sem_fees'),
  
  #created by ankit to get id of all 
  path('courses-with-id/', api_views.get_courses_by_university_with_id, name='get_courses_by_university_with_id'),
  path('streams-with-id/', api_views.get_stream_by_course_with_id, name='get_stream_by_course_with_id'),
  path('substreams-with-id/', api_views.get_substreams_by_stream_with_id, name='get_substreams_by_university_course_stream_with_id'),

    path('countries/', api_views.get_country, name='get_country'),
    path('states/', api_views.get_states, name='get_states'),
    path('cities/', api_views.get_cities, name='get_cities'),

    path('get-student/<int:enrollment_id>', api_views.get_student_details, name='get_student_details'),
    path('update-student/<int:enrollment_id>', api_views.update_student_details, name='update_student_details'),
    # path('upload-student-documents/', api_views.upload_student_documents, name='upload_student_documents'),
  # path('update-quick-student/<int:enrollment_id>', api_views.update_quick_student_details, name='update_quick_student_details'),
  
  path('bulk-student-upload/', api_views.bulk_student_upload, name='bulk_student_upload'),
  path('get_uploaded_student_files/', api_views.get_uploaded_student_files, name='get-uploaded-student-files'),
  path('delete_student_file_upload/<int:file_id>/', api_views.delete_student_file_upload, name='delete-student-file-upload'),
  path('download_student_data_excel/', api_views.download_student_data_excel, name='download-student-data-excel'),

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

  path('registered_save_enrollment_to_next_semyear/', api_views.registered_save_enrollment_to_next_semyear, name='save_enrollment_to_next_semyear'),


  path('get_subjects_by_stream/<int:stream_id>/', api_views.get_subjects_by_stream, name='get_subjects_by_stream'),



  path('update-multiple-subjects/', api_views.update_multiple_subjects, name='update_multiple_subjects'),
  path('student-cancel/<int:id>/', api_views.register_cancel_student, name='register_cancel_student'),
  
  path("register-enrollment-new/", api_views.registered_new_university_enrollment_number, name="register_enrollment_new"),
  path("register-enrollment-old/", api_views.registered_old_university_enrollment_number, name="register_enrollment_old"),
  path("courier/", api_views.courier_api, name="courier_api"), 
  
  # path('get_additional_fees/',api_views.get_additional_fees,name="get_additional_fees"),
  # path('create_additional_fees/', api_views.create_additional_fees, name='create_additional_fees'),
  # path('update_additional_fees/', api_views.update_additional_fees, name='update_additional_fees'),
  
  path('result_uploaded_view/', api_views.result_uploaded_view, name='result_uploaded_view'),

  path('update_result_uploaded_by_student_sem/', api_views.update_result_uploaded_by_student_sem, name='update_result_uploaded_by_student_sem'),


  path('create_university_exam/', api_views.create_university_examination, name='create_university_exam'),
  
  path('create_university_reregistration/', api_views.create_university_reregistration, name='create_university_reregistration'),
  path('get_university_reregistration/', api_views.get_university_reregistration, name='get_university_reregistration'),
  path('get_paid_fees/', api_views.get_paid_fees, name='get_paid_fees'),

    path('save_single_answers/', api_views.save_single_question_answer, name='save_single_answers'),

  path('document-management/<int:enrollment_id>/',api_views.document_management, name='document_management'),

  path('save_exam_timer/', api_views.save_exam_timer, name="save_exam_timer"),
  path('get_exam_timer/', api_views.get_exam_timer, name="get_exam_timer"),
  
  path('save_result_after_exam/', api_views.save_result_after_exam,name="save_result_after_exam"),
  path('check_exam_result/', api_views.check_exam_result),
  
  path('check_exam_availability/', api_views.check_exam_availability, name="check_exam_availability"),

#-----Leads module--------------------------------------
  # path('categories-create/', api_views.create_category, name='create_category'),
  path('categories-update/<int:pk>/', api_views.update_category, name='update_category'),
  path('categories/', api_views.list_categories, name='list_categories'),
  
  path('sources-create/', api_views.create_source, name='create_source'),
  path('sources-update/<int:pk>/', api_views.update_source, name='update_source'),
  path('sources/', api_views.list_sources, name='list_sources'),
  
  path('statuses/', api_views.list_statuses, name='list_statuses'),
  path('statuses-create/', api_views.create_status, name='create_status'),
  path('statuses-update/<int:pk>/', api_views.update_status, name='update_status'),
  
  path('common-lead-labels/', api_views.list_common_lead_labels, name='list_common_lead_labels'),
  path('common-lead-labels-create/', api_views.create_common_lead_label, name='create_common_lead_label'),
  path('common-lead-labels-update/<int:pk>/', api_views.update_common_lead_label, name='update_common_lead_label'),
  
  # path('colors/', api_views.list_colors, name='list_colors'),
  # path('colors-create/', api_views.create_color, name='create_color'),
  # path('colors-update/<int:pk>/', api_views.update_color, name='update_color'),
  path('sync_answers/', api_views.sync_answers, name='sync_answers'),
  
  path('export_exam_data_to_excel/', api_views.export_exam_data_to_excel, name='export_exam_data_to_excel'),
  path('fetch_complete_student_data/', api_views.fetch_complete_student_data_api, name='fetch_complete_student_data'),
  path('view_all_assigned_students_api/', api_views.view_all_assigned_students_api, name='view_all_assigned_students_api'),
#---------------------Role----------------------------------------------#

  path('get_roles/', api_role.get_roles, name='view_all_assigned_students_api'),
  path('create_role/', api_role.create_role, name='create_role'),
  path("roles/save-permissions/", api_role.save_role_permissions, name="save-role-permissions"),
  path("roles/permissions/<int:role_id>/", api_role.get_role_permissions, name="get-role-permissions"),
  path("edit_role/<int:role_id>/", api_role.edit_role, name="edit_role"),
  path('get_role_user/', api_role.get_role_user, name='get_role_user'),
  path('get_user_dropdown/', api_role.get_user_dropdown, name='get_user_dropdown'),

  path('create_or_update_user/', api_role.create_or_update_user, name='create_user'),
  path('get_user/<int:user_id>/', api_role.get_user_by_id, name='get_user_by_id'),
  path('create_category/', api_role.create_category, name='create_category'),
  path('get_all_categories/', api_role.get_all_categories, name='get_all_categories'),
  path('update_category/<int:category_id>/', api_role.update_category, name='update_category'),
  path('delete_category/<int:category_id>/', api_role.delete_category, name='delete_category'),
  path('get_all_sources/', api_role.get_all_sources, name='get_all_sources'),
  path('create_source/', api_role.create_source, name='create_source'),
  path('update_source/<int:source_id>/', api_role.update_source, name='update_source'),
  path('delete_source/<int:source_id>/', api_role.delete_source, name='delete_source'),
  path('get_all_role_status/', api_role.get_all_role_status, name='get_all_role_status'),
  path('create_role_status/', api_role.create_role_status, name='create_role_status'),
  path('update_role_status/<int:role_status_id>/', api_role.update_role_status, name='update_role_status'),
  path('delete_role_status/<int:role_status_id>/', api_role.delete_role_status, name='delete_role_status'),  
  path('get_all_lead_label_tags/', api_role.get_all_lead_label_tags, name='get_all_lead_label_tags'),
  path('create_lead_label_tag/', api_role.create_lead_label_tag, name='create_lead_label_tag'),
  path('update_lead_label_tag/<int:tag_id>/', api_role.update_lead_label_tag, name='update_lead_label_tag'),
  path('delete_lead_label_tag/<int:tag_id>/', api_role.delete_lead_label_tag, name='delete_lead_label_tag'),  
  path('get_all_countries/', api_role.get_all_countries, name='get_all_countries'),
  path('create_country/', api_role.create_country, name='create_country'),
  path('update_country/<int:country_id>/', api_role.update_country, name='update_country'),
  path('delete_country/<int:country_id>/', api_role.delete_country, name='delete_country'),


  path('states_new/', api_role.list_states, name='list_states'),
  path('states_new/create/', api_role.create_state, name='create_state'),
  path('states_new/<int:state_id>/update/', api_role.update_state, name='update_state'),
  path('states_new/<int:state_id>/delete/', api_role.delete_state, name='delete_state'),
  
  path('cities/', api_role.list_cities, name='list_cities'),
  path('cities/create/', api_role.create_city, name='create_city'),
  path('cities/<int:city_id>/update/', api_role.update_city, name='update_city'),
  path('cities/<int:city_id>/delete/', api_role.delete_city, name='delete_city'),

  path("get_user_profile/", api_role.get_user_profile, name="get_user_profile"),

  path('get_all_colors/', api_role.get_all_colors, name='get_all_colors'),
  path('create_color/', api_role.create_color, name='create_color'),
  path('update_color/<int:color_id>/', api_role.update_color, name='update_color'),
  path('delete_color/<int:color_id>/', api_role.delete_color, name='delete_color'),
  path("create_lead/", api_role.create_lead, name="create_lead"),
  path("role_status_list/", api_role.role_status_list, name="role_status_list"),
  path("filter_leads_by_status/", api_role.filter_leads_by_status, name="filter_leads_by_status"),
  path("get_lead_user/", api_role.get_lead_user, name="get_lead_user"),
  path("update_lead/<int:lead_id>/", api_role.update_lead, name="update_lead"),
  path("get_lead/<int:lead_id>/", api_role.get_lead_by_id, name="get_lead"),
  path("get_all_leads/", api_role.get_all_leads, name="get_all_leads"),

  path("filter_leads/", api_role.filter_leads, name="filter_leads"),
  # path("leads/comments/<int:lead_id>/", api_role.get_lead_comments, name="get_lead_comments"),
  # path("leads/add_comment/<int:lead_id>/", api_role.create_lead_comment, name="create_lead_comment"),
  path("leads/update_mobiles/<int:lead_id>/", api_role.update_lead_mobiles, name="update_lead_mobiles"),
  path('edit_user/<int:user_id>/', api_role.update_user, name='update_user'),


  # urls for job portal -----------------------------------------------------
  path("add_job_seeker_education/", api_jobportal.add_job_seeker_education, name="add_job_seeker_education"),
  path("add_work_preferences/", api_jobportal.add_work_preferences, name="add_work_preferences"),
  path("add_employment_details/", api_jobportal.add_employment_details, name="add_employment_details"),
  path('post_job/', api_jobportal.create_job_post, name='post_job'),
  path('get_job_posts/', api_jobportal.get_job_posts, name='get_job_posts'),
  path('get_job_posts/<int:jobpostid>', api_jobportal.get_job_post_by_id, name='get_job_posts'),

  path('update_job_post/<int:pk>/', api_jobportal.update_job_post, name='update_job_post'),
  path('delete_job_post/<int:job_post_id>/', api_jobportal.delete_job_post, name='delete_job_post'),
  
  path('register_job_seeker/', api_jobportal.register_job_seeker, name='job-seeker-register'),
  path('authenticate_job_seeker/', api_role.authenticate_job_seeker,  name='job-seeker-login'),
  
  path('apply_for_job/', api_jobportal.apply_for_job, name='apply_for_job'),
  path('applications/<int:application_id>/resume/', api_role.view_application_resume, name='view-application-resume'),
  path('applications_status/<int:application_id>/', api_role.update_application_status, name='update-application-status'),
  path('applications/', api_role.get_job_applications, name='get-job-applications'),
  path('jobpost_update_status/<int:jobpost_id>/', api_role.update_jobpost_status),
  #------------------------job portal master data--------------------------
  path('departments/', api_role.jobport_department_list_create, name='jobport-department-list-create'),
  path('departments/<int:pk>/', api_role.jobport_department_detail, name='jobport-department-detail'),

  # Qualification
  path('qualifications/', api_jobportal.jobport_qualification_list_create, name='jobport-qualification-list-create'),
  path('qualifications/<int:pk>/', api_jobportal.jobport_qualification_detail, name='jobport-qualification-detail'),

  # Additional Benefits
  path('benefits/', api_jobportal.jobport_additionalbenefit_list_create, name='jobport-benefit-list-create'),
  path('benefits/<int:pk>/', api_jobportal.jobport_additionalbenefit_detail, name='jobport-benefit-detail'),

  # Required Skills
  path('skills/', api_jobportal.jobport_requiredskill_list_create, name='jobport-skill-list-create'),
  path('skills/<int:pk>/', api_jobportal.jobport_requiredskill_detail, name='jobport-skill-detail'),

  # Languages
  path('languages/', api_jobportal.jobport_language_list_create, name='jobport-language-list-create'),
  path('languages/<int:pk>/', api_jobportal.jobport_language_detail, name='jobport-language-detail'),
  
  # Department Master APIs
  path('departments/', api_role.jobport_department_list_create, name='jobport-department-list-create'),
  path('departments/<int:pk>/', api_role.jobport_department_detail, name='jobport-department-detail'),
  
  #------------------------------
  path('bulk-upload-lead/', api_role.bulk_upload_lead, name='bulk_upload_lead'),
    
  path('lead_status_count/', api_role.get_lead_count_by_status, name='get_lead_count_by_status'),

  path('search_leads/', api_role.search_leads, name='search_leads'),
  path('filter_leads_dashboard/', api_role.filter_leads_dashboard, name='filter_leads_dashboard'),

  path('filter_leads_by_status_dashboard/', api_role.filter_leads_by_status_dashboard, name='filter_leads_by_status_dashboard'),
  path('get_all_leads_dashboard/', api_role.get_all_leads_dashboard, name='get_all_leads_dashboard'),
  
  path("filter_leads_export/", api_role.filter_leads_export, name="filter_leads_export"),
  path("filter_leads_by_status_export/", api_role.filter_leads_by_status_export, name="filter_leads_by_status_export"),
  path("get_all_leads_export/", api_role.get_all_leads_export),
  path("get_applied_jobs_jobseeker/", api_jobportal.get_applied_and_unapplied_jobs_jobseeker,name='get_applied_jobs_jobseeker'), 
  path("get_all_jobs_with_application_status/", api_jobportal.get_all_jobs_with_application_status,name='get_all_jobs_with_application_status'),
  path("get_jobseeker_profile_details/",api_jobportal.get_jobseeker_profile_details,name="get_jobseeker_profile_details",),

  path("education/", api_jobportal.get_educations, name="get_educations"),
  path("education-update/<int:pk>/", api_jobportal.update_education, name="update_education"),

  # Employment
  path("employment/", api_jobportal.get_employments, name="get_employments"),
  path("employment-update/<int:pk>/", api_jobportal.update_employment, name="update_employment"),

  # Work Preferences
  path("work-preferences/", api_jobportal.get_work_preferences, name="get_work_preferences"),
  path("work-preferences-update/<int:pk>/", api_jobportal.update_work_preference, name="update_work_preference"),

  path('add_lead_logs/<int:lead_id>/', api_role.get_lead_change_logs, name='get_lead_change_logs'),


  path('industries/', api_jobportal.industry_list, name='industry-list'),
  path('industries/<int:pk>/', api_jobportal.industry_detail, name='industry-detail'),
  path('industries/create/', api_jobportal.industry_create, name='industry-create'),
  path('industries/update/<int:pk>/', api_jobportal.industry_update, name='industry-update'),
  path('industries/delete/<int:pk>/', api_jobportal.industry_delete, name='industry-delete'),
  
  
  path('jobseekerprofile/<int:user_id>/', api_jobportal.get_jobseeker_profile, name='get_jobseeker_profile'),  
  path('jobseekerprofile/update/<int:user_id>/', api_jobportal.update_jobseeker_profile, name='update_jobseeker_profile'),  
  path('jobseekerprofile/delete/<int:user_id>/', api_jobportal.delete_jobseeker_profile, name='delete_jobseeker_profile'),  
  
  path("me/team-info/", api_views.my_team_info, name="me-team-info"),

  path("whatsapp/send/", WhatsAppSendView.as_view(), name="whatsapp_send"),
  
  
  path("source_status_summary/", api_role.source_status_summary, name="source_status_summary"),
  path("user_status_summary/", api_role.leads_user_status_summary, name="user_status_summary"),
  
  path("application_shortlist/<int:pk>", api_jobportal.application_shortlist,name="application_shortlist"),
  path("application_reject/<int:pk>", api_jobportal.application_reject,name="application_reject"),
  path("application_view_resume/<int:pk>", api_jobportal.application_view_resume,name="application_view_resume"),
  path("send_email_for_interview_details/<int:pk>", api_jobportal.send_email_for_interview_details, name="send_email_for_interview_details"),
  path('filter_students_all_register/',api_views.filter_students_all_register,name='filter_students_all_register'),
  path('filter_students_quick_register/',api_views.filter_students_quick_register,name='filter_students_quick_register'),
  path('filter_students_register_student/',api_views.filter_students_register_student,name='filter_students_register_student'),

path("student_form/<int:student_id>/", api_views.student_form, name="student_form"),
path('student_document/<int:student_id>/',  api_views.student_documents, name='student-documents'),
path('students/search/', api_views.search_student_by_name_email_mob_enroll_id, name='students_search'),

path("get_courses/", api_views.list_courses, name="list_courses"),
path("get_streams/", api_views.list_streams_by_course, name="list_streams_by_course"),

path('students_by_stream/', api_views.students_by_course_stream, name='students_by_course_stream'),
path('student-fees/<int:student_id>/', api_views.get_student_fees, name='get_student_fees'),
path("student-fees-update-by-sem/<int:student_id>/", api_views.update_student_fees_by_sem, name="update_student_fees_by_sem"),
path("get-payment-receipt/<int:student_id>/", api_views.payment_receipt, name="payment_receipt"),
path("create-payment-receipts/", api_views.create_payment_receipt, name="payment-receipt-create"),

path("bootstrap/student-register/", views_bootstrap.student_register_bootstrap, name="student-register-bootstrap"),
path("lead_bootstrap/", views_bootstrap.lead_bootstrap, name="lead-bootstrap"),

path("universities-with-courses/", api_views.universities_with_courses, name="universities-with-courses"),

path('get_uploaded_files/', api_views.get_uploaded_files, name='get_uploaded_files'),
# path('download_original_file/<int:file_id>/', api_views.download_exam_data_excel, name='download_exam_data_excel'),

path('download_exam_data_excel/', api_views.download_exam_data_excel, name='download_exam_data_excel'),

path('delete_uploaded_file/<int:file_id>/', api_views.delete_uploaded_file, name='delete_uploaded_file'),
path('delete_student/<int:user_id>/', api_views.delete_user_and_student, name='delete_student'),
path('delete_examination/<int:exam_id>/', api_views.delete_examination, name='delete_examination'),

path('delete_exam_file_upload/<int:file_upload_id>/', api_views.delete_exam_file_upload, name='delete_exam_file_upload'),


path('payment_receipt_details/', api_views.payment_receipt_details, name='payment_receipt_details'),

path("students/search-any-quick/", api_views.search_students_by_any_quick, name="students-search-any-quick"),
path("students/search-any-register/", api_views.search_students_by_any_register, name="students-search-any-register"),



path("students/lookup-one/", api_views.lookup_student_by_q_with_university, name="students-lookup-one"),
path("result-report-grouped/", api_views.result_report_grouped, name="result-report-grouped"),

path("create_payment_receipt_edit/", api_views.create_payment_receipt_edit, name="create_payment_receipt_edit"),

path("students/mark-pending-fbv/<int:student_id>/", api_views.mark_student_pending, name="mark-student-pending-fbv"),

path("approve_student/<int:student_id>/", api_views.approve_student, name="approve_student"),

path("pending_verification_student/",api_views.pending_verification_student,name="pending_verification_student"),

path('list_additional_receipts/', api_views.list_additional_receipts, name='list_additional_receipts'),
path('create_additional_receipt/', api_views.create_additional_receipt, name='create_additional_receipt'),
path('get_additional_receipt/<int:pk>/', api_views.get_additional_receipt, name='get_additional_receipt'),
path('update_additional_receipt/<int:pk>/', api_views.update_additional_receipt, name='update_additional_receipt'),
path('delete_additional_receipt/<int:pk>/', api_views.delete_additional_receipt, name='delete_additional_receipt'),
path('send_additional_receipt/', api_views.send_additional_receipt, name='send_additional_receipt'),
path('create_refund_receipt/', api_views.create_refund_receipt, name='create_refund_receipt'),

path('create_university_reregistration_examfee/', api_views.create_university_reregistration_Examfee, name='create_university_reregistration_examfee'),

path('university-reregistration-fees/list/', api_views.list_university_reregistration_fees, name='list-university-rereg-fee'),

path('university-reregistration-fees/<int:pk>/', api_views.update_university_reregistration_fee, name='update-university-rereg-fee'),

path('university-reregistration-fees-delete/<int:pk>/', api_views.delete_university_reregistration_fee, name='update-university-rereg-fee-delete'),

path('university-re-registration-fees/', api_views.create_university_re_registration_fee, name='create-university-re-reg-fee'),
path('university-re-registration-fees/list/', api_views.list_university_re_registration_fees, name='list-university-re-reg-fee'),
path('university-re-registration-fees/<int:pk>/', api_views.update_university_re_registration_fee, name='update-university-re-reg-fee'),

  path('student-documents/', api_views.create_student_document, name='create-student-document'),
  
  path('student-documents/list/', api_views.list_student_documents, name='list-student-documents'),

  # PersonalDocuments
  path('personal-documents/', api_views.create_personal_document, name='create-personal-document'),
  path('personal-documents/list/', api_views.list_personal_documents, name='list-personal-documents'),

  path('create_qualification/', api_views.create_qualification, name='create_qualification'),
  path('list_qualifications', api_views.list_qualifications, name='list_qualifications'),
  path('update_qualification/<int:pk>/', api_views.update_qualification, name='update_qualification'),
  path('delete_qualification/<int:pk>/', api_views.delete_qualification, name='delete_qualification'),
  path('get_additional_payment_exclude_refund/', api_views.get_additional_payment_exclude_refund, name='get_additional_payment_exclude_refund'),
  path('update_payment_status/<int:payment_id>/', api_views.update_payment_status, name='update_payment_status'),
  path('student-profile-image/<int:student_id>/', api_views.get_student_profile_image, name='get_student_profile_image'),
  path('update-student-profile-image/<int:student_id>/', api_views.update_student_profile_image, name='update_student_profile_image'),

  path('send-fees-request-email/', api_views.send_fees_request_email, name='send_fees_request_email'),
  path('send-reminder-email/', api_views.send_reminder_email, name='send-reminder-email'),
    # Create
    path('student-forms/create/', api_views.create_student_form, name='create-student-form'),
    
    # Read - All forms with filtering
    path('student-forms/', api_views.get_all_forms, name='get-all-forms'),
    
    # Read - Forms by type (FIXED: This matches your frontend URL pattern)
    path('student-forms/type/<str:form_type>/', api_views.get_forms_by_type, name='forms-by-type'),
    
    # Read - Student specific forms
    path('student-forms/student/<str:student_id>/', api_views.get_student_forms, name='student-forms'),
    
    # Read - Single form detail
    path('student-forms/<int:form_id>/', api_views.get_form_detail, name='form-detail'),
    
    # Update
    path('student-forms/<int:form_id>/update/', api_views.update_student_form, name='update-form'),
    
    # Delete
    path('student-forms/<int:form_id>/delete/', api_views.delete_student_form, name='delete-form'),
    
    # Form types
    path('form-types/', api_views.get_form_types, name='form-types'),

    path('call-recordings/', api_views.get_call_recordings, name='get_call_recordings'),
    
    # Drive folders management
    path('drive-folders/', api_views.get_drive_folders, name='get_drive_folders'),
    path('drive-folders/add/', api_views.add_drive_folder, name='add_drive_folder'),
    
    path('sync/logs/', api_views.get_sync_logs, name='get_sync_logs'),
    path('sync/status/', api_views.get_sync_status, name='get_sync_status'),
    
    # Playback
    path('playback/log/', api_views.log_playback, name='log_playback'),
    path('playback/logs/', api_views.get_playback_logs, name='get_playback_logs'),


]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
