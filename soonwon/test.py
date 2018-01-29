# -*- coding: utf-8 -*-
from setuptools import setup
import py2exe

# name, description, version등의 정보는 일반적인 setup.py와 같습니다.
setup(name="test_py2xxx",
      description="py2exe test application",
      version="0.0.1",
      windows=[{"script": "testrun.py"}],
      options={
          "py2exe": {
              # PySide 구동에 필요한 모듈들은 포함시켜줍니다.
              "includes": ["PySide.QtCore",
                           "PySide.QtGui",
                           "PySide.QtWebKit",
                           "PySide.QtNetwork",
                           "PySide.QtXml"],
<<<<<<< HEAD
              # 존재하지 않거나 불필요한 파일은 제거합니다.!
=======
              # 존재하지 않거나 불필요한 파일은 제거합니다.
>>>>>>> f9ad7629997e15ea4b40b488babe9207690538cf
              #"dll_excludes": ["msvcr71.dll", "OLEAUT32.dll", "IMM32.dll", "COMDLG32.dll", "WINMM.dll", "WINSPOOL.DRV", "ole32.dll",
              #                "MSVCP90.dll", "WSOCK32.dll", "USER32.dll", "ADVAPI32.dll", "SHELL32.dll", "KERNEL32.dll", "WS2_32.dll", "GDI32.dll"],
          }
      })