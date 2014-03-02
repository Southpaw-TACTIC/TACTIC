############################################################
#
#    Copyright (c) 2014, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#


__all__ = ['WatchFolder']

#import logging
#logging.basicConfig(filename='myapp.log', level=logging.INFO)

import time
import os

try:
    from watchdog.observers import Observer
    from watchdog.events import LoggingEventHandler
except ImportError:
    
    class LogginEventHandler(object):
        pass 


class WatchFolder(LoggingEventHandler):
    """Logs all the events captured."""

    def on_moved(self, event):
        super(LoggingEventHandler, self).on_moved(event)

        what = 'directory' if event.is_directory else 'file'
        print "Moved %s: from %s to %s" % (what, event.src_path, event.dest_path)

    def on_created(self, event):
        super(LoggingEventHandler, self).on_created(event)

        what = 'directory' if event.is_directory else 'file'
        print "Created %s: %s" % (what, event.src_path)

    def on_deleted(self, event):
        super(LoggingEventHandler, self).on_deleted(event)

        what = 'directory' if event.is_directory else 'file'
        print "Deleted %s: %s" % (what, event.src_path)

    def on_modified(self, event):
        super(LoggingEventHandler, self).on_modified(event)

        what = 'directory' if event.is_directory else 'file'
        print "Modified %s: %s" % (what, event.src_path)


    def watch(self, path):

        if not os.path.isdir(path):
            raise Exception("Path [%s] is not a directory" % path);

        event_handler = self
        observer = Observer()

        observer.schedule(event_handler, path=path, recursive=False)
        observer.start()


