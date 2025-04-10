from django.urls import path
from . import views
# from dataentry.views import Index2
urlpatterns = [

    path('export_excel/<str:student_ids>', views.export_users_xls, name='export_excel'),
    path('export_pdf/<str:student_ids>', views.export_pdf, name='export_pdf'),
    
    path('test/',views.test,name="test"),
    path('home/',views.home,name="home"),
    path('',views.index,name="index"),
    
    path('overview/',views.Overview,name="overview"),
    path('readmission/',views.StudentReAdmission,name="readmission"),

    
    path('payment/',views.PayFees,name="payfees"),
    
    path('exam/',views.GiveExamination,name="giveexamination"),
    path('checkresult/',views.CheckResult,name="checkresult"),
    path('examsubmitted/',views.ExamSubmitted,name="examsubmitted"),

    path('addcourse/',views.AddCourse,name="addcourse"),
    path('addstream/',views.AddStream,name="addstream"),
    path('addsyllabus/',views.AddSyllabus,name="addsyllabus"),
    path('adduniversity/',views.AddUniversity,name="adduniversity"),
    path('streamfees/',views.AddStreamFees,name="streamfees"),
    path('setexam/',views.SetExam,name="setexam"),

    path('setexamination/',views.SetExamination,name="setexamination"),
    
    path('printaddress/',views.PrintAddress,name="printaddress"),
    
    path('registrationcash/',views.Registration_Cash,name="registrationcash"),
    
    
    path('addstudent/',views.AddStudent,name="addstudent"),
    path('quickregistration/',views.AddStudentQuick,name="quickaddstudent"),
    path('cancelledstudents/',views.CancelledStudent,name="cancelledstudents"),
    
    path('pending/',views.PendingVerification,name="pendingverification"),
    path('registered/',views.RegisteredStudent,name="registered"),
    path('addfees/',views.AddFees,name="addfees"),
    path('additionaldetail/',views.AddAdditionalDetails,name="additionaldetail"),
    path('editoldfees/',views.EditOldStudentFees,name="editoldfees"),
    
    
    
    path('editfees/',views.EditFees,name="editfees"),
    path('login/',views.ULogin,name="login"),
    path('pendingfees/',views.PendingFees,name="pendingfees"),
    path('paidfees/',views.PaidFees,name="paidfees"),
    path('studentreport/',views.StudentReport,name="studentreport"),
    
    
    
    
    path('import/',views.ImportCsv,name="import"),
    path('logout/',views.logout_page,name="logout"),
    
    path('usercreation/',views.UserCreation,name="usercreation"),
    path('advancesearch/',views.AdvanceSearch,name="advancesearch"),
    path('sendemail/',views.SendEmail,name="sendemail"),
    path('paymentsuccess/',views.PaymentSuccess,name="paymentsuccess"),
    path('paymentfailure/',views.PaymentFailure,name="paymentfailure"),
    path('getinvoice/<int:pk>',views.GetInvoice,name="getinvoice"),
    path('redirectmail/<int:pk>',views.RedirectMail,name="redirectmail"),
    
    path('payment/<str:identifier>',views.OnlinePayment,name="payment"),
    
    path('edit/<int:enroll_id>/',views.EditStudent,name="editstudent"),
    path('deletearchive/<int:enroll_id>/',views.DeleteArchive,name="deletearchive"),
    
    path('unarchive/',views.UnArchive,name="unarchive")
    
]