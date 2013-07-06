# -*- coding: iso-8859-1 -*-
"""active_directory - a lightweight wrapper around COM support
 for Microsoft's Active Directory

Active Directory is Microsoft's answer to LDAP, the industry-standard
 directory service holding information about users, computers and
 other resources in a tree structure, arranged by departments or
 geographical location, and optimized for searching.

There are several ways of attaching to Active Directory. This
 module uses the Dispatchable GC:// objects and wraps them
 lightly in helpful Python classes which do a bit of the
 otherwise tedious plumbing. The module is quite naive, and
 has only really been developed to aid searching, but since
 you can always access the original COM object, there's nothing
 to stop you using it for any AD operations.

+ The active directory object (AD_object) will determine its
   properties and allow you to access them as instance properties.

   eg
     import active_directory
     goldent = active_directory.find_user ("goldent")
     print ad.displayName

+ Any object returned by the AD object's operations is themselves
   wrapped as AD objects so you get the same benefits.

  eg
    import active_directory
    users = active_directory.root ().child ("cn=users")
    for user in users.search ("displayName='Tim*'"):
      print user.displayName

+ To search the AD, there are two module-level general
   search functions, two module-level functions to
   find a user and computer specifically and the search
   method on each AD_object. Usage is illustrated below:

   import active_directory as ad

   for user in ad.search (
     "objectClass='User'",
     "displayName='Tim Golden' OR sAMAccountName='goldent'"
   ):
     #
     # This search returns an AD_object
     #
     print user

   query = \"""
     SELECT Name, displayName
     FROM 'GC://cn=users,DC=gb,DC=vo,DC=local'
     WHERE displayName = 'John*'
   \"""
   for user in ad.search_ex (query):
     #
     # This search returns an ADO_object, which
     #  is faster but doesn't give the convenience
     #  of the AD methods etc.
     #
     print user

   print ad.find_user ("goldent")

   print ad.find_computer ("vogbp200")

   users = ad.root ().child ("cn=users")
   for u in users.search ("displayName='Tim*'"):
     print u

+ Typical usage will be:

import active_directory

for computer in active_directory.search ("objectClass='computer'"):
  print computer.displayName

(c) Tim Golden <active-directory@timgolden.me.uk> October 2004
Licensed under the (GPL-compatible) MIT License:
http://www.opensource.org/licenses/mit-license.php

Many thanks, obviously to Mark Hammond for creating
 the pywin32 extensions.
"""
from __future__ import generators

__VERSION__ = "0.6.7"

import os, sys
import datetime
import win32api
import socket

from win32com.client import Dispatch, GetObject
import win32security

#
# Code contributed by Stian Søiland <stian@soiland.no>
#
def i32(x):
  """Converts a long (for instance 0x80005000L) to a signed 32-bit-int.

  Python2.4 will convert numbers >= 0x80005000 to large numbers
  instead of negative ints.    This is not what we want for
  typical win32 constants.

  Usage:
      >>> i32(0x80005000L)
      -2147363168
  """
  # x > 0x80000000L should be negative, such that:
  # i32(0x80000000L) -> -2147483648L
  # i32(0x80000001L) -> -2147483647L     etc.
  return (x&0x80000000L and -2*0x40000000 or 0) + int(x&0x7fffffff)

class Enum (object):

  def __init__ (self, **kwargs):
    self._name_map = {}
    self._number_map = {}
    for k, v in kwargs.items ():
      self._name_map[k] = i32 (v)
      self._number_map[i32 (v)] = k

  def __getitem__ (self, item):
    try:
      return self._name_map[item]
    except KeyError:
      return self._number_map[i32 (item)]

  def item_names (self):
    return self._name_map.items ()

  def item_numbers (self):
    return self._number_map.items ()

GROUP_TYPES = Enum (
  GLOBAL_GROUP = 0x00000002,
  DOMAIN_LOCAL_GROUP = 0x00000004,
  LOCAL_GROUP = 0x00000004,
  UNIVERSAL_GROUP = 0x00000008,
  SECURITY_ENABLED = 0x80000000
)

