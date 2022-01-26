# coding:utf-8
from common.logger import Logger
from PyQt5.QtSql import QSqlQuery, QSqlError, QSqlDatabase


class SqlQuery(QSqlQuery):
    """ 数据库语句执行类 """

    cacheLogger = Logger('cache')

    def exec(self, query: str = None):
        """ 执行 SQL 语句 """
        if not query:
            return self.check(super().exec())

        return self.check(super().exec(query))

    def check(self, success: bool):
        """ 检查数据库操作结果 """
        if success:
            return True

        error = self.lastError()
        if error.isValid() and error.type() != QSqlError.NoError:
            msg = f'"{error.text()}" for query "{self.lastBoundQuery()}"'
            self.cacheLogger.error(msg)

        return False

    def lastBoundQuery(self):
        """ 最后一条操作指令 """
        query = self.lastQuery()
        for k, v in self.boundValues().items():
            query = query.replace('?', str(v))
            query = query.replace(k, str(v))

        return query
