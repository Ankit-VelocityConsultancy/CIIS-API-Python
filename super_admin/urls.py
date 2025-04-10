from django.urls import path
from .views import *
from .registeredstudents import *
from .views_others import *

urlpatterns = [
    path('',index,name="index"),
    path('home/',home,name="home"),
    path('overview/',Overview,name="overview"),
    path('login/',ULogin,name="login"),
    path('logout/',ULogout,name="logout"),
    path('change_password/',ChangePassword,name="change_password"),
    path('forgot_password/',ForgotPassword,name="forgot_password"),
    path('test/',Test,name="test"),
    path('university/',AddUniversity,name="adduniversity"),
    path('course/',AddCourse,name="addcourse"),
    path('stream/',AddStream,name="addstream"),


    path('streamfees/',AddStreamFees,name="addstreamfees"),
    path('studentfees/',EditOldStudentFees,name="studentfees"),

    path('addstudent/',AddStudent,name="addstudent"),
    path('quickregistration/',AddStudentQuick,name="quickaddstudent"),
    path('savestudent/',SaveStudent,name="savestudent"),
    path('check_mobile_unique/',check_mobile_unique,name="check_mobile_unique"),
    path('check_email_unique/',check_email_unique,name="check_email_unique"),
    
    path('pending/',PendingStudentVerification,name="pending_verification"),
    path('testing_api/',testing_api,name="testing_api"),
    path('pending_fees/',PendingStudentVerification_fees,name="pendingverification_fees"),
    path('pending_fees_view/',PendingStudentVerification_fees_viewreciept,name="pendingverification_feesview"),
    path('pending_get_documents/',PendingStudentVerification_get_documents,name="pendingverification_getdocuments"),
    
    
    path('registered/',RegisteredStudent,name="registered"),
    path('registered_api/',RegisteredStudentApi,name="registered_api"),
    path('advancesearch/',AdvanceSearch,name="advancesearch"),
    path('cancelledstudents/',CancelledStudent,name="cancelledstudents"),
    path('usercreation/',UserCreation,name="usercreation"),
    path('printaddress/',PrintAddress,name="printaddress"),

    path('registered_get_fees/',registered_get_fees,name="registered_get_fees"),
    path('registered_view_fees/',registered_view_fees,name="registered_view_fees"),
    path('registered_show_common_fees/',registered_show_common_fees,name="registered_show_common_fees"),
    path('registered_show_additional_fees/',registered_show_additional_fees,name="registered_show_additional_fees"),
    path('registered_edit_payment_reciept/',registered_edit_payment_reciept,name="registered_edit_payment_reciept"),
    path('register_edit_payment_reciept_save/',register_edit_payment_reciept_save,name="register_edit_payment_reciept_save"),
    path('registered_get_common_fees_details/',registered_get_common_fees_details,name="registered_get_common_fees_details"),
    path('registered_save_common_fees_details/',registered_save_common_fees_details,name="registered_save_common_fees_details"),
    path('registered_save_extra_fees/',registered_save_extra_fees,name="registered_save_extra_fees"),
    path('registered_get_idcard/',registered_get_idcard,name="registered_get_idcard"),
    path('registered_request_fees/',registered_request_fees,name="registered_request_fees"),
    path('registered_fetch_message_request_fees/',registered_fetch_message_request_fees,name="registered_fetch_message_request_fees"),
    path('registered_enroll_to_next_semyear/',registered_enroll_to_next_semyear,name="registered_enroll_to_next_semyear"),
    path('registered_save_enrollment_to_next_semyear/',registered_save_enrollment_to_next_semyear,name="registered_save_enrollment_to_next_semyear"),
     path('registered_result_uploaded/',registered_result_uploaded,name="registered_result_uploaded"),
    path('registered_university_exam_fee/',registered_university_exam_fee,name="registered_university_exam_fee"),
    path('registered_university_re_registration/',registered_university_re_registration,name="registered_university_re_registration"),
    path('registered_show_personal_documents/',registered_show_personal_documents,name="registered_show_personal_documents"),
    path('registered_get_qualification_documents/',registered_get_qualification_documents,name="registered_get_qualification_documents"),
    path('registered_get_remarks/',registered_get_remarks,name="registered_get_remarks"),
    path('registered_new_university_enrollment_number/',registered_new_university_enrollment_number,name="registered_new_university_enrollment_number"),
    path('registered_old_university_enrollment_number/',registered_old_university_enrollment_number,name="registered_old_university_enrollment_number"),
    path('registered_courier_details/',registered_courier_details,name="registered_courier_details"),
    path('registered_update_payment_status/',registered_update_payment_status,name="registered_update_payment_status"),
    path('registered_cancel_student/',registered_cancel_student,name="registered_cancel_student"),
    path('registered_payment_gateway/',registered_payment_gateway,name="registered_payment_gateway"),    
    path('setexamination/',SetExamination,name="setexamination"),
    path('setexam/',SetExam,name="setexam"),
    path('exam/',GiveExamination,name="giveexamination"),
    path('examsubmitted/',ExamSubmitted,name="examsubmitted"),
    path('checkresult/',CheckResult,name="checkresult"),

    path('verify_examination_import_upload/',verify_examination_import_upload,name="verify_examination_import_upload"),
    path('examination_login/',examination_login,name="examination_login"),
    
    path('examination/',ExaminationThroughLink,name="examination_through_link"),
    path('import_student/',ImportStudent,name="import_student"),
    path('validate_student_import_file/',ValidateStudentImportFile,name="validate_student_import_file"),

    path('edit/<int:enroll_id>/',EditStudent,name="editstudent"),
    path('saveEditStudent/',saveEditStudent,name="saveEditStudent"),
    path('change_course/',changeStudentCourse,name='changeStudentCourse'),

    path('deletearchive/<int:enroll_id>/',DeleteArchive,name="deletearchive"),




    path('paymentsuccess/',PaymentSuccess,name="paymentsuccess"),



    path('export_excel/<str:student_ids>', export_users_xls, name='export_excel'),
    path('export_pdf/<str:student_ids>', export_pdf, name='export_pdf'),
    path('changecourse/', changecourse, name='changecourse'), ## added by Avani
    path('viewquickregister/', viewquickregister, name='viewquickregister'), ## added by Avani
    path('viewregister/', viewregister, name='viewregister'), ## added by Avani
    path('viewpaymentstatus/', viewpaymentstatus, name='viewpaymentstatus'), ## added by Avani
    path('savechangecourse/', savechangecourse, name='savechangecourse'), ## added by Avani
    path('showstudentform/<int:enroll_id>', showstudentform, name='showstudentform'), ## added by Avani
    path('documentmanagement/<int:enroll_id>', documentmanagement, name='documentmanagement'), ## added by Avani
    path('paymentmode/', paymentmode, name='paymentmode'), ## added by Avani
    path('editpaymentmode/', editpaymentmode, name='editpaymentmode'), ## added by Avani
    path('deletepaymentmode/', deletepaymentmode, name='deletepaymentmode'), ## added by Avani
    path('feereceiptoption/', feereceiptoption, name='feereceiptoption'), ## added by Avani
    path('editfeereceiptoption/', editfeereceiptoption, name='editfeereceiptoption'), ## added by Avani
    path('deletefeereceiptoption/', deletefeereceiptoption, name='deletefeereceiptoption'), ## added by Avani
    path('bankname/', bankname, name='bankname'), ## added by Avani
    path('editbankname/', editbankname, name='editbankname'), ## added by Avani
    path('deletebankname/', deletebankname, name='deletebankname'), ## added by Avani
    path('sessionname/', sessionname, name='sessionname'), ## added by Avani
    path('editsessionname/', editsessionname, name='editsessionname'), ## added by Avani
    path('deletesessionname/', deletesessionname, name='deletesessionname'), ## added by Avani
    path('substream/', addsubstream, name='addsubstream'), ## added by Avani
    path('getstream/', getstream, name='getstream'), ## added by Avani
    path('updatesubstream/', updatesubstream, name='updatesubstream'), ## added by Avani
    path('deletesubstream/', deletesubstream, name='deletesubstream'), ## added by Avani
    path('getsubstream/', getsubstream, name='getsubstream'), ## added by Avani
    path('others/addstudent/', addothersstudent, name='addothersstudent'), ## added by Avani
    path('saveothersstudent/', saveothersstudent, name='saveothersstudent'), ## added by Avani
    path('getcourse/', getcourse, name='getcourse'), ## added by Avani
    path('others/viewstudents/', viewregisterother, name='viewregisterother'), ## added by Avani
    path('others/edit/<int:enroll_id>/',EditOtherStudent,name="editotherstudent"),
    path('saveEditOtherStudent/',saveEditOtherStudent,name="saveEditOtherStudent"),
    path('showallstudents/',showallstudents,name="showallstudents"),
    path('others/showstudents/',showstudents,name="showstudents"),
    path('others_registered_get_fees/',others_registered_get_fees,name="others_registered_get_fees"),
    path('others_registered_view_fees/',others_registered_view_fees,name="others_registered_view_fees"),
    path('others_registered_get_common_fees_details/',others_registered_get_common_fees_details,name="others_registered_get_common_fees_details"),
    path('save_more_fees_others/',save_more_fees_others,name="save_more_fees_others"),
    path('other_edit_payment_reciept/', other_edit_payment_reciept, name='other_edit_payment_reciept'),
    path('other_edit_payment_reciept_save/', other_edit_payment_reciept_save, name='other_edit_payment_reciept_save'),
    path('others/deletestudent/<int:enroll_id>/', DeleteOtherStudent, name='deleteotherstudent'),
    path('others/showstudentform/<int:enroll_id>', showstudentformothers, name='showstudentformothers'), ## added by Avani
    path('others/documentmanagement/<int:enroll_id>', documentmanagementothers, name='documentmanagementothers'), ## added by Avani
    
]