AUTHENTICATION_TYPES = Enum (
  SECURE_AUTHENTICATION = i32 (0x01),
  USE_ENCRYPTION = i32 (0x02),
  USE_SSL = i32 (0x02),
  READONLY_SERVER = i32 (0x04),
  PROMPT_CREDENTIALS = i32 (0x08),
  NO_AUTHENTICATION = i32 (0x10),
  FAST_BIND = i32 (0x20),
  USE_SIGNING = i32 (0x40),
  USE_SEALING = i32 (0x80),
  USE_DELEGATION = i32 (0x100),
  SERVER_BIND = i32 (0x200),
  AUTH_RESERVED = i32 (0x800000000)
)

SAM_ACCOUNT_TYPES = Enum (
  SAM_DOMAIN_OBJECT = 0x0 ,
  SAM_GROUP_OBJECT = 0x10000000 ,
  SAM_NON_SECURITY_GROUP_OBJECT = 0x10000001 ,
  SAM_ALIAS_OBJECT = 0x20000000 ,
  SAM_NON_SECURITY_ALIAS_OBJECT = 0x20000001 ,
  SAM_USER_OBJECT = 0x30000000 ,
  SAM_NORMAL_USER_ACCOUNT = 0x30000000 ,
  SAM_MACHINE_ACCOUNT = 0x30000001 ,
  SAM_TRUST_ACCOUNT = 0x30000002 ,
  SAM_APP_BASIC_GROUP = 0x40000000,
  SAM_APP_QUERY_GROUP = 0x40000001 ,
  SAM_ACCOUNT_TYPE_MAX = 0x7fffffff
)

USER_ACCOUNT_CONTROL = Enum (
  ADS_UF_SCRIPT = 0x00000001,
  ADS_UF_ACCOUNTDISABLE = 0x00000002,
  ADS_UF_HOMEDIR_REQUIRED = 0x00000008,
  ADS_UF_LOCKOUT = 0x00000010,
  ADS_UF_PASSWD_NOTREQD = 0x00000020,
  ADS_UF_PASSWD_CANT_CHANGE = 0x00000040,
  ADS_UF_ENCRYPTED_TEXT_PASSWORD_ALLOWED = 0x00000080,
  ADS_UF_TEMP_DUPLICATE_ACCOUNT = 0x00000100,
  ADS_UF_NORMAL_ACCOUNT = 0x00000200,
  ADS_UF_INTERDOMAIN_TRUST_ACCOUNT = 0x00000800,
  ADS_UF_WORKSTATION_TRUST_ACCOUNT = 0x00001000,
  ADS_UF_SERVER_TRUST_ACCOUNT = 0x00002000,
  ADS_UF_DONT_EXPIRE_PASSWD = 0x00010000,
  ADS_UF_MNS_LOGON_ACCOUNT = 0x00020000,
  ADS_UF_SMARTCARD_REQUIRED = 0x00040000,
  ADS_UF_TRUSTED_FOR_DELEGATION = 0x00080000,
  ADS_UF_NOT_DELEGATED = 0x00100000,
  ADS_UF_USE_DES_KEY_ONLY = 0x00200000,
  ADS_UF_DONT_REQUIRE_PREAUTH = 0x00400000,
  ADS_UF_PASSWORD_EXPIRED = 0x00800000,
  ADS_UF_TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION = 0x01000000
)

ENUMS = {
  "GROUP_TYPES" : GROUP_TYPES,
  "AUTHENTICATION_TYPES" : AUTHENTICATION_TYPES,
  "SAM_ACCOUNT_TYPES" : SAM_ACCOUNT_TYPES,
  "USER_ACCOUNT_CONTROL" : USER_ACCOUNT_CONTROL
}

def _set (obj, attribute, value):
  """Helper function to add an attribute directly into the instance
   dictionary, bypassing possible __getattr__ calls
  """
  obj.__dict__[attribute] = value

def _and (*args):
  """Helper function to return its parameters and-ed
   together and bracketed, ready for a SQL statement.

  eg,

    _and ("x=1", "y=2") => "(x=1 AND y=2)"
  """
  return " AND ".join (args)

def _or (*args):
  """Helper function to return its parameters or-ed
   together and bracketed, ready for a SQL statement.

  eg,

    _or ("x=1", _and ("a=2", "b=3")) => "(x=1 OR (a=2 AND b=3))"
  """
  return " OR ".join (args)

