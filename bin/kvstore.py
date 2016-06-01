import json
from collections import OrderedDict
import conf
import threading
class kv():
	def __init__(self):
		self.data = {}
		self.lock = threading.Lock()
		self.locks = {}

	def insert(self,key,value):
		# self.lock.acquire()
		if key not in self.locks:
			self.locks[key] = threading.Lock()
		self.locks[key].acquire()
		print 'acquire lock'
		result = OrderedDict([("success", conf.FALSE)])
		if key in self.data:
			result['success'] = conf.FALSE
		else:
			self.data[key] = value
			result['success'] = conf.TRUE
		self.locks[key].release()
		print 'release lock'
		return json.dumps(result)

	def delete(self, key):
		# self.lock.acquire()
		if key not in self.locks:
			self.locks[key] = threading.Lock()
		self.locks[key].acquire()
		result = OrderedDict([("success", conf.FALSE), ("value", conf.ARB_STR)])
		if key in self.data:
			result['success'] = conf.TRUE
			result['value'] = self.data.pop(key)
		else:
			result['success'] = conf.FALSE
			result['value'] = conf.ARB_STR
		# self.lock.release()
		self.locks[key].release()
		return json.dumps(result)

	def get(self, key):
		result = OrderedDict([("success", conf.FALSE), ("value", conf.ARB_STR)])
		if key in self.data:
			result['success'] = conf.TRUE
			result['value'] = self.data[key]
		else:
			result['value'] = conf.ARB_STR
			result['success'] = conf.FALSE
		return json.dumps(result) 

	def update(self, key, value):
		# self.lock.acquire()
		if key not in self.locks:
			self.locks[key] = threading.Lock()
		self.locks[key].acquire()
		result = OrderedDict([("success", conf.FALSE)])
		if key in self.data:
			self.data[key] = value
			result['success'] = conf.TRUE
		else:
			result['success'] = conf.FALSE
		# self.lock.release()
		self.locks[key].release()
		return json.dumps(result)

	def countkey(self):
		result = OrderedDict([("result", 0)])
		result['result'] = str(len(self.data))
		return json.dumps(result)

	def dump(self):
		result = self.data.items()
		# print json.dumps(result)
		return json.dumps(result)

	# def fetch(self, keys, values):
		
