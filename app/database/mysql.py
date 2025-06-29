# -*- coding: utf-8 -*-
import databases
import pymysql
import sqlalchemy
from enum import Enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

from config import Config

pymysql.install_as_MySQLdb()

DATABASE_URL = f'''mysql://{Config.DB_USER_NAME}:{Config.DB_USER_PASSWD}@{Config.DB_HOST}/{Config.DB_NAME}'''
database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()
todo_user_table = sqlalchemy.Table(
    'TodoUser',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('email', sqlalchemy.String(255), unique=True),
    sqlalchemy.Column('password', sqlalchemy.String(255), nullable=True),
    sqlalchemy.Column('nickname', sqlalchemy.String(20), nullable=True),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP, nullable=True),
)
todo_table = sqlalchemy.Table(
    'Todo',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('user_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('title', sqlalchemy.String(40), nullable=True),
    sqlalchemy.Column('content', sqlalchemy.TEXT, nullable=True),
    sqlalchemy.Column('completed_at', sqlalchemy.TIMESTAMP, nullable=True),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP, nullable=True),
)
user_table = sqlalchemy.Table(
    'User',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('email', sqlalchemy.String(255), unique=True),
    sqlalchemy.Column('provider', sqlalchemy.String(40), nullable=True),
    sqlalchemy.Column('phone_number', sqlalchemy.String(40), nullable=True),
    sqlalchemy.Column('phone_validation_number', sqlalchemy.String(10), nullable=True),
    sqlalchemy.Column('phone_send_at', sqlalchemy.TIMESTAMP, nullable=True),
    sqlalchemy.Column('phone_is_validation', sqlalchemy.SMALLINT, server_default='0', nullable=True),
    sqlalchemy.Column('email_validation_number', sqlalchemy.String(10), nullable=True),
    sqlalchemy.Column('email_is_validation', sqlalchemy.SMALLINT, server_default='0', nullable=True),
    sqlalchemy.Column('profile_image', sqlalchemy.String(255), nullable=True),
    sqlalchemy.Column('nickname', sqlalchemy.String(20), nullable=True),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP, nullable=True),
)
channel_table = sqlalchemy.Table(
    'Channel',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('user_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('name', sqlalchemy.String(255), unique=True),
    sqlalchemy.Column('image', sqlalchemy.TEXT, nullable=True),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP, nullable=True),
)
tag_table = sqlalchemy.Table(
    'Tag',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('video_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('name', sqlalchemy.String(20), nullable=True),
)
shorts_table = sqlalchemy.Table(
    'Shorts',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('channel_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('title', sqlalchemy.String(255), nullable=True),
    sqlalchemy.Column('thumbnail', sqlalchemy.TEXT, nullable=True),
    sqlalchemy.Column('content', sqlalchemy.TEXT, nullable=True),
    sqlalchemy.Column('view_cnt', sqlalchemy.BIGINT, server_default='0'),
    sqlalchemy.Column('like_cnt', sqlalchemy.BIGINT, server_default='0'),
    sqlalchemy.Column('dislike_cnt', sqlalchemy.BIGINT, server_default='0'),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP, nullable=True),
    sqlalchemy.Column('tag', sqlalchemy.String(20), nullable=True),
)
shorts_comment_table = sqlalchemy.Table(
    'ShortsComment',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('parent_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('content', sqlalchemy.TEXT, nullable=True),
    sqlalchemy.Column('shorts_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('user_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('like_cnt', sqlalchemy.BIGINT, server_default='0'),
    sqlalchemy.Column('dislike_cnt', sqlalchemy.BIGINT, server_default='0'),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP, nullable=True),
)
shorts_comment_like_table = sqlalchemy.Table(
    'ShortsCommentLike',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('kind', sqlalchemy.String(10), nullable=True),
    sqlalchemy.Column('comment_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('shorts_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('user_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP, nullable=True),
)
shorts_like_table = sqlalchemy.Table(
    'ShortsLike',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('kind', sqlalchemy.String(10), nullable=True),
    sqlalchemy.Column('shorts_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('user_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP, nullable=True),
)
video_table = sqlalchemy.Table(
    'Video',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('channel_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('title', sqlalchemy.String(255), nullable=True),
    sqlalchemy.Column('thumbnail', sqlalchemy.TEXT, nullable=True),
    sqlalchemy.Column('content', sqlalchemy.TEXT, nullable=True),
    sqlalchemy.Column('view_cnt', sqlalchemy.BIGINT, server_default='0'),
    sqlalchemy.Column('like_cnt', sqlalchemy.BIGINT, server_default='0'),
    sqlalchemy.Column('dislike_cnt', sqlalchemy.BIGINT, server_default='0'),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP, nullable=True),
    sqlalchemy.Column('tag', sqlalchemy.String(20), nullable=True),
)
video_like_table = sqlalchemy.Table(
    'VideoLike',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('kind', sqlalchemy.String(10), nullable=True),
    sqlalchemy.Column('video_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('user_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP, nullable=True),
)
video_comment_table = sqlalchemy.Table(
    'VideoComment',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('parent_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('content', sqlalchemy.TEXT, nullable=True),
    sqlalchemy.Column('video_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('user_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('like_cnt', sqlalchemy.BIGINT, server_default='0'),
    sqlalchemy.Column('dislike_cnt', sqlalchemy.BIGINT, server_default='0'),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP, nullable=True),
)
video_comment_like_table = sqlalchemy.Table(
    'VideoCommentLike',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('kind', sqlalchemy.String(10), nullable=True),
    sqlalchemy.Column('comment_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('video_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('user_id', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('created_at', sqlalchemy.TIMESTAMP, nullable=True),
)
engine = sqlalchemy.create_engine(DATABASE_URL)


class TodoUserEntity(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    password: str
    nickname: str
    created_at: datetime


class TodoEntity(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    title: str
    content: str
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class ShortsEntity(BaseModel):
    id: Optional[int] = None
    channel_id: Optional[int] = None
    tag: str
    title: str
    thumbnail: str
    content: str
    view_cnt: int
    like_cnt: Optional[int] = 0
    dislike_cnt: Optional[int] = 0
    created_at: datetime


class ShortsCommentEntity(BaseModel):
    id: Optional[int] = None
    parent_id: Optional[int] = None
    content: str
    shorts_id: Optional[int] = None
    user_id: Optional[int] = None
    like_cnt: Optional[int] = 0
    dislike_cnt: Optional[int] = 0
    created_at: datetime

    # tmp
    profile_image: Optional[str] = None
    nickname: Optional[str] = None
    child_comments: List['ShortsCommentEntity'] = Field(default_factory=list)
    liked: bool = False
    disliked: bool = False


class ShortsCommentLikeEnum(Enum):
    LIKE = 'LIKE'
    DISLIKE = 'DISLIKE'


class ShortsCommentLikeEntity(BaseModel):
    id: Optional[int] = None
    kind: ShortsCommentLikeEnum
    comment_id: Optional[int] = None
    shorts_id: Optional[int] = None
    user_id: Optional[int] = None
    created_at: datetime


class ShortsLikeEnum(Enum):
    LIKE = 'LIKE'
    DISLIKE = 'DISLIKE'


class ShortsLikeEntity(BaseModel):
    id: Optional[int] = None
    kind: ShortsLikeEnum
    shorts_id: Optional[int] = None
    user_id: Optional[int] = None
    created_at: datetime


class VideoEntity(BaseModel):
    id: Optional[int] = None
    channel_id: Optional[int] = None
    tag: str
    title: str
    thumbnail: str
    content: str
    view_cnt: int
    like_cnt: Optional[int] = 0
    dislike_cnt: Optional[int] = 0
    created_at: datetime

    # mix
    name: Optional[str] = None
    image: Optional[str] = None


class VideoCommentEntity(BaseModel):
    id: Optional[int] = None
    parent_id: Optional[int] = None
    content: str
    video_id: Optional[int] = None
    user_id: Optional[int] = None
    like_cnt: Optional[int] = 0
    dislike_cnt: Optional[int] = 0
    created_at: datetime

    # tmp
    profile_image: Optional[str] = None
    nickname: Optional[str] = None
    child_comments: List['ShortsCommentEntity'] = Field(default_factory=list)
    liked: bool = False
    disliked: bool = False


class VideoCommentLikeEnum(Enum):
    LIKE = 'LIKE'
    DISLIKE = 'DISLIKE'


class VideoCommentLikeEntity(BaseModel):
    id: Optional[int] = None
    kind: VideoCommentLikeEnum
    comment_id: Optional[int] = None
    video_id: Optional[int] = None
    user_id: Optional[int] = None
    created_at: datetime


class VideoLikeEnum(Enum):
    LIKE = 'LIKE'
    DISLIKE = 'DISLIKE'


class VideoLikeEntity(BaseModel):
    id: Optional[int] = None
    kind: VideoLikeEnum
    video_id: Optional[int] = None
    user_id: Optional[int] = None
    created_at: datetime


class ChannelEntity(BaseModel):
    id: Optional[int] = None
    name: str
    image: str
    created_at: datetime


class TagEntity(BaseModel):
    id: Optional[int] = None
    video_id: Optional[int] = None
    name: str

class UserEntity(BaseModel):
    id: Optional[int] = None
    email: str
    provider: str
    phone_number: str | None
    phone_validation_number: str | None
    phone_send_at: datetime | None
    phone_is_validation: int
    email_validation_number: str | None
    email_is_validation: int
    nickname: str
    profile_image: str
    created_at: datetime
