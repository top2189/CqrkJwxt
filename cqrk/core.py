import cqrk.config as config

from datetime import datetime
import logging
import time

import os
import colorlog

class core:
    def __init__(self,user=None,pwd=None,DEBUG=None):
        """程序核心类，包括日志记录，通用方法，全局变量等

        Args:
            user (str, optional): 学生学号. Defaults to None.
            pwd (str, optional): 登录密码. Defaults to None.
            DEBUG (bool, optional): 是否开启DEBUG模式. 不传参则从 config.py 中加载配置
        """
        self.logger   = logging.getLogger(__name__)
        self.ROOT     = os.getcwd()
        self.config   = config

        self.user     = user
        self.pwd      = pwd

        if not isinstance(DEBUG,bool):
            DEBUG = self.config.DEBUG
        
        if DEBUG:
            Level = logging.DEBUG
        else:
            Level = logging.INFO

        self.log(Level)


    def setUser(self,user:str):
        """设置目标用户的学号

        Args:
            user (str): 学号
        """
        self.user = user

    def setPassword(self,password:str):
        """设置目标用户的密码

        Args:
            password (str): 登录密码
        """
        self.pwd = password

    def log(self,Level):
        log_colors_config = {
            'DEBUG': 'blue',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }

        # 输出到控制台
        console_handler = logging.StreamHandler()
        # 输出到文件
        now = datetime.now()
        file_handler = logging.FileHandler(filename=f'{self.ROOT}/cache/{now.strftime("%Y-%m-%d")}.log', mode='a', encoding='utf8')
    
        # 日志级别，logger 和 handler以最高级别为准，不同handler之间可以不一样，不相互影响
        self.logger.setLevel(Level)
        console_handler.setLevel(Level)
        file_handler.setLevel(logging.INFO)
    
        # 日志输出格式
        file_format = "[%(asctime)s][%(name)s][%(levelname)s][%(filename)s:%(lineno)d][%(funcName)s] %(message)s"
        

        log_format = '%(log_color)s %(asctime)s -> %(message)s'

        file_formatter = logging.Formatter(
            fmt='{}'.format(file_format),
            datefmt='%Y-%m-%d  %H:%M:%S'
        )
        console_formatter = colorlog.ColoredFormatter(
            fmt='{}'.format(log_format),
            log_colors=log_colors_config
        )

        console_handler.setFormatter(console_formatter)
        file_handler.setFormatter(file_formatter)
    
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
    
        console_handler.close()
        file_handler.close()