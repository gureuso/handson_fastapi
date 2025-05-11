# -*- coding: utf-8 -*-
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

from config import Config

router = APIRouter(prefix='/ch2')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)


classes = []
@router.get('/classes')
async def ch2_get_classes():
    return {'classes': classes}


@router.post('/classes')
async def ch2_create_class():
    if len(classes) == 0:
        classes.append({'class_id': 1, 'class_name': f'1학년 {1}반', 'students': []})
    else:
        class_id = classes[-1]['class_id'] + 1
        classes.append({'class_id': class_id, 'class_name': f'1학년 {class_id}반', 'students': []})
    return {}


@router.get('/classes/{class_id}')
async def ch2_get_class(class_id: int):
    for klass in classes:
        if klass['class_id'] == class_id:
            return {'class': klass}
    return {'class': None}


@router.get('/classes/{class_id}/students')
async def ch2_get_students(class_id: int):
    for klass in classes:
        if klass['class_id'] == class_id:
            return {'students': klass['students']}
    return {'students': []}


@router.post('/classes/{class_id}/students')
async def ch2_create_student(class_id: int):
    for klass in classes:
        if klass['class_id'] == class_id:
            klass['students'].append({'class_id': klass['class_id'], 'student_name': f'test{len(klass["students"]) + 1}'})
            break
    return {}
