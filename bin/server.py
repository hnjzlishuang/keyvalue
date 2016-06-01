from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
from urlparse import urlparse, parse_qs
from urllib import unquote, unquote_plus
from kvstore import kv
import socket
import sys
import urllib
import httplib
import json
import conf
import signal
import os
from SocketServer import ThreadingMixIn
import threading


class KVRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		#parse the query
		try:
			path = urlparse(self.path).path
			if len(path.split('/')) == 3:
				op1 = path.split('/')[1]
				op2 = path.split('/')[2]

				if op1 == 'kv': 
					query = urlparse(self.path).query
					query_components = dict(qc.split("=") for qc in query.split("&"))
					if op2 == 'get' and 'key' in query_components and len(query_components)==1:
						key = unquote_plus(query_components['key'])
						self.get(key)

				if op1 == 'kvman':
					if op2 == 'countkey':
						self.countkey()
					elif op2 == 'dump':
						self.dump()
					elif op2 == 'shutdown':
						self.shutdown()

			if self.path == '/getdata':
				self.dump()
		except:
			pass

		#send response
	def do_POST(self):
		try:
		#read and parse data
			length = self.headers['content-length']
			data = self.rfile.read(int(length))
			# print data
			# data = unquote(unquote_plus(data))
			# print data
			query_components = dict(qc.split("=") for qc in data.split("&"))
			if 'key' in query_components:
				key = unquote_plus(query_components['key'])
			if 'value' in query_components:
				value = unquote_plus(query_components['value'])


			if self.path == '/kv/insert':
				self.insert(key, value)
			if self.path == '/kv/delete':
				self.delete(key)
			if self.path == '/kv/update':
				self.update(key, value)
		except:
			pass

	def get(self, key):
		self.send_response(200)
		result = db.get(key)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		self.wfile.write(result)

	def insert(self, key, value):
		self.send_response(200)
		print key
		print value
		result = db.insert(key, value)
		print result
		self.send_header("Content-type", "application/json")
		self.end_headers()

		if ask_backup():
			params = urllib.urlencode({'key': key, 'value':value})
			conn = httplib.HTTPConnection(conf.BACKUP, conf.PORT, timeout=conf.TIMEOUT)
			conn.request('POST', '/kv/insert', params)
			response = conn.getresponse()

		self.wfile.write(result)

	def delete(self, key):
		self.send_response(200)
		result = db.delete(key)
		self.send_header('Content-type', 'application/json')
		self.end_headers()

		if ask_backup():
			params = urllib.urlencode({'key': key})
			conn = httplib.HTTPConnection(conf.BACKUP, conf.PORT, timeout=conf.TIMEOUT)
			conn.request('POST', '/kv/delete', params)
			response = conn.getresponse()

		self.wfile.write(result)

	def update(self, key, value):
		self.send_response(200)
		result = db.update(key, value)
		self.send_header('Content-type', 'application/json')
		self.end_headers()

		if ask_backup():
			params = urllib.urlencode({'key': key, 'value': value})
			conn = httplib.HTTPConnection(conf.BACKUP, conf.PORT, timeout=conf.TIMEOUT)
			conn.request('POST', '/kv/update', params)
			response = conn.getresponse()

		self.wfile.write(result)

	def countkey(self):
		self.send_response(200)
		result = db.countkey()
		self.send_header('Content-type', 'application/json')
		self.end_headers()
		self.wfile.write(result)

	def dump(self):
		self.send_response(200)
		result = db.dump()
		self.send_header('Content-type', 'application/json')
		self.end_headers()
		self.wfile.write(result)

	def shutdown(self):
		self.send_response(200)
		self.end_headers()
		self.wfile.write('')
		# server.server_close()
		primary_pid = int(open('conf/primary_pid').read().strip())
		os.kill(primary_pid, signal.SIGKILL)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def ask_backup():
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		result = sock.connect_ex((conf.BACKUP, conf.PORT))
		sock.close()
		return result == 0
	except:
		return False

def fetch():
	print "Fetching data from backup"
	conn = httplib.HTTPConnection(conf.BACKUP, conf.PORT, timeout=conf.TIMEOUT)
	conn.request('GET', '/getdata')
	response = conn.getresponse()
	data = json.loads(response.read())
	for pair in data:
		db.insert(pair[0], pair[1])

db = kv()

server = ThreadedHTTPServer((conf.PRIMARY, conf.PORT), KVRequestHandler)
if ask_backup():
	print "Backup is ready"
	try:
		fetch()
	except:
		print "Backup just went down"
else:
	print "Backup is not ready"

print 'starting to serve as primary'
server.serve_forever()


