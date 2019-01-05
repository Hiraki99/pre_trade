import requests
from ..pre_trade.models import ExecutionReport,TransactionTrading 
from ..pre_trade.process import CollectData,mem
from ..initdb import db_session
from ..pre_trade.socket_pre_trade import celery
from celery.schedules import crontab

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(minute='*/2'),
        startUp.s()
    )
@celery.task
def startUp():
    print("--------Update All Balance with Order-------------")
    mem["data"] =CollectData()
