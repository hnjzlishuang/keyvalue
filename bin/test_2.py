import requests, json
import unittest
import os
from time import sleep
import subprocess
from subprocess import Popen
from threading import Thread
import threading
def parse_output(r,k):
    if not r or not r.text:
        return None
    #print(r.text)
    output = json.loads(r.text)
    if k in output:
        return output[k]
    else:
        return None

class TestStringMethods(unittest.TestCase):
    url = ''
    path_insert='/kv/insert'
    path_update='/kv/update'
    path_delete='/kv/delete'
    path_get='/kv/get?key='

    def setUp(self):
        with open('../conf/settings.conf') as f:
            d = json.load(f)
            self.url = 'http://'+d['primary']+':'+d['port']

    def do_insert(self,payload):
        r = requests.post(self.url+self.path_insert, data=payload)
        self.assertEqual(parse_output(r,'success'),'true')
        print('Insert success')

    def do_update(self,payload):
        r = requests.post(self.url+self.path_update, data=payload)
        self.assertEqual(parse_output(r,'success'),'true')

    def do_delete(self,key):
        payload={'key':key}
        r = requests.post(self.url+self.path_delete, data=payload)
        self.assertEqual(parse_output(r,'success'),'true')
        return parse_output(r,'value')

    def do_get(self, key):
        r = requests.get(self.url+self.path_get+key)
        self.assertEqual(parse_output(r,'success'),'true')
        return 'This is output of do_get:  ' + parse_output(r,'value')

    def od_insert(self,payload):
        r = requests.post(self.url+self.path_insert, data=payload)
        self.assertEqual(parse_output(r,'success'),'false')

    def od_update(self,payload):
        r = requests.post(self.url+self.path_update, data=payload)
        self.assertEqual(parse_output(r,'success'),'false')

    def od_delete(self,key):
        payload={'key':key}
        r = requests.post(self.url+self.path_delete, data=payload)
        self.assertEqual(parse_output(r,'success'),'false')
        return parse_output(r,'value')

    def od_get(self, key):
        r = requests.get(self.url+self.path_get+key)
        self.assertEqual(parse_output(r,'success'),'false')
        return parse_output(r,'value')
    
    def do_dump(self):
        r = requests.get(self.url+'/kvman/dump') #problematic
        return r

    def two(self):
        pid = os.fork()
        if pid != 0:
            sleep(1)
        self.do_insert({'key': 'sha', 'value': str(pid)})
        print (self.do_delete('sha') )
        
    def many(self):
        for i in range(1,90):
            pid = os.fork()
            if pid == 0:
                self.do_insert({'key': str(os.getpid()), 'value': '0'})
                return
            sleep(0.05)
            if pid != 0:
                print (self.do_delete(str(pid)))
            #payload={'key':str(os.getpid())}
            #requests.post(self.url+self.path_delete, data=payload)

    def toomany(self):
        ''' may be too many things will cause bug...'''
        mainpid = os.getpid()
        #self.do_insert({'key': 'oldman', 'value': 'twooo'})
        for i in range(1,6):
            os.fork()
            self.do_insert({'key': str(os.getpid()), 'value': str(os.getpid())})
            sleep(0.001)
            self.do_delete(str(os.getpid()))
        #if mainpid == os.getpid():
            #print(self.do_delete('oldman'))

    # This is xpd1's part

    def fork_insert(self,id):
        self.do_insert({'key': 'HandsomeXuwei'+str(id), 'value': str(id*10)})
    def fork_insertFail(self,id):
        self.od_insert({'key': 'HandsomeXuwei'+str(id), 'value': str(id*10)})
    def fork_get(self,id):
        print(self.do_get('HandsomeXuwei'+str(id)))
    def fork_update(self,id,value):
        self.do_update({'key': 'HandsomeXuwei'+str(id), 'value': str(value)})
    def testTeacher1(self):
        '''
        os.chdir('..');
        proc = Popen('python primary_server.py', shell=True,
             stdin=None, stdout=None, stderr=None, close_fds=True)
        proc = Popen('python backup_server.py', shell=True,
             stdin=None, stdout=None, stderr=None, close_fds=True)
        '''
        medemede = 3000
        pP = Popen(['python', 'primary_server.py'], cwd='..') # something long running
        pB = Popen(['python', 'backup_server.py'], cwd='..') # something long running
        sleep(3)
        
        threadid = [0]
        for i in range(1,medemede+1):
            if i == 1:
               threadid.append(Thread(self.fork_insert(1)))
               threadid[i].start()
               threadid[i].join()
               continue
            else:
               threadid.append(Thread(self.fork_update(1,i*10)))
            threadid[i].start()

        for i in range(1,medemede+1):
            threadid[i].join()

        
        r = requests.get(self.url+'/kvman/countkey')
        self.assertEqual(parse_output(r,'result'),str(1))
        print('countkey OK ' + str(medemede))

        for i in range(1,1+1):
            threadid[i] = Thread(self.fork_get(i))

        pP.terminate()
        pB.terminate()
        
        pass

    


class RunPrimary(threading.Thread):
    def run(self):
        os.chdir("/..");
        os.system('python primary_server.py')
        pass
class RunBackup(threading.Thread):
    def run(self):
        os.chdir("/..");
        os.system('python backup_server.py')
        pass

if __name__ == '__main__':
    unittest.main();
