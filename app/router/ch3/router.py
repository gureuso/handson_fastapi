# -*- coding: utf-8 -*-
from typing import Union, Optional

from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from config import Config

router = APIRouter(prefix='/ch3')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


@router.get('/base_model')
async def ch3_base_model():
    class Item(BaseModel):
        name: str
        age: int
    return {'item': Item(name='alex', age=28)}


class Item(BaseModel):
    name: str = Field(default=..., description='name', min_length=3, max_length=10)
    age: int = Field(description='age', lt=100, gt=0)


@router.post('/base_model_2')
async def ch3_base_model_2(item: Item):
    return {'name': item.name, 'age': item.age}


@router.get('/type_hint')
async def ch3_type_hint():
    def add(x: Union[int, float], y: int) -> float:
        return x + y

    return {'result': add(10.1, 20)}


@router.get('/type_hint_2')
async def ch3_type_hint_2():
    class Item(BaseModel):
        name: str
        age: int

    a: str = 'alex'
    b: int = 10
    c: float = 10.1
    d: dict[str, Item] = {'item': Item(name='alex', age=28)}
    e: list[int] = [1, 2, 3, 4, 5]
    f: tuple[int, int] = (1, 1)
    g: Optional[str] = None
    h: Union[int, float] = 10.1
    i: str | None = None

    return {}
