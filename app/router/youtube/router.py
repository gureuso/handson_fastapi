from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

from config import Config

router = APIRouter(prefix='/youtube')
templates = Jinja2Templates(directory=Config.TEMPLATES_DIR)
