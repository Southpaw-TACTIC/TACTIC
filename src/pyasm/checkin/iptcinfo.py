#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 fileformat=unix:
# Author: 2004-2008 Gulácsi Tamás
#
# Ported from Josh Carter's Perl IPTCInfo.pm by Tamás Gulácsi
#
# IPTCInfo: extractor for IPTC metadata embedded in images
# Copyright (C) 2000-2004 Josh Carter <josh@multipart-mixed.com>
# Copyright (C) 2004-2008 Tamás Gulácsi <gthomas@gthomas.hu>
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the same terms as Python itself.
#
# VERSION = '1.9';
u"""
IPTCInfo - Python module for extracting and modifying IPTC image meta-data

Ported from Josh Carter's Perl IPTCInfo-1.9.pm by Tamás Gulácsi

Ever wish you add information to your photos like a caption, the place
you took it, the date, and perhaps even keywords and categories? You
already can. The International Press Telecommunications Council (IPTC)
defines a format for exchanging meta-information in news content, and
that includes photographs. You can embed all kinds of information in
your images. The trick is putting it to use.

That's where this IPTCInfo Python module comes into play. You can embed
information using many programs, including Adobe Photoshop, and
IPTCInfo will let your web server -- and other automated server
programs -- pull it back out. You can use the information directly in
Python programs, export it to XML, or even export SQL statements ready
to be fed into a database.


PREFACE

First, I want to apologize a little bit: as this module is originally
written in Perl by Josh Carter, it is quite non-Pythonic (for example
the addKeyword, clearSupplementalCategories functions - I think it
would be better having a derived list class with add, clear functions)
and tested only by me reading/writing IPTC metadata for family photos.
Any suggestions welcomed!

Thanks,
Tamás Gulácsi <gthomas at fw dot hu>

SYNOPSIS

    from iptcinfo import IPTCInfo
    import sys

    fn = (len(sys.argv) > 1 and [sys.argv[1]] or ['test.jpg'])[0]
    fn2 = (len(sys.argv) > 2 and [sys.argv[2]] or ['test_out.jpg'])[0]

    # Create new info object
    info = IPTCInfo(fn)

    # for file without IPTC data use
    info = IPTCInfo(fn, force=True)

    # Check if file had IPTC data
    if len(info.data) < 4: raise Exception(info.error)


    # Print list of keywords, supplemental categories, or contacts
    print info.keywords
    print info.supplementalCategories
    print info.contacts

    # Get specific attributes...
    caption = info.data['caption/abstract']

    # Create object for file that may or may not have IPTC data.
    info = IPTCInfo(fn)

    # Add/change an attribute
    info.data['caption/abstract'] = 'Witty caption here'
    info.data['supplemental category'] = ['portrait']

    # Save new info to file
    ##### See disclaimer in 'SAVING FILES' section #####
    info.save()
    info.saveAs(fn2)

    #re-read IPTC info
    print IPTCInfo(fn2)

DESCRIPTION

    USING IPTCINFO

    To integrate with your own code, simply do something like what's in
    the synopsys above.

    The complete list of possible attributes is given below. These are
    as specified in the IPTC IIM standard, version 4. Keywords and
    categories are handled slightly differently: since these are lists,
    the module allows you to access them as Python lists. Call
    keywords() and supplementalCategories() to get each list.

    IMAGES NOT HAVING IPTC METADATA

    If yout apply

        info = IPTCInfo('file-name-here.jpg')

    to an image not having IPTC metadata, len(info.data) will be 3
    ('supplemental categories', 'keywords', 'contacts') will be empty
    lists.

    MODIFYING IPTC DATA

    You can modify IPTC data in JPEG files and save the file back to
    disk. Here are the commands for doing so:

        # Set a given attribute
        info.data['iptc attribute here'] = 'new value here'

        # Clear the keywords or supp. categories list
        info.keywords = []
        info.supplementalCategories = []
        info.contacts = []

        # Add keywords or supp. categories
        info.keyword.append('frob')

        # You can also add a list reference
        info.keyword.extend(['frob', 'nob', 'widget'])
        info.keyword += ['gadget']

    SAVING FILES

    With JPEG files you can add/change attributes, add keywords, etc., and
    then call:

        info.save()
        info.saveAs('new-file-name.jpg')

    This will save the file with the updated IPTC info. Please only run
    this on *copies* of your images -- not your precious originals! --
    because I'm not liable for any corruption of your images. (If you
    read software license agreements, nobody else is liable,
    either. Make backups of your originals!)

    If you're into image wizardry, there are a couple handy options you
    can use on saving. One feature is to trash the Adobe block of data,
    which contains IPTC info, color settings, Photoshop print settings,
    and stuff like that. The other is to trash all application blocks,
    including stuff like EXIF and FlashPix data. This can be handy for
    reducing file sizes. The options are passed as a dict to save()
    and saveAs(), e.g.:

        info.save({'discardAdobeParts': 'on'})
        info.saveAs('new-file-name.jpg', {'discardAppParts': 'on'})

    Note that if there was IPTC info in the image, or you added some
    yourself, the new image will have an Adobe part with only the IPTC
    information.

    XML AND SQL EXPORT FEATURES

    IPTCInfo also allows you to easily generate XML and SQL from the image
    metadata. For XML, call:

        xml = info.exportXML('entity-name', extra-data,
                                                  'optional output file name')

    This returns XML containing all image metadata. Attribute names are
    translated into XML tags, making adjustments to spaces and slashes
    for compatibility. (Spaces become underbars, slashes become dashes.)
    You provide an entity name; all data will be contained within this
    entity.  You can optionally provides a reference to a hash of extra
    data. This will get put into the XML, too. (Example: you may want to
    put info on the image's location into the XML.) Keys must be valid
    XML tag names.  You can also provide a filename, and the XML will be
    dumped into there.

    For SQL, it goes like this:

        self mappings = {
                  'IPTC dataset name here': 'your table column name here',
                  'caption/abstract':       'caption',
                  'city':                   'city',
                  'province/state':         'state} # etc etc etc.

        statement = info.exportSQL('mytable', mappings, extra-data)

    This returns a SQL statement to insert into your given table name a
    set of values from the image. You pass in a reference to a hash
    which maps IPTC dataset names into column names for the database
    table. As with XML export, you can also provide extra information to
    be stuck into the SQL.

IPTC ATTRIBUTE REFERENCE

    object name               originating program
    edit status               program version
    editorial update          object cycle
    urgency                   by-line
    subject reference         by-line title
    category                  city
    fixture identifier        sub-location
    content location code     province/state
    content location name     country/primary location code
    release date              country/primary location name
    release time              original transmission reference
    expiration date           headline
    expiration time           credit
    special instructions      source
    action advised            copyright notice
    reference service         contact
    reference date            caption/abstract
    reference number          writer/editor
    date created              image type
    time created              image orientation
    digital creation date     language identifier
    digital creation time

    custom1 - custom20: NOT STANDARD but used by Fotostation.
    IPTCInfo also supports these fields.

KNOWN BUGS

IPTC meta-info on MacOS may be stored in the resource fork instead
of the data fork. This program will currently not scan the resource
fork.

I have heard that some programs will embed IPTC info at the end of the
file instead of the beginning. The module will currently only look
near the front of the file. If you have a file with IPTC data that
IPTCInfo can't find, please contact me! I would like to ensure
IPTCInfo works with everyone's files.

AUTHOR

Josh Carter, josh@multipart-mixed.com
"""

