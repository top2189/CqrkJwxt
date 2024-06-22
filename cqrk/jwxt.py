import pickle
from typing import Union

from bs4 import BeautifulSoup
from cqrk.core import core
import requests
import os

class jwxt(core):
    def __init__(self,cookies=None):
        super().__init__()

        self.cookies = cookies

    def getStudentInfo(self) -> Union[dict, None]:
        """获取学生基本信息

        Returns:
            (dict | None): 成功返回dict，失败返回None
        """
        mainPage   = f'{self.config.domain}{self.config.mainPage}'
        response   = requests.get(mainPage, headers=self.config.headers, cookies=self.cookies)
        if response.status_code != 200:
            return None
        
        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')

        middletopttxlr = soup.find('div', {'class': 'middletopttxlr'})
        data = []
        for ttxlr in middletopttxlr.contents:
            if ttxlr.name != 'div' : continue
            wxxcont = ttxlr.find(class_='middletopdwxxcont')
            if wxxcont and len(wxxcont.text.replace('\xa0','')) != 0:
                data.append(wxxcont.text)
        
        result = {
            'name':   data[0],
            'uid':    data[1],
            'college':data[2],
            'major':  data[3],
            'class':  data[4]
        }

        return result
    
    def getMainPageSoup(self) -> BeautifulSoup:
        """获取主页面的soup对象

        Returns:
            BeautifulSoup: soup对象
        """
        mainPage   = f'{self.config.domain}{self.config.mainPage}'
        response   = requests.get(mainPage, headers=self.config.headers, cookies=self.cookies)

        if response.status_code != 200:
            self.logger.error(f'响应码错误，错误码{response.status_code}')
            False
        
        soup = BeautifulSoup(response.text, 'html.parser')


        return soup
    
    def getSheetID(self) -> str:
        """获取当前学期ID
        
        例如: 2023-2024-2

        Returns:
            str: xnxq01id 参数
        """
        classTable = f'{self.config.domain}{self.config.classTable}'
        response   = requests.get(classTable, headers=self.config.headers, cookies=self.cookies)

        if response.status_code != 200:
            self.logger.error(f'响应码错误，错误码{response.status_code}')
            return ''
        
        soup = BeautifulSoup(response.text, 'html.parser')

        return str(soup.find(selected="selected")['value'])

    def getNowWeek(self) -> int:
        """获取当前是第几周

        Returns:
            int: 当前的周数
        """

        mainPageSoup = self.getMainPageSoup()

        return int(mainPageSoup.find(class_='main_text main_color').text[1:-1])
    
    def getCourseSheet(self,sheetID=None,parse=False,onlyName=False) -> Union[list,None]:
        """获取学生课程表

        Args:
            sheetID (str, optional): 当前学期ID. Defaults to None.
            parse (bool, optional): 是否解析输出. Defaults to False.
            onlyName (bool, optional): 仅输出课程名称. Defaults to False.

        Returns:
            (list | None): 成功返回list，失败返回None
        """
        if self.cookies is None:
            self.logger.warning('缺少必要参数：cookies')
            return None
        
        if sheetID is None:
            sheetID = self.getSheetID()
        
        rowTup = [[],[],[],[],[],[],[]]

        classTable =  f'{self.config.domain}{self.config.classTable}'

        data = {
            'xnxq01id':sheetID
        }

        try:
            response = requests.post(classTable, headers=self.config.headers,data=data, cookies=self.cookies)
        except:
            self.logger.error('网络连接超时！')
            return None
        
        
        soup = BeautifulSoup(response.text, 'html.parser')
        valigns = soup.find_all(valign="top")

        i = 0
        for valign in valigns:
            kbcontent  = valign.find(class_="kbcontent")
            kbcontent1 = valign.find(class_="kbcontent1")

            kbstr = kbcontent1.get_text()
            if len(kbstr.strip()) != 0:
                kb_name = kbstr.split('----------------------')

            d = []
            kb_teacher = valign.find_all(title="老师")
            kb_week    = kbcontent.find_all(title="周次(节次)")
            kb_room    = kbcontent.find_all(title="教室")
    

            if len(kb_teacher) == 0:
                if parse:
                    r = ''
                else:
                    r = []
                rowTup[i%7].append(r)
                i += 1
                continue

            for n in range(len(kb_teacher)):
                c_teacher = kb_teacher[n].text.strip()
                c_week    = kb_week[n].text.strip().split('(周)')
                
                # 修复解析体育课的教室时，报错的Bug
                if len(kb_room) == len(kb_teacher):
                    c_room = kb_room[n].text.strip()
                else:
                    c_room = '无教室'

                c_name    = kb_name[n].split(c_week[0])[0].replace('&nbsp',' ')
                c_time    = c_week[1].replace('节','')[1:-1]

                if onlyName:
                    r2 = (c_name)
                else:
                    r2 = (
                        c_name,
                        c_teacher,
                        c_week[0],
                        c_time,
                        c_room
                    )

                if parse:
                    r2 = ''.join(r2)
                    d.append(r2)
                else:
                    d.append(r2)


            if parse:
                rowTup[i%7].append('\n'.join(d))
            else:
                rowTup[i%7].append(d)

            i += 1
        
        return rowTup


    def downloadSheet(self,sheetID=None,week='',download_all=False) -> bool:
        """下载学生课程表

        Args:
            sheetID (str, optional): 当前学期ID. Defaults to None.
            week (str, optional): 下载第几周的数据. Defaults to ''.
            download_all (bool, optional): 下载当前学期的所有课程. Defaults to False.

        Returns:
            bool: 是否保存成功
        """
        if self.cookies is None:
            self.logger.warning('缺少必要参数：cookies')
            return False
        
        if sheetID is None:
            sheetID = self.getSheetID()

        # 解析HTML内容
        mainPageSoup = self.getMainPageSoup()

        if not download_all and len(week) == 0:
            week = self.getNowWeek()

        # 获取所有的 option 标签
        options = mainPageSoup.find_all('option')
        # 遍历 option 标签并获取 value 属性
        kbjcmsid = [option['value'] for option in options][0]
        download =  f'{self.config.domain}{self.config.xskbPrint}?xnxq01id={sheetID}&zc={week}&kbjcmsid={kbjcmsid}'

        try:
            file = requests.get(download, headers=self.config.headers, cookies=self.cookies).content
        except:
            self.logger.error('网络连接超时！')
            return False
        kb_path = f"{self.ROOT}/xls/{self.getStudentInfo()['name']}-{sheetID}.xls"

        if os.path.exists(kb_path):
            os.remove(kb_path)
        
        try:
            with open(kb_path,'wb') as f:
                f.write(file)
            return True
        except:
            return False


    