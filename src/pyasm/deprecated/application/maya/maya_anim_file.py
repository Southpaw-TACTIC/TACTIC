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

import cStringIO

from maya_environment import *


class MayaAnimFile:
    '''Provides ability to extract some limited information from the file
    generated from the mayaImport/mayaExport plugin that is shipped with Maya
    '''

    def __init__(my, path):
        my.path = path
        my.buffers = {}
        my.static_buffers = {}

    def parse(my):
        my.parse_v01()
        my.parse_v01('STATIC')


    def parse_v01(my, file_type='ANIM'):
        file = open(my.path, "r")
        buffer = None
        instance = None

        # parse the file and store by instance
        for line in file.readlines():
            line = line.rstrip()
            # //END is not needed for parsing, a visual indicator only
            if line.startswith("//START_%s="%file_type)\
                or line.startswith("//START="): # backward-compatibility

                index = line.index("=")
                instance = line[index+1:]
                buffer = cStringIO.StringIO()

                # maintain backwards compatibility with old maya instances
                if instance.find(":") != -1:
                    instance, tmp = instance.split(":",1)
                
                if file_type=='STATIC':
                    my.static_buffers[instance] = buffer
                else:
                    my.buffers[instance] = buffer
            
            #if line.startswith("// POS:  <tx>34.43</tx><ty>

        
            if instance != None:
                buffer.write(line)
                buffer.write("\n")
            
            if line.startswith("//END_%s="%file_type)\
                or line.startswith("//END="): # backward-compatibility
                instance == None
                
        file.close()


    def write_v01(my, buffer):
        pass






    def get_anim(my, instance):

        try:
            return my.buffers[instance].getvalue()
        except KeyError, e:
            return ""

    def get_static(my, instance):

        try:
            return my.static_buffers[instance].getvalue()
        except KeyError, e:
            return ""
         
       




if __name__ == '__main__':

    anim_file = MayaAnimFile("./set100_0000005349.anim")
    anim_file.parse()

    print anim_file.get_anim( "alarm_clock_C:product202")


