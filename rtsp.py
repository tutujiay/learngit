#! /usr/bin/python

import socket,time,string,random,thread
import sys,re
import hashlib
RTSP_VERSION = 'RTSP/1.0'
USER_AGENT_STR = 'User-Agent:'
DEFAULT_USERAGENT = 'LibVLC/2.2.8 (LIVE555 Streaming Media v2016.02.22)'
DEFAULT_SERVER_PORT = 554

class rtspClient():
    def __init__(self,url,username,password):
        self.Sock = None
        self.Buffer = ''
        self.CSeq = 2
        self.Url = url
        self.Username = username
        self.Password = password
        self.Session = 0
        self.nonce =None
        self.realm = None
        self.m3=None
        self.Server_ip = self.rtsp_parse_url(url)
        self.rtsp_connect()


    def rtsp_parse_url(self, url):
        ip = None
        m = re.match(r'[rtspRTSP:/]+(?P<ip>(\d{1,3}\.){3}\d{1,3})', url)
        if m is not None:
            ip = m.group('ip')
        # PRINT('ip: %s, port: %d, target: %s'%(ip,port,target), GREEN)
        print("parse url: "+str(ip))
        return ip

    def rtsp_connect(self):
        self.Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Sock.connect((self.Server_ip, DEFAULT_SERVER_PORT))

    def rtsp_OPTIONS(self):
        msg = "OPTIONS " + str(self.Url) + " " + str(RTSP_VERSION) + "\r\n"
        msg += "CSeq: " + str(self.CSeq) + "\r\n"
        msg += str(USER_AGENT_STR) + str(DEFAULT_USERAGENT) + "\r\n"
        msg += "\r\n"
        print(msg)
        self.Sock.send(msg)
        self.CSeq += 1
        self.Buffer = self.Sock.recv(1024)
        print(self.Buffer)

    def rtsp_DESCRIBE(self):
        msg = "DESCRIBE " + str(self.Url) + " " + str(RTSP_VERSION) + "\r\n"
        msg += "CSeq: " + str(self.CSeq) + "\r\n"
        msg += str(USER_AGENT_STR) + str(DEFAULT_USERAGENT) + "\r\n"
        msg += "Accept: application/sdp\r\n"
        msg += "\r\n"
        print(msg)
        self.Sock.send(msg)
        self.CSeq += 1
        self.Buffer = self.Sock.recv(1024)
        print(self.Buffer)
        self.realm = self.Buffer.split("realm=\"")[1].split("\"")[0]
        self.nonce = self.Buffer.split("nonce=\"")[1].split("\"")[0]
        print self.realm
        print self.nonce
        # calc rtsp response by md5
        #response = md5(md5(<username>:<realm>:<password>):<nonce>:md5(<cmd>:<uri>));
        data1 = self.Username +":"+self.realm+":"+self.Password
        data2 = "DESCRIBE:"+self.Url
        m1 = hashlib.md5()
        m1.update(data1.encode())
        m2 = hashlib.md5()
        m2.update(data2.encode())
        self.m3 = hashlib.md5()
        data3 = m1.hexdigest()+":"+self.nonce+":"+m2.hexdigest()
        self.m3.update(data3.encode())
        print self.m3.hexdigest()

        #send DESCRIBE with calated response value.
        msg = "DESCRIBE " + str(self.Url) + " " + str(RTSP_VERSION) + "\r\n"
        msg += "CSeq: " + str(self.CSeq) + "\r\n"
        msg += "Authorization: Digest username=\""+str(self.Username)+"\", realm=\""+str(self.realm)+"\", nonce=\""+str(self.nonce)+"\", uri=\""+str(self.Url)+"\", response=\""+str(self.m3.hexdigest())+"\"\r\n"
        msg += str(USER_AGENT_STR) + str(DEFAULT_USERAGENT) + "\r\n"
        msg += "Accept: application/sdp\r\n"
        msg += "\r\n"
        print(msg)
        self.Sock.send(msg)
        self.CSeq += 1
        self.Buffer = self.Sock.recv(1024)
        print(self.Buffer)


    def rtsp_SETUP(self):
        msg = "SETUP " + str(self.Url) + " " + str(RTSP_VERSION) + "\r\n"
        msg += "CSeq: " + str(self.CSeq) + "\r\n"
        msg += "Authorization: Digest username=\"" + str(self.Username) + "\", realm=\"" + str(self.realm) + "\", nonce=\"" + str(self.nonce) + "\", uri=\"" + str(self.Url) + "\", response=\"" + str(self.m3.hexdigest()) + "\"\r\n"
        msg += str(USER_AGENT_STR) + str(DEFAULT_USERAGENT) + "\r\n"
        msg += "Transport: RTP/AVP;unicast;client_port=64288-64289\r\n"
        msg += "\r\n"
        print(msg)
        self.Sock.send(msg)
        self.CSeq += 1
        self.Buffer = self.Sock.recv(1024)
        self.Session = decodeMsg(self.Buffer)['Session']
        print(self.Buffer)

def calcResponse(method):
    # calc rtsp response by md5
    # response = md5(md5(<username>:<realm>:<password>):<nonce>:md5(<cmd>:<uri>));
    data1 = self.Username + ":" + self.realm + ":" + self.Password
    data2 = "DESCRIBE:" + self.Url
    m1 = hashlib.md5()
    m1.update(data1.encode())
    m2 = hashlib.md5()
    m2.update(data2.encode())
    m3 = hashlib.md5()
    data3 = m1.hexdigest() + ":" + self.nonce + ":" + m2.hexdigest()
    m3.update(data3.encode())
    print m3.hexdigest()


def decodeMsg(strContent):
    mapRetInf = {}
        for str in [elem for elem in strContent.split("\n") if len(elem) >= 1][2:-1]:
        # print str
            tmp2 = str.split(":")
        mapRetInf[tmp2[0]] = tmp2[1][:-1]
        print mapRetInf
        return mapRetInf



if __name__ == '__main__':
    url = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    print(url+username+password)
    rtsp = rtspClient(url,username,password)
    rtsp.rtsp_OPTIONS()
    rtsp.rtsp_DESCRIBE()
    rtsp.rtsp_SETUP()
