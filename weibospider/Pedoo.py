#This Python file uses the following encoding: utf-8

""" pedoo """

import MySQLdb


class Pedoo:
    """ mysqldb expansion pedoo """

    def __init__(self, mysql_config):
        self.mysql = MySQLdb.connect(
            host = mysql_config['host'],
            user = mysql_config['user'],
            passwd = mysql_config['passwd'],
            db = mysql_config['db'],
            charset = mysql_config['charset'])

        self.db = self.mysql.cursor(cursorclass = MySQLdb.cursors.DictCursor)

    def select(self, table, join = '', field = '*', where = {}, other = []):
        self.db.execute(self.__selectString(
            table = table, join = join, field = field,
            where = where, other = other))

        return self.db.fetchall()

    def get(self, table, join = '', field = '*', where = {}, other = []):
        self.db.execute(self.__selectString(
            table = table, join = join, field = field,
            where = where, other = other))

        return self.db.fetchone()

    def has(self, table, where):
        res = self.get(table = table, field = '*', where = where)

        return not res is None

    def update(self, table, dictionary, where = {}):
        sql = "UPDATE %s SET " % table

        sql += self.__spliceWhereString(dictionary = dictionary)

        sql += " WHERE %s " % self.__spliceWhereString(dictionary = where)

        self.db.execute(sql)

        return self.mysql.commit()

    def insert(self, table, dictionary):
        keylist =  dictionary[0].keys() if isinstance(dictionary, list) else dictionary.keys()
        sql = "INSERT INTO %s ( %s ) VALUES " % (table, ', '.join(keylist))

        if isinstance(dictionary, list):
            values = []

            for instance in dictionary:
                temporary_list = []

                for key in keylist:
                    temporary_list.append("'%s'" % instance.get(key))

                values.append(" (%s) " %  ', '.join(temporary_list))

            sql += ', '.join(values)
        else:
            temporary_list = []

            for key in keylist:
                temporary_list.append("'%s'" % dictionary.get(key))

            sql += " (%s) " % ', '.join(temporary_list)

        self.db.execute(sql)

        return self.mysql.commit()

    def delete(self, table, where = {}):
        sql = "DELETE FROM %s " % table

        if len(where) > 0:
            sql += "WHERE %s" % self.__spliceWhereString(dictionary = where)

        self.db.execute(sql)

        return self.mysql.commit()

    def __selectString(self, table, join = '', field = '*', where = {}, other = []):
        field = " %s " % field if isinstance(field, str) else " %s " % ', '.join(field)
        where = "" if len(where) > 0 else self.__spliceWhereString(where)
        other = "" if len(other) > 0 else ' '.join(other)

        return "SELECT %s FROM %s %s WHERE %s %s" % (field, table, join, where, other)

    def __spliceWhereString(self, dictionary):
        temporary_list = []

        for key in dictionary:
            temporary_list.append(key + "='" + dictionary.get(key) + "'")

        return ' AND '.join(temporary_list)

    def close(self):
        return self.mysql.close()