import os

from config import Config

try:
    activate_this = os.path.join(*[Config.ROOT_DIR, 'venv', 'bin', 'activate_this.py'])
    with open(activate_this) as f:
        exec(f.read(), dict(__file__=activate_this))
except FileNotFoundError:
    activate_this = os.path.join(*[Config.ROOT_DIR, 'venv', 'Scripts', 'activate_this.py'])
    with open(activate_this) as f:
        exec(f.read(), dict(__file__=activate_this))


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        'app.router.main:app',
        host=Config.APP_HOST,
        port=Config.APP_PORT,
        reload=True if Config.APP_MODE == Config.APP_MODE_DEVELOPMENT else False,
        workers=4,
        log_level='info',
    )
