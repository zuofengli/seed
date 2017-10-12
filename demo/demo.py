import sys,os
_curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) ))
head, tail = os.path.split(_curpath)
while tail != 'demo':
    path = head
    head, tail = os.path.split(path)
ROOT_DIR = head
BIN_DIR = os.path.join(ROOT_DIR, 'bin')
DATA_DIR = os.path.join(ROOT_DIR, 'data')
PDFS_DIR = '{root}//data//pdfs'.format(root = ROOT_DIR)
TXTS_DIR = '{root}//data//txts'.format(root = ROOT_DIR)
sys.path.append(ROOT_DIR)
sys.path.append(BIN_DIR)



    