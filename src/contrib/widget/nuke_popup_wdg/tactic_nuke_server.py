# Copyright (c) 2009 The Foundry Visionmongers Ltd.  All Rights Reserved.

import socket, threading
import nuke
from nukescripts import utils

HOST='localhost'
PORT=50007

class server():
  """
  Example of running a IPV6 socket server on a separate thread inside Nuke
  The default command is to create the named node
  
  from nukescripts import server
  server.threaded_server()
  """

  def __init__(self, host = HOST, port = PORT):
    for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
      af, socktype, proto, canonname, sa = res
      try:
        self.s = socket.socket(af, socktype, proto)
      except socket.error, msg:
        self.s = None
        continue
      try:
        self.s.bind(sa)
        self.s.listen(1)
      except socket.error, msg:
        self.s.close()
        self.s = None
        continue
      break

    if not self.s: raise RuntimeError, "Unable to initialise server"

  
  def start(self):
    while 1:
      try:
        (conn, addr) = self.s.accept()
        data = conn.recv(4096)
        data = data.strip()
        print "TACTIC [%s]" %data
        result =  nuke.executeInMainThreadWithResult(tactic_exec, (data,) )
        conn.send(str(result))
	conn.close()
      except Exception, e:
        print str(e)
        print "Error: restarting ..."
    

def start_server(host = HOST, port = PORT):
  s = server(host, port)
  s.start()

def threaded_server():
  t = threading.Thread(None, start_server)
  t.start()

def tactic_exec(cmd):
  data  = {}
  exec(cmd)
  return data
  
def log_tactic_temp(path, data):
  fp = open(path ,"w")
  fp.write(data)
  fp.close()

def main():
  ## start the server
  threaded_server()
  
if __name__ == '__main__':
  main()
  
