from uuid import uuid1
from typing import Tuple, Dict

from pymysql import Connection
from pymysql.cursors import DictCursor, Cursor
from .abs_table import AbsTableHandler, AbsSqlStmtHolder

class RecordStmts(AbsSqlStmtHolder):

    @property
    def create_db(self) -> str: return """
        create table IF NOT EXISTS G01.Record (
            id              varchar(128)                        primary key,
            type            varchar(128)                        not null,
            slevel          int                                 not null, 
            content         varchar(2048), 
            created_time timestamp default CURRENT_TIMESTAMP not null
        );
    """

    @property
    def select_all_records(self) -> str: return """
        SELECT * FROM G01.Record
    """

    @property
    def select_records_by_type(self) -> str: return """
        SELECT * FROM G01.Record 
        WHERE type='{type}' AND slevel >= {slevel}
    """

    @property
    def select_record_by_id(self) -> str: return """
        SELECT * FROM G01.Record
        WHERE id=%(id)s
    """

    @property
    def insert_record(self) -> str: return """
        INSERT INTO G01.Record(id, type, slevel, content)
        VALUE (%(id)s, %(type)s, %(slevel)s, %(content)s)
    """

    @property
    def whether_is_empty(self) -> str: return """
        SELECT 1 FROM G01.Record
        LIMIT 1
    """

class RecordTable(AbsTableHandler):

    def __init__(self, connection: Connection):
        super().__init__(connection, RecordStmts())

    @property
    def _stmts(self)-> RecordStmts:
        holder = super(RecordTable, self)._stmts
        if not isinstance(holder, RecordStmts): raise TypeError("IMPOSSIBLE")
        return holder

    def get_all_records(self) -> Tuple[Dict]:
        with self._db_connection.cursor(DictCursor) as cursor:
            cursor.execute(self._stmts.select_all_records)
            return cursor.fetchall()

    def get_records_by_type(self, type: str, security_level: int=10) -> Tuple[Dict]:
        with self._db_connection.cursor(DictCursor) as cursor:
            cmd = self._stmts.select_records_by_type.format(type=type, slevel=security_level)
            cursor.execute(cmd)
            output = cursor.fetchall()
            print(output)
            return output

    def get_record_by_id(self, id: str) -> Dict:
        with self._db_connection.cursor(DictCursor) as cursor:
            cursor.execute(self._stmts.select_record_by_id, {"id": id})
            return cursor.fetchone()

    def record(self, type: str, content: str, security_level: int=10, ) -> int: 
        output = None
        with self._db_connection.cursor(DictCursor) as cursor: 
            output = cursor.execute(self._stmts.insert_record, {'id': str(uuid1()), 'type': type, 'content': content, 'slevel': security_level})
        self._db_connection.commit()
        return output

    def is_empty(self) -> bool: 
        with self._db_connection.cursor(Cursor) as cursor: 
            cursor.execute(self._stmts.whether_is_empty)
            return cursor.fetchone() is None