__version__ = '1.9.5-6'
__author__ = u'Gulácsi, Tamás'

SURELY_WRITE_CHARSET_INFO = False

from struct import pack, unpack
#~ from cStringIO import StringIO
import sys
import re
import os
import tempfile
import shutil

import logging
LOG = logging.getLogger('iptcinfo')
LOGDBG = logging.getLogger('iptcinfo.debug')


class String(basestring):
    def __iadd__(self, other):
        assert isinstance(other, str)
        super(type(self), self).__iadd__(other)


class EOFException(Exception):
    def __init__(self, *args):
        Exception.__init__(self)
        self._str = '\n'.join(args)

    def __str__(self):
        return self._str


def push(diction, key, value):
    if key in diction and hasattr(diction[key], 'append'):
        diction[key].append(value)
    else:
        diction[key] = value


def duck_typed(obj, prefs):
    if isinstance(prefs, basestring):
        prefs = [prefs]
    for pref in prefs:
        if not hasattr(obj, pref):
            return False
    return True

sys_enc = sys.getfilesystemencoding()

#  Debug off for production use
debugMode = 0

#####################################
# These names match the codes defined in ITPC's IIM record 2.
# This hash is for non-repeating data items; repeating ones
# are in %listdatasets below.
c_datasets = {
    # 0: 'record version',    # skip -- binary data
    5: 'object name',
    7: 'edit status',
    8: 'editorial update',
    10: 'urgency',
    12: 'subject reference',
    15: 'category',
    20: 'supplemental category',
    22: 'fixture identifier',
    25: 'keywords',
    26: 'content location code',
    27: 'content location name',
    30: 'release date',
    35: 'release time',
    37: 'expiration date',
    38: 'expiration time',
    40: 'special instructions',
    42: 'action advised',
    45: 'reference service',
    47: 'reference date',
    50: 'reference number',
    55: 'date created',
    60: 'time created',
    62: 'digital creation date',
    63: 'digital creation time',
    65: 'originating program',
    70: 'program version',
    75: 'object cycle',
    80: 'by-line',
    85: 'by-line title',
    90: 'city',
    92: 'sub-location',
    95: 'province/state',
    100: 'country/primary location code',
    101: 'country/primary location name',
    103: 'original transmission reference',
    105: 'headline',
    110: 'credit',
    115: 'source',
    116: 'copyright notice',
    118: 'contact',
    120: 'caption/abstract',
    121: 'local caption',
    122: 'writer/editor',
#  125: 'rasterized caption', # unsupported (binary data)
    130: 'image type',
    131: 'image orientation',
    135: 'language identifier',
    200: 'custom1',  # These are NOT STANDARD, but are used by
    201: 'custom2',  # Fotostation. Use at your own risk. They're
    202: 'custom3',  # here in case you need to store some special
    203: 'custom4',  # stuff, but note that other programs won't
    204: 'custom5',  # recognize them and may blow them away if
    205: 'custom6',  # you open and re-save the file. (Except with
    206: 'custom7',  # Fotostation, of course.)
    207: 'custom8',
    208: 'custom9',
    209: 'custom10',
    210: 'custom11',
    211: 'custom12',
    212: 'custom13',
    213: 'custom14',
    214: 'custom15',
    215: 'custom16',
    216: 'custom17',
    217: 'custom18',
    218: 'custom19',
    219: 'custom20',
}

