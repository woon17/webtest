from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .models import Report
from django.utils import timezone

def updateDatabase():
    now = timezone.localtime(timezone.now())
    print(f'\nnow: {now}')
    print("0000000000000000000000000000")
    for re in Report.objects.all():
        print(f're: {re}\n')
        

def getTask():
    scheduler = BackgroundScheduler()
    scheduler.add_job(updateDatabase, 
                      CronTrigger.from_crontab("* * * * *"))
    # scheduler.add_job(updateDatabase, 
    #                   'interval', seconds=20)
    scheduler.start()

    