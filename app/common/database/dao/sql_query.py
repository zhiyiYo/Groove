# coding:utf-8
from common.logger import Logger
from PyQt5.QtSql import QSqlQuery, QSqlError


class SqlQuery(QSqlQuery):
    """ Database sql statement execution class """

    logger = Logger('cache')

    def exec(self, query: str = None):
        """ execute sql statement """
        if not query:
            return self.check(super().exec())

        return self.check(super().exec(query))

    def check(self, success: bool):
        """ check execution result """
        if success:
            return True

        error = self.lastError()
        if error.isValid() and error.type() != QSqlError.NoError:
            msg = f'"{error.text()}" for query "{self.lastBoundQuery()}"'
            self.logger.error(msg)

        return False

    def lastBoundQuery(self):
        query = self.lastQuery()
        for k, v in self.boundValues().items():
            query = query.replace('?', str(v), 1)
            query = query.replace(k, str(v))

        return query
