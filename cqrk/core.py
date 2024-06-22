import cqrk.config as config


import logging
import time

import os
import colorlog

class core:
    def __init__(self,user=None,pwd=None):
        self.logger   = logging.getLogger(__name__)
        self.ROOT     = os.getcwd()
        self.config   = config

        self.user     = user
        self.pwd      = pwd

        self.log()


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

    def log(self):
        log_colors_config = {
            'DEBUG': 'white',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }

        # 输出到控制台
        console_handler = logging.StreamHandler()
        # 输出到文件
        # file_handler = logging.FileHandler(filename='test.log', mode='a', encoding='utf8')
    
        # 日志级别，logger 和 handler以最高级别为准，不同handler之间可以不一样，不相互影响
        self.logger.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)
        # file_handler.setLevel(logging.INFO)
    
        # 日志输出格式
        # log_format = "%(log_color)s[%(asctime)s][%(name)s][%(levelname)s][%(filename)s:%(lineno)d][%(funcName)s] %(message)s"
        log_format = '%(log_color)s%(levelname)s : %(asctime)s -> %(message)s'

        # file_formatter = logging.Formatter(
        #     fmt=log_format,  no %(log_color)s
        #     datefmt='%Y-%m-%d  %H:%M:%S'
        # )
        console_formatter = colorlog.ColoredFormatter(
            fmt='{}'.format(log_format),
            log_colors=log_colors_config
        )
        console_handler.setFormatter(console_formatter)
        # file_handler.setFormatter(file_formatter)
    
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
            # logger.addHandler(file_handler)
    
        console_handler.close()
        # file_handler.close()