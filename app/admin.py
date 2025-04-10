from django.contrib import admin
from .models import  Countries,States,Cities,StudentArchive,Course,Student,ImportCsvData,UserLevel,User,PaymentReciept,Stream,Qualification,Enrolled,StreamFees,University,Status,Examination,Questions,Result,AdditionalEnrollmentDetails,FeesDetails,Syllabus,Courier,StudentFees,TransactionDetails,SaveStudentTransaction,StudentDocuments,PersonalDocuments,PersonalDocumentsImages,EmailSentHistory
# Register your models here.

admin.site.register(Course)
admin.site.register(Student)
admin.site.register(User)
admin.site.register(ImportCsvData)
admin.site.register(UserLevel)
admin.site.register(Stream)
admin.site.register(Qualification)
admin.site.register(Enrolled)
admin.site.register(StreamFees)
admin.site.register(University)
admin.site.register(Status)
admin.site.register(Examination)
admin.site.register(Questions)
admin.site.register(Result)
admin.site.register(AdditionalEnrollmentDetails)
admin.site.register(PaymentReciept)
admin.site.register(StudentDocuments)
admin.site.register(FeesDetails)
admin.site.register(Syllabus)
admin.site.register(Courier)
admin.site.register(StudentFees)
admin.site.register(TransactionDetails)
admin.site.register(SaveStudentTransaction)
admin.site.register(PersonalDocuments)
admin.site.register(PersonalDocumentsImages)
admin.site.register(EmailSentHistory)
admin.site.register(StudentArchive)
admin.site.register(Countries)
admin.site.register(States)
admin.site.register(Cities)



