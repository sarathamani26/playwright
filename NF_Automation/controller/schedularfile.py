from datetime import timedelta
import datetime

from django.http import JsonResponse

from webscraping.settings import logger
from NF_Automation.controller.backgroundschedular import BackgroundScheduler
from django import db

from NF_Automation.util import VysfinList


def automation_schedular(testcasecode,client,testcase_id):
    current_time = datetime.datetime.now() + timedelta(seconds=5)
    sched = BackgroundScheduler()
    h=current_time.hour
    m=current_time.minute
    s=current_time.second
    logger.info('trigger scheduler')
    sched.add_job(db_scheduler_process, 'cron',hour=h,minute=m,second =s,args=[testcasecode,client,testcase_id])
    sched.start()
    return [{"key": "Automation Starts"}]


def db_scheduler_process(testcasecode,client,testcase_id):
    from NF_Automation.service.NF_ECF_service import NFECF
    try:
        logger.info('triggered fileinsert')
        NFECF().nf_vendor_creationdr(testcasecode,client,testcase_id)
    finally:
        db.connections['scheduler'].close()
    return

# def schedular_stop(request)
#     db.connections['scheduler'].close()
#     return JsonResponse {"key":"Automation Stoped"}
