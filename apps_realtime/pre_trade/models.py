from sqlalchemy import ForeignKey
from sqlalchemy import asc, desc, func
from sqlalchemy.sql.expression import and_, or_, exists
from sqlalchemy import Column, Integer, Unicode, String, DateTime, Boolean, Numeric, Text, Date, UniqueConstraint, UnicodeText, Index, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
import json
import datetime
from ..initdb import Base, db_session
import uuid, random
from ..ulib import obj_to_dict
from passlib.apps import custom_app_context as pwd_context


class BaseModel(object):
    __tablename__ = 'BaseModel'
    id = Column(Integer, primary_key=True)
    live = Column(Boolean,  nullable=False, default=True)
    createAt = Column(DateTime,   nullable=False, default=datetime.datetime.now, index=True)

    @staticmethod
    def to_dict(row):
        d = obj_to_dict(row)
        return d

    def __repr__(self):
        return '<%s is: id= %r>' % (self.__tablename__, self.id)

class ExecutionReport(BaseModel, Base):
    __tablename__ = 'ExecutionReport'

    id = Column(Integer, primary_key=True)
    # Account no
    Account = Column(String(40), nullable=False)
    ClOrdID = Column(String(40), nullable=False)
    OrderID = Column(String(40), nullable=False)
    DisplayName = Column(String(255), nullable=False)
    UserID = Column(Integer, nullable=False)
    OrigClOrdID = Column(String(40),nullable=False)
    OrderQty = Column(Float,nullable=False)
    LeavesQty= Column(Float,nullable=False)
    CumQty= Column(Float,nullable=False)
    OrdType = Column(String(40),nullable=False, default= "LO")
    OrdStatus = Column(String(40),nullable=False)
    Price = Column(Float,nullable=False)
    Symbol = Column(String(40), nullable=False, index=True)
    Side = Column(String(20), nullable=False, index=True)
    Currency = Column(String(20),  nullable=False, index=True)
    AllocSettlCurrency = Column(String(20),  nullable=False, index=True)
    TimeInForce = Column(String(20),  nullable=False, index=True)
    TransactTime = Column(DateTime, nullable=False, index=True)
    Commission = Column(Float,nullable=False)
    AllocAccount = Column(String(40), nullable=False, index=True)
    SecondaryOrderID = Column(String(40), nullable=False, index=True)
    execution_style = Column(String(40), nullable=False, index=True)
    
    createAt = Column(DateTime, nullable=False, default=datetime.datetime.now, index=True)
    updateAt = Column(DateTime, nullable=False, default=datetime.datetime.now, index=True)

    def __init__(self,Account=None,ClOrdID=None,OrderID=None,OrigClOrdID=None,OrderQty=None,LeavesQty=None,CumQty=None,OrdType=None,
                    OrdStatus=None,Price=None,Symbol=None,Side=None,Currency=None,AllocSettlCurrency=None,TimeInForce=None,TransactTime=None,
                    Commission=None, AllocAccount=None,SecondaryOrderID=None,execution_style=None,DisplayName=None, UserID=None):
        self.Account = Account
        self.ClOrdID = ClOrdID
        self.OrderID = OrderID
        self.OrigClOrdID = OrigClOrdID
        self.OrderQty = OrderQty
        self.LeavesQty = LeavesQty
        self.CumQty = CumQty
        self.OrdType = OrdType
        self.OrdStatus = OrdStatus
        self.Price = Price
        self.Symbol = Symbol
        self.Side = Side
        self.Currency = Currency
        self.AllocSettlCurrency = AllocSettlCurrency
        self.TimeInForce = TimeInForce
        self.TransactTime = TransactTime
        self.Commission = Commission
        self.AllocAccount = AllocAccount
        self.SecondaryOrderID = SecondaryOrderID
        self.execution_style = execution_style
        self.DisplayName = DisplayName
        self.UserID = UserID

