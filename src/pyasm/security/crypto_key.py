###########################################################
#
# Copyright (c) 2005-2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['CryptoKey']

import os, binascii

from Crypto.Hash import MD5
from Crypto.PublicKey import RSA


class CryptoKey(object):
    def __init__(self):
        self.key = None
        self.private_key = None
        self.public_key = None

    def generate(self, size=2048):
        self.key = RSA.generate(size, os.urandom)
        self.private_key = (self.key.n, self.key.e, self.key.d)
        self.public_key = (self.key.n, self.key.e)

    def import_key(self, key_location='mykey.pem', passphrase=None):
        f = open(key_location, 'r')
        self.key = RSA.importKey(f.read(), passphrase)
        self.private_key = (self.key.n, self.key.e, self.key.d)
        self.public_key = (self.key.n, self.key.e)

    def export_key(self, key_location='mykey.pem', key_format='PEM', passphrase=None, pkcs=1):
        f = open(key_location, 'w')
        f.write(RSA.exportKey(key_format, passphrase, pkcs))
        f.close()

    def get_private_key(self):
        return self.private_key

    def get_public_key(self):
        return self.public_key

    def set_private_key(self, private_key):
        self.private_key = private_key
        self.key = RSA.construct(private_key)
        self.public_key = (self.key.n, self.key.e)

    def set_public_key(self, public_key):
        self.private_key = None
        self.public_key = public_key
        self.key = RSA.construct(public_key)


    def get_signature(self, msg):
        hash = MD5.new(msg).digest()
        signature = self.key.sign(hash, "")
        return signature


    def verify(self, msg, signature):
        hash = MD5.new(msg).digest()
        return self.key.verify(hash, signature)



    def encrypt(self, msg):
        k = 84744 # A random parameter (for compatibility only. This value will be ignored) 
        coded = self.key.encrypt(msg.encode(), k) # encode required for Python3
        #hex = binascii.hexlify(str(coded))
        hex = binascii.hexlify(coded[0])
        return hex
     
        #f = open("password", "w")
        #f.write(hex)
        #f.close()



    def decrypt(self, hex):
        uncoded = binascii.unhexlify(hex)
        decrypt = self.key.decrypt(uncoded)
        decrypt = decrypt.decode('ascii')
        return decrypt


