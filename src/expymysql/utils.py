from operator import contains
import os, re, json, pymysql
from flask import Flask
from typing import Optional
from dataclasses import dataclass
from pymysql.constants import CLIENT

from .tables.user import UserTable
from .tables.records import RecordTable

@dataclass
class __Table:
    users: Optional[UserTable]
    records: Optional[RecordTable]

tables = __Table(None, None)

def init_dbmanager(
    app: Flask, 
    db_uri: Optional[str] = None, 
    init_users_json: Optional[str] = None, 
    init_records_json: Optional[str] = None
) -> __Table:
    if db_uri is None: db_uri = os.environ['DB_URI']
    db_paras_regex = r'.+:\/\/(?P<user>.+):(?P<password>.+)@(?P<host>.+):(?P<port>\d+)(\/.+)?'
    db_paras = re.match(db_paras_regex, db_uri).groupdict()
    main_connection = pymysql.connect(
        user=db_paras['user'],password=db_paras['password'], 
        host=db_paras['host'],port=int(db_paras['port']), 
        client_flag=CLIENT.MULTI_STATEMENTS
    )
    tables.users = UserTable(main_connection)
    tables.records = RecordTable(main_connection)
    if init_users_json is not None and not tables.users.is_empty(): 
        for user_json in json.loads(init_users_json): tables.users.register(**user_json)
    if init_records_json is not None and not tables.records.is_empty(): 
        for record_json in json.loads(init_records_json): tables.records.record(record_json)
    return tables

def is_correct(username: str, password: str) -> bool: 
    return tables.users.is_correct_password(username, password)