c_datasets_r = dict([(v, k) for k, v in c_datasets.iteritems()])
del k, v


class IPTCData(dict):
    """Dict with int/string keys from c_listdatanames"""
    def __init__(self, diction={}, *args, **kwds):
        dict.__init__(self, *args, **kwds)
        self.update(dict((self.keyAsInt(k), v)
                         for k, v in diction.iteritems()))

    c_cust_pre = 'nonstandard_'

    @classmethod
    def keyAsInt(cls, key):
        #~ global c_datasets_r
        if isinstance(key, int):
            return key
        elif key in c_datasets_r:
            return c_datasets_r[key]
        elif (key.startswith(cls.c_cust_pre)
                    and key[len(cls.c_cust_pre):].isdigit()):
            return int(key[len(cls.c_cust_pre):])
        else:
            raise KeyError("Key %s is not in %s!" % (key, c_datasets_r.keys()))

    @classmethod
    def keyAsStr(cls, key):
        if isinstance(key, basestring) and key in c_datasets_r:
            return key
        elif key in c_datasets:
            return c_datasets[key]
        elif isinstance(key, int):
            return cls.c_cust_pre + str(key)
        else:
            raise KeyError("Key %s is not in %s!" % (key, c_datasets.keys()))

    def __getitem__(self, name):
        return dict.get(self, self.keyAsInt(name), None)

    def __setitem__(self, name, value):
        key = self.keyAsInt(name)
        if key in self and isinstance(dict.__getitem__(self, key),
                (tuple, list)):
            #print key, c_datasets[key], o.__getitem__(key)
            if isinstance(value, (tuple, list)):
                dict.__setitem__(self, key, value)
            else:
                raise ValueError("For %s only lists acceptable!" % name)
        else:
            dict.__setitem__(self, self.keyAsInt(name), value)


def _getSetSomeList(name):
    def getList(self):
        """Returns the list of %s.""" % name
        return self._data[name]

    def setList(self, value):
        """Sets the list of %s.""" % name
        if isinstance(value, (list, tuple)):
            self._data[name] = list(value)
        elif isinstance(value, basestring):
            self._data[name] = [value]
            print 'Warning: IPTCInfo.%s is a list!' % name
        else:
            raise ValueError('IPTCInfo.%s is a list!' % name)

    return (getList, setList)


