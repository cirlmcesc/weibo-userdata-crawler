# -*- coding: utf-8 -*-

""" mysqldb connect package Pedoo """

import functools
import time
try:
    import MySQLdb
except ImportError:
    import pymysql as MySQLdb


class MySQLConnect(object): 
    """ MySQL connect"""
    
    sql_statement_log = []
    last_execute_sql = ""

    def __init__(self, db_connect={}, db_config={}):
        if len(db_connect) > 0:
            self.db_connect = db_connect
            self.db = db_connect.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        elif len(db_connect) == 0 and len(db_config) > 0:
            MySQLConnect.getDBConnect(db_config)

    @classmethod
    def getDBConnect(cls, db_config):
        cls.db_connect = MySQLdb.connect(
            host=db_config.get("host", ""), user=db_config.get("user", ""), 
            passwd=db_config.get("password", ""), db=db_config.get("db", ""), 
            charset=db_config.get("charset", ""))
        cls.db = MySQLConnect.db_connect.cursor(
            cursorclass=MySQLdb.cursors.DictCursor)
        
    def execute(self, sql=""):
        self.db.execute(sql)
        self.sql_statement_log.insert(-1, {time.time(): sql})
        self.last_execute_sql = sql

        return self.db.fetchall() if "SELECT" in sql else self.db_connect.commit()

    def log(self):
        return self.sql_statement_log


class ActionDispatcher(object):
    def CheckBaseClass(func):
        def checkclass(cls, *args):
            return func(cls, *args) if not ORMModel in cls.__bases__ else QueryBuilder(cls, *args)

        return checkclass

    @classmethod
    @CheckBaseClass
    def get(cls):
        print(cls)
        return cls

    @classmethod
    @CheckBaseClass
    def where(cls, *args):
        return cls


class QueryBuilder(ActionDispatcher):
    """ Query Builder """

    __ormmodel = ""
    __table_name = ""
    __fields = "*"
    __join = []
    __where = {
        "and": [],
        'or': [],
    }
    __order = []
    __final_sql = ""

    def __init__(self, ormmodel, table_name):
        self.__ormmodel = ormmodel
        self.__table_name = ormmodel.table_name

    def select(self, *fields):
        """ set select fields """

        if len(fields) == 1:
            self.__fields = fields[0]
        elif len(fields) > 1:
             self.__fields = ", ".join(fields)
  
        return self

    def buildSelectString(self):
        sql = "SElECT %s FROM %s" % (self.__fields, self.__table_name)

        return sql + self.__buildJoinString() + self.__buildWhereString() + self.__buildOrderString() + self.__buildLimitString

    def join(self, table, current_table_field, judge, target_table_field):
        pass

    def __buildJoinString(self):
        return " " + "JOIN ".join(self.__join)

    def where(self, field, judge, value):
        pass

    def between(self, from_condition, to_condition):
        pass

    def orWhere(self, field, judge, value):
        pass

    def like(self, field, cmp):
        pass

    def __buildWhereString(self):
        return ""

    def limit(self, offset, number):
        pass

    def __buildLimitString(self):
        return ""

    def orderBy(self, field, cmp):
        pass

    def __buildOrderString(self):
        return ""

    def get(self):
        return ResaultBuilder.query(MySQLConnect(), self.__ormmodel, self)

    def first(self):
        return ResaultBuilder.query(MySQLConnect(), self.__ormmodel, self, few=False)


class ResaultBuilder(object):
    """ Resault Builder """

    @classmethod
    def execute(cls, MySQLConnect, QueryBuilder):
        """ execute """

        return MySQLConnect.execute(QueryBuilder.getSQL())

    @classmethod
    def query(cls, MySQLConnect, ORMModel, QueryBuilder, few=True):
        """ query """

        resault = MySQLConnect.execute(QueryBuilder.buildSelectString())

        if len(resault) == 0:                                                                                   
            return [] if few else None

        if few:
            return list(map(lambda attributes: 
                cls.buildORMModelInstance(ORMModel, attributes), resault))
        else:
            return cls.buildORMModelInstance(ORMModel, resault[0])

    @classmethod
    def buildORMModelInstance(cls, ormmodel, attributes):
        """ build model instance """

        return ormmodel(attributes=attributes)


class ORMModel(ActionDispatcher):
    """ Action Model """

    table_name = ""
    fields = []

    def __init__(self, table_name="", attributes={}):
        if self.table_name == "" and table_name == "":
            self.table_name = self.__class__.__name__.lower()
        elif table_name != "":
            self.table_name = table_name
        
        if len(attributes) > 0:
            for attribute in attributes:
                self.__setattr__(self, attribute, attributes.get(attribute))

    def __setattr__(self, attr, value):
        fields = self.fields
        fields.insert(-1, attr)
        self.__dict__["fields"] = fields
        self.__dict__[attr] = value

    def __getattribute__(self, attr):
        pass

    @classmethod
    def get(cls):
        return QueryBuilder(cls, cls.table_name).get()

    @classmethod
    def first(cls):
        return QueryBuilder(cls, cls.table_name).first()

    def save(self):
        pass
