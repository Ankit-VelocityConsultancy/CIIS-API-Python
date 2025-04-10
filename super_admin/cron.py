from datetime import datetime

# from apscheduler.schedulers.background import BackgroundScheduler

# scheduler = BackgroundScheduler()

# def my_cron_job():
#     # Add your cron job logic here
#     # For example, let's print a message to the console
#     f = open("insert_file.txt", "a")
#     f.write(f"{str(datetime.now())} :\n")
#     f.close()
#     print("Cron job executed successfully!")

# scheduler.add_job(my_cron_job, 'cron', minute='*')  # Run every minute
# scheduler.start()

# def doCron():
    # f = open("demofile2.txt", "a")
    # f.write(f"{str(datetime.now())} :\n")
    # f.close()
#     # Add your cron job logic here
#     # For example, let's print a message to the console
#     print("Cron job executed successfully!")
    
# from django_crontab import CronJobBase, Schedule

# class MyCronJob(CronJobBase):
#     schedule = Schedule(run_every_minute=True)
#     code = 'myapp.my_cron_job'  # Specify the path to your cron job function

#     def do(self):
#         f = open("demofile2.txt", "a")
#     #     f.write(f"{str(datetime.now())} :\n")
#     #     f.close()
#         # Add your cron job logic here
#         # For example, let's print a message to the console
#         print("Cron job executed successfully!")

# def my_cron_job():
#     MyCronJob().do()