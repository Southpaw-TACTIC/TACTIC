


__all__ = ['DrupalPasswordHasher']

import hashlib

# Copied from: https://djangosnippets.org/snippets/2729/#c4520


"""
DrupalPasswordHasher

To use, put this in any app and add to your settings.py, something like this:

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'myproject.myapp.drupal_hasher.DrupalPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

Two notes: First, in Drupal the number of iterations is a multiple of 2,
which is represented by the first character after the $, so set the iterations
class member appropriately.

Secondly, in Drupal the passwords are stored as:

$S$<hash>

while in Django the passwords are stored as

S$<hash>

So you must cut off the first character of each password when migrating.
"""

import hashlib, sys

_ITOA64 = './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

IS_Pv3 = sys.version_info[0] > 2


class DrupalPasswordHasher(object):
    algorithm = u'S'
    iter_code = u'C'
    salt_length = 8

    def encode(self, password, salt, iter_code=None):
        """The Drupal 7 method of encoding passwords"""
        password = password.encode("utf8")
        salt = salt.encode("utf8")

        if iter_code == None:
            iterations = 2 ** _ITOA64.index(self.iter_code)
        else:
            iterations = 2 ** _ITOA64.index(iter_code)
        hash = hashlib.sha512(salt + password).digest()

        for i in range(iterations):
            hash = hashlib.sha512(hash + password).digest()

        l = len(hash)

        output = ''
        i = 0

        while i < l:

            num = hash[i]
            if IS_Pv3:
                value = hash[i] # python 3
            else:
                value = ord(hash[i])

            i = i + 1

            output += _ITOA64[value & 0x3f]
            if i < l:
                value |= num << 8

            output += _ITOA64[(value >> 6) & 0x3f]
            if i >= l:
                break
            i += 1

            if i < l:
                value |= num << 16

            output += _ITOA64[(value >> 12) & 0x3f]
            if i >= l:
                break
            i += 1

            output += _ITOA64[(value >> 18) & 0x3f]

        longhashed = "%s$%s%s%s" % (self.algorithm, iter_code,
                                    salt, output)
        return "$%s" % longhashed[:54]

    def verify(self, password, encoded):
        hash = encoded.split("$")[1]
        iter_code = hash[0]
        salt = hash[1:1 + self.salt_length]
        return encoded == self.encode(password, salt, iter_code)

if __name__ == '__main__':
    print(DrupalPasswordHasher().encode("123", "GC3Nis52", 'D'))


