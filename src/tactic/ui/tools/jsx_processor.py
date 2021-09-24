#!/usr/bin/python

__all__ = ["JSXTranspile"]

import tacticenv
from pyasm.common import Xml, Config, GlobalContainer

from subprocess import Popen, PIPE

import os, sys


class JSXTranspile():


    def process_jsx(cls, behavior):
        '''This method is used in the custom LayoutEditor which
        will take jsx in a behavior xml and produce the appropariate js'''

        jsxs = []
        behaviors = []

        # process the jsx
        test = "<jsx>%s</jsx>" % behavior
        xml = Xml()
        xml.read_string(test)
        items = xml.get_nodes("jsx/behavior")
        for item in items:

            attributes = xml.get_attributes(item)
            attributes_str = ""
            for name, value in attributes.items():
                attributes_str += '''%s="%s" ''' % (name, value)
            attributes_str = attributes_str.strip()


            try:
                jsx = xml.get_node_value(item)

                js = cls.transpile(jsx)

            except Exception as e:
                print("WARNING: ", e)
                js = None


            # store the original behaviors as jsx
            behavior = "<jsx %s><![CDATA[\n%s\n]]></jsx>" % (attributes_str, jsx)
            jsxs.append(behavior)

            if js:
                behavior = "<behavior %s><![CDATA[\n%s\n]]></behavior>" % (attributes_str, js)
                behaviors.append(behavior)


        behaviors_str = "\n".join(behaviors)
        jsxs_str = "\n".join(jsxs)

        return (behaviors_str, jsxs_str)

    process_jsx = classmethod(process_jsx)




    def transpile(cls, jsx):
        '''Method to transpile jsx to js'''

        executable = __file__
        python = Config.get_value("services", "python") or "python"

        cmds = [python, executable, "-f", "temp"]

        if isinstance(jsx, str):
            jsx = jsx.encode()

        from subprocess import Popen, PIPE
        p = Popen(cmds, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        (o, e) = p.communicate(input=jsx)
        o = o.strip()
        e = e.strip()
        if e:
            print("WARNING: ", e)
            raise Exception(e)

        if jsx and not o:
            raise Exception("No compiled code")

        return o.decode()
    transpile = classmethod(transpile)



    def cache_jsx(cls, path, jsx, top=None):
        '''Onload JSX with caching'''

        tactic_mode = os.environ['TACTIC_MODE']
        is_dev_mode = False
        if tactic_mode == "development":
            is_dev_mode = True



        cache_key = "jsx:%s" % path


        # store this somewhere
        basename, ext = os.path.splitext(path)
        js_path = "%s.js" % basename


        js = GlobalContainer.get(cache_key)
        if js == None and not is_dev_mode:
            # production mode always reads from file first time as there
            # likely is no jsx processor
            f = open(js_path, "r")
            js = f.read()
            f.close()

            GlobalContainer.put(cache_key, js)

        if js == None:
            #jsx = self.get_onload_jsx()

            from tactic.ui.tools import JSXTranspile

            # transpile the jsx into js
            if is_dev_mode:
                try:
                    js = JSXTranspile.transpile(jsx)
                except Exception as e:
                    # if transpile fails, then try to read the js file
                    # (for those who do not have a JSX processor
                    print("WARNING: ", e)
                    f = open(js_path, "r")
                    js = f.read()
                    f.close()
                else:
                    print("Compiled JSX." )
                    f = open(js_path, "w")
                    f.write(js)
                    f.close()

            else:
                raise Exception("No corresponding js file found for jsx")

            GlobalContainer.put(cache_key, js)

        if top:
            top.add_behavior( {
                'type': 'load',
                'cbjs_action': js
            } )

        return js

    cache_jsx = classmethod(cache_jsx)







    def main(cls, text):
        '''method that is run from the command line in Popen above'''


        # Need this to get the environment right.
        # FIXME: hard coded
        # FIXME: there must be a better way to set the environment of node.js

        dirname = Config.get_value("jsx", "babel")
        if not dirname:
            dirname = "/home/tactic/npm/babel"

        os.chdir(dirname)

        if isinstance(text, str):
            text = text.encode()


        executable = "%s/node_modules/.bin/babel" % dirname

        cmds = [executable, "-f", "temp", "--no-comments"]
        p = Popen(cmds, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        (o, e) = p.communicate(input=text)
        if e:
            sys.stderr.write(e.decode())

        return o.decode()
    main = classmethod(main)



if __name__ == "__main__":

    # read from stdin
    text = sys.stdin.read()
    js = JSXTranspile.main(text)
    # output to stdout
    print(js)