def _add_path (root_path, relative_path):
  """Add another level to an LDAP path.
  eg,

    _add_path ('GC://DC=gb,DC=vo,DC=local', "cn=Users")
      => "GC://cn=users,DC=gb,DC=vo,DC=local"
  """
  protocol = "GC://"
  if relative_path.startswith (protocol):
    return relative_path

  if root_path.startswith (protocol):
    start_path = root_path[len (protocol):]
  else:
    start_path = root_path

  return protocol + relative_path + "," + start_path

#
# Global cached ADO Connection object
#
_connection = None
def connection ():
  global _connection
  if _connection is None:
    _connection = Dispatch ("ADODB.Connection")
    _connection.Provider = "ADsDSOObject"
    _connection.Open ("Active Directory Provider")
  return _connection

class ADO_record (object):
  """Simple wrapper around an ADO result set"""

  def __init__ (self, record):
    self.record = record
    self.fields = {}
    for i in range (record.Fields.Count):
      field = record.Fields.Item (i)
      self.fields[field.Name] = field

  def __getattr__ (self, name):
    """Allow access to field names by name rather than by Item (...)"""
    try:
      return self.fields[name]
    except KeyError:
      raise AttributeError

  def __str__ (self):
    """Return a readable presentation of the entire record"""
    s = []
    s.append (repr (self))
    s.append ("{")
    for name, item in self.fields.items ():
      s.append ("  %s = %s" % (name, item))
    s.append ("}")
    return "\n".join (s)

def query (query_string, **command_properties):
  """Auxiliary function to serve as a quick-and-dirty
   wrapper round an ADO query
  """
  command = Dispatch ("ADODB.Command")
  command.ActiveConnection = connection ()
  #
  # Add any client-specified ADO command properties.
  # NB underscores in the keyword are replaced by spaces.
  #
  # Examples:
  #   "Cache_results" = False => Don't cache large result sets
  #   "Page_size" = 500 => Return batches of this size
  #   "Time Limit" = 30 => How many seconds should the search continue
  #
  for k, v in command_properties.items ():
    command.Properties (k.replace ("_", " ")).Value = v
  command.CommandText = query_string

  recordset, result = command.Execute ()
  while not recordset.EOF:
    yield ADO_record (recordset)
    recordset.MoveNext ()

BASE_TIME = datetime.datetime (1601, 1, 1)
def ad_time_to_datetime (ad_time):
  hi, lo = i32 (ad_time.HighPart), i32 (ad_time.LowPart)
  ns100 = (hi << 32) + lo
  delta = datetime.timedelta (microseconds=ns100 / 10)
  return BASE_TIME + delta

def convert_to_object (item):
  if item is None: return None
  return AD_object (item)

def convert_to_objects (items):
  if items is None:
    return []
  else:
    if not isinstance (items, (tuple, list)):
      items = [items]

    #return [AD_object (item) for item in items]
    ad_objects = []
    for item in items:
        try:
            ad_object = AD_object(item)
        except:
            # NOTE: this ignores any item that causes an exception ... silently
            # This was done for MMS, which fails on a group with a "/" in it.
            # We cannot have zero objects return just because there is a single
            # bad entry
            pass
        else:
            ad_objects.append(ad_object)
    return ad_objects


def convert_to_datetime (item):
  if item is None: return None
  return ad_time_to_datetime (item)

def convert_to_sid (item):
  if item is None: return None
  return win32security.SID (item)

def convert_to_guid (item):
  if item is None: return None
  guid = convert_to_hex (item)
  return "{%s-%s-%s-%s-%s}" % (guid[:8], guid[8:12], guid[12:16], guid[16:20], guid[20:])

def convert_to_hex (item):
  if item is None: return None
  return "".join (["%x" % ord (i) for i in item])

def convert_to_enum (name):
  def _convert_to_enum (item):
    if item is None: return None
    return ENUMS[name][item]
  return _convert_to_enum

def convert_to_flags (enum_name):
  def _convert_to_flags (item):
    if item is None: return None
    item = i32 (item)
    enum = ENUMS[enum_name]
    return set (name for (bitmask, name) in enum.item_numbers () if item & bitmask)
  return _convert_to_flags

class _AD_root (object):
  def __init__ (self, obj):
    _set (self, "com_object", obj)
    _set (self, "properties", {})
    for i in range (obj.PropertyCount):
      property = obj.Item (i)
      proprties[property.Name] = property.Value

