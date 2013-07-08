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
    def __init__(my):
        my.key = None
        my.private_key = None
        my.public_key = None

    def generate(my, size=1024):
        my.key = RSA.generate(size, os.urandom)
        my.private_key = (my.key.n, my.key.e, my.key.d)
        my.public_key = (my.key.n, my.key.e)

    def get_private_key(my):
        return my.private_key

    def get_public_key(my):
        return my.public_key

    def set_private_key(my, private_key):
        my.private_key = private_key
        my.key = RSA.construct(private_key)
        my.public_key = (my.key.n, my.key.e)

    def set_public_key(my, public_key):
        my.private_key = None
        my.public_key = public_key
        my.key = RSA.construct(public_key)


    def get_signature(my, msg):
        hash = MD5.new(msg).digest()
        signature = my.key.sign(hash, "")
        return signature


    def verify(my, msg, signature):
        hash = MD5.new(msg).digest()
        return my.key.verify(hash, signature)



    def encrypt(my, msg):
        coded = my.key.encrypt(msg, "x1y2y3")
        hex = binascii.hexlify(str(coded))
        return hex
     
        #f = open("password", "w")
        #f.write(hex)
        #f.close()



    def decrypt(my, hex):
        #f2 = open("password", "r")
        #hex = f2.read()
        uncoded = binascii.unhexlify(hex)
        try:
            xx2 = eval(uncoded)
        except:
            return ""

        decrypt = my.key.decrypt(xx2)
        return decrypt


