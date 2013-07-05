############################################################
#
#    Copyright (c) 2009, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#

import os

import tacticenv

from pyasm.common import Environment
import tactic.ui.app.js_includes as js_includes


# This function gathers all javascript files listed in js_includes (as defined by js_includes.all_lists)
# and puts them all in on single javascript file.
#
# The compacting process also removes block comments and lines that begin with the line comment marker ("//").
# Also removed are any leading spaces on any line written out to the single javascript file.
#
# The generated output file is placed into tactic/src/context/spt_js and the file is named with:
#
#     _compact_spt_all_r<release_number>.js
#
# ... where <release_number> is the TACTIC install's release version number with dots changed to underscores.
#

def compact_javascript_files():

    print " "
    print "Processing javascript files to compact into single '_compact_spt_all.js' file ..."
    print " "

    context_path = "%s/src/context" % Environment.get_install_dir()
    all_js_path = js_includes.get_compact_js_filepath()

    out_fp = open( all_js_path, "w" )

    for (dir, includes_list) in js_includes.all_lists:
        for include in includes_list:
            js_path = "%s/%s/%s" % (context_path, dir, include)
            print "    >> processing '%s' ..." % js_path
            out_fp.write( "// %s\n\n" % js_path )
            in_fp = open( js_path, "r" )
            done = False
            comment_flag = False
            while not done:
                line = in_fp.readline()
                if not line:
                    done = True
                    continue
                line = line.strip()
                if line.startswith("//"):
                    continue
                start_comment_idx = line.find( "/*" )
                if start_comment_idx != -1:
                    comment_flag = True
                    tmp_line = line[ : start_comment_idx ].strip()
                    if tmp_line:
                        out_fp.write( "%s\n" % tmp_line )
                if line.find( "*/" ) != -1:
                    comment_flag = False
                    tmp_line = line[ line.find("*/") + 2 : ].strip()
                    if tmp_line:
                        out_fp.write( "%s\n" % tmp_line )
                    continue

                if comment_flag:
                    continue

                line = line.strip()
                if line:
                    out_fp.write( "%s\n" % line )

            in_fp.close()
            out_fp.write( "\n\n" )

    out_fp.close()

    print " "
    print "Generated compact '%s' file." % all_js_path

    print " "
    print "DONE compacting javascript files into single file."
    print " "


if __name__ == "__main__":

    compact_javascript_files()



