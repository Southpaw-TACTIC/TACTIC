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


__all__ = ["Container", "GlobalContainer"]


import thread


# Get the container instance
INSTANCES = {}              # containers separated by thread
#session_instances = {}      # containers separated by ticket

def _get_instance():
    # get the current thread
    instance = INSTANCES.get(thread.get_ident())
    if instance == None:
        # create a new container
        instance = Container()
        INSTANCES[thread.get_ident()] = instance

    return instance

def _set_instance(instance):
    INSTANCES[thread.get_ident()] = instance


def _create_instance():
    instance = Container()
    INSTANCES[thread.get_ident()] = instance
    return instance

def _delete_instance():
    # delete old one for this thread
    container = INSTANCES[thread.get_ident()]
    container.clear_data()
    del(container)
    del(INSTANCES[thread.get_ident()])


class Container(object):
    '''general low level container object to store global information
    to the entire application'''

    def __init__(self):
        #print "INITIALIZING CONTAINER: ", thread.get_ident(), self
        self.info = dict()


    def get_data(self):
        return self.info

    def clear_data(self):
        self.info = {}


    def get_instance():
        return _get_instance()
    get_instance = staticmethod(get_instance)

    def set_instance(instance):
        return _set_instance(instance)
    set_instance = staticmethod(set_instance)


    def get_all_instances():
        return INSTANCES
    get_all_instances = staticmethod(get_all_instances)


    def put(key, value):
        _get_instance().info[key] = value
    put = staticmethod(put)


    stats = {}

    def get(key):
        #try:
        #    return _get_instance().info[key]
        #except:
        #    return None
        return _get_instance().info.get(key)
        #instance = _get_instance()
        #return instance.info.get(key)
    get = staticmethod(get)


    def has(key):
        return _get_instance().info.has_key(key)
    has = staticmethod(has)


    def remove(key):
        instance = _get_instance()
        if instance.info.has_key(key):
            del(instance.info[key])
    remove = staticmethod(remove)


    # convenience methods for managing a sequence
    #
    def clear_seq(key):
        seq = Container.get(key)
        if seq == None:
            seq = []
            Container.put(key, seq)
        else:
            del seq[:]  # clear the sequence
    clear_seq = staticmethod(clear_seq)

    def append_seq(key, value):
        seq = Container.get(key)
        if seq == None:
            seq = []
            Container.put(key, seq)
        seq.append(value)
        return seq
    append_seq = staticmethod(append_seq)

    def get_seq(key):
        seq = Container.get(key)
        if seq == None:
            seq = []
            Container.put(key, seq)
        return seq
    get_seq = staticmethod(get_seq)



    # convenience methods for managing a dictionary
    def _get_dict(dict_name):
        data = Container.get(dict_name)
        if data == None:
            data = {}
            Container.put(dict_name, data)
        return data
    _get_dict = staticmethod(_get_dict)

    def put_dict(dict_name, key, value):
        dict = Container._get_dict(dict_name)
        dict[key] = value
    put_dict = staticmethod(put_dict)

    def get_dict(dict_name, key):
        dict = Container._get_dict(dict_name)
        return dict.get(key)
    get_dict = staticmethod(get_dict)

    def get_full_dict(dict_name):
        dict = Container._get_dict(dict_name)
        return dict
    get_full_dict = staticmethod(get_full_dict)

    def clear_dict(dict_name):
        Container.put(dict_name, {})
    clear_dict = staticmethod(clear_dict)


    ###############################
    # Counter methods
    #
    def start_counter(key):
        Container.put(key, 0)
        return 0
    start_counter = staticmethod(start_counter)


    def get_counter(key):
        counter = Container.get(key)
        if counter == None:
            counter = Container.start_counter(key)
        return counter
    get_counter = staticmethod(get_counter)


    def increment(key):
        counter = Container.get(key)
        if counter == None:
            counter = 1
        else:
            counter += 1
        Container.put(key, counter)
        return counter
    increment = staticmethod(increment)


    def decrement(key):
        counter = Container.get(key)
        if counter == None:
            counter = -1 
        else:
            counter -= 1
        Container.put(key, counter)
        return counter
    decrement = staticmethod(decrement)




    def clear():
        '''Clears the container.  Should be called at the initialization
        of the application'''
        #print "clearing container!!!"
        instance = _get_instance()
        #del(instance.info)
        instance.info = {}
    clear = staticmethod(clear)


    def create():
        '''Creates the container.  Should be called at the initialization
        of the application'''
        instance = _create_instance()
        return instance
    create = staticmethod(create)

    def delete():
        '''Removes the container.'''
        #print "deleting container"
        _delete_instance()
    delete = staticmethod(delete)



    def clear_all():
        '''clears all the instances for all threads'''
        INSTANCES = {}
    clear_all = staticmethod(clear_all)



GLOBAL_CONTAINER = {}

class GlobalContainer(object):
    '''Global container that spans across all threads'''

    def put(key, value):
        GLOBAL_CONTAINER[key] = value
    put = staticmethod(put)

    def get(key):
        return GLOBAL_CONTAINER.get(key)
    get = staticmethod(get)


    def remove(key):
        instance = GLOBAL_CONTAINER
        if instance.has_key(key):
            del(instance[key])
    remove = staticmethod(remove)





