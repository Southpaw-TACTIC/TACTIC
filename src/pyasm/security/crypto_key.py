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

    def generate(self, size=1024):
        self.key = RSA.generate(size, os.urandom)
        self.private_key = (self.key.n, self.key.e, self.key.d)
        self.public_key = (self.key.n, self.key.e)

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
        coded = self.key.encrypt(msg, "x1y2y3")
        hex = binascii.hexlify(str(coded))
        return hex
     
        #f = open("password", "w")
        #f.write(hex)
        #f.close()



    def decrypt(self, hex):
        #f2 = open("password", "r")
        #hex = f2.read()
        uncoded = binascii.unhexlify(hex)
        try:
            xx2 = eval(uncoded)
        except:
            return ""

        decrypt = self.key.decrypt(xx2)
        return decrypt


