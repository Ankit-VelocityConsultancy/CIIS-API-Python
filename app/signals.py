from django.contrib.auth.signals import user_logged_in,user_logged_out,user_login_failed
from django.dispatch import receiver
from .models import Status
from  datetime import datetime

@receiver(user_logged_in)
def log_user_login(sender,request,user, **kwargs):
    print("user logged in")
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("date and time =", dt_string)
    try:
        status = Status.objects.get(user=user.id)
        status.status = "Active"
        status.last_login = dt_string
        status.save()
    except Status.DoesNotExist:
        status = Status(user=user.id,status="Active",last_login=dt_string)
        status.save()


@receiver(user_login_failed)
def log_user_login_failed(sender,credentials,request,**kwargs):
    print("user login failed")

@receiver(user_logged_out)
def log_user_logout(sender,request,user, **kwargs):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    try:
        status = Status.objects.get(user=user.id)
        status.status = "Offline"
        status.last_logout = dt_string
        status.save()
    except Status.DoesNotExist:
        status = Status(user=user.id,status="Offline",last_logout=dt_string)
        status.save()