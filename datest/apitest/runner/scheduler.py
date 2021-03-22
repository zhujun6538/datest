"""
@project: PyCharm
@author: MZM
@file: scheduler.py
@ide: PyCharm
@time: 2021/3/21 17:09
@desc： 
"""
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_job

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), 'apitest')
scheduler.start()