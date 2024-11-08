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
    sqlalchemy.Column('nickname', sqlalchemy.String(40), unique=True),
    sqlalchemy.Column('image', sqlalchemy.String(255), nullable=True),
    sqlalchemy.Column('provider', sqlalchemy.String(40), nullable=True),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP, nullable=True),
)
user_email_table = sqlalchemy.Table(
    'UserEmail',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('user_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('email', sqlalchemy.String(255), nullable=True),
    sqlalchemy.Column('value', sqlalchemy.String(40), nullable=True),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP, nullable=True),
)
user_fcm_table = sqlalchemy.Table(
    'UserFcm',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('fcm', sqlalchemy.String(255), nullable=True),
    sqlalchemy.Column('user_id', sqlalchemy.Integer, nullable=True),
)
room_table = sqlalchemy.Table(
    'Room',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('first_user_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('second_user_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('room', sqlalchemy.String(255), nullable=True),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP, nullable=True),
)
question_comment_table = sqlalchemy.Table(
    'QuestionComment',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('commenter', sqlalchemy.Integer),
    sqlalchemy.Column('question_id', sqlalchemy.Integer),
    sqlalchemy.Column('content', sqlalchemy.Text),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP),
)
question_like_table = sqlalchemy.Table(
    'QuestionLike',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('liker', sqlalchemy.Integer),
    sqlalchemy.Column('question_id', sqlalchemy.Integer),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP),
)
question_table = sqlalchemy.Table(
    'Question',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('user_id', sqlalchemy.Integer),
    sqlalchemy.Column('content', sqlalchemy.Text),
    sqlalchemy.Column('likes', sqlalchemy.Integer),
    sqlalchemy.Column('reports', sqlalchemy.Integer),
    sqlalchemy.Column('comments', sqlalchemy.Integer),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP),
)
report_table = sqlalchemy.Table(
    'Report',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('reporter', sqlalchemy.Integer),
    sqlalchemy.Column('document_id', sqlalchemy.String(255), nullable=True),
    sqlalchemy.Column('type', sqlalchemy.String(40)),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP),
)
engine = sqlalchemy.create_engine(DATABASE_URL)


class UserEntity(BaseModel):
    id: Optional[int] = None
    email: str
    nickname: str
    provider: str
    image: Optional[str] = None
    created_at: datetime


class UserEmailEntity(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    email: str
    value: str
    created_at: datetime


class UserFcmEntity(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    fcm: str


class RoomEntity(BaseModel):
    id: Optional[int] = None
    first_user_id: Optional[int] = None
    second_user_id: Optional[int] = None
    room: str
    created_at: datetime
    # tmp
    first_user_image: Optional[str] = None
    first_user_nickname: Optional[str] = None
    second_user_image: Optional[str] = None
    second_user_nickname: Optional[str] = None
    last_message: Optional[str] = None


class ReportEntity(BaseModel):
    id: Optional[int] = None
    reporter: int
    document_id: Optional[int] = None
    type: str
    created_at: datetime


class QuestionEntity(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    content: str
    likes: int
    reports: int
    comments: int
    created_at: datetime
    # tmp
    nickname: Optional[str] = None


class QuestionCommentEntity(BaseModel):
    id: Optional[int] = None
    commenter: int
    question_id: Optional[int] = None
    content: str
    created_at: datetime
    # tmp
    nickname: Optional[str] = None


class QuestionLikeEntity(BaseModel):
    id: Optional[int] = None
    liker: int
    question_id: Optional[int] = None
    created_at: datetime
