from cqrk.core import core


from typing import Union
import requests
from bs4 import BeautifulSoup
import pickle
import os
import re

class user(core):
    def __init__(self,username=None,password=None):
        super().__init__(username,password)

    def login(self,user=None,password=None,use_cookie=True) -> bool:
        """登录教务系统

        Args:
            user (str, optional): 学号. Defaults to None.
            password (str, optional): 登录密码. Defaults to None.
            use_cookie (bool, optional): 是否直接使用cookie登录. Defaults to True.

        Returns:
            bool: 是否登录成功
        """

        if user is not None:
            self.setUser(user)

        if password is not None:
            self.setPassword(password)

        if self.user is None:
            self.logger.warning('用户名不能为空')
            return False
        
        if use_cookie:
            cookies = self.loadCookie()
        else:
            cookies = None

        if cookies is None and self.pwd is None:
            self.logger.warning('密码不能为空')
            return False
        
        request = requests.Session()
        dataTest = request.get(f'{self.config.domain}{self.config.classTable}', headers=self.config.headers, cookies=cookies).text
        isLogin = BeautifulSoup(dataTest, 'html.parser').title.string

        if isLogin == '登录':
            if self.isCookieExists():
                self.logger.warning('cookie 已过期，正在重新登录中')
                # 删除过期 Cookie
                if not self.rmCookie():
                    return False
            else:
                self.logger.warning('正在登录中')
            
            dataStr = request.post(f'{self.config.domain}{self.config.getLoginScode}', headers=self.config.headers, cookies=cookies).text
            scode   = dataStr.split("#")[0]
            code    = f"{self.user}%%%{self.pwd}"
            sxh     = dataStr.split("#")[1]
            encoded = ""
            for i in range(0, len(code)):
                if i < 20:
                    encoded += code[i] + scode[:int(sxh[i])]
                    scode = scode[int(sxh[i]):]
                else:
                    encoded += code[i:]
                    break
            data = {
                "userAccount": "",
                "userPassword": "",
                "encoded":encoded
            }

            response = request.post(f'{self.config.domain}{self.config.loginPost}', headers=self.config.headers, data=data)

            if response.status_code != 200:
                self.logger.warning(f'登录失败，错误码：{response.status_code}')
                return False
            
            # 保存cookie登录凭证
            cookies = request.cookies.get_dict()

            if self.isCookieExists():
                self.rmCookie()

            with open(f'{self.ROOT}/cookies/{self.user}.pkl', 'wb') as f:
                pickle.dump(cookies, f)
            
            if self.isCookieExists():
                return True
            else:
                return False
        else:
            return True
    
    def loadCookie(self) -> Union[dict, None]:
        """加载本地cookie

        Returns:
            (dict | None): 本地cookie加载成功，则返回 dict
        """
        if self.user is None:
            return None

        cookieFile = f'{self.ROOT}/cookies/{self.user}.pkl'
        if not os.path.exists(cookieFile):
            return None

        try:
            with open(cookieFile, 'rb') as f:
                return pickle.load(f)
        except:
            return None
        
    def isCookieExists(self) -> bool:
        """检查cookie文件是否存在

        Returns:
            bool: 是否存在cookie文件
        """
        if os.path.exists(f'{self.ROOT}/cookies/{self.user}.pkl'):
            return True
        else:
            return False
    
    def rmCookie(self) -> bool:
        """删除cookie文件

        Returns:
            bool: 是否删除成功
        """
        if self.user is None:
            return False
        
        cookieFile = f'{self.ROOT}/cookies/{self.user}.pkl'
        if not self.isCookieExists():
            return True
                    
        try:
            os.remove(cookieFile)
            return True
        except OSError:
            self.logger.error("Error: 文件未找到或无法删除")
            return False


    def isCookieEnable(self) -> bool:
        """cookies 是否可以用
        
        Returns:
            bool: cookies 是否可以用
        """
        
        if self.user is None:
            self.logger.error('学号为空')

        if os.path.exists(self.ROOT+'/cookies/'+str(self.user)+'.pkl'):
            classTable   = f'{self.config.domain}{self.config.classTable}'
            response   = requests.get(classTable, headers=self.config.headers, cookies=self.loadCookie())
            if response.status_code != 200:
                return False
            
            title = BeautifulSoup(response.text, 'html.parser').title.string
            if title == '学期理论课表':
                # 登录成功
                return True
            else:
                # 登录失败
                return False
        else:
            # 登录失败
            return False


    def resetCookie(self,JSESSIONID:str):
        """ 重置本地保存的cookie，
            该方法一般用于浏览器抓包后，
            直接传入JSESSIONID，
            不会被强制下线

        Args:
            JSESSIONID (str): 浏览器抓包后的JSESSIONID
        """
        
        file = f'{self.ROOT}/cookies/{self.user}.pkl'

        cookies = {
            'JSESSIONID':JSESSIONID,
            'Path':'/',
            'name': 'value'
        }

        if self.isCookieExists():
            self.rmCookie()

        with open(file, 'wb') as file:
            pickle.dump(cookies, file)