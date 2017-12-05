/* *********************************************
 *
 * Copyright (c) 2005, Southpaw Technology
 *                     All Rights Reserved
 *
 * PROPRIETARY INFORMATION.  This software is proprietary to
 * Southpaw Technology, and is not to be reproduced, transmitted,
 * or disclosed in any way without written permission.
 *
 *
 *
 */


package perforce;


import java.io.*;
import java.util.*;
import java.lang.*;

/* class that abstracts out perforce commands */
public class Perforce
{
    String PORT = "1666";

    void Perforce()
    {
        //System.setenv("P4PORT", PORT );
        //exec_path = get_exec_path();
        //if not os.path.exists(exec_path):
        //    raise SetupException( "Executable '%s' does not exist" % exec_path )
    }

    String get_exec_path()
    {
        return "p4";
    }


    String[] execute(String cmd, String input)
    {
        String p4_cmd = get_exec_path() + ' ' + cmd;
        return Common.execute(p4_cmd, input);
    }


    String[] execute(String cmd)
    {
        return execute(cmd, null);
    }


    byte[] execute2(String cmd)
    {
        String p4_cmd = get_exec_path() + ' ' + cmd;
        return Common.execute2(p4_cmd, null);
    }





    void add_file(String path)
    {
        path = path.replace("//", "/");
        String cmd = "add \"" + path + "\"";
        String[] ret_val = execute(cmd);
        System.out.println( ret_val );
    }


    String[] get_checkout(String path)
    {
        String cmd = "opened \"" + path + "...\"";
        String[] ret_val = execute(cmd.toString());
        return ret_val;
    }


    String[] get_repo(String path, boolean synced)
    {
        String p4_cmd = "files";
        if (synced)
            p4_cmd = "have";
        String cmd = p4_cmd + " \"" + path + "...\"";
        String[] ret_val = execute(cmd);
        return ret_val;
    }


    
    String checkin(String path)
    {
        String cmd = "add \"" + path + "\"";
        String[] ret_val = execute(cmd);
        return join(ret_val, "|") ;
    }

    String edit(String path)
    {
        path = path.replace("//", "/");
        String cmd = "edit \"" + path + "\"";
        String[] ret_val = execute(cmd);
        
        return join(ret_val,"|") ;
    }

    String revert(String path)
    {
        String cmd = "revert -a \"" + path + "\"";
        String[] ret_val = execute(cmd);
        
        return join(ret_val, "|") ;
    }

    String sync(String path)
    {
        String cmd = "sync -f \"" + path + "\"";
        String[] ret_val = execute(cmd);
        
        return join(ret_val, "|") ;
    }

    String get_root()
    {
        String[] ret_val = execute("workspaces");
        String[] tmp = ret_val[0].split(" ");

        // HACK: big hack to overcome the bad output from perforce
        String path = tmp[4];
        for (int i = 5; i < tmp.length; i++) {
            if ( tmp[i].startsWith("'") == false ) {
                path += " " + tmp[i];
            }
            else {
                break;
            }
        }

        String root = path.replace("\\", "/");
        return root;
    }


    String get_workspaces()
    {
        byte[] ret_val = execute2("workspaces");
        String root = Common.hexify(ret_val);
        return root;
    }
 
     
    /* param@ paths - list of file paths to be commited
     * param@ description - check in description
     * param@ root - P4 client installation root path
     */  
    String commit( String[] paths, String description, String root)
        
    {
        // Start a new changelist
        // get the change list and edit it
        String description_key = "<enter description here>";
        String[] output = execute("change -o");
        
        ArrayList input = new ArrayList();
        ArrayList files = new ArrayList();
        String line = null;
        for (int i=0; i<paths.length; i++)
        {
            String stripped_path = paths[i].replace(root.toLowerCase(), "");
            // force everything to lower case
            paths[i] = stripped_path.toLowerCase();
        }

        boolean files_flag = false;



        for (int i = 0; i < output.length; i++ )
        {
            // replace description
            line = output[i];
            line = line.replace(description_key, description);
            
            if ( line.startsWith("Files:") ) {
                files_flag = true;
            }
            else if ( files_flag == true && !match_path(paths, line) )
            {
                continue;
            }
            else {
                files.add(line);
            }

            input.add(line);
        }

        // if the are no file, do nothing
        if (files.size() == 0) {
            return "There are no files to checkin.";
        }

        String[] input_array = new String[input.size()];
        input.toArray(input_array);
        String input_str = join( input_array, "\n" );

        String[] ret_val = execute("change -i", input_str);
        String ret_val_str = join( ret_val, "\n" );
        System.out.println("ret: " + ret_val_str);

        // get the change list number
        String[] tmp = ret_val_str.split(" ");
        int changelist = Integer.valueOf(tmp[1]).intValue();

        // submit the change
        ret_val = execute("submit -c " + changelist );
        return join(ret_val, "|") ;

    }

    /* Match the line with one of the given paths */
    private boolean match_path(String[] paths, String line)
    {
        boolean matched = false;
        // force only the output paths to lower case
        line = line.toLowerCase();
        for (int i=0; i<paths.length && matched == false; i++)
        {
            if (line.indexOf(paths[i]) != -1)
            {
                matched = true;
            }
        }
        return matched;
    }
            
        

    private void print(String str)
    {
        System.out.println(str);
    }

    private String join(String[] a, String separator) {
        StringBuffer result = new StringBuffer();
        if (a.length > 0) {
            result.append(a[0]);
            for (int i=1; i<a.length; i++) {
                result.append(separator);
                result.append(a[i]);
            }
        }
        return result.toString();
    }

}