class TransactionTrading(BaseModel, Base):
    __tablename__ = 'TransactionTrading'

    id = Column(Integer, primary_key=True)
    # Account no
    TradeReportID = Column(String(40), nullable=False)
    Commission = Column(Float, nullable=False)
    LastQty = Column(Float,nullable=False)
    LastPx = Column(Float,nullable=False)
    TransactTime= Column(DateTime,nullable=False)
    Side= Column(String(40),nullable=False)
    Symbol = Column(String(40),nullable=False, default= "LO")
    OrderID = Column(String(40),nullable=False)
    SecondaryOrderID = Column(String(40),nullable=False)
    Account = Column(String(40), nullable=False, index=True)
    Currency = Column(String(20),  nullable=False, index=True)
    Quantity = Column(Float,  nullable=False, index=True)
    AllocAccount = Column(String(40),nullable=False)
    AllocSettlCurrency = Column(String(40), nullable=False, index=True)
    AllocQty = Column(Float, nullable=False, index=True)

    createAt = Column(DateTime, nullable=False, default=datetime.datetime.now, index=True)
    updateAt = Column(DateTime, nullable=False, default=datetime.datetime.now, index=True)

    def __init__(self,TradeReportID=None,Commission=None,LastQty=None,LastPx=None,TransactTime=None,Side=None,Symbol=None,OrderID=None,
                SecondaryOrderID=None,Account=None,Currency=None,Quantity=None,AllocAccount=None,AllocSettlCurrency=None,AllocQty=None):
        self.TradeReportID = TradeReportID
        self.Commission = Commission
        self.LastQty = LastQty
        self.LastPx = LastPx
        self.TransactTime = TransactTime
        self.Side = Side
        self.Symbol = Symbol
        self.OrderID = OrderID
        self.SecondaryOrderID = SecondaryOrderID
        self.Account = Account
        self.Currency = Currency
        self.Quantity = Quantity
        self.AllocAccount = AllocAccount
        self.AllocQty = AllocQty
        self.AllocSettlCurrency = AllocSettlCurrency
    
    @staticmethod
    def view_account_transaction(parameter_list):
        pass

    @staticmethod
    def open_account_transactio(parameter_list):
        pass

    @staticmethod
    def cancel_account_transactio(parameter_list):
        pass

    @staticmethod
    def process_account_transactio(parameter_list):
        pass 

class User(BaseModel, Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    username = Column(String(250), unique=True, nullable=False)
    password = Column(String(250), nullable=False)

    passwordresettoken = Column(String(250),default='')
    passwordresetexpires = Column(DateTime,default=datetime.datetime.utcnow)
    confirmed = Column(Boolean, default=False)
    confirmed_on = Column(DateTime)
    email = Column(String(250), unique=True, nullable=False)
    phone = Column(String(30), unique=True, nullable=False,default='')
    facebook = Column(String(250),default='')
    google = Column(String(250),default='')
    linkin = Column(String(250),default='')

    live = Column(Boolean, default=True, nullable=False)
    createAt = Column(DateTime, nullable=False,
                           default=datetime.datetime.utcnow)
    updateAt = Column(DateTime, nullable=False,
                           default=datetime.datetime.utcnow)
    
    role = Column(String(125), nullable=False)

    def __init__(self, username, password, email,role):
        """[Create New User for T-Rex]
        
        Arguments:
            username {[string]} -- [user name user login]
            password {[type]} -- [Password for user login]
            email {[type]} -- [Email regist t-rex exchange]
            role {[type]} -- [Role of user]
        """
        self.username = username
        self.password = password
        self.email = email
        self.role = role

    def __repr__(self):
        return '<User %r>' % self.username
    
    @staticmethod
    def hash_password(password):
        return pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

class Account(BaseModel, Base):
    __tablename__ = 'Account'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer)
    account_no = Column(String(32), unique=True, nullable=False)
    subkey = Column(String(255),  nullable=False, index=True)
    description = Column(String(255),  nullable=False)
    type = Column(String(10),  nullable=False, index=True)
    currency = Column(String(10),  nullable=False, index=True)
    balance = Column(Float, nullable=False, default=0, index=True)
    subkey_id = Column(Integer, nullable=False)
    lastest_transaction_id = Column(Integer, nullable=False)
    
    live = Column(Boolean,  nullable=False, default=True)
    createAt = Column(DateTime,   nullable=False, default=datetime.datetime.now, index=True)
    updateAt = Column(DateTime,   nullable=False, default=datetime.datetime.now, index=True)

    def __init__(self, user_id, account_no, type='0001', description='', currency='VND', balance=0.0,subkey_id=0,lastest_transaction_id=0 ):
        self.user_id = user_id
        self.account_no = account_no
        self.subkey = uuid.uuid4().hex # will replace by real subkey later
        self.type = type
        self.description = description
        self.currency = currency
        self.balance = balance
        self.subkey_id = subkey_id
        self.lastest_transaction_id = lastest_transaction_id

    @staticmethod
    def view_account_all():
        with db_session() as session:
            list_query = session.query(Account).filter(
                Account.live == True).order_by(Account.createAt.desc())
            full_accs = [Account.to_dict(row) for row in list_query]
        return full_accs
    
    @staticmethod
    def view_account(account_no):
        with db_session() as session:
            list_query = session.query(Account).filter(Account.account_no == account_no,
                Account.live == True).order_by(Account.createAt.desc())
            full_accs = [Account.to_dict(row) for row in list_query]
        return full_accs
    
    @staticmethod
    def hide_account(parameter_list):
        pass

