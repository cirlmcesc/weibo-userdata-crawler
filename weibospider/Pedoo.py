# -*- coding: utf-8 -*-

""" mysqldb connect package Pedoo """

import random
import time
try:
    import MySQLdb
except ImportError:
    import pymysql as MySQLdb

MYSQL_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "passwd": "",
    "db": "schema",
    "charset": "utf-8"
}

class MySQLConnect(object):
    """ MySQL connect"""

    execute_count = 0
    sql_statement_log = []
    last_execute_sql = ""
    db_connect = {}
    db = {}

    def CheckConnect(self, func):
        def execute(cls, *args):
            if not len(cls.db_connect) or cls.execute_count > 100:
                cls.connect(MYSQL_CONFIG)
                cls.execute_count = 0

            return func(*args)

        return execute

    @classmethod
    @CheckConnect
    def getDB(cls):
        return cls.db

    @classmethod
    @CheckConnect
    def getDBConnect(cls):
        return cls.db_connect

    @classmethod
    def connect(cls, db_config):
        """ set db connect, example:
            db_config = {
                "host": "127.0.0.1",
                "user": "root",
                "passwd": "",
                "db": "schema",
                "charset": "utf-8"
            }
        """

        cls.db_connect = MySQLdb.connect(**db_config)
        cls.db = cls.db_connect.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    @classmethod
    @CheckConnect
    def execute(cls, sql=""):
        """ execute sql """

        cls.db.execute(sql)
        cls.sql_statement_log.append({time.time(): sql})
        cls.last_execute_sql = sql
        cls.execute_count = cls.execute_count + 1

        if sql.upper().replace(" ", "").startswith("SELECT"):
            return cls.db.fetchall()

        return cls.db_connect.commit()

    @classmethod
    def log(cls):
        """ sql execute log"""

        return cls.sql_statement_log


class QueryBuilder(object):
    """ Query Builder """

    _ormmodel = ""
    _table_name = ""
    _fields = "*"
    _join = []
    _where = []
    _order = []
    _limit = ""
    _final_sql = ""

    def __init__(self, ormmodel):
        self._ormmodel = ormmodel
        self._table_name = ormmodel.table_name

    def select(self, *fields):
        """ set select fields """

        if not len(fields):
            self._fields = "*"
        elif len(fields) > 1:
            self._fields = "id, " + (", ".join(fields))

        return self

    def BuildQuerySQLString(self):
        """ build sql string """

        sql = "SElECT %s FROM %s" % (self._fields, self._table_name)

        return sql + "".join(
            map(lambda condition: self._buildConditionString(condition), [
                "_join", "_where", "_order", "_limit"
            ]))

    def _buildConditionString(self, condition):
        """ build condition string """

        def transConditionString():
            """ transformation condition string """

            if condition == "_order":
                return " ORDER BY "

            return " %s " % condition.replace("_", " ").upper()

        content = getattr(self, condition)
        joinstring = ", " if condition == "_order" else " "
        startstring =  " " if condition != "join" else transConditionString()

        if isinstance(content, str):
            return content

        return (startstring + joinstring.join(content)) if len(content) else ""

    def join(self, table, current_table_field, target_table_field, **kw):
        """ join """

        self._join.append("%s %s ON %s = %s" % (
            "INNER JOIN" if not len(kw) else kw["_cmp"],
            table, current_table_field, target_table_field))

        return self

    def leftJoin(self, table, current_table_field, target_table_field):
        """ left join """

        return self.join(table, current_table_field, target_table_field, _cmp="LEFT JOIN")

    def rightJogin(self, table, current_table_field, target_table_field):
        """ right join """

        return self.join(table, current_table_field, target_table_field, _cmp="RIGHT JOin")

    def where(self, field, *args, **kw):
        """ where """

        last_join_string_check = self._where[-1] != "AND" and self._where[-1] != "OR"

        if len(self._where) != 0 and last_join_string_check:
            self._where.append("AND" if not len(kw) else kw['_cmp'])

        if hasattr(field, "__call__"):
            builder = field(QueryBuilder(self._ormmodel))
            self._where.append("(%s)" % builder._buildConditionString("_where").replace(" WHERE ", ""))
        elif isinstance(field, list):
            for condition in field:
                self.where(*condition)
        else:
            _cmp = "=" if len(args) == 1 else args[0]
            value = args[0] if len(args) == 1 else args[1]
            restring = value.replace(" ", "")

            if (not isinstance(value, int) or
                    not restring.startswith("(") or
                    not restring.startswith("'") or
                    not restring.startswith("NULL")):
                value = "'%s'" % value

            self._where.append(" ".join((field, _cmp, value)))

        return self

    def orWhere(self, field, *args):
        """ or where """

        return self.where(field, *args, _cmp="OR")

    def whereIn(self, field, _tuple, **kw):
        """ where in """

        _cmp = "IN" if not len(kw) else kw["_cmp"]

        return self.where(field, _cmp, "('%s')" % ("' ,'".join(_tuple)))

    def whereNotIn(self, field, _tuple):
        """ where not in """

        return self.whereIn(field, _tuple, _cmp="NOT IN")

    def whereBetween(self, field, from_condition, to_condition, **kw):
        """ where between """

        between = "BETWEEN" if not len(kw) else kw["_cmp"]

        return self.where(field, between, "'%s' AND '%s'" % (from_condition, to_condition))

    def whereNotBetween(self, field, from_condition, to_condition):
        """ where not between """

        return self.whereBetween(field, from_condition, to_condition, _cmp="NOT BETWEEN")

    def whereNull(self, field, **kw):
        """ where field null """

        _cmp = "IS" if not len(kw) else kw["_cmp"]

        return self.where(field, _cmp, "NUll")

    def whereNotNull(self, field):
        """ where field is not null"""

        return self.whereNull(field, _cmp="IS NOT")

    def limit(self, offset, *args):
        """ limit """

        offset = 0 if not len(args) else offset
        number = offset if not len(args) else args[0]
        self._limit = "%d, %d" % (offset, number)

        return self

    def orderBy(self, field, *args):
        """ order by """

        _cmp = "ASC" if not len(args) else "DESC"
        self._order.append(" ".join((field, _cmp)))

        return self

    def update(self, attributes):
        """ execute update """

        source_data = ["%s = %s" % (attr, attributes.get(attr, None)) for attr in attributes]
        sql = ("UPDATE %s SET " % self._table_name) + ", ".join(source_data)
        sql = sql + self._buildConditionString("_where")

        return MySQLConnect.execute(sql)

    def delete(self):
        """ execute delete """

        sql = "DELETE FROM %s" % self._table_name
        sql = sql + self._buildConditionString("_where")

        return MySQLConnect.execute(sql)

    def get(self):
        """ query data """

        return ResaultBuilder.query(self)

    def first(self):
        """ query first one col data """

        return ResaultBuilder.query(self, few=False)


