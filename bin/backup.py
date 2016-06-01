from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
from urlparse import urlparse, parse_qs
from urllib import unquote, unquote_plus
from kvstore import kv
import socket
import sys
import urllib
import httplib
import conf
import json
from SocketServer import ThreadingMixIn
import threading


class BackupRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		path = urlparse(self.path).path
		if len(path.split('/')) == 3:
			op1 = path.split('/')[1]
			op2 = path.split('/')[2]

			if op1 == 'kvman':
				if op2 == 'countkey':
					self.countkey()
				elif op2 == 'dump':
					self.dump()
				elif op2 == 'shutdown':
					self.shutdown()

		if path == '/getdata':
			self.dump()
			print "Data fetched by primary"


	def do_POST(self):
		#read and parse data
		length = self.headers['content-length']
		data = self.rfile.read(int(length))

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

	def get(self, key):
		self.send_response(200)
		result = db.get(key)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		self.wfile.write(result)

	def insert(self, key, value):
		self.send_response(200)
		result = db.insert(key, value)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		self.wfile.write(result)

	def delete(self, key):
		self.send_response(200)
		result = db.delete(key)
		self.send_header('Content-type', 'application/json')
		self.end_headers()
		self.wfile.write(result)

	def update(self, key, value):
		self.send_response(200)
		result = db.update(key, value)
		self.send_header('Content-type', 'application/json')
		self.end_headers()
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
		# print result

	def shutdown(self):
		self.send_response(200)
		self.end_headers()
		self.wfile.write('')
		# server.socket.close()
		backup_pid = int(open('conf/backup_pid').read().strip())
		os.kill(backup_pid, signal.SIGKILL)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def fetch():
	print "Fetching data from primary"
	conn = httplib.HTTPConnection(conf.PRIMARY, conf.PORT, timeout=300)
	conn.request('GET', '/getdata')
	response = conn.getresponse()
	data = json.loads(response.read())
	for pair in data:
		db.insert(pair[0], pair[1])

def ask_primary():
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		result = sock.connect_ex((conf.PRIMARY, conf.PORT))
		sock.close()
		return result == 0
	except:
		return False

db = kv()
server = ThreadedHTTPServer((conf.BACKUP, conf.PORT), BackupRequestHandler)

if ask_primary():
	print "Primary is ready"
	try:
		fetch()
	except:
		print "Primary just went down"
else:
	print "Primary is not ready"

print 'starting to serve as backup'
server.serve_forever()