class _AD_object (object):
  """Wrap an active-directory object for easier access
   to its properties and children. May be instantiated
   either directly from a COM object or from an ADs Path.

   eg,

     import active_directory
     users = AD_object (path="GC://cn=Users,DC=gb,DC=vo,DC=local")
  """

  def __init__ (self, obj):
    #
    # Be careful here with attribute assignment;
    #  __setattr__ & __getattr__ will fall over
    #  each other if you aren't.
    #
    _set (self, "com_object", obj)
    schema = GetObject (obj.Schema)
    _set (self, "properties", schema.MandatoryProperties + schema.OptionalProperties)
    _set (self, "is_container", schema.Container)

    self._property_map = dict (
      objectGUID = convert_to_guid,
      uSNChanged = convert_to_datetime,
      uSNCreated = convert_to_datetime,
      replicationSignature = convert_to_hex,
      Parent = convert_to_object,
      wellKnownObjects = convert_to_objects
    )
    self._delegate_map = dict ()

  def __getitem__ (self, key):
    return getattr (self, key)

  def __getattr__ (self, name):
    #
    # Allow access to object's properties as though normal
    #  Python instance properties. Some properties are accessed
    #  directly through the object, others by calling its Get
    #  method. Not clear why.
    #
    if name not in self._delegate_map:
      try:
        attr = getattr (self.com_object, name)
      except AttributeError:
        try:
          attr = self.com_object.Get (name)
        except:
          raise AttributeError

      converter = self._property_map.get (name)
      if converter:
        self._delegate_map[name] = converter (attr)
      else:
        self._delegate_map[name] = attr

    return self._delegate_map[name]

  def __setitem__ (self, key, value):
    setattr (self, key, value)

  def __setattr__ (self, name, value):
    #
    # Allow attribute access to the underlying object's
    #  fields.
    #
    if name in self.properties:
      self.com_object.Put (name, value)
      self.com_object.SetInfo ()
    else:
      _set (self, name, value)

  def as_string (self):
    return self.path ()

  def __str__ (self):
    return self.as_string ()

  def __repr__ (self):
    return "<%s: %s>" % (self.__class__.__name__, self.as_string ())

  def __eq__ (self, other):
    return self.com_object.Guid == other.com_object.Guid

  class AD_iterator:
    """ Inner class for wrapping iterated objects
    (This class and the __iter__ method supplied by
    Stian Søiland <stian@soiland.no>)
    """
    def __init__(self, com_object):
      self._iter = iter(com_object)
    def __iter__(self):
      return self
    def next(self):
      return AD_object(self._iter.next())

  def __iter__(self):
    return self.AD_iterator(self.com_object)
    
  def walk (self):
    children = list (self)
    this_containers = [c for c in children if c.is_container]
    this_items = [c for c in children if not c.is_container]
    yield self, this_containers, this_items
    for c in this_containers:
      for container, containers, items in c.walk ():
        yield container, containers, items

  def dump (self, ofile=sys.stdout):
    ofile.write (self.as_string () + "\n")
    ofile.write ("{\n")
    for name in self.properties:
      try:
        value = getattr (self, name)
      except:
        value = "Unable to get value"
      if value:
        try:
          if isinstance (name, unicode):
            name = name.encode (sys.stdout.encoding)
          if isinstance (value, unicode):
            value = value.encode (sys.stdout.encoding)
          ofile.write ("  %s => %s\n" % (name, value))
        except UnicodeEncodeError:
          ofile.write ("  %s => %s\n" % (name, repr (value)))

    ofile.write ("}\n")

  def set (self, **kwds):
    """Set a number of values at one time. Should be
     a little more efficient than assigning properties
     one after another.

    eg,

      import active_directory
      user = active_directory.find_user ("goldent")
      user.set (displayName = "Tim Golden", description="SQL Developer")
    """
    for k, v in kwds.items ():
      self.com_object.Put (k, v)
    self.com_object.SetInfo ()

  def path (self):
    return self.com_object.ADsPath

  def parent (self):
    """Find this object's parent"""
    return AD_object (path=self.com_object.Parent)

  def child (self, relative_path):
    """Return the relative child of this object. The relative_path
     is inserted into this object's AD path to make a coherent AD
     path for a child object.

    eg,

      import active_directory
      root = active_directory.root ()
      users = root.child ("cn=Users")

    """
    return AD_object (path=_add_path (self.path (), relative_path))

  def find_user (self, name=None):
    name = name or win32api.GetUserName ()
    for user in self.search ("sAMAccountName='%s' OR displayName='%s' OR cn='%s'" % (name, name, name), objectCategory='Person', objectClass='User'):
      return user

  def find_users (self, name=None):
    name = name or win32api.GetUserName ()
    return self.search ("sAMAccountName='%s' OR displayName='%s' OR cn='%s'" % (name, name, name), objectCategory='Person', objectClass='User')


  def find_computer (self, name=None):
    name = name or socket.gethostname ()
    for computer in self.search (objectCategory='Computer', cn=name):
      return computer

  def find_group (self, name):
    for group in self.search (objectCategory='group', cn=name):
      return group
      
  def find_ou (self, name):
    for ou in self.search (objectClass="organizationalUnit", ou=name):
      return ou
      
  def find_public_folder (self, name):
    for public_folder in self.search (objectClass="publicFolder", displayName=name):
      return public_folder

  def search (self, *args, **kwargs):
    sql_string = []
    sql_string.append ("SELECT *")
    sql_string.append ("FROM '%s'" % self.path ())
    clauses = []
    if args:
      clauses.append (_and (*args))
    if kwargs:
      clauses.append (_and (*("%s='%s'" % (k, v) for (k, v) in kwargs.items ())))
    where_clause = _and (*clauses)
    if where_clause:
      sql_string.append ("WHERE %s" % where_clause)

    for result in query ("\n".join (sql_string), Page_size=50):
      yield AD_object (result.ADsPath.Value)