class ResaultBuilder(object):
    """ Resault Builder """

    @classmethod
    def execute(cls, sql):
        """ execute """

        return MySQLConnect.execute(sql)

    @classmethod
    def query(cls, builder, few=True):
        """ query """

        resault = MySQLConnect.execute(builder.BuildQuerySQLString())

        if not len(resault):
            return [] if few else None

        if few:
            return list(map(
                lambda attributes:cls.buildORMModelInstance(builder._ormmodel, attributes), resault))
        else:
            return cls.buildORMModelInstance(builder._ormmodel, resault[0])

    @classmethod
    def buildORMModelInstance(cls, model, attributes):
        """ build model instance """

        return model(attributes=attributes, origin_attributes=attributes)


class ORMModel(object):
    """ Model """

    table_name = ""
    fields = []
    no_attribute = ("table_name", "origin_attributes", "id")
    origin_attributes = {}
    __id = 0

    def __init__(self, table_name="", attributes={}, origin_attributes={}):
        if self.table_name == "" and table_name == "":
            self.table_name = self.__class__.__name__.lower()
        elif table_name != "":
            self.table_name = table_name

        if len(attributes):
            for attribute in attributes:
                self.__setattr__(self, attribute, attributes.get(attribute))

        if len(origin_attributes):
            self.origin_attributes = origin_attributes
            self.__id = origin_attributes.get("id", "")

    def __setattr__(self, attr, value):
        if not attr in self.no_attribute:
            fields = self.fields
            fields.append(attr)
            self.__dict__["fields"] = fields

        self.__dict__[attr] = value

    def __getattribute__(self, attr):
        new_instance = super(ORMModel, self)

        if attr == "table_name" and new_instance.__getattribute__("table_name") == "":
            return new_instance.__class__.__name__.lower()

        return new_instance.__getattribute__(attr)

    @classmethod
    def get(cls):
        """ get all data """

        return cls.all()

    @classmethod
    def all(cls):
        """ get all data """

        return ResaultBuilder.query(QueryBuilder(cls))

    @classmethod
    def first(cls):
        """ get first data """

        return ResaultBuilder.query(QueryBuilder(cls).limit(1), few=False)

    @classmethod
    def select(cls, *fields):
        """ select """

        return QueryBuilder(cls).select(*fields)

    @classmethod
    def query(cls, sql):
        """ execute sql string """

        return MySQLConnect.execute(sql)

    @staticmethod
    def DB():
        """ get MySQLConnect.db """

        return MySQLConnect.getDB()

    @staticmethod
    def log():
        """ get MySQLConnect.sql_statement_log """

        return MySQLConnect.sql_statement_log

    def arrangeAttributes(self):
        """ arrange self attribute """

        attributes = dict().fromkeys(self.fields)

        for attr in attributes:
            attributes[attr] = getattr(self, attr)

        return attributes

    def save(self):
        """ update model attribute change """

        attributes = self.arrangeAttributes()

        if len(self.origin_attributes):
            return QueryBuilder(self).where("id", self.__id).update(attributes)
        else:
            return self.insert(attributes)

    def delete(self):
        """ delete this model data """

        if self.__id == 0:
            raise AttributeError("Instance have not attribute 'ID'")

        return QueryBuilder(self).where("id", self.__id).delete()

    @classmethod
    def insert(cls, data):
        """ attribute insert to table"""

        if (not isinstance(data, list) and
            not isinstance(data, dict)) or not len(data):
            raise AttributeError("data type error.")

        def buildInsertIntoValueSQLString(fields, attribute):
            values = ["'%s'" % attribute.get(field, "") for field in fields]

            return "(%s)" % ", ".join(values)

        fields = data.keys() if isinstance(data, dict) else random.choice(data).keys()
        values = buildInsertIntoValueSQLString(fields, data) if isinstance(data, dict) else ", ".join(
            map(lambda attr: buildInsertIntoValueSQLString(fields, attr), data))
        sql = "INSERT INTO %s (%s) VALUES %s" % (cls.table_name, fields, values)

        return MySQLConnect.execute(sql)

