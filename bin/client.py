# coding=utf-8
import httplib
import urllib
import conf
import json
httpClient = None

class Request():
	def get(self, key):
		params = urllib.urlencode({'key':key})

		conn = httplib.HTTPConnection(conf.PRIMARY, conf.PORT, timeout=30)

		conn.request('GET', '/kv/get'+'?' + params)

		response = conn.getresponse()

		self.test(response)

		return response

	def insert(self, key, value):
		params = urllib.urlencode({'key': key, 'value':value})
		
		conn = httplib.HTTPConnection(conf.PRIMARY, conf.PORT, timeout=30)
		
		conn.request('POST', '/kv/insert', params)
		
		response = conn.getresponse()

		self.test(response)

		return response

	def delete(self, key):
		params = urllib.urlencode({'key': key})

		conn = httplib.HTTPConnection(conf.PRIMARY, conf.PORT, timeout=30)

		conn.request('POST', '/kv/delete', params)

		response = conn.getresponse()

		self.test(response)

		return response

	def update(self, key, value):
		params = urllib.urlencode({'key': key, 'value': value})

		conn = httplib.HTTPConnection(conf.PRIMARY, conf.PORT, timeout=30)

		conn.request('POST', '/kv/update', params)

		response = conn.getresponse()

		self.test(response)

		return response

	def countkey(self):

		conn = httplib.HTTPConnection(conf.PRIMARY, conf.PORT, timeout=30)

		conn.request('GET', '/kvman/countkey')

		response = conn.getresponse()

		self.test(response)

		return response

	def dump(self):
		conn = httplib.HTTPConnection(conf.PRIMARY, conf.PORT, timeout=30)

		conn.request('GET', '/kvman/dump')

		response = conn.getresponse()

		self.test(response)

		return response

	def shutdown(self):
		conn = httplib.HTTPConnection(conf.PRIMARY, conf.PORT, timeout=30)

		conn.request('GET', '/kvman/shutdown')

		response = conn.getresponse()

		self.test(response)

		return response
	def test(self, response):
		# print response.status
		# print response.reason
		print response.read()
		# print response.getheaders()


rq = Request()
rq.update('100', '200')
longstr = '&=1'*(10**1)
rq.insert('111', longstr)
# result = json.loads(rq.get('111').read())
# resultstr = result['value']
# if resultstr == longstr:
# 	print 'right'
rq.insert('333', '444')
rq.insert('torch', 'sucks')
rq.insert('caf fe', 'sucks mo e')
rq.get('caf fe')
rq.get('111')
rq.get('torch')
rq.get('333')

rq.insert('+++', '===\%\%呵呵')
rq.get('+++')
rq.delete('+++')
rq.delete('111')
rq.delete(' sss')

rq.update('torch', 'best')
rq.update('caf fe', '哈哈')
rq.get('torch')
rq.get('caf fe')

rq.insert('tf', 'dont+know')
rq.insert('==', '==')
rq.get('==')
rq.insert('''"""hehe""lll""''', '''""""""hw'"'"''')
rq.insert('汉字测试', '哈哈')
rq.delete('汉字测试')
rq.delete("汉字测试")
rq.update('tf', 'good to use')
rq.update('tf', 'haha')
rq.delete('haha')
rq.delete('torch')
rq.get('torch')
rq.get('tf')
rq.delete('333')
rq.insert('+++!!!+++', '*&^%$#@!~()_+')
rq.dump()
rq.countkey()
# rq.shutdown()



