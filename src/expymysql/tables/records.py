from uuid import uuid1
from typing import Tuple, Dict, List

from pymysql import Connection
from pymysql.cursors import DictCursor
from .abs_table import AbsTableHandler, AbsSqlStmtHolder


class RecordStmts(AbsSqlStmtHolder):

    @property
    def create_db(self) -> str: return """
        CREATE TABLE IF NOT EXISTS main.Record (
            id      int                                 primary key,
            type    varchar(128)                        not null,
            time    timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
        );
    """

    @property
    def select_all_records(self) -> str: return """
        SELECT * FROM main.Record
    """

    @property
    def select_records_by_type(self) -> str: return """
        SELECT * FROM main.Record
        WHERE type = %(type)s
    """

    @property
    def select_record_by_id(self) -> str: return """
        SELECT * FROM main.Record
        WHERE id = %(id)s
    """

    @property
    def insert_record(self) -> str: return """
        INSERT INTO main.Record(id, type)
        VALUE (%(id)s, %(type)s)
    """


class RecordTable(AbsTableHandler):

    def __init__(self, connection: Connection):
        super().__init__(connection, RecordStmts())

    @property
    def _stmts(self) -> RecordStmts:
        holder = super(RecordStmts, self)._stmts
        if not isinstance(holder, RecordStmts): raise TypeError("IMPOSSIBLE")
        return holder

    def get_all_records(self) -> Tuple[Dict]:
        with self._db_connection.cursor(DictCursor) as cursor:
            cursor.execute(self._stmts.select_all_records)
            return cursor.fetchall()

    def get_records_by_type(self, type: str) -> Tuple[Dict]:
        with self._db_connection.cursor(DictCursor) as cursor:
            cursor.execute(self._stmts.select_records_by_type, {"type": type})
            return cursor.fetchall()

    def get_records_by_id(self, id: int) -> Dict:
        with self._db_connection.cursor(DictCursor) as cursor:
            cursor.execute(self._stmts.select_records_by_type, {"id": id})
            return cursor.fetchone()

    def insert_records(self, records: List[Dict]) -> None: 
        with self._db_connection.cursor(DictCursor) as cursor: 
            for record in records: cursor.execute(self._stmts.insert_record, {'id': uuid1()} | record)
        self._db_connection.commit()
        return None