class _AD_user (_AD_object):
  def __init__ (self, *args, **kwargs):
    _AD_object.__init__ (self, *args, **kwargs)
    self._property_map.update (dict (
      pwdLastSet = convert_to_datetime,
      memberOf = convert_to_objects,
      objectSid = convert_to_sid,
      accountExpires = convert_to_datetime,
      badPasswordTime = convert_to_datetime,
      lastLogoff = convert_to_datetime,
      lastLogon = convert_to_datetime,
      lastLogonTimestamp = convert_to_datetime,
      lockoutTime = convert_to_datetime,
      msExchMailboxGuid = convert_to_guid,
      publicDelegates = convert_to_objects,
      publicDelegatesBL = convert_to_objects,
      sAMAccountType = convert_to_enum ("SAM_ACCOUNT_TYPES"),
      userAccountControl = convert_to_flags ("USER_ACCOUNT_CONTROL")
    ))

class _AD_computer (_AD_object):
  def __init__ (self, *args, **kwargs):
    _AD_object.__init__ (self, *args, **kwargs)
    self._property_map.update (dict (
      objectSid = convert_to_sid,
      accountExpires = convert_to_datetime,
      badPasswordTime = convert_to_datetime,
      lastLogoff = convert_to_datetime,
      lastLogon = convert_to_datetime,
      lastLogonTimestamp = convert_to_datetime,
      publicDelegates = convert_to_objects,
      publicDelegatesBL = convert_to_objects,
      pwdLastSet = convert_to_datetime,
      sAMAccountType = convert_to_enum ("SAM_ACCOUNT_TYPES"),
      userAccountControl = convert_to_flags ("USER_ACCOUNT_CONTROL")
    ))

class _AD_group (_AD_object):
  def __init__ (self, *args, **kwargs):
    _AD_object.__init__ (self, *args, **kwargs)
    self._property_map.update (dict (
      groupType = convert_to_flags ("GROUP_TYPES"),
      objectSid = convert_to_sid,
      member = convert_to_objects,
      memberOf = convert_to_objects,
      sAMAccountType = convert_to_enum ("SAM_ACCOUNT_TYPES")
    ))

  def walk (self):
    members = self.member or []
    groups = [m for m in members if m.Class == 'group']
    users = [m for m in members if m.Class == 'user']
    yield (self, groups, users)
    for group in groups:
      for result in group.walk ():
        yield result

class _AD_organisational_unit (_AD_object):
  def __init__ (self, *args, **kwargs):
    _AD_object.__init__ (self, *args, **kwargs)
    self._property_map.update (dict (
    ))

