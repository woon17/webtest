from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .models import Report
from django.utils import timezone
import datetime
import requests
from .scannerService import api_key

def updateDatabase():
    now = timezone.localtime(timezone.now())
    print(f'\nnow: {now}')
    for re in Report.objects.all():
        print(f're: {re}\n')
        targetResponse = requests.get('https://www.virustotal.com/api/v3/files/{}'.format(re.SHA_256), headers={'x-apikey': api_key})
        if targetResponse.status_code == 200:
            stats = targetResponse.json()['data']['attributes']['last_analysis_stats']
        re.modifiedAt = now
        re.stats = stats
        re.save()


def getTask():
    scheduler = BackgroundScheduler()
    LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    if str(LOCAL_TIMEZONE) == 'Malay Peninsula Standard Time':
        scheduler.add_job(updateDatabase, CronTrigger.from_crontab("00 00 * * *"))
    else:
        scheduler.add_job(updateDatabase, CronTrigger.from_crontab("00 16 * * *"))
    scheduler.start()
