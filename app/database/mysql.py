# -*- coding: utf-8 -*-
import databases
import pymysql
import sqlalchemy
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from config import Config

pymysql.install_as_MySQLdb()

DATABASE_URL = f'''mysql://{Config.DB_USER_NAME}:{Config.DB_USER_PASSWD}@{Config.DB_HOST}/{Config.DB_NAME}'''
database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()
user_table = sqlalchemy.Table(
    'User',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('email', sqlalchemy.String(255), unique=True),
    sqlalchemy.Column('provider', sqlalchemy.String(40), nullable=True),
    sqlalchemy.Column('phone_number', sqlalchemy.String(40), nullable=True),
    sqlalchemy.Column('phone_validation_number', sqlalchemy.String(10), nullable=True),
    sqlalchemy.Column('phone_send_at', sqlalchemy.TIMESTAMP, nullable=True),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP, nullable=True),
)
engine = sqlalchemy.create_engine(DATABASE_URL)


class UserEntity(BaseModel):
    id: Optional[int] = None
    email: str
    provider: str
    phone_number: str | None
    phone_validation_number: str | None
    phone_send_at: datetime | None
    created_at: datetime
