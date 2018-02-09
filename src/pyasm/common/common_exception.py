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
'''Low level execptions or warning'''

__all__ = ["TacticException", "ClientTacticException", "SetupException", "UserException", "SecurityException", "SObjectSecurityException", "TacticWarning"]


class TacticException(Exception):

    def get_title(cls):
        try:
            return cls.TITLE
        except AttributeError:
            return cls.__class__.__name__

class ClientTacticException(TacticException):
    TITLE = "Client Error"

class SetupException(TacticException):
    '''Exception that will be caught by tactic and displayed in the interface
    as a setup error'''
    pass


class CodeException(TacticException):
    TITLE = "Code Error" 


class UserException(TacticException):
    TITLE = "User Error" 

class SecurityException(Exception):
    TITLE = "Security Error" 

class SObjectSecurityException(SecurityException):
    TITLE = "SObject Security Error" 

class TacticWarning(Warning):
    ''' a simple Warning Class, not really using the built-in Warning much '''
    def __init__(self, label, msg, type=''):
        self.label = label
        self.msg = msg
        self.type = type
        Warning.__init__(self)
        #super(TacticWarning, self).__init__()

    def get_label(self):
        return self.label

    def get_msg(self):
        return self.msg

    def get_type(self):
        return self.type




