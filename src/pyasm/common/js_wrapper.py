###########################################################
#
# Copyright (c) 2015, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['JsWrapper']

import tacticenv


from pyasm.common import Environment, jsonloads, jsondumps, Container

from tactic_client_lib import TacticServerStub


try:
    import PyV8
    HAS_PYV8 = True
except:
    HAS_PYV8 = False


def has_pyv8():
    return HAS_PYV8



# Replace console.log
class MyConsole(PyV8.JSClass):
    def log(self, *args):
        args2 = []
        for arg in args:
            arg = PyV8.convert(arg)
            args2.append(arg)

        print(" ".join([str(x) for x in args2]))




class ApiDelegator(PyV8.JSClass):

    def execute(my, func_name, args=[], kwargs={}):

        server = TacticServerStub.get()

        if args:
            args = jsonloads(args)
        if kwargs:
            kwargs = jsonloads(kwargs)


        if kwargs:
            # Quirk ... when there is a kwargs, the last args is the kwargs
            if args:
                args.pop()
            call = "server.%s(*args, **kwargs)" % func_name
        else:
            call = "server.%s(*args)" % func_name

        try:
            ret_val = eval(call)
        except Exception, e:
            print "ERROR: ", e
            raise


        ret_val = jsondumps(ret_val)
        return ret_val


class JSFile(object):

    def copy(my, src, dst):
        print "src: ", src
        print "dst: ", dst

    def move(my, src, dst):
        pass






class GlobalContext(PyV8.JSClass):
    console = MyConsole()
    spt_delegator = ApiDelegator()
    spt_file = JSFile()




class JsWrapper(object):

    def __init__(my):
        with PyV8.JSLocker():
            my.ctx = PyV8.JSContext(GlobalContext())
            my.ctx.enter()
            my.init()
            my.ctx.leave()



    def get():
        key = "JsWrapper"
        wrapper = Container.get(key)
        if wrapper == None:
            wrapper = JsWrapper()
            Container.put(key, wrapper)
        return wrapper
    get = staticmethod(get)


    def set_value(name, value):
        my.ctx.locals[name] = value


    def execute(my, js, kwargs={}):
        with PyV8.JSLocker():
            my.ctx.enter()

            for name, value in kwargs.items():
                my.ctx.locals[name] = value

            data = my.ctx.eval(js)
            my.ctx.leave()
        return data



    def execute_func(my, js, kwargs={}):

        js = '''
        var func = function() {
            %s
        }
        var ret_val = func();
        ret_val = JSON.stringify(ret_val);
        ''' % js
        ret_val = my.execute(js, kwargs)

        return ret_val



    def init(my):

        install_dir = Environment.get_install_dir()

        # initialize
        js = '''
        <!-- TACTIC -->
        // Fixes
        var spt = {};
        spt.browser = {};
        spt.browser.is_IE = function() { return false; }
        spt.error = function(error) {
            throw(error);
        }
        '''
        my.ctx.eval(js)
       
        sources = [
                "environment.js",
                "client_api.js"
        ]
        for source in sources: 
            #path = "tactic/%s" % source
            path = "%s/src/context/spt_js/%s" % (install_dir, source)
            js = open(path).read()
            my.ctx.eval(js)

        js = '''
spt._delegate = function(func_name, args, kwargs) {

    // convert everything to json
    var args2 = [];
    for (var i in args) {
        args2.push(args[i]);
    }

    if (typeof(kwargs) == "undefined") {
        kwargs = {};
    }

    args2 = JSON.stringify(args2);
    kwargs = JSON.stringify(kwargs);

    var ret_val = spt_delegator.execute(func_name, args2, kwargs);
    ret_val = JSON.parse(ret_val);
    return ret_val;

}

var server = TacticServerStub.get();
        '''
        my.ctx.eval(js)




def test():

    # TEST
    cmd = JsWrapper.get()

    import time
    start = time.time()
    js = '''
    console.log(server.ping() );

    console.log("---");
    var result = server.eval("@SOBJECT(sthpw/file)");
    for (var i in result) {
        var item = result[i];
        if ( i > 5 ) break;
        console.log(item.code);
    }
    '''
    cmd.execute(js)
    print time.time() - start


    js = '''
    console.log("---");
    var result = server.get_by_search_key(result[0].__search_key__);
    console.log(result.code);
    '''
    cmd.execute(js)
 
    js = '''
    console.log("---");
    var result = server.eval("@SOBJECT(sthpw/file)", {single: true});
    console.log(result.code);
    '''

    cmd.execute(js)


    print "---"
    js = '''
    return ['stream1','stream2'];
    ''';
    ret_val = cmd.execute_func(js)
    print "ret_val: ", ret_val


    print "---"
    js = '''
    spt_file.copy("tactic.png", "tactic2.png"); 
    ''';
    cmd.execute_func(js)


    print "---"
    kwargs = {
        'a': 123,
        'b': 234,
        'c': "This isn't it"
    }
    js = '''
    spt_file.copy("tactic.png", "tactic2.png"); 
    ''';
    cmd.execute_func(js, kwargs)





if __name__ == '__main__':

    from pyasm.security import Batch
    Batch()

    test()


