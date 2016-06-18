# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 17:30:37 2016

@author: Administrator
"""

import urllib
import urllib.request
import http.cookiejar
from bs4 import BeautifulSoup
import os
import zipfile
import pandas as pd
import copy
import time
import json

class spider():
    
    def __init__(self):
        self.homepage = 'http://data.cma.cn/site/index.html'
        self.logpage = 'http://data.cma.cn/user/Login.html'
        self.vericodepage = 'http://data.cma.cn/site/captcha/v/575fd23f3d1c0.html'
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36'
        self.head = {'User-Agent':self.user_agent}
        self.id = 'luokai0223@126.com'
        self.pw = 'qxsam0223'
        self.postdict = {'userName':self.id, 'password':self.pw, 'verifyCode':'1234'}
        self.codepath = 'C:/Users/luokai/Desktop/code.png'
        self.datapage = 'http://data.cma.cn/dataService/index/datacode/A.0029.0001.html'
        self.datapage1 = 'http://data.cma.cn/dataService/ajax.html'
        self.formdata1 = {'act':'getStationsByProvinceID','provinceID':'num','dataCode':'A.0029.0001'}
        self.filepath = 'c:/github/weat/data/'
        
    def getopener(self,head):    #创建一个带cookie的opener
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        header = []
        for key,value in head.items():
            elem = (key,value)
            header.append(elem)
        opener.addheaders = header
        return opener
        
    def getcookie(self):    #请求验证码页面更新cookies
        postdata = urllib.parse.urlencode(self.postdict).encode()
        old_opener = self.getopener(self.head)
        old_opener.open(self.vericodepage, postdata)
        return old_opener
        
    def getvericode(self):    #获取验证码
        opener = self.getcookie()
        vericode = opener.open(self.vericodepage).read()
        with open(self.codepath,'wb') as file:
            file.write(vericode)
        return opener
        
    def login(self):    #登陆网站，跳转首页获取用户名
        opener = self.getvericode()
        vericode = str(input('please type the code:'))
        self.postdict['verifyCode'] = vericode
        postdata = urllib.parse.urlencode(self.postdict).encode()
        loginrequest = opener.open(self.logpage,postdata)
        afterlogin = opener.open(self.homepage)
        soup = BeautifulSoup(afterlogin.read().decode('utf-8'))
        if soup.find_all(href="/user/info.html"):
            name = soup.find_all(href="/user/info.html")[0].string
            print('登录成功，登录名：',name)
            return opener
        else:
            print('登录失败！')
            return 'fail'
            
    def savejsonfile(self):    #利用登陆后的cookies请求数据页面，保存所有地区信息
        p_id_list = []
        with open('provinceID.csv') as f:
            for i in f.read().split():
                p_id_list.append(i)
        jsonfilelist = []
        formdata1 = copy.deepcopy(self.formdata1)
        opener = self.login()
        if opener == 'fail': return
        for i,id in enumerate(p_id_list):
            newdict = copy.copy(formdata1)
            newdict['provinceID'] = id
            formdata = urllib.parse.urlencode(newdict).encode()
            datapage = opener.open(self.datapage1,formdata)
            jsondata = datapage.read().decode('utf-8')
            jsonfilepath = 'C:/github/weat/data/'+'data'+str(i+1)+'.json'
            jsonfilelist.append(jsonfilepath)
            try:
                with open(jsonfilepath) as file:
                    if file:
                        print('第',i+1,'个文件已存在，跳过保存')
                        continue
            except:pass
            with open(jsonfilepath,'w') as file:
                file.write(jsondata)
            time.sleep(1)
            print('保存第', i+1, '个')
        return jsonfilelist
        
    def processjsonfile(self):    #读取保存的地区json文件，生成一个地区详情的df
        file_list = self.savejsonfile()
        dflist = []
        for i in file_list:
            with open(i,'r') as file:
                jsondata = json.loads(file.read())
                df = pd.DataFrame(jsondata['stations'])
                df['cityName'] = jsondata['cityName']
                dflist.append(df)
        totaldf = pd.concat(dflist)
        return totaldf
                
    def getfilename(self):    #生成天气zip文件列表
        filelist = os.listdir(self.filepath)
        pathlist = [self.filepath + x for x in filelist]
        return pathlist
        
    def readzip(self,filepath,num):    #读取zip文件，生成对应的一个df
        onelist = []
        with zipfile.ZipFile(filepath, 'r') as onezip:
            with onezip.open(onezip.namelist()[int(num)], 'r') as onefile:
                for i in onefile.readlines():
                    onelist.append(i.decode('utf-8').split())
        if num == 0:
            for i in range(1,4):
                onelist[i].insert(2,'')
            df0 = pd.DataFrame(onelist[1:], columns = onelist[0][:4])
            return df0
        df1 = pd.DataFrame(onelist[1:], columns = onelist[0])
        return df1
        
    def getweather(self):    #合并所有df
        pathlist = self.getfilename()
        dflist = []
        for i,file in enumerate(pathlist):
            onedf = self.readzip(file,1)
            dflist.append(onedf)
            print('读取第',i+1,'个表格')
        alldf = pd.concat(dflist)
        return alldf
           
                    
a = spider()
df = a.processjsonfile()


                    
        
    


        
        