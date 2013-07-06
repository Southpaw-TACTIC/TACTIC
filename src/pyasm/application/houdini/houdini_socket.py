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

    def __init__(my):
        #define the socket to Houdini
        my.HOU = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(my, port=None):
        "Open a connection with Houdini"
        if not socket:
            my.HOU.connect((my.SERVER, my.PORT))
        else:
            my.HOU.connect((my.SERVER, int(port) ))
        return()

    def send_data(my, command):
        "Pass a command to Houdini"
        my.HOU.send(command + '\n')
        return()

    def get_data(my):
        "Keep grabbing data from Houdini until you hit the delimiter"
        delimiter = '\x00'
        buffer = ""
        while delimiter not in buffer:
            buffer = buffer + my.HOU.recv(8192)
        return(buffer[:-2]) #trim the delimiter

    def close(my):
        "Close the connection with Houdini"
        my.HOU.close()
        return()


    def hscript(my, cmd):
        my.send_data(cmd)
        buffer = my.get_data()
        return buffer



