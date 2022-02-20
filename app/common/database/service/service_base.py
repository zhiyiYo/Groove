# coding:utf-8
from typing import List

from common.singleton import Singleton
from PyQt5.QtSql import QSqlDatabase

from ..entity import Entity


class ServiceBase:
    """ Service abstract class """

    def __init__(self):
        super().__init__()

    def createTable(self) -> bool:
        """ create table """
        raise NotADirectoryError

    def findBy(self, **condition) -> Entity:
        """ query a record that meets the condition

        Parameters
        ----------
        condition: dict
            query condition

        Returns
        -------
        entity: Entity
            entity instance, `None` if no record is found
        """
        raise NotImplementedError

    def listBy(self, **condition) -> List[Entity]:
        """ query all records that meet the conditions

        Parameters
        ----------
        condition: dict
            query condition

        Returns
        -------
        entities: List[Entity]
            entity instances, empty if no records are found
        """
        raise NotImplementedError

    def listLike(self, **condition) -> List[Entity]:
        """ fuzzy query all records that meet the conditions (or relationships)

        Parameters
        ----------
        condition: dict
            query confition

        Returns
        -------
        entities: List[Entity]
            entity instances, empty if no records are found
        """
        raise NotImplementedError

    def listAll(self) -> List[Entity]:
        """ query all records """
        raise NotImplementedError

    def listByIds(self, ids: list) -> List[Entity]:
        """ query the records of the primary key value in the list """
        raise NotImplementedError

    def modify(self, id, field: str, value) -> bool:
        """ modify the value of a field in a record

        Parameters
        ----------
        id:
            primary key value

        filed: str
            field name

        value:
            field value

        Returns
        -------
        success: bool
            is the modify successful
        """
        raise NotImplementedError

    def modifyById(self, entity: Entity) -> bool:
        """ modify a record

        Parameters
        ----------
        entity: Entity
            entity instance

        Returns
        -------
        success: bool
            is the modify successful
        """
        raise NotImplementedError

    def modifyByIds(self, entities: List[Entity]) -> bool:
        """ modify multi records

        Parameters
        ----------
        entities: List[Entity]
            entity instances

        Returns
        -------
        success: bool
            is the modify successful
        """
        raise NotImplementedError

    def add(self, entity: Entity) -> bool:
        """ add a record

        Parameters
        ----------
        entity: Entity
            entity instance

        Returns
        -------
        success: bool
            is the add successful
        """
        raise NotImplementedError

    def addBatch(self, entities: List[Entity]) -> bool:
        """ add multi records

        Parameters
        ----------
        entities: List[Entity]
            entity instances

        Returns
        -------
        success: bool
            is the add successful
        """
        raise NotImplementedError

    def removeById(self, id) -> bool:
        """ remove a record

        Parameters
        ----------
        id:
            primary key value

        Returns
        -------
        success: bool
            is the remove successful
        """
        raise NotImplementedError

    def removeByIds(self, ids: list) -> bool:
        """ remove multi records

        Parameters
        ----------
        ids: list
            primary key values

        Returns
        -------
        success: bool
            is the remove successful
        """
        raise NotImplementedError

    def setDatabase(self, db: QSqlDatabase):
        """ use the specified database """
        raise NotImplementedError
