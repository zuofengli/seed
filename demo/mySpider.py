import demo
import regex as re
import chardet
import uuid
from datetime import datetime
from pymongo import MongoClient

MAIN_COLLECTION_NAME = 'seeds'

#client = MongoClient()
client = MongoClient('mongodb://localhost:27017/')
db = client.KG
db.drop_collection(MAIN_COLLECTION_NAME)


import os
import urllib2
import html2text
 



URLS_DIR = '{root}//data//URLs'.format(root = demo.ROOT_DIR)
def toBeFiltered(url):
    for stopWord in ['wj.qq.com']:
        if url.find(stopWord)>=0:
            return True
    return False


urllist = []
for fileName in os.listdir(URLS_DIR):
    filePathName = '{root}//data//URLs//{name}'.format(root = demo.ROOT_DIR, name = fileName)
    lines =  open(filePathName, 'r').readlines()
    for index in range(1, len(lines)):
        line = lines[index].strip()
        fds = line.split(',')
        url = fds[4].strip('"')
        #if len(url) > 10:
        if toBeFiltered(url):
            continue
            
        if url.lower().find('http') >=0:
            urllist.append(url)
def selectOneField(fields, index):
    if index == -1:
        hasChineseChar = False
        for char in fields[index]:
            if not re.search(' a-zA-Z\.', char):
                hasChineseChar = True
        if hasChineseChar:
            return fields[index]
        else:
            return fields[-2]
            
    return fields[index]
def getMediaName(webPageInfo):
    title = webPageInfo['title']
    url = webPageInfo['url']
    
    if url.find('http://www.shanghai.gov.cn')>=0:
        return u'上海政府网'
    
    for splitter in [u'--', u' - ', u'|',u'-', u'_', u'——', u' ']:
        fds = title.split(splitter)
        if len(fds) > 1:
            if fds[-1] in [u'百度百科']:
                return fds[-1]
            else:
            
                for jiguan in [u'大学',u'日报']:
                    if fds[0].find(jiguan) == len(fds[0]) - len(jiguan) and not title.find(u'大学吧')>=0:
                        return selectOneField(fds, 0)
                return selectOneField(fds, -1)
    if url.find('mp.weixin.qq.com')>=0:
        rlt = re.search(u'【(.*)】', title)
        if rlt:
            return rlt.group(1)
    
    if url.find('mp.weixin.qq.com')>=0:
        return u'微信网文'
    
    return 'NDTD'
'''
来源: 上观新闻  作者:彭德倩 2017-09-25 17:30:16
来源：新民晚报 | 作者：邵宁 | 编辑：乐先文
【来源】文汇报
'''
def getSource(htmlResponse, htmlText):
    '''
    htmlText: unicode, string
    '''
    
    if htmlResponse.url.find('http://news.sina.com.cn') ==0:
        return ''.join(htmlResponse.xpath('//span/span/span/a/text()').extract())
    else:
    
        #lines = htmlText.split('\n')
        
        #for line in lines:
        rlt = re.search(u'来源[:：】](\W*)(\w+)\W', htmlText)
        if rlt:
            if rlt.group(1).find('\n')>=0:
                pass
            else:
                return rlt.group(2)
        return 'NDTD'

THISRUN_DATETIME = datetime.now().strftime('%Y_%m_%d_%H_%M')
htmlFileFolder = '{root}//data//htmls//{dt}'.format(root = demo.ROOT_DIR, dt = THISRUN_DATETIME)
import os
os.makedirs(htmlFileFolder)

txtFileFolder = '{root}//data//txts//{dt}'.format(root = demo.ROOT_DIR, dt = THISRUN_DATETIME)
import os
os.makedirs(txtFileFolder)

import scrapy
class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    #start_urls = ['http://www.pumch.ac.cn/Category_171/Index.aspx']
    start_urls = urllist

    def parse(self, response):
        pageInfo = {}
        pageInfo['url'] = response.url
        
        title = ''.join(response.xpath('//title/text()').extract()).strip()
        pageInfo['title'] = title
        
        pageInfo['media'] = getMediaName(pageInfo)
        
        
        #uniqueName = response.url.encode('hex')
        uniqueName = str(uuid.uuid1())
        pageInfo['uid'] = uniqueName
        
        htmlFile = open('{root}//data//htmls//{dt}//{name}.html'.format(root = demo.ROOT_DIR, dt = THISRUN_DATETIME, name = uniqueName),'w')
        #htmlFile.write(response.text.encode('utf8'))
        bodyHtml = response.body
        htmlFile.write(bodyHtml)
        htmlFile.close()
        
        txtFile = open('{root}//data//txts//{dt}//{name}.txt'.format(root = demo.ROOT_DIR, dt = THISRUN_DATETIME, name = uniqueName),'w')
        #htmlFile.write(response.text.encode('utf8'))
        h = html2text.HTML2Text()
        h.ignore_links = True
        
        myHTMLCoding = chardet.detect(bodyHtml)
        if myHTMLCoding['encoding'] in ['ascii','GB2312']:
            bodyHtml = bodyHtml.decode('gbk')
            bodyHtml = bodyHtml.encode('utf8')
            
        if myHTMLCoding['encoding'] in ['windows-1252','ISO-8859-2']:
            bodyHtml = bodyHtml.encode('utf8')
            
        #print 145
        #print isinstance(bodyHtml, unicode)
        #print pageInfo['uid']
        #print pageInfo['url']
        #raw_input(chardet.detect(bodyHtml))
        
        sContent = h.handle(bodyHtml.decode('utf8', 'ignore'))
        
        myTextCoding = chardet.detect(sContent)
        if not myTextCoding['encoding'] in ['ascii','windows-1252','ISO-8859-2']:
            try:
                sContent = sContent.decode(myTextCoding['encoding'], 'ignore')
            except:
                
                raw_input(myTextCoding)
        
        txtFile.write(sContent.encode('utf8'))
        txtFile.close()
        
        pageInfo['source'] = getSource(response, sContent)

        #print response.text.encode('hex','ignore')
        #print hexStr.decode('hex').encode('gbk')
        db[MAIN_COLLECTION_NAME].insert(pageInfo)
        
        image_urls = response.xpath('//img//@src').extract()#提取图片链接
        #aw_input(image_urls)
        dir_path = '{root}//data//images'.format(root = demo.ROOT_DIR)
        for image_url in image_urls:
            list_name=image_url.split('/')
            file_name=list_name[len(list_name)-1]#图片名称
            file_path='%s/%s'%(dir_path,file_name)
            if os.path.exists(file_name):
                continue

            with open(file_path,'wb') as file_writer:
                conn=urllib2.urlopen(image_url)#下载图片
                file_writer.write(conn.read())
                file_writer.close()