class IPTCInfo(object):
    """info = IPTCInfo('image filename goes here')

    File can be a file-like object or a string. If it is a string, it is
    assumed to be a filename.

    Returns IPTCInfo object filled with metadata from the given image
    file. File on disk will be closed, and changes made to the IPTCInfo
    object will *not* be flushed back to disk.

    If force==True, than forces an object to always be returned. This
    allows you to start adding stuff to files that don't have IPTC info
    and then save it.

    If inp_charset is None, then no translation is done to unicode (except
    when charset is encoded in the image metadata). In this case you should
    be VERY careful to use bytestrings overall with the SAME ENCODING!
    """

    def __init__(self, fobj, force=False, inp_charset=None, out_charset=None,
                 *args, **kwds):
        # Open file and snarf data from it.
        self._error = None
        self._data = IPTCData({'supplemental category': [], 'keywords': [],
                               'contact': []})
        if duck_typed(fobj, 'read'):
            self._filename = None
            self._fh = fobj
        else:
            self._filename = fobj

        fh = self._getfh()
        self.inp_charset = inp_charset
        self.out_charset = out_charset or inp_charset

        datafound = self.scanToFirstIMMTag(fh)
        if datafound or force:
            # Do the real snarfing here
            if datafound:
                self.collectIIMInfo(fh)
        else:
            LOG.info("No IPTC data found.")
            self._closefh(fh)
            raise Exception("No IPTC data found.")
        self._closefh(fh)

    def _closefh(self, fh):
        if fh and self._filename is not None:
            fh.close()

    def _getfh(self, mode='r'):
        assert self._filename is not None or self._fh is not None
        if self._filename is not None:
            fh = file(self._filename, (mode + 'b').replace('bb', 'b'))
            if not fh:
                LOG.error("Can't open file (%r)", self._filename)
                return None
            else:
                return fh
        else:
            return self._fh

    #######################################################################
    # New, Save, Destroy, Error
    #######################################################################

    def get_error(self):
        """Returns the last error message"""
        return self._error

    def set_error(self, obj):
        '''Sets the last error message'''
        self._error = obj
    error = property(get_error, set_error)

    def save(self, options=None):
        """Saves Jpeg with IPTC data back to the same file it came from."""
        assert self._filename is not None
        return self.saveAs(self._filename, options)

    def _filepos(self, fh):
        fh.flush()
        #~ return 'POS=%d\n' % fh.tell()
        return fh.tell()

    def saveAs(self, newfile, options=None):
        """Saves Jpeg with IPTC data to a given file name."""
        # Open file and snarf data from it.
        fh = self._getfh()
        assert fh
        fh.seek(0, 0)
        if not self.fileIsJpeg(fh):
            LOG.error("Source file is not a Jpeg; I can only save Jpegs."
                " Sorry.")
            return None
        ret = self.jpegCollectFileParts(fh, options)
        self._closefh(fh)
        if ret is None:
            LOG.error("collectfileparts failed")
            raise Exception('collectfileparts failed')

        (start, end, adobe) = ret
        LOGDBG.debug('start: %d, end: %d, adobe:%d', *map(len, ret))
        self.hexDump(start), len(end)
        LOGDBG.debug('adobe1: %r', adobe)
        if options is not None and 'discardAdobeParts' in options:
            adobe = None
        LOGDBG.debug('adobe2: %r', adobe)

        LOGDBG.info('writing...')
        (tmpfd, tmpfn) = tempfile.mkstemp()
        os.close(tmpfd)
        #~ fh = os.fdopen(tmpfh, 'wb')
        tmpfh = open(tmpfn, 'wb')
        #fh = StringIO()
        if not tmpfh:
            LOG.error("Can't open output file %r", tmpfn)
            return None
        LOGDBG.debug('start=%d end=%d', len(start), len(end))
        tmpfh.write(start)
        # character set
        ch = self.c_charset_r.get(self.out_charset, None)
        # writing the character set is not the best practice
        # - couldn't find the needed place (record) for it yet!
        if SURELY_WRITE_CHARSET_INFO and ch is not None:
            tmpfh.write(pack("!BBBHH", 0x1c, 1, 90, 4, ch))

        LOGDBG.debug('pos: %d', self._filepos(tmpfh))
        data = self.photoshopIIMBlock(adobe, self.packedIIMData())
        LOGDBG.debug('data len=%d dmp=%r', len(data), self.hexDump(data))
        tmpfh.write(data)
        LOGDBG.debug('pos: %d', self._filepos(tmpfh))
        tmpfh.write(end)
        LOGDBG.debug('pos: %d', self._filepos(tmpfh))
        tmpfh.flush()
        tmpfh.close()

        #print tmpfh, tmpfn, newfile
        #copy the successfully written file back to the given file
        if hasattr(tmpfh, 'getvalue'):  # StringIO
            fh2 = open(newfile, 'wb')
            fh2.truncate()
            fh2.seek(0, 0)
            tmpfh = open(tmpfn, 'rb')
            #~ fh.seek(0, 0)
            while 1:
                buf = tmpfh.read(8192)
                if not buf:
                    break
                fh2.write(buf)
            fh2.flush()
            fh2.close()
            tmpfh.close()
            os.unlink(tmpfn)
        else:
            if os.path.exists(newfile):
                shutil.move(newfile, newfile + '~')
            shutil.move(tmpfn, newfile)
        return True

    def __del__(self):
        """Called when object is destroyed.
        No action necessary in this case."""
        pass

    #######################################################################
    # Attributes for clients
    #######################################################################

    def getData(self):
        return self._data

    def setData(self, _):
        raise Exception('You cannot overwrite the data, only its elements!')
    data = property(getData, setData)

    keywords = property(*_getSetSomeList('keywords'))
    supplementalCategories = property(
        *_getSetSomeList('supplemental category'))
    contacts = property(*_getSetSomeList('contact'))

    def __str__(self):
        return ('charset: %s\n%s' % (self.inp_charset,
                str(dict((self._data.keyAsStr(k), v)
                         for k, v in self._data.iteritems()))))

    def readExactly(self, fh, length):
        """readExactly

        Reads exactly length bytes and throws an exception if EOF is hitten
        before.
        """
        ## assert isinstance(fh, file)
        assert duck_typed(fh, 'read')  # duck typing
        buf = fh.read(length)
        if buf is None or len(buf) < length:
            raise EOFException('readExactly: %s' % str(fh))
        return buf

    def seekExactly(self, fh, length):
        """seekExactly

        Seeks length bytes from the current position and checks the result
        """
        ## assert isinstance(fh, file)
        assert duck_typed(fh, ['seek', 'tell'])  # duck typing
        pos = fh.tell()
        fh.seek(length, 1)
        if fh.tell() - pos != length:
            raise EOFException()

    #######################################################################
    # XML, SQL export
    #######################################################################

    def exportXML(self, basetag, extra, filename):
        """xml = info.exportXML('entity-name', extra-data,
                                'optional output file name')

        Exports XML containing all image metadata. Attribute names are
        translated into XML tags, making adjustments to spaces and slashes
        for compatibility. (Spaces become underbars, slashes become
        dashes.)  Caller provides an entity name; all data will be
        contained within this entity. Caller optionally provides a
        reference to a hash of extra data. This will be output into the
        XML, too. Keys must be valid XML tag names. Optionally provide a
        filename, and the XML will be dumped into there."""

        def P(s):
            #global off
            return '  ' * off + s + '\n'
        off = 0

        if len(basetag) == 0:
            basetag = 'photo'
        out = [P("<%s>" % basetag)]

        off += 1
        # dump extra info first, if any
        for k, v in (isinstance(extra, dict)
                and [extra] or [{}])[0].iteritems():
            out.append(P("<%s>%s</%s>" % (k, v, k)))

        # dump our stuff
        for k, v in self._data.iteritems():
            if not isinstance(v, list):
                key = re.sub('/', '-',
                    re.sub(' +', ' ', self._data.keyAsStr(k)))
                out.append(P("<%s>%s</%s>" % (key, v, key)))

        # print keywords
        kw = self.keywords()
        if kw and len(kw) > 0:
            out.append(P("<keywords>"))
            off += 1
            for k in kw:
                out.append(P("<keyword>%s</keyword>" % k))
            off -= 1
            out.append(P("</keywords>"))

        # print supplemental categories
        sc = self.supplementalCategories()
        if sc and len(sc) > 0:
            out.append(P("<supplemental_categories>"))
            off += 1
            for k in sc:
                out.append(
                P("<supplemental_category>%s</supplemental_category>" % k))
            off -= 1
            out.append(P("</supplemental_categories>"))

        # print contacts
        kw = self.contacts()
        if kw and len(kw) > 0:
            out.append(P("<contacts>"))
            off += 1
            for k in kw:
                out.append(P("<contact>%s</contact>" % k))
            off -= 1
            out.append(P("</contacts>"))

        # close base tag
        off -= 1
        out.append(P("</%s>" % basetag))

        # export to file if caller asked for it.
        if len(filename) > 0:
            xmlout = file(filename, 'wb')
            xmlout.write(out)
            xmlout.close()

        return ''.join(out)

    def exportSQL(self, tablename, mappings, extra):
        """statement = info.exportSQL('mytable', mappings, extra-data)

        mappings = {
            'IPTC dataset name here': 'your table column name here',
            'caption/abstract': 'caption',
            'city': 'city',
            'province/state': 'state} # etc etc etc.

        Returns a SQL statement to insert into your given table name a set
        of values from the image. Caller passes in a reference to a hash
        which maps IPTC dataset names into column names for the database
        table. Optionally pass in a ref to a hash of extra data which will
        also be included in the insert statement. Keys in that hash must
        be valid column names."""

        if (tablename is None or mappings is None):
            return None
        statement = columns = values = None

        E = lambda s: "'%s'" % re.sub("'", "''", s)  # escape single quotes

        # start with extra data, if any
        columns = ', '.join(extra.keys() + mappings.keys())
        values = ', '.join(map(E, extra.values()
            + [self.data[k] for k in mappings.keys()]))
        # process our data

        statement = "INSERT INTO %s (%s) VALUES (%s)" \
                                % (tablename, columns, values)

        return statement

    #######################################################################
    # File parsing functions (private)
    #######################################################################

    def scanToFirstIMMTag(self, fh):  # OK
        """Scans to first IIM Record 2 tag in the file. The will either
        use smart scanning for Jpegs or blind scanning for other file
        types."""
        ## assert isinstance(fh, file)
        if self.fileIsJpeg(fh):
            LOG.info("File is Jpeg, proceeding with JpegScan")
            return self.jpegScan(fh)
        else:
            LOG.warn("File not a JPEG, trying blindScan")
            return self.blindScan(fh)

    def fileIsJpeg(self, fh):  # OK
        """Checks to see if this file is a Jpeg/JFIF or not. Will reset
        the file position back to 0 after it's done in either case."""

        # reset to beginning just in case
        ## assert isinstance(fh, file)
        assert duck_typed(fh, ['read', 'seek'])
        fh.seek(0, 0)
        if debugMode > 0:
            LOG.info("Opening 16 bytes of file: %r",
                self.hexDump(fh.read(16)))
            fh.seek(0, 0)
        # check start of file marker
        ered = False
        try:
            (ff, soi) = fh.read(2)
            if not (ord(ff) == 0xff and ord(soi) == 0xd8):
                ered = False
            else:
                # now check for APP0 marker. I'll assume that anything with a
                # SOI followed by APP0 is "close enough" for our purposes.
                # (We're not dinking with image data, so anything following
                # the Jpeg tagging system should work.)
                (ff, app0) = fh.read(2)
                if not (ord(ff) == 0xff):
                    ered = False
                else:
                    ered = True
        finally:
            # reset to beginning of file
            fh.seek(0, 0)
            return ered

    c_marker_err = {0: "Marker scan failed",
                    0xd9:  "Marker scan hit end of image marker",
                    0xda: "Marker scan hit start of image data"}

    def jpegScan(self, fh):  # OK
        """Assuming the file is a Jpeg (see above), this will scan through
        the markers looking for the APP13 marker, where IPTC/IIM data
        should be found. While this isn't a formally defined standard, all
        programs have (supposedly) adopted Adobe's technique of putting
        the data in APP13."""
        # Skip past start of file marker
        ## assert isinstance(fh, file)
        try:
            (ff, soi) = self.readExactly(fh, 2)
        except EOFException:
            return None

        if not (ord(ff) == 0xff and ord(soi) == 0xd8):
            self.error = "JpegScan: invalid start of file"
            LOG.error(self.error)
            return None
        # Scan for the APP13 marker which will contain our IPTC info (I hope).
        while 1:
            err = None
            marker = self.jpegNextMarker(fh)
            if ord(marker) == 0xed:
                break  # 237

            err = self.c_marker_err.get(ord(marker), None)
            if err is None and self.jpegSkipVariable(fh) == 0:
                err = "JpegSkipVariable failed"
            if err is not None:
                self.error = err
                LOG.error(err)
                return None

        # If were's here, we must have found the right marker. Now
        # blindScan through the data.
        return self.blindScan(fh, MAX=self.jpegGetVariableLength(fh))

    def jpegNextMarker(self, fh):  # OK
        """Scans to the start of the next valid-looking marker. Return
        value is the marker id."""

        ## assert isinstance(fh, file)
        # Find 0xff byte. We should already be on it.
        try:
            byte = self.readExactly(fh, 1)
        except EOFException:
            return None

        while ord(byte) != 0xff:
            LOG.warn("JpegNextMarker: warning: bogus stuff in Jpeg file")
            try:
                byte = self.readExactly(fh, 1)
            except EOFException:
                return None
        # Now skip any extra 0xffs, which are valid padding.
        while 1:
            try:
                byte = self.readExactly(fh, 1)
            except EOFException:
                return None
            if ord(byte) != 0xff:
                break

        # byte should now contain the marker id.
        LOG.debug("JpegNextMarker: at marker %02X (%d)", ord(byte), ord(byte))
        return byte

    def jpegGetVariableLength(self, fh):  # OK
        """Gets length of current variable-length section. File position
        at start must be on the marker itself, e.g. immediately after call
        to JPEGNextMarker. File position is updated to just past the
        length field."""
        ## assert isinstance(fh, file)
        try:
            length = unpack('!H', self.readExactly(fh, 2))[0]
        except EOFException:
            return 0
        LOG.debug('JPEG variable length: %d', length)

        # Length includes itself, so must be at least 2
        if length < 2:
            LOG.warn("JPEGGetVariableLength: erroneous JPEG marker length")
            return 0
        return length - 2

    def jpegSkipVariable(self, fh, rSave=None):  # OK
        """Skips variable-length section of Jpeg block. Should always be
        called between calls to JpegNextMarker to ensure JpegNextMarker is
        at the start of data it can properly parse."""

        ## assert isinstance(fh, file)
        # Get the marker parameter length count
        length = self.jpegGetVariableLength(fh)
        if length == 0:
            return None

        # Skip remaining bytes
        if rSave is not None or debugMode > 0:
            try:
                temp = self.readExactly(fh, length)
            except EOFException:
                LOG.error("JpegSkipVariable: read failed while skipping"
                    " var data")
                return None
        # prints out a heck of a lot of stuff
        # self.hexDump(temp)
        else:
            # Just seek
            try:
                self.seekExactly(fh, length)
            except EOFException:
                LOG.error("JpegSkipVariable: read failed while skipping"
                    " var data")
                return None

        return (rSave is not None and [temp] or [True])[0]

    c_charset = {100: 'iso8859_1', 101: 'iso8859_2', 109: 'iso8859_3',
                  110: 'iso8859_4', 111: 'iso8859_5', 125: 'iso8859_7',
                  127: 'iso8859_6', 138: 'iso8859_8',
                  196: 'utf_8'}
    c_charset_r = dict([(v, k) for k, v in c_charset.iteritems()])

    def blindScan(self, fh, MAX=8192):  # OK
        """Scans blindly to first IIM Record 2 tag in the file. This
        method may or may not work on any arbitrary file type, but it
        doesn't hurt to check. We expect to see this tag within the first
        8k of data. (This limit may need to be changed or eliminated
        depending on how other programs choose to store IIM.)"""

        ## assert isinstance(fh, file)
        assert duck_typed(fh, 'read')
        offset = 0
        # keep within first 8192 bytes
        # NOTE: this may need to change
        LOG.debug('blindScan: starting scan, max length %d', MAX)

        # start digging
        while offset <= MAX:
            try:
                temp = self.readExactly(fh, 1)
            except EOFException:
                LOG.error("BlindScan: hit EOF while scanning")
                return None
            # look for tag identifier 0x1c
            if ord(temp) == 0x1c:
                # if we found that, look for record 2, dataset 0
                # (record version number)
                (record, dataset) = fh.read(2)
                if ord(record) == 1 and ord(dataset) == 90:
                    # found character set's record!
                    try:
                        temp = self.readExactly(fh,
                            self.jpegGetVariableLength(fh))
                        try:
                            cs = unpack('!H', temp)[0]
                        except:
                            print (
                                'WARNING: problems with charset recognition',
                                repr(temp))
                            cs = None
                        if cs in self.c_charset:
                            self.inp_charset = self.c_charset[cs]
                        LOG.info("BlindScan: found character set '%s'"
                            " at offset %d", self.inp_charset, offset)
                    except EOFException:
                        pass

                elif ord(record) == 2:
                    # found it. seek to start of this tag and return.
                    LOG.debug("BlindScan: found IIM start at offset %d",
                        offset)
                    try:  # seek rel to current position
                        self.seekExactly(fh, -3)
                    except EOFException:
                        return None
                    return offset
                else:
                    # didn't find it. back up 2 to make up for
                    # those reads above.
                    try:  # seek rel to current position
                        self.seekExactly(fh, -2)
                    except EOFException:
                        return None

            # no tag, keep scanning
            offset += 1

        return False

    def collectIIMInfo(self, fh):  # OK
        """Assuming file is seeked to start of IIM data (using above),
        this reads all the data into our object's hashes"""
        # NOTE: file should already be at the start of the first
        # IPTC code: record 2, dataset 0.
        ## assert isinstance(fh, file)
        assert duck_typed(fh, 'read')
        while 1:
            try:
                header = self.readExactly(fh, 5)
            except EOFException:
                return None

            (tag, record, dataset, length) = unpack("!BBBH", header)
            # bail if we're past end of IIM record 2 data
            if not (tag == 0x1c and record == 2):
                return None

            alist = {'tag': tag, 'record': record, 'dataset': dataset,
                     'length': length}
            LOG.debug('\n'.join('%s\t: %s' % (k, v)
                for k, v in alist.iteritems()))
            value = fh.read(length)

            if self.inp_charset:
                try:
                    value = unicode(value, encoding=self.inp_charset,
                        errors='strict')
                except:
                    LOG.error('Data "%r" is not in encoding %s!',
                        value, self.inp_charset)
                    value = unicode(value, encoding=self.inp_charset,
                        errors='replace')

            # try to extract first into _listdata (keywords, categories)
            # and, if unsuccessful, into _data. Tags which are not in the
            # current IIM spec (version 4) are currently discarded.
            if (dataset in self._data
                    and hasattr(self._data[dataset], 'append')):
                self._data[dataset].append(value)
            elif dataset != 0:
                self._data[dataset] = value

    #######################################################################
    # File Saving
    #######################################################################

    def jpegCollectFileParts(self, fh, discardAppParts=False):
        """Collects all pieces of the file except for the IPTC info that
        we'll replace when saving. Returns the stuff before the info,
        stuff after, and the contents of the Adobe Resource Block that the
        IPTC data goes in. Returns None if a file parsing error occured."""

        ## assert isinstance(fh, file)
        assert duck_typed(fh, ['seek', 'read'])
        adobeParts = ''
        start = []

        # Start at beginning of file
        fh.seek(0, 0)
        # Skip past start of file marker
        (ff, soi) = fh.read(2)
        if not (ord(ff) == 0xff and ord(soi) == 0xd8):
            self.error = "JpegScan: invalid start of file"
            LOG.error(self.error)
            return None

        # Begin building start of file
        start.append(pack("BB", 0xff, 0xd8))

        # Get first marker in file. This will be APP0 for JFIF or APP1 for
        # EXIF.
        marker = self.jpegNextMarker(fh)
        app0data = ''
        app0data = self.jpegSkipVariable(fh, app0data)
        if app0data is None:
            self.error = 'jpegSkipVariable failed'
            LOG.error(self.error)
            return None

        if ord(marker) == 0xe0 or not discardAppParts:
            # Always include APP0 marker at start if it's present.
            start.append(pack('BB', 0xff, ord(marker)))
            # Remember that the length must include itself (2 bytes)
            start.append(pack('!H', len(app0data) + 2))
            start.append(app0data)
        else:
            # Manually insert APP0 if we're trashing application parts, since
            # all JFIF format images should start with the version block.
            LOGDBG.debug('discardAppParts=%r', discardAppParts)
            start.append(pack("BB", 0xff, 0xe0))
            start.append(pack("!H", 16))    # length (including these 2 bytes)
            start.append("JFIF")            # format
            start.append(pack("BB", 1, 2))  # call it version 1.2 (current
                                            # JFIF)
            start.append(pack('8B', 0))     # zero everything else

        # Now scan through all markers in file until we hit image data or
        # IPTC stuff.
        end = []
        while 1:
            marker = self.jpegNextMarker(fh)
            if marker is None or ord(marker) == 0:
                self.error = "Marker scan failed"
                LOG.error(self.error)
                return None
            # Check for end of image
            elif ord(marker) == 0xd9:
                LOG.debug("JpegCollectFileParts: saw end of image marker")
                end.append(pack("BB", 0xff, ord(marker)))
                break
            # Check for start of compressed data
            elif ord(marker) == 0xda:
                LOG.debug("JpegCollectFileParts: saw start of compressed data")
                end.append(pack("BB", 0xff, ord(marker)))
                break
            partdata = ''
            partdata = self.jpegSkipVariable(fh, partdata)
            if not partdata:
                self.error = "JpegSkipVariable failed"
                LOG.error(self.error)
                return None
            partdata = str(partdata)

            # Take all parts aside from APP13, which we'll replace
            # ourselves.
            if (discardAppParts and ord(marker) >= 0xe0
                    and ord(marker) <= 0xef):
                # Skip all application markers, including Adobe parts
                adobeParts = ''
            elif ord(marker) == 0xed:
                # Collect the adobe stuff from part 13
                adobeParts = self.collectAdobeParts(partdata)
                break
            else:
                # Append all other parts to start section
                start.append(pack("BB", 0xff, ord(marker)))
                start.append(pack("!H", len(partdata) + 2))
                start.append(partdata)

        # Append rest of file to end
        while 1:
            buff = fh.read(8192)
            if buff is None or len(buff) == 0:
                break
            end.append(buff)

        return (''.join(start), ''.join(end), adobeParts)

    def collectAdobeParts(self, data):
        """Part APP13 contains yet another markup format, one defined by
        Adobe.  See"File Formats Specification" in the Photoshop SDK
        (avail from www.adobe.com). We must take
        everything but the IPTC data so that way we can write the file back
        without losing everything else Photoshop stuffed into the APP13
        block."""
        assert isinstance(data, basestring)
        length = len(data)
        offset = 0
        out = []
        # Skip preamble
        offset = len('Photoshop 3.0 ')
        # Process everything
        while offset < length:
            # Get OSType and ID
            (ostype, id1, id2) = unpack("!LBB", data[offset:offset + 6])
            offset += 6
            if offset >= length:
                break

            # Get pascal string
            stringlen = unpack("B", data[offset:offset + 1])[0]
            offset += 1
            if offset >= length:
                break
            string = data[offset:offset + stringlen]
            offset += stringlen

            # round up if odd
            if (stringlen % 2 != 0):
                offset += 1
            # there should be a null if string len is 0
            if stringlen == 0:
                offset += 1
            if offset >= length:
                break

            # Get variable-size data
            size = unpack("!L", data[offset:offset + 4])[0]
            offset += 4
            if offset >= length:
                break

            var = data[offset:offset + size]
            offset += size
            if size % 2 != 0:
                offset += 1  # round up if odd

            # skip IIM data (0x0404), but write everything else out
            if not (id1 == 4 and id2 == 4):
                out.append(pack("!LBB", ostype, id1, id2))
                out.append(pack("B", stringlen))
                out.append(string)
                if stringlen == 0 or stringlen % 2 != 0:
                    out.append(pack("B", 0))
                out.append(pack("!L", size))
                out.append(var)
                out = [''.join(out)]
                if size % 2 != 0 and len(out[0]) % 2 != 0:
                    out.append(pack("B", 0))

        return ''.join(out)

    def _enc(self, text):
        """Recodes the given text from the old character set to utf-8"""
        res = text
        out_charset = self.out_charset or self.inp_charset
        if isinstance(text, unicode):
            res = text.encode(out_charset or 'utf8')
        elif isinstance(text, str) and out_charset:
            try:
                res = unicode(text, encoding=self.inp_charset).encode(
                    out_charset)
            except (UnicodeEncodeError, UnicodeDecodeError):
                LOG.error("_enc: charset %s is not working for %s",
                    self.inp_charset, text)
                res = unicode(text, encoding=self.inp_charset,
                    errors='replace').encode(out_charset)
        elif isinstance(text, (list, tuple)):
            res = type(text)(map(self._enc, text))
        return res

    def packedIIMData(self):
        """Assembles and returns our _data and _listdata into IIM format for
        embedding into an image."""
        out = []
        (tag, record) = (0x1c, 0x02)
        # Print record version
        # tag - record - dataset - len (short) - 4 (short)
        out.append(pack("!BBBHH", tag, record, 0, 2, 4))

        LOGDBG.debug('out=%r', self.hexDump(out))
        # Iterate over data sets
        for dataset, value in self._data.iteritems():
            if len(value) == 0:
                continue
            if not dataset in (c_datasets or isinstance(dataset, int)):
                LOG.error("PackedIIMData: illegal dataname '%s' (%d)",
                    c_datasets[dataset], dataset)
                continue
            LOG.debug('packedIIMData %r -> %r', value, self._enc(value))
            value = self._enc(value)
            if not isinstance(value, list):
                value = str(value)
                out.append(pack("!BBBH", tag, record, dataset, len(value)))
                out.append(value)
            else:
                for v in map(str, value):
                    if v is None or len(v) == 0:
                        continue
                    out.append(pack("!BBBH", tag, record, dataset, len(v)))
                    out.append(v)

        return ''.join(out)

    def photoshopIIMBlock(self, otherparts, data):
        """Assembles the blob of Photoshop "resource data" that includes our
        fresh IIM data (from PackedIIMData) and the other Adobe parts we
        found in the file, if there were any."""
        out = []
        assert isinstance(data, basestring)
        resourceBlock = ["Photoshop 3.0"]
        resourceBlock.append(pack("B", 0))
        # Photoshop identifier
        resourceBlock.append("8BIM")
        # 0x0404 is IIM data, 00 is required empty string
        resourceBlock.append(pack("BBBB", 0x04, 0x04, 0, 0))
        # length of data as 32-bit, network-byte order
        resourceBlock.append(pack("!L", len(data)))
        # Now tack data on there
        resourceBlock.append(data)
        # Pad with a blank if not even size
        if len(data) % 2 != 0:
            resourceBlock.append(pack("B", 0))
        # Finally tack on other data
        if otherparts is not None:
            resourceBlock.append(otherparts)
        resourceBlock = ''.join(resourceBlock)

        out.append(pack("BB", 0xff, 0xed))  # Jpeg start of block, APP13
        out.append(pack("!H", len(resourceBlock) + 2))  # length
        out.append(resourceBlock)

        return ''.join(out)

    #######################################################################
    # Helpers, docs
    #######################################################################

    @staticmethod
    def hexDump(dump):
        """Very helpful when debugging."""
        length = len(dump)
        P = lambda z: ((ord(z) >= 0x21 and ord(z) <= 0x7e) and [z] or ['.'])[0]
        ROWLEN = 18
        res = ['\n']
        for j in xrange(length // ROWLEN + int(length % ROWLEN > 0)):
            row = dump[j * ROWLEN:(j + 1) * ROWLEN]
            if isinstance(row, list):
                row = ''.join(row)
            res.append(
            ('%02X ' * len(row) + '   ' * (ROWLEN - len(row)) + '| %s\n') % \
                tuple(map(ord, list(row)) + [''.join(map(P, row))]))
        return ''.join(res)

    def jpegDebugScan(self, filename):
        """Also very helpful when debugging."""
        assert isinstance(filename, basestring) and os.path.isfile(filename)
        fh = file(filename, 'wb')
        if not fh:
            raise Exception("Can't open %s" % filename)

        # Skip past start of file marker
        (ff, soi) = fh.read(2)
        if not (ord(ff) == 0xff and ord(soi) == 0xd8):
            LOG.error("JpegScan: invalid start of file")
        else:
            # scan to 0xDA (start of scan), dumping the markers we see between
            # here and there.
            while 1:
                marker = self.jpegNextMarker(fh)
                if ord(marker) == 0xda:
                    break

                if ord(marker) == 0:
                    LOG.error("Marker scan failed")
                    break
                elif ord(marker) == 0xd9:
                    LOG.debug("Marker scan hit end of image marker")
                    break

                if not self.jpegSkipVariable(fh):
                    LOG.error("JpegSkipVariable failed")
                    return None

        self._closefh(fh)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        info = IPTCInfo(sys.argv[1])
        print info
