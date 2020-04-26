#!/usr/bin/env python
###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

# Repurposed from: http://odforce.net/wiki/index.php/PythonToHoudini 

__all__ = ['HoudiniSocket']

import socket, string , sys


class HoudiniSocket:

    #Define the system and port number - port should prob be passed as an arg
    SERVER = 'localhost'
    PORT = 10389

    def __init__(self):
        #define the socket to Houdini
        self.HOU = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, port=None):
        "Open a connection with Houdini"
        if not socket:
            self.HOU.connect((self.SERVER, self.PORT))
        else:
            self.HOU.connect((self.SERVER, int(port) ))
        return()

    def send_data(self, command):
        "Pass a command to Houdini"
        self.HOU.send(command + '\n')
        return()

    def get_data(self):
        "Keep grabbing data from Houdini until you hit the delimiter"
        delimiter = '\x00'
        buffer = ""
        while delimiter not in buffer:
            buffer = buffer + self.HOU.recv(8192)
        return(buffer[:-2]) #trim the delimiter

    def close(self):
        "Close the connection with Houdini"
        self.HOU.close()
        return()


    def hscript(self, cmd):
        self.send_data(cmd)
        buffer = self.get_data()
        return buffer



