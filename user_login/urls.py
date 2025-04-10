from django.urls import path
from . views import *

urlpatterns = [
    path('profile/',StudentProfile,name="profile"),
    path('dashboard/',StudentDashboard,name="studentdashboard"),
    path('study_materials/',StudentStudyMaterial,name="StudentStudyMaterial"),
    path('video_materials/',StudentVideoMaterial,name="StudentVideoMaterial"),
    

]