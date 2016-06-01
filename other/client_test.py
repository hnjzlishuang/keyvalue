import httplib
httpClient = None
try:
	httpClient = httplib.HTTPConnection('localhost', 8003, timeout=30)
	httpClient.request('POST', '/success')

	response = httpClient.getresponse()
	print response.status
	print response.reason
	print response.read()
	print response.getheaders()
except Exception, e:
	print e
finally:
	if httpClient:
		httpClient.close()