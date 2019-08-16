##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os, re, sys, unittest, doctest
import zc.lockfile, time, threading
from zope.testing import renormalizing, setupstack

checker = renormalizing.RENormalizing([
    # Python 3 adds module path to error class name.
    (re.compile("zc\.lockfile\.LockError:"),
     r"LockError:"),
    ])

def inc():
    while 1:
        try:
            lock = zc.lockfile.LockFile('f.lock')
        except zc.lockfile.LockError:
            continue
        else:
            break
    f = open('f', 'r+b')
    v = int(f.readline().strip())
    time.sleep(0.01)
    v += 1
    f.seek(0)
    f.write(('%d\n' % v).encode('ASCII'))
    f.close()
    lock.close()

def many_threads_read_and_write():
    r"""
    >>> with open('f', 'w+b') as file:
    ...     _ = file.write(b'0\n')
    >>> with open('f.lock', 'w+b') as file:
    ...     _ = file.write(b'0\n')

    >>> n = 50
    >>> threads = [threading.Thread(target=inc) for i in range(n)]
    >>> _ = [thread.start() for thread in threads]
    >>> _ = [thread.join() for thread in threads]
    >>> with open('f', 'rb') as file:
    ...     saved = int(file.read().strip())
    >>> saved == n
    True

    >>> os.remove('f')

    We should only have one pid in the lock file:

    >>> f = open('f.lock')
    >>> len(f.read().strip().split())
    1
    >>> f.close()

    >>> os.remove('f.lock')

    """

def pid_in_lockfile():
    r"""
    >>> import os, zc.lockfile
    >>> pid = os.getpid()
    >>> lock = zc.lockfile.LockFile("f.lock")
    >>> f = open("f.lock")
    >>> _ = f.seek(1)
    >>> f.read().strip() == str(pid)
    True
    >>> f.close()

    Make sure that locking twice does not overwrite the old pid:

    >>> lock = zc.lockfile.LockFile("f.lock")
    Traceback (most recent call last):
      ...
    LockError: Couldn't lock 'f.lock'

    >>> f = open("f.lock")
    >>> _ = f.seek(1)
    >>> f.read().strip() == str(pid)
    True
    >>> f.close()

    >>> lock.close()
    """

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'README.txt', checker=checker,
        setUp=setupstack.setUpDirectory, tearDown=setupstack.tearDown))
    suite.addTest(doctest.DocTestSuite(
        setUp=setupstack.setUpDirectory, tearDown=setupstack.tearDown,
        checker=checker))
    return suite
