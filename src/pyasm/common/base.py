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

__all__ = ["Base"]


import sys,time


class Base(object):
    """The base class for all classes in the framework"""
    __timing = 0

    def start_timer(my, name="top"):
        from container import Container
        if not Container.has("Base:total:%s" % name):
            Container.put("Base:total:%s" % name, 0)
        start = time.time()
        Container.put("Base:start:%s" % name, start)

    def end_timer(my, name="top"):
        end = time.time()
        from container import Container
        start = Container.get("Base:start:%s" % name)
        diff = end - start
        total = Container.get("Base:total:%s" % name)
        total += diff
        Container.put("Base:total:%s" % name, total)

        Base.__timing += diff
        return total


    def error(my, msg):
        sys.stderr.write(msg)
        sys.stderr.write("\n")
        sys.stderr.flush()

    def serror(msg):
        sys.stderr.write(msg)
        sys.stderr.write("\n")
        sys.stderr.flush()
    serror = staticmethod(serror)



