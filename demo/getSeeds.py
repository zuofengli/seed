import demo
import pymongo
from datetime import datetime 
from pymongo import MongoClient

MAIN_COLLECTION_NAME = 'seeds'
client = MongoClient('mongodb://localhost:27017/')
db = client.KG
THISRUN_DATETIME = datetime.now().strftime('%Y_%m_%d_%H_%M')
filePathName = '{root}//data//exports//seeds.export.{name}.tsv'.format(root = demo.ROOT_DIR, name = THISRUN_DATETIME)
exportFile = open(filePathName, 'w')

####remove duplication 2017.10.12
exported_url_list = []

titles = ['source', 'media', 'title', 'url']
exportFile.write('\t'.join(titles))
exportFile.write('\n')
for webInfo in db[MAIN_COLLECTION_NAME].find():
    if webInfo['url'] in exported_url_list:
        continue
    else:
        exported_url_list.append(webInfo['url'])
    values = []
    for title in titles:
        values.append(webInfo[title])
    exportFile.write('\t'.join(values).encode('utf8'))
    exportFile.write('\n')
exportFile.close()     