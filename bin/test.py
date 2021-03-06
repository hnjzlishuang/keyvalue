# coding=utf-8
import httplib
import urllib
import conf
import threading
import json
import time
import numpy as np
httpClient = None
eps = 1e-9

class Request():
	def __init__(self):
		self.success_count = 0
		self.insert_latency = []
		self.get_latency = []
	def get(self, key):
		params = urllib.urlencode({'key':key})
		try:
			conn = httplib.HTTPConnection(conf.PRIMARY, conf.PORT, timeout=conf.TIMEOUT)

			conn.request('GET', '/kv/get'+'?' + params)
			start = time.time()
			response = conn.getresponse()
			end = time.time()

			self.get_latency.append(end-start)

			return response
		except:
			pass

	def insert(self, key, value):
		params = urllib.urlencode({'key': key, 'value':value})
		
		
		try:
			conn = httplib.HTTPConnection(conf.PRIMARY, conf.PORT, timeout=conf.TIMEOUT)
			conn.request('POST', '/kv/insert', params)
			start = time.time()
			response = conn.getresponse()
			end = time.time()
			if '' != response.read():
				self.success_count += 1
				self.insert_latency.append(end-start)
			return response
		except:
			pass

	def delete(self, key):
		params = urllib.urlencode({'key': key})

		conn = httplib.HTTPConnection(conf.PRIMARY, conf.PORT, timeout=conf.TIMEOUT)

		conn.request('POST', '/kv/delete', params)

		response = conn.getresponse()

		return response

	def update(self, key, value):
		params = urllib.urlencode({'key': key, 'value': value})

		conn = httplib.HTTPConnection(conf.PRIMARY, conf.PORT, timeout=conf.TIMEOUT)

		conn.request('POST', '/kv/update', params)

		response = conn.getresponse()

		return response

	def countkey(self):

		conn = httplib.HTTPConnection(conf.PRIMARY, conf.PORT, timeout=conf.TIMEOUT)

		conn.request('GET', '/kvman/countkey')

		response = conn.getresponse()

		return response

	def dump(self):
		conn = httplib.HTTPConnection(conf.PRIMARY, conf.PORT, timeout=conf.TIMEOUT)

		conn.request('GET', '/kvman/dump')

		response = conn.getresponse()

		return response

	def shutdown(self):
		conn = httplib.HTTPConnection(conf.PRIMARY, conf.PORT, timeout=conf.TIMEOUT)

		conn.request('GET', '/kvman/shutdown')

		response = conn.getresponse()

		return response
	def test(self, response):
		# print response.status
		print response.reason
		# result = json.loads(response.read())
		# print result
		# if result['success'] == "True":
		# 	self.success_count += 1
		# print response.getheaders()

success = True

rq = Request()
keys = ['he  he""', '=+=', '汉字', '\%\%', '3&key=']
values = ['yinhao', '=+=', '测试', '!!**', '&&&']
for i in range(len(keys)):
	try:
		rq.insert(keys[i], values[i])
		response = rq.get(keys[i])
		result = json.loads(response.read())
	# print response.read()
		if result['success']!="true" or result['value'] != values[i].decode('utf-8'):
			# print result
			success = False
	except:
		success = False

# print success
threads_insert = []
threads_get = []
num = 2000
try:
	for i in range(num):
		threads_insert.append(threading.Thread(target = rq.insert, args=(str(i), str(i+1))))
		threads_insert[-1].start()

	for i in range(num):
		threads_insert[i].join()

	for i in range(num):
		threads_get.append(threading.Thread(target = rq.get, args=(str(i),)))
		threads_get[-1].start()
	
	for i in range(num):
		threads_get[i].join()
except:
	success = False

# print success
insert_count = num + len(keys)
if success == True and (insert_count - rq.success_count) < 1500:
	toprint = "success"
else:
	toprint = "fail"
print "Result: {}".format(toprint)
print "Insertion: {}/{}".format(rq.success_count, insert_count)

il = sum(rq.insert_latency)/float(len(rq.insert_latency)+eps)
gl = sum(rq.get_latency)/float(len(rq.get_latency)+eps)
print "Average latency: {}/{}".format(il, gl)

print "Percentile latency: {}/{}, {}/{}, {}/{}, {}/{}".format(\
	np.percentile(rq.insert_latency, 20), np.percentile(rq.get_latency, 20),
	np.percentile(rq.insert_latency, 50), np.percentile(rq.get_latency, 50),
	np.percentile(rq.insert_latency, 70), np.percentile(rq.get_latency, 70),
	np.percentile(rq.insert_latency, 90), np.percentile(rq.get_latency, 90))

# rq.dump()
# rq.insert('111', '222')
# rq.insert('333', '444')
# # rq.insert()
# rq.insert('torch', 'sucks')
# rq.insert('caf fe', 'sucks mo  e')
# rq.get('caf fe')
# rq.insert('tf', 'dont+know')
# rq.insert('==', '==')
# rq.get('==')
# rq.insert('''"""hehe""lll""''', '''""""""hw'"'"''')
# rq.insert('汉字测试', '哈哈')
# rq.delete('汉字测试')
# rq.delete("汉字测试")
# rq.update('tf', 'good to use')
# rq.update('tf', 'haha')
# rq.delete('haha')
# # rq.delete('torch')
# rq.get('torch')
# rq.get('tf')
# rq.delete('333')
# rq.dump()
# rq.countkey()
# rq.shutdown()



