#!/usr/bin/python

from subprocess import Popen, PIPE

import os, sys


class JSXTranspileCmd():

    def execute(self, text):
        local_path = __file__
        if not local_path:
            dirname = "."
        else:
            dirname = os.path.dirname(local_path)
        if not dirname:
            dirname = "."

        print("dirname: [%s]" % dirname)

        # Need this to get the environment right.
        # FIXME: there must be a better way to set the environment of node.js
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


if __name__ == "__main__":
    text = sys.stdin.read()

    cmd = JSXTranspileCmd()
    js = cmd.execute(text)
    print(js)
