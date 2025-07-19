# -*- coding: utf-8 -*-
import importlib
import os
import re
from fastapi import FastAPI


class APIRouterRegister:
    def __init__(self, app: FastAPI, module_path: str, controller_name: str):
        self.app = app
        self.module_path = module_path
        self.controller_name = controller_name
        self.controller_path = os.path.join(*[os.getcwd(), 'app', 'router'])
        self.directories = []

    def register(self):
        self._find_dir(self.controller_path)
        for dir_path in self.directories:
            dir_path = dir_path[1:].replace('/', '.').replace('\\', '.')
            module_path = '{}.{}.{}'.format(self.module_path, dir_path, self.controller_name)
            module = importlib.import_module(module_path)
            self.app.include_router(module.router)

    def _find_dir(self, path):
        files = os.listdir(path)
        for file_name in files:
            isdir = os.path.isdir(os.path.join(*[path, file_name]))
            if not isdir:
                continue
            ignore = self._ignore(file_name)
            if ignore:
                continue
            self._append_dir(path, file_name)

    def _append_dir(self, path, file_name):
        dir_path = os.path.join(*[path, file_name])
        self.directories.append(dir_path.replace(self.controller_path, ''))
        self._find_dir(dir_path)

    def _ignore(self, name):
        # __pycache__/
        if re.match('__.*__', name):
            return True
        return False
