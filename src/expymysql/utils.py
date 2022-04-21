import re, pymysql
from flask import Flask
from typing import Dict, Optional, List
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
    init_users: List[Dict] = [], 
    init_records: List[Dict] = []
) -> __Table:
    db_paras_regex = r'.+:\/\/(?P<user>.+):(?P<password>.+)@(?P<host>.+):(?P<port>\d+)(\/.+)?'
    db_paras = re.match(db_paras_regex, db_uri).groupdict()
    main_connection = pymysql.connect(
        user=db_paras['user'],password=db_paras['password'], 
        host=db_paras['host'],port=int(db_paras['port']), 
        client_flag=CLIENT.MULTI_STATEMENTS
    )
    tables.users = UserTable(main_connection)
    tables.records = RecordTable(main_connection)
    try: 
        if not tables.users.is_empty(): raise Exception('INITIALSED')
        for user in init_users: tables.users.register(**user)
    except: 
        print('\nWARNING: USER TABLE ALREADY INITIALSED PASS\n')

    try: 
        if not tables.records.is_empty(): raise Exception('INITIALSED')
        for record in init_records: tables.records.record(**record)
    except: 
        print('\nWARNING: RECORD TABLE INITIALSED PASS\n')
    
    return tables

def is_correct(username: str, password: str) -> bool: 
    return tables.users.is_correct_password(username, password)