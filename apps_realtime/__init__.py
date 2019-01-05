import click
from .pre_trade.socket_pre_trade import run_socket_pre_trade
from .initdb import Base, engine, db_session
def init_db():
    """Initiate all database. This should be use one time only
    """
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from .pre_trade import models
    Base.metadata.create_all(bind=engine)
from .crontab import crontab
@click.command()
@click.option('--env', default='env', help='Setup enviroment variable.')
def main(env='env'):
    """Running method for Margin call app
    
    Keyword Arguments:
        env {str} -- Can choose between initdb, PROD, or ENV/nothing. 'initdb' will create database table and its structures, use onetime only .PROD only change debug variable in webapp to true (default: {'ENV'})
    """
    if env == 'initdb':
        init_db()
    else:
        if env == 'test1':
            print('Test all exercises, enviroment =', env)
            from .testing import ex2
            ex2.main()
            return
            # ex4.main()
            # ex5.main()
            # testing_order.main()
        if env == 'consumer':
            print('Test all exercises, enviroment =', env)
            from .pre_trade.kafka import consumer
            consumer.main()
        else:
            run_socket_pre_trade()