class _AD_domain_dns (_AD_object):
  def __init__ (self, *args, **kwargs):
    _AD_object.__init__ (self, *args, **kwargs)
    self._property_map.update (dict (
      creationTime = convert_to_datetime,
      dSASignature = convert_to_hex,
      forceLogoff = convert_to_datetime,
      fSMORoleOwner = convert_to_object,
      lockoutDuration = convert_to_datetime,
      lockoutObservationWindow = convert_to_datetime,
      masteredBy = convert_to_objects,
      maxPwdAge = convert_to_datetime,
      minPwdAge = convert_to_datetime,
      modifiedCount = convert_to_datetime,
      modifiedCountAtLastProm = convert_to_datetime,
      objectSid = convert_to_sid,
      replUpToDateVector = convert_to_hex,
      repsFrom = convert_to_hex,
      repsTo = convert_to_hex,
      subRefs = convert_to_objects,
      wellKnownObjects = convert_to_objects
    ))
    self._property_map['msDs-masteredBy'] = convert_to_objects
    
class _AD_public_folder (_AD_object):
  pass

_CLASS_MAP = {
  "user" : _AD_user,
  "computer" : _AD_computer,
  "group" : _AD_group,
  "organizationalUnit" : _AD_organisational_unit,
  "domainDNS" : _AD_domain_dns,
  "publicFolder" : _AD_public_folder
}
_CACHE = {}
def cached_AD_object (path, obj):
  try:
    return _CACHE[path]
  except KeyError:
    classed_obj = _CLASS_MAP.get (obj.Class, _AD_object) (obj)
    _CACHE[path] = classed_obj
    return classed_obj

def AD_object (obj_or_path=None, path=""):
  """Factory function for suitably-classed Active Directory
  objects from an incoming path or object. NB The interface
  is now  intended to be:

    AD_object (obj_or_path)

  but for historical reasons will continue to support:

    AD_object (obj=None, path="")

  @param obj_or_path Either an COM AD object or the path to one. If
  the path doesn't start with "GC://" this will be prepended.

  @return An _AD_object or a subclass proxying for the AD object
  """
  if path and not obj_or_path:
    obj_or_path = path
  try:
    if isinstance (obj_or_path, basestring):
      if not obj_or_path.upper ().startswith ("GC://"):
        obj_or_path = "GC://" + obj_or_path
      return cached_AD_object (obj_or_path, GetObject (obj_or_path))
    else:
      return cached_AD_object (obj_or_path.ADsPath, obj_or_path)
  except:
    #raise Exception, "Problem with path or object %s" % obj_or_path
    raise

def AD (server=None):
  default_naming_context = _root (server).Get ("defaultNamingContext")
  return AD_object (GetObject ("GC://%s" % default_naming_context))

def _root (server=None):
  # FIXME: for some reason, the has to be the LDAP protocol.  Everywhere
  # else here, we have used the GC protocol
  if server:
    rootDSE = GetObject ("LDAP://%s/rootDSE" % server)
  else:
    rootDSE = GetObject ("LDAP://rootDSE")
  return rootDSE

  #if server:
  #  return GetObject ("GC://%s/rootDSE" % server)
  #else:
  #  return GetObject ("GC://rootDSE")

def find_user (name=None,server=None):
  return root (server).find_user (name)

def find_user (name=None,server=None):
  return root (server).find_users (name)

def find_computer (name=None):
  return root ().find_computer (name)

def find_group (name):
  return root ().find_group (name)
  
def find_ou (name):
  return root ().find_ou (name)
  
def find_public_folder (name):
  return root ().find_public_folder (name)

#
# root returns a cached object referring to the
#  root of the logged-on active directory tree.
#
_ad = None
def root (server=None):
  global _ad
  if _ad is None:
    _ad = AD (server)
  return _ad

def search (*args, **kwargs):
  return root ().search (*args, **kwargs)

def search_ex (query_string=""):
  """Search the Active Directory by specifying a complete
   query string. NB The results will *not* be AD_objects
   but rather ADO_objects which are queried for their fields.

   eg,

     import active_directory
     for user in active_directory.search_ex (\"""
       SELECT displayName
       FROM 'GC://DC=gb,DC=vo,DC=local'
       WHERE objectCategory = 'Person'
     \"""):
       print user.displayName
  """
  for result in query (query_string, Page_size=50):
    yield result

