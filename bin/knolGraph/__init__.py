class dbPediaCn():
	def __init__(self):
		pass
	def parse(self, entity):
		url = 'http://knowledgeworks.cn:30001/?p={word}'.format(word = entity.encode('utf8'))
		s=urllib2.urlopen(url)
		print s.read().decode('utf8')