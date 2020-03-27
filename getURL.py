# -*- coding:utf-8 -*-
import json
import os
import os.path
import re
import subprocess
import sys
import time
import urllib.request
from urllib.request import urlopen

import requests
import requests.utils
from bilibiliupload import *
from bs4 import BeautifulSoup

busername = ""
bpassword = ""

nusername = ""
npassword = ""


videodir = "./videos/"
rootdir = "./"
web = 'https://www.nicovideo.jp/watch/'

with open('cookies.txt','r') as fp1:
    load_cookies = json.load(fp1)
cookies = requests.utils.cookiejar_from_dict(load_cookies)
url = 'https://www.nicovideo.jp/api/nicorepo/timeline/my/all?client_app=pc_myrepo'
r = requests.get(url,cookies = cookies)

b = Bilibili()

if r.status_code != 200:
    #如果cookie失效，则写入cookie
    response = requests.post(
        "https://account.nicovideo.jp/api/v1/login?site=niconico",
        data={'mail_tel': nusername,
                'password': npassword},
        allow_redirects=False
    )
    cookies = requests.utils.dict_from_cookiejar(response.cookies)
    with open('cookies.txt','w') as fp:
        json.dump(cookies,fp)
        fp.close()
else:
    handler = urllib.request.HTTPCookieProcessor(cookies)
    opener = urllib.request.build_opener(handler)
    try:
        response = opener.open(url)
    except:
        pass
    else:
        resp = json.loads(response.read().decode('utf-8'))# 格式化得到的json
        for x in range(0,12,1):
            try:
                if resp['data'][x]['topic'] == "nicovideo.user.video.upload" or resp['data'][x]['topic'] == "nicovideo.channel.video.upload" and resp['data'][x]['video']['status'] == "PUBLIC":
                    sm = resp['data'][x]['video']['id']# sm号
                    url1 = (web + resp['data'][x]['video']['id'])
                    with open('0.txt','r') as f:
                        for line in f.readlines():
                            if url1 in line:
                                f.close()
                            else:
                                print ("视频更新时间：",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                                with open('0.txt','a') as f1:
                                    f1.write(url1 + ',')
                                    f1.close()
                                subprocess.call('youtube-dl --config-location ' + rootdir + 'dl.conf ' + url1, shell=True)
                                print("开始上传时间:",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                                for parent,dirnames,filenames in os.walk(videodir):
                                    for filename in filenames:
                                        name,ext = os.path.splitext(filename)
                                        mp4 = '.mp4'
                                        if ext == mp4:
                                            videotitle = resp['data'][x]['video']['title'] #标题
                                            html = urlopen(url1)
                                            bsObj = BeautifulSoup(html.read(), 'lxml')
                                            keywords = bsObj.find(attrs={"name":"keywords"})['content']#关键字
                                            description = bsObj.find(attrs={"itemprop":"description"})['content']#简介
                                            reg = re.compile('<[^>]+>',re.S) #正则过滤HTML标签
                                            content = reg.sub('',description).replace('\n','').replace(' ','').replace('&amp','').replace('・','·')#替换字符成空格
                                            #前三关键字
                                            keywords1 = keywords.split(",")[0]
                                            keywords2 = keywords.split(",")[1]
                                            keywords3 = keywords.split(",")[2]
                                            ttid = 30
                                            #判断字数
                                            if len(content) > 249:
                                                content = videotitle
                                            else:
                                                content = content
                                            #上传模块
                                            login_status = b.login(busername, bpassword)
                                            print("Login:", login_status)
                                            videoPart = VideoPart(videodir + filename)
                                            tags = {keywords1,keywords2,keywords3}
                                            b.upload(parts=videoPart, title=videotitle, tid=ttid, tag=tags, desc=content, source=sm)
                                            print("上传完毕时间：",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                                            subprocess.call('rm -rf ' + rootdir + 'videos/*.mp4', shell=True)
                                            time.sleep(32)
            except:
                pass
