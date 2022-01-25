# coding:utf-8
from typing import List

from common.singleton import Singleton

from ..entity import Entity


class ServiceBase(Singleton):
    """ 服务抽象类 """

    def __init__(self):
        super().__init__()

    def createTable(self) -> bool:
        """ 创建表 """
        raise NotADirectoryError

    def findBy(self, **condition) -> Entity:
        """ 查询一条符合条件的记录

        Parameters
        ----------
        condition: dict
            查询条件

        Returns
        -------
        entity: Entity
            实体类对象，没有查询到则为 None
        """
        raise NotImplementedError

    def listBy(self, **condition) -> List[Entity]:
        """ 查询所有符合条件的记录

        Parameters
        ----------
        condition: dict
            查询条件

        Returns
        -------
        entities: List[Entity]
            实体类对象列表，没有查询到则为空列表
        """
        raise NotImplementedError

    def listAll(self) -> List[Entity]:
        """ 查询所有记录 """
        raise NotImplementedError

    def modify(self, id, field: str, value) -> bool:
        """ 更新一条记录中某个字段的值

        Parameters
        ----------
        id:
            主键值

        filed: str
            字段名

        value:
            字段值

        Returns
        -------
        success: bool
            更新是否成功
        """
        raise NotImplementedError

    def modifyById(self, entity: Entity) -> bool:
        """ 更新一条记录

        Parameters
        ----------
        entity: Entity
            实体类对象

        Returns
        -------
        success: bool
            更新是否成功
        """
        raise NotImplementedError

    def modifyByIds(self, entities: List[Entity]) -> bool:
        """ 更新多条记录

        Parameters
        ----------
        entities: List[Entity]
            实体类对象

        Returns
        -------
        success: bool
            更新是否成功
        """
        raise NotImplementedError

    def add(self, entity: Entity) -> bool:
        """ 插入一条记录

        Parameters
        ----------
        entity: Entity
            实体类对象

        Returns
        -------
        success: bool
            插入是否成功
        """
        raise NotImplementedError

    def addBatch(self, entities: List[Entity]) -> bool:
        """ 插入多条记录

        Parameters
        ----------
        entities: List[Entity]
            实体类对象

        Returns
        -------
        success: bool
            插入是否成功
        """
        raise NotImplementedError

    def removeById(self, id) -> bool:
        """ 移除一条记录

        Parameters
        ----------
        id:
            主键值

        Returns
        -------
        success: bool
            更新是否成功
        """
        raise NotImplementedError

    def removeByIds(self, ids: list) -> bool:
        """ 移除多条记录

        Parameters
        ----------
        ids: list
            主键值列表

        Returns
        -------
        success: bool
            移除是否成功
        """
        raise NotImplementedError
